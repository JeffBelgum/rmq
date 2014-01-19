#!/usr/bin/env ruby
# encoding: utf-8

require "bunny"

topic = 'armrest'
route = 'tasks.import'
# route = 'armrest.c2'

conn = Bunny.new
conn.start

channel = conn.create_channel
exchange = channel.topic topic, durable: true

msg = ARGV.empty? ? "here's ya task!" : ARGV.join(" ")

# consider :mandatory
# condider :type to differentiate "do something" from "C&C:" like "halt" or "restart"
# consirer :app_id
# use: :reply_to
exchange.publish(msg, routing_key: route, persistent: true)
puts " [x] Sent #{topic} :: #{route} :: #{msg}"

conn.close
