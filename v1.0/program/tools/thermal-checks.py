"""Bavuso V1 thermal: energy balances, hand checks, convergence, hydraulics and cooling mass (tasks 3 and 5).
Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/thermal-checks.py
Reads program/data/thermal/cases.json; writes checks.json
"""
import importlib.util, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'data', 'thermal')
def L(n, f):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, f)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tl = L('tl', 'thermal-lib.py'); tr = L('tr', 'thermal-radiator.py'); dl = tl.dl
cases = json.load(open(os.path.join(OUT, 'cases.json')))
out = {}
# 1. thermal closure over every case
res = {k: v['balance']['residual_pct'] for k, v in cases.items() if isinstance(v, dict) and 'balance' in v}
out['thermal_closure_pct'] = dict(max_abs=round(max(abs(x) for x in res.values()), 4), n_cases=len(res))
# 2. electrical balance, drive: OCV power = wheel + belt + motor + inverter + pack I2R (drive-lib) + auxiliaries
el = {}
for name, prof, ta in (('125mph_25C', tl.steady(125), 25), ('hardride_25C', tl.hard_ride_cycle(), 25)):
    s = tl.Sim(tl.Rad(), ta, 'drive', prof, soc0=95).run(2400 if 'hard' in name else 3600, dt=1.0)
    e = s.en; tot = e['wheel'] + e['belt'] + e['motor'] + e['inv'] + e['rlib'] + e['aux']
    el[name] = dict(ocv_MJ=round(e['ocv'] / 1e6, 3), sum_MJ=round(tot / 1e6, 3), residual_pct=round(100 * (e['ocv'] - tot) / e['ocv'], 3),
                    wheel_MJ=round(e['wheel'] / 1e6, 3), losses_MJ=dict(belt=round(e['belt'] / 1e6, 3), motor=round(e['motor'] / 1e6, 3), inverter=round(e['inv'] / 1e6, 3),
                                                                      pack_lib=round(e['rlib'] / 1e6, 3), aux=round(e['aux'] / 1e6, 3)))
out['electrical_balance_drive'] = el
# charge: station = chemical + cell heat + external I2R
s = tl.Sim(tl.Rad(), 25, 'charge', soc0=10, soc_target=80, heater_w=0).run(3600, dt=0.5); e = s.en
chem = -e['ocv']
out['charge_balance_25C'] = dict(station_kWh=round(e['station'] / 3.6e6, 3), chemical_kWh=round(chem / 3.6e6, 3), cell_heat_kWh=round(e['cell_heat'] / 3.6e6, 3),
                                  external_kWh=round(e['ext'] / 3.6e6, 3),
                                  residual_pct=round(100 * (e['station'] - chem - e['cell_heat'] - e['ext']) / e['station'], 4),
                                  chemical_vs_70pct_nameplate_kWh=(round(chem / 3.6e6, 2), round(0.70 * dl.PACK_KWH, 2)), minutes=round(s.t_end / 60, 1),
                                  drive06_minutes=15.5, drive06_kWh=17.98)
# 3. hand checks
hc = {}
r = tl.r_cell_heat(25, 10.0); hc['cell_heat_3C_start_W_hand'] = round(1100 * 18 ** 2 * r)
hc['cell_heat_3C_start_W_model'] = round(tl.Sim(tl.Rad(), 25, 'charge', soc0=10, heater_w=0).loads(0, tl.Sim(tl.Rad(), 25).x0)['q_cell'])
sim = tl.Sim(tl.Rad(), 25, 'charge', soc0=10, soc_target=80, heater_w=0).run(3600, dt=0.5)
q_cells = sim.en['cell_heat']; c_cells = tl.N_CELL * tl.C_CELL
hc['adiabatic_cell_rise_K'] = round(q_cells / (c_cells + tl.C_PACK_OTHER), 1); hc['model_mean_rise_K'] = round(sim.series[-1]['Tc_mean'] - 25.0, 1)
hc['heat_removed_by_radiator_pct'] = round(100 * sim.balance['to_radiator_MJ'] / sim.balance['generated_MJ'], 1)
rad = tl.Rad(); v = 0.25 * 125 * tl.MPH; C_air = tl.RHO_AIR * rad.area * v * 1007.0; C_c = tl.mcp(22); UA = rad.ua5() * (v / 5) ** 0.5
q_ntu = rad.q(45.0, 25.0, v, C_c)
def lmtd_q():
    lo, hi = 0.0, min(C_air, C_c) * 20.0
    for _ in range(80):
        q = 0.5 * (lo + hi); th_o = 45.0 - q / C_c; ta_o = 25.0 + q / C_air
        d1, d2 = 45.0 - ta_o, th_o - 25.0
        lm = (d1 - d2) / math.log(d1 / d2) if abs(d1 - d2) > 1e-9 and d1 > 0 and d2 > 0 else max(d1, 1e-9)
        if UA * lm > q: lo = q
        else: hi = q
    return 0.5 * (lo + hi)
hc['radiator_125mph_Q_W'] = dict(e_NTU=round(q_ntu), counterflow_LMTD_upper_bound=round(lmtd_q()), UA_WperK=round(UA), air_capacity_WperK=round(C_air), coolant_capacity_WperK=round(C_c))
s125 = tl.Sim(tl.Rad(), 25, 'drive', tl.steady(125), soc0=95); s125.run(300, dt=1.0)
Lc = s125.loads(0, s125.x)
hc['loads_125mph_W'] = dict(cells=round(Lc['q_cell']), motor=round(Lc['q_mot']), inverter=round(Lc['q_inv']), dcdc=round(Lc['q_dc']),
                            total_to_coolant=round(Lc['q_cell'] + Lc['q_mot'] + Lc['q_inv'] + Lc['q_dc'] + tl.PUMP_HEAT_W),
                            drive06=dict(pack='1.7-2.7 kW', motor='1.9 kW', inverter='1.0 kW'), wheel_kW=round(Lc['p_wheel'] / 1e3, 1), cell_A=round(Lc['i_cell'], 1))
q_rib = tl.CELLS_PER_RIB * 18 ** 2 * tl.r_cell_heat(25, 10.0); hc['ribbon_heat_W_per_ribbon_3C'] = round(q_rib)
hc['ribbon_coolant_rise_K'] = round(q_rib / (tl.mcp(tl.Q_PACK_LPM) / tl.N_RIB), 1)
hc['cell_core_to_coolant_K_at_5W'] = round(5.0 * (tl.R_CORE_CAN * tl.ARC_PENALTY + tl.R_CW), 1)
out['hand_checks'] = hc
# 4. convergence: time step, cell FD grid
conv = {}
for dt in (0.25, 0.5, 1.0, 2.0):
    a = tl.Sim(tl.Rad(), 35, 'charge', soc0=10, soc_target=80, heater_w=0).run(3600, dt=dt).summary()
    b = tl.Sim(tl.Rad(), 38, 'drive', tl.steady(125), soc0=95).run(3600, dt=dt).summary()
    conv[f'dt{dt}'] = dict(charge35_min=a['minutes'], charge35_core=a['core_hot_max'], mph125_38C_core=b['core_hot_max'], mph125_38C_inlet=b['coolant_inlet_max'])
out['timestep_convergence'] = conv
out['cell_fd_convergence'] = {f'{nr}x{nz}': [round(x, 4) for x in tl.cell_fd(nr=nr, nz=nz)] for nr, nz in ((8, 16), (16, 32), (24, 48))}
# 5. hydraulics at 22 L/min
RHO, MU = tl.RHO_C, 2.2e-3
def pipe(lpm, d, Ln, k=0.0):
    Q = lpm / 60000; v = Q / (math.pi * d * d / 4); Re = RHO * v * d / MU
    f = 64 / Re if Re < 2300 else 0.316 / Re ** 0.25
    return (f * Ln / d + k) * RHO * v * v / 2, v, Re
a = tl.RIB_H / tl.RIB_W; fRe = 96 * (1 - 1.3553 * a + 1.9467 * a ** 2 - 1.7012 * a ** 3 + 0.9564 * a ** 4 - 0.2537 * a ** 5)
Qp = tl.Q_PACK_LPM / 60000 / tl.N_RIB; vr = Qp / (tl.RIB_PORTS * tl.RIB_W * tl.RIB_H); Rer = RHO * vr * tl.RIB_DH / MU
dp_rib = fRe / Rer * tl.RIB_LEN / tl.RIB_DH * RHO * vr ** 2 / 2 + 1.5 * RHO * vr ** 2 / 2
trunk, vt, ret = pipe(22, 0.014, 1.6, 5.0)
pk, vp, _ = pipe(10, 0.012, 1.0, 3.0); dr, vd, _ = pipe(12, 0.012, 1.2, 4.0)
dp_pack = dp_rib + 3000 + pk; dp_drive = 15000 + 8000 + 4000 + dr
dp_branch = max(dp_pack, dp_drive); dp_tot = trunk + 3500 + 4000 + 2500 + dp_branch
out['hydraulics'] = dict(ribbon=dict(velocity_ms=round(vr, 3), Re=round(Rer), dp_kPa=round(dp_rib / 1e3, 2)), trunk_14mm=dict(velocity_ms=round(vt, 2), Re=round(ret), dp_kPa=round(trunk / 1e3, 1)),
                         dp_pack_branch_kPa=round(dp_pack / 1e3, 1), dp_drive_branch_kPa=round(dp_drive / 1e3, 1), balancing_orifice_kPa=round((dp_drive - dp_pack) / 1e3, 1),
                         total_kPa=round(dp_tot / 1e3, 1), flow_lpm=22, hydraulic_W=round(dp_tot * 22 / 60000, 1), pump_electrical_W=round(dp_tot * 22 / 60000 / 0.25),
                         pump_note='CWA50 class: about 25 L/min at 53 kPa (datasheet in thermal-study.md); this duty is at the edge of that curve')
# 6. mass bill
bills = {}
for nm, rad in (('revC_165x128x28_slim', tl.Rad()), ('lean_152x118x28_slim', tl.Rad(h=0.118, w=0.152))):
    it, vols = tr.mass_items(rad)
    bills[nm] = dict(items=[(a, round(b, 2), c) for a, b, c in it], total_kg=round(sum(i[1] for i in it), 2), coolant_L=round(sum(vols.values()), 2))
    it2, _ = tr.mass_items(rad, valve=False); bills[nm]['with_wax_thermostat_instead_of_valve_kg'] = round(sum(i[1] for i in it2), 2)
out['mass_bills'] = bills
json.dump(out, open(os.path.join(OUT, 'checks.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
