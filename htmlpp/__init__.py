# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from htmlpp.lexer import Lexer  # NOQA
from htmlpp.parser import Parser  # NOQA
from htmlpp.codegen import Codegen  # NOQA
from htmlpp.loader import get_repository  # NOQA


def dump_tree(ast, indent=0, d=2, strip_empty_text=True):
    if not hasattr(ast, "children"):
        if not strip_empty_text or ast.strip():
            print("{}<text '{}'>".format(" " * indent, ast[:20].replace("\n", "\\n")))
    else:
        print("{}{}".format(" " * indent, ast))
        for child in ast.children:
            dump_tree(child, indent=indent + d, d=d)
