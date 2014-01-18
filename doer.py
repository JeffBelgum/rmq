#!/usr/bin/env python
import pika
import sys

topic = 'armrest'
route = 'tasks.import'
queue_name = 'importer' # FIXME: the SENDER should create the queue also, otherwise until the queue is created, messages are lost

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=topic, type='topic', durable=True)

# can't use anon queue, because then we lose messages after reboot

result = channel.queue_declare(queue=queue_name, durable=True)

channel.queue_bind(exchange=topic, queue=queue_name, routing_key=route)

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(callback, queue=queue_name)

channel.start_consuming()
# FIXME: exception when we reboot the server/lose conn

# TODO: daemonize, generalize