# -*- coding: utf-8 -*-
__all__ = ('NodeVisitor', 'Py27NodeVisitor', 'Py3NodeVisitor')

from typed_ast import ast27, ast3
import abc


class NodeVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_children(self, node) -> None:
        ...


class Py27NodeVisitor(NodeVisitor, ast27.NodeVisitor):
    def visit_children(self, node) -> None:
        for child in ast27.iter_child_nodes(node):
            self.generic_visit(child)


class Py3NodeVisitor(NodeVisitor, ast3.NodeVisitor):
    def visit_children(self, node) -> None:
        for child in ast3.iter_child_nodes(node):
            self.generic_visit(child)
