# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from htmlpp.lexer import Lexer
from htmlpp.parser import Parser
from htmlpp.codegen import Codegen


def dump_tree(ast, indent=0, d=2, strip_empty_text=True):
    if not hasattr(ast, "children"):
        if not strip_empty_text or ast.strip():
            print("{}<text '{}'>".format(" " * indent, ast[:20].replace("\n", "\\n")))
    else:
        print("{}{}".format(" " * indent, ast))
        for child in ast.children:
            dump_tree(child, indent=indent + d, d=d)


if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()
    s = """
<@define name="foo">
<div class="foo">
<@yield/>
<@define name="bar">
  <div class="bar">
  <@yield/>
  <@define name="boo">
    <div class="boo"/>
  </@define>
  <@boo/>
  <@yield/>
  </div>
</@define>
<@bar/>
<@yield/>
</div>
</@define>

    <@foo>
    <div>test</div>
    </@foo>
    <@foo>
    <div>test2</div>
    </@foo>
    """
    tokens = lexer(s)
    ast = parser(tokens)
    # dump_tree(ast)
    codegen = Codegen()
    print(codegen(ast))
    exec(codegen(ast))
    print(render({}))
