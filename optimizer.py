# optimizer.py
from rules.constant_folding import ConstantFolder
from rules.dead_code import DeadCodeRemover
from rules.unused_imports import UnusedImportRemover
from rules.unused_functions import UnusedFunctionRemover, collect_called_functions

from analyzer import collect_used_names

def optimize(tree):
    used_names = collect_used_names(tree)

    # Existing rules
    tree = ConstantFolder().visit(tree)
    tree = DeadCodeRemover().visit(tree)
    tree = UnusedImportRemover(used_names).visit(tree)

    # --- New logic ---
    called_functions = collect_called_functions(tree)
    tree = UnusedFunctionRemover(called_functions).visit(tree)

    return tree

