import fs from 'node:fs';
import assert from 'node:assert/strict';
import {predict,summarize} from '../web/scorer.mjs';
const model=JSON.parse(fs.readFileSync(new URL('../web/model.json',import.meta.url)));
const fixtures=JSON.parse(fs.readFileSync(new URL('../reports/web_parity_fixtures.json',import.meta.url)));
let maxError=0;
for(const f of fixtures){const error=Math.abs(predict(model,f.transaction)-f.probability);maxError=Math.max(error,maxError);assert.ok(error<2e-6,`Python/browser mismatch: ${error}`);}
const tx=fixtures[0].transaction;
for(const bad of [{amount:0},{hour:24},{amount:NaN},{distance_km:-1},{account_age_days:1.5},{is_international:2}])assert.throws(()=>predict(model,{...tx,...bad}));
const m=summarize([{score:.8,label:1},{score:.6,label:0},{score:.1,label:1},{score:.2,label:0}],.5);
assert.equal(m.tp,1);assert.equal(m.fp,1);assert.equal(m.fn,1);assert.equal(m.tn,1);assert.equal(m.precision,.5);assert.equal(m.recall,.5);
assert.equal(summarize([], .5).recall,null);
console.log(`PASS: ${fixtures.length} real XGBoost/browser parity cases; max error ${maxError}; validation and feedback metrics`);
