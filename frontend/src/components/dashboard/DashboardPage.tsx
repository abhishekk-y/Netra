import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Panel } from '../common/Panel';
import { DataTable } from '../common/DataTable';
import { Badge } from '../common/Badge';
import { RiskIndicator } from '../common/RiskIndicator';
import { useTelemetryStore } from '../../stores/telemetryStore';

export const DashboardPage: React.FC = () => {
  const telemetry = useTelemetryStore();
  const hasTelemetry = telemetry.packetsPerSec > 0 || telemetry.hostsCount > 0;

  // Mock data for initial render until hooked to API properly
  const mockRiskHosts = [
    { id: '1', ip: '192.168.1.45', name: 'USER-DESKTOP-1', risk: 85.4, alerts: 12 },
    { id: '2', ip: '10.0.0.5', name: 'DB-PROD-01', risk: 72.1, alerts: 4 },
    { id: '3', ip: '192.168.1.102', name: 'DEV-SERVER', risk: 45.0, alerts: 1 },
  ];

  const mockIncidents = [
    { id: 'INC-001', stage: 'Lateral Movement', severity: 'critical', time: '10m ago' },
    { id: 'INC-002', stage: 'Reconnaissance', severity: 'medium', time: '1h ago' },
  ];

  const trafficOption = {
    tooltip: { trigger: 'axis' },
    grid: { top: 10, right: 10, bottom: 20, left: 40 },
    xAxis: { type: 'category', data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25'], axisLine: { lineStyle: { color: '#52525b' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#27272a' } } },
    series: [{ data: [820, 932, 901, 934, 1290, 1330], type: 'line', smooth: true, areaStyle: { color: 'rgba(16, 185, 129, 0.2)' }, itemStyle: { color: '#10b981' } }]
  };

  const protocolOption = {
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center', textStyle: { color: '#a1a1aa' } },
    series: [
      {
        name: 'Protocols',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: '#18181b', borderWidth: 2 },
        label: { show: false },
        data: [
          { value: 1048, name: 'TCP' },
          { value: 735, name: 'UDP' },
          { value: 580, name: 'ICMP' },
          { value: 484, name: 'DNS' },
          { value: 300, name: 'TLS' }
        ]
      }
    ]
  };

  return (
    <div className="flex-1 overflow-auto bg-gray-950 p-2 custom-scrollbar">
      <div className="grid grid-cols-12 gap-2 h-full">
        
        {/* Row 1: Top Stats */}
        <div className="col-span-12 grid grid-cols-5 gap-2 h-20">
          {[
            { label: 'ACTIVE INCIDENTS', value: hasTelemetry ? '2' : '0', color: 'text-red-500' },
            { label: 'FORECAST RISK', value: hasTelemetry ? 'HIGH' : 'NONE', color: 'text-orange-500' },
            { label: 'TOTAL HOSTS', value: telemetry.hostsCount, color: 'text-emerald-500' },
            { label: 'NETWORK SESSIONS', value: telemetry.activeConnections, color: 'text-blue-500' },
            { label: 'CRITICAL ALERTS', value: hasTelemetry ? '14' : '0', color: 'text-red-500' },
          ].map((stat, i) => (
            <Panel key={i} title={stat.label} className="justify-center">
              <div className={`text-2xl font-mono font-bold text-center ${stat.color}`}>
                {stat.value}
              </div>
            </Panel>
          ))}
        </div>

        {/* Row 2 */}
        <div className="col-span-8 h-64">
          <Panel title="Traffic Analysis (bps)" noPadding>
            {!hasTelemetry ? (
              <div className="w-full h-full flex items-center justify-center text-gray-600 font-mono text-sm">NO TELEMETRY</div>
            ) : (
              <ReactECharts option={trafficOption} style={{ height: '100%', width: '100%' }} />
            )}
          </Panel>
        </div>
        <div className="col-span-4 h-64">
          <Panel title="Forecast Summary">
            {!hasTelemetry ? (
              <div className="w-full h-full flex items-center justify-center text-gray-600 font-mono text-sm">NO ACTIVE FORECASTS</div>
            ) : (
              <div className="flex flex-col gap-4">
                <div className="bg-gray-800/50 border border-red-500/20 p-3 rounded">
                  <h4 className="text-red-400 font-mono text-xs mb-1">PREDICTED NEXT STAGE</h4>
                  <div className="text-lg font-bold text-gray-100">Exfiltration</div>
                  <div className="w-full bg-gray-900 h-2 mt-2 rounded overflow-hidden">
                    <div className="bg-red-500 h-full w-[85%]" />
                  </div>
                  <div className="text-xs text-gray-400 mt-1 font-mono">85% Probability • Est. T+5m</div>
                </div>
                <div>
                  <h4 className="text-gray-400 font-mono text-xs mb-2">TOP TARGETS</h4>
                  <div className="flex justify-between items-center text-sm mb-1">
                    <span className="font-mono text-gray-300">10.0.0.5</span>
                    <span className="text-red-400">92%</span>
                  </div>
                  <div className="flex justify-between items-center text-sm mb-1">
                    <span className="font-mono text-gray-300">10.0.0.8</span>
                    <span className="text-orange-400">64%</span>
                  </div>
                </div>
              </div>
            )}
          </Panel>
        </div>

        {/* Row 3 */}
        <div className="col-span-6 h-64">
          <Panel title="Top Risk Hosts" noPadding>
            <DataTable
              data={hasTelemetry ? mockRiskHosts : []}
              keyExtractor={(h) => h.id}
              columns={[
                { key: 'ip', header: 'IP ADDRESS', render: (h) => <span className="font-mono text-blue-400">{h.ip}</span> },
                { key: 'name', header: 'HOSTNAME' },
                { key: 'alerts', header: 'ALERTS', align: 'center' },
                { key: 'risk', header: 'RISK SCORE', render: (h) => <RiskIndicator score={h.risk} size="sm" showLabel />, align: 'right' },
              ]}
            />
          </Panel>
        </div>
        <div className="col-span-6 h-64">
          <Panel title="Active Incidents" noPadding>
            <DataTable
              data={hasTelemetry ? mockIncidents : []}
              keyExtractor={(i) => i.id}
              columns={[
                { key: 'id', header: 'ID', render: (i) => <span className="font-mono">{i.id}</span> },
                { key: 'stage', header: 'STAGE' },
                { key: 'severity', header: 'SEVERITY', render: (i) => <Badge variant={i.severity as any}>{i.severity}</Badge> },
                { key: 'time', header: 'UPDATED', align: 'right', render: (i) => <span className="text-gray-500">{i.time}</span> },
              ]}
            />
          </Panel>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;
