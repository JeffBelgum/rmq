#!/usr/bin/env ruby
# encoding: utf-8

require "bunny"

topic = 'armrest'
route = 'tasks.import'


conn = Bunny.new
conn.start

channel = conn.create_channel
exchange = channel.topic topic, durable: true

msg = ARGV.empty? ? "here's ya task!" : ARGV.join(" ")

exchange.publish(msg, routing_key: route, persistent: true)
puts " [x] Sent #{topic} :: #{route} :: #{msg}"

conn.close
