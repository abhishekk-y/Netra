import React, { useState } from 'react';
import { PanelGroup, Panel as ResizablePanel, PanelResizeHandle } from 'react-resizable-panels';
import { FilterBar } from '../common/FilterBar';
import { DataTable } from '../common/DataTable';
import { Panel } from '../common/Panel';

export const PacketsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  
  const mockPackets = [
    { no: 1, time: '0.000000', src: '192.168.1.45', dst: '10.0.0.5', proto: 'TCP', len: 74, info: '54321 > 80 [SYN] Seq=0 Win=64240 Len=0 MSS=1460' },
    { no: 2, time: '0.001243', src: '10.0.0.5', dst: '192.168.1.45', proto: 'TCP', len: 74, info: '80 > 54321 [SYN, ACK] Seq=0 Ack=1 Win=28960 Len=0 MSS=1460' },
    { no: 3, time: '0.001300', src: '192.168.1.45', dst: '10.0.0.5', proto: 'TCP', len: 54, info: '54321 > 80 [ACK] Seq=1 Ack=1 Win=64240 Len=0' },
    { no: 4, time: '0.004500', src: '192.168.1.45', dst: '10.0.0.5', proto: 'HTTP', len: 432, info: 'GET / HTTP/1.1' },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-950">
      <FilterBar placeholder="Display filter (e.g. tcp.port == 80)..." onSearch={setSearch} />
      
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="vertical">
          <ResizablePanel defaultSize={40} minSize={20}>
            <DataTable
              data={mockPackets}
              keyExtractor={p => p.no.toString()}
              columns={[
                { key: 'no', header: 'NO.', width: 'w-16', render: p => <span className="font-mono text-gray-500">{p.no}</span> },
                { key: 'time', header: 'TIME', width: 'w-24', render: p => <span className="font-mono text-gray-400">{p.time}</span> },
                { key: 'src', header: 'SOURCE', width: 'w-32', render: p => <span className="font-mono">{p.src}</span> },
                { key: 'dst', header: 'DESTINATION', width: 'w-32', render: p => <span className="font-mono">{p.dst}</span> },
                { key: 'proto', header: 'PROTOCOL', width: 'w-20', render: p => <span className={`font-mono text-xs ${p.proto === 'HTTP' ? 'text-emerald-400' : 'text-blue-400'}`}>{p.proto}</span> },
                { key: 'len', header: 'LENGTH', width: 'w-20', align: 'right' },
                { key: 'info', header: 'INFO', render: p => <span className="font-mono text-[11px] text-gray-300">{p.info}</span> },
              ]}
            />
          </ResizablePanel>
          
          <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-emerald-500/50 cursor-row-resize transition-colors" />
          
          <ResizablePanel defaultSize={30} minSize={20}>
            <Panel title="Packet Details" className="h-full border-t-0 rounded-none border-l-0 border-r-0">
              <div className="font-mono text-xs text-gray-300 leading-relaxed space-y-1">
                <div className="flex gap-2"><span className="text-gray-500">▶</span> Frame 4: 432 bytes on wire (3456 bits)</div>
                <div className="flex gap-2"><span className="text-gray-500">▶</span> Ethernet II, Src: aa:bb:cc:dd:ee:ff, Dst: 11:22:33:44:55:66</div>
                <div className="flex gap-2 ml-4"><span className="text-gray-500">▼</span> Internet Protocol Version 4, Src: 192.168.1.45, Dst: 10.0.0.5</div>
                <div className="ml-8 text-gray-400">0100 .... = Version: 4</div>
                <div className="ml-8 text-gray-400">.... 0101 = Header Length: 20 bytes (5)</div>
                <div className="flex gap-2 ml-4"><span className="text-gray-500">▶</span> Transmission Control Protocol, Src Port: 54321, Dst Port: 80</div>
                <div className="flex gap-2 ml-4"><span className="text-gray-500">▶</span> Hypertext Transfer Protocol</div>
              </div>
            </Panel>
          </ResizablePanel>
          
          <PanelResizeHandle className="h-1 bg-gray-800 hover:bg-emerald-500/50 cursor-row-resize transition-colors" />
          
          <ResizablePanel defaultSize={30} minSize={20}>
            <Panel title="Packet Bytes" className="h-full border-t-0 rounded-none border-l-0 border-r-0 border-b-0">
              <div className="font-mono text-xs text-gray-400 whitespace-pre">
0000  11 22 33 44 55 66 aa bb cc dd ee ff 08 00 45 00   ."3DUf......E.
0010  01 a2 12 34 40 00 40 06 ab cd c0 a8 01 2d 0a 00   ...4@.@......-..
0020  00 05 d4 31 00 50 00 00 00 00 00 00 00 00 50 18   ...1.P........P.
0030  fa f0 12 34 00 00 47 45 54 20 2f 20 48 54 54 50   ...4..GET / HTTP
              </div>
            </Panel>
          </ResizablePanel>
        </PanelGroup>
      </div>
    </div>
  );
};

export default PacketsPage;
