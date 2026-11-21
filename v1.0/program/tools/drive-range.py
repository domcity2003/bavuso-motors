"""Bavuso V1 range at constant speed with the real drivetrain efficiency map (not a flat 90%).

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drive-range.py
Writes program/data/drive-range.json
Road load = Gate A (rho 1.225, Crr 0.015, CdA 0.38, 300 W auxiliaries, flat, still air, 240 kg + 90 kg).
Energy = integral of pack terminal power from 95% to 5% SOC (the 90% usable window), pack at constant temperature.
"""
import importlib.util, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
dl = _load('drive_lib', 'drive-lib.py')
G = 126.0 / 35.0
drv = dl.Drive(G)
MPH = dl.MPH

def cruise_range(mph, cda=dl.CDA, t_pack=25.0, t_wind=70.0, mass_extra=0.0, aux=dl.AUX_W, fe_scale=1.0):
    old_m, old_fe = dl.M_TOT, dl.FE_KW_5500
    dl.M_TOT = old_m + mass_extra
    dl.FE_KW_5500 = old_fe * fe_scale
    try:
        v = mph * MPH
        soc = dl.USABLE_SOC[1]
        e_pack = e_wheel = dist = 0.0
        losses = dict(belt=0.0, motor_cu=0.0, motor_fe=0.0, inverter=0.0, pack=0.0, aux=0.0)
        dt = 20.0
        while soc > dl.USABLE_SOC[0]:
            pw = dl.road_force(v, cda) * v
            bl = dl.belt_loss(pw)
            n = drv.rpm(v)
            T = (pw + bl) / (n * math.pi / 30.0)
            e = drv.electrical(T, n, soc, t_pack, t_wind, p_aux=aux)
            if e is None:
                break
            p_term = e['p_dc'] + aux
            soc -= e['i_dc'] * dt / (dl.PACK_AH * 3600.0) * 100.0
            e_pack += (e['vbus'] * e['i_dc']) * dt      # energy out of the terminals
            e_cells = dl.ocv_pack(soc) * e['i_dc'] * dt
            e_wheel += pw * dt
            dist += v * dt
            losses['belt'] += bl * dt; losses['motor_cu'] += e['cu'] * dt; losses['motor_fe'] += e['fe'] * dt
            losses['inverter'] += e['p_inv'] * dt; losses['pack'] += e['p_pack_loss'] * dt; losses['aux'] += aux * dt
        tot = e_wheel + sum(losses.values())
        return dict(mph=mph, cda=cda, range_mi=dist / 1609.344, wh_per_mi=tot / 3600.0 / (dist / 1609.344), kwh_used=tot / 3.6e6,
                    wheel_to_battery_eff_pct=100 * e_wheel / tot, shares_pct={k: 100 * x / tot for k, x in losses.items()} | {'wheel': 100 * e_wheel / tot})
    finally:
        dl.M_TOT, dl.FE_KW_5500 = old_m, old_fe

out = {}
rows = []
for mph in (50, 55, 60, 65, 70, 77, 85, 100, 125):
    r = cruise_range(mph)
    rows.append(r)
    print(f"{mph:4d} mph {r['range_mi']:6.1f} mi {r['wh_per_mi']:6.1f} Wh/mi  eff {r['wheel_to_battery_eff_pct']:.1f}%")
out['by_speed'] = rows
# Gate A flat-90% comparison at 70 and 77 mph
gate = {}
for mph in (70, 77):
    v = mph * MPH
    pw = dl.road_force(v) * v
    p_batt = pw / 0.90 + dl.AUX_W
    gate[mph] = dict(range_mi=21.384e3 / (p_batt / mph), wh_per_mi=p_batt / mph)   # 21.384 kWh = 90% of 23.76
out['gate_a_flat_90pct'] = gate
print('Gate A flat 90%:', gate)
sens = {}
for mph in (70, 77):
    sens[mph] = dict(
        cda033=cruise_range(mph, cda=0.33)['range_mi'], cda038=cruise_range(mph)['range_mi'], cda043=cruise_range(mph, cda=0.43)['range_mi'],
        luggage25=cruise_range(mph, mass_extra=25.0)['range_mi'],
        cold_5c=cruise_range(mph, t_pack=5.0)['range_mi'], warm_35c=cruise_range(mph, t_pack=35.0)['range_mi'],
        fe_x0p6=cruise_range(mph, fe_scale=0.6)['range_mi'], fe_x1p6=cruise_range(mph, fe_scale=1.6)['range_mi'],
        aux_500w=cruise_range(mph, aux=500.0)['range_mi'])
out['sensitivity'] = sens
for k, v in sens.items():
    print(k, {a: round(b, 1) for a, b in v.items()})
r70 = cruise_range(70)
print('70 mph shares', {k: round(v, 1) for k, v in r70['shares_pct'].items()})
json.dump(out, open(os.path.join(HERE, '..', 'data', 'drive-range.json'), 'w'), indent=1, default=float)
