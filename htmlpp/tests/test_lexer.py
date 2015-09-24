# -*- coding:utf-8 -*-
import unittest
import evilunit


@evilunit.test_target("htmlpp:Lexer")
class LexerTests(unittest.TestCase):
    def _makeOne(self, prefix="@"):
        return self._getTarget()(prefix=prefix)

    def test_token0(self):
        from htmlpp import OpenClose
        s = "<@yield/>"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], OpenClose)
        self.assertEqual(result[0].name, "yield")

    def test_token1(self):
        from htmlpp import Open
        s = "<@define x=y>"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], Open)
        self.assertEqual(result[0].name, "define")

    def test_token2(self):
        from htmlpp import Close
        s = "</@define>"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], Close)
        self.assertEqual(result[0].name, "define")

    def test_token__default_prefix(self):
        from htmlpp import Close
        s = "</!define>"
        target = self._makeOne(prefix="!")
        result = target(s)
        self.assertIsInstance(result[0], Close)
        self.assertEqual(result[0].name, "define")

    def test_sentence(self):
        from htmlpp import Close, Open, OpenClose
        s = """
<html><@define foo {{bar|boo}} >{% for line in body %}
</@define>{%endfor}
<@yield/>
</html>
"""
        target = self._makeOne()
        result = target(s)

        # [<str>, <Open>, <str>, <Close>, <str>, <OpenClose>, <str>]
        _, open_tag, __, close_tag, _, openclose_tag, ___ = result
        self.assertIsInstance(open_tag, Open)
        self.assertEqual(open_tag.name, "define")

        self.assertIsInstance(close_tag, Close)
        self.assertEqual(close_tag.name, "define")

        self.assertIsInstance(openclose_tag, OpenClose)
        self.assertEqual(openclose_tag.name, "yield")
