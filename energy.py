# energy.py
"""
Energy consumption tracking module.

Measures carbon emissions and energy consumption of code execution using CodeCarbon.
CodeCarbon is platform-dependent:
  - Linux: Accurate CPU/power measurements
  - macOS: Good support with proper drivers
  - Windows: Uses TDP estimation (consider Intel Power Gadget for better accuracy)
"""

import subprocess
import os
import tempfile
import sys
from codecarbon import EmissionsTracker


def measure_energy_simple(code_string):
    """
    Measure carbon emissions of a code snippet execution.
    
    Quick way to measure emissions without file operations.
    
    Args:
        code_string (str): Python code to execute and measure
        
    Returns:
        float: CO2 emissions in kilograms
        
    Note:
        On Windows, uses TDP-based estimation. Install Intel Power Gadget
        for accurate CPU power measurements.
    """
    tracker = EmissionsTracker(save_to_file=False, log_level="error")
    
    try:
        tracker.start()
        
        # Execute the code
        exec(code_string, {"__name__": "__main__"})
        
        emissions = tracker.stop()
        return emissions if emissions else 0.0
        
    except Exception as e:
        print(f"Error measuring energy: {str(e)}")
        return 0.0


def measure_energy(script_path, experiment_label="run"):
    """
    Measure carbon emissions and energy consumption of a script file.
    
    Uses CodeCarbon to track CO2 emissions during script execution.
    
    Args:
        script_path (str): Path to the Python script to measure
        experiment_label (str): Label for the experiment (default: "run")
            
    Returns:
        float: CO2 emissions in kilograms
        
    Raises:
        subprocess.CalledProcessError: If the script exits with non-zero status
        
    Note:
        Results are saved to emissions.csv in current directory.
        Windows users: Install Intel Power Gadget for accurate measurements.
    """
    tracker = EmissionsTracker(
        save_to_file=True,
        log_level="error"
    )

    tracker.start()

    try:
        subprocess.run([sys.executable, script_path], check=True)
        emissions = tracker.stop()
    except subprocess.CalledProcessError as e:
        tracker.stop()
        raise e

    return emissions if emissions else 0.0


def get_system_info():
    """
    Get information about CodeCarbon's current tracking setup.
    
    Returns:
        dict: System info including CPU, GPU, tracking methods
    """
    try:
        tracker = EmissionsTracker(save_to_file=False, log_level="error")
        tracker.start()
        
        info = {
            "cpu_count": tracker._cpu_count,
            "cpu_model": tracker._cpu_model if hasattr(tracker, '_cpu_model') else "Unknown",
            "gpu_available": tracker._gpu_count > 0 if hasattr(tracker, '_gpu_count') else False,
            "platform": tracker._platform_system if hasattr(tracker, '_platform_system') else "Unknown",
        }
        
        tracker.stop()
        return info
        
    except Exception:
        return {}
