import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useUIStore } from '../../stores/uiStore';
import {
  ShieldAlert, Filter, ChevronRight, ArrowRight,
  Clock, Target, Shield, Zap, Eye, CheckCircle,
  XCircle, AlertTriangle, Info, ExternalLink, Activity
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1';

const demoAlerts = [
  { id: 'a1', severity: 'critical', signature: 'Port Scan — Reconnaissance', srcIp: '10.42.0.10', dstIp: '10.42.0.20', protocol: 'TCP', mitreTactic: 'Discovery', mitreTechnique: 'T1046', confidence: 0.92, status: 'new', timestamp: new Date().toISOString(), detectionReason: 'Port fan-out: 12 destination ports within 5 minutes', flowId: 'f1' },
  { id: 'a2', severity: 'critical', signature: 'Data Exfiltration — Large Outbound', srcIp: '10.42.0.10', dstIp: '8.8.8.8', protocol: 'TCP', mitreTactic: 'Exfiltration', mitreTechnique: 'T1041', confidence: 0.95, status: 'new', timestamp: new Date(Date.now()-60000).toISOString(), detectionReason: 'Large outbound transfer to external address: 8.0 MB', flowId: 'f2' },
  { id: 'a3', severity: 'high', signature: 'Lateral Movement — SMB Activity', srcIp: '10.42.0.10', dstIp: '10.42.0.21', protocol: 'TCP', mitreTactic: 'Lateral Movement', mitreTechnique: 'T1021', confidence: 0.78, status: 'investigating', timestamp: new Date(Date.now()-120000).toISOString(), detectionReason: 'Remote service activity on SMB/RDP with 200+ packets', flowId: 'f3' },
  { id: 'a4', severity: 'medium', signature: 'Suspicious DNS Query Volume', srcIp: '192.168.1.45', dstIp: '8.8.8.8', protocol: 'UDP', mitreTactic: 'Command and Control', mitreTechnique: 'T1071.004', confidence: 0.62, status: 'new', timestamp: new Date(Date.now()-180000).toISOString(), detectionReason: 'High frequency DNS queries: 428 queries in 60 seconds', flowId: 'f4' },
  { id: 'a5', severity: 'high', signature: 'Brute Force SSH', srcIp: '185.220.101.42', dstIp: '10.42.0.20', protocol: 'TCP', mitreTactic: 'Credential Access', mitreTechnique: 'T1110.001', confidence: 0.88, status: 'new', timestamp: new Date(Date.now()-240000).toISOString(), detectionReason: '94 failed SSH login attempts from single IP in 2 minutes', flowId: 'f5' },
  { id: 'a6', severity: 'low', signature: 'Unusual Port Access', srcIp: '10.42.0.15', dstIp: '10.42.0.30', protocol: 'TCP', mitreTactic: 'Discovery', mitreTechnique: 'T1046', confidence: 0.45, status: 'resolved', timestamp: new Date(Date.now()-300000).toISOString(), detectionReason: 'Access to unusual high port 8443 outside business hours', flowId: 'f6' },
];

const severityConfig: Record<string, { label: string; textDark: string; textLight: string; bgDark: string; bgLight: string; border: string }> = {
  critical: { label: 'CRITICAL', textDark: 'text-red-400', textLight: 'text-red-700', bgDark: 'bg-red-500/10', bgLight: 'bg-red-50', border: 'border-red-500/20' },
  high:     { label: 'HIGH',     textDark: 'text-orange-400', textLight: 'text-orange-700', bgDark: 'bg-orange-500/10', bgLight: 'bg-orange-50', border: 'border-orange-500/20' },
  medium:   { label: 'MEDIUM',   textDark: 'text-yellow-400', textLight: 'text-yellow-700', bgDark: 'bg-yellow-500/10', bgLight: 'bg-yellow-50', border: 'border-yellow-500/20' },
  low:      { label: 'LOW',      textDark: 'text-blue-400',   textLight: 'text-blue-700',   bgDark: 'bg-blue-500/10',   bgLight: 'bg-blue-50',   border: 'border-blue-500/20' },
};

function SeverityBadge({ severity, isDark }: { severity: string; isDark: boolean }) {
  const cfg = severityConfig[severity] ?? severityConfig.low;
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
      isDark ? `${cfg.textDark} ${cfg.bgDark} ${cfg.border}` : `${cfg.textLight} ${cfg.bgLight} ${cfg.border}`
    }`}>{cfg.label}</span>
  );
}

function timeAgo(ts: string): string {
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  return `${Math.floor(diff/3600)}h ago`;
}

const AlertsPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';
  const [filter, setFilter] = useState<string>('all');
  const [selected, setSelected] = useState<any>(null);
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await fetch(`${API}/alerts`);
      if (!res.ok) throw new Error('fail');
      const j = await res.json();
      return j.data ?? j;
    },
    initialData: demoAlerts,
    refetchInterval: 10000,
  });

  const updateStatus = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const res = await fetch(`${API}/alerts/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error('fail');
      return res.json();
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const alerts: any[] = Array.isArray(data) ? data : demoAlerts;
  const filters = ['all','critical','high','medium','low'];
  const filtered = filter === 'all' ? alerts : alerts.filter(a => a.severity === filter);
  const counts: Record<string,number> = alerts.reduce((acc,a) => ({ ...acc, [a.severity]: (acc[a.severity]||0)+1 }), {} as Record<string,number>);

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in">

      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            isDark ? 'bg-red-500/10 border border-red-500/20' : 'bg-red-50'
          }`}>
            <ShieldAlert size={20} className="text-red-500" />
          </div>
          <div>
            <h1 className={`text-xl font-bold ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>Security Detections</h1>
            <p className={`text-xs ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{alerts.length} total · {alerts.filter(a=>a.status==='new').length} unreviewed</p>
          </div>
        </div>

        {/* Filter chips */}
        <div className="flex space-x-2">
          {filters.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide border transition-all ${
                filter === f
                  ? isDark
                    ? `bg-white/[0.08] border-white/[0.15] text-white`
                    : `bg-slate-800 border-slate-800 text-white`
                  : isDark
                    ? 'border-white/[0.06] text-slate-500 hover:text-slate-300 hover:border-white/[0.1]'
                    : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700'
              }`}
            >
              {f === 'all' ? `All (${alerts.length})` : `${f} (${counts[f]||0})`}
            </button>
          ))}
        </div>
      </div>

      {/* SPLIT PANE */}
      <div className="flex-1 flex space-x-4 overflow-hidden min-h-0">

        {/* Alert List */}
        <div className={`flex flex-col overflow-hidden rounded-2xl border ${
          selected ? 'w-[52%]' : 'flex-1'
        } ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        } transition-all duration-300`}>
          <div className={`px-5 py-3.5 border-b shrink-0 ${
            isDark ? 'border-white/[0.06] bg-[#0D0D18]' : 'border-slate-100 bg-slate-50/60'
          }`}>
            <span className={`text-xs font-semibold ${ isDark ? 'text-slate-500' : 'text-slate-400'}`}>
              {filtered.length} detections
            </span>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            {filtered.map((alert: any) => (
              <button
                key={alert.id}
                onClick={() => setSelected(alert.id === selected?.id ? null : alert)}
                className={`w-full text-left px-5 py-4 border-b transition-all ${
                  selected?.id === alert.id
                    ? isDark
                      ? 'bg-white/[0.04] border-white/[0.08]'
                      : 'bg-indigo-50/50 border-slate-200'
                    : isDark
                      ? 'border-white/[0.04] hover:bg-white/[0.02]'
                      : 'border-slate-50 hover:bg-slate-50/60'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <SeverityBadge severity={alert.severity} isDark={isDark} />
                    <div>
                      <div className={`text-sm font-semibold mb-0.5 ${
                        isDark ? 'text-slate-200' : 'text-slate-800'
                      }`}>{alert.signature}</div>
                      <div className={`text-xs font-mono ${
                        isDark ? 'text-slate-600' : 'text-slate-400'
                      }`}>
                        {alert.srcIp} <ArrowRight size={10} className="inline" /> {alert.dstIp}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-1 shrink-0 ml-3">
                    <span className={`text-[10px] ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{timeAgo(alert.timestamp)}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      alert.status === 'resolved'
                        ? isDark ? 'text-emerald-500 bg-emerald-500/10' : 'text-emerald-600 bg-emerald-50'
                        : alert.status === 'investigating'
                          ? isDark ? 'text-yellow-500 bg-yellow-500/10' : 'text-yellow-600 bg-yellow-50'
                          : isDark ? 'text-red-400 bg-red-500/10' : 'text-red-600 bg-red-50'
                    }`}>{alert.status.toUpperCase()}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3 mt-2">
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                    isDark ? 'bg-white/[0.04] text-slate-500' : 'bg-slate-100 text-slate-500'
                  }`}>{alert.mitreTactic}</span>
                  <span className={`text-[10px] font-mono ${
                    isDark ? 'text-slate-600' : 'text-slate-400'
                  }`}>{alert.mitreTechnique}</span>
                  <span className={`text-[10px] font-mono ${
                    isDark ? 'text-slate-600' : 'text-slate-400'
                  }`}>Conf: {(alert.confidence * 100).toFixed(0)}%</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        {selected && (
          <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden animate-slide-in ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <div className={`px-5 py-4 border-b flex items-center justify-between shrink-0 ${
              isDark ? 'border-white/[0.06] bg-[#0D0D18]' : 'border-slate-100 bg-slate-50/60'
            }`}>
              <div className="flex items-center space-x-3">
                <SeverityBadge severity={selected.severity} isDark={isDark} />
                <span className={`text-sm font-bold ${ isDark ? 'text-slate-200' : 'text-slate-800'}`}>
                  Alert Details
                </span>
              </div>
              <button
                onClick={() => setSelected(null)}
                className={`p-1.5 rounded-lg ${
                  isDark ? 'text-slate-600 hover:text-slate-300 hover:bg-white/[0.04]' : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                }`}
              >
                <XCircle size={16} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-5">

              <div>
                <h2 className={`text-lg font-bold mb-1 ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>{selected.signature}</h2>
                <p className={`text-sm ${ isDark ? 'text-slate-500' : 'text-slate-500'}`}>{selected.detectionReason}</p>
              </div>

              {/* IP Flow */}
              <div className={`flex items-center space-x-3 p-4 rounded-xl border ${
                isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-slate-50 border-slate-100'
              }`}>
                <span className={`font-mono text-sm font-bold ${ isDark ? 'text-cyan-400' : 'text-cyan-700'}`}>{selected.srcIp}</span>
                <ArrowRight size={16} className={isDark ? 'text-slate-600' : 'text-slate-400'} />
                <span className={`font-mono text-sm font-bold ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{selected.dstIp}</span>
                <span className={`ml-auto text-[10px] font-bold px-2 py-0.5 rounded border ${
                  isDark ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' : 'bg-cyan-50 text-cyan-700 border-cyan-100'
                }`}>{selected.protocol}</span>
              </div>

              {/* MITRE */}
              <div>
                <div className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
                  isDark ? 'text-slate-600' : 'text-slate-400'
                }`}>MITRE ATT&CK</div>
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                    isDark ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 'bg-purple-50 text-purple-700 border-purple-200'
                  }`}>{selected.mitreTactic}</span>
                  <span className={`font-mono text-xs font-bold ${
                    isDark ? 'text-slate-400' : 'text-slate-600'
                  }`}>{selected.mitreTechnique}</span>
                </div>
              </div>

              {/* Confidence */}
              <div>
                <div className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
                  isDark ? 'text-slate-600' : 'text-slate-400'
                }`}>ML Confidence Score</div>
                <div className={`h-2.5 rounded-full overflow-hidden ${
                  isDark ? 'bg-white/[0.05]' : 'bg-slate-100'
                }`}>
                  <div
                    className={`h-full rounded-full ${
                      selected.confidence > 0.85 ? 'bg-red-500' : selected.confidence > 0.7 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${selected.confidence * 100}%` }}
                  />
                </div>
                <div className={`text-right text-xs font-bold mt-1 ${
                  isDark ? 'text-slate-400' : 'text-slate-600'
                }`}>{(selected.confidence * 100).toFixed(1)}%</div>
              </div>

              {/* Actions */}
              <div>
                <div className={`text-[10px] font-bold uppercase tracking-widest mb-3 ${
                  isDark ? 'text-slate-600' : 'text-slate-400'
                }`}>Actions</div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => updateStatus.mutate({ id: selected.id, status: 'investigating' })}
                    className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-colors ${
                      isDark
                        ? 'border-yellow-500/20 bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20'
                        : 'border-yellow-200 bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                    }`}
                  >
                    Investigate
                  </button>
                  <button
                    onClick={() => updateStatus.mutate({ id: selected.id, status: 'resolved' })}
                    className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-colors ${
                      isDark
                        ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
                        : 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                    }`}
                  >
                    Resolve
                  </button>
                  <button
                    className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-colors ${
                      isDark
                        ? 'border-red-500/20 bg-red-500/10 text-red-400 hover:bg-red-500/20'
                        : 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100'
                    }`}
                  >
                    Escalate
                  </button>
                </div>
              </div>

              {/* Metadata */}
              <div className={`grid grid-cols-2 gap-3 p-4 rounded-xl border ${
                isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-slate-50 border-slate-100'
              }`}>
                {[
                  { label: 'Alert ID', value: selected.id },
                  { label: 'Flow ID', value: selected.flowId },
                  { label: 'Status', value: selected.status.toUpperCase() },
                  { label: 'Detected', value: timeAgo(selected.timestamp) },
                ].map((m, i) => (
                  <div key={i}>
                    <div className={`text-[10px] font-bold uppercase tracking-wider mb-0.5 ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{m.label}</div>
                    <div className={`text-xs font-mono ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{m.value}</div>
                  </div>
                ))}
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
