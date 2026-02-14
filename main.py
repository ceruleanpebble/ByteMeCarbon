# main.py
import sys
import os
from parser import parse_code, generate_code
from optimizer import optimize
from complexity import estimate_complexity
from energy import measure_energy
from benchmark import measure_time
from reporter import generate_report
import argparse


def main(file_path, runs_per_year=10000):

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    # -------- BASELINE --------
    print("Running baseline measurement...")
    baseline_time = measure_time(file_path)
    baseline_energy = measure_energy(file_path, experiment_label="baseline")

    # -------- OPTIMIZATION --------
    with open(file_path, "r") as f:
        source = f.read()

    tree = parse_code(source)
    before_complexity = estimate_complexity(tree)

    optimized_tree = optimize(tree)
    after_complexity = estimate_complexity(optimized_tree)

    optimized_code = generate_code(optimized_tree)

    optimized_path = "optimized.py"
    with open(optimized_path, "w") as f:
        f.write(optimized_code)

    # -------- OPTIMIZED MEASUREMENT --------
    print("Running optimized measurement...")
    optimized_time = measure_time(optimized_path)
    optimized_energy = measure_energy(optimized_path, experiment_label="optimized")
    # -------- REPORT --------
    print("\n--- RESULTS ---")
    print("Before Complexity:", before_complexity)
    print("After Complexity:", after_complexity)

    print(f"Baseline Time: {baseline_time:.6f}s")
    print(f"Optimized Time: {optimized_time:.6f}s")

    print(f"Baseline CO2 (kg): {baseline_energy:.6e}")
    print(f"Optimized CO2 (kg): {optimized_energy:.6e}")

    time_delta = baseline_time - optimized_time
    energy_delta = baseline_energy - optimized_energy

    print(f"Time Improvement: {time_delta:.6f}s")
    print(f"Energy Saved (kg CO2): {energy_delta:.6e}")
    print("Optimized code written to optimized.py")

    report_path = generate_report(
    file_path,
    before_complexity,
    after_complexity,
    baseline_time,
    optimized_time,
    baseline_energy,
    optimized_energy
    )

    print(f"JSON report written to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CarbonIQ Code Optimizer")

    parser.add_argument("file", help="Path to Python file to analyze")
    parser.add_argument("--runs", type=int, default=10000,
                        help="Estimated number of executions per year")

    args = parser.parse_args()

    main(args.file, runs_per_year=args.runs)


