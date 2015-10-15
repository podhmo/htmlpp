# -*- coding:utf-8 -*-
import unittest
import evilunit


@evilunit.test_target("htmlpp.parser:Parser")
class ParserTests(unittest.TestCase):
    def test_yield__openclose(self):
        from htmlpp.lexer import OpenClose
        from htmlpp.nodes import Yield
        tokens = [OpenClose("yield", {})]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 1)
        self.assertIsInstance(ast.children[0], Yield)

    def test_command__openclose(self):
        from htmlpp.lexer import OpenClose
        from htmlpp.nodes import Command
        tokens = [OpenClose("hmm", {})]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 1)
        self.assertIsInstance(ast.children[0], Command)

    def test_with_shortcut_blocknode_expression(self):
        from htmlpp.lexer import OpenClose
        from htmlpp.nodes import Block
        tokens = [OpenClose("box", {":title": "hmm"})]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(len(ast.children[0].children), 1)
        self.assertIsInstance(ast.children[0].children[0], Block)

    def test_def__with_nested(self):
        # <@def name="foo">
        #   <@yield/>
        #   <@def name="bar">
        #     <@yield/>
        #     <@def name="boo">
        #     </@def>
        #     <@yield/>
        #   </@def>
        #   <@yield/>
        # </@def>
        # <@foo/>

        # convert to:

        # def:foo
        #   yield
        #   def:bar
        #     yield
        #     def:boo
        #     yield
        #   yield
        # foo

        from htmlpp.lexer import OpenClose, Open, Close
        tokens = [
            Open("def", {"name": "foo"}),
            OpenClose("yield", {}),
            Open("def", {"name": "bar"}),
            OpenClose("yield", {}),
            Open("def", {"name": "boo"}),
            Close("def"),
            OpenClose("yield", {}),
            Close("def"),
            OpenClose("yield", {}),
            Close("def"),
            OpenClose("foo", {}),
        ]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 2)
        self.assertEqual(len(ast.children[0].children), 3)
        self.assertEqual(len(ast.children[0].children[1].children), 3)
