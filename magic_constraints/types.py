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

from magic_constraints.exception import MagicTypeError
from magic_constraints.utils import (
    type_object, nontype_object,
    repr_return, conditional_repr,
)


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
                raise MagicTypeError(
                    'invalid type.',
                    type_decl=type_decl,
                )

            ret_cls = generator_cls(cls.main_cls)
            ret_cls.partial_cls = type_decl
            return ret_cls

        # fix unbound error of Python 2.x.
        __instancecheck__ = unbound_getattr(generator_cls, '__instancecheck__')

        def __subclasscheck__(cls, subclass):
            if nontype_object(subclass):
                return False

            if unbound_getattr(generator_cls, '__subclasshook__'):
                subclasshook = unbound_getattr(
                    generator_cls, '__subclasshook__',
                )
                if not subclasshook(cls, subclass):
                    return False

            # corner case, subclass isn't MagicType.
            if not hasattr(subclass, 'partial_cls'):
                return issubclass(subclass, cls.main_cls)

            # subclass is MagicType.
            if cls.partial_cls or subclass.partial_cls:
                # if subclass has partial_cls, return False.
                return False
            else:
                # 1. subclass is normal type object.
                # 2. subclass is a MagicType.
                return issubclass(subclass.main_cls, cls.main_cls)

        def __repr__(cls):

            name = conditional_repr(cls.main_cls)
            if cls.partial_cls:
                partial = ', '.join(
                    map(
                        conditional_repr,
                        cls.partial_cls
                        if isinstance(cls.partial_cls, tuple)
                        else [cls.partial_cls],
                    ),
                )

                name = '{0}[{1}]'.format(
                    name, partial,
                )

            return repr_return(name)

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

    def __new__(cls, ABC):
        MetaMagicType = CreateMetaMagicType(cls)
        return CreateMagicType(cls, MetaMagicType, ABC)


def check_type_of_instance(cls, instance):
    return any(
        issubclass(t, cls)
        # handle old style class.
        for t in (instance.__class__, type(instance))
    )


def generate_immutable_abc(supercls, mutable_subclass):

    class ABCImmutableMeta(ABCMeta):

        def __subclasscheck__(cls, subclass):
            if not issubclass(subclass, supercls):
                return False
            return not issubclass(subclass, mutable_subclass)

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
        else:
            return False

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
        if self.partial_cls is None:
            raise MagicTypeError(
                'require T on Iterator[T].'
            )
        if not isinstance(iterator, abc.Iterator):
            raise MagicTypeError(
                'require Iterator.',
                iterator=iterator,
            )

        self.iterator = iterator

    def __iter__(self):
        return self

    def __next__(self):
        element = next(self.iterator)
        if isinstance(element, self.partial_cls):
            return element
        else:
            raise MagicTypeError(
                'type unmatched.',
                element=element,
                type_=self.partial_cls,
            )

    def __instancecheck__(cls, instance):
        return check_type_of_instance(cls, instance)


class IterableGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        return type_object(type_decl)

    def __init__(self, iterable):
        if self.partial_cls is None:
            raise MagicTypeError(
                'require T on Iterable[T].'
            )
        if not isinstance(iterable, abc.Iterable):
            raise MagicTypeError(
                'require Iterable.',
                iterable=iterable,
            )
        self.iterable = iterable

    def __iter__(self):
        return Iterator[self.partial_cls](
            iter(self.iterable),
        )

    def __instancecheck__(cls, instance):
        return check_type_of_instance(cls, instance)


class AnyMeta(ABCMeta):

    def __instancecheck__(cls, instance):
        return True

    def __subclasscheck__(cls, subclass):
        return type_object(subclass)


class Any(with_metaclass(AnyMeta, object)):
    pass


class UnionGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        if type_object(type_decl) or not isinstance(type_decl, tuple):
            return False

        for t in type_decl:
            if nontype_object(t):
                return False
        else:
            return True

    def __subclasshook__(cls, subclass):
        return False

    def __instancecheck__(cls, instance):
        if cls.partial_cls is None:
            return False

        for candidate_cls in cls.partial_cls:
            if isinstance(instance, candidate_cls):
                return True
        return False


class OptionalGenerator(MagicTypeGenerator):

    def check_getitem_type_decl(type_decl):
        return type_object(type_decl)

    def __subclasshook__(cls, subclass):
        return False

    def __instancecheck__(cls, instance):
        if cls.partial_cls is None:
            return False

        if instance is None:
            return True
        else:
            return isinstance(instance, cls.partial_cls)


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
Iterable = IterableGenerator(abc.Iterable)

Union = UnionGenerator(Any)
Optional = OptionalGenerator(Any)
NoneType = type(None)
