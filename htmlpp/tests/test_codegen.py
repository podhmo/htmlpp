# -*- coding:utf-8 -*-
import unittest
import evilunit


@evilunit.test_target("htmlpp:Codegen")
class CodegenTests(unittest.TestCase):
    def assert_normalized(self, left, right):
        self.assertEqual(_normalize(left), _normalize(right))

    def _callFUT(self, ast):
        codegen = self._makeOne()
        code = str(codegen(ast))
        M = {}
        exec(code, M)
        return M["render"]

    def test_empty(self):
        from htmlpp.nodes import _Root
        ast = _Root("", {}, [])
        render = self._callFUT(ast)
        context = {}
        result = render(context)
        self.assertEqual(result.strip(), "")

    def test_rawhtml(self):
        from htmlpp.nodes import _Root
        text = """
<!DOCTYPE html>
<html>
{% include "foo.bar.html" %}
{% for line in body%}
  <p>{{line}}</p>
{% endfor %}
</html>
"""
        ast = _Root(text, {}, [text])
        render = self._callFUT(ast)
        context = {}
        result = render(context)
        self.assert_normalized(result, text)


def _normalize(html):
    lines = [x.strip() for x in html.strip().split("\n")]
    return "".join(lines).replace("</", "\n</")
