import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { useUIStore } from '../../stores/uiStore';
import {
  Bug, Terminal, Crosshair, Eye, AlertTriangle,
  Globe, Wifi, Shield, Lock, Key, Activity,
  ChevronRight, Clock, User, Zap
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1';

const fetchHoneypots = async () => {
  try {
    const res = await fetch(`${API}/deception/honeypots`);
    if (!res.ok) throw new Error('fetch failed');
    return res.json();
  } catch {
    // Return demo data if backend not available
    return {
      honeypots: [
        { id: 'hp1', name: 'SSH-Trap-01', ip: '10.99.0.1', port: 22, protocol: 'SSH', engagements: 1402, status: 'active', lastActivity: '2s ago', attackerIp: '185.220.101.42', country: 'RU', credentialsCapt: 8 },
        { id: 'hp2', name: 'HTTP-Decoy-01', ip: '10.99.0.2', port: 80, protocol: 'HTTP', engagements: 892, status: 'active', lastActivity: '14s ago', attackerIp: '45.33.32.156', country: 'CN', credentialsCapt: 0 },
        { id: 'hp3', name: 'SMB-Ghost-01', ip: '10.99.0.3', port: 445, protocol: 'SMB', engagements: 234, status: 'active', lastActivity: '1m ago', attackerIp: '162.142.125.11', country: 'US', credentialsCapt: 3 },
        { id: 'hp4', name: 'RDP-Decoy-01', ip: '10.99.0.4', port: 3389, protocol: 'RDP', engagements: 567, status: 'triggered', lastActivity: '5s ago', attackerIp: '91.241.19.57', country: 'IR', credentialsCapt: 12 },
        { id: 'hp5', name: 'FTP-Lure-01', ip: '10.99.0.5', port: 21, protocol: 'FTP', engagements: 145, status: 'active', lastActivity: '3m ago', attackerIp: '193.109.69.7', country: 'NL', credentialsCapt: 1 },
        { id: 'hp6', name: 'Telnet-Trap-01', ip: '10.99.0.6', port: 23, protocol: 'Telnet', engagements: 2819, status: 'triggered', lastActivity: '1s ago', attackerIp: '112.30.4.56', country: 'CN', credentialsCapt: 28 },
      ]
    };
  }
};

const demoEngagements = [
  { t: '08:51:04', src: '185.220.101.42', action: 'SSH Auth Attempt', cred: 'root:password123', country: 'RU', ttl: 64 },
  { t: '08:51:01', src: '112.30.4.56', action: 'Telnet Login', cred: 'admin:admin', country: 'CN', ttl: 48 },
  { t: '08:50:59', src: '91.241.19.57', action: 'RDP Connect', cred: 'administrator:P@ssw0rd', country: 'IR', ttl: 56 },
  { t: '08:50:57', src: '162.142.125.11', action: 'SMB Share Enum', cred: '', country: 'US', ttl: 64 },
  { t: '08:50:52', src: '185.220.101.42', action: 'Shell Command: whoami', cred: '', country: 'RU', ttl: 64 },
  { t: '08:50:48', src: '45.33.32.156', action: 'HTTP POST /admin', cred: 'admin:admin123', country: 'CN', ttl: 52 },
  { t: '08:50:44', src: '112.30.4.56', action: 'Shell Command: cat /etc/passwd', cred: '', country: 'CN', ttl: 48 },
  { t: '08:50:39', src: '193.109.69.7', action: 'FTP Auth Attempt', cred: 'anonymous:', country: 'NL', ttl: 56 },
];

const countryFlag: Record<string,string> = { RU:'🇷🇺', CN:'🇨🇳', US:'🇺🇸', IR:'🇮🇷', NL:'🇳🇱', DE:'🇩🇪', BR:'🇧🇷' };

const DeceptionPage: React.FC = () => {
  const honeypotEvents = useTelemetryStore(s => s.honeypotEvents);
  const { theme } = useUIStore();
  const isDark = theme === 'dark';
  const [selectedHp, setSelectedHp] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'log'|'creds'>('log');

  const { data } = useQuery({ queryKey: ['honeypots'], queryFn: fetchHoneypots, refetchInterval: 5000 });
  const honeypots = data?.honeypots ?? [];

  const allEvents = [...honeypotEvents.map((e: any) => ({ t: e.t, src: e.src, action: e.action, cred: '', country: '??', ttl: 64 })), ...demoEngagements];

  const totalEngagements = honeypots.reduce((s: number, h: any) => s + (h.engagements || 0), 0);
  const triggeredCount = honeypots.filter((h: any) => h.status === 'triggered').length;
  const totalCreds = honeypots.reduce((s: number, h: any) => s + (h.credentialsCapt || 0), 0);

  const engagementOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: isDark ? '#0F172A' : '#fff', borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0', textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 11 } },
    grid: { top: 8, right: 8, bottom: 20, left: 32 },
    xAxis: { type: 'category', data: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], axisLabel: { fontSize: 10, color: isDark ? '#475569' : '#94a3b8' }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.04)' : '#f1f5f9', type: 'dashed' } }, axisLabel: { color: isDark ? '#475569' : '#94a3b8', fontSize: 10 }, axisLine: { show: false } },
    series: [{
      type: 'bar',
      data: [420, 680, 892, 1102, 1402, 2100, 2819],
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: isDark ? '#F97316' : '#F97316' },
            { offset: 1, color: isDark ? '#DC2626' : '#EF4444' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      },
      barMaxWidth: 28,
    }]
  };

  const protocolPieOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: isDark ? '#0F172A' : '#fff', borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0', textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 11 } },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: ['55%', '85%'],
      data: [
        { value: 2819, name: 'Telnet', itemStyle: { color: '#EF4444' } },
        { value: 1402, name: 'SSH', itemStyle: { color: '#F97316' } },
        { value: 892, name: 'HTTP', itemStyle: { color: '#22D3EE' } },
        { value: 567, name: 'RDP', itemStyle: { color: '#8B5CF6' } },
        { value: 234, name: 'SMB', itemStyle: { color: '#10B981' } },
        { value: 145, name: 'FTP', itemStyle: { color: '#6366F1' } },
      ],
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } }
    }]
  };

  const s = (cls: string) => cls;

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in">

      {/* HEADER STATS */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Active Honeypots', value: honeypots.length, icon: Bug, color: isDark ? 'text-orange-400' : 'text-orange-500', bg: isDark ? 'bg-orange-500/10 border-orange-500/20' : 'bg-orange-50 border-orange-100' },
          { label: 'Total Engagements', value: totalEngagements.toLocaleString(), icon: Activity, color: isDark ? 'text-red-400' : 'text-red-600', bg: isDark ? 'bg-red-500/10 border-red-500/20' : 'bg-red-50 border-red-100' },
          { label: 'Triggered Alerts', value: triggeredCount, icon: Zap, color: isDark ? 'text-yellow-400' : 'text-yellow-600', bg: isDark ? 'bg-yellow-500/10 border-yellow-500/20' : 'bg-yellow-50 border-yellow-100' },
          { label: 'Credentials Captured', value: totalCreds, icon: Key, color: isDark ? 'text-violet-400' : 'text-violet-600', bg: isDark ? 'bg-violet-500/10 border-violet-500/20' : 'bg-violet-50 border-violet-100' },
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl p-5 flex items-center justify-between border card-hover ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <div>
              <div className={`text-[10px] font-bold uppercase tracking-widest mb-1.5 ${
                isDark ? 'text-slate-600' : 'text-slate-400'
              }`}>{k.label}</div>
              <div className={`text-3xl font-bold tracking-tight ${
                isDark ? 'text-slate-100' : 'text-slate-800'
              }`}>{k.value}</div>
            </div>
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border ${k.bg}`}>
              <k.icon size={22} className={k.color} />
            </div>
          </div>
        ))}
      </div>

      {/* MAIN GRID */}
      <div className="flex-1 grid grid-cols-3 gap-4 overflow-hidden min-h-0">

        {/* HONEYPOT CARDS — LEFT */}
        <div className="col-span-1 flex flex-col space-y-2 overflow-y-auto custom-scrollbar">
          <div className={`text-[10px] font-bold uppercase tracking-widest mb-1 ${
            isDark ? 'text-slate-600' : 'text-slate-400'
          }`}>Active Decoys</div>
          {honeypots.map((hp: any) => (
            <button
              key={hp.id}
              onClick={() => setSelectedHp(hp.id === selectedHp ? null : hp.id)}
              className={`w-full text-left rounded-xl border p-4 transition-all ${
                selectedHp === hp.id
                  ? isDark
                    ? 'bg-orange-500/10 border-orange-500/30'
                    : 'bg-orange-50 border-orange-200'
                  : isDark
                    ? 'bg-[#0A0A12] border-white/[0.06] hover:border-white/[0.12]'
                    : 'bg-white border-slate-100 shadow-sm hover:shadow-md'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`font-semibold text-sm ${
                  isDark ? 'text-slate-200' : 'text-slate-800'
                }`}>{hp.name}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  hp.status === 'triggered'
                    ? isDark ? 'bg-red-500/15 text-red-400 border-red-500/20' : 'bg-red-50 text-red-600 border-red-200'
                    : isDark ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-emerald-50 text-emerald-600 border-emerald-200'
                }`}>
                  {hp.status.toUpperCase()}
                </span>
              </div>
              <div className={`flex items-center justify-between text-xs ${
                isDark ? 'text-slate-600' : 'text-slate-500'
              }`}>
                <span className="font-mono">{hp.ip}:{hp.port} ({hp.protocol})</span>
                <span className={`font-mono font-medium ${
                  isDark ? 'text-orange-400' : 'text-orange-600'
                }`}>{hp.engagements.toLocaleString()} hits</span>
              </div>
              <div className={`flex items-center justify-between text-[10px] mt-2 ${
                isDark ? 'text-slate-700' : 'text-slate-400'
              }`}>
                <span>Last: {hp.lastActivity}</span>
                <span>{countryFlag[hp.country] ?? '🌐'} {hp.attackerIp}</span>
              </div>
              {hp.credentialsCapt > 0 && (
                <div className={`mt-2 flex items-center space-x-1.5 text-[10px] font-bold ${
                  isDark ? 'text-violet-400' : 'text-violet-600'
                }`}>
                  <Key size={10} />
                  <span>{hp.credentialsCapt} credentials captured</span>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* MIDDLE: Charts */}
        <div className="col-span-1 flex flex-col space-y-4 overflow-hidden">

          {/* Engagement bar chart */}
          <div className={`rounded-2xl border p-5 flex-1 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h3 className={`text-sm font-semibold mb-3 ${
              isDark ? 'text-slate-200' : 'text-slate-800'
            }`}>Weekly Engagement Trend</h3>
            <div style={{ height: 140 }}>
              <ReactECharts option={engagementOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          {/* Protocol breakdown pie */}
          <div className={`rounded-2xl border p-5 flex-1 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h3 className={`text-sm font-semibold mb-2 ${
              isDark ? 'text-slate-200' : 'text-slate-800'
            }`}>Attack Protocol Distribution</h3>
            <div className="flex items-center">
              <div style={{ height: 120, flex: 1 }}>
                <ReactECharts option={protocolPieOption} style={{ height: '100%', width: '100%' }} />
              </div>
              <div className="space-y-1.5 text-xs">
                {['Telnet','SSH','HTTP','RDP','SMB','FTP'].map((p,i) => (
                  <div key={p} className="flex items-center space-x-2">
                    <div className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: ['#EF4444','#F97316','#22D3EE','#8B5CF6','#10B981','#6366F1'][i] }} />
                    <span className={isDark ? 'text-slate-500' : 'text-slate-600'}>{p}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Efficacy metrics */}
          <div className={`rounded-2xl border p-5 shrink-0 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h3 className={`text-sm font-semibold mb-4 ${
              isDark ? 'text-slate-200' : 'text-slate-800'
            }`}>Trap Efficacy</h3>
            {[
              { label: 'Avg. Time to Compromise', value: '4.2s', pct: 12, color: 'bg-orange-500' },
              { label: 'Payload Capture Rate', value: '84%', pct: 84, color: isDark ? 'bg-cyan-500' : 'bg-cyan-500' },
              { label: 'Zero-Day Heuristics', value: '3 fired', pct: 98, color: 'bg-red-500' },
            ].map((m, i) => (
              <div key={i} className="mb-3 last:mb-0">
                <div className={`flex justify-between text-xs mb-1.5 ${
                  isDark ? 'text-slate-500' : 'text-slate-500'
                }`}>
                  <span>{m.label}</span>
                  <span className={`font-bold ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{m.value}</span>
                </div>
                <div className={`h-1.5 rounded-full overflow-hidden ${
                  isDark ? 'bg-white/[0.05]' : 'bg-slate-100'
                }`}>
                  <div className={`h-full rounded-full ${m.color}`} style={{ width: `${m.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT: Engagement Log + Credentials */}
        <div className="col-span-1 flex flex-col space-y-4 overflow-hidden">

          {/* Tab switcher */}
          <div className={`flex rounded-xl border p-1 shrink-0 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-200 shadow-sm'
          }`}>
            {(['log','creds'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-colors ${
                  activeTab === tab
                    ? isDark
                      ? 'bg-orange-500/15 text-orange-400 border border-orange-500/20'
                      : 'bg-orange-50 text-orange-700 shadow-sm'
                    : isDark ? 'text-slate-600 hover:text-slate-400' : 'text-slate-400 hover:text-slate-700'
                }`}
              >
                {tab === 'log' ? '📡 Live Log' : '🔑 Credentials'}
              </button>
            ))}
          </div>

          {/* Engagement log */}
          {activeTab === 'log' && (
            <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden ${
              isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
            }`}>
              <div className={`px-4 py-3 border-b flex items-center justify-between shrink-0 ${
                isDark ? 'border-white/[0.06]' : 'border-slate-100'
              }`}>
                <span className={`text-sm font-semibold ${
                  isDark ? 'text-slate-200' : 'text-slate-800'
                }`}>Live Engagement Log</span>
                <div className="flex items-center space-x-1.5">
                  <div className="status-dot-danger" style={{ width: 6, height: 6 }} />
                  <span className={`text-[10px] font-bold ${ isDark ? 'text-red-400' : 'text-red-600'}`}>ACTIVE</span>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto custom-scrollbar p-1">
                {allEvents.map((log: any, i: number) => (
                  <div key={i} className={`p-3 rounded-xl mb-1 border transition-colors ${
                    log.action.includes('Shell') || log.action.includes('passwd')
                      ? isDark
                        ? 'bg-red-950/25 border-red-500/15'
                        : 'bg-red-50 border-red-100'
                      : isDark
                        ? 'bg-white/[0.02] border-white/[0.04] hover:bg-white/[0.04]'
                        : 'bg-slate-50/60 border-slate-100 hover:bg-slate-50'
                  }`}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className={`font-mono text-[10px] ${
                        isDark ? 'text-slate-600' : 'text-slate-400'
                      }`}>{log.t}</span>
                      <span className={`text-[10px] font-bold ${
                        log.action.includes('Shell') || log.action.includes('passwd')
                          ? isDark ? 'text-red-400' : 'text-red-600'
                          : isDark ? 'text-orange-400' : 'text-orange-600'
                      }`}>
                        {countryFlag[log.country] ?? '🌐'} {log.country}
                      </span>
                    </div>
                    <div className={`text-xs font-semibold mb-1 ${
                      isDark ? 'text-slate-300' : 'text-slate-700'
                    }`}>{log.action}</div>
                    <div className={`font-mono text-[10px] ${
                      isDark ? 'text-slate-600' : 'text-slate-400'
                    }`}>{log.src}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Credentials panel */}
          {activeTab === 'creds' && (
            <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden ${
              isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
            }`}>
              <div className={`px-4 py-3 border-b shrink-0 ${
                isDark ? 'border-white/[0.06]' : 'border-slate-100'
              }`}>
                <span className={`text-sm font-semibold ${
                  isDark ? 'text-slate-200' : 'text-slate-800'
                }`}>Captured Credentials</span>
              </div>
              <div className="flex-1 overflow-y-auto custom-scrollbar">
                <table className="w-full text-xs">
                  <thead className={isDark ? 'text-slate-600' : 'text-slate-400'}>
                    <tr>
                      <th className="px-4 py-2.5 text-left font-semibold uppercase tracking-wider">Time</th>
                      <th className="px-4 py-2.5 text-left font-semibold uppercase tracking-wider">Attacker</th>
                      <th className="px-4 py-2.5 text-left font-semibold uppercase tracking-wider">Credential</th>
                    </tr>
                  </thead>
                  <tbody className={`divide-y ${ isDark ? 'divide-white/[0.03]' : 'divide-slate-50'}`}>
                    {allEvents.filter(e => e.cred).map((log: any, i: number) => (
                      <tr key={i} className={isDark ? 'hover:bg-white/[0.02]' : 'hover:bg-slate-50'}>
                        <td className={`px-4 py-2.5 font-mono ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{log.t}</td>
                        <td className={`px-4 py-2.5 font-mono ${ isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                          {countryFlag[log.country] ?? '🌐'} {log.src}
                        </td>
                        <td className={`px-4 py-2.5 font-mono font-bold ${ isDark ? 'text-violet-400' : 'text-violet-700'}`}>{log.cred}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default DeceptionPage;
