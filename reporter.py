# reporter.py
"""
Report generation module.

Creates detailed optimization reports with metrics, analysis, and real-world impact.
"""

import json
from datetime import datetime


def real_world_equivalents(co2_saved_kg, runs_per_year=50000):
    """
    Calculate real-world equivalents for carbon savings.
    
    Converts CO2 savings into relatable metrics like electric car distance,
    laptop charges, and LED bulb usage hours.
    
    Args:
        co2_saved_kg (float): CO2 saved in kilograms
        runs_per_year (int): Estimated number of times code runs per year
        
    Returns:
        dict: Dictionary with per-run and yearly equivalents
            - per_run: CO2 and energy saved per execution
            - projected_yearly: Yearly savings with real-world equivalents
    """
    if co2_saved_kg <= 0:
        return {
            "message": "Energy difference is within measurement noise."
        }

    # Convert CO2 to kWh (approximation: 1 kWh ≈ 0.4 kg CO2)
    kwh_per_run = co2_saved_kg / 0.4
    yearly_kwh = kwh_per_run * runs_per_year

    grams_per_run = co2_saved_kg * 1000
    yearly_grams = grams_per_run * runs_per_year

    return {
        "per_run": {
            "co2_saved": f"{grams_per_run:.6f} grams",
            "energy_saved": f"{kwh_per_run * 1000:.6f} Wh"
        },
        "projected_yearly": {
            "runs_assumed": runs_per_year,
            "co2_saved": f"{yearly_grams:.2f} grams",
            "energy_saved": f"{yearly_kwh:.4f} kWh",
            "equivalents": {
                "led_10w_usage": f"{(yearly_kwh / 0.01):.2f} hours",
                "electric_car_distance": f"{(yearly_kwh / 0.15):.2f} km",
                "laptop_full_charges": f"{(yearly_kwh / 0.05):.2f} charges"
            }
        }
    }


def generate_report(
    input_file,
    before_complexity,
    after_complexity,
    baseline_time,
    optimized_time,
    baseline_energy,
    optimized_energy,
    runs_per_year=50000,
    output_file="report.json"
):
    """
    Generate a comprehensive optimization report.
    
    Creates a JSON report with:
    - Metadata (file name, timestamp)
    - Complexity analysis (before/after)
    - Performance metrics (time improvement)
    - Energy metrics (CO2 reduction)
    - Real-world impact calculations
    
    Args:
        input_file (str): Path or name of the input file
        before_complexity (str): Complexity before optimization (e.g., "O(n)")
        after_complexity (str): Complexity after optimization
        baseline_time (float): Execution time before optimization (seconds)
        optimized_time (float): Execution time after optimization (seconds)
        baseline_energy (float): CO2 emissions before optimization (kg)
        optimized_energy (float): CO2 emissions after optimization (kg)
        runs_per_year (int): Estimated yearly executions (default: 50000)
        output_file (str): Path to save the report (default: "report.json")
        
    Returns:
        str: Path to the generated report file
    """
    time_improvement = baseline_time - optimized_time
    co2_saved = baseline_energy - optimized_energy

    performance_status = "Improved" if time_improvement > 0 else "Slightly Slower"
    energy_status = "Reduced" if co2_saved > 0 else "Within Measurement Noise"

    report = {
        "metadata": {
            "input_file": input_file,
            "generated_at": datetime.now().isoformat()
        },
        "complexity": {
            "before": before_complexity,
            "after": after_complexity
        },
        "performance": {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "baseline_time_display": f"{baseline_time * 1000:.2f} ms",
            "optimized_time_display": f"{optimized_time * 1000:.2f} ms",
            "time_difference": f"{time_improvement * 1000:.2f} ms",
            "status": performance_status
        },
        "energy": {
            "baseline_co2": baseline_energy * 1000,
            "optimized_co2": optimized_energy * 1000,
            "baseline_co2_display": f"{baseline_energy * 1000:.6f} grams",
            "optimized_co2_display": f"{optimized_energy * 1000:.6f} grams",
            "co2_difference": f"{co2_saved * 1000:.6f} grams",
            "status": energy_status
        },
        "real_world_impact": real_world_equivalents(co2_saved, runs_per_year=runs_per_year)
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=4)

    return output_file
