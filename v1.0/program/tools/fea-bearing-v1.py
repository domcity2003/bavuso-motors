"""Pivot bearing L10 life at the duty spectrum (round 2). usage: python fea-bearing-v1.py <variant> [C_kN C0_kN]
November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
Bearing: pair of SKF 32012 X tapered rollers (60 x 95 x 23), C 101 kN, C0 122 kN from distributor listings (CONFIRM with SKF), at Y105 and Y185.
Loads: bearing reaction forces from the frame model (cases C1 static, C6 rear bump, C5L/R, D1, D2, D3). Spectrum: fea-fatigue-v1 bumps, cornering, launches, regen, belt shocks.
Oscillating duty: each load cycle swings the arm; equivalent revolutions per cycle = peak-to-peak angle / 360 deg, travel = 51 mm per g of bump (sag 30 % of 170 mm
at 1 g, calculated), launches/regen/cornering/shock count as 1 mm-travel-equivalent 10 mm swings. P = 1.2 x radial (induced axial allowance). a1 = 1, no contamination factor.
"""
import json, math, sys, importlib.util
from pathlib import Path
H = Path(__file__).resolve().parent; OUT = H.parents[1] / 'program' / 'data' / 'fea'
sp = importlib.util.spec_from_file_location('fat', str(H / 'fea-fatigue-v1.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
var = sys.argv[1]; C = float(sys.argv[2]) if len(sys.argv) > 2 else 101.0; C0 = float(sys.argv[3]) if len(sys.argv) > 3 else 122.0
R = json.loads((OUT / ('results-%s-h12.json' % var)).read_text())
def vec(case, k):
    v = R['cases'][case]['bearing_RF_N'][k]; return (v[0], v[2])   # radial (X, Z)
out = {}; tot_damage = {}
for k in ('stub_in', 'stub_out'):
    c1 = vec('C1_static_1g_solo', k)
    def rad(case, a=1.0):
        v = vec(case, k); return math.hypot(c1[0] + a * (v[0] - c1[0]), c1[1] + a * (v[1] - c1[1]))
    dmg = 0.0; rows = []
    def add(label, a, n, case, scale=1.0, travel_mm=None):
        global dmg
        P = 1.2 * rad(case, a * scale) / 1000.0
        tr = travel_mm if travel_mm is not None else min(170.0, 51.0 * a)
        revs = n * 2 * (tr / 545.0) / (2 * math.pi)            # peak-to-peak angle / 2pi, per cycle
        L10 = (C / P) ** (10 / 3) * 1e6                          # revolutions
        dmg += revs / L10; rows.append((label, a, n, round(P, 1), round(revs / 1e6, 4), dmg))
    for a, n in F.BUMP0: add('bump', a, n, 'C6_rear_bump_3g', scale=0.5)   # C6 is +2 g, so per g = 0.5 of its change
    for a, n in F.LAUNCH0: add('launch', a, n, 'D2_launch_peak_torque', travel_mm=10 * a + 1)
    for a, n in F.REGEN0: add('regen', a, n, 'D3_regen_peak_torque', travel_mm=10 * a + 1)
    for a, n in F.CORNER0: add('cornerL', a, n, 'C5L_corner_lean_left', scale=0.414 / 1.12, travel_mm=20); add('cornerR', a, n, 'C5R_corner_lean_right', scale=0.414 / 1.12, travel_mm=20)
    for a, n in F.SHOCK0: add('belt shock', a, n, 'D1_belt_design_11.3kN', travel_mm=5)
    P_static = max(math.hypot(*vec(c, k)) for c in ('D1_belt_design_11.3kN', 'C6_rear_bump_3g', 'D2_launch_peak_torque'))
    out[k] = dict(design_lives_of_L10=round(1 / dmg, 2) if dmg else None, damage_sum=dmg, max_radial_kN=round(P_static / 1000, 1),
                  static_safety_C0_over_P0=round(C0 / (P_static / 1000), 2), mean_P_static_kN=round(1.2 * rad('C1_static_1g_solo', 0) / 1000, 1) if False else round(1.2 * math.hypot(*c1) / 1000, 1))
print(json.dumps(out, indent=1)); (OUT / ('bearing-%s.json' % var)).write_text(json.dumps(out, indent=1))
