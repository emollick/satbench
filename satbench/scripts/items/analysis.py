import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # satbench/scripts
import sys, json
sys.path.insert(0, ROOT)
import numpy as np, pandas as pd
import common as c

AS_OF = c.AS_OF
YEAR_AGO = pd.Timestamp('2025-11-14')
MO = 30.4375

df = c.items()
df['rel_year'] = df.released.dt.year
AUD = json.load(open(os.path.join(ROOT, 'repo', 'data', 'audits.json')))
audit = {}
for a in AUD:
    for f in a['findings']:
        audit.setdefault(f['benchmark'], []).append((a['author'], a['date'], f['problems'], f['status'], f.get('numbers', '')))


def frontier_at(fr, t):
    v = [p for p in fr if pd.Timestamp(p['date']) <= t]
    return v[-1] if v else None


def holdouts():
    u = df[df.solved85.isna()].copy()
    rows = []
    for _, r in u.iterrows():
        fr = r.frontier
        base_d = max(YEAR_AGO, r.released)
        p0 = frontier_at(fr, base_d)
        if p0 is None:
            start_v, start_d, base = fr[0]['value'], pd.Timestamp(fr[0]['date']), 'first score'
        else:
            start_v, start_d, base = p0['value'], base_d, ('12 mo ago' if base_d == YEAR_AGO else 'release')
        months = (AS_OF - start_d).days / MO
        gain = r.best - start_v
        pace = gain / months if months > 0 else np.nan
        if gain <= 0 or not np.isfinite(pace):
            eta = pd.NaT
        else:
            eta = AS_OF + pd.Timedelta(days=(85 - r.best) / pace * MO)
        rows.append(dict(id=r.id, name=r['name'], area=r.area, released=r.released, n_cites=r.n_cites, status=r.status,
                         best=r.best, best_model=r.best_model, best_source=r.best_source, best_date=r.best_date,
                         start_v=start_v, start_d=start_d, base=base, window_mo=months, gain=gain, pace=pace, eta85=eta,
                         epoch_ceiling=r.epoch_ceiling, audit=audit.get(r.id)))
    return pd.DataFrame(rows).sort_values('n_cites', ascending=False).reset_index(drop=True)


def months_to_solve(d):
    """duration (months) and event flag; born-solved / pre-release crossings clipped to 0."""
    ev = d.solved85.notna()
    end = d.solved85.where(ev, AS_OF)
    t = ((end - d.released).dt.days / MO).clip(lower=0)
    return t.values, ev.values


def km(t, e):
    t = np.asarray(t, float); e = np.asarray(e, bool)
    times = np.unique(t[e])
    S, var_sum, out = 1.0, 0.0, [(0.0, 1.0, 1.0, 1.0)]
    for ti in times:
        n = (t >= ti).sum(); d = ((t == ti) & e).sum()
        S *= 1 - d / n
        if n > d:
            var_sum += d / (n * (n - d))
        # log-log CI
        if 0 < S < 1:
            se = np.sqrt(var_sum) / abs(np.log(S))
            lo = S ** np.exp(1.96 * se); hi = S ** np.exp(-1.96 * se)
        else:
            lo = hi = S
        out.append((ti, S, lo, hi))
    return pd.DataFrame(out, columns=['t', 'S', 'lo', 'hi'])


def km_median(t, e):
    k = km(t, e)
    def first_below(col):
        x = k[k[col] <= 0.5]
        return x.t.iloc[0] if len(x) else np.nan
    return first_below('S'), first_below('lo'), first_below('hi'), k  # median, lower CI (lower band), upper CI (upper band; nan = not reached)


def max_followup(t):
    return np.max(t)


if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    h = holdouts()
    print(h.drop(columns=['audit']).head(25).to_string())
    print('unsolved by status', h.status.value_counts().to_dict())
    print('no progress (gain<=0):', h[h.gain <= 0][['id', 'n_cites', 'best', 'best_date', 'status']].to_string())
    print('\nCOHORTS')
    for y in [2022, 2023, 2024, 2025, 2026]:
        d = df[df.rel_year == y] if y > 2022 else df[df.rel_year <= 2022]
        t, e = months_to_solve(d)
        m, lo, hi, k = km_median(t, e)
        s12 = k[k.t <= 12].S.iloc[-1]
        print(y, len(d), 'solved', e.sum(), 'born', int(d.born_solved.sum()), 'median', round(m, 1), 'CI', round(lo, 1), round(hi, 1),
              'maxfollow', round(t.max(), 1), 'share solved by 12mo', round(1 - s12, 2), 'raw med solved', round(np.median(t[e]), 1))
    print('\n85->95')
    g = df[df.solved95.notna()].copy()
    g['gap'] = (g.solved95 - g.solved85).dt.days / MO
    print(len(g), 'median', g.gap.median(), 'same-day', (g.gap == 0).sum(), 'IQR', g.gap.quantile([.25, .75]).tolist())
    g2 = g[~g.born_solved]
    print('excl born', len(g2), g2.gap.median())
    for y, gg in g.groupby('rel_year'): print(' ', y, len(gg), round(gg.gap.median(), 1))
    s85 = df[df.solved85.notna()]
    print('solved85 not95', (s85.solved95.isna()).sum(), 'of', len(s85))
    # KM 85->95 among solved85
    t = ((s85.solved95.where(s85.solved95.notna(), AS_OF) - s85.solved85).dt.days / MO).values
    m, lo, hi, _ = km_median(t, s85.solved95.notna().values)
    print('KM 85->95 median', m, lo, hi)
    print(g.sort_values('gap', ascending=False)[['id', 'solved85', 'solved95', 'gap']].head(8).to_string())
    print('\nAREAS')
    for a, d in df.groupby('area'):
        t, e = months_to_solve(d)
        m, lo, hi, _ = km_median(t, e)
        print(a, len(d), 'solved', e.sum(), round(100 * e.mean()), '% median', round(m, 1), (round(lo, 1), round(hi, 1)), 'born', d.born_solved.sum(),
              'rel median', d.released.median().date())
    print('\nborn solved', df[df.born_solved][['id', 'released', 'solved85', 'solver85', 'solver85_value']].to_string())
    print('negative/odd: solved before release', df[(df.solved85 < df.released)][['id', 'released', 'solved85', 'solver85']].to_string())
