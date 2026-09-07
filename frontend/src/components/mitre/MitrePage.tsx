import React from 'react';
import { useUIStore } from '../../stores/uiStore';

export const MitrePage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  const tactics = [
    'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation', 
    'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
    'Collection', 'Exfiltration', 'Impact'
  ];

  // Mock matrix data
  const observed = ['Valid Accounts', 'Exploit Public-Facing Application', 'OS Credential Dumping', 'Remote Services'];
  const forecasted = ['Data Encrypted for Impact', 'Exfiltration Over C2 Channel'];

  return (
    <div className={`flex flex-col h-full p-6 overflow-auto custom-scrollbar ${isDark ? 'bg-black' : 'bg-transparent'}`}>
      
      <div className={`flex gap-6 mb-6 shrink-0 p-4 rounded-xl items-center border shadow-sm ${isDark ? 'bg-[#111] border-[#333]' : 'bg-white border-slate-200'}`}>
        <div className="flex items-center gap-2 text-sm font-semibold">
          <div className="w-3 h-3 bg-red-500/20 border border-red-500 rounded-sm"></div>
          <span className={isDark ? 'text-gray-300 font-mono uppercase' : 'text-slate-700'}>Observed Activity</span>
        </div>
        <div className="flex items-center gap-2 text-sm font-semibold">
          <div className="w-3 h-3 bg-orange-500/20 border border-orange-500 border-dashed rounded-sm"></div>
          <span className={isDark ? 'text-gray-300 font-mono uppercase' : 'text-slate-700'}>Forecasted Path</span>
        </div>
        <div className="flex items-center gap-2 text-sm font-semibold">
          <div className={`w-3 h-3 border rounded-sm ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-slate-100 border-slate-300'}`}></div>
          <span className={isDark ? 'text-gray-500 font-mono uppercase' : 'text-slate-500'}>No Activity</span>
        </div>
      </div>

      <div className="flex gap-4 min-w-max pb-4">
        {tactics.map(tactic => (
          <div key={tactic} className="w-52 flex flex-col gap-3 shrink-0">
            <div className={`p-3 rounded-lg text-center text-sm font-bold shadow-sm border ${
              isDark ? 'bg-[#0A0A0A] border-[#333] text-gray-200 uppercase font-mono' : 'bg-slate-800 border-slate-900 text-white'
            }`}>
              {tactic}
            </div>
            
            {Array.from({ length: 8 }).map((_, i) => {
              const techName = i === 0 && tactic === 'Initial Access' ? 'Exploit Public-Facing Application' :
                               i === 1 && tactic === 'Lateral Movement' ? 'Remote Services' :
                               i === 0 && tactic === 'Impact' ? 'Data Encrypted for Impact' : 
                               `Technique ${i+1}`;
              
              const isObserved = observed.includes(techName);
              const isForecasted = forecasted.includes(techName);
              
              return (
                <div 
                  key={i} 
                  className={`p-3 rounded-lg text-sm transition-all cursor-pointer border shadow-sm ${
                    isObserved ? (isDark ? 'bg-red-500/10 border-red-500 text-red-100' : 'bg-red-50 border-red-200 text-red-700') :
                    isForecasted ? (isDark ? 'bg-orange-500/10 border-orange-500 border-dashed text-orange-200' : 'bg-orange-50 border-orange-300 border-dashed text-orange-700') :
                    (isDark ? 'bg-[#111] border-[#333] text-gray-400 hover:bg-[#222]' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50')
                  }`}
                >
                  <div className={`font-mono text-xs mb-1 font-semibold ${
                    isObserved ? (isDark ? 'text-red-400' : 'text-red-500') :
                    isForecasted ? (isDark ? 'text-orange-400' : 'text-orange-500') :
                    (isDark ? 'text-gray-500' : 'text-slate-400')
                  }`}>
                    T10{Math.floor(Math.random()*99)}
                  </div>
                  <div className={isDark ? 'font-mono text-[11px] uppercase leading-tight' : 'font-medium leading-tight'}>
                    {techName}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MitrePage;
