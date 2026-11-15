"""Bavuso V1.0 linear stability: capsize, weave, wobble vs speed (5-200 km/h), solo and two-up loaded,
with sweeps of frame/fork twist stiffness, steering damper, tyre properties, steering inertia and trail.

Inputs: detailed-design/dynamics/mass-properties.json (dyn-massprops.py). Geometry: steering-axis point X1206.954 /
Z840 above ground and 25 deg caster from tools/build-adventure.py; tyres per the Nov 13 supplier audit
(120/70R19 663 mm OD -> R 331.5 mm, 170/60R17 650 mm OD -> R 325 mm), which moves the front axle to a wheelbase
of 1483.9 mm and trail 114.7 mm with the 36.1 mm fork offset. Model: dyn-model.py (validated against the
Meijaard 2007 benchmark by dyn-validate.py). Outputs: detailed-design/dynamics/stability-*.json / *.png.

Modes are tracked by continuation in speed (nearest eigenvalue step to step) from seeds where they are
unambiguous: weave at 160 km/h (2-5 Hz, roll/yaw rich), wobble at 100 km/h (steer rich, 4-12 Hz),
twist at 60 km/h (15-30 Hz). Capsize = the slow real roll/heading root.

Run from v1.0 with the FreeCAD python. Prepared November 12-13, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import importlib.util, json, math, copy
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dynmodel', HERE / 'dyn-model.py'); dm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
OUT = HERE.parents[0] / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())

CASTER = math.radians(25.0)
S_PT = [1.206954, 0.0, 0.840]
FORK_OFF = 0.0361
RF, RR = 0.3315, 0.325          # supplier audit tyres (free radius; loaded radius ~5-8 mm less, ignored)
X_INT = S_PT[0] + S_PT[2] * math.tan(CASTER)          # steering axis meets the ground


def front_axle_x(rf=RF, off=FORK_OFF):
    # axle on the fork line: offset `off` ahead of the steering axis, at height rf
    w = (rf - S_PT[2] - math.sin(CASTER) * off) / math.cos(CASTER)
    return S_PT[0] + math.cos(CASTER) * off - math.sin(CASTER) * w


WB = front_axle_x()
TRAIL = X_INT - WB
# Tyres (normalised by vertical load). Sources and ranges in dynamics-study.md.
TYRE_F = dict(Ka=13.0, Kg=0.90, Ma=0.33, Mg=0.010, sigma=0.20, rho=0.060)
TYRE_R = dict(Ka=11.0, Kg=0.85, Ma=0.33, Mg=0.010, sigma=0.25, rho=0.085)
# Lumped twist at the steering head: fork lateral bending ~30 kNm/rad (Taraborrelli thesis: enduro fork 28,
# sport fork 35) in series with frame torsion ASSUMED 60 kNm/rad (Taraborrelli frames 51-129; FEA agent pending).
K_FORK, K_FRAME = 30e3, 60e3
K_TWIST = 1 / (1 / K_FORK + 1 / K_FRAME)
C_TWIST = 30.0
K_FORK_ONLY = 25e3   # fork-only bending model: lateral twist stiffness about the lower clamp (Taraborrelli 15-22 kNm/rad, 48 mm USD ADV fork assumed stiffer)
AERO_DFZ_100 = 80.0      # N moved front->rear at 100 km/h (aero-baseline-report.md), ~v^2
SPEEDS = np.arange(5.0, 200.1, 2.5)


def sched(c_low=20.0, c_high=5.0, v1=90.0, v2=140.0):
    """Semi-active steering damper: c_low (Nms/rad) up to v1 km/h, linear to c_high at v2 and above."""
    def f(v):
        k = v * 3.6
        return c_low if k <= v1 else (c_high if k >= v2 else c_low + (c_high - c_low) * (k - v1) / (v2 - v1))
    return f


def sym(I):
    I = np.array(I); I[0, 1] = I[1, 0] = I[1, 2] = I[2, 1] = 0.0
    return I.tolist()


def params(load='solo', d_off=0.0, k_twist=K_TWIST, c_steer=0.0, fork_mode=False):
    """d_off: change of fork offset (m, + = more offset = less trail). The front wheel and 60% of the front
    frame (fork legs, calipers) move with it."""
    mp = MP[load]
    B = mp['rear_frame']; H = mp['front_frame']; Fw = mp['front_wheel']; Rw = mp['rear_wheel']
    xf = front_axle_x(RF, FORK_OFF + d_off)
    dx = xf - MP['solo']['front_wheel']['c'][0]       # vs the roll-up position
    hc = list(H['c']); hc[0] += 0.6 * (xf - WB)
    mt = mp['total']['m']
    xg = (mt * mp['total']['c'][0] + Fw['m'] * dx + 0.6 * H['m'] * (xf - WB)) / mt
    FzF = mt * dm.G0 * xg / xf; FzR = mt * dm.G0 - FzF
    p = dict(caster=CASTER, S=S_PT,
             B=dict(m=B['m'], c=[B['c'][0], 0, B['c'][2]], I=sym(B['I'])),
             H=dict(m=H['m'], c=[hc[0], 0, hc[2]], I=sym(H['I'])),
             R=dict(m=Rw['m'], centre=[0, 0, RR], R=RR, Ixx=Rw['I'][0][0], Iyy=Rw['I'][1][1], Fz=FzR, **TYRE_R),
             F=dict(m=Fw['m'], centre=[xf, 0, RF], R=RF, Ixx=Fw['I'][0][0], Iyy=Fw['I'][1][1], Fz=FzF, **TYRE_F),
             k_twist=k_twist, c_twist=C_TWIST, c_steer=c_steer,
             rotor=(mp['rotor_gyro']['J'], mp['rotor_gyro']['ratio']),
             trail=X_INT - xf, wheelbase=xf, xg=xg, m=mt)
    if fork_mode:   # split the steered body: upper (clamps, bars, dash) and lower legs that bend with the wheel
        U = mp['front_upper']; L = mp['front_lower']
        lc = list(L['c']); lc[0] += (xf - WB)
        p.update(twist_mode='fork', k_twist=K_FORK_ONLY,
                 H=dict(m=U['m'], c=[U['c'][0], 0, U['c'][2]], I=sym(U['I'])),
                 L=dict(m=L['m'], c=[lc[0], 0, lc[2]], I=sym(L['I'])))
    return p


def steer_inertia(p):
    """Inertia of the steered assembly about the steering axis (front frame + front wheel), kg m2."""
    s = np.array([-math.sin(CASTER), 0, math.cos(CASTER)]); S = np.array(S_PT)
    tot = 0.0
    for key in ('H', 'F'):
        b = p[key]
        if key == 'H':
            I = np.array(b['I']); c = np.array(b['c'])
        else:
            I = np.diag([b['Ixx'], b['Iyy'], b['Ixx']]); c = np.array(b['centre'])
        d = c - S; dp = d - np.dot(d, s) * s
        tot += s @ I @ s + b['m'] * np.dot(dp, dp)
    return tot


def fz_at(p, kmh):
    d = AERO_DFZ_100 * (kmh / 100.0) ** 2
    return (p['R']['Fz'] + d, p['F']['Fz'] - d)


def modes_at(md, p, kmh):
    lam, X = md.eig(kmh / 3.6, fz_at(p, kmh))
    n = md.n; nm = md.names
    out = []
    for k, l in enumerate(lam):
        if np.imag(l) < -1e-9 or abs(l) < 1e-7:
            continue
        x = np.abs(X[:n, k])
        out.append(dict(l=complex(l), phi=x[nm.index('phi')], psi=x[nm.index('psi')], dl=x[nm.index('delta')],
                        bet=x[nm.index('beta')] if 'beta' in nm else 0.0, y=x[0]))
    return out


def seed(cands, mode):
    osc = [c for c in cands if abs(c['l'].imag) > 1e-6]
    f = lambda c: abs(c['l'].imag) / 2 / math.pi
    if mode == 'weave':
        cs = [c for c in osc if 1.5 < f(c) < 5.5]
        return max(cs, key=lambda c: (c['phi'] + c['psi']) / (c['dl'] + c['bet'] + 1e-9) * (1 if c['l'].real < 0 else 1) - 0.001 * abs(c['l'].real))['l']
    if mode == 'wobble':
        cs = [c for c in osc if 4.0 < f(c) < 13.0]
        return max(cs, key=lambda c: c['dl'] / (c['phi'] + c['psi'] + 0.05 * c['y'] + 1e-9))['l']
    if mode == 'twist':
        cs = [c for c in osc if 13.0 < f(c) < 40.0]
        return max(cs, key=lambda c: f(c))['l'] if cs else None


def track(md, p):
    """Return per-speed dict of tracked eigenvalues for weave, wobble, twist, plus capsize and max real part."""
    allm = {kmh: modes_at(md, p, kmh) for kmh in SPEEDS}
    res = {float(k): {} for k in SPEEDS}
    seeds = dict(weave=160.0, wobble=100.0, twist=60.0)
    for mode, s0 in seeds.items():
        if mode == 'twist' and 'beta' not in md.names:
            continue
        l0 = seed(allm[s0], mode)
        if l0 is None:
            continue
        res[s0][mode] = l0
        for direction in (1, -1):
            prev = l0; prevprev = None
            ks = [k for k in SPEEDS if (k > s0 if direction > 0 else k < s0)]
            ks = ks if direction > 0 else ks[::-1]
            for k in ks:
                pred = prev if prevprev is None else 2 * prev - prevprev
                cands = [c['l'] for c in allm[k]]
                best = min(cands, key=lambda z: abs(z - pred) / (1 + 0.05 * abs(pred)))
                prevprev, prev = prev, best
                res[float(k)][mode] = best
    for k in SPEEDS:
        real = [c for c in allm[k] if abs(c['l'].imag) <= 1e-6 and abs(c['l']) < 6.0]
        if real:
            res[float(k)]['capsize'] = min(real, key=lambda c: abs(c['l']))['l']
        lam = [c['l'] for c in allm[k]]
        res[float(k)]['max_real'] = max(z.real for z in lam)
        lowosc = [c['l'] for c in allm[k] if abs(c['l'].imag) > 1e-6 and abs(c['l'].imag) / 2 / math.pi < 1.5]
        res[float(k)]['lowspeed_weave'] = max(lowosc, key=lambda z: z.real) if lowosc else None
    return res


def to_rows(tr):
    rows = []
    for k, d in tr.items():
        r = dict(kmh=k, max_real=d['max_real'])
        for m in ('weave', 'wobble', 'twist', 'capsize', 'lowspeed_weave'):
            l = d.get(m)
            if l is not None:
                r[m] = dict(re=l.real, im=abs(l.imag), f_hz=abs(l.imag) / 2 / math.pi, zeta=-l.real / abs(l))
        rows.append(r)
    return rows


def summary(rows):
    s = {}
    for m in ('weave', 'wobble', 'twist'):
        v = [(r[m]['zeta'], r['kmh'], r[m]['f_hz']) for r in rows if m in r and r['kmh'] >= 20]
        if not v:
            continue
        zmin = min(v)
        s[m] = dict(min_zeta=zmin[0], at_kmh=zmin[1], f_at_min=zmin[2],
                    unstable_kmh=[r['kmh'] for r in rows if m in r and r[m]['re'] > 0 and r['kmh'] >= 20],
                    f_range=[min(x[2] for x in v), max(x[2] for x in v)])
    caps = [(r['capsize']['re'], r['kmh']) for r in rows if 'capsize' in r]
    s['capsize'] = dict(max_re=max(caps)[0] if caps else None, unstable_kmh=[k for re, k in caps if re > 0],
                        doubling_time_s_at_200=(math.log(2) / caps[-1][0]) if caps and caps[-1][0] > 0 else None)
    lw = [(r['kmh'], r['lowspeed_weave']['re']) for r in rows if 'lowspeed_weave' in r]
    s['lowspeed_unstable_below_kmh'] = max([k for k, re in lw if re > 0], default=None)
    return s


def run(md, p, label):
    rows = to_rows(track(md, p))
    return dict(label=label, rows=rows, summary=summary(rows))


def plot(sws, fname, title, modes=('weave', 'wobble')):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for sw in sws:
        for m, ls in zip(modes, ('-', '--')):
            xs = [r['kmh'] for r in sw['rows'] if m in r]
            ax[0].plot(xs, [r[m]['zeta'] for r in sw['rows'] if m in r], ls, label=f"{m}: {sw['label']}")
            ax[1].plot(xs, [r[m]['f_hz'] for r in sw['rows'] if m in r], ls, label=f"{m}: {sw['label']}")
    ax[0].axhline(0, color='k', lw=0.8); ax[0].axhline(0.05, color='r', lw=0.6, ls=':')
    ax[0].set_xlabel('speed, km/h'); ax[0].set_ylabel('damping ratio (below 0 = unstable)'); ax[0].set_ylim(-0.2, 0.6)
    ax[1].set_xlabel('speed, km/h'); ax[1].set_ylabel('frequency, Hz')
    ax[0].legend(fontsize=6); ax[0].set_title(title); ax[0].grid(alpha=.3); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=110); plt.close(fig)


def fmt(s):
    o = []
    for m in ('weave', 'wobble'):
        if m in s:
            u = s[m]['unstable_kmh']
            o.append(f"{m} zmin {s[m]['min_zeta']:+.3f}@{s[m]['at_kmh']:.0f} ({s[m]['f_at_min']:.1f}Hz)"
                     + (f" UNSTABLE {u[0]:.0f}-{u[-1]:.0f}" if u else ''))
    o.append(f"capsize maxRe {s['capsize']['max_re']:+.2f}" if s['capsize']['max_re'] is not None else '')
    o.append(f"low-speed unstable <= {s['lowspeed_unstable_below_kmh']}")
    return ' | '.join(o)


if __name__ == '__main__':
    builds = {}

    def get(load, d_off=0.0, fork=False):
        key = (load, d_off, fork)
        if key not in builds:
            p = params(load, d_off, fork_mode=fork)
            builds[key] = (dm.Model(p), p)
        md, p = builds[key]
        return md, copy.deepcopy(p)

    md, p = get('solo')
    results = dict(geometry=dict(trail_m=p['trail'], wheelbase_m=p['wheelbase'], FzF_solo=p['F']['Fz'], FzR_solo=p['R']['Fz'],
                                 steer_inertia_solo=steer_inertia(p), k_twist_baseline=K_TWIST, tyre_front=TYRE_F, tyre_rear=TYRE_R))
    print(json.dumps(results['geometry']))
    sw = {}

    def go(key, load, label, d_off=0.0, fork=False, **kw):
        md, p = get(load, d_off, fork)
        for k_, v_ in kw.items():
            if k_ in ('F', 'R'):
                for kk, fac in v_.items(): p[k_][kk] *= fac
            else:
                p[k_] = v_
        md.p = p
        sw[key] = run(md, p, label)
        print(f'{key:34s} {fmt(sw[key]["summary"])}', flush=True)

    # 1) baseline
    for load in ('solo', 'twoup'):
        go(f'{load} rigid', load, f'{load}, rigid frame', k_twist=1e9)
        go(f'{load} base', load, f'{load}, twist {K_TWIST/1e3:.0f} kNm/rad')
    # 2) frame stiffness (fork 30 kNm/rad in series)
    for kf in (20e3, 40e3, 120e3, 300e3):
        go(f'solo frame {kf/1e3:.0f}', 'solo', f'frame {kf/1e3:.0f} -> lumped {1/(1/K_FORK+1/kf)/1e3:.1f} kNm/rad', k_twist=1 / (1 / K_FORK + 1 / kf))
    go('solo fork 45 frame 60', 'solo', 'fork 45 + frame 60 -> 25.7', k_twist=1 / (1 / 45e3 + 1 / 60e3))
    go('solo fork 45 frame 120', 'solo', 'fork 45 + frame 120 -> 32.7', k_twist=1 / (1 / 45e3 + 1 / 120e3))
    # 3) total steering damping (damper + head bearing + rider arms)
    for cs in (3.0, 6.0, 10.0, 15.0, 20.0):
        for load in ('solo', 'twoup'):
            go(f'{load} damper {cs:g}', load, f'{load}, steering damping {cs:g} Nms/rad', c_steer=cs)
    # 4) tyres
    go('solo Ka x0.7', 'solo', 'cornering stiffness x0.7', F={'Ka': 0.7}, R={'Ka': 0.7})
    go('solo Ka x1.3', 'solo', 'cornering stiffness x1.3', F={'Ka': 1.3}, R={'Ka': 1.3})
    go('solo sigma x0.5', 'solo', 'relaxation length x0.5', F={'sigma': 0.5}, R={'sigma': 0.5})
    go('solo sigma x1.5', 'solo', 'relaxation length x1.5', F={'sigma': 1.5}, R={'sigma': 1.5})
    go('solo Kg x0.8', 'solo', 'camber stiffness x0.8', F={'Kg': 0.8}, R={'Kg': 0.8})
    # 5) steering inertia: TFT and mirrors on the fairing
    for load in ('solo_fm', 'twoup_fm'):
        go(f'{load} base', load, f'{load}: dash+mirrors on fairing')
        go(f'{load} damper 6', load, f'{load}: dash+mirrors on fairing, damping 6', c_steer=6.0)
        go(f'{load} damper 10', load, f'{load}: dash+mirrors on fairing, damping 10', c_steer=10.0)
    results['steer_inertia_fm'] = steer_inertia(get('solo_fm')[1])
    # 6) trail via fork offset
    for d in (-0.010, 0.010, 0.020):
        for load in ('solo', 'twoup'):
            md, p = get(load, d)
            go(f'{load} trail {p["trail"]*1000:.0f}', load, f'{load}, trail {p["trail"]*1000:.0f} mm', d_off=d)
            go(f'{load} trail {p["trail"]*1000:.0f} damper 6', load, f'{load}, trail {p["trail"]*1000:.0f} mm, damping 6', d_off=d, c_steer=6.0)
    # 7) fork-only lateral bending model (frame rigid): the other bound
    go('solo forkflex rigidcheck', 'solo', 'fork model, k=1e9 (must equal rigid)', fork=True, k_twist=1e9)
    for load in ('solo', 'twoup'):
        for kfk in (15e3, 25e3, 40e3):
            go(f'{load} forkflex {kfk/1e3:.0f}', load, f'{load}, fork bending {kfk/1e3:.0f} kNm/rad', fork=True, k_twist=kfk)
        for cs in (3.0, 6.0, 10.0):
            go(f'{load} forkflex 25 damper {cs:g}', load, f'{load}, fork 25, damping {cs:g}', fork=True, c_steer=cs)
        for cs in (15.0, 20.0, 25.0):
            go(f'{load} forkflex 25 damper {cs:g}', load, f'{load}, fork 25, damping {cs:g}', fork=True, c_steer=cs)
            go(f'{load} damper {cs:g}x', load, f'{load}, lumped, damping {cs:g}', c_steer=cs)
        go(f'{load} forkflex 25 semiactive', load, f'{load}, fork 25, semi-active 22->5', fork=True, c_steer=sched(22.0, 5.0))
        go(f'{load} lumped semiactive', load, f'{load}, lumped 20, semi-active 22->5', c_steer=sched(22.0, 5.0))
        go(f'{load} rigid semiactive', load, f'{load}, rigid, semi-active 22->5', k_twist=1e9, c_steer=sched(22.0, 5.0))
        go(f'{load}_fm forkflex 25 damper 6', load + '_fm', f'{load} fm, fork 25, damping 6', fork=True, c_steer=6.0)
    results['runs'] = sw
    (OUT / 'stability-results.json').write_text(json.dumps(results, indent=1, default=lambda o: str(o)))
    plot([sw['solo rigid'], sw['solo base'], sw['twoup base']], 'stability-baseline.png', 'Baseline, no steering damping')
    plot([sw[k] for k in ('solo damper 3', 'solo damper 6', 'solo damper 10', 'twoup damper 6', 'twoup damper 10')], 'stability-damper.png', 'Steering damping')
    plot([sw[k] for k in ('solo frame 20', 'solo frame 40', 'solo base', 'solo frame 120', 'solo frame 300', 'solo rigid')], 'stability-frame-stiffness.png',
         'Frame torsional stiffness (fork 30 kNm/rad in series)')
    plot([sw[k] for k in ('solo rigid', 'solo forkflex 40', 'solo forkflex 25', 'solo forkflex 15', 'solo base', 'solo forkflex 25 damper 6')],
         'stability-flex-models.png', 'Rigid vs fork-bending vs lumped head twist (solo)')
    plot([sw[k] for k in ('solo forkflex 25 semiactive', 'solo lumped semiactive', 'solo rigid semiactive', 'twoup forkflex 25 semiactive', 'twoup lumped semiactive')],
         'stability-semiactive.png', 'Semi-active steering damper 22 -> 5 Nms/rad (90-140 km/h)')
    print('steer inertia', results['geometry']['steer_inertia_solo'], '->', results['steer_inertia_fm'])
