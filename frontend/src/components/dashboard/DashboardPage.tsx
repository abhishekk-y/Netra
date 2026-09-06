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

  const mockRiskHosts = [
    { id: '1', ip: '192.168.1.45', name: 'USER-DESKTOP-1', risk: 85.4, alerts: 12 },
    { id: '2', ip: '10.0.0.5', name: 'DB-PROD-01', risk: 72.1, alerts: 4 },
    { id: '3', ip: '192.168.1.102', name: 'DEV-SERVER', risk: 45.0, alerts: 1 },
    { id: '4', ip: '10.0.0.15', name: 'APP-SERVER-2', risk: 30.5, alerts: 0 },
  ];

  const mockIncidents = [
    { id: 'INC-001', stage: 'Lateral Movement', severity: 'critical', time: '10m ago' },
    { id: 'INC-002', stage: 'Reconnaissance', severity: 'medium', time: '1h ago' },
    { id: 'INC-003', stage: 'Initial Access', severity: 'high', time: '2h ago' },
  ];

  const chartTheme = {
    color: ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
    textStyle: { color: '#94a3b8' }
  };

  const trafficOption = {
    ...chartTheme,
    tooltip: { trigger: 'axis', backgroundColor: '#1e293b', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    grid: { top: 10, right: 10, bottom: 20, left: 40 },
    xAxis: { type: 'category', data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25'], axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1e293b' } } },
    series: [{ data: [820, 932, 901, 934, 1290, 1330], type: 'line', smooth: true, areaStyle: { color: 'rgba(6, 182, 212, 0.2)' }, itemStyle: { color: '#06b6d4' } }]
  };

  const protocolOption = {
    ...chartTheme,
    tooltip: { trigger: 'item', backgroundColor: '#1e293b', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    legend: { top: '5%', left: 'center', textStyle: { color: '#94a3b8' } },
    series: [
      {
        name: 'Protocols',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: '#0f172a', borderWidth: 2 },
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

  const attackStageOption = {
    ...chartTheme,
    tooltip: { trigger: 'axis', backgroundColor: '#1e293b', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    grid: { top: 10, right: 10, bottom: 20, left: 40 },
    xAxis: { type: 'category', data: ['Recon', 'Access', 'Execution', 'Lateral', 'Action'], axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1e293b' } } },
    series: [{
      data: [120, 200, 150, 80, 70],
      type: 'bar',
      itemStyle: { color: '#10b981' }
    }]
  };

  return (
    <div className="flex-1 overflow-auto bg-slate-900 p-2 custom-scrollbar">
      <div className="grid grid-cols-12 gap-2 h-full">
        
        {/* Row 1: Top Stats - 4 metric cards */}
        <div className="col-span-12 grid grid-cols-4 gap-2 h-20">
          {[
            { label: 'HOSTS', value: telemetry.hostsCount, color: 'text-cyan-400' },
            { label: 'ACTIVE FLOWS', value: telemetry.activeConnections, color: 'text-emerald-400' },
            { label: 'ALERTS', value: hasTelemetry ? '14' : '0', color: 'text-amber-500' },
            { label: 'RISK SCORE', value: hasTelemetry ? '85' : '0', color: 'text-red-500' },
          ].map((stat, i) => (
            <Panel key={i} title={stat.label} className="justify-center bg-slate-800 border-slate-700">
              <div className={`text-2xl font-mono font-bold text-center ${stat.color}`}>
                {stat.value}
              </div>
            </Panel>
          ))}
        </div>

        {/* Row 2: Charts */}
        <div className="col-span-12 lg:col-span-4 h-64">
          <Panel title="Traffic Rate (bps)" noPadding className="bg-slate-800 border-slate-700">
            <ReactECharts option={trafficOption} style={{ height: '100%', width: '100%' }} />
          </Panel>
        </div>
        <div className="col-span-12 lg:col-span-4 h-64">
          <Panel title="Protocol Distribution" noPadding className="bg-slate-800 border-slate-700">
            <ReactECharts option={protocolOption} style={{ height: '100%', width: '100%' }} />
          </Panel>
        </div>
        <div className="col-span-12 lg:col-span-4 h-64">
          <Panel title="Attack Stages" noPadding className="bg-slate-800 border-slate-700">
            <ReactECharts option={attackStageOption} style={{ height: '100%', width: '100%' }} />
          </Panel>
        </div>

        {/* Row 3: Tables */}
        <div className="col-span-12 lg:col-span-6 h-64">
          <Panel title="Top Risk Hosts" noPadding className="bg-slate-800 border-slate-700">
            <DataTable
              data={hasTelemetry ? mockRiskHosts : []}
              keyExtractor={(h) => h.id}
              columns={[
                { key: 'ip', header: 'IP ADDRESS', render: (h) => <span className="font-mono text-cyan-400">{h.ip}</span> },
                { key: 'name', header: 'HOSTNAME' },
                { key: 'alerts', header: 'ALERTS', align: 'center' },
                { key: 'risk', header: 'RISK SCORE', render: (h) => <RiskIndicator score={h.risk} size="sm" showLabel />, align: 'right' },
              ]}
            />
          </Panel>
        </div>
        <div className="col-span-12 lg:col-span-6 h-64">
          <Panel title="Latest Incidents" noPadding className="bg-slate-800 border-slate-700">
            <DataTable
              data={hasTelemetry ? mockIncidents : []}
              keyExtractor={(i) => i.id}
              columns={[
                { key: 'id', header: 'ID', render: (i) => <span className="font-mono text-slate-300">{i.id}</span> },
                { key: 'stage', header: 'STAGE' },
                { key: 'severity', header: 'SEVERITY', render: (i) => <Badge variant={i.severity as any}>{i.severity}</Badge> },
                { key: 'time', header: 'UPDATED', align: 'right', render: (i) => <span className="text-slate-500">{i.time}</span> },
              ]}
            />
          </Panel>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;
