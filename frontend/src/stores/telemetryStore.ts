import { create } from 'zustand';

interface TelemetryState {
  packetsPerSec: number;
  flowsPerSec: number;
  hostsCount: number;
  activeConnections: number;
  sensorStatus: 'online' | 'offline' | 'degraded';
  captureDropPercent: number;
  cpuUsage: number;
  ramUsage: number;
  netIo: number;
  diskLatency: number;
  
  // New backend real-time event streams
  packets: any[];
  honeypotEvents: any[];
  topologyUpdates: any[];
  
  updateTelemetry: (data: Partial<TelemetryState>) => void;
  addPacket: (pkt: any) => void;
  addHoneypotEvent: (evt: any) => void;
  addTopologyUpdate: (upd: any) => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  packetsPerSec: 0,
  flowsPerSec: 0,
  hostsCount: 0,
  activeConnections: 0,
  sensorStatus: 'offline',
  captureDropPercent: 0,
  cpuUsage: 0,
  ramUsage: 0,
  netIo: 0,
  diskLatency: 0,
  
  packets: [],
  honeypotEvents: [],
  topologyUpdates: [],
  
  updateTelemetry: (data) => set((state) => ({ ...state, ...data })),
  
  addPacket: (pkt) => set((state) => {
    const next = [pkt, ...state.packets];
    if (next.length > 50) next.pop();
    return { packets: next };
  }),
  
  addHoneypotEvent: (evt) => set((state) => {
    const next = [evt, ...state.honeypotEvents];
    if (next.length > 30) next.pop();
    return { honeypotEvents: next };
  }),
  
  addTopologyUpdate: (upd) => set((state) => {
    const next = [upd, ...state.topologyUpdates];
    if (next.length > 20) next.pop();
    return { topologyUpdates: next };
  })
}));

// WebSocket Service
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private url = `ws://localhost:8000/ws`;
  private backoff = 1000;

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log('WS Connected');
      this.backoff = 1000;
      useTelemetryStore.getState().updateTelemetry({ sensorStatus: 'online' });
    };
    
    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const type = msg.type || msg.channel;
        
        if (type === 'telemetry' || type === 'telemetry_update') {
          if (msg.payload) useTelemetryStore.getState().updateTelemetry(msg.payload);
          if (msg.packet) useTelemetryStore.getState().addPacket(msg.packet);
          if (msg.honeypot) useTelemetryStore.getState().addHoneypotEvent(msg.honeypot);
          if (msg.topology) useTelemetryStore.getState().addTopologyUpdate(msg.topology);
        }
      } catch (err) {
        console.error('WS Parse Error', err);
      }
    };
    
    this.ws.onclose = () => {
      useTelemetryStore.getState().updateTelemetry({ sensorStatus: 'offline' });
      this.reconnect();
    };
    
    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  private reconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = window.setTimeout(() => {
      this.backoff = Math.min(this.backoff * 2, 30000);
      this.connect();
    }, this.backoff);
  }
}

export const wsService = new WebSocketService();
