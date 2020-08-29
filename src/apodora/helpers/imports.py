# -*- coding: utf-8 -*-
__all__ = ('ImportVisitor', 'Py27ImportVisitor', 'Py3ImportVisitor')

from typing import Sequence, Set
import abc
import typing

import attr

from ..util import NodeVisitor, Py27NodeVisitor, Py3NodeVisitor

if typing.TYPE_CHECKING:
    from ..models import Module


@attr.s(slots=True)
class ImportVisitor(NodeVisitor):
    """
    Limitation: this doesn't track module aliases.
    """
    module: str = attr.ib()
    imports: Set[str] = attr.ib(factory=set)
    _module_parts: Sequence[str] = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._module_parts = self.module.split('.')

    @staticmethod
    def for_module(module: 'Module') -> 'ImportVisitor':
        if module.program.is_py2:
            kls = Py27ImportVisitor
        elif module.program.is_py3:
            kls = Py3ImportVisitor
        else:
            m = f'module uses unknown Python version: {module.python}'
            raise ValueError(m)
        return kls(module=module.name)

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


class Py27ImportVisitor(ImportVisitor, Py27NodeVisitor):
    pass


class Py3ImportVisitor(ImportVisitor, Py3NodeVisitor):
    pass
