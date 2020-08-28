# -*- coding: utf-8 -*-
__all__ = ('NodeVisitor', 'Py27NodeVisitor', 'Py3NodeVisitor',
           'StmtVisitor', 'Py27StmtVisitor', 'Py3StmtVisitor')

from typed_ast import ast27, ast3
import abc


class NodeVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_children(self, node) -> None:
        ...

    @abc.abstractmethod
    def visit(self, node) -> None:
        ...

    @abc.abstractmethod
    def generic_visit(self, node) -> None:
        ...


class Py27NodeVisitor(ast27.NodeVisitor, NodeVisitor):
    def visit_children(self, node) -> None:
        for child in ast27.iter_child_nodes(node):
            self.generic_visit(child)


class Py3NodeVisitor(ast3.NodeVisitor, NodeVisitor):
    def visit_children(self, node) -> None:
        for child in ast3.iter_child_nodes(node):
            self.generic_visit(child)


class StmtVisitor(NodeVisitor, abc.ABC):
    def visit_stmt(self, node) -> None:
        self.generic_visit(node)


class Py27StmtVisitor(StmtVisitor, Py27NodeVisitor):
    def visit_FunctionDef(self, node) -> None:
        self.visit_stmt(node)

    def visit_ClassDef(self, node) -> None:
        self.visit_stmt(node)

    def visit_Return(self, node) -> None:
        self.visit_stmt(node)

    def visit_Delete(self, node) -> None:
        self.visit_stmt(node)

    def visit_Assign(self, node) -> None:
        self.visit_stmt(node)

    def visit_AugAssign(self, node) -> None:
        self.visit_stmt(node)

    def visit_Print(self, node) -> None:
        self.visit_stmt(node)

    def visit_For(self, node) -> None:
        self.visit_stmt(node)

    def visit_While(self, node) -> None:
        self.visit_stmt(node)

    def visit_If(self, node) -> None:
        self.visit_stmt(node)

    def visit_With(self, node) -> None:
        self.visit_stmt(node)

    def visit_Raise(self, node) -> None:
        self.visit_stmt(node)

    def visit_TryExcept(self, node) -> None:
        self.visit_stmt(node)

    def visit_TryFinally(self, node) -> None:
        self.visit_stmt(node)

    def visit_Assert(self, node) -> None:
        self.visit_stmt(node)

    def visit_Import(self, node) -> None:
        self.visit_stmt(node)

    def visit_ImportFrom(self, node) -> None:
        self.visit_stmt(node)

    def visit_Exec(self, node) -> None:
        self.visit_stmt(node)

    def visit_Global(self, node) -> None:
        self.visit_stmt(node)

    def visit_Expr(self, node) -> None:
        self.visit_stmt(node)

    def visit_Pass(self, node) -> None:
        self.visit_stmt(node)

    def visit_Break(self, node) -> None:
        self.visit_stmt(node)

    def visit_Continue(self, node) -> None:
        self.visit_stmt(node)


class Py3StmtVisitor(StmtVisitor, Py3NodeVisitor):
    def visit_FunctionDef(self, node) -> None:
        self.visit_stmt(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        self.visit_stmt(node)

    def visit_ClassDef(self, node) -> None:
        self.visit_stmt(node)

    def visit_Return(self, node) -> None:
        self.visit_stmt(node)

    def visit_Delete(self, node) -> None:
        self.visit_stmt(node)

    def visit_Assign(self, node) -> None:
        self.visit_stmt(node)

    def visit_AugAssign(self, node) -> None:
        self.visit_stmt(node)

    def visit_AnnAssign(self, node) -> None:
        self.visit_stmt(node)

    def visit_For(self, node) -> None:
        self.visit_stmt(node)

    def visit_AsyncFor(self, node) -> None:
        self.visit_stmt(node)

    def visit_While(self, node) -> None:
        self.visit_stmt(node)

    def visit_If(self, node) -> None:
        self.visit_stmt(node)

    def visit_With(self, node) -> None:
        self.visit_stmt(node)

    def visit_AsyncWith(self, node) -> None:
        self.visit_stmt(node)

    def visit_Raise(self, node) -> None:
        self.visit_stmt(node)

    def visit_Try(self, node) -> None:
        self.visit_stmt(node)

    def visit_Assert(self, node) -> None:
        self.visit_stmt(node)

    def visit_Import(self, node) -> None:
        self.visit_stmt(node)

    def visit_ImportFrom(self, node) -> None:
        self.visit_stmt(node)

    def visit_Global(self, node) -> None:
        self.visit_stmt(node)

    def visit_Nonlocal(self, node) -> None:
        self.visit_stmt(node)

    def visit_Expr(self, node) -> None:
        self.visit_stmt(node)

    def visit_Pass(self, node) -> None:
        self.visit_stmt(node)

    def visit_Break(self, node) -> None:
        self.visit_stmt(node)

    def visit_Continue(self, node) -> None:
        self.visit_stmt(node)
