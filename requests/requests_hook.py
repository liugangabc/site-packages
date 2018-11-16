# coding=utf-8

import time
from requests import Request


def requests_hook():
    def write_log(resp, *args, **kwargs):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        info = '{date}\t{moveut}\t{url}\t{method}\t{status}'.format(
            date=now,
            moveut=resp.elapsed.total_seconds() * 1000,  # ms
            url=resp.url,
            method=resp.request.method,
            status=resp.status_code
        )
        print info

    old_init = Request.__init__

    def patched_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        self.hooks['response'].append(write_log)

    Request.__init__ = patched_init


if __name__ == "__main__":
    # 在系统启动前加载，目前只支持 requests api 不支持 requests.Requests
    requests_hook()
    import requests

    response = requests.get("http://www.baidu.com")
    response.raise_for_status()
