# parser.py
import ast

def parse_code(source_code: str) -> ast.AST:
    return ast.parse(source_code)

def generate_code(tree: ast.AST) -> str:
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)
