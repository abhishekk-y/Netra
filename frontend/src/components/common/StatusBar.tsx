import React, { useEffect } from 'react';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { formatBytes } from '../../utils/formatters';

export const StatusBar: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="h-8 bg-gray-900 border-b border-gray-800 flex items-center px-4 text-xs font-mono justify-between select-none">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${telemetry.sensorStatus === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-red-500'}`} />
          <span className="text-gray-300">SENSOR {telemetry.sensorStatus.toUpperCase()}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-gray-500">PKT/S:</span>
          <span className="text-blue-400 w-16 text-right">{telemetry.packetsPerSec.toLocaleString()}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500">FLW/S:</span>
          <span className="text-blue-400 w-12 text-right">{telemetry.flowsPerSec.toLocaleString()}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500">HOSTS:</span>
          <span className="text-gray-300">{telemetry.hostsCount}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-gray-500">CONNS:</span>
          <span className="text-gray-300">{telemetry.activeConnections}</span>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-gray-500">DROP:</span>
          <span className={`${telemetry.captureDropPercent > 5 ? 'text-red-500' : 'text-emerald-500'}`}>
            {telemetry.captureDropPercent.toFixed(2)}%
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500">CPU:</span>
          <span className="text-gray-300">{telemetry.cpuUsage}%</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500">RAM:</span>
          <span className="text-gray-300">{telemetry.ramUsage}%</span>
        </div>
      </div>
    </div>
  );
};
