import ast
from rules.remove_unused_apis import optimize_remove_unused_apis


def test_remove_unused_function(tmp_path):
    # Create two module files: a.py defines an unused function, b.py does not reference it
    a = tmp_path / 'a.py'
    a.write_text('''
def used():
    return 1

def unused_api():
    return 42

''')

    b = tmp_path / 'b.py'
    b.write_text('''
from a import used

print(used())
''')

    # Now parse module a and run the optimizer pointing project_root at tmp_path
    tree = ast.parse(a.read_text())
    new_tree = optimize_remove_unused_apis(tree, project_root=str(tmp_path))

    # The unused_api function should be removed
    names = [n.name for n in new_tree.body if isinstance(n, ast.FunctionDef)]
    assert 'used' in names
    assert 'unused_api' not in names


def test_keep_exported_via_all(tmp_path):
    m = tmp_path / 'mod.py'
    m.write_text('''
__all__ = ['exported']

def exported():
    return 1

def internal():
    return 2
''')

    tree = ast.parse(m.read_text())
    new_tree = optimize_remove_unused_apis(tree, project_root=str(tmp_path))

    names = [n.name for n in new_tree.body if isinstance(n, ast.FunctionDef)]
    assert 'exported' in names
    assert 'internal' not in names
