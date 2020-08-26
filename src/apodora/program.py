# -*- coding: utf-8 -*-
__all__ = ('Program',)

from typing import Mapping
import functools
import types

import attr
import parso


@attr.s(slots=True, frozen=True)
class Program:
    """Describes the program under analysis.

    Attributes
    ----------
    python: str
        The version of Python used by the program.
    module_to_source: Mapping[str, str]
        The source code for each module, indexed by module name.
    module_to_ast: Mapping[str, parso.tree.NodeOrLeaf]
        The AST for each module, indexed by module name.
    main_module: str
        The name of the Python module that provides the entrypoint for the
        program. For now, we do not consider method entrypoints.

    Raises
    ------
    ValueError
        If no source code has been provided for the main module.
    """
    python: str = attr.ib()
    module_to_source: Mapping[str, str] = attr.ib(repr=False)
    module_to_ast: Mapping[str, parso.tree.NodeOrLeaf] = \
        attr.ib(repr=False, init=False)
    main_module: str = attr.ib(default='__main__')

    @main_module.validator
    def main_module_has_source(self, attribute, value: str) -> None:
        if not value in self.module_to_source:
            msg = f'source not provided for main module [{value}]'
            raise ValueError(msg)

    def __attrs_post_init__(self) -> None:
        module_to_source = types.MappingProxyType(self.module_to_source)
        object.__setattr__(self, 'module_to_source', module_to_source)

        parse_ast = functools.partial(parso.parse, version=self.python)
        module_to_ast: Mapping[str, parso.tree.NodeOrLeaf] = {
            name: parse_ast(source) for (name, source)
            in module_to_source.items()
        }
        module_to_ast = types.MappingProxyType(module_to_ast)
        object.__setattr__(self, 'module_to_ast', module_to_ast)
