import React from 'react';
import { Panel } from '../common/Panel';
import { useAppStore } from '../../stores/appStore';

export const SettingsPage: React.FC = () => {
  const { platformName, setPlatformName, performanceProfile, setPerformanceProfile } = useAppStore();

  return (
    <div className="p-4 bg-gray-950 h-full overflow-auto custom-scrollbar max-w-4xl mx-auto">
      <h1 className="text-xl font-bold text-gray-100 mb-6">Platform Settings</h1>
      
      <div className="space-y-6">
        <Panel title="General">
          <div className="space-y-4 p-2">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">PLATFORM NAME</label>
              <input 
                type="text" 
                value={platformName} 
                onChange={(e) => setPlatformName(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:border-emerald-500 outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">PERFORMANCE PROFILE</label>
              <select 
                value={performanceProfile}
                onChange={(e) => setPerformanceProfile(e.target.value as any)}
                className="w-full bg-gray-950 border border-gray-800 rounded p-2 text-sm text-gray-100 focus:border-emerald-500 outline-none transition-colors"
              >
                <option value="high">High Performance (Real-time updates, full animations)</option>
                <option value="balanced">Balanced (Throttled updates, smooth animations)</option>
                <option value="power-saver">Power Saver (Polling only, reduced animations)</option>
              </select>
            </div>
          </div>
        </Panel>

        <Panel title="Data Retention">
          <div className="space-y-4 p-2">
            <div className="flex justify-between items-center border-b border-gray-800 pb-2">
              <div>
                <div className="font-medium text-gray-200 text-sm">Full PCAP Retention</div>
                <div className="text-xs text-gray-500">How long to store full packet captures</div>
              </div>
              <select className="bg-gray-950 border border-gray-800 rounded p-1.5 text-sm text-gray-100">
                <option>3 Days</option>
                <option>7 Days</option>
                <option>14 Days</option>
              </select>
            </div>
            <div className="flex justify-between items-center border-b border-gray-800 pb-2">
              <div>
                <div className="font-medium text-gray-200 text-sm">Flow Data Retention</div>
                <div className="text-xs text-gray-500">How long to store network flow metadata</div>
              </div>
              <select className="bg-gray-950 border border-gray-800 rounded p-1.5 text-sm text-gray-100">
                <option>30 Days</option>
                <option>90 Days</option>
                <option>180 Days</option>
              </select>
            </div>
          </div>
        </Panel>

        <Panel title="Feature Flags">
          <div className="space-y-3 p-2">
            {[
              { id: 'f1', name: 'Enable Deception Network Integration', active: true },
              { id: 'f2', name: 'Advanced Threat Hunting Query Language', active: true },
              { id: 'f3', name: 'Experimental Graph Layout Algorithms', active: false },
              { id: 'f4', name: 'SIH Judge Mode UI', active: true },
            ].map(feature => (
              <label key={feature.id} className="flex items-center gap-3 cursor-pointer group">
                <div className={`w-10 h-5 rounded-full transition-colors relative ${feature.active ? 'bg-emerald-500' : 'bg-gray-800'}`}>
                  <div className={`absolute top-1 left-1 w-3 h-3 rounded-full bg-white transition-transform ${feature.active ? 'translate-x-5' : ''}`} />
                </div>
                <span className="text-sm text-gray-300 group-hover:text-gray-100 transition-colors">{feature.name}</span>
              </label>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
};

export default SettingsPage;
