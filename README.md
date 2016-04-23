# magic-constraints

[![PyPI](https://img.shields.io/pypi/pyversions/magic_constraints.svg)](https://pypi.python.org/pypi/magic_constraints) [![Build
  Status](https://travis-ci.org/huntzhan/magic-constraints.svg?branch=master)](https://travis-ci.org/huntzhan/magic-constraints)
[![Coverage Status](https://coveralls.io/repos/github/huntzhan/magic-constraints/badge.svg?branch=master)](https://coveralls.io/github/huntzhan/magic-constraints?branch=master) 


## Introduction

`magic-constraints` supports:

1. [type introspection][2] on "specialized" [abstract base classes][1] (kind of).
2. declaration and dynamic chekcing on the parameters of function/method.

[1]: https://docs.python.org/3/glossary.html#term-abstract-base-class
[2]: https://en.wikipedia.org/wiki/Type_introspection

## Quick Start

### Abstract Base Classes Inspection:

`magic-constraints` implemented a few ABCs for type introspection.

Details will be presented in the next section. Example:

```python
from magic_constraints import Sequence, MutableSequence, ImmutableSequence


# True.
isinstance([1, 2, 3], Sequence)
# True.
isinstance([1, 2, 3], MutableSequence)
# True.
isinstance((1, 2, 3), ImmutableSequence)

# True, Sequence with int.
isinstance([1, 2, 3],   Sequence[int])
# False, 2.0 is float.
isinstance([1, 2.0, 3], Sequence[int])

# True.
isinstance([(1, 2), (3, 4)],   Sequence[ImmutableSequence[int]])
# False, 3.0 is float.
isinstance([(1, 2), (3.0, 4)], Sequence[ImmutableSequence[int]])
# False, [3, 4] is MutableSequence.
isinstance([(1, 2), [3, 4]],   Sequence[ImmutableSequence[int]])


# more avaliable ABCs.
from magic_constraints import (
    Sequence,
    MutableSequence,
    ImmutableSequence,
    
    Set,
    MutableSet,
    ImmutableSet,
    
    Mapping,
    MutableMapping,
    ImmutableMapping,
    
    Iterable,
    Iterator,
    
    Any,
    Union,
)
```

Declaration on function parameters:

```python
from magic_constraints import function_constraints, Parameter, Sequence


@function_constraints(
    str, Sequence[int],
)
def func_foo(foo, bar):
    return {foo: bar}


@function_constraints(
    Parameter('foo', str),
    Parameter('bar', Sequence[int], nullable=True, default=[1, 2, 3]),
    pass_by_compound=True,
)
def func_bar(args):
    return {args.foo: args.bar}
    

# more decorators.
from magic_constraints.decorator import (
    function_constraints,
    method_constraints,
    class_initialization_constraints,
)
```

Parameter checking:

```python
>>> func_foo('ok', [1, 2, 3])
{'ok': [1, 2, 3]}
>>> func_foo('ops', 42)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: argument unmatched.
-----------------------------------
argument: 42
parameter: Parameter(name='bar', type_=Sequence[int])
-----------------------------------
>>> func_foo('ops', None)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: argument unmatched.
-----------------------------------
argument: None
parameter: Parameter(name='bar', type_=Sequence[int])
-----------------------------------
>>> 
>>>
>>> func_bar('ops')
{'ops': [1, 2, 3]}
>>> func_bar('ops', None)
{'ops': None}
>>> func_bar('ok', [2, 3, 4])
{'ok': [2, 3, 4]}
>>> func_bar('ops', 42)
Traceback (most recent call last):
...
MagicTypeError: argument unmatched.
-----------------------------------
argument: 42
parameter: Parameter(name='bar', type_=Sequence[int], default=[1, 2, 3], nullable=True)
-----------------------------------
```


## `magic_constrains.types`

```
type     ::=    abc
              | speical
              | <any other type object>

abc      ::=    sequence
              | set
              | mapping 
              | iterable
              | iterator

sequence ::=    Sequence
              | Sequence          [ type ]
              | Sequence          [ type, ... ]
              | MutableSequence
              | MutableSequence   [ type ]
              | MutableSequence   [ type, ... ]
              | ImmutableSequence
              | ImmutableSequence [ type ]
              | ImmutableSequence [ type, ... ]

set      ::=    Set
              | Set               [ type ]
              | MutableSet
              | MutableSet        [ type ]
              | ImmutableSet
              | ImmutableSet      [ type ]

mapping  ::=    Mapping
              | Mapping           [ type, type ]
              | MutableMapping
              | MutableMapping    [ type, type ]
              | ImmutableMapping
              | ImmutableMapping  [ type, type ]

iterable ::=    Iterable
              | Iterable          [ type ]
              | Iterable          [ type, ... ]

iterator ::=    Iterator
              | Iterator          [ type ]
              | Iterator          [ type, ... ]

speical  ::=    Any
              | Union             [ type, ... ]
```

## `magic_constrains.decorator`

* `function_constraints`,
* `method_constraints`,
* `class_initialization_constraints`,