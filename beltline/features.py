from datetime import timedelta
import numpy as np
from .data import DK,STEP,available,decision

THRESHOLD=10.
LAGS=(72,96,168,336)
NAMES=[f'{name}_lag_{lag}h' for name in ('DK1','DK2','spread') for lag in LAGS]+[
    'spread_mean','spread_std','spread_min','spread_max','mean_abs_spread','event_frequency',
    'day_sin','day_cos','day_sin2','day_cos2','year_sin','year_cos',
    *[f'weekday_{d}' for d in range(7)],'utc_offset_hours','dst_fold']

def event(spread):return np.abs(np.asarray(spread))>THRESHOLD

def matrix(values):
    times=sorted(values['DK1'])
    if times!=sorted(values['DK2']):raise ValueError('Areas must have identical timestamps')
    if any(b-a!=STEP for a,b in zip(times,times[1:])):raise ValueError('Missing quarter')
    p1=np.array([values['DK1'][t] for t in times]);p2=np.array([values['DK2'][t] for t in times]);spread=p2-p1
    ids=np.arange(336*4,len(times));target=[times[i] for i in ids]
    cols=[v[ids-h*4] for v in (p1,p2,spread) for h in LAGS]
    history=np.lib.stride_tricks.sliding_window_view(spread,96)[ids-72*4-95]
    cols += [history.mean(1),history.std(1),history.min(1),history.max(1),np.abs(history).mean(1),event(history).mean(1)]
    local=[t.astimezone(DK) for t in target];h=np.array([t.hour+t.minute/60 for t in local]);doy=np.array([t.timetuple().tm_yday for t in local])
    cols += [np.sin(h*2*np.pi/24),np.cos(h*2*np.pi/24),np.sin(h*4*np.pi/24),np.cos(h*4*np.pi/24),np.sin(doy*2*np.pi/365.25),np.cos(doy*2*np.pi/365.25)]
    cols += [np.array([t.weekday()==d for t in local],float) for d in range(7)]
    cols += [np.array([t.utcoffset().total_seconds()/3600 for t in local]),np.array([t.fold for t in local])]
    cutoffs={t.date():decision(t.date()) for t in local};margins=[(cutoffs[l.date()]-available(t-timedelta(hours=72))).total_seconds()/3600 for t,l in zip(target,local)]
    if not margins or min(margins)<0:raise ValueError('Insufficient history or future feature')
    X=np.column_stack(cols)
    if not np.isfinite(X).all():raise ValueError('Nonfinite feature')
    return {'times':target,'X':X,'y':spread[ids],'p1':p1[ids],'p2':p2[ids],'weekly':spread[ids-168*4],'minimum_feature_margin_hours':min(margins)}
