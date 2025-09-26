import os, csv, time, hashlib, hmac, random
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import threading

DATA_DIR = os.environ.get("DATA_DIR", "data")

# Thread-safe counter for message IDs
class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    
    def get_next(self):
        with self.lock:
            self.value += 1
            return self.value

msg_counter = Counter()

def ensure_dir(path: str):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

def now_us() -> int:
    """Get current timestamp in microseconds"""
    return int(time.time() * 1_000_000)

def now_ms() -> float:
    """Get current timestamp in milliseconds (with decimals)"""
    return time.time() * 1000.0

def write_csv(rows: List[Dict[str, Any]], path: str):
    """Write data to CSV file"""
    ensure_dir(os.path.dirname(path))
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def gen_id(prefix: str = "") -> str:
    """Generate unique ID"""
    return f"{prefix}{msg_counter.get_next()}"

def calculate_latency_percentile(latencies: List[float], percentile: int = 95) -> float:
    """Calculate latency percentile"""
    if not latencies:
        return 0.0
    sorted_latencies = sorted(latencies)
    index = int(len(sorted_latencies) * percentile / 100)
    return sorted_latencies[min(index, len(sorted_latencies)-1)]
