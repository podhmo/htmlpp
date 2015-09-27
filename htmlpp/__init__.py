# -*- coding:utf-8 -*-
"""
"""
import re
import shlex
from prestring.python import PythonModule
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


class _Root(Node):
    def codegen(self, gen, m):
        fnname = gen.naming["render_fmt"].format("")
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        m.outside = m.submodule()

        with m.def_(fnname, writer, context, kwargs):
            for node in self.children:
                if isinstance(node, Define):
                    gen.gencode(node, m.outside)
                else:
                    gen.gencode(node, m)


class Define(Node):
    def codegen(self, gen, m):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        with m.def_(fnname, writer, context, kwargs):
            if not self.children:
                m.stmt("pass")
            else:
                for node in self.children:
                    gen.gencode(node, m)


class Yield(Node):
    @property
    def content_name(self):
        return self.attrs.get("name") or "body"

    def codegen(self, gen, m):
        fnname = gen.naming["block_fmt"].format(self.content_name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        m.stmt('{kwargs}["{fnname}"]({writer}, {context}, {kwargs})'.format(
            fnname=fnname, writer=writer, context=context, kwargs=kwargs
        ))


class Import(Node):
    pass


class Block(Node):
    pass


class Command(Node):
    def codegen(self, gen, m):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        nodes = []
        block_nodes = []
        for node in self.children:
            if isinstance(node, Block):
                block_nodes.append(node)
            else:
                nodes.append(node)

        if not block_nodes:
            block_nodes.append(Block("body", {}, nodes))
            nodes = []

        m.stmt('new_{kwargs} = {kwargs}.new_child()  # kwargs is ChainMap'.format(
            kwargs=kwargs
        ))
        for node in block_nodes:
            block_name = gen.naming["block_fmt"].format(node.name)
            with m.def_(block_name, writer, context, kwargs):
                if not self.children:
                    m.stmt("pass")
                else:
                    for node in node.children:
                        gen.gencode(node, m)
            m.stmt('new_{kwargs}["{fnname}"] = {fnname}'.format(
                kwargs=kwargs, fnname=block_name
            ))
        m.stmt('{fnname}({writer}, {context}, new_{kwargs})'.format(
            fnname=fnname, writer=writer, context=context, kwargs=kwargs
        ))


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
            return token.attrs["name"]
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


class Codegen(object):
    def __init__(self, naming=None):
        self.naming = naming
        if self.naming is None:
            self.naming = dict(
                render_fmt="_render_{}",
                block_fmt="_block_{}",
                writer="_writer",
                context="_context",
                kwargs="_kwargs",
            )

    def __call__(self, ast):
        m = PythonModule()
        self.gencode(ast, m)
        self.genmainfn(m)
        return str(m)

    def gencode(self, node, m):
        if hasattr(node, "codegen"):
            return node.codegen(self, m)
        else:
            return self._codegen_text(node, m)

    def genmainfn(self, m):
        context = self.naming["context"]
        writer = self.naming["writer"]
        kwargs = self.naming["kwargs"]
        fnname = self.naming["render_fmt"].format("")

        with m.def_("render", context, **{writer: None}):
            m.stmt("from collections import ChainMap")
            m.stmt('{kwargs} = ChainMap()'.format(kwargs=kwargs))
            with m.if_("{writer}".format(writer=writer)):
                m.return_('{fnname}({writer}, {context}, {kwargs})'.format(
                    fnname=fnname, writer=writer, context=context, kwargs=kwargs
                ))
            with m.else_():
                m.stmt("from io import StringIO")
                m.stmt("port = StringIO()")
                m.stmt('{writer} = port.write'.format(writer=writer))
                m.stmt('{fnname}({writer}, {context}, {kwargs})'.format(
                    fnname=fnname, writer=writer, context=context, kwargs=kwargs
                ))
                m.return_("port.getvalue()")

    def _codegen_text(self, text, m):
        writer = self.naming["writer"]
        if text.strip():
            m.stmt('{writer}({body!r})'.format(writer=writer, body=str(text)))


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
<div class="foo">
<@yield/>
<@define name="bar">
  <div class="bar">
  <@yield/>
  <@define name="boo">
    <div class="boo"/>
  </@define>
  <@boo/>
  <@yield/>
  </div>
</@define>
<@bar/>
<@yield/>
</div>
</@define>

    <@foo>
    <div>test</div>
    </@foo>
    <@foo>
    <div>test2</div>
    </@foo>
    """
    tokens = lexer(s)
    ast = parser(tokens)
    # dump_tree(ast)
    codegen = Codegen()
    print(codegen(ast))
    exec(codegen(ast))
    print(render({}))
