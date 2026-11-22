# Bavuso V1 DFMEA (design failure mode and effects analysis)

> **Superseded in part (Nov 22, 2026).** This document predates the final V1 numbers; the authority is `00-V1-final-spec.md`. Stale here: "already at its 240 kg limit" (final 257.9 kg, T1 <= 260 kg); D24 and D30 describe the EMRAX housing as the yoke (final: steel pivot yoke at Z545, see new row D47); D34 and the open item on 300 vs 320 mm (final 320 x 5 front, 267 x 5 rear); the steering damper listed as "not analysed" (semi-active damper analysed in `15-dynamics.md`, see new row D48). Rows D47 and D48 were added Nov 22 and are not in the counts above.


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Full table with causes, today's controls and detection: `program/data/dfmea-v1.csv` (46 rows). Generator: `program/tools/build-dfmea-dvpr.py`. Test links point to `14-dvpr.md` (`program/data/dvpr-v1.csv`). Inputs: `09-structures.md`, `10-thermal.md`, `07-electrical.md`, `06-drive-performance.md`, `02-hardware.md`, `12-compliance.md`.

## The plain answer

**The V1 design has 13 High-priority risks out of 46 rows, and none has been tested.** They cluster in three places: the battery pack's fire safety (cell short, propagation, vents, crash and rock strength), the single-sided arm and its belt loop (arm fatigue, pivot bearings, the motor-housing yoke, the stub joint, frame welds), and the brakes (125 mph stopping, regen with ABS). One more, active discharge after a crash, is a specification gap rather than a physics question.

**The most important open item is the yoke.** The structures study only closes if the EMRAX 228 housing carries the belt loop (11.3 kN design pull). EMRAX publishes no housing limit. If it cannot, the frame needs far more mass or the arm must move to the belt side (rows D24 and D30). Ask EMRAX first; it costs nothing and decides the chassis.

Method: AIAG-VDA style (severity S, occurrence O, detection D, each 1 to 10, then an Action Priority H / M / L). **All S, O and D scores are my engineering judgement on a paper design; there is no field or test data.** Detection scores are high (poor) because most controls are analysis only. The Action Priority uses a conservative approximation of the AIAG-VDA 2019 table written for this study (every severity 9 to 10 item with occurrence 4 or more and weak detection is High), not the licensed table; a reviewer should re-score against the handbook. Status "open" is used for High items (needs a design or test result), "needs test" otherwise.

## Summary by system

| System | Rows | High | Medium | Low |
|---|---:|---:|---:|---:|
| Pack | 14 | 5 | 7 | 2 |
| HV | 6 | 1 | 4 | 1 |
| Inverter | 3 | 0 | 1 | 2 |
| Motor/frame | 1 | 1 | 0 | 0 |
| Drive | 3 | 0 | 1 | 2 |
| Swingarm | 4 | 3 | 0 | 1 |
| Frame | 2 | 1 | 1 | 0 |
| Brakes | 3 | 2 | 0 | 1 |
| Charging | 3 | 0 | 1 | 2 |
| Cooling | 2 | 0 | 1 | 1 |
| Software | 2 | 0 | 2 | 0 |
| Lighting | 3 | 0 | 0 | 3 |
| **Total** | **46** | **13** | **18** | **15** |

## High-priority items (recommended action and test)

| ID | Item | Failure and effect | S | O | D | Recommended action | Test |
|---|---|---|---:|---:|---:|---|---|
| D01 | Cell (P60B 21700, 1,100) | Internal short leads to thermal runaway of one cell; Vent gas and heat; fire risk to rider | 10 | 4 | 6 | Single-cell trigger test on a lane module; set wire-bond size from pulse tests; cell lot incoming inspection | V01, V02, V04, V18 |
| D02 | Pack module barriers | Runaway spreads from one cell to neighbours; Whole pack fire, no time for rider to stop | 10 | 5 | 7 | Prove with trigger test (single cell, then group of 11) with and without coolant; adopt segmented ribbon in CAD; add propagation alarm (neighbour dT/dt) | V02, V03 |
| D03 | Burst vents and plenum | Vent too small, blocked or not opening at 15-20 kPa; Case over-pressure, rupture, jet toward rider | 10 | 4 | 7 | Design plenum and vents into CAD; burst-pressure and flow test; keep path clear of rider, pump and inlet | V02, V03 |
| D07 | Pack case front wall and seams | Seam or wall fails in a 20 g frontal crash (FEA 167 MPa vs 140 allowable at 4 mm); Pack shifts or opens, cell damage in crash | 9 | 5 | 5 | Adopt 5 mm front wall and ribs; run cell-backed crash analysis; sled test of case | V19, V20 |
| D08 | Pack floor and skid | Rock strike dents case into cells; Cell damage, runaway, loss of isolation | 9 | 4 | 5 | Cell-backed crush analysis, then rock-strike test; keep 10 mm crush zone | V19, V43 |
| D17 | Active discharge (inverter bus) | Bus takes about 88 s to fall below 60 V (inverter bleed 70 kohm); Shock risk for rescuers after crash | 9 | 5 | 5 | Specify active discharge (below 60 V in 3 s) with Cascadia; measure | V13 |
| D24 | Motor housing as load-bearing yoke | EMRAX housing cannot carry the belt-loop load (11.3 kN design pull); Housing deformation, belt tension loss, or frame needs far more mass (tail rail 1,388 MPa without the yoke) | 9 | 6 | 6 | Ask EMRAX for housing and shaft loads; static proof of the housing under belt-loop load; decide belt-side arm option now if EMRAX declines | V08 |
| D28 | Cast A356 arm, brace bolt-on | Fatigue crack at brace bolt-on (damage about 4 unreinforced); Arm cracks, rear wheel alignment lost | 9 | 6 | 5 | Design boss and rib; casting NDT plan; fatigue test of full arm to 1.5 lives | V06, V31 |
| D29 | Pivot bearings (right side 80 mm span) | Overload or short life (43.6 kN in, 33.4 kN out at design; CAD span of 36 mm gives 85/74 kN); Bearing failure, pivot play, handling loss | 9 | 5 | 5 | Apply CAD change; bearing life calculation; pivot rig test at 1.2x design plus the 21 kN slider case | V07, V31 |
| D30 | Pivot stub to yoke joint (belt-side move open item) | Joint fatigue or slip where belt loop closes through stubs and motor housing; Loss of rear axle alignment; crack in stub | 9 | 5 | 6 | Design the joint; test with V07/V08; reconsider arm on belt side if it fails | V07, V08 |
| D32 | Tube welds (down-link, rails, headstock) | Weld fatigue crack (Miner D 0.40-0.49 vs 0.5); Frame crack, handling loss, possible separation | 9 | 5 | 5 | Rig test to 1.5 lives with crack monitoring; measure real road loads on a mule | V31, V50 |
| D34 | Front brake (dual 320 x 5 mm, Stylema) | Fade or insufficient stopping from 125-130 mph; Longer stopping distance, FMVSS 122 high-speed test fail | 9 | 5 | 5 | Brake dyno then vehicle high-speed stop; 320 mm adopted in rev E; confirm by dyno | V11, V41 |
| D35 | ABS and regen blending | Regen torque locks the rear wheel or reduces total deceleration; Rear wheel lock, fall | 9 | 4 | 5 | Calibrate on low-mu surfaces; regen off for the friction-only FMVSS 122 tests | V41, V42 |

## Medium-priority items

| ID | Item | Failure mode | S | O | D | Recommended action | Test |
|---|---|---|---:|---:|---:|---|---|
| D04 | Vent exhaust routing | Hot gas reaches rider, inlet or pump | 9 | 3 | 6 | CAD check of exit location in every tip-over pose; gas-jet test in propagation test | V02, V43 |
| D05 | Wire-bond links (2,200) and ribbons | Bond lift-off or fatigue under vibration | 7 | 4 | 6 | Shaker test (R136 8A profile) on modules with resistance monitoring; bond pull tests in production | V05 |
| D06 | Cell holders and lane structure | Cell moves or chafes against holder under shock | 8 | 4 | 6 | Shock/vibration test of modules; holder material and tolerance review | V05, V16 |
| D09 | Pack fuse and busbar | Short-circuit current (3.4-6.2 kA) not cleared safely; fuse I2t not checked | 9 | 3 | 6 | Select fuse from curve; bench short-circuit at pack voltage | V14 |
| D10 | BMS (Orion BMS2-108) | BMS fails to stop over-charge, over-discharge or over-temperature | 10 | 3 | 6 | Hazard analysis with ASIL for pack; add independent hardware over-voltage and over-temperature cut; HIL fault injection | V15, V17 |
| D12 | Cold charging (-10 C, 3 kW PTC) | Lithium plating from charging cold cells | 7 | 5 | 6 | Verify derate map and preheat on cold chamber; plating check by cell teardown | V01, V34 |
| D14 | P60B at 2C charging | Fast-charge cycle life lower than needed | 6 | 6 | 7 | Written cell charge-life data from Molicel; 1,000-cycle test with DC fast charge; P50B fallback (+9 kg) | V01, V34 |
| D15 | HV bus isolation | Isolation loss (water, chafe, coolant leak) | 10 | 4 | 4 | Isolation and ingress tests; routing rules for chafe | V13, V21, V47 |
| D16 | Contactors K1-K5 and HVIL | Contactor welded closed or HVIL loop open and undetected | 9 | 3 | 4 | Short-circuit and endurance of contactors at pack voltage | V13, V14 |
| D18 | Pyro cut-off | Does not fire on crash or hard fault | 9 | 2 | 6 | Fault injection and crash-pulse test of trigger chain | V14, V15 |
| D20 | Pack breathing and connectors in water | Hot pack drawn into cold water, water pulled past seals | 8 | 5 | 5 | Hot-into-cold wading and IP67 test; route vents high | V21, V47 |
| D22 | Torque control (CM200DX + VCU) | Unintended or excessive drive torque | 10 | 3 | 4 | Hazard analysis, ASIL assignment, HIL fault injection, vehicle fault tests | V15, V40 |
| D26 | Belt tracking with single-sided arm | Arm flexes (lateral 1.0 kN/mm) and belt walks off or jumps teeth | 7 | 5 | 5 | Measure belt tracking on rig and in road tests under lean and bump; confirm flange design | V09, V31 |
| D33 | Frame lateral stiffness 1.3 kN/mm | Below the 1.5 kN/mm target; weave or wobble at 77-130 mph | 7 | 5 | 5 | Modal and wobble test; adjust steering damper and trail; keep case at 4-5 mm | V30, V32, V39 |
| D38 | AC relays and K4/K5 | AC and DC paths closed at once | 9 | 2 | 5 | Fault-injection test of the interlock | V15, V23 |
| D41 | Hoses, manifolds and ribbons in pack | Coolant leak into pack or HV box | 9 | 3 | 5 | Burst and leak tests on ribbons, hoses and manifolds; add pack leak sensor | V13, V26 |
| D42 | Throttle (twist grip sensors) | Throttle sensor fault, stuck torque request | 10 | 3 | 4 | Hazard analysis; HIL and vehicle tests | V15, V40 |
| D43 | VCU, CAN1/CAN2 | VCU or CAN fault: torque lost or held | 9 | 3 | 4 | Safe-state design (torque to zero within the fault tolerant time); HIL | V15, V40 |

## Low-priority items

| ID | Item | Failure mode | S | O | D | Test |
|---|---|---|---:|---:|---:|---|
| D11 | BMS sense harness (100 sense wires) | Sense wire open or high-resistance | 8 | 4 | 4 | V05 |
| D13 | Hot-day 125 mph (38 C) | Cell reaches 60.9 C (limit 60 C) | 8 | 4 | 4 | V25, V33 |
| D19 | Pyro cut-off | False trigger at speed | 7 | 3 | 4 | V15, V50 |
| D21 | CM200DX inverter | Overtemperature at coolant 65 C (limit is an estimate) | 6 | 4 | 4 | V10, V33 |
| D23 | LV+43% winding, 650 A peak | Inverter overcurrent trip at low-SOC high power | 7 | 4 | 4 | V10 |
| D25 | Gates 8 mm belt | Belt breaks or tooth shear | 8 | 4 | 4 | V09 |
| D27 | 35T motor pulley and 126T rear pulley | Pulley fatigue, fretting or bolt loosening (30 m/s, 220 Nm) | 8 | 3 | 5 | V09 |
| D31 | Cross brace and shock force path | Little margin: SF 1.22 on rear bump (required 1.2), falls to 1.18 at 255 kg | 8 | 4 | 4 | V31, V38 |
| D36 | ABS unit and sensors | Loss of ABS function | 8 | 3 | 4 | V40, V42 |
| D37 | NACS inlet and 35 mm2 cables at 137 A | Connector or cable overheats during 20 min DC charge | 8 | 3 | 4 | V22 |
| D39 | EVCC and J3400 session | Session fails or no Supercharger authorisation | 4 | 7 | 5 | V23 |
| D40 | Coolant pump (22 L/min, about 74 kPa) | Pump failure or loss of flow | 8 | 4 | 3 | V25, V26 |
| D44 | Front indicators and light band (FMVSS 108) | Lamp spacing and photometry do not comply (rev C fails; V1 design unchecked) | 7 | 5 | 3 | V44 |
| D45 | 12 V supply (DC-DC and 4.5 Ah battery) | DC-DC failure; 12 V battery flat after parking | 8 | 3 | 3 | V40, V50 |
| D46 | Brake lamp logic under regen | No brake lamp when regen slows the bike | 7 | 5 | 4 | V42, V44 |
| D47 | Steel pivot yoke (rev E, cross-member Z545, welded to cast nodes; replaces D24 and D30 load path) | Yoke weld or section fatigue/yield under the 11.3 kN belt pull, or stiffness shortfall; Rear axle misalignment, belt tension loss, frame crack, handling loss | 9 | 5 | 5 | Static and fatigue rig on the yoke; re-run FEA at 257.9 kg with the cross-member at Z545 (09 Round 2 ran at 240 kg scaling); confirm weld class | V08, V07, V31 |
| D48 | Semi-active steering damper (speed-scheduled, about 0.5 kg, Ohlins EC class) | Controller, valve or speed-signal fault leaves the damper unscheduled; Without scheduled damping wobble is unstable at 15-85 mph (zeta down to -0.15); a fixed stiff setting takes weave at 130 mph to zero | 9 | 4 | 5 | Define the fail-safe state with the supplier (proposal: fixed medium damping plus a speed limit near 85 mph), dash warning, fault-injection test | V53 |

## Open design items this table depends on

1. **Yoke and belt side (D24, D30).** Structures assumes the EMRAX housing and the two pivot stubs form one load path. Decision gate: EMRAX written answer plus test V08. Fallback: arm on the belt side or a motor-in-pivot casing, which changes CAD and mass.
2. **Pack vents and barriers (D02, D03).** Four lane vents of at least 600 mm2, slotted ribbon and wire-bond links are specified in `10-thermal.md` but not yet in CAD.
3. **Pivot (D29).** The CAD change (62 mm stub, 80 mm span, about 50 mm tapered rollers) is in `09-structures.md` and has not been applied.
4. **Active discharge (D17).** Must be specified with Cascadia; the inverter's own bleed takes about 88 s.
5. **Front brake size (D34).** 320 x 5 mm front and 267 x 5 mm rear are adopted (CAD rev E); confirm with the brake dyno.

## What this does not prove

- No row has field, test or supplier failure-rate data behind it. Occurrence scores are judgement; they rank, they do not predict.
- The list is not exhaustive: the fork, triple clamps, axles, wheel bearings, stands, dash software, keyless and cybersecurity are not analysed (the structures study did not model them either).
- This is a design FMEA only. There is no process FMEA (cell assembly, welding, casting), no hazard analysis and no FMEDA, so the ASIL levels in `12-compliance.md` are proposals.
- Action priority is an approximation of the AIAG-VDA table, not the licensed table.
- Mitigations marked "planned" are not in the CAD or the mass ledger; some add mass (5 mm front wall, ribs, bearings) on a bike that is already near its 260 kg limit (257.9 kg final).
