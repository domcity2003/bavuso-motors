# Bavuso V1 DVP&R (design verification plan and report)

> **Superseded in part (Nov 22, 2026).** This document predates the final V1 numbers; the authority is `00-V1-final-spec.md`. Stale here: "T1 mass 240 kg" and test V38 at <= 240 kg (final T1 <= 260 kg, 257.9 kg); `cost-model.csv` as the T9 basis (final `cost-model-v1.csv`, $29.5k); V08 and V11 assume the EMRAX housing yoke and 300 mm discs (final steel yoke, 320 mm front). V08 was revised and V53 (steering damper fail-safe) added Nov 22; the $7,036,000 US total does not include V53 (+$40,000) and is not reconciled with the NRE in `11-cost.md`.


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Data: `program/data/dvpr-v1.csv` (51 lines: 45 tests, 3 hardware build lines, 3 EU add-on lines). Generators: `program/tools/build-dfmea-dvpr.py` and `write-dvpr-md.py`. Risk rows (D01 to D46) are in `13-dfmea.md`; targets T1 to T10 are in `GATE-A-targets-locked.md`; the standards behind each test are in `12-compliance.md`. The earlier plan is `detailed-design/compliance/dvpr.csv` (62 lines, for a different bike); I reused its test list, methods and unit costs where they still apply and cut the sample counts.

## The plain answer

**Verifying V1 for a US launch would take about $7,036,000 and about 28 months, and nothing in it has been done.** That is $5,562,000 of tests plus $1,474,000 for three hand-built mules, 12 extra test packs and eight pre-production bikes. Every line is **planned**. The money is an estimate (planning figures scaled from the earlier study, not quotes; plausible range 0.7x to 1.5x, about $4.9M to $10.6M). The EU add-on (R136 pack tests, braking, lighting, EMC, type approval) is another $1,250,000 and is excluded from the headline.

The plan is shaped by the biggest risks:
- **Test first what can kill the design cheaply.** The steel pivot yoke proof (V08, about $70k, 6 weeks) decides the chassis architecture; the pivot rig (V07) and cast-arm fatigue (V06) follow. Do these before building mules.
- **The battery chain is the critical path.** Cell 2C charge life (V01, 26 weeks), lane-module propagation (V02), then UN 38.3 (V17); no bike or pack ships to a lab without UN 38.3.
- **Every target T1 to T10 has a closing test** except T9 (cost), which follows from quotes. Every High risk in `13-dfmea.md` has at least one test.

Phases: **component** = parts and modules on rigs, before any bike exists; **prototype** = the three mules and early test packs; **pre-production** = eight soft-tooled bikes and production-intent confirmation.

## Summary

| Phase | Base cost | Notes |
|---|---:|---|
| Component | $1,720,000 | 17 rig tests; weeks 0 to 30 |
| Prototype | $3,366,000 | includes 3 mules ($450k) and 12 test packs ($264k) |
| Pre-production | $1,950,000 | includes 8 bikes ($760k) |
| **US total** | **$7,036,000** | tests $5,562,000 + hardware $1,474,000 |
| EU add-on (later) | $1,250,000 | not in the headline |

### Which test closes which target

| Target | Closing tests |
|---|---|
| T1 mass <= 260 kg (final 257.9 kg) | V38 (weigh every prototype), V06, V30, V31 |
| T2 pack safety and transport | V01 to V05, V13 to V21, V26 |
| T3 range 145 mi at 70 mph, CdA 0.38 | V35, V36 |
| T4 125 mph sustained, 130 governed | V33, V37, V09, V11, V25, V41 |
| T5 90 kW peak, 55 kW continuous | V10, V37, V08, V09 |
| T6 charging 10-80% in 25 min, NACS | V22, V23, V34 |
| T7 solo plus 25 kg luggage | V30, V31 (loads from `09-structures.md`) |
| T8 comfort, stability, functional safety | V06, V07, V15, V30, V31, V32, V39, V40, V42, V46, V47, V50 |
| T9 cost | no test; follows from the BOM and quotes (`cost-model-v1.csv`, $29.5k at 10k, estimate) |
| T10 look and lighting rules | V44, V45 |

## Test plan

| ID | Test | Standard or procedure | Samples | Acceptance | Closes (target; risk rows) | Phase | Est. cost | Weeks |
|---|---|---|---|---|---|---|---:|---:|
| V01 | Cell characterisation and 2C charge life (25, 0, -10 C) | IEC 62660-1/-2 plus Molicel written charge-life data | 60 cells | Capacity and resistance match model inputs; >=80% SOH at the test life with 30% DC fast charge; no plating at -10 C with derate | T2;T6; D01, D12, D14 | component | $120,000 | 26 |
| V02 | Thermal propagation, lane module (single cell then group of 11, with and without coolant) | Internal target modelled on GB 38031-2020 8.2.7; SAE J2464 practice | 3 modules | No external fire or explosion for >=5 min after warning; neighbour cells stay below 170 C; gas leaves by the belly vent | T2 safety; D01, D02, D03, D04 | component | $200,000 | 8 |
| V03 | Burst vent opening pressure and flow | Rig, pressure ramp | 6 vents | Opens at 15-20 kPa; >=600 mm2 free area each | T2 safety; D02, D03 | component | $40,000 | 4 |
| V04 | Wire-bond fuse pulse and fusing | Pulse bench per cell datasheet currents | 40 bond sets | Opens under shorted-cell current; neighbour bonds survive; no cell damage | T2 safety; D01 | component | $45,000 | 4 |
| V05 | Module vibration and shock with resistance monitoring | UN R136 Annex 8A profile (confirm with lab); ISO 16750-3 | 3 modules | No open bond or cell movement; interconnect resistance change <10% | T2; D05, D06, D11 | component | $60,000 | 4 |
| V06 | Cast swingarm static, fatigue and X-ray | ASTM E466-style; load cases from 09-structures.md | 3 arms | No crack (dye penetrant) after 1.5 lives; casting porosity within class | T1;T8; D28 | component | $140,000 | 10 |
| V07 | Pivot bearing and stub rig (design load 1.2x, plus 21 kN slider) | Bearing life ISO 281; static proof | 2 sets | No yield; L10 >= 160,000 km at spectrum; play within spec after test | T8; D29, D30 | component | $90,000 | 8 |
| V08 | Steel pivot yoke (rev E, cross-member Z545) static and fatigue proof under belt-loop load; EMRAX housing is not the load path | Static rig at 1.2 x 11.3 kN belt pull plus fatigue to 1.5 lives | 2 yokes | No yield or crack; deflection below the value used in FEA; weld class confirmed | T1;T5; D24, D30 | component | $70,000 | 6 |
| V09 | Belt, pulley and hub durability | Gates design manual; launch and regen reversals | 2 drive sets | 1.5 lives, no tooth shear; tension loss <15%; no pulley fretting; tracking within flange limits | T4;T5; D25, D26, D27 | component | $140,000 | 14 |
| V10 | Motor and inverter dyno (R85-style 30-min power) at 300-330 V and cold | UN R85 style; EMRAX/Cascadia data | 2 sets | Peak >=90 kW at 330 V bus; continuous >=55 kW; no derate surprises vs model | T5; D21, D23 | component | $200,000 | 10 |
| V11 | Brake dyno: fade and wear | SAE J2522-style | 2 sets | 320 mm front and 267 x 5 rear discs pass fade at 125 mph energy (the 300 mm option is dropped) | T4; D34 | component | $130,000 | 8 |
| V13 | HV electrical safety bench | ISO 6469-3; UN R136 Part I practice; IEC 60529 IPXXB/D | 2 HV box sets | Isolation >=500 ohm/V (210 kohm); bond <0.1 ohm; bus <60 V within 3 s of opening; HVIL opens contactors | T2 safety; D15, D16, D17, D41 | component | $45,000 | 3 |
| V14 | Short-circuit breaking: fuse, contactors, pyro | Bench at pack voltage, 3.4-6.2 kA prospective | 3 sets | Fuse and pyro clear without arc or damage; contactors open below 350 A only; fuse I2t within busbar withstand | T2 safety; D09, D16, D18 | component | $80,000 | 6 |
| V15 | BMS, throttle and VCU hazard analysis, FMEDA and HIL fault injection | ISO 26262 (Part 12 motorcycles) approach; ISO 13849 for non-electronic channels | 1 rig | All safety goals met; single faults reach safe state within the fault-tolerant time; ASIL table closed | T8; D10, D18, D19, D22, D38, D42, D43 | component | $250,000 | 20 |
| V16 | Pack vibration and thermal shock | UN R136 Annex 8A/8B practice | 2 packs | No leak, rupture, fire; isolation >=100 ohm/V | T2; D06 | prototype | $100,000 | 8 |
| V17 | UN 38.3 pack-level (T1-T5, T7) plus cell summary | UN Manual of Tests and Criteria 38.3 | 4 packs | No leakage, venting, rupture or fire; no mass loss; OCV drop <10% | T2 transport; D10 | prototype | $180,000 | 10 |
| V18 | UL 2580 pack abuse (voluntary) | UL 2580 / SAE J2464 | 3 packs | Report passes; no fire or explosion outside pack | T2; D01 | prototype | $250,000 | 16 |
| V19 | Pack crush and rock strike | Internal target: 75 mm half-cylinder to 100 kN (SAE J2464 practice); 50 mm impactor at 3 g bottom-out | 2 packs | No fire or explosion; no leakage after 1 h; dent <=12 mm | T2 safety; D08, D07 | prototype | $150,000 | 6 |
| V20 | Pack case crash retention (20 g) | Sled pulse test with dummy cells | 2 cases | Seams intact; no cell exposure | T2 safety; D07 | prototype | $60,000 | 4 |
| V21 | Pack IP67, immersion and hot-into-cold wading | IEC 60529 IP67; hot pack 40 C into 10 C water | 2 packs | No ingress; isolation held; no fire in salt immersion | T2; D15, D20 | prototype | $70,000 | 4 |
| V22 | Inlet and cable thermal soak at 137 A | J3400 / UL 2251 style temperature rise | 2 sets | Rise <=50 K at 40 C ambient for 30 min; no hot spots | T6; D37 | component | $30,000 | 3 |
| V23 | Charging interoperability and conformance | DIN SPEC 70121 / ISO 15118-2; SAE J3400; J1772 pilot states | 3 bikes, >=6 station models | Complete sessions at >=80% of stations; AC/DC interlock never allows both closed | T6; D38, D39 | prototype | $120,000 | 8 |
| V25 | Cooling loop bench and radiator ram-air check | Flow bench; wind tunnel ram factor | 2 loops | 74 kPa at 22 L/min; ram factor >=0.25; pump endurance 2,000 h | T4; D13, D40 | component | $60,000 | 4 |
| V26 | Hose, manifold and ribbon burst and leak | Pressure test at 3x working | 6 sets | No leak at 3x; no pinholes after vibration | T2 safety; D40, D41 | component | $20,000 | 2 |
| V30 | Frame static proof and stiffness | Hydraulic rig; load cases C1-C6, D1-D3 | 2 frames | No yield; lateral >=1.5 kN/mm target or documented waiver; torsion >=3 kNm/deg | T1;T8; D33 | prototype | $90,000 | 6 |
| V31 | Frame and arm multi-axial fatigue to 1.5 lives | Road-load replay plus drive spectrum | 2 chassis | No crack after 1.5 x 160,000 km equivalent; bolt preload loss <10% | T1;T8; D28, D29, D26, D31, D32 | prototype | $350,000 | 16 |
| V32 | Modal survey and wobble/weave check | Impact hammer, shaker | 1 chassis | Frame modes >=2 Hz from wobble/weave and motor orders | T8; D33 | prototype | $40,000 | 2 |
| V33 | 125 mph and 130 mph sustained at 25 C and 38 C | Climatic chassis dyno | 2 bikes | 25 C: 125 mph held, cell <55 C; 38 C: derates to about 105 mph, cell <60 C, EMRAX inlet within limit | T4; D13, D21 | prototype | $200,000 | 6 |
| V34 | DC fast charge 10-80% at -10, 25, 35, 45 C | SAE J3400 station or emulator | 3 bikes | <=25 min at 25 and 35 C; cold with preheat <=25 min; cell <55 C | T6; D12, D14 | prototype | $150,000 | 5 |
| V35 | Coastdown and constant-speed range at 70 and 77 mph | SAE J2263 adapted; chassis dyno | 2 bikes | Range >=145 mi at 70 mph, 90 kg rider; measured CdA | T3 | prototype | $80,000 | 4 |
| V36 | Wind tunnel CdA with rider | Full-scale tunnel | 1 bike | CdA <=0.38 m2 | T3 | prototype | $120,000 | 3 |
| V37 | Acceleration and top speed | GPS-instrumented | 2 bikes | 0-60 mph <=4.0 s; 125 mph sustained; 130 mph governor | T4;T5 | prototype | $50,000 | 3 |
| V38 | Weigh the bike wet, ready to ride | Calibrated scales | every prototype | <=260 kg (573 lb) | T1; D31 | prototype | $2,000 | 1 |
| V39 | Handling and high-speed stability, gusts at 77 mph | Proving ground | 2 bikes | Weave and wobble damping positive in all modes; rider rating >=4/5 | T8; D33 | prototype | $150,000 | 6 |
| V40 | Vehicle-level fault injection (throttle, VCU, ABS, 12 V loss) | Vehicle on rollers and track | 2 bikes | Safe state in every case; limp-home >=25 min | T8; D22, D36, D42, D43, D45 | prototype | $80,000 | 4 |
| V41 | Brake compliance pre-test, including high-speed stop | FMVSS 122 S6; 125 mph stop for design margin | 2 bikes | Dry stop limits met (front only 37.3 m, rear only 53.9 m from 60 km/h); fade ratio met; regen off for friction tests | T4; D34, D35 | prototype | $150,000 | 6 |
| V42 | ABS and regen blending on low-mu surfaces | Supplier calibration loops | 2 bikes | No wheel lock above 15 km/h; regen never reduces total deceleration below demand | T8; D35, D36, D46 | prototype | $200,000 | 8 |
| V43 | Tip-over and low-side slide | 10 falls each side; 30 and 50 km/h slide | 2 bikes | Pack never touches ground; isolation >=100 ohm/V; vent gas path clear | T2 safety; D04, D08 | prototype | $60,000 | 3 |
| V44 | Lighting photometry and installation; reflectors; stop-lamp logic | FMVSS 108 | 1 set | All lamps meet photometry and spacing; stop lamp on regen | T10; D44, D46 | pre-production | $60,000 | 4 |
| V45 | Mirrors, controls and displays, tyres and rims, glazing, brake fluid audit | FMVSS 111, 123, 119, 120, 205, 116 | 1 bike | All items meet the standard or a supplier certificate is on file | T10 | pre-production | $50,000 | 4 |
| V46 | Vehicle EMC and radio | UN R10 practice; FCC Part 15 | 1 bike | Emissions and immunity under limits; keyless and telematics grants | T8 | pre-production | $150,000 | 6 |
| V47 | Climate, altitude and wading trips | Hot, cold, 4,000 m; 450 mm wading | 2 bikes | No faults; isolation held after wading | T8; D15, D20 | pre-production | $120,000 | 5 |
| V50 | Durability fleet: road and gravel | 3 bikes x 30,000 km (reduced from the earlier plan) | 3 bikes | No structural or HV fault; wear within limits; pyro false trips logged | T1;T8; D32, D19, D45 | pre-production | $450,000 | 30 |
| V51 | Pre-production confirmation (brakes, lighting, EMC, charging) | Repeat key tests on production-intent bikes | 5 bikes | Results match prototype within tolerance | T1-T10 | pre-production | $300,000 | 12 |
| V52 | US certification file: Part 565 VIN, 566 registration, 567 label, FMVSS self-certification | 49 CFR 565, 566, 567, 571 | 1 file | Complete file; label and VIN pad on the frame | US launch | pre-production | $60,000 | 8 |
| V53 | Semi-active steering damper fail-safe (added Nov 22; not in the US total) | Bench and vehicle: sensor loss, power loss, valve stuck, controller reset | 3 dampers, 1 bike | Defined fail-safe state holds; warning shown; no wobble divergence at 15-85 mph in the failed state | T8; D48 | pre-production | $40,000 | 4 |

### Hardware builds and EU add-on

| ID | Line | Samples | Phase | Est. cost | Weeks |
|---|---|---|---|---:|---:|
| HW1 | Prototype hardware: 3 hand-built mules | 3 bikes | prototype | $450,000 | 20 |
| HW2 | Test packs (beyond the ones in bikes) and modules | 12 packs, 6 modules | prototype | $264,000 | 24 |
| HW3 | Pre-production builds: 8 bikes on soft tooling | 8 bikes | pre-production | $760,000 | 16 |
| EU1 | EU add-on: UN R136 REESS tests (vibration, thermal shock, mechanical shock, short, overcharge, over-discharge, over-temperature) | 3 packs | EU add-on | $450,000 | 16 |
| EU2 | EU add-on: R78 braking, R53 lighting, R10 EMC witnessed tests, R81 mirrors, R41 noise | 2 bikes | EU add-on | $450,000 | 16 |
| EU3 | EU add-on: L3e-A3 type approval, technical service, CoP | 1 file | EU add-on | $350,000 | 16 |

All status fields in the CSV read **planned**. There are no result or date columns because nothing has been run.

## Build-and-test timeline (weeks from go, about 28 months)

| Weeks | What happens |
|---|---|
| 0 to 6 | V08 steel-yoke proof; V15 hazard analysis starts; V01 cell tests start; V03 and V04 vent and bond tests |
| 6 to 30 | Component rigs: V02 propagation, V05, V06 arm, V07 pivot, V09 belt, V10 dyno, V11 brake dyno, V13, V14, V22, V25, V26. Decision gate at week 14: yoke, pivot, vent and brake size confirmed, then freeze CAD for the mules |
| 12 to 32 | HW1: build three mules (20 weeks); HW2 test packs |
| 30 to 70 | Prototype tests: V16 to V21, V23, V30 to V43; V17 (UN 38.3) must finish before packs travel; V31 fatigue runs 16 weeks |
| 60 to 76 | HW3: eight pre-production bikes on soft tooling |
| 70 to 112 | V44 to V47, V50 (30 weeks, 3 bikes x 30,000 km), V51 confirmation |
| 108 to 118 | V52: US self-certification file, Parts 565, 566, 567 |
| After 118 | EU1 to EU3, about 16 weeks, only if the EU market is pursued |

Critical path: V01 cell data, V02 propagation, V17 UN 38.3, pre-production build, V50 durability, V52 filing. A failure of V08 (yoke) or V02 (propagation) re-opens the design and moves everything after it.

## What this does not prove

- Nothing here has been tested; every status is "planned". All costs and durations are planning estimates scaled from the Nov 12 study (a heavier bike with an EU launch), not quotes from a lab, track or technical service. I contacted no one.
- The headline excludes engineering salaries, tooling, fees outside the listed filings, insurance, facility build-outs and contingency beyond the 0.7x to 1.5x range. The earlier plan (about $10.9M, with EU approval, 24 packs, 12 DV2 bikes and 4 x 40,000 km fleets) is not directly comparable.
- Acceptance numbers come from the target documents and the earlier plan; some (V51 "within tolerance", the 2,000 h pump run) need the lab's own criteria. UN R136 and SAE J2464 procedures were not read in full.
- Sample counts are small (2 to 3 bikes, 1 to 4 packs). They support engineering decisions, not statistical reliability claims.
- No measured road-load data exist, so the 160,000 km spectrum in `09-structures.md` is still an assumption; real data may change V31.
