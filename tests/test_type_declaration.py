# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

# import pytest
from magic_parameter.type_declaration import *  # noqa


class UserDefined(object):
    pass


def test_type_obj():
    type_decl_factory(list)
    type_decl_factory(int)
    type_decl_factory(UserDefined)


def test_nontype_obj():
    type_decl_factory(
        list_t(int),
    )
    type_decl_factory(
        tuple_t(int),
    )
    type_decl_factory(
        set_t(int),
    )
    type_decl_factory(
        dict_t(int, float),
    )
    type_decl_factory(
        list_t(or_t(int, float)),
    )
