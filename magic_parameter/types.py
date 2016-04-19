# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa
from future.utils import with_metaclass


from abc import ABCMeta
# collections.abc dosn't esist in Python 2.x.
import collections as abc


class MagicTypeGenerator(type):

    def __new__(cls, ABC):

        class GetItemHack(ABCMeta):

            # fix unbound error of Python 2.x.
            __getitem__ = cls.__dict__['__getitem__']
            __instancecheck__ = cls.__dict__['__instancecheck__']

        class MagicType(with_metaclass(GetItemHack, object)):

            nested_type = None

        # TODO: fix later.
        MagicType.register(ABC)

        return MagicType

    # cls bound to real Magic type.
    def __getitem__(cls, type_decl):
        raise NotImplemented

    # cls bound to real Magic type.
    def __instancecheck__(cls, ins):
        raise NotImplemented


class SequenceGenerator(MagicTypeGenerator):

    def __getitem__(cls, type_decl):

        NestedSequence = SequenceGenerator(cls)
        NestedSequence.nested_type = type_decl
        return NestedSequence

    def __instancecheck__(cls, ins):
        if not cls.__subclasscheck__(type(ins)):
            return False
        # is sequence.
        if cls.nested_type:
            for e in ins:
                print(e)
                if not isinstance(e, cls.nested_type):
                    return False
        return True


Sequence = SequenceGenerator(abc.Sequence)
