import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scenarios import run_comparison

if __name__ == "__main__":
    print("Starting Full Comparison...")
    results = run_comparison()
    print("\nAll scenarios completed successfully!")