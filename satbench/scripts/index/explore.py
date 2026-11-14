import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0,ROOT)
import common as c, pandas as pd, numpy as np
df=c.items()
s=c.satbench_series(df)
print(s[s.score>=50].iloc[0])
print(s[(s.date>='2025-10-01')&(s.date<='2025-12-01')])
for y in (2023,2024,2025):
    f=c.satbench_series(df, fixed_cutoff=pd.Timestamp(f'{y}-12-31'))
    print(y, f.iloc[-1].to_dict(), 'first>=85', f[f.score>=85].date.min())
# arrivals
df['ry']=df.released.dt.year
print(df.groupby('ry').agg(n=('id','size'), born=('born_solved','sum')))
print(df.groupby(df.released.dt.to_period('Q')).size().tail(12))
# hazard
def hazard(m0,m1,col='solved85'):
    ev=0; risk=0
    for m in pd.date_range(m0,m1,freq='MS'):
        at=df[(df.released<m)&(df[col].isna()|(df[col]>=m))]
        e=((at[col]>=m)&(at[col]<m+pd.offsets.MonthBegin(1))).sum()
        ev+=e; risk+=len(at)
    return ev,risk,ev/risk
for w,(a,b) in {'6':('2026-05-01','2026-10-01'),'12':('2025-11-01','2026-10-01'),'24':('2024-11-01','2026-10-01'),'2025':('2025-01-01','2025-12-01'),'2024':('2024-01-01','2024-12-01')}.items():
    print(w, hazard(a,b))
print(df[df.born_solved][['id','released','solved85','solver85','solver85_source']])
area=df.assign(sol=df.solved85.notna()).groupby('area').agg(n=('id','size'),sol=('sol','sum'))
area['pct']=100*area.sol/area.n; print(area)
print('unsolved', df.solved85.isna().sum())
print(df[df.solved85>c.AS_OF])
