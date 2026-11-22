"""V1 dynamics step 5: steady-state lean angle and cornering clearance from the rev D CAD.

Method (same as detailed-design/tools/dyn-lean.py): the bike rolls about the line through the tyre crown centres. A point (x, y, z)
on the leaning side touches the road when
    |y| sin(phi) = (z - drop(x) - rho(x)) cos(phi) + rho(x)
rho = tyre crown radius (front 65 mm, rear 90 mm: ESTIMATES for 110/80R19 and 150/70R17, swept 45-85), drop(x) = extra suspension +
tyre compression at the steady-turn load factor n = 1/cos(phi): front fork (coil + air spring) and rear shock (wheel rate), linear in x
between the axles for sprung parts, tyre part only for unsprung parts. Ride height with the rider on (and with luggage) is the CAD
position (the rear preload adjuster keeps it). Points: tessellation vertices of every CAD solid (dynamics-v1-extract.py).
The fork spring is re-fitted to the rev D loads with the sweep of dyn-suspension.py (30% sag, preload <= 35 mm, >= 15 mm left in a
0.94 g stop, >= 40 mm left at 45 deg lean).

Outputs: program/data/dynamics/lean-results.json, suspension-results.json, lean-clearance.csv.
Run from v1.0 with the FreeCAD python. November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import csv, json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'data' / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())
CAD = json.loads((OUT / 'cad-extract.json').read_text())
ROLL = json.loads((OUT / 'run' / 'mass-rollup-snapshot.json').read_text())
g = 9.81; WB = MP['geometry']['wheelbase_mm'] / 1000; EPS = math.radians(25)
TRAVEL_F = 170.0; TRAVEL_R = 170.0
LR, K_REAR_SPRING = 2.33, 109.0                      # rear-suspension.md (leverage at sag, spring N/mm): rev D shock is unchanged
KT_F, KT_R = 175.0, 210.0                            # N/mm tyre radial stiffness (typical radial values; estimates)
A_AIR = math.pi / 4 * 0.040 ** 2; GAMMA = 1.3
UNSPRUNG_F, UNSPRUNG_R = ROLL['unsprung_kg']['front'], ROLL['unsprung_kg']['rear']
RHO_F, RHO_R = 65.0, 90.0
EXCLUDE = ('_tire', '_wheel_STUDY', 'Front_disc', 'Rear_disc', 'Front_pulley')    # wheels, discs: not the clearance question
FRONT_UNSPRUNG = ('Fork_inner', 'Fork_axle_clamp', 'Front_caliper', 'Front_fender', 'Fork_reflector', 'Front_brake_hose_caliper', 'Front_caliper_banjo')
REAR_UNSPRUNG = ('Swingarm', 'Rear_caliper', 'Rear_hugger', 'Rear_brake_hose', 'Shock_Lower', 'Rear_pulley', 'Drive_belt', 'Rear_disc')
SOFT = ('Peg_rubber', 'Peg_reference', 'Crash_guard_slider', 'Pivot_slider', 'Peg_bracket', 'Side_stand')   # feelers / sliders: meant to touch first or be sacrificial


def axle_loads(case, ax=0.0):
    c = MP[case]['total']; m = c['m']; x, h = c['c'][0], c['c'][2]
    Nf = m * g * x / WB - m * ax * h / WB
    return Nf, m * g - Nf


def fork_force(x_mm, k_leg, preload, air_gap):
    return 2 * k_leg * (preload + x_mm) + 2 * 101325 * A_AIR * ((air_gap / max(air_gap - x_mm, 1.0)) ** GAMMA - 1)


def fork_x(F, k_leg, preload, air_gap):
    if fork_force(0, k_leg, preload, air_gap) >= F:
        return 0.0
    lo, hi = 0.0, TRAVEL_F + 60
    for _ in range(60):
        m = (lo + hi) / 2
        if fork_force(m, k_leg, preload, air_gap) < F: lo = m
        else: hi = m
    return (lo + hi) / 2


def fork_axial(Nf, Fx=0.0):
    return Nf * math.cos(EPS) + Fx * math.sin(EPS)


def fork_rate(x, k_leg, preload, air_gap):
    return fork_force(x + 0.5, k_leg, preload, air_gap) - fork_force(x - 0.5, k_leg, preload, air_gap)


def fit_fork():
    Nf_s, _ = axle_loads('solo'); Nf_l, _ = axle_loads('solo_luggage')
    F_static = fork_axial(Nf_s - UNSPRUNG_F * g); F_static_l = fork_axial(Nf_l - UNSPRUNG_F * g)
    def brake(case, a):
        m = MP[case]['total']['m']; Nf, Nr = axle_loads(case, -a * g)
        return fork_axial(Nf - UNSPRUNG_F * g, m * a * g * min(1.0, Nf / (Nf + Nr) + 0.1))
    Fb_s, Fb_l = brake('solo', 0.94), brake('solo_luggage', 0.94)
    F_corner = F_static / math.cos(math.radians(45))
    ms_f = (Nf_s - UNSPRUNG_F * g) / g
    best = None
    kw = K_REAR_SPRING / LR ** 2
    ms_r = (axle_loads('solo')[1] - UNSPRUNG_R * g) / g
    f_rear = math.sqrt(1 / (1 / kw + 1 / KT_R) * 1000 / ms_r) / (2 * math.pi)
    for k_leg in np.arange(5.0, 14.01, 0.25):
        for air in np.arange(110.0, 260.1, 10.0):
            lo, hi = -50.0, 200.0
            for _ in range(50):
                pre = (lo + hi) / 2
                if fork_force(51.0, k_leg, pre, air) < F_static: lo = pre
                else: hi = pre
            pre = (lo + hi) / 2
            if pre < 0 or pre > 35:
                continue
            x_l = fork_x(F_static_l, k_leg, pre, air); x_bs = fork_x(Fb_s, k_leg, pre, air); x_bl = fork_x(Fb_l, k_leg, pre, air)
            x_c = fork_x(F_corner, k_leg, pre, air); k_ax = fork_rate(51.0, k_leg, pre, air)
            kv = k_ax / math.cos(EPS) ** 2; kr = 1 / (1 / kv + 1 / KT_F)
            f = math.sqrt(kr * 1000 / ms_f) / (2 * math.pi)
            ok = (TRAVEL_F - max(x_bs, x_bl)) >= 15 and (TRAVEL_F - x_c) >= 40 and x_l <= 0.40 * TRAVEL_F
            score = abs(f - f_rear) + (0 if ok else 10) + 0.002 * pre
            if best is None or score < best[0]:
                best = (score, dict(k_leg=float(k_leg), air_gap=float(air), preload=float(pre), sag_with_luggage=x_l, x_brake_solo=x_bs, x_brake_luggage=x_bl,
                                    x_corner45=x_c, ride_hz=f, ok=bool(ok)))
    fr = best[1]; fr['rear_ride_hz_solo'] = f_rear
    return fr


FR = fit_fork()


def drops(phi, case='solo'):
    n = 1 / math.cos(phi)
    Nf, Nr = axle_loads(case)
    Fs = fork_axial(Nf - UNSPRUNG_F * g)
    xs = fork_x(Fs, FR['k_leg'], FR['preload'], FR['air_gap']); xn = fork_x(Fs * n, FR['k_leg'], FR['preload'], FR['air_gap'])
    tf = (n - 1) * Nf / KT_F
    df = (xn - xs) * math.cos(EPS) + tf
    sr = Nr - UNSPRUNG_R * g
    dr_s = min((n - 1) * sr / (K_REAR_SPRING / LR ** 2), TRAVEL_R - 51.0)
    tr = (n - 1) * Nr / KT_R
    return df, dr_s + tr, tf, tr, dr_s


def touch_angle(pts, side, case, loaded, rho_f=RHO_F, rho_r=RHO_R):
    pts = pts[pts[:, 1] * side > 0]
    if len(pts) == 0:
        return None
    x = pts[:, 0]; y = np.abs(pts[:, 1]); z = pts[:, 2]; kind = pts[:, 3]
    rho = rho_r + (rho_f - rho_r) * np.clip(x / (WB * 1000), 0, 1)
    for deg in np.arange(25.0, 75.0, 0.05):
        phi = math.radians(deg)
        df, dr, tf, tr, dr_s = drops(phi, case) if loaded else (0.0, 0.0, 0.0, 0.0, 0.0)
        sprung = dr + (df - dr) * np.clip(x / (WB * 1000), 0, 1)
        sa = tr + dr_s * np.clip((540 - x) / 540, 0, 1)
        d = np.where(kind == 0, sprung, np.where(kind == 1, tf, sa))
        gg = y * math.sin(phi) - ((z - d - rho) * math.cos(phi) + rho)
        if np.any(gg >= 0):
            i = int(np.argmax(gg)); return deg, pts[i]
    return None


def group_of(name):
    return 'soft' if name.startswith(SOFT) else 'hard'


if __name__ == '__main__':
    res = dict(fork=FR, unsprung_kg=dict(front=UNSPRUNG_F, rear=UNSPRUNG_R), crown_mm=dict(front=RHO_F, rear=RHO_R))
    print('fork fit', FR)
    allpts = []; owner = []
    for name, rec in CAD.items():
        if any(e in name for e in EXCLUDE) or 'lean_points' not in rec:
            continue
        kind = 1 if name.startswith(FRONT_UNSPRUNG) else (2 if name.startswith(REAR_UNSPRUNG) else 0)
        for p in rec['lean_points']:
            allpts.append((p[0], p[1], p[2], kind)); owner.append(name)
    allpts = np.array(allpts); own = np.array(owner); names = sorted(set(owner))
    print(len(allpts), 'points,', len(names), 'parts')

    def per_part(case, loaded, side, **kw):
        out = []
        for nm in names:
            r = touch_angle(allpts[own == nm], side, case, loaded, **kw)
            if r:
                out.append((round(float(r[0]), 2), nm, group_of(nm), [round(float(v)) for v in r[1][:3]]))
        out.sort()
        return out

    rows_csv = []
    for case in ('solo', 'solo_luggage'):
        for loaded in (False, True):
            key = f"{case}_{'turn' if loaded else 'static'}"
            res[key] = {}
            for side, sname in ((1, 'left'), (-1, 'right')):
                per = per_part(case, loaded, side)
                res[key][sname] = per[:10]
                hard = [p for p in per if p[2] == 'hard']; soft = [p for p in per if p[2] == 'soft']
                res[key][sname + '_first_hard'] = hard[0] if hard else None
                res[key][sname + '_first_soft'] = soft[0] if soft else None
                for p in per[:12]:
                    rows_csv.append([case, 'loaded steady turn' if loaded else 'upright geometry', sname, p[0], p[1], p[2], p[3][0], p[3][1], p[3][2]])
            print(key, 'L first hard', res[key]['left_first_hard'], 'soft', res[key]['left_first_soft'], '\n         R first hard', res[key]['right_first_hard'], 'soft', res[key]['right_first_soft'])
    # crown-radius sensitivity of the first hard part, loaded solo, both sides
    res['crown_sensitivity'] = {}
    for rf, rr in ((45.0, 60.0), (65.0, 90.0), (85.0, 110.0)):
        out = {}
        for side, sname in ((1, 'left'), (-1, 'right')):
            per = per_part('solo', True, side, rho_f=rf, rho_r=rr)
            hard = [p for p in per if p[2] == 'hard']; out[sname] = hard[0][:2] if hard else None
        res['crown_sensitivity'][f'{rf:.0f}/{rr:.0f}'] = out
    print('crown sensitivity', res['crown_sensitivity'])
    res['grip_lean_deg'] = {f'mu {mu}': math.degrees(math.atan(mu)) for mu in (0.8, 1.05, 1.2)}
    df, dr, tf, tr, drs = drops(math.radians(45))
    res['drop_at_45deg_mm_solo'] = dict(front_vertical=df, rear_vertical=dr, front_tyre=tf, rear_tyre=tr)
    (OUT / 'lean-results.json').write_text(json.dumps(res, indent=1))
    (OUT / 'suspension-results.json').write_text(json.dumps(dict(fork=FR, unsprung=res['unsprung_kg'], rear_wheel_rate_N_mm=K_REAR_SPRING / LR ** 2), indent=1))
    with open(OUT / 'lean-clearance.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['load', 'condition', 'side', 'touch_deg', 'part', 'class', 'x_mm', 'y_mm', 'z_mm']); w.writerows(rows_csv)
