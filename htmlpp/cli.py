# -*- coding:utf-8 -*-
import os
import sys
import argparse


def codegen(args):
    import fileinput
    from htmlpp.loader import ModuleTranspiler
    transpiler = ModuleTranspiler()
    with fileinput.FileInput(args.files) as rf:
        print(transpiler.emit(u"".join(list(rf))))


def main(sys_args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()

    codegen_parser = sub_parsers.add_parser("codegen")
    codegen_parser.add_argument("files", nargs="*")
    codegen_parser.set_defaults(func=codegen)
    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)
