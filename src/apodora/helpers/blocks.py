# -*- coding: utf-8 -*-
__all__ = ('BlockFinder', 'BlockVisitor')

from typing import Any, List, MutableSet, Sequence, Set
import abc
import typing

from loguru import logger
import attr

from ..util import StmtVisitor, Py27StmtVisitor, Py3StmtVisitor

if typing.TYPE_CHECKING:
    from ..program import Program


@attr.s(slots=True, auto_attribs=True)
class BasicBlock:
    stmts: List[Any] = attr.ib(factory=list)  # TODO: figure out type
    predecessors: List['BasicBlock'] = attr.ib(factory=list)
    successors: List['BasicBlock'] = attr.ib(factory=list)
    terminal: bool = attr.ib(default=False)


@attr.s(slots=True)
class BlockVisitor(StmtVisitor):
    # TODO: need to maintain entry blocks
    entry: BasicBlock = attr.ib(factory=BasicBlock)
    _block: BasicBlock = attr.ib(init=False)

    @classmethod
    def for_program(cls, program: 'Program') -> 'BlockVisitor':
        kls = _Py2BlockVisitor if program.is_py2 else _Py3BlockVisitor
        return kls()

    def __attrs_post_init__(self) -> None:
        self._block = self.entry

    def visit_stmt(self, node) -> None:
        print(f"STMT: {node}")
        self._block.stmts.append(node)

    def visit_FunctionDef(self, node) -> None:
        self._block.stmts.append(node)
        print(f"DO NOT GO INSIDE FUNCTION: {node}")

    def visit_For(self, node) -> None:
        print(f"FOR: {node}")

    def visit_If(self, node) -> None:
        print(f"IF: {node}")
        # end the current block
        guard_block = self._block
        guard_block.stmts.append(node)

        # body
        body_block = BasicBlock(predecessors=[guard_block])
        guard_block.successors.append(body_block)
        self._block = body_block
        for stmt in node.body:
            self.visit(stmt)

        # orelse
        else_block = BasicBlock(predecessors=[guard_block])
        guard_block.successors.append(else_block)
        self._block = else_block
        for stmt in node.orelse:
            self.visit(stmt)

        # after the ifelse
        after_block = BasicBlock(predecessors=[body_block, else_block])
        self._block = after_block

    def visit_Return(self, node) -> None:
        print(node)
        self._block.stmts.append(node)
        self._block.terminal = True
        self._block = BasicBlock()  # unreachable block

    def visit_Break(self, node) -> None:
        # exit the loop (_loop_exit_block)
        self._block.stmts.append(node)


class _Py2BlockVisitor(BlockVisitor, Py27StmtVisitor):
    pass


class _Py3BlockVisitor(BlockVisitor, Py3StmtVisitor):
    pass
