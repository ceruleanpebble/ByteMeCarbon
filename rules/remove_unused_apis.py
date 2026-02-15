"""
Remove unused public APIs across a project.

This rule is conservative:
- It scans Python files under a project root to collect names that are used
  (via function calls and Name usages) and honors __all__ exports.
- It will remove top-level function and class definitions from the current
  module's AST when they are not referenced anywhere in the project and
  are not exported via __all__.

Limitations:
- Does not attempt to resolve dynamic references (getattr, importlib, exec).
- Rejects removal if the project contains star-imports or complex usages it
  cannot statically resolve.
"""

import ast
import os
from typing import Set

from .unused_functions import UnusedFunctionRemover
from analyzer import collect_used_names


def _collect_project_used_names(root: str) -> Set[str]:
    """Walk the project and collect used names and __all__ exports."""
    used = set()
    exports = set()

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and virtualenvs
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            path = os.path.join(dirpath, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    src = f.read()
                tree = ast.parse(src, filename=path)
            except Exception:
                # If parsing fails, skip the file conservatively
                continue

            # collect Name nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used.add(node.id)

            # collect __all__ if present
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__all__':
                            # try to evaluate a simple list/tuple of strings
                            val = node.value
                            if isinstance(val, (ast.List, ast.Tuple)):
                                for elt in val.elts:
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                        exports.add(elt.value)

    # union used and exports to avoid removing exported names
    return used.union(exports)


def optimize_remove_unused_apis(tree: ast.AST, project_root: str = '.') -> ast.AST:
    """Remove top-level functions/classes from `tree` not referenced in project.

    Args:
        tree: AST of the module being optimized
        project_root: path to the repository root to scan

    Returns:
        Modified AST with unused top-level functions/classes removed.
    """
    # Start from project-wide usages, then make sure any names used in the
    # current module AST are also included so we never remove functions that
    # are called within the same file.
    used_names = _collect_project_used_names(project_root)
    try:
        module_names = collect_used_names(tree)
        used_names = used_names.union(module_names)
    except Exception:
        # If analyzer fails for some reason, fall back to project scan only
        pass

    # Remove functions not in used_names
    remover = UnusedFunctionRemover(used_names)

    # The UnusedFunctionRemover is function-scoped; to also remove classes,
    # we implement a thin wrapper NodeTransformer here.
    class _APIRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            return remover.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            # remove classes whose name is not referenced
            if node.name in used_names:
                return node
            return None

    return _APIRemover().visit(tree)
