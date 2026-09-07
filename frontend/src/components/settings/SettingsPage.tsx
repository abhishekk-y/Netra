import React from 'react';
import { Panel } from '../common/Panel';
import { useAppStore } from '../../stores/appStore';
import { useUIStore } from '../../stores/uiStore';

export const SettingsPage: React.FC = () => {
  const { platformName, setPlatformName, performanceProfile, setPerformanceProfile } = useAppStore();
  const { theme, toggleTheme } = useUIStore();
  const isDark = theme === 'dark';

  return (
    <div className={`p-6 h-full overflow-auto custom-scrollbar max-w-4xl mx-auto ${isDark ? 'bg-[#000]' : 'bg-transparent'}`}>
      <h1 className={`text-2xl font-bold mb-6 ${isDark ? 'text-gray-100 font-mono tracking-tighter' : 'text-slate-800'}`}>Platform Settings</h1>
      
      <div className="space-y-6">
        <Panel title="General Options">
          <div className="space-y-5 p-4">
            
            <div className={`flex justify-between items-center pb-6 border-b ${isDark ? 'border-gray-800' : 'border-slate-100'}`}>
              <div>
                <div className={`font-semibold text-lg ${isDark ? 'text-gray-200' : 'text-slate-800'}`}>UI Theme Mode</div>
                <div className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>Switch between the Intense Dark Mode and Enterprise Light Mode</div>
              </div>
              <button 
                onClick={toggleTheme}
                className={`px-5 py-2.5 rounded-xl font-semibold transition-all duration-300 transform hover:-translate-y-0.5 shadow-sm ${
                  isDark ? 'bg-white text-black hover:bg-gray-200 hover:shadow-[0_0_15px_rgba(255,255,255,0.3)]' 
                         : 'bg-gradient-to-r from-indigo-600 to-[#00bceb] text-white hover:shadow-lg hover:shadow-indigo-200 border border-transparent'
                }`}
              >
                {isDark ? 'Switch to Enterprise Light' : 'Switch to Intense Dark'}
              </button>
            </div>

            <div>
              <label className={`block text-xs font-semibold mb-2 uppercase ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>Platform Name</label>
              <input 
                type="text" 
                value={platformName} 
                onChange={(e) => setPlatformName(e.target.value)}
                className={`w-full border rounded p-2 text-sm outline-none transition-colors ${
                  isDark ? 'bg-[#111] border-[#333] text-gray-100 focus:border-rose-500' : 'bg-white border-slate-200 text-slate-800 focus:border-[#00bceb] focus:ring-2 focus:ring-[#00bceb]/20'
                }`}
              />
            </div>
            
            <div>
              <label className={`block text-xs font-semibold mb-2 uppercase ${isDark ? 'text-gray-400' : 'text-slate-500'}`}>Performance Profile</label>
              <select 
                value={performanceProfile}
                onChange={(e) => setPerformanceProfile(e.target.value as any)}
                className={`w-full border rounded p-2 text-sm outline-none transition-colors ${
                  isDark ? 'bg-[#111] border-[#333] text-gray-100 focus:border-rose-500' : 'bg-white border-slate-200 text-slate-800 focus:border-[#00bceb]'
                }`}
              >
                <option value="high">High Performance (Real-time updates, full animations)</option>
                <option value="balanced">Balanced (Throttled updates, smooth animations)</option>
                <option value="power-saver">Power Saver (Polling only, reduced animations)</option>
              </select>
            </div>
          </div>
        </Panel>

        <Panel title="Data Retention">
          <div className="space-y-4 p-4">
            <div className={`flex justify-between items-center border-b pb-4 ${isDark ? 'border-[#333]' : 'border-slate-100'}`}>
              <div>
                <div className={`font-medium ${isDark ? 'text-gray-200' : 'text-slate-700'}`}>Full PCAP Retention</div>
                <div className={`text-sm ${isDark ? 'text-gray-500' : 'text-slate-500'}`}>How long to store full packet captures</div>
              </div>
              <select className={`border rounded p-2 text-sm outline-none ${isDark ? 'bg-[#111] border-[#333] text-gray-100' : 'bg-white border-slate-200 text-slate-800'}`}>
                <option>3 Days</option>
                <option>7 Days</option>
                <option>14 Days</option>
              </select>
            </div>
          </div>
        </Panel>

      </div>
    </div>
  );
};

export default SettingsPage;
