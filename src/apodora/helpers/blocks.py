# -*- coding: utf-8 -*-
__all__ = ('BlockFinder', 'BlockVisitor')

from collections import deque
from typing import Any, Deque, List, Optional, MutableSet, Sequence, Set
import abc
import typing

from loguru import logger
import attr

from ..util import StmtVisitor, Py27StmtVisitor, Py3StmtVisitor

from ..models import BasicBlock, BlockNumbering

if typing.TYPE_CHECKING:
    from ..program import Program


@attr.s(slots=True)
class BlockVisitor(StmtVisitor):
    numbering: BlockNumbering = attr.ib(factory=BlockNumbering)
    entry: BasicBlock = attr.ib(init=False)
    _block: BasicBlock = attr.ib(init=False)
    _loop_header_block: Optional[BasicBlock] = attr.ib(default=None)
    _loop_end_block: Optional[BasicBlock] = attr.ib(default=None)

    def __attrs_post_init__(self) -> None:
        self.entry = self.create_block()
        self._block = self.entry

    @classmethod
    def for_program(cls, program: 'Program') -> 'BlockVisitor':
        kls = _Py2BlockVisitor if program.is_py2 else _Py3BlockVisitor
        return kls()

    @property
    def inside_loop(self) -> bool:
        return self._loop_header_block is not None

    def create_link(self,
                    from_block: BasicBlock,
                    to_block: BasicBlock
                    ) -> None:
        from_block.successors.append(to_block)
        to_block.predecessors.append(from_block)

    def create_block(self,
                     *,
                     predecessors: Optional[List['BasicBlock']] = None,
                     successors: Optional[List['BasicBlock']] = None,
                     terminal: bool = False
                     ) -> None:
        block = BasicBlock.create_with_numbering(self.numbering)
        block.terminal = terminal
        if predecessors:
            block.predecessors = predecessors
        if successors:
            block.successors = successors
        return block

    def visit_stmt(self, node) -> None:
        self._block.stmts.append(node)

    def visit_FunctionDef(self, node) -> None:
        self._block.stmts.append(node)
        print(f"DO NOT GO INSIDE FUNCTION: {node}")

    def visit_For(self, node) -> None:
        if node.orelse:
            m = "no handling of orelse for For statements"
            raise NotImplementedError(m)

        outer_loop_header_block = self._loop_header_block
        outer_loop_end_block = self._loop_end_block

        # the current block will be known as the loop header block
        loop_header_block = self._block
        loop_header_block.stmts.append(node)
        self._loop_header_block = loop_header_block
        logger.debug(f"Loop header block: {loop_header_block}")

        # create a block for after the loop
        loop_end_block = self.create_block()
        logger.debug(f"Loop end block: {loop_end_block}")
        self.create_link(loop_header_block, loop_end_block)
        self._loop_end_block = loop_end_block

        # handle the body of the loop
        loop_body_block = self.create_block()
        logger.debug(f"Loop body block: {loop_body_block}")
        self.create_link(loop_header_block, loop_body_block)
        self._block = loop_body_block
        for stmt in node.body:
            self.visit(stmt)

        # unless we've encountered a break/continue, connect the last
        # basic block inside the loop to both the header and end of the loop
        if not self._block.successors:
            print("COOL?")
            self._block.successors += [loop_header_block, loop_end_block]

        # switch to building the loop end block
        self._block = loop_end_block

        # restore the previous loop header and end blocks, if any
        self._loop_header_block = outer_loop_header_block
        self._loop_end_block = outer_loop_end_block

    def visit_If(self, node) -> None:
        # end the current block
        guard_block = self._block
        guard_block.stmts.append(node)
        logger.debug(f"If guard block: {guard_block}")

        # body
        body_block = self.create_block()
        logger.debug(f"If body block: {body_block}")
        self.create_link(guard_block, body_block)
        self._block = body_block
        for stmt in node.body:
            self.visit(stmt)

        # orelse
        else_block = self.create_block()
        logger.debug(f"If else block: {else_block}")
        self.create_link(guard_block, else_block)
        self._block = else_block
        for stmt in node.orelse:
            self.visit(stmt)

        # after the ifelse
        after_block = self.create_block()
        logger.debug(f"If after block: {after_block}")
        self.create_link(body_block, after_block)
        self.create_link(else_block, after_block)
        self._block = after_block

    def visit_Return(self, node) -> None:
        print(node)
        self._block.stmts.append(node)
        self._block.terminal = True
        self._block = self.create_block(terminal=True)  # unreachable

    def visit_Break(self, node) -> None:
        assert self.inside_loop
        self._block.stmts.append(node)
        self._block.successors.append(self._loop_end_block)
        self._block = self.create_block(terminal=True)  # unreachable


class _Py2BlockVisitor(BlockVisitor, Py27StmtVisitor):
    pass


class _Py3BlockVisitor(BlockVisitor, Py3StmtVisitor):
    pass
