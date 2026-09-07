import React, { useState, useEffect } from 'react';
import { Terminal, Database, ShieldAlert, Cpu } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';

export default function PacketsPage() {
  const [packets, setPackets] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const theme = useUIStore(s => s.theme);
  const isDark = theme === 'dark';

  useEffect(() => {
    // Generate synthetic realistic packets
    const p = [];
    for(let i=0; i<100; i++) {
      const isBad = Math.random() > 0.9;
      p.push({
        id: `PKT_${i.toString().padStart(5, '0')}`,
        time: new Date(Date.now() - i * 1000).toLocaleTimeString('en-US', { hour12: false }) + '.' + Math.floor(Math.random()*999),
        src: `10.0.${Math.floor(Math.random()*255)}.${Math.floor(Math.random()*255)}`,
        dst: `192.168.1.${Math.floor(Math.random()*255)}`,
        proto: ['TCP', 'UDP', 'ICMP', 'DNS'][Math.floor(Math.random()*4)],
        len: Math.floor(64 + Math.random() * 1400),
        flags: isBad ? '[SYN, ECE, CWR]' : '[PSH, ACK]',
        risk: isBad ? 90 + Math.random() * 10 : Math.random() * 20,
        hex: Array.from({length: 64}).map(() => Math.floor(Math.random()*255).toString(16).padStart(2, '0').toUpperCase())
      });
    }
    setPackets(p);
    setSelected(p[0]);
  }, []);

  return (
    <div className={`h-full flex flex-col tracking-tighter ${isDark ? 'bg-black text-gray-300 font-mono text-[9px] uppercase border border-[#333]' : 'bg-transparent text-sm'}`}>
      
      {/* HEADER */}
      <div className={`h-16 flex items-center justify-between px-6 shrink-0 shadow-sm ${isDark ? 'border-b border-[#333] bg-[#0A0A0A] text-gray-400' : 'bg-white/80 backdrop-blur-md rounded-t-2xl border border-slate-200 text-slate-700'}`}>
        <div className="flex items-center space-x-3 font-bold">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDark ? 'bg-blue-500/10' : 'bg-blue-50 shadow-sm border border-blue-100'}`}>
            <Database size={16} className={isDark ? "text-blue-500" : "text-blue-500"} />
          </div>
          <span className={`text-base tracking-tight ${!isDark ? 'text-slate-800' : ''}`}>Deep Packet Inspection (DPI)</span>
        </div>
        <div className="flex space-x-6">
          <span className={`text-sm font-medium ${!isDark ? 'text-slate-500' : ''}`}>Capture File: <span className={isDark ? 'text-white' : 'font-bold text-slate-800 bg-slate-100 px-2 py-1 rounded-md'}>eth0_live.pcap</span></span>
          <span className={`text-sm font-medium ${!isDark ? 'text-slate-500' : ''}`}>Packets Loaded: <span className={isDark ? 'text-white' : 'font-bold text-slate-800 bg-slate-100 px-2 py-1 rounded-md'}>{packets.length}</span></span>
        </div>
      </div>

      <div className={`flex-1 flex flex-col overflow-hidden ${isDark ? '' : 'bg-white rounded-b-2xl border-x border-b border-slate-200 shadow-sm'}`}>
        
        {/* TOP PANE: Packet List */}
        <div className={`h-[45%] flex flex-col ${isDark ? 'border-b border-[#333] bg-[#050505]' : 'border-b border-slate-100 bg-white'}`}>
          <div className="flex-1 overflow-auto custom-scrollbar p-2">
            <table className="w-full text-left whitespace-nowrap">
              <thead className={`sticky top-0 z-10 ${isDark ? 'bg-[#111] text-[#666] border-b border-[#333]' : 'bg-white text-slate-400 border-b border-slate-100/50 text-xs uppercase tracking-wider'}`}>
                <tr>
                  <th className="p-3 font-semibold">No.</th>
                  <th className="p-3 font-semibold">Time</th>
                  <th className="p-3 font-semibold">Source</th>
                  <th className="p-3 font-semibold">Destination</th>
                  <th className="p-3 font-semibold">Protocol</th>
                  <th className="p-3 font-semibold">Length</th>
                  <th className="p-3 font-semibold">Info / Flags</th>
                  <th className="p-3 font-semibold text-right">AI Risk</th>
                </tr>
              </thead>
              <tbody className={`divide-y ${isDark ? 'divide-[#222]' : 'divide-slate-50/50'}`}>
                {packets.map((p, i) => {
                  const isCritical = p.risk > 75;
                  const isSelected = selected?.id === p.id;
                  
                  let rowClass = 'cursor-pointer transition-all duration-200 ';
                  
                  if (isDark) {
                    rowClass += isSelected ? 'bg-[#1A1A1A] border-l-2 border-blue-500' : 'border-l-2 border-transparent hover:bg-[#111]';
                    if (isCritical) rowClass += ' bg-rose-950/20';
                  } else {
                    rowClass += isSelected ? 'bg-blue-50/50 shadow-sm scale-[0.995] rounded-xl' : 'hover:bg-slate-50 rounded-xl';
                    if (isCritical) rowClass += ' bg-red-50/30';
                  }

                  return (
                    <tr key={i} onClick={() => setSelected(p)} className={rowClass}>
                      <td className={`p-3 rounded-l-xl ${isDark ? 'text-[#555]' : 'text-slate-400 font-medium'}`}>{i + 1}</td>
                      <td className={`p-3 ${isDark ? 'text-[#777]' : 'text-slate-500'}`}>{p.time}</td>
                      <td className={`p-3 ${isDark ? 'text-[#ccc]' : 'text-slate-700 font-semibold'}`}>{p.src}</td>
                      <td className={`p-3 ${isDark ? 'text-[#ccc]' : 'text-slate-700 font-semibold'}`}>{p.dst}</td>
                      <td className={`p-3 font-bold ${isDark ? 'text-indigo-400' : 'text-indigo-500'}`}>{p.proto}</td>
                      <td className={`p-3 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>{p.len}</td>
                      <td className={`p-3 truncate max-w-[200px] ${isDark ? 'text-[#666]' : 'text-slate-500'}`}>{p.proto} {p.flags} Seq=1 Ack=1 Win=64240</td>
                      <td className={`p-3 text-right font-bold rounded-r-xl ${isCritical ? (isDark ? 'text-rose-500' : 'text-red-500') : (isDark ? 'text-emerald-500' : 'text-emerald-500')}`}>
                        <span className={!isDark && isCritical ? 'bg-red-100 text-red-600 px-2 py-1 rounded-md' : (!isDark ? 'bg-emerald-50 text-emerald-600 px-2 py-1 rounded-md' : '')}>
                          {p.risk.toFixed(1)}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* BOTTOM PANE: Packet Details */}
        <div className={`flex-1 flex ${isDark ? 'bg-black' : 'bg-transparent'}`}>
          
          {/* FRAME DECODER TREE */}
          <div className={`w-1/2 flex flex-col ${isDark ? 'border-r border-[#333] bg-[#050505]' : 'bg-slate-50/30'}`}>
            <div className={`p-4 flex items-center space-x-2 font-bold ${isDark ? 'border-b border-[#333] bg-[#111] text-gray-400' : 'text-slate-700'}`}>
              <Cpu size={16} className={isDark ? "text-emerald-500" : "text-emerald-500"} />
              <span>Protocol Decoder Tree</span>
            </div>
            {selected ? (
              <div className={`flex-1 p-6 overflow-auto custom-scrollbar font-mono ${isDark ? 'text-[10px] space-y-1' : 'text-xs space-y-2'}`}>
                <div><span className={isDark ? "text-emerald-400" : "text-indigo-500 font-bold"}>[-]</span> Frame {selected.id}: {selected.len} bytes on wire ({selected.len * 8} bits)</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Arrival Time: {selected.time}</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Frame Number: {selected.id.split('_')[1]}</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Frame Length: {selected.len} bytes</div>

                <div className="mt-4"><span className={isDark ? "text-emerald-400" : "text-indigo-500 font-bold"}>[-]</span> Ethernet II, Src: 00:1B:44:11:3A:B7, Dst: 00:1C:B3:09:85:15</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Destination: 00:1C:B3:09:85:15 (Cisco_09:85:15)</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Source: 00:1B:44:11:3A:B7 (Dell_11:3A:B7)</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Type: IPv4 (0x0800)</div>

                <div className="mt-4"><span className={isDark ? "text-emerald-400" : "text-indigo-500 font-bold"}>[-]</span> Internet Protocol Version 4, Src: {selected.src}, Dst: {selected.dst}</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Version: 4</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Header Length: 20 bytes (5)</div>
                <div className={`pl-4 ${isDark ? 'text-[#888]' : 'text-slate-500'}`}>Protocol: {selected.proto} (6)</div>

                <div className="mt-4"><span className={`${isDark ? 'text-rose-400' : 'text-red-500'} font-bold`}>[-]</span> {selected.proto} Protocol, Src Port: 443, Dst Port: 51920</div>
                <div className={`pl-4 ${isDark ? 'text-rose-300' : 'text-slate-500 font-medium'}`}>Flags: <span className={!isDark ? 'text-red-600 font-bold' : ''}>{selected.flags}</span></div>
                
                {selected.risk > 75 && (
                  <div className={`pl-4 mt-4 p-4 font-bold flex items-center space-x-2 rounded-xl shadow-sm ${isDark ? 'bg-rose-950/40 border border-rose-900/50 text-rose-400' : 'bg-red-50/80 border border-red-100 text-red-600'}`}>
                    <ShieldAlert size={16} />
                    <span>AI_INFERENCE: ANOMALOUS HEADER COMBINATION DETECTED</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-400 font-sans">No packet selected</div>
            )}
          </div>

          {/* HEX DUMP */}
          <div className={`w-1/2 flex flex-col ${isDark ? 'bg-[#020202]' : 'bg-slate-50 border-l border-slate-200'}`}>
            <div className={`p-4 flex items-center space-x-2 font-bold ${isDark ? 'border-b border-[#333] bg-[#111] text-gray-400' : 'text-slate-700'}`}>
              <Terminal size={16} className={isDark ? "text-purple-500" : "text-purple-500"} />
              <span>Raw Hex Dump</span>
            </div>
            {selected ? (
              <div className={`flex-1 p-6 overflow-auto custom-scrollbar font-mono select-text ${isDark ? 'text-[10px]' : 'text-xs'}`}>
                <div className={!isDark ? 'bg-white p-4 rounded-xl border border-slate-200 shadow-sm h-full' : ''}>
                  {Array.from({length: Math.ceil(selected.hex.length / 16)}).map((_, row) => {
                    const chunk = selected.hex.slice(row * 16, (row + 1) * 16);
                    const hexStr = chunk.join(' ');
                    
                    const asciiStr = chunk.map((h: string) => {
                      const code = parseInt(h, 16);
                      return (code >= 32 && code <= 126) ? String.fromCharCode(code) : '.';
                    }).join('');

                    return (
                      <div key={row} className={`flex space-x-4 mb-1.5 rounded px-2 py-1 transition-colors ${isDark ? 'hover:bg-[#111]' : 'hover:bg-slate-50'}`}>
                        <span className={`${isDark ? 'text-[#555]' : 'text-slate-400'} w-12 shrink-0`}>{(row * 16).toString(16).padStart(4, '0')}</span>
                        <span className={`flex-1 ${isDark ? 'text-[#AAA]' : 'text-slate-600 font-medium'} ${selected.risk > 75 && row === 2 ? (isDark ? 'text-rose-500 bg-rose-950/40 font-bold' : 'text-red-500 font-bold bg-red-50') : ''}`}>
                          {hexStr.padEnd(47, ' ')}
                        </span>
                        <span className={`w-16 shrink-0 ${isDark ? 'text-[#666]' : 'text-slate-400 font-bold'} ${selected.risk > 75 && row === 2 ? (isDark ? 'text-rose-400 font-bold' : 'text-red-500 font-bold') : ''}`}>
                          {asciiStr}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500 font-sans">No packet selected</div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
