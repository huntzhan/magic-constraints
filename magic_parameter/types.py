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

from magic_parameter.utils import type_object, nontype_object


def CreateMetaMagicType(generator_cls):

    class MetaMagicType(ABCMeta):

        def __getitem__(cls, type_decl):
            if generator_cls.disable_getitem:
                raise SyntaxError
            if isinstance(type_decl, tuple):
                if generator_cls.disable_getitem_tuple:
                    raise SyntaxError
                for t in type_decl:
                    if nontype_object(t):
                        raise SyntaxError

            ret_cls = generator_cls(cls.main_cls)
            ret_cls.partial_cls = type_decl
            return ret_cls

        # fix unbound error of Python 2.x.
        __instancecheck__ = generator_cls.__dict__['__instancecheck__']

        def __subclasscheck__(cls, sub):
            if nontype_object(sub):
                return False

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

    disable_getitem = False
    disable_getitem_tuple = False

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

        if not cls.partial_cls:
            return True

        if type_object(cls.partial_cls):
            for e in ins:
                if not isinstance(e, cls.partial_cls):
                    return False
        else:
            if not isinstance(cls.partial_cls, tuple):
                return False
            if len(cls.partial_cls) != len(ins):
                return False
            for i in range(len(ins)):
                if not isinstance(ins[i], cls.partial_cls[i]):
                    return False

        return True


class ABCImmutableSequenceMeta(ABCMeta):

    def __subclasscheck__(cls, sub):
        if not issubclass(sub, abc.Sequence):
            return False
        return not issubclass(sub, abc.MutableSequence)

    def __instancecheck__(cls, ins):
        return cls.__subclasscheck__(type(ins))


class ABCImmutableSequence(
        with_metaclass(ABCImmutableSequenceMeta, object)):
    pass


class SetGenerator(MagicTypeGenerator):

    disable_getitem_tuple = True

    def __instancecheck__(cls, ins):
        if not cls.__subclasscheck__(type(ins)):
            return False

        if not cls.partial_cls:
            return True

        if type_object(cls.partial_cls):
            for e in ins:
                if not isinstance(e, cls.partial_cls):
                    return False

        return True


class ABCImmutableSetMeta(ABCMeta):

    def __subclasscheck__(cls, sub):
        if not issubclass(sub, abc.Set):
            return False
        return not issubclass(sub, abc.MutableSet)

    def __instancecheck__(cls, ins):
        return cls.__subclasscheck__(type(ins))


class ABCImmutableSet(with_metaclass(ABCImmutableSetMeta, object)):
    pass


# dirty hack.
def BindSuperclass(super_abc, sub_abc):
    super_abc._abc_cache.add(sub_abc)


BindSuperclass(abc.Sequence, ABCImmutableSequence)
BindSuperclass(abc.Set, ABCImmutableSet)

Sequence = SequenceGenerator(abc.Sequence)
MutableSequence = SequenceGenerator(abc.MutableSequence)
ImmutableSequence = SequenceGenerator(ABCImmutableSequence)

Set = SetGenerator(abc.Set)
MutableSet = SetGenerator(abc.MutableSet)
ImmutableSet = SetGenerator(ABCImmutableSet)
