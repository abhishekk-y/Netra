import { create } from 'zustand';
import type { Incident, Forecast } from '../types';

interface IncidentState {
  activeIncidents: Incident[];
  selectedIncident: Incident | null;
  forecastData: Forecast | null;
  setActiveIncidents: (incidents: Incident[]) => void;
  setSelectedIncident: (incident: Incident | null) => void;
  setForecastData: (forecast: Forecast | null) => void;
}

export const useIncidentStore = create<IncidentState>((set) => ({
  activeIncidents: [],
  selectedIncident: null,
  forecastData: null,
  setActiveIncidents: (incidents) => set({ activeIncidents: incidents }),
  setSelectedIncident: (incident) => set({ selectedIncident: incident }),
  setForecastData: (forecast) => set({ forecastData: forecast }),
}));
