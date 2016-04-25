# magic-constraints

[![PyPI](https://img.shields.io/pypi/pyversions/magic_constraints.svg)](https://pypi.python.org/pypi/magic_constraints) [![Build
  Status](https://travis-ci.org/huntzhan/magic-constraints.svg?branch=master)](https://travis-ci.org/huntzhan/magic-constraints)
[![Coverage Status](https://coveralls.io/repos/github/huntzhan/magic-constraints/badge.svg?branch=master)](https://coveralls.io/github/huntzhan/magic-constraints?branch=master) 

# Introduction

`magic-constraints`:

1. Implemented (or hacked) several [abstract base classes][1] (ABC for short) to support [type introspection][2], that is, the `isinstance`/`issubclass` operatios in Python. Specialization of ABC is support, i.e. `Sequence -> Sequence[int]`.
2. Provides several decorators to enable runtime type/value checking on the parameters and return value of function/method. Especially, thoses decorators fit well with the type annotation feature introduced in Python 3.x:
  ```python
  from magic_constraints import function_constraints
  
  @function_constraints
  def function(foobar: int=None) -> float:
      if foobar is None:
          # should fail the return type checkin.
          return 42
      else:
          # good case.
          return 42.0
  
  >>> function(1)
  42.0
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



[1]: https://docs.python.org/3/glossary.html#term-abstract-base-class
[2]: https://en.wikipedia.org/wiki/Type_introspection

# Quick Start

## Install

```
pip install magic-constraints
```

## Usage Of ABCs

You can invoke `isinstance`/`issubclass` operatios on `Sequence/MutableSequence/ImmutableSequence`:

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

```
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
    NoneType,
)
```

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

```
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

```python
>>> func1('key', [1, 2, 3])
{'key': [1, 2, 3]}
>>> 
>>> func1('42 is not a sequence', 42)
Traceback (most recent call last):
...
magic_constraints.exception.MagicTypeError: 
MagicTypeError: argument unmatched.
-----------------------------------
argument: 42
parameter: Parameter(name='bar', type_=Sequence[int])
-----------------------------------
>>> 
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

# `magic_constrains.types`

Supported ABCs and avaliable forms of specialization:

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

speical  ::=  | Union             [ type, ... ]
              | Any
              | NoneType
              
```

Explanations are as follow.

`type` means type object in Python. `abc` defines several supported ABCs. `speical` defines some type objects for some special purposes.

## `sequence`

`Sequence` is equivalent to [collections.abc.Sequence][3]. `MutableSequence` is equivalent to [collections.abc.MutableSequence][4]. `ImmutableSequence` is a `Sequence` that is not a `MutableSequence`.

`Sequence[ type ]` specializes `Sequence`, accepting a sequence with instances of `type`.

`Sequence[ type, ... ]` specialized `Sequence`, accepting a sequence with instances of exactly mapping of `type, ...`. For example, `Sequence[int, float]` accepts `(1, 2.0)` or `[1, 2.0]`.

## `set`

`Set` is equivalent to [collections.abc.Set][5]. `MutableSet` is equivalent to [collections.abc.MutableSet][6]. `ImmutableSet` is a `Set` that is not a `MutableSet`.

`Set[ type ]` specializes `Sequence`, accepting a set with instances of `type`.

## `mapping`

`Mapping` is equivalent to [collections.abc.Mapping][7]. `MutableMapping` is equivalent to [collections.abc. MutableMapping][8]. `ImmutableMapping` is equivalent to [types.MappingProxyType][9].

`Mapping[ key_type, val_type ]` specializes `Mapping`, accepting items with key of `key_type` and value of `val_type`.

## `iterable`

`Iterable` is equivalent to [collections.abc.Iterable][10].

Dual to the side effect of iterating the iterable, `isinstance(instance, Iterable[ type ])` and `isinstance(instance, Iterable[ type, ... ])` always return `False`.

`Iterable[ type ](iterable)` and `Iterable[ type, ... ](iterable)` creates a iterable proxy with lazy type instrospection on its elements. Example:
	
```python
for i in Iterable[int]([1, 2, 3]):
    print(i)
``` 

## `iterator`

`Iterator` is equivalent to [collections.abc.Iterator][11].

Dual to the side effect of iterating the iterator, `isinstance(instance, Iterator[ type ])` and `isinstance(instance, Iterator[ type, ... ])` always return `False`.

`Iterator[ type ](iterator)` and `Iterator[ type, ... ](iterator)` creates a iterator proxy with lazy type instrospection on the elements. Example:
	
```python
for i in Iterator[int](iter([1, 2, 3])):
    print(i)
``` 

## `special`

`Union[ type, ... ]` acceps instance that match one of `type, ...`. For example, `isinstance(42, Union[int, float]` returns `True`.

`Any` accepts any object, including type and non-type objects. It's guaranteed that `isinstance(..., Any)` returns `True` and `issubclass(..., Any)` returns `True`.

`NoneType` is an alias of `type(None)`.

[3]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence
[4]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence
[5]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Set
[6]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet
[7]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping
[8]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping
[9]: https://docs.python.org/3.4/library/types.html#types.MappingProxyType
[10]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
[11]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator

# `magic_constrains.decorator`

`magic_constrains` provides following decorators for parameter declaration:

* `function_constraints`
* `method_constraints`
* `class_initialization_constraints`

## `function_constraints`

`function_constraints` is a function decorator supporting three forms of invocations:

1. `function_constraints(function)`
1. `function_constraints(*type_objects, return_type=None)`
1. `function_constraints(*contraints)`

### `function_constraints(function)`

Example:

```python
# py3 annotation.
@function_constraints
def func1(foo: str, bar: Sequence[int]) -> Mapping[str, Sequence[int]]:
    return {foo: bar}
    
# py2 annotation hack.
# NOT RECOMMENDED. Use the forms described later instead.
def func2(foo, bar):
    return {foo: bar}

func2.__annotations__ = {
    'foo': str,
    'bar': Sequence[int],
    'return': Mapping[str, Sequence[int]],
}

func2 = function_constraints(func2)
```

Each parameter should be bound with a type annotation. If missing, a `SyntaxError` would be raised. Return type can be omitted. If return type is omitted, it defaults to `Any`.

```python
# func1 is equivalent to func2.

@function_constraints
def func1():
    pass
    
@function_constraints
def func2() -> Any:
    pass
```

### `function_constraints(*type_objects, return_type=Any)`

Example:

```python
@function_constraints(
    str, Sequence[int],
    return_type=Mapping[str, Sequence[int]],
)
def func2(foo, bar=None):
    return {foo: bar}
```

In this case, `type_objects` should be an `n`-tuple of type objects, `n` equals to the
number of parameters in the decorated function. Keyword-only parameter `return_type` accepts a type object to indicate the type of return value. If omitted, `return_type` defaults to `Any`, meaning that there's no restriction on the return value.

There are rules should be followed:

* Only parameters with the the kind of `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` are accepted, see [inspect.Parameter.kind][12] for more information.
* Parameter without default value is treated as non-`nullable` and with no `default` value. `nullable` and `default` will be explained in the usage of `Parameter`.
* Parameter with `None` as its default value is treated as `nullable` and with `default` bound to `None`.
* Parameter with any default value other than `None` is treated as non-`nullable` and with `default` bound to such value.


### `function_constraints(*contraints)`

Example:

```python
# explicitly declare Parameter and ReturnType.
@function_constraints(
    Parameter('foo', str),
    Parameter('bar', Sequence[int], nullable=True, default=[1, 2, 3]),
    ReturnType(Mapping[str, Sequence[int]]),
)
def func3(args):
    return {args.foo: args.bar}
```

In this case, `contraints` accepts one or more instances of `Parameter` and `ReturnType`, with following restrictions:

* `contraints` should not be empty.
* `contraints` could only contains instances of `Parameter` and `ReturnType`, otherwise a `TypeError` will be raised.
* Instance of `ReturnType` can be omitted. If omitted, there's no restriction on the return value. If not omitted, instance of `ReturnType` must be placed as the last element of `contraints`, otherwise a `SyntaxError` will be raised.

After checking the input arguments in runtime, thoses arguments will
be bound to a single object as its attributes. Hence, user-defined function, that is, the one decorated by `function_constraints`
should accept only one `POSITIONAL_ONLY` argument.

#### `Parameter(name, type_, nullable=False, default=None, validator=None)`

* `name` is name of parameter. `name` must follows [the rule of defining identifier][13] of Python.
* `type_` defines the type valid argument, should be a type object.
* (optional) `nullable=True` means the parameter can accept `None` as its value. If omitted, `nullable=False`, meaning that `None` is not accepted. But there are some exceptional cases:
  * If `type_` is `Any`, `nullable` is ignored, since `Any` could accept any kinds of argument.
  * If `type_` is `NoneType`, `nullable` is ignored, since `NoneType` is the type of `None`.
* (optional) `default` defines the default value of parameter. If omitted and there is no argument could be bound to the parameter in the runtime, a `SyntaxError` will be raised.
* (optional) `validator` accepts a callable with a single positional argument and returns a boolean value. If defined, `validator` will be invoked after the type introspection. If `validator` returns `False`, a `TypeError` will be raised.

#### `ReturnType(type_, nullable=False, validator=None)`

`ReturnType` accepts less arguments than `Parameter`. The meaning of `ReturnType`'s parameter is identical to `Parameter`, see `Parameter` for the details.

[12]: https://docs.python.org/3.5/library/inspect.html#inspect.Parameter.kind
[13]: https://docs.python.org/2/reference/lexical_analysis.html#identifiers

## `method_constraints`

`method_constraints` is a method decorator supporting three forms of invocations:

1. `method_constraints(method)`
1. `method_constraints(*type_objects, return_type=None)`
1. `method_constraints(*contraints)`

`method_constraints` is almost identical to `function_constraints`, except that `method_constraints` decorates [method][14] instead of [function][15]. Make sure you understand what the method is. See `function_constraints` for more details.

Here's the example of usage:

```python
from magic_constraints import method_constraints, Parameter

class Example(object):

    @method_constraints
    def method1(self, foo: int, bar: float) -> float:
        return foo + bar

    @classmethod
    @method_constraints(
        int, float, int, str,
    )
    def method2(cls, a, b, c=42, d=None):
        return a, b, c, d

    @method_constraints(
        Parameter('a', int),
        Parameter('b', float),
        Parameter('c', int, default=42),
        Parameter('d', str, nullable=True, default=None),
    )
    def method3(self, args):
        return args.a, args.b, args.c, args.d
```

[14]: https://docs.python.org/3/glossary.html#term-method
[15]: https://docs.python.org/3/glossary.html#term-function

## `class_initialization_constraints`

`class_initialization_constraints` is a class decorator requires a class with `INIT_PARAMETERS` attribute. `INIT_PARAMETERS` should be a sequence contains one or more instances of `Parameter` and `ReturnType`. Restriction of `INIT_PARAMETERS` is identical to the `contraints` introduced in `function_constraints(*contraints)` section.

After decoration, `class_initialization_constraints` will inject a `__init__` for argument processing. After type/value checking, accepted arguments will be bound to `self` as its attributes. User-defined `__init__`, within the decorated class or the superclass, will be invoked with a single argument `self` within the injected `__init__`. As a consequence, user-defined `__init__` should not define any parameter except for `self`.

Example:

```python
from magic_constraints import class_initialization_constraints, Parameter

@class_initialization_constraints
class Example(object):
                                  
    INIT_PARAMETERS = [
        Parameter('a', int),
    ]
                                  
    def __init__(self):
        assert self.a == 1
```
