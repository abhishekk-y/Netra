import React from 'react';

interface RiskIndicatorProps {
  score: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const RiskIndicator: React.FC<RiskIndicatorProps> = ({ score, size = 'md', showLabel = false }) => {
  const getColor = (s: number) => {
    if (s >= 80) return 'text-red-500';
    if (s >= 60) return 'text-orange-500';
    if (s >= 40) return 'text-amber-500';
    return 'text-emerald-500';
  };

  const getBgColor = (s: number) => {
    if (s >= 80) return 'bg-red-500';
    if (s >= 60) return 'bg-orange-500';
    if (s >= 40) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const sizes = {
    sm: 'text-xs w-8',
    md: 'text-sm w-10',
    lg: 'text-base w-12'
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`font-mono font-bold text-right ${getColor(score)} ${sizes[size]}`}>
        {score.toFixed(1)}
      </div>
      {showLabel && (
        <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div 
            className={`h-full ${getBgColor(score)} transition-all duration-500`} 
            style={{ width: `${score}%` }}
          />
        </div>
      )}
    </div>
  );
};
