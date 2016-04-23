magic-constraints
=================

| |PyPI| |Build
  Status|
| |Coverage Status|

Introduction
------------

``magic-constraints`` supports:

#. `type
   introspection <https://en.wikipedia.org/wiki/Type_introspection>`__
   on "specialized" `abstract base
   classes <https://docs.python.org/3/glossary.html#term-abstract-base-class>`__
   (kind of).
#. declaration and dynamic chekcing on the parameters of
   function/method.

Quick Start
-----------

Install
~~~~~~~

::

    pip install magic-constraints

Abstract Base Classes Introspection:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``magic-constraints`` implemented a few ABCs for type introspection.

Details will be presented in the next section. Example:

.. code:: python

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

Declaration on function parameters:

.. code:: python

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

Parameter checking:

.. code:: python

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

``magic_constrains.types``
--------------------------

Supported ABCs and avaliable specialization of ABCs:

::

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

Explanations are as follow.

``type`` means type object in Python. ``abc`` defines several supported
ABCs. ``speical`` defines some type objects for some spectial purposes.

``sequence``:

-  ``Sequence`` is equivalent to
   `collections.abc.Sequence <https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence>`__.
   ``MutableSequence`` is equivalent to
   `collections.abc.MutableSequence <https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence>`__.
   ``ImmutableSequence`` is a ``Sequence`` that is not a
   ``MutableSequence``.
-  ``Sequence[ type ]`` specializes ``Sequence``, accepting a sequence
   with instances of ``type``.
-  ``Sequence[ type, ... ]`` specialized ``Sequence``, accepting a
   sequence with instances of exactly mapping of ``type, ...``. For
   example, ``Sequence[int, float]`` accepts ``(1, 2.0)`` or
   ``[1, 2.0]``.

``set``:

-  ``Set`` is equivalent to
   `collections.abc.Set <https://docs.python.org/3/library/collections.abc.html#collections.abc.Set>`__.
   ``MutableSet`` is equivalent to
   `collections.abc.MutableSet <https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet>`__.
   ``ImmutableSet`` is a ``Set`` that is not a ``MutableSet``.
-  ``Set[ type ]`` specializes ``Sequence``, accepting a set with
   instances of ``type``.

``mapping``:

-  ``Mapping`` is equivalent to
   `collections.abc.Mapping <https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping>`__.
   ``MutableMapping`` is equivalent to `collections.abc.
   MutableMapping <https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping>`__.
   ``ImmutableMapping`` is equivalent to
   `types.MappingProxyType <https://docs.python.org/3.4/library/types.html#types.MappingProxyType>`__.
-  ``Mapping[ key_type, val_type ]`` specializes ``Mapping``, accepting
   items with key of ``key_type`` and value of ``val_type``.

``iterable``:

-  ``Iterable`` is equivalent to
   `collections.abc.Iterable <https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable>`__.
-  Dual to the side effect of iterating the iterable,
   ``isinstance(instance, Iterable[ type ])`` and
   ``isinstance(instance, Iterable[ type, ... ])`` always return
   ``False``.
-  ``Iterable[ type ](iterable)`` and
   ``Iterable[ type, ... ](iterable)`` creates a iterable proxy with
   lazy type instrospection on the elements. Example:

   .. code:: python

       for i in Iterable[int]([1, 2, 3]):
           print(i)

``iterator``:

-  ``Iterator`` is equivalent to
   `collections.abc.Iterator <https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator>`__.
-  Dual to the side effect of iterating the iterator,
   ``isinstance(instance, Iterator[ type ])`` and
   ``isinstance(instance, Iterator[ type, ... ])`` always return
   ``False``.
-  ``Iterator[ type ](iterator)`` and
   ``Iterator[ type, ... ](iterator)`` creates a iterator proxy with
   lazy type instrospection on the elements. Example:

   .. code:: python

       for i in Iterator[int](iter([1, 2, 3])):
           print(i)

``special``:

-  ``Any`` accepts any object, including type and non-type objects. It's
   guaranteed that ``isinstance(..., Any)`` returns ``True`` and
   ``issubclass(..., Any)`` returns ``True``.
-  ``Union[ type, ... ]`` acceps instance that match one of
   ``type, ...``. For example, ``isinstance(42, Union[int, float]``
   returns ``True``.

``magic_constrains.decorator``
------------------------------

``magic_constrains`` provides following decorators for parameter
declaration:

-  ``function_constraints``
-  ``method_constraints``
-  ``class_initialization_constraints``

``function_constraints``
~~~~~~~~~~~~~~~~~~~~~~~~

``function_constraints`` supports two forms of invocations:

#. ``function_constraints(<type object>, ...)``
#. ``function_constraints(Parameter(name, <type object>, nullable=False, default=None), ..., pass_by_compound=True)``

Example:

.. code:: python

    from magic_constraints import function_constraints, Parameter


    @function_constraints(
        int, float, int, str,
    )
    def form1(a, b, c=42, d=None):
        return a, b, c, d


    @function_constraints(
        Parameter('a', int),
        Parameter('b', float),
        Parameter('c', int, default=42),
        Parameter('d', str, nullable=True, default=None),
        pass_by_compound=True,
    )
    def form2(args):
        return args.a, args.b, args.c, args.d

``form1`` of ``function_constraints`` accepts ``n`` type objects, ``n``
equals to the number of parameters of the function decorated by
``function_constraints``. There are some several promises on the form of
parameter:

-  only the ``POSITIONAL_ONLY`` or ``POSITIONAL_OR_KEYWORD`` parameters
   are accepted, see
   `inspect.Parameter.kind <https://docs.python.org/3.5/library/inspect.html#inspect.Parameter.kind>`__
   for more information.
-  parameter without default value is treated as non-\ ``nullable`` and
   without ``default``. This concepts will be introduced in the field of
   ``Parameter``.
-  parameter with default value other than ``None`` is treated as
   non-\ ``nullable`` and with ``default`` bound to such value.
-  parameter with ``None`` as its default value is treated as
   ``nullable`` and with ``default`` bound to ``None``.

``form2`` is enable by passing the keyword-only argument
``pass_by_compound=True`` to ``function_constraints``. ``form2`` accepts
arbitrary number of ``Parameter`` instances. After checking the input
arguments in runtime, thoses arguments will be bound to a single object
as its attributes. Hence, in this cases user-defined function, that is,
the one decorated by ``function_constraints`` should define only one
``POSITIONAL_ONLY`` argument.

Signature of Parameter:
``Parameter(name, type_, nullable=False, default=None, callback=None)``.
Explanation:

-  ``name`` is name of parameter. ``name`` must follows `the rule of
   defining
   identifier <https://docs.python.org/2/reference/lexical_analysis.html#identifiers>`__
   of Python.
-  ``type_`` defines the type of accepted instances, should be a type
   object.
-  (optional) ``nullable=True`` means the parameter can accept ``None``
   as its value, independent of ``type_``. If omitted,
   ``nullable=False``.
-  (optional) ``default`` defines the default value of parameter. If
   omitted and there is no argument could be bound to the parameter in
   the runtime, ``MagicSyntaxError`` will be raised.
-  (optional) ``callback`` accepts a callable that with single
   positional argument and returns a boolean value. If defined,
   ``callback`` will be invoked after the type introspection. If
   ``callback`` returns ``False``, ``MagicTypeError`` will be raised.

``method_constraints``
~~~~~~~~~~~~~~~~~~~~~~

``method_constraints`` is almost identical to ``function_constraints``,
except that ``method_constraints`` decorates
`method <https://docs.python.org/3/glossary.html#term-method>`__ instead
of `function <https://docs.python.org/3/glossary.html#term-function>`__.
Make sure you understand what the method is. Here's a example of usage:

.. code:: python

    from magic_constraints import method_constraints, Parameter


    class Example(object):

        @classmethod
        @method_constraints(
            int, float, int, str,
        )
        def form1(cls, a, b, c=42, d=None):
            return a, b, c, d

        @method_constraints(
            Parameter('a', int),
            Parameter('b', float),
            Parameter('c', int, default=42),
            Parameter('d', str, nullable=True, default=None),
            pass_by_compound=True,
        )
        def form2(self, args):
            return args.a, args.b, args.c, args.d

``class_initialization_constraints``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``class_initialization_constraints`` is a class decorator requires a
class with ``INIT_PARAMETERS`` attribute. ``INIT_PARAMETERS`` should be
a sequence of ``Parameter`` instances. After decoration,
``class_initialization_constraints`` will inject a ``__init__`` for
argument processing. Similar to ``pass_by_compound=True``, accepted
arguments will be bound to ``self``. User-defined ``__init__``, within
the decorated class or the superclass, will be invoked with single
argument ``self``. As a consequence, user-defined ``__init__`` should
not define any argument except ``self``.

Example:

.. code:: python

    from magic_constraints import class_initialization_constraints, Parameter


    @class_initialization_constraints
    class Example(object):
                                      
        INIT_PARAMETERS = [
            Parameter('a', int),
        ]
                                      
        def __init__(self):
            assert self.a == 1

.. |PyPI| image:: https://img.shields.io/pypi/pyversions/magic_constraints.svg
   :target: https://pypi.python.org/pypi/magic_constraints
.. |Build
Status| image:: https://travis-ci.org/huntzhan/magic-constraints.svg?branch=master
   :target: https://travis-ci.org/huntzhan/magic-constraints
.. |Coverage Status| image:: https://coveralls.io/repos/github/huntzhan/magic-constraints/badge.svg?branch=master
   :target: https://coveralls.io/github/huntzhan/magic-constraints?branch=master
