"""Build aggregate showcase data from the existing sibling project repositories.
From the portfolio root: python scripts/build-project-demos.py --source-root ..
No individual HR records are published by this script.
"""
from pathlib import Path
import argparse,csv,json,re,subprocess
from collections import Counter,defaultdict
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
def write(name,data):
 path=root/'projects'/name/'data.json';path.write_text(json.dumps(data,separators=(',',':'))+'\n')
with (a.source_root/'Netflix_SQL/netflix_titles.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
buckets={}
for x in rows:
 key=(int(x['release_year']),x['type'])
 b=buckets.setdefault(key,dict(year=key[0],type=key[1],count=0,countries=Counter(),genres=Counter(),ratings=Counter()))
 b['count']+=1
 b['countries'].update(c.strip() for c in x['country'].split(',') if c.strip())
 b['genres'].update(c.strip() for c in x['listed_in'].split(',') if c.strip())
 rating=x['rating'].strip()
 if rating and not re.match(r'^\d+ min$',rating):b['ratings'][rating]+=1
movies=[x for x in rows if x['type']=='Movie' and re.match(r'^\d+ min$',x['duration'])]
longest=max(movies,key=lambda x:int(x['duration'].split()[0]))
assert len(rows)==8807
assert sum(b['count'] for b in buckets.values())==len(rows)
write('netflix',dict(source_rows=len(rows),source='Netflix_SQL/netflix_titles.csv',buckets=list(buckets.values()),longest=dict(title=longest['title'],minutes=int(longest['duration'].split()[0])),note='Historical catalog snapshot, not current Netflix inventory.'))
hr=json.loads((a.source_root/'HR_SQL-PowerBi_Project/reports/audit.json').read_text())
assert hr['counts']['active_at_snapshot']+hr['counts']['terminated_at_snapshot']==hr['counts']['eligible_records']
assert sum(x['net_flow'] for x in hr['annual_flows'].values())==hr['counts']['active_at_snapshot']
write('hr-analytics',hr)
# Read the historical public notebook output, not the restricted source GeoPackage.
raw=subprocess.check_output(['git','-C',str(a.source_root/'Spatial_Python-QGIS_Project'),'show','53c66592d7e8e5057f8c073c0d3fd9c5f5644f0a:Basin.ipynb'])
notebook=json.loads(raw);country=[]
for c in notebook['cells']:
 for output in c.get('outputs',[]):
  text=''.join(output.get('data',{}).get('text/plain',[]))
  if 'Total Mining' not in text or 'ETM Mining' not in text:continue
  for line in text.splitlines():
   m=re.match(r'^(.+?)\s{2,}([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$',line)
   if m and m[1].strip()!='Congo Basin':country.append(dict(country=m[1].strip(),total=float(m[2]),etm=float(m[3]),non_etm=float(m[4])))
assert len(country)==5
assert abs(sum(x['total'] for x in country)-1381819.1)<.2
write('congo-basin',dict(countries=country,source_commit='53c66592d7e8e5057f8c073c0d3fd9c5f5644f0a',note='Historical notebook output. Summed concession areas may overlap; not a measure of active mine footprint.'))
print('PASS: Netflix totals, HR headcount reconciliation and Congo historical summaries')
