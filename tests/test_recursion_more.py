# More recursion-to-iteration test cases

# Pattern 1: tail-return immediately after an If
def fact2(n, acc=1):
    if n == 0:
        return acc
    return fact2(n-1, acc * n)


# Pattern 2: tail-return inside else branch (previous implementation covered this,
# but we include it to ensure the extended transformer keeps handling it)
def fact3(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact3(n-1, acc * n)


# Pattern 3: keyword arguments in recursive call
def kw_tail(n, acc=1):
    if n == 0:
        return acc
    return kw_tail(acc=acc * n, n=n-1)


print('more recursion tests loaded')
