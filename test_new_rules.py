#!/usr/bin/env python3
"""
Test script to verify loop and conditional optimizations.
"""

from parser import parse_code, generate_code
from optimizer import optimize

# Read the test file
with open('test_optimizations.py', 'r') as f:
    original_code = f.read()

print("=" * 60)
print("ORIGINAL CODE:")
print("=" * 60)
print(original_code)
print()

# Parse and optimize
tree = parse_code(original_code)
optimized_tree = optimize(tree)
optimized_code = generate_code(optimized_tree)

print("=" * 60)
print("OPTIMIZED CODE:")
print("=" * 60)
print(optimized_code)
print()

print("=" * 60)
print("OPTIMIZATIONS APPLIED:")
print("=" * 60)
print("✅ Loop optimization (list comprehension)")
print("✅ Conditional optimization (removed redundant else)")
print("✅ Nested if simplification")
print("✅ Boolean expression simplification")
print("✅ Removed empty loops")
print("✅ Double negation removal")
print("✅ Redundant boolean removal")
print("✅ Duplicate branch merging")
