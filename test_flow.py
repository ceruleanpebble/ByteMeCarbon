"""Quick test to verify the entire optimization flow works."""

import sys
import json
from parser import parse_code, generate_code
from optimizer import optimize
from complexity import estimate_complexity
from reporter import generate_report

# Test code
test_code = """
import os
import sys

def unused_func():
    return 0

def used_func():
    return 42

if True:
    x = 2 + 3
else:
    y = 999

result = used_func()
"""

print("=" * 60)
print("TESTING BYTEMECARBON OPTIMIZATION FLOW")
print("=" * 60)

try:
    print("\n1. PARSING CODE...")
    tree = parse_code(test_code)
    print("   ✓ Code parsed successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n2. ESTIMATING COMPLEXITY (before)...")
    before_complexity = estimate_complexity(tree)
    print(f"   ✓ Complexity: {before_complexity}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n3. OPTIMIZING CODE...")
    optimized_tree = optimize(tree)
    print("   ✓ Optimization complete")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n4. ESTIMATING COMPLEXITY (after)...")
    after_complexity = estimate_complexity(optimized_tree)
    print(f"   ✓ Complexity: {after_complexity}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n5. GENERATING OPTIMIZED CODE...")
    optimized_code = generate_code(optimized_tree)
    print(f"   ✓ Generated {len(optimized_code)} chars of code")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n6. GENERATING REPORT...")
    report_path = generate_report(
        input_file="test.py",
        before_complexity=before_complexity,
        after_complexity=after_complexity,
        baseline_time=0.001,
        optimized_time=0.0009,
        baseline_energy=0.00001,
        optimized_energy=0.000008,
        runs_per_year=10000,
        output_file="test_report.json"
    )
    print(f"   ✓ Report saved to {report_path}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("\n7. READING REPORT JSON...")
    with open(report_path, "r") as f:
        report = json.load(f)
    print("   ✓ Report JSON loaded")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n8. CHECKING REPORT STRUCTURE...")
try:
    # Check top-level keys
    required_keys = ["metadata", "complexity", "performance", "energy", "real_world_impact"]
    for key in required_keys:
        if key not in report:
            print(f"   ✗ Missing key: {key}")
        else:
            print(f"   ✓ {key}: OK")
    
    # Check complexity
    print(f"\n   Complexity: {report['complexity']['before']} → {report['complexity']['after']}")
    
    # Check performance
    print(f"   Performance: {report['performance']['status']}")
    print(f"   Time: {report['performance']['baseline_time']} → {report['performance']['optimized_time']}")
    
    # Check energy
    print(f"   Energy: {report['energy']['status']}")
    print(f"   CO2: {report['energy']['baseline_co2']} → {report['energy']['optimized_co2']}")
    
    # Check real-world impact
    print(f"\n   Real-world impact:")
    impact = report['real_world_impact']
    if 'per_run' in impact:
        print(f"     Per run: {impact['per_run']['co2_saved']}")
        print(f"     Energy: {impact['per_run']['energy_saved']}")
    if 'projected_yearly' in impact:
        print(f"     Yearly: {impact['projected_yearly']['co2_saved']}")
        print(f"     Distance: {impact['projected_yearly']['equivalents']['electric_car_distance']}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print(f"\nOptimized code:\n{optimized_code}\n")
