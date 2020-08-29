# -*- coding: utf-8 -*-
__all__ = ('Method', 'Py27Method', 'Py3Method')

from typed_ast import ast27, ast3
from typing import Generic, TypeVar
import typing

import attr

if typing.TYPE_CHECKING:
    from .module import Module

T = TypeVar('T', ast27.FunctionDef, ast3.FunctionDef)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class Method(Generic[T], abc.ABC):
    """Describes a method.

    Attributes
    ----------
    module: Module
        The module to which the method belongs.
    name: str
        The name of the method, relative to the module.
    qual_name: str
        The qualified name of the method (see PEP 3155).
    ast: T
        The abstract syntax tree for the method.
    """
    module: 'Module'
    name: str
    qual_name: str
    ast: T


class Py27Method(Method[ast27.FunctionDef]):
    """Describes a Python 2.7 method."""


class Py3Method(Method[ast3.FunctionDef]):
    """Describes a Python 3 method."""
