# Introduction

*magic-constraints* implemented (or hacked) a bunch of [abstract base classes][1] (ABCs for short) to support [type introspection][2], that is, the `isinstance`/`issubclass` operatios in Python. Specialization of ABC is support, i.e. `Sequence[int]` and `Sequence[int]` are specialized versions of `Sequence`.

Also, *magic-constraints* provides several decorators to enable runtime type/value checking on the parameters and return value of user-defined function and method. Especially, thoses decorators fit well with the type annotation feature introduced in Python 3.x:

```python
from magic_constraints import function_constraints, Optional


# foobar should accept either an int object or a None object.
@function_constraints
def function(foobar: Optional[int]) -> float:
    if foobar is None:
        # should fail the return type checking.
        return 42
    else:
        # good case.
        return 42.0
```

Runtime:

```
# ok.
>>> function(1)
42.0

# failed.
# 1.0 is float, while foobar requrie int or type(None).
>>> function(1.0)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError:
MagicTypeError: argument unmatched.
-----------------------------------
argument: 1.0
parameter: Parameter(name='foobar', type_=Optional[int])
-----------------------------------

# failed.
# when foobar is None, the function returns a float,
# leading to unmatched return type error.
>>> function(None)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: return value unmatched.
---------------------------------------
ret: 42
return_type: ReturnType(type_=float)
---------------------------------------
```

# Quick Start

## Install

```
$ pip install magic-constraints
```

## Usage Of ABCs

*magic-constraints* provides `Sequence/MutableSequence/ImmutableSequence`. You can invoke `isinstance`/`issubclass` operatios on :

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

# True
issubclass(MutableSequence, Sequence)
# True
issubclass(ImmutableSequence, Sequence)
# False
issubclass(MutableSequence, ImmutableSequence)
# False
issubclass(ImmutableSequence, MutableSequence)
```

More avaliable ABCs:

| name | supported specialization(s) |
| --- | --- |
| Sequence          | [ type ] , [ type , ... ] |
| MutableSequence   | [ type ] , [ type , ... ] |
| ImmutableSequence | [ type ] , [ type , ... ] |
| Set               | [ type ] |
| MutableSet        | [ type ] |
| ImmutableSet      | [ type ] |
| Mapping           | [ type , type ] |
| MutableMapping    | [ type , type ] |
| ImmutableMapping  | [ type , type ] |
| Iterator          | [ type ] , [ type , ... ] |
| Iterable          | [ type ] , [ type , ... ] |
| Callable          | [ [ type , ... ] , type ] , [ Ellipsis , type ] |
| Any               | *not support* |
| Union             | [ type , ... ] |
| Optional          | [ type ] |
| NoneType          | *not support* |


## Usage Of Decorators

Declaration on function parameters and return value:

```python
from magic_constraints import (
    function_constraints,
    Sequence, Mapping,
)

@function_constraints
def func1(foo: str, bar: Sequence[int]) -> Mapping[str, Sequence[int]]:
    return {foo: bar}
```

More decorators:

```python
from magic_constraints.decorator import (
    function_constraints,
    method_constraints,
    class_initialization_constraints,
)
```

## Runtime Type/Value Checking

Exceptoin would be raised if there's something wrong in the invocation of decorated function, i.e. input argument is not an instance of declared type. 

Only derived classes of `SyntaxError` and `TypeError` would be raised:

1. anything related to types, such as failing to pass `isinstance`, would raise an exception with derived type of `TypeError`.
2. besides (1), anything related to the promise of interface (function) invocation, would raise an exception with derived type of `SyntaxError`.

Example:

```
# ok.
>>> func1('key', [1, 2, 3])
{'key': [1, 2, 3]}

# failed, bar requires a sequnce.
>>> func1('42 is not a sequence', 42)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: argument unmatched.
-----------------------------------
argument: 42
parameter: Parameter(name='bar', type_=Sequence[int])
-----------------------------------

# failed, bar requires a sequence of ints.
>>> func1('2.0 is not int', [1, 2.0, 3])
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: argument unmatched.
-----------------------------------
argument: [1, 2.0, 3]
parameter: Parameter(name='bar', type_=Sequence[int])
-----------------------------------
```

# For more...

* [magic_constrains.types][3].
* [magic_constrains.decorator][4].


[1]: https://docs.python.org/3/glossary.html#term-abstract-base-class
[2]: https://en.wikipedia.org/wiki/Type_introspection
[3]: https://github.com/huntzhan/magic-constraints/wiki/magic_constrains.types
[4]: https://github.com/huntzhan/magic-constraints/wiki/magic_constraints.decorator

