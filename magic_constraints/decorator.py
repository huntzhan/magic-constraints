# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import types

from magic_constraints.parameter_declaration import (
    build_parameters_decl_package,
)
from magic_constraints.argument_processing import (
    transform_to_slots, bind_arguments,
)
from magic_constraints.utils import MagicArguments, nontype_object


class AttributesBinder(object):

    def __init__(self, obj, warning):
        self.obj = obj
        self.warning = warning

    def __call__(self, attr, val):
        if self.warning and attr in self.obj.__dict__:
            raise TypeError(
                'override attr {0}'.format(attr),
            )
        setattr(self.obj, attr, val)


def function_parameter(
        raw_parameter_decls,
        # 1.
        # pass_by_function_argument=True,
        # 2.
        # pass_by_function_attributes=False,
        # no_warning_on_func_attr=False,
):
    pdp = build_parameters_decl_package(raw_parameter_decls)

    def decorator(func):
        if not isinstance(func, types.FunctionType):
            raise TypeError(
                '{0} should be FunctionType.'.format(func),
            )

        def wrapper(*args, **kwargs):

            slots = transform_to_slots(pdp, *args, **kwargs)

            magic_args = MagicArguments()
            bind_callback = AttributesBinder(magic_args, False)
            bind_arguments(pdp.parameter_decls, slots, bind_callback)

            return func(magic_args)

        return wrapper
    return decorator


def method_parameter(
        raw_parameter_decls,
        # 1.
        pass_by_function_argument=False,
        # 2.
        pass_by_cls_or_self_attributes=False,
        no_warning_on_cls_or_self_attributes=True,
        # 3.
        # pass_by_function_attributes=False,
        # no_warning_on_func_attr=False,
):
    if not any([pass_by_function_argument, pass_by_cls_or_self_attributes]):
        raise SyntaxError(
            'please choose the way to pass arguments.'
        )

    pdp = build_parameters_decl_package(raw_parameter_decls)

    def decorator(func):
        if not isinstance(func, types.FunctionType):
            raise TypeError(
                '{0} should be FunctionType.'.format(func),
            )

        def wrapper(cls_or_self, *args, **kwargs):

            slots = transform_to_slots(pdp, *args, **kwargs)

            if pass_by_function_argument:
                magic_args = MagicArguments()
                warning = False
            elif pass_by_cls_or_self_attributes:
                magic_args = cls_or_self
                warning = not no_warning_on_cls_or_self_attributes

            bind_callback = AttributesBinder(magic_args, warning)
            bind_arguments(pdp.parameter_decls, slots, bind_callback)

            if pass_by_function_argument:
                return func(cls_or_self, magic_args)
            elif pass_by_cls_or_self_attributes:
                return func(cls_or_self)

        return wrapper
    return decorator


def method_init_parameter(raw_parameter_decls):
    return method_parameter(
        raw_parameter_decls,
        pass_by_cls_or_self_attributes=True,
        no_warning_on_cls_or_self_attributes=True,
    )


def class_init_parameter(user_defined_class):

    if nontype_object(user_defined_class):
        raise SyntaxError(
            '{0} is not a class.'.format(user_defined_class),
        )

    raw_parameter_decls = getattr(
        user_defined_class,
        'PARAMETERS',
        None,
    )

    predefined_init = getattr(
        user_defined_class,
        '__init__',
    )

    @method_init_parameter(raw_parameter_decls)
    def init(self):
        predefined_init(self)

    setattr(user_defined_class, '__init__', init)

    return user_defined_class
