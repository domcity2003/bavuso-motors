"""V1 dynamics step 3: weave / wobble / flex-mode eigenvalue sweep, 10-130 mph, three load cases, rev D.

Model: dynamics-v1-model.py (Sharp-type, exact second-order Lagrangian) with
  frame torsion  k_bf = K_head * h^2  (FEA lateral head stiffness 1.3 kN/mm, h = head height above the pivot axis),
  fork bending   k_bk  (ASSUMED 30 kNm/rad; the 48 mm USD fork is not designed; 40 is the spec target),
  swingarm       cantilever EI from FEA lateral 1.01 kN/mm (and yaw 1.73 kNm/deg, which it reproduces) + torsion 1.48 kNm/deg.
Load cases: bike alone, bike + 90 kg rider (hands off the bars), bike + rider + 25 kg luggage. Mass properties come from
program/data/dynamics/mass-properties.json (dynamics-v1-massprops.py).

Outputs: program/data/dynamics/stability-results.json, stability-*.png, stability-modes.csv.
Run from v1.0 with the FreeCAD python (numpy, sympy, matplotlib). November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import copy, csv, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dynmodel', HERE / 'dynamics-v1-model.py'); dm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
OUT = HERE.parent / 'data' / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())
GEO = MP['geometry']
CASES = {'bike_only': 'bike alone', 'solo': 'bike + 90 kg rider', 'solo_luggage': 'bike + rider + 25 kg luggage'}

CASTER = math.radians(GEO['rake_deg'])
S_PT = [v / 1000 for v in GEO['steering_axis_point_mm']]
XF = GEO['front_axle_x_mm'] / 1000; WB = GEO['wheelbase_mm'] / 1000
RF, RR = 0.3315, 0.325                 # CAD in-service outer radii (663 / 650 mm)
Z_PIVOT = GEO['pivot_mm'][2] / 1000
Z_HEAD = 0.930                         # Head_tube centre, saved CAD
# --- frame, fork and swingarm stiffness -------------------------------------------------------------------------
K_HEAD_LAT = 1.3e6                     # N/m, FEA (09-structures.md, "Lateral, head 1.3 kN/mm")
K_FRAME = K_HEAD_LAT * (Z_HEAD - Z_PIVOT) ** 2     # Nm/rad about the longitudinal axis at pivot height (~361e3)
K_FRAME_TORSION_FEA = 4.4e3 * 180 / math.pi        # Nm/rad: FEA "torsion head to pivot 4.4 kNm/deg" (~252e3), sensitivity
K_FORK = 30e3                          # Nm/rad ASSUMED (Taraborrelli enduro fork 28 bending; spec target is >= 40)
L_ARM = math.hypot(0.540, Z_PIVOT - 0.325)        # pivot to axle, 0.5456 m
K_SA_LAT = 1.01e6                      # N/m FEA, at the axle
K_SA_TORS = 1.48e3 * 180 / math.pi     # Nm/rad FEA torsion about the arm axis (~84.8e3)
EI_SA = K_SA_LAT * L_ARM ** 3 / 3      # cantilever; check: EI/L = 100 kNm/rad vs FEA yaw 1.73 kNm/deg = 99 kNm/rad
REAR_FLEX = dict(EI=EI_SA, L=L_ARM, k_ep=K_SA_TORS, c_ya=140.0, c_th=10.0, c_ep=10.0)
C_BF, C_BK = 30.0, 20.0                # structural damping, Nms/rad (about 2% critical)
# --- tyres (normalised per unit load), same mid-range literature set as detailed-design/dynamics-study.md ----------
TYRE_F = dict(Ka=13.0, Kg=0.90, Ma=0.33, Mg=0.010, sigma=0.20, rho=0.065)
TYRE_R = dict(Ka=11.0, Kg=0.85, Ma=0.33, Mg=0.010, sigma=0.25, rho=0.090)
AERO_DFZ_100 = 80.0                    # N moved front -> rear at 100 km/h (aero-baseline-report.md), scales with v^2
MPH = 0.44704
SPEEDS_MPH = np.arange(10.0, 130.01, 2.5)


def sched(c_low, c_high, v1_mph, v2_mph):
    def f(v):
        k = v / MPH
        return c_low if k <= v1_mph else (c_high if k >= v2_mph else c_low + (c_high - c_low) * (k - v1_mph) / (v2_mph - v1_mph))
    return f


def sym(I):
    I = np.array(I); I[0, 1] = I[1, 0] = I[1, 2] = I[2, 1] = 0.0
    return I.tolist()


def params(case, frame=True, fork=True, rear=True, k_frame=K_FRAME, k_fork=K_FORK, c_steer=0.0, tyre_scale=None):
    mp = MP[case]
    B = mp['rear_frame']; H = mp['front_frame']; Fw = mp['front_wheel']; Rw = mp['rear_wheel']
    mt = mp['total']['m']; xg = mp['total']['c'][0]
    FzF = mt * dm.G0 * xg / XF; FzR = mt * dm.G0 - FzF
    p = dict(caster=CASTER, S=S_PT, z_twist=Z_PIVOT,
             B=dict(m=B['m'], c=[B['c'][0], 0, B['c'][2]], I=sym(B['I'])),
             H=dict(m=H['m'], c=[H['c'][0], 0, H['c'][2]], I=sym(H['I'])),
             R=dict(m=Rw['m'], centre=[0, 0, RR], R=RR, Ixx=Rw['I'][0][0], Iyy=Rw['I'][1][1], Fz=FzR, **TYRE_R),
             F=dict(m=Fw['m'], centre=[XF, 0, RF], R=RF, Ixx=Fw['I'][0][0], Iyy=Fw['I'][1][1], Fz=FzF, **TYRE_F),
             c_steer=c_steer, rotor=(mp['rotor_gyro']['J'], mp['rotor_gyro']['ratio']), trail=GEO['trail_mm'] / 1000, m=mt, xg=xg)
    if frame:
        p.update(k_bf=k_frame, c_bf=C_BF)
    if fork:
        U = mp['front_upper']; L = mp['front_lower']
        p.update(k_bk=k_fork, c_bk=C_BK, H=dict(m=U['m'], c=[U['c'][0], 0, U['c'][2]], I=sym(U['I'])),
                 L=dict(m=L['m'], c=[L['c'][0], 0, L['c'][2]], I=sym(L['I'])))
    if rear:
        p['rear_flex'] = dict(REAR_FLEX)
    if tyre_scale:
        for k_, d_ in tyre_scale.items():
            for kk, fac in d_.items():
                p[k_][kk] *= fac
    return p


def steer_inertia(p):
    """Inertia of the steered assembly (front frame + front wheel) about the steering axis, kg m2."""
    s = np.array([-math.sin(CASTER), 0, math.cos(CASTER)]); S = np.array(S_PT); tot = 0.0
    for key in ('H', 'L', 'F'):
        if key not in p:
            continue
        b = p[key]
        if key == 'F':
            I = np.diag([b['Ixx'], b['Iyy'], b['Ixx']]); c = np.array(b['centre'])
        else:
            I = np.array(b['I']); c = np.array(b['c'])
        d = c - S; dp = d - np.dot(d, s) * s
        tot += s @ I @ s + b['m'] * np.dot(dp, dp)
    return tot


def fz_at(p, kmh):
    d = AERO_DFZ_100 * (kmh / 100.0) ** 2
    return (p['R']['Fz'] + d, p['F']['Fz'] - d)


def modes_at(md, p, mph):
    v = mph * MPH
    lam, X = md.eig(v, fz_at(p, v * 3.6))
    n = md.n; nm = md.names
    out = []
    sc = dict(y=0.3, psi=1, phi=1, delta=1, bf=1, bk=1, ya=0.01, th=1, ep=1)   # scale metres to ~radians for participation
    for k, l in enumerate(lam):
        if np.imag(l) < -1e-9 or abs(l) < 1e-7:
            continue
        x = {n_: abs(X[i, k]) / sc[n_] for i, n_ in enumerate(nm)}
        tot = sum(x.values()) + 1e-12
        out.append(dict(l=complex(l), x=x, tot=tot))
    return out


def seed(cands, mode):
    osc = [c for c in cands if abs(c['l'].imag) > 1e-6]
    f = lambda c: abs(c['l'].imag) / 2 / math.pi
    g = lambda c, k: c['x'].get(k, 0.0)
    if mode == 'weave':
        cs = [c for c in osc if 1.5 < f(c) < 5.5]
        return max(cs, key=lambda c: (g(c, 'phi') + g(c, 'psi')) / (g(c, 'delta') + g(c, 'bk') + g(c, 'bf') + 1e-9))['l']
    if mode == 'wobble':
        cs = [c for c in osc if 4.0 < f(c) < 13.0]
        return max(cs, key=lambda c: g(c, 'delta') / (g(c, 'phi') + g(c, 'psi') + 0.05 * g(c, 'y') + 1e-9))['l']


def track(md, p):
    allm = {m: modes_at(md, p, m) for m in SPEEDS_MPH}
    res = {float(m): {} for m in SPEEDS_MPH}
    for mode, s0 in dict(weave=100.0, wobble=65.0).items():
        l0 = seed(allm[s0], mode)
        res[s0][mode] = l0
        for direction in (1, -1):
            prev = l0; prevprev = None
            ks = [k for k in SPEEDS_MPH if (k > s0 if direction > 0 else k < s0)]
            ks = ks if direction > 0 else ks[::-1]
            for k in ks:
                pred = prev if prevprev is None else 2 * prev - prevprev
                best = min((c['l'] for c in allm[k]), key=lambda z: abs(z - pred) / (1 + 0.05 * abs(pred)))
                prevprev, prev = prev, best
                res[float(k)][mode] = best
    for m in SPEEDS_MPH:
        d = res[float(m)]
        real = [c for c in allm[m] if abs(c['l'].imag) <= 1e-6 and abs(c['l']) < 6.0]
        if real:
            d['capsize'] = min(real, key=lambda c: abs(c['l']))['l']
        osc = [c for c in allm[m] if abs(c['l'].imag) > 1e-6 and 0.3 < abs(c['l'].imag) / 2 / math.pi < 100.0]   # above 100 Hz the model has no tyre or material damping and means little
        # all the other oscillatory modes (flex modes, low-speed weave): the weakest damping among them
        used = [d.get('weave'), d.get('wobble')]
        others = [c for c in osc if all(abs(c['l'] - u) > 1e-3 for u in used if u is not None)]
        if others:
            w = min(others, key=lambda c: -c['l'].real / abs(c['l']))
            dom = max(w['x'], key=w['x'].get)
            d['other'] = w['l']; d['other_dom'] = dom
        d['max_real_osc'] = max([c['l'].real for c in osc], default=-1.0)
        d['max_real_all'] = max(c['l'].real for c in allm[m])
        low = [c['l'] for c in osc if abs(c['l'].imag) / 2 / math.pi < 1.5]
        d['lowspeed_weave'] = max(low, key=lambda z: z.real) if low else None
    return res


def to_rows(tr):
    rows = []
    for k, d in tr.items():
        r = dict(mph=k, max_real_osc=d['max_real_osc'], max_real_all=d['max_real_all'])
        for m in ('weave', 'wobble', 'capsize', 'other', 'lowspeed_weave'):
            l = d.get(m)
            if l is not None:
                r[m] = dict(re=l.real, im=abs(l.imag), f_hz=abs(l.imag) / 2 / math.pi, zeta=-l.real / abs(l))
        if 'other_dom' in d:
            r['other']['dominant'] = d['other_dom']
        rows.append(r)
    return rows


MPH_MIN = dict(weave=25.0, wobble=15.0, other=15.0)    # weave and capsize are unstable below about 20-25 mph on every motorcycle (rider's job)


def summary(rows, mph_min=15.0):
    s = {}
    for m in ('weave', 'wobble', 'other'):
        v = [(r[m]['zeta'], r['mph'], r[m]['f_hz'], r[m].get('dominant')) for r in rows if m in r and r['mph'] >= MPH_MIN[m]]
        if not v:
            continue
        zmin = min(v)
        s[m] = dict(min_zeta=zmin[0], at_mph=zmin[1], f_at_min=zmin[2], dominant=zmin[3],
                    unstable_mph=[r['mph'] for r in rows if m in r and r[m]['re'] > 0 and r['mph'] >= MPH_MIN[m]],
                    f_range=[min(x[2] for x in v), max(x[2] for x in v)])
    caps = [(r['capsize']['re'], r['mph']) for r in rows if 'capsize' in r]
    s['capsize'] = dict(max_re=max(caps)[0] if caps else None, unstable_mph=[k for re, k in caps if re > 0],
                        re_at_130=caps[-1][0] if caps else None, doubling_time_s_at_130=(math.log(2) / caps[-1][0]) if caps and caps[-1][0] > 0 else None)
    lw = [(r['mph'], r['lowspeed_weave']['re']) for r in rows if 'lowspeed_weave' in r]
    s['lowspeed_oscillation_unstable_up_to_mph'] = max([k for k, re in lw if re > 0], default=None)
    s['all_osc_stable_from_mph'] = None
    for r in rows:   # lowest speed above which every oscillatory mode is stable up to 130 mph
        if all(rr['max_real_osc'] < 0 for rr in rows if rr['mph'] >= r['mph']):
            s['all_osc_stable_from_mph'] = r['mph']; break
    s['max_real_osc_over_15_130'] = max(r['max_real_osc'] for r in rows if r['mph'] >= mph_min)
    return s


_CACHE = {}


def get_model(p, key):
    if key not in _CACHE:
        _CACHE[key] = dm.Model(p)
    md = _CACHE[key]; md.p = p
    return md


def run(p, label, key=None, md=None):
    md = md or (get_model(p, key) if key else dm.Model(p))
    rows = to_rows(track(md, p))
    return dict(label=label, rows=rows, summary=summary(rows))


def fmt(s):
    o = []
    for m in ('weave', 'wobble', 'other'):
        if m in s:
            u = s[m]['unstable_mph']
            o.append(f"{m} zmin {s[m]['min_zeta']:+.3f}@{s[m]['at_mph']:.0f}mph({s[m]['f_at_min']:.1f}Hz)" + (f" UNSTABLE {u[0]:.0f}-{u[-1]:.0f}" if u else ''))
    c = s['capsize']
    o.append(f"capsize re130 {c['re_at_130']:+.2f}" if c['re_at_130'] is not None else '')
    return ' | '.join(o)


def plot(sws, fname, title, modes=('weave', 'wobble')):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for sw in sws:
        for m, ls in zip(modes, ('-', '--')):
            xs = [r['mph'] for r in sw['rows'] if m in r]
            ax[0].plot(xs, [r[m]['zeta'] for r in sw['rows'] if m in r], ls, label=f"{m}: {sw['label']}")
            ax[1].plot(xs, [r[m]['f_hz'] for r in sw['rows'] if m in r], ls, label=f"{m}: {sw['label']}")
    ax[0].axhline(0, color='k', lw=0.8); ax[0].axhline(0.05, color='r', lw=0.6, ls=':')
    ax[0].set_xlabel('speed, mph'); ax[0].set_ylabel('damping ratio (below 0 = unstable)'); ax[0].set_ylim(-0.2, 0.6)
    ax[1].set_xlabel('speed, mph'); ax[1].set_ylabel('frequency, Hz')
    ax[0].legend(fontsize=6); ax[0].set_title(title); ax[0].grid(alpha=.3); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=110); plt.close(fig)


if __name__ == '__main__':
    results = dict(inputs=dict(K_FRAME_Nm_per_rad=K_FRAME, K_FRAME_from_torsion_fea=K_FRAME_TORSION_FEA, K_FORK=K_FORK, EI_swingarm=EI_SA,
                               L_arm_m=L_ARM, yaw_stiffness_check_EI_over_L=EI_SA / L_ARM, K_SA_TORS=K_SA_TORS, tyre_front=TYRE_F, tyre_rear=TYRE_R,
                               trail_m=GEO['trail_mm'] / 1000, wheelbase_m=WB))
    sw = {}

    def go(key, case, label, **kw):
        p = params(case, **{k: v for k, v in kw.items() if k in ('frame', 'fork', 'rear', 'k_frame', 'k_fork', 'c_steer', 'tyre_scale')})
        sw[key] = run(p, label, key=(case, kw.get('frame', True), kw.get('fork', True), kw.get('rear', True)))
        sw[key]['case'] = case
        print(f'{key:38s} {fmt(sw[key]["summary"])}', flush=True)
        return p

    for case in CASES:
        p = go(f'{case} flex', case, f'{case}, frame+fork+swingarm flex')
        results[f'steer_inertia_{case}_kgm2'] = steer_inertia(p)
        results[f'fz_{case}'] = dict(FzF=p['F']['Fz'], FzR=p['R']['Fz'])
        go(f'{case} rigid', case, f'{case}, rigid', frame=False, fork=False, rear=False)
    # sensitivities on the loaded solo case (the case the rider has most often), then the other two where it matters
    for case in ('solo', 'solo_luggage'):
        go(f'{case} frame torsion FEA', case, f'{case}, frame k from 4.4 kNm/deg torsion', k_frame=K_FRAME_TORSION_FEA)
        go(f'{case} frame 120k', case, f'{case}, frame 120 kNm/rad', k_frame=120e3)
        go(f'{case} fork 20k', case, f'{case}, fork 20 kNm/rad', k_fork=20e3)
        go(f'{case} fork 40k', case, f'{case}, fork 40 kNm/rad (spec)', k_fork=40e3)
        go(f'{case} no swingarm flex', case, f'{case}, rigid swingarm', rear=False)
        go(f'{case} Ka x0.7', case, f'{case}, tyre cornering stiffness x0.7', tyre_scale=dict(F=dict(Ka=0.7), R=dict(Ka=0.7)))
        go(f'{case} Ka x1.3', case, f'{case}, tyre cornering stiffness x1.3', tyre_scale=dict(F=dict(Ka=1.3), R=dict(Ka=1.3)))
        go(f'{case} sigma x1.5', case, f'{case}, relaxation length x1.5', tyre_scale=dict(F=dict(sigma=1.5), R=dict(sigma=1.5)))
        go(f'{case} sigma x0.5', case, f'{case}, relaxation length x0.5', tyre_scale=dict(F=dict(sigma=0.5), R=dict(sigma=0.5)))
        go(f'{case} rider hands 4', case, f'{case}, rider arms add 4 Nms/rad', c_steer=4.0)
    # fixed steering damper sweep (all cases), to find out whether one is needed and how much
    for case in CASES:
        for cs in (2.0, 4.0, 6.0, 10.0, 15.0):
            go(f'{case} damper {cs:g}', case, f'{case}, steering damper {cs:g} Nms/rad', c_steer=cs)
    results['runs'] = sw
    (OUT / 'stability-results.json').write_text(json.dumps(results, indent=1, default=lambda o: str(o)))
    plot([sw[f'{c} flex'] for c in CASES], 'stability-baseline.png', 'Rev D, frame + fork + swingarm flex, no damper (hands off)')
    plot([sw['solo rigid'], sw['solo flex'], sw['solo no swingarm flex']], 'stability-flex-effect.png', 'Effect of compliance (bike + rider)')
    plot([sw['solo frame 120k'], sw['solo frame torsion FEA'], sw['solo flex'], sw['solo fork 20k'], sw['solo fork 40k']], 'stability-stiffness.png',
         'Frame and fork stiffness sensitivity (bike + rider)')
    plot([sw[k] for k in ('solo flex', 'solo Ka x0.7', 'solo Ka x1.3', 'solo sigma x1.5', 'solo sigma x0.5')], 'stability-tyres.png', 'Tyre sensitivity (bike + rider)')
    # per-speed CSV of the headline run
    with open(OUT / 'stability-modes.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case', 'mph', 'weave_zeta', 'weave_hz', 'wobble_zeta', 'wobble_hz', 'capsize_re_1_per_s', 'weakest_other_zeta', 'weakest_other_hz', 'weakest_other_dominant', 'max_real_oscillatory'])
        for case in CASES:
            for r in sw[f'{case} flex']['rows']:
                g = lambda m, k: f"{r[m][k]:.4f}" if m in r else ''
                w.writerow([case, r['mph'], g('weave', 'zeta'), g('weave', 'f_hz'), g('wobble', 'zeta'), g('wobble', 'f_hz'), g('capsize', 're'),
                            g('other', 'zeta'), g('other', 'f_hz'), r.get('other', {}).get('dominant', ''), f"{r['max_real_osc']:.4f}"])
