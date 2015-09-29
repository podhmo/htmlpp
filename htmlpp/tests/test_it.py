# -*- coding:utf-8 -*-
import unittest


class Tests(unittest.TestCase):
    def assert_normalized(self, left, right):
        self.assertEqual(_normalize(left), _normalize(right))

    def _callFUT(self, input_html, context):
        from htmlpp import Lexer, Parser, Codegen
        lexer = Lexer()
        parser = Parser()
        codegen = Codegen()
        M = {}
        code = codegen(parser(lexer(input_html)))
        exec(code, M)
        return M["render"]

    def test_it(self):
        input_html = """
<@define name="box">
 <div class="box">
 <@yield/>
 </div>
</@define>

<@box><p>this is box</p></@box>
"""
        context = {}
        render = self._callFUT(input_html, context)
        result = render(context)
        expected = """
<div class="box">
<p>this is box</p>
</div>
"""
        self.assert_normalized(result, expected)

    def test_with_two_block(self):
        input_html = """
<@define name="box">
 <div class="box">
 <h1 class="heading"><@yield name="heading" /></h1>
 <@yield/>
 </div>
</@define>

<@box>
<@box.heading>this is title</@box.title>
<p>this is box</p>
</@box>
"""
        context = {}
        render = self._callFUT(input_html, context)
        result = render(context)
        expected = """
<div class="box">
<h1 class="heading">this is title</h1>
<p>this is box</p>
</div>
"""
        self.assert_normalized(result, expected)


def _normalize(html):
    lines = [x.strip() for x in html.strip().split("\n")]
    return "".join(lines).replace("</", "\n</")
