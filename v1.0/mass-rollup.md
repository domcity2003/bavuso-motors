# Bavuso V1.0 adventure: mass and centre-of-gravity roll-up

Prepared November 4, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).

- **Tools:** `tools/mass-rollup.py` (from the CAD) and `tools/acceleration-check.py`.
- **Data:** `mass-rollup.csv` (every line) and `mass-rollup.json` (totals).

> **Update, Nov 5:** with the IPM drive (`drive-study.md`), the roll-up is **282.9 kg (624 lb)**, which is +7.8 kg. The IPM and its reduction are estimated at 21 kg, plus 0.9 kg for gear oil and an oil cooler. CoG: bike only 803 mm ahead of the rear axle and 501 mm high; rider on, 637 mm. The rest of this page is the Nov 4 EMRAX roll-up.

## The plain answer

**The bike as modelled weighs about 275 kg (606 lb) ready to ride, not the 222.5 kg (490 lb) the optimiser assumed.** The pack matches the optimiser exactly (133.7 kg). The whole 53 kg gap is outside the pack: 141 kg bottom-up, against an 88.6 kg assumption that the earlier work itself labelled "focused mass target – unproven".

**606 lb is not heavy for what this bike carries:**

| Bike | Weight | Battery |
|---|---|---|
| Zero DSR/X | 247 kg | 17.3 kWh |
| Energica Experia | 260 kg | 22.5 kWh |
| **Bavuso (CAD roll-up)** | **275 kg** | **32.7 kWh** |

Bavuso carries 45% more energy than the Experia for 15 kg more.

**What the extra mass changes:**

| Item | At 222.5 kg | At 275.1 kg (CAD) | Verdict |
|---|---|---|---|
| Range at 70 mph, CdA 0.40 / 0.38 | 201 / 210 mi | 196 / 204 mi | About −5 mi. The 200-mile goal now depends on hitting the aero target. |
| CoG height, rider on | 644 mm (assumed) | **643 mm** | The assumption held, so anti-squat stays at 124% and the 390 mm pivot height stands. |
| Front/rear split, bike only / rider on | — | 54/46 / 50/50 | Good for an adventure bike. |
| Rear spring | 97 N/mm | **107 N/mm** | Updated. The 20 mm preload adjuster now holds two-up loaded sag at about 58 mm (it was 65). |
| 0–60 mph, rider on | 4.3 s | **5.0 s** | **Misses the 3.0 s target by a wide margin. This is the motor, not the mass.** See below. |

## The bigger finding: the motor can't reach 3.0 s

> **Correction, Nov 5:** the table below assumes the EMRAX reaches 6,500 rpm. On this 360–416 V pack it doesn't, because the MV winding needs about 630 V. The current drive actually tops out at about 114 mph, and the EMRAX 268 MV fails too. See `drive-study.md`, which recommends a radial IPM with a 2-stage reduction.

The EMRAX 228 MV makes **220 Nm peak** and is limited to **6,500 rpm** (EMRAX datasheet v1.7). That limits what one fixed gear ratio can do:

- **Tall gearing for 150 mph (3.1:1):** about 2,100 N at the tyre. With a rider aboard (360 kg) that is only about 0.6 g, so 0–60 takes **5.0 s**. The bike is torque-limited all the way to 60 mph; peak power never comes into play. Even at the optimiser's lighter mass it would be 4.3 s.
- **Short gearing for a 3.3 s launch (4.6:1):** top speed falls to 101 mph.

The optimiser only checked peak power (124 kW is enough), not torque at the wheel. That is why this wasn't caught.

| Drive option | 0–60 | Top speed | Mass vs now |
|---|---|---|---|
| EMRAX 228, 3.1:1 (current CAD) | 5.0 s | 150 mph | — |
| EMRAX 228, 4.6:1 | 3.3 s | 101 mph | — |
| EMRAX 268 MV (500 Nm, 4,500 rpm), 2.2:1, 130 kW pack limit | 3.1 s | 146 mph | +8.4 kg |
| High-speed radial motor (300 Nm, 16,000 rpm), 2-stage 7.3:1 | 2.7 s (grip-limited) | 157 mph | +7.5 kg |

Both alternatives reach the targets. They pull the layout in different directions:

- **EMRAX 268:** keeps the motor-on-pivot layout, so the belt length stays constant and the rear suspension work still applies. It is 40 mm larger in diameter (268 mm), so the pack loses some space around it, and the bigger torque needs a bigger inverter. Its rpm at a 416 V pack is not yet confirmed.
- **High-speed radial motor with a 2-stage reduction:** this is the "custom radial IPM from an e-drive tier-1" option the optimiser already rated as cheapest ($1.5k vs $3.6k per bike at 10k/yr). Only the gearbox output needs to sit on the pivot axis; the motor body can go elsewhere.

This is a powertrain decision. It needs its own study before the CAD changes again.

**Simulation assumptions:** rider 85 kg; rotating mass +5%; CdA 0.40 at launch and 0.38 at top speed; launch control limits acceleration to 1.0 g (the wheelie limit b/h is 1.15 g with this CoG); tyre rolling radius 305 mm; driveline efficiency 95% (93% for 2-stage).

## The roll-up

275.1 kg ready to ride (all fluids, 12 V lithium battery, no rider or luggage).

| Result | Value |
|---|---|
| **CoG, bike only** | 806 mm ahead of the rear axle, **505 mm** above ground, 1.8 mm left of centre |
| **CoG, rider on** (85 kg) | 738 mm ahead, **643 mm** high |
| **CoG, two-up with 30 kg luggage** | 580 mm ahead, 741 mm high (anti-squat about 107%) |
| **Unsprung mass** | Front 17.6 kg, rear 19.0 kg |
| **Pitch inertia about the CoG** | 36.8 kg·m² from point masses. That's a lower bound, because it ignores each part's own size. |

### Compared with the earlier 90 kg non-pack budget

| Category | CAD roll-up | Old budget | Why it's higher |
|---|---|---|---|
| Battery pack | 133.7 | (separate) | Matches the optimiser: 594 cells at 180 g, plus case and internals. Cells are 80% of the pack. |
| Frame, swingarm, structural hardware | 29.1 | 20 | Includes 9 kg of chromoly tube and steel brackets, pegs, stands, side stand and body brackets. The swingarm is probably *under*-estimated (see below). |
| Wheels, tyres, brakes | 27.3 | 25 | Forged wheels, 4.5 + 6.0 kg tyres, twin 320 mm discs, ABS. Close to budget. |
| Motor, inverter, final drive | 24.7 | 13 | The budget assumed the 9.4 kg EMRAX 208. The 228 is 13.5 kg, plus a 6.5 kg SiC inverter and 2.2 kg of HV cable. |
| Charging, 12 V, cooling | 19.3 | 7 | The 6.6 kW on-board charger alone is about 6.5 kg. Add radiators, coolant, DC-DC converter, BMS and contactor cabinet. |
| Suspension and steering | 17.5 | 14 | 48 mm USD fork, clamps, semi-active shock, bars and controls |
| Bodywork, seat, cockpit, lights | 16.6 | 6 | The 6 kg budget was never realistic. Panels from the CAD shells come to about 9 kg, plus seat 2.6, screen 0.8, headlamp 1.2, mirrors and lights. |
| Wiring, fasteners | 7.0 | 5 | |
| **Total** | **275.1** | **90 + pack** | |

**How each number was set** (every line is tagged in the CSV):

| Basis | Mass | Examples |
|---|---|---|
| Supplier or catalogue figure | 125 kg | Cells, EMRAX 228, front tyre, 6008 bearings |
| CAD volume or area × material density | 58 kg | Frame tubes, pack case, panels, swingarm |
| Engineering estimate | 92 kg | Inverter, charger, wheels, fork, shock, wiring, fasteners |

The estimates are the main uncertainty, probably ±8 kg overall.

### Known weak spots in the roll-up

- **The swingarm is probably 3 kg too light.** The CAD arms are small (74×34 mm tapering), and 3.5 mm walls give 3.3 kg for the whole swingarm. A real adventure-bike swingarm for a 475 kg two-up load is 6–7 kg.
- **Inverter:** 6.5 kg is an estimate for the contract SiC unit. The CM200DX in the CAD is about 11.3 kg (retailer figure).
- **Wheels:** these are forged (the premium package). Cast wheels would add about 2 kg.
- **The rider's CoG** (85 kg at 1,090 mm) is a standard seated estimate.

## Ways to take weight out (if wanted)

| Lever | Saves | Cost / effect |
|---|---|---|
| Drop the 6.6 kW AC charger for 3.3 kW, or AC charging through the traction inverter | 3–5 kg | Saves money. DC fast charging (the Supercharger goal) doesn't use the on-board charger at all. |
| Aluminium frame tubes instead of chromoly | about 4 kg | Small cost; needs fatigue design at the welds |
| Carbon bodywork, subframe and tank shroud (the optimiser's carbon package) | about 6 kg | About +$3.5k per bike at 10k/yr |
| Magnesium wheels | about 2 kg | Premium cost; durability off-road is a concern |

All four together give about 260 kg (573 lb), level with the Experia but with 45% more battery. Getting back to 490 lb would mean a much smaller pack, which breaks the 200-mile goal. **I recommend resetting the mass target to 265 kg (585 lb)**: take the charger change and the aluminium frame (both cheap), and leave carbon bodywork as an option.

## What changed in other files

- `tools/rear-kinematics.py` now reads the bike's mass, CoG and rear unsprung mass from `mass-rollup.json`. Spring rate 107 N/mm; rider-on rear load 1,592 N; two-up loaded 2,655 N.
- `rear-suspension.md`: spring and preload numbers updated.

Sources:
- [EMRAX 228 product page (13.5 kg LC)](https://emrax.com/e-motors/emrax-228/)
- [EMRAX 228 datasheet v1.7 (220 Nm, 6,500 rpm)](https://emrax.com/wp-content/uploads/2025/03/EMRAX-228_datasheet_v1.7.pdf)
- [EMRAX 268 datasheet v1.7 C (500 Nm, 4,500 rpm, 21.4–22.3 kg)](https://emrax.com/wp-content/uploads/2025/08/EMRAX-268_datasheet_v1.7_version_C.pdf)
- [New Eagle CM200DX listing (25 lb)](https://store.neweagle.net/?p=18103)
- [Orion BMS 2 changes (40% lighter 108-cell unit)](https://www.orionbms.com/downloads/documents/whats_new_in_orion2.pdf)
- [Michelin Anakee Adventure 120/70R19 listing](https://www.desertcart.com.ar/products/119842382-anakee-adventure-motorcycle-tire)
- [Pirelli: Experia 260 kg, DSR/X 247 kg](https://www.pirelli.com/global/en-ww/road/motorcycles/electric/the-first-electric-maxi-enduro-bikes-energica-and-zero-motorcycles-borderless-roads-62213/)
- [RideApart spec showdown: DSR/X vs Experia](https://www.rideapart.com/news/615118/spec-showdown-zerodsrx-vs-energicaexperia/)
