# -*- coding:utf-8 -*-
import re
import shlex
from collections import OrderedDict


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
        pattern = "<(/?)\s*{prefix}([a-zA-Z0-9_\.]+)(\s+[^\s>^/]+)*\s*(/?)>".format(prefix=prefix)
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
