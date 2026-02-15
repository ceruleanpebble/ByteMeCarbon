"""
Performance comparison: Recursive vs Optimized Fibonacci
This demonstrates the dramatic performance improvement from O(2^n) to O(n)
"""

import ast
import time
from optimizer import optimize

# Original recursive Fibonacci
recursive_code = '''
def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

result = fib_recursive(10)
'''

# Optimize it
tree = ast.parse(recursive_code)
optimized_tree = optimize(tree)
optimized_code = ast.unparse(optimized_tree)

print("ORIGINAL RECURSIVE CODE (O(2^n)):")
print(recursive_code)
print("\nOPTIMIZED ITERATIVE CODE (O(n)):")
print(optimized_code)
print("\n" + "="*60)
print("PERFORMANCE COMPARISON:")
print("="*60)

# Test with n=30
n = 30

# Time original (WARNING: This is slow!)
print(f"\nCalculating fib({n}) with ORIGINAL recursive version...")
exec(recursive_code)
start = time.time()
result1 = eval(f'fib_recursive({n})')
time1 = time.time() - start
print(f"Result: {result1}")
print(f"Time: {time1:.4f} seconds")

# Time optimized
print(f"\nCalculating fib({n}) with OPTIMIZED iterative version...")
exec(optimized_code)
start = time.time()
result2 = eval(f'fib_recursive({n})')
time2 = time.time() - start
print(f"Result: {result2}")
print(f"Time: {time2:.6f} seconds")

# Show improvement
print("\n" + "="*60)
print(f"SPEEDUP: {time1/time2:.0f}x faster!")
print(f"Time complexity reduced from O(2^n) to O(n)")
print("="*60)
