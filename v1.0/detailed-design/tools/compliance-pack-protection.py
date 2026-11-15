"""Pack impact/crush hand calculations for Bavuso V1.0 (compliance/crash discipline).

Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/compliance-pack-protection.py
Inputs from tools/build-adventure.py: pack case 4 mm wall (WALL), 1 mm cell-to-wall gap (CLR), outer lane cell end
2 mm from the inner side wall (YI = 128 + 60 + 2), skid 4 mm at 216 mm ground clearance, 18 mm skid-to-pack gap,
pack outer box X590-1088, Y+-194, Z238-613.5 (ground). Methods: Roark's Formulas for Stress and Strain (7th ed.)
Table 11.4 (rectangular plates, simply supported), yield-line collapse of a plate under a point load
(P = 2*pi*Mp, Mp = sy*t^2/4), lateral-plate pressure from cell inertia. Output: compliance/pack-protection-results.json
"""
import json, math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'compliance'
G = 9.81
E_AL = 70e3
def interp(tab, r):
    ks = sorted(tab)
    if r <= ks[0]: return tab[ks[0]]
    for a, b in zip(ks, ks[1:]):
        if a <= r <= b: return tab[a] + (tab[b] - tab[a]) * (r - a) / (b - a)
    return tab[ks[-1]]
# Roark Table 11.4 case 1a (uniform load, all edges simply supported), nu = 0.3, a = long side, b = short side
BETA_U = {1.0: .2874, 1.2: .3762, 1.4: .4530, 1.6: .5172, 1.8: .5688, 2.0: .6102, 3.0: .7134, 4.0: .7410, 5.0: .7476, 50: .7500}
ALPHA_U = {1.0: .0444, 1.2: .0616, 1.4: .0770, 1.6: .0906, 1.8: .1017, 2.0: .1110, 3.0: .1335, 4.0: .1400, 5.0: .1417, 50: .1421}
# Roark Table 11.4 case 1d (central point load on a small circle r0), nu = 0.3
ALPHA_P = {1.0: .1267, 1.2: .1478, 1.4: .1621, 1.6: .1715, 1.8: .1770, 2.0: .1805, 50: .1851}
BETA_P = {1.0: .435, 1.2: .650, 1.4: .789, 1.6: .875, 1.8: .927, 2.0: .958, 50: 1.000}
def plate_uniform(q, a, b, t):
    r = max(a, b) / min(a, b); b = min(a, b)
    return dict(sigma_MPa=interp(BETA_U, r) * q * b * b / t / t, w_mm=interp(ALPHA_U, r) * q * b ** 4 / (E_AL * t ** 3))
def plate_point(P, a, b, t, r0):
    r = max(a, b) / min(a, b); b = min(a, b)
    rp = math.sqrt(1.6 * r0 * r0 + t * t) - 0.675 * t if r0 < 0.5 * t else r0
    s = 3 * P / (2 * math.pi * t * t) * (1.3 * math.log(2 * b / (math.pi * rp)) + interp(BETA_P, r))
    return dict(sigma_elastic_MPa=s, w_elastic_mm=interp(ALPHA_P, r) * P * b * b / (E_AL * t ** 3))
def collapse_point(sy, t): return 2 * math.pi * sy * t * t / 4 / 1000   # kN, yield-line fan, independent of span

res = {}
# ---- 1. Bottom: skid plate and pack floor under a rock strike
m_lad = 287.2 + 85 + 15                                  # bike + rider + 15 kg luggage
loads = {'S1_static_highcentre_1g_kN': m_lad * G / 1000, 'S2_bottom_out_3g_kN': 3 * m_lad * G / 1000}
res['bottom_loads'] = loads
skids = {'CAD_4mm_5052H32': (4, 193, 2680), '6mm_5083H321': (6, 215, 2660), '8mm_5083H321': (8, 215, 2660),
         '5mm_7020T6': (5, 280, 2780)}
area_skid = 0.66 * 0.35     # m2, proposed extended plate X430-1090 x 350 wide
sk = {}
for k, (t, sy, rho) in skids.items():
    el = plate_point(loads['S1_static_highcentre_1g_kN'] * 1000, 450, 350, t, 25)
    sk[k] = dict(t_mm=t, sy_MPa=sy, P_collapse_kN=collapse_point(sy, t), S1_elastic_sigma_MPa=el['sigma_elastic_MPa'],
                 S1_elastic_w_mm=el['w_elastic_mm'], S1_margin=collapse_point(sy, t) / loads['S1_static_highcentre_1g_kN'],
                 S2_margin=collapse_point(sy, t) / loads['S2_bottom_out_3g_kN'], mass_kg_extended=area_skid * t / 1000 * rho)
res['skid'] = sk
res['pack_floor_4mm_6061T6'] = dict(P_collapse_kN=collapse_point(240, 4), S2_margin=collapse_point(240, 4) / loads['S2_bottom_out_3g_kN'],
                                   gap_floor_to_cell_mm=4 + 1 - 4)
# ---- 2. Inertial loads on the case walls (cells pushing on walls) for UN 38.3 T4 and R136 mechanical shock
m_cells = 594 * 0.180
cases = {'UN38.3_T4_large_battery_gn': min(50, math.sqrt(30000 / 133.7)),   # 38.3.4.4: large batteries 50 gn or sqrt(30000/m)
         'tipover_sidewall_gn_est': 15.0,                                    # side wall deceleration at guard contact, estimate
         'road_vertical_pothole_gn': 8.0}                                    # design pothole case, assumption
walls = {}
side_area_m2 = 0.498 * 0.3755 * 0.85          # stepped side face area (85% of the bbox)
floor_area_m2 = 0.498 * 0.388
for name, gn in cases.items():
    F = m_cells * gn * G
    q_side = F / side_area_m2 / 1e6            # MPa (all three lanes push the one side wall through end spacers)
    q_floor = F / floor_area_m2 / 1e6
    d = dict(g=gn, force_kN=F / 1000, q_side_kPa=q_side * 1000, q_floor_kPa=q_floor * 1000)
    for span in (375, 150, 100):
        d[f'side_4mm_span{span}'] = plate_uniform(q_side, 498, span, 4)
        d[f'side_6mm_span{span}'] = plate_uniform(q_side, 498, span, 6)
    d['floor_4mm_span388'] = plate_uniform(q_floor, 498, 388, 4)
    d['floor_4mm_span125'] = plate_uniform(q_floor, 388, 125, 4)
    walls[name] = d
res['wall_inertia'] = walls
# ---- 3. Side crush (internal target, adopted from GB 38031-2020 / SAE J2464 practice: 100 kN, 75 mm half-cylinder)
# Load path without a guard: cover (3 mm plastic) -> 4 mm wall -> 2 mm gap -> cell caps (axial). The cell axial
# crush is assumed to fail electrically after ~3-5 mm of cap deformation (assumption; cell supplier data needed).
res['side_crush'] = dict(target_kN=100.0, crush_zone_now_mm=(207 - 194) + 2, crush_zone_proposed_mm=(217 - 204) + 12,
                         note='cell caps face the side wall; without a crush zone, side intrusion shorts cells')
# ---- 4. Ground clearance, breakover and fording heights (ground coordinates)
L = 1486.8; h = 216.0
res['breakover_deg_flat_skid'] = 2 * math.degrees(math.atan(h / (L / 2)))
rear_bump, front_bump_v = 119.0, 170 * math.cos(math.radians(25))
res['skid_clearance_full_bump_mm'] = h - (rear_bump + (front_bump_v - rear_bump) * 865 / L)
heights = {'pack_case_bottom': 238, 'hv_cabinet_bottom': 245, 'gear_case_bottom_at_pivot': 390 - 75,
           'motor_bottom': 390 + 135 * math.sin(math.radians(75)) - 110, 'front_wheel_bearing': 325.3,
           'rear_wheel_bearing': 311.9, 'pack_case_top': 613.5, 'charger_bottom': 630, 'radiator_bottom': 640,
           'inverter_bottom': 715, 'bms_bottom': 820, 'pack_vent_proposed': 650}
res['component_heights_mm'] = heights
res['fording'] = dict(rated_depth_mm=450, bow_wave_allowance_mm=100,
                      ip67_required_below_mm=550, below=[k for k, v in heights.items() if v < 550])
(OUT / 'pack-protection-results.json').write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1)[:6000])
