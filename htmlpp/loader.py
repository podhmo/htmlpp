# -*- coding:utf-8 -*-
import os.path
import tempfile
import shutil
import logging
from importlib import machinery

from .exceptions import NotFound
from htmlpp.lexer import Lexer
from htmlpp.parser import Parser
from htmlpp.codegen import Codegen

logger = logging.getLogger(__name__)


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


class ModuleLoader(object):
    def __init__(self, namespace=None, tmpdir=None):
        self.lexer = Lexer()
        self.parser = Parser()
        self.codegen = Codegen()
        self.namespace = namespace
        self.tmpdir = tmpdir

    def full_module_id_of(self, module_id):
        if self.namespace:
            return "{}.{}".format(self.namespace.rstrip("."), module_id.lstrip("."))
        return module_id

    def compile(self, module_id, code):
        return compile_module(module_id, code, tmpdir=self.tmpdir)

    def load(self, module_id, path):
        module_id = self.full_module_id_of(module_id)
        return load_module(module_id, path)

    def __call__(self, module_id, filename):
        with open(filename) as rf:
            code = self.codegen(self.parser(self.lexer(rf.read())))
        path = self.compile(module_id, code)
        return self.load(module_id, path)


class FileSystemModuleLocator(object):
    def __init__(self, directoires, loader=None, ext=".pre.html"):
        self.directoires = directoires
        self.cache = {}
        self.ext = ext.lstrip(".")
        self.loader = loader or ModuleLoader()

    def __call__(self, module_name):
        path_name = self.get_path_name(module_name)
        for d in self.directoires:
            fullpath = os.path.join(d, path_name)
            if os.path.exists(fullpath):
                return self.loader(module_name, fullpath)
        raise NotFound(module_name)

    def get_path_name(self, module_name):
        prefix = module_name.replace(".", "/")
        return "{}.{}".format(prefix.rstrip("."), self.ext)
