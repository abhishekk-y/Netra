"""
Netra - Telemetry Simulator
Generates highly realistic ML telemetry data and pushes it over the WebSocket.
Now fully connected to a trained AI model for real inference.
"""
import asyncio
import json
import random
import os
import joblib
import pandas as pd
from datetime import datetime, timezone

from app.websocket.manager import ws_manager

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "nx_tfr_ensemble.pkl")
_clf = None
_le_proto = None
_features = None

def load_ai_model():
    global _clf, _le_proto, _features
    try:
        bundle = joblib.load(MODEL_PATH)
        _clf = bundle['model']
        _le_proto = bundle['proto_encoder']
        _features = bundle['features']
        print("[+] TelemetrySimulator: AI Model nx_tfr_v4 loaded successfully.")
    except Exception as e:
        print(f"[-] TelemetrySimulator: Failed to load AI Model: {e}")

class TelemetrySimulator:
    def __init__(self):
        self.running = False
        self._task = None
        self.hosts = 245
        self.base_flows = 1200
        load_ai_model()
        
    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())
        
    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            
    async def _loop(self):
        while self.running:
            jitter = random.uniform(-0.1, 0.1)
            current_flows = int(self.base_flows * (1 + jitter))
            is_attack_sim = random.random() > 0.85
            
            payload = {
                "hostsCount": self.hosts + random.randint(-2, 5),
                "flowsPerSec": current_flows,
                "packetsPerSec": current_flows * random.randint(12, 18),
                "activeConnections": current_flows * 5,
                "cpuUsage": random.uniform(80.0, 95.0) if is_attack_sim else random.uniform(15.0, 45.0),
                "ramUsage": random.uniform(70.0, 90.0) if is_attack_sim else random.uniform(40.0, 60.0),
                "netIo": random.uniform(40000, 95000),
                "diskLatency": random.uniform(2.0, 15.0),
                "sensorStatus": "online",
            }
            
            # Generate features for real inference
            proto = random.choice(["tcp", "udp", "icmp"])
            duration = 0 if not is_attack_sim else random.randint(0, 1000)
            src_bytes = random.randint(0, 500) if not is_attack_sim else random.randint(1000, 50000)
            dst_bytes = random.randint(0, 1000)
            count = random.randint(1, 10) if not is_attack_sim else random.randint(100, 500)
            srv_count = random.randint(1, 10) if not is_attack_sim else random.randint(100, 500)
            
            risk_score = 0
            is_anomaly = False
            
            # RUN REAL AI INFERENCE
            if _clf is not None:
                try:
                    proto_enc = _le_proto.transform([proto])[0]
                    # Match features exactly: ['duration', 'protocol_type', 'src_bytes', 'dst_bytes', 'count', 'srv_count']
                    x_input = pd.DataFrame([[duration, proto_enc, src_bytes, dst_bytes, count, srv_count]], columns=_features)
                    
                    # Predict probability of attack (class 1)
                    probs = _clf.predict_proba(x_input)[0]
                    risk_score = float(probs[1] * 100.0)
                    is_anomaly = risk_score > 75.0
                except Exception as e:
                    print(f"Inference error: {e}")
            
            # Generate a deep packet for DPI using the REAL AI risk score
            srcIp = f"10.0.{random.randint(0,255)}.{random.randint(0,255)}"
            dstIp = f"192.168.1.{random.randint(0,255)}"
            
            packet_event = {
                "id": f"PKT_{random.randint(10000, 99999)}",
                "time": datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
                "src": srcIp,
                "dst": dstIp,
                "proto": proto.upper(),
                "len": src_bytes,
                "flags": "[SYN, ECE, CWR]" if is_anomaly else "[PSH, ACK]",
                "risk": risk_score,
                "status": "DROP" if is_anomaly else "PASS",
                "sig": "AI_INFERENCE_ANOMALY" if is_anomaly else "-",
                "hex": [f"{random.randint(0, 255):02X}" for _ in range(min(64, max(16, src_bytes)))]
            }
            
            # Generate a Honeypot event
            actions = [
                {"action": 'SSH_AUTH_FAIL (root/admin)', "type": 'SCANNER'},
                {"action": 'TCP_PORT_SCAN (NMAP)', "type": 'SCANNER'},
                {"action": 'DROPPED_PAYLOAD (mirai.x86)', "type": 'MALWARE'},
                {"action": 'RDP_BRUTEFORCE', "type": 'HUMAN'}
            ]
            act = random.choice(actions)
            honeypot_event = {
                "t": datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
                "src": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "target": f"10.0.99.{random.randint(1,50)}",
                "action": act["action"],
                "type": act["type"]
            }
            
            # Generate Topology update (a random node gets a risk spike)
            topology_event = {
                "nodeId": f"edge-{random.randint(0, 59)}",
                "newRisk": risk_score
            }
            
            message = json.dumps({
                "type": "telemetry",
                "payload": payload,
                "packet": packet_event,
                "honeypot": honeypot_event,
                "topology": topology_event,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            for client_id, ws in list(ws_manager._connections.items()):
                try:
                    await ws.send_text(message)
                except Exception:
                    pass
                    
            await asyncio.sleep(0.5)

simulator = TelemetrySimulator()
