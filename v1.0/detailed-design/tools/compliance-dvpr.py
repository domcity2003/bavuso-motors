"""Builds detailed-design/compliance/dvpr.csv (design verification plan & report) and sums budget and timeline.
Costs are planning estimates (2026 USD, outsourced lab rates where a lab is named), not quotes.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/compliance-dvpr.py
"""
import csv, json
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'compliance'
H = ['test_id', 'order', 'phase', 'system', 'test', 'method_or_standard', 'acceptance_criteria', 'samples', 'sample_type',
     'cost_low_usd', 'cost_base_usd', 'cost_high_usd', 'duration_weeks', 'start_week', 'end_week', 'facility', 'depends_on',
     'requirement_ids', 'status', 'result']
# (id, phase, system, test, method, acceptance, samples, sample_type, base_cost_k, weeks, start_week, facility, depends, reqs)
T = [
 ('DV-H01','DV0','Ergonomics','Adjustable seating buck + static rider clinic','Buck built from CAD hard points; 30 riders 5th F-95th M; SAE J1100-style posture capture','>=80% of riders rate seat/bar/peg >=4/5; joint angles in comfort-study bands; standing reach <=500 mm; feet-down reach >=70% of riders on balls of both feet',1,'buck',85,8,4,'In-house + clinic agency','','X-01'),
 ('DV-H02','DV0','Ergonomics','Controls and displays audit on buck','FMVSS 123 Table 1/3, UN R60','All controls in mandated positions; telltales/symbols compliant; lever reach adjustable 75-95 mm',1,'buck',15,2,12,'In-house','DV-H01','US-14;EU-05'),
 ('DV-S01','DV1','Structure','Frame + pack-case static proof and ultimate','Hydraulic actuators at head tube/pivot/shock; load cases from FEA report (braking 1.5 g, bump 3 g, combined)','No yield at 1.0x limit loads; no failure at 1.5x; strain within 10% of FEA',2,'frame+pack case (no cells)',90,6,28,'Structures lab','FEA release','X-03'),
 ('DV-S02','DV1','Structure','Frame + pack-case + lugs multi-axial durability','Road-load data replay on 6-channel rig, 1.5 design lives','No crack (dye penetrant) after 1.5 lives; bolt preload loss <10%; lug joints intact',2,'frame+pack case (dummy cells)',450,16,40,'Structures lab (e.g., MIRA/Kistler)','DV-S01;DV-R02 data','X-03'),
 ('DV-S03','DV1','Chassis','Wheels, swingarm, fork, bars, pegs, stand fatigue','ISO 8644 (wheel radial/bending fatigue); component rigs','Wheels: no crack after ISO 8644 cycles; bars 100k cycles at +-500 N; pegs 1,500 N static',3,'components',160,12,30,'Component lab','','US-12'),
 ('DV-S04','DV2','Structure','Full-vehicle road simulator (2-post shaker)','Drive files from proving ground; accelerated 160,000 km equivalent','No structural, bracket, harness or HV connector failure; rattles closed; pack retained',2,'DV2 bike',380,12,56,'Road-simulator lab','DV-R02 data','X-03;EU-10'),
 ('DV-S05','DV1','NVH','Modal survey and steering-head wobble mode check','Impact hammer + shaker, frame on bungees and in-vehicle','Frame/pack first modes not within 2 Hz of wobble/weave and motor orders',1,'DV1 bike',40,2,34,'In-house','DV-S01',''),
 ('DV-B01','DV1','Brakes','Brake dyno: pad/rotor sizing, fade, green/burnished friction','SAE J2522-style motorcycle procedure; FMVSS 122/R78 schedules on the dyno','mu 0.40-0.50 stable +-15%; rotor <=650 C; fade stop within S2<=1.67S1-0.067V; no judder',2,'corner sets',150,8,20,'Brake dyno lab','','US-13;EU-06'),
 ('DV-B02','DV2','Brakes','Vehicle brake compliance pre-test (all FMVSS 122 / R78 tests)','FMVSS 122 S6.3-S6.11, R78','Category 3-3 limits: front S<=0.1V+0.0087V2, rear S<=0.1V+0.0133V2, all S<=0.0060V2, high speed S<=0.1V+0.0067V2, wet >=60%/<=120%, fade, ABS high/low mu, split failure, warning lamps',2,'DV2 bike',180,6,60,'Proving ground','DV-B01;DV-B03','US-13;EU-06'),
 ('DV-B03','DV2','Brakes','ABS + cornering ABS + regen blending calibration (incl. low mu)','Supplier ABS calibration loops; ice/snow and wet basalt','No wheel lock above 15 km/h; rear lift-off mitigation; regen never reduces total decel below rider demand; stop lamp logic',2,'DV2 bike',250,10,62,'Winter + summer proving grounds','DV-B01','US-13;EU-06'),
 ('DV-D01','DV1','Drive','Motor+inverter dyno: maps, R85 30-min power, thermal derate','UN R85 / 134/2014 Annex X','30-min power declared >35 kW (A3); peak 130 kW 30 s at 45 C coolant; efficiency map within 2% of model',2,'drive units',220,10,16,'E-drive dyno lab','','EU-19'),
 ('DV-D02','DV1','Drive','Reduction gear + belt durability','Rig with launch and regen reversals, 1.5 lives','No pitting/scuffing; belt tension loss <15%; seal leak none',2,'drive units',180,14,26,'Gear lab','DV-D01',''),
 ('DV-D03','DV2','Drive','Performance: 0-100 km/h, top speed, gradeability','Instrumented GPS; SAE J1491-like','0-60 mph <=3.3 s rider on; top speed >=200 km/h at 30% SOC',2,'DV2 bike',60,3,66,'Proving ground','DV-D01',''),
 ('DV-D04','PV','Drive','Energy consumption and range (WMTC) + 70 mph highway range','134/2014 Annex VII; constant 70 mph on chassis dyno','Declared range +-3%; >=200 mi at 70 mph if CdA target met',2,'PV bike',45,2,98,'Chassis-dyno lab','DV-A02','EU-20'),
 ('DV-A01','DV1','Aero','Wind tunnel with rider (two sessions: DV1 shape, DV2 refinement)','Full-scale tunnel, moving ground if available, yaw 0-15 deg','CdA <=0.40 m2 (target 0.38); front lift within dynamics limits; helmet buffeting below panel target',2,'clay/DV bike',160,4,44,'Full-scale tunnel (e.g., A2 Wind Tunnel)','CFD release','X-01'),
 ('DV-A02','DV2','Aero','Coastdown road-load','SAE J2263 adapted for motorcycles, two directions, 5 runs each','Road-load coefficients with 95% CI; CdA within 5% of tunnel',2,'DV2 bike',35,2,70,'Proving ground','DV-A01',''),
 ('DV-T01','DV2','Thermal','Hot climate drive + DC fast charge','Climatic chamber 45 C, 1,000 W/m2 solar; 70 mph soak then fast charge','Cells <=55 C, power derate only after 20 min at 130 kW; charge 10-80% within spec',2,'DV2 bike',200,6,60,'Climatic chassis-dyno chamber','DV-D01','X-02'),
 ('DV-T02','DV2','Thermal','Cold start, cold charge, cold range','-20 C soak; -30 C storage','Ready to ride within 10 s; charge accepted with pack heater; no BMS fault',2,'DV2 bike',120,4,66,'Climatic chamber','DV-T01',''),
 ('DV-T03','DV1','Thermal','Pack thermal balance and cooling plate validation','Pack in chamber on cycler: drive cycles and 3 consecutive DCFC','Cell-to-cell delta-T <=5 C; energy balance closes within 5%',2,'pack',90,6,30,'Battery lab','DV-P02',''),
 ('DV-T05','DV2','Sealing','Wading 450 mm + washing + pack/cabinet/motor IP67','Wading trough 450 mm at 10 km/h for 3 min, hot pack (40 C) into 10 C water; IPX6/IPX9K wash; IEC 60529 IP67 on pack, cabinet, motor, gear case, connectors','No water in any HV enclosure; isolation >=100 ohm/V during and after; R136 5.1.2.4.2 water test passed',2,'DV2 bike + enclosures',70,3,68,'Proving ground + IP lab','DV-S04','X-02;EU-09'),
 ('DV-T06','DV2','Durability','Cyclic corrosion','SAE J2334-type cyclic salt, 10 weeks','No red rust on structure; connectors no corrosion past seal; fasteners removable',2,'DV2 bike',110,12,64,'Corrosion chamber','',''),
 ('DV-T07','DV2','Sealing','Dust ingress','IEC 60529 IP6X on enclosures; dust road run','No dust inside HV enclosures; brake/belt wear within spec',1,'DV2 bike',40,2,74,'IP lab','',''),
 ('DV-E01','DV2','EMC','Vehicle EMC drive mode: emissions + immunity','UN R10 rev 6 (and FCC Part 15 check)','Broad/narrowband below R10 limits; no function loss at 30 V/m',1,'DV2 bike',180,6,66,'Vehicle EMC chamber','ESA pre-scans','EU-17;US-23'),
 ('DV-E02','DV2','EMC','EMC charge mode (harmonics, flicker, surge, conducted)','UN R10 RESS-charging annexes; IEC 61000-3-2/-3-3','Within limits; charging not interrupted by immunity tests',1,'DV2 bike + OBC',90,3,72,'Vehicle EMC chamber','DV-E01','EU-17'),
 ('DV-E03','DV2','Electrical safety','HV electrical safety','UN R136 Part I / ISO 13063: IPXXB/IPXXD probes, isolation, HVIL, equipotential <0.1 ohm, withstand','Isolation >=100 ohm/V DC; coupler >=1 Mohm; bonding <0.1 ohm; no exposed live parts',2,'DV2 bike',45,2,60,'Electrical safety lab','','EU-09;EU-23'),
 ('DV-E04','DV1','Functional safety','HARA/FMEA + HIL fault injection (throttle, regen, BMS, contactors)','ISO 26262-style process adapted; HIL rig','All ASIL-rated safety goals verified; single faults lead to safe state within FTTI',1,'HIL rig',250,20,12,'In-house + consultant','','EU-24'),
 ('DV-E05','DV2','Charging','Charging interoperability (AC, DC NACS/CCS)','SAE J1772/J3400, ISO 15118 / DIN 70121 conformance; field station tests','>=98% session success over 200 sessions on 5 networks',2,'DV2 bike',120,8,72,'Interop lab + field','DV-E02','US-24'),
 ('DV-P01','DV1','Battery','UN 38.3 pack-level (T1-T5, T7)','UN Manual of Tests 38.3; large battery: T4 15 gn/11 ms for 134 kg','No leakage, venting, disassembly, rupture or fire; OCV >=90%',4,'packs',180,10,36,'Accredited battery lab','DV-P02','EU-15;US-22'),
 ('DV-P02','DV0','Battery','Cell characterization and abuse (independent)','IEC 62660-1/-2/-3; nail, crush, overcharge, thermal ramp; supplier 38.3 report review','Data meets model inputs; abuse no fire/explosion where standard requires',60,'cells',150,10,6,'Battery lab','',"EU-16"),
 ('DV-P03','DV1','Battery','R136 vibration (Annex 8A)','UN R136 Annex 8A on pack in vehicle mounting','No leakage/rupture/fire/explosion; isolation >=100 ohm/V',1,'pack',60,4,46,'Battery lab','DV-P01','EU-10'),
 ('DV-P04','DV1','Battery','R136 thermal shock and cycling (Annex 8B)','UN R136 Annex 8B','As DV-P03',1,'pack',40,4,46,'Battery lab','','EU-11'),
 ('DV-P05','DV2','Battery','R136 mechanical shock (Annex 8D) vehicle fall-down from stand','UN R136 6.4.2 / Annex 8D, both sides','Pack retained, no leakage/rupture/fire/explosion; isolation >=100 ohm/V; with guards no pack contact with ground',1,'DV2 bike',50,2,62,'Proving ground + battery lab','DV-C01','EU-12'),
 ('DV-P06','DV1','Battery','External short, overcharge, over-discharge, over-temperature, over-current','UN R136 6.6-6.9 (Annex 8F-8I)','Protection operates; no fire/explosion; isolation maintained',4,'packs',160,8,48,'Battery lab','DV-E04','EU-14'),
 ('DV-P07','DV1','Battery','Thermal propagation (single-cell trigger)','Internal target modelled on GB 38031-2020 8.2.7 (5 min warning, no fire/explosion outside pack)','No external fire or explosion for >=5 min after warning; vent gas away from rider',2,'packs',200,6,52,'Battery abuse lab','DV-T03',''),
 ('DV-P08','DV1','Battery','Pack crush side and bottom','Internal target: 75 mm half-cylinder to 100 kN or 30% (GB 38031 / SAE J2464 practice)','No fire/explosion; no leakage after 1 h observation',2,'packs',120,4,52,'Battery abuse lab','','X-04'),
 ('DV-P09','DV1','Battery','Pack immersion and salt-water immersion','IEC 60529 IP67 (1 m, 30 min); 3.5% NaCl immersion 2 h (hazard check)','IP67: no ingress; salt: no fire/explosion',2,'packs',50,3,50,'Battery lab','','X-02'),
 ('DV-P10','DV1','Battery','Pack floor + skid rock-strike / penetration','Drop-weight rig, 50 mm hemispherical impactor, energy equal to 3 g bottom-out (11.4 kN quasi-static) and 300 J impact','No contact with pack floor; skid dent <=12 mm; floor no permanent set',3,'skid + pack case sections',60,3,40,'Impact lab','','X-04'),
 ('DV-P11','DV1','Battery','Pack cycle life incl. DC fast charge','1,000 cycles mixed (30% DCFC 10-80%)','>=80% SOH at 1,000 cycles; no cell-group imbalance >30 mV',2,'packs',350,40,40,'Battery lab','DV-T03',''),
 ('DV-P12','DV1','Battery','Calendar ageing','3 temperatures x 2 SOC, 12 months','Fade model within +-2% of prediction',12,'modules',100,52,30,'Battery lab','',''),
 ('DV-C01','DV2','Crash','Tip-over tests (standstill and from stand, with/without luggage)','10 falls each side from upright and from the side stand onto asphalt; high-speed video','No contact of pack, radiator, levers, mirrors (folded allowed), HV parts; guard permanent set 0 mm after a rider-assisted fall and <=5 mm after a free fall; only pucks replaceable',2,'DV2 bike',40,2,58,'Proving ground','DV-C04','X-03;EU-12'),
 ('DV-C02','DV2','Crash','Low-side slide 30 and 50 km/h','Bike released at 45 deg lean on asphalt sled rig or rider-less launch','Pack never contacts ground; HV isolation >=100 ohm/V after; puck wear <=15 mm of 20 mm; bike rideable home at 30 km/h',2,'DV2 bike',90,3,62,'Proving ground','DV-C01','X-03'),
 ('DV-C03','DV1','Crash','Skid plate quasi-static and drop test','Load 11.4 kN on 50 mm punch; drop 387 kg sled on 50 mm rock from bottomed suspension','Dent <=12 mm, no pack contact',3,'skid plates',35,2,38,'Impact lab','','X-04'),
 ('DV-C04','DV1','Crash','Crash guard and anchor static proof','Load at puck points normal to ground plane','Guard collapse >=12 kN; anchors no yield at 21 kN; pack/frame lug no damage',3,'guard sets + lugs',25,2,44,'Structures lab','DV-S01','X-03'),
 ('DV-C05','DV2','Geometry','Laden ground clearance, breakover, lean, fording audit','Measure at curb, rider, two-up + luggage; lean to contact on tilt table','Clearance >=200 mm rider-on; breakover >=28 deg; guard/peg contact >=45 deg lean',2,'DV2 bike',10,1,58,'In-house','','X-01;X-02;US-11'),
 ('DV-L01','DV2','Lighting','Lighting photometry and installation','FMVSS 108; UN R53 + R148/R149/R150','All lamps within photometry; spacing/angles met',1,'lamp set + bike',90,4,64,'Photometry lab','','US-01..07;EU-02;EU-03'),
 ('DV-L02','DV2','Mirrors','Mirror field of view and impact','FMVSS 111 S10; UN R81 (incl. impact test)','Areas and FoV met; mirror folds/ breaks per R81 impact test without sharp edges',2,'mirrors + bike',25,2,64,'Lab','','US-08;EU-04'),
 ('DV-L03','DV2','Horn','Audible warning','UN R28','Class I sound level and spectrum met',2,'horns',8,1,64,'Acoustic lab','','EU-07'),
 ('DV-N01','DV2','Noise','Drive-by noise / EPA check','UN R41 (EV adaptation) via 134/2014 Annex IX; EPA 40 CFR 205 App. I if applicable','Below limits; document AVAS decision',1,'DV2 bike',25,1,70,'Acoustic proving ground','','US-16;EU-18'),
 ('DV-H03','DV2','Ergonomics','Stands, handholds, plates, passenger','44/2014 VCMR annexes; FMVSS 123 stand','Stand holds on 8% slopes and 6 deg side slope; interlock blocks drive; passenger pegs/handholds load test',2,'DV2 bike',10,1,58,'In-house','','EU-21;US-14'),
 ('DV-H04','DV2','Ergonomics','Ride clinic on DV2 bikes','40 riders, road + gravel + standing off-road','Same as DV-H01 on the road; no rider-reported hazard',4,'DV2 bike',120,4,74,'Clinic agency','DV-H01',''),
 ('DV-R01','DV2','Durability','Road durability fleet','4 bikes x 40,000 km: 60% road, 25% gravel, 15% track; DCFC every day','No safety-relevant failure; defects per bike trend down; pack SOH within model',4,'DV2 bike',650,40,66,'Fleet ops (drivers + logistics)','DV-S04 start','X-03'),
 ('DV-R02','DV1','Durability','Proving-ground rough-road accelerated + load data','Belgian pave, washboard, potholes, jumps; 2 bikes x 8,000 km equivalent; strain/accel logging for rigs','No structural failure; load spectra captured for DV-S02/S04',2,'DV1 mule',300,12,36,'Proving ground','DV-S01','X-03'),
 ('DV-R03','DV2','Durability','Environmental road trips (heat, cold, altitude 4,300 m)','Death Valley summer, northern winter, Pikes Peak','No derate below targets; charging works at altitude/cold',2,'DV2 bike',180,8,80,'Fleet ops','DV-T01',''),
 ('DV-R04','DV2','Durability','Adventure off-road durability','2 bikes x 15,000 km incl. jumps <=1 m, ruts, sand, water crossings','No pack/skid/guard failure beyond replaceable parts',2,'DV2 bike',200,20,70,'Off-road test team','DV-C03',''),
 ('DV-R05','DV2','Dynamics','Handling, high-speed stability, weave/wobble, luggage','ISO 9816/7975-style tests; 0-200 km/h with/without luggage','Wobble/weave damping >0 at all speeds with luggage; no steering damper dependency for stability',2,'DV2 bike',150,6,68,'Proving ground','DV-S05',''),
 ('PV-01','PV','All','PV confirmation on production-tooled bikes','Repeat brakes, EMC, lighting, R136 subset, water, durability 10,000 km x 4','Same acceptance as DV tests on PV parts',10,'PV bike',400,16,96,'Mixed','DV complete',''),
 ('HOM-US','HOM','Homologation','US self-certification file, Part 565/566/567, NHTSA filings','FMVSS compliance file per standard','File complete; label and VIN approved',1,'documents',60,8,104,'In-house + compliance consultant','PV-01','US-18..21'),
 ('HOM-EU','HOM','Homologation','EU L3e-A3 whole-vehicle type approval, witnessed tests, CoP','168/2013; 3/2014; 44/2014; 134/2014; UN R10/R28/R41/R53/R60/R75/R78/R81/R136','Type-approval certificate; CoC',2,'PV bike',350,16,104,'Technical service + approval authority','PV-01','EU-01..24'),
 ('HW-DV1','DV1','Hardware','DV1 mule builds','4 hand-built mules','n/a',4,'vehicles',600,20,16,'Prototype shop','',''),
 ('HW-DV2','DV2','Hardware','DV2 builds','12 bikes on soft tooling','n/a',12,'vehicles',1080,16,40,'Prototype shop','HW-DV1',''),
 ('HW-PV','PV','Hardware','PV builds','10 bikes from production tooling','n/a',10,'vehicles',550,12,86,'Pilot line','',''),
 ('HW-PACK','DV1','Hardware','Destructive and test packs + modules','24 packs (beyond vehicles) + 60 coupons/modules','n/a',24,'packs',530,30,24,'Pack prototype line','',''),
]
rows = []
for i, t in enumerate(sorted(T, key=lambda t: (t[10], t[0])), 1):
    (tid, ph, sysn, test, meth, acc, n, st, c, wk, s, fac, dep, req) = t
    rows.append(dict(zip(H, [tid, i, ph, sysn, test, meth, acc, n, st, round(c * 700), c * 1000, round(c * 1500), wk, s, s + wk,
                             fac, dep, req, 'Planned', ''])))
with open(OUT / 'dvpr.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=H); w.writeheader(); w.writerows(rows)
tests = [r for r in rows if not r['test_id'].startswith('HW')]
hw = [r for r in rows if r['test_id'].startswith('HW')]
s = lambda rs, k: sum(r[k] for r in rs)
summary = dict(n_tests=len(tests), tests_base=s(tests, 'cost_base_usd'), tests_low=s(tests, 'cost_low_usd'), tests_high=s(tests, 'cost_high_usd'),
               hardware_base=s(hw, 'cost_base_usd'), total_base=s(rows, 'cost_base_usd'), total_low=s(rows, 'cost_low_usd'),
               total_high=s(rows, 'cost_high_usd'), end_week=max(r['end_week'] for r in rows),
               by_phase={p: s([r for r in rows if r['phase'] == p], 'cost_base_usd') for p in sorted({r['phase'] for r in rows})},
               by_system={p: s([r for r in rows if r['system'] == p], 'cost_base_usd') for p in sorted({r['system'] for r in rows})})
(OUT / 'dvpr-summary.json').write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
# validate the requirements matrix
with open(OUT / 'requirements-matrix.csv', encoding='utf-8') as f:
    rr = list(csv.reader(f))
bad = [r[0] for r in rr if len(r) != len(rr[0])]
print('matrix rows', len(rr) - 1, 'bad rows', bad)
from collections import Counter
print(Counter(r[7] for r in rr[1:]))
