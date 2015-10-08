# -*- coding:utf-8 -*-
import re
import shlex
from collections import OrderedDict


_marker = object()


def get_unquoted_string(x):
    if x and x.startswith('"') and x.endswith('"'):
        return x[1:-1]
    return x


def parse_attrs(attribute_string):
    """dict from html attribute like string"""
    d = OrderedDict()
    if not attribute_string:
        return d
    symbols = shlex.split(attribute_string.strip(), posix=False)
    buf = []
    for sym in symbols:
        if "=" in sym:
            if buf:
                d[" ".join(buf)] = _marker
            k, v = sym.split("=", 1)
            d[k] = v
        else:
            buf.append(sym)
    if buf:
        d[" ".join(buf)] = _marker
    return d


def string_from_attrs(attrs):
    if not attrs:
        return ""
    r = [""]

    for k in attrs:
        v = attrs[k]
        if v is _marker:
            r.append(k)
        else:
            r.append('{}={}'.format(k, v))
    return " ".join(r)


def create_html_tag_regex(prefix="@"):
    pattern = "<(/?)\s*{prefix}([a-zA-Z0-9_\.]+)((?:\s+[^\s>^/]+)+)*\s*(/?)>".format(prefix=prefix)
    return re.compile(pattern, re.MULTILINE)
