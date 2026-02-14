# analyzer.py
import ast

class NameCollector(ast.NodeVisitor):
    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        self.names.add(node.id)
        self.generic_visit(node)

def collect_used_names(tree):
    collector = NameCollector()
    collector.visit(tree)
    return collector.names
