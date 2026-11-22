"""Hand checks for the V1 structure model (statics and beam formulas, no FEA). usage: python fea-handcheck-v1.py <variant>
November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program."""
import json, math, sys
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'data' / 'fea'
var = sys.argv[1]; V = json.loads((OUT / (var + '-sections.json')).read_text())
R = [json.loads(p.read_text()) for p in sorted(OUT.glob('results-%s-h12.json' % var))][0]
Fr = R['static_wheel_N'][1]; out = {}
# 1. shock force at static: arm moment balance about the pivot (axle load less 14.1 kg wheel), lever from the FEA geometry
PZ, RZ = 350.0, 271.9; lo = (540 - 210 * 0.9906 + 120 * 0.1366, PZ + 210 * (-0.1427) + 120 * 0.9902)   # lower eye (u = (-0.9897,-0.1428), n = (-0.1428,0.9897) rotated)
ux, uz = (0 - 540) / 545.6, (RZ - PZ) / 545.6; nx, nz = -uz, ux
if nz < 0: nx, nz = -nx, -nz
lx, lz = 540 + 210 * ux + 120 * nx, PZ + 210 * uz + 120 * nz
tx, tz = V['geom']['shock_x'], V['geom']['eye_z']; ex, ez = lx - tx, lz - tz; n = math.hypot(ex, ez); ex, ez = ex / n, ez / n
lever = (lz - PZ) * ex - (lx - 540) * ez
F_ax = (Fr - 14.1 * 9.81) * 540.0
out['shock_static_hand_N'] = round(abs(F_ax / lever)); out['shock_static_fea_N'] = R['cases']['C1_static_1g_solo']['shock_force_N']
# 2. belt loop: arm sees the 11.3 kN pull offset by (arm face Y110 to belt Y-144) -> moment about Z, and a bearing couple over the pivot span
P = 11300.0; off = 110 + 144.0; Mz = P * off; span = V['piv_out'] - V['piv_in']
out['belt_design_Mz_Nm'] = round(Mz / 1000); out['bearing_force_each_N_at_span'] = round(Mz / span)
# 3. arm box section at the axle end: I_z (bending in Y) of the thin box, stress under Mz
W, H, t = V['arm_axle']
Iz = (H * W ** 3 - (H - 2 * t) * (W - 2 * t) ** 3) / 12; Zz = Iz / (W / 2)
out['arm_axle_Zz_mm3'] = round(Zz); out['arm_axle_stress_MPa_hand_Mz_only'] = round(Mz / Zz, 1)
# 4. tube: cantilever 400 mm, 1 kN, 38 x 3: sigma = M/Z
ro, tt = 19.0, 3.0; I = math.pi / 4 * (ro ** 4 - (ro - tt) ** 4); out['tube_38x3_400mm_1kN_MPa'] = round(1000 * 100 / (I / ro), 1)
print(json.dumps(out, indent=1)); (OUT / ('handcheck-%s.json' % var)).write_text(json.dumps(out, indent=1))
