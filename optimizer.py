# optimizer.py
"""
Code optimization module.

Applies a series of optimization rules to improve code efficiency.
"""

from rules.constant_folding import ConstantFolder
from rules.dead_code import DeadCodeRemover
from rules.unused_imports import UnusedImportRemover
from rules.unused_functions import UnusedFunctionRemover, collect_called_functions
from rules.loop_optimization import optimize_loops
from rules.conditional_optimization import optimize_conditionals
from rules.recursion_optimization import optimize_recursion
from rules.remove_unused_apis import optimize_remove_unused_apis

from analyzer import collect_used_names

def optimize(tree, remove_unused=False):
    """
    Apply all optimization rules to an AST.
    
    Optimization pipeline:
    1. Constant Folding: Pre-compute constant expressions
    2. Dead Code Removal: Remove unreachable code
    3. Conditional Optimization: Simplify if/else statements
    4. Loop Optimization: Optimize for/while loops
    5. Recursion Optimization: Convert recursion to iteration where beneficial
    6. Unused Import Removal: Remove imported but unused modules
    7. Unused Function Removal: Remove functions that are never called
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to optimize
        remove_unused (bool): Whether to remove unused functions/APIs (default False for web uploads)
        
    Returns:
        ast.AST: Optimized Abstract Syntax Tree
    """
    # Collect metadata needed for optimization
    used_names = collect_used_names(tree)

    # Apply optimization rules in order
    tree = ConstantFolder().visit(tree)
    tree = DeadCodeRemover().visit(tree)
    tree = optimize_conditionals(tree)  # Optimize conditionals
    tree = optimize_loops(tree)  # Optimize loops
    tree = optimize_recursion(tree)  # Convert simple tail-recursion to iteration + add memoization
    tree = optimize_remove_unused_apis(tree, project_root='.')  # Remove unused APIs project-wide (conservative)
    
    # Re-collect used names AFTER recursion optimization (which may add functools references)
    used_names = collect_used_names(tree)
    tree = UnusedImportRemover(used_names).visit(tree)

    # Apply function-level optimizations only if requested
    # (For web uploads with no top-level calls, we want to keep all functions)
    if remove_unused:
        called_functions = collect_called_functions(tree)
        tree = UnusedFunctionRemover(called_functions).visit(tree)

    return tree

