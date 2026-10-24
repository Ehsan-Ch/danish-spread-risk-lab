"""Fixed monthly walk-forward replay. No test-period model selection."""
import csv
import gzip
import io
import json
import platform
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import sklearn
from .data import load, midnight, decision, available, stamp, DK, digest
from .features import matrix, event, NAMES
from .models import Models, REG, PROB, regression_metrics, probability_metrics, daily_bootstrap
from .risk import exposure

ROOT=Path(__file__).resolve().parents[1]

def bounds(first):
    end=first-timedelta(days=2)
    cal=end-timedelta(days=28)
    return cal-timedelta(days=120),cal,end

def run(cache,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    values,manifest=load(cache);m=matrix(values);times=m['times']
    local=[t.astimezone(DK).date() for t in times]
    folds=[];days=[];validation=None;selected=None
    for month in (6,7,8,9):
        first=date(2026,month,1);fit_start,cal_start,cal_end=bounds(first)
        def mask(a,b):return np.array([midnight(a)<=t<midnight(b) for t in times])
        fit=mask(fit_start,cal_start);cal=mask(cal_start,cal_end)
        if available(times[np.flatnonzero(cal)[-1]])>decision(first):raise ValueError('Label leakage')
        if sum(fit)<11000 or sum(cal)<2600:raise ValueError('Incomplete training window')
        model=Models().fit(m['X'][fit],m['y'][fit]).calibrate(m['X'][cal],m['y'][cal],m['weekly'][cal])
        stop=date(2026,6,28) if month==6 else (date(2026,month+1,1))
        test=mask(first,stop);ids=np.flatnonzero(test)
        reg,prob=model.predict(m['X'][test],m['weekly'][test]);y=m['y'][test]
        scores={'regression':{k:regression_metrics(y,reg[k]) for k in REG},'probability':{k:probability_metrics(event(y),prob[k]) for k in PROB}}
        if month==6:
            validation=scores
            selected={'regression':min(REG,key=lambda k:scores['regression'][k]['mae']),'probability':min(PROB,key=lambda k:scores['probability'][k]['brier'])}
        fold={'month':str(first)[:7],'fit_start':str(fit_start),'fit_end_exclusive':str(cal_start),'calibration_start':str(cal_start),'calibration_end_exclusive':str(cal_end),'fit_n':int(fit.sum()),'calibration_n':int(cal.sum()),'last_label_available':stamp(available(times[np.flatnonzero(cal)[-1]])),'first_issue':stamp(decision(first)),'scores':scores}
        folds.append(fold)
        for day in sorted(set(local[i] for i in ids)):
            take=np.array([local[i]==day for i in ids]);di=ids[take]
            days.append({'date':str(day),'split':'validation' if month==6 else 'test','fold':fold['month'],'issue':stamp(decision(day)),
                         'times':[stamp(times[i]) for i in di],'labels':[times[i].astimezone(DK).isoformat() for i in di],
                         'dk1':m['p1'][di].tolist(),'dk2':m['p2'][di].tolist(),'actual':m['y'][di].tolist(),
                         'regression':{k:reg[k][take].tolist() for k in REG},'probability':{k:prob[k][take].tolist() for k in PROB}})
        print('Completed',fold['month'],scores['regression'][selected['regression']]['mae'],flush=True)
    testdays=[d for d in days if d['split']=='test'];y=np.concatenate([d['actual'] for d in testdays])
    scores={'regression':{},'probability':{}}
    for k in REG:
        pred=np.concatenate([d['regression'][k] for d in testdays]);s=regression_metrics(y,pred)
        s['skill_vs_zero']=1-s['mae']/float(np.abs(y).mean())
        diffs=[float((np.abs(np.asarray(d['regression'][k])[:,1]-d['actual'])-np.abs(d['actual'])).mean()) for d in testdays]
        s['daily_bootstrap']=daily_bootstrap(diffs);scores['regression'][k]=s
    for k in PROB:scores['probability'][k]=probability_metrics(event(y),np.concatenate([d['probability'][k] for d in testdays]))
    for d in days:d['exposure_1mw']=exposure(d['actual'],d['regression'][selected['regression']])
    results={'project':'Beltline','version':1,'source':manifest,'protocol_sha256':digest((ROOT/'docs/PROTOCOL.md').read_bytes()),
             'environment':{'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__},
             'data_quality':{'source_rows':sum(len(v) for v in values.values()),'duplicates':0,'missing':0,'features':NAMES,'minimum_feature_margin_hours':m['minimum_feature_margin_hours']},
             'selected':selected,'validation':validation,'test':scores,'folds':folds,'days':days,
             'exposure_1mw':exposure(y,np.concatenate([d['regression'][selected['regression']] for d in testdays]))}
    (output/'results.json').write_text(json.dumps(results,separators=(',',':'),allow_nan=False),encoding='utf-8')
    stream=io.StringIO(newline='');writer=csv.writer(stream)
    writer.writerow(['split','delivery_local','issue_utc','time_utc','dk1_eur_mwh','dk2_eur_mwh','spread_eur_mwh',*[f'{k}_{q}' for k in REG for q in ('lower','point','upper')],*[f'{k}_probability' for k in PROB]])
    for d in days:
        for i,t in enumerate(d['times']):writer.writerow([d['split'],d['labels'][i],d['issue'],t,d['dk1'][i],d['dk2'][i],d['actual'][i],*[v for k in REG for v in d['regression'][k][i]],*[d['probability'][k][i] for k in PROB]])
    (output/'predictions.csv.gz').write_bytes(gzip.compress(stream.getvalue().encode(),mtime=0))
    with (output/'exposure.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['date',*testdays[0]['exposure_1mw']]);w.writeheader()
        w.writerows({'date':d['date'],**d['exposure_1mw']} for d in testdays)
    print(json.dumps({'selected':selected,'test':scores,'exposure':results['exposure_1mw']},indent=2),flush=True)
    return results
