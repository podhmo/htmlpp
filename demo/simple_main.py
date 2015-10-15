# -*- coding:utf-8 -*-
from htmlpp import get_locator
import os.path
import logging
logging.basicConfig(level=logging.INFO)


here = os.path.join(os.path.abspath(os.path.dirname(__file__)))
locator = get_locator([here], outdir=here)

html = """\
<@import module="simple" alias="s"/>

<@s:box>
<p>this is the contents of a box</p>
</@s:box>
"""
print(locator.render(html))

# <div class="box">

# <p>this is the contents of a box</p>

# </div>
