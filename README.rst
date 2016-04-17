magic-parameter |Build Status|
==============================

**WARNING: Interfaces of this project is UNSTABLE, might be changed in
the future!**

``magic-parameter`` handles type checking for you.

Install
-------

::

    pip install magic-parameter

Supports Python 2.7 and 3.3+.

Usage
-----

Concepts
~~~~~~~~

Parameter Declaration:

-  ``(<name>, <type declaration>)``
-  ``(<name>, <type declaration>, <default value>)``
-  ``(<name>, <type declaration>, None)``

Type Declaration:

-  any **type object**, i.e. ``list``, ``int``, ``str``, ``FooBar``.
-  instance of ``magic-parameter.<nested type>``:

   -  ``magic_parameter.list_t(<type declaration>)``
   -  ``magic_parameter.tuple_t(<type declaration>)``
   -  ``magic_parameter.set_t(<type declaration>)``
   -  ``magic_parameter.dict_t(<key type declaration>, <val type declaration>)``

-  instance of ``magic-parameter.<relation type>``

   -  ``magic_parameter.or_t(<type declaration>, ...)``

Decorators:

-  ``magic_parameter.function_parameter``
-  ``magic_parameter.method_parameter``
-  ``magic_parameter.method_init_parameter``
-  ``magic_parameter.class_init_parameter``

``function_parameter(raw_parameter_decls)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``function_parameter`` is a function decorator.

Flowing example defines a function with parameter ``a`` that accepts
``list`` of ``int``\ s.

.. code:: python

    from magic_parameter import function_parameter, list_t


    @function_parameter([
        ('a', list_t(int)),
    ])
    def func(args):
        return args.a

Runtime:

.. code:: ipython

    In [2]: func([1, 2, 3])
    Out[2]: [1, 2, 3]
    In [3]: func([1, 2.0, 3])
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    ...
    TypeError: Rule:
    name: None
    type: <class 'int'>
    Arg: 2.0

``method_parameter(raw_parameter_decls, pass_by_function_argument=False, pass_by_cls_or_self_attributes=False, no_warning_on_cls_or_self_attributes=True)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``method_parameter`` is a class method decorator. ``method_parameter``
provides two ways to pass arguments:

#. By function argument, same as function\_parameter. In this case,
   ``pass_by_function_argument`` should be set as ``True``.
#. By attributes binding to the first parameter of class method. In this
   case, ``pass_by_cls_or_self_attributes`` should be set as ``True``.
   By default, ``no_warning_on_cls_or_self_attributes=True``, meaning
   there's no warning on attribute override.

Flowing example defines a class with two methods:

#. ``func1`` is a ``classmethod`` with a parameter ``a``, accepting a
   ``dict`` with ``str`` as its key and ``int`` as its value.
#. ``func2`` is a function with a parameter ``a``, accepting a ``list``
   or a ``tuple``.

.. code:: python

    from magic_parameter import method_parameter, dict_t, or_t


    class Example(object):

        @classmethod
        @method_parameter(
            [
                ('a', dict_t(str, int)),
            ],
            pass_by_function_argument=True,
        )
        def func1(cls, args):
            return args.a

        @method_parameter(
            [
                ('a', or_t(list, tuple)),
            ],
            pass_by_cls_or_self_attributes=True,
        )
        def func2(self):
            return self.a

Runtime:

.. code:: ipython

    In [8]: Example.func1({'k1': 1, 'k2': 2})
    Out[8]: {'k1': 1, 'k2': 2}
    In [9]: Example.func1({'k1': 1, 1: 2})
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    ...
    TypeError: Rule:
    name: None
    type: <class 'str'>
    Arg: 1

    In [16]: example = Example()

    In [17]: example.func2([1, 2, 3])
    Out[17]: [1, 2, 3]

    In [18]: example.func2((1, 2, 3))
    Out[18]: (1, 2, 3)

    In [19]: example.func2(1)
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    ...
    TypeError: 1 cannot match [<magic_parameter.type_declaration.TypeDecl object at 0x1076ac048>, <magic_parameter.type_declaration.TypeDecl object at 0x1076ac080>]

``method_init_parameter(raw_parameter_decls)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``method_init_parameter`` could be viewed as ``method_parameter`` with
``pass_by_cls_or_self_attributes=True, no_warning_on_cls_or_self_attributes=True``
partial binding. It's designed to declare the parameters of ``__init__``
class method.

Following example defines a class accepting an ``int`` for the
initialization.

.. code:: python

    from magic_parameter import method_init_parameter


    class Example(object):

        @method_init_parameter([
            ('a', int),
        ])
        def __init__(self):
            print(self.a)

Runtime:

.. code:: ipython

    In [3]: Example(1)
    1
    Out[3]: <__main__.Example at 0x1029bda20>

    In [4]: Example(1.0)
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    ...
    TypeError: Rule:
    name: None
    type: <class 'int'>
    Arg: 1.0

``class_init_parameter(user_defined_class)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``class_init_parameter`` is a class decorator. ``class_init_parameter``
will extract parameter declarations from
``user_defined_class.PARAMETERS``, then inject a ``__init__`` function
to ``user_defined_class``.

Following example defines a class accepting an ``int`` for the
initialization.

.. code:: python

    from magic_parameter import class_init_parameter


    @class_init_parameter
    class Example1(object):

        PARAMETERS = [
            ('a', int),
        ]


    @class_init_parameter
    class Example2(object):

        PARAMETERS = [
            ('a', int),
        ]

        def __init__(self):
            print(self.a)

Runtime:

.. code:: ipython

    In [5]: Example1(1)
    Out[5]: <f.Example1 at 0x106b529b0>

    In [6]: Example1(a=1)
    Out[6]: <f.Example1 at 0x106ba83c8>

    In [7]: Example1(1.0)
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    ...
    TypeError: Rule:
    name: None
    type: <class 'int'>
    Arg: 1.0

    In [8]: Example2(1)
    1
    Out[8]: <f.Example2 at 0x107405828>

.. |Build Status| image:: https://travis-ci.org/huntzhan/magic-parameter.svg?branch=master
   :target: https://travis-ci.org/huntzhan/magic-parameter
