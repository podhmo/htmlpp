# -*- coding:utf-8 -*-
import pickle
from prestring.python import PythonModule
from .utils import create_html_tag_regex, parse_attrs, string_from_attrs


class Codegen(object):
    def __init__(self, naming=None):
        self.naming = naming
        self.html_tag_regex = create_html_tag_regex(prefix="")

        if self.naming is None:
            self.naming = dict(
                render_fmt="render_{}",
                block_fmt="block_{}",
                writer="_writer",
                context="_context",
                kwargs="_kwargs",
                attributes="_attributes",
                default_attributes="_default_attributes",
            )

    def __call__(self, ast):
        m = PythonModule()
        m.stmt("import pickle")
        m.stmt("from collections import OrderedDict")
        m.stmt("from htmlpp.utils import string_from_attrs, merge_dict, render_with")
        m.sep()
        m.outside = m.submodule()
        m.storestack = m.outside.storestack = []
        self.gencode(ast, m)
        self.genmainfn(m)
        return str(m)

    def gencode(self, node, m, attrs=None, use_pickle=False):
        if hasattr(node, "codegen"):
            node.codegen(self, m, attrs=attrs)
            return True
        else:
            return self._codegen_text(node, m, passed_attrs=attrs, use_pickle=use_pickle)

    def genmainfn(self, m):
        context = self.naming["context"]
        writer = self.naming["writer"]
        kwargs = self.naming["kwargs"]
        fnname = self.naming["render_fmt"].format("")

        with m.def_("render", context, **{writer: None}):
            m.stmt('return render_with({fnname}, {context}, {writer}={writer})'.format(
                fnname=fnname, writer=writer, context=context, kwargs=kwargs
            ))

    def _codegen_text_simple(self, text, m, use_pickle=False):
        if text.strip():
            writer = self.naming["writer"]
            m.stmt('{writer}({body!r})'.format(writer=writer, body=str(text)))

    def _codegen_default_attributes(self, attrs, m, use_pickle=False):
        if attrs and use_pickle:
            default_attributes = self.naming["default_attributes"]
            m.storestack[-1].body.body.pop()  # xxx
            m.storestack[-1].body.append('pickle.loads({code!r})'.format(code=pickle.dumps(attrs)))
            m.stmt('# {} :: {!r}'.format(default_attributes, attrs))

    def _codegen_text(self, text, m, passed_attrs=None, use_pickle=False):
        writer = self.naming["writer"]
        kwargs = self.naming["kwargs"]
        attributes = self.naming["attributes"]
        default_attributes = self.naming["default_attributes"]

        if not text.strip():
            return False

        match = self.html_tag_regex.search(text)
        if not match:
            m.stmt('{writer}({body!r})'.format(writer=writer, body=str(text)))
            return True

        prefix, tag, attrs_str, suffix = match.groups()
        attrs = parse_attrs(attrs_str or "")
        self._codegen_default_attributes(attrs, m, use_pickle=use_pickle)

        if passed_attrs:
            attrs.update(passed_attrs)

        m.stmt('{writer}({body!r})'.format(writer=writer, body=text[:match.start()]))
        if not prefix and use_pickle:
            body = "<{prefix}{tag}{{attrs}}{suffix}>{rest}".format(
                prefix=prefix,
                tag=tag,
                suffix=suffix,
                rest=text[match.end():]
            )
            m.stmt("D = OrderedDict()")
            m.stmt("merge_dict(D, {defaults})".format(defaults=default_attributes))
            with m.if_("{attributes!r} in {kwargs}".format(attributes=attributes, kwargs=kwargs)):
                m.stmt("merge_dict(D, {kwargs}[{attributes!r}])".format(attributes=attributes, kwargs=kwargs))
            m.stmt('{writer}({body!r}.format(attrs=string_from_attrs(D)))'.format(writer=writer, body=body))
            return True
        else:
            body = "<{prefix}{tag}{attrs}{suffix}>{rest}".format(
                prefix=prefix,
                tag=tag,
                attrs=string_from_attrs(attrs),
                suffix=suffix,
                rest=text[match.end():]
            )
            m.stmt('{writer}({body!r})'.format(writer=writer, body=body))
            return True
