# -*- coding: utf-8 -*-
__all__ = ('Program',)

from typing import AbstractSet, Generic, Mapping, TypeVar
from typed_ast import ast27, ast3
import functools
import types

import attr

T = TypeVar('T', ast27.AST, ast3.AST)


@attr.s(slots=True, frozen=True)
class Program(Generic[T]):
    """Describes the program under analysis.

    Attributes
    ----------
    python: str
        The version of Python used by the program.
    module_to_source: Mapping[str, str]
        The source code for each module, indexed by module name.
    module_to_ast: Mapping[str, T]
        The AST for each module, indexed by module name.
    modules: AbstractSet[str]
        The names of the modules for this program.
    main_module: str
        The name of the Python module that provides the entrypoint for the
        program. For now, we do not consider method entrypoints.

    Raises
    ------
    ValueError
        If no source code has been provided for the main module.
    """
    python: str = attr.ib(validator=attr.validators.instance_of(str))
    module_to_source: Mapping[str, str] = attr.ib(repr=False)
    module_to_ast: Mapping[str, 'T'] = \
        attr.ib(repr=False, init=False)
    modules: AbstractSet[str] = attr.ib(init=False, repr=False)
    main_module: str = attr.ib(default='__main__')

    @main_module.validator
    def main_module_has_source(self, attribute, value: str) -> None:
        if not value in self.module_to_source:
            msg = f'source not provided for main module [{value}]'
            raise ValueError(msg)

    @property
    def is_py2(self) -> bool:
        return self.python.startswith('2.')

    @property
    def is_py3(self) -> bool:
        return self.python.startswith('3.')

    def __attrs_post_init__(self) -> None:
        modules: AbstractSet[str] = frozenset(self.module_to_source)
        object.__setattr__(self, 'modules', modules)

        module_to_source = types.MappingProxyType(self.module_to_source)
        object.__setattr__(self, 'module_to_source', module_to_source)

        parse_ast = ast27.parse if self.is_py2 else ast3.parse
        module_to_ast: Mapping[str, parso.tree.NodeOrLeaf] = {
            name: parse_ast(source) for (name, source)
            in module_to_source.items()
        }
        module_to_ast = types.MappingProxyType(module_to_ast)
        object.__setattr__(self, 'module_to_ast', module_to_ast)
