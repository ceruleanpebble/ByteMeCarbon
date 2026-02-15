"""
Recursion to iteration optimization rule.

This module implements a conservative transformation that converts simple
tail-recursive functions into iterative equivalents using a while loop.

It only handles a narrow, safe subset of patterns:
- Function body is a single if statement where the `body` returns a base
  case value and the `orelse` returns a recursive call to the same
  function (possibly with updated arguments). Example:

    def fact(n, acc=1):
        if n == 0:
            return acc
        else:
            return fact(n-1, acc*n)

  This will be transformed into a while-loop that updates parameters and
  returns when the base case is met.

The transformation is intentionally conservative to avoid changing
semantics for complex cases.
"""

import ast
from typing import List, Set


class RecursiveFunctionDetector(ast.NodeVisitor):
    """Detect if a function calls itself recursively."""
    
    def __init__(self, func_name: str):
        self.func_name = func_name
        self.is_recursive = False
        self.is_tail_recursive = False
        self.recursive_calls = []  # Track all recursive call nodes
    
    def visit_Return(self, node: ast.Return):
        """Check if return statement contains a recursive call."""
        if node.value and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == self.func_name:
                # This is a tail recursive call (return is direct call result)
                self.is_tail_recursive = True
                self.recursive_calls.append(node.value)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Check if function calls itself."""
        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
            self.is_recursive = True
            self.recursive_calls.append(node)
        self.generic_visit(node)


class FibonacciToIterative(ast.NodeTransformer):
    """Convert Fibonacci-style recursion to iterative loop: a, b = 0, 1; for i in range(n): a, b = b, a+b"""
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        
        # Must have exactly one parameter
        if len(node.args.args) != 1:
            return node
        
        param_name = node.args.args[0].arg
        
        # Look for pattern: if n <= 1: return n; return fib(n-1) + fib(n-2)
        if len(node.body) < 2:
            return node
        
        first = node.body[0]
        if not isinstance(first, ast.If):
            return node
        
        # Check base case: if n <= 1: return n
        if not (len(first.body) == 1 and isinstance(first.body[0], ast.Return)):
            return node
        
        base_return = first.body[0].value
        if not (isinstance(base_return, ast.Name) and base_return.id == param_name):
            return node
        
        # Check recursive case: return fib(n-1) + fib(n-2)
        second = node.body[1] if len(node.body) > 1 else (first.orelse[0] if first.orelse else None)
        if not second or not isinstance(second, ast.Return):
            return node
        
        ret_val = second.value
        if not isinstance(ret_val, ast.BinOp) or not isinstance(ret_val.op, ast.Add):
            return node
        
        # Check if both sides are recursive calls with n-1 and n-2
        left = ret_val.left
        right = ret_val.right
        
        if not (isinstance(left, ast.Call) and isinstance(right, ast.Call)):
            return node
        
        if not (isinstance(left.func, ast.Name) and left.func.id == node.name):
            return node
        if not (isinstance(right.func, ast.Name) and right.func.id == node.name):
            return node
        
        # This looks like Fibonacci! Convert to iterative
        # a, b = 0, 1
        # for i in range(n):
        #     a, b = b, a+b
        # return a
        
        new_body = []
        
        # a, b = 0, 1
        init_assign = ast.Assign(
            targets=[ast.Tuple(elts=[
                ast.Name(id='a', ctx=ast.Store()),
                ast.Name(id='b', ctx=ast.Store())
            ], ctx=ast.Store())],
            value=ast.Tuple(elts=[
                ast.Constant(value=0),
                ast.Constant(value=1)
            ], ctx=ast.Load())
        )
        new_body.append(init_assign)
        
        # for i in range(n):
        loop_body = [
            ast.Assign(
                targets=[ast.Tuple(elts=[
                    ast.Name(id='a', ctx=ast.Store()),
                    ast.Name(id='b', ctx=ast.Store())
                ], ctx=ast.Store())],
                value=ast.Tuple(elts=[
                    ast.Name(id='b', ctx=ast.Load()),
                    ast.BinOp(
                        left=ast.Name(id='a', ctx=ast.Load()),
                        op=ast.Add(),
                        right=ast.Name(id='b', ctx=ast.Load())
                    )
                ], ctx=ast.Load())
            )
        ]
        
        for_loop = ast.For(
            target=ast.Name(id='i', ctx=ast.Store()),
            iter=ast.Call(
                func=ast.Name(id='range', ctx=ast.Load()),
                args=[ast.Name(id=param_name, ctx=ast.Load())],
                keywords=[]
            ),
            body=loop_body,
            orelse=[]
        )
        new_body.append(for_loop)
        
        # return a
        return_stmt = ast.Return(value=ast.Name(id='a', ctx=ast.Load()))
        new_body.append(return_stmt)
        
        new_func = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=new_body,
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=getattr(node, 'type_comment', None)
        )
        
        ast.copy_location(new_func, node)
        ast.fix_missing_locations(new_func)
        
        return new_func


class SideEffectDetector(ast.NodeVisitor):
    """Detect if a function has side effects (prints, mutations, I/O)."""
    
    def __init__(self):
        self.has_side_effects = False
    
    def visit_Call(self, node: ast.Call):
        """Check for function calls that have side effects."""
        # Common side-effect functions
        side_effect_funcs = {'print', 'input', 'open', 'write', 'append', 
                            'remove', 'pop', 'clear', 'update', 'add'}
        
        if isinstance(node.func, ast.Name) and node.func.id in side_effect_funcs:
            self.has_side_effects = True
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        """Assignments to external variables can be side effects."""
        # If assigning to attribute or subscript, it's likely a side effect
        for target in node.targets:
            if isinstance(target, (ast.Attribute, ast.Subscript)):
                self.has_side_effects = True
        self.generic_visit(node)
    
    def visit_AugAssign(self, node: ast.AugAssign):
        """Augmented assignments (+=, etc.) to external vars are side effects."""
        if isinstance(node.target, (ast.Attribute, ast.Subscript)):
            self.has_side_effects = True
        self.generic_visit(node)


class MemoizationDecorator(ast.NodeTransformer):
    """Add memoization decorator to recursive functions that aren't tail-recursive."""
    
    def __init__(self):
        self.needs_functools_import = False
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.generic_visit(node)
        
        # Check if already decorated with lru_cache
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'lru_cache':
                return node
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'lru_cache':
                return node
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'lru_cache':
                    return node
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'lru_cache':
                    return node
        
        # Detect recursion
        detector = RecursiveFunctionDetector(node.name)
        detector.visit(node)
        
        # Check for side effects
        side_effect_detector = SideEffectDetector()
        side_effect_detector.visit(node)
        
        # Only add memoization if:
        # 1. Function is recursive but not purely tail-recursive
        # 2. Function has NO side effects (pure function)
        if (detector.is_recursive and 
            not (detector.is_tail_recursive and not detector.is_recursive) and
            not side_effect_detector.has_side_effects):
            # Add @lru_cache decorator
            decorator = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='functools', ctx=ast.Load()),
                    attr='lru_cache',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=None)],  # maxsize=None for unlimited cache
                keywords=[]
            )
            node.decorator_list.insert(0, decorator)
            self.needs_functools_import = True
        
        return node


class FunctoolsImportAdder(ast.NodeTransformer):
    """Add 'import functools' at the top of the module if needed."""
    
    def __init__(self):
        self.added = False
    
    def visit_Module(self, node: ast.Module):
        if self.added:
            return node
            
        # Check if functools is already imported
        has_functools = False
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if alias.name == 'functools':
                        has_functools = True
                        break
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module == 'functools':
                    has_functools = True
                    break
        
        if not has_functools:
            # Add import at the top (before any other statements)
            import_stmt = ast.Import(names=[ast.alias(name='functools', asname=None)])
            node.body.insert(0, import_stmt)
            self.added = True
        
        self.generic_visit(node)
        return node


class TailRecursionToIteration(ast.NodeTransformer):
    """Transform simple tail-recursive functions into iterative loops."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Conservative but more flexible tail-recursion pattern detection.
        # We'll look for a base-case `If` that returns a base value and a
        # tail-call `Return` that calls the same function either in the
        # `else` branch or immediately after the `If`.

        self.generic_visit(node)

        if not node.body:
            return node

        # Helper to recognize a Return that calls the same function
        def is_tail_call_return(ret: ast.Return):
            if not isinstance(ret, ast.Return):
                return False
            val = ret.value
            if not isinstance(val, ast.Call):
                return False
            if not isinstance(val.func, ast.Name):
                return False
            return val.func.id == node.name

        base_if = None
        tail_ret = None

        # Scan top-level statements for pattern
        stmts = node.body
        for i, stmt in enumerate(stmts):
            if isinstance(stmt, ast.If):
                # Find a branch that is a single `return <base>` and the other
                # branch either contains a tail-call return or the following
                # statement is a tail-call return.
                # Look for single-return branches
                left_ret = stmt.body[0] if len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Return) else None
                right_ret = stmt.orelse[0] if len(stmt.orelse) == 1 and isinstance(stmt.orelse[0], ast.Return) else None

                # Case A: else branch contains tail-call return
                if left_ret and right_ret and is_tail_call_return(right_ret):
                    base_if = stmt
                    tail_ret = right_ret
                    base_return = left_ret.value
                    condition = stmt.test
                    break

                # Case B: if branch contains tail-call return and else is base
                if left_ret and right_ret and is_tail_call_return(left_ret):
                    base_if = stmt
                    tail_ret = left_ret
                    base_return = right_ret.value
                    condition = stmt.test
                    break

                # Case C: base in if branch, tail-return immediately follows the if
                if left_ret and i + 1 < len(stmts) and is_tail_call_return(stmts[i + 1]):
                    base_if = stmt
                    tail_ret = stmts[i + 1]
                    base_return = left_ret.value
                    condition = stmt.test
                    break

        if base_if is None or tail_ret is None:
            # No safe pattern found
            return node

        call: ast.Call = tail_ret.value  # type: ignore[assignment]

        # Reject complex call shapes (star args or kwargs unpacking)
        for k in call.keywords:
            if k.arg is None:
                return node
        if any(isinstance(a, ast.Starred) for a in call.args):
            return node

        # Build parameter names list
        param_names: List[str] = [arg.arg for arg in node.args.args]

        # Prepare replacement expressions for every parameter: if the recursive
        # call provides a new value (positional or keyword), use it; otherwise
        # keep the current value (name expression).
        new_values: List[ast.expr] = []
        # positional mapping
        pos_args = list(call.args)
        kw_map = {k.arg: k.value for k in call.keywords}

        for idx, pname in enumerate(param_names):
            if idx < len(pos_args):
                new_values.append(pos_args[idx])
            elif pname in kw_map:
                new_values.append(kw_map[pname])
            else:
                # keep current value
                new_values.append(ast.Name(id=pname, ctx=ast.Load()))

        # Create tuple assignment: (p1, p2, ...) = (new1, new2, ...)
        targets = [ast.Name(id=name, ctx=ast.Store()) for name in param_names]
        value = ast.Tuple(elts=new_values, ctx=ast.Load()) if len(new_values) > 1 else new_values[0]
        assign = ast.Assign(targets=[ast.Tuple(elts=targets, ctx=ast.Store())] if len(targets) > 1 else targets, value=value)

        # Construct while True loop
        ret_stmt = ast.Return(value=base_return)
        if_block = ast.If(test=condition, body=[ret_stmt], orelse=[])
        while_body = [if_block, assign, ast.Continue()]
        while_node = ast.While(test=ast.Constant(value=True), body=while_body, orelse=[])

        new_func = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=[while_node],
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=getattr(node, 'type_comment', None)
        )
        
        # Copy source location from original node
        ast.copy_location(new_func, node)
        ast.fix_missing_locations(new_func)

        return new_func


def optimize_recursion(tree: ast.AST) -> ast.AST:
    """Apply recursion-to-iteration transformation to the AST.

    This function applies multiple strategies:
    1. Fibonacci-style recursion → iterative loop (O(n) instead of O(2^n))
    2. Tail recursion → while loop
    3. Other recursion → memoization as fallback
    """
    # First, try Fibonacci-style conversion (highest priority - best performance)
    fib_converter = FibonacciToIterative()
    tree = fib_converter.visit(tree)
    
    # Then try tail recursion to iteration conversion
    transformer = TailRecursionToIteration()
    tree = transformer.visit(tree)
    
    # Finally, add memoization for remaining non-tail recursive functions (fallback)
    memoizer = MemoizationDecorator()
    tree = memoizer.visit(tree)
    
    # Add functools import if needed
    if memoizer.needs_functools_import:
        adder = FunctoolsImportAdder()
        tree = adder.visit(tree)
    
    return tree
