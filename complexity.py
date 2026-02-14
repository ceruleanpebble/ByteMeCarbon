# complexity.py
import ast

class LoopDepthAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def visit_For(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.visit_For(node)

def estimate_complexity(tree):
    analyzer = LoopDepthAnalyzer()
    analyzer.visit(tree)

    if analyzer.max_depth == 0:
        return "O(1)"
    elif analyzer.max_depth == 1:
        return "O(n)"
    else:
        return f"O(n^{analyzer.max_depth})"
