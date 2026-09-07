import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Download, Upload, FileSearch } from 'lucide-react';
import { api } from '../../services/api';
import { Page, QueryState } from '../WorkspacePages';
import { Panel } from '../common/Panel';
import { DataTable } from '../common/DataTable';

type Packet = {id:string;timestamp:string;srcIp:string;dstIp:string;protocol:string;length:number;info:string;artifactId:string;flowId:string;index:number};
type Detail = Packet & {rawHex:string;ascii:string;layers:unknown;truncated:boolean};
type Evidence = {id?:string;sha256?:string;filename?:string;size?:number;packetCount?:number};
export default function PacketsPage() {
 const [params]=useSearchParams(); const [page,setPage]=useState(1);const [selected,setSelected]=useState<string|null>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);const client=useQueryClient();
 const packets=useQuery({queryKey:['packets',page,params.get('flowId')],queryFn:async()=>(await api.get<{data:Packet[];total:number}>('/packets',{params:{page,pageSize:50,flowId:params.get('flowId')||undefined}})).data});
 const evidence=useQuery({queryKey:['evidence'],queryFn:async()=>(await api.get<{data:Evidence[]}>('/evidence')).data});
 const detail=useQuery({queryKey:['packet',selected],queryFn:async()=>(await api.get<Detail>(`/packets/${selected}`)).data,enabled:!!selected});
 async function upload(file:File){setBusy(true);setError('');try{if(file.size>16*1024*1024)throw new Error('Choose a PCAP no larger than 16 MiB.');await api.post('/evidence/pcap',file,{headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name)},timeout:60000});setPage(1);await client.invalidateQueries();}catch(e){setError(e instanceof Error?e.message:'PCAP import failed.');}finally{setBusy(false);}}
 async function download(id:string,name:string){setError('');try{const res=await api.get(`/evidence/${id}/download`,{responseType:'blob'});const url=URL.createObjectURL(res.data);const link=document.createElement('a');link.href=url;link.download=name;link.click();URL.revokeObjectURL(url);}catch{setError('Unable to download this evidence artifact.');}}
 return <Page title="Packet inspector" description="Import a packet capture, inspect recorded bytes and decoded fields, and retain the original evidence artifact." action={<label className="button primary"><Upload size={16}/>{busy?'Importing...':'Import PCAP'}<input type="file" accept=".pcap,.pcapng,.cap" className="sr-only" disabled={busy} onChange={e=>{const file=e.target.files?.[0];if(file)upload(file);e.target.value='';}}/></label>}>
  <QueryState queries={[packets,evidence]}/>{error&&<div className="notice error" role="alert">{error}</div>}
  <div className="toolbar"><span className="muted">{packets.data?.total||0} recorded packets {params.get('flowId')&&` / Flow ${params.get('flowId')}`}</span><button className="button" disabled={page===1} onClick={()=>setPage(p=>p-1)}>Previous</button><span className="muted">Page {page}</span><button className="button" disabled={page*50>=(packets.data?.total||0)} onClick={()=>setPage(p=>p+1)}>Next</button></div>
  <div className="table-card"><DataTable data={packets.data?.data||[]} keyExtractor={p=>p.id} selectedId={selected||undefined} columns={[{key:'index',header:'No.',render:p=><button className="link" onClick={()=>setSelected(p.id)}>Inspect {p.index}</button>},{key:'timestamp',header:'Timestamp',render:p=>new Date(p.timestamp).toLocaleString()},{key:'srcIp',header:'Source'},{key:'dstIp',header:'Destination'},{key:'protocol',header:'Protocol'},{key:'length',header:'Bytes'},{key:'info',header:'Summary'}]} emptyMessage="No packet capture imported. Flow JSON does not contain raw packet bytes."/></div>
  {selected&&<><QueryState queries={[detail]}/>{detail.data&&<div className="chart-grid"><Panel title="Decoded protocol layers"><pre className="text-xs whitespace-pre-wrap break-all">{JSON.stringify(detail.data.layers,null,2)}</pre></Panel><Panel title="Recorded bytes"><pre className="text-xs whitespace-pre-wrap break-all font-mono">{detail.data.rawHex}</pre><hr className="my-4 border-[var(--color-border)]"/><pre className="text-xs whitespace-pre-wrap break-all">{detail.data.ascii}</pre>{detail.data.truncated&&<p className="muted mt-3">Preview truncated. Download the original evidence for the complete packet.</p>}</Panel></div>}</>}
  <Panel title="Evidence artifacts">{evidence.data?.data.length?<div className="space-y-3">{evidence.data.data.map((artifact,i)=><div className="toolbar" key={artifact.sha256||artifact.id||i}><FileSearch size={18}/><div className="flex-1 min-w-0"><p>{artifact.filename||'Packet capture'}</p><p className="muted font-mono break-all">SHA-256: {artifact.sha256||artifact.id}</p></div><button className="button" onClick={()=>download(artifact.sha256||artifact.id||'',artifact.filename||'evidence.pcap')}><Download size={15}/>Original PCAP</button></div>)}</div>:<p className="muted">Imported captures appear here with their evidence identifiers.</p>}</Panel>
 </Page>;
}
