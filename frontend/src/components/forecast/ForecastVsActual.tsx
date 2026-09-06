import React from 'react';
import ReactECharts from 'echarts-for-react';

export const ForecastVsActual: React.FC = () => {
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#a1a1aa' } },
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: ['T-50m', 'T-40m', 'T-30m', 'T-20m', 'T-10m', 'Now'],
      axisLine: { lineStyle: { color: '#52525b' } }
    },
    yAxis: {
      type: 'value',
      name: 'Stage Progression (1-5)',
      splitLine: { lineStyle: { color: '#27272a' } },
      min: 0,
      max: 5
    },
    series: [
      {
        name: 'Actual Progression',
        type: 'step',
        data: [1, 1, 2, 2, 3, 3],
        itemStyle: { color: '#ef4444' },
        lineStyle: { width: 2 }
      },
      {
        name: 'AI Forecast',
        type: 'line',
        data: [1, 2, 2, 3, 4, 4],
        itemStyle: { color: '#f59e0b' },
        lineStyle: { type: 'dashed', width: 2 }
      }
    ]
  };

  return (
    <div className="w-full h-full">
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
    </div>
  );
};
