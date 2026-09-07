import React from 'react';
import { Panel } from '../common/Panel';
import { Badge } from '../common/Badge';
import { Activity, ShieldAlert, FastForward, Server, Network } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';

export const ForecastPage: React.FC = () => {
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

  // Hardcoded for demo purposes as requested for realistic states
  const forecast = {
    currentStage: 'Lateral Movement',
    stageConfidence: 0.92,
    timeInStage: '14m 32s',
    nextStages: [
      { stage: 'Exfiltration', probability: 0.85, horizon: 'T+5m' },
      { stage: 'Impact', probability: 0.12, horizon: 'T+30m' },
      { stage: 'Command and Control', probability: 0.03, horizon: 'T+1m' }
    ],
    targets: [
      { id: 'srv-db', ip: '10.0.0.5', name: 'DB-PROD-01', probability: 0.92 },
      { id: 'srv-fs', ip: '10.0.0.8', name: 'FILE-SERVER', probability: 0.45 },
      { id: 'ws-admin', ip: '192.168.1.100', name: 'ADMIN-WS', probability: 0.15 }
    ],
    evidence: [
      'SMB brute force observed from 192.168.1.45 to 10.0.0.5',
      'Suspicious RDP session established',
      'BloodHound-like AD enumeration detected'
    ]
  };

  return (
    <div className={`flex flex-col h-full p-4 gap-4 overflow-auto custom-scrollbar ${isDark ? 'bg-[#000]' : 'bg-transparent'}`}>
      {/* Header Banner */}
      <div className={`p-4 rounded-xl flex items-center justify-between shrink-0 shadow-sm border ${
        isDark ? 'bg-orange-500/10 border-orange-500/20' : 'bg-orange-50 border-orange-200'
      }`}>
        <div className="flex items-center gap-4">
          <FastForward size={28} className={isDark ? 'text-orange-500' : 'text-orange-600'} />
          <div>
            <h1 className={`text-lg font-bold ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>Active Attack Forecast</h1>
            <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-slate-600'}`}>Netra AI has identified an unfolding attack path and predicts imminent lateral movement.</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant="critical">INC-001</Badge>
          <Badge variant="high">CONFIDENCE: 92%</Badge>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        
        {/* Left: Current State */}
        <div className="col-span-3 flex flex-col gap-4">
          <Panel title="Current Attack State" className="flex-1">
            <div className="flex flex-col items-center text-center p-2">
              <ShieldAlert size={48} className={isDark ? 'text-red-500 mb-4' : 'text-red-600 mb-4'} />
              <div className={`text-sm font-semibold mb-1 ${isDark ? 'text-gray-400 font-mono uppercase' : 'text-slate-500'}`}>OBSERVED STAGE</div>
              <div className={`text-2xl font-bold mb-6 ${isDark ? 'text-gray-100' : 'text-slate-800'}`}>{forecast.currentStage}</div>
              
              <div className="w-full space-y-2">
                <div className="flex justify-between text-xs font-semibold">
                  <span className={isDark ? 'text-gray-500' : 'text-slate-500'}>Model Confidence</span>
                  <span className={isDark ? 'text-emerald-400 font-mono' : 'text-emerald-600 font-mono'}>{(forecast.stageConfidence * 100).toFixed(0)}%</span>
                </div>
                <div className={`w-full h-2 rounded-full overflow-hidden ${isDark ? 'bg-gray-900' : 'bg-slate-100'}`}>
                  <div className="bg-emerald-500 h-full" style={{ width: `${forecast.stageConfidence * 100}%` }} />
                </div>
              </div>

              <div className={`mt-8 p-4 rounded-xl w-full text-left border ${isDark ? 'bg-gray-900/50 border-gray-800' : 'bg-slate-50 border-slate-200'}`}>
                <div className={`text-xs font-semibold mb-1 flex items-center gap-2 ${isDark ? 'text-gray-500' : 'text-slate-500'}`}><Activity size={14}/> Time in Stage</div>
                <div className={`font-mono ${isDark ? 'text-gray-200' : 'text-slate-700 font-semibold'}`}>{forecast.timeInStage}</div>
              </div>
            </div>
          </Panel>
        </div>

        {/* Center: Next Stages */}
        <div className="col-span-5 flex flex-col gap-4">
          <Panel title="Predicted Next Stages" className="flex-1">
            <div className="space-y-4">
              {forecast.nextStages.map((stage, idx) => (
                <div key={idx} className={`p-4 rounded-xl border ${isDark ? 'bg-gray-900/50 border-gray-800' : 'bg-slate-50 border-slate-200'}`}>
                  <div className="flex justify-between items-center mb-3">
                    <div className={`font-bold ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>{stage.stage}</div>
                    <div className="flex gap-3 items-center">
                      <span className={`text-xs font-semibold ${isDark ? 'text-gray-500 font-mono' : 'text-slate-500'}`}>{stage.horizon}</span>
                      <span className={`font-mono font-bold ${idx === 0 ? 'text-orange-500 text-lg' : (isDark ? 'text-gray-400' : 'text-slate-400')}`}>
                        {(stage.probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className={`w-full h-2 rounded-full overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-slate-200'}`}>
                    <div 
                      className={`h-full ${idx === 0 ? 'bg-orange-500' : (isDark ? 'bg-gray-600' : 'bg-slate-400')}`} 
                      style={{ width: `${stage.probability * 100}%` }} 
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8">
              <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>Forecast Evidence</h4>
              <ul className="space-y-3">
                {forecast.evidence.map((ev, idx) => (
                  <li key={idx} className={`text-sm flex items-start gap-3 ${isDark ? 'text-gray-300' : 'text-slate-700 font-medium'}`}>
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          </Panel>
        </div>

        {/* Right: Targets */}
        <div className="col-span-4 flex flex-col gap-4">
          <Panel title="Predicted Targets" className="flex-1">
            <div className="space-y-4">
              {forecast.targets.map((target, idx) => (
                <div key={idx} className={`flex items-center gap-4 p-3 rounded-xl transition-colors border ${
                  isDark ? 'hover:bg-gray-800/50 border-transparent hover:border-gray-800' : 'hover:bg-slate-50 border-transparent hover:border-slate-200'
                }`}>
                  <Server size={24} className={idx === 0 ? 'text-red-500' : (isDark ? 'text-gray-500' : 'text-slate-400')} />
                  <div className="flex-1 min-w-0">
                    <div className={`text-sm font-bold truncate ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>{target.name}</div>
                    <div className={`text-xs font-mono ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>{target.ip}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-mono font-bold ${idx === 0 ? 'text-red-400' : (isDark ? 'text-gray-400' : 'text-slate-500')}`}>
                      {(target.probability * 100).toFixed(0)}%
                    </div>
                    <div className={`text-[10px] uppercase font-semibold ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>Risk</div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className={`mt-8 p-6 rounded-xl flex flex-col items-center justify-center text-center border ${
              isDark ? 'border-gray-800 bg-gray-950' : 'border-slate-200 bg-slate-50'
            }`}>
               <Network size={32} className={`mb-3 ${isDark ? 'text-gray-600' : 'text-slate-400'}`} />
               <div className={`text-sm font-medium ${isDark ? 'text-gray-400' : 'text-slate-600'}`}>View attack path in Topology</div>
               <button className={`mt-4 text-xs px-4 py-2 font-semibold rounded-lg transition-colors ${
                 isDark ? 'bg-gray-800 hover:bg-gray-700 text-gray-200' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 shadow-sm'
               }`}>
                 Open Topology View
               </button>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
};

export default ForecastPage;
