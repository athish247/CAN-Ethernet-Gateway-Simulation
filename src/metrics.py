import statistics
from typing import List, Dict, Any
from .utils import calculate_latency_percentile

class MetricsCalculator:
    """Calculate comprehensive metrics for gateway performance"""
    
    @staticmethod
    def compute_latency(samples: List[Dict]) -> Dict[str, float]:
        """Compute latency statistics"""
        latencies = [s.get("latency_ms", 0) for s in samples if "latency_ms" in s]
        
        if not latencies:
            return {"mean": 0, "p50": 0, "p95": 0, "p99": 0}
        
        return {
            "mean": statistics.mean(latencies),
            "p50": calculate_latency_percentile(latencies, 50),
            "p95": calculate_latency_percentile(latencies, 95),
            "p99": calculate_latency_percentile(latencies, 99),
            "min": min(latencies),
            "max": max(latencies)
        }
    
    @staticmethod
    def compute_throughput(samples: List[Dict], duration_s: float = None) -> float:
        """Compute throughput in messages per second"""
        if not samples:
            return 0.0
        
        if duration_s is None:
            first_ts = samples[0].get("ts_ms", 0)
            last_ts = samples[-1].get("ts_ms", 0)
            duration_s = max((last_ts - first_ts) / 1000.0, 0.001)
        
        return len(samples) / duration_s
    
    @staticmethod
    def compute_jitter(samples: List[Dict]) -> float:
        """Compute jitter (variation in latency)"""
        if len(samples) < 2:
            return 0.0
        
        timestamps = [s.get("ts_ms", 0) for s in samples]
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not intervals:
            return 0.0
        
        return statistics.stdev(intervals) if len(intervals) > 1 else 0.0
    
    @staticmethod
    def compute_packet_loss(sent: int, received: int) -> float:
        """Compute packet loss percentage"""
        if sent == 0:
            return 0.0
        return ((sent - received) / sent) * 100.0
    
    @staticmethod
    def generate_report(metrics: Dict[str, Any]) -> str:
        """Generate a formatted metrics report"""
        report = []
        report.append("=" * 60)
        report.append(f"Performance Metrics Report - {metrics.get('mode', 'Unknown')}")
        report.append("=" * 60)
        
        if "latency" in metrics:
            report.append("\nLatency Statistics:")
            lat = metrics["latency"]
            report.append(f"  Mean: {lat['mean']:.2f} ms")
            report.append(f"  P50:  {lat['p50']:.2f} ms")
            report.append(f"  P95:  {lat['p95']:.2f} ms")
            report.append(f"  P99:  {lat['p99']:.2f} ms")
        
        if "throughput" in metrics:
            report.append(f"\nThroughput: {metrics['throughput']:.2f} msg/s")
        
        if "jitter" in metrics:
            report.append(f"Jitter: {metrics['jitter']:.2f} ms")
        
        if "packet_loss" in metrics:
            report.append(f"Packet Loss: {metrics['packet_loss']:.2f}%")
        
        if "security" in metrics:
            sec = metrics["security"]
            report.append("\nSecurity Metrics:")
            report.append(f"  Attacks Detected: {sec.get('detected', 0)}")
            report.append(f"  Attacks Blocked:  {sec.get('blocked', 0)}")
            report.append(f"  Detection Rate:   {sec.get('rate', 0):.2%}")
        
        report.append("=" * 60)
        return "\n".join(report)
