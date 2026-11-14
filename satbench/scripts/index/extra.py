import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0,ROOT)
import common as c, pandas as pd, numpy as np
df=c.items()
cov=df[[bool(c._INDEP.get(i)) for i in df.id]]
s=c.satbench_series(cov,col='solved85_indep'); s2=c.satbench_series(cov)
print('indep on covered', len(cov), s.iloc[-1].score, 'all-src on covered', s2.iloc[-1].score, s[s.date=='2025-01-01'].score.values)
# deterministic live projection with A=2.76 (observed 2026)
h=43/858; b=8/85
for A in (2.76,4.67,6.17):
    U=64.;N=173.;out={}
    for t in range(1,12*20):
        U=U*(1-h)+A*(1-b); N+=A
        d=pd.Timestamp('2026-11-01')+pd.DateOffset(months=t)
        if 100*(N-U)/N>=85 and 'x' not in out: out['x']=d
        if d in (pd.Timestamp('2027-11-01'),pd.Timestamp('2028-12-01')): out[str(d.date())]=round(100*(N-U)/N,1)
    print(A,out)
# what share of last-12m live rise is due to denominators: if 2026 arrivals had been 4.67/mo with same born-solved + same hazard?
print(df[df.solved85.notna()].groupby(df.solved85.dt.to_period('Q')).size().tail(8))
# solved in Mar 2026 jump
print(df[(df.solved85>='2026-02-01')&(df.solved85<'2026-03-01')][['id','solved85','solver85','solver85_source']])
