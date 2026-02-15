# Test file to demonstrate loop and conditional optimizations

# Example 1: Inefficient loop that will be optimized
result = []
for item in [1, 2, 3, 4, 5]:
    result.append(item * 2)

# Example 2: Redundant else with pass
def check_value(x):
    if x > 0:
        print("Positive")
    else:
        pass

# Example 3: Nested if statements
def process(a, b):
    if a > 0:
        if b > 0:
            return a + b

# Example 4: Boolean simplification
def validate(data):
    if data == True:
        return "valid"
    return "invalid"

# Example 5: Empty while loop
count = 0
while True:
    pass

# Example 6: Double negation
def is_ready(status):
    if not (not status):
        return "Ready"
    return "Not ready"

# Example 7: Redundant boolean in condition
def check_flag(flag):
    if flag and True:
        return "Active"
    return "Inactive"

# Example 8: Duplicate branches
def process_data(value):
    if value > 10:
        print("Processing")
        return True
    else:
        print("Processing")
        return True

print("Test file loaded")
