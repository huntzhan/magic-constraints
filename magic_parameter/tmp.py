# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import types
import collections


def check_iterable_decl(name, type_):
    for t in type_:
        if not is_type_object(t) and not isinstance(t, CompositeDecl):
            raise TypeError(
                '{0} contains non-type object {1}.'.format(
                    name, t,
                )
            )


def check_type_decl(name, type_):

    if isinstance(type_, collections.Iterable):
        check_iterable_decl(name, type_)
    elif is_type_object(type_):
        pass
    elif isinstance(type_, CompositeDecl):
        pass
    else:
        raise TypeError(
            '{0} should be a type object.'.format(name),
        )


def check_value(val, name, type_):
    fail = True

    if isinstance(type_, collections.Iterable):
        for t in type_:
            try:
                check_value(val, name, t)
                fail = False
            except TypeError:
                pass

    elif isinstance(type_, CompositeDecl):
        fail = not type_.check(val, name)
    else:
        fail = not isinstance(val, type_)

    if fail:
        raise TypeError(
            '{0} unmatch: {1} could not match {2}'.format(
                name, val, type_,
            ),
        )


class CompositeDecl(object):

    BASE_TYPE = None

    def __init__(self, type_):
        check_type_decl('[]', type_)
        self.type_ = type_

    def check(self, vals, name):
        if not isinstance(vals, self.BASE_TYPE):
            raise TypeError(
                'in {0}, {1} should be {2}'.format(name, vals, self.BASE_TYPE),
            )

        for val in vals:
            check_value(val, name, self.type_)

        return True


class list_d(CompositeDecl):

    BASE_TYPE = list


class tuple_d(CompositeDecl):

    BASE_TYPE = tuple


def preprocess_parameter_defs(parameter_defs):

    name_idx_mapping = {}
    defs = []
    defaults = []

    if parameter_defs is None or\
            not isinstance(parameter_defs, collections.Iterable):
        return name_idx_mapping, defs, defaults

    for definition in parameter_defs:
        if len(definition) < 2:
            raise TypeError

        name = definition[0]
        type_ = definition[1]
        check_type_decl(name, type_)

        if len(definition) >= 3:
            default = definition[2]
            with_default = True
        else:
            default = None
            with_default = False

        if name in name_idx_mapping:
            raise SyntaxError('duplicates on ' + name)

        defs.append(
            (name, type_, with_default, default),
        )
        idx = len(defs) - 1
        name_idx_mapping[name] = idx
        if with_default:
            defaults.append(
                (idx, default),
            )

    return name_idx_mapping, defs, defaults


def bind_parameters(env, *args, **kwargs):

    class UnFill(object):
        pass

    name_idx_mapping, defs, defaults, self = env

    if len(args) > len(defs):
        raise TypeError

    slots = [UnFill] * len(defs)

    # 1. fill args.
    for i, val in enumerate(args):
        slots[i] = val
    # 2. fill kwargs.
    for key, val in kwargs.items():
        if key not in name_idx_mapping:
            raise TypeError
        idx = name_idx_mapping[key]
        if slots[idx] is not UnFill:
            raise TypeError
        slots[idx] = val
    # 3. fill defaults if not set.
    for idx, val in defaults:
        if slots[idx] is UnFill:
            slots[idx] = val

    # check and bind values.
    for idx in range(len(defs)):
        name, type_, with_default, default = defs[idx]
        val = slots[idx]

        if val is UnFill:
            raise TypeError(
                'missing {0}'.format(name),
            )
        if val is None:
            if (with_default and default is None) or\
                    type_ is type(None):  # noqa
                # 1. None by default and implicitly set.
                # 2. None by default and explicitly set.
                # 3. type(None).
                pass
            else:
                raise TypeError(
                    '{0} should not be None.'.format(name),
                )
        else:
            check_value(val, name, type_)

        setattr(self, name, val)


def inject_type_object(parameter_defs, py2_nonlocal_fix, target):

    PARAMETERS = 'PARAMETERS'

    if parameter_defs is None and hasattr(target, PARAMETERS):
        _name_idx_mapping, _defs, _defaults = preprocess_parameter_defs(
            getattr(target, PARAMETERS),
        )

        py2_nonlocal_fix['name_idx_mapping'] = _name_idx_mapping
        py2_nonlocal_fix['defs'] = _defs
        py2_nonlocal_fix['defaults'] = _defaults

    predefined_init = getattr(target, '__init__')

    def injected_init(self, *args, **kwargs):
        env = (
            py2_nonlocal_fix['name_idx_mapping'],
            py2_nonlocal_fix['defs'],
            py2_nonlocal_fix['defaults'],
            self,
        )
        bind_parameters(env, *args, **kwargs)
        predefined_init(self)

    setattr(target, '__init__', injected_init)


def init_parameters(parameter_defs_or_type_obj=None):

    name_idx_mapping, defs, defaults = preprocess_parameter_defs(
        parameter_defs_or_type_obj,
    )
    py2_nonlocal_fix = {
        'name_idx_mapping': name_idx_mapping,
        'defs': defs,
        'defaults': defaults,
    }

    if is_type_object(parameter_defs_or_type_obj):
        target = parameter_defs_or_type_obj
        inject_type_object(None, py2_nonlocal_fix, target)
        return target
    else:
        parameter_defs = parameter_defs_or_type_obj

    def decorator(target):

        def init(self, *args, **kwargs):
            env = (
                name_idx_mapping, defs, defaults,
                self,
            )
            bind_parameters(env, *args, **kwargs)
            return target(self)

        if isinstance(target, types.FunctionType):
            return init
        elif is_type_object(target):
            # type object.
            inject_type_object(parameter_defs, py2_nonlocal_fix, target)
            return target
        else:
            raise TypeError('target should be a function or a type object.')

    return decorator
