import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scenarios import run_baseline

if __name__ == "__main__":
    print("Starting Baseline Scenario...")
    metrics = run_baseline()
    print("\nBaseline scenario completed successfully!")