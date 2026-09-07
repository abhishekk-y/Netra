import React from 'react';
import { Panel } from '../common/Panel';
import { Database, Cpu, Activity, HardDrive, Server, Globe, ShieldAlert } from 'lucide-react';
import { useTelemetryStore } from '../../stores/telemetryStore';

export const HealthPage: React.FC = () => {
  const telemetry = useTelemetryStore();
  const isOnline = telemetry.sensorStatus === 'online';

  const components = [
    { name: 'Capture Engine (Zeek)', icon: Activity, status: isOnline ? 'up' : 'down', metrics: 'Receiving packets' },
    { name: 'IDS Engine (Suricata)', icon: ShieldAlert, status: isOnline ? 'up' : 'down', metrics: 'Signatures loaded' },
    { name: 'ML Inference Engine', icon: Cpu, status: 'up', metrics: 'Model: v2.4 (Latency: 12ms)' },
    { name: 'Timeseries Database', icon: Database, status: 'up', metrics: 'Size: 45GB' },
    { name: 'Graph Database', icon: Globe, status: 'up', metrics: 'Nodes: 124, Edges: 890' },
    { name: 'Message Broker', icon: Server, status: 'up', metrics: 'Queue: 0' },
  ];

  return (
    <div className="p-4 bg-transparent h-full overflow-auto custom-scrollbar">
      <h1 className="text-xl font-bold text-gray-100 mb-6">System Health</h1>
      
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Panel title="CPU Usage">
           <div className="flex flex-col items-center justify-center py-6">
             <div className="text-4xl font-mono text-emerald-500 mb-2">{telemetry.cpuUsage}%</div>
             <div className="w-full bg-gray-900 h-2 rounded mt-2">
               <div className="bg-emerald-500 h-full rounded" style={{ width: `${telemetry.cpuUsage}%` }} />
             </div>
           </div>
        </Panel>
        <Panel title="Memory Usage">
           <div className="flex flex-col items-center justify-center py-6">
             <div className="text-4xl font-mono text-blue-500 mb-2">{telemetry.ramUsage}%</div>
             <div className="w-full bg-gray-900 h-2 rounded mt-2">
               <div className="bg-blue-500 h-full rounded" style={{ width: `${telemetry.ramUsage}%` }} />
             </div>
           </div>
        </Panel>
        <Panel title="Packet Drop Rate">
           <div className="flex flex-col items-center justify-center py-6">
             <div className={`text-4xl font-mono mb-2 ${telemetry.captureDropPercent > 5 ? 'text-red-500' : 'text-emerald-500'}`}>
               {telemetry.captureDropPercent.toFixed(2)}%
             </div>
             <div className="text-gray-500 text-sm mt-2">Threshold: 5.00%</div>
           </div>
        </Panel>
      </div>

      <h2 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">Component Status</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {components.map(c => (
          <div key={c.name} className="bg-gray-900 border border-gray-800 p-4 rounded flex items-start gap-4">
            <div className={`p-2 rounded bg-gray-950 border ${c.status === 'up' ? 'border-emerald-500/30' : 'border-red-500/30'}`}>
              <c.icon size={24} className={c.status === 'up' ? 'text-emerald-500' : 'text-red-500'} />
            </div>
            <div>
              <div className="font-bold text-gray-200">{c.name}</div>
              <div className="text-sm text-gray-500 mt-1">{c.metrics}</div>
              <div className="mt-2 flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-full ${c.status === 'up' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                <span className="text-xs font-mono uppercase text-gray-400">{c.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HealthPage;
