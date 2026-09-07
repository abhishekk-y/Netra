import React from 'react';
import clsx from 'clsx';
import { useUIStore } from '../../stores/uiStore';

type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

interface BadgeProps {
  children: React.ReactNode;
  variant?: Severity | 'success' | 'warning' | 'default';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className }) => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const darkVariants = {
    info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    low: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    critical: 'bg-red-500/10 text-red-400 border-red-500/20',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    default: 'bg-gray-800 text-gray-300 border-gray-700',
  };

  const lightVariants = {
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    high: 'bg-orange-50 text-orange-700 border-orange-200',
    critical: 'bg-red-50 text-red-700 border-red-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    default: 'bg-slate-100 text-slate-600 border-slate-200',
  };

  const variants = isDark ? darkVariants : lightVariants;

  return (
    <span className={clsx(
      "inline-flex items-center px-2 py-0.5 rounded-md font-medium border",
      isDark ? "text-[10px] font-mono uppercase" : "text-xs",
      variants[variant as keyof typeof variants] || variants.default,
      className
    )}>
      {children}
    </span>
  );
};
