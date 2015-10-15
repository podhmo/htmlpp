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

    def _makeContext(self, D):
        from htmlpp.structure import Context

        class DummyLocator:
            pass
        return Context(D, DummyLocator())

    def test_it(self):
        input_html = """
<@def name="box">
 <div class="box">
 <@yield/>
 </div>
</@def>

<@box><p>this is box</p></@box>
"""
        context = self._makeContext({})
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
<@def name="box">
<div class="box">
<@yield/>
</div>
</@def>

<@box id="myBox">hmm</@box>
<@box id="yourBox">oyoyo</@box>
"""
        context = self._makeContext({})
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="box" id="myBox">hmm</div>
<div class="box" id="yourBox">oyoyo</div>
"""
        self.assert_normalized(result, expected)

    def test_with_add_attributes(self):
        input_html = """
<@def name="box">
<div class="box" id="nobodyBox">
<@yield/>
</div>
</@def>

<@box class:add="mine" id="myBox">hmm</@box>
<@box class:add="yours" id="yourBox">oyoyo</@box>
<@box class:del="box">nobody</@box>
"""
        context = self._makeContext({})
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
<div class="box mine" id="myBox">hmm</div>
<div class="box yours" id="yourBox">oyoyo</div>
<div class="" id="nobodyBox">nobody</div>
"""
        self.assert_normalized(result, expected)

    def test_with_two_block(self):
        input_html = """
<@def name="box">
 <div class="box">
 <h1 class="heading"><@yield name="heading" /></h1>
 <@yield/>
 </div>
</@def>

<@box>
<@box.heading>this is title</@box.heading>
<p>this is box</p>
</@box>
"""
        context = self._makeContext({})
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
<@def name="twobox">
 <@def name="left">
   <div class="left">
   <@yield/>
   </div>
 </@def>
 <@def name="right">
   <div class="right">
   <@yield/>
   </div>
 </@def>
<div class="twobox">
  <@left><@yield name="left"/></@left>
  <@right><@yield name="right"/></@right>
</div>
</@def>

<@twobox>
<@twobox.left>
X
</@twobox.left>
<@twobox.right>
Y
</@twobox.right>
</@twobox>
"""
        context = self._makeContext({})
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
<@def name="nested">
<@def name="nested0">
0<@yield/>
<@nested1/>
0<@yield/>
</@def>

<@def name="nested1">
1<@yield/>
1<@yield/>
<@nested2/>
1<@yield/>
1<@yield/>
</@def>

<@def name="nested2">
<@yield/><@yield/><@yield/>
</@def>
<div class="nested"><@nested0><@yield/></@nested0></div>
</@def>

<@nested>
<p>foo</p>
</@nested>
"""
        context = self._makeContext({})
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
<@def name="nested">
  <@def name="nested0">
    <@def name="nested1">
      <@def name="nested2">
      <@yield/><@yield/><@yield/>
      </@def>
    1<@yield/>
    1<@yield/>
    <@nested2/>
    1<@yield/>
    1<@yield/>
    </@def>
  0<@yield/>
  <@nested1/>
  0<@yield/>
  </@def>
<div class="nested"><@nested0><@yield/></@nested0></div>
</@def>

<@nested>
<p>foo</p>
</@nested>
"""
        context = self._makeContext({})
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
<@def name="FOO">
<@def name="name">foo</@def>
<@name/>
</@def>

<@def name="BOO">
<@def name="name">boo</@def>
<@name/>
</@def>

<@FOO/>
<@BOO/>
<@FOO/>
"""
        context = self._makeContext({})
        render = self._callFUT(input_html)
        result = render(context)
        self.assert_normalized(result, "fooboofoo")

    def test_same_name_block(self):
        input_html = """
<@def name="FOO">
<@yield name="name"/>
</@def>

<@def name="BOO">
<@yield name="name"/>
</@def>

<@FOO><@FOO.name>foo</@FOO.name></@FOO>
<@BOO><@BOO.name>boo</@BOO.name></@BOO>
<@FOO><@FOO.name>foo</@FOO.name></@FOO>
"""
        context = self._makeContext({})
        render = self._callFUT(input_html)
        result = render(context)
        self.assert_normalized(result, "fooboofoo")

    def test_with_condition(self):
        input_html = """
<@def name="a">
{% if <@yield name="condition"/> %}
 <a><@yield/></a>
{% else %}
<p>oops</p>
{% endif %}
</@def>

<@a href="#"><@a.condition>xs</@a.condition><i class="icon-scope"/>find</@a>
<@a href="#" :condition="xs"><i class="icon-scope"/>find</@a>
"""
        context = self._makeContext({})
        render = self._callFUT(input_html)
        result = render(context)
        expected = """
{% if xs %}
 <a href="#"><i class="icon-scope"/>find</a>
{% else %}
<p>oops</p>
{% endif %}
{% if xs %}
 <a href="#"><i class="icon-scope"/>find</a>
{% else %}
<p>oops</p>
{% endif %}
"""
        self.assert_normalized(result, expected)


def _normalize(html):
    lines = [x.strip() for x in html.strip().split("\n")]
    return "".join(lines).replace("</", "\n</")
