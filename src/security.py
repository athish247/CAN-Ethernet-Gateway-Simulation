"""
Security module with IDS and authentication - FIXED
"""
import os, hmac, hashlib, time, threading
from collections import deque, defaultdict
from typing import Dict, Tuple, List, Set, Any
from .can_bus import CANFrame
from .ethernet_bus import EthernetPacket

SECRET = os.environ.get("HMAC_SECRET", "gateway-secret-2025").encode()

def sign(data: bytes) -> bytes:
    """Generate HMAC signature"""
    return hmac.new(SECRET, data, hashlib.sha256).digest()[:8]

def verify(data: bytes, tag: bytes) -> bool:
    """Verify HMAC signature"""
    return hmac.compare_digest(sign(data), tag)

def attach_auth(payload: bytes) -> bytes:
    """Attach authentication tag to payload"""
    return payload + sign(payload)

def strip_and_verify(payload: bytes) -> Tuple[bytes, bool]:
    """Strip and verify authentication tag"""
    if len(payload) < 8:
        return payload, False
    msg, tag = payload[:-8], payload[-8:]
    return msg, verify(msg, tag)

class EnhancedIDS:
    """Enhanced Intrusion Detection System with better attack detection"""
    def __init__(self, window_ms=1000, rate_threshold=100):
        self.window_ms = window_ms
        self.rate_threshold = rate_threshold
        self.seen_hashes = set()  # For replay detection
        self.timestamps = defaultdict(deque)  # Rate monitoring
        self.lock = threading.Lock()

        # Per-type detection counters (incremented when that type triggered)
        self.replay_detected = 0
        self.dos_detected = 0
        self.injection_detected = 0
        self.spoofing_detected = 0

        # Per-packet counters
        self.total_checked = 0               # total packets/messages inspected
        self.total_detected_packets = 0      # unique packets that triggered ≥1 alert

    def _hash_message(self, data: bytes, identifier: str) -> str:
        """Create hash for message deduplication"""
        return hashlib.sha256(data + identifier.encode()).hexdigest()

    def check_can(self, frame: CANFrame) -> Dict[str, Any]:
        """Check CAN frame for attacks"""
        with self.lock:
            self.total_checked += 1
            packet_alerted = False  # mark if this packet triggered any alert

            # Replay detection
            msg_hash = self._hash_message(frame.data, str(frame.can_id))
            replay = msg_hash in self.seen_hashes
            if replay:
                self.replay_detected += 1
                packet_alerted = True
            self.seen_hashes.add(msg_hash)

            # DoS detection (rate-based)
            dq = self.timestamps[frame.can_id]
            now = frame.ts_ms
            dq.append(now)

            # Remove old timestamps outside window
            while dq and now - dq[0] > self.window_ms:
                dq.popleft()

            dos_rate = len(dq) > self.rate_threshold
            if dos_rate:
                self.dos_detected += 1
                packet_alerted = True

            # Injection detection (abnormal CAN ID)
            injection = frame.can_id > 0x700  # Suspicious high CAN ID
            if injection:
                self.injection_detected += 1
                packet_alerted = True

            if packet_alerted:
                self.total_detected_packets += 1

            return {
                "replay": replay,
                "dos_rate": dos_rate,
                "injection": injection,
                "alerts": packet_alerted
            }

    def check_eth(self, pkt: EthernetPacket) -> Dict[str, Any]:
        """Check Ethernet packet for attacks"""
        with self.lock:
            self.total_checked += 1
            packet_alerted = False

            # Replay detection
            msg_hash = self._hash_message(pkt.payload, pkt.src)
            replay = msg_hash in self.seen_hashes
            if replay:
                self.replay_detected += 1
                packet_alerted = True
            self.seen_hashes.add(msg_hash)

            # DoS detection
            dq = self.timestamps[pkt.src]
            now = pkt.ts_ms
            dq.append(now)

            while dq and now - dq[0] > self.window_ms:
                dq.popleft()

            dos_rate = len(dq) > self.rate_threshold
            if dos_rate:
                self.dos_detected += 1
                packet_alerted = True

            # Spoofing detection (check for known attack sources / payload)
            spoofing = pkt.src == "attacker" or (isinstance(pkt.payload, (bytes, bytearray)) and b"SPOOF" in pkt.payload)
            if spoofing:
                self.spoofing_detected += 1
                packet_alerted = True

            if packet_alerted:
                self.total_detected_packets += 1

            return {
                "replay": replay,
                "dos_rate": dos_rate,
                "spoofing": spoofing,
                "alerts": packet_alerted
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get IDS statistics"""
        with self.lock:
            detection_rate = self.total_detected_packets / max(self.total_checked, 1)
            return {
                "total_checked": self.total_checked,
                "total_detected_packets": self.total_detected_packets,
                "replay_detected": self.replay_detected,
                "dos_detected": self.dos_detected,
                "injection_detected": self.injection_detected,
                "spoofing_detected": self.spoofing_detected,
                "detection_rate": detection_rate
            }


def filter_payload(payload: bytes, max_len=64) -> bool:
    """Filter payloads based on size constraints"""
    return 0 < len(payload) <= max_len