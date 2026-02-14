# Contributing to ByteMeCarbon

Thank you for your interest in contributing to ByteMeCarbon! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/ByteMeCarbon.git
   cd ByteMeCarbon
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_optimizer.py -v
```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular

## Adding New Optimization Rules

To add a new optimization rule:

1. Create a new file in `rules/` folder
2. Implement a class extending `ast.NodeTransformer`
3. Add docstrings explaining the optimization
4. Add the rule to `optimizer.py`
5. Write tests in `tests/test_rules.py`

Example template:

```python
# rules/my_optimization.py
"""
My optimization rule description.
"""

import ast

class MyOptimizer(ast.NodeTransformer):
    """Optimization description."""
    
    def visit_NodeType(self, node):
        """
        Visit a node and apply optimization.
        
        Args:
            node: The AST node to visit
            
        Returns:
            Optimized AST node or None to remove
        """
        self.generic_visit(node)
        # Your optimization logic here
        return node
```

4. Register in `optimizer.py`:

```python
def optimize(tree):
    # ... existing code ...
    tree = MyOptimizer().visit(tree)
    return tree
```

5. Add test in `tests/test_rules.py`:

```python
def test_my_optimization():
    code = "# Your test code"
    tree = parse_code(code)
    optimizer = MyOptimizer()
    optimized = optimizer.visit(tree)
    # Assert optimization worked
```

## Bug Reports

When reporting bugs, include:

1. Python version
2. ByteMeCarbon version
3. Detailed steps to reproduce
4. Expected vs. actual behavior
5. Error message or traceback

## Feature Requests

When suggesting features, describe:

1. The use case
2. Expected behavior
3. Example code if applicable
4. Why this would be beneficial

## Pull Request Process

1. Create a descriptive branch name: `feature/my-feature` or `fix/my-bug`
2. Make commits with clear messages
3. Write or update tests for your changes
4. Ensure all tests pass: `pytest`
5. Update documentation as needed
6. Submit PR with description of changes

## Code Review

After submitting a PR:

- Maintainers will review your code
- Provide feedback or request changes
- Once approved, your PR will be merged
- Your contribution will be acknowledged

## Reporting Security Issues

Please do NOT open an issue for security vulnerabilities. Instead, email security@bytemecarbon.dev with details.

## Questions?

- Check existing issues and discussions
- Ask in GitHub Discussions
- Email: support@bytemecarbon.dev

Thank you for contributing to greener code! 🌱
