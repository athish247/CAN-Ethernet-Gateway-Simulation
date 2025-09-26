from typing import Optional, Dict, Any, List
from .can_bus import CANFrame
from .ethernet_bus import EthernetPacket
from .utils import gen_id, now_ms
import threading, time

class ProtocolTranslator:
    """Translates between CAN and Ethernet protocols"""
    def __init__(self, can_to_eth_map: Dict[int, str] = None, 
                 eth_to_can_map: Dict[str, int] = None):
        self.can_to_eth_map = can_to_eth_map or {
            0x100: "192.168.0.10", 
            0x101: "192.168.0.11",
            0x200: "192.168.0.20",
            0x300: "192.168.0.30"
        }
        self.eth_to_can_map = eth_to_can_map or {
            "192.168.0.10": 0x100, 
            "192.168.0.11": 0x101,
            "192.168.0.20": 0x200,
            "192.168.0.30": 0x300
        }
        self.translation_count = 0
        self.lock = threading.Lock()
        self.latencies = []
    
    def can_to_eth(self, frame: CANFrame, dst: Optional[str] = None) -> EthernetPacket:
        """Convert CAN frame to Ethernet packet"""
        start_time = now_ms()
        if not hasattr(self, '_scenario') or self._scenario == 'baseline':
            time.sleep(0.00005)  # 0.05ms
            
        # ATTACK: Slower due to congestion (0.2ms)  
        elif self._scenario == 'attack':
            time.sleep(0.0002)   # 0.2ms
            
        # SECURE: Medium with security (0.1ms)
        else:  # secure
            time.sleep(0.0001)   # 0.1ms
        ip = dst or self.can_to_eth_map.get(frame.can_id, "192.168.0.99")
        pkt = EthernetPacket(
            ts_ms=now_ms(), 
            src="gateway", 
            dst=ip, 
            payload=frame.data,
            msg_id=frame.msg_id or gen_id("eth")
        )
        
        # Track translation metrics
        with self.lock:
            self.translation_count += 1
            latency = now_ms() - start_time
            self.latencies.append(latency)
        
        return pkt
    
    def eth_to_can(self, pkt: EthernetPacket) -> CANFrame:
        """Convert Ethernet packet to CAN frame"""
        start_time = now_ms()
        if not hasattr(self, '_scenario') or self._scenario == 'baseline':
            time.sleep(0.00008)  # Slightly slower for ETH->CAN
        elif self._scenario == 'attack':
            time.sleep(0.00025)  
        else:  # secure
            time.sleep(0.00015)
        can_id = self.eth_to_can_map.get(pkt.src, 0x200)
        frame = CANFrame(
            ts_ms=now_ms(), 
            can_id=can_id, 
            dlc=min(len(pkt.payload), 8),  # CAN limit
            data=pkt.payload[:8],  # Truncate to CAN size
            src="gateway",
            msg_id=pkt.msg_id or gen_id("can")
        )
        
        with self.lock:
            self.translation_count += 1
            latency = now_ms() - start_time
            self.latencies.append(latency)
        
        return frame
    
    def get_stats(self) -> Dict[str, Any]:
        """Get translation statistics"""
        with self.lock:
            avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
            return {
                "translations": self.translation_count,
                "avg_latency_ms": avg_latency
            }
