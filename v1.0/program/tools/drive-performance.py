"""Bavuso V1 drive performance: acceleration, roll-on, top speed, 125 mph thermal, low-SOC sag, regen.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drive-performance.py
Writes program/data/drive-performance.json and program/data/drive-accel-trace.csv
Drive: EMRAX 228 LC LV+43% winding, Cascadia CM200DX, 8MGT belt 35T/126T (G = 3.600), 150/70R17 rear tyre.
Bike 240 kg + 90 kg rider.
"""
import importlib.util, json, math, os, csv

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
dl = _load('drive_lib', 'drive-lib.py')
DATA = os.path.join(HERE, '..', 'data')
G = 126.0 / 35.0
drv = dl.Drive(G)
MPH = dl.MPH
out = {'G': G}

# ------------------------------------------------------------ 1. acceleration table
def run(v0, v1, soc, tp, mu=1.0, cda=dl.CDA, log=None):
    return dl.accel_run(drv, v0 * MPH, v1 * MPH, soc=soc, t_pack=tp, mu=mu, cda=cda, log=log)

acc = []
cases = [('SOC 90, 25 C', 90, 25), ('SOC 50, 25 C', 50, 25), ('SOC 20, 25 C', 20, 25), ('SOC 10, 25 C', 10, 25), ('SOC 5, 25 C', 5, 25), ('SOC 90, 5 C', 90, 5), ('SOC 20, 5 C', 20, 5)]
for name, soc, tp in cases:
    r60 = run(0, 60, soc, tp)
    rk = dl.accel_run(drv, 0, 100 / 3.6, soc=soc, t_pack=tp)
    r100 = run(0, 100, soc, tp)
    ro = run(60, 100, soc, tp)
    acc.append(dict(case=name, zero_60_s=round(r60['t'], 2), zero_100kmh_s=round(rk['t'], 2), zero_100mph_s=round(r100['t'], 2), rollon_60_100_s=round(ro['t'], 2),
                    v_bus_min_V=round(r100['v_min']), i_dc_peak_A=round(r100['i_pk'])))
    print(acc[-1])
out['acceleration'] = acc
# luggage case (T7: +25 kg) and low-grip case
dl_M = dl.M_TOT
dl.M_TOT = dl_M + 25.0
rl = run(0, 60, 90, 25)
dl.M_TOT = dl_M
out['zero_60_with_25kg_luggage'] = round(rl['t'], 2)
out['zero_60_mu_0.7_wet'] = round(run(0, 60, 90, 25, mu=0.7)['t'], 2)
out['zero_60_cda_0.43'] = round(run(0, 60, 90, 25, cda=0.43)['t'], 2)
print('luggage', out['zero_60_with_25kg_luggage'], 'wet', out['zero_60_mu_0.7_wet'])
out['traction_cap_g_mu1'] = round(dl.traction_limit_a(1.0) / dl.G0, 2)
out['launch_g_motor_limited'] = round((220 * G * dl.ETA_BELT_PEAK / dl.R_E0) / (dl.M_TOT + dl.rot_mass(G)) / dl.G0, 2)

log = []
run(0, 100, 90, 25, log=log)
with open(os.path.join(DATA, 'drive-accel-trace.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['t_s', 'v_mph', 'a_g', 'motor_torque_Nm', 'dc_kW', 'bus_V', 'motor_rpm'])
    for i, rw in enumerate(log):
        if i % 10 == 0: w.writerow([round(x, 3) for x in rw])

# ------------------------------------------------------------ 2. top speed: power-limited vs speed-limited
def avail_force(v, soc, tp, tw=60.0):
    T, vb, e = drv.max_torque(v, soc, tp, tw)
    return drv.wheel_force(T, v), T, vb, e

def power_limited_top(soc, tp, cda=dl.CDA, tcap=None):
    """Highest speed where peak wheel force >= road load, with the rpm cap removed (model extends to 7200 rpm)."""
    lo, hi = 30.0, 80.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        F, T, vb, e = avail_force(mid, soc, tp)
        if tcap is not None:
            F = min(F, drv.wheel_force(tcap, mid))
        if F >= dl.road_force(mid, cda):
            lo = mid
        else:
            hi = mid
    return lo

rpm_cap_v = 6500 / (G * 30 / math.pi)       # rad/s of wheel at 6500 rpm -> v = w * r_eff
v_rpm = None
lo, hi = 30.0, 90.0
for _ in range(40):
    mid = 0.5 * (lo + hi)
    if drv.rpm(mid) <= 6500: lo = mid
    else: hi = mid
v_rpm = lo
T_CONT = 118.0 * 300.0 / 330.0   # inverter-limited continuous torque, Nm
top = []
for soc in (100, 50, 20, 10):
    for cda in (0.38, 0.43):
        pl = power_limited_top(soc, 25, cda)
        pl_cont = power_limited_top(soc, 25, cda, tcap=T_CONT)
        top.append(dict(soc=soc, cda=cda, power_limited_peak_mph=round(pl / MPH, 1), power_limited_continuous_mph=round(pl_cont / MPH, 1),
                        rpm_limited_mph=round(v_rpm / MPH, 1), top_mph=round(min(pl, v_rpm) / MPH, 1), limited_by='speed (6500 rpm)' if v_rpm < pl else 'power'))
        print(top[-1])
out['top_speed'] = top
out['governor_mph'] = 130

# power needed at speed (wheel and battery) at CdA 0.38 / 0.43
need = []
for mph in (70, 77, 100, 125, 130):
    v = mph * MPH
    pw = dl.road_force(v) * v
    pw43 = dl.road_force(v, 0.43) * v
    need.append(dict(mph=mph, wheel_kw=round(pw / 1e3, 1), wheel_kw_cda043=round(pw43 / 1e3, 1)))
out['road_power'] = need

# ------------------------------------------------------------ 3. cruise point and 125 mph thermal
def cruise(v, soc, tp, tw, cda=dl.CDA):
    pw = dl.road_force(v, cda) * v
    p_shaft = pw + dl.belt_loss(pw)
    n = drv.rpm(v)
    w_m = n * math.pi / 30.0
    T = p_shaft / w_m
    e = drv.electrical(T, n, soc, tp, tw, p_aux=dl.AUX_W)
    return T, n, pw, p_shaft, e

rad_ua = lambda v: 55.0 + 3.6 * v      # W/K radiator + ram air, grows with speed [est]
def thermal_run(mph, t_amb, soc0=95.0, minutes=60, cda=dl.CDA, ua_scale=1.0):
    v = mph * MPH
    soc, tp, tw, ti, tc = soc0, t_amb, t_amb, t_amb, t_amb
    C_COOL, UA_PACK, UA_MOT, UA_INV, C_INV = 14e3, 300.0, 1.0 / dl.RTH_WINDING, 40.0, 3e3
    t, dist = 0.0, 0.0
    hist = []
    stop = 'time'
    while t < minutes * 60.0:
        T, n, pw, ps, e = cruise(v, soc, tp, tw, cda)
        if e is None or e['i_dc'] > dl.I_PACK_CAP:
            stop = 'power'; break
        q_pack = e['p_pack_loss']
        q_mot = e['cu'] + e['fe']
        q_inv = e['p_inv']
        dt = 5.0
        soc -= e['i_dc'] * dt / (dl.PACK_AH * 3600.0) * 100.0
        tp += (q_pack - UA_PACK * (tp - tc)) * dt / dl.PACK_CAP_J_PER_K
        tw += (q_mot - UA_MOT * (tw - tc)) * dt / dl.C_MOTOR
        ti += (q_inv - UA_INV * (ti - tc)) * dt / C_INV
        q_rad = rad_ua(v) * ua_scale * (tc - t_amb)
        tc += (UA_PACK * (tp - tc) + UA_MOT * (tw - tc) + UA_INV * (ti - tc) - q_rad) * dt / C_COOL
        t += dt; dist += v * dt
        if int(t) % 300 == 0:
            hist.append((round(t / 60), round(soc, 1), round(tp, 1), round(tw, 1), round(ti, 1), round(tc, 1)))
        if soc <= dl.USABLE_SOC[0]:
            stop = 'soc 5%'; break
    last = dict(T=T, n=n, wheel_kw=pw / 1e3, i_dc=e['i_dc'] if e else None, i_rms=e['i_rms'] if e else None, q_pack_kw=q_pack / 1e3, q_mot_kw=q_mot / 1e3, q_inv_kw=q_inv / 1e3)
    return dict(mph=mph, t_amb=t_amb, minutes=round(t / 60, 1), miles=round(dist / 1609.344, 1), stop=stop, pack_c=round(tp, 1), winding_c=round(tw, 1),
                inverter_case_c=round(ti, 1), coolant_c=round(tc, 1), soc_end=round(soc, 1), steady=last, hist=hist)
th = []
for mph in (125, 130):
    for ta in (25, 38):
        r = thermal_run(mph, ta)
        th.append(r)
        print({k: v for k, v in r.items() if k not in ('hist',)})
out['thermal'] = th
# radiator 40% smaller sensitivity
r = thermal_run(125, 38, ua_scale=0.6)
out['thermal_hot_small_radiator'] = {k: v for k, v in r.items() if k != 'hist'}
print('hot, 0.6x radiator', out['thermal_hot_small_radiator'])
# steady operating point at 125 mph with margins vs continuous ratings
T, n, pw, ps, e = cruise(125 * MPH, 50, 35, 80)
out['op125'] = dict(motor_torque_nm=round(T, 1), motor_rpm=round(n), wheel_kw=round(pw / 1e3, 1), motor_shaft_kw=round(ps / 1e3, 1), i_rms=round(e['i_rms']), i_dc=round(e['i_dc']),
                    bus_v=round(e['vbus']), motor_loss_kw=round((e['cu'] + e['fe']) / 1e3, 2), inv_loss_kw=round(e['p_inv'] / 1e3, 2), pack_loss_kw=round(e['p_pack_loss'] / 1e3, 2),
                    cell_a=round(e['i_dc'] / dl.N_P, 1), cell_c_rate=round(e['i_dc'] / dl.N_P / dl.CELL_AH, 2),
                    motor_i_vs_inverter_cont=round(e['i_rms'] / 300.0, 2), torque_vs_cont=round(T / T_CONT, 2),
                    drivetrain_eff_pct=round(100 * pw / (e['p_dc'] + dl.AUX_W), 1))
print(out['op125'])

# ------------------------------------------------------------ 4. low-SOC sag table (peak power at the motor)
sag = []
for soc in (100, 80, 50, 20, 10, 5):
    for tp in (25, 5):
        T, vb, e = drv.max_torque(26.82 * 2.2, soc, tp, 60.0)       # about 130 mph? no: 59 m/s -> use 5500 rpm point
        v55 = 5500 / (G * 30 / math.pi) * dl.r_eff(40.0)
        T55, vb55, e55 = drv.max_torque(v55, soc, tp, 60.0)
        Tl, vbl, el = drv.max_torque(2.0, soc, tp, 40.0)
        sag.append(dict(soc=soc, t_c=tp, ocv=round(dl.ocv_pack(soc)), v_loaded_5500rpm=round(vb55), torque_5500rpm=round(T55), p_mech_5500rpm_kw=round(T55 * 5500 * math.pi / 30 / 1e3, 1),
                        launch_torque=round(Tl), launch_vbus=round(vbl), i_dc_5500rpm=round(e55['i_dc']) if e55 else None))
        print(sag[-1])
out['sag'] = sag

# ------------------------------------------------------------ 5. regen
def regen_stop(v0_mph, v1_mph=0.0, a_cap_g=0.25, soc=60.0, tp=25.0, chg_c=3.0):
    """Coast-down with regen on the rear wheel only; the front brake supplies the rest (not counted).  Returns recovered kWh and KE."""
    v = v0_mph * MPH
    tw = 60.0
    e_in = 0.0
    t = 0.0
    dt = 0.02
    ke0 = 0.5 * (dl.M_TOT + dl.rot_mass(G)) * v * v
    while v > v1_mph * MPH + 0.2:
        n = drv.rpm(v)
        # charge limit: pack current <= chg_c C per cell, taper to 0 at 100% SOC
        taper = max(0.0, min(1.0, (97.0 - soc) / 17.0))
        i_lim = chg_c * dl.CELL_AH * dl.N_P * taper
        vb = dl.ocv_pack(soc)
        t_map = min(drv.mmap.tmax(n, vb), 220.0)
        t_grip = a_cap_g * dl.G0 * (dl.M_TOT + dl.rot_mass(G)) * dl.r_eff(v) / (G * dl.ETA_BELT_PEAK)    # rear-only decel cap
        T = min(t_map, t_grip)
        for _ in range(30):
            e = drv.electrical(-T, n, soc, tp, tw)
            if e is None or -e['i_dc'] > i_lim:
                T *= 0.9
            else:
                break
        e = drv.electrical(-T, n, soc, tp, tw)
        if e is None:
            break
        f_reg = T * G * dl.ETA_BELT_PEAK / dl.r_eff(v)
        a = (f_reg + dl.road_force(v)) / (dl.M_TOT + dl.rot_mass(G))
        e_in += -e['p_dc'] * dt
        soc += -e['i_dc'] * dt / (dl.PACK_AH * 3600.0) * 100.0
        v -= a * dt
        t += dt
    return dict(v0_mph=v0_mph, kinetic_kwh=round(ke0 / 3.6e6, 4), recovered_kwh=round(e_in / 3.6e6, 4), recovered_pct_of_ke=round(100 * e_in / ke0, 1), time_s=round(t, 1),
                regen_peak_decel_g=round(a_cap_g, 2))
reg = []
for v0 in (70, 50, 30):
    for cap in (0.15, 0.25, 0.35):
        reg.append(regen_stop(v0, a_cap_g=cap))
        print(reg[-1])
out['regen'] = reg
out['regen_cold_5C_70mph'] = regen_stop(70, a_cap_g=0.25, tp=5.0, chg_c=1.0)
out['regen_soc95_70mph'] = regen_stop(70, a_cap_g=0.25, soc=95.0)
out['regen_max_torque_nm'] = 220
out['regen_peak_kw_at_5500rpm'] = round(220 * 5500 * math.pi / 30 / 1e3 * 0.85, 1)
json.dump(out, open(os.path.join(DATA, 'drive-performance.json'), 'w'), indent=1, default=float)
print('wrote drive-performance.json')
