# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function,
    # commented out since __all__ require str in Python 2.
    # unicode_literals,
)

from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints.exception import (
    MagicError,
    MagicSyntaxError,
    MagicTypeError,
    MagicIndexError,
)

from magic_constraints.constraint import (
    Constraint,
    Parameter,
    ReturnType,
)

from magic_constraints.decorator import (
    function_constraints,
    method_constraints,
    class_initialization_constraints,
)

from magic_constraints.types import (
    Sequence,
    MutableSequence,
    ImmutableSequence,

    Set,
    MutableSet,
    ImmutableSet,

    Mapping,
    MutableMapping,
    ImmutableMapping,

    Iterator,
    Iterable,

    Callable,

    Any,
    Union,
    Optional,
    NoneType,
)

__all__ = [
    'MagicError',
    'MagicSyntaxError',
    'MagicTypeError',
    'MagicIndexError',

    'Constraint',
    'Parameter',
    'ReturnType',

    'function_constraints',
    'method_constraints',
    'class_initialization_constraints',

    'Sequence',
    'MutableSequence',
    'ImmutableSequence',

    'Set',
    'MutableSet',
    'ImmutableSet',

    'Mapping',
    'MutableMapping',
    'ImmutableMapping',

    'Iterator',
    'Iterable',

    'Callable',

    'Any',
    'Union',
    'Optional',
    'NoneType',
]
