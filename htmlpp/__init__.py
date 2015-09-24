# -*- coding:utf-8 -*-
"""
"""
import re


class Node:
    pass


class Open(Node):
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr

    def __repr__(self):
        return '<@{} at {}>'.format(self.name, hex(id(self)))


class OpenClose(Node):
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr

    def __repr__(self):
        return '<@{} at {}/>'.format(self.name, hex(id(self)))


class Close(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '</@{} at {}>'.format(self.name, hex(id(self)))


class Lexer(object):
    def __init__(self, prefix="@"):
        pattern = "<(/?)\s*{prefix}([a-zA-Z0-9_]+)(\s+[^\s>]+)*\s*(/?)>".format(prefix=prefix)
        self.scanner = re.compile(pattern, re.MULTILINE)

    def dispatch(self, m):
        gs = m.groups()
        if gs[0]:
            return Close(gs[1])
        elif gs[-1]:
            return OpenClose(gs[1], gs[2])
        else:
            return Open(gs[1], gs[2])

    def add(self, buf, x):
        if x:
            buf.append(x)

    def __call__(self, body, default=list):
        buf = default()
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
