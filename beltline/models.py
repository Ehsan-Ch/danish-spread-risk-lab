import math
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
from sklearn.linear_model import Ridge,LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score,average_precision_score
from threadpoolctl import threadpool_limits
from .features import event

REG=('zero','weekly','ridge','boosted')
PROB=('frequency','logistic','boosted')
TREE={'max_iter':100,'learning_rate':.05,'max_leaf_nodes':15,'min_samples_leaf':80,'l2_regularization':1.,'early_stopping':False,'random_state':42}

def correction(errors):
    e=np.asarray(errors,float);rank=math.ceil((len(e)+1)*.8)
    if not len(e) or rank>len(e) or not np.isfinite(e).all():raise ValueError('Invalid calibration errors')
    return float(np.sort(e)[rank-1])

class Models:
    def fit(self,X,y):
        with threadpool_limits(limits=2):
            self.reg={'ridge':make_pipeline(StandardScaler(),Ridge(alpha=10.)).fit(X,y),'boosted':HistGradientBoostingRegressor(loss='quantile',quantile=.5,**TREE).fit(X,y)}
            labels=event(y).astype(int);self.constant=None
            if len(np.unique(labels))<2:self.constant=float(labels[0]);self.prob={}
            else:self.prob={'logistic':make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=1000,random_state=42)).fit(X,labels),'boosted':HistGradientBoostingClassifier(**TREE).fit(X,labels)}
        return self
    def raw(self,X,weekly):
        with threadpool_limits(limits=2):
            r={'zero':np.zeros(len(X)),'weekly':np.asarray(weekly),**{k:m.predict(X) for k,m in self.reg.items()}}
            p={k:m.predict_proba(X)[:,1] for k,m in self.prob.items()} if self.constant is None else {k:np.full(len(X),self.constant) for k in ('logistic','boosted')}
        return r,p
    def calibrate(self,X,y,weekly):
        r,p=self.raw(X,weekly);labels=event(y).astype(int)
        self.widths={name:correction(np.abs(y-v)) for name,v in r.items()}
        self.calibrators={name:IsotonicRegression(out_of_bounds='clip',y_min=0,y_max=1).fit(v,labels) for name,v in p.items()}
        self.frequency=float((labels.sum()+1)/(len(labels)+2));return self
    def predict(self,X,weekly):
        r,p=self.raw(X,weekly)
        return ({name:np.column_stack([v-self.widths[name],v,v+self.widths[name]]) for name,v in r.items()},
                {'frequency':np.full(len(X),self.frequency),**{name:self.calibrators[name].predict(v) for name,v in p.items()}})

def regression_metrics(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float)
    if not len(y):return None
    if p.shape!=(len(y),3) or not np.isfinite(p).all() or not np.isfinite(y).all() or (p[:,0]>p[:,1]).any() or (p[:,1]>p[:,2]).any():raise ValueError('Invalid regression inputs')
    e=p[:,1]-y
    return {'n':len(y),'mae':float(np.abs(e).mean()),'rmse':float(np.sqrt((e*e).mean())),'bias':float(e.mean()),'coverage':float(((y>=p[:,0])&(y<=p[:,2])).mean()),'width':float((p[:,2]-p[:,0]).mean())}

def probability_metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float)
    if y.shape!=p.shape or not len(y) or not np.isfinite(p).all() or ((p<0)|(p>1)).any() or not np.isin(y,[0,1]).all():raise ValueError('Invalid probability inputs')
    clipped=np.clip(p,1e-12,1-1e-12);alarm=p>=.6;tp=int((alarm&(y==1)).sum());fp=int((alarm&(y==0)).sum());positives=int(y.sum())
    bins=[]
    for i in range(10):
        take=(p>=i/10)&((p<(i+1)/10) if i<9 else (p<=1));n=int(take.sum())
        bins.append({'bin':i,'n':n,'predicted':float(p[take].mean()) if n else None,'observed':float(y[take].mean()) if n else None})
    both=len(np.unique(y))==2
    return {'n':len(y),'events':positives,'base_rate':float(y.mean()),'brier':float(((p-y)**2).mean()),'log_loss':float(-(y*np.log(clipped)+(1-y)*np.log(1-clipped)).mean()),'roc_auc':float(roc_auc_score(y,p)) if both else None,'average_precision':float(average_precision_score(y,p)) if both else None,'alerts':int(alarm.sum()),'true_alerts':tp,'false_alerts':fp,'precision':tp/int(alarm.sum()) if alarm.any() else None,'recall':tp/positives if positives else None,'reliability':bins}

def daily_bootstrap(differences):
    d=np.asarray(differences,float)
    if not len(d) or not np.isfinite(d).all():raise ValueError('Invalid daily differences')
    rng=np.random.default_rng(42);draws=rng.choice(d,size=(2000,len(d)),replace=True).mean(1)
    return {'mean_mae_difference':float(d.mean()),'lower':float(np.quantile(draws,.025)),'upper':float(np.quantile(draws,.975)),'unit':'EUR/MWh','blocks':len(d)}
