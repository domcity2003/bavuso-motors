"""Bavuso V1.0 adventure: electrical BOM with masses and costs, compared with mass-rollup allowances.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).
Costs are planning estimates (USD): 'proto' = one-off/catalogue price, 'vol' = 10k/yr target. Sources in column.
Run from v1.0 after elec-pack.py, elec-hv.py and elec-lv.py.
"""
import csv, json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / 'detailed-design' / 'electrical'
pk = json.load(open(OUT / 'pack-electrical.json'))
hv = json.load(open(OUT / 'hv-system.json'))
lv = json.load(open(OUT / 'lv-system.json'))
bus_kg = pk['busbar_choice']['busbar_mass_kg']
hv_m = sum(r['length_each_mm'] * r['conductors'] for r in hv['routes'].values() if r['mm2'] >= 16) / 1000
hv_kg = sum(r['mass_kg'] for r in hv['routes'].values())
taps_m = pk['bms']['sense_wire_len_total_m']

B = [  # area, item, part number / spec, qty, kg each, proto $ each, vol $ each, source, rollup line it replaces
 ('Pack', 'Traction cells', '26120 fast-charge cylinder 55 Wh (EVE / Wanxiang A123, Stark platform)', 594, 0.180, 11.55, 8.25, 'powertrain-cost-down.md: $210 / $150 per kWh', 'Cell_lane_1..3'),
 ('Pack', 'Series busbars', f"Al 1350 tapered, 4.0 x 24 mm full section, PI film, {len(open(OUT / 'busbars.csv').readlines()) - 1} links + 2 end plates", 1, bus_kg, 600, 60, 'material + stamping est.', 'Pack internals allowance'),
 ('Pack', 'Fuse-collector plates', 'Ni-plated Cu C11000 0.30 mm, per-cell fusible necks 8.1 x 0.30 mm', 1, 1.1, 500, 40, 'est.', 'Pack internals allowance'),
 ('Pack', 'Insulation films and lane barriers', 'PI 0.5 mm films, 1 mm PC barriers', 1, 0.5, 200, 25, 'est.', 'Pack internals allowance'),
 ('Pack', 'BMS', 'Orion BMS2 108-cell (Ewert Energy)', 1, 1.47, 1285, 350, 'orionbms.com MSRP; vol = custom BMS per cost-down study', 'Orion_BMS2_108_supplier_STEP'),
 ('Pack', 'Thermistor expansion module', 'Orion Thermistor Expansion Module (80 ch)', 1, 0.15, 350, 40, 'est.', 'Pack internals allowance'),
 ('Pack', 'Cell NTC thermistors', '10 k NTC ring/can-mount, 75 pcs', 75, 0.002, 2, 0.4, 'est.', 'Pack internals allowance'),
 ('Pack', 'Cell-tap harness', f"22 AWG UL11028 600 V, {taps_m} m, 3 x Orion tap connectors (TE 1123343-2 crimps)", 1, taps_m * 0.006, 250, 40, 'Orion wiring manual', 'Pack internals allowance'),
 ('Pack', 'Cell-tap fuses', 'Bel Fuse 0ACG-2000-TE (2 A, 500 VDC, AEC-Q200)', 100, 0.0005, 1.5, 0.5, 'belfuse.com', 'Pack internals allowance'),
 ('Pack', 'Pack lid pass-throughs + breather', '3 x sealed sense pass-through, GORE PolyVent', 1, 0.15, 120, 25, 'est.', 'Pack internals allowance'),
 ('Protection', 'Service disconnect + main fuse', 'Amphenol MSD08 fused (400 A fuse option, HVIL)', 1, 0.45, 250, 90, 'amphenol MSD08 datasheet', 'Main_fuse_branch_search_region'),
 ('Protection', 'Pyro breaker', 'Sensata STP500P (500 A cont, 500 V / 22 kA)', 1, 0.25, 150, 45, 'Mouser Sensata A+P PyroFuse page', ''),
 ('Protection', 'Main contactors', 'Sensata GIGAVAC GX14 with 12 V coil (GX14 B-coil code; aux contact suffix TBC)', 2, 0.50, 250, 90, 'GX14 datasheet 0.5 kg', 'GX14_main_positive/negative_OUTLINE'),
 ('Protection', 'DC charge contactors', 'Sensata GIGAVAC GX14, 12 V coil', 2, 0.50, 250, 90, 'GX14 datasheet', ''),
 ('Protection', 'Precharge relay', 'TE Kilovac LEV100 series, 12 V coil', 1, 0.15, 120, 35, 'te.com', ''),
 ('Protection', 'Precharge resistor', f"TE/CGS HSC100 {hv['precharge']['choice']['R_ohm']} ohm 100 W", 1, 0.10, 40, 10, 'te.com', ''),
 ('Protection', 'AC routing relays (inlet -> OBC)', '2 x TE Kilovac LEV100 (interlocked with DC contactors)', 2, 0.15, 120, 35, 'te.com', ''),
 ('Protection', 'Branch fuses + holders', 'Eaton Bussmann EV series 30 A / 10 A / 15 A, 500 VDC', 3, 0.05, 20, 7, 'eaton.com EV fuses', ''),
 ('Sensing', 'Pack current + 3 voltages', 'Isabellenhuette IVT-S-500-U3-I-CAN2-12/24', 1, 0.20, 350, 120, 'isabellenhuette.com IVT-S datasheet', ''),
 ('Sensing', 'Insulation monitor', 'Bender ISOMETER iso175C-32-SS (100 k fault / 500 k warn)', 1, 0.15, 350, 120, 'bender.de iso175', ''),
 ('Enclosures', 'BDU (upper positive junction)', 'Al die-cast/sheet IP67 100 x 150 x 115 mm, PA66-GF carriers, HVIL lid switch', 1, 0.90, 400, 80, 'est.', 'HV_cabinet_2mm_STUDY (split)'),
 ('Enclosures', 'RJB (rear negative junction)', 'existing 2 mm Al cabinet, IP67 + drain', 1, 0.83, 250, 50, 'CAD volume', 'HV_cabinet_2mm_STUDY'),
 ('Enclosures', 'CJB (charge junction)', 'Al IP67 230 x 60 x 120 mm', 1, 0.50, 250, 40, 'est.', ''),
 ('HV harness', 'HV cable 50 mm2 shielded', f"Coroplast Coroflex FHLR2GCB2G 50 mm2 (9-2611), {hv_m:.1f} m", 1, hv_kg, hv_m * 25, hv_m * 10, 'Coroflex sheet 630 g/m', 'HV cables and lugs'),
 ('HV harness', 'HV connectors', 'Amphenol PowerLok 300 (PL082X receptacles / PL282X plugs, 50 mm2, shielded backshells)', 10, 0.12, 80, 25, 'RS / Amphenol listings', 'HV cables and lugs'),
 ('HV harness', 'Lugs, clamps, conduit, labels', 'tin-plated Cu lugs, P-clamps, orange split conduit', 1, 0.40, 120, 30, 'est.', 'HV cables and lugs'),
 ('Charging', 'NACS inlet', 'Volex NACS inlet 1000 V, 500 A cont (UL 2251, SAE J3400), with door and lock actuator', 1, 0.90, 300, 120, 'volex.com datasheet', ''),
 ('Charging', 'Charge communication', 'ADVANTICS ADM-CS-EVCC', 1, 0.20, 1200, 150, 'advantics docs; price est.', ''),
 ('Charging', 'On-board charger', 'BROGEN PV1776 6.6 kW (<=3 kg catalogue)', 1, 3.0, 900, 350, 'BROGEN catalogue p11', 'BROGEN_PV1776_body (6.5 kg estimate)'),
 ('LV', 'DC-DC converter', 'HELLA high-voltage DC/DC 400 V -> 12 V (1.2 kW passive / 1.5 kW active air, 2.8 kg)', 1, 2.8, 600, 200, 'hella.com product 4957', 'DC-DC converter 1 kW (1.2 kg)'),
 ('LV', '12 V battery', 'Shorai LFX14A4-BS12 LiFePO4 4.5 Ah, 210 CCA', 1, 0.90, 200, 60, 'Shorai spec sheet', '12 V lithium battery'),
 ('LV', 'VCU', 'AEM EV VCU200 (30-8000) prototype; custom VCU at volume', 1, 0.40, 1500, 150, 'AEM product description', ''),
 ('LV', 'Power distribution', 'ECUMaster PMU16 prototype (16 smart outputs, 1.15 kg); custom PDU at volume (0.5 kg)', 1, 1.15, 1385, 120, 'reseller listings', 'LV wiring harness (fuse box part)'),
 ('LV', 'LV harness', f"FLRY-B 0.35-16 mm2, TE/Deutsch DT/DTM connectors, copper {lv['lv_harness_copper_mass_kg']} kg", 1, 2.4, 600, 150, 'elec-lv.py lengths x2.3 for insulation/connectors', 'LV wiring harness'),
 ('LV', 'Keyless + immobiliser + steering lock', 'Huf/Continental-class keyless module, 2 fobs', 1, 0.25, 250, 60, 'est.', ''),
 ('LV', 'Bonding straps, HVIL loop, seals', '6 mm2 tinned straps, HVIL wiring, cable glands', 1, 0.30, 120, 30, 'est.', ''),
]
rows, tot = [], dict(kg=0, proto=0, vol=0)
for a, item, pn, q, kg, cp, cv, src, rl in B:
    rows.append(dict(area=a, item=item, part=pn, qty=q, kg_each=round(kg, 4), kg_total=round(kg * q, 3),
                     usd_proto_each=round(cp, 2), usd_proto_total=round(cp * q), usd_vol_each=round(cv, 2), usd_vol_total=round(cv * q),
                     source=src, replaces_rollup_line=rl))
    tot['kg'] += kg * q; tot['proto'] += cp * q; tot['vol'] += cv * q
with open(OUT / 'electrical-bom.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# mass comparison with mass-rollup.csv allowances (non-cell)
roll = {r[0]: float(r[2]) for r in csv.reader(open(R / 'mass-rollup.csv')) if len(r) > 2 and r[2].replace('.', '', 1).isdigit()}
keys = ['Pack internals (busbars, cooling ribbon, potting, slave boards)', 'HV cables and lugs', 'DC-DC converter 1 kW', '12 V lithium battery',
        'LV wiring harness', 'Orion_BMS2_108_supplier_STEP', 'HV_cabinet_2mm_STUDY', 'GX14_main_positive_OUTLINE', 'GX14_main_negative_OUTLINE', 'BROGEN_PV1776_body']
roll_sum = sum(roll.get(k, 0) for k in keys)
non_cell = [r for r in rows if r['item'] != 'Traction cells']
bom_comparable = sum(r['kg_total'] for r in non_cell)
pack_internal = sum(r['kg_total'] for r in rows if r['area'] == 'Pack' and r['item'] not in ('Traction cells', 'BMS'))
summary = dict(total_kg=round(tot['kg'], 1), total_usd_proto=round(tot['proto']), total_usd_vol=round(tot['vol']),
               cells_usd_vol=round(594 * 8.25), noncell_usd_vol=round(tot['vol'] - 594 * 8.25),
               rollup_lines_compared=keys, rollup_kg=round(roll_sum, 2), bom_noncell_kg=round(bom_comparable, 2),
               delta_kg=round(bom_comparable - roll_sum, 2),
               pack_internal_electrical_kg=round(pack_internal, 2), pack_internal_allowance_kg=roll.get(keys[0]),
               note='pack-internal electrical mass excludes cooling ribbon, potting and cell restraints, which share the same allowance')
json.dump(summary, open(OUT / 'electrical-bom-summary.json', 'w'), indent=1)
print(json.dumps(summary, indent=1))
