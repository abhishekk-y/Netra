import React, { useState } from 'react';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';

export const AlertsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);

  const mockAlerts = [
    { id: 'ALT-1001', time: '10:14:22', severity: 'critical', source: 'Suricata', signature: 'ET EXPLOIT Possible CVE-2023-XXXX', src: '192.168.1.55', dst: '10.0.0.2', details: 'Detected multiple buffer overflow attempts directed at the internal domain controller. Immediate containment recommended.', mitre: 'T1190' },
    { id: 'ALT-1002', time: '10:12:05', severity: 'high', source: 'ML Inference', signature: 'Anomalous Lateral Movement Model', src: '10.0.0.2', dst: '10.0.0.8', details: 'Unusual RDP connection pattern observed between two internal workstations that do not typically communicate.', mitre: 'T1021' },
    { id: 'ALT-1003', time: '09:55:10', severity: 'medium', source: 'Zeek', signature: 'Excessive DNS Queries', src: '192.168.1.102', dst: '8.8.8.8', details: 'Client is generating an abnormal volume of TXT record queries, potentially indicating DNS tunneling.', mitre: 'T1071' },
  ];

  return (
    <div className="flex h-full p-6 bg-transparent gap-6">
      
      {/* MAIN TABLE AREA */}
      <div className={`flex flex-col flex-1 transition-all duration-300 ${selectedAlert ? 'max-w-[calc(100%-400px)]' : 'max-w-full'}`}>
        <div className="mb-4">
          <FilterBar placeholder="Search alerts..." onSearch={setSearch} />
        </div>
        
        <div className="flex-1 overflow-hidden">
          <DataTable
            data={mockAlerts}
            keyExtractor={a => a.id}
            onRowClick={(a) => setSelectedAlert(a)}
            selectedId={selectedAlert?.id}
            columns={[
              { key: 'time', header: 'TIME', width: 'w-24', render: a => <span className="font-mono text-slate-400">{a.time}</span> },
              { key: 'severity', header: 'SEVERITY', width: 'w-24', render: a => <Badge variant={a.severity as any}>{a.severity}</Badge> },
              { key: 'source', header: 'SOURCE', width: 'w-32', render: a => <span className="text-slate-500 font-semibold">{a.source}</span> },
              { key: 'signature', header: 'SIGNATURE', render: a => <span className="font-semibold text-slate-700">{a.signature}</span> },
              { key: 'src', header: 'SRC IP', width: 'w-32', render: a => <span className="font-mono font-medium text-indigo-500">{a.src}</span> },
              { key: 'dst', header: 'DST IP', width: 'w-32', render: a => <span className="font-mono font-medium text-emerald-500">{a.dst}</span> },
            ]}
          />
        </div>
      </div>

      {/* DETAIL SIDE PANEL */}
      {selectedAlert && (
        <div className="w-[380px] h-full bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-200/60 flex flex-col animate-in slide-in-from-right-8 duration-300">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h2 className="font-bold text-lg text-slate-800 tracking-tight">Alert Details</h2>
            <button onClick={() => setSelectedAlert(null)} className="text-slate-400 hover:text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-full w-8 h-8 flex items-center justify-center transition-colors">
              ✕
            </button>
          </div>
          <div className="p-6 space-y-6 overflow-y-auto">
            
            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Signature</div>
              <div className="font-semibold text-slate-800 text-lg leading-tight">{selectedAlert.signature}</div>
            </div>

            <div className="flex space-x-4">
              <div className="flex-1 bg-indigo-50/50 p-4 rounded-xl border border-indigo-100/50">
                <div className="text-xs font-bold text-indigo-400/80 uppercase tracking-widest mb-1">Source</div>
                <div className="font-mono font-semibold text-indigo-600">{selectedAlert.src}</div>
              </div>
              <div className="flex-1 bg-emerald-50/50 p-4 rounded-xl border border-emerald-100/50">
                <div className="text-xs font-bold text-emerald-400/80 uppercase tracking-widest mb-1">Destination</div>
                <div className="font-mono font-semibold text-emerald-600">{selectedAlert.dst}</div>
              </div>
            </div>

            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">AI Analysis & Context</div>
              <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                {selectedAlert.details}
              </p>
            </div>

            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">MITRE ATT&CK</div>
              <div className="inline-block px-3 py-1 bg-rose-50 text-rose-600 font-bold rounded-lg border border-rose-100 shadow-sm">
                {selectedAlert.mitre}
              </div>
            </div>

            <button className="w-full py-3 mt-4 bg-gradient-to-r from-indigo-600 to-[#00bceb] text-white font-bold rounded-xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300">
              Escalate to Incident
            </button>

          </div>
        </div>
      )}

    </div>
  );
};

export default AlertsPage;
