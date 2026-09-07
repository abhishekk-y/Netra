import React, { useEffect, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { useUIStore } from '../../stores/uiStore';
import {
  AlertCircle, Activity, Server, Shield, Database,
  ArrowUpRight, Network, Terminal, TrendingUp, TrendingDown,
  Cpu, MemoryStick, HardDrive, Wifi, Zap
} from 'lucide-react';

const fetchSummary = async () => {
  const res = await fetch('http://localhost:8000/api/v1/summary');
  if (!res.ok) return null;
  return res.json();
};

function AnimatedNumber({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [displayed, setDisplayed] = React.useState(value);
  useEffect(() => {
    const diff = value - displayed;
    if (Math.abs(diff) < 0.1) { setDisplayed(value); return; }
    const step = diff / 10;
    const timer = setInterval(() => {
      setDisplayed(prev => {
        const next = prev + step;
        if (Math.abs(next - value) < Math.abs(step)) { clearInterval(timer); return value; }
        return next;
      });
    }, 40);
    return () => clearInterval(timer);
  }, [value]);
  return <>{typeof displayed === 'number' ? displayed.toFixed(suffix === '%' || suffix === 'ms' ? 1 : 0) : displayed}{suffix}</>;
}

const DashboardPage: React.FC = () => {
  const telemetry = useTelemetryStore();
  const { theme } = useUIStore();
  const isDark = theme === 'dark';
  const terminalRef = useRef<HTMLDivElement>(null);
  const packets = telemetry.packets;

  const { data: summary } = useQuery({ queryKey: ['summary'], queryFn: fetchSummary, refetchInterval: 5000 });

  useEffect(() => {
    if (terminalRef.current) terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
  }, [packets]);

  const currentRisk = packets.length > 0 ? packets[0].risk : 0;
  const isCritical = currentRisk > 75;

  const kpis = [
    {
      label: 'Active Connections',
      value: telemetry.activeConnections || (summary?.totalFlows ?? 0),
      icon: Activity,
      color: isDark ? 'text-cyan-400' : 'text-[#00bceb]',
      bg: isDark ? 'bg-cyan-500/10 border-cyan-500/20' : 'bg-cyan-50 border-cyan-100',
      trend: '+12%',
      up: true,
    },
    {
      label: 'Packets / sec',
      value: telemetry.packetsPerSec,
      icon: Zap,
      color: isDark ? 'text-violet-400' : 'text-violet-600',
      bg: isDark ? 'bg-violet-500/10 border-violet-500/20' : 'bg-violet-50 border-violet-100',
      trend: '+5.2%',
      up: true,
    },
    {
      label: 'Monitored Hosts',
      value: telemetry.hostsCount || (summary?.totalHosts ?? 0),
      icon: Server,
      color: isDark ? 'text-emerald-400' : 'text-emerald-600',
      bg: isDark ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-emerald-50 border-emerald-100',
      trend: '+3',
      up: true,
    },
    {
      label: 'Active Incidents',
      value: summary?.activeIncidents ?? 0,
      icon: Shield,
      color: isDark ? 'text-red-400' : 'text-red-600',
      bg: isDark ? 'bg-red-500/10 border-red-500/20' : 'bg-red-50 border-red-100',
      trend: summary?.activeIncidents > 0 ? `${summary?.activeIncidents} open` : 'All clear',
      up: false,
    },
  ];

  const heroOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDark ? '#0F172A' : '#FFFFFF',
      borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#E2E8F0',
      textStyle: { color: isDark ? '#E2E8F0' : '#1E293B', fontSize: 12, fontFamily: 'Inter' },
      formatter: (params: any[]) => {
        return params.map(p => `${p.marker} ${p.seriesName}: <b>${p.value}</b>`).join('<br/>');
      }
    },
    legend: {
      data: ['Bandwidth (B)', 'AI Risk Score'],
      textStyle: { color: isDark ? '#64748B' : '#94A3B8', fontSize: 11 },
      top: 0, right: 0
    },
    grid: { top: 36, right: 16, bottom: 24, left: 50, containLabel: false },
    xAxis: {
      type: 'category',
      data: packets.slice().reverse().map((p: any) => p.time),
      axisLabel: { fontSize: 10, color: isDark ? '#334155' : '#94A3B8', fontFamily: 'JetBrains Mono' },
      axisLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.06)' : '#E2E8F0' } },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: 'Bytes',
        nameTextStyle: { color: isDark ? '#334155' : '#CBD5E1', fontSize: 10 },
        splitLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.04)' : '#F1F5F9', type: 'dashed' } },
        axisLabel: { color: isDark ? '#334155' : '#94A3B8', fontSize: 10 },
        axisLine: { show: false },
      },
      {
        type: 'value',
        name: 'Risk',
        max: 100,
        nameTextStyle: { color: isDark ? '#334155' : '#CBD5E1', fontSize: 10 },
        splitLine: { show: false },
        axisLabel: { show: false },
        axisLine: { show: false },
      }
    ],
    series: [
      {
        name: 'Bandwidth (B)',
        type: 'line',
        smooth: true,
        yAxisIndex: 0,
        symbol: 'none',
        lineStyle: { width: 2, color: isDark ? '#22D3EE' : '#00BCEB' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: isDark ? 'rgba(34,211,238,0.25)' : 'rgba(0,188,235,0.18)' },
              { offset: 1, color: 'rgba(0,0,0,0)' }
            ]
          }
        },
        data: packets.slice().reverse().map((p: any) => p.len)
      },
      {
        name: 'AI Risk Score',
        type: 'line',
        step: 'middle',
        yAxisIndex: 1,
        symbol: 'none',
        lineStyle: { width: 2, type: 'dashed', color: '#F97316' },
        itemStyle: { color: '#F97316' },
        data: packets.slice().reverse().map((p: any) => p.risk)
      }
    ]
  };

  const severityColor = (risk: number) => {
    if (risk > 90) return isDark ? 'text-red-400' : 'text-red-600';
    if (risk > 70) return isDark ? 'text-orange-400' : 'text-orange-600';
    if (risk > 40) return isDark ? 'text-yellow-400' : 'text-yellow-600';
    return isDark ? 'text-emerald-400' : 'text-emerald-600';
  };

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in">

      {/* ALERT BANNER */}
      <div className={`rounded-xl px-5 py-3.5 flex items-center justify-between border transition-all ${
        isCritical
          ? isDark
            ? 'bg-red-500/[0.08] border-red-500/25'
            : 'bg-red-50 border-red-200'
          : isDark
            ? 'bg-emerald-500/[0.06] border-emerald-500/15'
            : 'bg-emerald-50 border-emerald-200'
      }`}>
        <div className="flex items-center space-x-3">
          {isCritical
            ? <AlertCircle size={18} className="text-red-500 animate-pulse" />
            : <Shield size={18} className="text-emerald-500" />}
          <span className={`text-sm font-semibold ${
            isCritical
              ? isDark ? 'text-red-400' : 'text-red-700'
              : isDark ? 'text-emerald-400' : 'text-emerald-700'
          }`}>
            {isCritical
              ? 'CRITICAL — High-probability threat detected by ML Ensemble'
              : 'System Normal — All sensors healthy, no active threats'}
          </span>
        </div>
        <div className={`flex items-center space-x-3 text-xs font-medium ${
          isDark ? 'text-slate-500' : 'text-slate-500'
        }`}>
          <span>ML Confidence:</span>
          <span className={`px-2.5 py-1 rounded-lg font-bold text-sm ${
            isCritical
              ? 'bg-red-500 text-white'
              : 'bg-emerald-500 text-white'
          }`}>
            <AnimatedNumber value={currentRisk} suffix="%" />
          </span>
        </div>
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-4 gap-4">
        {kpis.map((k, i) => (
          <div
            key={i}
            className={`rounded-2xl p-5 flex items-center justify-between border card-hover cursor-default ${
              isDark
                ? 'bg-[#0A0A12] border-white/[0.06] hover:border-white/[0.1]'
                : 'bg-white border-slate-100 shadow-sm hover:shadow-md'
            }`}
          >
            <div>
              <div className={`text-[10px] font-bold uppercase tracking-widest mb-1.5 ${
                isDark ? 'text-slate-600' : 'text-slate-400'
              }`}>{k.label}</div>
              <div className={`text-3xl font-bold tracking-tight ${
                isDark ? 'text-slate-100' : 'text-slate-800'
              }`}>
                <AnimatedNumber value={typeof k.value === 'number' ? k.value : 0} />
              </div>
              <div className={`text-xs mt-1.5 font-semibold flex items-center space-x-1 ${
                k.up
                  ? isDark ? 'text-emerald-500' : 'text-emerald-600'
                  : k.value > 0 ? 'text-red-500' : isDark ? 'text-slate-600' : 'text-slate-400'
              }`}>
                {k.up ? <TrendingUp size={11} /> : k.value > 0 ? <TrendingDown size={11} /> : null}
                <span>{k.trend}</span>
              </div>
            </div>
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border ${k.bg}`}>
              <k.icon size={22} className={k.color} />
            </div>
          </div>
        ))}
      </div>

      {/* MAIN GRID */}
      <div className="flex-1 grid grid-cols-3 gap-4 overflow-hidden min-h-0">

        {/* LEFT: Chart + Table */}
        <div className="col-span-2 flex flex-col space-y-4 overflow-hidden">

          {/* Traffic Chart */}
          <div className={`rounded-2xl border p-5 flex flex-col min-h-[260px] ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <div className="flex justify-between items-center mb-3">
              <h2 className={`font-semibold ${
                isDark ? 'text-slate-200 text-sm' : 'text-slate-800 text-base'
              }`}>Traffic Volume vs. AI Risk Forecasting</h2>
              <button className={`text-xs font-semibold flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-colors ${
                isDark
                  ? 'text-cyan-400 hover:bg-cyan-500/10 border border-cyan-500/20'
                  : 'text-[#00bceb] hover:bg-cyan-50 border border-cyan-100'
              }`}>
                <span>View Report</span>
                <ArrowUpRight size={13} />
              </button>
            </div>
            <div className="flex-1">
              <ReactECharts option={heroOption} style={{ height: '100%', width: '100%', minHeight: 180 }} />
            </div>
          </div>

          {/* Packet Table */}
          <div className={`rounded-2xl border flex-1 flex flex-col overflow-hidden ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <div className={`px-5 py-3.5 border-b flex items-center justify-between shrink-0 ${
              isDark ? 'border-white/[0.06] bg-[#0D0D18]' : 'border-slate-100 bg-slate-50/60'
            }`}>
              <h2 className={`text-sm font-semibold ${
                isDark ? 'text-slate-300' : 'text-slate-700'
              }`}>Deep Packet Inspection Feed</h2>
              <div className={`flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider ${
                isDark ? 'text-slate-600' : 'text-slate-400'
              }`}>
                <div className="status-dot-online" style={{ width: 6, height: 6 }} />
                <span>Live</span>
              </div>
            </div>
            <div className="flex-1 overflow-auto custom-scrollbar">
              <table className="w-full text-left text-xs whitespace-nowrap">
                <thead className={`sticky top-0 ${
                  isDark ? 'bg-[#0D0D18] text-slate-600' : 'bg-slate-50 text-slate-400'
                }`}>
                  <tr>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider">Time</th>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider">Source</th>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider">Destination</th>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider">Protocol</th>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider text-right">Risk</th>
                    <th className="px-4 py-3 font-semibold uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${
                  isDark ? 'divide-white/[0.03]' : 'divide-slate-50'
                }`}>
                  {packets.map((p: any, i: number) => (
                    <tr
                      key={i}
                      className={`transition-colors ${
                        p.status === 'DROP'
                          ? isDark ? 'bg-red-950/20 hover:bg-red-950/30' : 'bg-red-50/60 hover:bg-red-50'
                          : isDark ? 'hover:bg-white/[0.02]' : 'hover:bg-slate-50/60'
                      }`}
                    >
                      <td className={`px-4 py-2.5 font-mono ${
                        isDark ? 'text-slate-600' : 'text-slate-400'
                      }`}>{p.time}</td>
                      <td className={`px-4 py-2.5 font-mono font-medium ${
                        isDark ? 'text-slate-300' : 'text-slate-700'
                      }`}>{p.src}</td>
                      <td className={`px-4 py-2.5 font-mono ${
                        isDark ? 'text-slate-400' : 'text-slate-600'
                      }`}>{p.dst}</td>
                      <td className="px-4 py-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          isDark
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'bg-cyan-50 text-cyan-700 border border-cyan-100'
                        }`}>{p.proto}</span>
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <span className={`font-bold font-mono ${severityColor(p.risk)}`}>
                          {p.risk.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          p.status === 'DROP'
                            ? isDark
                              ? 'bg-red-500/15 text-red-400 border border-red-500/20'
                              : 'bg-red-100 text-red-700'
                            : isDark
                              ? 'bg-white/[0.04] text-slate-500'
                              : 'bg-slate-100 text-slate-500'
                        }`}>{p.status}</span>
                      </td>
                    </tr>
                  ))}
                  {packets.length === 0 && (
                    <tr>
                      <td colSpan={6} className={`px-4 py-12 text-center text-sm ${
                        isDark ? 'text-slate-700' : 'text-slate-400'
                      }`}>Awaiting live packet feed...</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* RIGHT: Diagnostics + Terminal */}
        <div className="col-span-1 flex flex-col space-y-4 overflow-hidden">

          {/* System Diagnostics */}
          <div className={`rounded-2xl border p-5 shrink-0 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h2 className={`font-semibold mb-5 flex items-center space-x-2 ${
              isDark ? 'text-slate-200 text-sm' : 'text-slate-800'
            }`}>
              <Cpu size={15} className={isDark ? 'text-slate-600' : 'text-slate-400'} />
              <span>System Diagnostics</span>
            </h2>
            {[
              { label: 'CPU Usage', value: telemetry.cpuUsage, color: isDark ? 'bg-violet-500' : 'bg-violet-500', icon: Cpu, suffix: '%' },
              { label: 'Memory Usage', value: telemetry.ramUsage, color: isDark ? 'bg-cyan-500' : 'bg-cyan-500', icon: MemoryStick, suffix: '%' },
              { label: 'Disk Latency', value: Math.min(100, telemetry.diskLatency * 5), color: isDark ? 'bg-orange-500' : 'bg-orange-400', icon: HardDrive, suffix: 'ms', rawValue: telemetry.diskLatency },
            ].map((m, i) => (
              <div key={i} className="mb-4 last:mb-0">
                <div className="flex justify-between items-center mb-1.5">
                  <span className={`text-xs font-medium flex items-center space-x-1.5 ${
                    isDark ? 'text-slate-500' : 'text-slate-500'
                  }`}>
                    <m.icon size={11} />
                    <span>{m.label}</span>
                  </span>
                  <span className={`text-xs font-bold font-mono ${
                    isDark ? 'text-slate-300' : 'text-slate-700'
                  }`}>
                    <AnimatedNumber value={m.rawValue ?? m.value} suffix={m.suffix} />
                  </span>
                </div>
                <div className={`h-1.5 w-full rounded-full overflow-hidden ${
                  isDark ? 'bg-white/[0.05]' : 'bg-slate-100'
                }`}>
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${m.color}`}
                    style={{ width: `${Math.min(100, m.value)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* ML Inference Status */}
          <div className={`rounded-2xl border p-5 shrink-0 ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <h2 className={`font-semibold mb-4 text-sm ${
              isDark ? 'text-slate-200' : 'text-slate-800'
            }`}>ML Ensemble Status</h2>
            {[
              { model: 'XGBoost Classifier', acc: '97.4%', status: 'active' },
              { model: 'Isolation Forest', acc: '94.1%', status: 'active' },
              { model: 'LSTM Sequence', acc: '91.8%', status: 'active' },
            ].map((m, i) => (
              <div key={i} className={`flex items-center justify-between py-2 border-b last:border-0 ${
                isDark ? 'border-white/[0.04]' : 'border-slate-50'
              }`}>
                <div>
                  <div className={`text-xs font-medium ${
                    isDark ? 'text-slate-300' : 'text-slate-700'
                  }`}>{m.model}</div>
                  <div className={`text-[10px] mt-0.5 ${
                    isDark ? 'text-slate-600' : 'text-slate-400'
                  }`}>Accuracy: {m.acc}</div>
                </div>
                <div className={`flex items-center space-x-1.5 text-[10px] font-bold px-2 py-1 rounded-lg ${
                  isDark ? 'bg-emerald-500/10 text-emerald-400' : 'bg-emerald-50 text-emerald-600'
                }`}>
                  <div className="status-dot-online" style={{ width: 5, height: 5 }} />
                  <span>LIVE</span>
                </div>
              </div>
            ))}
          </div>

          {/* Raw Hex Terminal */}
          <div className={`flex flex-col flex-1 overflow-hidden rounded-2xl border ${
            isDark ? 'bg-[#03030A] border-white/[0.06]' : 'bg-slate-900 border-slate-700'
          }`}>
            <div className={`px-4 py-3 border-b flex justify-between items-center shrink-0 ${
              isDark ? 'border-white/[0.06] bg-[#08080F]' : 'border-slate-700'
            }`}>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono">Raw Hex Stream</span>
              <Terminal size={12} className="text-slate-600" />
            </div>
            <div
              ref={terminalRef}
              className="flex-1 p-3 overflow-y-auto custom-scrollbar font-mono text-[10px] leading-relaxed"
            >
              {packets.map((p: any, i: number) => (
                <div key={i} className={`mb-0.5 ${
                  p.risk > 75 ? 'text-red-500' : 'text-slate-600'
                }`}>
                  <span className="text-slate-700 mr-2">{p.id?.split('_')[1] ?? i.toString().padStart(4,'0')}</span>
                  <span>{p.hex?.slice(0, 8).join(' ') ?? '-- -- -- -- -- -- -- --'}</span>
                  <span className="text-slate-800"> ...</span>
                </div>
              ))}
              {packets.length === 0 && (
                <div className="text-slate-700">Waiting for capture feed<span className="animate-blink">_</span></div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
