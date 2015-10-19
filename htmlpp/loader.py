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
    pathname = module_id.replace(".", "/")
    if "." in module_id:
        dirpath = os.path.dirname(os.path.join(outdir, pathname)).rstrip("/")
        logger.info("generated directory: %s", dirpath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        # __init__.py
        outdir = outdir.rstrip("/")
        while dirpath != outdir:
            initpath = os.path.join(dirpath, "__init__.py")
            if not os.path.exists(initpath):
                logger.info("generated __init__: %s", initpath)
                open(initpath, "a").close()
            dirpath = dirpath.rsplit("/", 1)[0]
    dst = os.path.join(outdir, pathname) + suffix
    logger.info("generated file: %s", dst)
    shutil.move(path, dst)
    return dst


def load_module(module_id, path):
    return machinery.SourceFileLoader(module_id, path).load_module()


def get_repository(directories, outdir=None, ext=".pre.html"):
    # TODO: include also sys.site_packages?
    if outdir is None:
        outdir = tempfile.gettempdir()
    transpiler = ModuleTranspiler(outdir=outdir)
    repository = FileSystemModuleRepository(directories, transpiler, ext=ext)
    repository = SysPathImportRepositoryWrapper(repository, outdir=outdir)
    return repository


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


class UseChildRepository(object):
    def __contains__(self, module_name):
        return module_name in self.repository

    def __getitem__(self, module_name):
        return self.repository[module_name]

    def __setitem__(self, module_name, module):
        self.repository[module_name] = module


class SysPathImportRepositoryWrapper(UseChildRepository):
    def __init__(self, repository, outdir=None, file_check=True):
        self.repository = repository
        self.outdir = outdir
        self.file_check = file_check
        # side effect!!
        if outdir is not None and outdir not in sys.path:
            logger.info(os.path.abspath(outdir))
            sys.path.append(os.path.abspath(outdir))

    def create_context(self):
        return Context({}, self)

    def from_module_name(self, module_name):
        if module_name in self.repository:
            return self.repository[module_name]
        target_file_path = None
        try:
            module = import_module(module_name)
            if self.file_check:
                target_file_path = self.repository.lookup_target_file_path(module_name)
                if module._HTMLPP_MTIME <= os.stat(target_file_path).st_mtime:
                    raise ImportError(module_name)
            self.repository[module_name] = module
            return module
        except ImportError:
            logger.info("import error: %s", module_name)
            return self.repository.from_module_name(module_name, fullpath=target_file_path)

    __call__ = from_module_name

    def from_string(self, template, outdir=OUTDIR, context=None):
        context = context or self.create_context()
        outdir = outdir if outdir is not OUTDIR else self.outdir
        return self.repository.from_string(template, outdir=outdir, context=context)

    def render(self, template):
        return self.from_string(template, outdir=None).getvalue()

    def clean(self):
        self.repository.clean()


class FileSystemModuleRepository(UseChildRepository):
    def __init__(self, directoires, transpiler, ext=".pre.html"):
        self.directoires = directoires
        self.repository = {}
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
        if module_name in self.repository:
            return self.repository[module_name]

        fullpath = fullpath or self.lookup_target_file_path(module_name)
        if fullpath is None:
            raise NotFound(module_name)
        module = self.transpiler(fullpath, module_name)
        self.repository[module_name] = module
        return module

    __call__ = from_module_name

    def from_string(self, template, outdir=OUTDIR, context=None):
        module = self.transpiler.transpile(template, outdir=outdir)
        module.context = context or self.create_context()
        module.getvalue = partial(module.render, module.context)
        return module

    def render(self, template):
        return self.from_string(template, outdir=None).getvalue()

    def clean(self):
        self.repository = {}
