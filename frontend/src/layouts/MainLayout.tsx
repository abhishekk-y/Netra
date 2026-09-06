import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Activity, Share2, ActivitySquare, AlertTriangle, ShieldAlert, FastForward, Search, Crosshair, Server, Map, Globe, Lock, Ghost, HeartPulse, Settings } from 'lucide-react';
import { StatusBar } from '../components/common/StatusBar';
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
  { path: '/health', label: 'Health', icon: HeartPulse },
  { path: '/settings', label: 'Settings', icon: Settings },
];

const MainLayout: React.FC = () => {
  const { sidebarCollapsed, toggleSidebar, platformName } = useAppStore();

  React.useEffect(() => {
    wsService.connect();
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-900 text-slate-100 font-sans">
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside 
          className={`bg-slate-800 border-r border-slate-700 transition-all duration-200 flex flex-col ${sidebarCollapsed ? 'w-12' : 'w-48'}`}
        >
          <div 
            className="h-12 flex items-center justify-center border-b border-slate-700 cursor-pointer hover:bg-slate-700 transition-colors"
            onClick={toggleSidebar}
            title="Toggle Sidebar"
          >
            <span className={`font-mono font-bold text-lg text-cyan-400 ${sidebarCollapsed ? 'hidden' : 'block'}`}>
              Netra
            </span>
            {sidebarCollapsed && <ShieldAlert size={16} className="text-cyan-400" />}
          </div>
          
          <nav className="flex-1 overflow-y-auto py-2 custom-scrollbar">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `flex items-center px-3 py-2 my-0.5 mx-2 rounded cursor-pointer transition-colors ${
                    isActive ? 'bg-slate-700 text-cyan-400' : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200'
                  }`
                }
                title={item.label}
              >
                <item.icon size={16} className="min-w-[16px]" />
                {!sidebarCollapsed && <span className="ml-3 text-xs font-medium tracking-wide">{item.label}</span>}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-slate-900">
          <Outlet />
        </main>
      </div>
      <StatusBar />
    </div>
  );
};

export default MainLayout;
