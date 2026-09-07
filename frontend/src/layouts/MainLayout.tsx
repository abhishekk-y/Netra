import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { 
  Activity, Share2, ActivitySquare, AlertTriangle, ShieldAlert, 
  FastForward, Search, Crosshair, Server, Map, Settings,
  LogOut, Bell, User
} from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { wsService } from '../stores/telemetryStore';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Activity },
  { path: '/topology', label: 'Topology', icon: Share2 },
  { path: '/flows', label: 'Flows', icon: ActivitySquare },
  { path: '/alerts', label: 'Alerts', icon: AlertTriangle },
  { path: '/incidents', label: 'Incidents', icon: ShieldAlert },
  { path: '/forecast', label: 'Forecast', icon: FastForward },
  { path: '/packets', label: 'Packets', icon: Search },
  { path: '/hunting', label: 'Hunting', icon: Crosshair },
  { path: '/assets', label: 'Assets', icon: Server },
  { path: '/mitre', label: 'ATT&CK', icon: Map },
];

export const MainLayout: React.FC = () => {
  const { platformName } = useAppStore();
  const location = useLocation();

  React.useEffect(() => {
    wsService.connect();
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0B0F19] text-[#9CA3AF] font-sans selection:bg-cyan-900 selection:text-white">
      
      {/* Sidebar - Inspired by Mockup 3 */}
      <aside className="w-64 flex flex-col bg-[#0A0F1C] border-r border-[#1F2937] z-20">
        
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-[#1F2937]">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)]">
              <ShieldAlert size={18} className="text-white" />
            </div>
            <span className="font-bold text-lg text-white tracking-wide">
              {platformName || 'Netra'}
            </span>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-1 custom-scrollbar">
          <div className="text-[10px] font-bold tracking-widest text-[#4B5563] mb-3 px-3 uppercase">General</div>
          
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-transparent text-cyan-400' 
                    : 'text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#111827]'
                }`}
              >
                <item.icon size={18} className={`mr-3 ${isActive ? 'text-cyan-400' : 'text-[#6B7280]'}`} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Sidebar Settings */}
        <div className="p-4 border-t border-[#1F2937] space-y-1">
          <NavLink to="/settings" className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#111827] transition-all">
            <Settings size={18} className="mr-3 text-[#6B7280]" />
            Settings
          </NavLink>
          <button className="flex items-center w-full px-3 py-2.5 rounded-lg text-sm font-medium text-[#ef4444] hover:bg-[#ef4444]/10 transition-all">
            <LogOut size={18} className="mr-3" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-[#0B0F19]">
        
        {/* Top Header Row (Pill buttons & Profile) */}
        <header className="h-20 flex items-center justify-between px-8 z-10 pt-4 pb-2">
          
          {/* Pill Navigation (Like Mockup 1 & 3) */}
          <div className="flex bg-[#111827] rounded-full p-1 border border-[#1F2937] shadow-lg">
            <button className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-sm font-medium rounded-full shadow-md">Dashboard</button>
            <button className="px-6 py-2 text-[#9CA3AF] hover:text-white text-sm font-medium rounded-full transition-colors">Endpoints</button>
            <button className="px-6 py-2 text-[#9CA3AF] hover:text-white text-sm font-medium rounded-full transition-colors">Findings</button>
            <button className="px-6 py-2 text-[#9CA3AF] hover:text-white text-sm font-medium rounded-full transition-colors">Alerts</button>
          </div>

          {/* Right Header actions */}
          <div className="flex items-center space-x-4">
            <button className="w-10 h-10 rounded-full bg-[#111827] border border-[#1F2937] flex items-center justify-center text-[#9CA3AF] hover:text-white transition-colors">
              <Bell size={18} />
            </button>
            <button className="w-10 h-10 rounded-full bg-[#111827] border border-[#1F2937] flex items-center justify-center text-[#9CA3AF] hover:text-white transition-colors">
              <Search size={18} />
            </button>
            <div className="flex items-center bg-[#111827] border border-[#1F2937] rounded-full p-1 pr-4 shadow-lg cursor-pointer hover:bg-[#1F2937] transition-colors">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center mr-3">
                <User size={16} className="text-white" />
              </div>
              <span className="text-sm font-medium text-white">Analyst Team</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-hidden relative z-0">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
