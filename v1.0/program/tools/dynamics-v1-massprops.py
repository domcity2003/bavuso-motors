"""V1 dynamics step 2: mass properties of the rev D bike for three load cases, and the bodies for the stability model.

Inputs: the mass roll-up (snapshot of mass-rollup.csv taken when this study started, in program/data/dynamics/run/;
pass --live to re-read the live file) and the per-solid inertia shapes from dynamics-v1-extract.py. Each CAD part keeps its
own rotational inertia (CAD volume inertia scaled to its ledger mass); allowances with no solid are point masses.
Rider: 90 kg, 1,755 mm, from segment joints in rider-fit.json (Winter/Dempster segment masses). Luggage: 25 kg box.
Coordinates: saved CAD model (X forward from the rear axle, Y, Z up from ground), SI units in the output.

Outputs: program/data/dynamics/mass-properties.json (bodies per load case), mass-properties-summary.json and .csv.
Run from v1.0 with the FreeCAD python (numpy only). November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parents[2]
D = R / 'program' / 'data' / 'dynamics'
ROLL = (R / 'mass-rollup.csv') if '--live' in sys.argv else (D / 'run' / 'mass-rollup-snapshot.csv')
cad = json.loads((D / 'cad-extract.json').read_text())

FRONT_WHEEL = {'Front_nominal_tire', 'Front_wheel_STUDY', 'Front_disc_m1', 'Front_disc_p1',
               'Front_disc_carrier_m1', 'Front_disc_carrier_p1', 'Front axle spacers'}
REAR_WHEEL = {'Rear_nominal_tire', 'Rear_wheel_STUDY', 'Rear_pulley_PITCH_STUDY', 'Rear_disc_p1',
              'Rear_disc_carrier_p1', 'Rear axle, spacers, adjusters'}
STEER_PREFIX = ('Fork_', 'Lower_triple', 'Upper_triple', 'Bar_', 'Hand_grip', 'Hand_lever', 'Lever_perch', 'Switch_cube',
                'Front_master', 'Front_brake_reservoir', 'Front_caliper', 'Front_fender', 'Mirror_', 'Display_',
                'Harness_connector', 'Harness_bar', 'Front_brake_hose_caliper', 'Front_brake_splitter', 'Handguard')
LOWER_FORK = ('Fork_inner', 'Fork_axle_clamp', 'Front_caliper', 'Front_fender', 'Fork_reflector', 'Front_brake_hose_caliper')
HALF_STEER = ('Steering bearings', 'Front_brake_hose_upper', 'Steering_damper_envelope')   # half rides on the steered side

G_RIDER, M_RIDER = 1755.0, 90.0
LUGGAGE = dict(m=25.0, x=-100.0, z=880.0, dims=(0.45, 0.60, 0.35))    # rack-mounted bag/case: ASSUMED position
RATIO, ROTOR_J = 3.6, 0.0124     # EMRAX 228 rotor (est.) spinning 3.6x the wheel (06-drive-performance.md); belt does not reverse it


def box_I(m, a, b, c):
    return np.diag([m * (b * b + c * c) / 12, m * (a * a + c * c) / 12, m * (a * a + b * b) / 12])


def rod_I(m, p0, p1, r):
    """Solid circular rod from p0 to p1 (m), radius r, inertia about its centre in world axes."""
    d = np.array(p1, float) - np.array(p0, float); L = np.linalg.norm(d); u = d / L
    It = m * (L * L / 12 + r * r / 4); Ia = m * r * r / 2
    return It * np.eye(3) + (Ia - It) * np.outer(u, u)


def rider_parts(M=M_RIDER):
    j = json.loads((R / 'rider-fit.json').read_text())['joints']
    P = lambda side, k: np.array(j[side][k], float) / 1000.0
    mid = lambda k: (P('right', k) + P('left', k)) / 2
    parts = []

    def add(name, f, p0, p1, frac, r):
        m = M * f; pc = p0 + (p1 - p0) * frac
        parts.append(dict(name=name, m=m, p=pc, I=rod_I(m, p0, p1, r), body='rear_frame', src='rider'))
    hip, sh = mid('hip'), mid('shoulder')
    m_tr = M * 0.497; ptr = hip + (sh - hip) * 0.5
    parts.append(dict(name='rider_trunk', m=m_tr, p=ptr, I=box_I(m_tr, 0.22, 0.34, np.linalg.norm(sh - hip)), body='rear_frame', src='rider'))
    mh = M * 0.081; ph = sh + np.array([0.04, 0, 0.19])
    parts.append(dict(name='rider_head', m=mh, p=ph, I=np.eye(3) * (0.4 * mh * 0.11 ** 2 * 1.4), body='rear_frame', src='rider'))
    for side in ('right', 'left'):
        add(f'rider_upper_arm_{side}', 0.028, P(side, 'shoulder'), P(side, 'elbow'), 0.436, 0.045)
        add(f'rider_forearm_{side}', 0.016 + 0.006, P(side, 'elbow'), P(side, 'grip'), 0.45, 0.04)
        add(f'rider_thigh_{side}', 0.100, P(side, 'hip'), P(side, 'knee'), 0.433, 0.08)
        add(f'rider_shank_{side}', 0.0465, P(side, 'knee'), P(side, 'ankle'), 0.433, 0.055)
        add(f'rider_foot_{side}', 0.0145, P(side, 'ankle'), P(side, 'ball'), 0.5, 0.04)
    return parts


def bike_parts(fairing_mounted=False):
    rows = list(csv.DictReader(open(ROLL, encoding='utf-8')))
    out = []
    for r in rows:
        m = float(r['kg'])
        if m <= 0:
            continue
        name = r['item']
        p = np.array([float(r['x_mm']), float(r['y_mm']), float(r['height_mm'])]) / 1000.0
        I = np.zeros((3, 3)); src = 'point'
        c = cad.get(name)
        if c and 'inertia' in c and c.get('volume', 0) > 1:
            I = np.array(c['inertia']) * (m / c['volume']) * 1e-6     # mm^5 * kg/mm^3 -> kg mm^2 -> kg m^2
            src = 'cad'
        if name in FRONT_WHEEL:
            body = 'front_wheel'
        elif name in REAR_WHEEL:
            body = 'rear_wheel'
        elif name.startswith(HALF_STEER):
            out.append(dict(name=name + ' (steered half)', m=m / 2, p=p, I=I / 2, body='front_frame', src=src, unspr=r['unsprung']))
            m, I, body = m / 2, I / 2, 'rear_frame'
        elif name.startswith(STEER_PREFIX) and not (fairing_mounted and name.startswith(('Mirror_', 'Display_'))):
            body = 'front_frame'
        else:
            body = 'rear_frame'
        out.append(dict(name=name, m=m, p=p, I=I, body=body, src=src, unspr=r['unsprung']))
    return out


def combine(items):
    m = sum(i['m'] for i in items)
    c = sum(i['m'] * i['p'] for i in items) / m
    I = np.zeros((3, 3))
    for i in items:
        d = i['p'] - c
        I += i['I'] + i['m'] * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    return m, c, I


def load_parts(load):
    ps = bike_parts()
    if 'rider' in load:
        ps += rider_parts()
    if 'luggage' in load:
        L = LUGGAGE
        ps.append(dict(name='luggage', m=L['m'], p=np.array([L['x'], 0, L['z']]) / 1000, I=box_I(L['m'], *L['dims']), body='rear_frame', src='box'))
    return ps


def bodies(load):
    ps = load_parts(load)
    out = {}
    for b in ('rear_frame', 'front_frame', 'front_wheel', 'rear_wheel'):
        m, c, I = combine([p for p in ps if p['body'] == b])
        out[b] = dict(m=m, c=c.tolist(), I=I.tolist())
    for b, sel in (('front_lower', True), ('front_upper', False)):
        m, c, I = combine([p for p in ps if p['body'] == 'front_frame' and p['name'].startswith(LOWER_FORK) == sel])
        out[b] = dict(m=m, c=c.tolist(), I=I.tolist())
    mt, ct, It = combine(ps)
    out['total'] = dict(m=mt, c=ct.tolist(), I=It.tolist())
    out['rotor_gyro'] = dict(J=ROTOR_J, ratio=-RATIO)
    out['cad_inertia_mass_kg'] = sum(p['m'] for p in ps if p['src'] == 'cad')
    out['point_mass_kg'] = sum(p['m'] for p in ps if p['src'] == 'point')
    return out, ps


if __name__ == '__main__':
    res = {}; summ = {}
    roll = json.loads((D / 'run' / 'mass-rollup-snapshot.json').read_text()) if '--live' not in sys.argv else json.loads((R / 'mass-rollup.json').read_text())
    # geometry from the CAD: axle centres, steering axis, pivot
    bb = lambda n: cad[n]['bbox']
    fw = cad['Front_wheel_STUDY']['centre']; rw = cad['Rear_wheel_STUDY']['centre']
    xF = (bb('Front_nominal_tire')[0] + bb('Front_nominal_tire')[1]) / 2; xR = (bb('Rear_nominal_tire')[0] + bb('Rear_nominal_tire')[1]) / 2
    WB = xF - xR
    caster = math.radians(25.0); S = np.array([1206.954, 0.0, 800.0 + 53.1])   # build-adventure.py SA0, + the 53.1 mm model lift
    FORK_OFF = 36.1; RF = (bb('Front_nominal_tire')[5] - bb('Front_nominal_tire')[4]) / 2; RR = (bb('Rear_nominal_tire')[5] - bb('Rear_nominal_tire')[4]) / 2
    x_int = S[0] + S[2] * math.tan(caster)
    trail = (RF * math.sin(caster) - FORK_OFF) / math.cos(caster)
    geom = dict(front_axle_x_mm=xF, rear_axle_x_mm=xR, wheelbase_mm=WB, front_tyre_radius_mm=RF, rear_tyre_radius_mm=RR,
                rake_deg=25.0, fork_offset_mm=FORK_OFF, trail_mm=trail, steering_axis_point_mm=S.tolist(),
                axis_ground_intercept_x_mm=x_int, pivot_mm=[540.0, 0.0, 403.1],
                trail_horizontal_from_axis_intercept_mm=x_int - xF, trail_normal_to_axis_mm=(x_int - xF) * math.cos(caster))
    res['geometry'] = geom
    print('geometry', json.dumps(geom))
    for key, load in (('bike_only', ()), ('solo', ('rider',)), ('solo_luggage', ('rider', 'luggage'))):
        b, ps = bodies(load)
        res[key] = b
        T = np.array(b['total']['I']); m = b['total']['m']; c = np.array(b['total']['c']) * 1000
        # weight distribution on the real wheelbase (axle centres from the CAD tyre bounding boxes)
        fz_front = m * 9.81 * (c[0] - xR) / WB
        summ[key] = dict(mass_kg=m, cg_x_mm=c[0], cg_y_mm=c[1], cg_z_mm=c[2], cg_x_from_rear_axle_mm=c[0] - xR,
                         front_pct=100 * (c[0] - xR) / WB, rear_pct=100 * (1 - (c[0] - xR) / WB),
                         Ixx=T[0, 0], Iyy=T[1, 1], Izz=T[2, 2], Ixy=T[0, 1], Ixz=T[0, 2], Iyz=T[1, 2],
                         roll_gyr_mm=1000 * math.sqrt(T[0, 0] / m), pitch_gyr_mm=1000 * math.sqrt(T[1, 1] / m), yaw_gyr_mm=1000 * math.sqrt(T[2, 2] / m),
                         cad_shaped_kg=b['cad_inertia_mass_kg'], point_mass_kg=b['point_mass_kg'])
        for body in ('rear_frame', 'front_frame', 'front_wheel', 'rear_wheel'):
            B = b[body]; I = np.array(B['I'])
            summ[key][body] = dict(m=B['m'], c_mm=[v * 1000 for v in B['c']], Ixx=I[0, 0], Iyy=I[1, 1], Izz=I[2, 2], Ixz=I[0, 2])
        print(f"== {key}: {m:.1f} kg CoG x {c[0]:.0f} (from rear axle {c[0]-xR:.0f}) y {c[1]:.1f} z {c[2]:.0f} mm; "
              f"front {summ[key]['front_pct']:.1f}%  Ixx {T[0,0]:.2f} Iyy {T[1,1]:.2f} Izz {T[2,2]:.2f} Ixz {T[0,2]:.2f}  "
              f"[CAD-shaped {b['cad_inertia_mass_kg']:.0f} kg, point {b['point_mass_kg']:.0f} kg]")
    # check against the roll-up
    bo = summ['bike_only']
    chk = dict(rollup_total_kg=roll['total_kg'], ours_total_kg=bo['mass_kg'], rollup_cg_x_mm=roll['cog_mm']['x_from_rear_axle'],
               ours_cg_x_from_rear_axle_mm=bo['cg_x_from_rear_axle_mm'], rollup_cg_z_mm=roll['cog_mm']['height'], ours_cg_z_mm=bo['cg_z_mm'],
               rollup_cg_y_mm=roll['cog_mm']['y'], ours_cg_y_mm=bo['cg_y_mm'], rollup_front_pct=roll['front_rear_split_pct'][0],
               ours_front_pct_on_cad_wheelbase=bo['front_pct'],
               rollup_pitch_inertia_point_mass=roll['pitch_inertia_point_mass_kgm2'], ours_pitch_inertia_with_part_shapes=bo['Iyy'])
    res['rollup_check'] = chk
    print('roll-up check', json.dumps(chk))
    # rider alone
    rp = rider_parts(); m, c, I = combine(rp)
    summ['rider_alone'] = dict(mass_kg=m, cg_mm=(c * 1000).tolist(), Ixx=I[0, 0], Iyy=I[1, 1], Izz=I[2, 2])
    print('rider', summ['rider_alone'])
    res['prepared'] = 'November 22, 2026, US Central. Claude Sonnet 5.5 (claude-sonnet-5-5)'
    res['summary'] = summ; res['assumptions'] = dict(rollup_file=str(ROLL.name), luggage=LUGGAGE, rider_kg=M_RIDER, rider_height_mm=G_RIDER)
    (D / 'mass-properties.json').write_text(json.dumps(res, indent=1))
    keys = list(summ['bike_only'].keys())
    with open(D / 'mass-properties-summary.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['quantity', 'bike_only', 'solo_rider90', 'rider90_luggage25'])
        for k in keys:
            if isinstance(summ['bike_only'][k], dict):
                continue
            w.writerow([k] + [f"{summ[c][k]:.4g}" for c in ('bike_only', 'solo', 'solo_luggage')])
