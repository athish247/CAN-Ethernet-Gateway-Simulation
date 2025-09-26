"""
Attack simulation module with multithreading support - FIXED
"""
import time, random, threading
from typing import List
from concurrent.futures import ThreadPoolExecutor
from .can_bus import CANFrame
from .ethernet_bus import EthernetPacket
from .utils import now_ms, gen_id

class ThreadedAttackSimulator:
    """Multithreaded attack simulator for realistic attack patterns"""
    
    def __init__(self, executor: ThreadPoolExecutor = None):
        self.executor = executor or ThreadPoolExecutor(max_workers=4)
        self.active_attacks = []
        
    def replay_attack_can(self, bus, captured: List[CANFrame], 
                          rate_hz=100, duration_s=2):
        """Replay captured CAN frames"""
        end_time = time.time() + duration_s
        i = 0
        
        while time.time() < end_time and captured:
            frame = captured[i % len(captured)]
            replayed = CANFrame(
                ts_ms=now_ms(),
                can_id=frame.can_id,
                dlc=frame.dlc,
                data=frame.data,
                src="replay_attacker",
                msg_id=gen_id("replay")
            )
            bus.send(replayed)
            i += 1
            time.sleep(0.0005)
    
    def dos_attack_can(self, bus, can_id=0x7FF, payload=b"DOS"*3,  # Ensure bytes
                       rate_hz=500, duration_s=2):
        """DoS attack flooding CAN bus"""
        end_time = time.time() + duration_s
        
        while time.time() < end_time:
            for _ in range(5): 
                dos_frame = CANFrame(
                    ts_ms=now_ms(),
                    can_id=can_id,
                    dlc=len(payload[:8]),
                    data=payload[:8],
                    src="dos_attacker",
                    msg_id=gen_id("dos")
            )
            bus.send(dos_frame)
            time.sleep(0.002)
    
    def injection_attack_can(self, bus, duration_s=2):
        """Inject malicious CAN frames"""
        end_time = time.time() + duration_s
        malicious_ids = [0x7AA, 0x7BB, 0x7CC]
        
        while time.time() < end_time:
            can_id = random.choice(malicious_ids)
            payload = bytes([random.randint(0, 255) for _ in range(8)])
            
            injected = CANFrame(
                ts_ms=now_ms(),
                can_id=can_id,
                dlc=8,
                data=payload,
                src="injection_attacker",
                msg_id=gen_id("inject")
            )
            bus.send(injected)
            time.sleep(0.0005)  # 100Hz injection
    
    def spoof_attack_eth(self, bus, dst="192.168.0.10", 
                         payload=b"SPOOFED",  # Ensure bytes
                         rate_hz=50, duration_s=2):
        """Spoofing attack on Ethernet"""
        end_time = time.time() + duration_s
        
        while time.time() < end_time:
            spoofed = EthernetPacket(
                ts_ms=now_ms(),
                src="attacker",
                dst=dst,
                payload=payload,
                msg_id=gen_id("spoof")
            )
            bus.send(spoofed)
            time.sleep(0.0005)
    
    def launch_combined_attack(self, can_bus, eth_bus, captured_frames):
        """Launch multiple attacks simultaneously using threading"""
        futures = []
        
        # Launch attacks in parallel with bytes payloads
        futures.append(self.executor.submit(
            self.replay_attack_can, can_bus, captured_frames, 150, 5
        ))
        futures.append(self.executor.submit(
            self.dos_attack_can, can_bus, 0x7FF, b"FLOOD!", 800, 5  # bytes
        ))
        futures.append(self.executor.submit(
            self.injection_attack_can, can_bus, 5
        ))
        futures.append(self.executor.submit(
            self.spoof_attack_eth, eth_bus, "192.168.0.10", b"EVIL", 200, 5  # bytes
        ))
        
        self.active_attacks = futures
        return futures
    
    def wait_completion(self):
        """Wait for all attacks to complete"""
        for future in self.active_attacks:
            future.result()
        self.active_attacks = []