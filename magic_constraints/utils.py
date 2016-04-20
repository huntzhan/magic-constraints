# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa


def type_object(obj):
    return hasattr(obj, '__bases__')


def nontype_object(obj):
    return not type_object(obj)


class MagicArguments(object):
    pass
