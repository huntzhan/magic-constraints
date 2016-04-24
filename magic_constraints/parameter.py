# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from collections import namedtuple

from magic_constraints.exception import MagicSyntaxError


class BaseType(object):

    def __init__(self, type_, **options):

        raise_on_nontype_object(type_)
        self.type_ = type_

        # key only arguemnt.
        # 1. if nullable, None is accepted.
        self.nullable = options.get('nullable', False)

        # 2. record default value.
        # NOTICE that ReturnType do not support default.
        if 'default' in options:
            self.with_default = True
            self.default = options['default']
        else:
            self.with_default = False
            self.default = None

        # 3. user-defined validator on input argument.
        self.validator = options.get(
            'validator', lambda instance: True,
        )

        # generator serialized string for repr.
        self._arguments_repr = '{prefix}, {suffix}'.format(
            # op 1.
            prefix=self.init_arguments_repr_prefix(type_, **options),
            # common suffix.
            suffix=self._init_arguments_repr_suffix(type_, **options),
        )

    def check_argument(self, instance):
        if instance is None:
            if not (self.nullable or issubclass(self.type_, type(None))):
                return False
            else:
                return self.validator(None)
        if not isinstance(instance, self.type_):
            return False
        return self.validator(instance)

    def _init_arguments_repr_suffix(self, type_, **options):
        # positional arguments.
        prefix = "type_={type_}".format(
            type_=conditional_repr(type_),
        )
        # keyword-only arguments.
        suffix = ', '.join(map(
            lambda p: "{0}={1}".format(p[0], conditional_repr(p[1])),
            sorted(options.items(), key=lambda p: p[0]),
        ))

        # merge.
        if suffix:
            arguemnt_repr = "{0}, {1}".format(prefix, suffix)
        else:
            arguemnt_repr = prefix

        return arguemnt_repr


class Parameter(BaseType):

    def __init__(self, name, type_, **options):
        self.name = name
        super().__init__(type_, **options)

    def init_arguments_repr_prefix(self, type_, **options):
        return 'name={0}'.format(
            conditional_repr(self.name),
        )

    def __repr__(self):
        return repr_return(
            'Parameter({})'.format(self._arguments_repr),
        )


def build_parameter_package(parameters):
    raise_on_non_parameters(parameters)

    name_hash = {}
    start_of_defaults = -1

    idx = 0
    for parameter in parameters:

        if parameter.name in name_hash:
            raise MagicSyntaxError(
                'redefinition of parameter',
                name=parameter.name,
            )

        name_hash[parameter.name] = idx

        if parameter.with_default:
            if start_of_defaults < 0:
                start_of_defaults = idx
        else:
            if start_of_defaults >= 0:
                raise MagicSyntaxError(
                    'Parameter without default should be placed '
                    'in front of all parameters with default.',
                    name=parameter.name,
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
    raise_on_nontype_object, raise_on_non_parameters,
    repr_return, conditional_repr,
)  # noqa
