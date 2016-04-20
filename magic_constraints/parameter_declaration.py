# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from collections import namedtuple, Iterable

from magic_constraints.type_declaration import type_decl_factory


class ParameterDecl(object):

    def __init__(self, name, raw_type, with_default, default):
        self.name = name
        self.type_decl = type_decl_factory(raw_type)
        self.with_default = with_default
        self.default = default

    def check_argument(self, arg):
        if arg is None:
            # 1. None by default and implicitly set.
            # 2. None by default and explicitly set.
            # 3. type(None).
            if self.with_default and self.default is None or\
                    self.type_decl.type_ is type(None):  # noqa
                pass
            else:
                raise TypeError(
                    'cannot pass None to {0}.'.format(self.name),
                )
        else:
            self.type_decl.check_argument(arg)


# intput: (<name>, <type decl>, [<default>])...
# output: ParameterDeclPackage
def build_parameters_decl_package(raw_parameter_decls):
    if not isinstance(raw_parameter_decls, Iterable):
        raise TypeError(
            'raw_parameter_decls should be Iterable.',
        )

    name_hash = {}
    parameter_decls = []
    start_of_defaults = -1

    for raw_parameter_decl in raw_parameter_decls:
        if len(raw_parameter_decl) < 2:
            raise TypeError(
                'Should be (<name>, <type decl>, [<default>])',
            )

        name = raw_parameter_decl[0]
        raw_type = raw_parameter_decl[1]

        if len(raw_parameter_decl) >= 3:
            with_default = True
            default = raw_parameter_decl[2]
        else:
            with_default = False
            default = None

        if name in name_hash:
            raise SyntaxError('duplicates on ' + name)

        parameter_decls.append(
            ParameterDecl(name, raw_type, with_default, default),
        )

        idx = len(parameter_decls) - 1
        name_hash[name] = idx

        if with_default:
            if start_of_defaults < 0:
                start_of_defaults = idx
        else:
            if start_of_defaults >= 0:
                raise SyntaxError(
                    'Parameter without default should be placed '
                    'in front of all parameters with default.'
                )

    ParameterDeclPackage = namedtuple(
        'ParameterDeclPackage',
        ['parameter_decls', 'name_hash', 'start_of_defaults'],
    )

    return ParameterDeclPackage(
        parameter_decls, name_hash, start_of_defaults,
    )
