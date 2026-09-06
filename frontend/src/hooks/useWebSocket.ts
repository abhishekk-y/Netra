import { useEffect } from 'react';
import { wsService } from '../stores/telemetryStore';

export function useWebSocket(channels: string[] = []) {
  useEffect(() => {
    // In a real implementation, you might send subscription messages here
    // For now, wsService connects on app load and receives all telemetry
    wsService.connect();
    
    return () => {
      // Cleanup if needed
    };
  }, [channels]);
}
