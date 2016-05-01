# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa


class MagicError(Exception):

    def __init__(self, message='[Empty Message]', **kwargs):
        super().__init__(conditional_to_bytes(message))

        self._message = message
        self._kwargs = kwargs

    def __str__(self):
        title = '{exception_name}: {message}'.format(
            exception_name=type(self).__name__,
            message=self._message,
        )
        sep_line = '-' * len(title)

        kv_line_template = '{0}: {1}'
        kv_lines = '\n'.join(map(
            lambda p: kv_line_template.format(p[0], p[1]),
            sorted(self._kwargs.items(), key=lambda p: p[0]),
        ))

        return conditional_to_bytes(
            # prefix \n for traceback display.
            '\n{title}\n{sep_line}\n{kv_lines}\n{sep_line}'.format(
                title=title,
                kv_lines=kv_lines or '[Empty kwargs]',
                sep_line=sep_line,
            ),
        )

    def serialize(self):
        ret = dict(self._kwargs)
        ret['message'] = self._message
        return ret


class MagicSyntaxError(MagicError, SyntaxError):
    pass


class MagicTypeError(MagicError, TypeError):
    pass


class MagicIndexError(MagicError, IndexError):
    pass


from magic_constraints.utils import conditional_to_bytes  # noqa
