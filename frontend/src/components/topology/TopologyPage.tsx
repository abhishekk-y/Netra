import React, { useEffect } from 'react';
import { PanelGroup, Panel as ResizablePanel, PanelResizeHandle } from 'react-resizable-panels';
import { FilterBar } from '../common/FilterBar';
import { TopologyCanvas } from './TopologyCanvas';
import { NodeDetail } from './NodeDetail';
import { useTopologyStore } from '../../stores/topologyStore';

export const TopologyPage: React.FC = () => {
  const { setTopology, setViewMode, setLayoutMode, viewMode, layoutMode, selectedNodeId } = useTopologyStore();

  // Load mock initial data
  useEffect(() => {
    const mockNodes = [
      { data: { id: 'router', label: 'EDGE-RTR-01', type: 'router', risk: 10 } },
      { data: { id: 'fw', label: 'CORE-FW', type: 'firewall', risk: 20 } },
      { data: { id: 'sw1', label: 'DIST-SW-01', type: 'switch', risk: 15 } },
      { data: { id: 'srv1', label: 'WEB-PROD', type: 'server', risk: 85, isAttacked: true } },
      { data: { id: 'srv2', label: 'DB-PROD', type: 'server', risk: 65, isForecast: true } },
      { data: { id: 'ws1', label: 'USER-1', type: 'workstation', risk: 5 } },
    ];
    
    const mockEdges = [
      { data: { id: 'e1', source: 'router', target: 'fw', weight: 100, risk: 10 } },
      { data: { id: 'e2', source: 'fw', target: 'sw1', weight: 80, risk: 10 } },
      { data: { id: 'e3', source: 'sw1', target: 'srv1', weight: 50, risk: 90, isAttackPath: true } },
      { data: { id: 'e4', source: 'sw1', target: 'srv2', weight: 20, risk: 10 } },
      { data: { id: 'e5', source: 'sw1', target: 'ws1', weight: 5, risk: 5 } },
      { data: { id: 'e6', source: 'srv1', target: 'srv2', weight: 10, risk: 80, isForecastPath: true } }, // Forecast lateral movement
    ];

    setTopology(mockNodes, mockEdges);
  }, [setTopology]);

  const filters = (
    <div className="flex gap-4 items-center">
      <select 
        value={viewMode}
        onChange={(e) => setViewMode(e.target.value as any)}
        className="bg-gray-800 text-xs text-gray-200 border-none outline-none p-1 rounded cursor-pointer"
      >
        <option value="security">Security View</option>
        <option value="physical">Physical L1</option>
        <option value="l2">Data Link L2</option>
        <option value="l3">Network L3</option>
        <option value="attack">Attack Path View</option>
        <option value="forecast">Forecast View</option>
      </select>
      
      <select 
        value={layoutMode}
        onChange={(e) => setLayoutMode(e.target.value as any)}
        className="bg-gray-800 text-xs text-gray-200 border-none outline-none p-1 rounded cursor-pointer"
      >
        <option value="force">Force Directed</option>
        <option value="hierarchical">Hierarchical</option>
        <option value="radial">Radial</option>
        <option value="tree">Tree</option>
      </select>
    </div>
  );

  return (
    <div className="flex flex-col h-full w-full">
      <FilterBar placeholder="Search nodes by IP, hostname, or MAC..." onSearch={() => {}} filters={filters} />
      
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="horizontal">
          <ResizablePanel defaultSize={selectedNodeId ? 75 : 100} minSize={50}>
            <div className="w-full h-full relative">
              <TopologyCanvas />
              {/* Optional legend overlay could go here */}
            </div>
          </ResizablePanel>
          
          {selectedNodeId && (
            <>
              <PanelResizeHandle className="w-1 bg-gray-800 hover:bg-emerald-500/50 cursor-col-resize transition-colors" />
              <ResizablePanel defaultSize={25} minSize={20} maxSize={40}>
                <NodeDetail />
              </ResizablePanel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
};

export default TopologyPage;
