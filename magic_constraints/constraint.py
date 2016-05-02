# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from collections import namedtuple
import collections as abc

from funcsigs import signature
from funcsigs import Parameter as SigParameter


from magic_constraints.types import (
    Any,
    BasicMagicType,
)

from magic_constraints.exception import (
    MagicSyntaxError,
    MagicTypeError,
)

from magic_constraints.utils import (
    type_object,
    nontype_object,
    raise_on_nontype_object,
    conditional_to_bytes,
    conditional_repr,
    return_true,
)


class Constraint(object):

    def __init__(self, type_, **options):

        raise_on_nontype_object(type_)
        self.type_ = type_

        # 1. record default value.
        # NOTICE that ReturnType do not support default.
        if 'default' in options:
            self.with_default = True
            self.default = options['default']
        else:
            self.with_default = False
            self.default = None

        # 2. user-defined validator on input argument.
        self.validator = options.get(
            'validator', return_true,
        )

        # generator serialized string for repr.
        # op 1.
        prefix = self.init_arguments_repr_prefix(type_, **options)
        # common suffix.
        suffix = self._init_arguments_repr_suffix(type_, **options)
        if prefix:
            self._arguments_repr = '{0}, {1}'.format(prefix, suffix)
        else:
            self._arguments_repr = suffix

        # check default.
        if self.with_default and not self.check_instance(self.default):
            raise MagicTypeError(
                'default value unmatched.',
                parameter=self,
            )

    def wrapper_for_deferred_checking(self):
        if not issubclass(self.type_, BasicMagicType):
            return None

        if issubclass(self.type_.main_cls, (abc.Iterator, abc.Callable)) and\
                self.type_.partial_cls:
            return self.type_

        else:
            return None

    def check_instance(self, instance, *args, **kwargs):
        if not isinstance(instance, self.type_):
            return False

        return self.validator(instance, *args, **kwargs)

    def init_arguments_repr_prefix(self, type_, **options):
        return ''

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

    def __repr__(self):
        return conditional_to_bytes(
            '{cls_name}({arguemnt_repr})'.format(
                cls_name=type(self).__name__,
                arguemnt_repr=self._arguments_repr,
            ),
        )


class Parameter(Constraint):

    def __init__(self, name, type_, **options):
        self.name = name
        super().__init__(type_, **options)

    def init_arguments_repr_prefix(self, type_, **options):
        return 'name={0}'.format(
            conditional_repr(self.name),
        )


class ReturnType(Constraint):

    def __init__(self, type_, **options):
        if 'default' in options:
            raise MagicSyntaxError(
                'default is invalid in ReturnType',
                default=options['default'],
            )
        super().__init__(type_, **options)


def raise_on_non_parameters(parameters):
    if not isinstance(parameters, abc.Sequence):
        raise MagicTypeError(
            'parameter should be Sequence.',
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


def raise_on_non_constraints(constraints):
    raise_on_non_parameters(constraints[:-1])
    if not isinstance(constraints[-1], Constraint):
        raise MagicTypeError(
            'require Parameter or ReturnType in the ending of constraints.',
            constraints=constraints,
        )


def check_and_preprocess_parameters(parameters):
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

    return name_hash, start_of_defaults


def build_constraints_package(constraints):
    if isinstance(constraints[-1], ReturnType):
        parameters = constraints[:-1]
        return_type = constraints[-1]
    else:
        parameters = constraints
        return_type = ReturnType(Any)

    name_hash, start_of_defaults = check_and_preprocess_parameters(parameters)

    ConstraintsPackage = namedtuple(
        'ConstraintsPackage',
        [
            'parameters', 'name_hash', 'start_of_defaults',
            'return_type',
        ],
    )

    return ConstraintsPackage(
        parameters, name_hash, start_of_defaults,
        return_type,
    )


def build_parameter_in_inspection(name, type_, sig_parameter):
    # check the form of parameter.
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

    annotation = sig_parameter.annotation
    default = sig_parameter.default

    # two cases on annotation.
    if type_ is None:
        if annotation is SigParameter.empty:
            raise MagicSyntaxError(
                'missing annotation',
                name=name,
            )
    else:
        if nontype_object(type_):
            raise MagicTypeError(
                'type_ should be a type object.',
                name=name,
                type_=type_,
            )
        annotation = type_

    if default is SigParameter.empty:
        # without default.
        return Parameter(name, annotation)
    else:
        return Parameter(name, annotation, default=default)


def build_return_type(return_type):
    if return_type is SigParameter.empty:
        return ReturnType(Any)

    elif type_object(return_type):
        return ReturnType(return_type)

    else:
        raise MagicTypeError(
            'return_type should be None or type object.',
            return_type=return_type,
        )


def build_constraints_with_annotation(function, skip_first_argument):
    function_sig = signature(function)

    constraints = []
    # 1. parameters.
    for name, sig_parameter in function_sig.parameters.items():
        if skip_first_argument:
            skip_first_argument = False
            continue

        constraints.append(
            build_parameter_in_inspection(name, None, sig_parameter),
        )

    # 2. return type.
    constraints.append(
        build_return_type(function_sig.return_annotation),
    )

    return constraints


def build_constraints_with_given_type_args(
        function, skip_first_argument,
        type_args, return_type=SigParameter.empty):

    argument_sigs = signature(function)

    parameter_length = len(argument_sigs.parameters)
    if skip_first_argument:
        parameter_length -= 1

    if parameter_length != len(type_args):
        raise MagicSyntaxError(
            'length of arguments not match.',
            type_args=type_args,
            function_signature=argument_sigs.parameters,
        )

    constraints = []
    # 1. parameters.
    ti = 0
    for name, sig_parameter in argument_sigs.parameters.items():
        if skip_first_argument:
            skip_first_argument = False
            continue

        constraints.append(
            build_parameter_in_inspection(name, type_args[ti], sig_parameter),
        )
        ti += 1

    # 2. return type.
    constraints.append(
        build_return_type(return_type),
    )

    return constraints
