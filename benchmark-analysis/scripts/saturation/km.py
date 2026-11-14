from sat_calc import *
def km(t, e):
    order = np.argsort(t, kind='stable'); t = np.asarray(t)[order]; e = np.asarray(e)[order]
    n = len(t); S = 1.0; xs = [0.0]; ys = [1.0]
    for i, (ti, ei) in enumerate(zip(t, e)):
        if ei:
            S *= (1 - 1 / (n - i)); xs.append(ti); ys.append(S)
    return np.array(xs), np.array(ys)
def S_at(xs, ys, x):
    return ys[xs <= x][-1]
def cohort_table(T):
    T = T.copy()
    T['coh'] = pd.cut(T.released.dt.year, [0, 2022, 2023, 2024, 2025, 2026], labels=['2022 or earlier', '2023', '2024', '2025', '2026'])
    out = {}
    for coh, g in T.groupby('coh', observed=True):
        t = np.where(g.m85.notna(), g.m85, g.age); e = g.m85.notna().values
        xs, ys = km(t, e)
        med = xs[ys <= 0.5][0] if (ys <= 0.5).any() else np.nan
        out[coh] = dict(n=len(g), sat=int(e.sum()), on_arrival=int(g.on_arrival.sum()), xs=xs, ys=ys, median=med,
                        sat12=1 - S_at(xs, ys, 12), sat24=1 - S_at(xs, ys, 24) if g.age.max() >= 24 else np.nan, maxage=g.age.max())
    return out
if __name__ == '__main__':
    el = eligible()
    for label, ids in [('cites>=10', el[el.n_cites >= 10].index), ('board>=20 any cites', el[el.n_board >= 20].index),
                       ('board>=20 & cites==0', el[(el.n_board >= 20) & (el.n_cites == 0)].index)]:
        T = sat_table(ids); T = T[T.first_pt.notna()]
        print(label, len(T))
        for k, v in cohort_table(T).items():
            print(f"   {k}: n={v['n']} sat={v['sat']} arr={v['on_arrival']} med={v['median']:.1f} sat12={v['sat12']:.2f} sat24={v['sat24']:.2f}")
