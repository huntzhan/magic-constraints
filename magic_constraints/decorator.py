# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints.parameter import (
    build_parameter_package,
)
from magic_constraints.argument import (
    transform_to_slots, check_and_bind_arguments,
)
from magic_constraints.utils import (
    CompoundArgument,
    AttributesBinder,
    raise_on_non_function,
    raise_on_non_parameters,
    raise_on_nontype_object,
    build_parameters_by_function_inspection,
)


# @function_constraints(
#     int, float,
# )
# def function(foo, bar=1.0):
#     return foo + bar
#
#
def _function_constraints_pass_by_positional_args(type_args):

    def decorator(function):
        raise_on_non_function(function)

        parameter_package = build_parameters_by_function_inspection(
            type_args,
            function, 0,
        )

        def wrapper(*args, **kwargs):

            slots = transform_to_slots(parameter_package, *args, **kwargs)
            check_and_bind_arguments(
                parameter_package.parameters, slots, lambda name, arg: None,
            )

            return function(*slots)
        return wrapper
    return decorator


# @function_constraints(
#     Parameter('foo', int),
#     Parameter('bar', float, default=1.0),
#     pass_by_compound=True,
# )
# def function(args):
#     return args.foo + args.bar
#
#
def _function_constraints_pass_by_compound_args(parameters):
    raise_on_non_parameters(parameters)

    parameter_package = build_parameter_package(parameters)

    def decorator(function):
        raise_on_non_function(function)

        def wrapper(*args, **kwargs):

            slots = transform_to_slots(parameter_package, *args, **kwargs)

            compound_args = CompoundArgument()
            bind_callback = AttributesBinder(compound_args)

            check_and_bind_arguments(parameters, slots, bind_callback)

            return function(compound_args)
        return wrapper
    return decorator


def function_constraints(*args, **options):
    if not args:
        raise SyntaxError(
            'args should not be empty',
        )

    if options.get('pass_by_compound', False):
        return _function_constraints_pass_by_compound_args(args)
    else:
        return _function_constraints_pass_by_positional_args(args)


# @method_constraints(
#     int, float,
# )
# def method(self_or_cls, foo, bar):
#     return foo + bar
def _method_constraints_pass_by_positional_args(type_args):

    def decorator(function):
        raise_on_non_function(function)

        parameter_package = build_parameters_by_function_inspection(
            type_args,
            function, 1,
        )

        def wrapper(self_or_cls, *args, **kwargs):

            slots = transform_to_slots(parameter_package, *args, **kwargs)
            check_and_bind_arguments(
                parameter_package.parameters, slots, lambda name, arg: None,
            )

            return function(self_or_cls, *slots)
        return wrapper
    return decorator


# @method_constraints(
#     Parameter('foo', int),
#     Parameter('bar', float, default=1.0),
#     pass_by_compound=True,
# )
# def method(self_or_cls, args):
#     return args.foo + args.bar
#
#
def _method_constraints_pass_by_compound_args(parameters):
    raise_on_non_parameters(parameters)

    parameter_package = build_parameter_package(parameters)

    def decorator(function):
        raise_on_non_function(function)

        def wrapper(self_or_cls, *args, **kwargs):

            slots = transform_to_slots(parameter_package, *args, **kwargs)

            compound_args = CompoundArgument()
            bind_callback = AttributesBinder(compound_args)

            check_and_bind_arguments(parameters, slots, bind_callback)

            return function(self_or_cls, compound_args)
        return wrapper
    return decorator


def method_constraints(*args, **options):
    if not args:
        raise SyntaxError(
            'args should not be empty',
        )

    if options.get('pass_by_compound', False):
        return _method_constraints_pass_by_compound_args(args)
    else:
        return _method_constraints_pass_by_positional_args(args)


# @class_initialization_constraints
# class FooBar(object):
#
#     INIT_PARAMETERS = [
#         Parameter('foo', int),
#         Parameter('bar', float, default=1.0),
#     ]
def class_initialization_constraints(user_defined_class):
    raise_on_nontype_object(user_defined_class)

    parameters = getattr(user_defined_class, 'INIT_PARAMETERS', None)
    raise_on_non_parameters(parameters)
    parameter_package = build_parameter_package(parameters)

    predefined_init = getattr(
        user_defined_class,
        '__init__',
    )

    def init(self, *args, **kwargs):

        slots = transform_to_slots(parameter_package, *args, **kwargs)
        bind_callback = AttributesBinder(self)
        check_and_bind_arguments(parameters, slots, bind_callback)

        predefined_init(self)

    setattr(user_defined_class, '__init__', init)

    return user_defined_class
