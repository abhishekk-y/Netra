import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings } from 'lucide-react';

export const JudgeMode: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'j') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-purple-600/20 border border-purple-500/50 text-purple-400 p-2 rounded-full hover:bg-purple-600/30 transition-colors z-50 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
        title="SIH Judge Mode (Ctrl+J)"
      >
        <Settings size={20} />
      </button>
    );
  }

  const buttons = [
    { label: '1. Network', path: '/topology' },
    { label: '2. Attack Starts', path: '/alerts' },
    { label: '3. Forecast', path: '/forecast' },
    { label: '4. Explain', path: '/incidents' },
    { label: '5. Forensics', path: '/packets' },
    { label: '6. Deception', path: '/deception' },
    { label: '7. Playback', path: '/replay/INC-001' },
    { label: '8. Results', path: '/' },
  ];

  return (
    <div className="fixed inset-0 bg-gray-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-purple-500/50 rounded-lg p-6 max-w-2xl w-full shadow-2xl">
        <div className="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
              <span className="text-purple-500">◆</span> SIH Demo Navigation
            </h2>
            <p className="text-sm text-gray-400 mt-1">Guided tour for Smart India Hackathon evaluation</p>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-white px-3 py-1 rounded bg-gray-800">
            Close (Ctrl+J)
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {buttons.map((btn, idx) => (
            <button
              key={idx}
              onClick={() => {
                navigate(btn.path);
                setIsOpen(false);
              }}
              className="bg-gray-800 hover:bg-purple-900/40 border border-gray-700 hover:border-purple-500 p-4 rounded text-left transition-all group flex flex-col justify-center min-h-[80px]"
            >
              <span className="font-mono text-xs text-purple-400 mb-1 group-hover:text-purple-300">STEP {idx + 1}</span>
              <span className="text-gray-200 font-bold group-hover:text-white">{btn.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
