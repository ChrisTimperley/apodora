# -*- coding: utf-8 -*-
__all__ = ('MethodCollector', 'Py27MethodCollector', 'Py3MethodCollector')

from typed_ast import ast27 as _ast27
from typed_ast import ast3 as _ast3
from typing import AbstractSet, Generic, MutableSet, Tuple, TypeVar
import abc
import typing

import attr

from ..models import Method, Py27Method, Py3Method
from ..util import NodeVisitor, Py27NodeVisitor, Py3NodeVisitor

if typing.TYPE_CHECKING:
    from ..models import Module, Py27Module, Py3Module


AT = TypeVar('AT', _ast27.FunctionDef, _ast3.FunctionDef)
MOD = TypeVar('MOD', 'Py27Module', 'Py3Module')
MTH = TypeVar('MTH', Py27Method, Py3Method)


@attr.s(slots=True)
class MethodCollector(Generic[AT, MOD, MTH], NodeVisitor):
    module: MOD = attr.ib()
    methods: MutableSet[MTH] = attr.ib(factory=set, repr=False)
    # use deque?
    _dot_prefix: Tuple[str, ...] = attr.ib(factory=tuple, repr=False)

    @classmethod
    def collect(cls, module: MOD) -> AbstractSet[MTH]:
        visitor = cls(module)
        visitor.visit(module.ast)
        return frozenset(visitor.methods)

    # TODO maintain qual name

    def visit_FunctionDef(self, node: AT) -> None:
        name = node.name
        self._dot_prefix = self._dot_prefix + (name,)
        qual_name = '.'.join(self._dot_prefix)

        method = self._create_method(name, qual_name, node)
        self.methods.add(method)

        self.generic_visit(node)
        self._dot_prefix = self._dot_prefix[:-1]

    @abc.abstractmethod
    def _create_method(self, name: str, qual_name: str, node: AT) -> MTH:
        ...


class Py27MethodCollector(
        MethodCollector[_ast27.FunctionDef, 'Py27Module', Py27Method],
        Py27NodeVisitor):
    def _create_method(self,
                       name: str,
                       qual_name: str,
                       node: _ast27.FunctionDef
                       ) -> Py27Method:
        return Py27Method(module=self.module,
                          name=name,
                          qual_name=qual_name,
                          ast=node)


class Py3MethodCollector(
        MethodCollector[_ast3.FunctionDef, 'Py3Module', Py3Method],
        Py3NodeVisitor):
    def _create_method(self,
                       name: str,
                       qual_name: str,
                       node: _ast3.FunctionDef
                       ) -> Py3Method:
        return Py3Method(module=self.module,
                         name=name,
                         qual_name=qual_name,
                         ast=node)
