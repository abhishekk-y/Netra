import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Download, Network, Route } from 'lucide-react';
import { api } from '../services/api';
import { Panel } from './common/Panel';
import { DataTable } from './common/DataTable';
import { QueryState } from './WorkspacePages';

type Snapshot={id:string;timestamp:string;currentStage:string;nextStages:{stage:string;probability:number}[];synthetic:boolean;outcome?:{observedStage:string;observedAt:string;leadTimeSeconds:number|null;prospective:boolean}};
export function ForecastHistory(){
 const query=useQuery({queryKey:['forecast-history'],queryFn:async()=>(await api.get<{data:Snapshot[]}>('/forecasts/history')).data,refetchInterval:15000});
 return <Panel title="Forecast versus later evidence"><QueryState queries={[query]}/><DataTable data={query.data?.data||[]} keyExtractor={s=>s.id} columns={[{key:'timestamp',header:'Snapshot created',render:s=>new Date(s.timestamp).toLocaleString()},{key:'currentStage',header:'Observed stage'},{key:'nextStages',header:'Predicted next stage',render:s=>s.nextStages[0]?.stage||'No prediction'},{key:'outcome',header:'Later rule match',render:s=>s.outcome?.observedStage||'Pending evidence'},{key:'lead',header:'Prospective lead time',render:s=>s.outcome?.prospective&&s.outcome.leadTimeSeconds!=null?`${s.outcome.leadTimeSeconds.toFixed(1)} seconds`:s.synthetic?'Synthetic replay / N/A':'Not established'}]}/><p className="muted mt-4">Later matches are rule-generated observations, not independent ground truth. Historical and synthetic records do not establish prospective forecasting accuracy.</p></Panel>;
}
export function ReportButton({id}:{id:string}){
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 async function download(){setBusy(true);try{const data=(await api.get(`/incidents/${id}/report`)).data;const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`netra-incident-${id}.json`;a.click();URL.revokeObjectURL(url);setError('');}catch{setError('Report export failed. Retry when the API is available.');}finally{setBusy(false);}}
 return <div><button className="button" disabled={busy} onClick={download}><Download size={15}/>{busy?'Preparing report...':'Export evidence report'}</button>{error&&<p role="alert" className="muted">{error}</p>}</div>;
}
export function GraphAnalysis({source}:{source:string}){
 const [destination,setDestination]=useState('');const [result,setResult]=useState<unknown>();const [error,setError]=useState('');const [busy,setBusy]=useState(false);
 async function run(mode:'path'|'blast-radius'){setBusy(true);setError('');try{setResult((await api.get(`/topology/${mode}`,{params:mode==='path'?{source,destination}:{source,max_hops:2}})).data);}catch{setError('No matching path or host is available. Use an observed IP address.');}finally{setBusy(false);}}
 return <Panel title={`Communication analysis / ${source}`}><p className="muted mb-3">Reachability is inferred from observed communications. It does not prove exploitation or firewall access.</p><div className="toolbar"><input aria-label="Path destination IP" placeholder="Destination IP" value={destination} onChange={e=>setDestination(e.target.value)}/><button className="button" disabled={busy||!destination} onClick={()=>run('path')}><Route size={15}/>Find path</button><button className="button" disabled={busy} onClick={()=>run('blast-radius')}><Network size={15}/>Two-hop neighborhood</button><Link className="button" to={`/flows?q=${encodeURIComponent(source)}`}>Inspect host flows</Link></div>{error&&<p className="notice error mt-3" role="alert">{error}</p>}{result!==undefined&&<details open className="mt-4"><summary className="link cursor-pointer">Analysis evidence</summary><pre className="text-xs overflow-auto max-h-72 mt-3">{JSON.stringify(result,null,2)}</pre></details>}</Panel>;
}
