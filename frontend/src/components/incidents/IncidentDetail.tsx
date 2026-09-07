import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, PlayCircle, Shield, Target, AlertTriangle, FastForward } from 'lucide-react';
import { Badge } from '../common/Badge';
import { Panel } from '../common/Panel';
import { ForecastVsActual } from '../forecast/ForecastVsActual';
import { useUIStore } from '../../stores/uiStore';

export const IncidentDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'timeline' | 'forecast' | 'mitre' | 'forensics' | 'response'>('overview');
  const { theme } = useUIStore();
  const isDark = theme === 'dark';

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
    <div className={`flex flex-col h-full overflow-hidden transition-colors duration-300 ${isDark ? 'bg-black' : 'bg-transparent'}`}>
      
      {/* Header */}
      <div className={`h-16 border-b flex items-center px-6 gap-6 shrink-0 transition-all ${isDark ? 'border-[#333] bg-[#0A0A0A]' : 'border-slate-200/60 bg-white/80 backdrop-blur-md rounded-t-2xl shadow-sm mx-6 mt-6'}`}>
        <button onClick={() => navigate('/incidents')} className={`flex items-center justify-center w-8 h-8 rounded-full transition-colors ${isDark ? 'text-gray-400 hover:text-white hover:bg-[#222]' : 'text-slate-400 hover:text-slate-700 bg-slate-50 hover:bg-slate-100'}`}>
          <ArrowLeft size={18} />
        </button>
        <div className={`flex items-center gap-4 pr-6 border-r ${isDark ? 'border-[#333]' : 'border-slate-200'}`}>
          <span className={`font-mono font-bold text-xl tracking-tight ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>{id}</span>
          <Badge variant="critical">CRITICAL</Badge>
          <span className={`text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-md ${isDark ? 'text-red-400 border border-red-900/50 bg-red-950/40' : 'text-red-600 border border-red-200 bg-red-50'}`}>ACTIVE</span>
        </div>
        <div className="flex-1 truncate">
          <h1 className={`text-lg font-bold truncate ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>Ransomware precursor behavior on segment A</h1>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => navigate(`/replay/${id}`)}
            className={`flex items-center gap-2 px-4 py-2 font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 ${
              isDark ? 'bg-[#111] hover:bg-[#222] text-gray-200 border border-[#333]' : 'bg-gradient-to-r from-indigo-600 to-[#00bceb] text-white border-transparent'
            }`}
          >
            <PlayCircle size={16} /> Replay Incident
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className={`flex border-b px-6 shrink-0 transition-colors ${isDark ? 'border-[#333] bg-[#050505]' : 'border-slate-200 bg-white/50 backdrop-blur-sm mx-6'}`}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-5 py-4 text-sm font-bold uppercase tracking-wider border-b-2 transition-all duration-200 ${
              activeTab === tab.id 
                ? (isDark ? 'border-emerald-500 text-emerald-400' : 'border-indigo-500 text-indigo-600') 
                : (isDark ? 'border-transparent text-gray-500 hover:text-gray-200 hover:border-[#333]' : 'border-transparent text-slate-400 hover:text-slate-700 hover:border-slate-300')
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className={`flex-1 overflow-auto p-6 custom-scrollbar ${isDark ? '' : 'mx-6 mb-6 bg-white/40 backdrop-blur-md rounded-b-2xl border-x border-b border-slate-200 shadow-sm'}`}>
        {activeTab === 'overview' && (
          <div className="grid grid-cols-12 gap-6 h-full">
            <div className="col-span-8 flex flex-col gap-6">
              <Panel title="Executive Summary" className="shrink-0">
                <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-300' : 'text-slate-600 font-medium'}`}>
                  Multiple indicators suggest early-stage ransomware activity. Initial access likely achieved via SMB brute force on <span className="font-mono font-bold text-indigo-500">10.0.0.5</span>, followed by successful lateral movement to <span className="font-mono font-bold text-emerald-500">192.168.1.45</span>. The AI model forecasts a <span className="font-bold text-rose-500">92% probability</span> of exfiltration occurring within the next 5 minutes.
                </p>
              </Panel>
              
              <Panel title="Blast Radius & Affected Hosts" className="flex-1 min-h-[300px]">
                <div className={`flex items-center justify-center h-full font-mono text-sm border-2 border-dashed m-6 rounded-2xl ${isDark ? 'text-gray-500 border-[#333]' : 'text-slate-400 border-slate-200 bg-slate-50/50'}`}>
                  [Mini Topology Visualization rendering...]
                </div>
              </Panel>
            </div>
            
            <div className="col-span-4 flex flex-col gap-6">
              <Panel title="Current Status" className="shrink-0">
                <div className="space-y-6">
                  <div className={`p-4 rounded-xl border ${isDark ? 'bg-[#111] border-[#333]' : 'bg-white shadow-sm border-slate-100'}`}>
                    <div className={`text-xs font-bold font-mono uppercase tracking-widest mb-2 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>CURRENT STAGE</div>
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDark ? 'bg-red-950/40' : 'bg-red-50'}`}>
                        <Target size={18} className={isDark ? "text-red-400" : "text-red-500"} />
                      </div>
                      <span className={`font-bold text-lg ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>Lateral Movement</span>
                    </div>
                  </div>
                  
                  <div className={`p-4 rounded-xl border ${isDark ? 'bg-[#111] border-[#333]' : 'bg-white shadow-sm border-slate-100'}`}>
                    <div className={`text-xs font-bold font-mono uppercase tracking-widest mb-2 ${isDark ? 'text-gray-500' : 'text-slate-400'}`}>AI FORECAST (T+5m)</div>
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDark ? 'bg-orange-950/40' : 'bg-orange-50'}`}>
                        <FastForward size={18} className={isDark ? "text-orange-400" : "text-orange-500"} />
                      </div>
                      <span className={`font-bold text-lg ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>Exfiltration (92%)</span>
                    </div>
                  </div>
                </div>
              </Panel>
            </div>
          </div>
        )}
        
        {activeTab === 'forecast' && (
          <div className="h-[500px]">
             <Panel title="Forecast vs Actual Timeline" className="h-full">
               <ForecastVsActual />
             </Panel>
          </div>
        )}

        {/* Other tabs would have their content... */}
        {activeTab !== 'overview' && activeTab !== 'forecast' && (
           <div className={`flex items-center justify-center h-full font-mono text-sm tracking-widest uppercase ${isDark ? 'text-[#333]' : 'text-slate-300'}`}>
             CONTENT FOR {activeTab} RENDERING...
           </div>
        )}
      </div>
    </div>
  );
};

export default IncidentDetail;
