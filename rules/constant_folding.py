# rules/constant_folding.py
"""
Constant folding optimization rule.

Evaluates constant expressions at compile time instead of runtime.
Example: 2 + 3 -> 5
"""

import ast

class ConstantFolder(ast.NodeTransformer):
    """Transforms constant binary operations into their computed values."""
    
    def visit_BinOp(self, node):
        """
        Visit a binary operation node and fold if both operands are constants.
        
        Args:
            node (ast.BinOp): The binary operation node
            
        Returns:
            ast.AST: Either the folded constant or the original node
        """
        self.generic_visit(node)

        # Check if both operands are constants
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                # Safely evaluate the operation
                value = eval(compile(ast.Expression(node), filename="", mode="eval"))
                return ast.Constant(value=value)
            except Exception:
                # If evaluation fails, keep original
                return node

        return node
