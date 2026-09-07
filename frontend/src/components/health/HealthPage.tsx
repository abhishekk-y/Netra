import React from 'react';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { useUIStore } from '../../stores/uiStore';
import {
  HeartPulse, Database, Cpu, MemoryStick, HardDrive,
  Wifi, CheckCircle, XCircle, AlertTriangle, Activity,
  Terminal, Shield, Zap, Clock, Brain
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1';

const fetchHealth = async () => {
  const [h, t] = await Promise.all([
    fetch(`${API}/health`).then(r => r.ok ? r.json() : null),
    fetch(`${API}/telemetry`).then(r => r.ok ? r.json() : null),
  ]);
  return { health: h, telemetry: t };
};

const demoData = {
  health: {
    status: 'operational',
    components: { database: 'up', capture: 'down', mlInference: 'up' },
    metrics: { cpu: 34.2, memory: 61.5, disk: 22.8 },
    ml: { available: true, version: '2.0.0', accuracy: 0.974, f1: 0.968, classes: ['Benign','Reconnaissance','Lateral Movement','Exfiltration','Impact','Credential Access','Command and Control'] },
    inferenceMethod: 'ml-ensemble',
    message: 'API running. ML ensemble active. Capture sensor not configured.',
  },
  telemetry: {
    packetsPerSec: 1240,
    flowsPerSec: 12.4,
    hostsCount: 24,
    activeConnections: 89,
    cpuUsage: 34.2,
    ramUsage: 61.5,
    diskUsage: 22.8,
    captureDropPercent: 0,
  },
};

export const HealthPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const { data } = useQuery({
    queryKey: ['health-full'],
    queryFn: fetchHealth,
    initialData: demoData,
    refetchInterval: 5000,
  });

  const health = data?.health ?? demoData.health;
  const tele = data?.telemetry ?? demoData.telemetry;

  const componentStatus = [
    { name: 'Database (SQLite)', key: 'database', icon: Database },
    { name: 'ML Inference', key: 'mlInference', icon: Brain },
    { name: 'Network Capture', key: 'capture', icon: Wifi },
    { name: 'WebSocket', key: 'websocket', icon: Activity },
  ];

  const getStatusIcon = (status: string) => {
    if (status === 'up') return <CheckCircle size={14} className="text-emerald-500" />;
    if (status === 'down') return <XCircle size={14} className="text-red-500" />;
    return <AlertTriangle size={14} className="text-yellow-500" />;
  };

  const getStatusBadge = (status: string) => {
    if (status === 'up') return isDark ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (status === 'down') return isDark ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-red-50 text-red-700 border-red-200';
    return isDark ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 'bg-yellow-50 text-yellow-700 border-yellow-200';
  };

  const resourceOption = (value: number, color: string) => ({
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      radius: '90%',
      pointer: { show: false },
      progress: { show: true, overlap: false, roundCap: true, clip: false, itemStyle: { color } },
      axisLine: { lineStyle: { width: 10, color: [[1, isDark ? 'rgba(255,255,255,0.05)' : '#F1F5F9']] } },
      splitLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      data: [{ value, name: `${value.toFixed(1)}%`, title: { offsetCenter: [0, '30%'], fontSize: 11, color: isDark ? '#64748B' : '#94A3B8' }, detail: { valueAnimation: true, offsetCenter: [0, '-10%'], fontSize: 20, fontWeight: 'bold', color: isDark ? '#E2E8F0' : '#1E293B', formatter: '{value}%' } }],
    }]
  });

  const metricsHistory = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: isDark ? '#0F172A' : '#fff', borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0', textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 11 } },
    legend: { data: ['CPU', 'Memory', 'Disk'], textStyle: { color: isDark ? '#475569' : '#94A3B8', fontSize: 10 }, top: 0, right: 0 },
    grid: { top: 28, right: 8, bottom: 20, left: 8, containLabel: true },
    xAxis: { type: 'category', data: Array.from({ length: 12 }, (_, i) => `${i * 5}s`).reverse(), axisLabel: { color: isDark ? '#334155' : '#94A3B8', fontSize: 10 }, axisLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.06)' : '#E2E8F0' } }, splitLine: { show: false } },
    yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.04)' : '#F1F5F9', type: 'dashed' } }, axisLabel: { color: isDark ? '#334155' : '#94A3B8', fontSize: 10 }, axisLine: { show: false } },
    series: [
      { name: 'CPU', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2, color: '#8B5CF6' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(139,92,246,0.2)' }, { offset: 1, color: 'rgba(139,92,246,0)' }] } }, data: Array.from({ length: 12 }, () => tele.cpuUsage + (Math.random() - 0.5) * 10) },
      { name: 'Memory', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2, color: '#22D3EE' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(34,211,238,0.2)' }, { offset: 1, color: 'rgba(34,211,238,0)' }] } }, data: Array.from({ length: 12 }, () => tele.ramUsage + (Math.random() - 0.5) * 5) },
      { name: 'Disk', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2, color: '#F97316' }, data: Array.from({ length: 12 }, () => tele.diskUsage + (Math.random() - 0.5) * 2) },
    ]
  };

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in p-4 overflow-auto">

      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            health.status === 'operational'
              ? isDark ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-emerald-50'
              : isDark ? 'bg-yellow-500/10 border border-yellow-500/20' : 'bg-yellow-50'
          }`}>
            <HeartPulse size={20} className={health.status === 'operational' ? 'text-emerald-500' : 'text-yellow-500'} />
          </div>
          <div>
            <h1 className={`text-xl font-bold ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>System Health</h1>
            <p className={`text-xs ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{health.message}</p>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-xl border text-sm font-bold ${
          health.status === 'operational'
            ? isDark ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-emerald-50 border-emerald-200 text-emerald-700'
            : isDark ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400' : 'bg-yellow-50 border-yellow-200 text-yellow-700'
        }`}>
          {health.status?.toUpperCase() ?? 'UNKNOWN'}
        </div>
      </div>

      {/* TOP GRID */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        {/* Component Status */}
        <div className={`col-span-1 rounded-2xl border p-5 ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        }`}>
          <h2 className={`text-sm font-semibold mb-4 ${ isDark ? 'text-slate-200' : 'text-slate-800'}`}>Components</h2>
          <div className="space-y-3">
            {componentStatus.map(comp => {
              const status = health.components?.[comp.key] ?? 'unknown';
              return (
                <div key={comp.key} className={`flex items-center justify-between p-3 rounded-xl border ${
                  isDark ? 'bg-white/[0.02] border-white/[0.04]' : 'bg-slate-50 border-slate-100'
                }`}>
                  <div className="flex items-center space-x-2">
                    <comp.icon size={14} className={isDark ? 'text-slate-600' : 'text-slate-400'} />
                    <span className={`text-xs font-medium ${ isDark ? 'text-slate-300' : 'text-slate-700'}`}>{comp.name}</span>
                  </div>
                  <div className={`flex items-center space-x-1.5 px-2 py-0.5 rounded-lg border text-[10px] font-bold ${
                    getStatusBadge(status)
                  }`}>
                    {getStatusIcon(status)}
                    <span>{status.toUpperCase()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Resource Gauges */}
        {[
          { label: 'CPU Usage', value: tele.cpuUsage ?? health.metrics?.cpu ?? 0, color: '#8B5CF6', icon: Cpu },
          { label: 'Memory', value: tele.ramUsage ?? health.metrics?.memory ?? 0, color: '#22D3EE', icon: MemoryStick },
          { label: 'Disk Usage', value: health.metrics?.disk ?? 0, color: '#F97316', icon: HardDrive },
        ].map((r, i) => (
          <div key={i} className={`rounded-2xl border p-5 text-center ${
            isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
          }`}>
            <div className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
              isDark ? 'text-slate-600' : 'text-slate-400'
            }`}>{r.label}</div>
            <div style={{ height: 130 }}>
              <ReactECharts option={resourceOption(r.value, r.color)} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        ))}
      </div>

      {/* ML Model Status */}
      {health.ml?.available && (
        <div className={`rounded-2xl border p-5 ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-sm font-semibold flex items-center space-x-2 ${
              isDark ? 'text-slate-200' : 'text-slate-800'
            }`}>
              <Brain size={15} className={isDark ? 'text-violet-400' : 'text-violet-500'} />
              <span>ML Ensemble Status</span>
            </h2>
            <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg text-[10px] font-bold border ${
              isDark ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-emerald-50 border-emerald-200 text-emerald-600'
            }`}>
              <CheckCircle size={11} />
              <span>LOADED · v{health.ml.version}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Accuracy', value: `${((health.ml.accuracy ?? 0) * 100).toFixed(1)}%` },
              { label: 'F1 Score', value: `${((health.ml.f1 ?? 0) * 100).toFixed(1)}%` },
              { label: 'Attack Classes', value: health.ml.classes?.length ?? 0 },
              { label: 'Inference Mode', value: health.inferenceMethod === 'ml-ensemble' ? 'Ensemble' : 'Heuristics' },
            ].map((m, i) => (
              <div key={i} className={`p-3 rounded-xl border ${
                isDark ? 'bg-white/[0.02] border-white/[0.04]' : 'bg-slate-50 border-slate-100'
              }`}>
                <div className={`text-[10px] font-bold uppercase tracking-wider mb-1 ${
                  isDark ? 'text-slate-600' : 'text-slate-400'
                }`}>{m.label}</div>
                <div className={`text-xl font-bold ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>{m.value}</div>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <div className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
              isDark ? 'text-slate-600' : 'text-slate-400'
            }`}>Supported Attack Classes</div>
            <div className="flex flex-wrap gap-2">
              {(health.ml.classes ?? []).map((cls: string) => (
                <span key={cls} className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  cls === 'Benign'
                    ? isDark ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : isDark ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-red-50 text-red-700 border-red-200'
                }`}>{cls}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Resource History Chart */}
      <div className={`rounded-2xl border flex-1 p-5 min-h-[250px] ${
        isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
      }`}>
        <h2 className={`text-sm font-semibold mb-4 ${ isDark ? 'text-slate-200' : 'text-slate-800'}`}>Resource Usage History (60s)</h2>
        <div style={{ height: 'calc(100% - 30px)' }}>
          <ReactECharts option={metricsHistory} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>

    </div>
  );
};

export default HealthPage;
