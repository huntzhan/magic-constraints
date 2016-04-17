# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_parameter.decorator import (
    function_parameter,
    method_parameter,
    method_init_parameter,
    class_init_parameter,
)
from magic_parameter.type_declaration import (
    list_t,
    tuple_t,
    set_t,
    dict_t,
    or_t,
)


__all__ = [
    'function_parameter',
    'method_parameter',
    'method_init_parameter',
    'class_init_parameter',

    'list_t',
    'tuple_t',
    'set_t',
    'dict_t',
    'or_t',
]
