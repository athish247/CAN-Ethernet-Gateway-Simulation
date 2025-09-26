import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scenarios import run_secure

if __name__ == "__main__":
    print("Starting Secure Scenario...")
    metrics = run_secure()
    print("\nSecure scenario completed successfully!")