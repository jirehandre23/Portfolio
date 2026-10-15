import {analyze,portfolio} from './engine.mjs';
const $=id=>document.getElementById(id),money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
let loans=[],current=[];
const scenario=()=>[$('revenue').value/100,$('expense').value/100,$('rate').value/10000];
const element=(tag,text,cls)=>{const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;};
function render(){
 const params=scenario();current=loans.map(x=>analyze(x,...params));const total=portfolio(current);
 $('revenue-value').textContent=`${$('revenue').value}%`;$('expense-value').textContent=`${$('expense').value}%`;$('rate-value').textContent=`${$('rate').value} bp`;
 $('exposure').textContent=`$${(total.exposure/1e6).toFixed(1)}M`;$('dscr').textContent=`${total.dscr.toFixed(2)}×`;$('breaches').textContent=`${total.breaches} / ${loans.length}`;$('risk').textContent=`${(100*total.breach_share).toFixed(0)}%`;
 $('summary').textContent=total.breaches?`${total.breaches} borrowers fall below their modeled covenant, representing ${money(total.breached_exposure)} in principal. Inspect individual cash flow before drawing a conclusion.`:'All six fictional borrowers meet their modeled covenants in this scenario. This does not measure their probability of default.';
 const tbody=$('borrowers');tbody.replaceChildren();current.forEach((x,i)=>{const tr=document.createElement('tr');[x.name,loans[i].rate_type,`${x.dscr.toFixed(2)}×`,`${x.covenant.toFixed(2)}×`,x.cash_days.toFixed(0)].forEach(v=>tr.append(element('td',v)));tr.append(element('td',x.breach?'Below covenant':'Meets covenant',`flag ${x.breach?'bad':'ok'}`));tbody.append(tr);});
 renderBorrower();
}
function renderBorrower(){
 const i=Number($('borrower').value||0),row=current[i],loan=loans[i];if(!row)return;
 const dl=document.createElement('dl');
 for(const [label,value] of [['Stressed revenue',money(row.revenue)],['− Operating expenses',money(row.expenses)],['= Cash available for debt service',money(row.cfads)],['Annual debt service',money(row.debt_service)],['DSCR',`${row.dscr.toFixed(3)}×`],['Covenant cash headroom',money(row.covenant_cash_gap)],['Revenue headroom to covenant',`${(100*row.revenue_headroom).toFixed(1)}%`],['Opening cash + annual cash after debt',money(row.cash_after_year)]]){dl.append(element('dt',label),element('dd',value));}
 $('calculation').replaceChildren(dl);
 const table=document.createElement('table'),head=document.createElement('tr');['Revenue / rate', '0 bp','100 bp','200 bp','300 bp','400 bp'].forEach(t=>head.append(element('th',t)));table.append(head);
 for(const rev of [0,-.05,-.1,-.15,-.2]){const tr=document.createElement('tr');tr.append(element('th',`${(rev*100).toFixed(0)}%`));for(const shock of [0,.01,.02,.03,.04]){const r=analyze(loan,rev,scenario()[1],shock);tr.append(element('td',`${r.dscr.toFixed(2)}×`,r.dscr<1?'bad':r.breach?'warn':'ok'));}table.append(tr);}
 $('heatmap').replaceChildren(table);
}
for(const id of ['revenue','expense','rate'])$(id).addEventListener('input',()=>{document.querySelectorAll('[data-preset]').forEach(b=>b.classList.remove('active'));render();});
$('borrower').addEventListener('change',renderBorrower);
for(const b of document.querySelectorAll('[data-preset]'))b.addEventListener('click',()=>{const values={baseline:[0,0,0],moderate:[-5,3,200],severe:[-10,7,400]}[b.dataset.preset];['revenue','expense','rate'].forEach((id,i)=>$(id).value=values[i]);document.querySelectorAll('[data-preset]').forEach(x=>x.classList.toggle('active',x===b));render();});
$('download').addEventListener('click',()=>{const data={data_source:'fictional educational fixtures',scenario:scenario(),portfolio:portfolio(current),borrowers:current};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='creditlens-scenario.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
try{const r=await fetch('./data/borrowers.json');if(!r.ok)throw new Error('Could not load portfolio');loans=await r.json();loans.forEach((x,i)=>{const option=element('option',x.name);option.value=i;$('borrower').append(option);});render();}catch(e){$('error').hidden=false;$('error').textContent=`Unable to load the model: ${e.message}. Serve this directory over HTTP rather than opening the file directly.`;}
