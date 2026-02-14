import ast


class UnusedFunctionRemover(ast.NodeTransformer):
    def __init__(self, called_functions):
        self.called_functions = called_functions

    def visit_FunctionDef(self, node):
        # Keep function if it is called
        if node.name in self.called_functions:
            return node

        # Otherwise remove it
        return None


class FunctionCallCollector(ast.NodeVisitor):
    def __init__(self):
        self.called = set()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        self.generic_visit(node)


def collect_called_functions(tree):
    collector = FunctionCallCollector()
    collector.visit(tree)
    return collector.called
