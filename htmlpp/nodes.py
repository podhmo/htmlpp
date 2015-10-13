# -*- coding:utf-8 -*-
from .utils import get_unquoted_string
import pickle


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
    def codegen(self, gen, m, attrs=None):
        fnname = gen.naming["render_fmt"].format("")
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]
        default_attributes = gen.naming["default_attributes"]

        with m.def_(fnname, writer, context, kwargs, **{default_attributes: "{}"}):
            is_emitted = False
            for node in self.children:
                if isinstance(node, Def):
                    gen.gencode(node, m.outside, use_pickle=False)
                else:
                    is_emitted = gen.gencode(node, m, use_pickle=False) or is_emitted
            if not is_emitted:
                m.stmt("pass")


class Def(Node):
    def codegen(self, gen, m, attrs=None):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]
        defaults = gen.naming["default_attributes"]

        m.body.append("def {}({}, {}, {}, {}=".format(fnname, writer, context, kwargs, defaults))
        m.storestack.append(m.submodule("{}", newline=False))
        m.stmt("):")
        with m.scope():
            m.stmt("")
            is_emitted = False
            for node in self.children:
                is_emitted = gen.gencode(node, m, attrs=attrs, use_pickle=True) or is_emitted
            if not is_emitted:
                m.stmt("pass")
        m.storestack.pop()
        m.sep()


class Yield(Node):
    @property
    def content_name(self):
        return get_unquoted_string(self.attrs.get("name")) or "body"

    def codegen(self, gen, m, attrs=None):
        fnname = gen.naming["block_fmt"].format(self.content_name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]

        m.stmt('{kwargs}["{fnname}"]({writer}, {context})'.format(
            fnname=fnname, writer=writer, context=context, kwargs=kwargs
        ))


class Import(Node):
    def __init__(self, *args, **kwargs):
        super(Import, self).__init__(*args, **kwargs)
        # TODO: gentle implementation
        assert "module" in self.attrs
        assert "alias" in self.attrs

    @property
    def module(self):
        return self.attrs["module"]

    @property
    def alias(self):
        return self.attrs["alias"]

    def codegen(self, gen, m, attrs=None):
        context = gen.naming["context"]
        m.stmt('{context}.import_module({module!r}, {alias!r})'.format(
            context=context, module=self.module, alias=self.alias
        ))


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

    def is_self_module_function(self, fnname):
        return "." not in fnname

    def as_block_node(self, node):
        name = node.name.replace(self.block_prefix, "", 1)
        return Block(name, node.attrs, node.children)

    def collect_block_nodes(self):
        nodes = []
        block_nodes = []
        for node in self.children:
            if self.is_block_node(node):
                block_nodes.append(self.as_block_node(node))
            else:
                nodes.append(node)
        if nodes:
            block_nodes.append(Block("body", {}, nodes))
        return block_nodes

    def codegen(self, gen, m, attrs=None):
        fnname = gen.naming["render_fmt"].format(self.name)
        writer = gen.naming["writer"]
        context = gen.naming["context"]
        kwargs = gen.naming["kwargs"]
        attributes = gen.naming["attributes"]

        m.stmt('new_{kwargs} = {kwargs}.new_child()  # kwargs is ChainMap'.format(
            kwargs=kwargs
        ))
        for node in self.collect_block_nodes():
            block_name = gen.naming["block_fmt"].format(node.name)
            with m.def_(block_name, writer, context):
                for snode in node.children:
                    gen.gencode(snode, m, attrs=None, use_pickle=False)
                if node.is_empty():
                    m.stmt("pass")
            m.stmt('new_{kwargs}["{fnname}"] = {fnname}'.format(
                kwargs=kwargs, fnname=block_name
            ))

        if self.attrs:
            m.stmt("# {attributes} :: {code!r}".format(attributes=attributes, code=self.attrs))
            m.stmt("new_{kwargs}[{attributes!r}] = pickle.loads({code!r})".format(
                kwargs=kwargs, attributes=attributes, code=pickle.dumps(self.attrs)
            ))

        if self.is_self_module_function(fnname):
            m.stmt('{fnname}({writer}, {context}, new_{kwargs})'.format(
                fnname=fnname, writer=writer, context=context, kwargs=kwargs
            ))
        else:
            m.stmt('{context}[{fnname!r}]({writer}, {context}, new_{kwargs})'.format(
                fnname=fnname, writer=writer, context=context, kwargs=kwargs
            ))
