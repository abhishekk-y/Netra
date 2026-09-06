import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, Pause, SkipBack, SkipForward, ArrowLeft } from 'lucide-react';
import { Panel } from '../common/Panel';

export const ReplayPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [progress, setProgress] = useState(0);

  return (
    <div className="flex flex-col h-full bg-gray-950 overflow-hidden">
      {/* Header */}
      <div className="h-14 border-b border-gray-800 bg-gray-900 flex items-center px-4 gap-4 shrink-0">
        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-gray-200">
          <ArrowLeft size={18} />
        </button>
        <div className="flex items-center gap-3 border-r border-gray-800 pr-4">
          <span className="font-mono text-gray-400">REPLAY INCIDENT</span>
          <span className="font-mono font-bold text-emerald-400">{id}</span>
        </div>
        
        {/* Controls */}
        <div className="flex-1 flex items-center justify-center gap-4">
           <button className="text-gray-400 hover:text-gray-200"><SkipBack size={20} /></button>
           <button 
             className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30 flex items-center justify-center transition-colors border border-emerald-500/50"
             onClick={() => setIsPlaying(!isPlaying)}
           >
             {isPlaying ? <Pause size={20} /> : <Play size={20} className="ml-1" />}
           </button>
           <button className="text-gray-400 hover:text-gray-200"><SkipForward size={20} /></button>
           
           <div className="flex bg-gray-800 rounded ml-4 p-0.5">
             {[0.5, 1, 2, 5, 10].map(s => (
               <button 
                 key={s}
                 onClick={() => setSpeed(s)}
                 className={`px-2 py-1 text-xs font-mono rounded ${speed === s ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-gray-200'}`}
               >
                 {s}x
               </button>
             ))}
           </div>
        </div>
        
        <div className="font-mono text-emerald-400 font-bold">
          T - 14:32:01
        </div>
      </div>

      <div className="flex-1 flex flex-col p-2 gap-2 overflow-hidden">
        <div className="flex-1 flex gap-2 overflow-hidden">
          {/* Main Visualization Area */}
          <Panel title="Historical Topology State" className="flex-[3]">
            <div className="flex items-center justify-center h-full border border-dashed border-gray-800 m-4 rounded bg-gray-950 text-gray-600 font-mono text-sm">
              [Topology Replay Canvas]
            </div>
          </Panel>
          
          {/* Event Log */}
          <Panel title="Chronological Events" className="flex-[1]">
             <div className="space-y-4">
               {[
                 { t: 'T-14:32:01', msg: 'Initial compromise on 10.0.0.5' },
                 { t: 'T-14:32:05', msg: 'Command execution detected' },
                 { t: 'T-14:33:10', msg: 'Network enumeration started' },
               ].map((ev, i) => (
                 <div key={i} className="flex gap-3 text-sm">
                   <div className="font-mono text-gray-500 shrink-0">{ev.t}</div>
                   <div className="text-gray-300">{ev.msg}</div>
                 </div>
               ))}
             </div>
          </Panel>
        </div>
        
        {/* Scrubber */}
        <div className="h-16 bg-gray-900 border border-gray-800 rounded p-4 flex items-center shrink-0">
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={progress}
            onChange={(e) => setProgress(Number(e.target.value))}
            className="w-full accent-emerald-500"
          />
        </div>
      </div>
    </div>
  );
};

export default ReplayPage;
