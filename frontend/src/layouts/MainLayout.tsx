import React, { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  Activity, ShieldAlert, Network, Database,
  Terminal, Settings, Bell, Search, Cpu,
  Eye, Bug, Play, Box, FileText, HeartPulse, Moon, Sun,
  ChevronRight, Shield, Layers, Crosshair, Wifi, Globe
} from 'lucide-react';
import { wsService } from '../stores/telemetryStore';
import { useUIStore } from '../stores/uiStore';
import { useTelemetryStore } from '../stores/telemetryStore';

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useUIStore();
  const isDark = theme === 'dark';
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const telemetry = useTelemetryStore();

  useEffect(() => {
    wsService.connect();
  }, []);

  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.setAttribute('data-theme', 'dark');
      html.classList.add('dark');
      document.body.style.background = '#020204';
    } else {
      html.setAttribute('data-theme', 'light');
      html.classList.remove('dark');
      document.body.style.background = '#F4F6F8';
    }
  }, [isDark]);

  const navGroups = [
    {
      group: 'Intelligence',
      items: [
        { path: '/', label: 'Overview', icon: Activity },
        { path: '/topology', label: 'Network Map', icon: Network },
        { path: '/flows', label: 'Traffic Logs', icon: Database },
      ]
    },
    {
      group: 'Threats',
      items: [
        { path: '/alerts', label: 'Detections', icon: ShieldAlert },
        { path: '/incidents', label: 'Investigations', icon: FileText },
        { path: '/mitre', label: 'ATT&CK Matrix', icon: Box },
        { path: '/forecast', label: 'AI Forecast', icon: Eye },
      ]
    },
    {
      group: 'Hunt & Deceive',
      items: [
        { path: '/hunting', label: 'Threat Hunt', icon: Crosshair },
        { path: '/deception', label: 'Honeypots', icon: Bug },
      ]
    },
    {
      group: 'Forensics',
      items: [
        { path: '/packets', label: 'Packet Inspector', icon: Terminal },
        { path: '/forensics/replay', label: 'Event Replay', icon: Play },
      ]
    },
    {
      group: 'System',
      items: [
        { path: '/assets', label: 'Asset Inventory', icon: Layers },
        { path: '/health', label: 'System Health', icon: HeartPulse },
        { path: '/settings', label: 'Configuration', icon: Settings },
      ]
    }
  ];

  const pageTitle = location.pathname === '/'
    ? 'Platform Overview'
    : location.pathname.replace(/^\//, '').replace(/\//g, ' / ').replace(/-/g, ' ');

  return (
    <div className={`flex h-screen w-screen overflow-hidden font-sans ${
      isDark ? 'bg-[#020204]' : 'bg-[#F4F6F8]'
    }`}>

      {/* Dark mode CRT vignette overlay */}
      {isDark && (
        <div
          className="absolute inset-0 z-[9999] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%)' }}
        />
      )}

      {/* SIDEBAR */}
      <aside
        onMouseEnter={() => setIsSidebarOpen(true)}
        onMouseLeave={() => setIsSidebarOpen(false)}
        style={{ width: isSidebarOpen ? '260px' : '72px', transition: 'width 0.25s cubic-bezier(0.4,0,0.2,1)' }}
        className={`flex flex-col z-50 shrink-0 overflow-hidden ${
          isDark
            ? 'bg-[#08080D] border-r border-white/[0.06]'
            : 'bg-white border-r border-slate-200 shadow-sm'
        }`}
      >
        {/* Brand */}
        <div className={`h-16 flex items-center px-4 shrink-0 border-b overflow-hidden ${
          isDark ? 'border-white/[0.06] bg-[#0A0A12]' : 'border-slate-100'
        }`}>
          <div className="flex items-center space-x-3 shrink-0">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
              isDark
                ? 'bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/20'
                : 'bg-gradient-to-br from-[#00bceb] to-indigo-600 shadow-md shadow-[#00bceb]/30'
            }`}>
              <Shield size={18} className={isDark ? 'text-cyan-400' : 'text-white'} />
            </div>
            <div
              style={{
                opacity: isSidebarOpen ? 1 : 0,
                width: isSidebarOpen ? 'auto' : 0,
                transition: 'opacity 0.2s ease, width 0.25s ease',
                overflow: 'hidden',
                whiteSpace: 'nowrap'
              }}
            >
              <span className={`font-bold text-lg tracking-tight ${
                isDark ? 'text-white' : 'text-slate-800'
              }`}>
                Netra<span className={isDark ? 'text-cyan-400' : 'text-indigo-600'}>-X</span>
              </span>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar py-4">
          {navGroups.map((grp, gi) => (
            <div key={gi} className="mb-1 px-3">
              {/* Group Label */}
              <div
                style={{
                  opacity: isSidebarOpen ? 1 : 0,
                  height: isSidebarOpen ? 'auto' : 0,
                  transition: 'opacity 0.15s ease, height 0.2s ease',
                  overflow: 'hidden',
                }}
                className={`px-2 py-1.5 text-[9px] font-bold uppercase tracking-[0.15em] mb-1 ${
                  isDark ? 'text-slate-600' : 'text-slate-400'
                }`}
              >
                {grp.group}
              </div>
              <div className="space-y-0.5">
                {grp.items.map((item) => {
                  const isActive = item.path === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(item.path);
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      title={!isSidebarOpen ? item.label : undefined}
                      className={`flex items-center px-2.5 py-2.5 rounded-xl transition-all duration-150 group relative ${
                        isDark
                          ? isActive
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                            : 'text-slate-500 hover:bg-white/[0.04] hover:text-slate-200'
                          : isActive
                            ? 'bg-indigo-50 text-indigo-700 shadow-sm'
                            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
                      } ${!isSidebarOpen ? 'justify-center' : ''}`}
                    >
                      {isActive && isDark && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-cyan-400 rounded-full" />
                      )}
                      <item.icon
                        size={18}
                        className={`shrink-0 transition-colors ${
                          isDark
                            ? isActive ? 'text-cyan-400' : 'text-slate-600 group-hover:text-slate-300'
                            : isActive ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-700'
                        }`}
                      />
                      <span
                        style={{
                          opacity: isSidebarOpen ? 1 : 0,
                          width: isSidebarOpen ? 'auto' : 0,
                          marginLeft: isSidebarOpen ? '10px' : 0,
                          transition: 'opacity 0.15s ease, width 0.2s ease, margin 0.2s ease',
                          overflow: 'hidden',
                          whiteSpace: 'nowrap',
                          fontSize: '13px',
                          fontWeight: isActive ? 600 : 400,
                          fontFamily: isDark ? 'var(--font-mono)' : 'var(--font-sans)',
                          letterSpacing: isDark ? '0.03em' : 'normal',
                        }}
                      >
                        {item.label}
                      </span>
                    </NavLink>
                  );
                })}
              </div>
              {gi < navGroups.length - 1 && (
                <div className={`my-3 mx-1 h-px ${
                  isDark ? 'bg-white/[0.04]' : 'bg-slate-100'
                }`} />
              )}
            </div>
          ))}
        </nav>

        {/* Bottom sensor status */}
        <div className={`p-3 border-t shrink-0 ${
          isDark ? 'border-white/[0.06]' : 'border-slate-100'
        }`}>
          <div className={`flex items-center ${
            isSidebarOpen ? 'space-x-3 px-2' : 'justify-center'
          }`}>
            <div className="status-dot-online shrink-0" />
            <span
              style={{
                opacity: isSidebarOpen ? 1 : 0,
                width: isSidebarOpen ? 'auto' : 0,
                transition: 'opacity 0.15s ease',
                overflow: 'hidden',
                whiteSpace: 'nowrap',
                fontSize: '11px',
              }}
              className={isDark ? 'text-slate-500' : 'text-slate-400'}
            >
              Sensors Active
            </span>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* HEADER */}
        <header className={`h-16 flex items-center justify-between px-6 shrink-0 ${
          isDark
            ? 'bg-[#0A0A12] border-b border-white/[0.06]'
            : 'bg-white/80 backdrop-blur-md border-b border-slate-200/80 shadow-sm'
        }`}>

          <div className="flex items-center space-x-2">
            <h1 className={`font-semibold capitalize ${
              isDark
                ? 'text-slate-200 text-sm tracking-wide'
                : 'text-slate-800 text-base'
            }`}>
              {pageTitle}
            </h1>
          </div>

          <div className="flex items-center space-x-3">

            {/* Sensor Status */}
            <div className={`hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-medium ${
              isDark
                ? 'bg-emerald-500/[0.08] border-emerald-500/20 text-emerald-400'
                : 'bg-emerald-50 border-emerald-200 text-emerald-700'
            }`}>
              <div className="status-dot-online" style={{ width: 6, height: 6 }} />
              <span>Live Monitoring</span>
            </div>

            {/* Search */}
            <div className="relative">
              <Search size={14} className={`absolute left-3 top-1/2 -translate-y-1/2 ${
                isDark ? 'text-slate-600' : 'text-slate-400'
              }`} />
              <input
                type="text"
                placeholder="Search IPs, rules, incidents..."
                className={`pl-9 pr-4 py-1.5 w-64 rounded-lg text-sm focus:outline-none focus:ring-2 transition-all ${
                  isDark
                    ? 'bg-white/[0.04] border border-white/[0.08] text-slate-300 placeholder-slate-600 focus:ring-cyan-500/30 focus:border-cyan-500/40'
                    : 'bg-slate-50 border border-slate-200 text-slate-700 placeholder-slate-400 focus:ring-indigo-500/30 focus:border-indigo-400'
                }`}
              />
            </div>

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? 'bg-white/[0.04] border border-white/[0.08] text-amber-400 hover:bg-white/[0.08]'
                  : 'bg-slate-100 border border-slate-200 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {isDark ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {/* Notifications */}
            <button className={`relative p-2 rounded-lg transition-colors ${
              isDark
                ? 'bg-white/[0.04] border border-white/[0.08] text-slate-400 hover:bg-white/[0.08]'
                : 'bg-slate-100 border border-slate-200 text-slate-600 hover:bg-slate-200'
            }`}>
              <Bell size={16} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border border-transparent" />
            </button>

            {/* Avatar */}
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              isDark
                ? 'bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400'
                : 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-sm'
            }`}>
              NX
            </div>

          </div>
        </header>

        {/* PAGE CONTENT */}
        <div className={`flex-1 overflow-auto custom-scrollbar ${
          isDark ? 'p-5' : 'p-6'
        }`}>
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
