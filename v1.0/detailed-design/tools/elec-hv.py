"""Bavuso V1.0 adventure: HV system detailed design + CAD routing check.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).

  1. Protection coordination: mid-pack fused MSD, pyro-fuse, main/charge contactors, precharge sweep, discharge.
  2. HV cable gauge sweep from a heat balance (continuous + 30 s peak), with ambient/bundle derating.
  3. Proposed HV enclosures and cable routes (saved-model coordinates: generator +40 mm Z) with lengths,
     bend radii, voltage drop; every route and box is checked against the saved CAD with FreeCAD distToShape.
  4. Insulation coordination per IEC 60664-1 (creepage/clearance) and ISO 6469-3 / ECE R136 items.
Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe -I detailed-design/tools/elec-hv.py
Needs elec-pack.py output (detailed-design/electrical/pack-electrical.json).
"""
import csv, json, math, sys, os
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / 'detailed-design' / 'electrical'
pack = json.load(open(OUT / 'pack-electrical.json'))['pack']
V_MAX, V_NOM = pack['v_max'], pack['v_nom']
I_PEAK, I_CONT = pack['i_peak_A'], pack['i_cont_A']
I_SC = pack['i_short_circuit_bolted_A']
res = {}

# ------------------------------------------------------------------ 1. protection and precharge
C_LINK = {'traction inverter DC link (CM200DX reference 650 uF; contract SiC unit assumed similar)': 650e-6,
          'DC-DC input (HELLA-class 1.5 kW, est.)': 20e-6, 'OBC output (BROGEN PV1776, est.)': 40e-6,
          'Y-caps and cable (est.)': 5e-6}
C_TOT = sum(C_LINK.values())
pre = []
for Rp in (47, 68, 100, 150, 220, 330):
    tau = Rp * C_TOT
    t95 = -tau * math.log(0.05)            # to 95% of pack voltage
    e = 0.5 * C_TOT * V_MAX ** 2           # energy dissipated in R equals energy stored (series RC charge)
    p0 = V_MAX ** 2 / Rp
    p_fault_1s = p0                        # precharging into a shorted bus until the 3-tau timeout
    e_fault = p0 * 3.2 * tau
    pre.append(dict(R_ohm=Rp, tau_s=round(tau, 3), t95_s=round(t95, 3), I0_A=round(V_MAX / Rp, 2), P0_W=round(p0),
                    E_per_event_J=round(e, 1), E_into_short_until_timeout_J=round(e_fault), ok=(t95 <= 0.5 and V_MAX / Rp <= 10)))
pre_choice = min((p for p in pre if p['ok']), key=lambda p: p['P0_W'])
dV_close = 0.05 * V_MAX
res['precharge'] = dict(C_total_uF=round(C_TOT * 1e6), components_uF={k: round(v * 1e6) for k, v in C_LINK.items()},
                        sweep=pre, choice=pre_choice,
                        rule=f'close main+ when bus >= 95 pct of pack (dV <= {dV_close:.0f} V); abort and latch if not reached in 3.2 tau',
                        resistor='TE Connectivity (CGS) HSC100 series, 100 W aluminium-housed wirewound, %d ohm; pulse energy rating to be confirmed with TE for the into-short case' % pre_choice['R_ohm'],
                        relay='TE Kilovac LEV100 series (100 A, 900 VDC), 12 V coil; suffix to confirm')
tau_pass = 70e3 * 650e-6
res['discharge'] = dict(passive_bleed_kohm=70, tau_s=round(tau_pass, 1),
                        passive_t_to_60V_s=round(tau_pass * math.log(V_MAX / 60), 1),
                        active_target='inverter active discharge to <60 V in <=3 s after contactors open (ISO 6469-3 / R136: below 60 VDC or 0.2 J within manufacturer-stated time)',
                        energy_J=round(0.5 * C_TOT * V_MAX ** 2, 1))

# fuse coordination (time-current sanity at the points that matter)
res['protection'] = dict(
    bolted_short_circuit_A=I_SC,
    layers=[
        dict(layer='cell', device='fusible neck in Ni-Cu collector (per cell, both ends)', clears='internal cell short, crushed cell', speed='~20 ms at ~5 kA'),
        dict(layer='mid-pack', device='MSD with integrated 400 A fuse, Amphenol MSD08 family (fused 200-400 A, HVIL)', clears='bolted pack short (7.5 kA) and halves the pack for service',
             note='fused MSD rated 690 V(AC catalogue); DC breaking capacity at 416 V and I2t vs 30 s 433 A peak to confirm with Amphenol'),
        dict(layer='pack+', device='Sensata STP500P pyrotechnic breaker (500 A cont, 500 V / 22 kA break, <1 ms active)', clears='crash (IMU/ABS crash flag), mid-current faults 600 A-3 kA where the fuse is slow, contactor weld',
             trigger='VCU: IVT-S current > 650 A for > 20 ms, or > 480 A for > 40 s, or crash signal; BMS hard fault'),
        dict(layer='contactors', device='2 x GIGAVAC GX14 (350 A cont on 2/0, 12-800 VDC); open only below ~350 A (coordinated: pyro clears above)', clears='normal isolation, key-off, BMS open request'),
        dict(layer='branches', device='Eaton Bussmann EV fuses: OBC 30 A, DC-DC 10 A, battery heater 15 A', clears='branch cable faults'),
    ],
    coordination_checks=dict(
        peak_433A_30s_vs_400A_fuse='fuse at 1.08 x In for 30 s: below the ~1.3 x In conventional non-fusing level of EV fuses -> holds (confirm on curve)',
        cont_260A_vs_400A_fuse_derated='400 A x 0.8 thermal derate = 320 A > 260 A -> OK',
        pyro_cont_500A_vs_433A_peak='OK',
        gx14_350A_cont_vs_260A='OK, 1.35 x margin; 433 A for 30 s exceeds 350 A cont -> needs GIGAVAC overload curve (open)',
        short_7_5kA_vs_pyro_22kA='OK 2.9 x', short_7_5kA_vs_fuse_breaking='typ 20-50 kA for EV fuses -> OK, confirm'))

# ------------------------------------------------------------------ 2. HV cable sweep (Coroplast/Coroflex FHLR2GCB2G shielded)
CABLE = {  # mm2: (OD mm, mass g/m, R20 mohm/m). 50 mm2 from Coroflex 9-2611 sheet (0.368 mohm/m, ~630 g/m, OD 15.8);
           # 35 mm2 mass 485 g/m from Coroflex sheet; others scaled from IEC 60228 class 6 resistance.
    16: (10.6, 230, 1.21), 25: (12.2, 340, 0.780), 35: (13.6, 485, 0.554), 50: (15.8, 630, 0.368), 70: (18.0, 860, 0.272)}
T_COND_MAX = 150.0       # conductor limit for the 150 C class shielded cables used (ISO 6722 class E/F region)
def ampacity(mm2, T_amb, derate):
    OD, _, r20 = CABLE[mm2]
    h = 11.0                                    # W/m2K, still air natural convection + radiation (e~0.9) at ~100 K rise
    k_ins = 0.25                                # W/mK silicone/XLPE, insulation+jacket radial resistance
    d_c = math.sqrt(4 * mm2 / math.pi) * 1.15   # stranded conductor OD
    R_ins = math.log(OD / d_c) / (2 * math.pi * k_ins)
    R_conv = 1 / (h * math.pi * OD / 1000)
    r = r20 / 1000 * (1 + 0.00393 * (T_COND_MAX - 20))
    I = math.sqrt((T_COND_MAX - T_amb) / ((R_ins + R_conv) * r))
    return I * derate
def adiabatic_rise(mm2, I, t):
    r20 = CABLE[mm2][2] / 1000
    r = r20 * (1 + 0.00393 * (90 - 20))
    m_cu = 8960 * mm2 * 1e-6
    return I * I * r * t / (m_cu * 385)
cab = []
for mm2 in CABLE:
    for env, Ta, der in (('free air 40 C', 40, 1.0), ('body/motor bay 65 C, pair in conduit', 65, 0.80)):
        Ia = ampacity(mm2, Ta, der)
        cab.append(dict(mm2=mm2, environment=env, ampacity_A=round(Ia), od_mm=CABLE[mm2][0], g_per_m=CABLE[mm2][1],
                        dT_30s_at_433A_from_90C_K=round(adiabatic_rise(mm2, I_PEAK, 30), 1),
                        meets_260A_cont=Ia >= I_CONT, meets_peak=adiabatic_rise(mm2, I_PEAK, 30) <= 40))
def charge_end_temp(mm2, T_amb, derate, I=I_CONT, t=14 * 60):
    """Conductor temperature at the end of a 14-min DC fast charge, first-order thermal model.
    The bundle derating is applied as a thermal resistance multiplier 1/derate^2 (same steady current ratio)."""
    OD, g_m, r20 = CABLE[mm2]
    d_c = math.sqrt(4 * mm2 / math.pi) * 1.15
    Rth = (math.log(OD / d_c) / (2 * math.pi * 0.25) + 1 / (11.0 * math.pi * OD / 1000)) / derate ** 2
    C = 8960 * mm2 * 1e-6 * 385 + (g_m / 1000 - 8960 * mm2 * 1e-6) * 1500      # copper + insulation/shield heat capacity per m
    T = 90.0 if False else T_amb                                                  # start at ambient (parked bike)
    dt = 1.0
    for _ in range(int(t)):
        r = r20 / 1000 * (1 + 0.00393 * (T - 20))
        T += (I * I * r - (T - T_amb) / Rth) / C * dt
    return T, Rth * C
for c in cab:
    Ta, der = (40, 1.0) if '40' in c['environment'] else (65, 0.80)
    Tend, tau = charge_end_temp(c['mm2'], Ta, der)
    c['T_end_14min_charge_C'] = round(Tend, 1); c['tau_thermal_s'] = round(tau)
    c['meets_charge_transient'] = Tend <= T_COND_MAX
res['cable_sweep'] = cab
# Selection rule: the 260 A case is the 14-min fast charge (bike parked); riding at 260 A happens only near top speed,
# with airflow. So a gauge passes if it meets the 30 s peak AND either steady 260 A or the 14-min charge transient,
# in the hot, bundled case.
DC_GAUGE = min(m for m in CABLE if all((c['meets_260A_cont'] or c['meets_charge_transient']) and c['meets_peak']
                                       for c in cab if c['mm2'] == m and '65' in c['environment']))
# hand check against published data: Coroflex 50 mm2 class cables are commonly rated ~250-270 A at 85 C ambient
res['cable_choice'] = dict(dc_mm2=DC_GAUGE, phase_mm2=DC_GAUGE, cable='Coroplast Coroflex FHLR2GCB2G shielded, 600 V AC / 1000 V DC, orange',
                           part_50mm2='Coroflex 9-2611 (50 mm2)', bend_radius_static_x_od=3, bend_radius_dynamic_x_od=6)

# ------------------------------------------------------------------ 3. enclosures and routes (saved-model coordinates, mm)
BOX = {  # iteration 2 (Nov 13): BDU kept behind the tank rear wall (X690-693, present from Z~700 up), phases outside it
  'BDU_upper_positive_junction': dict(box=(606, 686, -125, 82, 645, 765), contents='Sensata STP500P pyro, GX14 main+, LEV100 + HSC100 precharge, OBC/DC-DC/heater EV fuses, HV+ and HV- distribution bars, HVIL loop; front connectors through a cut-out in the tank rear wall'),
  'RJB_rear_negative_junction (existing HV_cabinet envelope)': dict(box=(445, 580, -20, 95, 245, 398), contents='GX14 main-, IVT-S-500-U3 shunt on pack-, MSD08 fused service disconnect in link S066/S067'),
  'CJB_charge_junction': dict(box=(730, 860, 116, 176, 640, 760), contents='2 x GX14 DC charge contactors stacked, 2-pole AC relay pair to OBC (interlocked)'),
  'NACS_inlet_Volex_1000V': dict(box=(860, 928, 127, 222, 845, 929), contents='Volex NACS 1000 V inlet, 84 x 68 x 95 mm, 500 A cont; face at Y+222 under a hinged door'),
  'DCDC_1kW_envelope_left_pocket': dict(box=(720, 950, -180, -120, 622, 762), contents='HV/12 V DC-DC >=0.75 kW, required envelope 230 x 60 x 140 mm (HELLA unit size to confirm)'),
  'LV_battery_Shorai_LFX14A4_under_seat': dict(box=(512, 599, -75, 75, 670, 763), contents='12 V LiFePO4 150 x 87 x 93 mm, long side across the bike'),
  'VCU_envelope_left_upper': dict(box=(770, 950, -150, -110, 785, 863), contents='VCU 200 x 78 x 40 mm, on edge beside the inverter'),
  'PDM_envelope_right_upper': dict(box=(765, 855, 108, 148, 785, 865), contents='LV smart distribution 90 x 40 x 80 mm envelope (custom PDU; PMU16 prototype is larger, bench only)'),
}
ROUTES = {  # name: (points, cable mm2, conductors, ends-to-ignore)
  'HV+ pack lid stud -> BDU': ([(985, 150, 614), (985, 186, 628), (700, 186, 628), (668, 120, 628), (650, -20, 628), (650, -20, 650)], DC_GAUGE, 1,
                               ['Pack_case_structural_4mm_STUDY', 'Battery_installation_keepout', 'BDU']),
  'HV- pack rear (S001) -> RJB': ([(588, -5, 283), (560, -5, 283)], DC_GAUGE, 1, ['Pack_case_structural_4mm_STUDY', 'Battery_installation_keepout', 'RJB', 'HV_cabinet_2mm_STUDY', 'GX14_main_negative_OUTLINE', 'GX14_main_positive_OUTLINE', 'Main_fuse_branch_search_region']),
  'HV- bus RJB -> BDU (left channel)': ([(575, -12, 252), (574, -60, 258), (574, -100, 275), (574, -100, 300), (603, -130, 324), (610, -135, 450), (640, -135, 630), (650, -110, 670)], DC_GAUGE, 1,
                               ['RJB', 'HV_cabinet_2mm_STUDY', 'BDU', 'GX14_main_negative_OUTLINE', 'GX14_main_positive_OUTLINE', 'Main_fuse_branch_search_region']),
  'MSD links S066/S067 -> RJB': ([(588, 64, 285), (565, 64, 285)], DC_GAUGE, 2, ['Pack_case_structural_4mm_STUDY', 'Battery_installation_keepout', 'RJB', 'HV_cabinet_2mm_STUDY', 'Main_fuse_branch_search_region', 'GX14_main_negative_OUTLINE', 'GX14_main_positive_OUTLINE']),
  'Inverter DC+/DC- (BDU -> inverter rear, through tank wall)': ([(680, -40, 725), (712, -40, 725)], DC_GAUGE, 2, ['BDU', 'Cascadia_CM200_supplier_STEP', 'Upper_body_fairing_tank_STUDY']),
  'Motor phases U/V/W (inverter rear -> motor top terminal)': ([(712, 120, 725), (686, 120, 725), (620, 120, 700), (605, 118, 668), (598, 100, 648)], DC_GAUGE, 3,
                               ['Cascadia_CM200_supplier_STEP', 'IPM_motor_and_gear_case_ENVELOPE', 'Upper_body_fairing_tank_STUDY']),
  'DC charge+/- inlet -> CJB': ([(900, 125, 880), (900, 140, 790), (850, 146, 760)], DC_GAUGE, 2, ['NACS', 'CJB']),
  'DC charge+/- CJB -> BDU': ([(732, 148, 660), (690, 132, 660), (672, 78, 665)], DC_GAUGE, 2, ['CJB', 'BDU']),
  'OBC DC out -> BDU (4 mm2)': ([(705, -60, 660), (680, -60, 660)], 4, 2, ['BROGEN_PV1776_body', 'BDU']),
  'DC-DC HV in (2.5 mm2)': ([(680, -110, 660), (722, -150, 660)], 4, 2, ['BDU', 'DCDC']),
}
for name, (pts, mm2, n, ign) in ROUTES.items():
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) + 80     # +40 mm each end for lug/connector
    bends = []
    for i in range(1, len(pts) - 1):
        a = [pts[i][k] - pts[i - 1][k] for k in range(3)]; b = [pts[i + 1][k] - pts[i][k] for k in range(3)]
        cosang = sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))
        turn = math.degrees(math.acos(max(-1, min(1, cosang))))
        seg = min(math.hypot(*a), math.hypot(*b))
        od = CABLE.get(mm2, (6.5, 60, 4.7))[0]
        rmin = 3 * od                                    # static installation, Coroflex sheet
        # space available for the bend: the shorter adjacent segment must hold the tangent length R*tan(turn/2)
        tan_len = rmin * math.tan(math.radians(turn) / 2) if turn > 1 else 0
        bends.append(dict(turn_deg=round(turn), r_min_mm=round(rmin, 1), tangent_needed_mm=round(tan_len, 1), shorter_segment_mm=round(seg, 1), ok=tan_len <= seg / 2 + 1e-6 or turn < 1))
    r = CABLE.get(mm2, (6.5, 60, 4.7))[2] / 1000 * (1 + 0.00393 * 70)
    I_route = 22 if mm2 == 4 else I_PEAK
    ROUTES[name] = dict(points=pts, mm2=mm2, conductors=n, length_each_mm=round(L), bends=bends,
                        vdrop_peak_V=round(I_route * r * L / 1000 * (2 if 'DC+/' in name or 'charge' in name else 1), 3),
                        loss_cont_W=round((I_CONT if mm2 != 4 else 22) ** 2 * r * L / 1000 * n, 1),
                        mass_kg=round(CABLE.get(mm2, (6.5, 60, 4.7))[1] * L / 1e6 * n, 3), ignore=ign)

# ------------------------------------------------------------------ 4. insulation coordination (IEC 60664-1)
# Working voltage 416 V DC -> use the 500 V rows (no interpolation credit). Rated impulse withstand: on-board DC
# system, galvanically isolated from mains in drive, but connected to EVSE in DC charging -> treat as OVC II, 600 V
# class -> 4 kV impulse (Table F.1). Clearance for 4 kV, inhomogeneous field, PD2/PD3: 3.0 mm (Table F.2).
# Creepage, Table F.5, 500 V: PD2 MG I/II/IIIa = 2.5/3.6/5.0 mm; PD3 = 6.3/7.1/8.0 mm.
ins = [
  dict(location='inside sealed pack (IP67, desiccant breather) - busbar to busbar / to case', PD=2, MG='IIIa (PI film, PC, FR4 CTI>=175)', creepage_req_mm=5.0, clearance_req_mm=3.0, design_mm=8.0, how='0.5 mm PI film on all busbars + PC barrier between lanes; lane gap 12.6 mm'),
  dict(location='cell-to-cell adjacent groups in a row (max 4.2 V, intra-lane)', PD=2, MG='IIIa', creepage_req_mm=0.04, clearance_req_mm=0.2, design_mm=2.0, how='PET cell sleeve + 2 mm gap; full pack voltage never appears between neighbours in the proposed snake (max lane-to-lane 139 V across a barrier)'),
  dict(location='lane-to-lane barrier (up to 139 V between lanes away from links)', PD=2, MG='IIIa', creepage_req_mm=1.6, clearance_req_mm=0.5, design_mm=12.6, how='1 mm PC/FR4 barrier sheet in the lane gap'),
  dict(location='BDU / RJB / CJB internals (IP67 boxes, but condensation possible)', PD=3, MG='IIIa', creepage_req_mm=8.0, clearance_req_mm=3.0, design_mm=10.0, how='contactor/fuse terminals on raised PA66-GF ribs; 10 mm creepage designed in'),
  dict(location='Orion sense harness at pack lid pass-through', PD=2, MG='IIIa', creepage_req_mm=5.0, clearance_req_mm=3.0, design_mm=5.0, how='Orion connector 2.5 kVrms between connectors; sealed lid feed-through'),
  dict(location='HV cable shield to conductor', PD='n/a (solid insulation)', MG='-', creepage_req_mm=0, clearance_req_mm=0, design_mm=0, how='cable rated 1000 V DC, 5 kV test'),
]
res['insulation'] = ins
res['hv_safety_items'] = [
  ('Isolation resistance', 'ISO 6469-3 / R136: >=100 ohm/V DC circuits, >=500 ohm/V if AC (OBC) galvanically connected', '416 V x 500 = 208 kohm warning; 100 ohm/V = 41.6 kohm min; Bender iso175 set 500 kohm warn / 100 kohm fault + Orion internal check as plausibility'),
  ('Protection against direct contact', 'IPXXD inside passenger/rider zones, IPXXB in pack/motor bay', 'all HV boxes IP67 with tool-only lids; MSD finger-proof IPXXB when removed'),
  ('Indirect contact / equipotential', 'exposed conductive parts bonded, <0.1 ohm at 0.2 A', 'pack case, BDU/RJB/CJB, inverter, motor, OBC, DC-DC bonded to frame with 6 mm2 straps; frame = LV ground'),
  ('HVIL', 'interlock opens contactors when any HV connector or lid is opened', 'single loop through MSD, BDU lid, CJB lid, inverter, OBC, DC-DC, inlet; VCU monitors 20 mA PWM loop'),
  ('Marking', 'orange HV cables, ISO 7010 W012 symbol on HV boxes', 'Coroflex orange jacket, labels on all enclosures'),
  ('Charging inlet', 'no hazardous voltage at inlet when unplugged (R136 / J3400)', 'DC charge contactors normally open, weld check before unlock; AC relays interlocked; inlet voltage sensed by IVT-S U3'),
  ('Water immersion / IP', 'R136 water exposure (IPX5/IPX7 equivalent for L-category)', 'pack, boxes and connectors IP67; breather: GORE PolyVent on pack and boxes'),
  ('Functional safety of driving state', 'R136: active driving possible mode indicated, unintended movement prevented', 'VCU: READY lamp, brake + start, side-stand interlock, throttle plausibility'),
  ('Post-crash', 'R136 / ISO 6469-3: HV isolated automatically', 'IMU crash flag (ABS unit) fires pyro + opens contactors <20 ms'),
]
res['emc'] = [
  ('Inverter DC input', 'X/Y capacitors inside inverter; add ferrite rings (e.g. Vacuumschmelze VITROPERM nanocrystalline) over DC pair at BDU exit'),
  ('Motor phases', 'shielded 3-core-as-3-single cables, 360 deg shield termination at both ends (Amphenol PowerLok shielded backshells); keep < 0.3 m'),
  ('DC-DC and OBC', 'built-in EMC filters (supplier); shields bonded at both ends; LV output twisted pair'),
  ('CAN', '120 ohm split terminations at both ends, twisted pair 1 twist/25 mm, routed > 50 mm from phase cables'),
  ('Standards', 'UNECE R10.06 (EMC) for type approval; CISPR 25 class 3 targets for receivers on board'),
]

# ------------------------------------------------------------------ 5. CAD check (FreeCAD)
try:
    if os.environ.get("ELEC_NO_CAD"): raise ImportError
    import FreeCAD as A, Part
    doc = A.openDocument(str(R / 'cad' / 'Bavuso-V1.0-adventure.FCStd'))
    objs = [o for o in doc.Objects if o.TypeId.startswith('Part::Feature') and hasattr(o, 'Shape') and not o.Shape.isNull()]
    skip_always = {'Cell_lane_1', 'Cell_lane_2', 'Cell_lane_3'}   # inside the pack case; case stands in
    def mkbox(b):
        x0, x1, y0, y1, z0, z1 = b
        return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, A.Vector(x0, y0, z0))
    boxes = {k: mkbox(v['box']) for k, v in BOX.items()}
    def tag(name):
        for t in ('BDU', 'RJB', 'CJB', 'NACS', 'DCDC', 'LV_battery', 'VCU', 'PDM'):
            if t in name: return t
        return name
    def nearest(shape, ignore):
        best = []
        sb = shape.BoundBox
        for o in objs:
            if o.Name in skip_always or o.Name in ignore: continue
            ob = o.Shape.BoundBox
            gap_bb = max(ob.XMin - sb.XMax, sb.XMin - ob.XMax, ob.YMin - sb.YMax, sb.YMin - ob.YMax, ob.ZMin - sb.ZMax, sb.ZMin - ob.ZMax, 0)
            if gap_bb > 40: continue            # bounding boxes > 40 mm apart: cannot be the nearest that matters
            d = shape.distToShape(o.Shape)[0]
            best.append((d, o.Name))
        for k, s in boxes.items():
            if tag(k) in ignore or s.isSame(shape): continue
            best.append((shape.distToShape(s)[0], k))
        best.append((40.0, "nothing else within 40 mm"))
        best.sort()
        return best[:4]
    check = {}
    for k, s in boxes.items():
        ign = {'HV_cabinet_2mm_STUDY', 'GX14_main_negative_OUTLINE', 'GX14_main_positive_OUTLINE', 'Main_fuse_branch_search_region'} if 'RJB' in k else set()
        if 'NACS' in k: ign |= {'Upper_body_fairing_tank_STUDY'}     # the inlet is meant to pierce the tank skin
        near = [(d, n) for d, n in nearest(s, ign) if n != k]
        check[k] = dict(min_gap_mm=round(near[0][0], 1), nearest=[(round(d, 1), n) for d, n in near[:3]], ok=near[0][0] >= 3.0)
    for name, rt in ROUTES.items():
        od = CABLE.get(rt['mm2'], (6.5, 60, 4.7))[0]
        pts = [A.Vector(*p) for p in rt['points']]
        segs = []
        for i in range(len(pts) - 1):
            d = pts[i + 1] - pts[i]
            if d.Length < 1: continue
            segs.append(Part.makeCylinder(od / 2 * (1.6 if rt['conductors'] > 1 else 1), d.Length, pts[i], d))
        sh = Part.makeCompound(segs)
        near = nearest(sh, set(rt['ignore']) | {'Pack_case_structural_4mm_STUDY' if 'pack' in name.lower() else ''})
        check[name] = dict(min_gap_mm=round(near[0][0], 1), nearest=[(round(d, 1), n) for d, n in near[:3]], ok=near[0][0] >= 3.0)
    res['cad_check'] = check
    A.closeDocument(doc.Name)
except ImportError:
    res['cad_check'] = 'FreeCAD not available: run with the FreeCAD python'

res['boxes'] = BOX
res['routes'] = {k: {kk: vv for kk, vv in v.items() if kk != 'ignore'} for k, v in ROUTES.items()}
json.dump(res, open(OUT / 'hv-system.json', 'w'), indent=1, default=str)
with open(OUT / 'hv-cables.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['route', 'cable_mm2', 'conductors', 'length_each_mm', 'mass_kg', 'vdrop_peak_V', 'loss_cont_W', 'bends(turn/rmin/ok)', 'cad_min_gap_mm', 'cad_ok', 'points_saved_coords_mm'])
    for k, v in ROUTES.items():
        c = res['cad_check'][k] if isinstance(res['cad_check'], dict) else {}
        w.writerow([k, v['mm2'], v['conductors'], v['length_each_mm'], v['mass_kg'], v['vdrop_peak_V'], v['loss_cont_W'],
                    ';'.join(f"{b['turn_deg']}/{b['r_min_mm']}/{b['ok']}" for b in v['bends']), c.get('min_gap_mm'), c.get('ok'),
                    ' '.join(str(tuple(p)) for p in v['points'])])
with open(OUT / 'insulation-coordination.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(ins[0].keys())); w.writeheader(); w.writerows(ins)
print(json.dumps({k: res[k] for k in ('precharge', 'discharge', 'cable_choice')}, indent=1, default=str)[:3000])
for c in cab: print(c)
print('DC gauge', DC_GAUGE)
for k, v in (res['cad_check'].items() if isinstance(res['cad_check'], dict) else []): print(k, v)
for k, v in ROUTES.items(): print(k, v['length_each_mm'], v['bends'])
