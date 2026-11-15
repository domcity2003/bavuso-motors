"""Bavuso V1.0 lean (ground) clearance from the CAD, static and in a steady turn with the suspension compressed.

Method: the bike rolls about the line through the tyre crown centres (crown radius 60 mm front, 80 mm rear,
about half the section widths). A point (x, y, z) on the side the bike leans to touches the road when
  |y| sin(phi) = (z - drop(x) - rho(x)) cos(phi) + rho(x)
drop(x) is the extra suspension and tyre compression at load factor n = 1/cos(phi) (steady turn), linear in x
between the axles for sprung parts; unsprung parts take only the tyre part (swingarm parts pro rata to the pivot).
Points: tessellation vertices of every visible solid (dyn-cad-extract.py), saved model, ground at Z = 0.

Run from v1.0 with the FreeCAD python. Output: detailed-design/dynamics/lean-results.json
Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import json, math, importlib.util
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; OUT = HERE.parents[0] / 'dynamics'
spec = importlib.util.spec_from_file_location('susp', HERE / 'dyn-suspension.py'); su = importlib.util.module_from_spec(spec); spec.loader.exec_module(su)
cad = json.loads((OUT / 'cad-extract.json').read_text())
sres = json.loads((OUT / 'suspension-results.json').read_text())
fr = sres['front_optimum']; rr = sres['rear']
RHO_F, RHO_R, WB = 60.0, 80.0, 1486.8
EXCLUDE = ('_tire', '_wheel_STUDY', 'Front_disc', 'Rear_disc', 'Rear_pulley', 'Drive_belt', 'Front_pulley')
FRONT_UNSPRUNG = ('Fork_inner', 'Fork_axle_clamp', 'Front_caliper', 'Front_fender', 'Fork_reflector', 'Front_brake_hose_caliper', 'Front_caliper_banjo')
REAR_UNSPRUNG = ('Swingarm', 'Rear_caliper', 'Rear_hugger', 'Rear_brake_hose', 'Shock_Lower', 'Swingarm_shock_tower', 'Swingarm_cross_brace')


def drops(phi, case='solo'):
    n = 1 / math.cos(phi)
    Nf, Nr = su.axle_loads(case)
    # front: fork axial compression beyond static, vertical component, + tyre
    Fs = su.fork_axial_load(Nf - su.UNSPRUNG_F * su.g)
    xs = su.fork_x(Fs, fr['k_leg'], fr['preload'], fr['air_gap']); xn = su.fork_x(Fs * n, fr['k_leg'], fr['preload'], fr['air_gap'])
    tf = (n - 1) * Nf / su.KT_F
    df = (xn - xs) * math.cos(su.EPS) + tf
    # rear: wheel rate, capped at the travel left; + tyre
    sr = (Nr - su.UNSPRUNG_R * su.g)
    dr_s = min((n - 1) * sr / rr['solo']['wheel_rate'], su.TRAVEL_R - 51.0)
    tr = (n - 1) * Nr / su.KT_R
    return df, dr_s + tr, tf, tr, dr_s


def touch_angle(points, side, case='solo', loaded=True):
    pts = np.array([p for p in points if p[1] * side > 0])
    if len(pts) == 0:
        return None
    for deg in np.arange(25.0, 70.0, 0.05):
        phi = math.radians(deg)
        if loaded:
            df, dr, tf, tr, dr_s = drops(phi, case)
        else:
            df = dr = tf = tr = dr_s = 0.0
        x = pts[:, 0]; y = np.abs(pts[:, 1]); z = pts[:, 2]; kind = pts[:, 3]
        rho = RHO_R + (RHO_F - RHO_R) * np.clip(x / WB, 0, 1)
        sprung_drop = dr + (df - dr) * np.clip(x / WB, 0, 1)
        unsp_f = tf
        sa = tr + dr_s * np.clip((540 - x) / 540, 0, 1)
        d = np.where(kind == 0, sprung_drop, np.where(kind == 1, unsp_f, sa))
        g = y * math.sin(phi) - ((z - d - rho) * math.cos(phi) + rho)
        if np.any(g >= 0):
            i = int(np.argmax(g)); return deg, i, pts[i]
    return None


if __name__ == '__main__':
    res = {}
    allpts = []; owner = []
    for name, rec in cad.items():
        if any(e in name for e in EXCLUDE) or 'lean_points' not in rec:
            continue
        kind = 1 if name.startswith(FRONT_UNSPRUNG) else (2 if name.startswith(REAR_UNSPRUNG) else 0)
        for p in rec['lean_points']:
            allpts.append((p[0], p[1], p[2], kind)); owner.append(name)
    allpts = np.array(allpts)
    # per-part angles (so we can list the order in which things touch)
    for case in ('solo', 'twoup'):
        for loaded in (False, True):
            key = f"{case}_{'turn' if loaded else 'static'}"
            res[key] = {}
            for side, sname in ((1, 'left'), (-1, 'right')):
                per = []
                names = sorted(set(owner))
                own = np.array(owner)
                for nm in names:
                    sel = allpts[own == nm]
                    r = touch_angle(sel, side, case, loaded)
                    if r: per.append((round(r[0], 1), nm, [round(float(v), 0) for v in r[2][:3]]))
                per.sort()
                res[key][sname] = per[:8]
            print(key, 'L', res[key]['left'][:4], '\n      R', res[key]['right'][:4])
    df, dr, tf, tr, drs = drops(math.radians(45))
    res['drop_at_45deg_mm'] = dict(front_vertical=df, rear_vertical=dr, front_tyre=tf, rear_tyre=tr)
    print('drops at 45 deg', res['drop_at_45deg_mm'])
    (OUT / 'lean-results.json').write_text(json.dumps(res, indent=1))
