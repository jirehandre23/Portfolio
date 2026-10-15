"""Run from this directory: python run.py. Uses only the Python standard library."""
from pathlib import Path
import csv,json,sqlite3
from engine import analyze,portfolio
SCENARIOS={'Baseline':(0,0,0),'Moderate':(-.05,.03,.02),'Severe':(-.10,.07,.04)}

def main():
    root=Path(__file__).parent
    loans=json.loads((root/'data/borrowers.json').read_text())
    reports=root/'reports';reports.mkdir(exist_ok=True)
    summaries={};all_rows=[]
    with sqlite3.connect(root/'creditlens.db') as db:
        db.executescript((root/'schema.sql').read_text())
        db.execute('DELETE FROM results');db.execute('DELETE FROM scenarios');db.execute('DELETE FROM borrowers')
        db.executemany('INSERT INTO borrowers VALUES (?,?,?,?)',[(x['id'],x['name'],x['sector'],x['principal']) for x in loans])
        for name,params in SCENARIOS.items():
            rows=[analyze(x,*params) for x in loans]
            summaries[name]=portfolio(rows)
            db.execute('INSERT INTO scenarios VALUES (?,?,?,?)',(name,*params))
            for row in rows:
                all_rows.append(dict(scenario=name,**row))
                db.execute('INSERT INTO results VALUES (?,?,?,?,?,?,?,?,?)',(row['id'],name,row['cfads'],row['debt_service'],row['dscr'],row['covenant'],int(row['breach']),row['cash_days'],row['cash_after_year']))
        sql_rows=db.execute('SELECT * FROM sector_risk ORDER BY scenario,sector').fetchall()
    (reports/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    with (reports/'scenario_results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
    fixtures=[dict(loan=loan,params=params,expected=analyze(loan,*params)) for loan in loans for params in SCENARIOS.values()]
    (reports/'parity_fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    print(json.dumps(summaries,indent=2));print('SQL sector summaries:',len(sql_rows))
if __name__=='__main__':main()
