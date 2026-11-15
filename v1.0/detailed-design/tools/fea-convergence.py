"""Mesh convergence of the structural pack case (the critical part) over three shell meshes (24, 12, 6 mm).

November 13, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).
Reads run/pack-retention-<variant>-h{24,12,6}.frd (C7a 20 g longitudinal = step 1, C7b = step 2) and
run/frame-<variant>-h*.frd (C3 braking = step 3) and reports, per mesh:
  - the peak von Mises on the pack (sits at a re-entrant step corner or a rigid lug-patch edge: singular, expected to grow);
  - von Mises at fixed probe points in smooth regions (mid-panel), which should converge;
  - the 99th-percentile pack stress (robust to the corner singularity).
usage: python fea-convergence.py revised
"""
import sys, json, re
import numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'structures'; RUN = OUT / 'run'
var = sys.argv[1] if len(sys.argv) > 1 else 'revised'

def read(frd, inp):
    n_shell = 0; on = False
    for l in open(inp):
        if l.startswith('*'):
            on = l.startswith('*ELEMENT,TYPE=S4'); continue
        if on: n_shell += 1
    coords, el, steps = {}, {}, []
    L = open(frd).readlines(); i = 0
    while i < len(L):
        s = L[i]
        if s.startswith('    2C'):
            i += 1
            while not L[i].startswith(' -3'):
                t = L[i]; coords[int(t[3:13])] = (float(t[13:25]), float(t[25:37]), float(t[37:49])); i += 1
        elif s.startswith('    3C'):
            i += 1
            while not L[i].startswith(' -3'):
                t = L[i]
                if t.startswith(' -1'): eid = int(t[3:13]); el[eid] = []
                elif t.startswith(' -2'): el[eid] += [int(t[3 + 10 * k:13 + 10 * k]) for k in range((len(t.rstrip()) - 3) // 10)]
                i += 1
        elif s.startswith(' -4  STRESS'):
            i += 1
            while L[i].startswith(' -5'): i += 1
            d = {}
            while not L[i].startswith(' -3'):
                t = L[i]; d[int(t[3:13])] = [float(t[13 + 12 * k:25 + 12 * k]) for k in range(6)]; i += 1
            steps.append(d)
        i += 1
    sn = sorted({n for e in range(1, n_shell + 1) if e in el for n in el[e]})
    X = np.array([coords[n] for n in sn])
    return sn, X, steps

def vm(a):
    a = np.asarray(a); s = a[:, :3]; m = s.mean(1, keepdims=True); d = s - m
    return np.sqrt(1.5 * (np.sum(d * d, 1) + 2 * np.sum(a[:, 3:] ** 2, 1)))

# probe points (model mm): front-wall panel centre between the lugs, side-wall centre, roof centre
PROBES = {'front_wall_centre (1050,0,420)': (1050, 0, 420), 'side_wall_centre (850,194,400)': (850, 194, 400),
          'roof_centre (850,0,573)': (850, 0, 573.5), 'floor_centre (850,0,198)': (850, 0, 198)}
out = {}
for h in (24, 12, 6):
    tag = '%s-h%d' % (var, h); res = {}
    for stem, cases in [('pack-retention', {'C7a_20g': 0, 'C7b_8g_lat': 1}), ('frame', {'C3_braking': 2, 'C2_front_bump': 1})]:
        frd = RUN / ('%s-%s.frd' % (stem, tag)); inp = RUN / ('%s-%s.inp' % (stem, tag))
        if not frd.exists(): continue
        sn, X, steps = read(frd, inp)
        for cname, k in cases.items():
            S = np.array([steps[k][n] for n in sn]); v = vm(S)
            r = dict(peak=round(float(v.max()), 1), peak_at=X[int(v.argmax())].round(1).tolist(), p99=round(float(np.percentile(v, 99)), 1))
            for pn, p in PROBES.items():
                d = np.linalg.norm(X - np.array(p), axis=1); near = d <= max(h, 8) * 1.0
                r[pn] = round(float(v[near].max()), 1) if near.any() else None
            res[cname] = r
    out['h%d' % h] = res
(OUT / ('convergence-%s.json' % var)).write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
