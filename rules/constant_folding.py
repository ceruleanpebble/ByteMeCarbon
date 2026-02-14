# rules/constant_folding.py
import ast

class ConstantFolder(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)

        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                value = eval(compile(ast.Expression(node), filename="", mode="eval"))
                return ast.Constant(value=value)
            except Exception:
                return node

        return node
