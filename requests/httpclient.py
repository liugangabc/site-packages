#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests


def log(**data):
    pass
    # import pprint
    # pprint.pprint(data)


LOG = log


class HTTPClient(object):
    def __init__(self, host="127.0.0.1",
                 port='', protocol="http", timeout=3, allow_redirects=False):
        self.url = "{protocol}://{host}:{port}".format(
            **{"protocol": protocol, "host": host, "port": port})
        self.session = requests.session()
        self.option = dict(timeout=timeout, allow_redirects=allow_redirects)

    def get(self, url="", data=None, **kwargs):
        url = self.url + url
        self.option.update(kwargs)
        LOG(type="GET", url=url, data=data, option=self.option)
        return self.session.get(url=url, data=data, **self.option)

    def post(self, url="", data=None, json=None, **kwargs):
        url = self.url + url
        self.option.update(kwargs)
        LOG(type="POST", url=url, data=data, json=json, option=self.option)
        return self.session.post(url=url, json=json, data=data, **self.option)


class DjangoClient(object):
    def __init__(self, host="", port="80", auth_url="", auth_data=None):
        self.http = HTTPClient(host=host, port=port)
        resp = self.http.get(url=auth_url)
        csrftoken = resp.cookies.get_dict()["csrftoken"]
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken
        }
        self.http.post(url=auth_url, data=auth_data, headers=self.headers)

    def get(self, url="", data=None, **kwargs):
        url = self.http.url + url
        options = {
            "headers": {
                "Content-Type": "application/json",
            }
        }
        options.update(kwargs)
        return self.http.session.get(url=url, data=data, **options)

    def post(self, url="", data=None, json=None, **kwargs):
        url = self.http.url + url
        if json:
            options = {
                "headers": {
                    "Content-Type": "application/json",
                }
            }
        else:
            options = {
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            }
        options.update(kwargs)
        return self.http.session.post(url=url, json=json, data=data, **options)

        # django = DjangoClient(
        #     host="172.16.25.10",
        #     auth_url="/auth/login/",
        #     auth_data={
        #         "username": "admin",
        #         "password": "passw0rd"
        #     }
        # )
        # r = django.get(url="/restapi/")
        # print r.content
        # 通过 Djangoclient实例测试 restful接口
