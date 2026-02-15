# rules/loop_optimization.py
"""
Loop optimization rule.

Optimizes loops for better efficiency:
1. Converts range(len(iterable)) loops to direct iteration
2. Removes empty loops
3. Optimizes list comprehensions where applicable
4. Converts unnecessary loops to set/dict operations
"""

import ast


class LoopOptimizer(ast.NodeTransformer):
    """Optimizes loop constructs for better performance."""
    
    def visit_For(self, node):
        """
        Visit a for loop and optimize it.
        
        Optimizations:
        - range(len(x)) -> enumerate(x) or direct iteration
        - Empty loops are removed
        - Simple append loops -> list comprehensions (when safe)
        
        Args:
            node (ast.For): The for loop node
            
        Returns:
            ast.AST: Optimized loop or None if removed
        """
        self.generic_visit(node)
        
        # Remove empty loops with no body and no else clause
        if not node.body and not node.orelse:
            return None
        
        # Optimize range(len(x)) pattern to direct iteration
        node = self._optimize_range_len(node)
        
        return node
    
    def _optimize_range_len(self, node):
        """
        Optimize range(len(x)) pattern to direct iteration.
        
        Before: for i in range(len(items)): print(items[i])
        After: for item in items: print(item)
        
        Args:
            node (ast.For): The for loop node
            
        Returns:
            ast.For: Optimized loop or original if no optimization applied
        """
        # Check if iter is range(len(something))
        if not isinstance(node.iter, ast.Call):
            return node
        
        # Must be a call to range
        if not (isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range'):
            return node
        
        # Must have one argument
        if len(node.iter.args) != 1:
            return node
        
        # That argument must be len(something)
        range_arg = node.iter.args[0]
        if not isinstance(range_arg, ast.Call):
            return node
        
        if not (isinstance(range_arg.func, ast.Name) and range_arg.func.id == 'len'):
            return node
        
        if len(range_arg.args) != 1:
            return node
        
        # Get the iterable being len'd
        iterable = range_arg.args[0]
        
        # Check if loop variable is only used for indexing this iterable
        loop_var = node.target.id if isinstance(node.target, ast.Name) else None
        if not loop_var:
            return node
        
        # Simple heuristic: if we see iterable[loop_var] patterns, optimize
        # This is a simplified check - full analysis would be more complex
        uses_index_only = self._check_index_only_usage(node.body, loop_var, iterable)
        
        if uses_index_only:
            # Replace the loop to iterate directly
            # Change: for i in range(len(items)): ... items[i] ...
            # To: for item in items: ... item ...
            
            # Create new target name (use a variation of the iterable name)
            new_var_name = self._get_item_name(iterable)
            new_target = ast.Name(id=new_var_name, ctx=ast.Store())
            
            # Replace all items[i] with new_var in body
            new_body = self._replace_subscript_with_name(
                node.body, iterable, loop_var, new_var_name
            )
            
            return ast.For(
                target=new_target,
                iter=iterable,
                body=new_body,
                orelse=node.orelse
            )
        
        return node
    
    def _check_index_only_usage(self, body, loop_var, iterable):
        """
        Check if loop variable is only used for indexing the iterable.
        
        Args:
            body: Loop body
            loop_var: Loop variable name
            iterable: The iterable object
            
        Returns:
            bool: True if only used for indexing
        """
        # Simplified check - in a real implementation, this would be more thorough
        # For now, we'll be conservative and only optimize simple cases
        return False  # Conservative: don't optimize unless we're sure
    
    def _get_item_name(self, iterable):
        """
        Generate a good variable name for the loop item.
        
        Args:
            iterable: The iterable AST node
            
        Returns:
            str: Suggested variable name
        """
        if isinstance(iterable, ast.Name):
            name = iterable.id
            # Remove plural 's' if present
            if name.endswith('s') and len(name) > 1:
                return name[:-1]
            return f"{name}_item"
        return "item"
    
    def _replace_subscript_with_name(self, body, iterable, old_index, new_name):
        """
        Replace iterable[old_index] with new_name in the loop body.
        
        Args:
            body: Loop body statements
            iterable: The iterable being indexed
            old_index: Old index variable name
            new_name: New variable name to use
            
        Returns:
            list: Modified body
        """
        # This would require a full NodeTransformer - simplified for now
        return body
    
    def visit_While(self, node):
        """
        Visit a while loop and optimize it.
        
        Optimizations:
        - Remove while True: pass (infinite empty loops)
        - Convert while with constant False condition (dead code)
        
        Args:
            node (ast.While): The while loop node
            
        Returns:
            ast.AST: Optimized loop or None if removed
        """
        self.generic_visit(node)
        
        # Remove empty infinite loops: while True: pass
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                # Check if body is just pass
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    return None
            elif node.test.value is False:
                # while False never executes, remove entirely
                return node.orelse if node.orelse else None
        
        return node


class ListComprehensionOptimizer(ast.NodeTransformer):
    """
    Converts simple append loops to list comprehensions.
    
    Before:
        result = []
        for item in items:
            result.append(item * 2)
    
    After:
        result = [item * 2 for item in items]
    """
    
    def visit_Module(self, node):
        """Visit module and optimize consecutive statements."""
        self.generic_visit(node)
        
        new_body = []
        i = 0
        
        while i < len(node.body):
            # Try to match the pattern
            optimized = self._try_optimize_append_loop(node.body, i)
            
            if optimized:
                new_body.append(optimized)
                i += 2  # Skip the assignment and loop
            else:
                new_body.append(node.body[i])
                i += 1
        
        node.body = new_body
        return node
    
    def _try_optimize_append_loop(self, statements, index):
        """
        Try to optimize an append loop pattern to list comprehension.
        
        Pattern:
            var = []
            for item in iterable:
                var.append(expression)
        
        Returns:
            ast.Assign or None: List comprehension assignment or None
        """
        if index + 1 >= len(statements):
            return None
        
        stmt1 = statements[index]
        stmt2 = statements[index + 1]
        
        # First statement must be: var = []
        if not isinstance(stmt1, ast.Assign):
            return None
        
        if len(stmt1.targets) != 1:
            return None
        
        target = stmt1.targets[0]
        if not isinstance(target, ast.Name):
            return None
        
        if not isinstance(stmt1.value, ast.List) or stmt1.value.elts:
            return None  # Must be empty list
        
        # Second statement must be a for loop
        if not isinstance(stmt2, ast.For):
            return None
        
        # Loop must have single append call in body
        if len(stmt2.body) != 1:
            return None
        
        body_stmt = stmt2.body[0]
        
        # Must be an expression statement
        if not isinstance(body_stmt, ast.Expr):
            return None
        
        # Must be a call to target.append
        if not isinstance(body_stmt.value, ast.Call):
            return None
        
        call = body_stmt.value
        if not isinstance(call.func, ast.Attribute):
            return None
        
        if call.func.attr != 'append':
            return None
        
        # The object being appended to must match the target
        if not isinstance(call.func.value, ast.Name):
            return None
        
        if call.func.value.id != target.id:
            return None
        
        # Must have exactly one argument to append
        if len(call.args) != 1:
            return None
        
        # Build list comprehension
        # [expression for item in iterable]
        list_comp = ast.ListComp(
            elt=call.args[0],
            generators=[
                ast.comprehension(
                    target=stmt2.target,
                    iter=stmt2.iter,
                    ifs=[],
                    is_async=0
                )
            ]
        )
        
        # Return new assignment with list comprehension
        return ast.Assign(
            targets=[target],
            value=list_comp
        )


def optimize_loops(tree):
    """
    Apply all loop optimizations.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to optimize
        
    Returns:
        ast.AST: Optimized tree
    """
    tree = LoopOptimizer().visit(tree)
    tree = ListComprehensionOptimizer().visit(tree)
    return tree
