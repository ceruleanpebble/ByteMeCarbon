# energy.py
import subprocess
import os
from codecarbon import EmissionsTracker


def measure_energy(script_path, experiment_label="run"):
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
