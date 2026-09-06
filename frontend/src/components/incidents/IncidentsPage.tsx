import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';

export const IncidentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  const mockIncidents = [
    { id: 'INC-001', title: 'Ransomware precursor behavior on segment A', status: 'investigating', severity: 'critical', stage: 'Lateral Movement', hosts: 3, created: '2023-10-01 14:32:00', updated: '2 mins ago' },
    { id: 'INC-002', title: 'Anomalous outbound transfer to external IP', status: 'active', severity: 'high', stage: 'Exfiltration', hosts: 1, created: '2023-10-01 10:15:00', updated: '1 hr ago' },
    { id: 'INC-003', title: 'Failed SSH brute force campaign', status: 'mitigated', severity: 'medium', stage: 'Reconnaissance', hosts: 5, created: '2023-09-30 08:22:00', updated: '1 day ago' },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-950">
      <FilterBar placeholder="Search incidents by ID, title, or host..." onSearch={setSearch} />
      
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockIncidents}
          keyExtractor={i => i.id}
          onRowClick={(i) => navigate(`/incidents/${i.id}`)}
          columns={[
            { key: 'id', header: 'ID', width: 'w-24', render: i => <span className="font-mono text-emerald-400 font-bold">{i.id}</span> },
            { key: 'title', header: 'TITLE', render: i => <span className="font-medium text-gray-200">{i.title}</span> },
            { key: 'status', header: 'STATUS', width: 'w-32', render: i => (
                <span className={`uppercase text-xs font-mono ${i.status === 'active' ? 'text-red-400' : i.status === 'investigating' ? 'text-orange-400' : 'text-gray-500'}`}>
                  {i.status}
                </span>
            )},
            { key: 'severity', header: 'SEVERITY', width: 'w-28', render: i => <Badge variant={i.severity as any}>{i.severity}</Badge> },
            { key: 'stage', header: 'ATTACK STAGE', width: 'w-48' },
            { key: 'hosts', header: 'HOSTS', width: 'w-20', align: 'center' },
            { key: 'created', header: 'CREATED', width: 'w-40', render: i => <span className="font-mono text-gray-400">{i.created}</span> },
            { key: 'updated', header: 'UPDATED', width: 'w-32', align: 'right', render: i => <span className="text-gray-500">{i.updated}</span> },
          ]}
        />
      </div>
    </div>
  );
};

export default IncidentsPage;
