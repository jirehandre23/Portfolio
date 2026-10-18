import {$,bars,table,data} from '../shared/ui.mjs';
let catalog,minYear,maxYear;
const queries={duration:`-- Guard the numeric cast, then sort by minutes.\nSELECT title, SPLIT_PART(duration, ' ', 1)::INT AS minutes\nFROM netflix\nWHERE type = 'Movie' AND duration ~ '^[0-9]+ min$'\nORDER BY minutes DESC, title LIMIT 1;`,countries:`-- A co-production receives one credit per listed country.\nSELECT TRIM(c) AS country, COUNT(DISTINCT show_id) AS titles\nFROM netflix\nCROSS JOIN LATERAL\n  UNNEST(STRING_TO_ARRAY(country, ',')) AS countries(c)\nGROUP BY TRIM(c)\nORDER BY titles DESC;`,dates:`CASE\n WHEN TRIM(date_added) ~ '^[0-9]{1,2}-[A-Za-z]{3}-[0-9]{2}$'\n   THEN TO_DATE(TRIM(date_added), 'DD-Mon-YY')\n WHEN TRIM(date_added) ~ '^[A-Za-z]+ [0-9]{1,2}, [0-9]{4}$'\n   THEN TO_DATE(TRIM(date_added), 'Month DD, YYYY')\n ELSE NULL\nEND AS parsed_added`};
function render(){if(!catalog)return;const from=Number($('year-from').value),to=Number($('year-to').value),type=$('type').value;
 if(!Number.isInteger(from)||!Number.isInteger(to)||from>to){$('status').textContent='Choose whole years with the start no later than the end.';return;}
 const buckets=catalog.buckets.filter(x=>x.year>=from&&x.year<=to&&(type==='all'||type===x.type));
 const count=t=>buckets.filter(x=>x.type===t).reduce((s,x)=>s+x.count,0),movies=count('Movie'),shows=count('TV Show');
 $('titles').textContent=(movies+shows).toLocaleString('en-US');$('movies').textContent=movies.toLocaleString('en-US');$('shows').textContent=shows.toLocaleString('en-US');$('years').textContent=new Set(buckets.map(x=>x.year)).size;
 const aggregate=k=>{const result={};for(const b of buckets)for(const [key,v]of Object.entries(b[k]))result[key]=(result[key]||0)+v;return Object.entries(result).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,10);};
 bars('country-bars',aggregate('countries'));bars('genre-bars',aggregate('genres'));
 const years={};for(const b of buckets){years[b.year]??={Movie:0,'TV Show':0};years[b.year][b.type]+=b.count;}
 table('year-table',Object.keys(years).map(Number).sort((a,b)=>b-a).slice(0,15).map(y=>[y,years[y].Movie,years[y]['TV Show'],years[y].Movie+years[y]['TV Show']]));
 $('status').textContent=`Ready · ${movies+shows} of ${catalog.source_rows} source titles match · release years ${from}–${to}.`;
}
for(const id of ['type','year-from','year-to'])$(id).addEventListener('change',render);
$('query').addEventListener('change',()=>{$('sql-code').textContent=queries[$('query').value];});$('sql-code').textContent=queries.duration;
$('reset').addEventListener('click',()=>{$('type').value='all';$('year-from').value=minYear;$('year-to').value=maxYear;render();});
try{catalog=await data(new URL('./data.json',import.meta.url));minYear=Math.min(...catalog.buckets.map(x=>x.year));maxYear=Math.max(...catalog.buckets.map(x=>x.year));for(const id of ['year-from','year-to']){$(id).min=minYear;$(id).max=maxYear;}$('year-from').value=minYear;$('year-to').value=maxYear;render();}catch(e){$('status').textContent=e.message+' Reload the page to retry.';}
