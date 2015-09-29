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

    def is_empty(self):
        for child in self.children:
            if not hasattr(child, "strip"):
                return False
            if child.strip():
                return False
        return True

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
            if self.is_empty():
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
            if self.is_empty():
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

        m.stmt('{kwargs}["{fnname}"]({writer}, {context})'.format(
            fnname=fnname, writer=writer, context=context, kwargs=kwargs
        ))


class Import(Node):
    pass


class Block(Node):
    pass


class Command(Node):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        # <@foo><@foo.title/><@foo>  # @foo.title is treated as block node
        self.block_prefix = "{}.".format(self.name)

    def is_block_node(self, node):
        return (isinstance(node, Block)
                or (isinstance(node, Command) and node.name.startswith(self.block_prefix)))

    def as_block_node(self, node):
        name = node.name.replace(self.block_prefix, "", 1)
        return Block(name, node.attrs, node.children)

    def codegen(self, gen, m):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        nodes = []
        block_nodes = []
        for node in self.children:
            if self.is_block_node(node):
                block_nodes.append(self.as_block_node(node))
            else:
                nodes.append(node)
        if nodes:
            block_nodes.append(Block("body", {}, nodes))
        nodes = []

        m.stmt('new_{kwargs} = {kwargs}.new_child()  # kwargs is ChainMap'.format(
            kwargs=kwargs
        ))
        for node in block_nodes:
            block_name = gen.naming["block_fmt"].format(node.name)
            with m.def_(block_name, writer, context):
                for snode in node.children:
                    gen.gencode(snode, m)
                if node.is_empty():
                    m.stmt("pass")
            m.stmt('new_{kwargs}["{fnname}"] = {fnname}'.format(
                kwargs=kwargs, fnname=block_name
            ))
        m.stmt('{fnname}({writer}, {context}, new_{kwargs})'.format(
            fnname=fnname, writer=writer, context=context, kwargs=kwargs
        ))
