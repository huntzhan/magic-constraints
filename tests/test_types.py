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


def test_sequence():

    assert isinstance([], Sequence)
    assert isinstance((1, 2, 3), Sequence[int])
    assert not isinstance([1, 2.0, 3], Sequence[int])

    assert isinstance([1, 2.0], Sequence[int, float])
    assert not isinstance([1, 2], Sequence[int, float])
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

    with pytest.raises(TypeError):
        Sequence[int, 1]

    with pytest.raises(TypeError):
        Sequence[[int, int]]


def test_set():

    assert isinstance({1, 2}, Set)
    assert isinstance({1, 2}, MutableSet)
    assert not isinstance({1, 2}, ImmutableSet)
    assert isinstance(frozenset((1, 2)), ImmutableSet)

    assert isinstance({1, 2}, Set[int])
    assert not isinstance({1, 2.0}, Set[int])

    with pytest.raises(TypeError):
        Set[int, ]
    with pytest.raises(TypeError):
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

    assert not isinstance(1, Mapping)

    with pytest.raises(TypeError):
        Mapping[int]
    with pytest.raises(TypeError):
        Mapping[int, ]
    with pytest.raises(TypeError):
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

    assert not isinstance(iter([1, 2]), Iterator[int])

    for _ in Iterator[int](iter([1, 2])):
        pass

    Iterator[int, int, int]

    for _ in Iterator[int, int](iter([1, 2])):
        pass

    for _ in Iterator[int, float](iter([1, 2.0])):
        pass

    with pytest.raises(TypeError):
        Iterator([1, 2])
    with pytest.raises(TypeError):
        Iterator[int]([1, 2])

    with pytest.raises(TypeError):
        for _ in Iterator[int](iter([1, 2.0])):
            pass

    with pytest.raises(TypeError):
        for _ in Iterator[int, int](iter([1, 2.0])):
            pass

    # lazy evaluation.
    it = Iterator[int, int](iter([1, 2, 3]))
    with pytest.raises(IndexError):
        for _ in it:
            pass

    assert isinstance(
        (i for i in range(10)),
        Iterator,
    )


def test_iterable():
    assert isinstance([1, 2, 3], Iterable)
    assert not isinstance(1, Iterable)

    for _ in Iterable[int]([1, 2]):
        pass

    with pytest.raises(TypeError):
        Iterable(1)
    with pytest.raises(TypeError):
        Iterable[int](1)

    with pytest.raises(TypeError):
        for _ in Iterable[int]([1, 2.0]):
            pass
    with pytest.raises(TypeError):
        Iterable[int, int]

    assert isinstance(
        (i for i in range(10)),
        Iterable,
    )


def test_any():

    assert isinstance(1, Any)
    assert isinstance(1.0, Any)
    assert isinstance(object, Any)
    assert isinstance(type, Any)

    assert not issubclass(1, Any)
    assert not issubclass(1.0, Any)
    assert issubclass(object, Any)
    assert issubclass(type, Any)

    assert issubclass(Sequence, Any)
    assert issubclass(Union, Any)


def test_union():
    assert not isinstance(1, Union)
    assert not issubclass(int, Union)

    assert isinstance(1, Union[int, float])
    assert isinstance(1.0, Union[int, float])
    assert not isinstance('str', Union[int, float])

    assert not issubclass(str, Union)
    assert not issubclass(str, Union[int, float])

    with pytest.raises(TypeError):
        Union[1]


def test_callable():

    def c1(a, b=1): pass

    assert isinstance(c1, Callable)
    assert isinstance(lambda a, b: None, Callable)

    Callable[[int, int], Any]

    c1_wrapper = Callable[[int, int], Any](c1)

    c1_wrapper(42, 42)
    with pytest.raises(TypeError):
        c1_wrapper(42, 42.0)


@pytest.mark.xfail(
    sys.version_info.major > 2,
    reason="future problem.",
)
def test_repr_python2():
    assert repr_return('Sequence') == repr(Sequence)
    assert repr_return('Sequence[newint]') == repr(Sequence[int])
    assert repr_return('Sequence[newint, float]') == repr(Sequence[int, float])


@pytest.mark.xfail(
    sys.version_info.major < 3,
    reason="future problem.",
)
def test_repr_python3():
    assert repr_return('Sequence') == repr(Sequence)
    assert repr_return('Sequence[int]') == repr(Sequence[int])
    assert repr_return('Sequence[int, float]') == repr(Sequence[int, float])


def test_corner_cases():
    assert not issubclass(1, Sequence)
    assert not issubclass(int, ImmutableSequence)
    assert not isinstance(int, ImmutableSequence)

    assert not isinstance(1, Optional)
    assert not issubclass(int, Optional)
