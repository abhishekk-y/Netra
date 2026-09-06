import React from 'react';
import { X, Server, Activity, AlertTriangle, Shield, Clock, Crosshair } from 'lucide-react';
import { useTopologyStore } from '../../stores/topologyStore';
import { Badge } from '../common/Badge';
import { RiskIndicator } from '../common/RiskIndicator';
import { Panel } from '../common/Panel';

export const NodeDetail: React.FC = () => {
  const { selectedNodeId, setSelectedNode, nodes } = useTopologyStore();
  
  if (!selectedNodeId) return null;

  const node = nodes.find(n => n.data.id === selectedNodeId);
  if (!node) return null;

  // Mock detail data based on node
  const mockDetail = {
    ip: '192.168.1.45',
    mac: '00:1A:2B:3C:4D:5E',
    os: 'Windows Server 2022',
    firstSeen: '2023-10-01 08:00:00',
    lastSeen: 'Just now',
    openPorts: [80, 443, 3389, 445],
    activeAlerts: [
      { id: 'ALT-101', name: 'Suspicious RDP Brute Force', severity: 'high' },
      { id: 'ALT-102', name: 'SMB Enumeration', severity: 'medium' }
    ]
  };

  return (
    <div className="w-80 bg-gray-900 border-l border-gray-800 flex flex-col h-full overflow-hidden shrink-0">
      <div className="h-12 border-b border-gray-800 flex items-center justify-between px-4 bg-gray-950/50">
        <div className="flex items-center gap-2 overflow-hidden">
          <Server size={16} className="text-gray-400 shrink-0" />
          <h2 className="text-sm font-bold text-gray-100 truncate">{node.data.label}</h2>
        </div>
        <button onClick={() => setSelectedNode(null)} className="text-gray-500 hover:text-gray-300">
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-4">
        
        <Panel title="Identity" className="bg-gray-950">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between"><span className="text-gray-500">IP</span><span className="font-mono text-blue-400">{mockDetail.ip}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">MAC</span><span className="font-mono">{mockDetail.mac}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">TYPE</span><span className="uppercase">{node.data.type}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">OS</span><span>{mockDetail.os}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">LAST SEEN</span><span>{mockDetail.lastSeen}</span></div>
          </div>
        </Panel>

        <Panel title="Security Posture" className="bg-gray-950">
          <div className="space-y-4 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-gray-500">RISK SCORE</span>
              <RiskIndicator score={node.data.risk} />
            </div>
            {node.data.isAttacked && (
              <div className="bg-red-500/10 border border-red-500/20 p-2 rounded flex items-start gap-2">
                <AlertTriangle size={14} className="text-red-500 shrink-0 mt-0.5" />
                <div>
                  <div className="text-red-400 font-bold">COMPROMISED</div>
                  <div className="text-gray-400 mt-1">Active lateral movement detected from 10.0.0.5</div>
                </div>
              </div>
            )}
            {node.data.isForecast && (
              <div className="bg-orange-500/10 border border-orange-500/20 p-2 rounded flex items-start gap-2">
                <Crosshair size={14} className="text-orange-500 shrink-0 mt-0.5" />
                <div>
                  <div className="text-orange-400 font-bold">HIGH PROBABILITY TARGET</div>
                  <div className="text-gray-400 mt-1">Forecasted next step in attack path (82%)</div>
                </div>
              </div>
            )}
          </div>
        </Panel>

        <Panel title="Services" className="bg-gray-950">
          <div className="flex flex-wrap gap-2">
            {mockDetail.openPorts.map(port => (
              <Badge key={port} variant="info">PORT {port}</Badge>
            ))}
          </div>
        </Panel>

        <Panel title="Active Alerts" className="bg-gray-950">
          <div className="space-y-2">
            {mockDetail.activeAlerts.map(alert => (
              <div key={alert.id} className="border border-gray-800 p-2 rounded text-xs bg-gray-900/50">
                <div className="flex justify-between mb-1">
                  <span className="font-mono text-gray-500">{alert.id}</span>
                  <Badge variant={alert.severity as any}>{alert.severity}</Badge>
                </div>
                <div className="text-gray-300">{alert.name}</div>
              </div>
            ))}
            {mockDetail.activeAlerts.length === 0 && (
              <div className="text-center text-gray-500 py-2">NO ALERTS</div>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
};
