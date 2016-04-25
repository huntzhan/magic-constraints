# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest

from magic_constraints import *  # noqa


def test_on_init():

    @class_initialization_constraints
    class Case(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
            Parameter('b', list),
            Parameter('c', list, default=[1, 2, 3]),
        ]

        def __init__(self):
            assert self.a == 42
            assert self.b
            assert self.c == [1, 2, 3]

    Case(42, [1])
    with pytest.raises(AssertionError):
        Case(42, [])
    with pytest.raises(AssertionError):
        Case(42, [1], [1, 2, 3, 4])
    Case(42, [1], [1, 2, 3])

    with pytest.raises(SyntaxError):
        Case(1.0)
    with pytest.raises(TypeError):
        Case(42, 1)
    with pytest.raises(TypeError):
        Case(42, [1, 2, 3], 42)


def test_none():

    @class_initialization_constraints
    class Case(object):

        INIT_PARAMETERS = [
            Parameter('a', Optional[int], default=None),
            Parameter('b', Optional[list], default=None),
        ]

    Case()
    Case(1)
    Case(1, [])
    Case(None)
    Case(None, None)


def test_on_typeobj():

    @class_initialization_constraints
    class Case1(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

    Case1(1)
    with pytest.raises(TypeError):
        Case1(1.0)

    @class_initialization_constraints
    class Case2(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_class_parameter():

    @class_initialization_constraints
    class Case1(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

    Case1(1)
    Case1(a=1)
    with pytest.raises(SyntaxError):
        Case1(b=1)

    @class_initialization_constraints
    class Case2(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_nested_type():

    @class_initialization_constraints
    class Case(object):

        INIT_PARAMETERS = [
            Parameter('a', Union[list, tuple]),
        ]

    Case(
        [1, 2],
    )
    Case(
        (1, 2),
    )
    with pytest.raises(TypeError):
        Case(1)

    with pytest.raises(TypeError):

        @class_initialization_constraints
        class Case1(object):

            INIT_PARAMETERS = [
                Parameter('a', Union[list, 1]),
            ]


def test_none_2():

    @class_initialization_constraints
    class Case1(object):

        INIT_PARAMETERS = [
            Parameter('a', Optional[int], default=None),
        ]

    @class_initialization_constraints
    class Case2(object):

        INIT_PARAMETERS = [
            Parameter('a', type(None)),
        ]

    @class_initialization_constraints
    class Case3(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

    Case1()
    Case1(None)
    Case2(None)
    with pytest.raises(TypeError):
        Case3(None)


def test_corner_case():

    with pytest.raises(SyntaxError):
        function_constraints([])(1)
    with pytest.raises(SyntaxError):
        function_constraints(1)(1)

    with pytest.raises(SyntaxError):

        @class_initialization_constraints
        class Case2(object):

            INIT_PARAMETERS = [
                Parameter('duplicates', bool),
                Parameter('duplicates', bool),
            ]

    @class_initialization_constraints
    class Case3(object):

        INIT_PARAMETERS = [
            Parameter('a', int),
        ]

    with pytest.raises(SyntaxError):
        Case3()
    with pytest.raises(SyntaxError):
        Case3(1, 2)
    with pytest.raises(SyntaxError):
        Case3(1, a=2)
    with pytest.raises(SyntaxError):
        Case3(b=2)

    with pytest.raises(TypeError):

        @class_initialization_constraints
        class Case4(object):

            INIT_PARAMETERS = [
                Parameter('a', 1),
            ]

    with pytest.raises(SyntaxError):

        @class_initialization_constraints
        class Case5(object):

            INIT_PARAMETERS = [
                Parameter('a', bool),
                Parameter('with_default', bool, default=True),
                Parameter('without_default', bool),
            ]


def test_types():

    @class_initialization_constraints
    class Case1(object):

        INIT_PARAMETERS = [
            Parameter('a', MutableSequence[int]),
        ]

    Case1(
        [1, 2, 3],
    )
    with pytest.raises(TypeError):
        Case1(
            [1, 2.0],
        )
    with pytest.raises(TypeError):
        Case1(
            (1, 2),
        )

    @class_initialization_constraints
    class Case2(object):

        INIT_PARAMETERS = [
            Parameter('a', ImmutableSequence[int]),
        ]

    Case2(
        (1, 2, 3),
    )
    with pytest.raises(TypeError):
        Case2(
            (1, 2.0),
        )
    with pytest.raises(TypeError):
        Case2(
            [1, 2],
        )

    @class_initialization_constraints
    class Case3(object):

        INIT_PARAMETERS = [
            Parameter(
                'a', Optional[Sequence[int]],
                default=None,
            ),
            Parameter(
                'b', Optional[MutableSequence[Union[int, float]]],
                default=None,
            ),
        ]

    Case3(
        a=[1, 2, 3],
    )
    Case3(
        a=(1, 2, 3),
    )
    Case3(
        b=[1, 2],
    )
    Case3(
        b=[1, 2.0],
    )
    with pytest.raises(TypeError):
        Case3(
            a=[1, 2.0],
        )
    with pytest.raises(TypeError):
        Case3(
            b=(1, 2.0),
        )
