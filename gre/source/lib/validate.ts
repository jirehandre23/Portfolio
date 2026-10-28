import { wordNames } from './word-names';
const names=new Set(wordNames);
const number=(n:unknown,max=1e14)=>typeof n==='number'&&Number.isFinite(n)&&n>=0&&n<=max;
const object=(v:any)=>v&&typeof v==='object'&&!Array.isArray(v);
export function validState(s:any):boolean {
 if(!object(s)||s.version!==6||!object(s.progress)||!object(s.settings)||!object(s.filters))return false;
 for(const [w,v] of Object.entries(s.progress) as [string,any][]){if(!names.has(w)||!object(v)||!Number.isInteger(v.level)||!number(v.level,5)||!number(v.due)||!number(v.lastPromotion)||typeof v.wrong!=='boolean'||typeof v.seen!=='boolean')return false;}
 if(!['daily','all','due','wrong'].includes(s.filters.mode)||typeof s.filters.group!=='string'||typeof s.filters.search!=='string'||s.filters.search.length>200)return false;
 if(!['flash','recall','context'].includes(s.settings.style)||!['showFr','showEx','showSyn'].every(k=>typeof s.settings[k]==='boolean'))return false;
 if(s.session!==null){const q=s.session;if(!object(q)||!Array.isArray(q.queue)||q.queue.length>506||!q.queue.every((w:unknown)=>typeof w==='string'&&names.has(w))||!Number.isInteger(q.index)||!number(q.index,q.queue.length)||!['good','bad','skipped'].every(k=>Number.isInteger(q[k])&&number(q[k],1000000))||!object(q.rated)||!object(q.retried))return false;}
 return true;
}
