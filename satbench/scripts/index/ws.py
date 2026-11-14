import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys; sys.path.insert(0,ROOT)
import common as c, pandas as pd, numpy as np
S=[x for x in c.summaries() if (x['unit'] or '%')=='%' and x['better']!='lower']
print(len(S))
def ws(t,k=2):
    lo=t-pd.DateOffset(months=6); n=0; sol=0
    for x in S:
        cards={cc['card'] for cc in x['cites'] if lo< pd.Timestamp(cc['date'])<=t}
        if len(cards)>=k:
            n+=1; cr=c.crossing(x['frontier'],85)
            if cr and pd.Timestamp(cr['date'])<=t: sol+=1
    return n,sol
for t in list(pd.date_range('2023-07-01','2026-11-01',freq='QS'))+[c.AS_OF]:
    print(t.date(), ws(t), ws(t,3))
