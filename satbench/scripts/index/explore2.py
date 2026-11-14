import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0,ROOT)
import common as c, pandas as pd, numpy as np
df=c.items()
s=c.satbench_series(df); print(s[(s.date>='2026-01-01')&(s.date<='2026-04-01')])
# hazard by age at risk, last 12 months
rows=[]
for m in pd.date_range('2025-11-01','2026-10-01',freq='MS'):
    at=df[(df.released<m)&(df.solved85.isna()|(df.solved85>=m))]
    e=(at.solved85>=m)&(at.solved85<m+pd.offsets.MonthBegin(1))
    age=(m-at.released).dt.days/30.4
    for a,ee,bst in zip(age,e,at.best): rows.append((a,ee))
r=pd.DataFrame(rows,columns=['age','e'])
r['ab']=pd.cut(r.age,[0,6,12,24,36,600])
print(r.groupby('ab').e.agg(['sum','size','mean']))
# unsolved current items: age and best
u=df[df.solved85.isna()]
print(((c.AS_OF-u.released).dt.days/365).describe())
print(u.best.describe()); print((u.best>=75).sum(), 'unsolved with best>=75')
print(u.sort_values('best')[['id','released','best','n_cites','area']].to_string())
for k in (3,5,10,20):
    d=c.items(k); print(k, len(d), d.groupby(d.released.dt.year).size().loc[2023:].to_dict(), 'born', d.born_solved.sum())
# 10th cite lag for 2024/2025 releases
def nth(x,n=10):
    ds=sorted(cc['date'] for cc in x['cites']); return pd.Timestamp(ds[n-1]) if len(ds)>=n else pd.NaT
S={x['id']:x for x in c.summaries()}
df['tenth']=[nth(S[i]) for i in df.id]
df['lag']=(df.tenth-df.released).dt.days/30.4
for y in (2024,2025):
    d=df[df.released.dt.year==y]; print(y, d.lag.describe()[['25%','50%','75%','max']].round(1).to_dict(), (d.lag<=6).mean().round(2),(d.lag<=12).mean().round(2))
