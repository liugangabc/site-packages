# coding=utf-8

import json
import requests
import time
from elasticsearch import Elasticsearch

es_host_1 = "10.19.180.200:9200"
es_servers = [es_host_1]


def print_hookl(resp, **kwargs):
    # if kwargs:
    #     print(kwargs)
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    info = '[{date}]\t{moveut} [ms]\t{url}\t{method}\t{status}'.format(
        date=now,
        moveut=resp.elapsed.total_seconds() * 1000,  # ms
        url=resp.url,
        method=resp.request.method,
        status=resp.status_code
    )
    print info


class ES(object):

    def __init__(self, host, proto='http'):
        self.session = requests.session()
        self.base_url = "{}://{}/".format(proto, host)

    def get(self, url, params=None, data=None):
        return self.session.get("{}{}".format(self.base_url, url), params=params, data=data,
                                hooks=dict(response=print_hookl))


ES = ES(host=es_host_1)


def es_health():
    url = '_cat/health?v'
    resp = ES.get(url)
    if resp.text:
        out = [node.split() for node in resp.text.encode("utf-8").split("\n") if node]
    else:
        out = []
    return out


def node_list():
    url = '_cat/nodes?v'
    resp = ES.get(url)
    if resp.text:
        out = [node.split() for node in resp.text.encode("utf-8").split("\n") if node]
    else:
        out = []
    return out


def get_node(to_dict=True):
    url = '?pretty'
    resp = ES.get(url)
    if to_dict:
        return json.loads(resp.text)
    return resp.text


def index_list():
    url = '_cat/indices?v'
    resp = ES.get(url)
    if resp.text:
        out = [idx.split() for idx in resp.text.encode("utf-8").split("\n") if idx]
    else:
        out = []
    return out


def get_index(name, pretty=True, to_dict=True):
    url = '{name}{pretty}'.format(name=name, pretty="?pretty" if pretty else "")
    resp = ES.get(url)
    if to_dict:
        return json.loads(resp.text)
    return resp.text


def doc_type_list(pretty=True):
    url = '_mapping{pretty}'.format(pretty="?pretty" if pretty else "")
    resp = ES.get(url)
    return resp.text


ES2 = Elasticsearch(es_servers)


def create_index(name):
    return ES2.indices.create(name)


def create_doc(index, doc_type, body, doc_id=None):
    return ES2.index(index, doc_type, body, id=doc_id)


def get_doc(index, doc_type, doc_id):
    return ES2.get(index, doc_type, doc_id)


def delete_doc(index, doc_type, doc_id):
    return ES2.delete(index, doc_type, doc_id)


def detete_doc_by_query(index, query, doc_type):
    return ES2.delete_by_query(index, body=query, doc_type=doc_type)


def doc_search(index, doc_type, query=None):
    """

    :param index:
    :param doc_type:
    :param query:
    查询name="python"的所有数据
    {
        "query":{
            "term":{
                "name":"python"
            }
        }
    }
    搜索出name="python"或name="android"的所有数据
    {
        "query":{
            "terms":{
                "name":[
                    "python","android"
                ]
            }
        }
    }
    match:匹配name包含python关键字的数据
     {
        "query":{
            "match":{
                "name":"python"
            }
        }
    }
    multi_match:在name和addr里匹配包含深圳关键字的数据
    {
        "query":{
            "multi_match":{
                "query":"深圳",
                "fields":["name","addr"]
            }
        }
    }
    搜索出id为1或2d的所有数据
    {
        "query":{
            "ids":{
                "type":"test_type",
                "values":[ "1","2" ]
            }
        }
    }
    获取name="python"并且age=18的所有数据
    must(都满足),should(其中一个满足),must_not(都不满足)
    {
        "query":{
            "bool":{
                "must":[
                    {
                        "term":{
                            "name":"python"
                        }
                    },
                    {
                        "term":{
                            "age":18
                        }
                    }
                ]
            }
        }
    }


    :return:
    """
    return ES2.search(index, doc_type, body=query)


def main(argv=None):
    print "Test case start\n"

    # SEVICE
    # print es_health()
    # print node_list()
    # print get_node(to_dict=False)

    # INDEX
    # print index_list()
    # index_name = "xxxxxx"
    # index = get_index(index_name)
    # print index
    # types = index[index_name]["mappings"].keys()
    # print(types)
    # json_body = dict(name="test", old=7, address="xxx")

    # DOCUMENT
    # new_doc = create_doc(index_name, types[0], body=json_body)
    # doc_id = new_doc["id"]
    # print delete_doc(index_name, types[0], doc_id)
    # print get_doc(index_name, types[0], doc_id)


if __name__ == "__main__":
    import sys

    sys.exit(main())
