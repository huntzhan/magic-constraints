# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import types
from funcsigs import signature
from funcsigs import Parameter as SigParameter

from magic_constraints.parameter import (
    Parameter, build_parameter_package,
)
from magic_constraints.argument import (
    transform_to_slots, check_and_bind_arguments,
)
from magic_constraints.utils import nontype_object


class CompoundArgument(object):
    pass


class AttributesBinder(object):

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, attr, val):
        setattr(self.obj, attr, val)


def raise_on_non_function(function):
    if not isinstance(function, types.FunctionType):
        raise TypeError(
            '{0} should be FunctionType.'.format(function),
        )


def raise_on_non_parameters(parameters):
    for p in parameters:
        if isinstance(p, Parameter):
            continue
        else:
            raise SyntaxError(
                '{0} is not the instance of Parameter.'.format(p),
            )


def build_parameters_by_function_inspection(type_args, function, fi):
    argument_sigs = signature(function)

    if len(argument_sigs.parameters) - fi != len(type_args):
        raise SyntaxError(
            'length of arguments not match.',
        )

    parameters = []
    ti = 0
    for name, sig_parameter in argument_sigs.parameters.items():
        if fi > 0:
            fi -= 1
            continue

        if sig_parameter.kind not in [
            SigParameter.POSITIONAL_ONLY,
            SigParameter.POSITIONAL_OR_KEYWORD
        ]:
            raise SyntaxError(
                'not support argument [{0}] with the kind of [{1}].'.format(
                    name, SigParameter.kind,
                ),
            )

        if sig_parameter.default is sig_parameter.empty:
            # no default.
            parameters.append(
                Parameter(name, type_args[ti]),
            )
        else:
            parameters.append(
                Parameter(name, type_args[ti], default=sig_parameter.default),
            )
        ti += 1

    return build_parameter_package(parameters)


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

    if nontype_object(user_defined_class):
        raise SyntaxError(
            '{0} is not a class.'.format(user_defined_class),
        )

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
