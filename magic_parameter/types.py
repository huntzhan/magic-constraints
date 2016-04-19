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


def CreateMetaMagicType(cls):

    class MetaMagicType(ABCMeta):

        # fix unbound error of Python 2.x.
        __getitem__ = cls.__dict__['__getitem__']
        __instancecheck__ = cls.__dict__['__instancecheck__']

        def __subclasscheck__(cls, sub):
            # corner case, sub isn't MagicType.
            if not hasattr(sub, 'partial_cls'):
                return issubclass(sub, cls.main_cls)

            # sub is MagicType.
            if cls.partial_cls or sub.partial_cls:
                # if sub has partial_cls, return False.
                return False
            else:
                # 1. sub is normal type object.
                # 2. sub is a MagicType.
                return issubclass(sub.main_cls, cls.main_cls)

    return MetaMagicType


def CreateMagicType(MetaMagicType, ABC):

    class MagicType(with_metaclass(MetaMagicType, object)):

        main_cls = ABC
        partial_cls = None

    return MagicType


class MagicTypeGenerator(type):

    def __new__(cls, ABC):
        return CreateMagicType(
            CreateMetaMagicType(cls),
            ABC,
        )

    # cls bound to real Magic type.
    def __getitem__(cls, type_decl):
        raise NotImplemented

    # cls bound to real Magic type.
    def __instancecheck__(cls, ins):
        raise NotImplemented


class SequenceGenerator(MagicTypeGenerator):

    def __getitem__(cls, type_decl):

        NestedSequence = SequenceGenerator(cls)
        NestedSequence.partial_cls = type_decl
        return NestedSequence

    def __instancecheck__(cls, ins):
        if not cls.__subclasscheck__(type(ins)):
            return False
        # is sequence.
        if cls.partial_cls:
            for e in ins:
                if not isinstance(e, cls.partial_cls):
                    return False
        return True


Sequence = SequenceGenerator(abc.Sequence)
