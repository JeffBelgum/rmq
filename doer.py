#!/usr/bin/env python
import pika

# FIXME: error handling on all pika calls
# FIXME: exception when we reboot the server/lose conn
# TODO: daemonize, generalize
# FIXME: verify message persistence handling
# FIXME: replace print with logger

class Caerbannog(object):
    def __init__(self, topic, queue_name, host='localhost'):
        self.topic, self.queue_name, self.host = topic, queue_name, host

        self.routes = {}

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=self.topic, type='topic', durable=True)
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        super(Caerbannog, self).__init__()

    def consume(self):
        print " [i] consuming routes: (%r)" % (self.routes,)

        self.channel.basic_consume(self._callback, queue=self.queue_name)
        self.channel.start_consuming()

    def route(self, route, callback):
        self.routes[route] = callback
        self.channel.queue_bind(exchange=self.topic, queue=self.queue_name, routing_key=route)

    def _callback(self, channel, method, properties, body):
        print " [r] %r:%r" % (method.routing_key, body,)

        # FIXME: will this work for # and * routes?
        #
        callback = self.routes[method.routing_key]

        if callback:
            callback(body)
        else:
            print " [!] consuming unroutable msg: %r" % (method.routing_key,)

        print "%r" % ch
        print "%r" % method
        channel.basic_ack(delivery_tag=method.delivery_tag)        

class ArmrestImporter(Caerbannog):
    def __init__(self, host='localhost'):
        super(ArmrestImporter, self).__init__('armrest', 'importer', host)

        self.route('tasks.import', self.task_import)
        self.route('armrest.c2', self.c2)

    def task_import(self, msg):
        print " [m] task_import: [%r]" % (msg,)

    def c2(self, msg):
        print " [m] c2: [%r]" % (msg,)

ai = ArmrestImporter()
ai.consume()



