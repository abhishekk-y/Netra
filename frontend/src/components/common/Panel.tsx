import React from 'react';
import { useUIStore } from '../../stores/uiStore';

interface PanelProps {
  title: string;
  children: React.ReactNode;
  headerRight?: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Panel: React.FC<PanelProps> = ({ title, children, headerRight, className = '', noPadding = false }) => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  return (
    <div className={`flex flex-col overflow-hidden transition-all duration-300 ${isDark ? 'bg-gradient-to-br from-[#111] to-[#0A0A0A] border border-[#333] rounded-2xl' : 'bg-white/80 backdrop-blur-md border border-slate-200/60 shadow-sm rounded-2xl'} ${className}`}>
      <div className={`h-14 flex items-center justify-between px-5 select-none shrink-0 border-b ${
        isDark ? 'border-[#333] bg-[#1a1a1a]/50' : 'border-slate-100/60 bg-slate-50/50'
      }`}>
        <h3 className={`text-sm font-bold tracking-widest uppercase ${isDark ? 'text-gray-300' : 'text-slate-800'}`}>
          {title}
        </h3>
        {headerRight && <div className="flex items-center gap-2">{headerRight}</div>}
      </div>
      <div className={`flex-1 overflow-auto custom-scrollbar ${noPadding ? '' : 'p-4'}`}>
        {children}
      </div>
    </div>
  );
};
