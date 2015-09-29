# -*- coding:utf-8 -*-
from prestring.python import PythonModule


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
