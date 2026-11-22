"""Fully-stressed sizing loop for the Bavuso V1 frame + single-sided swingarm (drives fea-frame-v1.py and fea-fatigue-v1.py).

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
Each iteration: run the CalculiX model (--only sizing: frame cases C1-C6, D1-D3, pack retention C7a-d, crash sliders C9b/c), compute
Miner damage, form for every design group the demand ratio = max(stress/allowable over all cases, (D/0.5)^(1/3)), and rescale the wall
(tubes), width/height (arm) or depth (plates) toward ratio = 1 with damping. Walls are quantised to 0.25 mm, min wall 1.5 mm (steel) / 3.5 mm (cast Al).
Outer diameters are kept at the CAD value except where a wall would exceed 13 % of the diameter (then OD +2 mm, flagged).
usage: python fea-size-v1.py --start <sections.json> --name <name> [--iters 8] [--h 36]
"""
import json, math, subprocess, sys, argparse, csv, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE.parents[1] / 'program' / 'data' / 'fea'
PY = sys.executable
sys.path.insert(0, str(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location('fat', str(HERE / 'fea-fatigue-v1.py')); FAT = importlib.util.module_from_spec(spec); spec.loader.exec_module(FAT)

ap = argparse.ArgumentParser()
ap.add_argument('--start', required=True); ap.add_argument('--name', required=True)
ap.add_argument('--iters', type=int, default=8); ap.add_argument('--h', type=float, default=36.0)
ap.add_argument('--fix', default='', help='comma list of groups kept fixed')
ap.add_argument('--skip', default='', help='comma list of case-name prefixes ignored for strength ratios (sensitivity)')
ap.add_argument('--tmax', type=float, default=0.13, help='max wall / OD before the OD grows by 2 mm (999 = never)')
ap.add_argument('--arm_t', type=float, default=0.0, help='fix arm wall (mm); 0 = free')
args = ap.parse_args()
FIX = set(args.fix.split(',')) if args.fix else set()
SKIP = tuple(args.skip.split(',')) if args.skip else ()

SFREQ = lambda c: 1.5 if c.startswith('C1') else 1.0 if c.startswith(('C7', 'C9')) else 1.2
FY = dict(steel=435.0, AL6061=240.0, A356=200.0)

def group(m):
    if m.startswith('SAR'): return 'arm'
    for pre, g in (('UR0', 'rail0'), ('UR1', 'rail'), ('UR2', 'rail2'), ('DL', 'downlink'), ('RL', 'rearlink'), ('TR', 'tailrail'), ('TB', 'tailbrace'),
                   ('ST0', 'post0'), ('ST1', 'post1'), ('SD', 'shock_diag'), ('TX', 'tailx_box'), ('STB', 'topbr'), ('HT', 'headtube'), ('GUS', 'head_gusset'),
                   ('STUB', 'stub'), ('SAX', 'brace'), ('STW', 'tower'), ('PIV', 'piv'), ('LUG', 'lug'), ('YOKE', 'yoke')):
        if m.startswith(pre): return g
    return None

def fy_of(g, V):
    if g in ('brace', 'tower'): return FY['A356']
    if g == 'arm': return FY[V.get('arm_mat', 'AL6061')]
    return FY['steel']

def quant(t, q=0.25): return round(t / q) * q

def evaluate(R):
    V = R['V']; ratios = {}; detail = {}
    for c, d in R['cases'].items():
        if SKIP and c.startswith(SKIP): continue
        for m, v in d['stress'].items():
            g = group(m)
            if g is None or g in ('yoke',): continue
            r = v[0] / (fy_of(g, V) / SFREQ(c))
            if r > ratios.get(m, (0, ''))[0]: ratios[m] = (r, c)
    rows = FAT.compute(R, 1.0)
    D = {r['member']: r['miner_D'] for r in rows}
    return ratios, D

def chassis_mass(R):
    tot = 0.0; keep = ('UR0', 'UR1', 'UR2', 'DL', 'RL', 'TR', 'TB', 'ST0', 'ST1', 'SD', 'TX', 'STB', 'HT', 'GUS', 'STUB', 'SAR', 'SAX', 'STW', 'PIV', 'LUG')
    for k, v in R['member_mass_kg'].items():
        if k.startswith(keep): tot += v
    return tot

def step(V, R):
    ratios, D = evaluate(R); newV = json.loads(json.dumps(V)); log = {}
    grp = {}
    for m, (r, c) in ratios.items():
        g = group(m)
        rf = max(r, (D.get(m, 0) / 0.5) ** (1 / 3) if D.get(m, 0) > 0 else 0)
        # arms are split by station index for the taper
        key = g
        if g == 'arm':
            k = int(m[3:]); key = 'arm_p' if k <= 5 else 'arm_a'
        if rf > grp.get(key, (0, ''))[0]: grp[key] = (rf, m, c, D.get(m, 0))
    for key, (rf, m, c, Dm) in grp.items(): log[key] = (round(rf, 3), m, c, Dm)
    def tube(name, lo_t=1.5):
        if name in FIX or name not in grp: return
        ro, t = newV[name]; rf = grp[name][0]
        if 0.92 <= rf <= 1.0: return
        f = min(1.4, max(0.75, rf ** 0.9)); tn = quant(t * f)
        tn = max(lo_t, tn)
        if tn > args.tmax * 2 * ro: ro += 1.0; tn = quant(tn * 0.8)
        newV[name] = [ro, tn]
    for nm in ('rail', 'rail0', 'rail2', 'downlink', 'rearlink', 'tailrail', 'tailbrace', 'shock_diag'): tube(nm)
    for k in (0, 1):
        nm = 'post%d' % k
        if nm in grp and nm not in FIX:
            s = newV['struts'][k]; ro, t = s[2], s[3]; f = min(1.4, max(0.75, grp[nm][0] ** 0.9)); f = 1.0 if 0.92 <= grp[nm][0] <= 1.0 else f; tn = max(1.5, quant(t * f))
            if tn > args.tmax * 2 * ro: ro += 1.0; tn = quant(tn * 0.8)
            newV['struts'][k] = [s[0], s[1], ro, tn, s[4]]
    if 'tailx_box' in grp and 'tailx_box' not in FIX:
        a, b, t = newV['tailx_box']; f = min(1.4, max(0.75, grp['tailx_box'][0] ** 0.9)); tn = max(2.0, quant(t * f))
        if tn > 8: a += 5; tn = 6.0
        newV['tailx_box'] = [a, b, tn]
    if 'topbr' in grp and 'topbr' not in FIX:
        t, d = newV['topbr']; f = grp['topbr'][0]
        d = quant(d * min(1.3, max(0.8, f ** 0.5)), 1.0); t = quant(t * min(1.3, max(0.8, f ** 0.4)), 1.0); newV['topbr'] = [max(8, min(t, 20)), max(36, min(d, 90))]
    if 'head_gusset' in grp and 'head_gusset' not in FIX:
        newV['head_gusset'] = max(4.0, quant(newV['head_gusset'] * min(1.4, max(0.75, grp['head_gusset'][0] ** 0.9))))
    if 'stub' in grp and 'stub' not in FIX:
        ro, t = newV['stub']; f = grp['stub'][0]
        if f > 1.0: ro = min(40.0, ro + math.ceil((f - 1) * 6)); t = min(t + 1, 0.4 * ro)
        elif f < 0.85: ro = max(20.0, ro - 1); t = max(4, t)
        newV['stub'] = [ro, t]
    for nm, lo in (('brace', 3.5),):
        if nm in grp and nm not in FIX:
            ro, t = newV[nm]; f = grp[nm][0]
            if f > 1.0 or f < 0.8: ro = max(22, ro * min(1.25, max(0.85, f ** 0.4)))
            t = max(lo, quant(t * min(1.3, max(0.8, f ** 0.5)), 0.5)); newV[nm] = [round(ro * 2) / 2, t]
    if 'tower' in grp and 'tower' not in FIX:
        t, d = newV['tower']; f = grp['tower'][0]
        d = quant(d * min(1.35, max(0.8, f ** 0.6)), 2.0); t = quant(t * min(1.3, max(0.85, f ** 0.3)), 1.0)
        newV['tower'] = [max(6, min(t, 16)), max(40, min(d, 110))]
    # arm: scale W,H (not t) toward ratio 1; t fixed at args.arm_t (or kept)
    for key, idx in (('arm_p', 'arm_pivot'), ('arm_a', 'arm_axle')):
        if key in grp and 'arm' not in FIX:
            W, H, t = newV[idx]; f = grp[key][0]; s = min(1.25, max(0.85, f ** (1 / 2.5)))
            if args.arm_t: t = args.arm_t
            newV[idx] = [round(W * s * 2) / 2, round(H * s * 2) / 2, t]
    # arm centreline: inner face 110 at the axle end
    newV['arm_y'] = 110.0 + newV['arm_axle'][0] / 2
    return newV, grp

V = json.loads(Path(args.start).read_text())
logf = OUT / ('sweep-%s.csv' % args.name)
rowsout = []
for it in range(args.iters + 1):
    vf = OUT / ('%s-sections.json' % args.name); vf.write_text(json.dumps(V, indent=1))
    p = subprocess.run([PY, str(HERE / 'fea-frame-v1.py'), '--h', str(args.h), '--variant', args.name, '--only', 'sizing', '--tag', 'it'], capture_output=True, text=True, cwd=str(HERE))
    rf = OUT / ('results-%s-h%g-sizing-it.json' % (args.name, args.h))
    if not rf.exists() or p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-2000:]); raise SystemExit('run failed')
    R = json.loads(rf.read_text()); m = chassis_mass(R)
    V = R['V']; newV, grp = step(V, R)
    mx = max(g[0] for g in grp.values()); worst = max(grp.items(), key=lambda kv: kv[1][0])
    print('it %d: chassis %.2f kg, max ratio %.2f (%s %s %s) arm_p %s arm_a %s' % (it, m, mx, worst[0], worst[1][1], worst[1][2], V['arm_pivot'], V['arm_axle']), flush=True)
    rowsout.append(dict(it=it, kg=round(m, 3), max_ratio=round(mx, 3), worst=worst[0], **{k: json.dumps(V[k]) for k in ('rail', 'rail0', 'rail2', 'downlink', 'rearlink', 'tailrail', 'tailbrace', 'shock_diag', 'tailx_box', 'topbr', 'stub', 'brace', 'tower', 'arm_pivot', 'arm_axle', 'head_gusset', 'struts')}))
    if newV == V and it > 0: print('converged'); break
    V = newV
with open(logf, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rowsout[0].keys())); w.writeheader(); w.writerows(rowsout)
print(json.dumps(V))
