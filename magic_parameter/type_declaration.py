# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from magic_parameter.utils import type_object


def list_t(raw_type):
    return list((
        raw_type,
    ))


def tuple_t(raw_type):
    return tuple((
        raw_type,
    ))


def set_t(raw_type):
    return set((
        raw_type,
    ))


def dict_t(key_raw_type, val_raw_type):
    return dict({
        key_raw_type: val_raw_type,
    })


def type_decl_factory(raw_type):

    if isinstance(raw_type, (TypeRelationship, TypeDecl)):
        return raw_type
    if type_object(raw_type):
        return TypeDecl(raw_type)

    if isinstance(raw_type, (list, tuple, set)):
        if len(raw_type) != 1:
            raise SyntaxError(
                '{0} should be 1-list or 1-tuple or 1-set'.format(raw_type),
            )
        return ArrayDecl(
            type(raw_type),
            # child.
            type_decl_factory(
                # compatiable with set.
                next(iter(raw_type)),
            ),
        )

    if isinstance(raw_type, dict):
        if len(raw_type) != 1:
            raise SyntaxError(
                '{0} should be 1-dict'.format(raw_type),
            )
        key_raw_type, val_raw_type = next(iter(raw_type.items()))
        return DictDecl(
            type(raw_type),
            type_decl_factory(key_raw_type),
            type_decl_factory(val_raw_type),
        )

    raise TypeError(
        'NotSupport: {0}'.format(raw_type),
    )


class TypeDecl(object):

    def __init__(self, type_):
        self.type_ = type_
        self.name = None
        self.parent = None
        self.child = None

    def __str__(self):
        tpl = [
            'name: {0}',
            'type: {1}',
        ]
        return '\n'.join(tpl).format(
            self.name,
            self.type_,
        )

    def _check_value_type(self, val, type_):
        if not isinstance(val, type_):
            tpl = (
                'Rule:\n{0}\n'
                'Arg: {1}\n'
            )
            raise TypeError(tpl.format(self, arg))

    def check_argument(self, arg):
        self._check_value_type(arg, self.type_)


# for list_t(...) and tuple_t(...) and set_t(...)
#      ^ self.type_            ^ self.child
class ArrayDecl(TypeDecl):

    def __init__(self, type_, child):
        super().__init__(type_)
        self.child = child

    def check_argument(self, arg):
        super().check_argument(arg)
        for element in arg:
            self.child.check_argument(element)


# for dict_t(<type decl>, <type decl>)
#      ^ self.type_
#           (           ...          )
#                      ^ self.child
class DictDecl(TypeDecl):

    def __init__(self, type_, key_child, val_child):
        super().__init__(type_)
        self.child = (key_child, val_child)

    def check_argument(self, arg):
        super().check_argument(arg)

        key_child, val_child = self.child
        for key, val in arg.items():
            key_child.check_argument(key)
            val_child.check_argument(val)


class TypeRelationship(object):
    pass


class or_t(TypeRelationship):

    def __init__(self, *raw_types):

        self.childrens = []
        for raw_type in raw_types:
            self.childrens.append(
                type_decl_factory(raw_type),
            )

    def check_argument(self, arg):

        success = False
        for child in self.childrens:
            try:
                child.check_argument(arg)
                success = True
                break
            except TypeError:
                pass
        if not success:
            raise TypeError(
                '{0} cannot match {1}'.format(
                    arg, self.childrens,
                ),
            )
