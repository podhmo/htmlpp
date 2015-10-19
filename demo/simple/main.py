# -*- coding:utf-8 -*-
from htmlpp import get_repository
import os.path
import logging
logging.basicConfig(level=logging.INFO)


here = os.path.join(os.path.abspath(os.path.dirname(__file__)))
repository = get_repository([here], outdir=here)

html = """\
<@import module="simple" alias="s"/>

<@s:box>
<p>this is the contents of a box</p>
</@s:box>
"""
print(repository.render(html))

# <div class="box">

# <p>this is the contents of a box</p>

# </div>
