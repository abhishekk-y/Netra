import { create } from 'zustand';
import type { TopologyNode, TopologyEdge } from '../types';

interface TopologyState {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  selectedNodeId: string | null;
  viewMode: 'physical' | 'l2' | 'l3' | 'logical' | 'security' | 'attack' | 'forensic' | 'forecast';
  layoutMode: 'hierarchical' | 'force' | 'radial' | 'tree';
  setTopology: (nodes: TopologyNode[], edges: TopologyEdge[]) => void;
  setSelectedNode: (id: string | null) => void;
  setViewMode: (mode: TopologyState['viewMode']) => void;
  setLayoutMode: (mode: TopologyState['layoutMode']) => void;
}

export const useTopologyStore = create<TopologyState>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  viewMode: 'security',
  layoutMode: 'force',
  setTopology: (nodes, edges) => set({ nodes, edges }),
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setLayoutMode: (mode) => set({ layoutMode: mode }),
}));
