# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest
from magic_constraints import *  # noqa
from magic_constraints.utils import (
    conditional_to_bytes,
)


def test_validator():
    p = Parameter('a', int, validator=lambda n: n == 42)
    assert p.check_instance(42)
    assert not p.check_instance(0)
    assert not p.check_instance('test')


def test_repr():
    assert (
        conditional_to_bytes("Parameter(name='a', type_=Sequence[int])") ==
        repr(Parameter(name='a', type_=Sequence[int]))
    )
    assert (
        conditional_to_bytes(
            "Parameter("
            "name='a', "
            "type_=Sequence[int]"
            ")"
        ) ==
        repr(Parameter(name='a', type_=Sequence[int]))
    )
    # test keyword sorting.
    assert (
        conditional_to_bytes(
            "Parameter("
            "name='a', "
            "type_=Sequence[int], "
            "default=[1, 2, 3]"
            ")"
        ) ==
        repr(Parameter(
            name='a', type_=Sequence[int], default=[1, 2, 3],
        ))
    )


def test_constraints():

    def validator(val, expected, *args, **kwargs):
        return val == expected

    c = Constraint(int, validator=validator)
    assert c.check_instance(42, 42)
    assert not c.check_instance(42, 43)

    c.check_instance(42, 43, 123, 123, a=1)


def test_corner_case():

    with pytest.raises(TypeError):
        Parameter('a', int, default=None)

    with pytest.raises(SyntaxError):
        ReturnType(int, default=1)
