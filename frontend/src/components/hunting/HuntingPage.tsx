import React from 'react';
import { PanelGroup, Panel as ResizablePanel, PanelResizeHandle } from 'react-resizable-panels';
import { FilterBar } from '../common/FilterBar';
import { Panel } from '../common/Panel';
import ReactECharts from 'echarts-for-react';

export const HuntingPage: React.FC = () => {
  const timeOption = {
    grid: { top: 10, right: 10, bottom: 20, left: 40 },
    xAxis: { type: 'category', data: ['10:00', '11:00', '12:00', '13:00', '14:00'], axisLine: { lineStyle: { color: '#52525b' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#27272a' } } },
    series: [{ data: [120, 200, 150, 80, 70], type: 'bar', itemStyle: { color: '#3b82f6' } }]
  };

  return (
    <div className="flex flex-col h-full p-4 bg-transparent">
      <FilterBar placeholder="Enter investigation query (e.g. protocol == 'ssh' and bytes > 1000)..." onSearch={() => {}} />
      
      <div className="flex-1 overflow-hidden p-2">
        <PanelGroup direction="vertical" className="gap-2">
          
          <ResizablePanel defaultSize={50} minSize={30}>
            <PanelGroup direction="horizontal" className="gap-2">
              <ResizablePanel defaultSize={40} minSize={20}>
                <Panel title="Timeline Distribution" className="h-full">
                  <ReactECharts option={timeOption} style={{ height: '100%', width: '100%' }} />
                </Panel>
              </ResizablePanel>
              <ResizablePanel defaultSize={60} minSize={30}>
                <Panel title="Results" className="h-full">
                  <div className="flex items-center justify-center h-full text-gray-500 font-mono text-sm">
                    Enter query to see results
                  </div>
                </Panel>
              </ResizablePanel>
            </PanelGroup>
          </ResizablePanel>

          <ResizablePanel defaultSize={50} minSize={30}>
            <PanelGroup direction="horizontal" className="gap-2">
              <ResizablePanel defaultSize={50} minSize={20}>
                <Panel title="Related Topology" className="h-full">
                  <div className="flex items-center justify-center h-full text-gray-500 font-mono text-sm">
                    No nodes matched in current scope
                  </div>
                </Panel>
              </ResizablePanel>
              <ResizablePanel defaultSize={50} minSize={20}>
                <Panel title="Facets" className="h-full">
                  <div className="grid grid-cols-2 gap-4">
                     <div>
                       <h4 className="text-xs font-semibold text-gray-400 mb-2 border-b border-gray-800 pb-1">Protocols</h4>
                       <div className="text-sm font-mono text-gray-500">No data</div>
                     </div>
                     <div>
                       <h4 className="text-xs font-semibold text-gray-400 mb-2 border-b border-gray-800 pb-1">Src IPs</h4>
                       <div className="text-sm font-mono text-gray-500">No data</div>
                     </div>
                  </div>
                </Panel>
              </ResizablePanel>
            </PanelGroup>
          </ResizablePanel>
          
        </PanelGroup>
      </div>
    </div>
  );
};

export default HuntingPage;
