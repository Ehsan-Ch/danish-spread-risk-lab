import math
import numpy as np

def exposure(actual,forecast,mw=1):
    a=np.asarray(actual,float);f=np.asarray(forecast,float)
    if not math.isfinite(mw) or not 0<=mw<=10 or a.ndim!=1 or f.shape!=(len(a),3) or not np.isfinite(a).all() or not np.isfinite(f).all() or (f[:,0]>f[:,1]).any() or (f[:,1]>f[:,2]).any():raise ValueError('Invalid exposure input')
    q=mw*.25
    return {'mw':mw,'mwh':q*len(a),'net_cost':float(q*a.sum()),'absolute_cost':float(q*np.abs(a).sum()),'forecast_cost':float(q*f[:,1].sum()),'envelope_lower':float(q*f[:,0].sum()),'envelope_upper':float(q*f[:,2].sum())}
