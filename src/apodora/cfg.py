# -*- coding: utf-8 -*-
from typing import Deque, Dict
from collections import deque
import typing

from loguru import logger
import attr

if typing.TYPE_CHECKING:
    from .program import Program


@attr.s(slots=True)
class ModuleCFG:
    program: 'Program' = attr.ib()
    module: str = attr.ib()

    @classmethod
    def build(cls, program: 'Program', module: str) -> 'ModuleCFG':
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
