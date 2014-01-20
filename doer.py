#!/usr/bin/env python
import pika
import daemon
import daemon.runner
import lockfile
import os
import logging
import logging.config

# FIXME: error handling on all pika calls
# FIXME: exception when we reboot the server/lose conn
#            logger.error('Failed to open file', exc_info=True)

# FIXME: graceful exit
# FIXME: verify message persistence handling
# FIXME: merge daemon boilerplate into Caerbannog

class Caerbannog(object):
    def __init__(self, topic, queue_name, host='localhost'):
        self.topic, self.queue_name, self.host = topic, queue_name, host
        
        self.logger = logging.getLogger('caerbannog')

        self.routes = {}

        self.logger.info("connecting to rabbitmq: [%s]" % (self.host))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.topic, type='topic', durable=True)
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        super(Caerbannog, self).__init__()

    def consume(self):
        self.channel.basic_consume(self._callback, queue=self.queue_name)
        self.logger.info("consuming")
        self.channel.start_consuming()

    def route(self, route, callback):
        self.logger.debug("adding route: %s => %r" % (route, callback))
        self.routes[route] = callback
        self.channel.queue_bind(exchange=self.topic, queue=self.queue_name, routing_key=route)

    def _callback(self, channel, method, properties, body):
        self.logger.debug("%r:%r" % (method.routing_key, body))

        # FIXME: will this work for # and * routes?
        #
        callback = self.routes[method.routing_key]

        if callback:
            callback(body)
        else:
            self.logger.warning("consuming unroutable message: [%s]:[%s]" % (method.routing_key, body))

        channel.basic_ack(delivery_tag=method.delivery_tag)        

class ArmrestImporter(Caerbannog):
    def __init__(self, host='localhost'):
        super(ArmrestImporter, self).__init__('armrest', 'importer', host=host)

        self.route('tasks.import', self.task_import)
        self.route('armrest.c2', self.c2)

    def task_import(self, msg):
        print " [m] task_import: [%r]" % (msg,)

    def c2(self, msg):
        print " [m] c2: [%r]" % (msg,)


class App(object):
    def __init__(self, chdir_path):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/tmp/doer.pid'
        self.pidfile_timeout = 1
        self.chdir_path = chdir_path

    def run(self):
        os.chdir(self.chdir_path)
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

        ai = ArmrestImporter()
        ai.consume()

app = App(os.getcwd())
runner = daemon.runner.DaemonRunner(app)
runner.do_action()