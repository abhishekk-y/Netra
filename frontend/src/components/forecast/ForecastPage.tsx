import React from 'react';
import { Panel } from '../common/Panel';
import { Badge } from '../common/Badge';
import { Activity, ShieldAlert, FastForward, Server, Network } from 'lucide-react';

export const ForecastPage: React.FC = () => {
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
    <div className="flex flex-col h-full bg-gray-950 p-2 gap-2 overflow-auto custom-scrollbar">
      {/* Header Banner */}
      <div className="bg-orange-500/10 border border-orange-500/20 p-3 rounded flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <FastForward size={24} className="text-orange-500" />
          <div>
            <h1 className="text-lg font-bold text-gray-100">Active Attack Forecast</h1>
            <p className="text-sm text-gray-400">Netra AI has identified an unfolding attack path and predicts imminent lateral movement.</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant="critical">INC-001</Badge>
          <Badge variant="high">CONFIDENCE: 92%</Badge>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-2 min-h-0">
        
        {/* Left: Current State */}
        <div className="col-span-3 flex flex-col gap-2">
          <Panel title="Current Attack State" className="flex-1">
            <div className="flex flex-col items-center text-center p-4">
              <ShieldAlert size={48} className="text-red-500 mb-4" />
              <div className="text-sm text-gray-400 font-mono mb-1">OBSERVED STAGE</div>
              <div className="text-2xl font-bold text-gray-100 mb-4">{forecast.currentStage}</div>
              
              <div className="w-full space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Model Confidence</span>
                  <span className="text-emerald-400 font-mono">{(forecast.stageConfidence * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-900 h-1.5 rounded overflow-hidden">
                  <div className="bg-emerald-500 h-full" style={{ width: `${forecast.stageConfidence * 100}%` }} />
                </div>
              </div>

              <div className="mt-8 p-3 bg-gray-900/50 border border-gray-800 rounded w-full text-left">
                <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><Activity size={12}/> Time in Stage</div>
                <div className="font-mono text-gray-200">{forecast.timeInStage}</div>
              </div>
            </div>
          </Panel>
        </div>

        {/* Center: Next Stages */}
        <div className="col-span-5 flex flex-col gap-2">
          <Panel title="Predicted Next Stages" className="flex-1">
            <div className="space-y-4">
              {forecast.nextStages.map((stage, idx) => (
                <div key={idx} className="bg-gray-900/50 p-3 border border-gray-800 rounded">
                  <div className="flex justify-between items-center mb-2">
                    <div className="font-bold text-gray-200">{stage.stage}</div>
                    <div className="flex gap-2 items-center">
                      <span className="text-xs text-gray-500 font-mono">{stage.horizon}</span>
                      <span className={`font-mono font-bold ${idx === 0 ? 'text-orange-500 text-lg' : 'text-gray-400'}`}>
                        {(stage.probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-950 h-2 rounded overflow-hidden">
                    <div 
                      className={`h-full ${idx === 0 ? 'bg-orange-500' : 'bg-gray-600'}`} 
                      style={{ width: `${stage.probability * 100}%` }} 
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6">
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Forecast Evidence</h4>
              <ul className="space-y-2">
                {forecast.evidence.map((ev, idx) => (
                  <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          </Panel>
        </div>

        {/* Right: Targets */}
        <div className="col-span-4 flex flex-col gap-2">
          <Panel title="Predicted Targets" className="flex-1">
            <div className="space-y-3">
              {forecast.targets.map((target, idx) => (
                <div key={idx} className="flex items-center gap-3 p-2 hover:bg-gray-800/50 rounded transition-colors border border-transparent hover:border-gray-800">
                  <Server size={20} className={idx === 0 ? 'text-red-500' : 'text-gray-500'} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-bold text-gray-200 truncate">{target.name}</div>
                    <div className="text-xs font-mono text-gray-500">{target.ip}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-mono font-bold ${idx === 0 ? 'text-red-400' : 'text-gray-400'}`}>
                      {(target.probability * 100).toFixed(0)}%
                    </div>
                    <div className="text-[10px] text-gray-500 uppercase">Risk</div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 border border-gray-800 bg-gray-950 rounded flex flex-col items-center justify-center text-center">
               <Network size={32} className="text-gray-600 mb-2" />
               <div className="text-sm text-gray-400">View attack path in Topology</div>
               <button className="mt-3 bg-gray-800 hover:bg-gray-700 text-xs px-3 py-1.5 rounded text-gray-200 transition-colors">
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
