export interface Host {
  id: string;
  ip: string;
  hostname?: string;
  mac?: string;
  deviceType: 'router' | 'switch' | 'firewall' | 'server' | 'workstation' | 'iot' | 'unknown';
  os?: string;
  vendor?: string;
  riskScore: number;
  criticality: 'low' | 'medium' | 'high' | 'critical';
  firstSeen: string;
  lastSeen: string;
}

export interface HostDetail extends Host {
  openPorts: number[];
  protocols: string[];
  activeAlerts: Alert[];
  recentFlows: Flow[];
}

export interface Flow {
  id: string;
  timestamp: string;
  srcIp: string;
  srcPort: number;
  dstIp: string;
  dstPort: number;
  protocol: string;
  appProtocol?: string;
  packets: number;
  bytes: number;
  duration: number;
  riskScore: number;
  anomalyScore: number;
  attackType?: string;
}

export interface FlowDetail extends Flow {
  features: Record<string, number>;
  relatedAlerts: Alert[];
}

export interface Alert {
  id: string;
  timestamp: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  source: string;
  signature: string;
  srcIp: string;
  dstIp: string;
  protocol: string;
  mitreTactic?: string;
  mitreTechnique?: string;
  confidence: number;
  status: 'new' | 'acknowledged' | 'resolved';
}

export interface Incident {
  id: string;
  title: string;
  status: 'active' | 'investigating' | 'mitigated' | 'closed';
  severity: 'low' | 'medium' | 'high' | 'critical';
  stage: string;
  affectedHosts: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Forecast {
  id: string;
  timestamp: string;
  incidentId?: string;
  currentStage: string;
  stageConfidence: number;
  nextStages: { stage: string; probability: number }[];
  targetPredictions: { hostId: string; ip: string; probability: number }[];
}

export interface TopologyNode {
  data: {
    id: string;
    label: string;
    type: string;
    risk: number;
    hasAlert?: boolean;
    isAttacked?: boolean;
    isForecast?: boolean;
  };
  position?: { x: number; y: number };
}

export interface TopologyEdge {
  data: {
    id: string;
    source: string;
    target: string;
    weight: number;
    risk: number;
    isAttackPath?: boolean;
    isForecastPath?: boolean;
  };
}

export interface TopologyGraph {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface DashboardSummary {
  activeIncidents: number;
  criticalAlerts: number;
  forecastRiskLevel: 'low' | 'medium' | 'high' | 'critical';
  totalHosts: number;
  totalFlows: number;
}

export interface WSMessage {
  type: 'telemetry' | 'alert' | 'incident_update' | 'forecast_update' | 'topology_update';
  payload: any;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  components: {
    database: 'up' | 'down';
    capture: 'up' | 'down';
    inference: 'up' | 'down';
  };
  metrics: {
    cpu: number;
    memory: number;
    disk: number;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}
