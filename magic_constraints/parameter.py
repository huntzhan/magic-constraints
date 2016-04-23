# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from collections import namedtuple, Iterable


class Parameter(object):

    def __init__(self, name, type_, **kwargs):
        self.name = name

        raise_on_nontype_object(type_)
        self.type_ = type_

        # key only arguemnt.
        # 1. if nullable, None is accepted.
        self.nullable = kwargs.get('nullable', False)
        # 2. record default value.
        if 'default' in kwargs:
            self.with_default = True
            self.default = kwargs['default']
        else:
            self.with_default = False
            self.default = None
        # 3. user-defined callback on input argument.
        self.callback = kwargs.get(
            'callback', lambda instance: True,
        )

        self._arguments_repr = self._generate_init_arguments_repr(
            name, type_, **kwargs
        )

    def check_argument(self, instance):
        if instance is None:
            if not (self.nullable or issubclass(self.type_, type(None))):
                return False
            else:
                return self.callback(None)
        if not isinstance(instance, self.type_):
            return False
        return self.callback(instance)

    def _generate_init_arguments_repr(self, name, type_, **kwargs):
        # positional arguments.
        prefix = "name={name}, type_={type_}".format(
            name=conditional_repr(name),
            type_=conditional_repr(type_),
        )
        # keyword-only arguments.
        suffix = ', '.join(map(
            lambda p: "{0}={1}".format(p[0], conditional_repr(p[1])),
            sorted(kwargs.items(), key=lambda p: p[0]),
        ))

        # merge.
        if suffix:
            arguemnt_repr = "{0}, {1}".format(prefix, suffix)
        else:
            arguemnt_repr = prefix

        return arguemnt_repr

    def __repr__(self):
        return repr_return(
            'Parameter({})'.format(self._arguments_repr),
        )


def build_parameter_package(parameters):
    if not isinstance(parameters, Iterable):
        raise TypeError(
            'parameter should be Iterable.',
        )

    name_hash = {}
    start_of_defaults = -1

    idx = 0
    for parameter in parameters:
        if not isinstance(parameter, Parameter):
            raise SyntaxError(
                'parameter should be instsance of Parameter.'
            )

        if parameter.name in name_hash:
            raise SyntaxError('duplicates on ' + parameter.name)

        name_hash[parameter.name] = idx

        if parameter.with_default:
            if start_of_defaults < 0:
                start_of_defaults = idx
        else:
            if start_of_defaults >= 0:
                raise SyntaxError(
                    'Parameter without default should be placed '
                    'in front of all parameters with default.'
                )

        idx += 1

    ParameterPackage = namedtuple(
        'ParameterPackage',
        ['parameters', 'name_hash', 'start_of_defaults'],
    )

    return ParameterPackage(
        parameters, name_hash, start_of_defaults,
    )


from magic_constraints.utils import (
    raise_on_nontype_object,
    repr_return, conditional_repr,
)  # noqa
