import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scenarios import run_attack

if __name__ == "__main__":
    print("Starting Attack Scenario...")
    metrics = run_attack()
    print("\nAttack scenario completed successfully!")