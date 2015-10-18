# -*- coding:utf-8 -*-
from functools import partial
import os.path
import tempfile
import shutil
import logging
from importlib import machinery

from .structure import Context
from .exceptions import NotFound
from .utils import Gensym
from .lexer import Lexer
from .parser import Parser
from .codegen import Codegen

logger = logging.getLogger(__name__)

TMPDIR = object()


def compile_module(module_id, code, tmpdir=None, suffix=".py"):
    tmpdir = tmpdir or tempfile.gettempdir()
    logger.debug("compiled code:\n%s", code)
    fd, path = tempfile.mkstemp()
    os.write(fd, code.encode("utf-8"))
    dst = os.path.join(tmpdir, module_id) + suffix
    logger.info("generated module file: %s", dst)
    shutil.move(path, dst)
    return dst


def load_module(module_id, path):
    return machinery.SourceFileLoader(module_id, path).load_module()


def get_locator(directories, outdir=None, ext=".pre.html"):
    # TODO: include also sys.site_packages?
    transpiler = ModuleTranspiler(tmpdir=outdir)
    return FileSystemModuleLocator(directories, transpiler, ext=ext)


class ModuleTranspiler(object):
    def __init__(self, tmpdir=None):
        self.lexer = Lexer()
        self.parser = Parser()
        self.codegen = Codegen()
        self.tmpdir = tmpdir
        self.gensym = Gensym()

    def load(self, module_id, path):
        return load_module(module_id, path)

    def __call__(self, filepath, module_id, tmpdir=TMPDIR):
        with open(filepath) as rf:
            return self.transpile(rf.read(), module_id, tmpdir=tmpdir)

    def emit(self, html):
        return self.codegen(self.parser(self.lexer(html)))

    def transpile(self, html, module_id=None, tmpdir=TMPDIR):
        module_id = module_id or self.gensym("_htmlpp_internal")
        code = self.emit(html)
        if tmpdir is TMPDIR:
            tmpdir = self.tmpdir
        path = compile_module(module_id, code, tmpdir=tmpdir)
        return self.load(module_id, path)


class FileSystemModuleLocator(object):
    def __init__(self, directoires, transpiler=None, ext=".pre.html"):
        self.directoires = directoires
        self.cache = {}
        self.ext = ext.lstrip(".")
        self.transpiler = transpiler or ModuleTranspiler()

    def create_context(self):
        return Context({}, self)

    def get_path_name(self, module_name):
        prefix = module_name.replace(".", "/")
        return "{}.{}".format(prefix.rstrip("."), self.ext)

    def from_module_name(self, module_name):
        path_name = self.get_path_name(module_name)
        for d in self.directoires:
            fullpath = os.path.join(d, path_name)
            if os.path.exists(fullpath):
                return self.transpiler(fullpath, module_name)
        raise NotFound(module_name)
    __call__ = from_module_name

    def from_string(self, template, tmpdir=TMPDIR):
        module = self.transpiler.transpile(template, tmpdir=tmpdir)
        module.context = self.create_context()
        module.getvalue = partial(module.render, module.context)
        return module

    def render(self, template):
        return self.from_string(template, tmpdir=None).getvalue()
