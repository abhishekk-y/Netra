import React from 'react';
import { PanelGroup, Panel as ResizablePanel, PanelResizeHandle } from 'react-resizable-panels';
import { FilterBar } from '../common/FilterBar';
import { Panel } from '../common/Panel';
import ReactECharts from 'echarts-for-react';

export const HuntingPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const timeOption = {
    backgroundColor: 'transparent',
    grid: { top: 20, right: 20, bottom: 20, left: 40 },
    xAxis: { type: 'category', data: ['10:00', '11:00', '12:00', '13:00', '14:00'], axisLine: { lineStyle: { color: isDark ? '#333' : '#cbd5e1' } }, axisLabel: { color: isDark ? '#888' : '#64748b', fontFamily: 'Outfit' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: isDark ? '#222' : '#f1f5f9' } }, axisLabel: { color: isDark ? '#888' : '#64748b', fontFamily: 'Outfit' } },
    series: [{ 
      data: [120, 200, 150, 80, 70], 
      type: 'bar', 
      itemStyle: { 
        color: isDark ? '#3b82f6' : '#00bceb',
        borderRadius: [4, 4, 0, 0]
      } 
    }]
  };

  return (
    <div className="flex flex-col h-full p-6 bg-transparent gap-6">
      <div className="shrink-0">
        <FilterBar placeholder="Enter investigation query (e.g. protocol == 'ssh' and bytes > 1000)..." onSearch={() => {}} />
      </div>
      
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="vertical" className="gap-6">
          
          <ResizablePanel defaultSize={45} minSize={30}>
            <PanelGroup direction="horizontal" className="gap-6">
              <ResizablePanel defaultSize={35} minSize={20}>
                <Panel title="Timeline Distribution" className="h-full">
                  <ReactECharts option={timeOption} style={{ height: '100%', width: '100%' }} />
                </Panel>
              </ResizablePanel>
              <ResizablePanel defaultSize={65} minSize={30}>
                <Panel title="Results" className="h-full">
                  <div className={`flex items-center justify-center h-full font-mono text-sm uppercase tracking-widest ${isDark ? 'text-[#444]' : 'text-slate-300'}`}>
                    Enter query to see results
                  </div>
                </Panel>
              </ResizablePanel>
            </PanelGroup>
          </ResizablePanel>

          <ResizablePanel defaultSize={55} minSize={30}>
            <PanelGroup direction="horizontal" className="gap-6">
              <ResizablePanel defaultSize={60} minSize={20}>
                <Panel title="Related Topology" className="h-full">
                  <div className={`flex items-center justify-center h-full font-mono text-sm uppercase tracking-widest ${isDark ? 'text-[#444]' : 'text-slate-300'}`}>
                    No nodes matched in current scope
                  </div>
                </Panel>
              </ResizablePanel>
              <ResizablePanel defaultSize={40} minSize={20}>
                <Panel title="Facets" className="h-full">
                  <div className="grid grid-cols-2 gap-6 p-2">
                     <div className={`p-4 rounded-xl border ${isDark ? 'bg-[#111] border-[#222]' : 'bg-slate-50 border-slate-100'}`}>
                       <h4 className={`text-xs font-bold uppercase tracking-widest mb-3 pb-2 border-b ${isDark ? 'text-gray-500 border-[#333]' : 'text-slate-400 border-slate-200'}`}>Protocols</h4>
                       <div className={`text-sm font-mono font-medium ${isDark ? 'text-gray-600' : 'text-slate-400'}`}>No data</div>
                     </div>
                     <div className={`p-4 rounded-xl border ${isDark ? 'bg-[#111] border-[#222]' : 'bg-slate-50 border-slate-100'}`}>
                       <h4 className={`text-xs font-bold uppercase tracking-widest mb-3 pb-2 border-b ${isDark ? 'text-gray-500 border-[#333]' : 'text-slate-400 border-slate-200'}`}>Src IPs</h4>
                       <div className={`text-sm font-mono font-medium ${isDark ? 'text-gray-600' : 'text-slate-400'}`}>No data</div>
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
