import axios from 'axios';
import type { 
  DashboardSummary, Host, Flow, Alert, Incident, Forecast, 
  TopologyGraph, PaginatedResponse, SystemHealth
} from '../types';

export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Dashboard
  getDashboardSummary: () => api.get<DashboardSummary>('/dashboard/summary').then(res => res.data),
  
  // Hosts
  getHosts: () => api.get<PaginatedResponse<Host>>('/hosts', {params: {pageSize: 500}}).then(res => res.data),
  getHost: (id: string) => api.get<Host>(`/hosts/${id}`).then(res => res.data),
  
  // Topology
  getTopologyGraph: () => api.get<TopologyGraph>('/topology/graph').then(res => res.data),
  
  // Flows
  getFlows: () => api.get<PaginatedResponse<Flow>>('/flows', {params: {pageSize: 500}}).then(res => res.data),
  
  // Alerts
  getAlerts: () => api.get<PaginatedResponse<Alert>>('/alerts', {params: {pageSize: 500}}).then(res => res.data),
  
  // Incidents
  getIncidents: () => api.get<PaginatedResponse<Incident>>('/incidents', {params: {pageSize: 500}}).then(res => res.data),
  getIncident: (id: string) => api.get<Incident>(`/incidents/${id}`).then(res => res.data),
  
  // Forecast
  getCurrentForecast: () => api.get<Forecast>('/forecasts/current').then(res => res.data),
  
  // Health
  getHealth: () => api.get<SystemHealth>('/health').then(res => res.data),
};
