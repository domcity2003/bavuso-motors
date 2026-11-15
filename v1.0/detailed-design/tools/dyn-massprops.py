"""Vehicle dynamics: rigid-body mass properties for the stability model, from the mass roll-up and the CAD.

Splits mass-rollup.csv into the four bodies of a Sharp/Whipple-type model:
  rear frame  (frame, pack, motor, body, rider rigidly attached, swingarm and rear unsprung non-rotating)
  front frame (everything that steers and does not spin: fork, clamps, bars, controls, calipers, display)
  front wheel (spinning: tyre, rim, discs, carriers)
  rear wheel  (spinning: tyre, rim, discs, belt pulley)
Each part keeps its own inertia: the CAD volume inertia (dyn-cad-extract.py) scaled to the roll-up mass.
Parts without a CAD solid are point masses (allowances: harness, fasteners, coolant...).
Riders are boxes (Cossalter-style seated-rider estimate). Output: detailed-design/dynamics/mass-properties.json
(SI units, frame: origin at the rear contact patch, X forward, Y left, Z up).

Run from v1.0 with the FreeCAD python (numpy only).
Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import csv, json, math
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parents[2]
D = R / 'detailed-design' / 'dynamics'
cad = json.loads((D / 'cad-extract.json').read_text())

FRONT_WHEEL = {'Front_nominal_tire', 'Front_wheel_STUDY', 'Front_disc_m1', 'Front_disc_p1',
               'Front_disc_carrier_m1', 'Front_disc_carrier_p1'}
REAR_WHEEL = {'Rear_nominal_tire', 'Rear_wheel_STUDY', 'Rear_pulley_PITCH_STUDY', 'Rear_disc_p1',
              'Rear_disc_carrier_p1'}
STEER_PREFIX = ('Fork_', 'Lower_triple', 'Upper_triple', 'Bar_', 'Hand_grip', 'Hand_lever', 'Lever_perch',
                'Switch_cube', 'Front_master', 'Front_brake_reservoir', 'Front_caliper', 'Front_fender',
                'Mirror_', 'Display_', 'Harness_connector', 'Harness_bar', 'Front_brake_hose_caliper',
                'Front_brake_splitter', 'Front axle')
LOWER_FORK = ('Fork_inner', 'Fork_axle_clamp', 'Front_caliper', 'Front_fender', 'Fork_reflector',
              'Front_brake_hose_caliper', 'Front axle')   # moves with fork lateral bending
HALF_STEER = {'Steering bearings, stem nut, steering damper', 'Front_brake_hose_upper'}

# Rider/passenger/luggage: (mass kg, x mm, z mm above ground, box dims x,y,z m). Same positions as
# tools/rear-kinematics.py (rider 85 kg at X520/Z1090, passenger X150/Z1150, luggage 30 kg at X-100/Z750).
RIDERS = dict(rider=(85.0, 520.0, 1090.0, (0.50, 0.45, 0.75)),
              passenger=(85.0, 150.0, 1150.0, (0.50, 0.45, 0.75)),
              luggage=(30.0, -100.0, 750.0, (0.45, 0.80, 0.40)))
ROTOR_J = 0.0124      # kg m2: IPM rotor about 4.5 kg, OD 140 / shaft 50 mm (estimate), spins at -7.8x wheel speed
RATIO = 7.8           # drive-study.md total reduction; the gear stage reverses direction, the belt does not


def box_I(m, a, b, c):
    return np.diag([m * (b * b + c * c) / 12, m * (a * a + c * c) / 12, m * (a * a + b * b) / 12])


def parts(fairing_mounted=False):
    rows = list(csv.DictReader(open(R / 'mass-rollup.csv', encoding='utf-8')))
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
            I = np.array(c['inertia']) * (m / c['volume']) * 1e-6   # mm^5 * kg/mm^3 -> kg mm^2 -> kg m^2
            src = 'cad'
        if name in FRONT_WHEEL:
            body = 'front_wheel'
        elif name in REAR_WHEEL:
            body = 'rear_wheel'
        elif name.startswith(STEER_PREFIX) and not (fairing_mounted and name.startswith(('Mirror_', 'Display_'))):
            body = 'front_frame'
        elif name in HALF_STEER:
            out.append(dict(name=name + ' (steered half)', m=m / 2, p=p, I=I / 2, body='front_frame', src=src))
            m, I, body = m / 2, I / 2, 'rear_frame'
        else:
            body = 'rear_frame'
        out.append(dict(name=name, m=m, p=p, I=I, body=body, src=src))
    return out


def combine(items):
    m = sum(i['m'] for i in items)
    c = sum(i['m'] * i['p'] for i in items) / m
    I = np.zeros((3, 3))
    for i in items:
        d = i['p'] - c
        I += i['I'] + i['m'] * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    return m, c, I


def bodies(load=('rider',), fairing_mounted=False):
    ps = parts(fairing_mounted)
    for k in load:
        m, x, z, dims = RIDERS[k]
        ps.append(dict(name=k, m=m, p=np.array([x, 0, z]) / 1000, I=box_I(m, *dims), body='rear_frame', src='box'))
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
    return out


if __name__ == '__main__':
    res = {}
    for key, load in (('bike_only', ()), ('solo', ('rider',)), ('twoup', ('rider', 'passenger', 'luggage'))):
        res[key] = bodies(load)
        if key != 'bike_only':   # variant: TFT and mirrors on the fairing instead of the bars/top clamp
            res[key + '_fm'] = bodies(load, fairing_mounted=True)
    res['prepared'] = 'November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5)'
    (D / 'mass-properties.json').write_text(json.dumps(res, indent=1))
    for key in ('bike_only', 'solo', 'twoup', 'solo_fm'):
        r = res[key]
        print(f"== {key}: total {r['total']['m']:.1f} kg, CoG x {r['total']['c'][0]*1000:.0f} z {r['total']['c'][2]*1000:.0f} mm;"
              f" CAD-shaped {r['cad_inertia_mass_kg']:.0f} kg, point {r['point_mass_kg']:.0f} kg")
        for b in ('rear_frame', 'front_frame', 'front_wheel', 'rear_wheel'):
            B = r[b]; I = np.array(B['I'])
            print(f"  {b:12s} m {B['m']:7.2f}  c ({B['c'][0]:.3f},{B['c'][1]:.3f},{B['c'][2]:.3f})  "
                  f"Ixx {I[0,0]:.3f} Iyy {I[1,1]:.3f} Izz {I[2,2]:.3f} Ixz {I[0,2]:.3f}")
