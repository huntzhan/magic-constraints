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


def CreateMetaMagicType(generator_cls):

    class MetaMagicType(ABCMeta):

        def __getitem__(cls, type_decl):
            ret_cls = generator_cls(cls.main_cls)
            ret_cls.partial_cls = type_decl
            return ret_cls

        # fix unbound error of Python 2.x.
        __instancecheck__ = generator_cls.__dict__['__instancecheck__']

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
    def __instancecheck__(cls, ins):
        raise NotImplemented


class SequenceGenerator(MagicTypeGenerator):

    def __instancecheck__(cls, ins):
        if not cls.__subclasscheck__(type(ins)):
            return False
        # is sequence.
        if cls.partial_cls:
            for e in ins:
                if not isinstance(e, cls.partial_cls):
                    return False
        return True


class ABCImmutableSequenceMeta(ABCMeta):

    def __subclasscheck__(cls, sub):
        if not issubclass(sub, abc.Sequence):
            return False
        return not issubclass(sub, abc.MutableSequence)

    def __instancecheck__(cls, ins):
        return cls.__subclasscheck__(type(ins))


class ABCImmutableSequence(with_metaclass(ABCImmutableSequenceMeta, object)):
    pass


Sequence = SequenceGenerator(abc.Sequence)
MutableSequence = SequenceGenerator(abc.MutableSequence)
ImmutableSequence = SequenceGenerator(ABCImmutableSequence)
