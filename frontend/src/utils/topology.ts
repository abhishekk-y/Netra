import cytoscape from 'cytoscape';

export const getDeviceColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'firewall': return '#ef4444'; // red
    case 'router': return '#3b82f6'; // blue
    case 'switch': return '#8b5cf6'; // purple
    case 'server': return '#10b981'; // emerald
    case 'workstation': return '#64748b'; // slate
    default: return '#a1a1aa'; // zinc
  }
};

export const getRiskColor = (risk: number) => {
  if (risk >= 80) return '#ef4444'; // red
  if (risk >= 60) return '#f97316'; // orange
  if (risk >= 40) return '#f59e0b'; // amber
  return '#10b981'; // emerald
};

export const defaultStylesheet: cytoscape.StylesheetJson = [
  {
    selector: 'node',
    style: {
      'background-color': '#1f2937',
      'border-width': 2,
      'border-color': (ele) => getDeviceColor(ele.data('type')),
      'label': 'data(label)',
      'color': '#f3f4f6',
      'font-size': '10px',
      'font-family': 'monospace',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'text-margin-y': 4,
      'width': 30,
      'height': 30,
      'shape': (ele) => {
        const type = ele.data('type');
        if (type === 'firewall') return 'rectangle';
        if (type === 'server') return 'barrel';
        if (type === 'router') return 'diamond';
        return 'ellipse';
      }
    }
  },
  {
    selector: 'node[risk >= 60]',
    style: {
      'background-color': (ele) => getRiskColor(ele.data('risk')),
      'border-color': '#fff',
      'color': '#fff',
      'text-background-color': '#000',
      'text-background-opacity': 0.7,
      'text-background-padding': '2px',
      'text-background-shape': 'roundrectangle'
    }
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#10b981',



    }
  },
  {
    selector: 'edge',
    style: {
      'width': (ele: cytoscape.EdgeSingular) => Math.max(1, Math.min(5, ele.data('weight') / 100)),
      'line-color': '#3f3f46',
      'target-arrow-color': '#3f3f46',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'opacity': 0.6
    }
  },
  {
    selector: 'edge[isAttackPath]',
    style: {
      'line-color': '#ef4444',
      'target-arrow-color': '#ef4444',
      'width': 3,
      'opacity': 1,
      'z-index': 10
    }
  },
  {
    selector: 'edge[isForecastPath]',
    style: {
      'line-color': '#f59e0b',
      'target-arrow-color': '#f59e0b',
      'line-style': 'dashed',
      'width': 2,
      'opacity': 0.8,
      'z-index': 9
    }
  }
];

export const getLayoutConfig = (mode: string) => {
  switch (mode) {
    case 'hierarchical':
      return { name: 'breadthfirst', directed: true, spacingFactor: 1.5 };
    case 'radial':
      return { name: 'concentric', minNodeSpacing: 50 };
    case 'tree':
      return { name: 'breadthfirst', directed: true, grid: true };
    case 'force':
    default:
      return { name: 'cose', idealEdgeLength: 100, nodeOverlap: 20, refresh: 20, fit: true, padding: 30, randomize: false, componentSpacing: 100, nodeRepulsion: 400000, edgeElasticity: 100, nestingFactor: 5 };
  }
};


