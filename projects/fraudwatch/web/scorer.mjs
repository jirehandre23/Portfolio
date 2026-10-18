const fields=['amount','hour','distance_km','account_age_days','is_international'];
export function validate(tx) {
 for(const key of fields) if(typeof tx[key]!=='number'||!Number.isFinite(tx[key]))throw new Error(`${key} must be a finite number.`);
 if(tx.amount<=0||tx.amount>1e6)throw new Error('Amount must be above 0 and at most 1,000,000.');
 if(!Number.isInteger(tx.hour)||tx.hour<0||tx.hour>23)throw new Error('Hour must be an integer from 0 to 23.');
 if(tx.distance_km<0||tx.distance_km>20000)throw new Error('Distance must be between 0 and 20,000 km.');
 if(!Number.isInteger(tx.account_age_days)||tx.account_age_days<0||tx.account_age_days>36500)throw new Error('Account age must be a whole number from 0 to 36,500 days.');
 if(![0,1].includes(tx.is_international))throw new Error('International must be 0 or 1.');
}
export function predict(model,tx) {
 validate(tx);
 if(model.format!=='fraudwatch-numeric-v1'||model.features.join(',')!=='log_amount,hour,distance_km,account_age_days,is_international')throw new Error('Unsupported model format.');
 const f=[Math.log1p(tx.amount),tx.hour,tx.distance_km,tx.account_age_days,tx.is_international].map(Math.fround);
 let margin=Math.fround(Math.log(model.base_score/(1-model.base_score)));
 for(const t of model.trees) {
  let node=0;
  while(t.left[node]!==-1)node=f[t.feature[node]]<Math.fround(t.value[node])?t.left[node]:t.right[node];
  margin=Math.fround(margin+Math.fround(t.value[node]));
 }
 return 1/(1+Math.exp(-margin));
}
export function summarize(rows,threshold) {
 const labeled=rows.filter(x=>x.label===0||x.label===1);
 const tp=labeled.filter(x=>x.score>=threshold&&x.label===1).length;
 const fp=labeled.filter(x=>x.score>=threshold&&x.label===0).length;
 const fn=labeled.filter(x=>x.score<threshold&&x.label===1).length;
 const tn=labeled.length-tp-fp-fn;
 return {count:rows.length,flagged:rows.filter(x=>x.score>=threshold).length,labeled:labeled.length,tp,fp,fn,tn,
         precision:tp+fp?tp/(tp+fp):null,recall:tp+fn?tp/(tp+fn):null};
}
