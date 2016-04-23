# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import sys
import types
from abc import ABCMeta
import collections as abc

from funcsigs import signature
from funcsigs import Parameter as SigParameter


class CompoundArgument(object):
    pass


class AttributesBinder(object):

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, attr, val):
        setattr(self.obj, attr, val)


def type_object(obj):
    return hasattr(obj, '__bases__')


def nontype_object(obj):
    return not type_object(obj)


def raise_on_non_function(function):
    if not isinstance(function, types.FunctionType):
        raise MagicTypeError(
            'require FunctionType.',
            function=function,
        )


def raise_on_non_parameters(parameters):
    if not isinstance(parameters, abc.Iterable):
        raise MagicTypeError(
            'parameter should be Iterable.',
            parameters=parameters,
        )

    for p in parameters:
        if isinstance(p, Parameter):
            continue
        else:
            raise MagicTypeError(
                'require instance of Parameter.',
                p=p,
            )


def raise_on_nontype_object(obj):
    if nontype_object(obj):
        raise MagicTypeError(
            'require type object.',
            obj=obj,
        )


def build_parameters_by_function_inspection(type_args, function, fi):
    argument_sigs = signature(function)

    if len(argument_sigs.parameters) - fi != len(type_args):
        raise MagicSyntaxError(
            'length of arguments not match.',
            type_args=type_args,
            function_signature=argument_sigs.parameters,
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
            raise MagicSyntaxError(
                'supports only POSITIONAL_ONLY '
                'or POSITIONAL_OR_KEYWORD argument.',
                name=name,
                kine=SigParameter.kind,
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


def repr_return(text):
    if sys.version_info.major == 2:
        text = text.encode('utf-8')
    return text


def conditional_repr(obj):
    if isinstance(obj, ABCMeta) and hasattr(obj, 'main_cls'):
        return repr(obj)
    elif type_object(obj):
        return obj.__name__
    else:
        return repr(obj)


from magic_constraints.parameter import (
    Parameter, build_parameter_package,
)  # noqa
from magic_constraints.exception import (
    MagicSyntaxError, MagicTypeError,
)  # noqa
