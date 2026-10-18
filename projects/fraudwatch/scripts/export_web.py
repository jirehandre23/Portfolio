"""Export the supported numeric binary-logistic XGBoost model for browser inference.
Run after `python -m fraudwatch.train`, from the FraudWatch directory.
"""
import hashlib,json,os
from pathlib import Path
import numpy as np
from xgboost import XGBClassifier
from fraudwatch.features import synthetic,features,RAW,FEATURES

def main():
    artifacts=Path(os.getenv('ARTIFACT_DIR','artifacts'))
    raw=(artifacts/'booster.json').read_bytes();source=json.loads(raw)
    learner=source['learner'];gb=learner['gradient_booster']
    if learner['objective']['name']!='binary:logistic' or gb['name']!='gbtree':
        raise ValueError('Browser export supports only binary logistic numeric gbtree models')
    trees=gb['model']['trees']
    if any(any(t['split_type']) for t in trees):raise ValueError('Categorical splits are not supported')
    metadata=json.loads((artifacts/'metadata.json').read_text())
    model=dict(format='fraudwatch-numeric-v1',features=FEATURES,
               base_score=float(learner['learner_model_param']['base_score']),
               model_version=metadata['model_version'],threshold=metadata['threshold'],
               source_sha256=hashlib.sha256(raw).hexdigest(),
               trees=[dict(left=t['left_children'],right=t['right_children'],feature=t['split_indices'],value=t['split_conditions']) for t in trees])
    out=Path('web');out.mkdir(exist_ok=True)
    (out/'model.json').write_text(json.dumps(model,separators=(',',':'))+'\n')
    estimator=XGBClassifier();estimator.load_model(artifacts/'booster.json')
    batch={};fixtures=[]
    for name,shift,seed in [('normal',False,64),('shifted',True,73)]:
        # Fixed synthetic examples, not a live production feed.
        frame=synthetic(500,seed=seed,shift=shift)
        probability=estimator.predict_proba(features(frame))[:,1]
        batch[name]=[]
        for i,(_,row) in enumerate(frame.iterrows()):
            tx={k:float(row[k]) if k in ('amount','distance_km') else int(row[k]) for k in RAW}
            batch[name].append(dict(id=f'{name}-{i+1:04d}',transaction=tx,label=int(row.fraud)))
            fixtures.append(dict(transaction=tx,probability=float(probability[i])))
    # Explicit boundaries and illustrative presets; expected values come from Python.
    extras=[dict(amount=25,hour=14,distance_km=2,account_age_days=2000,is_international=0),
            dict(amount=1500,hour=2,distance_km=1500,account_age_days=10,is_international=1),
            dict(amount=1e6,hour=23,distance_km=20000,account_age_days=36500,is_international=1),
            dict(amount=.01,hour=0,distance_km=0,account_age_days=0,is_international=0)]
    p=estimator.predict_proba(features(extras))[:,1]
    fixtures.extend(dict(transaction=t,probability=float(v)) for t,v in zip(extras,p))
    (out/'samples.json').write_text(json.dumps(batch,separators=(',',':'))+'\n')
    Path('reports/web_parity_fixtures.json').write_text(json.dumps(fixtures,separators=(',',':'))+'\n')
    print(f'Exported {len(trees)} trees and {len(fixtures)} Python reference predictions')

if __name__=='__main__':main()
