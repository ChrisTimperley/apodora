# -*- coding: utf-8 -*-
import tempfile
import typing

import attr
import graphviz

if typing.TYPE_CHECKING:
    from ..models import Program


@attr.s(slots=True, auto_attribs=True)
class ImportGraph:
    _dot: graphviz.Digraph

    @classmethod
    def for_program(cls, program: 'Program') -> 'ImportGraph':
        dot = graphviz.Digraph(comment='Import Graph')

        for module_name in program.modules:
            dot.node(module_name, module_name)

        for module in program.modules.values():
            for import_name in module.imports:
                dot.edge(module.name, import_name)

        return ImportGraph(dot)

    def render(self, filename: str, view: bool = False) -> None:
        """Renders this graph to a given file and optionally view it."""
        self._dot.render(filename, view=view)

    def view(self) -> None:
        """Views the graph."""
        self._dot.view(tempfile.mktemp('.gv'))
