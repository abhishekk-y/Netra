import React, { useState } from 'react';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { formatIP, formatBytes, formatDuration } from '../../utils/formatters';

export const FlowsPage: React.FC = () => {
  const [search, setSearch] = useState('');

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
    <div className="flex flex-col h-full p-4 bg-transparent">
      <FilterBar placeholder="Filter flows (e.g. ip.src == 192.168.1.1)..." onSearch={setSearch} />
      
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockFlows}
          keyExtractor={f => f.id}
          columns={[
            { key: 'timestamp', header: 'TIME', width: 'w-40', render: f => <span className="text-gray-400">{new Date(f.timestamp).toLocaleTimeString()}</span> },
            { key: 'srcIp', header: 'SRC IP', width: 'w-32', render: f => <span className="font-mono text-blue-400">{formatIP(f.srcIp)}</span> },
            { key: 'srcPort', header: 'SPORT', width: 'w-20', render: f => <span className="font-mono">{f.srcPort}</span> },
            { key: 'dstIp', header: 'DST IP', width: 'w-32', render: f => <span className="font-mono text-emerald-400">{formatIP(f.dstIp)}</span> },
            { key: 'dstPort', header: 'DPORT', width: 'w-20', render: f => <span className="font-mono">{f.dstPort}</span> },
            { key: 'protocol', header: 'PROTO', width: 'w-20' },
            { key: 'appProtocol', header: 'APP', width: 'w-24' },
            { key: 'packets', header: 'PACKETS', width: 'w-24', align: 'right' },
            { key: 'bytes', header: 'BYTES', width: 'w-24', align: 'right', render: f => formatBytes(f.bytes) },
            { key: 'duration', header: 'DUR', width: 'w-24', align: 'right', render: f => formatDuration(f.duration) },
            { key: 'risk', header: 'RISK', width: 'w-20', align: 'right', render: f => (
              <span className={`font-mono font-bold ${f.risk > 80 ? 'text-red-500' : f.risk > 50 ? 'text-orange-500' : 'text-emerald-500'}`}>
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
