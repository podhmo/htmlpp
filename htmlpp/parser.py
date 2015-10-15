# -*- coding:utf-8 -*-
from .exceptions import ParseException
from .lexer import (
    Open,
    OpenClose,
    Close
)
from .nodes import (
    Command,
    _Root,
    Def,
    Import,
    Yield,
    Block
)
from .utils import get_unquoted_string, Gensym


class Parser(object):
    node_classes = {}
    command_node = Command

    def __init__(self):
        self.gensym = Gensym()

    @classmethod
    def register(cls, nodeclass):
        cls.node_classes[nodeclass.get_class_name()] = nodeclass

    def create_node(self, token):
        if token.name in self.node_classes:
            factory = self.node_classes[token.name]
            return factory(name=self.get_node_name(token), attrs=token.attrs)
        else:
            factory = self.command_node
            return self._create_node_for_command_node(factory, name=token.name, attrs=token.attrs)

    def _create_node_for_command_node(self, factory, name, attrs):
        # treating. :params attributes as block node
        blocks = []
        for k in list(attrs.keys()):
            if k.startswith(":"):
                block_node_name = "{}.{}".format(name, k[1:])  # :foo -> <node>.foo
                block_node = self.node_classes["block"](name=block_node_name)
                block_node.add_child(get_unquoted_string(attrs.pop(k)))
                blocks.append(block_node)
        new_node = factory(name=name, attrs=attrs)
        for b in blocks:
            new_node.add_child(b)
        return new_node

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


Parser.register(Def)
Parser.register(Yield)
Parser.register(Import)
Parser.register(Block)
