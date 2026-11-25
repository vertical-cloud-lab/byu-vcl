from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
P=Path(__file__).resolve().parent
m=pd.read_csv(P/'source_cache/legacy_master.csv')
d=m[(m.funding_total_usd>0)&(m.latest_value_usd>0)&~m.ownership_status.isin(['nonprofit','government','foundation'])].copy()
d['ratio']=d.latest_value_usd/d.funding_total_usd
assert len(d)==37
r,p=spearmanr(d.openness_current,d.ratio)
med=d.groupby(d.openness_current>=2).ratio.median()
rng=np.random.default_rng(20261125);cs=[];rs=[]
x=d.openness_current.to_numpy();y=d.ratio.to_numpy()
for _ in range(10000):
    i=rng.integers(0,len(d),len(d));cs.append(spearmanr(x[i],y[i]).statistic)
    a=y[i][x[i]>=2];b=y[i][x[i]<2]
    if len(a) and len(b):rs.append(np.median(a)/np.median(b))
print('n',len(d),'rho',r,'p',p,'rhoCI',np.quantile(cs,[.025,.975]))
print('open/closed medians',med[True],med[False],'ratio',med[True]/med[False],'CI',np.quantile(rs,[.025,.975]))
