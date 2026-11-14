from data import *

def sat_table(ids):
    rows = []
    for k in ids:
        b = R[k]; rel = rel_date(b['released']); f = frontier(k)
        s85 = pd.Timestamp(b['saturatedAt']) if b.get('saturatedAt') else pd.NaT
        s95 = pd.Timestamp(b['nearCeilingAt']) if b.get('nearCeilingAt') else pd.NaT
        pre = f[f.date <= rel]['value'].max() if len(f) else np.nan
        ep = b.get('epoch') or {}
        rnd, ceil = ep.get('random'), ep.get('ceiling')
        s85n = pd.NaT
        if rnd is not None and ceil is not None:
            thr = rnd + 0.85 * (ceil - rnd)
            hit = f[f.value >= thr]
            s85n = hit.date.iloc[0] if len(hit) else pd.NaT
        rows.append(dict(id=k, name=b['name'], area=b['area'], released=rel, sat85=s85, sat95=s95,
                         pre_best=pre, best=f.value.max() if len(f) else np.nan, n_cites=b['ncites'],
                         s85n=s85n, rnd=rnd, ceil=ceil,
                         first_pt=f.date.min() if len(f) else pd.NaT))
    T = pd.DataFrame(rows).set_index('id')
    T['eff85'] = T[['sat85', 'released']].max(axis=1).where(T.sat85.notna())
    T['eff95'] = T[['sat95', 'released']].max(axis=1).where(T.sat95.notna())
    T['on_arrival'] = T.sat85.notna() & (T.sat85 <= T.released)
    T['m85'] = (T.eff85 - T.released).dt.days / 30.44
    T['m95'] = (T.eff95 - T.released).dt.days / 30.44
    T['age'] = (AS_OF - T.released).dt.days / 30.44
    return T

def eligible():
    b = B[(B.unit == '%') & (B.better == 'higher') & (B.area != 'safety') & B.released.notna()]
    return b

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
    top = eligible().sort_values('n_cites', ascending=False).head(32).index
    T = sat_table(top)
    print(T.sort_values('released')[['name','released','sat85','sat95','pre_best','best','on_arrival','m85','m95','s85n','rnd','ceil','n_cites']].round(1).to_string())
