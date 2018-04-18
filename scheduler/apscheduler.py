# coding=utf-8
from __future__ import absolute_import, division, print_function
import abc
import datetime
import six
import signal
import logging
import os
import requests
import time
from multiprocessing.pool import ThreadPool as Pool
from apscheduler.schedulers.blocking import BlockingScheduler

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
            except OSError:
                raise OSError
            except Exception as e:
                gen_log.error(e)
            if (time.time() - self.option["last_restart"]) > 1:
                self.option["restart_num"] = 0
            self.option["restart_num"] += 1
            if self.option["restart_num"] > self.option["restart_max"]:
                print("restart too match")
                exit(1)
            time.sleep(self.option["restart_interval"])


sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=600)
def timed_job():
    print('This job is run every sixth minutes.')


@sched.scheduled_job('interval', seconds=600)
def timed_job():
    print('This job is run every 60 minutes.')


# @sched.scheduled_job('cron', day_of_week='mon-fri', hour='0-9', minute='30-59', second='*/3')
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')


class S(WorkerBase):
    name = "s"

    def run(self):
        print('before the start funciton')
        sched.start()
        print("let us figure out the situation")


def webhook(url, method="GET"):
    d = requests.request(url=url, method=method)
    print(d)


def mqhook(url, route_key, exchange, data):
    pass


def call_back(type, **kwargs):
    if type == "webhook":
        webhook(**kwargs)
    elif type == "mqhook":
        mqhook(**kwargs)


class B(WorkerBase):
    name = "b"

    def run(self):
        time.sleep(3)
        print("b run")
        while True:
            cmd = raw_input("CMD:")
            if cmd == "list":
                for i in sched.get_jobs():
                    print(i.id)
            elif cmd.startswith("get"):
                uuid = sched.get_job(cmd.split()[-1])
                print(uuid)
            elif cmd.startswith("stop"):
                job = sched.get_job(cmd.split()[-1])
                job.pause()
            elif cmd.startswith("restart"):
                job = sched.get_job(cmd.split()[-1])
                job.resume()
            elif cmd.startswith("restart"):
                job = sched.get_job(cmd.split()[-1])
                job.resume()
            elif cmd.startswith("add"):
                cmd, type, url = cmd.split()
                data = {
                    "type": type,
                    "url": url
                }
                data = {
                    "scheduler_type": "interval",  # "date"
                    "years": 0,
                    "months": 0,
                    "days": 0,
                    "hours": 0,
                    "minutres": 0,
                    "seconds": 0
                }
                # 间隔调度（每隔多久执行)
                sched.add_job(call_back, 'interval', days=03, hours=17, minutes=19, seconds=07)
                # 定时调度（作业只会执行一次）
                sched.add_job(call_back, 'date', run_date=datetime.datetime(2009, 11, 6, 16, 30, 5))
            elif cmd.startswith("remove"):
                cmd, id = cmd.split()
                job = sched.get_job(id)
                job.remove()
            elif cmd == "exit":
                os.kill(os.getgid(), signal.SIGKILL)
            else:
                continue


m = ThreadMaster()
m.add(S)
m.add(B)
m.run()
