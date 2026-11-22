#!/usr/bin/env python
"""Bavuso V1 rev E indented BOM, built from the parts ledger (read only).

Run (any python 3, no FreeCAD needed):
    ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/bom-v1.py
from the v1.0 folder.  Output: program/data/bom-v1-indented.csv and
program/data/bom-v1-reconcile.json  (the doc 18-bom-and-drawings.md quotes these).

Also the single source for which CAD solids sit in which drawing (SHEETS); drawings-v1.py
imports it.  Nothing here writes the ledger or the registry.
"""
import csv, json, re, os, sys, collections, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LEDGER = os.path.join(ROOT, 'program', 'data', 'parts-ledger.csv')
OUT_CSV = os.path.join(ROOT, 'program', 'data', 'bom-v1-indented.csv')
OUT_JSON = os.path.join(ROOT, 'program', 'data', 'bom-v1-reconcile.json')
ROLLUP = os.path.join(ROOT, 'mass-rollup.json')

# ------------------------------------------------------------------ structure
VEHICLE = ('BV-VEH-0001', 'Bavuso V1.0 Adventure motorcycle, rev E')

# system key -> (part number, name, ledger system codes)
SYSTEMS = collections.OrderedDict([
    ('pack',   ('BV-SYS-0001', 'Pack (cells, case, internals)', ('ENG',))),
    ('chassis', ('BV-SYS-0002', 'Chassis (frame, pivot yoke, swingarm)', ('CHS',))),
    ('running', ('BV-SYS-0003', 'Running gear (suspension, wheels, brakes, controls)', ('RUN',))),
    ('drive',  ('BV-SYS-0004', 'Drive (motor, inverter, belt, pulleys)', ('DRV',))),
    ('elec',   ('BV-SYS-0005', 'Electronics (charging, HV, BMS, LV, lamps, display)', ('ELC',))),
    ('body',   ('BV-SYS-0006', 'Body and protection', ('BOD', 'PRO'))),
    ('cooling', ('BV-SYS-0007', 'Cooling', ('THM',))),
    ('wiring', ('BV-SYS-0008', 'Wiring, fasteners, fluids', ('ALW',))),
])
CODE2SYS = {c: k for k, v in SYSTEMS.items() for c in v[2]}

# assembly key -> (part number, name, system key, drawing number or '')
ASM = collections.OrderedDict([
    ('cells',   ('BV-ASM-0101', 'Cell lanes, 4 x 25s11p modules (1,100 cells)', 'pack', '')),
    ('case',    ('BV-ASM-0102', 'Pack case assembly (tub, lid, pads)', 'pack', '')),
    ('packint', ('BV-ASM-0103', 'Pack internals (busbars, ribbons, manifolds: allowances)', 'pack', '')),
    ('frame',   ('BV-ASM-0201', 'Welded main frame with cast nodes', 'chassis', 'BV-ASM-0201')),
    ('yoke',    ('BV-ASM-0202', 'Pivot yoke (legs, cross-member, nodes, blocks, spindles)', 'chassis', 'BV-ASM-0202')),
    ('swingarm', ('BV-ASM-0203', 'Single-sided swingarm (cast A356) with tower and brace', 'chassis', 'BV-ASM-0203')),
    ('fork',    ('BV-ASM-0301', 'Front fork, triple clamps, steering bearings', 'running', '')),
    ('shock',   ('BV-ASM-0302', 'Rear shock (Ohlins-class, direct mount)', 'running', '')),
    ('wheels',  ('BV-ASM-0303', 'Wheels, tyres and axles', 'running', '')),
    ('brakes',  ('BV-ASM-0304', 'Brakes (discs, calipers, ABS, hoses)', 'running', '')),
    ('controls', ('BV-ASM-0305', 'Controls and cockpit (bars, levers, grips, switches)', 'running', '')),
    ('pegs',    ('BV-ASM-0306', 'Footrests and side stand', 'running', '')),
    ('damper',  ('BV-ASM-0307', 'Steering damper (semi-active)', 'running', '')),
    ('motor',   ('BV-ASM-0401', 'Motor and inverter', 'drive', '')),
    ('belt',    ('BV-ASM-0402', 'Belt and pulleys (8M carbon belt, 35T / 126T)', 'drive', '')),
    ('carrier', ('BV-ASM-0403', 'Motor-side pulley carrier ("motor mount")', 'drive', '')),
    ('charge',  ('BV-ASM-0501', 'Charging (NACS inlet, on-board charger, EVCC)', 'elec', '')),
    ('hv',      ('BV-ASM-0502', 'HV distribution (cabinet, GX14 contactors, VCU)', 'elec', '')),
    ('bms',     ('BV-ASM-0503', 'Battery management system', 'elec', '')),
    ('lv',      ('BV-ASM-0504', 'LV power (DC-DC, 12 V battery)', 'elec', '')),
    ('lamps',   ('BV-ASM-0505', 'Lighting and signalling', 'elec', '')),
    ('display', ('BV-ASM-0506', 'Display and horn', 'elec', '')),
    ('upper',   ('BV-ASM-0601', 'Upper body, tank cover and screen', 'body', '')),
    ('lower',   ('BV-ASM-0602', 'Lower body, skid and pivot caps', 'body', '')),
    ('tail',    ('BV-ASM-0603', 'Seat, tail and plate bracket', 'body', '')),
    ('pods',    ('BV-ASM-0604', 'Radiator pod shrouds and grilles', 'body', '')),
    ('mirrors', ('BV-ASM-0605', 'Mirrors', 'body', '')),
    ('fender',  ('BV-ASM-0606', 'Front fender and reflectors', 'body', '')),
    ('bodyalw', ('BV-ASM-0607', 'Body allowances (paint, decals)', 'body', '')),
    ('protect', ('BV-ASM-0608', 'Crash protection (handguards, sliders, mounts)', 'body', '')),
    ('radiators', ('BV-ASM-0701', 'Radiator cores and fans', 'cooling', '')),
    ('coolant', ('BV-ASM-0702', 'Coolant circuit (pump, thermostat, PTC, fluid)', 'cooling', '')),
    ('harness', ('BV-ASM-0801', 'HV cables and LV harness', 'wiring', '')),
    ('fasten',  ('BV-ASM-0802', 'Fasteners and body brackets', 'wiring', '')),
])
# any ledger row the rules below do not recognise lands here, so the totals still reconcile
FALLBACK = {k: ('BV-ASM-09%02d' % i, 'Other %s parts (new ledger rows, not yet assigned to an assembly)' % v[1].split(' (')[0], k, '')
            for i, (k, v) in enumerate(SYSTEMS.items(), 1)}

# ordered rules: (ledger system code, regex on cad_solid-or-name, assembly key)
RULES = [
    ('ENG', r'^Cell_lane', 'cells'),
    ('ENG', r'^Pack_case', 'case'),
    ('ENG', r'^Pack internals', 'packint'),
    ('CHS', r'^(Head_tube|Upper_rail_[012]_|Upper_post|Lower_downlink|Lower_pack_rear_link|Tail_rail|Tail_brace|Head_gusset|'
            r'Shock_top_bracket|Tail_shock_cross_tube|Shock_bridge_diagonal|Upper_rail_node_rail|Nose subframe|Chassis unmodelled)', 'frame'),
    ('CHS', r'^(Upper_rail_yoke|Upper_rail_node_yoke|Upper_rail_pivot_block|Independent_hollow_pivot_stub|Pivot_6008)', 'yoke'),
    ('CHS', r'^(Swingarm)', 'swingarm'),
    ('RUN', r'^(Fork_|43 mm USD|Lower_triple|Upper_triple|Steering bearings)', 'fork'),
    ('RUN', r'^(Shock_|Ohlins)', 'shock'),
    ('RUN', r'^(Rear_wheel|Front_wheel|Rear_nominal|Front_nominal|.*tyre|.*wheel|Rear axle|Front axle)', 'wheels'),
    ('RUN', r'^(Front_disc|Rear_disc|Front_caliper|Rear_caliper|Front[ _]brake|Rear[ _]brake|Front_master|Bosch ABS|.*disc|.*caliper)', 'brakes'),
    ('RUN', r'^(Bar_|Hand_|Lever_|Switch_cube)', 'controls'),
    ('RUN', r'^(Peg_|Side_stand)', 'pegs'),
    ('RUN', r'^Steering_damper', 'damper'),
    ('DRV', r'^(EMRAX|Cascadia)', 'motor'),
    ('DRV', r'^(Drive_belt|Front_pulley|Rear_pulley)', 'belt'),
    ('DRV', r'^Motor_pulley_bearing_carrier', 'carrier'),
    ('ELC', r'^(OBC|BROGEN|Volex|NACS|ADVANTICS)', 'charge'),
    ('ELC', r'^(HV_cabinet|GX14|single HV box|VCU)', 'hv'),
    ('ELC', r'^(Orion|BMS)', 'bms'),
    ('ELC', r'^(DCDC|0\.8 kW|12 V)', 'lv'),
    ('ELC', r'^(Headlamp|Taillamp|Front_indicator|Rear_indicator|Plate_lamp)', 'lamps'),
    ('ELC', r'^(Display|Horn)', 'display'),
    ('BOD', r'^(Upper_body|Windscreen|Waist_ledge|Seam_trim_tank)', 'upper'),
    ('BOD', r'^(Lower_body|Belly_skid|Pivot_cover_cap)', 'lower'),
    ('BOD', r'^(Seat|Tail_|Rear_hugger|Rear_rack|Plate_hanger|Licence_plate|Rear_reflector|Side_reflector|Seam_trim_tail)', 'tail'),
    ('BOD', r'^Radiator_pod', 'pods'),
    ('BOD', r'^Mirror', 'mirrors'),
    ('BOD', r'^(Front_fender|Fork_reflector)', 'fender'),
    ('BOD', r'^Paint', 'bodyalw'),
    ('PRO', r'.*', 'protect'),
    ('THM', r'^Radiator_(core|fan)', 'radiators'),
    ('THM', r'^(Coolant|Radiator)', 'coolant'),
    ('ALW', r'^(HV cables|LV wiring|Harness_)', 'harness'),
    ('ALW', r'^(Fasteners|Body brackets)', 'fasten'),
]

# ---- which CAD solids go in each drawing (drawings-v1.py reads this) ----
SHEETS = collections.OrderedDict([
    ('BV-ASM-0201', dict(title='Welded main frame with cast nodes', asm='frame')),
    ('BV-ASM-0202', dict(title='Pivot yoke', asm='yoke')),
    ('BV-ASM-0203', dict(title='Single-sided swingarm (cast A356)', asm='swingarm')),
    ('BV-ENG-0001', dict(title='Pack case tub (3 mm walls, 5 mm front wall)', solids=['Pack_case_structural_4mm_STUDY'])),
    ('BV-ENG-0101', dict(title='Pack lid', derived=True)),
    ('BV-BOD-0004', dict(title='Lower body panel', solids=['Lower_body_battery_covers_STUDY'])),
    ('BV-DRV-0006', dict(title='Rear belt pulley and hub', solids=['Rear_pulley_PITCH_STUDY'])),
    ('BV-DRV-0007', dict(title='Motor-side pulley carrier (motor mount)', solids=['Motor_pulley_bearing_carrier'])),
    ('BV-ENG-0102', dict(title='Battery module cell holder (one module)', derived=True)),
])

# provisional IDs for drawing-derived parts (not in the ledger registry: see doc section 3)
DERIVED = {
    'BV-ENG-0101': dict(name='Pack lid (roof slab of the case solid, Z625.1 to 628.1)', material='aluminium 5xxx/6xxx sheet 3 mm',
                        process='laser-cut sheet, bolted and sealed to the tub flange (flange not modelled)',
                        parent='BV-ENG-0001', density=2.70e-6),
    'BV-ENG-0102': dict(name='Cell holder pair for one 25s11p module (concept, not in ledger)', material='PA66-GF30 (est. 1.35 g/cm3)',
                        process='injection moulded, two plates per module', density=1.35e-6),
}


# notes added to specific ledger rows (things the BOM build found; they do not change any mass)
ROW_NOTES = {
    'BV-DRV-0003': 'ledger name says 14 mm belt; CAD and 06-drive-performance use Gates 8MGT-1760-62 (8 mm pitch, 62 mm wide)',
    'BV-DRV-0004': 'ledger name says 21T; CAD and 06-drive-performance use 35T (8 mm pitch)',
    'BV-DRV-0006': 'ledger name says 80T; CAD/drive report use 126T (8 mm pitch, Ø319.3 root). CAD solid is a filled disc (9.1 kg in Al); ledger 2.1 kg is an estimate for a webbed pulley',
    'BV-DRV-0007': 'CAD solid volume is 0.79 kg in aluminium (2.3 kg in steel); ledger carries 0.4 kg estimate',
    'BV-CHS-0021': 'CAD solid is a filled envelope; ledger mass is the 4.0 mm shell rule, not volume',
    'BV-BOD-0004': 'rev E report says 2 mm panel; ledger process text still says 3 mm (mass follows CAD volume at 1.05 g/cm3)',
    'BV-ENG-0006': 'no cell-holder line exists in the ledger; see BV-ENG-0102',
}


def pretty(solid):
    s = solid.replace('_STUDY', '').replace('_', ' ').strip()
    s = re.sub(r' m1$', ' (Y-)', s)
    s = re.sub(r' p1$', ' (Y+)', s)
    s = re.sub(r' 1$', ' (Y+)', s)
    s = re.sub(r' 2$', ' (2)', s)
    return s


def load_ledger():
    rows = list(csv.DictReader(open(LEDGER, newline='', encoding='utf-8')))
    return rows


def assign(row):
    code = row['system']
    key = (row['cad_solid'] or row['name']).strip()
    # the damper row has no system or id in the ledger; it is a CAD solid the roll-up could not match
    if code == 'UNMATCHED' or row['cad_solid'].startswith('Steering_damper'):
        return 'running', 'damper'
    for c, rx, a in RULES:
        if c == code and re.search(rx, key):
            return ASM[a][2], a
    sk = CODE2SYS.get(code)
    return sk, None


def fnum(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def build(lid_mass_kg=None, holder_est_kg=None):
    """Return (bom rows, reconcile dict). lid mass comes from drawings-v1.py output if present."""
    rows = load_ledger()
    if lid_mass_kg is None:
        side = os.path.join(ROOT, 'program', 'data', 'drawings-derived.json')
        if os.path.exists(side):
            j = json.load(open(side))
            lid_mass_kg = j.get('BV-ENG-0101', {}).get('mass_kg')
            holder_est_kg = j.get('BV-ENG-0102', {}).get('mass_kg')
    ledger_total = sum(fnum(r['mass_kg']) for r in rows)
    by_asm = collections.defaultdict(list)
    unassigned = []
    for r in rows:
        sk, ak = assign(r)
        if ak is None:
            unassigned.append(r)
            ak = 'FALLBACK:' + sk
        by_asm[ak].append(r)

    out = []

    def row(level, pn, desc, qty, mb, mat, each, ext, sup, dwg, note, src='', sysk=''):
        out.append(collections.OrderedDict(level=level, part_number=pn, description=desc, qty=qty, make_buy=mb,
                                           material_process=mat, mass_each_kg=('%.4f' % each) if each is not None else '',
                                           mass_ext_kg=('%.4f' % ext) if ext is not None else '', mass_source=src,
                                           supplier_part_ref=sup, drawing_number=dwg, note=note))

    def part_row(r, mass_override=None, dwg_override=None, note_extra=''):
        qty = int(fnum(r['qty'], 1)) or 1
        mass = fnum(r['mass_kg']) if mass_override is None else mass_override
        solid = r['cad_solid']
        name = r['name']
        desc = pretty(solid) if (solid and name.strip() == solid.strip()) else name
        if solid and name.strip() != solid.strip():
            desc = name + ' [' + pretty(solid) + ']'
        mat = ' / '.join(x for x in (r['material'].strip(), r['process'].strip()) if x)
        mb = r['make_buy']
        pn = r['id'] or 'BV-RUN-TBD'
        note = []
        if not r['id']:
            note.append('no ID in ledger yet; solid not matched by the roll-up (mass 0.0 in total; about 0.5 kg missing)')
        if note_extra:
            note.append(note_extra)
        if r['id'] in ROW_NOTES:
            note.append(ROW_NOTES[r['id']])
        dwg = dwg_override if dwg_override is not None else ''
        sup = ''
        if mb == 'buy':
            sup = (name if not (solid and name.strip() == solid.strip()) else '') or 'catalogue/standard part'
            sup = sup[:70]
        return dict(pn=pn, desc=desc, qty=qty, mb=mb or '', mat=mat, each=mass / qty, ext=mass, sup=sup, dwg=dwg,
                    note='; '.join(note), src=r['mass_source'])

    # which drawing covers which assembly's made parts
    asm_dwg = {k: v[3] for k, v in ASM.items()}
    drawn_part = {'Pack_case_structural_4mm_STUDY': 'BV-ENG-0001', 'Lower_body_battery_covers_STUDY': 'BV-BOD-0004',
                  'Rear_pulley_PITCH_STUDY': 'BV-DRV-0006', 'Motor_pulley_bearing_carrier': 'BV-DRV-0007'}

    sys_tot = collections.OrderedDict()
    row(0, VEHICLE[0], VEHICLE[1], 1, 'assembly', '', None, ledger_total, '', '', 'level 0 total = ledger total', '')
    veh_idx = len(out) - 1
    for sk, (spn, sname, codes) in SYSTEMS.items():
        keys = [a for a, v in ASM.items() if v[2] == sk] + (['FALLBACK:' + sk] if ('FALLBACK:' + sk) in by_asm else [])
        s_rows = []
        s_tot = 0.0
        row(1, spn, sname, 1, 'assembly', '', None, None, '', '', '', '')
        s_idx = len(out) - 1
        for ak in keys:
            plist = by_asm.get(ak, [])
            if not plist and not ak.startswith('FALLBACK'):
                continue
            if ak.startswith('FALLBACK'):
                apn, aname = FALLBACK[sk][0], FALLBACK[sk][1]
                adwg = ''
            else:
                apn, aname, _, adwg = ASM[ak]
            row(2, apn, aname, 1, 'assembly', '', None, None, '', adwg, '', '')
            a_idx = len(out) - 1
            a_tot = 0.0
            plist = sorted(plist, key=lambda r: (-fnum(r['mass_kg']), r['id']))
            for r in plist:
                solid = r['cad_solid']
                dwg = ''
                if r['make_buy'] == 'make':
                    dwg = drawn_part.get(solid, asm_dwg.get(ak, ''))
                    if solid.startswith('Pack_case_pad'):
                        dwg = 'BV-ENG-0001'
                p = part_row(r, dwg_override=dwg)
                # pack case: split lid out of the ledger mass (lid is a drawing-derived part)
                if solid == 'Pack_case_structural_4mm_STUDY' and lid_mass_kg:
                    p['ext'] = p['each'] = fnum(r['mass_kg']) - lid_mass_kg
                    p['desc'] = 'Pack case tub (3 mm walls, 5 mm front wall, floor ribs) [Pack_case_structural_4mm_STUDY]'
                    p['note'] = ('ledger mass %.4f minus lid %.4f (lid split out of the same solid, net zero)' % (fnum(r['mass_kg']), lid_mass_kg))
                row(3, p['pn'], p['desc'], p['qty'], p['mb'], p['mat'], p['each'], p['ext'], p['sup'], p['dwg'], p['note'], p['src'])
                a_tot += p['ext']
                if solid == 'Pack_case_structural_4mm_STUDY' and lid_mass_kg:
                    d = DERIVED['BV-ENG-0101']
                    row(3, 'BV-ENG-0101', d['name'], 1, 'make', d['material'] + ' / ' + d['process'], lid_mass_kg, lid_mass_kg, '',
                        'BV-ENG-0101', 'PROVISIONAL ID, not in the registry; split from BV-ENG-0001 (net zero)', 'calculated')
                    a_tot += lid_mass_kg
                if solid == 'Cell_lane_4' and holder_est_kg:
                    d = DERIVED['BV-ENG-0102']
                    row(3, 'BV-ENG-0102', d['name'], 4, 'make', d['material'] + ' / ' + d['process'], 0.0, 0.0, '', 'BV-ENG-0102',
                        'PROVISIONAL ID; NOT counted: no ledger line (est. %.2f kg per module, %.1f kg for 4, concept drawing mass); '
                        'see doc 18 section 3' % (holder_est_kg, 4 * holder_est_kg), 'estimate')
            out[a_idx]['mass_ext_kg'] = '%.4f' % a_tot
            out[a_idx]['mass_each_kg'] = '%.4f' % a_tot
            s_tot += a_tot
        out[s_idx]['mass_ext_kg'] = '%.4f' % s_tot
        out[s_idx]['mass_each_kg'] = '%.4f' % s_tot
        sys_tot[sk] = s_tot
    out[veh_idx]['mass_each_kg'] = '%.4f' % sum(sys_tot.values())
    out[veh_idx]['mass_ext_kg'] = '%.4f' % sum(sys_tot.values())

    leaf = sum(fnum(r['mass_ext_kg']) for r in out if r['level'] == 3)
    rec = dict(
        prepared=str(datetime.date.today()), ledger_file='program/data/parts-ledger.csv', ledger_rows=len(rows),
        ledger_total_kg=round(ledger_total, 4), bom_leaf_sum_kg=round(leaf, 4), bom_system_sum_kg=round(sum(sys_tot.values()), 4),
        diff_kg=round(leaf - ledger_total, 6), within_0p1=abs(leaf - ledger_total) <= 0.1,
        by_system_kg={k: round(v, 3) for k, v in sys_tot.items()},
        unassigned_rows=[(r['id'], r['name']) for r in unassigned],
        part_lines=sum(1 for r in out if r['level'] == 3), assemblies=sum(1 for r in out if r['level'] == 2),
        lid_mass_kg=lid_mass_kg, holder_est_kg=holder_est_kg,
    )
    # cross-check against the roll-up file the ledger agent writes
    if os.path.exists(ROLLUP):
        j = json.load(open(ROLLUP))
        rec['rollup_total_kg'] = j.get('total_kg')
        rec['rollup_by_system_kg'] = j.get('by_system')
        rec['diff_to_rollup_kg'] = round(leaf - fnum(j.get('total_kg')), 3)
    return out, rec


def main():
    out, rec = build()
    cols = list(out[0].keys())
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    json.dump(rec, open(OUT_JSON, 'w'), indent=1)
    print(json.dumps(rec, indent=1))
    if not rec['within_0p1']:
        print('RECONCILIATION FAILED', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
