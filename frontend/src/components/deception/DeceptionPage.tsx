import React from 'react';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { useUIStore } from '../../stores/uiStore';
import { Bug, Terminal, Crosshair } from 'lucide-react';

const fetchHoneypots = async () => {
  const res = await fetch('http://localhost:8000/api/v1/deception/honeypots');
  if (!res.ok) return { honeypots: [] };
  return res.json();
};

const DeceptionPage: React.FC = () => {
  const honeypotEvents = useTelemetryStore(s => s.honeypotEvents);
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const { data } = useQuery({
    queryKey: ['honeypots'],
    queryFn: fetchHoneypots
  });
  
  const honeypots = data?.honeypots || [];

  const scatterOption = {
    backgroundColor: 'transparent',
    tooltip: { show: false },
    grid: { top: 30, right: 30, bottom: 30, left: 30 },
    xAxis: { type: 'value', min: 0, max: 100, splitLine: { show: true, lineStyle: { color: isDark ? '#222' : '#f1f5f9' } }, axisLabel: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { show: true, lineStyle: { color: isDark ? '#222' : '#f1f5f9' } }, axisLabel: { show: false }, axisTick: { show: false } },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: any) => Math.min(30, Math.max(10, data[2] / 2)),
        itemStyle: {
          color: (params: any) => params.data[3] ? (isDark ? '#ef4444' : '#ef4444') : (isDark ? '#3b82f6' : '#00bceb'),
          shadowBlur: 15,
          shadowColor: (params: any) => params.data[3] ? 'rgba(239,68,68,0.4)' : (isDark ? 'rgba(59,130,246,0.4)' : 'rgba(0,188,235,0.4)')
        },
        data: honeypots.map((h: any) => [h.x, h.y, h.value, h.isHuman])
      }
    ]
  };

  return (
    <div className={`h-full flex flex-col space-y-6 ${isDark ? 'bg-black text-gray-200' : 'bg-transparent text-slate-800'}`}>
      
      {/* HEADER */}
      <div className={`rounded-2xl shadow-sm border p-6 flex justify-between items-center transition-all duration-300 ${isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border-[#333]' : 'bg-white/80 backdrop-blur-md border-slate-200'}`}>
        <div>
          <h1 className="text-2xl font-bold flex items-center tracking-tight">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mr-4 shadow-sm ${isDark ? 'bg-orange-500/10' : 'bg-orange-50 border border-orange-100'}`}>
              <Bug className={isDark ? "text-orange-500" : "text-[#f6821f]"} size={22} />
            </div>
            Deception Grid Analytics
          </h1>
          <p className={`text-sm mt-2 font-medium ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>Live monitoring of active honeypots and decoy engagements across all VLANs.</p>
        </div>
        <div className="flex space-x-10">
          <div className="text-right">
            <div className={`text-xs font-semibold uppercase tracking-wider mb-1 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>Active Traps</div>
            <div className={`text-3xl font-bold tracking-tight ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>{honeypots.length}</div>
          </div>
          <div className="text-right">
            <div className={`text-xs font-semibold uppercase tracking-wider mb-1 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>Total Engagements</div>
            <div className={`text-3xl font-bold tracking-tight ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>{(12402 + honeypotEvents.length).toLocaleString()}</div>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden space-x-6">
        
        {/* LEFT COLUMN: Decoy Map */}
        <div className={`flex-1 rounded-2xl shadow-sm border flex flex-col overflow-hidden relative transition-all duration-300 hover:shadow-md ${isDark ? 'bg-[#050505] border-[#333]' : 'bg-white border-slate-200'}`}>
          <div className={`p-5 border-b flex justify-between items-center ${isDark ? 'border-[#333] bg-[#111]' : 'border-slate-100 bg-slate-50'}`}>
            <h2 className={`font-bold ${isDark ? 'text-gray-300 font-mono text-sm uppercase' : 'text-slate-800'}`}>Decoy Interaction Map (VLAN 99)</h2>
            <div className={`text-xs font-semibold px-3 py-1 rounded-full ${isDark ? 'bg-[#222] text-gray-400' : 'bg-white border border-slate-200 text-slate-500 shadow-sm'}`}>Live</div>
          </div>
          <div className={`flex-1 relative p-4 ${!isDark ? 'bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] opacity-80' : ''}`}>
            <ReactECharts option={scatterOption} style={{ height: '100%', width: '100%' }} />
            
            {/* Overlay Legend */}
            <div className={`absolute top-6 left-6 px-5 py-3 rounded-xl shadow-lg border backdrop-blur-md ${isDark ? 'bg-[#111]/80 border-[#333]' : 'bg-white/90 border-slate-200'}`}>
              <div className="flex items-center space-x-3 mb-3 text-sm font-semibold">
                <div className={`w-3.5 h-3.5 rounded-full shadow-sm ${isDark ? 'bg-blue-500' : 'bg-[#00bceb]'}`}></div>
                <span className={isDark ? 'text-gray-300' : 'text-slate-700'}>Automated Scanner</span>
              </div>
              <div className="flex items-center space-x-3 text-sm font-semibold">
                <div className="w-3.5 h-3.5 bg-red-500 rounded-full shadow-sm shadow-red-500/50"></div>
                <span className={isDark ? 'text-gray-300' : 'text-slate-700'}>Targeted Human</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Efficacy & Logs */}
        <div className="w-[420px] flex flex-col space-y-6 shrink-0">
          
          <div className={`rounded-2xl shadow-sm border overflow-hidden transition-all duration-300 hover:shadow-md ${isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border-[#333]' : 'bg-white border-slate-200'}`}>
            <div className={`p-5 border-b flex justify-between items-center ${isDark ? 'border-[#333]' : 'border-slate-100'}`}>
              <h2 className={`font-bold ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>Trap Efficacy Metrics</h2>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDark ? 'bg-blue-500/10' : 'bg-blue-50'}`}>
                <Crosshair size={16} className={isDark ? 'text-blue-500' : 'text-[#00bceb]'} />
              </div>
            </div>
            <div className="p-6 space-y-6">
               <div>
                 <div className="flex justify-between text-sm font-semibold mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>Time to Compromise (Avg)</span><span className={isDark ? 'text-gray-100' : 'text-slate-800'}>4.2 secs</span></div>
                 <div className={`h-2.5 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className="h-full bg-orange-500 w-[12%] rounded-full"></div></div>
               </div>
               <div>
                 <div className="flex justify-between text-sm font-semibold mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>Payloads Captured (24h)</span><span className={isDark ? 'text-gray-100' : 'text-slate-800'}>1,402</span></div>
                 <div className={`h-2.5 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className={`h-full w-[84%] rounded-full ${isDark ? 'bg-blue-500' : 'bg-[#00bceb]'}`}></div></div>
               </div>
               <div>
                 <div className="flex justify-between text-sm font-semibold mb-2"><span className={isDark ? 'text-gray-400' : 'text-slate-500'}>Zero-Day Heuristics Triggered</span><span className={isDark ? 'text-gray-100' : 'text-slate-800'}>3</span></div>
                 <div className={`h-2.5 w-full rounded-full overflow-hidden ${isDark ? 'bg-[#222]' : 'bg-slate-100'}`}><div className="h-full bg-red-500 w-[98%] rounded-full shadow-[0_0_10px_rgba(239,68,68,0.8)]"></div></div>
               </div>
            </div>
          </div>

          <div className={`rounded-2xl shadow-sm border flex-1 flex flex-col overflow-hidden transition-all duration-300 ${isDark ? 'bg-[#0A0A0A] border-[#333]' : 'bg-white border-slate-200'}`}>
            <div className={`p-5 border-b flex justify-between items-center ${isDark ? 'border-[#333] bg-[#111]' : 'border-slate-100 bg-slate-50'}`}>
              <h2 className={`font-bold ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>Active Engagement Log</h2>
              <Terminal size={16} className={isDark ? "text-gray-500" : "text-slate-400"} />
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
              <table className="w-full text-left whitespace-nowrap text-sm">
                <thead className={isDark ? "text-[#666]" : "text-slate-400"}>
                  <tr>
                    <th className="p-3 font-semibold uppercase tracking-wider text-xs">Time</th>
                    <th className="p-3 font-semibold uppercase tracking-wider text-xs">Attacker IP</th>
                    <th className="p-3 font-semibold uppercase tracking-wider text-xs">Action</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${isDark ? 'divide-[#222]' : 'divide-slate-50/50'}`}>
                  {honeypotEvents.map((log: any, i: number) => (
                    <tr key={i} className={`transition-colors rounded-xl ${isDark ? 'hover:bg-[#111]' : 'hover:bg-slate-50 hover:shadow-sm'}`}>
                      <td className={`p-3 rounded-l-xl ${isDark ? 'text-[#555]' : 'text-slate-400 font-medium'}`}>{log.t}</td>
                      <td className={`p-3 font-semibold ${isDark ? 'text-gray-300' : 'text-slate-700'}`}>{log.src}</td>
                      <td className={`p-3 rounded-r-xl ${isDark ? 'text-gray-400' : 'text-slate-600 font-medium'}`}>
                        <span className={`px-2 py-1 rounded-md text-xs font-bold ${
                          log.action.includes('Shell') || log.action.includes('Command') 
                            ? (isDark ? 'bg-red-950/40 text-red-400' : 'bg-red-50 text-red-600') 
                            : (isDark ? 'bg-[#222] text-gray-300' : 'bg-slate-100 text-slate-600')
                        }`}>
                          {log.action}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default DeceptionPage;
