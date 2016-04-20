# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import pytest
from magic_constraints.types import *  # noqa


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

    assert issubclass(MutableSequence, Sequence)
    assert issubclass(ImmutableSequence, Sequence)
    assert not issubclass(MutableSequence, ImmutableSequence)
    assert not issubclass(ImmutableSequence, MutableSequence)


def test_set():

    assert isinstance({1, 2}, Set)
    assert isinstance({1, 2}, MutableSet)
    assert not isinstance({1, 2}, ImmutableSet)
    assert isinstance(frozenset((1, 2)), ImmutableSet)

    assert isinstance({1, 2}, Set[int])
    assert not isinstance({1, 2.0}, Set[int])

    with pytest.raises(SyntaxError):
        Set[int, ]
    with pytest.raises(SyntaxError):
        Set[int, float]

    assert issubclass(MutableSet, Set)
    assert issubclass(ImmutableSet, Set)
    assert not issubclass(MutableSet, ImmutableSet)
    assert not issubclass(ImmutableSet, MutableSet)


def test_mapping():
    assert isinstance({'a': 1}, Mapping)
    assert isinstance({'a': 1}, MutableMapping)

    assert isinstance({'a': 1}, Mapping[str, int])
    assert not isinstance({'a': 1.0}, Mapping[str, int])
    assert not isinstance({1: 1}, Mapping[str, int])

    assert isinstance({'a': 1}, MutableMapping[str, int])
    assert not isinstance({'a': 1.0}, MutableMapping[str, int])
    assert not isinstance({1: 1}, MutableMapping[str, int])

    with pytest.raises(SyntaxError):
        Mapping[int]
    with pytest.raises(SyntaxError):
        Mapping[int, ]
    with pytest.raises(SyntaxError):
        Mapping[int, int, int]

    assert issubclass(MutableMapping, Mapping)
    assert issubclass(ImmutableMapping, Mapping)
    assert not issubclass(MutableMapping, ImmutableMapping)
    assert not issubclass(ImmutableMapping, MutableMapping)


@pytest.mark.skipif(
    sys.version_info < (3, 3),
    reason="types.MappingProxyType new in 3.3",
)
def test_immutable_mapping():
    from types import MappingProxyType as idict
    assert isinstance(
        idict({'a': 1}), ImmutableMapping,
    )

    assert isinstance(
        idict({'a': 1}), Mapping[str, int],
    )
    assert not isinstance(
        idict({'a': 1.0}), Mapping[str, int],
    )
    assert not isinstance(
        idict({1: 1}), Mapping[str, int],
    )


def test_iterator():
    assert isinstance(iter([1, 2]), Iterator)
    assert not isinstance([1, 2], Iterator)

    for _ in Iterator[int](iter([1, 2])):
        pass
    with pytest.raises(TypeError):
        for _ in Iterator[int](iter([1, 2.0])):
            pass
    with pytest.raises(SyntaxError):
        Iterator[int, int]
