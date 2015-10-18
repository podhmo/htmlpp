# -*- coding:utf-8 -*-
from htmlpp.lexer import Lexer  # NOQA
from htmlpp.parser import Parser  # NOQA
from htmlpp.codegen import Codegen  # NOQA


if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()
    s = """
<@def name="foo">
<div class="foo">
<@yield/>
<@def name="bar">
  <div class="bar">
  <@yield/>
  <@def name="boo">
    <div class="boo"/>
  </@def>
  <@boo/>
  <@yield/>
  </div>
</@def>
<@bar/>
<@yield/>
</div>

</@def>

    <@foo>
    <div>test</div>
    </@foo>
    <@foo>
    <div>test2</div>
    </@foo>
    """
    s = """
<@def name="box">
<div class="box">
  <div class="wrapper"><@yield/></div>
</div>
</@def>
<@def name="box2">
<div>
  <div class="wrapper"><@yield/></div>
</div>
</@def>

<@box id="mine">
  <p>hmm.</p>
</@box>
<@box y="2" id="yours" class="hmm" x="10">
  <p>hmm.</p>
</@box>
"""
    tokens = lexer(s)
    ast = parser(tokens)
    # dump_tree(ast)
    codegen = Codegen()
    # print(codegen(ast))
    # exec(codegen(ast))
    # print(render({}))
