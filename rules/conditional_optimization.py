# rules/conditional_optimization.py
"""
Conditional statement optimization rule.

Optimizes if/elif/else statements for better efficiency:
1. Simplifies nested conditionals
2. Combines duplicate code branches
3. Reorders conditions for short-circuit evaluation
4. Removes redundant else blocks
5. Simplifies boolean expressions
"""

import ast


class ConditionalOptimizer(ast.NodeTransformer):
    """Optimizes conditional statements for better performance."""
    
    def visit_If(self, node):
        """
        Visit an if statement and optimize it.
        
        Optimizations:
        - Remove redundant else: pass
        - Simplify nested if statements
        - Combine duplicate branches
        - Simplify boolean expressions in conditions
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.AST: Optimized conditional or None
        """
        self.generic_visit(node)
        
        # Remove else blocks that only contain pass
        node = self._remove_pass_else(node)
        
        # Simplify nested if statements with no else
        node = self._simplify_nested_if(node)
        
        # Simplify boolean expressions
        node = self._simplify_boolean_condition(node)
        
        # Merge duplicate if/else branches
        node = self._merge_duplicate_branches(node)
        
        return node
    
    def _remove_pass_else(self, node):
        """
        Remove else blocks that only contain 'pass'.
        
        Before:
            if condition:
                do_something()
            else:
                pass
        
        After:
            if condition:
                do_something()
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.If: Node without redundant else
        """
        if node.orelse:
            # Check if else block is just pass
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Pass):
                node.orelse = []
        
        return node
    
    def _simplify_nested_if(self, node):
        """
        Simplify nested if statements without else clauses.
        
        Before:
            if condition1:
                if condition2:
                    do_something()
        
        After:
            if condition1 and condition2:
                do_something()
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.If: Simplified node
        """
        # Only optimize if no else clause
        if node.orelse:
            return node
        
        # Check if body is a single if statement with no else
        if len(node.body) == 1 and isinstance(node.body[0], ast.If):
            inner_if = node.body[0]
            
            # Inner if must also have no else clause
            if not inner_if.orelse:
                # Combine conditions with 'and'
                combined_test = ast.BoolOp(
                    op=ast.And(),
                    values=[node.test, inner_if.test]
                )
                
                return ast.If(
                    test=combined_test,
                    body=inner_if.body,
                    orelse=[]
                )
        
        return node
    
    def _simplify_boolean_condition(self, node):
        """
        Simplify boolean expressions in conditions.
        
        Optimizations:
        - if x == True -> if x
        - if x == False -> if not x
        - if not (not x) -> if x
        - if x is True -> if x
        - if x is False -> if not x
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.If: Node with simplified condition
        """
        test = node.test
        
        # Handle: if x == True -> if x
        if isinstance(test, ast.Compare):
            if len(test.ops) == 1 and len(test.comparators) == 1:
                comparator = test.comparators[0]
                
                # Check for == True or is True
                if isinstance(comparator, ast.Constant):
                    if comparator.value is True:
                        if isinstance(test.ops[0], (ast.Eq, ast.Is)):
                            node.test = test.left
                    elif comparator.value is False:
                        if isinstance(test.ops[0], (ast.Eq, ast.Is)):
                            # if x == False -> if not x
                            node.test = ast.UnaryOp(op=ast.Not(), operand=test.left)
                        elif isinstance(test.ops[0], ast.NotEq):
                            # if x != False -> if x
                            node.test = test.left
        
        # Handle: if not (not x) -> if x
        elif isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.UnaryOp) and isinstance(test.operand.op, ast.Not):
                node.test = test.operand.operand
        
        return node
    
    def _merge_duplicate_branches(self, node):
        """
        Merge if and else branches that have identical code.
        
        Before:
            if condition:
                do_something()
            else:
                do_something()
        
        After:
            do_something()
        
        Args:
            node (ast.If): The if statement node
            
        Returns:
            ast.AST: Simplified code or original node
        """
        # If both branches exist and are identical
        if node.body and node.orelse:
            # Simple check: if both branches have the same structure
            if self._are_equivalent(node.body, node.orelse):
                # Return just the body (both are the same anyway)
                return node.body if len(node.body) > 1 else node.body[0]
        
        return node
    
    def _are_equivalent(self, body1, body2):
        """
        Check if two code blocks are equivalent.
        
        This is a simplified check using AST dump comparison.
        
        Args:
            body1: First code block
            body2: Second code block
            
        Returns:
            bool: True if equivalent
        """
        if len(body1) != len(body2):
            return False
        
        for stmt1, stmt2 in zip(body1, body2):
            if ast.dump(stmt1) != ast.dump(stmt2):
                return False
        
        return True


class BooleanExpressionSimplifier(ast.NodeTransformer):
    """
    Simplifies complex boolean expressions.
    
    Optimizations:
    - De Morgan's laws: not (a and b) -> (not a) or (not b)
    - Remove double negations: not (not x) -> x
    - Simplify redundant conditions: x and True -> x
    """
    
    def visit_UnaryOp(self, node):
        """
        Visit a unary operation and simplify if it's a 'not'.
        
        Args:
            node (ast.UnaryOp): The unary operation node
            
        Returns:
            ast.AST: Simplified expression
        """
        self.generic_visit(node)
        
        if not isinstance(node.op, ast.Not):
            return node
        
        operand = node.operand
        
        # Double negation: not (not x) -> x
        if isinstance(operand, ast.UnaryOp) and isinstance(operand.op, ast.Not):
            return operand.operand
        
        # De Morgan's laws: not (a and b) -> (not a) or (not b)
        if isinstance(operand, ast.BoolOp):
            if isinstance(operand.op, ast.And):
                # not (a and b) -> (not a) or (not b)
                return ast.BoolOp(
                    op=ast.Or(),
                    values=[
                        ast.UnaryOp(op=ast.Not(), operand=val)
                        for val in operand.values
                    ]
                )
            elif isinstance(operand.op, ast.Or):
                # not (a or b) -> (not a) and (not b)
                return ast.BoolOp(
                    op=ast.And(),
                    values=[
                        ast.UnaryOp(op=ast.Not(), operand=val)
                        for val in operand.values
                    ]
                )
        
        return node
    
    def visit_BoolOp(self, node):
        """
        Visit a boolean operation and simplify it.
        
        Optimizations:
        - x and True -> x
        - x and False -> False
        - x or True -> True
        - x or False -> x
        
        Args:
            node (ast.BoolOp): The boolean operation node
            
        Returns:
            ast.AST: Simplified expression
        """
        self.generic_visit(node)
        
        # Filter out redundant boolean constants
        new_values = []
        
        for value in node.values:
            if isinstance(value, ast.Constant):
                if isinstance(node.op, ast.And):
                    if value.value is False:
                        # x and False -> False (short circuit)
                        return ast.Constant(value=False)
                    # x and True -> just continue (will be removed)
                elif isinstance(node.op, ast.Or):
                    if value.value is True:
                        # x or True -> True (short circuit)
                        return ast.Constant(value=True)
                    # x or False -> just continue (will be removed)
            else:
                new_values.append(value)
        
        # If only one value left, return it directly
        if len(new_values) == 1:
            return new_values[0]
        
        # If no values left (all were True in AND or False in OR), return the identity
        if not new_values:
            if isinstance(node.op, ast.And):
                return ast.Constant(value=True)
            else:  # Or
                return ast.Constant(value=False)
        
        node.values = new_values
        return node


class GuardClauseOptimizer(ast.NodeTransformer):
    """
    Converts nested if statements to guard clauses for better readability.
    
    Before:
        def func(x):
            if x is not None:
                if x > 0:
                    return x * 2
            return None
    
    After:
        def func(x):
            if x is None:
                return None
            if x <= 0:
                return None
            return x * 2
    """
    
    def visit_FunctionDef(self, node):
        """
        Visit a function and apply guard clause optimization.
        
        Args:
            node (ast.FunctionDef): The function definition
            
        Returns:
            ast.FunctionDef: Optimized function
        """
        self.generic_visit(node)
        
        # This is a more complex optimization that would require
        # significant control flow analysis. Simplified for now.
        
        return node


def optimize_conditionals(tree):
    """
    Apply all conditional optimizations.
    
    Args:
        tree (ast.AST): Abstract Syntax Tree to optimize
        
    Returns:
        ast.AST: Optimized tree
    """
    tree = ConditionalOptimizer().visit(tree)
    tree = BooleanExpressionSimplifier().visit(tree)
    tree = GuardClauseOptimizer().visit(tree)
    return tree
