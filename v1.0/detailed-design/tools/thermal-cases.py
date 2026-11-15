"""Thermal study: run duty cases (a)-(d) plus the motor continuous check on the coupled lumped model.

Run from v1.0:
  "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cases.py [area_side_m2]
Writes detailed-design/thermal/cases.json and thermal/case-*.png.
"""
import sys, json, math, pathlib, importlib.util, time
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tl', HERE / 'thermal-lib.py'); tl = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl)
OUT = HERE.parent / 'thermal'; OUT.mkdir(exist_ok=True)
AREA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.035
MPH = 0.44704

def summarise(name, m, s, extra=None):
    eb = m.energy_balance()
    Tc = s['T_core']
    r = dict(case=name, duration_min=round(s['t'][-1] / 60, 1), soc_start=round(float(s['soc'][0]), 3), soc_end=round(float(s['soc'][-1]), 3),
             cell_core_mean_max_C=round(float(Tc.max()), 1), cell_hotspot_max_C=round(float(s['core_peak'].max()), 1),
             cell_sentinel_core_mean_max_C=round(float(s['T_sent'].max()), 1),
             pack_spread_max_K=round(float((s['core_peak'] - Tc.min(axis=0)).max()), 1),
             coolant_rise_in_pack_max_K=round(float((s['T_cool'][-1] - s['T_in']).max()), 1),
             pack_heat_peak_kW=round(float(s['q_pack'].max()) / 1e3, 2), pack_heat_mean_kW=round(float(np.mean(s['q_pack'])) / 1e3, 2),
             case_max_C=round(float(s['T_case'].max()), 1), case_heat_mean_W=round(float(np.mean(s['q_case'])), 0),
             batt_loop_max_C=round(float(s['T_BL'].max()), 1),
             winding_max_C=round(float(s['T_w'].max()), 1), magnet_max_C=round(float(s['T_r'].max()), 1),
             oil_max_C=round(float(s['T_o'].max()), 1), inverter_base_max_C=round(float(s['T_inv'].max()), 1),
             junction_max_C=round(float(s['Tj'].max()), 1), drive_loop_max_C=round(float(s['T_DL'].max()), 1),
             motor_loss_peak_kW=round(float(s['q_motor'].max()) / 1e3, 2), inverter_loss_peak_kW=round(float(s['q_inv'].max()) / 1e3, 2),
             gear_loss_peak_kW=round(float(s['q_gear'].max()) / 1e3, 2),
             radiator_batt_peak_kW=round(float(s['q_rad_b'].max()) / 1e3, 2), radiator_drive_peak_kW=round(float(s['q_rad_d'].max()) / 1e3, 2),
             min_derate=round(float(s['derate'].min()), 3), energy_balance=eb)
    if extra: r.update(extra)
    return r

def plot(name, s, title):
    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    tm = s['t'] / 60
    ax[0].plot(tm, s['core_peak'], label='hottest cell core'); ax[0].plot(tm, s['T_core'].mean(axis=0), label='cell core, pack mean')
    ax[0].plot(tm, s['T_BL'], label='battery coolant'); ax[0].plot(tm, s['T_case'], label='pack case')
    ax[0].set_ylabel('degC'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3); ax[0].set_title(title)
    ax[1].plot(tm, s['T_w'], label='winding'); ax[1].plot(tm, s['T_r'], label='rotor/magnets'); ax[1].plot(tm, s['T_o'], label='oil')
    ax[1].plot(tm, s['Tj'], label='inverter junction'); ax[1].plot(tm, s['T_DL'], label='drive coolant')
    ax[1].set_ylabel('degC'); ax[1].set_xlabel('minutes'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / (f'case-{name}.png' if len(sys.argv) < 3 else f'case-{name}-{sys.argv[2]}.png'), dpi=110); plt.close(fig)

results = {}
def go(name, model, t_end, title, extra=None, every=1):
    t0 = time.time(); model.run(t_end); s = model.series(every)
    r = summarise(name, model, s, extra); r['runtime_s'] = round(time.time() - t0, 1)
    results[name] = r; plot(name, s, title)
    print(name, json.dumps({k: v for k, v in r.items() if k != 'energy_balance'}), '\n   EB:', r['energy_balance'], flush=True)
    return model, s

# (a) 70 mph steady cruise to empty, 35 degC
p = tl.to_arrays(tl.hold(70 * MPH, 6 * 3600, dt=10.0))
go('a_cruise70_35C', tl.Model(35.0, AREA, profile=p, soc0=1.0, soc_stop=0.05), 6 * 3600, '(a) 70 mph cruise to empty, 35 degC')
p = tl.to_arrays(tl.hold(70 * MPH, 6 * 3600, dt=10.0))
go('a2_cruise70_35C_cda044', tl.Model(35.0, AREA, profile=p, soc0=1.0, soc_stop=0.05, cda=0.44), 6 * 3600, '(a2) 70 mph, CdA 0.44')

# (b) 8 full-power sprints 0-125 mph, then 10 min at top speed (rpm-limited ~146 mph), then 125 mph to 10 % SOC
m = tl.M_BIKE + tl.M_RIDER
segs = []
for k in range(8):
    segs += tl.accel_profile(0.0, 125 * MPH, m) + tl.hold(125 * MPH, 30) + tl.brake_profile(125 * MPH, 0.0) + tl.hold(0.0, 15)
segs += tl.accel_profile(0.0, 65.0, m) + tl.hold(65.0, 600) + tl.brake_profile(65.0, 125 * MPH, decel=1.0) + tl.hold(125 * MPH, 4 * 3600)
p = tl.to_arrays(segs)
mb, sb = go('b_sprints_topspeed_125_35C', tl.Model(35.0, AREA, profile=p, soc0=1.0, soc_stop=0.10), p['t'][-1],
            '(b) 8 x 0-125 mph sprints, 10 min at 146 mph, then 125 mph to 10 % SOC, 35 degC')
acc = tl.accel_profile(0.0, 125 * MPH, m); acc60 = tl.accel_profile(0.0, 60 * MPH, m)
results['b_sprints_topspeed_125_35C']['t_0_60_s'] = round(sum(d for d, _, _ in acc60), 2)
results['b_sprints_topspeed_125_35C']['t_0_125_s'] = round(sum(d for d, _, _ in acc), 2)
# phase peaks for (b)
tb = sb['t']; n_spr = sum(d for d, _, _ in (tl.accel_profile(0.0, 125 * MPH, m) + tl.hold(125 * MPH, 30) + tl.brake_profile(125 * MPH, 0.0) + tl.hold(0.0, 15))) * 8
t_top = n_spr + sum(d for d, _, _ in tl.accel_profile(0.0, 65.0, m)) + 600
for lab, lo, hi in (('sprints', 0, n_spr), ('topspeed', n_spr, t_top), ('cruise125', t_top, 1e9)):
    k = (tb >= lo) & (tb < hi)
    if k.any():
        results['b_sprints_topspeed_125_35C'][f'phase_{lab}'] = dict(
            end_min=round(min(hi, tb[-1]) / 60, 1), winding_max=round(float(sb['T_w'][k].max()), 1), magnet_max=round(float(sb['T_r'][k].max()), 1),
            junction_max=round(float(sb['Tj'][k].max()), 1), cell_hotspot_max=round(float(sb['core_peak'][k].max()), 1),
            min_derate=round(float(sb['derate'][k].min()), 3))

# (c) mountain pass: 24 km at 7.5 % (1,800 m), hairpin every 600 m (25 -> 65 mph full power), 5 min at the top,
# then the same road down with regen (capped 45 kW), rider + 40 kg luggage
m_c = tl.M_BIKE + tl.M_RIDER + 40.0
def leg(grade):
    a = tl.accel_profile(25 * MPH, 65 * MPH, m_c, grade=grade, rho=1.0)
    b = tl.brake_profile(65 * MPH, 25 * MPH)
    da = sum(d * v for d, v, _ in a); db = sum(d * v for d, v, _ in b)
    return a + tl.hold(65 * MPH, max(0.0, (600 - da - db) / (65 * MPH))) + b
segs = tl.accel_profile(0, 25 * MPH, m_c) + leg(0.075) * 40 + tl.brake_profile(25 * MPH, 0) + tl.hold(0.0, 300) + \
       tl.accel_profile(0, 25 * MPH, m_c) + leg(-0.075) * 40 + tl.brake_profile(25 * MPH, 0) + tl.hold(0.0, 60)
L = 24000.0
p = tl.to_arrays(segs, grade_fn=lambda d: 0.075 if d < L else -0.075,
                 alt_fn=lambda d: 0.075 * d if d < L else max(0.0, 1800 - 0.075 * (d - L)))
go('c_mountain_35C', tl.Model(35.0, AREA, profile=p, soc0=0.95, m_total=m_c, soc_stop=0.02), p['t'][-1],
   '(c) 1,800 m climb, 40 hairpins at full power, regen descent, 35 degC')

# Motor continuous check: 87 kW at the wheel at 12,000 rpm-equivalent road speed for 20 min (pack drains first)
v12 = 12000 * 2 * math.pi / 60 / tl.RATIO * tl.R_WHEEL
p = tl.to_arrays(tl.hold(v12, 1500, dt=1.0)); p['pw'] = np.full_like(p['t'], 87e3 * tl.BELT_EFF)
go('motor_continuous_87kW_35C', tl.Model(35.0, AREA, profile=p, soc0=1.0, soc_stop=0.05), 1500, 'Motor continuous: 87 kW at 12k rpm, 35 degC')

# (d) DC fast charge 10-80 %
go('d1_dcfc_35C', tl.Model(35.0, AREA, mode='charge', T0=38.0, soc0=0.10), 3600, '(d1) DC fast charge 10-80 %, 35 degC, pack arrives at 38 degC')
go('d1b_dcfc_35C_3C_nolimit_reference', tl.Model(35.0, AREA, mode='charge', T0=38.0, soc0=0.10, chiller_w=4000), 3600,
   '(d1b) same with a 4 kW chiller')
go('d2_dcfc_0C_noheater', tl.Model(0.0, AREA, mode='charge', T0=0.0, soc0=0.10), 3 * 3600, '(d2) 0 degC, cold-soaked, no heater')
go('d3_dcfc_0C_heater5kW', tl.Model(0.0, AREA, mode='charge', T0=0.0, soc0=0.10, heater_w=5000), 3 * 3600, '(d3) 0 degC, 5 kW heater at the station')
# preconditioned: 25 min at 70 mph in 0 degC, heater on for the last 20 min, then charge
p = tl.to_arrays(tl.hold(70 * MPH, 1500, dt=5.0))
pre = tl.Model(0.0, AREA, profile=p, soc0=0.26, T0=0.0, precondition=(300.0, 5000.0), soc_stop=0.0)
go('d4a_precondition_ride_0C', pre, 1500, '(d4a) 25 min ride at 0 degC, heater 5 kW in the last 20 min')
x_end = pre.sol.y[:, -1].copy()
ch = tl.Model(0.0, AREA, mode='charge', soc0=float(x_end[pre.iSOC]), heater_w=5000)
ch.x0 = x_end.copy(); ch.x0[ch.iE:] = 0.0
go('d4b_dcfc_0C_after_precondition', ch, 3 * 3600, '(d4b) charge after preconditioning, 0 degC')

# charge time 10-80 % from each charge run
for k, r in results.items():
    if k.startswith('d') and 'precondition_ride' not in k:
        r['charge_time_10_80_min'] = r['duration_min']

meta = dict(area_side_m2=AREA, note='Lumped-parameter model, thermal-lib.py; fixed-step RK4, dt 0.25 s')
(OUT / ('cases.json' if len(sys.argv) < 3 else f'cases-{sys.argv[2]}.json')).write_text(json.dumps(dict(meta=meta, results=results), indent=1, default=float))
print('wrote', OUT / 'cases.json')
