import assert from 'node:assert/strict';
import fs from 'node:fs';
import {analyze,annualDebtService} from '../engine.mjs';
const fixtures=JSON.parse(fs.readFileSync(new URL('../reports/parity_fixtures.json',import.meta.url),'utf8'));
for(const {loan,params,expected} of fixtures){
 const got=analyze(loan,...params);
 for(const [key,value] of Object.entries(expected)) {
  if(typeof value==='number') assert.ok(Math.abs(got[key]-value)<=1e-8*Math.max(1,Math.abs(value)),key);
  else assert.equal(got[key],value,key);
 }
}
assert.equal(annualDebtService(120000,0,10),12000);
assert.throws(()=>annualDebtService(100,-.1,10));
console.log(`PASS: Python/JavaScript parity for ${fixtures.length} borrower-scenario combinations`);
