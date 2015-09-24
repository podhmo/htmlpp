# -*- coding:utf-8 -*-
import unittest
import evilunit


@evilunit.test_target("htmlpp:Parser")
class ParserTests(unittest.TestCase):
    def test_yield__openclose(self):
        from htmlpp import OpenClose
        from htmlpp import Yield
        tokens = [OpenClose("yield", {})]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 1)
        self.assertIsInstance(ast.children[0], Yield)

    def test_command__openclose(self):
        from htmlpp import OpenClose
        from htmlpp import Command
        tokens = [OpenClose("hmm", {})]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 1)
        self.assertIsInstance(ast.children[0], Command)

    def test_define__with_nested(self):
        # <@define name="foo">
        #   <@yield/>
        #   <@define name="bar">
        #     <@yield/>
        #     <@define name="boo">
        #     </@define>
        #     <@yield/>
        #   </@define>
        #   <@yield/>
        # </@define>
        # <@foo/>

        # convert to:

        # define:foo
        #   yield
        #   define:bar
        #     yield
        #     define:boo
        #     yield
        #   yield
        # foo

        from htmlpp import OpenClose, Open, Close
        tokens = [
            Open("define", {"name": "foo"}),
            OpenClose("yield", {}),
            Open("define", {"name": "bar"}),
            OpenClose("yield", {}),
            Open("define", {"name": "boo"}),
            Close("define"),
            OpenClose("yield", {}),
            Close("define"),
            OpenClose("yield", {}),
            Close("define"),
            OpenClose("foo", {}),
        ]
        target = self._makeOne()
        ast = target(tokens)
        self.assertEqual(len(ast.children), 2)
        self.assertEqual(len(ast.children[0].children), 3)
        self.assertEqual(len(ast.children[0].children[1].children), 3)
