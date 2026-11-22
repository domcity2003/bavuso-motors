# Gate A: V1 targets locked

November 21, 2026, US Central. Decided by Claude Opus 5.5 (program lead), on the owner's instruction to complete V1. The evidence is in `01-targets.md`, `02-hardware.md` and `03-mass-ledger.md`. The owner can revise these targets later.

## The plain answer
**V1 is a 240 kg (529 lb) solo adventure-touring EV.** It does about 150 miles at 70 mph, reaches 125+ mph, and charges 10–80% in about 20 minutes on native NACS.

It replaces the brief's "under 400 lb + 200 mi" targets, which cannot both be met:
- At 400 lb the bike carries about 11 kWh, enough for roughly 74 miles.
- 200 miles needs about 32 kWh and a 631 lb bike.

The chosen point matches the BMW R 1300 GS (523 lb). It is lighter than the Energica Experia (573 lb) and the Zero DSR/X (544 lb).

## Locked targets (V1 design requirements)
| # | Target | Value |
|---|---|---|
| T1 | Wet mass, ready to ride, no rider | **≤ 240 kg / 529 lb**, including a 12 kg (5%) margin |
| T2 | Pack | Molicel P60B 21700, **100s11p**. 1,100 cells, about 23.8 kWh gross, about 21.4 kWh usable, 370 V nominal; pack ≤ 103 kg |
| T3 | Range at 70 mph, flat, still air, 90 kg rider | **≥ 145 mi**, about 150 mi at CdA 0.38 m². CdA target ≤ 0.38 m² with the rider |
| T4 | Top speed | **125 mph sustained**, governed at 130 mph |
| T5 | Power | **≥ 90 kW peak, ≥ 55 kW continuous**: EMRAX 228-class axial-flux motor plus a matched inverter, single-stage belt drive. EMRAX 188 (60 kW) rejected as too thin for a premium bike |
| T6 | Charging | Native NACS inlet, DC 10–80% in **≤ 25 min**, about 20 min target. AC onboard charger 3.3 kW min (6.6 kW preferred if the mass fits) |
| T7 | Load case | **Solo** rider 90 kg (95th-percentile male design case) plus 25 kg luggage. Two-up is a later variant |
| T8 | Comfort and stability | Upright posture, seat about 830 mm, comfort and gust stability at 77 mph. Weave and wobble damping positive in all modes |
| T9 | Cost | Unit cost **≤ $32k at 10k units/year**, MSRP about $45k (premium) |
| T10 | Look | Freeze the appearance direction: beak, slim light band, clear screen, narrow waist, sculpted saddle, matte black. Clean up the battery cover, side pods and tail as one family |

## Mass budget by system (kg)
| System | Budget | Today (reconciled) |
|---|---|---|
| Battery pack | 103 | 131.1 |
| Chassis (frame, swingarm, subframe, shock mount) | 18 | 34.9 |
| Running gear (fork, shock, wheels, tires, brakes, ABS, controls, stand) | 37 | 44.9 |
| Drive (motor, inverter, belt, pulleys) | 20 | 23.6 |
| Electronics (charger, DC-DC, BMS, junction box, VCU, lights, display) | 18 | 24.5 |
| Body and protection | 15 | 30.8 |
| Cooling | 6 | 8.6 |
| Wiring, fasteners, fluids | 11 | 27.7 |
| **Margin** | **12** | — |
| **Total** | **240** | **~320** |

## Main risks carried forward
1. **P60B fast-charge rating:** the 2C-or-better charge rate is unconfirmed. Fallback: P50B (+9 kg), at the cost of some margin.
2. **Inverter:** voltage class and mass are to be confirmed against the supplier datasheet.
3. **Chassis at 18 kg:** this halves today's structure. The solo load case and the smaller pack are what make it possible, and FEA must prove it.
4. **Estimates:** most chassis and body masses are still estimates until the parts are designed.

## Decision log
- **Nov 21: inverter.** The inverter is the Cascadia CM200DX (6.75 kg), driving an EMRAX 228 with the LV winding. The emDrive H100 gives only about 29 kW continuous on this 360 V pack (`07-electrical.md`). The drive budget rises from 20 to 23 kg and the margin falls from 12 to 9 kg (3.75%). The total stays at 240 kg.
- **Nov 21: nominal voltage.** The pack nominal is 360 V (P60B 3.6 V per cell), not 370 V.
- **Nov 21: hot-day top speed.** Sustained 125 mph is required at 25 °C ambient. On a 38 °C day the pack reaches about 57 °C, which is still under the cell's 60 °C limit, so V1 has no chiller. A hot-day derate is allowed. Drive is final: ratio 3.60, 8 mm Gates belt, 23.1 kg (`06-drive-performance.md`).
- **Nov 21: thermal (`10-thermal.md`).**
  - **Hot days:** 125 mph sustained at 25 °C. At 38 °C, full speed is allowed for about 10 min, then the bike derates to about 105 mph for the rest of the pack. Correcting the Gate A note above: the cell would reach 60.9 °C without the derate.
  - **Cold charging:** keep the 3 kW PTC heater. Preheat is triggered when the rider navigates to a charger (14 min at −10 °C), so no heater mass is added.
  - **Cooling mass:** a wax thermostat replaces the 4-port valve. The 1.1 kg of pack ribbons and manifold coolant is booked to the pack, so cooling comes to about 5.7 kg against its 6 kg budget.
  - **Radiators:** rev C halves kept.
