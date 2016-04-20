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


def unbound_getattr(target, name):
    return target.__dict__.get(name, None)


def CreateMetaMagicType(generator_cls):

    class MetaMagicType(ABCMeta):

        def __getitem__(cls, type_decl):

            type_decl_checker = unbound_getattr(
                generator_cls,
                'check_getitem_type_decl',
            )
            if type_decl_checker and not type_decl_checker(type_decl):
                raise SyntaxError

            ret_cls = generator_cls(cls.main_cls)
            ret_cls.partial_cls = type_decl
            return ret_cls

        # fix unbound error of Python 2.x.
        __instancecheck__ = unbound_getattr(generator_cls, '__instancecheck__')

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


def CreateMagicType(generator_cls, MetaMagicType, ABC):

    class MagicType(with_metaclass(MetaMagicType, object)):

        main_cls = ABC
        partial_cls = None

        for attr in [
            '__new__',
            '__init__',
            # iterator.
            '__iter__',
            '__next__',
        ]:
            if unbound_getattr(generator_cls, attr):
                locals()[attr] = unbound_getattr(generator_cls, attr)

    return MagicType


class MagicTypeGenerator(type):

    disable_getitem = False
    disable_getitem_tuple = False

    def __new__(cls, ABC):
        MetaMagicType = CreateMetaMagicType(cls)
        return CreateMagicType(cls, MetaMagicType, ABC)

    # cls bound to real Magic type.
    def __instancecheck__(cls, instance):
        raise NotImplemented


def check_type_of_instance(cls, instance):
    return any(
        issubclass(t, cls)
        # handle old style class.
        for t in (instance.__class__, type(instance))
    )


def generate_immutable_abc(supercls, mutable_subcls):

    class ABCImmutableMeta(ABCMeta):

        def __subclasscheck__(cls, sub):
            if not issubclass(sub, supercls):
                return False
            return not issubclass(sub, mutable_subcls)

        def __instancecheck__(cls, instance):
            return cls.__subclasscheck__(type(instance))

    class ABCImmutable(with_metaclass(ABCImmutableMeta, object)):
        pass

    # dirty hack to assert issubclass(ABCImmutable, supercls).
    supercls._abc_cache.add(ABCImmutable)

    return ABCImmutable


class SequenceGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        if type_object(type_decl):
            return True

        if isinstance(type_decl, tuple):
            for t in type_decl:
                if nontype_object(t):
                    return False
        return True

    def __instancecheck__(cls, instance):
        if not check_type_of_instance(cls, instance):
            return False

        if not cls.partial_cls:
            return True

        if type_object(cls.partial_cls):
            for e in instance:
                if not isinstance(e, cls.partial_cls):
                    return False
        else:
            if not isinstance(cls.partial_cls, tuple):
                return False
            if len(cls.partial_cls) != len(instance):
                return False
            for i in range(len(instance)):
                if not isinstance(instance[i], cls.partial_cls[i]):
                    return False

        return True


class SetGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        return type_object(type_decl)

    def __instancecheck__(cls, instance):
        if not check_type_of_instance(cls, instance):
            return False

        if not cls.partial_cls:
            return True

        if type_object(cls.partial_cls):
            for e in instance:
                if not isinstance(e, cls.partial_cls):
                    return False

        return True


class MappingGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        if type_object(type_decl) or not isinstance(type_decl, tuple):
            return False
        if len(type_decl) != 2:
            return False
        return type_object(type_decl[0]) and type_object(type_decl[1])

    def __instancecheck__(cls, instance):
        if not check_type_of_instance(cls, instance):
            return False

        if cls.partial_cls:
            key_cls, val_cls = cls.partial_cls
            for key, val in instance.items():
                if not (isinstance(key, key_cls) and isinstance(val, val_cls)):
                    return False
        return True


class IteratorGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        return type_object(type_decl)

    def __init__(self, iterator):
        if not isinstance(iterator, abc.Iterator):
            raise TypeError
        self.iterator = iterator

    def __iter__(self):
        return self

    def __next__(self):
        element = next(self.iterator)
        if isinstance(element, self.partial_cls):
            return element
        else:
            raise TypeError

    def __instancecheck__(cls, instance):
        return check_type_of_instance(cls, instance)


ABCImmutableSequence = generate_immutable_abc(
    abc.Sequence, abc.MutableSequence,
)
ABCImmutableSet = generate_immutable_abc(
    abc.Set, abc.MutableSet,
)
ABCImmutableMapping = generate_immutable_abc(
    abc.Mapping, abc.MutableMapping,
)

Sequence = SequenceGenerator(abc.Sequence)
MutableSequence = SequenceGenerator(abc.MutableSequence)
ImmutableSequence = SequenceGenerator(ABCImmutableSequence)

Set = SetGenerator(abc.Set)
MutableSet = SetGenerator(abc.MutableSet)
ImmutableSet = SetGenerator(ABCImmutableSet)

Mapping = MappingGenerator(abc.Mapping)
MutableMapping = MappingGenerator(abc.MutableMapping)
ImmutableMapping = MappingGenerator(ABCImmutableMapping)

Iterator = IteratorGenerator(abc.Iterator)
