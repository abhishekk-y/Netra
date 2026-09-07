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
    <div className={`flex flex-col overflow-hidden ${isDark ? 'bg-[#0A0A0A] border border-[#333] rounded' : 'bg-white border border-slate-200 shadow-sm rounded-xl'} ${className}`}>
      <div className={`h-12 flex items-center justify-between px-4 select-none shrink-0 border-b ${
        isDark ? 'border-[#333] bg-[#111]' : 'border-slate-100 bg-slate-50'
      }`}>
        <h3 className={`text-sm font-semibold tracking-wider ${isDark ? 'text-gray-300 uppercase font-mono' : 'text-slate-800'}`}>
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
