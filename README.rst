.. image:: https://travis-ci.org/podhmo/htmlpp.svg
  :target: https://travis-ci.org/podhmo/htmlpp.svg

htmlpp
========================================

simple.pre.html

.. code-block:: html

  <@def name="box">
  <div class="box">
    <@yield/>
  </div>
  </@def>


code

.. code-block:: python

  # -*- coding:utf-8 -*-
  from htmlpp import get_locator
  import os.path


  here = os.path.join(os.path.abspath(os.path.dirname(__file__)))
  locator = get_locator([here], outdir=here)

  html = """\
  <@import module="simple" alias="s"/>

  <@s:box>
  <p>this is the contents of a box</p>
  </@s:box>
  """
  print(locator.render(html))


output

::

  <div class="box">

  <p>this is the contents of a box</p>

  </div>

TODO: gentle introduction.
