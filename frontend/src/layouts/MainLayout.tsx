import React, { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { 
  Activity, ShieldAlert, Network, Database, 
  Terminal, Settings, Bell, Search, Cloud,
  Eye, Bug, Play, Box, FileText, HeartPulse, Moon, Sun
} from 'lucide-react';
import { wsService } from '../stores/telemetryStore';
import { useUIStore } from '../stores/uiStore';

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useUIStore();

  useEffect(() => {
    wsService.connect();
  }, []);

  // Sync theme with document class
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.className = "bg-[#000000] text-gray-400 font-mono antialiased overflow-hidden selection:bg-rose-500/30 selection:text-white";
    } else {
      document.documentElement.classList.remove('dark');
      document.body.className = "bg-[#F4F6F8] text-slate-800 font-sans antialiased overflow-hidden selection:bg-blue-500/30 selection:text-blue-900";
    }
  }, [theme]);

  const navGroups = [
    {
      group: 'Network Intelligence',
      items: [
        { path: '/', label: 'Overview', icon: Activity },
        { path: '/topology', label: 'Topology map', icon: Network },
      ]
    },
    {
      group: 'Security & Threat',
      items: [
        { path: '/alerts', label: 'Detections', icon: ShieldAlert },
        { path: '/incidents', label: 'Investigations', icon: FileText },
        { path: '/mitre', label: 'ATT&CK Framework', icon: Box },
        { path: '/forecast', label: 'AI Forecasting', icon: Eye },
      ]
    },
    {
      group: 'Deception',
      items: [
        { path: '/deception', label: 'Honeypots', icon: Bug },
      ]
    },
    {
      group: 'Forensics',
      items: [
        { path: '/flows', label: 'Traffic Logs', icon: Database },
        { path: '/packets', label: 'Packet Inspection', icon: Terminal },
        { path: '/hunting', label: 'Threat Hunt', icon: Search },
        { path: '/forensics/replay', label: 'Event Replay', icon: Play },
      ]
    },
    {
      group: 'System',
      items: [
        { path: '/assets', label: 'Asset Inventory', icon: Database },
        { path: '/health', label: 'System Health', icon: HeartPulse },
        { path: '/settings', label: 'Configuration', icon: Settings },
      ]
    }
  ];

  return (
    <div className={`flex h-screen w-screen overflow-hidden ${theme === 'dark' ? 'bg-[#000]' : 'bg-[#F4F6F8]'}`}>
      
      {/* CRT OVERLAY (Only visible in dark mode) */}
      {theme === 'dark' && (
        <>
          <div className="absolute inset-0 z-[9999] pointer-events-none mix-blend-overlay opacity-50" 
               style={{ background: 'linear-gradient(to bottom, rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%)', backgroundSize: '100% 4px' }}></div>
          <div className="absolute inset-0 z-[9998] pointer-events-none"
               style={{ background: 'radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,0.6) 100%)' }}></div>
        </>
      )}

      {/* SIDEBAR */}
      <aside className={`w-[260px] flex flex-col z-50 shrink-0 transition-colors ${
        theme === 'dark' 
          ? 'bg-[#050505] border-r border-[#333] shadow-[0_0_30px_rgba(0,0,0,0.9)]' 
          : 'bg-slate-50/50 backdrop-blur-xl border-r border-slate-200 shadow-sm'
      }`}>
        
        {/* Brand Header */}
        <div className={`h-20 flex items-center justify-between px-6 shrink-0 border-b ${
          theme === 'dark' ? 'border-[#333] bg-[#0A0A0A]' : 'border-slate-200/60 bg-transparent'
        }`}>
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${theme === 'dark' ? 'bg-rose-500/20' : 'bg-gradient-to-br from-[#00bceb] to-indigo-500 shadow-sm shadow-[#00bceb]/30'}`}>
              <Cloud size={18} className={theme === 'dark' ? 'text-rose-500' : 'text-white'} />
            </div>
            <span className={`font-bold text-xl tracking-tight ${theme === 'dark' ? 'text-white font-mono uppercase' : 'text-slate-800 font-sans'}`}>
              Netra<span className={theme === 'dark' ? 'text-rose-500' : 'text-indigo-500'}>X</span>
            </span>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto custom-scrollbar pb-6 pt-6 px-4">
          {navGroups.map((group, idx) => (
            <div key={idx} className="mb-8">
              <div className={`px-3 mb-3 text-[11px] font-bold uppercase tracking-widest ${
                theme === 'dark' ? 'text-[#555]' : 'text-slate-400/80'
              }`}>
                {group.group}
              </div>
              <div className="space-y-1.5">
                {group.items.map((item) => {
                  const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`flex items-center px-4 py-2.5 rounded-xl transition-all duration-300 group ${
                        theme === 'dark' 
                          ? (isActive ? 'bg-[#111] text-white border-l-2 border-rose-500 rounded-none' : 'text-[#888] hover:bg-[#111] hover:text-white')
                          : (isActive ? 'bg-white text-indigo-600 shadow-sm shadow-indigo-100/50 font-semibold' : 'text-slate-500 hover:bg-white/60 hover:text-slate-800')
                      }`}
                    >
                      <item.icon size={18} className={`${
                        theme === 'dark' 
                          ? (isActive ? 'text-rose-500' : 'text-[#555]') 
                          : (isActive ? 'text-indigo-500' : 'text-slate-400 group-hover:text-slate-600')
                      } shrink-0 transition-colors`} />
                      <span className={`ml-3 text-sm ${theme === 'dark' ? 'uppercase text-[10px] tracking-widest' : ''}`}>{item.label}</span>
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        
        {/* HEADER */}
        <header className={`h-20 flex items-center justify-between px-8 shrink-0 z-40 transition-colors ${
          theme === 'dark' ? 'bg-[#0A0A0A] border-b border-[#333]' : 'bg-white/80 backdrop-blur-md border-b border-slate-200/60 shadow-sm'
        }`}>
          
          <div className="flex items-center">
            <div className={`text-xl font-semibold capitalize ${
              theme === 'dark' ? 'text-gray-300 font-mono uppercase tracking-widest text-[14px]' : 'text-slate-800 font-sans'
            }`}>
              {location.pathname === '/' ? 'Platform Overview' : location.pathname.split('/')[1].replace('-', ' ')}
            </div>
          </div>

          <div className="flex items-center space-x-6">
            
            {/* THEME TOGGLE */}
            <button 
              onClick={toggleTheme}
              className={`p-2 rounded-full transition-colors flex items-center justify-center ${
                theme === 'dark' ? 'bg-[#111] text-yellow-500 border border-[#333] hover:bg-[#222]' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
              title="Toggle Intense Mode"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <div className="relative flex items-center">
              <Search size={16} className={`absolute left-3 ${theme === 'dark' ? 'text-[#666]' : 'text-slate-400'}`} />
              <input 
                type="text" 
                placeholder="Search IPs, domains, or rules..." 
                className={`py-1.5 pl-9 pr-4 w-72 rounded-md focus:outline-none transition-all ${
                  theme === 'dark' 
                    ? 'bg-[#111] border border-[#333] text-gray-300 text-[10px] uppercase font-mono focus:border-rose-500' 
                    : 'bg-slate-50 border border-slate-200 text-sm text-slate-700 focus:ring-2 focus:ring-[#00bceb]/20 focus:border-[#00bceb]'
                }`}
              />
            </div>
            
            <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-md border ${
              theme === 'dark' 
                ? 'bg-[#111] border-[#333] text-[#888] font-mono text-[10px] uppercase' 
                : 'bg-slate-50 border-slate-200 text-sm text-slate-600'
            }`}>
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
              <span>Sensors Active</span>
            </div>
            
            <button className={`relative transition-colors ${theme === 'dark' ? 'text-[#666] hover:text-white' : 'text-slate-400 hover:text-slate-700'}`}>
              <Bell size={20} />
              <div className="absolute top-0 right-0 w-2 h-2 bg-rose-500 border-2 border-transparent rounded-full"></div>
            </button>
            
          </div>
        </header>

        {/* SCROLLABLE PAGE CONTENT */}
        <div className={`flex-1 overflow-auto relative ${theme === 'dark' ? 'p-0' : 'p-6'}`}>
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
