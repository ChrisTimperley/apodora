# -*- coding: utf-8 -*-
__all__ = ('Module',)

from typing import AbstractSet, Any
import typing

import attr

if typing.TYPE_CHECKING:
    from .program import Program


@attr.s(slots=True, auto_attribs=True)
class Module:
    program: 'Program'
    name: str
    source: str = attr.ib(repr=False)
    imports: AbstractSet[str] = attr.ib(init=False, repr=False)
    ast: Any = attr.ib(init=False, repr=False)
    # TODO: add filepath

    def __getattr__(self, name: str) -> Any:
        if name == 'ast':
            return self._compute_ast()
        return super().__getattr__(name)

    def _compute_ast(self) -> Any:
        self.ast = self.program.parse(self.source)
        return self.ast
