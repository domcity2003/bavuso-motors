"""Bavuso V1 thermal: radiator / fan sizing sweep, cooling mass and hydraulics (task 3).
Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/thermal-radiator.py
Writes program/data/thermal/radiator-sweep.json/.csv, cooling-mass.json
Sizing requirements:
  R1  125 mph for the full pack (95 -> 5 %) at 25 C: coolant inlet <= 50 C (EMRAX limit), hottest cell core <= 55 C, winding <= 100 C, inverter inlet <= 65 C
  R2  DC 10-80 % at 35 C ambient (start 35 C), 3C cap: <= 25 min (T6) with hottest cell core <= 55 C
  R3  (information, derate allowed by Gate A) highest steady speed at 38 C that holds the same limits for 27 min
"""
import importlib.util, json, math, os, csv, itertools, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'data', 'thermal'); os.makedirs(OUT, exist_ok=True)
sp = importlib.util.spec_from_file_location('tl', os.path.join(HERE, 'thermal-lib.py')); tl = importlib.util.module_from_spec(sp); sp.loader.exec_module(tl)

def mass_items(rad, heater_kw=3.0, valve=True):
    hose_l = (1.6 * math.pi * 0.007 ** 2 + 2.2 * math.pi * 0.006 ** 2) * 1000      # 1.6 m trunk 14 mm ID + 2.2 m branches 12 mm ID
    hose_kg = 1.6 * 0.14 + 2.2 * 0.12 + 0.10
    rib_l = tl.N_RIB * tl.RIB_PORTS * tl.RIB_W * tl.RIB_H * tl.RIB_LEN * 1000
    vols = dict(radiators=rad.coolant_l(), hoses=hose_l, pack_ribbons=rib_l, pack_manifolds=0.25, motor_jacket=0.20, inverter_plate=0.12, charger_plate=0.08, heater=0.12, pump_valve=0.10)
    coolant_kg = sum(vols.values()) * tl.RHO_C / 1000
    items = [('radiator cores + tanks (dry)', rad.mass(), 'est, scaled from thermal-study.md 0.805 kg per 210x140x32'),
             (f'fans x{rad.n} ({rad.fan})', tl.FANS[rad.fan]['kg'] * rad.n, 'est'),
             ('pump (CWA50 class, 22 L/min)', 0.55, 'est, thermal-study.md'),
             ('4-port valve (radiator bypass)' if valve else 'wax thermostat bypass', 0.45 if valve else 0.15, 'est'),
             (f'PTC heater {heater_kw:g} kW', 0.38 * heater_kw, 'est, 1.9 kg per 5 kW'),
             ('hoses: 1.6 m 14 mm trunk + 2.2 m 12 mm branches, clamps', hose_kg, 'est'),
             ('temperature sensors', 0.10, 'est'),
             (f'coolant {sum(vols.values()):.2f} L 50/50 EG', coolant_kg, 'calc from volumes')]
    return items, vols

def evaluate(rad, hot_speed=False):
    r = {}
    s1 = tl.Sim(rad, 25, 'drive', tl.steady(125), soc0=95).run(3600, dt=1.0).summary()
    r['R1'] = s1
    r['R1_pass'] = bool(s1['coolant_inlet_max'] <= 50 and s1['core_hot_max'] <= 55 and s1['winding_max'] <= 100 and s1['inverter_inlet_max'] <= 65 and s1['stop'] == 'soc')
    s2 = tl.Sim(rad, 35, 'charge', soc0=10, soc_target=80, heater_w=0).run(3600, dt=1.0).summary()
    r['R2'] = s2
    r['R2_pass'] = bool(s2['stop'] == 'target' and s2['minutes'] <= 25 and s2['core_hot_max'] <= 55)
    if hot_speed:
        best = None
        for mph in (125, 120, 115, 110, 105, 100, 95, 90):
            s = tl.Sim(rad, 38, 'drive', tl.steady(mph), soc0=95).run(3600, dt=1.0).summary()
            ok = s['coolant_inlet_max'] <= 50 and s['core_hot_max'] <= 55 and s['winding_max'] <= 100 and s['inverter_inlet_max'] <= 65
            r.setdefault('R3_trace', []).append((mph, s['coolant_inlet_max'], s['core_hot_max'], s['winding_max']))
            if ok and best is None: best = mph
        r['R3_hot_mph'] = best
    return r

if __name__ == '__main__':
    base_h, base_w = 0.128, 0.165
    rows = []; full = []
    scales = (0.40, 0.55, 0.70, 0.85, 1.0, 1.3, 1.7)
    for d, fan, s in itertools.product((0.028, 0.040), ('slim', 'mid', 'big'), scales):
        k = math.sqrt(s)
        rad = tl.Rad(h=round(base_h * k, 4), w=round(base_w * k, 4), d=d, n=2, fan=fan)
        ev = evaluate(rad)
        items, vols = mass_items(rad)
        mass = sum(i[1] for i in items)
        row = dict(depth_mm=d * 1000, fan=fan, area_scale=s, core_h_mm=round(rad.h * 1000), core_w_mm=round(rad.w * 1000), area_m2=round(rad.area, 4),
                   R1_inlet=ev['R1']['coolant_inlet_max'], R1_core=ev['R1']['core_hot_max'], R1_winding=ev['R1']['winding_max'], R1_pass=ev['R1_pass'],
                   R2_min=ev['R2']['minutes'], R2_core=ev['R2']['core_hot_max'], R2_pass=ev['R2_pass'],
                   cooling_mass_kg=round(mass, 2), radiator_fan_kg=round(rad.mass() + tl.FANS[fan]['kg'] * 2, 2), fan_w=tl.FANS[fan]['w'] * 2)
        rows.append(row); print(row, flush=True)
    with open(os.path.join(OUT, 'radiator-sweep.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(rows, open(os.path.join(OUT, 'radiator-sweep.json'), 'w'), indent=1)
