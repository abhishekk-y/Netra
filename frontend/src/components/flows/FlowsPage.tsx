import React, { useState } from 'react';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { formatIP, formatBytes, formatDuration } from '../../utils/formatters';

import { useUIStore } from '../../stores/uiStore';

export const FlowsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const mockFlows = Array.from({ length: 50 }).map((_, i) => ({
    id: `flw-${i}`,
    timestamp: new Date(Date.now() - i * 10000).toISOString(),
    srcIp: `192.168.1.${Math.floor(Math.random() * 255)}`,
    srcPort: Math.floor(Math.random() * 60000) + 1024,
    dstIp: `10.0.0.${Math.floor(Math.random() * 255)}`,
    dstPort: [80, 443, 22, 3389, 53][Math.floor(Math.random() * 5)],
    protocol: Math.random() > 0.3 ? 'TCP' : 'UDP',
    appProtocol: Math.random() > 0.5 ? 'HTTP' : 'TLS',
    packets: Math.floor(Math.random() * 1000) + 1,
    bytes: Math.floor(Math.random() * 500000) + 64,
    duration: Math.floor(Math.random() * 5000) + 10,
    risk: Math.random() * 100
  }));

  return (
    <div className="flex flex-col h-full p-6 bg-transparent gap-6">
      <div className="shrink-0">
        <FilterBar placeholder="Filter flows (e.g. ip.src == 192.168.1.1)..." onSearch={setSearch} />
      </div>
      
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockFlows}
          keyExtractor={f => f.id}
          columns={[
            { key: 'timestamp', header: 'TIME', width: 'w-40', render: f => <span className={`font-mono text-xs ${isDark ? 'text-[#888]' : 'text-slate-400'}`}>{new Date(f.timestamp).toLocaleTimeString()}</span> },
            { key: 'srcIp', header: 'SRC IP', width: 'w-32', render: f => <span className={`font-mono font-medium ${isDark ? 'text-indigo-400' : 'text-indigo-600'}`}>{formatIP(f.srcIp)}</span> },
            { key: 'srcPort', header: 'SPORT', width: 'w-20', render: f => <span className={`font-mono ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>{f.srcPort}</span> },
            { key: 'dstIp', header: 'DST IP', width: 'w-32', render: f => <span className={`font-mono font-medium ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>{formatIP(f.dstIp)}</span> },
            { key: 'dstPort', header: 'DPORT', width: 'w-20', render: f => <span className={`font-mono ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>{f.dstPort}</span> },
            { key: 'protocol', header: 'PROTO', width: 'w-20', render: f => <span className={`font-bold text-[11px] px-2 py-1 rounded ${isDark ? 'bg-[#222] text-gray-300' : 'bg-slate-100 text-slate-600'}`}>{f.protocol}</span> },
            { key: 'appProtocol', header: 'APP', width: 'w-24', render: f => <span className={`font-bold text-[11px] px-2 py-1 rounded ${isDark ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>{f.appProtocol}</span> },
            { key: 'packets', header: 'PACKETS', width: 'w-24', align: 'right', render: f => <span className={`font-mono ${isDark ? 'text-gray-300' : 'text-slate-600'}`}>{f.packets}</span> },
            { key: 'bytes', header: 'BYTES', width: 'w-24', align: 'right', render: f => <span className={`font-mono ${isDark ? 'text-gray-300' : 'text-slate-600'}`}>{formatBytes(f.bytes)}</span> },
            { key: 'duration', header: 'DUR', width: 'w-24', align: 'right', render: f => <span className={`font-mono ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>{formatDuration(f.duration)}</span> },
            { key: 'risk', header: 'RISK', width: 'w-20', align: 'right', render: f => (
              <span className={`font-mono font-bold ${f.risk > 80 ? (isDark ? 'text-red-400' : 'text-red-600') : f.risk > 50 ? (isDark ? 'text-orange-400' : 'text-orange-500') : (isDark ? 'text-emerald-500' : 'text-emerald-500')}`}>
                {f.risk.toFixed(1)}
              </span>
            )},
          ]}
        />
      </div>
    </div>
  );
};

export default FlowsPage;
