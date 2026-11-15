"""Bavuso V1.0 adventure: 12 V system detailed design.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).
Load list -> worst-case continuous and transient demand -> DC-DC rating sweep and 12 V battery check ->
LV harness gauges (ISO 6722 FLRY-B, voltage drop and ampacity) -> fuse / smart-channel assignment -> CAN plan.
Run from v1.0 with any python 3.
"""
import csv, json, math
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / 'detailed-design' / 'electrical'
V = 13.5
# name, watts, kind (cont/intermit/transient), duty in case A night-cold ride, B hot DC fast charge, C peak 1 s,
# location (saved coords, mm) for harness length, source/basis
LOADS = [
 ('Headlamp low beam LED', 25, 1, 0, 1, (1430, 0, 875), 'typical motorcycle LED low beam 20-30 W'),
 ('Headlamp high beam LED (adds)', 30, 1, 0, 1, (1430, 0, 875), 'typical LED high +25-35 W'),
 ('DRL blade', 8, 0, 0, 0, (1430, 0, 905), 'DRL off when low beam on'),
 ('Aux fog / cornering lamps (adventure pack)', 30, 1, 0, 1, (1385, 0, 830), '2 x 15 W LED'),
 ('Tail / stop LED', 6, 1, 0, 1, (-178, 0, 856), 'stop 5 W + tail 1 W'),
 ('Indicators LED (2 flashing, 50%)', 5, 0.5, 0, 1, (0, 0, 800), '4 x 5 W, 2 active at 50 % duty'),
 ('Plate lamp', 2, 1, 0, 1, (-342, 0, 668), ''),
 ('TFT dash 7 in + switch cubes', 12, 1, 1, 1, (1110, 0, 1150), 'automotive TFT cluster 8-15 W'),
 ('VCU (AEM VCU200 class)', 6, 1, 1, 1, (550, 0, 670), 'supplier 9-16 V, est. 0.45 A'),
 ('BMS Orion BMS2', 2, 1, 1, 1, (900, 0, 860), 'Orion spec <2 W active'),
 ('Thermistor expansion module', 1, 1, 1, 1, (900, 0, 860), 'est.'),
 ('Isolation monitor Bender iso175', 2, 1, 1, 1, (650, -60, 700), 'est.'),
 ('Current sensor IVT-S', 1.5, 1, 1, 1, (510, 40, 320), 'IVT-S datasheet ~ 1.2 W at 12 V'),
 ('Inverter control board', 15, 1, 0.3, 1, (860, 0, 760), 'Cascadia CM200 LV ~1 A at 12 V (hardware manual)'),
 ('OBC / DC-DC / EVCC control', 8, 0.3, 1, 1, (880, 0, 670), 'est.'),
 ('Main contactors GX14 x2 (economised hold)', 5.6, 1, 1, 0, (600, 0, 700), 'GX14 hold ~2.3-2.8 W each'),
 ('Contactor pull-in x2 (75 ms)', 60, 0, 0, 1, (600, 0, 700), 'est. ~2.2 A each before economiser drops a coil'),
 ('DC charge contactors GX14 x2 (hold)', 5.6, 0, 1, 0, (835, 146, 700), 'only while DC charging'),
 ('ABS / cornering ABS ECU + IMU (Bosch MSC class)', 10, 1, 1, 1, (400, 60, 700), 'ECU+valves average'),
 ('ABS pump motor (pressure modulation)', 0, 0, 0, 300, (400, 60, 700), 'transient 20-25 A for <1 s; Bosch does not publish, est.'),
 ('Coolant pump drive loop (motor oil HX, inverter, OBC)', 45, 1, 1, 1, (900, -150, 600), 'Pierburg CWA50-class 12 V e-pump, ~40-50 W at duty point'),
 ('Coolant pump battery loop', 45, 0.6, 1, 1, (900, 150, 600), 'CWA50-class; full flow during fast charge'),
 ('Gearbox / motor oil pump', 40, 0.7, 0.3, 1, (520, 40, 420), 'oil-cooled IPM + gear stage (drive-study.md), est.'),
 ('Radiator fans x2', 130, 0.2, 1, 1, (1015, 0, 710), '2 x 65 W 7-in brushless; full speed while hot charging'),
 ('Heated grips', 40, 1, 0, 1, (900, 0, 1130), 'Oxford-class OEM grips 35-50 W at high'),
 ('Heated seat (rider)', 40, 1, 0, 1, (400, 0, 880), 'OEM heated seat 35-50 W'),
 ('USB-C PD outlet', 60, 0.5, 0.5, 1, (1050, 60, 1000), 'one 60 W PD port'),
 ('Keyless (KESSY-class) + immobiliser + steering lock', 1, 1, 0.5, 0, (1100, 0, 950), 'standby 10 mA'),
 ('Steering lock actuator (transient)', 0, 0, 0, 30, (1150, 0, 900), '2-3 A, 0.5 s'),
 ('Horn', 0, 0, 0, 45, (1300, 0, 700), 'disc horn ~3.5 A'),
 ('Telematics / LTE + GNSS', 4, 1, 1, 1, (300, 0, 850), 'est.'),
 ('TPMS receiver + radar (future ARAS)', 8, 1, 0, 1, (1380, 0, 800), 'est. ARAS radar 6-8 W'),
 ('Electric screen adjust (transient)', 0, 0, 0, 40, (1250, 0, 1050), 'est.'),
 ('Battery-pack heater control relay', 1, 0.5, 0.5, 0, (650, 0, 700), 'HV PTC heater itself runs from HV, fused 15 A'),
]
tot = {'A_night_cold_ride': 0.0, 'B_hot_DC_fast_charge': 0.0, 'C_peak_1s': 0.0}
rows = []
for name, w, a, b, c, loc, note in LOADS:
    pa, pb = w * a, w * b
    pc = (w + (c if c > 1 else 0)) if c else 0
    if c == 1: pc = w
    tot['A_night_cold_ride'] += pa; tot['B_hot_DC_fast_charge'] += pb; tot['C_peak_1s'] += pc
    rows.append(dict(load=name, W_rated=w, case_A_W=round(pa, 1), case_B_W=round(pb, 1), case_C_W=round(pc, 1),
                     x=loc[0], y=loc[1], z=loc[2], basis=note))
cont = max(tot['A_night_cold_ride'], tot['B_hot_DC_fast_charge'])

# DC-DC sweep: smallest rating with >=25 % margin over the worst continuous case at 50 C derating (0.9),
# transients above the rating come from the 12 V battery
dcdc = []
for P in (500, 750, 1000, 1500, 2000):
    usable = P * 0.9
    margin = usable / cont - 1
    batt_A = max(0.0, (tot['C_peak_1s'] - usable) / V)
    dcdc.append(dict(rating_W=P, usable_hot_W=usable, margin_vs_worst_cont=round(margin, 2), battery_assist_peak_A=round(batt_A, 1), ok=margin >= 0.25))
dcdc_choice = min((d for d in dcdc if d['ok']), key=lambda d: d['rating_W'])

# 12 V battery: Shorai LFX14A4-BS12 4.5 Ah 13.2 V 59.4 Wh, 210 CCA, 0.90 kg.
# Duties: (1) wake-up and close contactors with DC-DC off (pull-in 60 W + electronics 60 W for 5 s),
# (2) 30 days parked with keyless/telematics standby 15 mA, (3) ride home on battery if DC-DC fails: 10 min at the essential load.
standby_A = 0.015
batt = dict(part='Shorai LFX14A4-BS12 (LiFePO4, 4.5 Ah true, 59.4 Wh, 210 CCA, 0.90 kg)',
            boot_energy_Wh=round((60 + 60) * 5 / 3600, 3),
            park_30_days_Ah_at_15mA=round(standby_A * 24 * 30, 2), park_ok_without_topup=standby_A * 24 * 30 < 0.6 * 4.5,
            max_standby_mA_for_30_days_unattended=round(0.6 * 4.5 / 720 * 1000, 2),
            essential_W=sum(r['case_A_W'] for r in rows if r['load'].startswith(('Headlamp low', 'Tail', 'TFT', 'VCU', 'BMS', 'Inverter', 'Main contactors', 'ABS / cornering', 'Coolant pump drive'))),
            )
batt['limp_home_minutes_on_battery'] = round(59.4 * 0.8 / batt['essential_W'] * 60, 1)
batt['note'] = 'a 15 mA keyless+telematics standby drains the 4.5 Ah battery in ~12 days: design rule = VCU wakes once a day, closes contactors and tops the 12 V battery from the pack via the DC-DC for ~10 min (as cars do); without top-up the standby budget is 3.75 mA'

# LV harness: FLRY-B copper, 105 C class. Ampacity at 60 C ambient in a bundle (derated table, conservative),
# and 3 % voltage-drop limit for lighting/motors (5 % for others), round-trip with frame return only for chassis-bonded loads (not used: 2-wire)
FLRY = {0.35: (52.0, 6), 0.5: (37.1, 8), 0.75: (24.7, 11), 1.0: (18.5, 14), 1.5: (12.7, 18), 2.5: (7.6, 25), 4.0: (4.71, 32), 6.0: (3.14, 41), 10.0: (1.82, 57), 16.0: (1.16, 75), 25.0: (0.743, 100)}
# (mohm/m at 20 C, bundled ampacity at 60 C ambient A). Resistances: ISO 6722-1 FLRY-B; ampacity: conservative values from typical derating charts.
PDM_LOC = (552, 0, 735)
harness = []
for r in rows:
    W = max(r['W_rated'], r['case_C_W'])
    if W <= 0: continue
    I = W / V
    L = (abs(r['x'] - PDM_LOC[0]) + abs(r['y'] - PDM_LOC[1]) + abs(r['z'] - PDM_LOC[2])) * 1.15 / 1000 + 0.3
    vd_lim = 0.03 if any(k in r['load'] for k in ('lamp', 'Headlamp', 'pump', 'fan', 'Fans', 'Heated', 'motor')) else 0.05
    for g, (mohm, amp) in FLRY.items():
        Rloop = 2 * L * mohm / 1000 * 1.3
        if amp >= I * 1.25 and I * Rloop <= vd_lim * V and g >= 0.5:
            break
    fuse = next(f for f in (2, 3, 5, 7.5, 10, 15, 20, 25, 30, 40) if f >= I * 1.35)
    harness.append(dict(circuit=r['load'], I_A=round(I, 2), run_length_m=round(L, 2), gauge_mm2=g,
                        vdrop_pct=round(100 * I * 2 * L * FLRY[g][0] / 1000 * 1.3 / V, 2), fuse_or_channel_A=fuse))
# feeds
I_dcdc = dcdc_choice['rating_W'] / V
feeds = [dict(circuit='DC-DC output -> PDM main (+ and return)', I_A=round(I_dcdc, 1), run_length_m=1.2, gauge_mm2=16.0, vdrop_pct=round(100 * I_dcdc * 2 * 1.2 * 1.16e-3 * 1.3 / V, 2), fuse_or_channel_A='150 A MIDI fuse at DC-DC'),
         dict(circuit='12 V battery -> PDM main', I_A=round(tot['C_peak_1s'] / V, 1), run_length_m=0.5, gauge_mm2=10.0, vdrop_pct=round(100 * tot['C_peak_1s'] / V * 2 * 0.5 * 1.82e-3 * 1.3 / V, 2), fuse_or_channel_A='100 A MIDI fuse at battery'),
         dict(circuit='Chassis/HV-box bonding straps', I_A=0, run_length_m=0.3, gauge_mm2=6.0, vdrop_pct=0, fuse_or_channel_A='none (bonding <0.1 ohm)')]
harness = feeds + harness
lv_mass = sum(h['run_length_m'] * 2 * {0.5: 7, 0.75: 10, 1.0: 13, 1.5: 18, 2.5: 29, 4.0: 45, 6.0: 65, 10.0: 105, 16.0: 165, 25.0: 255}.get(h['gauge_mm2'], 7) for h in harness) / 1000

can = dict(
  CAN1_powertrain_500k=['VCU (term.)', 'inverter', 'BMS CAN1', 'IVT-S current sensor', 'DC-DC', 'OBC', 'EVCC ADM-CS-EVCC', 'isolation monitor iso175 (term. at far end)'],
  CAN2_chassis_500k=['VCU', 'ABS/MSC (Bosch)', 'TFT dash (term.)', 'keyless/immobiliser', 'PDM', 'telematics', 'BMS CAN2 (term.)'],
  diagnostic='OBD-style service connector on CAN2 under the seat; BMS also on CAN2 for Orion utility',
  topology='two linear buses, 120 ohm split termination at both physical ends, stubs < 0.3 m, twisted pair 0.35 mm2 FLRY-B, total length CAN1 ~2.5 m, CAN2 ~3.5 m')
keyless = dict(concept='proximity fob (125 kHz LF wake + 315/433 MHz UHF) -> keyless ECU on CAN2 -> VCU authorises READY; electric steering lock; immobiliser challenge between keyless ECU and VCU and inverter (CAN2/1 gateway in VCU)',
               start='fob present + side-stand up + brake held + start button -> VCU: BMS OK, iso OK, HVIL closed -> precharge -> main+ -> READY lamp',
               reference='production motorcycles use this pattern (e.g. BMW Keyless Ride); hardware: Continental/Huf-class keyless module, choose with VCU supplier')

json.dump(dict(prepared='2026-11-12 US Central, Claude Opus 5.5', totals_W={k: round(v) for k, v in tot.items()}, worst_continuous_W=round(cont),
               dcdc_sweep=dcdc, dcdc_choice=dcdc_choice, battery=batt, lv_harness_copper_mass_kg=round(lv_mass, 2), can=can, keyless=keyless),
          open(OUT / 'lv-system.json', 'w'), indent=1)
for fn, data in (('lv-loads.csv', rows), ('lv-harness.csv', harness)):
    with open(OUT / fn, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
print(tot, 'worst cont', round(cont)); print(dcdc); print(dcdc_choice); print(batt); print('lv copper kg', round(lv_mass, 2))
for h in harness: print(h)
