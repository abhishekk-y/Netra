import React from 'react';
import { Panel } from '../common/Panel';

export const MitrePage: React.FC = () => {
  const tactics = [
    'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation', 
    'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
    'Collection', 'Exfiltration', 'Impact'
  ];

  // Mock matrix data
  const observed = ['Valid Accounts', 'Exploit Public-Facing Application', 'OS Credential Dumping', 'Remote Services'];
  const forecasted = ['Data Encrypted for Impact', 'Exfiltration Over C2 Channel'];

  return (
    <div className="flex flex-col h-full bg-gray-950 p-2 overflow-auto custom-scrollbar">
      <div className="flex gap-4 mb-4 shrink-0 px-2 pt-2 items-center">
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="w-3 h-3 bg-red-500/20 border border-red-500 rounded-sm"></div>
          <span className="text-gray-300">OBSERVED</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="w-3 h-3 bg-orange-500/20 border border-orange-500 border-dashed rounded-sm"></div>
          <span className="text-gray-300">FORECASTED</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="w-3 h-3 bg-gray-800 border border-gray-700 rounded-sm"></div>
          <span className="text-gray-500">NO ACTIVITY</span>
        </div>
      </div>

      <div className="flex gap-2 min-w-max pb-4">
        {tactics.map(tactic => (
          <div key={tactic} className="w-48 flex flex-col gap-2 shrink-0">
            <div className="bg-gray-900 border border-gray-800 p-2 rounded text-center text-xs font-bold text-gray-200">
              {tactic}
            </div>
            
            {/* Generate some dummy techniques per tactic for visual demo */}
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
                  className={`p-2 rounded text-xs transition-colors cursor-pointer border ${
                    isObserved ? 'bg-red-500/10 border-red-500 text-red-100 hover:bg-red-500/20' :
                    isForecasted ? 'bg-orange-500/10 border-orange-500 border-dashed text-orange-200 hover:bg-orange-500/20' :
                    'bg-gray-900/50 border-gray-800 text-gray-400 hover:bg-gray-800'
                  }`}
                >
                  <div className="font-mono text-[10px] text-gray-500 mb-1">T10{Math.floor(Math.random()*99)}</div>
                  {techName}
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
