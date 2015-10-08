# -*- coding:utf-8 -*-
import unittest
import evilunit
from collections import OrderedDict


@evilunit.test_function("htmlpp.utils:parse_attrs")
class ParseAttrsTests(unittest.TestCase):
    def test_simple(self):
        attr_string = """ x=y a=b """
        result = self._callFUT(attr_string)
        expected = OrderedDict([("x", "y"), ('a', 'b')])
        self.assertEqual(result, expected)

    def test_quoted(self):
        attr_string = """foo="bar" """
        result = self._callFUT(attr_string)
        expected = OrderedDict([('foo', '"bar"')])
        self.assertEqual(result, expected)

    def test_noattributes(self):
        from htmlpp.utils import _marker
        attr_string = """
        name="foo"
        {%for i in lines %}
        {{i}}
        {% endfor %}
        """
        result = self._callFUT(attr_string)
        expected = OrderedDict([
            ('name', '"foo"'),
            ('{%for i in lines %} {{i}} {% endfor %}', _marker)
        ])
        self.assertEqual(result, expected)


@evilunit.test_function("htmlpp.utils:string_from_attrs")
class StringFromAttrsTest(unittest.TestCase):
    def test_simple(self):
        attrs = OrderedDict([("x", "y"), ('a', 'b')])
        result = self._callFUT(attrs)
        expected = """ x=y a=b"""
        self.assertEqual(result, expected)

    def test_quoted(self):
        attrs = OrderedDict([('foo', '"bar"')])
        result = self._callFUT(attrs)
        expected = ' foo="bar"'
        self.assertEqual(result, expected)

    def test_noattributes(self):
        from htmlpp.utils import _marker
        attrs = OrderedDict([
            ('name', '"foo"'),
            ('{%for i in lines %} {{i}} {% endfor %}', _marker)
        ])
        result = self._callFUT(attrs)
        expected = """ name="foo" {%for i in lines %} {{i}} {% endfor %}"""
        self.assertEqual(result, expected)


@evilunit.test_function("htmlpp.utils:merge_dict")
class MergeDictTest(unittest.TestCase):
    def test_it__overwrite__empty(self):
        d0 = {}
        d1 = {"a": "b"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": "b"})

    def test_it__overwrite(self):
        d0 = {"a": "b"}
        d1 = {"a": "c"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": "c"})

    def test_it__overwrite__quoted(self):
        d0 = {"a": "b"}
        d1 = {"a": '"c"'}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": '"c"'})

    def test_it__add__empty(self):
        d0 = {}
        d1 = {"a:add": "b"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": "b"})

    def test_it__add(self):
        d0 = {"a": "b"}
        d1 = {"a:add": "c"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": "b c"})

    def test_it__add__qouted(self):
        d0 = {"a": "b"}
        d1 = {"a:add": '"c"'}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": '"b c"'})

    def test_it__add__qouted2(self):
        d0 = {"a": '"b"'}
        d1 = {"a:add": '"c"'}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": '"b c"'})

    def test_it__del__empty(self):
        d0 = {}
        d1 = {"a:del": "b"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {})

    def test_it__del(self):
        d0 = {"a": "b c"}
        d1 = {"a:del": "b"}
        self._callFUT(d0, d1)
        self.assertEqual(d0, {"a": " c"})
