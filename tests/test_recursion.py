# Test file to demonstrate recursion to iteration optimization

# Tail-recursive factorial (should be converted)
def fact(n, acc=1):
    if n == 0:
        return acc
    else:
        return fact(n-1, acc * n)


# Non-tail-recursive Fibonacci (should NOT be converted by conservative rule)
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)


print('Recursion test file loaded')
