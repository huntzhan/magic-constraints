# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import collections as abc


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


def raise_on_non_callable(callable_):
    if not isinstance(callable_, abc.Callable):
        raise MagicTypeError(
            'require Callable.',
            callable_=callable_,
        )


def raise_on_nontype_object(obj):
    if nontype_object(obj):
        raise MagicTypeError(
            'require type object.',
            obj=obj,
        )


def conditional_to_bytes(text):
    if sys.version_info.major == 2:  # pragma: no cover
        text = text.encode('utf-8')
    return text


def conditional_repr(obj):
    if type_object(obj):
        if issubclass(obj, BasicMagicType):
            return repr(obj)
        else:
            return obj.__name__

    elif isinstance(obj, (list, tuple)):
        return '[{}]'.format(
            ', '.join(map(conditional_repr, obj)),
        )

    else:
        return repr(obj)


def return_true(*args, **kwargs):
    return True


from magic_constraints.exception import (
    MagicTypeError,
)  # noqa
from magic_constraints.types import (
    BasicMagicType,
)  # noqa
