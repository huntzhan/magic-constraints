# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_parameter.types import *  # noqa


def test_shit():

    assert isinstance([], Sequence)
    assert isinstance([1, 2, 3], Sequence[int])
    assert not isinstance([1, 2.0, 3], Sequence[int])

    assert not issubclass(Sequence[int], Sequence)
    assert not issubclass(Sequence, Sequence[int])
    assert not isinstance(Sequence[int], Sequence)
    assert not isinstance(Sequence, Sequence[int])
