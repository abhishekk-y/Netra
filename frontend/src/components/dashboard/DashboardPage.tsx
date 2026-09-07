import React, { useEffect, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { useUIStore } from '../../stores/uiStore';
import { AlertCircle, Activity, Server, Shield, Database, ArrowUpRight, Network, Terminal } from 'lucide-react';

const DashboardPage: React.FC = () => {
  const telemetry = useTelemetryStore();
  const { theme } = useUIStore();
  const isDark = theme === 'dark';
  
  const terminalRef = useRef<HTMLDivElement>(null);
  const packets = telemetry.packets;

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [packets]);

  const currentAnomaly = packets.length > 0 ? packets[0].risk : 0;
  const isCritical = currentAnomaly > 75;

  // Cloudflare/Cisco style Chart
  const heroOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0', textStyle: { color: '#1e293b', fontSize: 12 } },
    grid: { top: 20, right: 20, bottom: 20, left: 40, containLabel: false },
    xAxis: { type: 'category', data: packets.slice().reverse().map((p: any) => p.time), axisLabel: { fontSize: 10, color: '#64748b' }, axisLine: { lineStyle: { color: '#cbd5e1' } }, splitLine: { show: true, lineStyle: { color: '#f1f5f9' } } },
    yAxis: [
      { type: 'value', max: 1500, splitLine: { lineStyle: { color: '#f1f5f9', type: 'solid' } }, axisLabel: { color: '#64748b', fontSize: 10 } },
      { type: 'value', max: 100, splitLine: { show: false }, axisLabel: { show: false } }
    ],
    series: [
      {
        name: 'Bandwidth (B)', type: 'line', smooth: true, yAxisIndex: 0,
        itemStyle: { color: '#00bceb' }, lineStyle: { width: 2, color: '#00bceb' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(0,188,235,0.2)' }, { offset: 1, color: 'rgba(0,188,235,0)' }]
          }
        },
        data: packets.slice().reverse().map((p: any) => p.len)
      },
      {
        name: 'AI Risk Score', type: 'line', step: 'middle', yAxisIndex: 1,
        itemStyle: { color: '#f6821f' }, lineStyle: { width: 2, type: 'dashed', color: '#f6821f' }, 
        data: packets.slice().reverse().map((p: any) => p.risk)
      }
    ]
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      
      {/* ALERT BANNER */}
      <div className={`rounded-lg p-4 flex items-center justify-between transition-colors shadow-sm ${isCritical ? 'bg-red-50 border border-red-200' : 'bg-white border border-slate-200'}`}>
        <div className="flex items-center space-x-3">
          <AlertCircle size={20} className={isCritical ? 'text-red-500 animate-pulse' : 'text-slate-400'} />
          <span className={`font-medium ${isCritical ? 'text-red-700' : 'text-slate-600'}`}>
            {isCritical ? 'CRITICAL: High probability threat detected by ML Ensemble' : 'System Normal: No active threats detected.'}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-sm font-medium">
          <span className="text-slate-500">Live AI Confidence:</span>
          <span className={`px-2 py-1 rounded text-white ${isCritical ? 'bg-red-500' : 'bg-emerald-500'}`}>
            {currentAnomaly.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* TOP ROW: KPIs */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: 'Active Connections', val: telemetry.activeConnections.toLocaleString(), icon: Activity, lightColor: 'text-[#00bceb]', darkColor: 'text-blue-500', lightBg: 'bg-blue-50', darkBg: 'bg-blue-500/10' },
          { label: 'Ingress Rate', val: `${(telemetry.netIo / 1000).toFixed(1)}k PPS`, icon: Network, lightColor: 'text-indigo-500', darkColor: 'text-purple-500', lightBg: 'bg-indigo-50', darkBg: 'bg-purple-500/10' },
          { label: 'Total Packets Scanned', val: '14.2B', icon: Database, lightColor: 'text-[#f6821f]', darkColor: 'text-orange-500', lightBg: 'bg-orange-50', darkBg: 'bg-orange-500/10' },
          { label: 'Active Honeypots', val: '30', icon: Shield, lightColor: 'text-emerald-500', darkColor: 'text-emerald-500', lightBg: 'bg-emerald-50', darkBg: 'bg-emerald-500/10' }
        ].map((k, i) => (
          <div key={i} className={`rounded-2xl p-5 flex items-center justify-between transition-all duration-300 hover:-translate-y-1 ${
            isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border border-[#333] hover:border-gray-600 hover:shadow-lg' 
                   : 'bg-white border border-slate-100 shadow-sm hover:shadow-md hover:border-slate-200'
          }`}>
            <div>
              <div className={`text-xs font-semibold uppercase tracking-wider mb-2 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>{k.label}</div>
              <div className={`text-3xl font-bold tracking-tight ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>{k.val}</div>
            </div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isDark ? k.darkBg : k.lightBg}`}>
              <k.icon size={22} className={isDark ? k.darkColor : k.lightColor} />
            </div>
          </div>
        ))}
      </div>

      <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
        
        {/* LEFT COLUMN: Main Chart & Metrics */}
        <div className="col-span-2 flex flex-col space-y-6 overflow-hidden">
          
          <div className={`rounded-2xl shadow-sm border p-5 flex-1 flex flex-col min-h-[300px] ${
            isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border-[#333]' : 'bg-white border-slate-100'
          }`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className={`text-lg font-semibold ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>Traffic Volume vs. AI Risk Forecasting</h2>
              <button className={`text-sm font-medium flex items-center hover:underline ${isDark ? 'text-blue-400' : 'text-[#00bceb]'}`}>View Report <ArrowUpRight size={16} className="ml-1"/></button>
            </div>
            <div className="flex-1 w-full relative">
               <ReactECharts option={heroOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          <div className={`rounded-2xl shadow-sm border overflow-hidden flex-1 flex flex-col ${
            isDark ? 'bg-[#0A0A0A] border-[#333]' : 'bg-white border-slate-100'
          }`}>
            <div className={`p-4 border-b ${isDark ? 'border-[#333] bg-[#111]' : 'border-slate-100 bg-slate-50'}`}>
              <h2 className={`font-semibold ${isDark ? 'text-gray-200 font-mono uppercase tracking-wider text-sm' : 'text-slate-800'}`}>Deep Packet Inspection Feed</h2>
            </div>
            <div className="flex-1 overflow-auto custom-scrollbar">
              <table className="w-full text-left whitespace-nowrap text-sm">
                <thead className={`sticky top-0 ${isDark ? 'bg-[#111] text-gray-500 border-b border-[#333]' : 'bg-white text-slate-500 border-b border-slate-100'}`}>
                  <tr>
                    <th className="p-3 font-medium">Time</th>
                    <th className="p-3 font-medium">Source IP</th>
                    <th className="p-3 font-medium">Dest IP</th>
                    <th className="p-3 font-medium">Protocol</th>
                    <th className="p-3 font-medium text-right">Risk Score</th>
                    <th className="p-3 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${isDark ? 'divide-[#222]' : 'divide-slate-100'}`}>
                  {packets.map((p: any, i: number) => (
                    <tr key={i} className={`transition-colors ${
                      p.status === 'DROP' ? (isDark ? 'bg-red-950/20 hover:bg-red-950/30' : 'bg-red-50/50 hover:bg-red-50') 
                                          : (isDark ? 'hover:bg-[#111]' : 'hover:bg-slate-50')
                    }`}>
                      <td className={`p-3 ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>{p.time}</td>
                      <td className={`p-3 font-medium ${isDark ? 'text-gray-300' : 'text-slate-700'}`}>{p.src}</td>
                      <td className={`p-3 ${isDark ? 'text-gray-300' : 'text-slate-700'}`}>{p.dst}</td>
                      <td className={`p-3 font-medium ${isDark ? 'text-blue-400' : 'text-[#00bceb]'}`}>{p.proto}</td>
                      <td className="p-3 text-right">
                        <span className={`font-semibold ${p.risk > 75 ? (isDark ? 'text-red-400' : 'text-red-600') : (isDark ? 'text-emerald-400' : 'text-emerald-600')}`}>{p.risk.toFixed(1)}</span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          p.status === 'DROP' ? (isDark ? 'bg-red-500/20 text-red-400 border border-red-500/20' : 'bg-red-100 text-red-700') 
                                              : (isDark ? 'bg-[#222] text-gray-400' : 'bg-slate-100 text-slate-600')
                        }`}>
                          {p.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN: Real-time Diagnostics & Raw Log */}
        <div className="col-span-1 flex flex-col space-y-6 overflow-hidden">
          
          {/* SNMP Panel */}
          <div className={`rounded-2xl shadow-sm border p-5 shrink-0 ${
            isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border-[#333]' : 'bg-white border-slate-100'
          }`}>
            <h2 className={`text-lg font-semibold mb-5 flex items-center ${isDark ? 'text-gray-100' : 'text-slate-800'}`}><Server size={18} className={`mr-2 ${isDark ? 'text-blue-500' : 'text-slate-400'}`}/> System Diagnostics</h2>
            <div className="space-y-5">
              <div>
                <div className="flex justify-between text-sm mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>CPU Usage</span><span className={`font-medium ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>{telemetry.cpuUsage.toFixed(1)}%</span></div>
                <div className={`h-2 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${telemetry.cpuUsage}%` }}></div></div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>Memory Allocation</span><span className={`font-medium ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>{telemetry.ramUsage.toFixed(1)}%</span></div>
                <div className={`h-2 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${telemetry.ramUsage}%` }}></div></div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>Disk Latency</span><span className={`font-medium ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>{telemetry.diskLatency.toFixed(1)}ms</span></div>
                <div className={`h-2 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className="h-full bg-orange-500 transition-all duration-300" style={{ width: `${Math.min(100, telemetry.diskLatency * 5)}%` }}></div></div>
              </div>
            </div>
          </div>

          {/* Raw Log */}
          <div className={`flex flex-col flex-1 overflow-hidden rounded-xl shadow-sm border ${isDark ? 'bg-[#020202] border-[#333]' : 'bg-white border-slate-200'}`}>
            <div className={`p-3 border-b flex justify-between items-center ${isDark ? 'border-[#333] bg-[#111]' : 'border-slate-100 bg-slate-50'}`}>
              <span className={`font-medium text-sm ${isDark ? 'text-gray-400' : 'text-slate-600'}`}>Raw Hex Stream</span>
              <Terminal size={14} className={isDark ? "text-purple-500" : "text-indigo-400"} />
            </div>
            <div ref={terminalRef} className={`flex-1 p-4 overflow-y-auto custom-scrollbar font-mono text-[10px] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {packets.map((p: any, i: number) => (
                <div key={i} className={`mb-1 ${p.risk > 75 ? (isDark ? 'text-red-400' : 'text-red-600') : (isDark ? 'text-slate-500' : 'text-slate-500')}`}>
                  <span className={isDark ? "text-slate-600 mr-2" : "text-slate-400 mr-2"}>{p.id.split('_')[1]}</span>{p.hex?.slice(0, 6).join(' ')} ...
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default DashboardPage;
