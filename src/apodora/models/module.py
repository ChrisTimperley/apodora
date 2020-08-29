# -*- coding: utf-8 -*-
__all__ = ('Module',)

from typing import AbstractSet, Any
import typing

from loguru import logger
import attr

from ..helpers import ImportVisitor

if typing.TYPE_CHECKING:
    from ..program import Program


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Module:
    program: 'Program'
    name: str
    source: str = attr.ib(repr=False)
    _imports: AbstractSet[str] = attr.ib(init=False, repr=False)
    _ast: Any = attr.ib(init=False, repr=False)
    # TODO: add filepath

    @property
    def ast(self) -> Any:
        if not hasattr(self, '_ast'):
            logger.debug(f'computing AST for module: {self}')
            object.__setattr__(self, '_ast', self.program.parse(self.source))
        return self._ast

    @property
    def imports(self) -> AbstractSet[str]:
        if not hasattr(self, '_imports'):
            visitor = ImportVisitor.for_module(self)
            visitor.visit(self.ast)
            object.__setattr__(self, '_imports', frozenset(visitor.imports))
        return self._imports
