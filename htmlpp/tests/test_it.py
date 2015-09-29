# -*- coding:utf-8 -*-
import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, input_html, context):
        from htmlpp import Lexer, Parser, Codegen
        lexer = Lexer()
        parser = Parser()
        codegen = Codegen()
        M = {}
        code = codegen(parser(lexer(input_html)))
        print(code)
        exec(code, M)
        return M["render"]

    def test_it(self):
        input_html = """
<@define name="box">
 <div class="box">
 <@yield/>
 </div>
</@define>

<@box>this is box</@box>
"""
        context = {}
        render = self._callFUT(input_html, context)
        result = render(context)
        print(result)
