# -*- coding:utf-8 -*-
import unittest


class Tests(unittest.TestCase):
    def assert_normalized(self, left, right):
        self.assertEqual(_normalize(left), _normalize(right))

    def _callFUT(self, input_html):
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
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="box">
<p>this is box</p>
</div>
"""
        self.assert_normalized(result, expected)

    def test_with_attributes(self):
        input_html = """
<@define name="box">
<div class="box">
<@yield/>
</div>
</@define>

<@box id="myBox">hmm</@box>
<@box id="yourBox">oyoyo</@box>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="box" id="myBox">hmm</div>
<div class="box" id="yourBox">oyoyo</div>
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
<@box.heading>this is title</@box.heading>
<p>this is box</p>
</@box>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="box">
<h1 class="heading">this is title</h1>
<p>this is box</p>
</div>
"""
        self.assert_normalized(result, expected)

    def test_internal_fn(self):
        input_html = """
<@define name="twobox">
 <@define name="left">
   <div class="left">
   <@yield/>
   </div>
 </@define>
 <@define name="right">
   <div class="right">
   <@yield/>
   </div>
 </@define>
<div class="twobox">
  <@left><@yield name="left"/></@left>
  <@right><@yield name="right"/></@right>
</div>
</@define>

<@twobox>
<@twobox.left>
X
</@twobox.left>
<@twobox.right>
Y
</@twobox.right>
</@twobox>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="twobox">
<div class="left">X</div>
<div class="right">Y</div>
</div>
"""
        self.assert_normalized(result, expected)

    def test_nested(self):
        input_html = """
<@define name="nested">
<@define name="nested0">
0<@yield/>
<@nested1/>
0<@yield/>
</@define>

<@define name="nested1">
1<@yield/>
1<@yield/>
<@nested2/>
1<@yield/>
1<@yield/>
</@define>

<@define name="nested2">
<@yield/><@yield/><@yield/>
</@define>
<div class="nested"><@nested0><@yield/></@nested0></div>
</@define>

<@nested>
<p>foo</p>
</@nested>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="nested">
0<p>foo</p>
1<p>foo</p>1<p>foo</p>
<p>foo</p><p>foo</p><p>foo</p>
1<p>foo</p>1<p>foo</p>
0<p>foo</p>
</div>
"""
        self.assert_normalized(result, expected)

    def test_nested2(self):
        input_html = """
<@define name="nested">
  <@define name="nested0">
    <@define name="nested1">
      <@define name="nested2">
      <@yield/><@yield/><@yield/>
      </@define>
    1<@yield/>
    1<@yield/>
    <@nested2/>
    1<@yield/>
    1<@yield/>
    </@define>
  0<@yield/>
  <@nested1/>
  0<@yield/>
  </@define>
<div class="nested"><@nested0><@yield/></@nested0></div>
</@define>

<@nested>
<p>foo</p>
</@nested>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="nested">
0<p>foo</p>
1<p>foo</p>1<p>foo</p>
<p>foo</p><p>foo</p><p>foo</p>
1<p>foo</p>1<p>foo</p>
0<p>foo</p>
</div>
"""
        self.assert_normalized(result, expected)

    def test_same_name_render(self):
        input_html = """
<@define name="FOO">
<@define name="name">foo</@define>
<@name/>
</@define>

<@define name="BOO">
<@define name="name">boo</@define>
<@name/>
</@define>

<@FOO/>
<@BOO/>
<@FOO/>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        self.assert_normalized(result, "fooboofoo")

    def test_same_name_block(self):
        input_html = """
<@define name="FOO">
<@yield name="name"/>
</@define>

<@define name="BOO">
<@yield name="name"/>
</@define>

<@FOO><@FOO.name>foo</@FOO.name></@FOO>
<@BOO><@BOO.name>boo</@BOO.name></@BOO>
<@FOO><@FOO.name>foo</@FOO.name></@FOO>
"""
        context = {}
        render = self._callFUT(input_html)
        result = render(context)
        self.assert_normalized(result, "fooboofoo")


def _normalize(html):
    lines = [x.strip() for x in html.strip().split("\n")]
    return "".join(lines).replace("</", "\n</")
