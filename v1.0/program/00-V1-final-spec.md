# Bavuso V1: final spec sheet (single source of truth)

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program. Built from the independent review (`19-independent-review.md`, `data/review-number-table.csv`) and the final ledger, BOM, drive re-run, CAD rev E and cost model.

**Everything here is analysis or estimate. Nothing is built, weighed or tested.** If another document disagrees with this sheet, this sheet wins. Type key: **measured** = taken from CAD geometry or a weighed part (no part is weighed); **supplier** = published datasheet or catalogue; **calculated** = computed by the program's scripts or hand checks; **estimate** = judgement.

## The plain answer

V1 is a deliberate compromise: a buildable 257.9 kg (569 lb) solo adventure-touring EV with a 23.8 kWh pack, about 152 miles at 70 mph (calculated at an assumed CdA), a 135 mph speed limit and about 21-minute DC charging, instead of the brief's under-400 lb and 200-mile goals, which cannot both be met. It is a paper design with thin margins on mass, range and power, and nothing in it has been tested. The planned improvement path is better cells, lower drag, a lighter chassis and later a two-up variant.

## Headline numbers

| Quantity | Value | Source (document, section) | Type |
|---|---|---|---|
| Wet mass, no rider | **257.9 kg / 569 lb** (headroom 2.1 kg against T1) | `mass-rollup.json` `total_kg`; `parts-ledger.csv`; `bom-v1-reconcile.json` | calculated (0 kg measured; about 110 supplier, 75 calculated, 73 estimate) |
| Mass target T1 | <= 260 kg / 573 lb | `GATE-A-targets-locked.md` T1 and decision log | target |
| Ledger growth-adjusted mass | about 287 kg | `data/mass-budget-report.csv` (ledger's own +15% concept, +10% proposed rule) | estimate, not a forecast |
| Mass by system (kg) | pack 108.0, chassis about 31, running gear 43.2, drive 23.65, electronics 17.44, body and protection 14.4, cooling 6.9, wiring and fasteners 12.9 | `data/bom-v1-reconcile.json`; `mass-budget-report.csv` | calculated / estimate |
| CG (bike) | 787 mm ahead of the rear axle, 529 mm high | `mass-rollup.json` | calculated |
| Wheelbase | 1,490 mm | `15-dynamics.md`; `16-cad-revE.md` | measured (CAD) |
| Seat height | 832 mm | `16-cad-revE.md`, rider fit | measured (CAD) |
| Pack | Molicel P60B 21700, **100s11p**, 1,100 cells | `07-electrical.md` section 1 | supplier (datasheet v0.1) |
| Pack energy | **23.76 kWh gross, 21.4 kWh usable** (5-95%) | `06-drive-performance.md` section 1 | calculated |
| Pack voltage | **360 V nominal** (3.6 V per cell), 250-420 V | `07-electrical.md` section 1 | calculated |
| Pack mass | **108.0 kg** (cells 82.5, case 7.9, internals 14.5, holders 3.1) | `parts-ledger.csv` (ENG) | supplier (cells, 75 g max) / estimate (rest) |
| Peak power | **124 kW** motor datasheet cap. At the 350 A DC cap and 25 C: 124 / 109 / 100 / 93 / 87 kW at SOC 100 / 50 / 20 / 10 / 5 (`07`'s hand model gives 96 kW at 10%). At 5 C and SOC 20 or lower: 86 kW or less | `06` Final V1 update | supplier cap / calculated |
| Continuous power | **61.6 kW** at 5,500 rpm, inverter-limited; below 56 kW under 103 mph | `06` section 5 | calculated |
| 0-60 mph | **4.15 s** (4.44 s with 25 kg luggage; 5.47 s on a wet road) | `06` Final V1 update | calculated |
| 0-100 km/h / 0-100 mph / 60-100 mph | 4.31 s / 7.26 s / 3.12 s | `06` Final V1 update | calculated |
| Top speed | **135 mph limit** (6,500 rpm), governed at 130 mph; 125 mph sustained needs 43.5 kW at the wheel | `06` sections 1 and 2 | calculated (not verified) |
| CdA | **PENDING AERO, currently calculated at assumed CdA 0.38** (unmeasured; `17-aero.md` does not exist yet) | `06`; `19-independent-review.md` section 2 | assumption |
| Range at 70 / 77 mph | **PENDING AERO, currently calculated at assumed CdA 0.38: 152.4 / 132.2 mi** (flat, still air, 90 kg rider, 25 C). T3 fails above CdA about 0.407. Real-world about 15-20% lower | `06` Final V1 update | calculated |
| DC charge 10-80% | **about 21 min** at 25 C, 2C cell cap (12 A per cell, about 137 A pack). Other conditions (`10-thermal.md`, 3C-cap model): 23.0 min at 35 C, 25.4 min at -10 C with the 3 kW heater (14.0 min pre-heated), 40.9 min at 45 C. At a 2C cap, 35 C takes 27.4 min | `06` Final V1 update; `10-thermal.md` | calculated |
| AC charge | BROGEN PV1776 6.6 kW: 3.1 h for 10-90%, 2.7 h for 10-80%; no 120 V input on this unit class | `07` Final values | supplier / calculated |
| NACS | Native J3400 inlet and DIN 70121 / ISO 15118 charge controller (design). **Supercharger access and Plug and Charge are not established** | `07` section 3 | design / open |
| Motor | EMRAX 228 liquid-cooled, **LV+43% winding**, 220 Nm, 124 kW peak, 13.2 kg, 6,500 rpm | `06` section 1; `07` Final values | supplier (datasheet v1.7) |
| Inverter | Cascadia CM200DX, 300 A rms continuous, 740 A rms peak, 6.75 kg | `06` section 1 | supplier |
| Belt drive | Gates 8MGT-1760-62, 62 mm, 35T / 126T, **3.60:1**, centre distance 545.9 mm (CAD 545.6) | `06` section 1 | supplier / calculated |
| Drive mass | 23.65 kg | `parts-ledger.csv` (DRV) | supplier / estimate |
| DC cap, contactors, fuse | 350 A cap; GX14 contactors 350 A carry; **450 A** class fuse | `07` Final values | supplier / calculated |
| HV cable | 50 mm2 DC bus; 35 mm2 inlet; 70 mm2 motor phases | `07` Final values | calculated |
| Onboard charger | 6.6 kW, 3.0 kg | `07` Final values; ledger BV-ELC-0016 | supplier |
| Brakes | **320 x 5 mm** front discs, **267 x 5 mm** rear disc; front discs 362-375 C in a 125-0 mph stop (limit about 450 C) | `16-cad-revE.md`; `15-dynamics.md` | measured (CAD) / calculated (fade) |
| Frame | Steel pivot yoke, cross-member at **Z545**; pivot bearings 2 x 32012 X | `16-cad-revE.md`; `09-structures.md` Round 2 | measured (CAD) / calculated (FEA at 240 kg scaling, not re-run) |
| Wheels | Carbon, 2.6 kg front, 3.3 kg rear | `16-cad-revE.md` | estimate (no maker publishes masses) |
| Steering damper | Speed-scheduled semi-active, about 0.5 kg; thinnest damping ratio 0.028 (weave, with luggage) | `15-dynamics.md`; DFMEA D48; DVP&R V53 | calculated / estimate |
| Belt to rear tyre | 12.0 mm against a 12 mm limit (zero margin) | `16-cad-revE.md` | measured (CAD) |
| CAD checks | 91 of 91 envelope checks pass; the saved model lacks two generator fixes and many small parts | `16-cad-revE.md` | calculated |
| Unit cost at 10k/yr | **$29.5k** ($39.3k at 1k, $58.0k at 100). $32.3k if cells, motor and inverter stay at 1k prices | `11-cost.md` | estimate (no quotes) |
| Rider design case | 90 kg rider + 25 kg luggage, 1,755 mm (about the adult male average, not the 95th percentile) | `GATE-A-targets-locked.md` T7; `19` S7 | assumption |
| Validation plan | about $7.04M, 28 months, all planned (V53 adds $40k); not reconciled with the NRE in `11` | `14-dvpr.md` | estimate |

## T1 to T10 verdicts

Key: **met** = supported by analysis with margin; **met-thin** = passes on paper with little margin or on an assumption; **not met**; **not verified** = no analysis on the exact claim. Nothing in V1 is met by test.

| # | Target | Verdict | Evidence |
|---|---|---|---|
| T1 | Wet mass <= 260 kg | **Met-thin** | 257.9 kg, headroom 2.1 kg; nothing weighed; 28% estimate; the ledger's growth rule gives about 287 kg; group budgets were re-set to actuals, so "budget pass" proves little |
| T2 | Pack 100s11p, 23.8 kWh, 360 V, <= 108 kg | **Met (revised)** | 23.76 / 21.4 kWh, 360 V, 108.0 kg; revised from 370 V / 103 kg on Nov 22 |
| T3 | Range >= 145 mi at 70 mph | **Met-thin, not verified** | 152.4 mi at assumed CdA 0.38; fails above CdA about 0.407; aero pending |
| T4 | 125 mph sustained, governed 130 | **Met-thin, not verified** | 135 mph limit, 2.4x power margin; 25 C thermal passes in two models; at 38 C derates to about 105 mph |
| T5 | >= 90 kW peak, >= 55 kW continuous | **Met-thin** | 124 kW at high charge; 93 kW at 10% SOC and 87 kW at 5% (25 C, 350 A cap); 86 kW or less cold at low charge; continuous 61.6 kW, below 56 kW under 103 mph |
| T6 | Native NACS, DC 10-80% <= 25 min, AC >= 3.3 kW | **Met-thin, not verified** | about 21 min at 25 C and a 2C cap; the 35 C and cold figures lean on a 3C cap the cell data does not confirm; AC 6.6 kW booked; Supercharger access not established |
| T7 | Solo 90 kg + 25 kg luggage | **Met, thin** | FEA Round 3 (`09-structures.md`) at 257.3 kg + 90 kg rider + 25 kg luggage, yoke at Z545: all strength cases pass after +0.45 kg of wall increases (D1 arm SF about 1.25 vs 1.2; fatigue Miner D ≤ 0.5). Not tested. The rider is 1,755 mm, about the adult male average (not the 95th percentile) |
| T8 | Comfort, 77 mph gust stability, positive damping | **Met-thin, not verified** | positive damping only with the scheduled damper (0.028 thinnest); dynamics run at rev D mass; damper fail-safe now in DFMEA D48 and test V53 |
| T9 | Unit cost <= $32k at 10k/yr | **Met-thin (estimate)** | $29.5k; $32.3k with cells, motor and inverter at 1k prices; no quotes |
| T10 | Frozen appearance direction | **Met-thin** | direction kept; pods 55 mm proud, no R15 on the lower body and the second flank line are open (V1.1) |

## Open items carried forward

- **PENDING AERO:** CdA, range at 70 / 77 mph, cooling-duct pressure and gust side force wait for `17-aero.md`. The lead finalises them.
- Ledger follow-ups: 70 mm2 motor phase cables (about +0.3 kg) are not booked; the ledger and CAD names for the motor ("HV", "MV") and charger (`OBC_3p3kW`) are stale labels; the cost sheet still labels the rear disc 245 x 5 and the cable set 35 mm2.
- Structures were not re-run at the final mass or at the yoke's built height of Z545; dynamics were not re-run on rev E (the 177 mm pulley flange gives 48.6 deg, exactly the "pegs + 3 deg" rule).
- Nothing measured: no weighed part, no coast-down, no bench or crash test; P60B charge life above 2C and all supplier confirmations are missing.
