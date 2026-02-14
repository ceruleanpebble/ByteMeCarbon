# rules/dead_code.py
import ast

class DeadCodeRemover(ast.NodeTransformer):
    def visit_If(self, node):
        self.generic_visit(node)

        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                return node.body
            elif node.test.value is False:
                return node.orelse

        return node
