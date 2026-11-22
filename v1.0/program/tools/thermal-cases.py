"""Bavuso V1 thermal: duty cases on the rev C cooling concept (tasks 1, 2, 5).
Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/thermal-cases.py
Writes program/data/thermal/cases.json and series-<case>.csv
"""
import importlib.util, json, os, csv, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'data', 'thermal'); os.makedirs(OUT, exist_ok=True)
sp = importlib.util.spec_from_file_location('tl', os.path.join(HERE, 'thermal-lib.py')); tl = importlib.util.module_from_spec(sp); sp.loader.exec_module(tl)
dl = tl.dl
REVC = tl.Rad()            # 2 x 165 x 128 x 28 mm, slim fans (rev C CAD)
LEAN = tl.Rad(h=0.118, w=0.152)   # 15 % smaller option
res = {}
def keep(name, sim, rec=None):
    s = sim.summary(); res[name] = s
    with open(os.path.join(OUT, f'series-{name}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(sim.series[0].keys())); w.writeheader(); w.writerows(sim.series)
    print(name, {k: v for k, v in s.items() if k != 'balance'}, 'bal%', s['balance']['residual_pct'], flush=True)
    return sim
R = {'revC': REVC, 'lean': LEAN}
for rn, rad in R.items():
    # ---- 1a DC fast charge 10-80 %, 3C cap (cell 18 A), NACS 250 kW station
    for ta, t0, tag in ((25, 25, '25C'), (35, 35, '35C'), (35, 42, '35C_arrive42'), (45, 45, '45C')):
        keep(f'{rn}_dc_{tag}', tl.Sim(rad, ta, 'charge', soc0=10, soc_target=80, T0=t0, heater_w=0).run(3 * 3600, dt=0.5))
    keep(f'{rn}_dc_35C_2Ccap', tl.Sim(rad, 35, 'charge', soc0=10, soc_target=80, heater_w=0, c_cap=2.0).run(3 * 3600, dt=0.5))
    # ---- 1b sustained 125 mph (95 -> 5 % SOC) and 130 mph governed top speed
    for ta in (25, 38):
        keep(f'{rn}_125mph_{ta}C', tl.Sim(rad, ta, 'drive', tl.steady(125), soc0=95).run(3 * 3600, dt=0.5))
    keep(f'{rn}_130mph_25C', tl.Sim(rad, 25, 'drive', tl.steady(130), soc0=95).run(3 * 3600, dt=0.5))
    # hot-day derate: highest steady speed that keeps every limit for the whole pack at 38 C
    best = None; trace = []
    for mph in range(125, 80, -5):
        s = tl.Sim(rad, 38, 'drive', tl.steady(mph), soc0=95).run(3 * 3600, dt=1.0).summary()
        ok = s['coolant_inlet_max'] <= 50 and s['core_hot_max'] <= 55 and s['winding_max'] <= 100 and s['inverter_inlet_max'] <= 65
        trace.append((mph, s['minutes'], s['coolant_inlet_max'], s['core_hot_max'], s['winding_max']))
        if ok and best is None: best = mph
    res[f'{rn}_hot38_derate'] = dict(max_steady_mph=best, trace=trace); print(rn, 'hot-day steady mph', best, trace, flush=True)
    # ---- 1c repeated hard mountain riding: 90 s cycle until the pack is at 5 %, and a 25 min climb + descent
    for ta in (25, 38):
        keep(f'{rn}_hardride_{ta}C', tl.Sim(rad, ta, 'drive', tl.hard_ride_cycle(), soc0=95).run(5 * 3600, dt=0.5, rec_every=30))
    keep(f'{rn}_mountain_38C', tl.Sim(rad, 38, 'drive', tl.mountain_profile(), soc0=95).run(40 * 60, dt=0.5))
    # ---- 1d cold charging at -10 C with the 3 kW PTC (cold soaked), plus 2 / 5 kW and a pre-heated arrival
    for hw in (2000, 3000, 5000):
        keep(f'{rn}_cold_m10C_ptc{hw // 1000}kW', tl.Sim(rad, -10, 'charge', soc0=10, soc_target=80, heater_w=hw).run(4 * 3600, dt=0.5))
    keep(f'{rn}_cold_m10C_noheater', tl.Sim(rad, -10, 'charge', soc0=10, soc_target=80, heater_w=0).run(2 * 3600, dt=1.0))
    # 0 C and -20 C for the edge
    keep(f'{rn}_cold_0C_ptc3kW', tl.Sim(rad, 0, 'charge', soc0=10, soc_target=80, heater_w=3000).run(4 * 3600, dt=0.5))
    # ---- AC 3.3 kW at 38 C (charger plate), 10 -> 80 %
    keep(f'{rn}_ac_38C', tl.Sim(rad, 38, 'ac', soc0=10, soc_target=80).run(8 * 3600, dt=2.0, rec_every=60))
    if rn == 'lean': pass
# preheated arrival at -10 C: the pack is warmed to 20 C on the ride in (heater from the pack), then DC-charged
s = tl.Sim(REVC, -10, 'charge', soc0=10, soc_target=80, heater_w=3000, T0=20.0)
s.x0[s.i['Tcase']] = 5.0
keep('revC_cold_m10C_preheated20', s.run(2 * 3600, dt=0.5))
# energy for the preheat itself: heat 100 kJ/K-class pack from -10 to 20 C
e_pre = (tl.C_CELL * tl.N_CELL + tl.C_PACK_OTHER) * 30.0
res['preheat_energy'] = dict(MJ=round(e_pre / 1e6, 2), kWh=round(e_pre / 3.6e6, 2), pct_of_pack=round(100 * e_pre / 3.6e6 / dl.PACK_KWH, 1),
                              minutes_at_3kW_ideal=round(e_pre / 3000 / 60, 1))
# ram-air sensitivity on the 125 mph cases
sens = []
for ram in (0.15, 0.20, 0.25, 0.35):
    for rn, base in (('revC', REVC), ('lean', LEAN)):
        rad = tl.Rad(h=base.h, w=base.w, d=base.d, fan='slim', ram=ram)
        for ta in (25, 38):
            s = tl.Sim(rad, ta, 'drive', tl.steady(125), soc0=95).run(3 * 3600, dt=1.0).summary()
            sens.append(dict(ram=ram, rad=rn, ambient=ta, inlet=s['coolant_inlet_max'], core=s['core_hot_max'], winding=s['winding_max'], t_inlet50=s['t_inlet50_min']))
res['ram_sensitivity'] = sens
# cell-resistance sensitivity on the hot charge
rs = []
for k in (0.8, 1.0, 1.25):
    s = tl.Sim(REVC, 35, 'charge', soc0=10, soc_target=80, heater_w=0, r_scale=k).run(3 * 3600, dt=1.0).summary()
    rs.append(dict(r_scale=k, minutes=s['minutes'], core=s['core_hot_max']))
res['r_sensitivity_35C_charge'] = rs
json.dump(res, open(os.path.join(OUT, 'cases.json'), 'w'), indent=1)
print('wrote cases.json')
