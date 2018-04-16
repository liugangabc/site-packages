# coding=utf-8
"""
这是一个线程管理接口，将不同任务放入运行。
缺点：如果有一个线程异常，所有线程都会挂掉。
"""
from __future__ import absolute_import, division, print_function
import abc
import logging
from multiprocessing.pool import ThreadPool as Pool
import six
import time

gen_log = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class WorkerBase(object):
    name = ''

    @abc.abstractmethod
    def run(self):
        pass


class ThreadMaster(object):
    def __init__(self, **kwargs):
        self.option = {
            "restart_max": kwargs.get("restart_count", 3),
            "restart_num": 0,
            "restart_interval": kwargs.get("restart_interval", 1),
            "last_restart": kwargs.get("restart_interval", 1)
        }
        self.works = []

    def add(self, work):
        if not issubclass(work, WorkerBase):
            raise
        self.works.append(work)

    def _run(self, work):
        work().run()

    def run(self):
        while True:
            print(self.option)
            try:
                self.option["last_restart"] = time.time()
                pool = Pool(len(self.works))
                pool.map(self._run, self.works)
            except Exception as e:
                gen_log.error(e)
            if (time.time() - self.option["last_restart"]) > (self.option["restart_interval"] + 1):
                self.option["restart_num"] = 0
            self.option["restart_num"] += 1
            if self.option["restart_num"] >= self.option["restart_max"]:
                gen_log.error("restart too match")
                exit(1)
            time.sleep(self.option["restart_interval"])

# rabbitmq 聊天室 ，每个进程独占一个 队列（通过统一router_key，绑定到统一exchange的队列），当表一个用户， 所有的信息发送都会发送到 exchange，exchange会把所有信息个发送一份给所有绑定的 队列
# import signal
# import os
# from kombu.entity import Exchange, Queue
# from kombu.messaging import Producer, Consumer
# from kombu.connection import Connection
# # from kombu.pools import connections
#
# OO = {
#     "name": "xiaohong",
#     "status": False,
#     "message": None
# }
#
# room_exchange = Exchange('room', 'direct')
# message_queue = Queue('user1', exchange=room_exchange, routing_key='portkeys')
#
#
# class SendMessage(WorkerBase):
#     name = "SendM essage"
#
#     def __init__(self):
#         self.conn = Connection(hostname='localhost')
#         self.chan = self.conn.channel()
#         self.producer = Producer(self.chan, exchange=room_exchange, routing_key="portkeys")
#
#     def run(self):
#         try:
#             while True:
#                 time.sleep(1)
#                 send_buff = raw_input("\r我：")
#                 if send_buff == 'exit':
#                     pid = os.getpid()
#                     os.kill(pid, signal.SIGKILL)
#                 OO["message"] = send_buff
#                 self.producer.publish(
#                     OO,
#                     declare=[message_queue]
#                 )
#         except Exception as e:
#             print("send exception:", e)
#
#
# class GetMessage(WorkerBase):
#     name = "Get Message"
#
#     def __init__(self):
#         self.conn = Connection(hostname='localhost')
#         self.chan = self.conn.channel()
#         self.consumer = Consumer(self.chan, queues=[message_queue], callbacks=[GetMessage.call_back])
#         self.consumer.consume()
#
#     def run(self):
#         while True:
#             self.conn.drain_events()
#
#     @staticmethod
#     def call_back(data, message):
#         message.ack()
#         print("\r[{}]: {}".format(data['name'], data['message']))
#
#
# # test case chat
# m = ThreadMaster()
# m.add(GetMessage)
# m.add(SendMessage)
# m.run()
