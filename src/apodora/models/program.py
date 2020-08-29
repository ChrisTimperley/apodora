# -*- coding: utf-8 -*-
__all__ = ('Program', 'Py27Program', 'Py3Program')

from types import MappingProxyType
from typed_ast import ast27, ast3
from typing import (AbstractSet, Callable, Generic, Mapping, MutableMapping,
                    TypeVar)
import abc
import functools
import types

import attr

from .module import Module, Py27Module, Py3Module

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
    modules: Mapping[str, Module] = attr.ib(repr=False, init=False)
    _modules: MutableMapping[str, Module] = attr.ib(repr=False, init=False)
    main_module: str = attr.ib(default='__main__')

    def __attrs_post_init__(self) -> None:
        modules: MutableMapping[str, Module] = {}
        read_only_modules: Mapping[str, Module] = MappingProxyType(modules)
        object.__setattr__(self, '_modules', modules)
        object.__setattr__(self, 'modules', read_only_modules)

    @staticmethod
    def from_sources(python: str,
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

        program: Program
        if python.startswith('2.'):
            program = Py27Program(python=python, main_module=main_module)
        elif python.startswith('3.'):
            program = Py3Program(python=python, main_module=main_module)
        else:
            raise ValueError(f"unsupported Python version: {python}")

        # TODO introduce a proper module loader
        for name, source in module_to_source.items():
            module = program.load_module(name, source)
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

    @abc.abstractmethod
    def load_module(self, name: str, source: str) -> Module:
        """Loads a given module from source."""
        ...

    def add_module(self, module: Module) -> None:
        """Registers a given module with this program."""
        assert module.program == self
        self._modules[module.name] = module


class Py27Program(Program[ast27.AST]):
    """Describes a Python 2.7 program."""
    @property
    def is_py2(self) -> bool:
        return True

    @property
    def is_py3(self) -> bool:
        return False

    def load_module(self, name: str, source: str) -> Module:
        """Loads a given module from source."""
        return Py27Module(program=self, name=name, source=source)


class Py3Program(Program[ast3.AST]):
    """Describes a Python 3 program."""
    @property
    def is_py2(self) -> bool:
        return False

    @property
    def is_py3(self) -> bool:
        return True

    def load_module(self, name: str, source: str) -> Module:
        """Loads a given module from source."""
        return Py3Module(program=self, name=name, source=source)
