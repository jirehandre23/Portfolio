import {predict,summarize} from './scorer.mjs';
const $=id=>document.getElementById(id),percent=x=>`${(100*x).toFixed(2)}%`,money=x=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(x);
let model,samples,rows=[],latestCustom=null,latestScore=null,counter=0;
const threshold=()=>Number($('review-threshold').value)/100;
const cell=text=>{const td=document.createElement('td');td.textContent=text;return td;};
function render(){
 const t=threshold(),m=summarize(rows,t);$('threshold-value').textContent=`${Math.round(100*t)}%`;
 for(const [id,value] of Object.entries({count:m.count,flagged:m.flagged,labeled:m.labeled,recall:m.recall===null?'—':`${(100*m.recall).toFixed(1)}%`}))$(id).textContent=value;
 if(latestScore!==null){$('latest-score').textContent=percent(latestScore);$('decision').textContent=latestScore>=t?'Review suggested':'Below review threshold';$('decision').classList.toggle('review',latestScore>=t);}
 else{$('latest-score').textContent='—';$('decision').textContent='Submit a transaction to begin';$('decision').classList.remove('review');}
 $('label-summary').textContent=m.labeled?`On ${m.labeled} labeled outcomes: ${m.tp} caught fraud, ${m.fn} missed fraud, ${m.fp} false alarms, ${m.tn} correctly unflagged. Precision: ${m.precision===null?'not defined':(100*m.precision).toFixed(1)+'%'}. These sample outcomes are not production performance.`:'Add or reveal labels to evaluate mistakes. Model performance cannot be measured from scores alone.';
 const body=$('transaction-history');body.replaceChildren();
 if(!rows.length){const tr=document.createElement('tr'),td=cell('No transactions yet.');td.colSpan=5;tr.append(td);body.append(tr);}
 for(const row of rows.slice(-30).reverse()){const tr=document.createElement('tr');[row.id,money(row.transaction.amount),percent(row.score),row.score>=t?'Review':'Below threshold',row.label===1?'Fraud':row.label===0?'Legitimate':'Not revealed'].forEach(x=>tr.append(cell(x)));body.append(tr);}
 $('label-legit').disabled=$('label-fraud').disabled=latestCustom===null;
 $('reveal-labels').disabled=!rows.some(r=>r.expectedLabel!==undefined&&r.label===undefined);
}
function setPreset(unusual){const tx=unusual?{amount:1500,hour:2,distance:1500,'account-age':10,international:1}:{amount:25,hour:14,distance:2,'account-age':2000,international:0};for(const [key,value]of Object.entries(tx))$(key).value=value;}
$('preset-routine').addEventListener('click',()=>setPreset(false));$('preset-unusual').addEventListener('click',()=>setPreset(true));
$('score-form').addEventListener('submit',e=>{e.preventDefault();$('input-error').hidden=true;try{
 const tx={amount:Number($('amount').value),hour:Number($('hour').value),distance_km:Number($('distance').value),account_age_days:Number($('account-age').value),is_international:Number($('international').value)};
 const score=predict(model,tx);latestCustom={id:`custom-${String(++counter).padStart(3,'0')}`,transaction:tx,score};rows.push(latestCustom);latestScore=score;render();
}catch(error){$('input-error').textContent=error.message;$('input-error').hidden=false;}});
$('review-threshold').addEventListener('input',render);
for(const [id,label]of [['label-legit',0],['label-fraud',1]])$(id).addEventListener('click',()=>{if(latestCustom){latestCustom.label=label;render();}});
function loadBatch(name){rows=samples[name].map(x=>({id:x.id,transaction:x.transaction,expectedLabel:x.label,score:predict(model,x.transaction)}));latestCustom=null;latestScore=rows.at(-1).score;$('batch-message').textContent=`Loaded 500 ${name==='normal'?'normal':'shifted'} synthetic examples. Labels are hidden until you reveal them.`;render();}
$('batch-normal').addEventListener('click',()=>loadBatch('normal'));$('batch-shifted').addEventListener('click',()=>loadBatch('shifted'));
$('reveal-labels').addEventListener('click',()=>{for(const row of rows)if(row.expectedLabel!==undefined)row.label=row.expectedLabel;$('batch-message').textContent='Synthetic sample labels revealed. Inspect the errors below; a change between samples alone does not establish real-world model decay.';render();});
$('clear-session').addEventListener('click',()=>{rows=[];latestCustom=null;latestScore=null;counter=0;$('batch-message').textContent='Session cleared.';render();});
async function load(){
 $('retry-demo').hidden=true;$('demo-status').textContent='Loading the trained model…';
 try{
  const responses=await Promise.all([fetch(new URL('./model.json',import.meta.url)),fetch(new URL('./samples.json',import.meta.url))]);
  if(responses.some(r=>!r.ok))throw new Error('Model assets could not be downloaded.');
  [model,samples]=await Promise.all(responses.map(r=>r.json()));
  predict(model,samples.normal[0].transaction); // Validate exported model before enabling controls.
  $('review-threshold').value=Math.round(model.threshold*100);
  $('tx-fields').disabled=false;for(const id of ['review-threshold','batch-normal','batch-shifted','clear-session'])$(id).disabled=false;
  $('demo-status').textContent=`Ready · ${model.trees.length} XGBoost trees loaded · inference runs in your browser.`;
  $('model-provenance').textContent=`Model version: ${model.model_version}. Source model SHA-256: ${model.source_sha256}. The browser executes the numeric tree ensemble with the same log-amount feature transformation as Python. Test tolerance: 0.000002 absolute score difference.`;
  render();
 }catch(error){$('demo-status').textContent=`Demo could not load: ${error.message} Check your connection and retry.`;$('retry-demo').hidden=false;}
}
$('retry-demo').addEventListener('click',load);load();
