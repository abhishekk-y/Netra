import React from 'react';
import clsx from 'clsx';

type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

interface BadgeProps {
  children: React.ReactNode;
  variant?: Severity | 'success' | 'warning' | 'default';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className }) => {
  const variants = {
    info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    low: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    critical: 'bg-red-500/10 text-red-400 border-red-500/20',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    default: 'bg-gray-800 text-gray-300 border-gray-700',
  };

  return (
    <span className={clsx(
      "inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border uppercase",
      variants[variant as keyof typeof variants] || variants.default,
      className
    )}>
      {children}
    </span>
  );
};
