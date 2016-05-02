# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_constraints import *  # noqa


def test_method_constraints():

    class Case2(object):

        @method_constraints(...)
        def test_self1(self, *a):
            pass

        @method_constraints(..., return_type=int)
        def test_self2(self, a):
            return a

    case2 = Case2()
    case2.test_self1(1, 2, 3.5)
    case2.test_self1()
    case2.test_self2(42)
    with pytest.raises(TypeError):
        case2.test_self2(42.0)


def test_ellipsis():

    @function_constraints(...)
    def func1(*args): pass

    func1(1, 2, 3)
    func1(1.0, 2, 3)

    @function_constraints(..., return_type=int)
    def func2(a):
        return a

    func2(1)
    with pytest.raises(TypeError):
        func2(1.0)
