"""Tests for optimization rules."""

import ast
import pytest
from parser import parse_code, generate_code
from rules.constant_folding import ConstantFolder
from rules.dead_code import DeadCodeRemover
from rules.unused_imports import UnusedImportRemover
from rules.unused_functions import UnusedFunctionRemover, collect_called_functions


class TestConstantFolding:
    """Tests for ConstantFolder rule."""
    
    def test_fold_addition(self):
        """Test folding addition expressions."""
        code = "x = 2 + 3"
        tree = parse_code(code)
        folder = ConstantFolder()
        optimized = folder.visit(tree)
        # Verify the constant is folded
        assert isinstance(optimized.body[0].value, ast.Constant)
        assert optimized.body[0].value.value == 5
    
    def test_fold_multiplication(self):
        """Test folding multiplication."""
        code = "x = 4 * 5"
        tree = parse_code(code)
        folder = ConstantFolder()
        optimized = folder.visit(tree)
        assert optimized.body[0].value.value == 20
    
    def test_no_fold_variables(self):
        """Test that constants with variables are not folded."""
        code = "x = y + 3"
        tree = parse_code(code)
        folder = ConstantFolder()
        optimized = folder.visit(tree)
        # Should still be a BinOp, not a Constant
        assert isinstance(optimized.body[0].value, ast.BinOp)


class TestDeadCodeRemover:
    """Tests for DeadCodeRemover rule."""
    
    def test_remove_false_branch(self):
        """Test removing else branch when condition is False."""
        code = "if False:\n    x = 1\nelse:\n    x = 2"
        tree = parse_code(code)
        remover = DeadCodeRemover()
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        assert "else" not in generated
    
    def test_remove_true_branch(self):
        """Test keeping if branch when condition is True."""
        code = "if True:\n    x = 1\nelse:\n    x = 2"
        tree = parse_code(code)
        remover = DeadCodeRemover()
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        # Should have x = 1 but no else
        assert "x = 1" in generated
        assert "else" not in generated
    
    def test_keep_variable_conditions(self):
        """Test that variable conditions are preserved."""
        code = "if x > 5:\n    pass"
        tree = parse_code(code)
        remover = DeadCodeRemover()
        optimized = remover.visit(tree)
        # Should keep the whole if statement
        generated = generate_code(optimized)
        assert "if" in generated


class TestUnusedImportRemover:
    """Tests for UnusedImportRemover rule."""
    
    def test_remove_unused_simple_import(self):
        """Test removing unused import."""
        code = "import os\nx = 5"
        tree = parse_code(code)
        remover = UnusedImportRemover({'x', '5'})
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        assert "import os" not in generated
    
    def test_keep_used_import(self):
        """Test keeping used imports."""
        code = "import os\npath = os.path.exists('.')"
        tree = parse_code(code)
        remover = UnusedImportRemover({'os', 'path'})
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        assert "import os" in generated


class TestUnusedFunctionRemover:
    """Tests for UnusedFunctionRemover rule."""
    
    def test_remove_unused_function(self):
        """Test removing unused function definitions."""
        code = """
def unused():
    return 5

x = 10
"""
        tree = parse_code(code)
        called = collect_called_functions(tree)
        assert "unused" not in called
        remover = UnusedFunctionRemover(called)
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        assert "def unused" not in generated
    
    def test_keep_used_function(self):
        """Test keeping used function definitions."""
        code = """
def used():
    return 5

x = used()
"""
        tree = parse_code(code)
        called = collect_called_functions(tree)
        assert "used" in called
        remover = UnusedFunctionRemover(called)
        optimized = remover.visit(tree)
        generated = generate_code(optimized)
        assert "def used" in generated
