# analyzer.py
"""
Code analysis module.

Analyzes Python AST to collect used names and identify references.
"""

import ast

class NameCollector(ast.NodeVisitor):
    """Visitor that collects all referenced names in code."""
    
    def __init__(self):
        """Initialize the name collector."""
        self.names = set()

    def visit_Name(self, node):
        """
        Visit a Name node and add it to the set of names.
        
        Args:
            node (ast.Name): The name node to visit
        """
        self.names.add(node.id)
        self.generic_visit(node)

def collect_used_names(tree):
    """
    Collect all names referenced in an AST.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to analyze
        
    Returns:
        set: Set of all referenced name identifiers
    """
    collector = NameCollector()
    collector.visit(tree)
    return collector.names
