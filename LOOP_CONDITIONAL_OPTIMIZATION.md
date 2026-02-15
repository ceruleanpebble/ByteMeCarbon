# Loop and Conditional Optimization Rules

## Overview
Two new optimization rules have been added to ByteMeCarbon to make code more efficient:

1. **Loop Optimization** (`loop_optimization.py`)
2. **Conditional Optimization** (`conditional_optimization.py`)

## Loop Optimization

### Features

#### 1. List Comprehension Conversion
Converts simple append loops to more efficient list comprehensions.

**Before:**
```python
result = []
for item in items:
    result.append(item * 2)
```

**After:**
```python
result = [item * 2 for item in items]
```

#### 2. Empty Loop Removal
Removes loops that don't perform any operations.

**Before:**
```python
while True:
    pass
```

**After:**
```python
# (removed entirely)
```

#### 3. Range-Len Pattern Optimization
Optimizes `range(len(x))` patterns to direct iteration (conservative implementation).

**Before:**
```python
for i in range(len(items)):
    print(items[i])
```

**After:**
```python
for item in items:
    print(item)
```

## Conditional Optimization

### Features

#### 1. Redundant Else Removal
Removes else blocks that only contain `pass`.

**Before:**
```python
if condition:
    do_something()
else:
    pass
```

**After:**
```python
if condition:
    do_something()
```

#### 2. Nested If Simplification
Combines nested if statements without else clauses.

**Before:**
```python
if condition1:
    if condition2:
        do_something()
```

**After:**
```python
if condition1 and condition2:
    do_something()
```

#### 3. Boolean Expression Simplification
Simplifies redundant boolean comparisons.

**Before:**
```python
if x == True:
    return "yes"

if y == False:
    return "no"

if not (not z):
    return "maybe"
```

**After:**
```python
if x:
    return "yes"

if not y:
    return "no"

if z:
    return "maybe"
```

#### 4. Redundant Boolean Removal
Removes unnecessary `True` and `False` in boolean operations.

**Before:**
```python
if flag and True:
    return "active"

if value or False:
    return "valid"
```

**After:**
```python
if flag:
    return "active"

if value:
    return "valid"
```

#### 5. De Morgan's Laws
Applies De Morgan's laws to simplify negated boolean expressions.

**Before:**
```python
if not (a and b):
    return "invalid"
```

**After:**
```python
if (not a) or (not b):
    return "invalid"
```

#### 6. Duplicate Branch Merging
Merges if/else branches that contain identical code.

**Before:**
```python
if condition:
    do_something()
    return True
else:
    do_something()
    return True
```

**After:**
```python
do_something()
return True
```

## Integration

These rules are automatically applied in the optimization pipeline in `optimizer.py`:

```python
def optimize(tree):
    # ... other optimizations ...
    tree = optimize_conditionals(tree)  # Conditional optimizations
    tree = optimize_loops(tree)  # Loop optimizations
    # ... more optimizations ...
    return tree
```

## Testing

Run the test script to see all optimizations in action:

```bash
python test_new_rules.py
```

## Benefits

### Performance Improvements
- **List comprehensions** are 20-30% faster than equivalent loops
- **Simplified conditionals** reduce branching overhead
- **Removed dead code** reduces execution time and memory

### Code Quality
- More readable and Pythonic code
- Fewer lines of code
- Better maintenance

### Energy Efficiency
- Faster execution = less CPU time
- Less CPU time = lower energy consumption
- Lower energy = reduced carbon footprint

## Examples

See `test_optimizations.py` for comprehensive examples of all optimization patterns.

## Technical Details

Both rules use AST (Abstract Syntax Tree) transformations:
- **NodeTransformer** for modifying the tree
- **NodeVisitor** for analyzing patterns
- Conservative optimizations to ensure correctness

## Future Enhancements

Potential additions:
- Set/dict comprehensions
- Generator expressions for large datasets
- Early return optimization (guard clauses)
- More aggressive loop fusion
- Constant propagation in conditionals
