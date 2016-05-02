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

speical  ::=  | Union             [ type, ... ]
              | Any
              | Optional          [ type ]
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

`Optional[T]` is equivalent to `Union[T, NoneType]`. 

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
