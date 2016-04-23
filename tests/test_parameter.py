# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import pytest
from magic_constraints import *  # noqa
from magic_constraints.utils import (
    repr_return,
)


pytestmark = pytest.mark.skipif(
    sys.version_info.major < 3,
    reason="future problem.",
)


def test_callback():
    p = Parameter('a', int, callback=lambda n: n == 42)
    assert p.check_argument(42)
    assert not p.check_argument(0)
    assert not p.check_argument('test')


def test_repr():
    assert (
        repr_return("Parameter(name='a', type_=Sequence[int])") ==
        repr(Parameter(name='a', type_=Sequence[int]))
    )
    assert (
        repr_return(
            "Parameter("
            "name='a', "
            "type_=Sequence[int], "
            "nullable=True"
            ")"
        ) ==
        repr(Parameter(name='a', type_=Sequence[int], nullable=True))
    )
    # test keyword sorting.
    assert (
        repr_return(
            "Parameter("
            "name='a', "
            "type_=Sequence[int], "
            "default=[1, 2, 3], "
            "nullable=True"
            ")"
        ) ==
        repr(Parameter(
            name='a', type_=Sequence[int], nullable=True, default=[1, 2, 3],
        ))
    )
