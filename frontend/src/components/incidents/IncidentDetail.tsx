import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, PlayCircle, Shield, Target, AlertTriangle, FastForward } from 'lucide-react';
import { Badge } from '../common/Badge';
import { Panel } from '../common/Panel';
import { ForecastVsActual } from '../forecast/ForecastVsActual';

export const IncidentDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'timeline' | 'forecast' | 'mitre' | 'forensics' | 'response'>('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'forecast', label: 'Forecast History' },
    { id: 'mitre', label: 'ATT&CK' },
    { id: 'forensics', label: 'Forensics' },
    { id: 'response', label: 'Response' }
  ] as const;

  return (
    <div className="flex flex-col h-full bg-gray-950 overflow-hidden">
      {/* Header */}
      <div className="h-14 border-b border-gray-800 bg-gray-900 flex items-center px-4 gap-4 shrink-0">
        <button onClick={() => navigate('/incidents')} className="text-gray-400 hover:text-gray-200">
          <ArrowLeft size={18} />
        </button>
        <div className="flex items-center gap-3 border-r border-gray-800 pr-4">
          <span className="font-mono font-bold text-lg text-emerald-400">{id}</span>
          <Badge variant="critical">CRITICAL</Badge>
          <span className="text-xs font-mono uppercase text-red-400 border border-red-400/30 bg-red-400/10 px-2 py-0.5 rounded">ACTIVE</span>
        </div>
        <div className="flex-1 truncate">
          <h1 className="text-base font-medium text-gray-200 truncate">Ransomware precursor behavior on segment A</h1>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => navigate(`/replay/${id}`)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs rounded transition-colors border border-gray-700"
          >
            <PlayCircle size={14} /> Replay Incident
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 bg-gray-900/50 px-4 shrink-0">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id 
                ? 'border-emerald-500 text-emerald-400' 
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 custom-scrollbar">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-12 gap-4 h-full">
            <div className="col-span-8 flex flex-col gap-4">
              <Panel title="Executive Summary" className="shrink-0">
                <p className="text-sm text-gray-300 leading-relaxed">
                  Multiple indicators suggest early-stage ransomware activity. Initial access likely achieved via SMB brute force on 10.0.0.5, followed by successful lateral movement to 192.168.1.45. The AI model forecasts a 92% probability of exfiltration occurring within the next 5 minutes.
                </p>
              </Panel>
              
              <Panel title="Blast Radius & Affected Hosts" className="flex-1 min-h-[300px]">
                <div className="flex items-center justify-center h-full text-gray-500 font-mono text-sm border border-dashed border-gray-800 m-4 rounded">
                  [Mini Topology Visualization goes here]
                </div>
              </Panel>
            </div>
            <div className="col-span-4 flex flex-col gap-4">
              <Panel title="Current Status" className="shrink-0">
                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-gray-500 font-mono mb-1">CURRENT STAGE</div>
                    <div className="flex items-center gap-2">
                      <Target size={16} className="text-red-500" />
                      <span className="text-gray-200 font-bold">Lateral Movement</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 font-mono mb-1">AI FORECAST (T+5m)</div>
                    <div className="flex items-center gap-2">
                      <FastForward size={16} className="text-orange-500" />
                      <span className="text-gray-200 font-bold">Exfiltration (92%)</span>
                    </div>
                  </div>
                </div>
              </Panel>
            </div>
          </div>
        )}
        
        {activeTab === 'forecast' && (
          <div className="h-[400px]">
             <Panel title="Forecast vs Actual Timeline" className="h-full">
               <ForecastVsActual />
             </Panel>
          </div>
        )}

        {/* Other tabs would have their content... */}
        {activeTab !== 'overview' && activeTab !== 'forecast' && (
           <div className="flex items-center justify-center h-full text-gray-500 font-mono">
             CONTENT FOR {activeTab.toUpperCase()}
           </div>
        )}
      </div>
    </div>
  );
};

export default IncidentDetail;
