import React from 'react';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { useUIStore } from '../../stores/uiStore';
import {
  Eye, Target, Brain, ChevronRight, AlertTriangle,
  TrendingUp, Activity, Clock, Cpu, Shield
} from 'lucide-react';

const API = 'http://localhost:8000/api/v1';

const KILL_CHAIN = [
  'Reconnaissance',
  'Initial Access',
  'Execution',
  'Persistence',
  'Privilege Escalation',
  'Defense Evasion',
  'Credential Access',
  'Discovery',
  'Lateral Movement',
  'Collection',
  'Command & Control',
  'Exfiltration',
  'Impact',
];

const demoForecast = {
  id: 'f1',
  currentStage: 'Reconnaissance',
  stageConfidence: 0.87,
  sourceIp: '10.42.0.10',
  nextStages: [
    { stage: 'Initial Access', probability: 0.55 },
    { stage: 'Lateral Movement', probability: 0.30 },
    { stage: 'Impact', probability: 0.15 },
  ],
  targetPredictions: [
    { hostId: 'h1', ip: '10.42.0.20', probability: 0.68, hostname: 'web-server' },
    { hostId: 'h2', ip: '10.42.0.21', probability: 0.22, hostname: 'file-server' },
    { hostId: 'h3', ip: '10.42.0.30', probability: 0.10, hostname: 'db-server' },
  ],
  method: 'heuristic-transition-rules',
  explanation: 'Port scan activity detected from 10.42.0.10. Rapid fan-out to 12 destination ports within 5 minutes is consistent with automated reconnaissance tooling.',
  timestamp: new Date().toISOString(),
};

function stageColor(stage: string, isDark: boolean): string {
  const map: Record<string, string> = {
    'Reconnaissance': isDark ? 'text-yellow-400' : 'text-yellow-600',
    'Initial Access': isDark ? 'text-orange-400' : 'text-orange-600',
    'Lateral Movement': isDark ? 'text-red-400' : 'text-red-600',
    'Exfiltration': isDark ? 'text-red-500' : 'text-red-700',
    'Impact': isDark ? 'text-red-600' : 'text-red-800',
    'Command & Control': isDark ? 'text-purple-400' : 'text-purple-600',
    'Credential Access': isDark ? 'text-orange-400' : 'text-orange-600',
  };
  return map[stage] ?? (isDark ? 'text-slate-400' : 'text-slate-600');
}

function stageBg(stage: string, isDark: boolean): string {
  const map: Record<string, string> = {
    'Reconnaissance': isDark ? 'bg-yellow-500/10 border-yellow-500/20' : 'bg-yellow-50 border-yellow-200',
    'Initial Access': isDark ? 'bg-orange-500/10 border-orange-500/20' : 'bg-orange-50 border-orange-200',
    'Lateral Movement': isDark ? 'bg-red-500/10 border-red-500/20' : 'bg-red-50 border-red-200',
    'Exfiltration': isDark ? 'bg-red-600/10 border-red-600/20' : 'bg-red-100 border-red-300',
    'Impact': isDark ? 'bg-red-700/10 border-red-700/20' : 'bg-red-100 border-red-300',
  };
  return map[stage] ?? (isDark ? 'bg-slate-500/10 border-slate-500/20' : 'bg-slate-50 border-slate-200');
}

export const ForecastPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const { data: forecast } = useQuery({
    queryKey: ['forecast'],
    queryFn: async () => {
      const res = await fetch(`${API}/forecast`);
      if (!res.ok) throw new Error('fail');
      return res.json();
    },
    initialData: demoForecast,
    refetchInterval: 5000,
  });

  const fc = forecast ?? demoForecast;
  const currentIdx = KILL_CHAIN.indexOf(fc.currentStage);

  const gaugeOption = {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      radius: '100%',
      center: ['50%', '80%'],
      min: 0,
      max: 100,
      splitNumber: 4,
      axisLine: {
        lineStyle: {
          width: 12,
          color: [
            [0.3, isDark ? '#334155' : '#E2E8F0'],
            [0.6, isDark ? '#F59E0B' : '#D97706'],
            [0.8, isDark ? '#F97316' : '#EA580C'],
            [1, isDark ? '#EF4444' : '#DC2626'],
          ]
        }
      },
      pointer: {
        length: '65%',
        width: 4,
        itemStyle: { color: isDark ? '#E2E8F0' : '#1E293B' }
      },
      splitLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      detail: {
        valueAnimation: true,
        formatter: (v: number) => `${v.toFixed(0)}%`,
        color: isDark ? '#E2E8F0' : '#1E293B',
        fontSize: 20,
        fontWeight: 'bold',
        offsetCenter: [0, '-15%'],
      },
      data: [{ value: fc.stageConfidence * 100 }],
    }]
  };

  const barOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: isDark ? '#0F172A' : '#fff', borderColor: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0', textStyle: { color: isDark ? '#e2e8f0' : '#1e293b', fontSize: 11 }, formatter: (p: any[]) => `${p[0].name}: ${(p[0].value * 100).toFixed(1)}%` },
    grid: { top: 8, right: 16, bottom: 0, left: 0, containLabel: true },
    xAxis: { type: 'value', max: 1, splitLine: { show: false }, axisLabel: { show: false }, axisLine: { show: false } },
    yAxis: { type: 'category', data: fc.nextStages.map((s: any) => s.stage).reverse(), axisLabel: { color: isDark ? '#94A3B8' : '#475569', fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false } },
    series: [{
      type: 'bar',
      data: fc.nextStages.map((s: any) => s.probability).reverse(),
      label: { show: true, position: 'right', formatter: (p: any) => `${(p.value * 100).toFixed(0)}%`, color: isDark ? '#94A3B8' : '#475569', fontSize: 11 },
      itemStyle: {
        color: (params: any) => {
          const colors = isDark
            ? ['#EF4444', '#F97316', '#F59E0B']
            : ['#DC2626', '#EA580C', '#D97706'];
          return colors[params.dataIndex % colors.length];
        },
        borderRadius: [0, 4, 4, 0],
      },
      barMaxWidth: 24,
      background: { show: true, itemStyle: { color: isDark ? 'rgba(255,255,255,0.03)' : '#F1F5F9', borderRadius: [0, 4, 4, 0] } },
    }]
  };

  return (
    <div className="h-full flex flex-col space-y-4 animate-fade-in p-4 overflow-auto">

      {/* HEADER */}
      <div className="flex items-center space-x-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          isDark ? 'bg-violet-500/10 border border-violet-500/20' : 'bg-violet-50'
        }`}>
          <Brain size={20} className={isDark ? 'text-violet-400' : 'text-violet-600'} />
        </div>
        <div>
          <h1 className={`text-xl font-bold ${ isDark ? 'text-slate-100' : 'text-slate-800'}`}>AI Attack Forecasting</h1>
          <p className={`text-xs ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>Real-time predictive threat intelligence · Method: {fc.method}</p>
        </div>
      </div>

      {/* TOP ROW: 3 cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Current Stage */}
        <div className={`rounded-2xl border p-5 ${
          isDark ? `bg-[#0A0A12] ${stageBg(fc.currentStage, isDark)}` : `bg-white ${stageBg(fc.currentStage, isDark)} shadow-sm`
        }`}>
          <div className={`text-[10px] font-bold uppercase tracking-widest mb-3 ${
            isDark ? 'text-slate-600' : 'text-slate-400'
          }`}>Current Attack Stage</div>
          <div className={`text-2xl font-bold mb-2 ${stageColor(fc.currentStage, isDark)}`}>
            {fc.currentStage}
          </div>
          <div style={{ height: 120 }}>
            <ReactECharts option={gaugeOption} style={{ height: '100%', width: '100%' }} />
          </div>
          <div className="mt-2 space-y-2">
            <div className={`flex items-center space-x-2 text-xs ${
              isDark ? 'text-slate-500' : 'text-slate-500'
            }`}>
              <Cpu size={11} />
              <span>Attacker: <code className={`font-mono ${ isDark ? 'text-cyan-400' : 'text-cyan-700'}`}>{fc.sourceIp}</code></span>
            </div>
            <div className={`flex items-center space-x-2 text-xs ${
              isDark ? 'text-slate-500' : 'text-slate-500'
            }`}>
              <Clock size={11} />
              <span>Detected at {new Date(fc.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        {/* Next Stage Predictions */}
        <div className={`rounded-2xl border p-5 ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        }`}>
          <div className={`text-[10px] font-bold uppercase tracking-widest mb-3 ${
            isDark ? 'text-slate-600' : 'text-slate-400'
          }`}>Predicted Next Stages</div>
          <div style={{ height: 160 }}>
            <ReactECharts option={barOption} style={{ height: '100%', width: '100%' }} />
          </div>
          <div className={`mt-3 text-[10px] ${ isDark ? 'text-slate-700' : 'text-slate-400'}`}>
            ⚠ Heuristic transition weights · Not a calibrated probability model
          </div>
        </div>

        {/* Target Predictions */}
        <div className={`rounded-2xl border p-5 ${
          isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
        }`}>
          <div className={`text-[10px] font-bold uppercase tracking-widest mb-3 ${
            isDark ? 'text-slate-600' : 'text-slate-400'
          }`}>Predicted Target Hosts</div>
          <div className="space-y-4">
            {fc.targetPredictions.map((t: any, i: number) => (
              <div key={t.hostId}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <div className={`w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold ${
                      i === 0
                        ? isDark ? 'bg-red-500/20 text-red-400' : 'bg-red-50 text-red-600'
                        : isDark ? 'bg-white/[0.05] text-slate-500' : 'bg-slate-100 text-slate-500'
                    }`}>{i + 1}</div>
                    <div>
                      <div className={`text-xs font-semibold ${ isDark ? 'text-slate-200' : 'text-slate-800'}`}>{t.hostname}</div>
                      <div className={`font-mono text-[10px] ${ isDark ? 'text-slate-600' : 'text-slate-400'}`}>{t.ip}</div>
                    </div>
                  </div>
                  <span className={`text-xs font-bold ${
                    t.probability > 0.5
                      ? isDark ? 'text-red-400' : 'text-red-600'
                      : isDark ? 'text-orange-400' : 'text-orange-600'
                  }`}>{(t.probability * 100).toFixed(0)}%</span>
                </div>
                <div className={`h-1.5 rounded-full overflow-hidden ${
                  isDark ? 'bg-white/[0.05]' : 'bg-slate-100'
                }`}>
                  <div
                    className={`h-full rounded-full ${
                      i === 0 ? 'bg-red-500' : i === 1 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${t.probability * 100}%`, transition: 'width 1s ease' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* KILL CHAIN TIMELINE */}
      <div className={`rounded-2xl border p-5 ${
        isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
      }`}>
        <div className={`text-[10px] font-bold uppercase tracking-widest mb-4 ${
          isDark ? 'text-slate-600' : 'text-slate-400'
        }`}>MITRE ATT&CK Kill Chain Progress</div>
        <div className="flex items-center space-x-1 overflow-x-auto custom-scrollbar pb-2">
          {KILL_CHAIN.map((stage, idx) => {
            const isCurrent = idx === currentIdx;
            const isPast = idx < currentIdx;
            const isPredicted = fc.nextStages.some((s: any) => s.stage === stage);
            const predProb = fc.nextStages.find((s: any) => s.stage === stage)?.probability ?? 0;

            return (
              <div key={stage} className="flex items-center shrink-0">
                <div className={`px-3 py-2 rounded-xl text-center border transition-all ${
                  isCurrent
                    ? isDark
                      ? 'bg-red-500/20 border-red-500/40 shadow-[0_0_12px_rgba(239,68,68,0.3)]'
                      : 'bg-red-50 border-red-300 shadow-sm shadow-red-100'
                    : isPast
                      ? isDark ? 'bg-white/[0.04] border-white/[0.08]' : 'bg-slate-100 border-slate-200'
                      : isPredicted
                        ? isDark
                          ? 'bg-orange-500/10 border-orange-500/20 border-dashed'
                          : 'bg-orange-50 border-orange-200 border-dashed'
                        : isDark ? 'bg-transparent border-white/[0.04]' : 'bg-transparent border-slate-100'
                }`}>
                  <div className={`text-[9px] font-bold uppercase tracking-wider whitespace-nowrap ${
                    isCurrent
                      ? isDark ? 'text-red-400' : 'text-red-700'
                      : isPast
                        ? isDark ? 'text-slate-500' : 'text-slate-400'
                        : isPredicted
                          ? isDark ? 'text-orange-400' : 'text-orange-600'
                          : isDark ? 'text-slate-700' : 'text-slate-300'
                  }`}>
                    {isCurrent && <span className="mr-1">▶</span>}
                    {isPredicted && !isCurrent && <span className="mr-1">◈</span>}
                    {stage}
                  </div>
                  {isPredicted && !isCurrent && (
                    <div className={`text-[9px] font-bold mt-0.5 ${ isDark ? 'text-orange-500' : 'text-orange-600'}`}>
                      {(predProb * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
                {idx < KILL_CHAIN.length - 1 && (
                  <div className={`h-px w-3 mx-0.5 ${
                    isPast || isCurrent
                      ? isDark ? 'bg-red-500/40' : 'bg-red-200'
                      : isDark ? 'bg-white/[0.06]' : 'bg-slate-200'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
        <div className="flex items-center space-x-6 mt-3">
          {[
            { color: isDark ? 'bg-red-500/20 border-red-500/40' : 'bg-red-50 border-red-300', label: 'Current Stage', border: 'border' },
            { color: isDark ? 'bg-orange-500/10 border-orange-500/20' : 'bg-orange-50 border-orange-200', label: 'Predicted Next', border: 'border border-dashed' },
            { color: isDark ? 'bg-white/[0.04] border-white/[0.08]' : 'bg-slate-100 border-slate-200', label: 'Observed / Past', border: 'border' },
          ].map((l, i) => (
            <div key={i} className="flex items-center space-x-2 text-[10px]">
              <div className={`w-5 h-3 rounded-sm ${l.color} ${l.border}`} />
              <span className={isDark ? 'text-slate-600' : 'text-slate-400'}>{l.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Explanation */}
      <div className={`rounded-2xl border p-5 ${
        isDark ? 'bg-[#0A0A12] border-white/[0.06]' : 'bg-white border-slate-100 shadow-sm'
      }`}>
        <div className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
          isDark ? 'text-slate-600' : 'text-slate-400'
        }`}>Forecast Reasoning</div>
        <p className={`text-sm leading-relaxed ${ isDark ? 'text-slate-400' : 'text-slate-600'}`}>{fc.explanation}</p>
      </div>

    </div>
  );
};

export default ForecastPage;
