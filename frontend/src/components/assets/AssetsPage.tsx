import React, { useState } from 'react';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';

export const AssetsPage: React.FC = () => {
  const [search, setSearch] = useState('');

  const mockAssets = [
    { ip: '10.0.0.5', name: 'DB-PROD-01', type: 'Server', vendor: 'Dell', os: 'Linux', crit: 'high', vlan: 100, status: 'Known', last: '2 mins ago' },
    { ip: '10.0.0.8', name: 'FILE-SERVER', type: 'Server', vendor: 'HP', os: 'Windows', crit: 'medium', vlan: 100, status: 'Known', last: '5 mins ago' },
    { ip: '192.168.1.45', name: 'USER-DESKTOP-1', type: 'Workstation', vendor: 'Lenovo', os: 'Windows 11', crit: 'low', vlan: 200, status: 'Known', last: '1 min ago' },
    { ip: '192.168.1.199', name: 'UNKNOWN-DEV', type: 'IoT', vendor: 'Unknown', os: 'Unknown', crit: 'low', vlan: 200, status: 'New', last: 'Just now' },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-950">
      <FilterBar placeholder="Search assets..." onSearch={setSearch} />
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockAssets}
          keyExtractor={a => a.ip}
          columns={[
            { key: 'ip', header: 'IP ADDRESS', width: 'w-32', render: a => <span className="font-mono text-blue-400">{a.ip}</span> },
            { key: 'name', header: 'HOSTNAME' },
            { key: 'type', header: 'TYPE', width: 'w-32' },
            { key: 'vendor', header: 'VENDOR', width: 'w-32' },
            { key: 'os', header: 'OS', width: 'w-32' },
            { key: 'crit', header: 'CRITICALITY', width: 'w-32', render: a => <Badge variant={a.crit === 'high' ? 'critical' : a.crit === 'medium' ? 'warning' : 'info'}>{a.crit}</Badge> },
            { key: 'vlan', header: 'VLAN', width: 'w-24', render: a => <span className="font-mono text-gray-400">{a.vlan}</span> },
            { key: 'status', header: 'STATUS', width: 'w-32', render: a => <Badge variant={a.status === 'New' ? 'warning' : 'default'}>{a.status}</Badge> },
            { key: 'last', header: 'LAST SEEN', width: 'w-32', align: 'right', render: a => <span className="text-gray-500">{a.last}</span> },
          ]}
        />
      </div>
    </div>
  );
};

export default AssetsPage;
