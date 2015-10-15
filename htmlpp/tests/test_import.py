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
        from htmlpp.loader import get_locator
        return get_locator(directories, outdir=outdir)

    def setUp(self):
        self.datadir = os.path.join(here, "data")
        self.path = os.path.join(self.datadir, "box.py")
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_generate_module_by_loading(self):
        with assert_switch_off_to_on(self, lambda: os.path.exists(self.path)):
            locator = self._makeOne([self.datadir], outdir=self.datadir)
            m = locator("box")
            self.assertTrue(m.__file__, self.path)

    def test_not_generate_module_by_loading__outdir_is_None(self):
        with self.assertRaises(AssertionError):
            with assert_switch_off_to_on(self, lambda: os.path.exists(self.path)):
                locator = self._makeOne([self.datadir], outdir=None)
                locator("box")

    @unittest.skip("TODO")
    def test_loading_is_cached(self):
        pass


class UsingExternalModuleTests(unittest.TestCase):
    def _makeOne(self, directories, outdir):
        from htmlpp.loader import get_locator
        return get_locator(directories, outdir=outdir)

    def setUp(self):
        self.datadir = os.path.join(here, "data")

    def test_render_self(self):
        locator = self._makeOne([self.datadir], None)
        html = """\
<@def name="hmm">
<div class="hmm"><@yield/></div>
</@def>
<@hmm>hai</@hmm>
"""
        result = locator.render(html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')

    def test_render_with_external_module(self):
        locator = self._makeOne([self.datadir], None)
        with open(os.path.join(self.datadir, "hmm.pre.html"), "w") as wf:
            html = """\
<@def name="hmm">
<div class="hmm"><@yield/></div>
</@def>
"""
            wf.write(html)
        module = locator.from_module_name("hmm")
        self.assertTrue(module.__name__.endswith("hmm"))

        main_html = """\
<@import module="hmm"/>
<@hmm:hmm>hai</@hmm:hmm>
"""
        result = locator.render(main_html)
        self.assertEqual(result.strip(), '<div class="hmm">hai</div>')
