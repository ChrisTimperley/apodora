# -*- coding: utf-8 -*-
__all__ = ('ImportFinder',)

from typing import Sequence, Set
import abc
import typing

import attr

from ..util import NodeVisitor, Py27NodeVisitor, Py3NodeVisitor

if typing.TYPE_CHECKING:
    from ..program import Program


@attr.s(frozen=True, slots=True)
class ImportFinder(abc.ABC):
    """
    Limitation: this doesn't track module aliases.
    """
    program: 'Program' = attr.ib()

    @attr.s(slots=True)
    class _Visitor(NodeVisitor):
        module: str = attr.ib()
        imports: Set[str] = attr.ib(factory=set)
        _module_parts: Sequence[str] = attr.ib(init=False)

        def __attrs_post_init__(self) -> None:
            self._module_parts = self.module.split('.')

        def visit_Import(self, node) -> None:
            for alias in node.names:
                self.imports.add(alias.name)

        def visit_ImportFrom(self, node) -> None:
            if node.level:  # relative imports
                if self.module == '__main__':
                    m = 'relative imports not allowed in __main__ script'
                    raise ValueError(m)
                import_from = '.'.join(self._module_parts[:-node.level])
            else:
                import_from = node.module
            self.imports.add(import_from)

    @classmethod
    def for_program(cls, program: 'Program') -> 'ImportFinder':
        """Builds an import finder for a given program."""
        kls = _Py2ImportFinder if program.is_py2 else _Py3ImportFinder
        return kls(program=program)

    @abc.abstractmethod
    def for_module(self, module: str) -> Set[str]:
        """Finds all modules imports within a given module."""
        ...


class _Py2ImportFinder(ImportFinder):
    class _Visitor(ImportFinder._Visitor, Py27NodeVisitor):
        pass

    def for_module(self, module: str) -> Set[str]:
        visitor = _Py2ImportFinder._Visitor(module)
        visitor.visit(self.program.modules[module].ast)
        return visitor.imports


class _Py3ImportFinder(ImportFinder):
    class _Visitor(ImportFinder._Visitor, Py3NodeVisitor):
        pass

    def for_module(self, module: str) -> Set[str]:
        visitor = _Py3ImportFinder._Visitor(module)
        visitor.visit(self.program.modules[module].ast)
        return visitor.imports
