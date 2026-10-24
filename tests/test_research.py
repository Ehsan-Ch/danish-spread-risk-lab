import csv
import gzip
import io
import json
import threading
import unittest
import urllib.request
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from beltline.data import day_slots,midnight,decision,available,validate,stamp,digest,DK,STEP
from beltline.features import matrix,event,NAMES
from beltline.models import Models,correction,regression_metrics,probability_metrics,daily_bootstrap
from beltline.risk import exposure
from beltline.pipeline import bounds
from beltline.server import Handler,ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/'reports/benchmark/results.json').read_text())

class TimeAndData(unittest.TestCase):
    def test_dst_days(self):
        self.assertEqual(len(day_slots('2025-10-26')),100);self.assertEqual(len(day_slots('2026-03-29')),92)
        slots=day_slots('2025-10-26');self.assertEqual(len(set(slots)),100)
        self.assertEqual(sum(t.astimezone(DK).fold for t in slots),4)
    def test_local_issue(self):
        self.assertEqual(decision('2026-07-01').hour,8)
        self.assertEqual(decision('2026-01-01').hour,9)
    def test_label_boundaries(self):
        for month in (6,7,8,9):
            first=date(2026,month,1);a,b,c=bounds(first)
            self.assertEqual((b-a).days,120);self.assertEqual((c-b).days,28)
            self.assertLessEqual(available(midnight(c)-STEP),decision(first))
    def records(self):return [{'TimeUTC':stamp(t),'PriceArea':area,'DayAheadPriceEUR':-5} for t in day_slots('2026-07-01') for area in ('DK1','DK2')]
    def test_negative_prices_preserved(self):
        v=validate(self.records(),'2026-07-01','2026-07-02');self.assertEqual(min(v['DK1'].values()),-5)
    def test_duplicates_and_gaps_rejected(self):
        r=self.records()
        for bad in (r[:-1],r+[r[0]]):
            with self.assertRaises(ValueError):validate(bad,'2026-07-01','2026-07-02')
    def test_nonfinite_and_misaligned_rejected(self):
        for key,value in [('DayAheadPriceEUR',float('nan')),('TimeUTC','2026-06-30T22:01:00Z')]:
            r=self.records();r[0][key]=value
            with self.assertRaises(ValueError):validate(r,'2026-07-01','2026-07-02')
    def test_future_mutation_cannot_change_features(self):
        ts=[midnight('2026-01-01')+i*STEP for i in range(96*18)]
        v={'DK1':{t:float(i%96) for i,t in enumerate(ts)},'DK2':{t:float(i%96+4) for i,t in enumerate(ts)}}
        a=matrix(v);target=midnight('2026-01-17');idx=a['times'].index(target)
        for t in ts:
            if available(t)>decision('2026-01-17'):v['DK2'][t]+=10000
        b=matrix(v);np.testing.assert_array_equal(a['X'][idx],b['X'][idx]);self.assertNotEqual(a['y'][idx],b['y'][idx])
        self.assertEqual(a['X'].shape[1],len(NAMES));self.assertEqual(a['weekly'][idx],4)
    def test_strict_event_threshold_and_sign(self):
        np.testing.assert_array_equal(event([-11,-10,0,10,11]),[1,0,0,0,1])

class Statistics(unittest.TestCase):
    def test_finite_sample_rank(self):self.assertEqual(correction(np.arange(9)),7)
    def test_bad_intervals_rejected(self):
        with self.assertRaises(ValueError):regression_metrics([0],[[2,1,3]])
    def test_probability_endpoints_and_empty_bins(self):
        s=probability_metrics([0,1],[0,1]);self.assertEqual(s['brier'],0);self.assertEqual(s['precision'],1);self.assertEqual(s['recall'],1)
        self.assertEqual(sum(b['n'] for b in s['reliability']),2);self.assertIsNone(s['reliability'][5]['observed']);self.assertEqual(s['reliability'][9]['n'],1)
    def test_undefined_probability_metrics(self):
        s=probability_metrics([0,0],[.1,.2]);self.assertIsNone(s['roc_auc']);self.assertIsNone(s['average_precision']);self.assertIsNone(s['recall']);self.assertIsNone(s['precision'])
    def test_probabilities_reject_outside_range(self):
        with self.assertRaises(ValueError):probability_metrics([0],[1.1])
    def test_bootstrap_is_paired_and_deterministic(self):
        self.assertEqual(daily_bootstrap([1,2,3]),daily_bootstrap([1,2,3]));self.assertEqual(daily_bootstrap([2]*10)['lower'],2)
    def test_constant_class_model_and_separate_calibration(self):
        rng=np.random.default_rng(9);X=rng.normal(size=(300,3));m=Models().fit(X[:200],np.zeros(200));before=m.reg['ridge'].named_steps['ridge'].coef_.copy()
        m.calibrate(X[200:],np.full(100,20.),np.zeros(100));reg,prob=m.predict(X[:4],np.zeros(4))
        np.testing.assert_array_equal(before,m.reg['ridge'].named_steps['ridge'].coef_);np.testing.assert_array_equal(prob['boosted'],np.ones(4));self.assertEqual(prob['frequency'][0],101/102);self.assertEqual(reg['zero'][0,2],20)

class Exposure(unittest.TestCase):
    def test_quarter_units_and_cancellation(self):
        s=exposure([20,-20],[[-5,1,5],[-5,1,5]],2)
        self.assertEqual(s['net_cost'],0);self.assertEqual(s['absolute_cost'],20);self.assertEqual(s['forecast_cost'],1);self.assertEqual(s['mwh'],1)
    def test_zero_and_invalid_mw(self):
        self.assertEqual(exposure([20],[[0,0,0]],0)['absolute_cost'],0)
        for mw in (-1,11,float('nan')):
            with self.assertRaises(ValueError):exposure([20],[[0,0,0]],mw)
    def test_bad_exposure_shape_or_order(self):
        for f in ([[1,0,2]],[[1,2]]):
            with self.assertRaises(ValueError):exposure([0],f)

class FrozenReport(unittest.TestCase):
    def test_protocol_hash(self):self.assertEqual(R['protocol_sha256'],digest((ROOT/'docs/PROTOCOL.md').read_bytes()))
    def test_selection_uses_validation(self):
        for family,metric in [('regression','mae'),('probability','brier')]:self.assertEqual(R['selected'][family],min(R['validation'][family],key=lambda k:R['validation'][family][k][metric]))
    def test_chronology_and_spread(self):
        days=[d for d in R['days'] if d['split']=='test'];self.assertEqual(len(days),92);self.assertEqual(sum(len(d['actual']) for d in days),8832)
        for d in days:
            self.assertEqual(d['issue'],stamp(decision(d['date'])));self.assertEqual(d['times'],[stamp(t) for t in day_slots(d['date'])]);np.testing.assert_allclose(np.array(d['dk2'])-d['dk1'],d['actual'])
    def test_metrics_reconciled_from_predictions(self):
        ds=[d for d in R['days'] if d['split']=='test'];y=np.concatenate([d['actual'] for d in ds])
        for k,v in R['test']['regression'].items():
            s=regression_metrics(y,np.concatenate([d['regression'][k] for d in ds]));self.assertAlmostEqual(s['mae'],v['mae']);self.assertAlmostEqual(s['coverage'],v['coverage'])
        for k,v in R['test']['probability'].items():
            s=probability_metrics(event(y),np.concatenate([d['probability'][k] for d in ds]));self.assertEqual(s,v)
    def test_csv_reconciles_all_rows(self):
        with gzip.open(ROOT/'reports/benchmark/predictions.csv.gz','rt') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),11424);self.assertEqual(sum(r['split']=='test' for r in rows),8832)
        for r in rows:self.assertAlmostEqual(float(r['dk2_eur_mwh'])-float(r['dk1_eur_mwh']),float(r['spread_eur_mwh']))
        self.assertEqual(len({r['time_utc'] for r in rows}),len(rows))
    def test_exposure_journal_reconciles(self):
        ds=[d for d in R['days'] if d['split']=='test']
        with (ROOT/'reports/benchmark/exposure.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),92)
        for d,row in zip(ds,rows):
            e=exposure(d['actual'],d['regression'][R['selected']['regression']]);self.assertEqual(e,d['exposure_1mw']);self.assertAlmostEqual(e['net_cost'],float(row['net_cost']))
        self.assertAlmostEqual(sum(d['exposure_1mw']['net_cost'] for d in ds),R['exposure_1mw']['net_cost'])

class Server(unittest.TestCase):
    def test_allowlist_and_traversal(self):
        with ThreadingHTTPServer(('127.0.0.1',0),Handler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            try:
                with urllib.request.urlopen(base+'/') as r:self.assertEqual(r.status,200)
                for path in ('/data/prices.json','/.git/config','/%2e%2e/README.md','/reports/'):
                    with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(base+path)
                    self.assertEqual(e.exception.code,404)
            finally:server.shutdown();thread.join()

if __name__=='__main__':unittest.main()
