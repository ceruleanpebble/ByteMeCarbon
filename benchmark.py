# benchmark.py
import subprocess
import time

def measure_time(script_path):
    start = time.perf_counter()

    subprocess.run(["python", script_path], check=True)

    end = time.perf_counter()

    return end - start
