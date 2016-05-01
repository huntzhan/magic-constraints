# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_constraints.exception import MagicSyntaxError, MagicTypeError


def transform_to_slots(constraints_package, *args, **kwargs):

    class UnFill(object):
        pass

    plen = len(constraints_package.parameters)

    if len(args) > plen:
        raise MagicSyntaxError(
            'argument length unmatched.',
            parameters=constraints_package.parameters,
            args=args,
        )

    slots = [UnFill] * plen
    unfill_count = plen

    # 1. fill args.
    for i, val in enumerate(args):
        slots[i] = val
    unfill_count -= len(args)

    # 2. fill kwargs.
    for key, val in kwargs.items():
        if key not in constraints_package.name_hash:
            raise MagicSyntaxError(
                'invalid keyword argument',
                parameters=constraints_package.parameters,
                key=key,
            )

        i = constraints_package.name_hash[key]
        if slots[i] is not UnFill:
            raise MagicSyntaxError(
                'key reassignment error.',
                parameters=constraints_package.parameters,
                key=key,
            )

        slots[i] = val
        unfill_count -= 1

    # 3. fill defaults if not set.
    # 3.1. deal with the case that default not exists.
    default_begin = constraints_package.start_of_defaults
    if default_begin < 0:
        default_begin = plen
    # 3.2 fill defaults.
    for i in range(default_begin, plen):
        parameter = constraints_package.parameters[i]
        j = constraints_package.name_hash[parameter.name]

        if slots[j] is UnFill:
            slots[j] = parameter.default
            unfill_count -= 1

    # 4. test if slots contains UnFill.
    if unfill_count != 0:
        raise MagicSyntaxError(
            'slots contains unfilled argument(s).',
            parameters=constraints_package.parameters,
            slots=slots,
        )

    return slots


def check_and_bind_arguments(parameters, slots, bind_callback):

    plen = len(parameters)

    for i in range(plen):
        arg = slots[i]
        parameter = parameters[i]

        wrapper = parameter.wrapper_for_deferred_checking()

        # defer checking by wrapping the element of slot.
        if wrapper:
            slots[i] = wrapper(arg)

        # check now.
        elif not parameter.check_instance(arg):
            raise MagicTypeError(
                'argument unmatched.',
                parameter=parameter,
                argument=arg,
            )

        # bind.
        bind_callback(parameter.name, arg)
