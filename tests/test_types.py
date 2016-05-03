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
    conditional_to_bytes,
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


def touch(iterable):
    for _ in iterable:
        pass


def test_iterator():
    assert isinstance(iter([1, 2]), Iterator)
    assert not isinstance([1, 2], Iterator)

    assert not isinstance(iter([1, 2]), Iterator[int])

    for _ in Iterator[int](iter([1, 2])):
        pass

    Iterator[int, int, int]

    touch(
        Iterator[int, int](iter([1, 2])),
    )

    touch(
        Iterator[int, float](iter([1, 2.0])),
    )

    with pytest.raises(TypeError):
        Iterator([1, 2])
    with pytest.raises(TypeError):
        Iterator[int]([1, 2])

    with pytest.raises(TypeError):
        touch(
            Iterator[int](iter([1, 2.0])),
        )

    with pytest.raises(TypeError):
        touch(
            Iterator[int, int](iter([1, 2.0])),
        )

    # lazy evaluation.
    it = Iterator[int, int](iter([1, 2, 3]))
    with pytest.raises(IndexError):
        touch(it)

    it = Iterator[int, int](iter([1]))
    with pytest.raises(IndexError):
        touch(it)

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
        touch(
            Iterable[int]([1, 2.0]),
        )

    Iterable[int, int]
    touch(
        Iterable[int, int]([1, 2]),
    )
    with pytest.raises(TypeError):
        touch(
            Iterable[int, int]([1, 2.0]),
        )

    with pytest.raises(IndexError):
        touch(
            Iterable[int, int]([1]),
        )
    with pytest.raises(IndexError):
        touch(
            Iterable[int, int]([1, 2, 3]),
        )

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

    c1_wrapper1 = Callable[[int, int], Any](c1)

    c1_wrapper1(42, 42)
    with pytest.raises(TypeError):
        c1_wrapper1(42, 42.0)


def test_callable_ellipsis():
    def c1(a, b=1): pass

    c1_wrapper2 = Callable[Ellipsis, Any](c1)
    c1_wrapper2(42, 42)
    c1_wrapper2(42, 42.0)


def test_repr():

    assert conditional_to_bytes('Any') == repr(Any)
    assert conditional_to_bytes('Union') == repr(Union)
    assert conditional_to_bytes('Optional') == repr(Optional)


@pytest.mark.xfail(
    sys.version_info.major > 2,
    reason="future problem.",
)
def test_repr_python2():
    assert conditional_to_bytes('Sequence') == repr(Sequence)
    assert conditional_to_bytes('Sequence[newint]') == repr(Sequence[int])
    assert conditional_to_bytes('Sequence[newint, float]') ==\
        repr(Sequence[int, float])

    assert conditional_to_bytes('Callable[[newint, float], float]') ==\
        repr(Callable[[int, float], float])


@pytest.mark.xfail(
    sys.version_info.major < 3,
    reason="future problem.",
)
def test_repr_python3():
    assert conditional_to_bytes('Sequence') == repr(Sequence)
    assert conditional_to_bytes('Sequence[int]') == repr(Sequence[int])
    assert conditional_to_bytes('Sequence[int, float]') ==\
        repr(Sequence[int, float])

    assert conditional_to_bytes('Callable[[int, float], float]') ==\
        repr(Callable[[int, float], float])


def test_corner_cases():
    assert not issubclass(1, Sequence)
    assert not issubclass(int, ImmutableSequence)
    assert not isinstance(int, ImmutableSequence)

    assert not isinstance(1, Optional)
    assert not issubclass(int, Optional)
