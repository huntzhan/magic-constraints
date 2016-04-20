# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa


# pdp: parameter_decl_package
def transform_to_slots(pdp, *args, **kwargs):

    class UnFill(object):
        pass

    plen = len(pdp.parameter_decls)

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
        if key not in pdp.name_hash:
            raise TypeError(
                'invalid key: {0}'.format(key),
            )

        i = pdp.name_hash[key]
        if slots[i] is not UnFill:
            raise TypeError(
                'reassign key: {0}'.format(key),
            )
        slots[i] = val
        unfill_count -= 1

    # 3. fill defaults if not set.
    for i in range(pdp.start_of_defaults, plen):
        parameter_decl = pdp.parameter_decls[i]
        j = pdp.name_hash[parameter_decl.name]

        if slots[j] is UnFill:
            slots[j] = parameter_decl.default
            unfill_count -= 1

    # 4. test if slots contains UnFill.
    if unfill_count != 0:
        raise TypeError(
            'slots contains unfilled argument(s).',
        )

    return slots


def bind_arguments(parameter_decls, slots, bind_callback):

    plen = len(parameter_decls)

    for i in range(plen):
        arg = slots[i]
        pdcl = parameter_decls[i]
        # check.
        pdcl.check_argument(arg)
        # bind.
        bind_callback(pdcl.name, arg)
