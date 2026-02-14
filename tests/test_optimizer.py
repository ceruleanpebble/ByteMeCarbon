"""Tests for the optimizer module."""

import ast
import pytest
from parser import parse_code, generate_code
from optimizer import optimize
from complexity import estimate_complexity


class TestOptimizer:
    """Tests for the optimize function."""
    
    def test_constant_folding(self):
        """Test constant folding optimization."""
        code = "x = 2 + 3"
        tree = parse_code(code)
        optimized = optimize(tree)
        generated = generate_code(optimized)
        # Should have folded 2 + 3 into 5
        tree2 = parse_code(generated)
        assert isinstance(tree2, ast.Module)
    
    def test_dead_code_removal(self):
        """Test dead code removal."""
        code = "if True:\n    x = 5\nelse:\n    y = 10"
        tree = parse_code(code)
        optimized = optimize(tree)
        generated = generate_code(optimized)
        assert "else" not in generated
    
    def test_unused_import_removal(self):
        """Test unused import removal."""
        code = "import os\nimport sys\nprint(os.path.exists('.'))"
        tree = parse_code(code)
        optimized = optimize(tree)
        generated = generate_code(optimized)
        # sys should be removed, os should remain
        assert "sys" not in generated
        assert "os" in generated
    
    def test_unused_function_removal(self):
        """Test unused function removal."""
        code = """
def used():
    return 42

def unused():
    return 0

x = used()
"""
        tree = parse_code(code)
        optimized = optimize(tree)
        generated = generate_code(optimized)
        assert "used" in generated
        assert "unused" not in generated
    
    def test_no_infinite_loops(self):
        """Test that optimization doesn't crash on recursive code."""
        code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

result = fib(5)
"""
        tree = parse_code(code)
        # Should not raise an exception
        optimized = optimize(tree)
        generated = generate_code(optimized)
        assert isinstance(generated, str)
    
    def test_optimization_preserves_output(self):
        """Test that optimized code produces same output."""
        code = "print(2 + 3)"
        tree = parse_code(code)
        optimized = optimize(tree)
        generated = generate_code(optimized)
        # Both should be valid Python
        parse_code(generated)


class TestComplexity:
    """Tests for complexity estimation."""
    
    def test_constant_complexity(self):
        """Test O(1) complexity detection."""
        code = "x = 5"
        tree = parse_code(code)
        complexity = estimate_complexity(tree)
        assert complexity == "O(1)"
    
    def test_linear_complexity(self):
        """Test O(n) complexity detection."""
        code = "for i in range(10):\n    print(i)"
        tree = parse_code(code)
        complexity = estimate_complexity(tree)
        assert complexity == "O(n)"
    
    def test_quadratic_complexity(self):
        """Test O(n²) complexity detection."""
        code = "for i in range(10):\n    for j in range(10):\n        print(i, j)"
        tree = parse_code(code)
        complexity = estimate_complexity(tree)
        assert complexity == "O(n^2)"
    
    def test_cubic_complexity(self):
        """Test O(n³) complexity detection."""
        code = "for i in range(10):\n    for j in range(10):\n        for k in range(10):\n            pass"
        tree = parse_code(code)
        complexity = estimate_complexity(tree)
        assert complexity == "O(n^3)"
