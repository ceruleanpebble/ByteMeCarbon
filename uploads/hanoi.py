def solve_hanoi_iterative(n, src, aux, dest):
    # Total moves is 2^n - 1
    rods = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    
    # If n is even, swap target and auxilia
    if n % 2 == 0:
        aux, dest = dest, aux
    
    for i in range(1, 2**n):
        if i % 3 == 1:
            move_disk(rods, src, dest)
        elif i % 3 == 2:
            move_disk(rods, src, aux)
        elif i % 3 == 0:
            move_disk(rods, aux, dest)

def move_disk(rods, from_r, to_r):
    # Determine direction based on top disk
    if not rods[to_r] or (rods[from_r] and rods[from_r][-1] < rods[to_r][-1]):
        print(f"Move {rods[from_r].pop()} from {from_r} to {to_r}")
        rods[to_r].append(rods[from_r].pop())
