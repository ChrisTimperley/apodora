# -*- coding: utf-8 -*-
__all__ = ('BasicBlock', 'BlockNumbering')

from collections import deque
from typing import Any, Deque, List, Set

import attr


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
