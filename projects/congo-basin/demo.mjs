import {$,node,bars,table,data} from '../shared/ui.mjs';
let summary;
const labels={total:'Total concession area',etm:'ETM-classified concession area',share:'ETM share'};
function render(){if(!summary)return;const selection=$('country').value,metric=$('area-metric').value,rows=summary.countries.filter(x=>selection==='all'||x.country===selection);
 const total=rows.reduce((s,x)=>s+x.total,0),etm=rows.reduce((s,x)=>s+x.etm,0),compact=x=>new Intl.NumberFormat('en-US',{notation:'compact',maximumFractionDigits:2}).format(x);
 $('total-area').textContent=compact(total);$('etm-area').textContent=compact(etm);$('etm-share').textContent=(100*etm/total).toFixed(1)+'%';$('country-count').textContent=rows.length;
 bars('area-bars',rows.map(x=>[x.country,metric==='share'?100*x.etm/x.total:x[metric]]).sort((a,b)=>b[1]-a[1]),x=>metric==='share'?x.toFixed(1)+'%':Math.round(x).toLocaleString('en-US'));
 table('area-table',rows.map(x=>[x.country,x.total.toLocaleString('en-US'),x.etm.toLocaleString('en-US'),x.non_etm.toLocaleString('en-US')]));
 $('status').textContent=`Ready · historical notebook summary · ${labels[metric]}.`;
}
for(const id of ['country','area-metric'])$(id).addEventListener('change',render);
$('map').addEventListener('change',()=>{const maps={basin:['basin.webp','Historical DRC energy-transition minerals map'],tenke:['tenke.webp','Historical Tenke Fungurume map'],kamoto:['kamoto.webp','Historical Kamoto Copper Company map']};const [file,alt]=maps[$('map').value];$('map-image').src='maps/'+file;$('map-image').alt=alt;$('map-caption').textContent=alt+'. Existing QGIS output, not a live concession-boundary service.';});
try{summary=await data(new URL('./data.json',import.meta.url));for(const x of summary.countries){const option=node('option',x.country);option.value=x.country;$('country').append(option);}render();}catch(e){$('status').textContent=e.message+' Reload the page to retry.';}
