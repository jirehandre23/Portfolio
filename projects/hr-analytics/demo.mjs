import {$,node,bars,table,data} from '../shared/ui.mjs';
let audit;
function render(){if(!audit)return;const dep=$('department').value,metric=$('metric').value;const rows=Object.entries(audit.departments).filter(([name])=>dep==='all'||dep===name);
 const records=rows.reduce((s,[,x])=>s+x.records,0),terminated=rows.reduce((s,[,x])=>s+x.terminated,0);
 for(const [id,value]of Object.entries({records:records.toLocaleString('en-US'),active:(records-terminated).toLocaleString('en-US'),terminated:terminated.toLocaleString('en-US'),share:records?(100*terminated/records).toFixed(1)+'%':'—'}))$(id).textContent=value;
 const sorted=[...rows].sort((a,b)=>b[1][metric]-a[1][metric]);bars('department-bars',sorted.map(([name,x])=>[name,x[metric]]),x=>metric==='records'?x.toLocaleString('en-US'):x.toFixed(2)+(metric==='termination_share_pct'?'%':' y'));
 table('department-table',rows.map(([name,x])=>[name,x.records,x.records-x.terminated,x.terminated,x.termination_share_pct.toFixed(2)+'%',x.mean_tenure_years.toFixed(2)+' y']));
 table('quality-table',[['Reporting snapshot',audit.as_of],['Source rows',audit.source_rows],['Eligible records',audit.counts.eligible_records],['Under 18 at snapshot',audit.counts.under_18_at_snapshot],['Duplicate ID excess',audit.duplicate_id_excess],['Future exits still active',audit.counts.future_termination_still_active]]);
 table('flow-table',Object.entries(audit.annual_flows).filter(([year])=>Number(year)>=Number($('flow-from').value)).map(([year,x])=>[year,x.hires,x.exits,x.net_flow]));
 $('status').textContent=`Ready · ${audit.as_of} snapshot · ${dep==='all'?'all departments':dep}.`;
}
for(const id of ['department','metric','flow-from'])$(id).addEventListener('change',render);
try{audit=await data(new URL('./data.json',import.meta.url));for(const name of Object.keys(audit.departments).sort()){const option=node('option',name);option.value=name;$('department').append(option);}render();}catch(e){$('status').textContent=e.message+' Reload the page to retry.';}
