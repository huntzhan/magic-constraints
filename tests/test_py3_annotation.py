# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_constraints import *  # noqa


def test_function_annotation():

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


def test_method_annotation():

    class Example(object):

        @classmethod
        @method_constraints
        def func1(cls, foo: int, bar: float) -> float:
            return foo + bar

        @method_constraints
        def func2(self, foo: int, bar: float = None) -> float:
            if bar is None:
                # should fail the return type checkin.
                return 42
            else:
                # good case.
                return foo + bar

    assert 3.0 == Example.func1(1, 2.0)
    e = Example()
    assert 3.0 == e.func2(1, 2.0)
    with pytest.raises(TypeError):
        e.func2(1)
