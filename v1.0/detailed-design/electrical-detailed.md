# Bavuso V1.0 adventure: electrical detailed design (HV and LV)

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5). Finished November 13 after a usage-limit pause, adding the Molicel P60B fallback requested by the supplier audit.

Scripts: `detailed-design/tools/elec-pack.py`, `elec-hv.py` (includes the FreeCAD clearance check), `elec-lv.py`, `elec-schematic.py`, `elec-bom.py`. Outputs are in `detailed-design/electrical/`. Run each from `v1.0` with the FreeCAD python, in the order pack → hv → lv → schematic → bom.

> **Coordinates:** all coordinates here are **saved-model** coordinates (generator coordinates +40 mm in Z), the same frame as `cell-placement-adventure.csv`. Subtract 40 from Z to get generator values.
>
> **Which pack this covers:** `electrical-design.md` still describes the older 100s7p Amprius pack. This report follows the CAD and the brief instead: **99s6p, 594 × 26120 cells, 32.7 kWh, 416 V**.

## The plain answer

**The electrical system closes on paper, and it fits the bike, with four changes to the CAD.** The current CAD has no room for busbars, so the pack must get about 10 mm wider on each side. One lane's cell numbering has to be reversed. And the HV hardware moves into three small sealed boxes, all of which the CAD check shows clear the surrounding parts by at least 3 mm.

**The battery pack** has three lanes of 33 cell groups in series, each group six cells in parallel. Each lane is split into three 11-group sub-modules. Each sub-module stays under 46 V, so it is safe to handle bare during assembly.

**Busbars:** the best point in the sweep is **4 mm-thick EC-grade aluminium (Al 1350)**.
- The busbars are tapered, 24 mm wide where they carry full current.
- They are laser-welded to the cells through a 0.3 mm nickel-plated copper plate.
- That plate has a built-in fuse neck for every cell.
- All 98 links together weigh 4.7 kg and lose 352 W at the 260 A fast-charge current.
- They drop 2.3 V at full power (0.6% of pack voltage) and heat up by under 8 K in a 30-second full-power burst.

**Protection** works in layers, each covering faults the others are slow on:
- a fuse neck at every cell;
- a 400 A fuse inside the service plug, at the midpoint of the pack;
- a pyrotechnic cut-off on pack positive, triggered by the controller;
- two GX14 main contactors;
- a 220 Ω precharge resistor that brings the inverter up to 95% voltage in 0.47 s.

**HV cables:** 50 mm² shielded cable throughout, 3.3 m in total, 2.1 kg.

**BMS:** the Orion BMS2-108 works for 99 cell groups. Wire them as 9 groups of 11 cells. That also forces the service disconnect to sit between lanes 2 and 3, which is exactly where the new numbering puts it.

**12 V system:** the worst continuous load is 402 W (riding on a cold night with everything on). The 1-second peak is 1,043 W.
- A DC-DC converter rated 0.75–1 kW, plus a 0.9 kg lithium 12 V battery, covers it.
- Rule: the bike tops up its 12 V battery from the pack once a day, or a parked bike drains it in about 12 days.

**BOM:**
- **Total:** 137.6 kg, including 106.9 kg of cells.
- **Cost:** about **$8.3k per bike at 10k/yr** ($4.9k cells, $3.4k everything else) and about $22k for a one-off prototype.
- **Mass vs the roll-up:** the electrical parts other than cells weigh 2.7 kg less than the roll-up's matching allowances, because the real charger is lighter than the roll-up assumed.

**Molicel P60B fallback** (100s15p, the purchasable cell): electrically it works. It costs three things:
- a pack about 36 mm wider (five lanes of short cells);
- about 1.7 times as much cell heat at 260 A;
- 2.5 times as many cell welds.

## Verdict table

| # | Item | Value | Required | Margin | Result |
|---|---|---|---|---|---|
| 1 | Pack voltage window | 247.5–415.8 V (356 V nominal) | inside inverter 200–480 V and Orion 800 V | 64 V top / 47 V bottom | pass |
| 2 | Cell current at 130 kW peak (300 V loaded floor) | 72 A per cell (4.7C) for 30 s | 26120 rating unknown | — | **open** (no cell datasheet) |
| 3 | Busbar current density, continuous | 2.71 A/mm² (Al) | ≤ 4 A/mm² (design rule) | 1.48× | pass |
| 4 | Busbar temperature rise, 30 s at 433 A, no cooling at all | 7.7 K | ≤ 15 K | 1.9× | pass |
| 5 | Busbar temperature rise between welds, 260 A continuous | 0.10 K | ≤ 2 K | 20× | pass |
| 6 | Busbar temperature rise if the cell-side cooling path were lost (still air only) | 52 K | ≤ 60 K | 1.15× | pass, thin margin |
| 7 | Interconnect voltage drop at peak | 2.25 V | ≤ 1% (3.56 V) | 1.6× | pass |
| 8 | Interconnect loss at 260 A | 352 W (0.36% of 98 kW) | — | — | info for thermal |
| 9 | Hand check of one link's effective length | script 113.6 mm = hand 113.6 mm | agree | — | pass |
| 10 | Cell fuse neck survives the peak (adiabatic) | 91 s at 72 A | ≥ 90 s (3 × 30 s) | 1.0× | pass, sized to the limit |
| 11 | Cell fuse neck opens on a shorted cell | 17.5 ms (neighbours' necks need 438 ms) | selective by ≥ 3× | 25× | pass (model) |
| 12 | Pack short-circuit current (bolted) | 7.5 kA | pyro break 22 kA; EV fuse 20–50 kA | 2.9× | pass |
| 13 | Main contactor carry, GX14 | 260 A continuous; 433 A for 30 s | 350 A continuous | 1.35× | continuous pass; **30 s overload open** (needs GIGAVAC curve) |
| 14 | Precharge time to 95% | 0.47 s at 220 Ω, 715 µF | ≤ 0.5 s, ≤ 10 A | 1.06× | pass |
| 15 | Passive discharge to 60 V | 88 s (inverter's own 70 kΩ bleed) | active ≤ 3 s required | — | open (inverter active discharge must be specified) |
| 16 | HV cable: 30 s peak heating, 50 mm² | +15 K | ≤ 40 K | 2.6× | pass |
| 17 | HV cable: end of a 14-min fast charge, hot bay (65 °C), bundled | 111 °C | ≤ 150 °C conductor | 39 K | pass |
| 18 | HV cable: steady 260 A in the hot bundled bay | ampacity 212 A | 260 A | 0.82× | **fail if sustained**; acceptable only because 260 A is the 14-min charge (row 17) or top speed with airflow (301 A ampacity in free air) |
| 19 | Orion channels vs groups | 99 used of 108 (9 groups × 11 cells) | ≥ 4 cells and ≥ 11 V per group | 27.5 V minimum vs 11 V | pass |
| 20 | Orion rule: service disconnect at a connector boundary | MSD in link S066/S067, between connectors 2 and 3 | multiple of 36 BMS taps | — | pass (needs the lane-2 numbering reversal) |
| 21 | Cell-tap sense wires | 100 × 22 AWG UL11028, longest 1.21 m | ≤ 36 ft (Orion) | 9× | pass |
| 22 | Thermistors | 75 (67 on cells via the expansion module + 8 local) | — | — | pass |
| 23 | Creepage inside the sealed pack (PD2, MG IIIa, 500 V row) | 8 mm designed | 5.0 mm | 1.6× | pass (design) |
| 24 | Creepage inside the HV boxes (PD3) | 10 mm designed | 8.0 mm | 1.25× | pass (design) |
| 25 | Clearance (4 kV impulse, OVC II) | ≥ 5 mm designed | 3.0 mm | 1.7× | pass (design) |
| 26 | Busbar room at the cell ends | now 2 mm (outer faces) / 8 mm (between lanes) | 7.3 / 12.6 mm | **−5.3 / −4.6 mm** | **fail in current CAD** → CAD request 1 |
| 27 | Cell numbering, lane-to-lane links | current: 546 mm full-current links; proposed: 34 mm | short | — | **fail in current CAD** → CAD request 2 |
| 28 | CAD clearance, 8 HV/LV boxes + 10 routes (static) | minimum 3.0 mm (PDM to seat); all others ≥ 3.2 mm | ≥ 3 mm | — | pass (PDM marginal) |
| 29 | HV cable bend radius (3 × OD = 47 mm) | 9 bends too tight for their straight run | — | — | **fail** → formed insulated busbar at those bends (CAD request 12) |
| 30 | DC-DC rating | ≥ 0.75 kW required; 1.2 kW candidate | 1.25 × 402 W at 50 °C derating | 2.2× | pass |
| 31 | 12 V battery: limp home if the DC-DC fails | 22 min on essential loads | ≥ 15 min | 1.5× | pass |
| 32 | 12 V battery: 30 days parked without top-up | budget 3.75 mA; realistic standby 15 mA | — | — | **fail** → daily HV top-up rule |
| 33 | Non-cell electrical mass vs the roll-up | 30.7 kg vs 33.4 kg | ≤ roll-up | −2.7 kg | pass |
| 34 | Pack-internal electrical mass vs the internals allowance | 7.3 kg vs 16.3 kg | leaves room for cooling/potting | 9.0 kg left | pass |

## 1. Pack

### Topology and modules

| Level | Content | Voltage | Energy |
|---|---|---|---|
| Cell | 26120, 55 Wh, about 15.3 Ah, 180 g; DCIR **assumed** 3.0 mΩ (no public datasheet) | 2.5–4.2 V | 55 Wh |
| Group (S001–S099) | 6 cells in parallel | 2.5–4.2 V | 330 Wh |
| Sub-module (M11–M33, nine) | 11 groups in series = one Orion cell group | 27.5–46.2 V (**under 60 V DC**) | 3.63 kWh |
| Lane (three) | 33 groups = one Orion connector | 82.5–138.6 V | 10.9 kWh |
| Pack | 99s6p, 594 cells | 247.5–415.8 V | 32.67 kWh, 91.7 Ah |

Pack resistance comes to 55.6 mΩ:
- cells 49.5 mΩ;
- busbars 5.2 mΩ;
- fuse necks 0.9 mΩ.

**Heat-load note for thermal:** at 260 A the cells generate **3.35 kW** and the busbars another 0.35 kW. The cooling ribbon has to remove that during a 14-minute fast charge.

### Series numbering (CAD request 2)

The generator numbers every lane in the same snake: bottom-rear to top-front. So the lane-to-lane links (S033→S034 and S066→S067) each run **546 mm** from the top of one lane to the bottom of the next, carrying the full current.

Reversing lane 2's snake brings each lane-to-lane link down to a **34 mm** fold through the lane gap. The terminals then end up as follows:

- **Pack negative:** group S001, lane 1 outer face, bottom-rear (608, −128, 256). It is brought out through the rear wall at X590, Y−5, Z283 into the rear junction box.
- **Pack positive:** group S099, lane 3 outer face, top-front (991, 128, 595). It leaves through a lid stud at (985, 150, 614).
- **Service disconnect link S066/S067:** bottom-rear, Y0 to Y128, beside the rear junction box. It is brought out through a 2-pole pass-through at X590, Y64, Z285.

This also puts the full 139 V between lanes only across a barrier, never between neighbouring cells.

### Busbars: sweep and choice (`busbar-sweep.csv`, `busbars.csv`)

**Method:**
- Each link is modelled as a strip along the snake. Current builds up cell by cell in group g, crosses to g+1, then drains away.
- Effective length comes from summing (I/I₀)² × length. A hand check for the first in-row link gives 113.6 mm both ways.
- The sweep covers 3 materials × 2 profiles (uniform, or tapered with width following the current) × 6 thicknesses.
- **Rules:**
  - adiabatic rise over a 30 s peak ≤ 15 K;
  - rise between welds ≤ 2 K;
  - rise with still air only ≤ 60 K;
  - voltage drop at peak ≤ 1%.
- **Score:** mass plus 1 kg for every 100 W of continuous loss.

| Option (passing) | Mass | Loss at 260 A | Score |
|---|---|---|---|
| **Al 1350 tapered, 4.0 mm** | **4.66 kg** | **352 W** | **8.17** (chosen) |
| Al 1060 tapered, 4.0 mm | 4.66 kg | 354 W | 8.20 |
| Al 1350 uniform, 3.0 mm | 6.45 kg | 323 W | 9.68 |
| Cu C11000 tapered, 2.5 mm | 9.64 kg | 346 W | 13.1 |
| Cu C11000 uniform, 2.0 mm | 14.25 kg | 298 W | 17.2 |

Copper is two to three times heavier for the same loss. Each link: 24 × 4 mm full section, about 336 mm long, about 47 g, 52–55 µΩ.

**Joining:**
- Each cell end is fiber-laser welded to a **0.30 mm nickel-plated copper fuse-collector plate**. Both cell ends get one.
- The collector is ultrasonically welded to the aluminium busbar, using a Cu-Al clad tab where needed.
- Laser-welding aluminium straight onto the nickel-plated steel cell can is avoided, because it forms brittle intermetallic compounds.
- 0.5 mm polyimide film covers every busbar.

**Per-cell fusing:**
- The neck in the collector is 8.1 × 0.30 mm (2.44 mm²), 4 mm long, about 28 µΩ, and loses 0.15 W at 72 A.
- It was sized with the Onderdonk adiabatic melting formula.
- It survives 91 s at the peak current.
- On a shorted cell, the five healthy cells in its group push about 5.2 kA through its neck, which opens in about 17.5 ms. Each neighbour's neck sees only about 1 kA and would need 438 ms to melt, so they survive.
- That 5.2 kA depends on the assumed 3 mΩ cell resistance (open item).

**Room needed at the cell ends** (collector 0.3 + busbar 4.0 + film 0.5 = 4.8 mm per face):

| Location | Now | Needed | Needed = |
|---|---|---|---|
| Outer faces | 2 mm | 7.3 mm | face stack + 1.0 mm compliance + 1.5 mm for tap fuses |
| Between lanes | 8 mm | 12.6 mm | two face stacks + 1 mm barrier + 2 mm sense-wire channel |

## 2. BMS (Orion BMS2-108)

**Channels:** 3 connectors × 3 cell groups × 12 taps. We fill 11 taps per cell group (S001–S011 → cell group 1, and so on), and tie the 12th tap to the group's top cell, as the Orion wiring manual requires. The **negative-most lane goes on connector 1**, because Orion's isolation check measures from tap 1−.

Orion spec sheet:
- 0.25% voltage error;
- 200 mA passive balancing;
- 2.5 kVrms isolation between connectors;
- 8 thermistor inputs;
- built-in isolation-fault detection;
- 1.47 kg with heatsink.

**Sense harness** (`bms-tap-map.csv`):
- 100 wires, 22 AWG UL11028 (600 V, 105 °C), 83 m in total, longest 1.21 m.
- The taps are welded tabs on each group's positive busbar. Each tap has a **Bel Fuse 0ACG-2000-TE** fuse (2 A, 500 VDC, AEC-Q200) right at the busbar, inside Orion's ≤ 5 A limit.
- **Routing:** inside the pack, along the lane-gap channels and outer faces, in PA clips 10 mm from the busbar edges. Out through three sealed pass-throughs on the pack lid near X700, Z613. Then up the rear of the tank stack to the Orion unit at X775–1017, Z820–893, kept away from the phase cables.

**Thermistors** (`thermistor-map.csv`): 75 in total, all 10 k NTC.

| Where | Count | Input |
|---|---|---|
| Lane 2 (sandwiched, runs hottest): mid-group can at the busbar end | 1 per group = 33 | Orion thermistor expansion module (80 channels) |
| Lanes 1 and 3: mid-group can at the busbar end | 1 per two groups = 34 | expansion module |
| Pack + and − terminals, MSD link, lane link, coolant in, coolant out, BDU air, pack air | 8 | Orion local inputs, so they keep reading if the expansion module drops off CAN |

**Isolation monitoring:** the primary monitor is a **Bender ISOMETER iso175C-32-SS**, set to 500 kΩ warning and 100 kΩ fault, on the HV bus. The Orion's own circuit is a plausibility cross-check. During DC charging, the charging station's insulation monitor and the bike's must be coordinated: the bike's iso175 pauses while the station is measuring.

## 3. HV distribution, protection and cables

### Architecture

See the `electrical/schematic.png` / `.svg` block diagram; Mermaid source is in `schematic.mmd`.

**Rear junction box (RJB):** the existing HV cabinet envelope, X445–580, Y−20…95, Z245–398, sealed IP67 with a drain. It holds:
- the pack-negative GX14 contactor;
- the **Isabellenhütte IVT-S-500-U3-I-CAN2-12/24** shunt sensor (current, plus U1 pack voltage, U2 bus voltage, U3 inlet voltage);
- the **Amphenol MSD08** fused service disconnect (400 A fuse, built-in interlock), in link S066/S067.

**Upper battery disconnect unit (BDU):** new box, X606–686, Y−125…82, Z645–765. It sits behind the tank rear wall (X690–693), directly behind the inverter and charger rear faces. It holds:
- **Sensata STP500P** pyrotechnic cut-off (500 A continuous, 22 kA break at 500 V, under 1 ms);
- GX14 pack-positive contactor;
- **TE Kilovac LEV100** precharge relay with a **TE/CGS HSC100 220 Ω** resistor;
- Eaton Bussmann EV branch fuses: 30 A charger, 10 A DC-DC, 15 A pack heater;
- the HV+ and HV− distribution bars.

**Charge junction box (CJB):** new box, X730–860, Y116–176, Z640–760, in the right-hand pocket beside the charger. It holds:
- 2 × GX14 DC charge contactors;
- a 2-pole AC relay pair (2 × LEV100) feeding the onboard charger, mechanically and electronically interlocked with the DC contactors.

This is the "AC/DC routing" function that `electrical-design.md` left open: NACS uses the same two pins for AC and DC charging.

**Inlet:** **Volex NACS 1000 V inlet**, rated 500 A continuous, UL 2251 and SAE J3400, 84 × 68 × 95 mm, with a 100 k NTC on each power pin. It sits on the right tank flank at X860–928, Y127–222, Z845–929, under a hinged door. A NACS-to-CCS1 adapter on the cable side covers CCS stations.

**Charge controller:** ADVANTICS ADM-CS-EVCC, which handles the NACS/CCS protocol, the inlet lock and the temperature inputs.

### Protection coordination

| Fault | Cleared by | Why it works |
|---|---|---|
| Internal cell short | fuse neck | about 17 ms, selective (rows 10–11) |
| Bolted pack short, 7.5 kA | 400 A MSD fuse plus pyro | fuse breaks 20–50 kA; pyro 22 kA |
| Medium faults, 600 A–3 kA (fuse slow) | pyro, fired by the controller from the IVT-S | thresholds: > 650 A for 20 ms, or > 480 A for 40 s |
| Crash | pyro + contactors | IMU crash flag from the ABS unit, under 20 ms |
| Normal / BMS open request | GX14 | opened only below 350 A; higher currents are the pyro's job |
| Branch cable faults | EV fuses 30/10/15 A | — |

Steady loads against the main fuse:
- the 433 A, 30 s peak is 1.08 × the 400 A fuse rating, below the usual EV-fuse no-blow level of about 1.3×;
- 260 A continuous is under 320 A (the fuse with a 0.8 thermal derating).

Both still need confirming on the real fuse curve.

### Precharge and discharge

Total DC-link capacitance: **715 µF**. That is 650 µF for the CM200 reference inverter, plus estimates of 20 µF for the DC-DC, 40 µF for the charger and 5 µF for Y-caps and cable.

| Resistor | 47 Ω | 68 Ω | 100 Ω | 150 Ω | **220 Ω** | 330 Ω |
|---|---|---|---|---|---|---|
| Time to 95% | 0.10 s | 0.15 s | 0.21 s | 0.32 s | **0.47 s** | 0.71 s |
| Starting current | 8.8 A | 6.1 A | 4.2 A | 2.8 A | **1.9 A** | 1.3 A |
| Starting power | 3.7 kW | 2.5 kW | 1.7 kW | 1.15 kW | **0.79 kW** | 0.52 kW |

220 Ω is the lowest-stress option that still precharges within 0.5 s. Energy per precharge is 62 J.

**Precharge rule:** close the main positive contactor only when the bus voltage is within 21 V of the pack. If it isn't after 3.2 time constants (0.5 s), abort and latch. That caps the energy the resistor absorbs when precharging into a shorted bus at 396 J; TE still has to confirm the resistor's pulse rating.

**Discharge:**
- **Passive:** the inverter's 70 kΩ bleeder takes **88 s** to reach 60 V.
- **Active:** we require the inverter's active discharge to get below 60 V within 3 s. ISO 6469-3 and R136 require below 60 V DC or 0.2 J, within a time the manufacturer states.

### HV cables (`hv-cables.csv`)

**Cable:** **Coroplast Coroflex FHLR2GCB2G 50 mm² shielded** (9-2611): 0.368 mΩ/m, about 630 g/m, OD about 15.8 mm, 600 V AC / 1000 V DC, minimum bend radius 3 × OD static.

**Gauge sweep, hot bundled case** (65 °C bay, pair in conduit; free air at 40 °C in brackets):

| Gauge | Ampacity | Rise in 30 s at 433 A | Temperature after a 14-min charge |
|---|---|---|---|
| 35 mm² | 161 A (230 A) | 33 K | 152 °C (fail) |
| **50 mm²** | **212 A (301 A)** | **15 K** | **111 °C (pass)** |
| 70 mm² | 262 A (372 A) | 8 K | 91 °C |

50 mm² is chosen because 260 A is only ever a 14-minute fast charge or top speed with airflow (verdict row 18). Phases use 50 mm² too: about 260 A rms continuous at top speed, 400 A peak.

**Connectors:** Amphenol **PowerLok 300**. PL282X plugs (300 A, 50 mm², 1 kV) with shielded backshells, and PL082X receptacles with interlock contacts.

**Routes** (static clearance check against the saved model, FreeCAD `distToShape`):

| Route | Gauge | Length each | Min. gap | Nearest part |
|---|---|---|---|---|
| Pack + lid stud → BDU (right-side channel Y186, under the radiator, then in below the BDU) | 50 | 640 mm | 4.2 | seam trim |
| Pack − (S001) → RJB | 50 | 108 mm | 36 | motor |
| HV− bus RJB → BDU (left channel X574–640, Y−100…−135, behind the stepped pack face) | 50 | 602 mm | 3.7 | pack case |
| MSD links S066/S067 → RJB | 2 × 50 | 103 mm | 40 | — |
| Inverter DC± (BDU → inverter, bulkhead through tank wall) | 2 × 50 | 112 mm | 5.9 | charger |
| Motor U/V/W (inverter rear → motor top-right terminal) | 3 × 50 | 240 mm | 7.5 | charger |
| DC charge ± inlet → CJB | 2 × 50 | 230 mm | 6.2 | PDM |
| DC charge ± CJB → BDU | 2 × 50 | 182 mm | 3.2 | charger |
| Charger DC out → BDU | 2 × 4 | 105 mm | 40 | — |
| DC-DC HV in | 2 × 4 (2.5 is enough) | 138 mm | 7.1 | charger |

**Total:** 3.3 m of 50 mm², 2.1 kg. Worst voltage drop at peak is 0.13 V.

**Bends:** nine bends cannot reach a 47 mm radius within their straight runs. They are:
- the pack-positive stud exit and the BDU entry;
- three bends in the HV− channel at Z260–330;
- two phase bends;
- the CJB→BDU bend.

Make those short pieces as **formed, insulated Al 1350 busbars** (for example 6 × 25 mm, heat-shrink plus PA sleeve), or as pre-formed cable stubs with bolted joints.

## 4. 12 V system (`lv-loads.csv`, `lv-harness.csv`, `lv-system.json`)

**Load cases:**

| Case | Load | Main contributors |
|---|---|---|
| A: night, cold, riding | 402 W | lights 102 W, grips + seat 80 W, pumps/oil 108 W |
| B: hot weather, DC fast charge | 325 W | fans 130 W, pumps 90 W |
| C: 1-second peak | 1,043 W | adds ABS pump 300 W, horn, contactor pull-in, steering lock, screen motor |

**DC-DC sweep** (usable = 0.9 × rating at 50 °C; needs ≥ 25% margin over 402 W):

| Rating | Margin | 12 V battery assist at peak | Result |
|---|---|---|---|
| 0.5 kW | 12% | 44 A | fail |
| **0.75 kW** | **68%** | **27 A** | **pass (minimum)** |
| 1.0 kW | 124% | 11 A | pass |
| 1.5 kW | 235% | 0 | pass |

**Specification:** ≥ 0.75 kW continuous, 1 kW class, isolated, CAN, IP67, liquid- or passively cooled, inside a **230 × 60 × 140 mm** envelope. The candidate is the HELLA high-voltage DC/DC (400 V → 12 V, 220–470 V input, 1.2 kW passively cooled, **2.8 kg**). That is 1.6 kg over the roll-up's 1.2 kg allowance. Its envelope still has to be confirmed against the 60 mm-wide pocket. The roll-up's "1 kW" is right in size and too optimistic in mass.

**12 V battery:** Shorai LFX14A4-BS12 (LiFePO4, 4.5 Ah, 59.4 Wh, 210 CCA, 0.90 kg), under the seat.
- **Limp home** if the DC-DC fails: 22 min.
- **Standby:** with 15 mA of keyless + telematics standby, a parked bike flattens the battery in about 12 days. Rule: the controller wakes once a day, closes the contactors and tops the 12 V battery up from the pack for about 10 minutes.

**LV harness:**
- Wire: FLRY-B, ISO 6722-1. Sized for bundled ampacity at 60 °C with 1.25× margin, and voltage drop ≤ 3% for lamps and motors, ≤ 5% for the rest.
- Feeds:
  - DC-DC → distribution box: 16 mm² (1.5% drop), 150 A MIDI fuse;
  - battery → distribution box: 10 mm², 100 A MIDI fuse;
  - ABS pump: 4 mm², 30 A;
  - fans: 1.0 mm², 15 A;
  - everything else: 0.5 mm² on smart-fused channels of 2–7.5 A.
- Copper: 1.05 kg; about 2.4 kg finished, which is under the roll-up's 3.0 kg.
- Connectors: TE/Deutsch DT/DTM, sealed.
- Bonding: 6 mm² straps from every HV housing to the frame, under 0.1 Ω.

**Distribution:**
- Prototype: ECUMaster PMU16 smart distribution box (16 electronically fused outputs, 1.15 kg, about $1.4k), bench-mounted.
- Production: a custom 90 × 40 × 80 mm smart distribution unit in the right upper pocket.
- VCU: AEM EV VCU200 (part 30-8000; 4 CAN buses, IP6K7) as the prototype controller, in the left upper pocket.

**CAN:**
- **CAN1, powertrain, 500 k:** VCU, inverter, BMS, IVT-S, DC-DC, charger, EVCC, iso175.
- **CAN2, chassis, 500 k:** VCU, Bosch MSC/ABS, TFT dash, keyless, distribution box, telematics, BMS CAN2.
- Wiring: both are linear buses with 120 Ω split terminations at the two physical ends, stubs under 0.3 m, and 0.35 mm² twisted pair.

**Keyless and start sequence:** proximity fob with LF wake → keyless module → VCU immobiliser challenge (VCU ↔ inverter). To start:
1. Fob present, side-stand up, brake held, start pressed.
2. VCU checks BMS OK, isolation OK and the interlock loop closed.
3. Precharge.
4. Main positive closes.
5. READY lamp.

## 5. Insulation coordination and HV safety

**IEC 60664-1 basis:**
- Working voltage 416 V DC, so the **500 V rows** are used, with no interpolation credit.
- The bike connects to the charging station during DC charging, so it is treated as **OVC II, 600 V class → 4 kV impulse**.
- Clearance required: **3.0 mm** (Table F.2).
- Creepage required (Table F.5, MG IIIa): **5.0 mm** at PD2 (inside the sealed pack), **8.0 mm** at PD3 (HV boxes, where condensation is possible).
- Designed values: 8 mm in the pack, 10 mm in the boxes, ≥ 5 mm clearance (`insulation-coordination.csv`).

**ISO 6469-3 / UNECE R136 items:**

| Item | Design |
|---|---|
| Isolation resistance ≥ 100 Ω/V on the DC side, ≥ 500 Ω/V while the AC charger is connected | iso175 warns at 208 kΩ and faults at 41.6 kΩ minimum, set to 500 k / 100 k |
| Protection against direct contact | IPXXD on all HV boxes, with tool-only lids |
| Equipotential bonding | under 0.1 Ω |
| Interlock loop | one 20 mA PWM loop through the MSD, BDU, CJB, inverter, charger, DC-DC and inlet |
| Marking | orange cables, ISO 7010 W012 labels |
| Unplugged inlet must be dead | DC contactors weld-checked through IVT-S U3 before the inlet unlocks |
| Post-crash isolation | pyro fired automatically |
| Driving-state indication | READY lamp, side-stand interlock |

**IP67 sealing points:**
- the pack lid gasket;
- 3 sense pass-throughs plus 2 power pass-throughs;
- the RJB lid and drain;
- the BDU lid and its tank-wall bulkhead;
- the CJB lid;
- every PowerLok mating pair (IP67 when mated);
- the inlet (IP67 unmated, IP44 mated, per the Volex sheet);
- the MSD;
- breathers: GORE PolyVent on the pack and on each HV box.

**EMC:**
- shielded HV cables with 360° shield terminations at both ends;
- a nanocrystalline common-mode ferrite over the inverter DC pair at the BDU exit;
- phase cables kept under 0.3 m;
- CAN routed more than 50 mm from the phases.

Targets: UNECE R10.06, and CISPR 25 class 3 for the onboard radios.

## 6. BOM (`electrical-bom.csv`, `electrical-bom-summary.json`)

| Area | Main parts | kg | $ proto | $ at 10k/yr |
|---|---|---|---|---|
| Cells | 594 × 26120 (EVE / Wanxiang A123, Stark platform) | 106.9 | 6,861 | 4,900 |
| Pack internals | Al 1350 busbars, Ni-Cu fuse collectors, films, Orion BMS2-108 + expansion module + 75 NTCs, 83 m tap harness, 100 × Bel 0ACG-2000-TE, pass-throughs | 8.7 | 3,605 | 660 |
| Protection | MSD08, STP500P, 4 × GX14, 3 × LEV100, HSC100, Eaton EV fuses | 3.4 | 1,860 | 631 |
| Sensing | IVT-S-500-U3-I-CAN2-12/24, Bender iso175C-32-SS | 0.35 | 700 | 240 |
| Enclosures | BDU, RJB, CJB | 2.2 | 900 | 170 |
| HV harness | 3.3 m Coroflex 50 mm², 10 PowerLok 300 halves, lugs and conduit | 3.7 | 1,003 | 313 |
| Charging | Volex NACS inlet, ADVANTICS EVCC, BROGEN PV1776 charger | 4.1 | 2,400 | 620 |
| 12 V | HELLA DC/DC, Shorai LFX14A4, AEM VCU200, ECUMaster PMU16 → custom distribution box, LV harness, keyless, bonding | 8.2 | 4,655 | 770 |
| **Total** | | **137.6** | **≈ 21,980** | **≈ 8,300** |

Prices at volume are planning estimates (sources in the CSV), not quotes.

**Mass against the roll-up:** the non-cell electrical items total **30.7 kg**, against **33.4 kg** for the roll-up lines they replace (−2.7 kg).
- Charger: −3.5 kg (3.0 kg catalogue vs the roll-up's 6.5 kg estimate).
- DC-DC: +1.6 kg.
- HV cables plus connectors: +1.5 kg.
- New parts the roll-up didn't have: CJB, pyro, EVCC, inlet, VCU and distribution box.

## 7. Alternative: Molicel P60B 21700, 100s15p (purchasable fallback)

**Pack summary:** 1,500 cells, 32.4 kWh, 360 V nominal / 420 V maximum, 90 Ah, 105 kg of cells.
- Mass assumes 70 g per cell (P50B class); no P60B mass was found.
- Cell data: Molicel launch release ([source](https://en.prnasia.com/story/494251-0.shtml)): 6.0 Ah, 12.8 mΩ, 5C charge.

**What stays the same:**
- **Peak current:** 433 A at 130 kW. That is 28.9 A per cell, comfortably inside a 21700 power cell's rating, and less per cell than the 26120 design (72 A).
- **Fast charge:** 10–80% in about 14.5 min at the 5C cell limit, which matches the 26120 plan.
- **Orion BMS2-108:** 100 groups wire as 34 / 33 / 33 per connector (cell groups 12 / 11 / 11, then 11 / 11 / 11 twice), so the MSD can still sit at a connector boundary.
- **Everything outside the pack:** contactors, cables, BDU/RJB/CJB, inlet and the whole 12 V system are unchanged. The voltage window (250–420 V) is almost identical.

**What changes:**
- **Width:** the cells are 70 mm long, so the pack needs **5 transverse lanes**. Inner width becomes 415 mm and outer about 423 mm: **+35 mm** over today's 388 mm, and +15 mm over the widened 26120 pack.
- **Side-view area:** needs about 137,000 mm² per lane, against 134,000 mm² today (+2%).
- **Cell heat at 260 A:** 85 mΩ cell resistance gives **5.8 kW**, against 3.35 kW for the 26120. The cooling system has to handle about 70% more during fast charging.
- **Short circuit:** falls to 4.6 kA. That makes life easier for the protection.
- **Welds:** **3,000 cell-end welds** against 1,188. Still need a fuse neck per cell: 15 cells now feed a shorted one.
- **Verdict:** a workable bridge for prototypes and early builds. The 26120 remains the better production point, if a supplier quotes it.

## CAD change requests

All coordinates are saved-model (subtract 40 for generator Z). Numbers 1 and 2 are in `build-adventure.py`'s pack section; the rest are new objects.

1. **Busbar room:**
   - Change `LANES=(-128.0,0.0,128.0)` to **(−132.6, 0.0, +132.6)** (lane gap 8 → 12.6 mm).
   - Change the outer end gap from 2 → **7.3 mm**. That makes YI = **199.9**, YO = **203.9** (was 194).
   - Pack outer width 388 → **408 mm**.
   - Knock-on: the lower body covers (now Y±205–210) and the belly side panels (±205) must move out about 10 mm per side, to ±215–220. The lower covers' clearance to the front tyre and steering sweep needs re-checking.
2. **Cell numbering:** reverse lane 2's snake (`seq=seq[::-1]` for `li==1` in the cellmap loop), so S034 starts at lane 2's top-front and S066 ends at its bottom-rear.
3. **Pack terminals and pass-throughs:**
   - pack-positive lid stud at (985, 150, 614), M8, insulated;
   - pack-negative rear-wall pass-through at X590, Y−5, Z283;
   - MSD 2-pole pass-through at X590, Y64, Z285;
   - three sense-harness pass-throughs on the lid at X700, Y −128 / 0 / +128, Z613.5.
4. **RJB:** keep the existing `HV_cabinet_2mm_STUDY` envelope (X445–580, Y−20…95, Z245–398).
   - The `GX14_main_negative` slot stays.
   - The `GX14_main_positive` slot becomes the IVT-S shunt (about 90 × 60 × 40).
   - `Main_fuse_branch_search_region` becomes the MSD08 (needs Y48–95; size still to confirm from the Amphenol drawing).
   - Add a pull-handle access door on the left (−Y) face.
5. **BDU:** new box X606–686, Y−125…82, Z645–765. Cut-outs in the tank rear wall (X690–693):
   - **Y−60…−20, Z705–745** for the inverter DC bulkhead;
   - **Y105–135, Z700–750** for the phase grommet.
6. **CJB:** X730–860, Y116–176, Z640–760.
7. **NACS inlet:** box X860–928, Y127–222, Z845–929. Opening in the right fairing flank, about 90 × 75 mm, centred near (894, 225, 887), with a hinged door and drain.
8. **DC-DC:** envelope X720–950, Y−180…−120, Z622–762 (left pocket beside the charger).
9. **12 V battery:** X512–599, Y−75…75, Z670–763, under the seat front. This replaces the roll-up's X300/Z720 location, which sits in the rear-tyre bump zone.
10. **VCU:** X770–950, Y−150…−110, Z785–863. **Distribution box:** X765–855, Y108–148, Z785–865. It has only 3.0 mm to the seat; lower its top by 5 mm if the seat pan moves.
11. **Motor:** the IPM spec gets a phase terminal box on the top-right of the motor at (598, 100, 648), connectors facing up and forward. It goes into the motor specification.
12. **HV routes:** the polylines in `hv-cables.csv` (column `points_saved_coords_mm`). Model them as 15.8 mm tubes; for 2- and 3-cable bundles use about 25 mm. The nine short bends flagged in section 3 become formed insulated busbars.
13. **Mass roll-up updates:**
    - charger 6.5 → 3.0 kg;
    - DC-DC 1.2 → 2.8 kg;
    - HV cables and lugs 2.2 → 3.7 kg;
    - GX14 0.45 kg × 4;
    - add BDU 0.9 kg, CJB 0.5 kg, inlet 0.9 kg, VCU 0.4 kg, distribution box 0.5–1.15 kg.

## What this does not prove

- **The 26120 cell is unspecified.** Its resistance (3 mΩ assumed), terminal layout (positive cap at one end, negative can at the other, as in the CAD), tab metallurgy, current ratings and swelling are all assumptions. The fuse-neck fault current, the short-circuit current and the cell heat all scale with that resistance.
- **The busbar thermal model is a bound, not a simulation.** The fuse necks use Onderdonk's adiabatic formula: conservative for surviving the peak, optimistic for how fast they open. No pack-level thermal or FEA model was run. Weld resistance is not included.
- **The cable thermal model is a single-cable heat balance** with an assumed h = 11 W/m²K and a bundling factor. The 14-minute charge result depends on those, and on the cable starting at ambient temperature.
- **Clearances are static only.** No swingarm or steering sweep was run against the new cable routes; the HV− channel passes about 16 mm from the left rear pack link. Vibration, chafe and service access were not checked.
- **Part sizes not verified from drawings:** MSD08, STP500P, IVT-S and the HELLA DC/DC. Not found in a source: the GX14's 30 s overload rating, the HSC100's pulse rating, the main fuse curve and the P60B's mass. The precharge capacitance includes estimates for the DC-DC and charger.
- **Not designed here:** firmware, the safety concept (FMEA / ISO 26262 or ISO 13849-style), interlock logic, charging conformance (J3400 / DIN 70121 / ISO 15118) and EMC. Nothing was tested, and Tesla network access is still unestablished.
- **Insulation coordination is design intent,** not a measured creepage audit of real parts.
- **The LV load list is estimated from typical parts.** In particular, ABS pump current, radar and telematics standby are not from datasheets.
- **Costs are planning estimates,** not quotes.

**Sources:**
- Orion BMS2 [product page](https://www.orionbms.com/products/orion-bms-standard/), [spec sheet](https://www.orionbms.com/downloads/documents/orionbms2_specifications.pdf), [wiring manual](https://www.orionbms.com/manuals/pdf/orionbms2_wiring_manual.pdf)
- [Volex NACS inlet](https://www.volex.com/media/z3rmrwl5/volex-nacs-ev-charging-inlet.pdf)
- [Amphenol NACS catalogue](https://www.amphenol.co.jp/military/catalog/NACS.pdf)
- [Amphenol MSD08](https://www.amphenol.co.jp/military/catalog/MSD08_Datasheet.pdf)
- [TE AMP+ MSD](https://www.te.com/usa-en/products/connectors/automotive-connectors/intersection/amp-manual-service-disconnect.html)
- [Sensata pyrofuse](https://www.mouser.dk/new/sensata/sensata-a-plus-p-pyrofuse-circuit-breakers)
- [GIGAVAC GX14 listing](https://www.digikey.fr/en/products/detail/sensata-gigavac-clean-energy/GX14CBB/17867714)
- [Isabellenhütte IVT-S](https://www.isabellenhuette.com/hubfs/Files/Data-sheets/IVT-S.pdf)
- Bender [iso175](https://www.bender.de/fileadmin/content/Products/d/e/iso175_D00415_D_XXEN.pdf) and [IR155](https://www.bender.de/en/products/insulation-monitoring/isometer-ir155-3203-ir155-3204/)
- Eaton [EV fuses](https://images.eaton.com/my/en-us/catalog/emobility/ev-fuses.html)
- Coroflex [50 mm² sheet](https://media.iewc.com/SpecificationSheets/Coroflex-FHLR2GCB2G_50MM.pdf)
- [Amphenol PowerLok PL282X](https://uk.rs-online.com/web/p/ev-connectors/0560792)
- [Bel Fuse 0ACG-2000-TE](https://www.belfuse.com/products/circuit-protection/fuses/0acg-2000-te)
- [HELLA HV DC/DC](https://www.hella.com/soe/en/Products/Product-detail-4957/?pid=6342)
- [Shorai LFX14A4](https://www.revzilla.com/assets/0001/3958/shorai_specs_and_dimensions.pdf)
- [AEM VCU200](https://documents.aemelectronics.com/techlibrary_aemev_vcu200_product_description_revg.pdf)
- [ECUMaster PMU16](https://ecumasterusa.com/products/ecumaster-pmu16-power-management-unit)
- [Stark/EVE 26120](https://enduro21.com/en/news/industry-news/stark-future-partners-with-eve-energy-for-next-generation-battery-cells)
- [Molicel P60B release](https://en.prnasia.com/story/494251-0.shtml)
- Standards (not quoted): IEC 60664-1 Tables F.1/F.2/F.5, ISO 6469-3, UNECE R136, SAE J3400, UL 2251.
