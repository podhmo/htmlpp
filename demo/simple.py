import pickle
from collections import OrderedDict
from htmlpp.utils import string_from_attrs, merge_dict, render_with


def render_box(_writer, _context, _kwargs, _default_attributes=pickle.loads(b'\x80\x03ccollections\nOrderedDict\nq\x00]q\x01]q\x02(X\x05\x00\x00\x00classq\x03X\x05\x00\x00\x00"box"q\x04ea\x85q\x05Rq\x06.')):

    # _default_attributes :: OrderedDict([('class', '"box"')])
    _writer('\n')
    D = OrderedDict()
    merge_dict(D, _default_attributes)
    if '_attributes' in _kwargs:
        merge_dict(D, _kwargs['_attributes'])
    _writer('<div{attrs}>\n  '.format(attrs=string_from_attrs(D)))
    _kwargs["block_body"](_writer, _context)
    _writer('\n')
    _writer('</div>\n')


def render_(_writer, _context, _kwargs, _default_attributes={}):
    pass


def render(_context, _writer=None):
    return render_with(render_, _context, _writer=_writer)