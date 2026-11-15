"""Tip-over and low-side slide hand analysis for Bavuso V1.0 (compliance/crash discipline).

Run with the bundled FreeCAD python (numpy/scipy):
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/compliance-tipover.py

All coordinates are GROUND coordinates in mm: X forward from the rear contact patch, Y left, Z up from the ground
(model Z from tools/build-adventure.py + LIFT 40). Hard points are read by hand from build-adventure.py (Nov 12).
The bike is treated as a rigid body that falls sideways (straight-ahead steering) and comes to rest on the face of
the convex hull of its outer points that holds the CoG. Folding pegs and folding mirrors are not counted as supports.
Output: detailed-design/compliance/tipover-results.json
"""
import json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'compliance'
OUT.mkdir(exist_ok=True)
G = 9.81
M_BIKE = 287.2            # kg ready to ride (adventure-layout.md, Nov 12 full build)
COG = np.array([803.0, 0.0, 501.0])   # bike-only CoG, mm (mass-rollup.md Nov 5 update)
I_ROLL_CG = 25.0          # kg m^2 roll inertia about the CoG: assumption (large bikes 15-30 kg m^2, Cossalter ch.1 data)
FX, FZ, RF, WF = 1486.8, 325.3, 325.3, 120.0
RX, RZ, RR, WR = 0.0, 311.9, 311.9, 160.0

def torus(cx, cz, r, w, n=36, m=9):
    """Lower part of the tyre as a torus: crown radius w/2."""
    rc = w / 2; R0 = r - rc; pts = []
    for i in range(n):
        b = math.pi + math.pi * i / (n - 1)          # lower half of the wheel
        for j in range(m):
            a = -math.pi / 2 + math.pi * j / (m - 1)  # across the crown, sidewall to sidewall
            rr = R0 + rc * math.cos(a)
            pts.append((cx + rr * math.cos(b), rc * math.sin(a), cz + rr * math.sin(b)))
    return pts

# name: (point, role) roles: 'rigid' (can support), 'fold' (folds away, reported only), 'body' (reported only)
LEFT = {
    'lever_tip_as_CAD':        ((894, 447, 1112), 'rigid'),
    'bar_end_grip':            ((870, 408, 1116), 'rigid'),
    'mirror_head_outer_top':   ((843, 420, 1312), 'fold'),
    'mirror_head_outer_low':   ((843, 420, 1230), 'fold'),
    'peg_tip':                 ((420, 305, 340), 'fold'),
    'peg_pivot_bracket':       ((420, 232, 340), 'rigid'),
    'tank_side_front_top':     ((1050, 222, 840), 'rigid'),
    'tank_side_rear_top':      ((850, 222, 840), 'rigid'),
    'radiator_outer_face':     ((1015, 178, 710), 'body'),
    'side_grille_louvres':     ((1015, 189, 700), 'body'),
    'battery_panel_upper':     ((1040, 222, 618), 'rigid'),
    'battery_panel_lower':     ((626, 222, 380), 'rigid'),
    'battery_panel_lower_fwd': ((1045, 222, 380), 'rigid'),
    'lower_cover_bevel':       ((900, 205, 250), 'rigid'),
    'pack_case_side_wall':     ((900, 194, 400), 'body'),
    'pack_case_lower_edge':    ((900, 194, 240), 'body'),
    'pivot_cover_cap':         ((540, 219, 436), 'rigid'),
    'tail_side_rear':          ((300, 205, 815), 'rigid'),
    'tail_side_fwd':           ((560, 220, 800), 'rigid'),
    'tail_side_low':           ((560, 220, 600), 'rigid'),
    'seat_edge':               ((470, 224, 860), 'rigid'),
    'rear_indicator_tip':      ((-300, 146, 715), 'fold'),
    'front_indicator':         ((1405, 132, 844), 'rigid'),
    'front_axle_foot':         ((1487, 134, 325), 'rigid'),
    'rear_axle_nut':           ((0, 150, 312), 'rigid'),
    'hv_cabinet_side':         ((510, 95, 300), 'body'),
}
# Proposed protection (CAD change requests). Outer surfaces, i.e. tube centre + 14 mm or puck face.
GUARDS = {
    'guard_upper_B_puck':      ((1075, 300, 680), 'rigid'),   # upper bend of the front guard, POM puck
    'guard_mid_C_puck':        ((1040, 305, 470), 'rigid'),   # widest point, POM puck
    'guard_lower_D':           ((900, 290, 290), 'rigid'),
    'guard_lower_E':           ((700, 280, 290), 'rigid'),
    'handguard_bar_end':       ((870, 445, 1116), 'rigid'),   # aluminium backbone, bar-end clamp
    'handguard_loop_fwd':      ((955, 440, 1112), 'rigid'),
    'pivot_slider_puck':       ((540, 262, 390), 'rigid'),    # 50 mm POM puck on the pivot node lug
    'tail_slider_puck':        ((300, 245, 700), 'rigid'),    # puck on the tail rail / rack post
}
SHORT_LEVER = {'lever_tip_as_CAD': ((880, 425, 1110), 'rigid')}   # lever shortened 25 mm to end inside the grip end

def mirror(d):
    return {k + '_R': ((p[0], -p[1], p[2]), r) for k, (p, r) in d.items()}

def rest(points_named):
    """Resting pose on the left side: the ground plane is a supporting plane of the rigid points (tyres included).
    For a ground direction u (unit vector pointing down into the ground, in bike axes) the CoG height above the
    supporting plane is max_i(p_i.u) - CoG.u. The bike comes to rest at the minimum of that potential over lean and
    pitch, found here by a fine grid (scipy's hull is blocked on this machine, so no ConvexHull)."""
    tyres = torus(FX, FZ, RF, WF) + torus(RX, RZ, RR, WR)
    sup = np.array([p for p, r in points_named.values() if r == 'rigid'] + tyres, float)
    best = None
    for lean in np.arange(20.0, 90.01, 0.1):
        for pitch in np.arange(-25.0, 25.01, 0.25):
            a, b = math.radians(lean), math.radians(pitch)
            u = np.array([math.sin(b), math.sin(a) * math.cos(b), -math.cos(a) * math.cos(b)])
            # u points from the bike toward the ground; heights above ground = s - p.u
            s = sup @ u
            hc = s.max() - COG @ u
            if best is None or hc < best[0]: best = (hc, lean, pitch, u, s.max())
    hc, lean, pitch, u, smax = best
    heights = {k: float(smax - np.dot(u, p)) for k, (p, r) in points_named.items()}
    contacts = [k for k, (p, r) in points_named.items() if r == 'rigid' and heights[k] < 2.0]
    tyre_h = smax - np.array(tyres) @ u
    if tyre_h[:len(tyres)//2].min() < 2: contacts.append('front_tyre')
    if tyre_h[len(tyres)//2:].min() < 2: contacts.append('rear_tyre')
    return dict(lean_deg=float(lean), pitch_deg=float(pitch), cog_height_rest_mm=float(hc), contacts=contacts, heights=heights)

def energy(h_rest_mm, mass=M_BIKE, h0=COG[2]):
    dE = mass * G * (h0 - h_rest_mm) / 1000
    I = I_ROLL_CG + mass * (h0 / 1000) ** 2           # about the ground line
    w = math.sqrt(2 * dE / I)
    return dE, I, w

res = {}
cases = {
    'as_CAD': {**LEFT},
    'with_guards': {**LEFT, **SHORT_LEVER, **GUARDS},
}
for name, pts in cases.items():
    r = rest(pts)
    dE, I, w = energy(r['cog_height_rest_mm'])
    # contact speed of each support point: omega x its distance from the tyre line (X axis at ground)
    r['tipover_energy_J'] = dE
    r['roll_inertia_ground_kgm2'] = I
    r['omega_at_contact_rad_s'] = w
    r['contact_speed_m_s'] = {k: w * math.hypot(p[1], p[2]) / 1000 for k, (p, ro) in pts.items() if k in r['contacts']}
    res[name] = r
# Two-up luggage variant (bike + 40 kg luggage at 850 mm): energy only
m2 = M_BIKE + 40; h2 = (M_BIKE * 501 + 40 * 850) / m2
res['luggage_tipover_energy_J'] = m2 * G * (h2 - res['with_guards']['cog_height_rest_mm']) / 1000

# Static load on the guard when lying down: moments about the tyre line (approx: guard + bar end share the
# CoG load by their X position relative to the CoG; tyres carry the rest). Reported as the planar share.
lying = res['with_guards']
W = M_BIKE * G
# fraction of weight carried by side contacts ~ sin(lean) component taken by the side points; split by lever arm
res['static_side_load_N'] = W * math.sin(math.radians(lying['lean_deg']))

# Low-side slide
slide = {}
for v_kmh in (30, 50, 80):
    v = v_kmh / 3.6
    for mu in (0.35, 0.5):
        slide[f'{v_kmh}kmh_mu{mu}'] = dict(KE_kJ=0.5 * M_BIKE * v * v / 1000, distance_m=v * v / (2 * mu * G),
                                         time_s=v / (mu * G), normal_load_N=W)
res['lowside'] = slide
# Drop of the CoG during a low-side from 45 deg lean to rest (vertical impact energy)
res['lowside_vertical_drop_energy_J'] = M_BIKE * G * (501 * math.cos(math.radians(45)) - lying['cog_height_rest_mm']) / 1000

# Guard tube and anchor sizing (hand calc)
def tube(D, t, sy):
    d = D - 2 * t
    I = math.pi / 64 * (D ** 4 - d ** 4); Wel = I / (D / 2); Z = (D ** 3 - d ** 3) / 6
    return dict(D=D, t=t, I_mm4=I, W_el_mm3=Wel, Z_pl_mm3=Z, M_y_Nm=sy * Wel / 1000, M_p_Nm=sy * Z / 1000,
                mass_kg_per_m=7.85e-6 * math.pi / 4 * (D ** 2 - d ** 2) * 1000)
guard = {}
for D, t in ((25.4, 2.0), (28.0, 2.5), (30.0, 3.0)):
    g = tube(D, t, 435.0)            # 25CrMo4 / 4130 normalised, Rp0.2 >= 435 MPa (EN 10083-3 / AMS 6361 class)
    L = 400.0                        # span between upper and lower anchors of the loop at the contact, mm
    g['P_collapse_fixed_fixed_kN'] = 8 * g['M_p_Nm'] / (L / 1000) / 1000
    g['P_collapse_cantilever_250_kN'] = g['M_p_Nm'] / 0.25 / 1000
    g['k_fixed_fixed_N_per_mm'] = 192 * 200e3 * g['I_mm4'] / L ** 3
    g['elastic_energy_J'] = 0.5 * (8 * g['M_y_Nm'] / (L / 1000)) ** 2 / (g['k_fixed_fixed_N_per_mm'] * 1000)
    guard[f'{D}x{t}'] = g
res['guard_tubes'] = guard
gsel = guard['28.0x2.5']
E_guard = 0.5 * res['with_guards']['tipover_energy_J']     # half the fall energy into the front guard (assumption)
res['guard_selected'] = dict(section='28.0 x 2.5 25CrMo4', P_c_kN=gsel['P_collapse_fixed_fixed_kN'],
    energy_to_guard_J=E_guard, plastic_set_mm_if_all_plastic=E_guard / (gsel['P_collapse_fixed_fixed_kN'] * 1000) * 1000,
    anchor_design_load_kN=1.5 * gsel['P_collapse_fixed_fixed_kN'])
# Anchor bolt check: two M10 10.9 per anchor in single shear, As=58 mm2, shear ~0.6*1000 MPa
res['anchor_bolts'] = dict(per_anchor='2 x M10 10.9', shear_capacity_kN=2 * 58 * 600 / 1000,
                           demand_kN=res['guard_selected']['anchor_design_load_kN'])

(OUT / 'tipover-results.json').write_text(json.dumps(res, indent=1, default=float))
for k in ('as_CAD', 'with_guards'):
    r = res[k]
    print(k, 'lean %.1f deg, CoG at rest %.0f mm, contacts %s' % (r['lean_deg'], r['cog_height_rest_mm'], r['contacts']))
    print('   tip-over energy %.0f J, omega %.2f rad/s, contact speeds %s' % (r['tipover_energy_J'], r['omega_at_contact_rad_s'],
          {a: round(b, 2) for a, b in r['contact_speed_m_s'].items()}))
    low = sorted(r['heights'].items(), key=lambda t: t[1])[:14]
    print('   lowest points (mm above ground plane):', [(a, round(b)) for a, b in low])
print('luggage tip-over energy', round(res['luggage_tipover_energy_J']))
print('guard', {k: {a: round(b, 2) for a, b in v.items()} for k, v in guard.items()})
print('selected', res['guard_selected'], res['anchor_bolts'])
print('lowside', {k: {a: round(b, 1) for a, b in v.items()} for k, v in slide.items()}, round(res['lowside_vertical_drop_energy_J']))
