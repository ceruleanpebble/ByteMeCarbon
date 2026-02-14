# complexity.py
"""
Code complexity analysis module.

Estimates time complexity of code by analyzing loop depth and control structures.
"""

import ast

class LoopDepthAnalyzer(ast.NodeVisitor):
    """Analyzes loop nesting depth to estimate time complexity."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.max_depth = 0
        self.current_depth = 0

    def visit_For(self, node):
        """
        Visit a For loop node and update depth.
        
        Args:
            node (ast.For): The for loop node to visit
        """
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        """
        Visit a While loop node and update depth.
        
        Args:
            node (ast.While): The while loop node to visit
        """
        # While loops have same complexity implications as for loops
        self.visit_For(node)

def estimate_complexity(tree):
    """
    Estimate Big O complexity of code based on loop nesting.
    
    Simplified complexity analysis:
    - O(1): No loops
    - O(n): Single loop
    - O(n²): Nested loops (2 levels)
    - O(n^k): k levels of nested loops
    
    Note: This is a simplified heuristic. Real complexity analysis requires
    understanding the algorithm, not just loop structure.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to analyze
        
    Returns:
        str: Estimated Big O complexity notation (e.g., "O(n)", "O(n^2)")
    """
    analyzer = LoopDepthAnalyzer()
    analyzer.visit(tree)

    if analyzer.max_depth == 0:
        return "O(1)"
    elif analyzer.max_depth == 1:
        return "O(n)"
    else:
        return f"O(n^{analyzer.max_depth})"
