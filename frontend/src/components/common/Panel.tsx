import React from 'react';

interface PanelProps {
  title: string;
  children: React.ReactNode;
  headerRight?: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Panel: React.FC<PanelProps> = ({ title, children, headerRight, className = '', noPadding = false }) => {
  return (
    <div className={`bg-gray-900 border border-gray-800 rounded flex flex-col overflow-hidden ${className}`}>
      <div className="h-8 border-b border-gray-800 bg-gray-950/50 flex items-center justify-between px-3 select-none">
        <h3 className="text-xs font-semibold text-gray-300 tracking-wider uppercase">{title}</h3>
        {headerRight && <div className="flex items-center gap-2">{headerRight}</div>}
      </div>
      <div className={`flex-1 overflow-auto custom-scrollbar ${noPadding ? '' : 'p-3'}`}>
        {children}
      </div>
    </div>
  );
};
