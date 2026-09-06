import { create } from 'zustand';

interface AppState {
  sidebarCollapsed: boolean;
  activePage: string;
  theme: 'dark';
  platformName: string;
  performanceProfile: 'high' | 'balanced' | 'power-saver';
  toggleSidebar: () => void;
  setActivePage: (page: string) => void;
  setPlatformName: (name: string) => void;
  setPerformanceProfile: (profile: 'high' | 'balanced' | 'power-saver') => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: false,
  activePage: '/',
  theme: 'dark',
  platformName: 'NETRA-X',
  performanceProfile: 'high',
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setActivePage: (page) => set({ activePage: page }),
  setPlatformName: (name) => set({ platformName: name }),
  setPerformanceProfile: (profile) => set({ performanceProfile: profile }),
}));
