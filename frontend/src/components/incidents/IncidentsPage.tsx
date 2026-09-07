import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';

import { useUIStore } from '../../stores/uiStore';

export const IncidentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const mockIncidents = [
    { id: 'INC-001', title: 'Ransomware precursor behavior on segment A', status: 'investigating', severity: 'critical', stage: 'Lateral Movement', hosts: 3, created: '2023-10-01 14:32:00', updated: '2 mins ago' },
    { id: 'INC-002', title: 'Anomalous outbound transfer to external IP', status: 'active', severity: 'high', stage: 'Exfiltration', hosts: 1, created: '2023-10-01 10:15:00', updated: '1 hr ago' },
    { id: 'INC-003', title: 'Failed SSH brute force campaign', status: 'mitigated', severity: 'medium', stage: 'Reconnaissance', hosts: 5, created: '2023-09-30 08:22:00', updated: '1 day ago' },
  ];

  return (
    <div className="flex flex-col h-full bg-transparent p-6 gap-6">
      <div className="shrink-0">
        <FilterBar placeholder="Search incidents by ID, title, or host..." onSearch={setSearch} />
      </div>
      
      <div className="flex-1 overflow-hidden">
        <DataTable
          data={mockIncidents}
          keyExtractor={i => i.id}
          onRowClick={(i) => navigate(`/incidents/${i.id}`)}
          columns={[
            { key: 'id', header: 'ID', width: 'w-24', render: i => <span className={`font-mono font-bold ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>{i.id}</span> },
            { key: 'title', header: 'TITLE', render: i => <span className={`font-semibold ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>{i.title}</span> },
            { key: 'status', header: 'STATUS', width: 'w-32', render: i => (
                <span className={`uppercase text-[10px] tracking-widest font-bold px-2 py-1 rounded-md ${
                  i.status === 'active' 
                    ? (isDark ? 'bg-red-500/20 text-red-400' : 'bg-red-100 text-red-600') 
                    : i.status === 'investigating' 
                      ? (isDark ? 'bg-orange-500/20 text-orange-400' : 'bg-orange-100 text-orange-600') 
                      : (isDark ? 'bg-gray-800 text-gray-400' : 'bg-slate-100 text-slate-500')
                }`}>
                  {i.status}
                </span>
            )},
            { key: 'severity', header: 'SEVERITY', width: 'w-28', render: i => <Badge variant={i.severity as any}>{i.severity}</Badge> },
            { key: 'stage', header: 'ATTACK STAGE', width: 'w-48', render: i => <span className={`font-medium ${isDark ? 'text-gray-400' : 'text-slate-600'}`}>{i.stage}</span> },
            { key: 'hosts', header: 'HOSTS', width: 'w-20', align: 'center', render: i => <span className={`font-bold ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>{i.hosts}</span> },
            { key: 'created', header: 'CREATED', width: 'w-40', render: i => <span className={`font-mono text-xs ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>{i.created}</span> },
            { key: 'updated', header: 'UPDATED', width: 'w-32', align: 'right', render: i => <span className={`text-xs font-medium ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>{i.updated}</span> },
          ]}
        />
      </div>
    </div>
  );
};

export default IncidentsPage;
