# parser.py
"""
Code parsing and generation module.

Handles conversion between source code strings and Abstract Syntax Trees (AST).
"""

import ast

def parse_code(source_code: str) -> ast.AST:
    """
    Parse Python source code into an Abstract Syntax Tree.
    
    Args:
        source_code (str): Python source code as a string
        
    Returns:
        ast.AST: Abstract Syntax Tree representation of the code
        
    Raises:
        SyntaxError: If the source code contains syntax errors
    """
    return ast.parse(source_code)

def generate_code(tree: ast.AST) -> str:
    """
    Generate Python source code from an Abstract Syntax Tree.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to convert
        
    Returns:
        str: Python source code as a string
    """
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
