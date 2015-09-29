# -*- coding:utf-8 -*-
from collections import ChainMap
from .exceptions import CodegenException


class FrameMap(ChainMap):
    def __missing__(self, k):
        e = CodegenException("{} is not registered".format(k))
        e.key = k
        raise e
