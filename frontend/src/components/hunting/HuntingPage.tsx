import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useUIStore } from '../../stores/uiStore';
import {
  Search, Crosshair, Filter, Clock, Database,
  ArrowRight, ChevronDown, Save, Play, X,
  Activity, Shield, AlertTriangle
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1';

const demoFlows = [
  { id: 'f1', srcIp: '10.42.0.10', dstIp: '10.42.0.20', srcPort: 49231, dstPort: 445, protocol: 'TCP', appProtocol: 'SMB', bytes: 95000, packets: 200, duration: 10, riskScore: 78, attackType: 'Lateral Movement', timestamp: new Date().toISOString() },
  { id: 'f2', srcIp: '10.42.0.10', dstIp: '8.8.8.8', srcPort: 52000, dstPort: 443, protocol: 'TCP', appProtocol: 'TLS', bytes: 8000000, packets: 200, duration: 10, riskScore: 92, attackType: 'Exfiltration', timestamp: new Date(Date.now()-60000).toISOString() },
  { id: 'f3', srcIp: '10.42.0.10', dstIp: '10.42.0.20', srcPort: 40001, dstPort: 22, protocol: 'TCP', appProtocol: 'SSH', bytes: 5000, packets: 30, duration: 3, riskScore: 45, attackType: 'Reconnaissance', timestamp: new Date(Date.now()-120000).toISOString() },
  { id: 'f4', srcIp: '10.42.0.12', dstIp: '1.1.1.1', srcPort: 41002, dstPort: 53, protocol: 'UDP', appProtocol: 'DNS', bytes: 12000, packets: 42, duration: 5, riskScore: 10, attackType: null, timestamp: new Date(Date.now()-180000).toISOString() },
  { id: 'f5', srcIp: '192.168.1.45', dstIp: '10.42.0.20', srcPort: 54321, dstPort: 80, protocol: 'TCP', appProtocol: 'HTTP', bytes: 24000, packets: 88, duration: 8, riskScore: 30, attackType: null, timestamp: new Date(Date.now()-240000).toISOString() },
];

const savedHunts = [
  { id: 'h1', name: 'High Risk Flows', query: 'riskScore > 70' },
  { id: 'h2', name: 'External Exfil', query: 'bytes > 1000000' },
  { id: 'h3', name: 'SMB Lateral', query: 'dstPort == 445' },
  { id: 'h4', name: 'Brute Force SSH', query: 'dstPort == 22' },
];

function formatBytes(b: number): string {
  if (b >= 1e9) return `${(b/1e9).toFixed(1)} GB`;
  if (b >= 1e6) return `${(b/1e6).toFixed(1)} MB`;
  if (b >= 1e3) return `${(b/1e3).toFixed(1)} KB`;
  return `${b} B`;
}

function timeAgo(ts: string): string {
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  return `${Math.floor(diff/3600)}h ago`;
}

const HuntingPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';
  const [query, setQuery] = useState('');
  const [executedQuery, setExecutedQuery] = useState('');
  const [selected, setSelected] = useState<any>(null);
  const [showSaved, setShowSaved] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['hunt', executedQuery],
    queryFn: async () => {
      if (!executedQuery) return { data: demoFlows, total: demoFlows.length, facets: {} };
      const res = await fetch(`${API}/hunt?q=${encodeURIComponent(executedQuery)}`);
      if (!res.ok) throw new Error('fail');
      return res.json();
    },
    initialData: { data: demoFlows, total: demoFlows.length, facets: { TCP: 4, UDP: 1 } },
  });

  const flows = data?.data ?? demoFlows;
  const facets = data?.facets ?? {};

  const execute = () => setExecutedQuery(query);

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in">

      {/* HEADER */}
      <div className="flex items-center space-x-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          isDark ? 'bg-cyan-500/10 border border-cyan-500/20' : 'bg-cyan-50'
        }`}>
          <Crosshair size={20} className={isDark ? 'text-cyan-400' : 'text-cyan-600'} />
        </div>
        <div>
          <h1 className={`text-xl font-bold ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>Threat Hunter</h1>
          <p className={`text-xs ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>Query flow telemetry using field expressions</p>
        </div>
      </div>

      {/* QUERY BAR */}
      <div className={`rounded-2xl border p-4 space-y-3 ${
        isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
      }`}>
        <div className="flex space-x-3">
          <div className="relative flex-1">
            <Search size={14} className={`absolute left-4 top-1/2 -translate-y-1/2 ${
              isDark ? 'text-slate-600' : 'text-slate-400'
            }`} />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && execute()}
              placeholder="e.g.  riskScore > 70  or  srcIp == '10.42.0.10' and dstPort == 445"
              className={`w-full pl-10 pr-4 py-3 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 transition-all ${
                isDark
                  ? 'bg-white/[0.03] border border-white/[0.08] text-slate-200 placeholder-slate-700 focus:ring-cyan-500/30 focus:border-cyan-500/40'
                  : 'bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:ring-cyan-500/30 focus:border-cyan-400'
              }`}
            />
          </div>

          <div className="relative">
            <button
              onClick={() => setShowSaved(!showSaved)}
              className={`h-full px-4 rounded-xl border text-sm font-semibold flex items-center space-x-2 ${
                isDark
                  ? 'border-white/[0.08] bg-white/[0.03] text-slate-400 hover:bg-white/[0.06]'
                  : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Save size={14} />
              <span>Saved</span>
              <ChevronDown size={12} />
            </button>
            {showSaved && (
              <div className={`absolute right-0 top-full mt-1 w-56 rounded-xl border shadow-lg z-10 overflow-hidden ${
                isDark ? 'bg-[#0F0F1A] border-white/[0.1]' : 'bg-white border-slate-200'
              }`}>
                {savedHunts.map(h => (
                  <button
                    key={h.id}
                    onClick={() => { setQuery(h.query); setShowSaved(false); }}
                    className={`w-full text-left px-4 py-2.5 text-xs transition-colors ${
                      isDark
                        ? 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <div className={`font-semibold ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{h.name}</div>
                    <div className={`font-mono mt-0.5 ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{h.query}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={execute}
            className={`px-6 rounded-xl font-bold text-sm flex items-center space-x-2 transition-colors ${
              isDark
                ? 'bg-cyan-500/15 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/25'
                : 'bg-cyan-600 text-white hover:bg-cyan-700 shadow-sm'
            }`}
          >
            <Play size={14} fill="currentColor" />
            <span>Hunt</span>
          </button>
        </div>

        {/* Syntax hint */}
        <div className={`text-[10px] font-mono ${ isDark ? 'text-slate-700' : 'text-slate-400'}`}>
          Fields: srcIp · dstIp · srcPort · dstPort · protocol · appProtocol · bytes · packets · duration · riskScore · attackType &nbsp;|&nbsp; Ops: == &nbsp;!= &nbsp;&gt; &nbsp;&lt; &nbsp;&gt;= &nbsp;&lt;= &nbsp;&nbsp;|&nbsp; Combine: and
        </div>
      </div>

      {/* MAIN GRID */}
      <div className="flex-1 flex space-x-4 overflow-hidden min-h-0">

        {/* Results Table */}
        <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        }`}>
          <div className={`px-5 py-3.5 border-b flex items-center justify-between shrink-0 ${
            isDark ? 'border-white/[0.06] bg-[#0D0D18]' : 'border-slate-100 bg-slate-50/60'
          }`}>
            <span className={`text-xs font-semibold ${ isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {isLoading ? 'Hunting...' : `${flows.length} flows matched`}
            </span>
            {executedQuery && (
              <code className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                isDark ? 'bg-cyan-500/10 text-cyan-400' : 'bg-cyan-50 text-cyan-700'
              }`}>{executedQuery}</code>
            )}
          </div>
          <div className="flex-1 overflow-auto custom-scrollbar">
            <table className="w-full text-xs whitespace-nowrap">
              <thead className={`sticky top-0 ${
                isDark ? 'bg-[#0D0D18] text-slate-600' : 'bg-slate-50 text-slate-400'
              }`}>
                <tr>
                  {['Source','Destination','Protocol','Bytes','Packets','Risk','Type','Time'].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-semibold uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className={`divide-y ${
                isDark ? 'divide-white/[0.03]' : 'divide-slate-50'
              }`}>
                {flows.map((f: any) => (
                  <tr
                    key={f.id}
                    onClick={() => setSelected(f.id === selected?.id ? null : f)}
                    className={`cursor-pointer transition-colors ${
                      selected?.id === f.id
                        ? isDark ? 'bg-white/[0.04]' : 'bg-indigo-50/50'
                        : isDark ? 'hover:bg-white/[0.02]' : 'hover:bg-slate-50/60'
                    } ${
                      f.riskScore > 70 ? isDark ? 'border-l-2 border-red-500/40' : '' : ''
                    }`}
                  >
                    <td className={`px-4 py-3 font-mono ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{f.srcIp}:{f.srcPort}</td>
                    <td className={`px-4 py-3 font-mono ${ isDark ? 'text-slate-400' : 'text-slate-600'}`}>{f.dstIp}:{f.dstPort}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isDark ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'bg-cyan-50 text-cyan-700'
                      }`}>{f.appProtocol ?? f.protocol}</span>
                    </td>
                    <td className={`px-4 py-3 font-mono ${ isDark ? 'text-slate-400' : 'text-slate-600'}`}>{formatBytes(f.bytes)}</td>
                    <td className={`px-4 py-3 font-mono ${ isDark ? 'text-slate-400' : 'text-slate-600'}`}>{f.packets}</td>
                    <td className="px-4 py-3">
                      <span className={`font-bold font-mono ${
                        f.riskScore > 80 ? 'text-red-500' : f.riskScore > 60 ? 'text-orange-500' : f.riskScore > 40 ? 'text-yellow-500' : isDark ? 'text-emerald-500' : 'text-emerald-600'
                      }`}>{f.riskScore}</span>
                    </td>
                    <td className="px-4 py-3">
                      {f.attackType ? (
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isDark ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-red-50 text-red-700'
                        }`}>{f.attackType}</span>
                      ) : (
                        <span className={isDark ? 'text-slate-700' : 'text-slate-300'}>—</span>
                      )}
                    </td>
                    <td className={`px-4 py-3 ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{timeAgo(f.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sidebar: Facets + Detail */}
        <div className="w-72 flex flex-col space-y-4 shrink-0 overflow-y-auto custom-scrollbar">

          {/* Facets */}
          <div className={`rounded-2xl border p-5 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h3 className={`text-xs font-bold uppercase tracking-widest mb-4 ${
              isDark ? 'text-slate-600' : 'text-slate-400'
            }`}>Protocol Breakdown</h3>
            {Object.entries(facets).length > 0
              ? Object.entries(facets).map(([proto, cnt]: [string, any]) => (
                <div key={proto} className={`flex items-center justify-between py-2 border-b last:border-0 ${
                  isDark ? 'border-white/[0.04]' : 'border-slate-50'
                }`}>
                  <button
                    onClick={() => setQuery(`appProtocol == '${proto}'`)}
                    className={`text-xs font-semibold hover:underline ${
                      isDark ? 'text-cyan-400' : 'text-cyan-700'
                    }`}>{proto}</button>
                  <span className={`text-xs font-mono ${ isDark ? 'text-slate-500' : 'text-slate-500'}`}>{cnt}</span>
                </div>
              ))
              : <div className={`text-xs ${ isDark ? 'text-slate-700' : 'text-slate-400'}`}>Run a hunt to see facets</div>
            }
          </div>

          {/* Flow Detail */}
          {selected && (
            <div className={`rounded-2xl border p-5 space-y-4 animate-slide-in ${
              isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
            }`}>
              <div className="flex items-center justify-between">
                <h3 className={`text-xs font-bold uppercase tracking-widest ${ isDark ? 'text-slate-500' : 'text-slate-400'}`}>Flow Detail</h3>
                <button onClick={() => setSelected(null)} className={isDark ? 'text-slate-600 hover:text-slate-300' : 'text-slate-400 hover:text-slate-700'}>
                  <X size={14} />
                </button>
              </div>
              {[
                { label: 'Source', value: `${selected.srcIp}:${selected.srcPort}` },
                { label: 'Destination', value: `${selected.dstIp}:${selected.dstPort}` },
                { label: 'Protocol', value: selected.appProtocol ?? selected.protocol },
                { label: 'Bytes', value: formatBytes(selected.bytes) },
                { label: 'Packets', value: selected.packets },
                { label: 'Duration', value: `${selected.duration}s` },
                { label: 'Risk Score', value: selected.riskScore },
                { label: 'Attack Type', value: selected.attackType ?? 'Benign' },
              ].map((m, i) => (
                <div key={i} className={`flex justify-between text-xs border-b pb-2 last:border-0 ${
                  isDark ? 'border-white/[0.04]' : 'border-slate-50'
                }`}>
                  <span className={isDark ? 'text-slate-600' : 'text-slate-400'}>{m.label}</span>
                  <span className={`font-mono font-semibold ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{m.value}</span>
                </div>
              ))}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default HuntingPage;
