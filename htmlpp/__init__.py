# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from htmlpp.lexer import Lexer
from htmlpp.parser import Parser
from htmlpp.codegen import Codegen
from htmlpp.loader import FileSystemModuleLocator, ModuleLoader


def dump_tree(ast, indent=0, d=2, strip_empty_text=True):
    if not hasattr(ast, "children"):
        if not strip_empty_text or ast.strip():
            print("{}<text '{}'>".format(" " * indent, ast[:20].replace("\n", "\\n")))
    else:
        print("{}{}".format(" " * indent, ast))
        for child in ast.children:
            dump_tree(child, indent=indent + d, d=d)


def get_locator(directories, outdir=None, namespace="htmlpp.", ext=".pre.html"):
    # TODO: include also sys.site_packages?
    loader = ModuleLoader(namespace=namespace, tmpdir=outdir)
    return FileSystemModuleLocator(directories, loader, ext=ext)


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
    # namespace
