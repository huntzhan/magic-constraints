# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import collections as abc
from functools import wraps

# TODO: fix that later.
from funcsigs import Parameter as SigParameter

from magic_constraints.exception import (
    MagicSyntaxError,
    MagicTypeError,
)

from magic_constraints.constraint import (
    Constraint,

    build_constraints_package,
    build_constraints_with_given_type_args,
    build_constraints_with_annotation,
    build_return_type,

    raise_on_non_constraints,
    raise_on_non_parameters,
)

from magic_constraints.argument import (
    transform_to_slots, check_and_bind_arguments,
)

from magic_constraints.utils import (
    CompoundArgument,
    AttributesBinder,

    type_object,

    raise_on_non_callable,
    raise_on_nontype_object,
)


def decorator_dispather(
        args, options,
        by_positional, by_only_return_type_checking,
        by_compound, by_inspection):

    if not args and 'return_type' not in options:
        raise MagicSyntaxError(
            'empty args with no return_type option.',
        )

    if len(args) == 1 and args[0] is Ellipsis:
        return by_only_return_type_checking(
            options.get('return_type', SigParameter.empty),
        )

    elif 'return_type' in options or type_object(args[0]):
        return by_positional(args, options)

    elif isinstance(args[0], Constraint):
        return by_compound(args, options)

    elif len(args) == 1 and isinstance(args[0], abc.Callable):
        return by_inspection(args[0])

    else:
        raise MagicSyntaxError(
            'can not dispatch.',
        )


def check_ret(ret, return_type):
    if not return_type.check_instance(ret):
        raise MagicTypeError(
            'return value unmatched.',
            return_type=return_type,
            ret=ret,
        )


# @function_constraints(
#     int, float,
#     return_type=xxx,
# )
# def function(foo, bar=1.0):
#     return foo + bar
#
#
def _function_constraints_pass_by_positional_args(type_args, options):

    def decorator(function):
        raise_on_non_callable(function)

        input_type_args = [function, False, type_args]
        if 'return_type' in options:
            input_type_args.append(options['return_type'])

        constraints_package = build_constraints_package(
            build_constraints_with_given_type_args(*input_type_args),
        )

        @wraps(function)
        def wrapper(*args, **kwargs):

            slots = transform_to_slots(constraints_package, *args, **kwargs)
            check_and_bind_arguments(
                constraints_package.parameters, slots, lambda name, arg: None,
            )

            ret = function(*slots)
            check_ret(ret, constraints_package.return_type)
            return ret

        return wrapper
    return decorator


# @function_constraints(
#     Parameter('foo', int),
#     Parameter('bar', float, default=1.0),
#     ...,
#     ReturnType(float),
# )
# def function(args):
#     return args.foo + args.bar
#
#
def _function_constraints_pass_by_compound_args(constraints, options):
    raise_on_non_constraints(constraints)

    constraints_package = build_constraints_package(constraints)

    def decorator(function):
        raise_on_non_callable(function)

        @wraps(function)
        def wrapper(*args, **kwargs):

            slots = transform_to_slots(constraints_package, *args, **kwargs)

            compound_args = CompoundArgument()
            bind_callback = AttributesBinder(compound_args)

            check_and_bind_arguments(
                constraints_package.parameters, slots, bind_callback,
            )

            ret = function(compound_args)
            check_ret(ret, constraints_package.return_type)
            return ret

        return wrapper
    return decorator


# @function_constraints
# def function(foo: int, bar: float) -> float:
#     return foo + bar
def _function_constraints_by_inspection(function):
    raise_on_non_callable(function)

    constraints_package = build_constraints_package(
        build_constraints_with_annotation(function, False),
    )

    @wraps(function)
    def wrapper(*args, **kwargs):
        slots = transform_to_slots(constraints_package, *args, **kwargs)
        check_and_bind_arguments(
            constraints_package.parameters, slots, lambda name, arg: None,
        )

        ret = function(*slots)
        check_ret(ret, constraints_package.return_type)
        return ret

    return wrapper


def _function_constraints_by_only_return_type_checking(return_type):

    return_type = build_return_type(return_type)

    def decorator(function):
        raise_on_non_callable(function)

        @wraps(function)
        def wrapper(*args, **kwargs):
            ret = function(*args, **kwargs)
            check_ret(ret, return_type)
            return ret

        return wrapper
    return decorator


def function_constraints(*args, **options):
    return decorator_dispather(
        args, options,
        _function_constraints_pass_by_positional_args,
        _function_constraints_by_only_return_type_checking,
        _function_constraints_pass_by_compound_args,
        _function_constraints_by_inspection,
    )


# @method_constraints(
#     int, float,
#     return_type=xxx,
# )
# def method(self_or_cls, foo, bar):
#     return foo + bar
#
#
def _method_constraints_pass_by_positional_args(type_args, options):

    def decorator(function):
        raise_on_non_callable(function)

        input_type_args = [function, True, type_args]
        if 'return_type' in options:
            input_type_args.append(options['return_type'])

        constraints_package = build_constraints_package(
            build_constraints_with_given_type_args(*input_type_args),
        )

        @wraps(function)
        def wrapper(self_or_cls, *args, **kwargs):

            slots = transform_to_slots(constraints_package, *args, **kwargs)
            check_and_bind_arguments(
                constraints_package.parameters, slots, lambda name, arg: None,
            )

            ret = function(self_or_cls, *slots)
            check_ret(ret, constraints_package.return_type)
            return ret

        return wrapper
    return decorator


# @method_constraints(
#     Parameter('foo', int),
#     Parameter('bar', float, default=1.0),
#     ...,
#     ReturnType(float),
# )
# def method(self_or_cls, args):
#     return args.foo + args.bar
#
#
def _method_constraints_pass_by_compound_args(constraints, options):
    raise_on_non_constraints(constraints)

    constraints_package = build_constraints_package(constraints)

    def decorator(function):
        raise_on_non_callable(function)

        @wraps(function)
        def wrapper(self_or_cls, *args, **kwargs):

            slots = transform_to_slots(constraints_package, *args, **kwargs)

            compound_args = CompoundArgument()
            bind_callback = AttributesBinder(compound_args)

            check_and_bind_arguments(
                constraints_package.parameters, slots, bind_callback,
            )

            ret = function(self_or_cls, compound_args)
            check_ret(ret, constraints_package.return_type)
            return ret

        return wrapper
    return decorator


# @method_constraints
# def method(self_or_cls, foo: int, bar: float) -> float:
#     return foo + bar
def _method_constraints_by_inspection(function):
    raise_on_non_callable(function)

    constraints_package = build_constraints_package(
        build_constraints_with_annotation(function, True),
    )

    @wraps(function)
    def wrapper(self_or_cls, *args, **kwargs):
        slots = transform_to_slots(constraints_package, *args, **kwargs)
        check_and_bind_arguments(
            constraints_package.parameters, slots, lambda name, arg: None,
        )

        ret = function(self_or_cls, *slots)
        check_ret(ret, constraints_package.return_type)
        return ret

    return wrapper


def _method_constraints_by_only_return_type_checking(return_type):

    return_type = build_return_type(return_type)

    def decorator(function):
        raise_on_non_callable(function)

        @wraps(function)
        def wrapper(self_or_cls, *args, **kwargs):
            ret = function(self_or_cls, *args, **kwargs)
            check_ret(ret, return_type)
            return ret

        return wrapper
    return decorator


def method_constraints(*args, **options):
    return decorator_dispather(
        args, options,
        _method_constraints_pass_by_positional_args,
        _method_constraints_by_only_return_type_checking,
        _method_constraints_pass_by_compound_args,
        _method_constraints_by_inspection,
    )


# @class_initialization_constraints
# class FooBar(object):
#
#     INIT_PARAMETERS = [
#         Parameter('foo', int),
#         Parameter('bar', float, default=1.0),
#         ...,
#         ReturnType(float),
#     ]
#
#
def class_initialization_constraints(user_defined_class):
    raise_on_nontype_object(user_defined_class)

    parameters = getattr(user_defined_class, 'INIT_PARAMETERS', None)
    raise_on_non_parameters(parameters)
    constraints_package = build_constraints_package(parameters)

    predefined_init = getattr(
        user_defined_class,
        '__init__',
    )

    def init(self, *args, **kwargs):

        slots = transform_to_slots(constraints_package, *args, **kwargs)
        bind_callback = AttributesBinder(self)
        check_and_bind_arguments(
            parameters, slots, bind_callback,
        )

        predefined_init(self)

    setattr(user_defined_class, '__init__', init)

    return user_defined_class
