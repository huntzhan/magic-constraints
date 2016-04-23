# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_constraints import *  # noqa
from magic_constraints.parameter import *  # noqa
from magic_constraints.utils import *  # noqa


pytestmark = pytest.mark.skipif(
    sys.version_info.major < 3,
    reason="future problem.",
)


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
