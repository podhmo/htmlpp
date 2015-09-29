# -*- coding:utf-8 -*-
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
            else:
                m.stmt("pass")


class Define(Node):
    def codegen(self, gen, m):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        with m.def_(fnname, writer, context, kwargs):
            for node in self.children:
                gen.gencode(node, m)
            else:
                m.stmt("pass")


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