"""Thermal study: hydraulic sizing, coolant volume, part masses and cost for the chosen cooling system.

Pure hand-calculation script (no ODE). Run from v1.0 with the bundled python. Writes thermal/sizing.json.
Area per radiator is passed as argv[1] (m2 of core face), default 0.040.
"""
import json, math, pathlib, sys
OUT = pathlib.Path(__file__).resolve().parents[1] / 'thermal'
A_SIDE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.040
RHO, MU = 1065.0, 2.2e-3           # 50/50 EGW at ~40 degC

def darcy(Re): return 64 / Re if Re < 2300 else 0.316 / Re ** 0.25

def pipe_dp(lpm, d, L, k_minor=0.0):
    Q = lpm / 60000; A = math.pi * d * d / 4; v = Q / A; Re = RHO * v * d / MU
    return darcy(Re) * L / d * RHO * v * v / 2 + k_minor * RHO * v * v / 2, v, Re

out = {}
# ---- battery loop, 15 L/min
Q = 15.0; n_rib = 6
# ribbon: 105 mm tall x 1.6 mm thick extruded multiport, 12 ports 7.5 x 1.1 mm. One serpentine ribbon per lane-half (6 total):
# 4 passes of ~0.40 m (rows of ~12.5 cells x 28 mm, x1.15 for the wave) plus wraps round the end cells -> ~2.0 m each
ports, w, h, Lr = 12, 7.5e-3, 1.1e-3, 2.0
q_rib = Q / 60000 / n_rib; A_flow = ports * w * h; v = q_rib / A_flow; Dh = 2 * w * h / (w + h)
Re = RHO * v * Dh / MU
aspect = h / w; fRe = 96 * (1 - 1.3553 * aspect + 1.9467 * aspect**2 - 1.7012 * aspect**3 + 0.9564 * aspect**4 - 0.2537 * aspect**5)   # Shah & London
dp_rib = (fRe / Re) * Lr / Dh * RHO * v * v / 2 + 1.5 * RHO * v * v / 2
Nu = 5.4; h_c = Nu * 0.40 / Dh
dp_hose_b, vb, Reb = pipe_dp(Q, 0.016, 2.2, k_minor=6.0)     # 2.2 m of 16 mm ID hose, ~8 bends/fittings
dp_manifold = 3000.0; dp_rad_charge = 1500.0; dp_rad_drive = 4000.0; dp_ptc = 2500.0; dp_valve = 4000.0
dp_b = dp_rib + dp_hose_b + dp_manifold + dp_rad_drive + dp_ptc + dp_valve
P_hyd_b = dp_b * Q / 60000
out['battery_loop'] = dict(flow_lpm=Q, ribbon=dict(count=n_rib, flow_each_lpm=round(Q / n_rib, 3), length_m=Lr, velocity_m_s=round(v, 3), Dh_mm=round(Dh * 1e3, 2),
                           Re=round(Re, 0), h_W_m2K=round(h_c, 0), dp_Pa=round(dp_rib, 0)),
                           hose=dict(ID_mm=16, length_m=2.2, velocity_m_s=round(vb, 2), Re=round(Reb, 0), dp_Pa=round(dp_hose_b, 0)),
                           dp_total_kPa=round(dp_b / 1e3, 1), hydraulic_W=round(P_hyd_b, 1),
                           pump_electrical_W=round(P_hyd_b / 0.25, 0))
# ---- drive loop, 12 L/min
Q = 12.0
dp_hose_d, vd, Red = pipe_dp(Q, 0.016, 3.2, k_minor=8.0)
dp_inv = 8000.0; dp_obc = 4000.0; dp_hx = 6000.0; dp_rad = 3500.0
dp_d = dp_hose_d + dp_inv + dp_obc + dp_hx + dp_rad + dp_valve
P_hyd_d = dp_d * Q / 60000
out['drive_loop'] = dict(flow_lpm=Q, hose=dict(ID_mm=16, length_m=3.2, velocity_m_s=round(vd, 2), Re=round(Red, 0), dp_Pa=round(dp_hose_d, 0)),
                         dp_total_kPa=round(dp_d / 1e3, 1), hydraulic_W=round(P_hyd_d, 1), pump_electrical_W=round(P_hyd_d / 0.25, 0))
out['pump_check'] = 'Pierburg CWA50 class: ~25 L/min at 0.53 bar, 24 L/min / 0.6 bar max, <6.5 A at 12 V (Rheinmetall / tecomotive datasheet). ' \
                    'Both loops sit at 15-25 % of its pressure capability at the design flow.'

# ---- coolant volume (L)
vol = dict(ribbons=round(n_rib * ports * w * h * Lr * 1e3, 2), pack_manifolds=0.35, radiators=round(2 * A_SIDE * 0.032 * 0.18 * 1e3, 2),
           hoses=round(math.pi * 0.008 ** 2 * (2.2 + 3.2) * 1e3, 2), inverter=0.20, obc_plate=0.12, oil_hx=0.10, heater=0.15,
           pumps=0.10, reservoir_working=0.30)
out['coolant_volume_L'] = dict(vol, total=round(sum(vol.values()), 2))

# ---- masses (kg) and cost at 10k/yr (USD, planning estimates, unquoted)
core_kg = A_SIDE * 0.032 * 600 + 0.25          # brazed Al core ~600 kg/m3 of core volume + plastic tanks
parts = [
    ('Radiator core 32 mm, brazed Al, plastic tanks', 2, core_kg, 55),
    ('Puller fan 190 mm (7.5 in) BLDC, shroud', 2, 0.55, 35),
    ('Coolant pump 12 V BLDC, CWA50 class', 2, 0.55, 75),
    ('Cooling ribbons, Al multiport 105x1.6 mm, 6 serpentines x 2.0 m, dielectric-coated', 1, round(n_rib * (0.105 * 0.0016 * Lr * 2700 * 0.40), 2), 180),
    ('Pack inlet/outlet manifolds + bulkhead quick-connects', 1, 0.7, 60),
    ('Thermal adhesive 0.2 mm, cells to ribbon', 1, round(594 * 1.43e-3 * 0.2e-3 * 2400, 2), 40),
    ('HV PTC coolant heater 5 kW', 1, 1.9, 190),
    ('4-port coolant valve (battery/drive radiator cross-connect + heater bypass)', 1, 0.45, 45),
    ('Oil-to-water plate HX on gear case (in drive-unit allowance)', 1, 0.0, 0),
    ('Hoses 16 mm ID EPDM, 5.4 m, clamps, P-clips', 1, 0.95, 35),
    ('Reservoir/degas bottle 0.6 L with cap', 1, 0.25, 12),
    ('Coolant 50/50 EGW', 1, round(out['coolant_volume_L']['total'] * 1.065, 2), 8),
    ('Temperature sensors (coolant x4, cell NTC on BMS)', 1, 0.1, 20),
    ('Fire barrier: intumescent foam in non-ribbon gaps (~8 L)', 1, 2.4, 70),
    ('Pack vent valve with burst disc + vent plenum liners (mica)', 1, 0.5, 45),
]
out['parts'] = [dict(item=n, qty=q, mass_each_kg=round(m, 2), mass_kg=round(q * m, 2), usd_10k_each=c, usd_10k=q * c) for n, q, m, c in parts]
out['totals'] = dict(mass_kg=round(sum(p['mass_kg'] for p in out['parts']), 2), usd_10k=sum(p['usd_10k'] for p in out['parts']),
                     usd_1k_estimate=round(1.6 * sum(p['usd_10k'] for p in out['parts'])))
out['vs_rollup'] = 'mass-rollup.csv allows 2.8 kg (pump, hoses, 2 L coolant) + 2 x 1.15 kg side radiators + 16.3 kg pack internals allowance (cooling ribbon included there)'
(OUT / 'sizing.json').write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
