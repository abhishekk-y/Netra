import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { Network, Server, Shield, HardDrive, Terminal } from 'lucide-react';

export default function TopologyPage() {
  const container = useRef<HTMLDivElement>(null);
  const cy = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  
  const { data: graph } = useQuery({
    queryKey: ['topologyGraph'],
    queryFn: () => apiService.getTopologyGraph()
  });

  const topologyUpdates = useTelemetryStore(s => s.topologyUpdates);

  useEffect(() => {
    if (!container.current || !graph) return;

    const instance = cytoscape({
      container: container.current,
      elements: [...graph.nodes, ...graph.edges],
      layout: { name: 'cose', animate: true, animationDuration: 1000, nodeRepulsion: 400000, idealEdgeLength: 60 } as any,
      minZoom: 0.1, maxZoom: 3,
      style: [
        {
          selector: 'node',
          style: {
            'shape': 'ellipse',
            'width': 28, 'height': 28,
            'background-color': '#fff',
            'border-width': 2,
            'border-color': '#cbd5e1',
            'label': 'data(label)',
            'color': '#475569',
            'font-size': 8,
            'font-family': 'Inter, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'shadow-blur': 10,
            'shadow-color': 'rgba(0,0,0,0.1)'
          } as any
        },
        {
          selector: 'node[type = "CORE"]', style: { 'border-color': '#00bceb', 'width': 40, 'height': 40, 'border-width': 3 }
        },
        {
          selector: 'node[type = "FIREWALL"]', style: { 'border-color': '#f6821f', 'shape': 'roundrectangle' }
        },
        {
          selector: 'node[risk >= 75]', style: { 'border-color': '#ef4444', 'background-color': '#fee2e2', 'border-width': 3 }
        },
        {
          selector: 'node:selected', style: { 'border-width': 4, 'border-color': '#6366f1', 'shadow-blur': 20, 'shadow-color': 'rgba(99,102,241,0.4)' } as any
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5, 'line-color': '#e2e8f0', 'curve-style': 'bezier',
            'target-arrow-shape': 'none'
          }
        },
        {
          selector: 'edge[type = "TRUNK"]', style: { 'width': 3, 'line-color': '#94a3b8' }
        },
        {
          selector: 'edge:selected', style: { 'line-color': '#6366f1', 'width': 2.5 }
        }
      ]
    });

    cy.current = instance;
    instance.on('tap', 'node', (e) => setSelectedNode(e.target.data()));
    instance.on('tap', (e) => { if(e.target === instance) setSelectedNode(null); });
    return () => { instance.destroy(); cy.current = null; };
  }, [graph]);

  useEffect(() => {
    if (!cy.current || topologyUpdates.length === 0) return;
    const latest = topologyUpdates[0];
    const node = cy.current.getElementById(latest.nodeId);
    
    if (node && node.length > 0) {
      node.data('risk', latest.newRisk);
      node.style('background-color', '#fff1f2'); // flash red/pink
      setTimeout(() => {
        if (cy.current) node.removeStyle('background-color');
      }, 300);
      if (selectedNode && selectedNode.id === latest.nodeId) {
        setSelectedNode(node.data());
      }
    }
  }, [topologyUpdates]);

  return (
    <div className="h-full bg-white rounded-xl shadow-sm border border-slate-200 relative overflow-hidden flex">
      
      {/* DOT GRID BACKGROUND */}
      <div className="flex-1 relative z-10" ref={container} style={{ backgroundImage: 'radial-gradient(#e2e8f0 1px, transparent 0)', backgroundSize: '24px 24px' }}></div>
      
      {/* HEADER OVERLAY */}
      <div className="absolute top-6 left-6 z-20 glass-panel px-4 py-2 rounded-lg flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-slate-800 font-semibold"><Network size={16} className="text-[#00bceb]" /> <span>Global Network Map</span></div>
        <div className="h-5 w-px bg-slate-200"></div>
        <div className="flex space-x-4 text-xs font-medium text-slate-500">
          <span className="flex items-center"><div className="w-2.5 h-2.5 rounded-full bg-[#00bceb] mr-1.5 border border-white"></div> Core</span>
          <span className="flex items-center"><div className="w-2.5 h-2.5 rounded-full bg-[#f6821f] mr-1.5 border border-white"></div> Firewall</span>
          <span className="flex items-center"><div className="w-2.5 h-2.5 rounded-full bg-red-500 mr-1.5 border border-white"></div> Critical Risk</span>
        </div>
      </div>

      {/* INSPECTION SIDEBAR */}
      <div className={`absolute top-0 right-0 h-full w-96 bg-white/95 backdrop-blur-xl border-l border-slate-200 z-30 transition-transform duration-300 shadow-2xl flex flex-col ${selectedNode ? 'translate-x-0' : 'translate-x-full'}`}>
        {selectedNode && (
          <>
            <div className="h-20 border-b border-slate-100 flex items-center px-6 shrink-0 bg-slate-50/50">
              <div className="w-10 h-10 rounded-full bg-[#00bceb]/10 flex items-center justify-center mr-4">
                <Server size={20} className="text-[#00bceb]" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-slate-800 text-lg">{selectedNode.label}</span>
                <span className="text-slate-500 text-sm font-medium">{selectedNode.ip}</span>
              </div>
              <div className="ml-auto">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${selectedNode.risk > 75 ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'}`}>
                  Risk: {selectedNode.risk.toFixed(1)}
                </span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
              
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center"><HardDrive size={14} className="mr-2"/> Hardware Specifications</h3>
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-100 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-slate-500 text-sm">Model</span>
                    <span className="font-medium text-slate-800 text-sm">{selectedNode.model}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 text-sm">Firmware</span>
                    <span className="font-medium text-slate-800 text-sm">{selectedNode.fw}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center"><Shield size={14} className="mr-2"/> Vulnerability Matrix</h3>
                {selectedNode.risk > 50 ? (
                  <div className="space-y-2">
                    {[
                      { cve: 'CVE-2024-3094', score: 10.0, desc: 'RCE via SSH payload' },
                      { cve: 'CVE-2023-48795', score: 5.9, desc: 'Terrapin SSH attack' }
                    ].map(v => (
                      <div key={v.cve} className="bg-white border border-slate-200 rounded-lg p-3 hover:border-red-200 hover:shadow-sm transition-all cursor-pointer">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-slate-800 font-semibold text-sm">{v.cve}</span>
                          <span className="text-red-700 bg-red-100 px-2 py-0.5 rounded text-xs font-bold">{v.score}</span>
                        </div>
                        <span className="text-slate-500 text-sm">{v.desc}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-100 text-emerald-700 text-sm font-medium flex items-center">
                    <Shield size={16} className="mr-2"/> No active vulnerabilities
                  </div>
                )}
              </div>

              <button className="w-full bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 text-slate-700 font-medium p-3 rounded-lg flex items-center justify-center space-x-2 transition-all shadow-sm">
                <Terminal size={16} /> <span>Open Remote Console</span>
              </button>

            </div>
          </>
        )}
      </div>

    </div>
  );
}
