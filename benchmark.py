# benchmark.py
"""
Benchmarking module.

Measures execution time of Python scripts.
"""

import subprocess
import time

def measure_time(script_path):
    """
    Measure the execution time of a Python script.
    
    Args:
        script_path (str): Path to the Python script to measure
        
    Returns:
        float: Execution time in seconds
        
    Raises:
        subprocess.CalledProcessError: If the script exits with non-zero status
    """
    start = time.perf_counter()

    subprocess.run(["python", script_path], check=True)

    end = time.perf_counter()

    return end - start
