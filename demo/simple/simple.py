import pickle
from collections import OrderedDict
from htmlpp.utils import string_from_attrs, merge_dict
from htmlpp.codegen import render_with


_HTMLPP_MTIME = 1445271428.144295


def render_box(_writer, _context, _kwargs, _default_attributes=pickle.loads(b'\x80\x03ccollections\nOrderedDict\nq\x00]q\x01]q\x02(X\x05\x00\x00\x00classq\x03X\x05\x00\x00\x00"box"q\x04ea\x85q\x05Rq\x06.')):

    # _default_attributes :: OrderedDict([('class', '"box"')])
    _writer('\n')
    D = OrderedDict()
    merge_dict(D, _default_attributes)
    if '_attributes' in _kwargs:
        merge_dict(D, _kwargs['_attributes'])
    _writer('<div')
    _writer(string_from_attrs(D))
    _writer('>\n  ')
    _kwargs["block_body"](_writer, _context)
    _writer('\n')
    _writer('</div>\n')


def setup(_context):
    pass


def render_(_writer, _context, _kwargs, _default_attributes={}):
    pass


def render(_context, _writer=None):
    setup(_context)
    return render_with(render_, _context, _writer=_writer)