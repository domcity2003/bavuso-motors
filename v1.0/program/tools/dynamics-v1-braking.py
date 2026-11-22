"""V1 dynamics step 4: braking and launch. Load transfer, ideal split, 1.0 g stop distance, stoppie and wheelie limits,
disc temperature for a 125-mph-to-0 stop.

Inputs: program/data/dynamics/mass-properties.json (rev D CG and inertias; three load cases), the 0-60 3.95 s launch from
program/06-drive-performance.md (peak torque 220 Nm, ratio 3.6, 0.712 g at 330 kg), disc sizes from the CAD (dual 320x5 front,
267x5 rear). Method: the hand calculations of detailed-design/tools/dyn-braking.py (Cossalter ch. 6, Limpert for disc cooling),
extended with aero drag and rolling resistance in the thermal model.
Outputs: program/data/dynamics/braking-results.json and braking-thermal.png.
Run from v1.0 with the FreeCAD python. November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'data' / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())
CAD = json.loads((OUT / 'cad-extract.json').read_text())
g = 9.81; MPH = 0.44704
WB = MP['geometry']['wheelbase_mm'] / 1000
RF, RR = 0.3315, 0.325
CASES = {k: dict(m=MP[k]['total']['m'], x=MP[k]['total']['c'][0], h=MP[k]['total']['c'][2]) for k in ('bike_only', 'solo', 'solo_luggage')}
LAB = {'bike_only': 'bike alone', 'solo': 'bike + 90 kg rider', 'solo_luggage': 'bike + rider + 25 kg luggage'}
I_F = MP['solo']['front_wheel']['I'][1][1]; I_R = MP['solo']['rear_wheel']['I'][1][1]
J_ROT, RATIO = MP['solo']['rotor_gyro']['J'], 3.6
M_ROT_EQ = I_F / RF ** 2 + I_R / RR ** 2 + J_ROT * RATIO ** 2 / RR ** 2      # rotating inertia seen at the road, kg
MU = 1.05          # dry asphalt peak, road-biased adventure radial (estimate)
ABS_EFF = 0.90     # mean decel / peak under ABS
T_BUILD = 0.20     # s brake build-up, counted from control actuation
CDA, CRR, RHO_AIR = 0.38, 0.015, 1.2
RHO_STEEL, C_STEEL = 7750.0, 460.0
# launch (06-drive-performance.md): 0.712 g at t=0 for 330 kg (bike 240 + rider 90); rolling radius 0.3145 m
F_LAUNCH = 0.712 * g * (330.0 + M_ROT_EQ)       # N at the tyre, peak torque 220 Nm x 3.6 x belt/bearing efficiency
T0_60_S = 3.95; T0_60_LUGGAGE_S = 4.24


def loads(c, a):
    """Axle loads at longitudinal acceleration a (m/s2, braking negative)."""
    W = c['m'] * g
    Nf = W * c['x'] / WB - c['m'] * a * c['h'] / WB
    return Nf, W - Nf


def limits(c):
    x, h = c['x'], c['h']
    return dict(
        stoppie_g=(WB - x) / h,                 # rear unloads
        front_only_tyre_g=MU * x / (WB - MU * h),   # front tyre alone reaches mu (below the stoppie limit when smaller)
        rear_only_dry_g=MU * (WB - x) / (WB + MU * h),
        rear_only_wet_mu05_g=0.5 * (WB - x) / (WB + 0.5 * h),
        wheelie_g=x / h,                        # front unloads under drive
        traction_limited_accel_dry_g=MU * (WB - x) / (WB - MU * h),
        traction_limited_accel_wet_mu07_g=0.7 * (WB - x) / (WB - 0.7 * h))


def stop(v_mph, a_g, build=T_BUILD):
    v = v_mph * MPH
    return v * build / 2 + v ** 2 / (2 * a_g * g)


def ring(vol_mm3):
    return vol_mm3 * 7.75e-6      # kg, steel disc from the CAD volume


def disc_geom(name, od_mm, thick_mm):
    vol = CAD[name]['volume']
    ro = od_mm / 2; ri = math.sqrt(max(ro ** 2 - vol / (math.pi * thick_mm), 1.0))
    return dict(m=ring(vol), od=od_mm / 1000, band=(ro - ri) / 1000, thick=thick_mm / 1000, vol_mm3=vol)


FRONT = dict(disc_geom('Front_disc_p1', 320, 5), n=2, mu_pad=0.45)
REAR = dict(disc_geom('Rear_disc_p1', 267, 5), n=1, mu_pad=0.42)
REAR_6 = dict(REAR, m=REAR['m'] * 6 / 5, thick=6e-3)       # alternative: 267 x 6 mm (mass scaled from the CAD volume)


def heat(case, v0_mph, a_dec, n_stops, gap_m, fs, b, share_of_front=True, T0=60.0, Tamb=30.0, extra_m=0.10, a_acc=3.0, drag=True):
    """Lumped disc temperature through repeated stops (Limpert convection, radiation); fs = share of the braking force on this axle,
    divided over b['n'] discs. Aero drag and rolling resistance help the brakes (they are removed from the brake force)."""
    c = CASES[case]; m_eff = c['m'] + M_ROT_EQ
    md = b['m'] + extra_m
    A = 2 * math.pi * ((b['od'] / 2) ** 2 - (b['od'] / 2 - b['band']) ** 2) * 1.3
    k_air, nu_air, sig, eps = 0.028, 1.6e-5, 5.67e-8, 0.55
    T = T0; t = 0.0; dt = 0.02; ts = []; Ts = []
    v0 = v0_mph * MPH
    for i in range(n_stops):
        v = v0
        while v > 0:
            Fd = (0.5 * RHO_AIR * CDA * v * v + CRR * c['m'] * g) if drag else 0.0
            Fb = max(m_eff * a_dec - Fd, 0.0)
            P = Fb * v * fs / b['n'] * 0.92
            Re = v * b['od'] / nu_air
            h = (0.70 * Re ** 0.55 if Re < 2.4e5 else 0.04 * Re ** 0.8) * k_air / b['od']
            T += dt * (P - h * A * (T - Tamb) - eps * sig * A * ((T + 273) ** 4 - (Tamb + 273) ** 4)) / (md * C_STEEL)
            v -= a_dec * dt; t += dt; ts.append(t); Ts.append(T)
        x_stop = v0 ** 2 / (2 * a_dec); x = 0.0; v = 0.0
        while x < gap_m - x_stop:
            if v < v0: v = min(v0, v + a_acc * dt)
            x += v * dt
            Re = max(v, 0.5) * b['od'] / nu_air
            h = (0.70 * Re ** 0.55 if Re < 2.4e5 else 0.04 * Re ** 0.8) * k_air / b['od']
            T += dt * (- h * A * (T - Tamb) - eps * sig * A * ((T + 273) ** 4 - (Tamb + 273) ** 4)) / (md * C_STEEL)
            t += dt; ts.append(t); Ts.append(T)
    return np.array(ts), np.array(Ts)


if __name__ == '__main__':
    res = dict(rotating_mass_equivalent_kg=M_ROT_EQ, F_launch_N=F_LAUNCH, mu_dry=MU, wheelbase_m=WB)
    print(f'rotating equivalent mass {M_ROT_EQ:.1f} kg; launch force {F_LAUNCH:.0f} N; front disc {FRONT}; rear disc {REAR}')
    res['disc_front'] = FRONT; res['disc_rear'] = REAR
    # ---- limits, split, stop distance, launch -----------------------------------------------------------------------
    for k, c in CASES.items():
        L = limits(c)
        r = dict(label=LAB[k], m=c['m'], cg_x_from_rear_axle_mm=c['x'] * 1000, cg_h_mm=c['h'] * 1000, **L)
        # ideal front share of braking force at 0.5, 0.8, 1.0 g, and the rear axle load left
        r['ideal_front_share'] = {}
        for ag in (0.3, 0.5, 0.8, 1.0):
            Nf, Nr = loads(c, -ag * g); r['ideal_front_share'][str(ag)] = dict(front_pct=100 * Nf / (Nf + Nr), rear_load_N=Nr, rear_load_pct_of_static=100 * Nr / ((c['m'] * g) * (WB - c['x']) / WB))
        a_abs = ABS_EFF * MU
        r['abs_mean_decel_g'] = min(a_abs, 0.95 * L['stoppie_g'])
        for v in (60, 77):
            r[f'stop_{v}mph_1g_m'] = stop(v, 1.0)
            r[f'stop_{v}mph_1g_no_buildup_m'] = stop(v, 1.0, 0.0)
            r[f'stop_{v}mph_abs_m'] = stop(v, r['abs_mean_decel_g'])
        r['stoppie_margin_vs_1g_pct'] = 100 * (L['stoppie_g'] / 1.0 - 1)
        # launch: peak force and 0-60 average, wheelie and traction margins
        a_peak = F_LAUNCH / (c['m'] + M_ROT_EQ)
        Nf, Nr = loads(c, a_peak)
        r['launch'] = dict(a_peak_g=a_peak / g, a_avg_0_60_g=(60 * MPH) / (T0_60_S if k == 'solo' else T0_60_LUGGAGE_S) / g if k != 'bike_only' else None,
                           front_load_at_peak_N=Nf, front_load_pct_of_static=100 * Nf / (c['m'] * g * c['x'] / WB),
                           rear_mu_needed=F_LAUNCH / Nr, wheelie_margin_pct=100 * (L['wheelie_g'] * g / a_peak - 1))
        res[k] = r
        print(f"{LAB[k]:30s} m {c['m']:.1f} CG {c['x']*1000:.0f}/{c['h']*1000:.0f}: stoppie {L['stoppie_g']:.2f} g, front-only tyre {L['front_only_tyre_g']:.2f} g, "
              f"rear-only {L['rear_only_dry_g']:.2f} g dry / {L['rear_only_wet_mu05_g']:.2f} wet, wheelie {L['wheelie_g']:.2f} g, launch peak {a_peak/g:.2f} g "
              f"(front keeps {r['launch']['front_load_pct_of_static']:.0f}% of static), stop 60/77 mph at 1.0 g {r['stop_60mph_1g_m']:.1f}/{r['stop_77mph_1g_m']:.1f} m")
    # ---- thermal: 125 mph to 0 ---------------------------------------------------------------------------------------
    th = {}
    fig, ax = plt.subplots(figsize=(9, 4.2))
    runs = []
    for case in ('solo', 'solo_luggage'):
        for ag in (0.6, 0.9):
            Nf, Nr = loads(CASES[case], -ag * g); fs = Nf / (Nf + Nr)
            runs.append((f'{LAB[case]}: 125 to 0 mph at {ag} g, 1 stop, front disc', case, 125, ag * g, 1, 1000, fs, FRONT))
            runs.append((f'{LAB[case]}: 125 to 0 mph at {ag} g, 1 stop, rear disc 267x5', case, 125, ag * g, 1, 1000, 1 - fs, REAR))
        Nf, Nr = loads(CASES[case], -0.6 * g); fs = Nf / (Nf + Nr)
        runs.append((f'{LAB[case]}: 3 stops 125 to 0 mph at 0.6 g, 1 km apart, front disc', case, 125, 0.6 * g, 3, 1000, fs, FRONT))
        runs.append((f'{LAB[case]}: 3 stops 125 to 0 mph at 0.6 g, 1 km apart, rear disc 267x5', case, 125, 0.6 * g, 3, 1000, 1 - fs, REAR))
    # UN R78 rear-only heat fade (10 stops from 80 km/h, 3.25 m/s2, 1 km), laden
    runs.append(('R78 heat fade, rear only, 80 km/h, 10 stops, 267x5', 'solo_luggage', 80 / 1.609344, 3.25, 10, 1000, 1.0, REAR))
    runs.append(('R78 heat fade, rear only, 80 km/h, 10 stops, 267x6', 'solo_luggage', 80 / 1.609344, 3.25, 10, 1000, 1.0, REAR_6))
    runs.append(('R78 heat fade, front only, 100 km/h, 10 stops, 320x5', 'solo_luggage', 100 / 1.609344, 3.25, 10, 1000, 1.0, FRONT))
    for lab, k, v0, a, n, gap, fs, b in runs:
        t, T = heat(k, v0, a, n, gap, fs, b)
        i1 = int(v0 * MPH / a / 0.02)
        th[lab] = dict(peak_C=float(T.max()), first_stop_rise_K=float(T[:i1].max() - 60.0), stops=n, share=fs)
        if 'R78' not in lab and ('0.9 g' in lab or '3 stops' in lab) and 'luggage' not in lab:
            ax.plot(t, T, label=lab)
        print(f'{lab}: peak {T.max():.0f} C (first-stop rise {th[lab]["first_stop_rise_K"]:.0f} K, axle share {fs:.2f})')
    # energy check: adiabatic first-stop rise vs the simulation (one front disc, 0.6 g, no drag shown separately)
    c = CASES['solo']; v0 = 125 * MPH; Nf, Nr = loads(c, -0.6 * g); fs = Nf / (Nf + Nr)
    E_total = 0.5 * (c['m'] + M_ROT_EQ) * v0 ** 2
    E_drag = (0.5 * RHO_AIR * CDA * v0 ** 2 * (v0 ** 2 / (2 * 0.6 * g))) / 2 * (1 / 2) * 1.0   # crude: integral of c v^2 dx with v^2 = v0^2(1 - x/xs) = c v0^2 xs/2
    E_drag = 0.5 * RHO_AIR * CDA * v0 ** 2 * (v0 ** 2 / (2 * 0.6 * g)) / 2
    E_roll = CRR * c['m'] * g * (v0 ** 2 / (2 * 0.6 * g))
    E_disc = (E_total - E_drag - E_roll) * fs / 2 * 0.92
    th['energy_check_solo_0.6g'] = dict(KE_MJ=E_total / 1e6, drag_MJ=E_drag / 1e6, rolling_MJ=E_roll / 1e6, E_per_front_disc_kJ=E_disc / 1e3,
                                         adiabatic_rise_K=E_disc / ((FRONT['m'] + 0.10) * C_STEEL), simulated_first_stop_rise_K=th[f'{LAB["solo"]}: 125 to 0 mph at 0.6 g, 1 stop, front disc']['first_stop_rise_K'])
    print('energy check', th['energy_check_solo_0.6g'])
    ax.axhline(450, color='r', ls=':', lw=0.8); ax.text(2, 455, 'stainless disc / sintered pad working limit ~450 C', fontsize=7)
    ax.set_xlabel('time, s'); ax.set_ylabel('disc temperature, C'); ax.legend(fontsize=6); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / 'braking-thermal.png', dpi=110)
    res['thermal'] = th
    (OUT / 'braking-results.json').write_text(json.dumps(res, indent=1))
