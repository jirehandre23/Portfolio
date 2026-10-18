import fs from 'node:fs';
import assert from 'node:assert/strict';
const load=p=>JSON.parse(fs.readFileSync(new URL('../projects/'+p+'/data.json',import.meta.url)));
const netflix=load('netflix');assert.equal(netflix.source_rows,8807);assert.equal(netflix.buckets.reduce((n,x)=>n+x.count,0),8807);assert.equal(netflix.buckets.filter(x=>x.type==='Movie').reduce((n,x)=>n+x.count,0),6131);
const hr=load('hr-analytics');assert.equal(hr.counts.active_at_snapshot+hr.counts.terminated_at_snapshot,hr.counts.eligible_records);assert.equal(Object.values(hr.annual_flows).reduce((n,x)=>n+x.net_flow,0),hr.counts.active_at_snapshot);assert.ok(!JSON.stringify(hr).includes('first_name'));
const geo=load('congo-basin');assert.equal(geo.countries.length,5);for(const x of geo.countries)assert.ok(Math.abs(x.total-x.etm-x.non_etm)<.2);
assert.ok(Math.abs(geo.countries.reduce((n,x)=>n+x.total,0)-1381819.1)<.2);
console.log('PASS: Netflix counts, HR reconciliation/privacy scope and historical Congo area consistency');
