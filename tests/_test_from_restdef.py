# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest

from magic_constraints import *  # noqa


def test_on_init():

    class Case(object):

        @method_init_parameter([
            ('a', int),
            ('b', list),
            ('c', list, [1, 2, 3]),
        ])
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

    with pytest.raises(TypeError):
        Case(1.0)
    with pytest.raises(TypeError):
        Case(42, 1)
    with pytest.raises(TypeError):
        Case(42, [1, 2, 3], 42)


def test_none():

    class Case(object):

        parameters = [
            ('a', int, None),
            ('b', list, None),
        ]

        @method_init_parameter(parameters)
        def __init__(self):
            pass

    Case()
    Case(1)
    Case(1, [])
    Case(None)
    Case(None, None)


def test_on_typeobj():

    @class_init_parameter
    class Case1(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case1(1)
    with pytest.raises(TypeError):
        Case1(1.0)

    @class_init_parameter
    class Case2(object):

        PARAMETERS = [
            ('a', int),
        ]

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_class_parameter():

    @class_init_parameter
    class Case1(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case1(1)
    Case1(a=1)
    with pytest.raises(TypeError):
        Case1(b=1)

    @class_init_parameter
    class Case2(object):

        PARAMETERS = [
            ('a', int),
        ]

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_nested_type():

    @class_init_parameter
    class Case(object):

        PARAMETERS = [
            ('a', or_t(list, tuple)),
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

        @class_init_parameter
        class Case1(object):

            PARAMETERS = [
                ('a', or_t(list, 1)),
            ]


def test_none_2():

    @class_init_parameter
    class Case1(object):

        PARAMETERS = [
            ('a', int, None),
        ]

    @class_init_parameter
    class Case2(object):

        PARAMETERS = [
            ('a', type(None)),
        ]

    @class_init_parameter
    class Case3(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case1()
    Case1(None)
    Case2(None)
    with pytest.raises(TypeError):
        Case3(None)


def test_corner_case():

    with pytest.raises(TypeError):
        function_parameter([])(1)
    with pytest.raises(TypeError):
        function_parameter(1)(1)

    with pytest.raises(TypeError):

        @class_init_parameter
        class Case1(object):

            PARAMETERS = [
                ('name',),
            ]

    with pytest.raises(SyntaxError):

        @class_init_parameter
        class Case2(object):

            PARAMETERS = [
                ('duplicates', bool),
                ('duplicates', bool),
            ]

    @class_init_parameter
    class Case3(object):

        PARAMETERS = [
            ('a', int),
        ]

    with pytest.raises(TypeError):
        Case3()
    with pytest.raises(TypeError):
        Case3(1, 2)
    with pytest.raises(TypeError):
        Case3(1, a=2)
    with pytest.raises(TypeError):
        Case3(b=2)

    with pytest.raises(TypeError):

        @class_init_parameter
        class Case4(object):

            PARAMETERS = [
                ('a', 1),
            ]

    with pytest.raises(SyntaxError):

        @class_init_parameter
        class Case5(object):

            PARAMETERS = [
                ('a', bool),
                ('with_default', bool, None),
                ('without_default', bool),
            ]


def test_nested_decl():

    @class_init_parameter
    class Case1(object):

        PARAMETERS = [
            ('a', list_t(int)),
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

    @class_init_parameter
    class Case2(object):

        PARAMETERS = [
            ('a', tuple_t(int)),
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

    @class_init_parameter
    class Case3(object):

        PARAMETERS = [
            ('a', or_t(list_t(int), tuple_t(int)), None),
            ('b', list_t(or_t(int, float)), None),
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
