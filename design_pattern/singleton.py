# coding=utf-8


class Singleton(object):
    """
    使用 __new__ 来控制实例的创建过程
    """
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


class MyClass(Singleton):
    a = 1

# 在 __init__ 文件 使用变量的形式        app = MyClass()
# 对外开放 一个初始化的对象 达到单例的效果   all = ["app"]
