# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import pytest
from magic_constraints import *  # noqa


pytestmark = pytest.mark.skipif(
    sys.version_info.major < 3,
    reason="",
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
