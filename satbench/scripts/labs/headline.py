from data import *
# per card: % / higher-better benchmarks cited, and whether frontier was >=85 strictly before post date
elig = [x for x in c.summaries() if (x['unit'] or '%') == '%' and x['better'] != 'lower']
rows = {}
for x in elig:
    fr = x['frontier']
    for ci in x['cites']:
        key = (ci['card'], x['id'])
        if key in rows: continue
        d = ci['date']
        prior = [p for p in fr if p['date'] < d]
        pb = max([p['value'] for p in prior], default=np.nan)
        rows[key] = dict(card=ci['card'], bench=x['id'], date=pd.Timestamp(d), lab=ci['lab'], model=ci['model'],
                         score=ci['score'], prior_best=pb, sat=bool(pb >= 85) if pb == pb else False,
                         item=len(x['cites']) >= 10)
H = pd.DataFrame(rows.values())
P = H.groupby('card').agg(date=('date', 'first'), lab=('lab', 'first'), n=('bench', 'size'), k=('sat', 'sum')).reset_index()
P['share'] = P.k / P.n
P['year'] = P.date.dt.year
P['frontier'] = P.lab.isin(c.FRONTIER_LABS)
