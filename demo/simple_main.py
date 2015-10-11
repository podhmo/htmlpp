# -*- coding:utf-8 -*-
from htmlpp import get_locator
import os.path
import logging
logging.basicConfig(level=logging.INFO)


here = os.path.join(os.path.abspath(os.path.dirname(__file__)))
locator = get_locator([here], outdir=here, namespace="demo")
simple = locator("simple")

import sys
assert simple == sys.modules["demo.simple"]
