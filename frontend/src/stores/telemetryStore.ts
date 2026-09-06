import { create } from 'zustand';
import type { WSMessage } from '../types';

interface TelemetryState {
  packetsPerSec: number;
  flowsPerSec: number;
  hostsCount: number;
  activeConnections: number;
  sensorStatus: 'online' | 'offline' | 'degraded';
  captureDropPercent: number;
  cpuUsage: number;
  ramUsage: number;
  diskUsage: number;
  updateTelemetry: (data: Partial<TelemetryState>) => void;
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
  diskUsage: 0,
  updateTelemetry: (data) => set((state) => ({ ...state, ...data })),
}));

// WebSocket Service
class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private url = `ws://${window.location.host}/ws`;
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
        const msg: WSMessage = JSON.parse(event.data);
        if (msg.type === 'telemetry') {
          useTelemetryStore.getState().updateTelemetry(msg.payload);
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
// Typically you'd call wsService.connect() in App or layout mount
