# -*- coding: utf-8 -*-
__all__ = ('Module', 'Py27Module', 'Py3Module')

from typed_ast import ast27 as _ast27
from typed_ast import ast3 as _ast3
from types import MappingProxyType
from typing import AbstractSet, Any, Generic, Mapping, TypeVar
import abc
import typing

from loguru import logger
import attr

from .method import Py27Method, Py3Method
from ..helpers import Py27ImportVisitor, Py3ImportVisitor
# from ..helpers import MethodCollector


if typing.TYPE_CHECKING:
    from ..program import Program

AT = TypeVar('AT', _ast27.AST, _ast3.AST)
MT = TypeVar('MT', Py27Method, Py3Method)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Module(Generic[AT, MT], abc.ABC):
    program: 'Program'
    name: str
    source: str = attr.ib(repr=False)
    _imports: AbstractSet[str] = attr.ib(init=False, repr=False)
    _ast: AT = attr.ib(init=False, repr=False)
    _methods: Mapping[str, MT] = attr.ib(init=False, repr=False)
    # TODO: add filepath

    @property
    def ast(self) -> AT:
        if not hasattr(self, '_ast'):
            logger.debug(f'computing AST for module: {self}')
            ast = self._compute_ast()
            object.__setattr__(self, '_ast', ast)
        return self._ast

    @property
    def imports(self) -> AbstractSet[str]:
        if not hasattr(self, '_imports'):
            logger.debug(f'computing imports for module: {self}')
            imports = frozenset(self._compute_imports())
            object.__setattr__(self, '_imports', imports)
        return self._imports

#    @property
#    def methods(self) -> Mapping[str, Method]:
#        if not hasattr(self, '_methods'):
#            methods = MethodCollector.for_module(self)
#            name_to_method = {m.name: m for m in methods}
#            name_to_method = MappingProxyType(name_to_method)
#            object.__setattr__(self, '_methods', name_to_method)
#        return self._methods

    @abc.abstractmethod
    def _compute_ast(self) -> AT:
        ...

    @abc.abstractmethod
    def _compute_imports(self) -> AbstractSet[str]:
        ...


class Py27Module(Module[_ast27.AST, Py27Method]):
    def _compute_ast(self) -> _ast27.AST:
        return _ast27.parse(self.source)

    def _compute_imports(self) -> AbstractSet[str]:
        visitor = Py27ImportVisitor(module=self.name)
        visitor.visit(self.ast)
        return visitor.imports


class Py3Module(Module[_ast3.AST, Py3Method]):
    def _compute_ast(self) -> _ast3.AST:
        return _ast3.parse(self.source)

    def _compute_imports(self) -> AbstractSet[str]:
        visitor = Py3ImportVisitor(module=self.name)
        visitor.visit(self.ast)
        return visitor.imports
