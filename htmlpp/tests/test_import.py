# -*- coding:utf-8 -*-
import unittest
import os
import contextlib


here = os.path.abspath(os.path.dirname(__file__))


@contextlib.contextmanager
def assert_switch_off_to_on(self, fn):
    self.assertFalse(fn())
    yield
    self.assertTrue(fn())


class GeneratingModuleTests(unittest.TestCase):
    def _makeOne(self, directories, outdir):
        from htmlpp.loader import get_repository
        return get_repository(directories, outdir=outdir)

    def setUp(self):
        self.datadir = os.path.join(here, "data")
        self.path = os.path.join(self.datadir, "box.py")
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_generate_module_by_loading(self):
        with assert_switch_off_to_on(self, lambda: os.path.exists(self.path)):
            repository = self._makeOne([self.datadir], outdir=self.datadir)
            m = repository("box")
            self.assertTrue(m.__file__, self.path)

    def test_not_generate_module_by_loading__outdir_is_None(self):
        with self.assertRaises(AssertionError):
            with assert_switch_off_to_on(self, lambda: os.path.exists(self.path)):
                repository = self._makeOne([self.datadir], outdir=None)
                repository("box")

    @unittest.skip("TODO")
    def test_loading_is_cached(self):
        pass


class UsingExternalModuleTests(unittest.TestCase):
    def _makeOne(self, directories, outdir):
        from htmlpp.loader import get_repository
        return get_repository(directories, outdir=outdir)

    def setUp(self):
        self.datadir = os.path.join(here, "data")

    def test_render_self(self):
        repository = self._makeOne([self.datadir], None)
        html = """\
<@def name="this_is_external_module">
<div class="hmm"><@yield/></div>
</@def>
<@this_is_external_module>hai</@this_is_external_module>
"""
        result = repository.render(html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')

    def test_render_with_external_module(self):
        repository = self._makeOne([self.datadir], None)
        with open(os.path.join(self.datadir, "this_is_external_module.pre.html"), "w") as wf:
            html = """\
<@def name="this_is_external_module">
<div class="hmm"><@yield/></div>
</@def>
"""
            wf.write(html)
        module = repository.from_module_name("this_is_external_module")
        self.assertTrue(module.__name__.endswith("this_is_external_module"))

        main_html = """\
<@import module="this_is_external_module"/>
<@this_is_external_module:this_is_external_module>hai</@this_is_external_module:this_is_external_module>
"""
        result = repository.render(main_html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')

    def test_render_with_external_module2(self):
        repository = self._makeOne([self.datadir], None)
        with open(os.path.join(self.datadir, "alpha.pre.html"), "w") as wf:
            html = """\
<@def name="one">
<div class="one"><@yield/></div>
</@def>
"""
            wf.write(html)
        with open(os.path.join(self.datadir, "beta.pre.html"), "w") as wf:
            html = """\
<@import module="alpha"/>
<@def name="two">
<@alpha:one><div class="two"><@yield/></div></@alpha:one>
</@def>
"""
            wf.write(html)

        main_html = """\
<@import module="beta"/>
<@beta:two>hmm</@beta:two>
"""

        result = repository.render(main_html)
        expected = '<div class="one"><div class="two">hmm</div></div>'
        self.assertEqual(result.strip(), expected)

    def test_render_with_nexted_external_module(self):
        repository = self._makeOne([self.datadir], None)
        with open(os.path.join(self.datadir, "_htmlpp_nested/this_is_external_module.pre.html"), "w") as wf:
            html = """\
<@def name="this_is_external_module">
<div class="hmm"><@yield/></div>
</@def>
"""
            wf.write(html)
        module = repository.from_module_name("this_is_external_module")
        self.assertTrue(module.__name__.endswith("this_is_external_module"))

        main_html = """\
<@import module="_htmlpp_nested.this_is_external_module"/>
<@_htmlpp_nested.this_is_external_module:this_is_external_module>hai</@_htmlpp_nestedthis_is_external_module:this_is_external_module>
"""
        result = repository.render(main_html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')

    def test_render_with_nexted_external_module__alias(self):
        repository = self._makeOne([self.datadir], None)
        with open(os.path.join(self.datadir, "_htmlpp_nested/this_is_external_module.pre.html"), "w") as wf:
            html = """\
<@def name="this_is_external_module">
<div class="hmm"><@yield/></div>
</@def>
"""
            wf.write(html)
        module = repository.from_module_name("this_is_external_module")
        self.assertTrue(module.__name__.endswith("this_is_external_module"))

        main_html = """\
<@import module="_htmlpp_nested.this_is_external_module" alias="m"/>
<@m:this_is_external_module>hai</@m:this_is_external_module>
"""
        result = repository.render(main_html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')


class UsingExternalPythonModuleTests(unittest.TestCase):
    def _makeOne(self, directories, outdir=None):
        from htmlpp.loader import get_repository
        return get_repository(directories, outdir=outdir)

    def test_it(self):
        repository = self._makeOne(["."], None)
        html = """\
<@pyimport module="htmlpp.utils"/>
<@htmlpp.utils:hello/>
"""
        result = repository.render(html)
        self.assertEqual(result.strip(), 'hello')

    def test_it_with_alias(self):
        repository = self._makeOne(["."], None)
        html = """\
<@pyimport module="htmlpp.utils" alias="u"/>
<@u:hello/>
"""
        result = repository.render(html)
        self.assertEqual(result.strip(), 'hello')
