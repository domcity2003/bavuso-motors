"""Bavuso V1 charging: DC fast charge 10-80% on NACS / CCS1 400 V-class chargers, and AC.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drive-charge.py
Writes program/data/drive-charge.json
Cell limits: Molicel P60B data sheet v0.1: standard charge 6 A, maximum 30 A (5C), 70 C cell cut-off, charge window -20..60 C.
Thermal limit used here is MY derating (the data sheet gives no current-vs-temperature curve): 0 A at 0 C, half current at 10 C,
full current 20-40 C, linear to zero at 55 C cell temperature.
"""
import importlib.util, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
dl = _load('drive_lib', 'drive-lib.py')

CHARGERS = {
    'NACS V3 Supercharger (250 kW, 500 V max)': dict(p=250e3, i=600.0, v=500.0),
    'CCS1 150 kW (500 V, 375 A)':               dict(p=150e3, i=375.0, v=500.0),
    'CCS1 50 kW (125 A)':                       dict(p=50e3,  i=125.0, v=500.0),
}
def derate(t):
    if t <= 0: return 0.0
    if t < 10: return 0.5 * t / 10.0
    if t < 20: return 0.5 + 0.5 * (t - 10) / 10.0
    if t <= 40: return 1.0
    if t < 55: return 1.0 - (t - 40) / 15.0
    return 0.0

def dc_charge(charger, c_cap=3.0, t0=25.0, t_amb=25.0, soc0=10.0, soc1=80.0, ua_rad=100.0, ua_pack=300.0, c_cool=14e3, tmax_run=3600.0):
    ch = CHARGERS[charger]
    soc, tc, tcool = soc0, t0, t0
    t, e_in = 0.0, 0.0
    p_peak, tpk, i_cell_peak = 0.0, tc, 0.0
    trace = []
    while soc < soc1 and t < tmax_run:
        r_cell = dl.R_CELL_DC50 * float(dl.np.interp(soc, dl.SOC_PTS, dl.RSOC_PTS)) * dl.r_temp(tc)
        r_pk = dl.N_S / dl.N_P * r_cell * dl.R_PACK_INTERCONNECT + dl.R_PACK_EXTRA
        e0 = dl.ocv_pack(soc)
        i_lim_cell = min(c_cap * dl.CELL_AH, dl.I_CHG_MAX) * derate(tc)
        i = i_lim_cell * dl.N_P
        i = min(i, ch['i'], ch['p'] / max(e0 + i * r_pk, 1.0))
        # per-cell voltage ceiling 4.2 V (constant-voltage taper)
        i_cv = (dl.N_S * 4.2 - e0) / r_pk
        i = max(0.0, min(i, i_cv))
        i = min(i, (ch['v'] - e0) / r_pk)
        if i < 1.0:
            break
        v_term = e0 + i * r_pk
        dt = 2.0
        q_cells = i * i * dl.N_S / dl.N_P * r_cell * dl.R_PACK_INTERCONNECT
        soc += i * dt / (dl.PACK_AH * 3600.0) * 100.0
        tc += (q_cells - ua_pack * (tc - tcool)) * dt / dl.PACK_CAP_J_PER_K
        tcool += (ua_pack * (tc - tcool) - ua_rad * (tcool - t_amb)) * dt / c_cool
        t += dt
        e_in += v_term * i * dt
        p_peak = max(p_peak, v_term * i); tpk = max(tpk, tc); i_cell_peak = max(i_cell_peak, i / dl.N_P)
        if int(t) % 120 == 0:
            trace.append((round(t / 60, 1), round(soc, 1), round(v_term * i / 1e3, 1), round(i / dl.N_P, 1), round(tc, 1)))
    return dict(charger=charger, c_cap=c_cap, t0=t0, t_amb=t_amb, soc0=soc0, soc1=soc1, minutes=round(t / 60.0, 1), reached=soc >= soc1 - 0.01,
                energy_kwh=round(e_in / 3.6e6, 2), avg_kw=round(e_in / max(t, 1) / 1e3, 1), peak_kw=round(p_peak / 1e3, 1),
                peak_cell_a=round(i_cell_peak, 1), peak_cell_c=round(i_cell_peak / dl.CELL_AH, 2), max_cell_temp_c=round(tpk, 1), trace=trace)

out = {}
rows = []
for chg in CHARGERS:
    for c in (2.0, 3.0, 4.0, 5.0):
        r = dc_charge(chg, c)
        rows.append(r)
        print(f"{chg[:28]:28s} cap {c}C: {r['minutes']:5.1f} min  avg {r['avg_kw']:6.1f} kW peak {r['peak_kw']:6.1f} kW cell {r['peak_cell_a']:4.1f} A  Tmax {r['max_cell_temp_c']}")
out['dc_10_80'] = rows
# recommended: NACS V3, 3C cap
rec = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0)
out['recommended'] = rec
print('trace', rec['trace'])
out['dc_10_80_hot_35C'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0, t0=35.0, t_amb=35.0)
out['dc_10_80_hot_35C_5C_cap'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 5.0, t0=35.0, t_amb=35.0)
out['dc_10_80_cold_5C_no_preheat'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0, t0=5.0, t_amb=5.0)
out['dc_10_80_cold_preheated_20C'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0, t0=20.0, t_amb=5.0)
out['dc_10_100'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0, soc1=99.5, tmax_run=7200)
out['dc_10_90'] = dc_charge('NACS V3 Supercharger (250 kW, 500 V max)', 3.0, soc1=90.0, tmax_run=7200)
for k in ('dc_10_80_hot_35C', 'dc_10_80_hot_35C_5C_cap', 'dc_10_80_cold_5C_no_preheat', 'dc_10_80_cold_preheated_20C', 'dc_10_90', 'dc_10_100'):
    r = out[k]; print(k, r['minutes'], 'min', r['reached'], 'avg', r['avg_kw'], 'peak', r['peak_kw'], 'Tmax', r['max_cell_temp_c'])
# miles added in the 10-80 stop at 70 mph (Wh/mi from the range script, 144.7)
wh_mi = 144.7
out['miles_added_10_80_at_70mph'] = round(0.70 * dl.PACK_KWH * 1000 / wh_mi, 0)
# AC
def ac(p_ac_kw, eta=0.94, soc0=10.0, soc1=80.0):
    e_cells_wh = (soc1 - soc0) / 100.0 * dl.PACK_KWH * 1000.0
    e_cells_wh *= 1.02       # IR and CV tail on the cells
    p_dc = p_ac_kw * 1000.0 * eta
    hours = e_cells_wh / p_dc
    return dict(p_ac_kw=p_ac_kw, soc0=soc0, soc1=soc1, hours=round(hours, 2), grid_kwh=round(e_cells_wh / eta / 1000.0, 1))
out['ac'] = [ac(3.3), ac(3.3, soc1=100), ac(3.3, soc0=0, soc1=100), ac(6.6), ac(6.6, soc1=100), ac(6.6, soc0=0, soc1=100), ac(1.4, soc0=10, soc1=100)]
for a in out['ac']: print(a)
json.dump(out, open(os.path.join(HERE, '..', 'data', 'drive-charge.json'), 'w'), indent=1, default=float)
