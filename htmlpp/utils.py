# -*- coding:utf-8 -*-
import re
import shlex
from collections import OrderedDict, defaultdict


_marker = object()


class Gensym(object):
    def __init__(self):
        self.c = defaultdict(int)

    def __call__(self, name=""):
        i = self.c[name]
        self.c[name] += 1
        return "{}{}".format(name, i)


def get_unquoted_string(x):
    if x and x.startswith('"') and x.endswith('"'):
        return x[1:-1]
    return x


def merge_dict(d0, d1):
    """roughly merging strategy for attribute strings(dict)"""
    for k, v in d1.items():
        is_add = k.endswith(":add")
        is_del = k.endswith(":del")
        if is_del or is_add:
            k = k[:-4]
        if is_add:
            if k not in d0:
                d0[k] = v
            else:
                stored_value = d0[k]
                is_quoted = False
                if stored_value and stored_value.startswith('"') and stored_value.endswith('"'):
                    is_quoted = True
                    stored_value = stored_value[1:-1]
                if v and v.startswith('"') and v.endswith('"'):
                    is_quoted = True
                    v = v[1:-1]
                if is_quoted:
                    d0[k] = '"{} {}"'.format(stored_value, v)
                else:
                    d0[k] = '{} {}'.format(stored_value, v)
        elif is_del:
            if k in d0:
                stored_value = d0[k]
                for sym in v.split(" "):
                    if sym and sym.startswith('"') and sym.endswith('"'):
                        sym = sym[1:-1]
                    stored_value = stored_value.replace(sym, "")
                d0[k] = stored_value
        else:
            d0[k] = v
    return d0


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
    pattern = "<(/?)\s*{prefix}([a-z:A-Z0-9_\.]+)((?:\s+[^\s>^/]+)+)*\s*(/?)>".format(prefix=prefix)
    return re.compile(pattern, re.MULTILINE)


def render_hello(_writer, _context, _kwargs, _default_attributes={}):
    return _writer("hello")
