import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { Activity, ShieldAlert, Wifi, Globe, Lock, Cpu, Server } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const telemetry = useTelemetryStore();
  const [timeSeriesData, setTimeSeriesData] = useState<{time: string, download: number, upload: number}[]>([]);

  // Simulate incoming ECharts data dynamically if telemetry updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeSeriesData(prev => {
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        // Base traffic on simulated telemetry flows to make it "live"
        const baseTraffic = telemetry.flowsPerSec > 0 ? telemetry.flowsPerSec / 100 : Math.random() * 5 + 5;
        const newPoint = {
          time: timeStr,
          download: baseTraffic * (Math.random() * 0.5 + 0.8),
          upload: (baseTraffic * 0.3) * (Math.random() * 0.5 + 0.8)
        };
        
        const next = [...prev, newPoint];
        if (next.length > 30) next.shift(); // Keep last 30 points
        return next;
      });
    }, 2000);
    return () => clearInterval(interval);
  }, [telemetry.flowsPerSec]);

  // Deep dark theme ECharts Config (Inspired by Mockup 1)
  const trafficOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: '#0B0F19', borderColor: '#1F2937', textStyle: { color: '#F3F4F6' } },
    legend: { data: ['Download', 'Upload'], textStyle: { color: '#9CA3AF' }, top: 0, right: 0 },
    grid: { top: 40, right: 10, bottom: 30, left: 40 },
    xAxis: { 
      type: 'category', 
      boundaryGap: false,
      data: timeSeriesData.map(d => d.time), 
      axisLine: { lineStyle: { color: '#1F2937' } },
      axisLabel: { color: '#6B7280', fontFamily: 'JetBrains Mono', fontSize: 10 }
    },
    yAxis: { 
      type: 'value', 
      splitLine: { lineStyle: { color: '#111827', type: 'dashed' } },
      axisLabel: { color: '#6B7280', fontFamily: 'JetBrains Mono', fontSize: 10, formatter: '{value} Gbps' }
    },
    series: [
      { 
        name: 'Download',
        data: timeSeriesData.map(d => d.download.toFixed(2)), 
        type: 'line', 
        smooth: true,
        showSymbol: false,
        areaStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(6,182,212,0.4)' }, { offset: 1, color: 'rgba(6,182,212,0)' }]
          }
        }, 
        itemStyle: { color: '#06b6d4' },
        lineStyle: { width: 2, shadowColor: 'rgba(6,182,212,0.5)', shadowBlur: 10 }
      },
      { 
        name: 'Upload',
        data: timeSeriesData.map(d => d.upload.toFixed(2)), 
        type: 'line', 
        smooth: true,
        showSymbol: false,
        areaStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(139,92,246,0.4)' }, { offset: 1, color: 'rgba(139,92,246,0)' }]
          }
        }, 
        itemStyle: { color: '#8b5cf6' },
        lineStyle: { width: 2, shadowColor: 'rgba(139,92,246,0.5)', shadowBlur: 10 }
      }
    ]
  };

  // Radial Risk Score Gauge (Inspired by Mockup 3)
  const riskOption = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      radius: '100%',
      center: ['50%', '75%'],
      pointer: { show: false },
      progress: {
        show: true,
        overlap: false,
        roundCap: true,
        clip: false,
        itemStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#06b6d4' }, { offset: 0.5, color: '#f59e0b' }, { offset: 1, color: '#ef4444' }]
          }
        }
      },
      axisLine: { lineStyle: { width: 14, color: [[1, '#111827']] } },
      splitLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      data: [{ value: telemetry.hostsCount > 0 ? 68.4 : 12.0, name: 'Risk Score' }],
      title: { fontSize: 10, color: '#6B7280', offsetCenter: [0, '25%'] },
      detail: { width: 50, height: 14, fontSize: 32, color: '#F3F4F6', offsetCenter: [0, '-10%'], formatter: '{value}%', fontFamily: 'JetBrains Mono' }
    }]
  };

  return (
    <div className="p-4 md:p-6 h-full flex flex-col space-y-4 bg-[#0B0F19] overflow-y-auto custom-scrollbar">
      
      {/* Top Bar / Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] rounded-xl p-4 border border-white/5 flex justify-between items-center shadow-lg">
          <div>
            <div className="text-[#6B7280] text-xs font-medium mb-1">TOTAL ENDPOINTS</div>
            <div className="text-2xl font-mono text-white">{telemetry.hostsCount || 42} <span className="text-emerald-500 text-xs ml-2">▲ 6.4%</span></div>
          </div>
          <div className="w-10 h-10 rounded-full bg-cyan-500/10 flex items-center justify-center">
            <Server size={20} className="text-cyan-500" />
          </div>
        </div>
        
        <div className="bg-[#111827] rounded-xl p-4 border border-white/5 flex justify-between items-center shadow-lg">
          <div>
            <div className="text-[#6B7280] text-xs font-medium mb-1">NETWORK FLOWS/s</div>
            <div className="text-2xl font-mono text-white">{telemetry.flowsPerSec || 1204} <span className="text-emerald-500 text-xs ml-2">▲ 3.2%</span></div>
          </div>
          <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
            <Activity size={20} className="text-blue-500" />
          </div>
        </div>
        
        <div className="bg-[#111827] rounded-xl p-4 border border-white/5 flex justify-between items-center shadow-lg">
          <div>
            <div className="text-[#6B7280] text-xs font-medium mb-1">OPEN INCIDENTS</div>
            <div className="text-2xl font-mono text-white">4 <span className="text-red-500 text-xs ml-2">▲ 1 High</span></div>
          </div>
          <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
            <ShieldAlert size={20} className="text-red-500" />
          </div>
        </div>

        <div className="bg-[#111827] rounded-xl p-4 border border-white/5 flex justify-between items-center shadow-lg">
          <div>
            <div className="text-[#6B7280] text-xs font-medium mb-1">SENSOR UPTIME</div>
            <div className="text-2xl font-mono text-white">99.9%</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
            <Wifi size={20} className="text-emerald-500" />
          </div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-[350px]">
        
        {/* Large Traffic Area Chart (Span 2) */}
        <div className="bg-[#111827] rounded-xl border border-white/5 shadow-lg p-5 flex flex-col lg:col-span-2 relative overflow-hidden">
          <div className="flex justify-between items-center mb-4 z-10">
            <h3 className="text-white text-sm font-medium">Network Traffic (Bandwidth Usage)</h3>
            <div className="flex space-x-2">
              <span className="bg-white/5 text-gray-400 text-xs px-2 py-1 rounded">24H</span>
              <span className="bg-cyan-500/20 text-cyan-400 text-xs px-2 py-1 rounded border border-cyan-500/30">LIVE</span>
            </div>
          </div>
          <div className="flex-1 w-full min-h-[250px] z-10">
            <ReactECharts option={trafficOption} style={{ height: '100%', width: '100%' }} />
          </div>
          {/* Subtle Glow Background */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-cyan-500/5 blur-[100px] pointer-events-none"></div>
        </div>

        {/* Risk Score Radial Gauge */}
        <div className="bg-[#111827] rounded-xl border border-white/5 shadow-lg p-5 flex flex-col relative overflow-hidden">
          <h3 className="text-white text-sm font-medium mb-2">Current Security Risk Score</h3>
          <div className="flex-1 flex flex-col items-center justify-center z-10">
             <div className="w-full h-48">
               <ReactECharts option={riskOption} style={{ height: '100%', width: '100%' }} />
             </div>
             <div className="mt-4 text-xs text-[#9CA3AF] text-center px-4 leading-relaxed">
               Failing security rating. Your systems are vulnerable, with multiple alerts requiring attention.
             </div>
          </div>
        </div>
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        {/* Alerts Table */}
        <div className="bg-[#111827] rounded-xl border border-white/5 shadow-lg overflow-hidden flex flex-col">
          <div className="p-4 border-b border-white/5 flex justify-between items-center">
            <h3 className="text-white text-sm font-medium">Top 5 Open Alerts by Severity</h3>
            <div className="relative">
              <input type="text" placeholder="Search Alerts" className="bg-[#0B0F19] text-xs text-white border border-white/10 rounded px-3 py-1.5 focus:outline-none focus:border-cyan-500" />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0B0F19] text-[#6B7280]">
                <tr>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Alert Name</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Source IP</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Severity</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {[
                  { name: 'Brute Force Attempt', ip: '192.168.1.45', sev: 'Critical', color: 'text-red-400 bg-red-400/10 border-red-400/20' },
                  { name: 'Suspicious Lateral Move', ip: '10.0.0.5', sev: 'High', color: 'text-orange-400 bg-orange-400/10 border-orange-400/20' },
                  { name: 'Malware Beaconing', ip: '192.168.56.20', sev: 'High', color: 'text-orange-400 bg-orange-400/10 border-orange-400/20' },
                  { name: 'Unusual Port Scan', ip: '10.0.0.12', sev: 'Medium', color: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20' },
                  { name: 'Multiple Failed Logins', ip: '192.168.1.100', sev: 'Low', color: 'text-blue-400 bg-blue-400/10 border-blue-400/20' },
                ].map((alert, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors group">
                    <td className="py-3 px-4 text-[#E5E7EB] font-medium">{alert.name}</td>
                    <td className="py-3 px-4 text-[#9CA3AF] font-mono">{alert.ip}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-[10px] border ${alert.color}`}>{alert.sev}</span>
                    </td>
                    <td className="py-3 px-4 text-[#9CA3AF]">
                      <button className="text-cyan-500 hover:text-cyan-400">Review</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* IP Metadata Table (Like Image 2) */}
        <div className="bg-[#111827] rounded-xl border border-white/5 shadow-lg overflow-hidden flex flex-col">
          <div className="p-4 border-b border-white/5 flex justify-between items-center">
            <h3 className="text-white text-sm font-medium">IP Metadata & Flow Ranking</h3>
            <span className="text-cyan-500 text-xs cursor-pointer">View All Flow Logs</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0B0F19] text-[#6B7280]">
                <tr>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Source IP</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Target IP</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Protocol</th>
                  <th className="py-3 px-4 font-medium uppercase tracking-wider">Tendency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {[
                  { src: '221.80.21.104', dst: '10.0.1.20', proto: 'TCP', tend: '+ 12%', up: true },
                  { src: '192.168.56.20', dst: '192.168.56.1', proto: 'UDP', tend: '- 8%', up: false },
                  { src: '10.45.1.22', dst: '8.8.8.8', proto: 'DNS', tend: '+ 2%', up: true },
                  { src: '221.80.21.104', dst: '10.0.1.21', proto: 'TCP', tend: '+ 15%', up: true },
                  { src: '172.16.0.4', dst: '172.16.0.255', proto: 'MDNS', tend: '- 4%', up: false },
                ].map((flow, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4 text-[#3B82F6] font-mono font-medium">{flow.src}</td>
                    <td className="py-3 px-4 text-[#9CA3AF] font-mono">{flow.dst}</td>
                    <td className="py-3 px-4 text-[#E5E7EB]">{flow.proto}</td>
                    <td className="py-3 px-4">
                      <span className={`font-mono ${flow.up ? 'text-red-400' : 'text-emerald-400'}`}>
                        {flow.up ? '▲' : '▼'} {flow.tend}
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
  );
};
