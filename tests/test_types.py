# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_parameter.types import *  # noqa


def test_sequence():

    assert isinstance([], Sequence)
    assert isinstance((1, 2, 3), Sequence[int])
    assert not isinstance([1, 2.0, 3], Sequence[int])

    assert isinstance([1, 2.0], Sequence[int, float])
    assert not isinstance([1], Sequence[int, float])
    assert not isinstance([1.0], Sequence[int, float])

    assert isinstance([], MutableSequence)
    assert isinstance([1, 2, 3], MutableSequence)
    assert not isinstance((1, 2, 3), MutableSequence)

    assert isinstance((), ImmutableSequence)
    assert isinstance((1, 2, 3), ImmutableSequence)
    assert not isinstance([1, 2, 3], ImmutableSequence)

    assert not issubclass(Sequence[int], Sequence)
    assert not issubclass(Sequence, Sequence[int])
    assert not isinstance(Sequence[int], Sequence)
    assert not isinstance(Sequence, Sequence[int])
