# -*- coding: utf-8 -*-
__all__ = ('BlockFinder', 'BlockVisitor')

from typing import Any, List, Optional, MutableSet, Sequence, Set
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
    _loop_header_block: Optional[BasicBlock] = attr.ib(default=None)
    _loop_end_block: Optional[BasicBlock] = attr.ib(default=None)

    @classmethod
    def for_program(cls, program: 'Program') -> 'BlockVisitor':
        kls = _Py2BlockVisitor if program.is_py2 else _Py3BlockVisitor
        return kls()

    @property
    def inside_loop(self) -> bool:
        return self._loop_header_block is not None

    def __attrs_post_init__(self) -> None:
        self._block = self.entry

    def visit_stmt(self, node) -> None:
        print(f"STMT: {node}")
        self._block.stmts.append(node)

    def visit_FunctionDef(self, node) -> None:
        self._block.stmts.append(node)
        print(f"DO NOT GO INSIDE FUNCTION: {node}")

    def visit_For(self, node) -> None:
        if node.orelse:
            m = "no handling of orelse for For statements"
            raise NotImplementedError(m)

        print(f"FOR: {node}")
        outer_loop_header_block = self._loop_header_block
        outer_loop_end_block = self._loop_end_block

        # the current block will be known as the loop header block
        loop_header_block = self._block
        loop_header_block.stmts.append(node)
        self._loop_header_block = loop_header_block

        # create a block for after the loop
        loop_end_block = BasicBlock(predecessors=[loop_header_block])
        loop_header_block.successors.append(loop_end_block)
        self._loop_end_block = loop_end_block

        # handle the body of the loop
        loop_body_block = BasicBlock(predecessors=[loop_header_block])
        loop_header_block.successors.append(loop_body_block)
        self._block = loop_body_block
        for stmt in node.body:
            self.visit(stmt)

        # unless we've encountered a break/continue, connect the last
        # basic block inside the loop to both the header and end of the loop
        if not self._block.successors:
            self._block.successors += [loop_header_block, loop_end_block]

        # restore the previous loop header and end blocks, if any
        self._loop_header_block = outer_loop_header_block
        self._loop_end_block = outer_loop_end_block

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
        assert self.inside_loop
        self._block.stmts.append(node)
        self._block.successors.append(self._loop_end_block)
        self._block = BasicBlock(terminal=True)  # unreachable


class _Py2BlockVisitor(BlockVisitor, Py27StmtVisitor):
    pass


class _Py3BlockVisitor(BlockVisitor, Py3StmtVisitor):
    pass
