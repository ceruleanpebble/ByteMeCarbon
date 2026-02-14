# optimizer.py
"""
Code optimization module.

Applies a series of optimization rules to improve code efficiency.
"""

from rules.constant_folding import ConstantFolder
from rules.dead_code import DeadCodeRemover
from rules.unused_imports import UnusedImportRemover
from rules.unused_functions import UnusedFunctionRemover, collect_called_functions

from analyzer import collect_used_names

def optimize(tree):
    """
    Apply all optimization rules to an AST.
    
    Optimization pipeline:
    1. Constant Folding: Pre-compute constant expressions
    2. Dead Code Removal: Remove unreachable code
    3. Unused Import Removal: Remove imported but unused modules
    4. Unused Function Removal: Remove functions that are never called
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to optimize
        
    Returns:
        ast.AST: Optimized Abstract Syntax Tree
    """
    # Collect metadata needed for optimization
    used_names = collect_used_names(tree)

    # Apply optimization rules in order
    tree = ConstantFolder().visit(tree)
    tree = DeadCodeRemover().visit(tree)
    tree = UnusedImportRemover(used_names).visit(tree)

    # Apply function-level optimizations
    called_functions = collect_called_functions(tree)
    tree = UnusedFunctionRemover(called_functions).visit(tree)

    return tree

