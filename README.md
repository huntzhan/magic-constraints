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

### Install

```
pip install magic-constraints
```

### Abstract Base Classes Introspection:

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

Supported ABCs and avaliable specialization of ABCs:

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

Explanations.

`type` means type object in Python. `abc` defines several supported ABCs. `speical` defines some type objects for some spectial purposes.

`sequence`:

* `Sequence` is equivalent to [collections.abc.Sequence][3]. `MutableSequence` is equivalent to [collections.abc.MutableSequence][4]. `ImmutableSequence` is a `Sequence` that is not a `MutableSequence`.
* `Sequence[ type ]` specializes `Sequence`, accepting a sequence with instances of `type`.
* `Sequence[ type, ... ]` specialized `Sequence`, accepting a sequence with instances of exactly mapping of `type, ...`. For example, `Sequence[int, float]` accepts `(1, 2.0)` or `[1, 2.0]`.

`set`:

* `Set` is equivalent to [collections.abc.Set][5]. `MutableSet` is equivalent to [collections.abc.MutableSet][6]. `ImmutableSet` is a `Set` that is not a `MutableSet`.
* `Set[ type ]` specializes `Sequence`, accepting a set with instances of `type`.

`mapping`:

* `Mapping` is equivalent to [collections.abc.Mapping][7]. `MutableMapping` is equivalent to [collections.abc. MutableMapping][8]. `ImmutableMapping` is equivalent to [types.MappingProxyType][9].
* `Mapping[ key_type, val_type ]` specializes `Mapping`, accepting items with key of `key_type` and value of `val_type`.

`iterable`:

* `Iterable` is equivalent to [collections.abc.Iterable][10].
* Dual to the side effect of iterating the iterable, `isinstance(instance, Iterable[ type ])` and `isinstance(instance, Iterable[ type, ... ])` always return `False`.
* `Iterable[ type ](iterable)` and `Iterable[ type, ... ](iterable)` creates a iterable proxy with lazy type instrospection on the elements. Example:
	
	```python
	for i in Iterable[int]([1, 2, 3]):
	    print(i)
	``` 

`iterator`:

* `Iterable` is equivalent to [collections.abc.Iterator][11].
* Dual to the side effect of iterating the iterator, `isinstance(instance, Iterator[ type ])` and `isinstance(instance, Iterator[ type, ... ])` always return `False`.
* `Iterator[ type ](iterator)` and `Iterator[ type, ... ](iterator)` creates a iterator proxy with lazy type instrospection on the elements. Example:
	
	```python
	for i in Iterator[int](iter([1, 2, 3])):
	    print(i)
	``` 

`special`:

* `Any` accepts any object, including type and non-type objects. It's guaranteed that `isinstance(..., Any)` returns `True` and `issubclass(..., Any)` returns `True`.
* `Union[ type, ... ]` acceps instance that match one of `type, ...`. For example, `isinstance(42, Union[int, float]` returns `True`.

[3]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence
[4]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence
[5]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Set
[6]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet
[7]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
[8]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping
[9]: https://docs.python.org/3.4/library/types.html#types.MappingProxyType
[10]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
[11]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator

## `magic_constrains.decorator`

* `function_constraints`,
* `method_constraints`,
* `class_initialization_constraints`,