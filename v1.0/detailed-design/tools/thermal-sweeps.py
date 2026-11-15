"""Thermal study: design-space sweeps on the coupled lumped model (thermal-lib.py).

1. Hot DC fast charge (35 degC): radiator face area per side x chiller size -> 10-80 % time and hottest cell.
2. Same at the chosen point: ambient 25/35/45 degC and cell resistance 3.5/5.0/6.5 mOhm.
3. Cold DC fast charge (0 degC, cold-soaked): station heater power 0/3/5/7 kW.
4. Sustained speed: winding / magnet / junction after 20 min at 110-146 mph, and time to derate at 146 mph.
5. Pack case 3 mm vs 4 mm (the brief vs the CAD).
Writes detailed-design/thermal/sweeps.json and sweep-charge.png.
"""
import json, math, pathlib, importlib.util
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tl', HERE / 'thermal-lib.py'); tl = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl)
OUT = HERE.parent / 'thermal'
MPH = 0.44704
res = {}

def charge(Ta, area, chiller=0.0, heater=0.0, T0=None, r25=None):
    m = tl.Model(Ta, area, mode='charge', T0=(Ta + 3 if T0 is None else T0), soc0=0.10, chiller_w=chiller, heater_w=heater, r25=r25)
    m.run(3 * 3600, dt=0.5); s = m.series()
    done = s['soc'][-1] >= 0.799
    return dict(time_10_80_min=round(s['t'][-1] / 60, 1) if done else None, soc_end=round(float(s['soc'][-1]), 3),
                hotspot_C=round(float(s['core_peak'].max()), 1), pack_spread_K=round(float((s['core_peak'] - s['T_core'].min(axis=0)).max()), 1),
                eb_residual_pct=m.energy_balance()['residual_pct_of_in'])

# 1. design sweep at 35 degC
areas = [0.009, 0.020, 0.029, 0.045, 0.060]; chillers = [0.0, 2000.0, 4000.0]
res['hot_charge_grid'] = []
for a in areas:
    for c in chillers:
        r = dict(area_side_m2=a, chiller_W=c, **charge(35.0, a, c)); res['hot_charge_grid'].append(r); print(r, flush=True)

# 2. robustness at the chosen point (read from argv-free default: 0.035 m2, no chiller)
A0 = 0.029   # chosen: side-pod core, 210 x 140 mm (thermal-cad-pods.py option B)
res['hot_charge_ambient'] = [dict(T_amb=Ta, **charge(Ta, A0)) for Ta in (25.0, 35.0, 40.0, 45.0)]
res['hot_charge_resistance'] = [dict(R25_mohm=r * 1e3, **charge(35.0, A0, r25=r)) for r in (3.5e-3, 5.0e-3, 6.5e-3)]
for k in ('hot_charge_ambient', 'hot_charge_resistance'):
    for r in res[k]: print(k, r, flush=True)

# 3. cold charge heater sweep
res['cold_charge_heater'] = []
for h in (0.0, 3000.0, 5000.0, 7000.0):
    r = dict(heater_W=h, **charge(0.0, A0, heater=h, T0=0.0)); res['cold_charge_heater'].append(r); print(r, flush=True)
res['cold_charge_minus10_heater5kW'] = charge(-10.0, A0, heater=5000.0, T0=-10.0); print('-10C', res['cold_charge_minus10_heater5kW'])

# 4. sustained speed (start at 35 degC soak, 35 degC ambient, 100 % SOC)
res['sustained_speed'] = []
for mph in (110, 120, 125, 130, 135, 140, 146):
    v = min(mph * MPH, 65.0)
    p = tl.to_arrays(tl.hold(v, 1200, dt=1.0))
    m = tl.Model(35.0, A0, profile=p, soc0=1.0, soc_stop=0.05); m.run(1200, dt=0.5); s = m.series()
    k = np.where(s['derate'] < 0.999)[0]
    r = dict(mph=mph, minutes=round(s['t'][-1] / 60, 1), winding_max=round(float(s['T_w'].max()), 1), magnet_max=round(float(s['T_r'].max()), 1),
             junction_max=round(float(s['Tj'].max()), 1), oil_max=round(float(s['T_o'].max()), 1), cell_hotspot=round(float(s['core_peak'].max()), 1),
             motor_loss_kW=round(float(s['q_motor'][-1]) / 1e3, 2), time_to_derate_min=round(float(s['t'][k[0]]) / 60, 1) if len(k) else None,
             min_derate=round(float(s['derate'].min()), 3))
    res['sustained_speed'].append(r); print(r, flush=True)

# 5. pack case 3 vs 4 mm on the hot charge
res['case_wall'] = [dict(case_t_mm=t * 1e3, **{k: v for k, v in (lambda m: (m.run(3600, dt=0.5), dict(
    time_min=round(m.sol.t[-1] / 60, 1), case_heat_MJ=round(m.energy_balance()['to_ambient_MJ'], 3),
    generated_MJ=round(m.energy_balance()['generated_MJ'], 3)))[1])(tl.Model(35.0, A0, mode='charge', T0=38.0, soc0=0.1, case_t=t)).items()})
    for t in (0.003, 0.004)]
print(res['case_wall'])

(OUT / 'sweeps.json').write_text(json.dumps(res, indent=1, default=float))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for c in chillers:
    rows = [r for r in res['hot_charge_grid'] if r['chiller_W'] == c]
    ax[0].plot([r['area_side_m2'] * 2 for r in rows], [r['time_10_80_min'] for r in rows], 'o-', label=f'chiller {c/1e3:.0f} kW')
    ax[1].plot([r['area_side_m2'] * 2 for r in rows], [r['hotspot_C'] for r in rows], 'o-', label=f'chiller {c/1e3:.0f} kW')
ax[0].set_xlabel('total radiator face area, m2'); ax[0].set_ylabel('10-80 % at 35 degC, min'); ax[0].grid(alpha=.3); ax[0].legend()
ax[1].set_xlabel('total radiator face area, m2'); ax[1].set_ylabel('hottest cell core, degC'); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'sweep-charge.png', dpi=110)
print('wrote sweeps.json')
