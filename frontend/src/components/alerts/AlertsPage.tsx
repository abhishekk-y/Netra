import React, { useState } from 'react';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';

export const AlertsPage: React.FC = () => {
  const [search, setSearch] = useState('');

  const mockAlerts = [
    { id: 'ALT-1001', time: '10:14:22', severity: 'critical', source: 'Suricata', signature: 'ET EXPLOIT Possible CVE-2023-XXXX', src: '192.168.1.55', dst: '10.0.0.2' },
    { id: 'ALT-1002', time: '10:12:05', severity: 'high', source: 'ML Inference', signature: 'Anomalous Lateral Movement Model', src: '10.0.0.2', dst: '10.0.0.8' },
    { id: 'ALT-1003', time: '09:55:10', severity: 'medium', source: 'Zeek', signature: 'Excessive DNS Queries', src: '192.168.1.102', dst: '8.8.8.8' },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-950">
      <FilterBar placeholder="Search alerts..." onSearch={setSearch} />
      
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockAlerts}
          keyExtractor={a => a.id}
          columns={[
            { key: 'time', header: 'TIME', width: 'w-24', render: a => <span className="font-mono text-gray-400">{a.time}</span> },
            { key: 'severity', header: 'SEVERITY', width: 'w-24', render: a => <Badge variant={a.severity as any}>{a.severity}</Badge> },
            { key: 'source', header: 'SOURCE', width: 'w-32', render: a => <span className="text-gray-300">{a.source}</span> },
            { key: 'signature', header: 'SIGNATURE', render: a => <span className="font-medium text-gray-200">{a.signature}</span> },
            { key: 'src', header: 'SRC IP', width: 'w-32', render: a => <span className="font-mono text-blue-400">{a.src}</span> },
            { key: 'dst', header: 'DST IP', width: 'w-32', render: a => <span className="font-mono text-emerald-400">{a.dst}</span> },
          ]}
        />
      </div>
    </div>
  );
};

export default AlertsPage;
