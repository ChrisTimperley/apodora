# -*- coding: utf-8 -*-
__all__ = ('Program',)

from typing import AbstractSet, Callable, Generic, Mapping, TypeVar
from typed_ast import ast27, ast3
import functools
import types

import attr

from .models import Module

T = TypeVar('T', ast27.AST, ast3.AST)


@attr.s(slots=True, frozen=True)
class Program(Generic[T]):
    """Describes the program under analysis.

    Attributes
    ----------
    python: str
        The version of Python used by the program.
    module_to_source: Mapping[str, Module]
        The modules for this program, indexed by name.
    main_module: str
        The name of the Python module that provides the entrypoint for the
        program. For now, we do not consider method entrypoints.
    """
    python: str = attr.ib(validator=attr.validators.instance_of(str))
    modules: Mapping[str, Module] = attr.ib(repr=False, factory=dict)
    main_module: str = attr.ib(default='__main__')

    @classmethod
    def from_sources(cls,
                     python: str,
                     module_to_source: Mapping[str, str],
                     main_module: str = '__main__'
                     ) -> 'Program':
        """Builds a program from a set of module sources.

        Raises
        ------
        ValueError
            If no source code has been provided for the main module.
        """
        if main_module not in module_to_source:
            raise ValueError("source code must be provided for main module.")
        program = Program(python=python, main_module=main_module)
        for name, source in module_to_source.items():
            module = Module(program=program, name=name, source=source)
            program.add_module(module)
        return program

    @property
    def is_py2(self) -> bool:
        return self.python.startswith('2.')

    @property
    def is_py3(self) -> bool:
        return self.python.startswith('3.')

    def add_module(self, module: Module) -> None:
        """Registers a given module with this program."""
        assert module.program == self
        self.modules[module.name] = module

    # TODO add Py27Program and Py3Program
    def parse(self, source: str):
        """Parses a given source text to an abstract syntax tree."""
        parse_ast: Callable[[str], 'T'] = \
            ast27.parse if self.is_py2 else ast3.parse  # type: ignore
        return parse_ast(source)
