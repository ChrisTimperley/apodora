# -*- coding: utf-8 -*-
__all__ = ('BlockFinder', 'BlockVisitor')

from collections import deque
from typing import Any, Deque, List, Optional, MutableSet, Sequence, Set
import abc
import typing

from loguru import logger
import attr

from ..util import StmtVisitor, Py27StmtVisitor, Py3StmtVisitor

if typing.TYPE_CHECKING:
    from ..program import Program


@attr.s(slots=True)
class BlockNumbering:
    _next: int = attr.ib(default=0)

    @classmethod
    def starting_from(cls, number: int) -> 'BlockNumbering':
        return BlockNumbering(number)

    def __next__(self) -> int:
        num = self._next
        self._next += 1
        return num


@attr.s(slots=True, auto_attribs=True, eq=False, hash=False)
class BasicBlock:
    number: int = attr.ib()
    stmts: List[Any] = attr.ib(factory=list)  # TODO: figure out type
    predecessors: List['BasicBlock'] = attr.ib(factory=list)
    successors: List['BasicBlock'] = attr.ib(factory=list)
    terminal: bool = attr.ib(default=False)

    @property
    def id(self) -> str:
        return f'B{self.number}'

    def __hash__(self) -> int:
        return self.number

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BasicBlock) and other.number == self.number

    def __str__(self) -> str:
        return self.id

    @classmethod
    def create_with_numbering(cls, numbering: BlockNumbering) -> 'BasicBlock':
        number = next(numbering)
        return BasicBlock(number)

    def descendants(self) -> Set['BasicBlock']:
        q: Deque[BasicBlock] = deque([self])
        seen = set([self])
        descendants = set()
        while q:
            block = q.pop()
            descendants.add(block)
            for successor in block.successors:
                if successor not in seen:
                    seen.add(successor)
                    q.append(successor)
        return descendants


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
        loop_end_block = self.create_block(predecessors=[loop_header_block])
        loop_header_block.successors.append(loop_end_block)
        self._loop_end_block = loop_end_block

        # handle the body of the loop
        loop_body_block = self.create_block(predecessors=[loop_header_block])
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
        body_block = self.create_block(predecessors=[guard_block])
        guard_block.successors.append(body_block)
        self._block = body_block
        for stmt in node.body:
            self.visit(stmt)

        # orelse
        else_block = self.create_block(predecessors=[guard_block])
        guard_block.successors.append(else_block)
        self._block = else_block
        for stmt in node.orelse:
            self.visit(stmt)

        # after the ifelse
        after_block = self.create_block(predecessors=[body_block, else_block])
        else_block.successors.append(after_block)
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
