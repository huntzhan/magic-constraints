# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints import *  # noqa


def test_callable_ellipsis():
    def c1(a, b=1): pass

    c1_wrapper2 = Callable[..., Any](c1)
    c1_wrapper2(42, 42)
    c1_wrapper2(42, 42.0)
