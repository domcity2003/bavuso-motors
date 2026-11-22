# Bavuso V1 drive and performance

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Scripts: `program/tools/drive-lib.py` (models), `drive-design.py`, `drive-performance.py`, `drive-range.py`, `drive-charge.py`. Results: `program/data/drive-design.json`, `drive-performance.json`, `drive-range.json`, `drive-charge.json`, `drive-accel-trace.csv`. Run each from `v1.0` with FreeCAD python.
Labels: **supplier** = published datasheet, **calc** = computed from supplier numbers, **est** = my estimate.

## Final V1 update (Nov 22, 2026, US Central)

Re-run by Claude Sonnet 5.5 (claude-sonnet-5-5) at the final roll-up of **257.5 kg / 568 lb** (the ledger kept ticking up while the work ran: it was 257.3 kg, then 257.5 kg, and reads 257.9 kg / 569 lb at the end; the drive figures were run at 257.5 kg, and the extra mass changes 0-60 and range by less than 0.05 s and 0.2 mi), rider 90 kg, so 347.5 kg on the road. **The sections below are the Nov 21 text at 240 kg and are kept as history; where they differ, this section wins, and `00-V1-final-spec.md` is the authority.** Scripts and data files were re-run and overwritten (`drive-design.py`, `drive-performance.py`, `drive-range.py`, `drive-charge.py`; `drive-lib.py` now has the final mass, a 350 A DC cap, wheelbase 1,490 mm and CG 732 / 667 mm). Everything here is a calculation or an estimate; nothing is built, weighed or tested.

**Three inputs changed besides mass.** (1) The BMS discharge cap is now **350 A**, the contactor and VCU limit in `07-electrical.md` (was 400 A here, which the contactors do not allow). (2) Wheelbase 1,490 mm and CG 732 / 667 mm (bike plus rider, rev D per `15-dynamics.md`) replace the old 1,480 mm and 738 / 643 mm; these affect only the grip and wheelie caps, not 0-60, which is torque-limited. (3) The charge headline is one figure (see below). Not changed: CdA 0.38 (**assumed, unmeasured**), Crr 0.015, 300 W auxiliaries, flat still air.

| Quantity | Nov 21 (240 kg, 400 A) | **Final (257.5 kg, 350 A)** |
|---|---|---|
| 0-60 mph | 3.95 s | **4.15 s** (4.44 s with 25 kg luggage; 5.47 s wet, mu 0.7) |
| 0-100 km/h / 0-100 mph | 4.10 / 6.91 s | **4.31 / 7.26 s** (SOC 90, 25 C) |
| 60-100 mph roll-on | 2.96 s | **3.12 s** |
| 0-100 mph at SOC 10 / 5 | 6.96 / 7.09 s | **7.48 / 7.69 s** (the 350 A cap costs time at low charge) |
| Range at 70 mph, CdA 0.38 | 154 mi | **152.4 mi** (146 Wh/mi) |
| Range at 77 mph, CdA 0.38 | 133 mi | **132.2 mi** (169 Wh/mi) |
| Range at 125 mph | 57 mi | **56.9 mi** |
| Range with 25 kg luggage, 70 / 77 mph | 152 / 132 mi | **150.9 / 130.9 mi** |
| Range at CdA 0.43, 70 / 77 mph | 140 / 121 mi | **138.8 / 119.8 mi** |
| Top speed | 135 mph (6,500 rpm limit) | **135 mph, unchanged** (governed at 130 mph; power-limited peak 178 mph) |
| Wheel power at 125 / 130 mph | 43.3 / 48.5 kW | **43.5 / 48.7 kW** |
| Peak shaft power, 25 C, at 350 A: SOC 100 / 50 / 20 / 10 / 5 | 124 / 122 / 111 / 103 / 96 kW | **124 / 109 / 100 / 93 / 87 kW** |
| Peak shaft power, 5 C: SOC 100 / 50 / 20 / 10 / 5 | n/a | **115 / 99 / 86 / 83 / 81 kW** |
| DC fast charge 10-80%, 25 C | 15.5 min (3C cap) | **about 21 min** (see below) |

**PENDING AERO, currently calculated at assumed CdA 0.38: 152.4 / 132.2 mi at 70 / 77 mph.** T3 (at least 145 mi at 70 mph) holds with a 5% margin at CdA 0.38 and fails above a break-even CdA of about **0.407** (0.405 gives 145.4 mi, 0.41 gives 143.9). No CdA has been measured or computed for V1; `17-aero.md` is pending. Real-world range is 15 to 20% lower than calculated (about 120 to 130 mi at 70 mph with wind, hills and cold). The Gate A flat-90%-efficiency model gives 149.7 / 128.6 mi.

**Power at low charge, honestly.** With the 350 A cap this model gives 93 kW at 10% SOC and **87 kW at 5% SOC at 25 C**, below T5's 90 kW; `07-electrical.md`'s separate hand model gives 96 kW at 10%. Both are models. At 5 C the bike is below 90 kW at 20% SOC and lower (86 kW or less). Treat T5 as met above about 10% SOC at 25 C and not met on a cold, nearly empty pack unless it is pre-warmed. Continuous power is unchanged (61.6 kW at 5,500 rpm, inverter-limited; below 56 kW under 103 mph). The 125 mph sustained case is unchanged: 27.4 min and 57 mi, pack 46 C at 25 C ambient; at 38 C the pack reaches 56.7 C and `10-thermal.md`'s more detailed model (hottest core 60.9 C, derate to about 105 mph) overrides this model's "marginal".

**One charge-time headline: about 21 minutes for 10-80% DC at 25 C ambient, with the charge current capped at 2C per cell (12 A per cell, about 137 A at the pack, 51 kW average, 54 kW peak), on NACS V3 or any 150 kW-or-better DC station.** This script gives 21.0 min; the independent hand model in `07-electrical.md` gives 20.2 min at 12.5 A per cell. Gate A's "about 20 min" is the same figure rounded; the target is 25 min or better. I use the 2C cap because the P60B datasheet (version 0.1) gives a 5C maximum but no cycle life above 2C. The faster numbers quoted earlier (15.5 min at a 3C cap in this document, 17.1 min in `10-thermal.md`) assume the unconfirmed 3C charge life and are **not claimed**. Other conditions, from `10-thermal.md`, which uses the 3C-cap profile: 23.0 min at 35 C, 25.4 min at -10 C with the 3 kW heater (14.0 min if pre-heated on the ride in), 40.9 min at 45 C, and 27.4 min at 35 C if the bike arrives hot at 42 C. **Open inconsistency:** `10-thermal.md` row 13 shows the 2C cap at 35 C takes 27.4 min, so the 25-minute claim at 35 C holds only if the cell is trusted to 3C. AC (booked unit, BROGEN 6.6 kW, 94% efficient): **2.7 h for 10-80%, 3.5 h for 10-100%**; at 3.3 kW it would be 5.5 h and 7.0 h; a 120 V outlet is not supported by the BROGEN class unit (see `07-electrical.md`).

**Parts that changed names or values since this document was written:** drive mass is **23.65 kg** in the ledger (motor 13.2 kg, not the 13.5 kg used here; carrier 0.4 kg and others added), the motor winding is **LV+43%** (the ledger and CAD solid names "HV" and "MV" are stale labels), and the HV cable and fuse values are in `07-electrical.md`, "Final values". The line "CAD change request 9" (35 mm2 cable, 400 A cap, 450 A fuse) is superseded by that table.

## The plain answer

**The drive works and meets T3 to T6 on paper, with three conditions.** It is an EMRAX 228 liquid-cooled motor (LV+43% winding) on a Cascadia CM200DX inverter, a single 8 mm Gates belt at 3.60:1, and the P60B 100s11p pack.

| What | Result |
|---|---|
| 0-60 mph / 0-100 km/h / 0-100 mph | **3.95 s / 4.10 s / 6.9 s** (torque-limited, same at any charge level) |
| 60-100 mph roll-on | **3.0 s** |
| Top speed | **135 mph, limited by the motor's 6,500 rpm, not by power**; governed at 130 mph |
| 125 mph sustained | **Passes at 25 C ambient** (pack 46 C, motor winding 80 C of 100 C). Marginal at 38 C (pack 57 C) |
| Range at 70 / 77 mph | **154 / 133 mi** with the real efficiency map (Gate A flat-90% model says 151 / 130) |
| DC fast charge 10-80% | **15.5 min** on NACS or any 80 kW+ CCS1 at 25 C; 20 min at 35 C |
| AC 10-80% | 5.5 h at 3.3 kW, 2.7 h at 6.6 kW |
| Drive mass | **23.1 kg** (budget 23 kg) |

The three conditions: (1) range passes only while CdA stays at or below about 0.41; (2) on a hot day, 125 mph for the full pack pushes the pack to about 57 C, so the cooling loop needs a bigger radiator or the bike must back off; (3) peak power at low charge in the cold drops to 80-86 kW (below T5's 90 kW) unless the pack is pre-warmed.

## 1. Parts and the reasons

### Cell: Molicel P60B (supplier, data sheet version 0.1)
| Item | Value |
|---|---|
| Capacity / voltage / energy | 6.0 Ah typical (5.85 min) / 3.6 V nominal / 21.6 Wh |
| Resistance | 12.8 mohm DC at 50% SOC, 6.5 mohm AC at 30% SOC |
| Discharge | 60 A max (90 C cut-off), 100 A pulse (3.0 V cut-off) |
| Charge | 6 A standard, **30 A maximum (5C)** (70 C cut-off), -20 to 60 C |
| Mass | 75 g max |

Pack 100s11p: 360 V nominal (3.6 V), 250-420 V, 23.76 kWh, 66 Ah, 116 mohm of cells (12.8 mohm x 100 / 11) plus an estimated 8% interconnect and 6 mohm fuse and contactors, about 125 mohm total at 50% SOC. At 400 A that sags about 50 V, and more at low SOC. **The datasheet is version 0.1** and I could not read the 5C cycle-life curve from the file; get P60B charge-life data in writing before relying on 5C.

### Motor: EMRAX 228, liquid cooled, LV+43% winding (supplier, datasheet v1.7)
Only the LV+43% winding lists **360 V for peak power**, which matches a pack that is 330-420 V open-circuit and about 290-380 V loaded.

| Winding | Needs for peak | Peak current | Peak power at 330 V loaded (model) | Verdict |
|---|---|---|---|---|
| HV | 830 V | 235 A | 52 kW | no |
| MV | 630 V | 360 A | 85 kW (model only, beyond datasheet) | no: datasheet corner is at 630 V |
| LV | 250 V | 920 A | 121 kW but only 178 Nm on a 740 A inverter, 72 Nm continuous | no |
| **LV+43%** | **360 V** | **650 A** | **135 kW model, 124 kW datasheet cap** | **yes** |
| LV+100% | 500 V | 460 A | 102 kW | no |

LV+43%: 220 Nm peak, 124 kW peak (30 s), 118 Nm / 68 kW continuous liquid-cooled, 6,500 rpm, 13.5 kg, IP66, Kt 0.34 Nm/A, 2.55 mohm, 21 uH. Liquid (LC) rather than combined (CC): CC needs about 0.4 m3/min of air per kW, which a bike cannot give at low speed, and LC is the sealed IP66 version an adventure bike wants (+0.3 kg).

### Inverter: Cascadia CM200DX (supplier, cascadiamotion.com)
200-480 V operating (500 V trip), **300 A rms continuous, 740 A rms peak (30 s)**, 225 kW, 6.75 kg.
- Needs: 650 A peak (motor) < 740 A. Full pack 420 V, regen to 432 V, 5% SOC under 400 A 253 V: all inside 200-480 V.
- **The shortlist pick fails.** The emDrive H100 "150/450" tops out at 450 A (needs 650 A), its voltage class is not published anywhere I could reach (the datasheet host blocks automated download and the part is not on Poclain's current page), and Poclain's 400 V-class H20B is 12-420 V and 400 A. A 420 V pack at full charge sits on that limit with no margin. Rejected on current alone.
- Continuous torque is inverter-limited: 118 Nm x 300/330 = **107 Nm**.

### Ratio and belt (Gates Poly Chain GT Carbon 8MGT, design manual pp. 52-55, 103-106)
- Rear tyre 150/70R17 (shortlist). Free diameter 641.8 mm (calc); rolling radius 0.3145 m at low speed, 0.319 m at 130 mph (est, -1.5%/+1.5% moves speed by the same percentage).
- **Ratio 3.600 (35T on the motor, 126T on the wheel).** 130 mph is 6,262 rpm (96% of the limit). Higher ratios gain little (3.7 is 0.1 s quicker) and push 130 mph to 99% of rpm limit.
- **14 mm pitch is out:** its smallest sprocket (28T, 125 mm) runs at 42 m/s at 6,500 rpm; Gates limits stock sprockets to 6,500 fpm (33 m/s). 8 mm pitch 35T runs at 30 m/s.
- **Belt: 8MGT-1760-62 (220 teeth, 62 mm).** 62 mm is needed: a 36 mm belt caps motor torque near 157 Nm and 0-60 goes to 5.6 s.
- Service factor **1.5 on peak torque** (Gates Table 5, inverter-controlled AC motor, intermittent service, with shock and regen reversal). Capacity margin 1.34-1.54 over 500-6,500 rpm.

| Drive spec | Value |
|---|---|
| Motor sprocket | 35T 8MGT, pitch dia 89.13 mm, OD 87.7 mm, face 68 mm, bolt-on flanges OD about 99.7 mm, 0.46 kg |
| Rear sprocket | 126T 8MGT, pitch dia 320.86 mm, OD 319.5 mm, face 68 mm, flange OD about 331.5 mm, 1.87 kg |
| Centre distance | stock belt gives **545.9 mm**; CAD pivot to axle is **545.6 mm** (0.3 mm apart) |
| Belt | 8MGT-1760-62, 0.50 kg; wrap 155.5 deg on the small sprocket, 15 teeth in mesh |
| Belt speed at 6,500 rpm | 30.3 m/s (5,971 fpm, limit 6,500) |
| Drive mass | motor 13.5 + inverter 6.75 + belt 0.50 + sprockets 2.33 = **23.1 kg** |

### Belt tension and bearing loads (for CAD and FEA)
Gates formulas 14, 17, 18 and Table 11. Pull is the vector sum of tight and slack side.

| Case | Effective tension | Tight / slack | **Belt pull on each shaft** |
|---|---|---|---|
| Continuous 118 Nm, 5,500 rpm | 2.65 kN | 3.5 / 0.85 kN | **4.3 kN** |
| **Peak torque 220 Nm (SF 1)**, also peak regen | 4.94 kN | 6.2 / 1.3 kN | **7.4 kN** |
| Design, SF 1.5 (shock, wheel hop) | 7.4 kN | 9.4 / 2.0 kN | **11.3 kN** (use as the static strength case) |

- **Install tension 3.05 kN per span** (formula 14 at peak torque; measure with a sonic tension meter). Static shaft load about 6.1 kN even when parked.
- Direction: along the line between the two shafts, +/-12.3 deg of span angle. Belt line drops 8.2 deg from the motor shaft (X540, Z350) to the rear axle (X0, Z271.9). On the motor pulley the pull points rearward and down; on the axle, forward and up.
- Centrifugal tension 0.06 kN per span at 3,000 rpm to 0.19 kN at 5,500 rpm.
- **The EMRAX shaft bearings (6206 | 3206) must not carry this.** EMRAX publishes no radial limit. The pulley needs its own two-bearing carrier on the motor flange, coupled to the rotor by a spline, and the rear hub needs the same 7.4 to 11.3 kN at the pulley plane.

## 2. Performance (bike 240 kg + rider 90 kg, CdA 0.38, Crr 0.015, rotating inertia included)

Model: time-stepped, motor torque from a dq voltage and current model calibrated to the datasheet's 124 kW at 5,500 rpm and 360 V corner (conservative: it carries EMRAX's own margin), pack with state-of-charge and temperature resistance, inverter and motor loss models, 400 A BMS cap, 124 kW motor peak cap.

| Case | 0-60 | 0-100 km/h | 0-100 mph | 60-100 | Lowest bus V | Peak DC A |
|---|---|---|---|---|---|---|
| SOC 90, 25 C | 3.95 s | 4.10 | 6.91 | 2.96 | 369 | 324 |
| SOC 50 | 3.95 | 4.10 | 6.91 | 2.96 | 328 | 365 |
| SOC 20 | 3.95 | 4.10 | 6.91 | 2.97 | 293 | 400 |
| SOC 10 | 3.95 | 4.10 | 6.96 | 3.01 | 270 | 400 |
| SOC 5 | 3.95 | 4.10 | 7.09 | 3.13 | 247 | 400 |
| SOC 20, 5 C | 3.95 | 4.10 | 7.04 | 3.09 | 254 | 400 |

- 0-60 is torque-limited (220 Nm gives 0.73 g), so it does not change with charge. With 25 kg luggage 4.24 s. On a wet road (mu 0.7) 5.46 s. Grip cap at mu 1.0 is 0.88 g and the wheelie cap is 1.15 g, so the bike will not lift the front at this torque.
- **Peak power with sag** (at 5,500 rpm, 25 C): 124 kW at SOC 100 and 80, 122 at 50, 111 at 20, 103 at 10, 96 at 5. At 5 C: 109 kW at SOC 50, 86 at SOC 20, 83 at 10, 81 at 5. The cold, low-SOC numbers are below T5's 90 kW.

### Top speed: speed-limited, not power-limited
| SOC | Power-limited, peak | Power-limited, continuous torque | Speed limit (6,500 rpm) | Top |
|---|---|---|---|---|
| 100 | 178 mph | 157 mph | 135 mph | 135 mph |
| 10 | 168 | 157 | 135 | 135 |
| 10, CdA 0.43 | 161 | 147 | 135 | 135 |

Power is not the limit at any charge level. Wheel power needed at CdA 0.38: 43.3 kW at 125 mph, 48.5 kW at 130 mph (54.5 kW at CdA 0.43).

### 125 mph sustained (full pack, 95% to 5%)
| | 25 C ambient | 38 C ambient |
|---|---|---|
| Duration / distance | 27.5 min / 57 mi | 27.8 min / 58 mi |
| Pack temperature at end | 46 C | **57 C** (my limit 55 C; cell rating 60 C) |
| Motor winding | 80 C (limit 100) | 93 C |
| Inverter case | 65 C | 77 C |
| Coolant | 41 C | 53 C |

Operating point at 125 mph: 69 Nm at 6,024 rpm, 204 A rms (68% of the inverter's 300 A), motor loss 1.9 kW, inverter loss 1.0 kW, pack loss 1.7-2.7 kW, cells at 12 A (2.0C), battery-to-wheel 92% (drivetrain only). With a radiator 40% smaller on a 38 C day the pack reaches 62 C. At 130 mph: pack 48 C (25 C) and 58 C (38 C).

### Regen
Max regen torque 220 Nm (same motor map); regen decel capped at 0.25 g on the rear wheel alone (rear-only grip, blended with the front brake and ABS). From 70 mph about **75% of the kinetic energy returns to the pack** (47 Wh, recovered 36 Wh; 65% at 95% SOC as the charge limit tapers; low-charge-rate limit of 3C per cell used). Regen is shut down below 0 C. These percentages are the model's, not measured, and ignore ABS blend losses.

## 3. Range (efficiency map, not 90%)
Pack energy 95% to 5% SOC, pack 25 C, 300 W auxiliaries, flat, still air.

| Speed | Range | Wh/mile | Wheel to battery |
|---|---|---|---|
| 55 mph | 214 mi | 104 | 81% |
| 65 | 171 | 130 | 84% |
| **70** | **154** | **145** | **85.4%** |
| **77** | **133** | **167** | **86.6%** |
| 100 | 86 | 260 | 88.5% |
| 125 | 57 | 394 | 88.1% |

At 70 mph the losses are: motor iron 5.1%, inverter 3.8%, auxiliaries 3.0%, belt 1.2%, pack 1.0%, motor copper 0.5%. Sensitivities at 70 / 77 mph: CdA 0.33 gives 171 / 148 mi; CdA 0.43 gives 140 / 121 mi; 25 kg luggage 152 / 132; pack at 5 C 153 / 132; iron loss 60% to 160% of my estimate gives 157-149 / 136-129; 500 W auxiliaries 151 / 131.

## 4. Charging
Cell limit used: 3C cap (18 A per cell, about 200 A pack), my thermal derating (zero at 0 C, half at 10 C, full 20-40 C, zero at 55 C), constant-voltage taper at 4.2 V per cell, stationary radiator 100 W/K (est).

| 10-80% DC | Time | Average / peak power | Peak cell current | Hottest cell |
|---|---|---|---|---|
| **NACS V3 or CCS1 150 kW, 3C cap, 25 C** | **15.5 min** | 70 / 77 kW | 18 A | 44 C |
| Same, 2C cap (if P60B is only trusted to 2C) | 21.0 min | 51 / 54 kW | 12 A | 39 C |
| Same, 4C / 5C cap | 13.8 / 13.0 min | 79 / 84 kW | 24 / 30 A | 46 / 48 C |
| 35 C ambient, 3C cap | 20.1 min | 53 / 74 kW | | 46 C |
| 5 C start, no pre-heat | 21.3 min | 51 kW | | 31 C |
| 5 C ambient, pack pre-heated to 20 C | 14.0 min | 78 / 82 kW | | 38 C |
| CCS1 50 kW (125 A) | 22.3 min | 48 kW | 11 A | 38 C |
| 10-90% / 10-100% (NACS, 3C) | 18.2 / 26.3 min | | | |

The bike never asks for more than about 80 kW at 3C, far below a 250 kW stall, and the cell (not the charger) is the limit. A 10-80% stop adds about 115 miles at 70 mph. The bike must implement the NACS or CCS1 handshake (DIN 70121 / ISO 15118) in its charge controller; that is not modelled.

AC (OBC at 94%): **3.3 kW: 5.5 h for 10-80%, 7.0 h for 10-100%; 6.6 kW: 2.7 h and 3.5 h; 1.4 kW (a 120 V outlet): 16.6 h for 10-100%.**

## 5. Verdicts

| Target | Verdict | Margin and condition |
|---|---|---|
| **T3** range at 70 mph >= 145 mi | **Pass, conditional** | 154 mi (6% margin). Fails if CdA is above about 0.41 (0.43 gives 140). Needs measured CdA. |
| **T4** 125 mph sustained, governed 130 | **Pass at 25 C; marginal at 38 C** | Power margin 2.4x; speed limit 135 mph; thermal passes at 25 C, pack hits 57 C at 38 C. Fix: larger radiator or a chiller. |
| **T5** >= 90 kW peak | **Pass; fails cold at low charge** | 124 kW at SOC 100-80; 96 kW at SOC 5 at 25 C; 81-86 kW at 5 C below SOC 20. Pre-warm the pack. |
| **T5** >= 55 kW continuous | **Pass, thin** | 61.6 kW at 5,500 rpm, inverter-limited (motor alone is 68 kW). Above 5,000 rpm (103 mph) it is >= 56 kW; at lower speed continuous power is lower (107 Nm). Depends on CM200DX holding 300 A rms in the bike's cooling. |
| **T6** DC 10-80% in <= 25 min | **Pass** | 15.5 min; 21 min even at a 2C cap; 20 min at 35 C. |
| **T6** AC 3.3 kW minimum | Pass | 5.5 h for 10-80%. |
| Drive mass 23 kg | Pass | 23.1 kg. |

## 6. CAD change requests (for the build-adventure.py owner)
1. **Motor:** EMRAX 228 **LC** LV+43% winding, 13.5 kg, 228 mm x 86 mm, shaft on the pivot axis (X540, Z350) as in the old EMRAX layout. Replace the IPM envelope.
2. **Sprockets, 8 mm pitch:** motor 35T pitch dia 89.13 mm (OD 87.7), rear 126T pitch dia 320.86 mm (OD 319.5). Old model had 20T/62T 14 mm: 89.1 mm and 276.3 mm, so the rear one grows by 44.5 mm. Face 68 mm, flange OD +12 mm over the OD. Motor sprocket flanges must be **bolt-on** (belt cannot pass a fixed flange without 33 mm of extra centre distance).
3. **Belt plane and width:** belt is **62 mm**, not 20 mm. With the 150/70R17 tyre half-width about 77 mm and a 12 mm gap, put the belt inner flange face at Y-89 and the outer face at about Y-157 (the old plane was Y-105 to -83). The belt-side swingarm arm's inner face must move from Y-116 to about Y-162, a 46 mm shift outward. **That collides with the peg reference (inner end Y-187)**: please re-check pegs and the arm sweep.
4. **Centre distance** 545.9 mm for the stock belt against 545.6 mm in CAD: keep the pivot and axle where they are, fit a +/-5 mm rear axle slider or eccentric for tension (Gates allows 0.8 mm tension allowance, 2.8 mm for installation if the flange is removed).
5. **Belt installation:** an endless belt cannot be fitted past a closed double-sided swingarm. Make the belt-side arm detachable at the pivot or make the swingarm single-sided.
6. **Pulley bearing carrier:** a two-bearing carrier on the motor flange carrying 7.4 kN peak (11.3 kN design) static and a spline to the rotor. Rear hub and axle sized for the same loads at the pulley plane. Reserve about 55 mm of extra shaft length beyond the 86 mm motor face for carrier and pulley.
7. **Inverter:** CM200DX envelope 330 x 188 x 97 mm, 6.75 kg, already in CAD; coolant about 12 L/min (shortlist figure, unverified). Phase cables to the motor must be 70 mm2 (or 2 x 35 mm2 using EMRAX's 2xUVW option), about 0.5 m.
8. **Rear tyre:** rolling radius is 0.3145 m for the 150/70R17. The CAD still has RR 325 mm (170/60R17 in service); the drive numbers assume the shortlist tyre.
9. **To the electrical owner:** the shortlist says a 35 mm2 HV cable for about 200 A peak. The BMS cap here is 400 A (36 A per cell, 0.6 of the 60 A rating) and 365 A flows at 0-60, so use 70 mm2 and a DC fuse of at least 450 A.
10. **To the cooling owner:** the shared loop sees up to 6 kW at 125 mph (pack 2.7, motor 1.9, inverter 1.0 kW). The model needs about 250 W/K of radiator at 56 m/s ram air and 100 W/K when parked for charging. On a 38 C day the single radiator plus no chiller reaches pack 57 C.
11. **To the suspension owner:** re-run `rear-kinematics.py`; the belt line changes because the rear sprocket radius grows from 138 to 160 mm.

## What this does not prove
- No supplier was contacted. The P60B datasheet is version 0.1 and I could not read its 5C cycle-life curve; the 5C charge rating is the cell's maximum, not a life guarantee.
- Cell open-circuit voltage curve, resistance scaling with charge and temperature, pack interconnect resistance, inverter losses, motor iron loss (1.2 kW at 5,500 rpm, calibrated only to the 96% peak efficiency), thermal conductances, coolant mass, the 55 C pack limit and the charge derating are **estimates**. A measured motor and inverter efficiency map is not available.
- The motor torque curve beyond the datasheet's 5,500 rpm corner is a dq model calibrated to that corner; EMRAX publishes no torque curve at 300 V. A MV-winding run with the same model also reaches 3.95 s, but the datasheet puts that winding's peak at 630 V, so I did not use it.
- Gates publishes belt ratings only to 4,000 rpm for these sprockets; 4,000 to 6,500 rpm is a **linear extrapolation** of effective tension. Gates Design Flex Pro or Gates application engineering must confirm the belt at 6,262 rpm and 7.4 kN. The 1.5 service factor is my choice.
- CM200DX's 300 A continuous rating depends on coolant temperature and voltage (the supplier page says so but gives no curve). The thermal check assumes it holds.
- The centre of gravity (for wheelie and grip limits) is from the old 283 kg roll-up, not the 240 kg bike. Tyre rolling radius is an estimate. Regen blending with ABS, the NACS handshake, noise, belt life, tyre-belt clearance and the measured CdA were not checked. No FEA or bench test was done.
- Hot-day pack temperature depends on a radiator conductance I assumed; the real figure comes from the cooling design.
