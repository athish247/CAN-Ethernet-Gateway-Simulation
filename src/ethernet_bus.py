import queue, threading, time
from typing import Optional, List, Dict
from dataclasses import dataclass
from .utils import now_ms

@dataclass
class EthernetPacket:
    ts_ms: int
    src: str
    dst: str
    payload: bytes
    msg_id: str = ""  # Unique identifier for tracking
    priority: int = 0 #

class HighPerformanceEthernetBus:
    """Thread-safe Ethernet bus with batch processing"""
    def __init__(self, batch_size=50):
        self.q = queue.Queue()
        self.batch_size = batch_size
        self.lock = threading.Lock()
        self.packets_sent = 0
        self.packets_received = 0
        
    def send(self, pkt: EthernetPacket):
        """Send an Ethernet packet"""
        with self.lock:
            self.packets_sent += 1
        self.q.put(pkt)
    
    def send_batch(self, packets: List[EthernetPacket]):
        """Send multiple packets efficiently"""
        with self.lock:
            self.packets_sent += len(packets)
        for pkt in packets:
            self.q.put(pkt)
    
    def recv(self, timeout: float = 0.5) -> Optional[EthernetPacket]:
        """Receive an Ethernet packet"""
        try:
            pkt = self.q.get(timeout=timeout)
            with self.lock:
                self.packets_received += 1
            return pkt
        except queue.Empty:
            return None
    
    def recv_batch(self, max_packets: int = 10, timeout: float = 0.5) -> List[EthernetPacket]:
        """Receive multiple packets efficiently"""
        packets = []
        deadline = time.time() + timeout
        
        while len(packets) < max_packets and time.time() < deadline:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            try:
                pkt = self.q.get(timeout=min(remaining, 0.01))
                packets.append(pkt)
                with self.lock:
                    self.packets_received += 1
            except queue.Empty:
                if packets:
                    break
        
        return packets
    
    def get_stats(self) -> Dict[str, int]:
        """Get bus statistics"""
        with self.lock:
            return {
                "sent": self.packets_sent,
                "received": self.packets_received,
                "queued": self.q.qsize()
            }

def make_eth_bus():
    """Factory function for Ethernet bus"""
    return HighPerformanceEthernetBus()
