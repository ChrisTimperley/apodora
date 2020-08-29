# -*- coding: utf-8 -*-
__all__ = ('Program', 'Py27Program', 'Py3Program')

from typing import AbstractSet, Callable, Generic, Mapping, TypeVar
from typed_ast import ast27, ast3
import abc
import functools
import types

import attr

from .models import Module

T = TypeVar('T', ast27.AST, ast3.AST)


@attr.s(slots=True, frozen=True)
class Program(Generic[T], abc.ABC):
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
            m = f"source code must be provided for main module: {main_module}"
            raise ValueError(m)

        if python.startswith('2.'):
            program_kls = Py27Program
        elif python.startswith('3.'):
            program_kls = Py3Program
        else:
            raise ValueError(f"unsupported Python version: {python}")

        program = program_kls(python=python, main_module=main_module)
        for name, source in module_to_source.items():
            module = Module(program=program, name=name, source=source)
            program.add_module(module)
        return program

    @property
    @abc.abstractmethod
    def is_py2(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def is_py3(self) -> bool:
        ...

    def add_module(self, module: Module) -> None:
        """Registers a given module with this program."""
        assert module.program == self
        self.modules[module.name] = module

    @abc.abstractmethod
    def parse(self, source: str) -> T:
        ...


class Py27Program(Program[ast27.AST]):
    """Describes a Python 2.7 program."""
    @property
    def is_py2(self) -> bool:
        return True

    @property
    def is_py3(self) -> bool:
        return False

    def parse(self, source: str) -> ast27.AST:
        return ast27.parse(source)


class Py3Program(Program[ast3.AST]):
    """Describes a Python 3 program."""
    @property
    def is_py2(self) -> bool:
        return False

    @property
    def is_py3(self) -> bool:
        return True

    def parse(self, source: str) -> ast3.AST:
        return ast3.parse(source)
