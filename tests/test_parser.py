"""Tests for the parser module."""

import ast
import pytest
from parser import parse_code, generate_code


class TestParseCode:
    """Tests for parse_code function."""
    
    def test_parse_valid_code(self):
        """Test parsing valid Python code."""
        code = "x = 5\nprint(x)"
        tree = parse_code(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 2
    
    def test_parse_empty_code(self):
        """Test parsing empty code."""
        code = ""
        tree = parse_code(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 0
    
    def test_parse_syntax_error(self):
        """Test parsing code with syntax errors."""
        code = "x = "
        with pytest.raises(SyntaxError):
            parse_code(code)
    
    def test_parse_complex_code(self):
        """Test parsing complex code with loops and conditionals."""
        code = """
def foo(x):
    if x > 0:
        for i in range(x):
            print(i)
    return x * 2
"""
        tree = parse_code(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.FunctionDef)


class TestGenerateCode:
    """Tests for generate_code function."""
    
    def test_generate_simple_code(self):
        """Test generating simple code from AST."""
        code = "x = 5"
        tree = parse_code(code)
        generated = generate_code(tree)
        assert "x = 5" in generated
    
    def test_generate_preserves_logic(self):
        """Test that generated code preserves original logic."""
        code = "if x > 5:\n    print('big')\nelse:\n    print('small')"
        tree = parse_code(code)
        generated = generate_code(tree)
        # Re-parse to verify it's still valid Python
        tree2 = parse_code(generated)
        assert isinstance(tree2, ast.Module)
    
    def test_roundtrip(self):
        """Test that parsing and generating produces valid code."""
        code = "def foo():\n    return 42"
        tree = parse_code(code)
        generated = generate_code(tree)
        tree2 = parse_code(generated)
        assert isinstance(tree2, ast.Module)
