# -*- coding:utf-8 -*-
"""
"""
import re
import shlex
from collections import defaultdict, OrderedDict


class HTMLPPException(Exception):
    pass


class ParseException(HTMLPPException):
    pass


class Token(object):
    pass


class Open(Token):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def __repr__(self):
        return '<@{} at {}>'.format(self.name, hex(id(self)))


class OpenClose(Token):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def __repr__(self):
        return '<@{} at {}/>'.format(self.name, hex(id(self)))


class Close(Token):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '</@{} at {}>'.format(self.name, hex(id(self)))


def parse_attrs(attribute_string):
    """dict from html attribute like string"""
    if not attribute_string:
        return {}
    d = OrderedDict()
    symbols = shlex.split(attribute_string.strip())
    for sym in symbols:
        if "=" in sym:
            k, v = sym.split("=", 1)
            d[k] = v
        else:
            d[sym] = True  # xxx
    return d


class Lexer(object):
    def __init__(self, prefix="@", parse_attrs=parse_attrs):
        pattern = "<(/?)\s*{prefix}([a-zA-Z0-9_]+)(\s+[^\s>]+)*\s*(/?)>".format(prefix=prefix)
        self.scanner = re.compile(pattern, re.MULTILINE)
        self.parse_attrs = parse_attrs

    def dispatch(self, m):
        gs = m.groups()
        if gs[0]:
            return Close(gs[1])
        elif gs[-1]:
            return OpenClose(gs[1], self.parse_attrs(gs[2]))
        else:
            return Open(gs[1], self.parse_attrs(gs[2]))

    def add(self, buf, x):
        if x:
            buf.append(x)

    def __call__(self, body):
        buf = []
        body = body.strip()
        search = self.scanner.scanner(body).search
        m = None
        end = 0
        while True:
            prev_m, m = m, search()
            if m is None:
                if prev_m is None:
                    self.add(buf, body)
                else:
                    self.add(buf, prev_m.string[prev_m.end():])
                return buf
            self.add(buf, m.string[end:m.start()])
            self.add(buf, self.dispatch(m))
            end = m.end()


class Node(object):
    def __init__(self, name, attrs=None, children=None):
        self.name = name
        self.attrs = attrs or {}
        self.children = children or []

    @classmethod
    def get_class_name(cls):
        return cls.__name__.lower()

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return "<{} {}>".format(self.get_class_name(), self.name)


class Define(Node):
    pass


class Yield(Node):
    pass


class Import(Node):
    pass


class Command(Node):
    pass


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
        except KeyError:
            factory = self.command_node
        return factory(name=self.get_node_name(token), attrs=getattr(token, "attrs"))

    def get_node_name(self, token):
        if hasattr(token, "attrs") and "name" in token.attrs:
            return token.attrs["name"]
        else:
            return self.gensym(token.name)

    def __call__(self, tokens):
        root = Node("*root")
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


def dump_tree(ast, indent=0, d=2, strip_empty_text=True):
    if not hasattr(ast, "children"):
        if not strip_empty_text or ast.strip():
            print("{}<text '{}'>".format(" " * indent, ast[:20].replace("\n", "\\n")))
    else:
        print("{}{}".format(" " * indent, ast))
        for child in ast.children:
            dump_tree(child, indent=indent + d, d=d)


Parser.register(Define)
Parser.register(Yield)
Parser.register(Import)


if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()
    s = """
    <@define name="foo">
      <@yield/>
      <@define name="bar">
        <@yield/>
        <@define name="boo">
        </@define>
        <@yield/>
      </@define>
      <@yield/>
    </@define>

    <@foo/>
    """
    tokens = lexer(s)
    ast = parser(tokens)
    dump_tree(ast)
