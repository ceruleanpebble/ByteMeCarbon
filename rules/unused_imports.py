# rules/unused_imports.py
import ast

class UnusedImportRemover(ast.NodeTransformer):
    def __init__(self, used_names):
        self.used_names = used_names

    def visit_Import(self, node):
        new_names = [alias for alias in node.names if alias.asname in self.used_names or alias.name in self.used_names]
        if new_names:
            node.names = new_names
            return node
        return None

    def visit_ImportFrom(self, node):
        new_names = [alias for alias in node.names if alias.asname in self.used_names or alias.name in self.used_names]
        if new_names:
            node.names = new_names
            return node
        return None
