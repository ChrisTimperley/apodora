# -*- coding: utf-8 -*-
import os

import astor
import graphviz

import apodora
import apodora.visualise


def stmt_to_text(stmt) -> str:
    return stmt.__class__.__name__


def stmts_to_text(stmts) -> str:
    text = [stmt_to_text(stmt) for stmt in stmts]
    if len(text) == 1:
        return text[0]
    else:
        return f"< {'; '.join(text)} >"


def label_block(block) -> str:
    return f"{block.id}: {stmts_to_text(block.stmts)}"


def main() -> None:
    filename = 'simple_param/silly_program.py'
    filename = os.path.join(os.path.dirname(__file__), filename)
    with open(filename, 'r') as f:
        contents = f.read()
    module_to_source = {'__main__': contents}
    program = apodora.Program.from_sources(module_to_source=module_to_source, python='2.7')

    # draw imports
    import_graph = apodora.visualise.ImportGraph.for_program(program)
    import_graph.view()
    # import_graph._dot.render('imports.gv', view=True)

    block_visitors = apodora.helpers.BlockVisitor.for_program(program)
    block_visitors.visit(program.modules['__main__'].ast)
    blocks = block_visitors.entry.descendants()

    dot = graphviz.Digraph(comment='Control Flow Graph')

    for block in blocks:
        dot.node(block.id, label_block(block))

    for edge_from in blocks:
        for edge_to in edge_from.successors:
            dot.edge(edge_from.id, edge_to.id)

    # dot.edge('B', 'L')
    dot.render('cfg.gv', view=True)

    # program_cfg = apodora.cfg.ProgramCFG.build(program)


if __name__ == '__main__':
    main()
