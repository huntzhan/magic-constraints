# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa


def transform_to_slots(parameter_package, *args, **kwargs):

    class UnFill(object):
        pass

    plen = len(parameter_package.parameters)

    if len(args) > plen:
        raise TypeError

    slots = [UnFill] * plen
    unfill_count = plen

    # 1. fill args.
    for i, val in enumerate(args):
        slots[i] = val
    unfill_count -= len(args)

    # 2. fill kwargs.
    for key, val in kwargs.items():
        if key not in parameter_package.name_hash:
            raise TypeError(
                'invalid key: {0}'.format(key),
            )

        i = parameter_package.name_hash[key]
        if slots[i] is not UnFill:
            raise TypeError(
                'reassign key: {0}'.format(key),
            )
        slots[i] = val
        unfill_count -= 1

    # 3. fill defaults if not set.
    for i in range(parameter_package.start_of_defaults, plen):
        parameter = parameter_package.parameters[i]
        j = parameter_package.name_hash[parameter.name]

        if slots[j] is UnFill:
            slots[j] = parameter.default
            unfill_count -= 1

    # 4. test if slots contains UnFill.
    if unfill_count != 0:
        raise TypeError(
            'slots contains unfilled argument(s).',
        )

    return slots


def check_and_bind_arguments(parameters, slots, bind_callback):

    plen = len(parameters)

    for i in range(plen):
        arg = slots[i]
        parameter = parameters[i]
        # check.
        if not parameter.check_argument(arg):
            raise TypeError(
                '{0} cannot match {1}'.format(arg, parameter),
            )
        # bind.
        bind_callback(parameter.name, arg)
