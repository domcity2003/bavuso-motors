"""Bavuso V1.0 suspension: front fork spring/air-gap/preload optimum, rear check, ride and hop frequencies,
damping targets, travel used under braking, cornering and two-up load. Also load transfer, wheelie limit and squat.

Inputs: mass-properties.json (dyn-massprops.py); rear geometry from rear-suspension.md (leverage 2.33 at sag,
109 N/mm spring, 170 mm wheel travel, anti-squat 125% at sag); fork 170 mm travel along a 25 deg axis
(build-adventure.py FRONT_TRAVEL); drive torque from drive-study.md (150 Nm x 7.8 x 0.93, rolling radius 305 mm).
Outputs: detailed-design/dynamics/suspension-results.json.

Run from v1.0 with the FreeCAD python. Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())
g = 9.81; WB = 1.4839; EPS = math.radians(25)   # wheelbase with the supplier-audit 663 mm front tyre
TRAVEL_F = 170.0                      # mm along the fork axis
TRAVEL_R = 170.0                      # mm vertical at the wheel
LR = 2.33                             # rear leverage at sag (rear-suspension.md)
K_REAR_SPRING = 109.0                 # N/mm (rear-suspension.md)
KT_F, KT_R = 175.0, 210.0             # N/mm tyre radial stiffness, 120/70R19 @2.5 bar, 160/60R17 @2.9 bar (typical radial values)
A_AIR = math.pi / 4 * 0.040 ** 2      # m2: effective air-displacement area per leg (48 mm USD with cartridge: ~40 mm equivalent)
GAMMA = 1.3                           # polytropic index (fast stroke)
UNSPRUNG_F = MP['solo']['front_wheel']['m'] + 6.3   # wheel + inner tubes, axle feet, calipers, half fender (kg)
UNSPRUNG_R = 19.3                      # mass-rollup.json
T_WHEEL_MAX = 150 * 7.8 * 0.93         # Nm at the rear wheel (drive-study.md)
R_ROLL = 0.318                          # rolling radius of the 650 mm OD rear (~0.98 x free radius)


def axle_loads(case, ax=0.0):
    """Static (and longitudinal-acceleration) vertical loads, N; ax > 0 accelerating, < 0 braking."""
    c = MP[case]['total']; m = c['m']; x, h = c['c'][0], c['c'][2]
    Nf = m * g * x / WB - m * ax * h / WB
    return Nf, m * g - Nf


def fork_force(x_mm, k_leg, preload, air_gap):
    """Total axial force of both legs at axial compression x (mm): coil + trapped air (per leg gas column)."""
    coil = 2 * k_leg * (preload + x_mm)
    air = 2 * 101325 * A_AIR * ((air_gap / max(air_gap - x_mm, 1.0)) ** GAMMA - 1)
    return coil + air


def fork_x(F, k_leg, preload, air_gap):
    lo, hi = 0.0, TRAVEL_F + 60
    if fork_force(0, k_leg, preload, air_gap) >= F:
        return 0.0
    for _ in range(60):
        m = (lo + hi) / 2
        if fork_force(m, k_leg, preload, air_gap) < F: lo = m
        else: hi = m
    return (lo + hi) / 2


def fork_axial_load(Nf, Fx_brake=0.0):
    return Nf * math.cos(EPS) + Fx_brake * math.sin(EPS)


def fork_rate(x, k_leg, preload, air_gap):
    return (fork_force(x + 0.5, k_leg, preload, air_gap) - fork_force(x - 0.5, k_leg, preload, air_gap))


def ride_freq(k_axial, m_sprung, kt):
    kv = k_axial / math.cos(EPS) ** 2
    kr = 1 / (1 / kv + 1 / kt)
    return math.sqrt(kr * 1000 / m_sprung) / (2 * math.pi), kv


if __name__ == '__main__':
    res = {}
    # ---------------- rear check ----------------
    rear = {}
    kw = K_REAR_SPRING / LR ** 2
    for case in ('solo', 'twoup'):
        Nf, Nr = axle_loads(case)
        ms = (Nr - UNSPRUNG_R * g) / g
        kr = 1 / (1 / kw + 1 / KT_R)
        f = math.sqrt(kr * 1000 / ms) / (2 * math.pi)
        rear[case] = dict(axle_N=Nr, sprung_N=Nr - UNSPRUNG_R * g, wheel_rate=kw, ride_hz=f,
                          c_crit_wheel_Ns_m=2 * math.sqrt(kw * 1000 * ms))
    # preload for 51 mm sag solo; sag two-up with the 20 mm adjuster added
    pre_solo = rear['solo']['sprung_N'] / kw - 51.0                 # mm at the wheel
    sag_two = rear['twoup']['sprung_N'] / kw - (pre_solo + 20 * LR)
    rear['preload_wheel_mm_solo'] = pre_solo; rear['preload_spring_mm_solo'] = pre_solo / LR
    rear['sag_twoup_with_20mm_adjuster'] = sag_two
    rear['hop_hz'] = math.sqrt((KT_R + kw) * 1000 / UNSPRUNG_R) / (2 * math.pi)
    for case in ('solo', 'twoup'):
        cc = rear[case]['c_crit_wheel_Ns_m']
        rear[case]['shock_c_comp_zeta0.25_Ns_m'] = 0.25 * cc * LR ** 2
        rear[case]['shock_c_reb_zeta0.5_Ns_m'] = 0.5 * cc * LR ** 2
    res['rear'] = rear
    print('rear', json.dumps(rear, indent=0)[:900])
    # ---------------- front optimum ----------------
    Nf_s, _ = axle_loads('solo'); Nf_t, _ = axle_loads('twoup')
    ms_f = (Nf_s - UNSPRUNG_F * g) / g
    F_static = fork_axial_load(Nf_s - UNSPRUNG_F * g)
    F_static_t = fork_axial_load(Nf_t - UNSPRUNG_F * g)
    # hardest braking: 0.94 g mean ABS decel solo and two-up (tyre-limited, dyn-braking.py)
    def brake_case(case, a):
        m = MP[case]['total']['m']; Nf, Nr = axle_loads(case, -a * g)
        return fork_axial_load(Nf - UNSPRUNG_F * g, m * a * g * min(1.0, Nf / (Nf + Nr) + 0.1))
    F_brake_s = brake_case('solo', 0.94); F_brake_t = brake_case('twoup', 0.94)
    F_corner = F_static / math.cos(math.radians(45))       # 45 deg steady lean: 1.41 g
    f_rear = rear['solo']['ride_hz']
    best = None; table = []
    for k_leg in np.arange(5.0, 14.01, 0.25):         # N/mm per leg
        for air in np.arange(110.0, 260.1, 10.0):       # mm equivalent air column
            # preload sets 30% sag solo (51 mm); allowed 0..35 mm
            lo, hi = -50.0, 200.0
            for _ in range(50):
                pre = (lo + hi) / 2
                if fork_force(51.0, k_leg, pre, air) < F_static: lo = pre
                else: hi = pre
            pre = (lo + hi) / 2
            if pre < 0 or pre > 35:
                continue
            x_t = fork_x(F_static_t, k_leg, pre, air)
            x_bs = fork_x(F_brake_s, k_leg, pre, air); x_bt = fork_x(F_brake_t, k_leg, pre, air)
            x_c = fork_x(F_corner, k_leg, pre, air)
            k_ax = fork_rate(51.0, k_leg, pre, air)
            f, kv = ride_freq(k_ax, ms_f, KT_F)
            reserve = TRAVEL_F - max(x_bs, x_bt)
            ok = reserve >= 15 and (TRAVEL_F - x_c) >= 40 and x_t <= 0.40 * TRAVEL_F
            score = abs(f - f_rear * 1.0) + (0 if ok else 10) + 0.002 * pre
            row = dict(k_leg=k_leg, air_gap=air, preload=pre, sag_twoup=x_t, x_brake_solo=x_bs, x_brake_twoup=x_bt,
                       x_corner45=x_c, ride_hz=f, k_axial_at_sag=k_ax, ok=ok)
            table.append(row)
            if best is None or score < best[0]:
                best = (score, row)
    fr = best[1]
    k_ax = fr['k_axial_at_sag']; kv = k_ax / math.cos(EPS) ** 2
    cc_wheel = 2 * math.sqrt(kv * 1000 * ms_f)
    fr.update(sprung_kg=ms_f, static_axial_N=F_static, brake_axial_solo_N=F_brake_s, brake_axial_twoup_N=F_brake_t,
              corner45_axial_N=F_corner, wheel_rate_vertical=kv, c_crit_wheel_Ns_m=cc_wheel,
              fork_c_comp_axial_zeta025_Ns_m=0.25 * cc_wheel * math.cos(EPS) ** 2,
              fork_c_reb_axial_zeta05_Ns_m=0.5 * cc_wheel * math.cos(EPS) ** 2,
              hop_hz=math.sqrt((KT_F + kv) * 1000 / UNSPRUNG_F) / (2 * math.pi), unsprung_kg=UNSPRUNG_F)
    res['front_optimum'] = fr
    res['front_candidates_ok'] = sum(1 for r in table if r['ok'])
    # coil-only check of the same spring (shows why the air column matters)
    fr['coil_only_x_brake_solo'] = (F_brake_s / (2 * fr['k_leg'])) - fr['preload']
    print('front optimum', json.dumps(fr, indent=0))
    # ---------------- load transfer, wheelie, squat ----------------
    lt = {}
    for case in ('solo', 'twoup', 'bike_only'):
        c = MP[case]['total']; m = c['m']; x, h = c['c'][0], c['c'][2]
        a_wheelie = g * x / h                            # front unloads (x = CoG ahead of the rear axle)
        F_drive = T_WHEEL_MAX / R_ROLL
        a_drive = F_drive / (m + 18.5)                   # rotating equivalent mass from dyn-braking.py
        Nf, Nr = axle_loads(case, min(a_drive, a_wheelie))
        lt[case] = dict(m=m, a_wheelie_g=a_wheelie / g, drive_force_N=F_drive, a_full_torque_g=a_drive / g,
                        front_load_at_full_torque_N=Nf, rear_load_N=Nr, rear_mu_needed=F_drive / max(Nr, 1),
                        wheelie=a_drive >= a_wheelie)
    # squat: with anti-squat AS, rear load transfer dW = m a h / WB; squat force at the wheel = (1-AS) dW
    AS = 1.25
    for case in ('solo', 'twoup'):
        c = MP[case]['total']; m = c['m']; h = c['c'][2]
        a = min(lt[case]['a_full_torque_g'], lt[case]['a_wheelie_g']) * g
        dW = m * a * h / WB
        lt[case]['rear_extension_mm_at_full_torque'] = (AS - 1) * dW / kw   # + = rear rises (jacks)
        lt[case]['front_extension_mm'] = dW * math.cos(EPS) / fork_rate(51, fr['k_leg'], fr['preload'], fr['air_gap'])
    lt['anti_squat_used'] = AS
    res['load_transfer'] = lt
    print('load transfer', json.dumps(lt, indent=0))
    (OUT / 'suspension-results.json').write_text(json.dumps(res, indent=1))
