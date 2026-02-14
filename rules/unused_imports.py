# rules/unused_imports.py
"""
Unused import removal optimization rule.

Removes import statements for modules that are never referenced in the code.
"""

import ast

class UnusedImportRemover(ast.NodeTransformer):
    """Removes unused import statements."""
    
    def __init__(self, used_names):
        """
        Initialize the remover with a set of used names.
        
        Args:
            used_names (set): Set of all names referenced in the code
        """
        self.used_names = used_names

    def visit_Import(self, node):
        """
        Visit an import statement and remove unused imports.
        
        Args:
            node (ast.Import): The import statement node
            
        Returns:
            ast.Import: Import with only used modules, or None if all removed
        """
        new_names = [alias for alias in node.names 
                     if alias.asname in self.used_names or alias.name in self.used_names]
        if new_names:
            node.names = new_names
            return node
        return None

    def visit_ImportFrom(self, node):
        """
        Visit a from...import statement and remove unused imports.
        
        Args:
            node (ast.ImportFrom): The from...import statement node
            
        Returns:
            ast.ImportFrom: Import with only used names, or None if all removed
        """
        new_names = [alias for alias in node.names 
                     if alias.asname in self.used_names or alias.name in self.used_names]
        if new_names:
            node.names = new_names
            return node
        return None
