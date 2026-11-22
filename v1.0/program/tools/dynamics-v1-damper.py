"""V1 dynamics step 3b: does the bike need a steering damper, and if so what? Speed-scheduled (semi-active) damper search.

Uses dynamics-v1-stability.py (same model, same parameters; frame + fork + swingarm flex). For each of the three load cases it
computes the weakest wobble damping ratio (15-130 mph) and weakest weave damping ratio (25-130 mph) with a damper of
  c(v) = c_low up to v1, falling linearly to c_high at v2   (Nms/rad about the steering axis, hands off the bars).
Search: smallest c_low, then smallest authority, for which every case has both modes at or above a target damping ratio.
Outputs: program/data/dynamics/damper-results.json, damper-schedule.png, damper-fixed-vs-scheduled.png.
Run from v1.0 with the FreeCAD python. November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import importlib.util, json, itertools, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stab', HERE / 'dynamics-v1-stability.py'); st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
OUT = st.OUT
CASES = ['bike_only', 'solo', 'solo_luggage']


def metrics(case, c_steer, **kw):
    p = st.params(case, c_steer=c_steer, **kw)
    sw = st.run(p, 'x', key=(case, kw.get('frame', True), kw.get('fork', True), kw.get('rear', True)))
    s = sw['summary']
    return dict(wobble=s['wobble']['min_zeta'], wobble_at=s['wobble']['at_mph'], weave=s['weave']['min_zeta'], weave_at=s['weave']['at_mph'],
                other=s.get('other', {}).get('min_zeta'), rows=sw['rows'])


def worst(c_steer, cases=CASES, **kw):
    out = {c: metrics(c, c_steer, **kw) for c in cases}
    return out, min(min(o['wobble'], o['weave']) for o in out.values())


if __name__ == '__main__':
    res = {}
    # 1) fixed damping sweep, all cases (reference)
    fixed = {}
    for cs in (0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 25.0):
        o, w = worst(cs)
        fixed[str(cs)] = {c: dict(wobble=o[c]['wobble'], weave=o[c]['weave']) for c in CASES}
        print(f'fixed {cs:5.1f}: ' + '  '.join(f"{c} wob {o[c]['wobble']:+.3f} weave {o[c]['weave']:+.3f}" for c in CASES), flush=True)
    res['fixed'] = fixed
    # 2) scheduled damper grid
    grid = []
    for c_low, c_high, v1, v2 in itertools.product((10.0, 15.0, 20.0, 25.0, 30.0, 40.0), (0.0, 3.0, 6.0, 9.0), (50.0, 65.0, 80.0), (95.0, 115.0)):
        if v2 <= v1:
            continue
        o, w = worst(st.sched(c_low, c_high, v1, v2))
        grid.append(dict(c_low=c_low, c_high=c_high, v1=v1, v2=v2, worst_zeta=w, per_case={c: dict(wobble=o[c]['wobble'], weave=o[c]['weave']) for c in CASES}))
    grid.sort(key=lambda r: -r['worst_zeta'])
    res['grid_top'] = grid[:12]
    print('best scheduled:'); [print('  ', {k: v for k, v in r.items() if k != 'per_case'}) for r in grid[:6]]
    targets = {}
    for tgt in (0.0, 0.02, 0.03, 0.05):
        ok = [r for r in grid if r['worst_zeta'] >= tgt]
        if ok:
            ok.sort(key=lambda r: (r['c_low'], r['c_high'], -r['v1']))
            targets[str(tgt)] = ok[0]
            print('smallest damper reaching worst zeta >=', tgt, {k: v for k, v in ok[0].items() if k != 'per_case'})
        else:
            targets[str(tgt)] = None
            print('no scheduled damper in the grid reaches', tgt)
    res['smallest_for_target'] = targets
    # 3) the recommended schedule: refine around the best, then full verification with sensitivities
    best = grid[0]
    rec = dict(c_low=best['c_low'], c_high=best['c_high'], v1=best['v1'], v2=best['v2'])
    # prefer the smallest c_low within 0.005 of the best worst-zeta
    near = [r for r in grid if r['worst_zeta'] >= best['worst_zeta'] - 0.005]
    near.sort(key=lambda r: (r['c_low'], r['c_high']))
    rec = {k: near[0][k] for k in ('c_low', 'c_high', 'v1', 'v2')}
    print('recommended', rec)
    sched = st.sched(rec['c_low'], rec['c_high'], rec['v1'], rec['v2'])
    ver = {}
    o, w = worst(sched)
    ver['nominal'] = dict(worst=w, per_case={c: dict(wobble=o[c]['wobble'], wobble_at=o[c]['wobble_at'], weave=o[c]['weave'], weave_at=o[c]['weave_at'], other=o[c]['other']) for c in CASES})
    for lab, kw in (('frame k from 4.4 kNm/deg torsion', dict(k_frame=st.K_FRAME_TORSION_FEA)), ('frame 120 kNm/rad', dict(k_frame=120e3)),
                    ('fork 20 kNm/rad', dict(k_fork=20e3)), ('fork 40 kNm/rad', dict(k_fork=40e3)), ('rigid swingarm', dict(rear=False)),
                    ('tyre Ka x0.7', dict(tyre_scale=dict(F=dict(Ka=0.7), R=dict(Ka=0.7)))), ('tyre Ka x1.3', dict(tyre_scale=dict(F=dict(Ka=1.3), R=dict(Ka=1.3)))),
                    ('relaxation x1.5', dict(tyre_scale=dict(F=dict(sigma=1.5), R=dict(sigma=1.5)))), ('relaxation x0.5', dict(tyre_scale=dict(F=dict(sigma=0.5), R=dict(sigma=0.5))))):
        o, w = worst(sched, **kw)
        ver[lab] = dict(worst=w, per_case={c: dict(wobble=o[c]['wobble'], weave=o[c]['weave']) for c in CASES})
        print(f'  sensitivity {lab:36s} worst {w:+.3f}  ' + ' '.join(f"{c}: {o[c]['wobble']:+.3f}/{o[c]['weave']:+.3f}" for c in CASES), flush=True)
    res['recommended'] = dict(schedule=rec, verification=ver)
    # 4) rows for the plots and the report
    nom = {c: metrics(c, sched)['rows'] for c in CASES}
    nod = {c: metrics(c, 0.0)['rows'] for c in CASES}
    res['rows_scheduled'] = nom; res['rows_no_damper'] = nod
    (OUT / 'damper-results.json').write_text(json.dumps(res, indent=1, default=str))
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for c, col in zip(CASES, ('tab:gray', 'tab:blue', 'tab:orange')):
        for rows, ls, lab in ((nod[c], ':', 'no damper'), (nom[c], '-', 'scheduled')):
            for k, a in (('wobble', ax[0]), ('weave', ax[1])):
                a.plot([r['mph'] for r in rows if k in r], [r[k]['zeta'] for r in rows if k in r], ls, color=col, label=f'{c}, {lab}')
    for a, t in ((ax[0], 'wobble damping ratio'), (ax[1], 'weave damping ratio')):
        a.axhline(0, color='k', lw=0.8); a.axhline(0.05, color='r', lw=0.6, ls=':'); a.set_ylim(-0.2, 0.4); a.set_xlabel('speed, mph'); a.set_title(t); a.grid(alpha=.3)
    ax[0].legend(fontsize=6)
    v = np.linspace(10, 130, 60); ax[2].plot(v, [sched(x * st.MPH) for x in v]); ax[2].set_xlabel('speed, mph'); ax[2].set_ylabel('steering damping, Nms/rad'); ax[2].set_title('recommended schedule'); ax[2].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / 'damper-schedule.png', dpi=110)
