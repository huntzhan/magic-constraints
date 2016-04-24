# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import types
from abc import ABCMeta


class CompoundArgument(object):
    pass


class AttributesBinder(object):

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, attr, val):
        setattr(self.obj, attr, val)


def type_object(obj):
    return hasattr(obj, '__bases__')


def nontype_object(obj):
    return not type_object(obj)


def raise_on_non_function(function):
    if not isinstance(function, types.FunctionType):
        raise MagicTypeError(
            'require FunctionType.',
            function=function,
        )


def raise_on_nontype_object(obj):
    if nontype_object(obj):
        raise MagicTypeError(
            'require type object.',
            obj=obj,
        )


def repr_return(text):
    if sys.version_info.major == 2:  # pragma: no cover
        text = text.encode('utf-8')
    return text


def conditional_repr(obj):
    if isinstance(obj, ABCMeta) and hasattr(obj, 'main_cls'):
        return repr(obj)
    elif type_object(obj):
        return obj.__name__
    else:
        return repr(obj)


from magic_constraints.exception import (
    # MagicSyntaxError,
    MagicTypeError,
)  # noqa
