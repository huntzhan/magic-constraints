# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_constraints import *  # noqa


def test_function_constraints_pass_by_compound():

    @function_constraints(
        Parameter('a', int),
        Parameter('b', float),
        pass_by_compound=True,
    )
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


def test_function_constraints_pass_by_positional():

    @function_constraints(
        int, float,
    )
    def example(a, b):
        assert a == 1
        assert b == 1.0

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


def test_method_constraints():

    class Case1(object):

        @classmethod
        @method_constraints(
            Parameter('a', int),
            pass_by_compound=True,
        )
        def test_cls(cls, args):
            assert args.a == 1

        @method_constraints(
            int,
        )
        def test_self(self, a):
            assert a == 1

    Case1.test_cls(1)
    Case1.test_cls(a=1)
    with pytest.raises(AssertionError):
        Case1.test_cls(2)

    case1 = Case1()
    case1.test_self(1)
    with pytest.raises(AssertionError):
        case1.test_self(2)


def test_class_initialization_constraints():

    @class_initialization_constraints
    class Case1(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

        def __init__(self):
            assert self.a == 1

    Case1(1)
    Case1(a=1)
    with pytest.raises(AssertionError):
        Case1(2)

    @class_initialization_constraints
    class Case2(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

    Case2(1)
    Case2(a=1)

    with pytest.raises(SyntaxError):
        class_initialization_constraints(1)
