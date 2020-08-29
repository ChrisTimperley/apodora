# -*- coding: utf-8 -*-
__all__ = ('ModuleCFG', 'ProgramCFG')

from collections import deque
from typing import (AbstractSet, Deque, Dict, List, MutableSequence, Optional,
                    Tuple)
from typed_ast import ast27, ast3
import abc
import ast
import typing

from loguru import logger
import attr

from .util import NodeVisitor, Py27NodeVisitor, Py3NodeVisitor

if typing.TYPE_CHECKING:
    from .program import Program


# TODO: ENTER/EXIT (i.e., source/sink)
@attr.s(slots=True)
class BasicBlock:
    number: int = attr.ib()
    statements = attr.ib(factory=list)
    calls: AbstractSet[str] = attr.ib(factory=list)
    # predecessors
    # successors

    def add_exit(self, exit: 'BasicBlock') -> None:
        raise NotImplementedError


@attr.s(slots=True)
class ModuleCFGVisitor(NodeVisitor):
    """
    Limitation: this doesn't track module aliases.
    """
    module: str = attr.ib()
    namespace: str = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self.namespace = self.module



@attr.s(slots=True)
class ModuleCFG:
    """
    Attributes
    ----------
    program: Program
        The program to which this CFG belongs.
    module: str
        The name of the module that this CFG represents.
    imports: AbstractSet[str]
        The fully-qualified names of the modules that are imported into this
        module.
    """
    program: 'Program' = attr.ib()
    module: str = attr.ib()
    imports: AbstractSet[str] = attr.ib()

    @classmethod
    def build(cls, program: 'Program', module: str) -> 'ModuleCFG':
        raise NotImplementedError

        ast = program.module_to_ast[module]

        visitor: ModuleCFGVisitor
        if program.is_py2:
            visitor = Py27ModuleCFGVisitor(module=module)
        elif program.is_py3:
            visitor = Py3ModuleCFGVisitor(module=module)
        else:
            m = f"unable to build CFG for Python version {program.python}"
            raise ValueError(m)

        visitor.visit(ast)

        # TODO
        cfg = ModuleCFG(program=program, module=module)
        return cfg

    @module.validator
    def module_in_program(self, attribute, value: str) -> None:
        if not value in self.program.modules:
            msg = f'module [{value}] not found in program [{self.program}]'
            raise ValueError(msg)


@attr.s(slots=True)
class ProgramCFG:
    program: 'Program' = attr.ib()
    module_to_cfg: Dict[str, ModuleCFG] = attr.ib(factory=dict)

    @classmethod
    def build(cls, program: 'Program') -> 'ProgramCFG':
        # start with the main module
        module_to_cfg: Dict[str, ModuleCFG] = {}
        for module in program.modules:
            logger.debug(f'building CFG for module: {module}')
            cfg = ModuleCFG.build(program, module)
            logger.debug(f'built CFG for module: {module}')
            module_to_cfg[module] = cfg
        return ProgramCFG(program=program, module_to_cfg=module_to_cfg)
