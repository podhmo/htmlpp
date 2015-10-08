# -*- coding:utf-8 -*-
import unittest
import evilunit


@evilunit.test_target("htmlpp.lexer:Lexer")
class LexerTests(unittest.TestCase):
    def _makeOne(self, prefix="@"):
        return self._getTarget()(prefix=prefix)

    def test_token__openclose(self):
        from htmlpp.lexer import OpenClose
        s = "<@yield/>"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], OpenClose)
        self.assertEqual(result[0].name, "yield")

    def test_token__open(self):
        from htmlpp.lexer import Open
        s = "<@def x=\"y\">"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], Open)
        self.assertEqual(result[0].name, "def")
        self.assertEqual(result[0].attrs, {'x': '"y"'})

    def test_token__close(self):
        from htmlpp.lexer import Close
        s = "</@def>"
        target = self._makeOne()
        result = target(s)
        self.assertIsInstance(result[0], Close)
        self.assertEqual(result[0].name, "def")

    def test_token__changing_default_prefix(self):
        from htmlpp.lexer import Close
        s = "</!def>"
        target = self._makeOne(prefix="!")
        result = target(s)
        self.assertIsInstance(result[0], Close)
        self.assertEqual(result[0].name, "def")

    def test_token__multiple_arguments(self):
        s = '<@box y="2" id="yours" class="hmm" x="10">'
        target = self._makeOne()
        result = target(s)
        self.assertEqual(result[0].name, "box")
        expected = {"y": '"2"', "id": '"yours"', "class": '"hmm"', "x": '"10"'}
        self.assertEqual(result[0].attrs, expected)

    def test_sentence(self):
        from htmlpp.lexer import Close, Open, OpenClose
        from htmlpp.utils import _marker
        s = """
<html><@def name="foo" {{bar|boo}} >{% for line in body %}
</@def>{%endfor}
<@yield/>
</html>
"""
        target = self._makeOne()
        result = target(s)

        # [<str>, <Open>, <str>, <Close>, <str>, <OpenClose>, <str>]
        _, open_tag, __, close_tag, _, openclose_tag, ___ = result
        self.assertIsInstance(open_tag, Open)
        self.assertEqual(open_tag.name, "def")
        self.assertEqual(open_tag.attrs, {"name": '"foo"', "{{bar|boo}}": _marker})

        self.assertIsInstance(close_tag, Close)
        self.assertEqual(close_tag.name, "def")

        self.assertIsInstance(openclose_tag, OpenClose)
        self.assertEqual(openclose_tag.name, "yield")
