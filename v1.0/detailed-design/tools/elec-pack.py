"""Bavuso V1.0 adventure: traction-pack electrical detailed design.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).

Reads cell-placement-adventure.csv (99s6p, 594 x 26120-class cells, three transverse lanes) and works out:
  - series-link geometry for the CURRENT numbering and for the PROPOSED numbering (lane 2 snake reversed);
  - busbar design sweep (material x thickness) with current density, resistance, I2R, voltage drop and
    temperature rise at peak (30 s) and continuous current; picks the lightest option that meets the rules;
  - per-cell fusible-neck sizing (Onderdonk adiabatic melt) and selectivity against a shorted cell;
  - Orion BMS2-108 cell-tap map (9 groups x 11 cells), sense-wire lengths, thermistor map;
  - pack short-circuit current and the protection coordination inputs used by elec-hv.py.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe -I detailed-design/tools/elec-pack.py   (from v1.0)
Plain python + math only, so any python 3 works.
"""
import csv, json, math
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / 'detailed-design' / 'electrical'
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ inputs and assumptions
SERIES, PAR = 99, 6
CELL = dict(
    format='26120 (26 x 120 mm) fast-charge cylinder, Stark Future / EVE / Wanxiang A123 class',
    wh=55.0, v_nom=3.6, v_max=4.2, v_min=2.5, mass_g=180.0,
    dcir_mohm=3.0,          # ASSUMPTION: 15 Ah power cylinder at 25 C, 50% SOC, 10 s. No datasheet public. OPEN.
    terminals='positive cap one end, negative can base other end (as modelled in CAD); OPEN until supplier drawing',
)
CELL['ah'] = CELL['wh'] / CELL['v_nom']
PACK_V_NOM, PACK_V_MAX, PACK_V_MIN = SERIES * CELL['v_nom'], SERIES * CELL['v_max'], SERIES * CELL['v_min']
P_PEAK_W, P_CONT_W = 130e3, 98e3            # drive-study pack limit; 10-80% in 14 min = 22.9 kWh/0.233 h = 98 kW
V_LOADED_MIN = 300.0                         # 3.03 V/cell under 4.5C at low SOC (design floor for current sizing)
I_PEAK = P_PEAK_W / V_LOADED_MIN             # 433 A for 30 s
I_CONT = 260.0                               # 98 kW DC fast charge at ~377 V mid-SOC; also ~85 kW top-speed cruise at 330 V
T_PEAK_S = 30.0
T_CHARGE_S = 14 * 60.0

MAT = {  # resistivity at 20 C (ohm m), temp coeff, density, cp, k
    'Cu-ETP C11000': dict(rho=1.724e-8, a=0.00393, d=8960, cp=385, k=390, j_max=6.0),
    'Al 1060-O':     dict(rho=2.82e-8,  a=0.00403, d=2705, cp=900, k=234, j_max=4.0),
    'Al 1350 (EC)':  dict(rho=2.80e-8,  a=0.00403, d=2705, cp=900, k=234, j_max=4.0),
}
# j_max: continuous design current-density rule (A/mm2) for short, conduction-cooled pack busbars.
# Copper Development Association Pub 22 ("Copper for busbars") sizes by temperature rise; the 6/4 A/mm2
# values are this study's design rule, checked below by the thermal bounds.
BUS_W = 24.0          # mm, busbar width over a 26 mm cell end (1 mm edge margin each side)
COLLECTOR_T = 0.30    # mm Ni-plated Cu fuse-collector between cell and busbar
FILM_T = 0.50         # mm polyimide/PET insulating film over each busbar face
T_OPER = 45.0         # C busbar operating temperature for resistance (cells held 25-45 C)

# ------------------------------------------------------------------ geometry
rows = list(csv.DictReader(open(R / 'cell-placement-adventure.csv')))
cells = {r['cell_id']: dict(g=int(r['series_group']), p=int(r['parallel_position']), lane=int(r['lane']),
                            x=float(r['x_mm']), y=float(r['y_mm']), z=float(r['z_mm'])) for r in rows}
assert len(cells) == SERIES * PAR
# Snake order inside a lane = order of the CSV rows (generator writes them in snake order).
lane_seq = {}
for r in rows:
    lane_seq.setdefault(int(r['lane']), []).append(r['cell_id'])

def numbering(reverse_lane2):
    """Return {group: [cell dicts in snake order]} for a numbering scheme."""
    groups = {}
    for lane in (1, 2, 3):
        seq = lane_seq[lane][::-1] if (reverse_lane2 and lane == 2) else lane_seq[lane]
        for j, cid in enumerate(seq):
            g = (lane - 1) * 33 + j // PAR + 1
            groups.setdefault(g, []).append(cells[cid])
    return groups

def dist(a, b):
    return math.dist((a['x'], a['y'], a['z']), (b['x'], b['y'], b['z']))

def link_geometry(groups, g):
    """Series link g -> g+1 modelled as a strip along the snake: current builds up cell by cell in group g,
    the whole current crosses to g+1, then drains cell by cell. Returns effective length (for R), the
    full-current span, physical strip length, and whether it crosses lanes."""
    a, b = groups[g], groups[g + 1]
    cross = a[0]['lane'] != b[0]['lane']
    segs = []
    for i in range(PAR - 1):
        segs.append(((i + 1) / PAR, dist(a[i], a[i + 1])))
    if cross:
        # between lanes the link folds through the lane gap: in-plane offset + the 8 mm gap + two 90 deg folds
        d_in_plane = math.hypot(a[-1]['x'] - b[0]['x'], a[-1]['z'] - b[0]['z'])
        full = d_in_plane + 8.0 + 2 * 13.0
    else:
        full = dist(a[-1], b[0])
    segs.append((1.0, full))
    for j in range(PAR - 1):
        segs.append(((PAR - 1 - j) / PAR, dist(b[j], b[j + 1])))
    l_eff = sum(f * f * l for f, l in segs)
    l_phys = sum(l for _, l in segs) + 26.0
    return dict(segs=segs, g=g, lanes=f"{a[0]['lane']}->{b[0]['lane']}", cross_lane=cross, full_current_span_mm=round(full, 1),
                l_eff_mm=round(l_eff, 1), l_phys_mm=round(l_phys, 1),
                x_from=a[-1]['x'], z_from=a[-1]['z'], x_to=b[0]['x'], z_to=b[0]['z'])

schemes = {}
for name, rev in (('current', False), ('proposed_lane2_reversed', True)):
    gr = numbering(rev)
    links = [link_geometry(gr, g) for g in range(1, SERIES)]
    schemes[name] = dict(groups=gr, links=links)

def terminal(gr, g, first):
    c = gr[g][0] if first else gr[g][-1]
    return dict(group=g, x=c['x'], y=c['y'], z=c['z'], lane=c['lane'])

# ------------------------------------------------------------------ busbar sweep
def res(m, l_mm, a_mm2, T=T_OPER):
    mm = MAT[m]
    return mm['rho'] * (1 + mm['a'] * (T - 20)) * (l_mm / 1000) / (a_mm2 * 1e-6)

sweep = []
links = schemes['proposed_lane2_reversed']['links']
MIN_W = 6.0   # mm, narrowest stamped bridge in a tapered plate

for L in links:
    segs = L['segs']
    for profile in ('uniform', 'tapered'):
        rs, ms = 0.0, 0.0
        for f, l in segs:
            wr = 1.0 if profile == 'uniform' else max(f, MIN_W / BUS_W)
            rs += f * f * l / wr; ms += l * wr
        ms += 26.0 * (1.0 if profile == 'uniform' else MIN_W / BUS_W)   # end overhang
        L['_r_' + profile], L['_m_' + profile] = rs, ms

for m in MAT:
  for profile in ('uniform', 'tapered'):
    for t in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        A = BUS_W * t
        mm = MAT[m]
        rho = mm['rho'] * (1 + mm['a'] * (T_OPER - 20))
        Rt = sum(rho * L['_r_' + profile] / 1000 / (A * 1e-6) for L in links)
        mass = sum(mm['d'] * L['_m_' + profile] / 1000 * BUS_W / 1000 * t / 1000 for L in links)
        mass += 2 * mm['d'] * (5 * 28 + 26) / 1000 * BUS_W / 1000 * t / 1000      # pack terminal end plates
        j_cont, j_peak = I_CONT / A, I_PEAK / A      # at the full-current span (tapered: same J everywhere)
        dT_peak_adiab = (j_peak * 1e6) ** 2 * rho * T_PEAK_S / (mm['d'] * mm['cp'])
        span = max(L['full_current_span_mm'] for L in links if not L['cross_lane']) / 1000
        dT_cond = (j_cont * 1e6) ** 2 * rho * span ** 2 / (8 * mm['k'])
        worst = max(links, key=lambda L: L['_r_' + profile])
        P_link = I_CONT ** 2 * rho * worst['_r_' + profile] / 1000 / (A * 1e-6)
        area = 2 * worst['_m_' + profile] / 1000 * BUS_W / 1000
        dT_conv_only = P_link / (8.0 * area)
        loss_cont, loss_peak, vdrop_peak = I_CONT ** 2 * Rt, I_PEAK ** 2 * Rt, I_PEAK * Rt
        ok = (dT_peak_adiab <= 15 and dT_cond <= 2 and dT_conv_only <= 60 and vdrop_peak <= 0.01 * PACK_V_NOM)
        sweep.append(dict(material=m, profile=profile, t_mm=t, w_full_mm=BUS_W, area_full_mm2=A, j_cont_A_mm2=round(j_cont, 2),
                          j_peak_A_mm2=round(j_peak, 2), R_links_total_mohm=round(Rt * 1e3, 3),
                          loss_cont_W=round(loss_cont, 1), loss_peak_W=round(loss_peak, 1),
                          vdrop_peak_V=round(vdrop_peak, 2), dT_peak30s_adiabatic_K=round(dT_peak_adiab, 2),
                          dT_cont_between_welds_K=round(dT_cond, 3), dT_cont_convection_only_K=round(dT_conv_only, 1),
                          busbar_mass_kg=round(mass, 3), score_kg_equiv=round(mass + loss_cont * 0.01, 2), meets_rules=ok))
passing = [s for s in sweep if s['meets_rules']]
best = min(passing, key=lambda s: s['score_kg_equiv'])  # 100 W of continuous loss counted as 1 kg
choice = dict(best)

with open(OUT / 'busbar-sweep.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(sweep[0].keys())); w.writeheader(); w.writerows(sweep)

# per-link table for the chosen busbar
mm = MAT[choice['material']]
A = choice['area_full_mm2']
prof = choice['profile']
rho_c = mm['rho'] * (1 + mm['a'] * (T_OPER - 20))
link_rows = []
for L in links:
    r = rho_c * L['_r_' + prof] / 1000 / (A * 1e-6)
    link_rows.append(dict(link=f"S{L['g']:03d}->S{L['g']+1:03d}", lanes=L['lanes'], cross_lane=L['cross_lane'],
                          face=('lane gap fold' if L['cross_lane'] else ('A' if L['g'] % 2 else 'B')),
                          x_from_mm=round(L['x_from'], 1), z_from_mm=round(L['z_from'], 1),
                          x_to_mm=round(L['x_to'], 1), z_to_mm=round(L['z_to'], 1),
                          strip_length_mm=L['l_phys_mm'], full_current_span_mm=L['full_current_span_mm'],
                          effective_length_mm=round(L['_r_' + prof], 1), material=choice['material'], profile=prof,
                          section_mm=f"{BUS_W:.0f} x {choice['t_mm']}", area_mm2=A,
                          j_peak_A_mm2=round(I_PEAK / A, 2), j_cont_A_mm2=round(I_CONT / A, 2),
                          R_uohm=round(r * 1e6, 2), loss_cont_W=round(I_CONT ** 2 * r, 2),
                          loss_peak_W=round(I_PEAK ** 2 * r, 2), vdrop_peak_mV=round(I_PEAK * r * 1e3, 2),
                          mass_g=round(mm['d'] * L['_m_' + prof] * BUS_W * choice['t_mm'] * 1e-6, 1)))
with open(OUT / 'busbars.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(link_rows[0].keys())); w.writeheader(); w.writerows(link_rows)

# hand check: one ordinary in-row link computed by hand formula
inrow = next(L for L in links if not L['cross_lane'] and abs(L['z_from'] - L['z_to']) < 1)
p = 28.0
l_eff_hand = 2 * (1 + 4 + 9 + 16 + 25) / 36 * p + p   # 1/6..5/6 steps each side + full span of one pitch
hand = dict(link=inrow['g'], l_eff_script_mm=inrow['l_eff_mm'], l_eff_hand_mm=round(l_eff_hand, 1),
            agree=abs(inrow['l_eff_mm'] - l_eff_hand) < 0.5)

# ------------------------------------------------------------------ cell fusible neck (Onderdonk, adiabatic)
def onderdonk_t(I, a_mm2, Ta=45.0, Tm=1083.0):
    cmil = a_mm2 * 1973.5
    return math.log10(1 + (Tm - Ta) / (234 + Ta)) / 33.0 * (cmil / I) ** 2

i_cell_peak = I_PEAK / PAR
i_cell_cont = I_CONT / PAR
neck = None
for a in [x / 100 for x in range(60, 300, 2)]:
    if onderdonk_t(i_cell_peak, a) >= 3 * T_PEAK_S:      # must survive 3x the 30 s peak even with no cooling
        neck = a; break
neck_t, neck_w = COLLECTOR_T, round(neck / COLLECTOR_T, 2)
cell_ocv = 3.7
# shorted cell: the other 5 cells of its group discharge into it, each limited by its DCIR + its neck + strip
r_cell = CELL['dcir_mohm'] / 1000
r_neck = MAT['Cu-ETP C11000']['rho'] * 0.004 / (neck * 1e-6)
i_feed_each = cell_ocv / (r_cell + 2 * r_neck + 0.5e-3)
i_fault = (PAR - 1) * i_feed_each
t_open_faulted = onderdonk_t(i_fault, neck)
t_open_feeder = onderdonk_t(i_feed_each, neck)
fuse = dict(material='Ni-plated Cu C11000 collector, 0.30 mm', neck_area_mm2=neck, neck_w_mm=neck_w, neck_len_mm=4.0,
            i_cell_peak_A=round(i_cell_peak, 1), i_cell_cont_A=round(i_cell_cont, 1),
            melt_time_at_cell_peak_s=round(onderdonk_t(i_cell_peak, neck), 1),
            melt_time_at_cell_cont_s=round(onderdonk_t(i_cell_cont, neck), 1),
            shorted_cell_fault_current_A=round(i_fault), each_neighbour_feed_A=round(i_feed_each),
            faulted_cell_neck_opens_ms=round(t_open_faulted * 1e3, 1),
            neighbour_neck_melt_time_ms=round(t_open_feeder * 1e3, 1),
            selective=t_open_feeder > 3 * t_open_faulted,
            neck_R_uohm=round(r_neck * 1e6, 1), neck_loss_at_cell_peak_W=round(i_cell_peak ** 2 * r_neck, 3),
            method='Onderdonk adiabatic melting (conservative for survival at peak, optimistic for opening time)')

# ------------------------------------------------------------------ pack resistance and short circuit
gr = schemes['proposed_lane2_reversed']['groups']
r_cells = SERIES * r_cell / PAR
r_bus = choice['R_links_total_mohm'] / 1000
r_coll = SERIES * 2 * (r_neck / PAR)           # two necks per cell (both ends), six in parallel
r_internal = r_cells + r_bus + r_coll
i_sc_bolted = PACK_V_MAX / r_internal
pack = dict(layout='99s6p', cells=594, energy_kwh_nom=round(594 * CELL['wh'] / 1000, 2), ah=round(PAR * CELL['ah'], 1),
            v_nom=round(PACK_V_NOM, 1), v_max=round(PACK_V_MAX, 1), v_min=round(PACK_V_MIN, 1),
            v_loaded_min_design=V_LOADED_MIN, i_peak_A=round(I_PEAK), t_peak_s=T_PEAK_S, i_cont_A=I_CONT,
            c_rate_peak=round(I_PEAK / (PAR * CELL['ah']), 2), c_rate_cont=round(I_CONT / (PAR * CELL['ah']), 2),
            cell_current_peak_A=round(I_PEAK / PAR, 1),
            r_cells_mohm=round(r_cells * 1e3, 1), r_busbars_mohm=round(r_bus * 1e3, 2), r_necks_mohm=round(r_coll * 1e3, 2),
            r_pack_internal_mohm=round(r_internal * 1e3, 1), i_short_circuit_bolted_A=round(i_sc_bolted),
            interconnect_share_of_pack_R_pct=round(100 * (r_bus + r_coll) / r_internal, 1))

# ------------------------------------------------------------------ modules and BMS taps
modules = []
for lane in (1, 2, 3):
    for k in range(3):
        g0 = (lane - 1) * 33 + k * 11 + 1
        modules.append(dict(module=f'M{lane}{k+1}', lane=lane, groups=f'S{g0:03d}-S{g0+10:03d}', series=11, parallel=6,
                            cells=66, v_nom=round(11 * 3.6, 1), v_max=round(11 * 4.2, 1),
                            energy_kwh=round(66 * CELL['wh'] / 1000, 2), orion_connector=lane, orion_cell_group=(lane - 1) * 3 + k + 1,
                            below_60VDC=11 * 4.2 < 60))
# Tap map: Orion connector n covers BMS taps 36(n-1)+1 .. 36n in three cell groups of 12; we populate 11 per group,
# the 12th tap of each group is tied to the group's top cell (Orion wiring manual rule for <12 cells).
taps = []
gr_p = schemes['proposed_lane2_reversed']['groups']
for g in range(1, SERIES + 1):
    lane = (g - 1) // 33 + 1; k = ((g - 1) % 33) // 11; i = (g - 1) % 11
    bms_tap = 36 * (lane - 1) + 12 * k + i + 1
    top = gr_p[g][-1]
    taps.append(dict(series_group=f'S{g:03d}', bms_cell=bms_tap, orion_connector=lane, cell_group=(lane - 1) * 3 + k + 1,
                     tap_on='positive busbar of group', x_mm=top['x'], y_mm=top['y'], z_mm=top['z']))
# sense-wire length: from tap (busbar) to the lane's pass-through on the pack lid at rear-top, then to the BMS
PASS = dict(x=700.0, z=613.5)     # pack lid connector (saved coords), rear of the top band
BMS_IN = dict(x=775.0, z=856.0)   # Orion connector face (front-bottom of the BMS STEP)
for t in taps:
    inside = abs(t['x_mm'] - PASS['x']) + abs(t['z_mm'] - PASS['z']) + abs(t['y_mm'])  # Manhattan along faces
    outside = math.hypot(BMS_IN['x'] - PASS['x'], BMS_IN['z'] - PASS['z']) * 1.25 + 60
    t['wire_len_mm'] = round(inside + outside)
    t['wire'] = '22 AWG UL11028 600 V (Orion spec), 2 A 500 VDC fuse at tap'
with open(OUT / 'bms-tap-map.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(taps[0].keys())); w.writeheader(); w.writerows(taps)

# Thermistors: lane 2 (sandwiched, hottest) one per group; lanes 1 and 3 one per two groups; plus specials.
therm = []
for g in range(1, SERIES + 1):
    lane = (g - 1) // 33 + 1
    if lane == 2 or g % 2 == 1:
        c = gr_p[g][PAR // 2]
        therm.append(dict(id=f'T{len(therm)+1:02d}', location=f'cell can S{g:03d}P{PAR//2+1}, mid-group, busbar end',
                          x_mm=c['x'], y_mm=c['y'], z_mm=c['z'], input='Orion thermistor expansion module'))
specials = [('pack+ terminal busbar', 'Orion local 1'), ('pack- terminal busbar', 'Orion local 2'),
            ('MSD link S066/S067', 'Orion local 3'), ('lane link S033/S034', 'Orion local 4'),
            ('coolant inlet', 'Orion local 5'), ('coolant outlet', 'Orion local 6'),
            ('BDU contactor bay air', 'Orion local 7'), ('pack interior air (top)', 'Orion local 8')]
for loc, inp in specials:
    therm.append(dict(id=f'T{len(therm)+1:02d}', location=loc, x_mm='', y_mm='', z_mm='', input=inp))
with open(OUT / 'thermistor-map.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(therm[0].keys())); w.writeheader(); w.writerows(therm)

# ------------------------------------------------------------------ face stack and CAD gaps
face_stack = COLLECTOR_T + choice['t_mm'] + FILM_T
outer_gap_req = face_stack + 1.0 + 1.5        # + compliance pad + tap-wire/fuse height
lane_gap_req = 2 * face_stack + 1.0 + 2.0     # two faces + 1 mm barrier (FR4/PI) + sense-wire channel
cad = dict(outer_end_gap_now_mm=2.0, outer_end_gap_required_mm=round(outer_gap_req, 1),
           lane_gap_now_mm=8.0, lane_gap_required_mm=round(lane_gap_req, 1),
           pack_half_width_now_mm=194.0)
d_outer = max(0, outer_gap_req - 2.0); d_lane = max(0, lane_gap_req - 8.0)
cad['lanes_proposed_mm'] = [-(128 + d_lane), 0.0, 128 + d_lane]
cad['YI_proposed_mm'] = round(128 + d_lane + 60 + outer_gap_req, 1)
cad['pack_half_width_proposed_mm'] = round(cad['YI_proposed_mm'] + 4.0, 1)

# ------------------------------------------------------------------ summary
cur, prop = schemes['current']['links'], schemes['proposed_lane2_reversed']['links']
def worst_cross(ls):
    return max((L for L in ls if L['cross_lane']), key=lambda L: L['full_current_span_mm'])
summary = dict(
    prepared='2026-11-12 US Central, Claude Opus 5.5 (claude-opus-5-5)',
    cell=CELL, pack=pack, busbar_choice=choice, hand_check_link=hand, cell_fuse_neck=fuse,
    numbering=dict(
        current=dict(lane_links=[(L['g'], L['full_current_span_mm']) for L in cur if L['cross_lane']],
                     pack_neg=terminal(schemes['current']['groups'], 1, True), pack_pos=terminal(schemes['current']['groups'], 99, False)),
        proposed=dict(lane_links=[(L['g'], L['full_current_span_mm']) for L in prop if L['cross_lane']],
                      pack_neg=terminal(gr_p, 1, True), pack_pos=terminal(gr_p, 99, False),
                      msd_link='S066->S067 at bottom-rear (lane 2 end, lane 3 start)')),
    modules=modules, bms=dict(unit='Orion BMS2 108-cell (3 connectors x 3 cell groups x 12 taps)', groups_used=9,
                              cells_per_group=11, unused_taps_per_group=1, min_group_voltage_V=11 * 2.5,
                              orion_min_group_V=11.0, sense_wires=len(taps) + 1,
                              sense_wire_len_max_mm=max(t['wire_len_mm'] for t in taps),
                              sense_wire_len_total_m=round(sum(t['wire_len_mm'] for t in taps) / 1000 + 1.0, 1),
                              thermistors=len(therm), thermistors_on_expansion=sum(1 for t in therm if 'expansion' in t['input'])),
    face_stack_mm=round(face_stack, 2), cad_gaps=cad,
)
json.dump(summary, open(OUT / 'pack-electrical.json', 'w'), indent=1, default=str)
print(json.dumps({k: summary[k] for k in ('pack', 'busbar_choice', 'hand_check_link', 'cell_fuse_neck', 'cad_gaps')}, indent=1))
print('numbering', json.dumps(summary['numbering'], indent=0, default=str))
print('bms', summary['bms'])

# ------------------------------------------------------------------ purchasable fallback: Molicel P60B 21700, 100s15p
# Supplier audit (Nov 13): 26120 cells are not on open sale. Molicel INR-21700-P60B is: 6.0 Ah, 12.8 mOhm (Molicel
# launch release), 5C charge (13 min full). Mass is not in the sources found: 70 g assumed (P50B class). OPEN.
P60 = dict(ah=6.0, v_nom=3.6, v_max=4.2, v_min=2.5, dcir_mohm=12.8, mass_g=70.0, d_mm=21.0, l_mm=70.0)
S2, P2 = 100, 15
alt = dict(cell='Molicel INR-21700-P60B', layout=f'{S2}s{P2}p', cells=S2 * P2,
           energy_kwh=round(S2 * P2 * P60['ah'] * P60['v_nom'] / 1000, 2), v_max=S2 * P60['v_max'], v_nom=S2 * P60['v_nom'],
           ah=P2 * P60['ah'], cells_kg=round(S2 * P2 * P60['mass_g'] / 1000, 1))
alt['i_peak_A'] = round(P_PEAK_W / (S2 * 3.0))                 # same 3.0 V/cell loaded floor
alt['cell_current_peak_A'] = round(alt['i_peak_A'] / P2, 1)
alt['c_rate_peak'] = round(alt['i_peak_A'] / alt['ah'], 2)
alt['charge_10_80_min_at_5C_cap'] = round(0.7 * 60 / min(5.0, 98e3 / (S2 * 3.77) / alt['ah']), 1)
alt['r_cells_mohm'] = round(S2 * P60['dcir_mohm'] / P2, 1)
alt['cell_heat_at_260A_W'] = round(I_CONT ** 2 * alt['r_cells_mohm'] / 1000)
alt['cell_heat_26120_at_260A_W'] = round(I_CONT ** 2 * pack['r_cells_mohm'] / 1000)
alt['i_short_circuit_A'] = round(alt['v_max'] / ((alt['r_cells_mohm'] + 6.0) / 1000))
# packaging: 21700 is 70 mm long -> 5 transverse lanes instead of 3; side-view area per lane at 23 mm hex pitch
lane_w = 5 * 70 + 4 * cad['lane_gap_required_mm'] + 2 * cad['outer_end_gap_required_mm']
alt['lanes'] = 5
alt['pack_inner_width_mm'] = round(lane_w, 1); alt['pack_outer_width_mm'] = round(lane_w + 8, 1)
alt['side_area_needed_mm2'] = round(S2 * P2 / 5 * 23.0 ** 2 * math.sqrt(3) / 2)
alt['side_area_now_mm2'] = round(198 * 28.0 ** 2 * math.sqrt(3) / 2)
alt['bms'] = 'Orion BMS2 108: 100 groups as 34 + 33 + 33 per connector (cell groups 12/11/11, 11/11/11, 11/11/11); MSD at a connector boundary'
alt['fusing'] = 'per-cell fusible necks still needed (15 cells feed a shorted one); 3,000 cell-end welds vs 1,188'
alt['verdict'] = 'electrically fine (29 A per cell at peak is inside P60B ratings); costs: pack ~36 mm wider, 1.7x the cell heat at 260 A, 2.5x the welds'
summary['alternative_p60b'] = alt
json.dump(summary, open(OUT / 'pack-electrical.json', 'w'), indent=1, default=str)
print('P60B alternative', json.dumps(alt, indent=1))
