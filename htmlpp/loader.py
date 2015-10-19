# -*- coding:utf-8 -*-
import sys
from functools import partial
import os.path
import tempfile
import shutil
import logging
from importlib import machinery, import_module

from .structure import Context
from .exceptions import NotFound
from .utils import Gensym
from .lexer import Lexer
from .parser import Parser
from .codegen import Codegen

logger = logging.getLogger(__name__)

OUTDIR = object()


def compile_module(module_id, code, outdir=None, suffix=".py"):
    outdir = outdir or tempfile.gettempdir()
    logger.debug("compiled code:\n%s", code)
    fd, path = tempfile.mkstemp()
    os.write(fd, code.encode("utf-8"))
    dst = os.path.join(outdir, module_id) + suffix
    logger.info("generated module file: %s", dst)
    shutil.move(path, dst)
    return dst


def load_module(module_id, path):
    return machinery.SourceFileLoader(module_id, path).load_module()


def get_locator(directories, outdir=None, ext=".pre.html"):
    # TODO: include also sys.site_packages?
    transpiler = ModuleTranspiler(outdir=outdir)
    locator = FileSystemModuleLocator(directories, transpiler, ext=ext)
    if outdir is None:
        outdir = tempfile.gettempdir()
    locator = SysPathImportLocatorWrapper(locator, outdir=outdir)
    return locator


class ModuleTranspiler(object):
    def __init__(self, outdir=None):
        self.lexer = Lexer()
        self.parser = Parser()
        self.codegen = Codegen()
        self.outdir = outdir
        self.gensym = Gensym()

    def load(self, module_id, path):
        return load_module(module_id, path)

    def __call__(self, filepath, module_id, outdir=OUTDIR):
        with open(filepath) as rf:
            return self.transpile(rf.read(), module_id, outdir=outdir)

    def emit(self, html):
        return self.codegen(self.parser(self.lexer(html)))

    def transpile(self, html, module_id=None, outdir=OUTDIR):
        module_id = module_id or self.gensym("_htmlpp_internal")
        code = self.emit(html)
        if outdir is OUTDIR:
            outdir = self.outdir
        path = compile_module(module_id, code, outdir=outdir)
        return self.load(module_id, path)


class SysPathImportLocatorWrapper(object):
    def __init__(self, locator, outdir=None, file_check=True):
        self.locator = locator
        self.outdir = outdir
        self.file_check = file_check
        # side effect!!
        if outdir is not None and outdir not in sys.path:
            sys.path.append(os.path.abspath(outdir))

    def from_module_name(self, module_name):
        if module_name in self.locator:
            return self.locator[module_name]
        target_file_path = None
        try:
            module = import_module(module_name)
            if self.file_check:
                target_file_path = self.locator.lookup_target_file_path(module_name)
                if module._HTMLPP_MTIME <= os.stat(target_file_path).st_mtime:
                    raise ImportError(module_name)
            self.locator[module_name] = module
            return module
        except ImportError:
            return self.locator.from_module_name(module_name, fullpath=target_file_path)

    __call__ = from_module_name

    def from_string(self, template):
        return self.locator.from_string(template, outdir=self.outdir or OUTDIR)

    def render(self, template):
        return self.locator.render(template)

    def clean(self):
        self.locator.clean()

    def __contains__(self, module_name):
        return module_name in self.locator

    def __getitem__(self, module_name):
        return self.locator[module_name]

    def __setitem__(self, module_name, module):
        self.locator[module_name] = module


class FileSystemModuleLocator(object):
    def __init__(self, directoires, transpiler, ext=".pre.html"):
        self.directoires = directoires
        self.cache = {}
        self.ext = ext.lstrip(".")
        self.transpiler = transpiler

    def create_context(self):
        return Context({}, self)

    def get_path_name(self, module_name):
        prefix = module_name.replace(".", "/")
        return "{}.{}".format(prefix.rstrip("."), self.ext)

    def lookup_target_file_path(self, module_name):
        path_name = self.get_path_name(module_name)
        for d in self.directoires:
            fullpath = os.path.join(d, path_name)
            if os.path.exists(fullpath):
                return fullpath
        return None

    def from_module_name(self, module_name, fullpath=None):
        if module_name in self.cache:
            return self.cache[module_name]

        fullpath = fullpath or self.lookup_target_file_path(module_name)
        if fullpath is None:
            raise NotFound(module_name)
        module = self.transpiler(fullpath, module_name)
        self.cache[module_name] = module
        return module

    __call__ = from_module_name

    def from_string(self, template, outdir=OUTDIR):
        module = self.transpiler.transpile(template, outdir=outdir)
        module.context = self.create_context()
        module.getvalue = partial(module.render, module.context)
        return module

    def render(self, template):
        return self.from_string(template, outdir=None).getvalue()

    def clean(self):
        self.cache = {}

    def __contains__(self, module_name):
        return module_name in self.cache

    def __getitem__(self, module_name):
        return self.cache[module_name]

    def __setitem__(self, module_name, module):
        self.cache[module_name] = module
