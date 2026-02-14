# energy.py
"""
Energy consumption tracking module.

Measures carbon emissions and energy consumption of code execution using CodeCarbon.
"""

import subprocess
import os
from codecarbon import EmissionsTracker


def measure_energy(script_path, experiment_label="run"):
    """
    Measure carbon emissions and energy consumption of a script.
    
    Uses CodeCarbon to track CO2 emissions during script execution.
    
    Args:
        script_path (str): Path to the Python script to measure
        experiment_label (str): Label for the experiment (default: "run")
            Used to identify emissions in the CSV output
        
    Returns:
        float: CO2 emissions in kilograms
        
    Raises:
        subprocess.CalledProcessError: If the script exits with non-zero status
    """
    tracker = EmissionsTracker(
        project_name="CarbonIQ",
        experiment_id=experiment_label,
        output_dir=".",
        output_file="emissions.csv",
        save_to_file=True,
        log_level="error"
    )

    tracker.start()

    subprocess.run(["python", script_path], check=True)

    emissions = tracker.stop()

    # Clean up backup files automatically
    for file in os.listdir("."):
        if file.startswith("emissions.csv") and file.endswith(".bak"):
            os.remove(file)

    return emissions
