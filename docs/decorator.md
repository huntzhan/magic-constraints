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

Type checking on the default value happens during function inspection. If default value is not an instance of corresponding type annotation, a `TypeError` will be raised.

### `function_constraints(*type_objects, return_type=Any)`

Example:

```python
@function_constraints(
    str, Sequence[int],
    # return value could be None or a sequence of ints.
    return_type=Optional[Mapping[str, Sequence[int]]],
)
def func2(foo, bar):
    return {foo: bar}
```

In this case, `type_objects` should be an `n`-tuple of type objects, `n` equals to the
number of parameters in the decorated function. Keyword-only parameter `return_type` accepts a type object to indicate the type of return value. If omitted, `return_type` defaults to `Any`, meaning that there's no restriction on the return value.

There are rules should be followed:

* Only parameters with the the kind of `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` are accepted, see [inspect.Parameter.kind][12] for more information.
* If default value exists and it is not an instance of corresponding type, a `TypeError` will be raised.

### `function_constraints(*contraints)`

Example:

```python
# explicitly declare Parameter and ReturnType.
@function_constraints(
    Parameter('foo', str),
    # bar accepts None or a sequence of ints.
    Parameter('bar', Optional[Sequence[int]], default=[1, 2, 3]),
    ReturnType(Mapping[str, Sequence[int]]),
)
def func3(args):
    return {args.foo: args.bar}
```

In this case, `contraints` accepts one or more instances of `Parameter` and `ReturnType`, with following restrictions:

* `contraints` should not be empty.
* `contraints` could only contains instances of `Parameter` and `ReturnType`, otherwise a `TypeError` will be raised.
* Instance of `ReturnType` can be omitted. If omitted, there's no restriction on the return value. If not omitted, instance of `ReturnType` must be placed as the last element of `contraints`, otherwise a `SyntaxError` will be raised.

After checking the input arguments in runtime, those arguments will
be bound to a single object as its attributes. Hence, user-defined function, that is, the one decorated by `function_constraints`
should accept only one `POSITIONAL_ONLY` argument.

#### `Parameter(name, type_, default=None, validator=None)`

* `name` is name of parameter. `name` must follows [the rule of defining identifier][13] of Python.
* `type_` defines the type valid argument, should be a type object.
* (optional) `default` defines the default value of parameter. If omitted and there is no argument could be bound to the parameter in the runtime, a `SyntaxError` will be raised.
* (optional) `validator` accepts a callable with a single positional argument and returns a boolean value. If defined, `validator` will be invoked after the type introspection. If `validator` returns `False`, a `TypeError` will be raised.

#### `ReturnType(type_, validator=None)`

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
        int, float, int, Optional[str],
    )
    def method2(cls, a, b, c=42, d=None):
        return a, b, c, d

    @method_constraints(
        Parameter('a', int),
        Parameter('b', float),
        Parameter('c', int, default=42),
        Parameter('d', Optional[str], default=None),
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

