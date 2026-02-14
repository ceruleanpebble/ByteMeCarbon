# rules/unused_functions.py
"""
Unused function removal optimization rule.

Removes function definitions that are never called.
"""

import ast


class UnusedFunctionRemover(ast.NodeTransformer):
    """Removes function definitions that are never called."""
    
    def __init__(self, called_functions):
        """
        Initialize the remover with a set of called functions.
        
        Args:
            called_functions (set): Set of all function names that are called
        """
        self.called_functions = called_functions

    def visit_FunctionDef(self, node):
        """
        Visit a function definition and remove if never called.
        
        Args:
            node (ast.FunctionDef): The function definition node
            
        Returns:
            ast.FunctionDef: The function if it's called, None otherwise
        """
        # Keep function if it is called
        if node.name in self.called_functions:
            return node

        # Otherwise remove it
        return None


class FunctionCallCollector(ast.NodeVisitor):
    """Collects all function names that are called in the code."""
    
    def __init__(self):
        """Initialize the collector."""
        self.called = set()

    def visit_Call(self, node):
        """
        Visit a function call and record the function name.
        
        Args:
            node (ast.Call): The call node to visit
        """
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        self.generic_visit(node)


def collect_called_functions(tree):
    """
    Collect all function names that are called in an AST.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to analyze
        
    Returns:
        set: Set of all called function names
    """
    collector = FunctionCallCollector()
    collector.visit(tree)
    return collector.called
