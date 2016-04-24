# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import pytest
from magic_constraints import *  # noqa


def test_function_constraints_pass_by_compound():

    @function_constraints(
        Parameter('a', int),
        Parameter('b', float),
    )
    def example(args):
        assert args.a == 1
        assert args.b == 1.0

    example(1, 1.0)
    example(b=1.0, a=1)
    with pytest.raises(AssertionError):
        example(2, 1.0)

    with pytest.raises(SyntaxError):
        example(1)
    with pytest.raises(SyntaxError):
        example(1.0)
    with pytest.raises(SyntaxError):
        example(1, a=1)


def test_function_constraints_pass_by_positional():

    @function_constraints(
        int, float, int, int,
    )
    def example(a, b, c=42, d=None):
        assert a == 1
        assert b == 1.0
        assert c == 42
        assert d is None

    example(1, 1.0)
    example(b=1.0, a=1)
    with pytest.raises(AssertionError):
        example(2, 1.0)

    example(1, 1.0, 42)
    with pytest.raises(AssertionError):
        example(2, 1.0, 43)

    example(1, 1.0, 42, None)
    with pytest.raises(AssertionError):
        example(1, 1.0, 42, d=42)

    with pytest.raises(SyntaxError):
        example(1)
    with pytest.raises(SyntaxError):
        example(1.0)
    with pytest.raises(SyntaxError):
        example(1, a=1)

    with pytest.raises(SyntaxError):
        function_constraints()


def test_method_constraints():

    class Case1(object):

        @classmethod
        @method_constraints(
            Parameter('a', int),
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

    with pytest.raises(SyntaxError):
        method_constraints()


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

    with pytest.raises(TypeError):
        class_initialization_constraints(1)


def test_corner_cases1():

    with pytest.raises(SyntaxError):
        @function_constraints(
            list(),
        )
        def example(args):
            pass

    with pytest.raises(TypeError):
        @class_initialization_constraints
        class Case2(object):

            INIT_PARAMETERS = 42

    with pytest.raises(SyntaxError):
        @function_constraints(
            int, float,
        )
        def func1(a):
            pass

    with pytest.raises(SyntaxError):
        @function_constraints(
            int, float,
        )
        def func2(*a, **b):
            pass


def test_return_type():

    @function_constraints(
        int,
        return_type=int,
    )
    def func1(a):
        return a

    @function_constraints(
        int,
        return_type=float,
    )
    def func2(a):
        return a

    func1(1)
    with pytest.raises(TypeError):
        func2(1)

    @function_constraints(
        Parameter('a', int, nullable=True),
        ReturnType(float, nullable=True),
    )
    def func3(args):
        return args.a

    func3(None)
    with pytest.raises(TypeError):
        func3(1)

    class Example(object):

        @method_constraints(
            int,
            return_type=float,
        )
        def func1(self, a):
            return a

        @method_constraints(
            Parameter('a', int, nullable=True),
            ReturnType(float, nullable=True),
        )
        def func2(self, args):
            return args.a

    e = Example()
    with pytest.raises(TypeError):
        e.func1(1)
    e.func2(None)
    with pytest.raises(TypeError):
        e.func2(1)

    @function_constraints(
        ReturnType(float, nullable=True),
    )
    def func4(args):
        return None

    func4()

    @function_constraints(
        return_type=int
    )
    def func5():
        return 42

    func5()


@pytest.mark.skipif(
    sys.version_info.major < 3,
    reason="annotation is Py3 feature.",
)
def test_annotation():

    @function_constraints
    def func1(foo: int, bar: float) -> float:
        return foo + bar

    assert 3.0 == func1(1, 2.0)

    @function_constraints
    def func2(foo: int, bar: float = None) -> float:
        if bar is None:
            # should fail the return type checkin.
            return 42
        else:
            # good case.
            return foo + bar

    assert 3.0 == func2(1, 2.0)
    with pytest.raises(TypeError):
        func2(1)
