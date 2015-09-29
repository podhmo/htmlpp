# -*- coding:utf-8 -*-
from collections import defaultdict
from .exceptions import ParseException
from .lexer import (
    Open,
    OpenClose,
    Close
)
from .nodes import (
    Command,
    _Root,
    Define,
    Import,
    Yield
)
from .utils import get_unquoted_string


class _Gensym(object):
    def __init__(self):
        self.c = defaultdict(int)

    def __call__(self, name=""):
        i = self.c[name]
        self.c[name] += 1
        return "{}{}".format(name, i)


class Parser(object):
    node_classes = {}
    command_node = Command

    def __init__(self):
        self.gensym = _Gensym()

    @classmethod
    def register(cls, nodeclass):
        cls.node_classes[nodeclass.get_class_name()] = nodeclass

    def create_node(self, token):
        try:
            factory = self.node_classes[token.name]
            return factory(name=self.get_node_name(token), attrs=getattr(token, "attrs"))
        except KeyError:
            factory = self.command_node
            return factory(name=token.name, attrs=getattr(token, "attrs"))

    def get_node_name(self, token):
        if hasattr(token, "attrs") and "name" in token.attrs:
            return get_unquoted_string(token.attrs["name"])
        else:
            return self.gensym(token.name)

    def __call__(self, tokens):
        root = _Root("*root")
        iterator = iter(tokens)
        self._construct([root], iterator)
        return root

    def is_open(self, token):
        return isinstance(token, Open)

    def is_close(self, token):
        return isinstance(token, Close)

    def is_openclose(self, token):
        return isinstance(token, OpenClose)

    def _construct(self, stack, iterator):
        for token in iterator:
            if self.is_open(token):
                newnode = self.create_node(token)
                stack[-1].add_child(newnode)
                stack.append(newnode)
            elif self.is_close(token):
                stack.pop()
            elif self.is_openclose(token):
                newnode = self.create_node(token)
                stack[-1].add_child(newnode)
            else:
                stack[-1].add_child(token)
        if len(stack) != 1:
            raise ParseException("unmatched tag: stack={}".format(stack))


Parser.register(Define)
Parser.register(Yield)
Parser.register(Import)
