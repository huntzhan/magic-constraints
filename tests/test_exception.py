# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints import *  # noqa
from magic_constraints.utils import (
    repr_return,
)


def test_repr_and_str():

    assert (
        repr_return(
            "MagicSyntaxError('[Empty Message]',)"
        ) ==
        repr(MagicSyntaxError())
    )

    assert (
        repr_return(
            "MagicSyntaxError('msg',)"
        ) ==
        repr(MagicSyntaxError('msg'))
    )

    assert (
        repr_return(
            "MagicSyntaxError('msg',)"
        ) ==
        repr(MagicSyntaxError('msg', b=1, a=2))
    )

    assert (
        repr_return(
            "\n"
            "MagicSyntaxError: [Empty Message]\n"
            "---------------------------------\n"
            "[Empty kwargs]\n"
            "---------------------------------"
        ) ==
        str(MagicSyntaxError())
    )

    assert (
        repr_return(
            "\n"
            "MagicSyntaxError: msg\n"
            "---------------------\n"
            "[Empty kwargs]\n"
            "---------------------"
        ) ==
        str(MagicSyntaxError('msg'))
    )

    assert (
        repr_return(
            "\n"
            "MagicSyntaxError: msg\n"
            "---------------------\n"
            "a: 2\n"
            "b: 1\n"
            "---------------------"
        ) ==
        str(MagicSyntaxError('msg', b=1, a=2))
    )


def test_serialize():

    e = MagicTypeError()
    assert {'message': '[Empty Message]'} == e.serialize()

    e = MagicTypeError('msg')
    assert {'message': 'msg'} == e.serialize()

    e = MagicTypeError('msg', a=1, b=2)
    assert {
        'message': 'msg',
        'a': 1,
        'b': 2,
    } == e.serialize()
