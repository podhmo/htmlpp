# -*- coding:utf-8 -*-
from collections import ChainMap
from .exceptions import CodegenException


class FrameMap(ChainMap):
    def __missing__(self, k):
        e = CodegenException("{} is not registered".format(k))
        e.key = k
        raise e


class Context(object):
    def __init__(self, d, repository):
        self.d = d
        self.repository = repository

    def import_module(self, module_name, alias):
        module = self.d.get(alias)
        if module is not None:
            return module

        module = self.repository(module_name)
        self.d[alias] = module
        return module

    def __contains__(self, k):
        return k in self.d

    def __getitem__(self, k):
        return self.d[k]

    def __setitem__(self, k, v):
        self.d[k] = v
