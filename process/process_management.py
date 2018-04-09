# coding=utf-8
"""
多进程管理服务，plant system 主要用来集中管理多个工作进程，每个工作进程的要处理业务可以相同，也可以完全不同，
主进程负责监控worker进程状态，异常结束的worker会被重新启动，尝试多次无法启动 会全体worker结束。
所以plant中 worker之间 最好是有业务依赖的 业务。要运行都运行，要结束都结束。
"""
from __future__ import absolute_import, division, print_function
import abc
import six
import os
import logging
import subprocess
import sys
import time

try:
    import multiprocessing
except ImportError:
    # Multiprocessing is not available on Google App Engine.
    multiprocessing = None

# Re-export this exception for convenience.
try:
    CalledProcessError = subprocess.CalledProcessError
except AttributeError:
    # The subprocess module exists in Google App Engine, but is empty.
    # This module isn't very useful in that case, but it should
    # at least be importable.
    if 'APPENGINE_RUNTIME' not in os.environ:
        raise

gen_log = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class WorkerBase(object):
    name = ''
    weight = 100
    status = False
    pid = 0

    @abc.abstractmethod
    def run(self):
        pass


class PlantSystem(object):
    def __init__(self, **kwargs):
        """
        配置系统参数，重试次数，重试间隔，配置文件路径
        """

        class PlantOption:
            workers = []
            workers_status = {}
            workers_info = {}
            restarts_interval = kwargs.get("restarts_interval", 3)
            restarts_max = kwargs.get("restarts_max", 5)

        self.option = PlantOption
        self.worker_info = None

    def add(self, worker):
        """
        注册工人类，检查工人类是否符合规范
        :param object:
        :return:
        """
        if not issubclass(worker, WorkerBase):
            raise
        name = getattr(worker, "name", None)
        if name is None:
            raise
        if name in self.option.workers_info:
            raise
        self.option.workers_info[name] = {"num_restarts": 0}
        self.option.workers.append(worker)

    def _run(self):
        """
        厂房运转 worker weight sort
        :return:
        """

        self.option.workers = sorted(self.option.workers, key=lambda w: w.name)

        def start_child(i):
            self.option.workers_info[i.name]["last_time"] = time.time()
            print(self.option.workers_info)
            pid = os.fork()
            if pid == 0:
                # child process
                i.status = True
                del self.option
                self.worker_info = i()
                return self.worker_info
            else:
                self.option.workers_status[pid] = i
                i.pid = pid
                return None

        for i in self.option.workers:
            id = start_child(i)
            if id is not None:
                return id
        while self.option.workers_status:
            try:
                pid, status = os.wait()
            except OSError as e:
                raise
            if pid not in self.option.workers_status:
                continue
            worker = self.option.workers_status.pop(pid)
            worker.status = False
            if os.WIFSIGNALED(status):
                gen_log.warning("child %d (pid %d) killed by signal %d, restarting",
                                worker.name, pid, os.WTERMSIG(status))
            elif os.WEXITSTATUS(status) != 0:
                gen_log.warning("child %d (pid %d) exited with status %d, restarting",
                                worker.name, pid, os.WEXITSTATUS(status))
            else:
                gen_log.info("child %d (pid %d) exited normally", worker.name, pid)
                continue

            if int(time.time() - self.option.workers_info[worker.name]["last_time"]) > self.option.restarts_interval:
                self.option.workers_info[worker.name]["num_restarts"] = 0
            else:
                self.option.workers_info[worker.name]["num_restarts"] += 1

            if self.option.workers_info[worker.name]["num_restarts"] > self.option.restarts_max:
                raise RuntimeError("Child name[{}] pid[{}] restarts giving up too many".format(worker.name, worker.pid))

            time.sleep(self.option.restarts_interval)

            gen_log.info("try restart child name[{}] pid[{}]".format(worker.name, worker.pid))
            new_id = start_child(worker)
            if new_id is not None:
                return new_id
        # All child processes exited cleanly, so exit the master process
        # instead of just returning to right after the call to
        # fork_processes (which will probably just start up another IOLoop
        # unless the caller checks the return value).
        sys.exit(0)

    def run(self):
        worker = self._run()
        worker.run()


# test case

class PrintWorker(WorkerBase):
    name = "xxxx"
    weight = 10

    def run(self):
        time.sleep(1)
        print("test 1")


class P(PrintWorker):
    name = "xxxx"
    weight = 1

    def run(self):
        raise


plant = PlantSystem()
plant.add(PrintWorker)
plant.add(P)
plant.run()
