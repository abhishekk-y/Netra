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
  { path: '/dns', label: 'DNS', icon: Globe },
  { path: '/tls', label: 'TLS', icon: Lock },
  { path: '/deception', label: 'Deception', icon: Ghost },
  { path: '/health', label: 'Health', icon: HeartPulse },
  { path: '/settings', label: 'Settings', icon: Settings },
];

const MainLayout: React.FC = () => {
  const { sidebarCollapsed, toggleSidebar, platformName } = useAppStore();

  React.useEffect(() => {
    wsService.connect();
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-gray-950 text-gray-100">
      <StatusBar />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside 
          className={`bg-gray-900 border-r border-gray-800 transition-all duration-200 flex flex-col ${sidebarCollapsed ? 'w-12' : 'w-48'}`}
        >
          <div 
            className="h-12 flex items-center justify-center border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors"
            onClick={toggleSidebar}
            title="Toggle Sidebar"
          >
            <span className={`font-mono font-bold text-sm text-emerald-500 ${sidebarCollapsed ? 'hidden' : 'block'}`}>
              {platformName}
            </span>
            {sidebarCollapsed && <ShieldAlert size={16} className="text-emerald-500" />}
          </div>
          
          <nav className="flex-1 overflow-y-auto py-2 custom-scrollbar">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `flex items-center px-3 py-2 my-0.5 mx-2 rounded cursor-pointer transition-colors ${
                    isActive ? 'bg-gray-800 text-emerald-400' : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
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
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
