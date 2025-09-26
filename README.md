# CAN-Ethernet-Gateway-Simulation
Simulation framework for a secure hybrid automotive gateway (CAN, CAN FD, Automotive Ethernet) with attack scenarios and intrusion detection.
# Secure Hybrid Gateway for Automotive Networks  
A Python/Scapy-based simulation framework for designing and evaluating a **secure hybrid gateway** between **CAN**, **CAN FD**, and **Automotive Ethernet** networks.  
This project was developed as part of an MSc research dissertation to study **performance–security trade-offs** in connected vehicle communication.

---

## 🚗 Overview
Modern vehicles use a mix of legacy **CAN/CAN FD** and high-bandwidth **Automotive Ethernet** protocols.  
While this enables advanced features (ADAS, infotainment, OTA updates), it also introduces serious **cybersecurity risks** such as:
- **Replay attacks**
- **Spoofing**
- **Denial of Service (DoS)**

This project:
1. **Designs** a secure hybrid gateway architecture.
2. **Simulates** real automotive traffic and multiple attack scenarios.
3. **Implements** security features (HMAC authentication, packet filtering, Intrusion Detection System).
4. **Measures** key performance metrics (latency, throughput, jitter, packet loss) to evaluate security vs. real-time performance.

---

## 🛠 Features
- **Multi-threaded traffic generation** of 10,000+ messages across CAN and Ethernet buses.
- **Attack simulation** modules: replay, spoofing, DoS, and combined attacks.
- **Secure gateway** implementation with:
  - HMAC-based authentication
  - Payload filtering
  - Rate-based Intrusion Detection System (IDS)
- **Metrics engine** for latency percentiles (P50/P95/P99), throughput, jitter, and security effectiveness.
- **Modular architecture** for easy extension and experimentation.

---

## 📂 Repository Structure
├── attacks.py # Multi-threaded attack simulator
├── can_bus.py # Thread-safe CAN bus implementation
├── ethernet_bus.py # Thread-safe Ethernet bus implementation
├── gateway.py # Protocol translator (CAN <-> Ethernet)
├── scenarios.py # Baseline, Attack, and Secure experiment scenarios
├── security.py # HMAC authentication & IDS logic
├── metrics.py # Latency/throughput/jitter/packet-loss calculations
├── utils.py # Helper utilities (timestamps, ID generation, CSV export)
└── README.md




## ⚡️Quick Start
> **Requirements**: Python 3.9+
>
> # Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

python -m script/run_baseline.py
python -m script/run_attack.py
python -m script/run_secure.py
python -m script/run_comparison.py
