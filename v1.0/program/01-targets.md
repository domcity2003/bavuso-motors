# Bavuso V1: the target point (weight, range, power, charging, price)

> **Superseded in part (Nov 22, 2026).** This document predates the final V1 numbers; the authority is `00-V1-final-spec.md`. Final: 257.9 kg / 569 lb (T1 <= 260 kg, 2.1 kg headroom), pack 100s11p 108.0 kg, 360 V, 23.76 kWh gross, CAD rev E, cost $29.5k at 10k/yr. All of it is analysis or estimate; nothing is built or weighed. Stale here: the 240 kg ceiling with a 12 kg (5%) margin (REQ-001); 23.0 / 20.7 kWh (final 23.76 / 21.4); 340 V nominal (360 V); pack 100 kg (108.0 kg); 146 / 125 mi at 70 / 77 mph (final 152.4 / 132.2 mi, calculated at an assumed CdA 0.38, pending aero); "125 mph verified" (calculated only, nothing verified); 60 kW continuous (final >= 55 kW, 61.6 kW); $24.8k unit cost ($29.5k).


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

## The plain answer

**Recommended V1 target: 240 kg / 529 lb wet and ready to ride (no rider, no luggage), 23 kWh gross (20.7 kWh usable), about 145 miles at a steady 70 mph, 125 mph verified top speed (governed at 130 mph), solo-rider design case, native NACS fast charging 10-80% in about 20 minutes.**

- **400 lb does not close.** With the lightest realistic bike outside the battery (about 140 kg including margin), a 400 lb bike carries only 11 kWh. That is about 74 miles at 70 mph, which is worse than a Zero.
- **200 miles at 70 mph does not close either.** It needs 32 kWh and a 286 kg / 631 lb bike. That is heavier than every electric road bike and petrol adventure bike listed here.
- **The sweet spot is the middle.** Every extra 10 miles of range costs about 8.3 kg (18 lb) of bike. Below about 140 miles the bike gets only slightly lighter, but the usable range stops being a long-trip bike. Above about 150 miles it gets steadily heavier, and the weight is felt every minute while the range is used only on some days.
- **Fast charging cheapens range.** Twenty minutes on a NACS charger adds about 100 to 120 miles at 70 mph. Two 20-minute stops cover a 300-mile day.
- **It lands where the premium competition is.** 529 lb is lighter than the Energica Experia (573 lb), LiveWire One (562 lb) and Zero DSR/X (544 lb), and about equal to a BMW R 1300 GS (523 lb) and a KTM 1390 Super Adventure S (about 538 lb fueled). Saying "weighs the same as the GS, goes 145 miles at 70 mph" is a strong claim.
- **The hard part is outside the pack.** The current bike has 195 kg outside the pack. The target needs 128 kg plus 12 kg of margin. That is a cut of about 67 kg (148 lb) beyond the 34 kg saved by shrinking the pack. The benchmarks show 112 to 158 kg is what shipping bikes achieve, so the target sits at the top of what has been done and needs honest part-by-part proof.

### Verdict table

| Item | Recommendation | Status |
|---|---|---|
| Weight ceiling | 240 kg / 529 lb wet, ready to ride, 90 % fluids, no rider | estimate, needs a re-architected bike |
| Gross / usable energy | 23.0 kWh / 20.7 kWh | calculated |
| Pack mass at planning density | 100 kg at 230 Wh/kg (pack level) | estimate, needs a cell chosen |
| 70 mph range (flat, still air) | about 146 mi at CdA 0.38 (range 132 to 163 mi for CdA 0.43 to 0.33) | calculated, drag unmeasured |
| Drag area assumption | CdA 0.38 m2 for bike plus rider; the 0.33 goal is upside, 0.43 is the floor | estimate |
| Load case | solo rider 90 kg plus 25 kg luggage; two-up is a later option | recommendation |
| Top speed | 125 mph verified, governed to 130 mph | calculated power, thermal unproven |
| Peak / continuous power | 90 kW peak, 60 kW continuous (a 3.9 C peak and 2.6 C continuous on 23 kWh) | recommendation |
| Fast charge | native NACS DC, 10-80 % in 20 min or better (average 2 C or more, about 55 kW average) | needs a 2 C-or-better charge cell |
| Price | MSRP target around $45k; unit cost at scale at or below $32k | estimate, owner decision |

## 1. Benchmark survey

Source key: **supplier** = maker or maker-quoted spec site, **review** = independent press, **estimate** = my number. I searched each page's result summary; I did not read every page in full, and several sites disagree with each other (noted). Pack masses are mostly **not published**, so the pack column is my estimate from kWh divided by a pack-level density of 150 to 180 Wh/kg, typical of 2018-2023 packs; the rest-of-bike figure inherits an uncertainty of about plus or minus 15 kg.

| Bike | Wet / curb kg (lb) | Gross kWh | Rated range | Peak power | Top speed | US price | Pack kg (estimate) | Mass outside pack kg (derived) |
|---|---|---|---|---|---|---|---|---|
| Zero DSR/X | 247 (545) | 17.3 | 85 mi at 70 mph claimed; 107 mi at 55 mph; reviewers 70-100 | 75 kW (100 hp) | 112 mph | $22,995 | about 115 | about 132 |
| Zero SR/F | 227 (500) | 17.3 | 117 mi combined (Cycle World test); 176 mi city | 83 kW (111 hp) | 124 mph | $18,495-20,495 | about 115 | about 112 |
| LiveWire One | 255 (562) | 15.5 | about 70 mi highway (speed unstated); 95 combined | 75 kW (100 hp) | 110 mph | $21,999-22,799 | about 97 | about 158 |
| LiveWire S2 Del Mar | 196 (432) | 10.5 | 43 to 62 mi at 70 mph (sources conflict) | not retrieved | not retrieved | $15,499-16,499 | about 66 | about 130 |
| Energica Experia | 260 (573) | 22.5 | 130 mi at about 68 mph claimed; 120 real | not retrieved | not retrieved | UK GBP 25-28k | about 136 | about 124 |
| Energica Ego+ | 258-260 (570) | 21.5 | about 100 mi mixed (160 km) | 126 kW (171 hp) | 149 mph limited | about $27k | about 130 | about 128 |
| Damon HyperSport Premier | about 200-227 (440-500, dry and estimated figures conflict) | 20 | 75 to 161 mi at 70 mph (sources conflict) | 150 kW | 200 mph claimed | $40-45k | about 111 | about 90-115 (unreliable) |
| BMW R 1300 GS (ICE) | 237 (523), road ready, fueled, 19 L | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| KTM 1390 Super Adventure S (ICE) | 244 (538) fueled; 227 dry; 23 L | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

URLs:
- Zero DSR/X: https://www.zeromotorcycles.com/model/zero-dsrx ; https://www.motorcycle.com/specs/zero-motorcycles/sport/2027/dsr-x/z-force-17-3/detail.html ; https://motorcyclistonline.com/reviews/zero-motorcycles-dsrx-electric-bike-review
- Zero SR/F: https://zeromotorcycles.com/model/zero-srf ; https://www.motorcycle.com/specs/zero/standard/2025/sr-f/z-force-17-3/detail.html ; https://www.cycleworld.com/zero/srf/
- LiveWire One: https://www.livewire.com/one ; https://www.motorcycle.com/specs/livewire/standard/2022/one/base/detail.html ; https://www.totalmotorcycle.com/motorcycles/2022/2022-livewire-one
- LiveWire S2 Del Mar: https://www.livewire.com/s2-del-mar ; https://www.rideapart.com/news/677322/livewire-s2-del-mar-specs/ ; https://www.motorcycle.com/specs/livewire/standard/2025/s2/del-mar/detail.html
- Energica Experia: https://asset.moto.it/pricelist/moto/fb7960978544b0ffec2bcac7b66d33ae/scheda-energica-experia-2023-eng.pdf ; https://www.revzilla.com/common-tread/2022-energica-experia-first-ride-motorcycle-review ; https://www.motorcycle.com/features/2023-energica-experia-rs-review-first-ride.html
- Energica Ego: https://en.wikipedia.com/wiki/Energica_Ego (a single secondary source for 21.5 kWh) ; https://asset.moto.it/pricelist/moto/cca3f0b66bf38604da7bdbf11bc44a8f/scheda-tecnica-eng.pdf
- Damon: https://www.totalmotorcycle.com/motorcycles/2023/2023-damon-hypersport ; https://www.bike-ev.com/transport/damon-hypersport-premier-review-price-specs/
- BMW R 1300 GS: https://bmwmotorcycles.com/en/models/adventure/r1300gs-2024/technicaldata.html ; https://www.1000ps.com/en-us/model/12167/bmw-r-1300-gs/2024
- KTM 1390 Super Adventure S: https://www.ktm.com/en-gb/models/adventure/2025-ktm-1390-superadventures/technical-specifications.html

### What the benchmarks say

1. **No shipping electric road bike gets below about 112 kg outside the pack.** The range is 112 to 158 kg, with the adventure-style DSR/X at 132. These bikes have no DC fast charge (Zero) or a basic CCS inlet (Energica), no 125 mph thermal load and no premium finish. Native NACS hardware and a 125 mph drive add a few kilograms.
2. **Realistic floor: 125 kg for a road-focused bike, 130 to 140 kg for an adventure bike.** The review's 105 kg is below every benchmark. The sweep covers 105 to 160 kg; I use **140 kg including margin** (128 kg of systems plus 12 kg) as the central case.
3. **The ICE adventure bikes are 237 to 244 kg fueled.** An electric adventure bike at 240 kg is level with them, with 23 kWh of energy that would cost 3 to 4 times as much in a fuel tank at the same weight.
4. **70 mph range is poorly published.** Maker numbers are at 55 mph, in city cycles or blended. The Experia's claim of about 130 mi at about 68 mph is the most useful and matches my calculation for a 22.5 kWh pack, which gives about 115 to 135 mi at 0.40 CdA. Real-world tests agree on roughly 100 to 120.
5. **The current 33 kWh pack is bigger than anything on sale** (Experia 22.5 kWh is the largest). Our pack at 245 Wh/kg is lighter per kWh than any shipping pack I could find (Enepaq's P50B module is 183-226 Wh/kg; 150-180 is typical for the bikes above).

## 2. Sweep

Script: `program/tools/target-sweep.py` (FreeCAD python, numpy and matplotlib). Output: `program/data/target-sweep.csv` (2,340 rows) and `program/data/target-sweep.png` (three panels: drag, pack density, rest-of-bike mass).

**Road-load model is the review's:** rho 1.225, Crr 0.015, 90 % battery-to-wheel, 300 W auxiliaries, 90 % usable energy, 90 kg rider, flat and still air. The script reproduces the review's numbers (32.7 kWh at CdA 0.377 and 328.4 kg; 27.2 kWh at CdA 0.330 and 181 kg) to rounding, so the model matches page 3 and page 5.

**Sweep ranges:** range at 70 mph 100-220 mi; CdA 0.33-0.43 m2; pack Wh/kg 200-280; rest-of-bike mass 105-160 kg.

**Pack density that is realistic for 2026 (my judgement, estimate).**
- The current ledger cell is 306 Wh/kg (594 cells at 180 g) with cells at 80 % of pack mass, giving 245 Wh/kg. That is an assumption, not a quote.
- Bare high-power cells: Molicel P50B 260 Wh/kg, P60C 284 Wh/kg (5 C charge advertised, delivery timing unverified); high-energy M65A 322 Wh/kg but only 1 C standard charge (see `research/battery-deep-dive.md`).
- Packaged: Enepaq's P50B module is 183-226 Wh/kg (urls in `research/range-weight-budget.md`); CATL's car-scale systems are up to 255-265 Wh/kg, which a small motorcycle pack cannot inherit.
- **Planning value: 230 Wh/kg**, which needs about 290 Wh/kg cells at 80 % cell mass. Stretch: 245. Prudent floor: 200-215 (for 260 Wh/kg cells that charge fast). At 200 Wh/kg, the same 23 kWh weighs 15 kg more.

**Mass compounding (secondary-mass factor).** Frame, swingarm, wheels, tires, brakes, fork and shock total about 55 kg and are sized by loaded mass (about 330 kg with rider). 55/330 is 0.17, and I use **0.15** because minimum-gauge limits stop part of it scaling. So each kilogram of pack also adds 0.15 kg elsewhere: 1 kWh costs 4.35 kg of pack plus 0.65 kg of compounding, about 5.0 kg in total. This is an estimate from my reading of the ledger, not a measurement.

**Central results (CdA 0.38, 230 Wh/kg, rest-of-bike 130 kg at a 100 kg reference pack):**

| 70 mph range | gross kWh | pack kg | bike kg | bike lb |
|---|---|---|---|---|
| 100 mi | 15.3 | 67 | 192 | 423 |
| 120 mi | 18.6 | 81 | 208 | 458 |
| 140 mi | 21.8 | 95 | 224 | 494 |
| 150 mi | 23.5 | 102 | 233 | 513 |
| 160 mi | 25.2 | 110 | 241 | 531 |
| 180 mi | 28.6 | 124 | 258 | 569 |
| 200 mi | 32.0 | 139 | 275 | 607 |

Findings from the full grid (read from the CSV, not from this table):
- Mass is nearly **linear in range** (about 8.0 to 8.8 kg per 10 mi). There is no sharp "knee" in the mass curve; the argument for the optimum has to come from usability, charging and where the weight goes, not from a kink.
- **400 lb with 125 kg or more outside the pack tops out at 120 mi at 70 mph** (110 mi with 135 kg), and only with a low CdA and dense pack (CSV rows with bike_lb_wet at or below 400).
- CdA is worth about 10 mi per 0.03 m2 at this size; 0.33 vs 0.43 is a 31-mile swing (163 vs 132 mi at 23 kWh).
- Rest-of-bike mass is worth about 20 mi per 15 kg. It is the largest controllable lever.

## 3. Power, C-rate and charging checks

All from the same script output.

**125+ mph power.** At CdA 0.38, steady 125 mph needs 43 kW at the wheel and 48 kW from the battery; 130 mph needs 48 kW and 54 kW. With 15 % extra for grade and wind, 56 kW and 62 kW. At CdA 0.43 add about 12 %. This confirms the review's 49-52 kW wheel-power screen is reasonable. A 90 kW battery peak gives a physical ceiling of about 150 mph, so a 125 mph claim has margin; I recommend governing at 130 mph. **125 mph uses about 386 Wh/mi, so range at that speed is about 54 mi.** That is true of every bike and should be stated.

**What the smaller pack can deliver.**

| Gross kWh | 125 mph cruise, 48 kW | 90 kW peak |
|---|---|---|
| 18 | 2.7 C | 5.0 C |
| 20 | 2.4 C | 4.5 C |
| **23** | **2.1 C** | **3.9 C** |
| 28 | 1.7 C | 3.2 C |
| 32 | 1.5 C | 2.8 C |

A 23 kWh pack needs cells that sustain about 2.1 C continuous and 3.9 C for 10 to 30 seconds, plus thermal headroom at 125 mph. High-power cells (P50B class, 5 C charge) do this; 1 C high-energy cells such as the M65A do not. **This choice drives pack mass (a 260 Wh/kg cell gives about 208 Wh/kg at 80 % cell fraction, so 23 kWh is 111 kg, not 100 kg) and is the main risk to the 230 Wh/kg planning value.** The P60C (284 Wh/kg, 5 C) would make 227 Wh/kg, which is why 230 is the planning figure; its delivery timing is unverified.

**Fast charge, 10-80 % with native NACS DC.**
- 10-80 % is 70 % of the pack. Time is 0.7 / (average C-rate) hours: **21 minutes at 2 C average, 14 minutes at 3 C.** These times are the same for any pack size, because the limit is the cell's C-rate, not the charger.
- Average power is about 46 kW (2 C) to 69 kW (3 C) for 23 kWh, well below Tesla's 250 kW stall limit. Voltage matters: the current pack is 340 V nominal (250-420 V summed), so about 140 to 200 A. It needs the NACS-side handshake (open item).
- A bigger pack charges at higher kW at the same C-rate, so a 33 kWh pack would add more miles per minute. That is the one real argument for a larger pack, and it holds only if the cell accepts 2 C or more. A **1 C cell (the M65A class) would take about 42 minutes** for 10-80 %, which would undo the premium charging story.
- **Miles added in 20 minutes at about 135 Wh/mi (70 mph):** 99-104 mi for 20 kWh; 119-124 mi for 24 kWh; 138-145 mi for 28 kWh. At the recommended 23 kWh: about 115 mi.
- So a smaller pack costs very little charging time, and the 150 mile pack is fine for road trips of 300+ miles with two 20-minute stops.

## 4. Recommended optimum and the trade

### The point

| Parameter | Value |
|---|---|
| Wet, ready-to-ride weight ceiling | **240 kg / 529 lb** (all fluids, no rider or luggage), including a 12 kg (5 %) margin |
| Energy | **23.0 kWh gross, 20.7 kWh usable** (a 100 kg pack at 230 Wh/kg planning) |
| Range at 70 mph, flat, still air | **146 mi** at CdA 0.38 (132-163 mi for CdA 0.43-0.33); 131 mi at 75 mph; 125 mi at 77 mph; real-world with wind and hills is about 15 to 20 % lower |
| CdA assumption | 0.38 m2 bike plus 90 kg rider (between the review's 0.330 goal and 0.423; the mid case is 0.377). Unmeasured; needs a wind-tunnel or coast-down check |
| Load case | **Solo.** Structure and suspension sized for a 90 kg rider plus 25 kg luggage (115 kg payload). Two-up (pillion plus luggage) as an optional, separately validated variant: it costs about 8 kg and CdA +0.06, giving about 125 mi |
| Top speed | 125 mph verified, governed at 130 mph; power and thermal need drive-study validation |
| Power | 90 kW peak (3.9 C), 60 kW continuous; 125 mph cruise needs 48-56 kW |
| Charging | native NACS DC, 10-80 % in about 20 minutes or better (cell must accept an average 2 C or more); AC onboard charger sized small (3.3 kW is plenty for overnight) |
| Price | MSRP about $45k; unit cost at scale at or below $32k |

### Why this beats the extremes (plain words)

- **The 400 lb bike is a bike that cannot go anywhere.** It would carry 11 kWh and do about 74 miles at highway speed with a 15-20 % real-world loss, so about 60 miles. A Zero DSR/X already does 85 and costs half as much. A status product cannot be out-ranged by a cheaper bike.
- **The 200-mile bike is a 631 lb bike.** Heavier than any rival, it needs a 32 kWh pack that has not been shipped in any motorcycle, makes the bike harder to handle, and still loses 15-20 % in real conditions. Weight is paid on every ride, range is used on a few.
- **Where the weight comes from matters.** Each extra 10 miles costs 8.3 kg (18 lb). From 120 to 145 miles you add about 20 kg of bike and gain 25 miles. Past 145 miles you add the same weight for the same miles, yet the benefit shrinks because a 20-minute stop restores 100-plus miles.
- **Money is not the constraint.** At a pack cost of roughly $120 to $150 per kWh (my estimate; the repository cost model has a wide range), the cost of 10 kWh is about $1.5k. The constraint is mass.
- **At 145 miles the bike sells on usability.** It beats every electric rival on 70 mph range and weight-per-mile, matches the leading petrol adventure bikes on weight and puts them on notice on charging convenience.

### Per-system mass budget (sums to the ceiling)

Current values are from `mass-rollup.csv` (review page 2, converted from pounds). Benchmark anchors are the best published or ledger numbers; every target line is an **estimate** until a part is selected.

| System | Budget kg | Today kg | Anchor |
|---|---|---|---|
| Pack (23 kWh, 230 Wh/kg incl. case, BMS, internal cooling) | 100.0 | 133.7 | Enepaq P50B module 183-226 Wh/kg; 290 Wh/kg cells x 0.80; Zero, Energica pack masses are about 110-136 kg for 17-22 kWh |
| Chassis (frame, swingarm, rails, subframe, stand, pack as stressed member) | 18.0 | 34.9 | benchmark estimate: ICE adventure frame plus swingarm about 25 kg; the pack case already weighs 10.7 kg and should carry load |
| Running gear (wheels and tires 18.6, fork 7.5, shock 2.5, brakes and ABS 5.5, bar and controls 3) | 37.0 | 44.9 | ledger: wheels and tires 41 lb today; DSR/X rest-of-bike sets the family limit |
| Drive (motor, 2-stage reduction, belt) | 22.0 | 23.6 | drive-study: radial IPM 14 kg plus reduction 7 kg plus belt 1 kg |
| Electronics (inverter 6.5, onboard charger 3.5, DC-DC 2.8, BMS and junction boxes 4, dash and lights 3) | 20.0 | 24.5 | ledger: CM200 inverter 6.5; NX W90 option is 3.1 kg; charger 6.5 kg today, a 3.3 kW unit saves about 3 kg |
| Body and protection (seat 2.6, panels 5, screen 2, skid plate 2, guards 2, lights 1.4) | 15.0 | 30.8 | ledger: seat 2.6, skid plate 3.7 kg at 4 mm, guards 2.4 kg each; cut guards and skid |
| Cooling hardware | 6.0 | 8.6 | one loop, smaller pack heat; ledger pump, hoses, coolant 2.8 kg |
| Wiring, fasteners, brackets, fluids | 10.0 | 27.7 | ledger: HV cables 2.2, LV harness 3.0, fasteners 3.0, brackets 2.0; the review found 7.5 lb of double counts |
| Margin (5 %) | 12.0 | 0 | planning margin on the ceiling |
| **Total** | **240.0** | **328.7** | |

Non-pack systems are 128 kg plus 12 kg margin, against 195 kg today. The reduction of 67 kg is the real work. Biggest cuts: body and protection (-16), running gear and chassis (-24 combined), wiring and other (-18, partly double counting), electronics (-4.5). **If systems come out heavier, the choices are: take the weight and lose range (about 1.2 mi per kg), lose features, or accept a heavier ceiling. Not a bigger battery.**

## 5. Draft requirements (REQ-001 onward)

- **REQ-001** Complete bike mass, wet and ready to ride (all fluids, 90 % charge not required for mass, no rider or luggage), must not exceed **240 kg / 529 lb**, including a margin of 12 kg tracked as a separate line.
- **REQ-002** The pack shall hold **23.0 kWh gross / at least 20.7 kWh usable** at beginning of life, with pack mass at or below **100 kg** (230 Wh/kg at pack level, including case, BMS and internal cooling).
- **REQ-003** Range shall be **at least 145 miles at a steady 70 mph** on a flat, still-air calculation at CdA 0.38 m2 with a 90 kg rider; the published claim shall state the conditions.
- **REQ-004** Drag area (bike plus rider, upright posture) shall be measured or computed on the final shape; **design target 0.38 m2, stretch 0.33 m2.** The range claim is revised to the measured value.
- **REQ-005** Design payload: solo rider 90 kg plus 25 kg luggage. Pillion operation is excluded from the V1 specification and may be offered only after a separate structural, braking and stability validation.
- **REQ-006** Top speed shall be **at least 125 mph, governed at 130 mph**, with thermal capability to hold 125 mph for 10 minutes on a 25 C day without power derating.
- **REQ-007** Power: **90 kW peak and 60 kW continuous** at the pack terminals, and the pack and cells shall sustain at least 2.2 C continuous and 3.9 C for 10 s at 20 percent state of charge.
- **REQ-008** Charging: **native NACS DC** on the bike (no adapter), **10-80 % in 20 minutes or better** at 25 C ambient, with a cell chosen for at least 2 C average charge acceptance; AC charging with a 3.3 kW onboard charger.
- **REQ-009** The mass budget shall be tracked per system with the table in this document as the starting point; any system more than 5 % over budget requires a documented trade.
- **REQ-010** The model for rolling resistance, drag and efficiency shall be the review's (rho 1.225, Crr 0.015, 90 % battery-to-wheel, 300 W auxiliaries, 90 % usable); changes need justification.
- **REQ-011** Planning pack density is 230 Wh/kg; a cell is not selected until it is confirmed to deliver REQ-002, REQ-007 and REQ-008 together, with datasheet evidence for energy, discharge and charge ratings.
- **REQ-012** Highway comfort and gust stability at 77 mph shall remain open acceptance criteria, evaluated together with REQ-004.
- **REQ-013** Price position: MSRP about **$45k**; unit cost at scale at or below **$32k** (owner's range is $30-35k).
- **REQ-014** Marketing claims shall use *measured* range and weight only; calculated figures are labelled as such.

## What this does not prove

- **Nothing here is measured.** The bike has not been weighed, its drag has not been measured, and the 128 kg systems budget has no selected parts behind most lines.
- **Benchmarks come from search summaries, not full reads.** Several have conflicting numbers (S2 Del Mar range, Damon weight and range, Zero SR/F price, Energica pricing). Pack masses for every benchmark bike are my estimates from kWh and an assumed density; the Damon number is especially unreliable.
- **Unit-cost and price figures are estimates.** I did not rebuild the cost model for the smaller pack; I assumed the cell cost scales roughly linearly and that the cost at scale stays within the owner's $30-35k band. MSRP of $45k comes from comparing the Damon ($40-45k) and Energica; it is a positioning judgement.
- **The secondary-mass factor (0.15) is an estimate.** A different value of 0.10 to 0.20 moves the 145-mile mass by about 3 kg.
- **The charge-time claims assume a cell that accepts 2 C or more;** no such cell has been selected, tested or confirmed for this pack, and neither Tesla site compatibility nor the NACS handshake has been proven.
- **No crosswind, hill, cold-weather, ageing or two-up analysis was done** beyond a single two-up sensitivity (125 mi).
- **No thermal analysis** was done for 125 mph or for repeated fast charging.
