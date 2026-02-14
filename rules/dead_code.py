# rules/dead_code.py
"""
Dead code removal optimization rule.

Removes unreachable code branches by evaluating constant conditions.
Example: if True: ... else: ... -> ... (keeps only if block)
"""

import ast

class DeadCodeRemover(ast.NodeTransformer):
    """Removes unreachable code based on constant conditions."""
    
    def visit_If(self, node):
        """
        Visit an if statement and remove unreachable branches.
        
        If the condition is a constant True or False, keep only the 
        reachable branch. Otherwise, keep the full if statement.
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.AST: Either the reachable branch(es) or the original node
        """
        self.generic_visit(node)

        # Check if condition is a constant
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                # Condition always true, keep the if block
                return node.body
            elif node.test.value is False:
                # Condition always false, keep the else block
                return node.orelse

        return node
