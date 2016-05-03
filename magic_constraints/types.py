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

from magic_constraints.utils import (
    type_object, nontype_object,
    conditional_to_bytes, conditional_repr,
)

from magic_constraints.exception import (
    MagicTypeError, MagicIndexError
)


def meta_create_class(prefix, classname, baseclass, generator_cls):

    injected_functions = {}
    for name in dir(generator_cls):
        if not name.startswith(prefix):
            continue
        # get unbound function.
        function = getattr(generator_cls, name)
        if hasattr(function, '__func__'):
            function = function.__func__

        # remove prefix.
        injected_functions[name[len(prefix):]] = function

    return type(
        conditional_to_bytes(classname), (baseclass,), injected_functions,
    )


def create_metaclass(baseclass, generator_cls):
    return meta_create_class(
        '_metaclass_', 'MetaMagicClass', baseclass, generator_cls,
    )


def create_class(baseclass, generator_cls):
    return meta_create_class(
        '_class_', 'MagicClass', baseclass, generator_cls,
    )


def safe_getmethod(cls, name):

    def do_nothing(*args, **kwargs):
        return True

    method = getattr(cls, name, None)
    return method if method else do_nothing


class BasicMagicType(object):
    pass


class BasicMetaMagicType(ABCMeta):

    def __getitem__(cls, type_decl):

        if not safe_getmethod(cls, 'check_getitem_type_decl')(type_decl):
            raise MagicTypeError(
                'invalid type.',
                type_decl=type_decl,
            )

        ret_cls = cls.generator_cls(cls.main_cls)
        ret_cls.partial_cls = type_decl
        return ret_cls

    def __subclasscheck__(cls, subclass):
        if nontype_object(subclass):
            return False

        if not safe_getmethod(cls, 'check_subclass')(subclass):
            return False

        # corner case, subclass isn't MagicType.
        if not issubclass(subclass, BasicMagicType):
            return issubclass(subclass, cls.main_cls)

        # subclass is MagicType.
        if cls.partial_cls or subclass.partial_cls:
            # if subclass has partial_cls, return False.
            return False
        else:
            # 1. subclass is normal type object.
            # 2. subclass is a MagicType.
            return issubclass(subclass.main_cls, cls.main_cls)

    def __instancecheck__(cls, instance):
        return safe_getmethod(cls, 'check_instance')(instance)

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

        return conditional_to_bytes(name)


# 1. _metaclass_{name} -> {name} in metaclass.
# 2. _class_{name}     -> {name} in class.
class MagicTypeGenerator(type):

    def __new__(generator_cls, ABC):
        MetaMagicType = create_metaclass(
            BasicMetaMagicType,
            generator_cls,
        )
        MagicType = create_class(
            with_metaclass(MetaMagicType, BasicMagicType),
            generator_cls,
        )

        MagicType.generator_cls = generator_cls
        MagicType.main_cls = ABC
        MagicType.partial_cls = None

        return MagicType


def check_type_of_instance(cls, instance):
    return any(
        issubclass(T, cls)
        # handle old style class.
        for T in (instance.__class__, type(instance))
    )


def check_getitem_tuple(type_decl, n):
    # type_decl should be a n-tuple.
    if not isinstance(type_decl, tuple):
        return False
    return len(type_decl) == n


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

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        if type_object(type_decl):
            return True

        if isinstance(type_decl, tuple):
            for T in type_decl:
                if nontype_object(T):
                    return False
            return True
        else:
            return False

    def _metaclass_check_instance(cls, instance):
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

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        return type_object(type_decl)

    def _metaclass_check_instance(cls, instance):
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

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        if not check_getitem_tuple(type_decl, 2):
            return False

        return type_object(type_decl[0]) and type_object(type_decl[1])

    def _metaclass_check_instance(cls, instance):
        if not check_type_of_instance(cls, instance):
            return False

        if cls.partial_cls:
            key_cls, val_cls = cls.partial_cls
            for key, val in instance.items():
                if not (isinstance(key, key_cls) and isinstance(val, val_cls)):
                    return False
        return True


class IteratorGenerator(MagicTypeGenerator):

    _class_ITERATOR_CASE_LENGTH = 1
    _class_ITERATOR_CASE_NO_LENGTH = 2

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        # 1. Iterator[T, ...]
        if isinstance(type_decl, tuple):
            for T in type_decl:
                if nontype_object(T):
                    return False
            return True

        # 2. Iterator[T]
        elif type_object(type_decl):
            return True

        else:
            return False

    def _metaclass_check_instance(cls, instance):
        if cls.partial_cls or not check_type_of_instance(cls, instance):
            return False
        else:
            # is Iterator and not Iterator[...].
            return True

    def _class___init__(self, iterator):
        if self.partial_cls is None:
            raise MagicTypeError(
                'Iterator should be specified.'
            )

        if not isinstance(iterator, self.main_cls):
            raise MagicTypeError(
                'require Iterator.',
                iterator=iterator,
            )

        if isinstance(self.partial_cls, tuple):
            # Iterator[T, ...]. Checking on:
            # 1. the number of elements in the iterator.
            # 2. the type of each element.
            self.case = self.ITERATOR_CASE_LENGTH
            self._type_idx = 0
        else:
            # Iterator[T]. Check only the type of element. There's no
            # limitation on the length of iterator.
            self.case = self.ITERATOR_CASE_NO_LENGTH

        self.iterator = iterator

    def _class___iter__(self):
        return self

    def _class___next__(self):
        try:
            element = next(self.iterator)
        except StopIteration:
            # check the stop condition.
            if self.case == self.ITERATOR_CASE_LENGTH and\
                    self._type_idx != len(self.partial_cls):
                raise IndexError

            # good case.
            else:
                raise

        if self.case == self.ITERATOR_CASE_LENGTH:
            # error 1.
            if self._type_idx >= len(self.partial_cls):
                raise MagicIndexError(
                    'iterator contains more elements declared in type.',
                    type_=self,
                    last_element=element,
                )

            # error 2.
            if not isinstance(element, self.partial_cls[self._type_idx]):
                raise MagicTypeError(
                    'type unmatched.',
                    element=element,
                    type_=self.partial_cls[self._type_idx],
                )

            # good case.
            self._type_idx += 1
            return element

        elif self.case == self.ITERATOR_CASE_NO_LENGTH:
            if not isinstance(element, self.partial_cls):
                raise MagicTypeError(
                    'type unmatched.',
                    element=element,
                    type_=self.partial_cls,
                )


class IterableGenerator(MagicTypeGenerator):

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        # [T]
        if type_object(type_decl):
            return True

        # [T, ...]
        elif isinstance(type_decl, tuple):
            for T in type_decl:
                if nontype_object(T):
                    return False
            else:
                return True

        # otherwise.
        else:
            return False

    def _metaclass_check_instance(cls, instance):
        if cls.partial_cls or not check_type_of_instance(cls, instance):
            return False
        else:
            # is Iterable and not Iterable[...].
            return True

    def _class___init__(self, iterable):
        if self.partial_cls is None:
            raise MagicTypeError(
                'require T on Iterable[T].'
            )

        if not isinstance(iterable, self.main_cls):
            raise MagicTypeError(
                'require Iterable.',
                iterable=iterable,
            )

        self.iterable = iterable

    def _class___iter__(self):
        return Iterator[self.partial_cls](iter(self.iterable))


class CallableGenerator(MagicTypeGenerator):

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        # Callable[[T, ...], T]
        if not check_getitem_tuple(type_decl, 2):
            return False

        # return type.
        if nontype_object(type_decl[1]):
            return False

        # types of parameters.
        if isinstance(type_decl[0], abc.Iterable):
            # [T, ...]
            for T in type_decl[0]:
                if nontype_object(T):
                    return False
            else:
                return True
        else:
            # special case, Ellipsis.
            return type_decl[0] is Ellipsis

    def _metaclass_check_instance(cls, instance):
        if cls.partial_cls or not check_type_of_instance(cls, instance):
            return False
        else:
            # is callable and not Callable[T, ...].
            return True

    def _class___new__(cls, instance):
        # 1. not Callable.
        if not isinstance(instance, cls.main_cls):
            raise MagicTypeError(
                'instance should be a Callable.',
                instance=instance,
            )
        # 2. with no specification.
        if not cls.partial_cls:
            raise MagicSyntaxError(
                'Callable should be specified to wrap the callable.',
            )

        parameters_types, return_type = cls.partial_cls

        if parameters_types is Ellipsis:
            parameters_types = [parameters_types]

        return function_constraints(
            *parameters_types,
            # tailing coma is invalid for version < 3.5.
            return_type=return_type
        )(instance)


class UnionGenerator(MagicTypeGenerator):

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        if type_object(type_decl) or not isinstance(type_decl, tuple):
            return False

        for T in type_decl:
            if nontype_object(T):
                return False
        else:
            return True

    def _metaclass_check_subclass(cls, subclass):
        return False

    def _metaclass_check_instance(cls, instance):
        if cls.partial_cls is None:
            return False

        for candidate_cls in cls.partial_cls:
            if isinstance(instance, candidate_cls):
                return True
        return False


class OptionalGenerator(MagicTypeGenerator):

    def _metaclass_check_getitem_type_decl(cls, type_decl):
        return type_object(type_decl)

    def _metaclass_check_subclass(cls, subclass):
        return False

    def _metaclass_check_instance(cls, instance):
        if cls.partial_cls is None:
            return False

        if instance is None:
            return True
        else:
            return isinstance(instance, cls.partial_cls)


def dummy_class(name):
    return type(conditional_to_bytes(name), (object,), {})


class AnyMeta(ABCMeta):

    def __instancecheck__(cls, instance):
        return True

    def __subclasscheck__(cls, subclass):
        return type_object(subclass)

    def __repr__(self):
        return conditional_to_bytes('Any')


class Any(with_metaclass(AnyMeta, object)):
    pass


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

Callable = CallableGenerator(abc.Callable)

Union = UnionGenerator(dummy_class('Union'))
Optional = OptionalGenerator(dummy_class('Optional'))
NoneType = type(None)


from magic_constraints.decorator import (
    function_constraints,
)  # noqa
