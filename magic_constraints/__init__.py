# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function,
    # commented out since __all__ require str in Python 2.
    # unicode_literals,
)

from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints.exception import (
    MagicSyntaxError,
    MagicTypeError,
)

from magic_constraints.parameter import Parameter

from magic_constraints.decorators import (
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

    Any,
    Union,
)

__all__ = [
    'MagicSyntaxError',
    'MagicTypeError',

    'Parameter',

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

    'Any',
    'Union',
]
