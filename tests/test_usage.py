# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_parameter import *  # noqa


def test_function_parameter():

    @function_parameter([
        ('a', int),
        ('b', float),
    ])
    def example(args):
        assert args.a == 1
        assert args.b == 1.0

    example(1, 1.0)
    example(b=1.0, a=1)
    with pytest.raises(AssertionError):
        example(2, 1.0)

    with pytest.raises(TypeError):
        example(1)
    with pytest.raises(TypeError):
        example(1.0)
    with pytest.raises(TypeError):
        example(1, a=1)


def test_method_parameter():

    class Case1(object):

        @classmethod
        @method_parameter(
            [
                ('a', int),
            ],
            pass_by_cls_or_self_attributes=True,
        )
        def test_cls(cls):
            assert cls.a == 1

        @method_parameter(
            [
                ('a', int),
            ],
            pass_by_cls_or_self_attributes=True,
            no_warning_on_cls_or_self_attributes=False,
        )
        def test_self(self):
            assert self.a == 1

    Case1.test_cls(1)
    Case1.test_cls(a=1)
    with pytest.raises(AssertionError):
        Case1.test_cls(2)

    case1 = Case1()
    case1.test_self(1)
    with pytest.raises(TypeError):
        case1.test_self(1)


def test_method_init_parameter():

    class Case1(object):

        @method_init_parameter([
            ('a', int),
        ])
        def __init__(self):
            assert self.a == 1

    Case1(1)
    Case1(a=1)
    with pytest.raises(AssertionError):
        Case1(2)

    with pytest.raises(TypeError):
        Case1(b=1)
    with pytest.raises(TypeError):
        Case1(1.0)


def test_class_init_parameter():

    @class_init_parameter
    class Case1(object):

        PARAMETERS = [
            ('a', int),
        ]

        def __init__(self):
            assert self.a == 1

    Case1(1)
    Case1(a=1)
    with pytest.raises(AssertionError):
        Case1(2)

    @class_init_parameter
    class Case2(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case2(1)
    Case2(a=1)
