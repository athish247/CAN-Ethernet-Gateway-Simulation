import os, time, queue, threading
from typing import Dict, Any, Optional, List, Dict
from dataclasses import dataclass
from .utils import now_ms
from concurrent.futures import ThreadPoolExecutor

USE_VCAN = os.environ.get("USE_VCAN", "0") == "1"
CAN_INTERFACE = os.environ.get("CAN_INTERFACE", "vcan0")

@dataclass
class CANFrame:
    ts_ms: int
    can_id: int
    dlc: int
    data: bytes
    src: str = "node"
    msg_id: str = ""  # Unique identifier for tracking

class HighPerformanceCANBus:
    """Thread-safe CAN bus with batch processing"""
    def __init__(self, batch_size=50):
        self.q = queue.Queue()
        self.batch_size = batch_size
        self.lock = threading.Lock()
        self.messages_sent = 0
        self.messages_received = 0
        
    def send(self, frame: CANFrame):
        """Send a CAN frame"""
        with self.lock:
            self.messages_sent += 1
        self.q.put(frame)
    
    def send_batch(self, frames: List[CANFrame]):
        """Send multiple frames efficiently"""
        with self.lock:
            self.messages_sent += len(frames)
        for frame in frames:
            self.q.put(frame)
    
    def recv(self, timeout: float = 0.5) -> Optional[CANFrame]:
        """Receive a CAN frame"""
        try:
            frame = self.q.get(timeout=timeout)
            with self.lock:
                self.messages_received += 1
            return frame
        except queue.Empty:
            return None
    
    def recv_batch(self, max_frames: int = 10, timeout: float = 0.5) -> List[CANFrame]:
        """Receive multiple frames efficiently"""
        frames = []
        deadline = time.time() + timeout
        
        while len(frames) < max_frames and time.time() < deadline:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            try:
                frame = self.q.get(timeout=min(remaining, 0.01))
                frames.append(frame)
                with self.lock:
                    self.messages_received += 1
            except queue.Empty:
                if frames:  # Return what we have if any
                    break
        
        return frames
    
    def get_stats(self) -> Dict[str, int]:
        """Get bus statistics"""
        with self.lock:
            return {
                "sent": self.messages_sent,
                "received": self.messages_received,
                "queued": self.q.qsize()
            }

def make_can_bus():
    """Factory function for CAN bus"""
    return HighPerformanceCANBus()
