import assert from 'node:assert/strict';
import {analyzeMemo,draftMemo} from './engine.mjs';
const x={organization:'Fictional borrower',period:'FY2025',purpose:'Renovation',revenue:3200000,expenses:2700000,debtService:330000,cash:600000,minDscr:1.2,minCash:60,reviewed:true,notes:'Confirm cash restrictions.'};
const r=analyzeMemo(x);assert.equal(r.cashAvailable,500000);assert.ok(Math.abs(r.dscr-1.5151515151515151)<1e-12);assert.ok(Math.abs(r.cashDays-81.11111111111111)<1e-10);assert.equal(r.flag,'Ready for further diligence');
assert.equal(analyzeMemo({...x,reviewed:false}).flag,'Requires follow-up');
assert.equal(analyzeMemo({...x,revenue:2500000,expenses:2350000,cash:120000}).reasons.length,2);
assert.throws(()=>analyzeMemo({...x,debtService:0}));assert.throws(()=>analyzeMemo({...x,revenue:NaN}));assert.throws(()=>analyzeMemo({...x,cash:-1}));
const text=draftMemo(x,r);assert.match(text,/1.52x/);assert.match(text,/Confirm cash restrictions/);assert.match(text,/No PDF extraction/);
console.log('PASS: memo calculations, review flags, source-review status, invalid inputs and traceable draft');
