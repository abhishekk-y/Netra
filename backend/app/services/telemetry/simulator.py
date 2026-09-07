"""
Netra - Telemetry Simulator
Generates highly realistic ML telemetry data and pushes it over the WebSocket.
"""
import asyncio
import json
import random
from datetime import datetime, timezone

from app.websocket.manager import ws_manager

class TelemetrySimulator:
    def __init__(self):
        self.running = False
        self._task = None
        
        # State
        self.hosts = 245
        self.base_flows = 1200
        
    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())
        
    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            
    async def _loop(self):
        while self.running:
            # Simulate realistic jitter
            jitter = random.uniform(-0.1, 0.1)
            current_flows = int(self.base_flows * (1 + jitter))
            
            payload = {
                "hostsCount": self.hosts + random.randint(-2, 5),
                "flowsPerSec": current_flows,
                "packetsPerSec": current_flows * random.randint(12, 18),
                "activeConnections": current_flows * 5,
                "cpuUsage": random.uniform(15.0, 45.0),
                "ramUsage": random.uniform(40.0, 60.0),
                "sensorStatus": "online",
            }
            
            # Use raw message format for the telemetry store to pick up
            message = json.dumps({
                "type": "telemetry",
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Broadcast to everyone connected
            for client_id, ws in list(ws_manager._connections.items()):
                try:
                    await ws.send_text(message)
                except Exception:
                    pass
                    
            await asyncio.sleep(2.0)

simulator = TelemetrySimulator()
