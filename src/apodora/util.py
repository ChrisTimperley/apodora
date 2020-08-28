# -*- coding: utf-8 -*-
__all__ = ('NodeVisitor', 'Py27NodeVisitor', 'Py3NodeVisitor',
           'StmtVisitor', 'Py27StmtVisitor', 'Py3StmtVisitor')

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


class StmtVisitor(NodeVisitor, abc.ABC):
    @abc.abstractmethod
    def generic_visit(self, node) -> None:
        ...

    def visit_stmt(self, node) -> None:
        self.generic_visit(node)


class Py27StmtVisitor(StmtVisitor, Py27NodeVisitor):
    def visit_stmt(self, node) -> None:
        super().visit_stmt(node)

    visit_FunctionDef = visit_stmt
    visit_ClassDef = visit_stmt
    visit_Return = visit_stmt
    visit_Delete = visit_stmt
    visit_Assign = visit_stmt
    visit_AugAssign = visit_stmt
    visit_Print = visit_stmt
    visit_For = visit_stmt
    visit_While = visit_stmt
    visit_If = visit_stmt
    visit_With = visit_stmt
    visit_Raise = visit_stmt
    visit_TryExcept = visit_stmt
    visit_TryFinally = visit_stmt
    visit_Assert = visit_stmt
    visit_Import = visit_stmt
    visit_ImportFrom = visit_stmt
    visit_Exec = visit_stmt
    visit_Global = visit_stmt
    visit_Expr = visit_stmt
    visit_Pass = visit_stmt
    visit_Break = visit_stmt
    visit_Continue = visit_stmt


class Py3StmtVisitor(StmtVisitor, Py3NodeVisitor):
    def visit_stmt(self, node) -> None:
        super().visit_stmt(node)

    visit_FunctionDef = visit_stmt
    visit_AsyncFunctionDef = visit_stmt
    visit_ClassDef = visit_stmt
    visit_Return = visit_stmt
    visit_Delete = visit_stmt
    visit_Assign = visit_stmt
    visit_AugAssign = visit_stmt
    visit_AnnAssign = visit_stmt
    visit_For = visit_stmt
    visit_AsyncFor = visit_stmt
    visit_While = visit_stmt
    visit_If = visit_stmt
    visit_With = visit_stmt
    visit_AsyncWith = visit_stmt
    visit_Raise = visit_stmt
    visit_Try = visit_stmt
    visit_Assert = visit_stmt
    visit_Import = visit_stmt
    visit_ImportFrom = visit_stmt
    visit_Global = visit_stmt
    visit_Nonlocal = visit_stmt
    visit_Expr = visit_stmt
    visit_Pass = visit_stmt
    visit_Break = visit_stmt
    visit_Continue = visit_stmt
