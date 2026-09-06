import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { useTopologyStore } from '../../stores/topologyStore';
import { defaultStylesheet, getLayoutConfig } from '../../utils/topology';

export const TopologyCanvas: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const { nodes, edges, layoutMode, setSelectedNode } = useTopologyStore();

  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: { nodes, edges },
      style: defaultStylesheet,
      layout: getLayoutConfig(layoutMode),
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.1
    });

    cyRef.current.on('tap', 'node', (evt) => {
      setSelectedNode(evt.target.id());
    });

    cyRef.current.on('tap', (evt) => {
      if (evt.target === cyRef.current) {
        setSelectedNode(null);
      }
    });

    return () => {
      cyRef.current?.destroy();
    };
  }, []);

  // Update elements when store data changes
  useEffect(() => {
    if (!cyRef.current) return;
    
    // Simplistic diffing for now (in production, use json diff or cy.add/remove)
    cyRef.current.elements().remove();
    cyRef.current.add({ nodes, edges });
    cyRef.current.layout(getLayoutConfig(layoutMode)).run();
    
  }, [nodes, edges, layoutMode]);

  return <div ref={containerRef} id="cy" className="bg-gray-950 w-full h-full" />;
};
