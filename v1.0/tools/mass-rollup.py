"""Bavuso V1 parts ledger, mass roll-up and Gate A budget check.

Reads the CAD solids (cad/Bavuso-V1.0-adventure.FCStd by default, read-only), gives every solid a mass, builds ONE parts ledger
(program/data/parts-ledger.csv, one row per part) and checks it against the Gate A per-system mass budget (program/data/budgets.csv).
How it works and how to run it: program/05-ledger-system.md.

Mass methods (column `method`):
  kg      fixed mass (supplier figure or estimate) placed at the part's CAD centroid
  vol     CAD volume x material density (the CAD shape is close to the real part)
  shell   CAD surface area x wall thickness x density (the CAD is a solid stand-in for a hollow section)
  pack    legacy only: cell volume / one 26120 cell x 180 g
  slot    mass comes from program/data/supplier-masses.csv (matched by NAME PATTERN, so renamed CAD solids still bind)
  slotfill  a supplier slot with no CAD solid: a ledger row without geometry (loud)
  allow   things the CAD does not model (wiring, fasteners, fluids): allowance rows, status concept
Mass-source labels: measured / supplier / calculated / estimate.

Nothing is silently dropped: solids with no rule are listed loudly (stdout, json, and as UNMATCHED rows in the ledger) and the exit code is 2.
Exit codes: 0 ok, 1 a budget is overrun, 2 ledger not clean (unmatched solids, duplicates, missing required parts).  --soft always exits 0.

Coordinates in the saved file: X forward from the rear axle, Z = height above ground, Y left(-)/right(+), mm.
Run (from v1.0):  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/mass-rollup.py [options]
Without FreeCAD:  tools/mass-rollup.py --solids-csv solids.csv   (name,group,vol_mm3,area_mm2,x_mm,y_mm,z_mm; written by --dump-solids)
"""
import argparse, csv, fnmatch, json, math, re, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
DATA = R / 'program/data'
STEEL, ALU, PLASTIC, PC = 7.85, 2.70, 1.05, 1.20          # g/cm3; plastic = painted PP/ABS panel
WB = 1490.0
SRC = dict(S='supplier', C='calculated', E='estimate', M='measured')
GROWTH = dict(concept=0.15, proposed=0.10, **{'design-intent': 0.05}, released=0.01)   # proposed margins, informational
OPT_REF_KG = 222.5
LEG_CELLS, LEG_CELL_G = 594, 180.0

# ---------------------------------------------------------------------------------------------------------------------
# RULES: CAD solids that are NOT supplier slots. glob patterns joined by '|' (case-insensitive, whole name; '*' wildcard).
# When several rules match a solid the MOST SPECIFIC wins (exact name, then longest literal text), not the file order.
#   legacy=True: only used with --legacy (old-bike hardware: in V1 mode the supplier slots replace these).
# kg/vol/shell values are the RECONCILED ones from program/03-mass-ledger.md (double counts already removed).
# ---------------------------------------------------------------------------------------------------------------------
RULES = []
def rule(pat, sys_, meth, val, src, note, uns=None, status=None, mat='', proc='', mb=None, legacy=False, required=False, tag=None):
    if status is None:
        status = 'proposed' if (meth in ('vol', 'shell') and sys_ in ('CHS', 'ENG')) or src == 'S' else 'concept'
    if mb is None: mb = 'make' if meth in ('vol', 'shell') else 'buy'
    RULES.append(dict(pat=pat, sys=sys_, meth=meth, val=val, src=SRC[src], note=note, uns=uns, status=status, mat=mat, proc=proc,
                      mb=mb, legacy=legacy, required=required,
                      tag=tag or re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', pat.split('|')[0].lower().replace('*', ''))).strip('_')))
CRM = dict(mat='25CrMo4 tube', proc='TIG-welded tube')
# ---- energy ----
rule('Pack_case*|Battery_case*|Pack_housing*', 'ENG', 'vol', ALU, 'C', '4 mm aluminium structural case, CAD volume', mat='aluminium 4 mm', proc='fabricated and welded', required=True, tag='pack_case')
rule('Cell_lane_*', 'ENG', 'pack', None, 'E', '594 x 180 g 26120-class cells (cell not on open sale: estimate)', legacy=True, status='concept', tag='cells_legacy')
# ---- drive (legacy hardware; V1 uses supplier slots) ----
rule('IPM_motor_and_gear_case_ENVELOPE', 'DRV', 'kg', 21.0, 'E', 'radial IPM about 14 kg + 2-stage reduction about 7 kg (drive-study.md)', legacy=True)
rule('Front_pulley_PITCH_STUDY', 'DRV', 'kg', 0.4, 'E', '20T 14 mm steel pulley', legacy=True)
rule('Rear_pulley_PITCH_STUDY', 'DRV', 'kg', 1.6, 'E', '62T 14 mm aluminium pulley', uns=('R', 1.0), legacy=True)
rule('Drive_belt_14mm_STUDY', 'DRV', 'kg', 0.5, 'E', '14 mm pitch carbon belt', uns=('R', 0.5), legacy=True)
# ---- electronics ----
rule('Cascadia_CM200_supplier_STEP', 'DRV', 'kg', 6.75, 'S', 'CM200DX, manufacturer-published 6.75 kg', legacy=True)
rule('BROGEN_PV1776_body', 'ELC', 'kg', 3.0, 'S', 'BROGEN catalogue max 3 kg (electrical-bom.csv)', legacy=True)
rule('Orion_BMS2_108_supplier_STEP', 'ELC', 'kg', 1.5, 'E', 'Orion BMS2 108-cell, lightened board set', legacy=True)
rule('HV_cabinet_2mm_STUDY', 'ELC', 'vol', ALU, 'C', '2 mm aluminium cabinet', mat='aluminium 2 mm', proc='folded sheet')
rule('GX14_main_*', 'ELC', 'kg', 0.5, 'S', 'Gigavac GX14 main contactor, datasheet 0.5 kg', legacy=True)
rule('HV_upper_junction_box', 'ELC', 'kg', 2.2, 'E', 'junction box with fuses', legacy=True)
rule('HV_charge_junction_box', 'ELC', 'kg', 1.4, 'E', 'charge contactors box', legacy=True)
rule('DCDC_converter_1p2kW', 'ELC', 'kg', 2.8, 'S', 'HELLA 1.2 kW DC-DC', legacy=True)
rule('NACS_charge_inlet', 'ELC', 'kg', 0.9, 'S', 'Volex NACS inlet incl. door and lock actuator', legacy=True)
rule('Horn_R28', 'ELC', 'kg', 0.4, 'S', 'R28 horn')
rule('Display_reserve', 'ELC', 'kg', 0.6, 'E', '7 in TFT')
rule('Display_glass', 'ELC', 'kg', 0.05, 'E', 'TFT cover glass')
rule('Display_mount', 'ELC', 'kg', 0.15, 'E', 'display bracket')
rule('Headlamp_installation_STUDY', 'ELC', 'kg', 1.2, 'E', 'LED headlamp')
rule('Headlamp_DRL_blade', 'ELC', 'kg', 0.0, 'E', 'DRL: included in the headlamp figure')
rule('Taillamp_installation_STUDY', 'ELC', 'kg', 0.25, 'E', 'LED tail lamp')
rule('Front_indicator_reserve_*', 'ELC', 'kg', 0.05, 'E', 'indicator')
rule('Rear_indicator_reserve_*', 'ELC', 'kg', 0.05, 'E', 'indicator')
rule('Rear_indicator_stalk_*', 'ELC', 'kg', 0.02, 'E', 'indicator stalk')
rule('Plate_lamp', 'ELC', 'kg', 0.05, 'E', 'plate lamp')
# ---- cooling ----
rule('Motor_pulley_bearing_carrier', 'DRV', 'kg', 0.4, 'E', 'aluminium bearing carrier on the motor flange (rev D); was wrongly bound to the pulley slot at 0.5 kg')
rule('Radiator_core_*', 'THM', 'kg', 0.805, 'E', 'dry core with plastic tanks (thermal-study.md); coolant is in the coolant allowance')
rule('Radiator_fan_*', 'THM', 'kg', 0.55, 'E', '190 mm BLDC fan with shroud (thermal-study.md)')
rule('Coolant_pump_*', 'THM', 'kg', 0.55, 'E', 'EWP-class pump, 1.10 kg for two (thermal-study.md)')
rule('Coolant_PTC_heater_5kW', 'THM', 'kg', 1.9, 'E', '5 kW HV PTC heater (thermal-study.md); superseded by the 3 kW unit', legacy=True)
rule('Coolant_PTC_heater_3kW', 'THM', 'kg', 1.14, 'E', '3 kW HV PTC heater, scaled from 1.9 kg for 5 kW (10-thermal.md section 5)')
rule('Coolant_thermostat_wax', 'THM', 'kg', 0.15, 'E', 'wax thermostat replacing the 4-port valve (10-thermal.md: saves 0.30 kg of the 0.45 kg valve)')
rule('Coolant_4port_valve', 'THM', 'kg', 0.45, 'E', '4-port coolant valve')
rule('Oil_cooler', 'THM', 'kg', 0.6, 'E', 'gear-oil cooler (IPM two-stage drive only)', legacy=True)
# ---- protection ----
rule('Crash_guard_*', 'PRO', 'vol', STEEL, 'C', '28x2.5 25CrMo4 crash guard', mat='25CrMo4 tube', proc='TIG-welded tube')
rule('Pivot_slider_*', 'PRO', 'kg', 0.06, 'E', 'POM puck')
rule('Handguard_*', 'PRO', 'vol', ALU, 'C', '22x3 6082 handguard backbone', mat='6082-T6 tube', proc='bent tube')
rule('Side_stand_retracted', 'RUN', 'kg', 1.4, 'E', 'forged side stand with switch')
# ---- frame (chromoly tube, CAD tubes are hollow) ----
for p, n in [('Upper_post_*', '32x2.5 chromoly post'), ('Head_gusset_*', '10 mm 4130 gusset'), ('Shock_bridge_diagonal_*', '25x2.5 chromoly'),
             ('Upper_rail_*', '32x2.5 chromoly'), ('Lower_downlink_*', '32x2.5 chromoly'), ('Lower_pack_rear_link_*', '32x2.5 chromoly'),
             ('Tail_rail_*', '28x2 chromoly'), ('Tail_brace_*', '28x2 chromoly'), ('Tail_shock_cross_tube', '28x3 chromoly'),
             ('Head_tube', 'head tube'), ('Shock_top_bracket', 'twin 8 mm plates, shock mount'), ('Independent_hollow_pivot_stub_*', 'pivot stub')]:
    rule(p, 'CHS', 'vol', STEEL, 'C', n, required=(p == 'Head_tube'), **CRM)
rule('Pivot_6008_size_reference_*', 'CHS', 'kg', 0.12, 'S', '6008 bearing (catalogue 0.12 kg)', uns=('R', 0.5))
# ---- swingarm ----
rule('Swingarm_1', 'CHS', 'shell', (ALU, 4.0), 'C', 'cast A356 box arm, 4.0 mm wall (program structures FEA; rev D)', uns=('R', 0.5), mat='aluminium 4.0 mm wall', proc='fabricated box', required=True)
rule('Swingarm_m1', 'CHS', 'shell', (ALU, 4.0), 'C', 'cast A356 box arm, 4.0 mm wall (program structures FEA; rev D)', uns=('R', 0.5), mat='aluminium 4.0 mm wall', proc='fabricated box')
rule('Swingarm_cross_brace', 'CHS', 'vol', ALU, 'C', '50x5 aluminium tube', uns=('R', 0.5), mat='aluminium tube', proc='tube')
rule('Swingarm_shock_tower', 'CHS', 'vol', ALU, 'C', 'twin 8 mm aluminium plates', uns=('R', 0.5), mat='aluminium plate', proc='plate')
# ---- running gear: wheels/tyres/brakes/fork/shock (legacy; V1 = supplier slots) ----
rule('Front_nominal_tire', 'RUN', 'kg', 4.5, 'S', '120/70R19 adventure tyre (retail ~4.5 kg)', uns=('F', 1.0), legacy=True)
rule('Rear_nominal_tire', 'RUN', 'kg', 6.4, 'E', '170/60R17 adventure tyre', uns=('R', 1.0), legacy=True)
rule('Front_wheel_STUDY', 'RUN', 'kg', 3.4, 'E', 'forged aluminium 19x3.0 with bearings', uns=('F', 1.0), legacy=True)
rule('Rear_wheel_STUDY', 'RUN', 'kg', 4.2, 'E', 'forged aluminium 17x4.5 with bearings, cush hub', uns=('R', 1.0), legacy=True)
rule('Front_disc_carrier_*', 'RUN', 'kg', 0.25, 'E', 'disc carrier', uns=('F', 1.0), legacy=True)
rule('Front_disc_*', 'RUN', 'kg', 1.2, 'E', '320 mm floating disc (matches CAD volume)', uns=('F', 1.0), legacy=True)
rule('Front_caliper_reserve_*', 'RUN', 'kg', 0.85, 'E', 'radial 4-piston caliper', uns=('F', 1.0), legacy=True)
rule('Rear_disc_p1', 'RUN', 'kg', 1.17, 'C', '267x6 mm disc: CAD 267x5 weighs 0.97 kg, x6/5', uns=('R', 1.0), legacy=True)
rule('Rear_disc_carrier_p1', 'RUN', 'kg', 0.1, 'E', 'disc carrier', uns=('R', 1.0), legacy=True)
rule('Rear_caliper_reserve', 'RUN', 'kg', 0.6, 'E', '2-piston caliper (+ bracket)', uns=('R', 1.0), legacy=True)
rule('Rear_caliper_bracket', 'RUN', 'kg', 0.3, 'E', 'floating caliper bracket', uns=('R', 1.0), legacy=True)
rule('Fork_outer_tube_*', 'RUN', 'kg', 2.6, 'E', '48 mm USD outer tube with cartridge and oil', legacy=True)
rule('Fork_inner_tube_*', 'RUN', 'kg', 1.0, 'E', 'inner tube', uns=('F', 1.0), legacy=True)
rule('Fork_axle_clamp_*', 'RUN', 'kg', 0.8, 'E', 'axle foot (half the axle too)', uns=('F', 1.0), legacy=True)
rule('Fork_top_cap_*', 'RUN', 'kg', 0.0, 'E', 'cap/adjuster: included in the outer tube figure', legacy=True)
rule('Shock_body_STUDY', 'RUN', 'kg', 2.0, 'E', 'semi-active damper body (with valves)', uns=('R', 0.5), legacy=True)
rule('Shock_spring_STUDY', 'RUN', 'kg', 1.2, 'E', '97 N/mm steel spring', uns=('R', 0.5), legacy=True)
rule('Shock_rod_STUDY', 'RUN', 'kg', 0.3, 'E', 'damper shaft', uns=('R', 0.5), legacy=True)
rule('Shock_reservoir_STUDY', 'RUN', 'kg', 0.6, 'E', 'remote reservoir + hose', legacy=True)
rule('Shock_Upper_eye_STUDY', 'RUN', 'kg', 0.15, 'E', 'eye and bearing', legacy=True)
rule('Shock_Lower_eye_STUDY', 'RUN', 'kg', 0.15, 'E', 'eye and bearing', uns=('R', 1.0), legacy=True)
# ---- running gear: always ----
rule('Fork_reflector_*', 'BOD', 'kg', 0.01, 'E', 'side reflector', uns=('F', 1.0))
rule('Lower_triple_clamp', 'RUN', 'kg', 1.3, 'E', 'forged clamp with stem')
rule('Upper_triple_clamp', 'RUN', 'kg', 0.7, 'E', 'machined clamp')
rule('Steering_damper_envelope', 'RUN', 'kg', 1.1, 'E', 'semi-active rotary steering damper')
rule('Bar_*', 'RUN', 'kg', 0.25, 'E', 'bar section / riser')
rule('Hand_grip_reserve_*', 'RUN', 'kg', 0.20, 'E', 'grip and throttle tube (switch housing is Switch_cube)')
rule('Hand_lever_*', 'RUN', 'kg', 0.45, 'E', 'lever with radial master cylinder')
rule('Lever_perch_*', 'RUN', 'kg', 0.12, 'E', 'forged perch')
rule('Switch_cube_*', 'RUN', 'kg', 0.15, 'E', 'switch housing')
rule('Front_master_cylinder', 'RUN', 'kg', 0.0, 'E', 'counted inside the lever (Hand_lever_*); one master cylinder exists')
rule('Front_brake_reservoir', 'RUN', 'kg', 0.1, 'E', 'reservoir with fluid')
rule('Front_master_banjo|Front_caliper_banjo_*|Rear_caliper_banjo', 'RUN', 'kg', 0.03, 'E', 'banjo bolt')
rule('Front_brake_splitter', 'RUN', 'kg', 0.08, 'E', 'splitter')
rule('Front_brake_hose_*', 'RUN', 'kg', 0.18, 'E', 'braided hose with fluid')
rule('Rear_brake_hose', 'RUN', 'kg', 0.15, 'E', 'braided hose with fluid')
rule('Rear_brake_junction', 'RUN', 'kg', 0.05, 'E', 'junction')
rule('Peg_bracket_*', 'RUN', 'kg', 0.35, 'E', 'machined aluminium hanger')
rule('Peg_reference_*', 'RUN', 'kg', 0.25, 'E', 'rider peg')
rule('Peg_rubber_*', 'RUN', 'kg', 0.1, 'E', 'peg rubber')
rule('Harness_*', 'ALW', 'kg', 0.08, 'E', 'bar harness leg and connector (inside the LV harness total)')
# ---- body ----
for p, mat_, n in [('Upper_body_fairing_tank_STUDY', PLASTIC, '3 mm painted panel'), ('Lower_body_battery_covers_STUDY', PLASTIC, '3 mm painted panel'),
                   ('Motor_side_covers_STUDY', PLASTIC, '3 mm panel'), ('Tail_side_panels_STUDY', PLASTIC, '3 mm panel'),
                   ('Waist_ledge_plates', PLASTIC, '3 mm closing plates under the thighs'), ('Battery_side_panel_*', ALU, 'proud bolted aluminium panel'),
                   ('Belly_side_panel_*', ALU, 'proud bolted aluminium panel'), ('Belly_skid_plate_STUDY', ALU, 'skid plate (generator builds 6 mm)'),
                   ('Front_fender_STUDY', PLASTIC, 'fork-mounted fender'), ('Rear_hugger_STUDY', PLASTIC, 'swingarm-mounted hugger'),
                   ('Windscreen_STUDY', PC, 'polycarbonate screen'), ('Seam_trim_*', PLASTIC, 'trim'), ('Side_grille_louvres_*', PLASTIC, 'grille'),
                   ('Tail_undertray_STUDY', PLASTIC, '3 mm undertray / inner fender'), ('Radiator_pod_shroud_*', PLASTIC, '3 mm pod shroud'),
                   ('Radiator_pod_grille_*', PLASTIC, 'pod grille louvres')]:
    rule(p, 'BOD', 'vol', mat_, 'C', n, mat=dict([(PLASTIC, 'painted PP/ABS 3 mm'), (ALU, 'aluminium'), (PC, 'polycarbonate')])[mat_],
         proc='moulded or formed panel')
rule('Seat_two_level_STUDY', 'BOD', 'kg', 2.6, 'E', 'foam + base and cover')
rule('Panel_bolts_*', 'BOD', 'kg', 0.0, 'E', 'counted in the fastener allowance')
rule('Mirror_body_*', 'BOD', 'kg', 0.3, 'E', 'mirror head')
rule('Mirror_stalk_*', 'BOD', 'kg', 0.08, 'E', 'mirror stalk')
rule('Mirror_glass_*', 'BOD', 'kg', 0.05, 'E', 'mirror glass')
rule('Plate_hanger_arm', 'BOD', 'kg', 0.45, 'E', 'cast plate hanger with plate bracket')
rule('Rear_rack_STUDY', 'BOD', 'kg', 0.9, 'E', 'aluminium rack (25 kg luggage case)')
rule('Pivot_cover_cap_*', 'BOD', 'kg', 0.04, 'E', 'moulded cap')
rule('Seat_welt', 'BOD', 'kg', 0.05, 'E', 'seat piping')
rule('Licence_plate_US', 'BOD', 'kg', 0.2, 'S', 'US motorcycle plate')
rule('Rear_reflector_red', 'BOD', 'kg', 0.03, 'E', 'reflector')
rule('Side_reflector_red_*', 'BOD', 'kg', 0.01, 'E', 'reflector')

# Allowances (not in the CAD): name, tag, system, kg, source, mass_ref, (x,y,z), unsprung, includes/excludes, watch-regex, mode ('both'|'legacy'|'v1')
# watch: if a CAD solid whose name matches the regex exists, print an OVERLAP warning (the allowance may now double count).
ALLOW = [
 ('Pack internals: electrical (busbars, fuse collectors, films, NTCs, tap harness)', 'pack_int_elec', 'ENG', 7.26, 'C', 'electrical-bom.csv excl. BMS (03-mass-ledger.md)', (860, 0, 425), None, 'EXCLUDES BMS, cells, case', '', 'both'),
 ('Pack internals: thermal (ribbons, manifolds, fire-barrier foam, vent)', 'pack_int_therm', 'ENG', 7.25, 'C', 'thermal-study.md 6.19 (03-mass-ledger.md) + 1.06 coolant in ribbons and manifolds moved here from the loop (10-thermal.md section 5: ribbons 0.81 + manifolds 0.25)', (860, 0, 425), None, 'EXCLUDES cells, case; INCLUDES the 1.06 kg of coolant held in the ribbons and manifolds', '', 'both'),
 ('LV wiring harness', 'lv_harness', 'ALW', 2.08, 'C', 'electrical-bom.csv 2.4 kg minus modelled bar-harness legs 0.32', (760, 0, 700), None, 'EXCLUDES Harness_* bar legs (modelled)', r'^lv_harness|^harness_lv', 'both'),
 ('HV cables, connectors and conduit', 'hv_cables', 'ALW', 5.53, 'C', '07-electrical.md / elec-harness.csv: 8.4 m cable (50/35/4/2.5/6 mm2) 2.99 + 2.54 connectors, lugs, conduit; lengths +-30%; short-bus layout could save about 1 kg', (640, 0, 520), None, 'EXCLUDES charge inlet', r'hv_cable', 'both'),
 ('12 V lithium battery', 'battery_12v', 'ELC', 0.9, 'S', 'Shorai LFX14A4-BS12 (electrical-bom.csv)', (300, 0, 720), None, '', r'12v|lv_battery|shorai', 'both'),
 ('VCU, distribution box, keyless, HVIL bonding', 'vcu_dist', 'ELC', 2.10, 'C', 'electrical-bom.csv: VCU 0.40 + distribution 1.15 + keyless 0.25 + bonding 0.30', (1200, 0, 880), None, 'EXCLUDES horn (modelled)', r'vcu|keyless|distribution_box', 'both'),
 ('Coolant in loop (1.66 L glycol), hoses and clamps 0.59, sensors 0.10', 'coolant_fluid', 'THM', 2.35, 'E', '10-thermal.md section 5: coolant 2.72 minus 1.06 in pack ribbons/manifolds + hoses 0.59 + sensors 0.10; the shortlist 1.6 omits sensors and part of the glycol', (880, 0, 600), None, 'EXCLUDES pumps, cores, fans (modelled) and the pack-side coolant (in pack_int_therm)', r'coolant_(fluid|hose)', 'both'),
 ('Rear brake pedal and master cylinder', 'rear_pedal', 'RUN', 0.7, 'E', 'allowance', (520, 200, 430), None, '', r'brake_pedal|rear_master', 'both'),
 ('Nose subframe and headlamp brackets', 'nose_subframe', 'CHS', 1.15, 'E', 'allowance; dash bracket is Display_mount (modelled)', (1330, 0, 900), None, 'EXCLUDES Display_mount', r'nose_subframe|headlamp_bracket', 'both'),
 ('Body brackets and fixings', 'body_brackets', 'ALW', 2.0, 'E', 'allowance; no BOM count exists', (850, 0, 700), None, '', r'body_bracket', 'both'),
 ('Fasteners (titanium where visible)', 'fasteners', 'ALW', 3.0, 'E', 'allowance; covers all bolts', (750, 0, 600), None, '', r'fastener', 'both'),
 ('Front axle spacers', 'axle_front', 'RUN', 0.15, 'E', 'allowance; axle is in the fork feet', (1487, 0, 325), ('F', 1.0), '', r'front_axle', 'both'),
 ('Rear axle, spacers, adjusters', 'axle_rear', 'RUN', 1.0, 'E', 'allowance', (0, 0, 312), ('R', 1.0), '', r'rear_axle', 'both'),
 ('Swingarm pivot bolt and hardware', 'pivot_hardware', 'CHS', 0.6, 'E', 'allowance', (540, 0, 390), ('R', 0.5), '', r'pivot_bolt', 'both'),
 ('Steering bearings, stem nut', 'steer_bearings', 'RUN', 0.30, 'E', 'allowance; damper is modelled', (1190, 0, 860), None, 'EXCLUDES steering damper (modelled)', r'steering_bearing', 'both'),
 ('Paint, decals, rubber, misc', 'paint_misc', 'BOD', 1.0, 'E', 'allowance', (800, 0, 650), None, '', r'paint', 'both'),
 ('ABS module (Bosch 10 class), lines, fluid', 'abs_legacy', 'RUN', 1.6, 'E', 'legacy allowance (V1 uses the abs_module supplier slot, 1.1 kg)', (700, 0, 760), None, '', '', 'legacy'),
 ('EVCC (charge controller)', 'evcc_legacy', 'ELC', 0.2, 'S', 'electrical-bom.csv (V1 uses the evcc supplier slot, 0.3 kg)', (1200, 0, 880), None, '', '', 'legacy'),
 ('Gear-case oil (0.5 L)', 'gear_oil', 'DRV', 0.45, 'E', 'IPM two-stage drive only (V1 single-stage belt has no gear oil)', (560, 0, 430), None, '', '', 'legacy'),
 ('Passenger pegs and hangers', 'passenger_pegs', 'RUN', 1.0, 'E', 'two-up layout; V1 is solo (Gate A T7), so omitted in V1 mode', (150, 0, 520), None, '', '', 'legacy'),
]

# ---------------------------------------------------------------------------------------------------------------------
def rx(p): return re.compile(p, re.I)
def glob_re(pat): return [re.compile(fnmatch.translate(g), re.I) for g in pat.split('|')]
def specificity(pat, name):
    """higher = more specific: exact name beats any glob; among globs the longest literal text wins"""
    best = 0
    for g in pat.split('|'):
        if g.lower() == name.lower(): return 1000
        if re.fullmatch(fnmatch.translate(g), name, re.I): best = max(best, len(g.replace('*', '')))
    return best

def load_slots(pick):
    slots = []
    for r in csv.DictReader(open(DATA / 'supplier-masses.csv', encoding='utf-8')):
        r['kg'] = float(r['kg']); r['count'] = int(r['count']) if r['count'] else None
        r['cost_usd'] = float(r['cost_usd']) if r['cost_usd'] else None
        r['re'] = rx(r['pattern'])
        d = r['default'] == '1'
        if r['group'] in pick: d = (pick[r['group']] == r['slot'])
        r['fill'] = d
        r['x_mm'], r['y_mm'], r['z_mm'] = (float(r[k] or 0) for k in ('x_mm', 'y_mm', 'z_mm'))
        slots.append(r)
    return slots

def parse_uns(s):
    return (s[0], float(s[1:])) if s else None

def load_cad(path):
    import FreeCAD as A
    d = A.openDocument(str(path)); out = []
    for o in d.Objects:
        if o.TypeId != 'Part::Feature' or not o.InList or o.InList[0].Name == 'Keepouts': continue
        s = o.Shape; sol = s.Solids
        v = sum(abs(x.Volume) for x in sol)
        c = sum((x.CenterOfMass * abs(x.Volume) for x in sol), A.Vector()) * (1 / v) if v > 0 else s.BoundBox.Center
        out.append(dict(name=o.Name, group=o.InList[0].Name, vol=v, area=s.Area, x=c.x, y=c.y, z=c.z))
    return out

def load_solids_csv(path):
    return [dict(name=r['name'], group=r['group'], vol=float(r['vol_mm3']), area=float(r['area_mm2']), x=float(r['x_mm']), y=float(r['y_mm']), z=float(r['z_mm']))
            for r in csv.DictReader(open(path, encoding='utf-8'))]

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--cad', default=str(R / 'cad/Bavuso-V1.0-adventure.FCStd'), help='FreeCAD file (opened read-only, never saved)')
    ap.add_argument('--solids-csv', help='read solids from a CSV instead of FreeCAD (name,group,vol_mm3,area_mm2,x_mm,y_mm,z_mm)')
    ap.add_argument('--dump-solids', help='write the solids read from the CAD to this CSV and continue')
    ap.add_argument('--out-dir', help='write all outputs flat into this folder (default: canonical places: v1.0/mass-rollup.*, program/data/parts-ledger.csv ...)')
    ap.add_argument('--legacy', action='store_true', help='old-bike mode: legacy hardware rules, no supplier slots (reproduces the reconciled 319.64 kg)')
    ap.add_argument('--pick', action='append', default=[], metavar='GROUP=SLOT', help='choose the variant used to FILL a supplier slot group, e.g. inverter=inverter_cm200')
    ap.add_argument('--budgets', default=str(DATA / 'budgets.csv'))
    ap.add_argument('--soft', action='store_true', help='always exit 0')
    a = ap.parse_args()
    pick = dict(p.split('=', 1) for p in a.pick)
    out = Path(a.out_dir) if a.out_dir else None
    if out: out.mkdir(parents=True, exist_ok=True)
    P = lambda canon, name: (out / name) if out else canon
    slots = [] if a.legacy else load_slots(pick)
    rules = [r for r in RULES if a.legacy or not r['legacy']]
    tags = {}
    for r in rules:                               # scope_tag guard: two rules may not claim the same tag
        if r['tag'] in tags: sys.exit('DUPLICATE rule scope_tag %s: %s / %s' % (r['tag'], tags[r['tag']], r['pat']))
        tags[r['tag']] = r['pat']
    for s in slots:
        if s['slot'] in tags: sys.exit('DUPLICATE scope_tag (slot vs rule): ' + s['slot'])
    for r in rules: r['res'] = glob_re(r['pat'])

    solids = load_solids_csv(a.solids_csv) if a.solids_csv else load_cad(a.cad)
    if a.dump_solids:
        with open(a.dump_solids, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(['name', 'group', 'vol_mm3', 'area_mm2', 'x_mm', 'y_mm', 'z_mm'])
            for s in solids: w.writerow([s['name'], s['group'], round(s['vol'], 3), round(s['area'], 3), round(s['x'], 3), round(s['y'], 3), round(s['z'], 3)])

    # ---- bind every solid: supplier slot first (by name pattern), else most specific rule, else UNMATCHED ----
    rows, unmatched, ambiguous = [], [], []
    slot_hits = {s['slot']: [] for s in slots}
    for so in solids:
        hits = [s for s in slots if s['re'].search(so['name'])]
        if hits:
            if len({h['group'] for h in hits}) > 1:
                ambiguous.append((so['name'], [h['slot'] for h in hits]))
            slot_hits[hits[0]['slot']].append(so); continue
        cands = [(specificity(r['pat'], so['name']), r) for r in rules if any(g.fullmatch(so['name']) for g in r['res'])]
        if not cands:
            unmatched.append(so); continue
        cands.sort(key=lambda t: -t[0])
        if len(cands) > 1 and cands[0][0] == cands[1][0]: ambiguous.append((so['name'], [c[1]['pat'] for c in cands]))
        rows.append(dict(kind='rule', so=so, r=cands[0][1]))

    L = []                                         # ledger rows (dict per part)
    def add(**k):
        base = dict(name='', system='', make_buy='', status='', material='', process='', qty=1, mass_kg=0.0, mass_source='', mass_ref='',
                    cost_usd='', cost_source='', drawing_id='', cad_solid='', scope_tag='', includes_excludes='', notes='', x=0.0, y=0.0, z=0.0,
                    unsprung=None, method='', group='', key='')
        base.update(k); L.append(base); return base
    cell_cm = {}
    for rr in rows:
        so, r = rr['so'], rr['r']
        v, m = so['vol'], r['meth']
        if m == 'kg': kg = r['val']
        elif m == 'vol': kg = v / 1000 * r['val'] / 1000
        elif m == 'shell': kg = so['area'] / 100 * r['val'][1] / 10 * r['val'][0] / 1000
        elif m == 'pack': kg = v / (math.pi * 13 ** 2 * 120) * LEG_CELL_G / 1000
        note = r['note']
        if m == 'kg' and v > 0 and kg > 0:
            dens = kg * 1e6 / v                    # g/cm3 implied by the CAD solid
            if dens > 8.0 or dens < 0.2: note += ' [CAD stand-in: implied density %.2f g/cm3, mass cannot be checked from the model]' % dens
        add(name=so['name'], system=r['sys'], make_buy=r['mb'], status=r['status'], material=r['mat'], process=r['proc'], mass_kg=kg,
            mass_source=r['src'], mass_ref=note, cad_solid=so['name'], scope_tag=r['tag'], unsprung=r['uns'], method=m, group=so['group'],
            x=so['x'], y=so['y'], z=so['z'], key=r['tag'] + '|' + so['name'])
    # supplier slots
    filled, count_warn = [], []
    grp_hit = {}
    for s in slots: grp_hit[s['group']] = grp_hit.get(s['group'], False) or bool(slot_hits[s['slot']])
    for s in slots:
        hs = slot_hits[s['slot']]
        if s['mode'] == 'total':
            tv = sum(h['vol'] for h in hs)
            for h in hs:
                f = (h['vol'] / tv) if tv > 0 else 1 / len(hs)
                add(name=s['name'], system=s['system'], make_buy='buy', status=s['status'], material=s['material'], process=s['process'], mass_kg=s['kg'] * f,
                    mass_source=s['mass_source'], mass_ref=s['mass_ref'] + ' [slot total %.3f kg split by volume over %d solids]' % (s['kg'], len(hs)),
                    cost_usd=round(s['cost_usd'] * f, 2) if s['cost_usd'] else '', cost_source=s['cost_source'], cad_solid=h['name'], scope_tag=s['slot'],
                    includes_excludes=s['notes'], unsprung=parse_uns(s['unsprung']), method='slot', group=h['group'], x=h['x'], y=h['y'], z=h['z'],
                    key=s['slot'] + '|' + h['name'])
            if not grp_hit[s['group']] and s['fill']:
                filled.append(s)
        else:
            for h in hs:
                add(name=s['name'], system=s['system'], make_buy='buy', status=s['status'], material=s['material'], process=s['process'], mass_kg=s['kg'],
                    mass_source=s['mass_source'], mass_ref=s['mass_ref'], cost_usd=s['cost_usd'] if s['cost_usd'] is not None else '', cost_source=s['cost_source'],
                    cad_solid=h['name'], scope_tag=s['slot'], includes_excludes=s['notes'], unsprung=parse_uns(s['unsprung']), method='slot', group=h['group'],
                    x=h['x'], y=h['y'], z=h['z'], key=s['slot'] + '|' + h['name'])
            exp = s['count']
            if hs and exp and len(hs) != exp:
                count_warn.append('%s: %d CAD solid(s) matched, %d expected (%s)' % (s['slot'], len(hs), exp, ', '.join(h['name'] for h in hs)))
            if hs and exp and len(hs) < exp:                       # some modelled, some missing
                filled.append(dict(s, miss=exp - len(hs)))
            elif not grp_hit[s['group']] and s['fill']:            # not modelled at all
                filled.append(dict(s, miss=exp or 1))
    # slotfill rows: slot with no (or too few) CAD solids -> a ledger row without geometry
    for s in filled:
        miss = s.get('miss', 1)
        add(name=s['name'] + ' [NOT IN CAD: from supplier table]', system=s['system'], make_buy='buy', status=s['status'], material=s['material'], process=s['process'],
            qty=miss if s['mode'] == 'each' else 1, mass_kg=s['kg'], mass_source=s['mass_source'], mass_ref=s['mass_ref'],
            cost_usd=s['cost_usd'] if s['cost_usd'] is not None else '', cost_source=s['cost_source'], scope_tag=s['slot'] + '_fill',
            includes_excludes=s['notes'], unsprung=parse_uns(s['unsprung']), method='slotfill', group='Allowance', x=s['x_mm'], y=s['y_mm'], z=s['z_mm'], key=s['slot'] + '|fill')
    # allowances
    overlaps = []
    names = [so['name'] for so in solids]
    for nm, tag, sy, kg, src, ref, pos, uns, inc, watch, mode in ALLOW:
        if mode == 'legacy' and not a.legacy: continue
        if watch:
            hit = [n for n in names if re.search(watch, n, re.I)]
            if hit: overlaps.append('allowance "%s" may double count modelled solid(s) %s' % (nm, hit))
        add(name=nm, system=sy, make_buy='buy', status='concept', mass_kg=kg, mass_source=SRC[src], mass_ref=ref, scope_tag=tag, includes_excludes=inc,
            unsprung=uns, method='allow', group='Allowance', x=pos[0], y=pos[1], z=pos[2], key=tag)
    # legacy cells: mass was cell-volume based; V1 cells come from the slot
    # integrity checks
    dups = []
    seen = {}
    for l in L:
        if l['cad_solid']:
            if l['cad_solid'] in seen: dups.append('solid %s has two ledger rows (%s, %s)' % (l['cad_solid'], seen[l['cad_solid']], l['scope_tag']))
            seen[l['cad_solid']] = l['scope_tag']
    by_tag = {}
    for l in L:
        if not l['cad_solid']: by_tag.setdefault(l['scope_tag'], []).append(l['name'])
    for t, ns in by_tag.items():
        if len(ns) > 1: dups.append('scope_tag %s used by %d non-CAD rows: %s' % (t, len(ns), ns))
    for l in L:
        if l['method'] == 'allow' and not l['mass_source']: dups.append('allowance %s has no mass_source' % l['name'])
    missing = [r['tag'] + ' (%s)' % r['pat'] for r in rules if r['required'] and not any(l['scope_tag'] == r['tag'] and l['cad_solid'] for l in L)]
    # UNMATCHED rows: visible in the ledger, zero mass
    for so in unmatched:
        add(name=so['name'], system='UNMATCHED', status='UNMATCHED', mass_source='none', mass_ref='NO RULE OR SLOT MATCHES THIS CAD SOLID: its mass is NOT counted', cad_solid=so['name'],
            scope_tag='UNMATCHED', method='none', group=so['group'], x=so['x'], y=so['y'], z=so['z'], key='UNMATCHED|' + so['name'])
        L[-1]['mass_kg'] = 0.0; L[-1]['vol_mm3'] = so['vol']

    # ---- stable ids ----
    reg_path = P(DATA / 'parts-id-registry.csv', 'parts-id-registry.csv')
    src_reg = DATA / 'parts-id-registry.csv'
    reg = {}; nxt = {}
    for rp in {src_reg, reg_path}:
        if rp.exists():
            for r in csv.DictReader(open(rp, encoding='utf-8')):
                reg[r['key']] = r['id']
    for i in reg.values():
        sy, n = i.split('-')[1], int(i.split('-')[2]); nxt[sy] = max(nxt.get(sy, 0), n)
    for l in L:
        if l['system'] == 'UNMATCHED': l['id'] = ''; continue
        if l['key'] not in reg:
            nxt[l['system']] = nxt.get(l['system'], 0) + 1
            reg[l['key']] = 'BV-%s-%04d' % (l['system'], nxt[l['system']])
        l['id'] = reg[l['key']]
    with open(reg_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['key', 'id'])
        for k, v in sorted(reg.items(), key=lambda t: t[1]): w.writerow([k, v])

    # ---- totals, CoG, budgets ----
    for l in L: l['tot'] = l['mass_kg'] * l['qty']
    cnt = [l for l in L if l['system'] != 'UNMATCHED']
    M = sum(l['tot'] for l in cnt)
    X, Y, Z = (sum(l['tot'] * l[k] for l in cnt) / M for k in 'xyz')
    unF = sum(l['tot'] * l['unsprung'][1] for l in cnt if l['unsprung'] and l['unsprung'][0] == 'F')
    unR = sum(l['tot'] * l['unsprung'][1] for l in cnt if l['unsprung'] and l['unsprung'][0] == 'R')
    Iyy = sum(l['tot'] * ((l['x'] - X) ** 2 + (l['z'] - Z) ** 2) for l in cnt) / 1e6
    bys = {}
    for l in cnt: bys[l['system']] = bys.get(l['system'], 0) + l['tot']
    bsrc = {k: 0.0 for k in ('measured', 'supplier', 'calculated', 'estimate')}
    bstat = {}
    for l in cnt:
        bsrc[l['mass_source']] = bsrc.get(l['mass_source'], 0) + l['tot']; bstat[l['status']] = bstat.get(l['status'], 0) + l['tot']
    groups = {}
    for l in cnt:
        g = groups.setdefault(l['group'], [0, 0, 0]); g[0] += l['tot']; g[1] += l['tot'] * l['x']; g[2] += l['tot'] * l['z']

    budget = []; total_budget = 240.0; margin = 12.0
    for r in csv.DictReader(open(a.budgets, encoding='utf-8')):
        if r['budget_group'] == 'TOTAL': total_budget = float(r['budget_kg']); continue
        if r['budget_group'] == 'MARGIN': margin = float(r['budget_kg']); continue
        sy = r['systems'].split(';')
        raw = sum(bys.get(s, 0) for s in sy)
        adj = sum(l['tot'] * (1 + GROWTH.get(l['status'], 0)) for l in cnt if l['system'] in sy)
        est = sum(l['tot'] for l in cnt if l['system'] in sy and l['mass_source'] == 'estimate')
        b = float(r['budget_kg']); head = b - raw
        flag = 'OVER' if raw > b else ('TIGHT' if head < 0.05 * b else 'ok')
        budget.append(dict(group=r['budget_group'], systems=r['systems'], budget_kg=b, raw_kg=round(raw, 2), headroom_kg=round(head, 2), headroom_pct=round(100 * head / b, 1),
                           growth_adjusted_kg=round(adj, 2), estimate_share_pct=round(100 * est / raw, 0) if raw else 0, flag=flag))
    known = {s for r in budget for s in r['systems'].split(';')}
    stray = {s: round(v, 2) for s, v in bys.items() if s not in known}
    sys_over = [b['group'] for b in budget if b['flag'] == 'OVER']
    total_over = M > total_budget
    budget_pass = (not sys_over) and (not total_over) and not stray
    ledger_clean = not (unmatched or dups or missing)
    out_j = dict(prepared=__import__("time").strftime("%Y-%m-%d") + ' (Claude Sonnet 5.5, mass-rollup.py ledger version)',
                 model=(a.solids_csv or a.cad).replace('\\', '/').split('/cad/')[-1] if not a.solids_csv else a.solids_csv,
                 mode='legacy (old-bike hardware rules)' if a.legacy else 'V1 (supplier slots)',
                 total_kg=round(M, 1), total_lb=round(M * 2.20462),
                 cog_mm=dict(x_from_rear_axle=round(X), y=round(Y, 1), height=round(Z)),
                 front_rear_split_pct=[round(100 * X / WB, 1), round(100 * (1 - X / WB), 1)],
                 unsprung_kg=dict(front=round(unF, 1), rear=round(unR, 1)), pitch_inertia_point_mass_kgm2=round(Iyy, 1),
                 cells_kg=round(sum(l['tot'] for l in cnt if l['scope_tag'] in ('cells_p60b', 'cells_legacy') or l['scope_tag'].startswith('cells')), 1),
                 pack_kg=round(bys.get('ENG', 0), 1),
                 by_group={g: dict(kg=round(v[0], 1), x=round(v[1] / v[0]) if v[0] else 0, z=round(v[2] / v[0]) if v[0] else 0) for g, v in sorted(groups.items(), key=lambda t: -t[1][0])},
                 by_source={k: round(v, 1) for k, v in bsrc.items()}, by_status={k: round(v, 1) for k, v in bstat.items()},
                 by_system={k: round(v, 2) for k, v in sorted(bys.items(), key=lambda t: -t[1])},
                 optimiser_reference_kg=OPT_REF_KG,
                 budget=dict(target_total_kg=total_budget, margin_kg=margin, design_cap_kg=total_budget - margin, groups=budget, system_over=sys_over,
                             total_over=total_over, unbudgeted_systems=stray, margin_kept=M <= total_budget - margin),
                 budget_pass=budget_pass, ledger_clean=ledger_clean, overall_pass=budget_pass and ledger_clean,
                 integrity=dict(unmatched_solids=[dict(name=s['name'], group=s['group'], vol_cm3=round(s['vol'] / 1000, 1)) for s in unmatched],
                                unmatched_count=len(unmatched), duplicates=dups, missing_required=missing, ambiguous=[dict(solid=n, matches=m) for n, m in ambiguous],
                                slot_count_mismatch=count_warn, slots_filled_without_cad=[f['slot'] for f in filled], allowance_overlaps=overlaps))
    # ---- outputs ----
    cols = ['id', 'name', 'system', 'make_buy', 'status', 'material', 'process', 'mass_kg', 'mass_source', 'cost_usd', 'cost_source', 'drawing_id', 'cad_solid',
            'qty', 'scope_tag', 'includes_excludes', 'mass_ref', 'method', 'unsprung', 'x_mm', 'y_mm', 'z_mm', 'group']
    with open(P(DATA / 'parts-ledger.csv', 'parts-ledger.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(cols)
        for l in sorted(L, key=lambda l: (l['system'] == 'UNMATCHED', l['system'], -l['tot'])):
            w.writerow([l['id'], l['name'], l['system'], l['make_buy'], l['status'], l['material'], l['process'], round(l['mass_kg'], 4), l['mass_source'], l['cost_usd'],
                        l['cost_source'], l['drawing_id'], l['cad_solid'], l['qty'], l['scope_tag'], l['includes_excludes'], l['mass_ref'], l['method'],
                        f"{l['unsprung'][0]}{l['unsprung'][1]}" if l['unsprung'] else '', round(l['x']), round(l['y']), round(l['z']), l['group']])
    # compatible mass-rollup.csv (same columns the existing studies read)
    with open(P(R / 'mass-rollup.csv', 'mass-rollup.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['item', 'group', 'kg', 'x_mm', 'y_mm', 'height_mm', 'unsprung', 'source', 'method', 'note'])
        for l in sorted(cnt, key=lambda l: -l['tot']):
            w.writerow([l['cad_solid'] or l['name'], l['group'], round(l['tot'], 3), round(l['x']), round(l['y']), round(l['z']),
                        f"{l['unsprung'][0]}{l['unsprung'][1]}" if l['unsprung'] else '', dict(supplier='supplier', calculated='CAD', estimate='estimate', measured='measured')[l['mass_source']],
                        l['method'], l['mass_ref']])
    with open(P(DATA / 'mass-budget-report.csv', 'mass-budget-report.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['budget_group', 'systems', 'budget_kg', 'raw_kg', 'headroom_kg', 'headroom_pct', 'growth_adjusted_kg', 'estimate_share_pct', 'flag'])
        for b in budget: w.writerow([b['group'], b['systems'], b['budget_kg'], b['raw_kg'], b['headroom_kg'], b['headroom_pct'], b['growth_adjusted_kg'], b['estimate_share_pct'], b['flag']])
        w.writerow(['TOTAL', '', total_budget, round(M, 2), round(total_budget - M, 2), round(100 * (total_budget - M) / total_budget, 1), '', '', 'OVER' if total_over else 'ok'])
    P(R / 'mass-rollup.json', 'mass-rollup.json').write_text(json.dumps(out_j, indent=1))

    # ---- console report ----
    pr = print
    pr('MASS LEDGER  mode=%s  solids=%d  ledger rows=%d' % (out_j['mode'], len(solids), len(L)))
    pr('%-26s %8s %9s %9s %7s %9s  %s' % ('system (Gate A)', 'budget', 'mass', 'headroom', '%', 'w/growth', 'flag'))
    for b in budget:
        pr('%-26s %8.1f %9.2f %9.2f %6.1f%% %9.2f  %s%s' % (b['group'], b['budget_kg'], b['raw_kg'], b['headroom_kg'], b['headroom_pct'], b['growth_adjusted_kg'], b['flag'],
                                                         '  (%d%% estimate)' % b['estimate_share_pct']))
    pr('%-26s %8.1f %9.2f %9.2f %6.1f%%            %s   (%.1f lb; design cap %.0f kg keeps the %.0f kg margin: %s)' % (
        'TOTAL (T1)', total_budget, M, total_budget - M, 100 * (total_budget - M) / total_budget, 'OVER' if total_over else 'ok', M * 2.20462, total_budget - margin, margin,
        'kept' if out_j['budget']['margin_kept'] else 'NOT kept'))
    if stray: pr('!! UNBUDGETED SYSTEMS (mass has no budget row):', stray)
    pr('by source: ' + ', '.join('%s %.1f' % kv for kv in bsrc.items()) + ' | by status: ' + ', '.join('%s %.1f' % kv for kv in bstat.items()))
    pr('CoG x=%d mm from rear axle, height %d mm; front/rear %s%%; unsprung F %.1f R %.1f kg' % (X, Z, out_j['front_rear_split_pct'], unF, unR))
    pr('BUDGET_PASS = %s   LEDGER_CLEAN = %s' % (budget_pass, ledger_clean))
    if sys_over: pr('!! OVER BUDGET:', ', '.join(sys_over))
    if unmatched:
        pr('!! UNMATCHED CAD SOLIDS (%d) - no rule or supplier slot matches; their mass is NOT in the total:' % len(unmatched))
        for s in unmatched: pr('     %-42s group %-12s %9.1f cm3' % (s['name'], s['group'], s['vol'] / 1000))
    if missing: pr('!! REQUIRED PART MISSING FROM CAD:', missing)
    for d in dups: pr('!! DUPLICATE / DOUBLE COUNT:', d)
    for n, m in ambiguous: pr('!! AMBIGUOUS MATCH (check which applies):', n, m)
    for c in count_warn: pr('!! SLOT COUNT:', c)
    for o in overlaps: pr('!! OVERLAP:', o)
    if filled: pr('!  Supplier slots with no CAD solid (mass carried from the supplier table):', ', '.join('%s%s' % (f['slot'], ' x%d' % f['miss'] if f.get('miss', 1) > 1 else '') for f in filled))
    pr('wrote:', P(DATA / 'parts-ledger.csv', 'parts-ledger.csv'), '|', P(R / 'mass-rollup.csv', 'mass-rollup.csv'), '|', P(R / 'mass-rollup.json', 'mass-rollup.json'), '|',
       P(DATA / 'mass-budget-report.csv', 'mass-budget-report.csv'))
    code = 2 if not ledger_clean else (1 if not budget_pass else 0)
    sys.exit(0 if a.soft else code)

main()
