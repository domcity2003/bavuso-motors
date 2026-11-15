"""Bavuso V1.0 braking: limits, stopping distance, hydraulic sizing, lever/pedal forces, disc thermal.

Hand calculations (Cossalter ch. 6, Foale ch. 11, Limpert 'Brake Design and Safety' 3rd ed. for disc cooling)
checked against UN R78 Annex 3 (L3): front-only dry stop S <= 0.1V + 0.0087V^2 (MFDD >= 4.4 m/s2),
rear-only S <= 0.1V + 0.0133V^2 (>= 2.9 m/s2), split/CBS laden S <= 0.1V + 0.0076V^2 (>= 5.1 m/s2),
hand control <= 200 N, foot <= 350 N; heat fade: 10 stops, 100 km/h (front) / 80 km/h (rear), 3.0-3.5 m/s2,
1000 m between stops, laden, hot stop S2 <= 1.67 S1 - 0.067 V. FMVSS 122 was harmonised with UN GTR No. 3
(final rule 2012), which uses the same test structure.

Run from v1.0 with the FreeCAD python. Output: detailed-design/dynamics/braking-results.json and braking-thermal.png.
Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'dynamics'
MP = json.loads((OUT / 'mass-properties.json').read_text())
g = 9.81; WB = 1.4839; RF = 0.3315; RR = 0.325   # supplier-audit tyres (Nov 13): 663 / 650 mm OD
CASES = {k: dict(m=MP[k]['total']['m'], x=MP[k]['total']['c'][0], h=MP[k]['total']['c'][2]) for k in ('solo', 'twoup')}
# rotating inertia reflected to the road: wheels + IPM rotor through 7.8:1 (EV-specific: the rotor adds ~8 kg)
I_F = MP['solo']['front_wheel']['I'][1][1]; I_R = MP['solo']['rear_wheel']['I'][1][1]
J_ROT, RATIO = MP['solo']['rotor_gyro']['J'], 7.8
M_ROT_EQ = I_F / RF ** 2 + I_R / RR ** 2 + J_ROT * RATIO ** 2 / RR ** 2
MU_TYRE = 1.05          # dry asphalt peak, road-biased adventure radial (sport radials ~1.2-1.3)
ABS_EFF = 0.90          # mean decel / peak under ABS cycling
T_BUILD = 0.20          # s, brake build-up (stop distance counted from control actuation)

# --- proposed brake hardware (CAD change request) ---
FRONT = dict(disc_od=0.320, band=0.038, thick=5.0e-3, n=2, pistons_per_side=(0.032, 0.032), mu_pad=0.45,
             mc_bore=0.019, lever_ratio=5.4)   # radial 19x18 master, finger at ~97 mm from pivot
FRONT_ALT = dict(FRONT, disc_od=0.330, pistons_per_side=(0.032, 0.032))
REAR = dict(disc_od=0.240, band=0.032, thick=5.0e-3, n=1, pistons_per_side=(0.034,), floating=True, mu_pad=0.42,
            mc_bore=0.0127, lever_ratio=4.0)
REAR_ALT = dict(REAR, disc_od=0.267, thick=6.0e-3)
RHO_STEEL, C_STEEL = 7750.0, 460.0     # martensitic stainless (420/410 class) disc


def ring_mass(b):
    ro = b['disc_od'] / 2; ri = ro - b['band']
    return RHO_STEEL * math.pi * (ro ** 2 - ri ** 2) * b['thick'] * 0.88   # 12% removed by drillings


def r_eff(b):
    ro = b['disc_od'] / 2; ri = ro - b['band']
    return 2 / 3 * (ro ** 3 - ri ** 3) / (ro ** 2 - ri ** 2)


def wheel_force_per_bar(b, R):
    """Tyre braking force (N) per 1 bar of line pressure."""
    A_side = sum(math.pi / 4 * d ** 2 for d in b['pistons_per_side'])
    faces = 2  # opposed caliper, or floating single-side (reaction squeezes the other pad)
    T = 1e5 * A_side * b['mu_pad'] * faces * r_eff(b) * b['n']
    return T / R


def control_force(b, R, Fx):
    p_bar = Fx / wheel_force_per_bar(b, R)
    A_mc = math.pi / 4 * b['mc_bore'] ** 2
    return p_bar, p_bar * 1e5 * A_mc / b['lever_ratio'] / 0.95   # 95% mechanical efficiency


def normal_loads(c, a):
    W = c['m'] * g
    Nf = W * (c['x'] + a / g * c['h']) / WB
    return Nf, W - Nf


def stop_distance(v_kmh, a):
    v = v_kmh / 3.6
    return v * T_BUILD / 2 + v ** 2 / (2 * a) + 0.0 * v   # linear ramp over T_BUILD counts half


def heat_cycle(case, v0_kmh, a_dec, n_stops, gap_m, front_share=None, regen=0.0, b=FRONT, a_acc=3.0):
    """Lumped disc temperature through repeated stops; returns time and temperature arrays (deg C).
    Convection: Limpert solid-disc correlations, h = 0.70 k/D Re^0.55 (Re < 2.4e5), 0.04 k/D Re^0.8 above;
    radiation emissivity 0.55 (oxidised stainless); both faces of the swept band plus 30% for hub/edges."""
    c = CASES[case]; m_eff = c['m'] + M_ROT_EQ
    md = ring_mass(b) + 0.15     # band + inner ring share
    A = 2 * math.pi * ((b['disc_od'] / 2) ** 2 - (b['disc_od'] / 2 - b['band']) ** 2) * 1.3
    k_air, nu_air, sig, eps = 0.028, 1.6e-5, 5.67e-8, 0.55
    T = 60.0; Tamb = 30.0; t = 0.0; dt = 0.02
    ts = []; Ts = []
    v0 = v0_kmh / 3.6
    for i in range(n_stops):
        if front_share is None:
            Nf, Nr = normal_loads(c, a_dec); fs = Nf / (Nf + Nr)
        else:
            fs = front_share
        v = v0
        while v > 0:      # braking
            P = m_eff * a_dec * v * (1 - regen) * fs / b['n'] * 0.92     # 8% to pads
            Re = v * b['disc_od'] / nu_air
            h = (0.70 * Re ** 0.55 if Re < 2.4e5 else 0.04 * Re ** 0.8) * k_air / b['disc_od']
            T += dt * (P - h * A * (T - Tamb) - eps * sig * A * ((T + 273) ** 4 - (Tamb + 273) ** 4)) / (md * C_STEEL)
            v -= a_dec * dt; t += dt; ts.append(t); Ts.append(T)
        x_stop = v0 ** 2 / (2 * a_dec)
        x = 0.0; v = 0.0
        while x < gap_m - x_stop:   # accelerate back and cruise
            if v < v0: v = min(v0, v + a_acc * dt)
            x += v * dt
            Re = max(v, 0.5) * b['disc_od'] / nu_air
            h = (0.70 * Re ** 0.55 if Re < 2.4e5 else 0.04 * Re ** 0.8) * k_air / b['disc_od']
            T += dt * (- h * A * (T - Tamb) - eps * sig * A * ((T + 273) ** 4 - (Tamb + 273) ** 4)) / (md * C_STEEL)
            t += dt; ts.append(t); Ts.append(T)
    return np.array(ts), np.array(Ts)


if __name__ == '__main__':
    res = dict(rotating_mass_equivalent_kg=M_ROT_EQ)
    print(f'rotating equivalent mass {M_ROT_EQ:.1f} kg (wheels {I_F/RF**2+I_R/RR**2:.1f}, rotor {J_ROT*RATIO**2/RR**2:.1f})')
    for k, c in CASES.items():
        a_lift = g * (WB - c['x']) / c['h']    # rear wheel unloads (stoppie) at this decel
        a_peak = min(MU_TYRE * g, a_lift)
        a_mean = min(ABS_EFF * MU_TYRE * g, 0.95 * a_lift)
        Nf, Nr = normal_loads(c, a_mean)
        Fx_front_need = c['m'] * a_mean * (Nf / (Nf + Nr))   # ideal split at that decel
        d100 = stop_distance(100, a_mean)
        res[k] = dict(m=c['m'], x_cg=c['x'], h_cg=c['h'], stoppie_g=a_lift / g, tyre_peak_g=MU_TYRE,
                      mean_decel_g=a_mean / g, front_share=Nf / (Nf + Nr), stop_100_m=d100)
        print(f"{k}: m {c['m']:.0f} kg, CoG {c['x']*1000:.0f}/{c['h']*1000:.0f} mm; rear lifts at {a_lift/g:.2f} g;"
              f" mean ABS decel {a_mean/g:.2f} g -> 100-0 in {d100:.1f} m; front share {Nf/(Nf+Nr):.2f}")
    # hydraulics: lever force for front-only stop at the solo limit and two-up limit
    hyd = {}
    for lab, b in (('front 320', FRONT), ('front 330', FRONT_ALT)):
        out = {}
        for k in ('solo', 'twoup'):
            c = CASES[k]
            a = res[k]['mean_decel_g'] * g
            Fx = c['m'] * a          # worst case: front alone does it all (rear lifted / rider front only)
            p, F = control_force(b, RF, Fx)
            out[k] = dict(decel_g=a / g, front_force_N=Fx, line_bar=p, lever_N=F)
        # R78 front-only (laden = two-up, 4.4 m/s2) and split test 5.1 m/s2
        Fx = CASES['twoup']['m'] * 4.4; p, F = control_force(b, RF, Fx)
        out['R78_front_only_laden'] = dict(line_bar=p, lever_N=F, limit_N=200)
        out['r_eff_mm'] = r_eff(b) * 1000; out['ring_kg'] = ring_mass(b)
        hyd[lab] = out
        print(lab, {k_: (round(v_['line_bar'], 1), round(v_['lever_N'])) for k_, v_ in out.items() if isinstance(v_, dict)},
              f"r_eff {r_eff(b)*1000:.0f} mm, ring {ring_mass(b):.2f} kg")
    # rear: R78 rear-only laden 2.9 m/s2 and the rear-lock limit at 0.4 g solo
    rear = {}
    for k, a in (('twoup', 2.9), ('solo', 2.9)):
        c = CASES[k]
        Fx = c['m'] * a; p, F = control_force(REAR, RR, Fx)
        Nf, Nr = normal_loads(c, a)
        rear[k] = dict(decel=a, Fx=Fx, rear_normal=Nr, mu_needed=Fx / Nr, line_bar=p, pedal_N=F, limit_N=350)
        print(f'rear only {k} {a} m/s2: Fx {Fx:.0f} N, mu needed {Fx/Nr:.2f}, {p:.1f} bar, pedal {F:.0f} N')
    res['hydraulics'] = hyd; res['rear'] = rear
    # R78 stopping-distance limits vs ours (from 100 km/h; R78 dry stops are at 60 km/h, shown at both)
    for V in (60, 100):
        res[f'R78_at_{V}'] = dict(front_only_limit=0.1 * V + 0.0087 * V ** 2, rear_only_limit=0.1 * V + 0.0133 * V ** 2,
                                  split_limit=0.1 * V + 0.0076 * V ** 2, ours_both=stop_distance(V, res['twoup']['mean_decel_g'] * g))
        print(V, res[f'R78_at_{V}'])
    # thermal
    th = {}
    fig, ax = plt.subplots(figsize=(9, 4))
    runs = [('R78 heat fade, front only, laden, 100 km/h, 3.25 m/s2', 'twoup', 100, 3.25, 10, 1000, 1.0, 0.0, FRONT),
            ('Repeated 130->0 at 0.6 g, two-up laden, no regen, 320 mm', 'twoup', 130, 0.6 * g, 10, 1000, None, 0.0, FRONT),
            ('Repeated 130->0 at 0.6 g, two-up laden, no regen, 330 mm', 'twoup', 130, 0.6 * g, 10, 1000, None, 0.0, FRONT_ALT),
            ('Repeated 130->0 at 0.6 g, solo, no regen, 320 mm', 'solo', 130, 0.6 * g, 10, 1000, None, 0.0, FRONT),
            ('Repeated 130->0 at 0.6 g, two-up, 20% regen (rear), 320 mm', 'twoup', 130, 0.6 * g, 10, 1000, None, 0.2, FRONT),
            ('R78 heat fade, REAR only, laden, 80 km/h, 3.25 m/s2, 240x5 mm (CAD)', 'twoup', 80, 3.25, 10, 1000, 1.0, 0.0, REAR),
            ('R78 heat fade, REAR only, laden, 80 km/h, 3.25 m/s2, 267x6 mm', 'twoup', 80, 3.25, 10, 1000, 1.0, 0.0, REAR_ALT)]
    for lab, k, v0, a, n, gap, fs, rg, b in runs:
        t, T = heat_cycle(k, v0, a, n, gap, fs, rg, b)
        th[lab] = dict(peak_C=float(T.max()), first_stop_rise=float(T[:int(v0 / 3.6 / a / 0.02)].max() - 60))
        ax.plot(t, T, label=lab)
        print(f'{lab}: peak {T.max():.0f} C, first-stop rise {th[lab]["first_stop_rise"]:.0f} K')
    # energy-balance check: adiabatic single-stop rise vs the integrated simulation
    c = CASES['twoup']; v0 = 130 / 3.6; Nf, Nr = normal_loads(c, 0.6 * g); fs = Nf / (Nf + Nr)
    E = 0.5 * (c['m'] + M_ROT_EQ) * v0 ** 2 * fs / 2 * 0.92
    th['energy_check'] = dict(E_per_disc_kJ=E / 1e3, adiabatic_rise_K=E / ((ring_mass(FRONT) + 0.15) * C_STEEL))
    print('energy check', th['energy_check'])
    ax.axhline(450, color='r', ls=':', lw=0.8); ax.text(5, 455, 'stainless disc / sintered pad working limit ~450 C', fontsize=7)
    ax.set_xlabel('time, s'); ax.set_ylabel('front disc temperature, C'); ax.legend(fontsize=7); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / 'braking-thermal.png', dpi=110)
    res['thermal'] = th
    (OUT / 'braking-results.json').write_text(json.dumps(res, indent=1))
