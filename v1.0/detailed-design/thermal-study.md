# Bavuso V1.0 detailed design: thermal study

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5). Runs finished early on November 13.

Scripts: `detailed-design/tools/thermal-*.py`. Raw outputs and plots: `detailed-design/thermal/`.

## The plain answer

**The pack needs liquid cooling. The rest of the system is ordinary.** Here is the design:

- **Pack cooling.** Six thin aluminium cooling ribbons snake between the cell rows, Tesla-style. Every cell touches one ribbon. Air cooling cannot work here. A 10–80% fast charge puts 4–6 kW of heat into the cells. The sealed aluminium case can only pass about 0.05–0.15 kW to the air.
- **Two coolant loops.**
  - A **battery loop**: the ribbons, a 5 kW electric heater, a pump and one radiator.
  - A **drive loop**: the inverter, then the charger and DC-DC plate, then the gearbox and motor oil cooler, then the second radiator.
- **A shared-radiator valve.** One valve hands *both* radiators to the battery while it fast-charges, because the motor is idle then.
- **Radiators.** One radiator sits each side of the tank, 210 × 140 mm, each with a 190 mm fan. **They need small side pods on the shroud** (±315 mm wide, like a KTM 1290 Super Adventure). The space reserved in today's body only fits a third of the area needed.
- **No air-conditioning chiller in the base bike.**
- **Added cost and mass:** about **17.8 kg and about $1,035 per bike at 10k/yr** (about $1,650 at 1k/yr). That is about +7.7 kg and +$500 over the current mass and cost allowances.

What the models say, at 35 °C ambient unless noted:

| Case | Result |
|---|---|
| (a) 70 mph to empty | Trivial. Cells rise less than 1 K. Motor winding about 56 °C. Range 181 min (211 mi) at CdA 0.40; 169 min (197 mi) at 0.44. |
| (b) 8 full-power 0–125 mph sprints | Fine. Winding peaks at 122 °C, inverter junction at 82 °C, hottest cell at 41 °C. |
| (b) held at top speed (146 mph) | **The motor derates after about 4 minutes** (140 mph: about 6 min). **130 mph can be held** (winding 145 °C); 135 mph is at the edge (165 °C). 125 mph: 128 °C. |
| (c) 1,800 m mountain climb, 40 hairpins at full power, then a regen descent | Fine. Winding 99 °C, hottest cell 39 °C. |
| (d) DC fast charge 10–80% at 35 °C | **18.9 minutes** (14 min is the cell's limit). The hottest cell core peaks at 51.7 °C against a 55 °C limit. At 25 °C ambient it takes 14.8 min; at 45 °C, 30.7 min. |
| (d) DC fast charge at 0 °C, cold-soaked | **Fails without a heater:** only 48% after 3 hours, because cells must not be fast-charged cold. With the 5 kW heater it takes **20.9 min**. If the bike preheats on the way to the charger, **14.6 min**. |

**Why no chiller:** a 2 kW chiller would cut the 35 °C charge from 19 to 15 min. It costs about $600–900 and 5–7 kg. The program requirement is 25 minutes, so the chiller is a "hot-climate pack" option, not base equipment.

**The one real flag is top speed.** With the supplier spec as written, 146 mph is a time-limited sprint, not a cruise. Either accept that (Energica and Zero also derate), or add "70 kW continuous at 16,000 rpm" to the motor RFQ.

**Fire safety.** A cell going into thermal runaway does not set off its neighbours while coolant flows. If the coolant is lost (a crash, a pump fault), the neighbours reach 120–160 °C. That is marginal. The main path between cells is the copper busbar, not the gap between them. So the spec asks for:
- fusible single-cell links;
- intumescent foam in the gaps;
- mica liners;
- a vent channel to a burst vent at the rear of the pack.

## Inputs taken from the repo

| Item | Value used | Source |
|---|---|---|
| Cells | 594 × 26120-class cylinders (26 × 120 mm), 99s6p, 55 Wh and 15.3 Ah each, 180 g. 32.7 kWh, 416 V full | `build-adventure.py` (CELL_* constants), `cell-placement-adventure.csv` |
| Pack layout | 3 lanes across the bike (Y −128/0/128), cells hex-packed in side view at 28 mm pitch (2 mm gaps), 15 rows in 8 two-row bands. Rows 11–17 cells long, X 595–1083, Z 243–608 (saved model). 4 mm case in CAD (the brief says 3 mm; both checked) | `build-adventure.py` lines 97–187, `geometry-adventure-audit.json` |
| Max charge rate | 3C, 10–80% in 14 min (about 98 kW) | `tools/powertrain-cost-down.py` (`chg_c=3.0`), `powertrain-cost-down.md` |
| Motor | Radial IPM, oil-cooled hairpin, 150 Nm, 130 kW from 8,300 to 16,000 rpm, 85–90 kW continuous, 14 kg | `drive-study.md` supplier spec |
| Reduction | 2 stages, 7.8:1 (helical gear about 2.4, then belt about 3.1), output on the pivot | `drive-study.md` |
| Inverter | 400 A peak SiC, about 6.5 kg (CM200 envelope still in CAD) | `drive-study.md`, `components-electrical.csv` |
| Charger / DC-DC | BROGEN PV1776 6.6 kW on-board charger (`electrical-design.md`); isolated DC-DC unselected | `components-electrical.csv` |
| Vehicle | 287.2 kg + 85 kg rider (+40 kg luggage in case c), CdA 0.40 (0.44 checked), Crr 0.015, 0.305 m rolling radius | `mass-rollup.md`, `aero-baseline-report.md`, `drive-study.md` |
| Space | Side radiator reservations X960–1070, Y±128–178, Z640–780 (saved); side grilles X1000–1140, Z650–770; charger X700–1073, Y±112, Z630–706; inverter Z715–812; upper rails Y±179–211 | saved `cad/Bavuso-V1.0-adventure.FCStd` |

**Note.** `electrical-design.md` still describes the old 100s7p Amprius pack and EMRAX 208, and `components-electrical.csv` does too. Both are stale against the adventure model. This study uses the CAD's 99s6p 26120 pack and the IPM drive.

## Prior art

| Bike or part | Cooling approach | What I took from it |
|---|---|---|
| Energica Ego (EMCE generation) | Motor and inverter share one liquid loop with a front radiator; the battery is air-cooled through finned casings ([epaddock technical](https://www.epaddock.it/en/technical-energica-ego-rs/), [Visordown on EMCE](https://visordown.com/news/industry/lighter-liquid-cooled-more-powerful-new-energica-emce-motor)) | One drive loop is normal. Energica's air-cooled pack is why it charges slowly (about 1C). Bavuso's 3C target rules that out. |
| Stark Varg (EVE 26120) | Aluminium-can 26120 cells, chosen for thermal conductivity and mass ([Enduro21](https://enduro21.com/en/news/industry-news/stark-future-partners-with-eve-energy-for-next-generation-battery-cells), [The Pack](https://thepack.news/stark-future-signs-new-strategic-partnership-with-eve-energy)) | This is the same cell class; the aluminium can helps side cooling. Stark has published no internal resistance. |
| Tesla 2170 module cooling ribbon | Serpentine extruded multiport tube bonded along the sides of the cell rows | Copied as the pack-cooling concept. |
| Molicel P50B 21700 | 5 Ah, **12.8 mΩ DC impedance at 50% SOC**, charges up to 60 °C ([datasheet](https://www.fsaeonline.com/content/Molicel-TDS--INR-21700-P50B-80122.pdf)) | Anchor for cell resistance: scaled to 15.3 Ah it gives 4.2 mΩ. I use 5.0 mΩ to cover the slow (diffusion) part of the voltage loss over a minutes-long charge. |
| Jelly-roll conductivity | Across the layers it is about 100× lower than along them ([Drake et al., *J. Power Sources* 252, 2014](https://mavmatrix.uta.edu/mechaerospace_dissertations/19); a 4680 model swept 0.9–2 W/mK radially, [Research Square](https://www.researchsquare.com/article/rs-11158435)) | k across layers 0.6 W/mK (0.2 and 1.0 checked), k along layers 25 W/mK. |
| Pump | Pierburg CWA50: about 25 L/min at 0.53 bar, 24 L/min / 0.6 bar max, under 6.5 A at 12 V ([tecomotive datasheet](https://tecomotive.de/download/datasheets/CWA50_EN.pdf), [Rheinmetall](https://www.rheinmetall.com/de/produkte/thermal-management/water/cwa_50)) | Pump class for both loops. |
| Fan | SPAL 7.5 in puller, 366–437 CFM free air ([BimmerWorld SPAL comparison](https://www.bimmerworld.com/SPAL-electric-cooling-fan-technical-info-specs-comparison-BMW.html), [JJ Motorsports listing](https://jj-motorsports.com/7-5in-puller-fan-straight-blade-437-cfm-spa30100394)) | I take about 60% of free-air flow through the core: about 3.2 m/s across the face at idle. |
| SiC power module | Infineon HybridPACK Drive G2 750 V / 620 A, Rds(on) about 2.2 mΩ max (distributor listing, [RS](https://se.rs-online.com/web/p/mosfets/0349030)) | 1.7 mΩ typical at 25 °C, ×1.5 when hot. Junction-to-fluid 0.12 K/W per switch (typical for this module class; not from that datasheet). |
| Runaway heat and venting | Total heat release of NMC cylinders is a few kJ per Wh; 40–60% leaves with the vented gas ([Feng et al., *Energy Storage Materials* 10, 2018](https://doi.org/10.1016/j.ensm.2017.05.013)) | 4.5 kJ/Wh × 55 Wh = 248 kJ, with 40–60% staying in the cell. That puts the trigger cell at 560–850 °C, the measured range. |
| Radiator cores | Louvred-fin compact surfaces (Kays & London, *Compact Heat Exchangers*) | UA about 3,400 W/K per m² of core face at 5 m/s, scaling with v^0.5. Cross-flow effectiveness (ε-NTU) used throughout. |

## The architecture

```
 BATTERY LOOP (15 L/min, coolant at or below 45 °C)        DRIVE LOOP (12 L/min, coolant at or below 65 °C)
 left radiator + fan --> 4-port valve --> pump -->          right radiator + fan --> 4-port valve --> pump -->
   5 kW PTC heater --> pack inlet manifold -->                inverter cold plate --> charger/DC-DC plate -->
   6 serpentine ribbons (2 per lane) --> outlet --> back      gear-case oil-to-water exchanger --> back
                                                             (10 L/min oil pump in the drive unit sprays the
 Valve state "DC charge":  both radiators on the battery     stator end-turns and cools rotor and gears)
 Valve state "heat":       radiator bypassed, heater on
```

**Why two loops.** Cells want coolant at about 35–45 °C. The inverter and motor are happy at 65 °C. With one shared loop, the battery would be held hot during every ride, or the drive would need a much bigger radiator.

**Why the valve.** During DC charging the drive makes no heat. Lending its radiator to the battery doubles heat rejection at no cost beyond the valve.

## The thermal model

### The network

There is one coupled model in `thermal-lib.py`, solved with fixed-step RK4 at dt = 0.25 s. It has 27 states:

- **Pack: 4 segments along the coolant path.** Each segment has a jelly-roll core node, a can node and a coolant node, holding 148.5 cells each. The pack also has:
  - a case node;
  - a battery-loop node (radiator, hoses, heater);
  - a **sentinel hottest cell**. It sits on the last, warmest coolant, carries 10% more heat (current spread across a parallel group) and has 25% more resistance in its cooling path (adhesive thickness tolerance).
- **Drive:**
  - an inverter base-plate node, with the junction reported as base + 0.07 K/W × switch loss × 1.15;
  - motor winding, stator iron, rotor/magnets, and oil + housing + gears;
  - a drive-loop coolant node.
- **State of charge** and **five energy accumulators**: heat generated, heat to the radiators, heat to the air, heater energy, chiller energy.

*Why scipy was not used:* its LAPACK DLLs are blocked on this machine by Windows Application Control. The brief asked for scipy, but RK4 in numpy does the same job here.

### Key resistances and capacities

| Path | Value | Basis |
|---|---|---|
| Cell core (mean) to can | 0.27 K/W | 2-D finite-difference solve, `thermal-cell-fd.py` (next table) |
| Penalty because a ribbon touches only about 60° of the can | ×1.3 on the line above | Estimate; tangential conductivity is high |
| Can to ribbon wall: adhesive 0.2 mm (k 2) + dielectric layer | 0.07 + 0.15 = 0.22 K/W per cell | The ribbon touches cells of many series groups, so it **must** be insulated: 2.5 kV hipot |
| Ribbon wall to coolant | 0.27 K/W per cell | Laminar ports, Dh 1.9 mm, Nu about 5.4, h about 1,130 W/m²K (`thermal-sizing.py`: Re 391) |
| **Cell core to coolant, total** | **about 0.84 K/W** | At 3C (about 7 W per cell): about 6 K core-to-coolant, plus about 1.65× that again to the core's hot spot |
| Cell heat capacity | 180 J/K (0.18 kg × 1,000 J/kgK) | Cylindrical NMC cells measure 900–1,100 J/kgK |
| Cell resistance for heat | 5.0 mΩ at 25 °C, Arrhenius B = 2,000 K (×1.9 at 0 °C, ×0.72 at 40 °C), up to ×1.6 below 20% SOC | P50B anchor, scaled |
| Case to air | (9 + 0.15·v) W/m²K × 1.05 m², about 10–15 W/K | It sits inside covers with an 8 mm gap |
| Edge cells to case | 15 W/K | Estimate |
| Motor | winding→iron 0.030, winding→oil (end-turn spray) 0.055, iron→oil 0.012, rotor→oil 0.10, rotor→iron (air gap) 0.25 K/W. Capacities 1,300 / 2,990 / 2,070 / 6,700 J/K | **These are RFQ requirements.** With them the spec's 87 kW continuous gives a winding of 166–173 °C (checked below). |
| Oil-to-water exchanger | 0.75 × min(C_oil, C_coolant) = 202 W/K | 10 L/min ATF-class oil |
| Inverter base to coolant | 0.0083 K/W total (0.05 per switch × 6), 1,350 J/K | HybridPACK Drive class |

### Loss models

- **Motor:**
  - copper = 6.5 kW × (I/I_max)² × AC factor (1 + 0.4·(n/16k)²) × resistance-temperature factor, with field-weakening current rising to 0.55·I_max at 16k rpm;
  - iron = 3.0 kW at 16k rpm with full flux, falling as flux drops in field weakening;
  - mechanical = 0.4 kW at 16k rpm.

  This gives about 95% at the 130 kW corner, 95.6% at 87 kW / 12k rpm, and about 88% at 150 Nm / 3,000 rpm. That is in line with automotive IPM maps (the combined Tesla Model 3 drive is claimed at 97%, [IDTechEx](https://www.electricvehiclesresearch.com/articles/23080/teslas-innovative-power-electronics-the-silicon-carbide-inverter)). **This is not a supplier map. It is the most important open input.**
- **Gearbox:** 1.2% of transmitted power + 150 W of churning at 16k rpm, all into the oil. Belt: 97.5%, lost to the air.
- **Inverter:** conduction loss 3·I²·Rds(T) plus switching loss 6·f·E(I,V)/π, with f = 10 kHz and E = 14 mJ at 400 V / 450 A. That gives 1.35 kW at peak, which is 99%.
- **DC-DC:** 93%. **On-board charger:** 94%.

## Results by duty case

These are for the chosen design: side-pod radiators of 0.029 m² each, 35 °C ambient unless noted. They come from `thermal/cases.json` and the plots `thermal/case-*.png`.

| Case | Time | Hottest cell core | Pack spread | Winding / magnets | Inverter junction | Drive coolant | Derate |
|---|---|---|---|---|---|---|---|
| (a) 70 mph to empty (CdA 0.40) | 181 min, 211 mi | 36.0 °C | 0.2 K | 58 / 64 °C | 47 °C | 47 °C | none |
| (a2) same at CdA 0.44 | 169 min, 197 mi | 36.1 °C | 0.2 K | 58 / 65 °C | 48 °C | 48 °C | none |
| (b) 8 sprints, 0–125 mph (8.0 s; 0–60 mph 3.0 s) | 8.3 min | 40.6 °C | 2.4 K | 122 / 84 °C | 82 °C | 61 °C | none |
| (b) then 10 min at 146 mph | | 43.0 °C | | **180 / 122 °C** | 81 °C | 73 °C | **derates after 3.7 min** |
| (b) then 125 mph to 10% SOC | 40 min total | 45.9 °C | 2.4 K | recovers to about 128 °C | 78 °C | 73 °C | none once cooled |
| (c) mountain: 24 km at 7.5% (1,800 m), 40 hairpins at full power, 412 kg, 5 min stop, regen descent | 35 min, SOC 95 → 83% | 39.4 °C | 0.8 K | 99 / 79 °C | 79 °C | 61 °C | none |
| Motor continuous: 87 kW at 12k rpm (about 140 mph) | 20 min, until the pack is empty | **62.6 °C** | 5.7 K | 173 / 124 °C | 83 °C | 78 °C | cells and winding throttle (0.61) |
| (d1) DC fast charge 10–80%, 35 °C, arriving at 38 °C | **18.9 min** | 51.7 °C | 3.1 K | — | — | — | charge current throttled above a 47 °C cell core |
| (d1b) same, with a 4 kW chiller (option) | 14.0 min | 48.7 °C | 8.7 K | | | | none |
| (d2) DC fast charge at 0 °C, cold-soaked, no heater | **3 h and only 48%** | 1 °C | | | | | **FAIL** |
| (d3) 0 °C, 5 kW heater powered by the station | **20.9 min** | 44.4 °C | 8.1 K | | | | |
| (d4) 0 °C, 20 min of preheat on the ride in, then charge | ride uses 5% SOC extra; charge **14.6 min** | 45.7 °C | 8.3 K | | | | |

**Sustained speed** (from `thermal/sweeps.json`; 20 min hold, 35 °C):

| mph | Winding | Magnets | Junction | Oil | Result |
|---|---|---|---|---|---|
| 110 | 94 °C | 86 °C | 60 °C | 65 °C | fine |
| 125 | 128 °C | 102 °C | 69 °C | 76 °C | fine (the 125+ mph goal) |
| 130 | 145 °C | 110 °C | 72 °C | 81 °C | fine |
| 135 | 165 °C | 118 °C | 77 °C | 87 °C | at the edge; still rising slowly |
| 140 | 176 °C | 123 °C | 78 °C | 89 °C | derates after 6.4 min |
| 146 (top) | 181 °C | 124 °C | 78 °C | 89 °C | derates after 3.7 min, settles near 130 mph |

**Temperature gradients in the pack:**
- **Hottest cell core to the coldest mean core:** 2–3 K while riding, about 3 K during a 35 °C charge, and about 8–9 K when the coolant is very cold relative to the cells (chiller, or a cold charge). That is within the usual ≤5–10 K pack-uniformity goal.
- **Inside one cell, at 3C:** the core hot spot sits about 7 K above the mean core.
- **Inlet to outlet coolant rise:** 1.5–4.7 K.

## Optimum: radiator size, chiller, heater

**Hot charging (35 °C) against radiator size and chiller** (`thermal/sweep-charge.png`):

| Face area per side | No chiller | 2 kW chiller | 4 kW chiller |
|---|---|---|---|
| 0.009 m² (fits today's body) | 23.2 min | 15.7 | 14.0 |
| 0.020 m² | 20.2 | 15.3 | 14.0 |
| **0.029 m² (chosen, side pods)** | **18.9** | 15.0 | 14.0 |
| 0.045 m² | 17.5 | 14.7 | 14.0 |
| 0.060 m² | 16.7 | 14.4 | 14.0 |

**What the charge sweep says:**
- **A bigger radiator buys little charging time.** The cells' own heat capacity, about 107 kJ/K, does most of the work in a 15–20 minute stop.
- **Ambient matters more than radiator size.** At 25 °C the charge takes 14.8 min; at 40 °C, 23.0 min; at 45 °C, 30.7 min.
- **Cell resistance matters too.** At 3.5 / 5.0 / 6.5 mΩ the charge takes 16.0 / 18.9 / 21.5 min.
- **The chiller is the only way to keep 14 minutes in the heat.** It costs about $600–900 and 5–7 kg.
- **Recommendation:** no chiller in the base bike, because 18.9 min meets the 25 min requirement. Offer it as a hot-climate option, and leave the pipe tee and harness connector for it.

**The radiator size is set by the drive, not by charging.**
- With the 0.009 m² cores that fit inside today's body, the motor runs much hotter: winding 236 °C uncapped in case (b), 127 °C in the mountain climb, junction 127 °C. That is unacceptable (`thermal/cases-optionA.json`).
- With 0.029 m² everything passes except a sustained 146 mph.

**Cold charging against heater power:**

| Heater | 10–80% at 0 °C |
|---|---|
| none | does not finish (48% after 3 h) |
| 3 kW | 24.3 min |
| **5 kW** | **20.9 min** |
| 7 kW | 19.2 min |
| 5 kW at −10 °C | 25.0 min |

**5 kW is the knee of the curve. With preheating on the way to the charger, the 0 °C charge takes 14.6 min**, the same as at 25 °C. The heater runs from the station during a charge, or from the pack while riding: 1.7 kWh for 20 min of preheat, about 5% of the pack.

## Radiators and where they go

**The radiators do not fit the body as it is today.** A free-space probe of the saved CAD (`thermal-cad-probe.py`, 20 mm grid) checked every point for:
- at least 10 mm from every part;
- at least 4 mm inside the skin;
- at least 20 mm from the steered, bumped front tyre plus fender.

Free space beside the charger and inverter is only about X950–1030, Y±130–200, Z670–790. Tested with a real core and fan (`thermal-cad-pods.py`), the biggest core that fits is about **85 × 110 mm (0.009 m²)**, and even that touches the grille louvres.

**Chosen: a side pod each side** (option B in `thermal-cad-pods.py`; it passes):
- **Core:** 210 mm long × 140 mm tall × 32 mm deep, brazed aluminium louvred fin, plastic tanks.
- **Angle:** the core runs from (X985, Y±160) at its inner rear end to (X1157, Y±280) at its outer front end, Z 640–780. That is 35° to the bike's centreline, with the face looking forward and inboard.
- **Fan:** a 190 mm slim fan (30 mm deep) on the inboard face.
- **Air path:** in through a scoop in the shroud nose, beside the fork (X 1150–1200, Y ±150–220); out rearward and outboard through the existing side louvres.
- **Envelope** (core + fan): X967–1174, Y ±135–307, Z640–780.
- **Clearances:** 17.7 mm to the upper rail, 68.9 mm to the front tyre + fender swept over ±35° lock × full bump (the conservative disc model), 105 mm to the fork and clamps at lock, and clear of the charger and inverter.
- **Prior art:** the same side-pod layout as the KTM 1290 Super Adventure.

**What it costs the body:** the shroud gets wider over X 960–1180, from about ±225 mm to **±315 mm** (630 mm across). That is still inside the grips (Y ±351) and well under a boxer GS's cylinder width. It needs a quick aero re-run; drag should change by less than 1–2% because the pods sit in the rider's shadow.

**Airflow it needs:**
- **At speed:** a face velocity of about 0.25 × road speed (14 m/s at 125 mph). The model takes the air side as the limit.
- **At idle:** 3.2 m/s from the fan, which moves about 0.09 m³/s per core and draws about 90 W each at 12 V.

**Service bay**, in the space the HV cabinet left on the pack roof (checked in `thermal-cad-bay.py`; all pass, 16–40 mm margins):

| Part | Saved-model box (X / Y / Z, mm) | Nearest part |
|---|---|---|
| Battery pump, CWA50 class | X593–657, Y−140…−50, Z673–737 | 39 mm to the seat |
| Drive pump, CWA50 class | X593–657, Y50…140, Z673–737 | 39 mm to the seat |
| 5 kW HV PTC heater | X598–653, Y−44…44, Z668–730 | 39 mm to the motor envelope |
| 4-port valve | X598–648, Y−188…−150, Z676–728 | 16 mm to the upper rail |
| Oil-to-water exchanger, on the gear case | X560–640, Y−150…−110, Z470–560 | 30 mm to the upper rail |
| Degas bottle | built into the right radiator's top tank, filler at about (X1100, Y+250, Z790) | inside the pod |

**Hoses** are 16 mm ID EPDM.
- **Battery loop, about 2.2 m:** pod radiator → valve → pump → heater → pack inlet bulkhead on the pack roof (X600–650, Z653, Y−40) → ribbons → outlet bulkhead (X600–650, Z653, Y+40) → back along the left tank side at Z about 700 to the left pod.
- **Drive loop, about 3.2 m:** right pod → valve → drive pump → inverter (X700–1030, Z715–812) → charger plate → down the right side behind the pack at X560–590 to the gear-case oil cooler (Z470–560) → back up the right side at Z about 700 to the right pod.

## Sized parts

Planning estimates, not quotes. From `thermal-sizing.py` → `thermal/sizing.json`. Volume = 10k bikes a year.

| Part | Qty | Mass, kg | $/bike at 10k/yr |
|---|---|---|---|
| Radiator core 210 × 140 × 32 mm, brazed Al, plastic tanks (one with a degas tank) | 2 | 1.61 | 110 |
| Slim fan 190 mm (7.5 in) BLDC, 12 V, about 90 W, with shroud | 2 | 1.10 | 70 |
| Coolant pump, 12 V BLDC, CWA50 class (about 25 L/min at 0.53 bar) | 2 | 1.10 | 150 |
| Cooling ribbons: aluminium multiport 105 × 1.6 mm, 12 ports of 7.5 × 1.1 mm, dielectric-coated; 6 serpentines × 2.0 m | 1 set | 2.18 | 180 |
| Pack inlet/outlet manifolds and bulkhead quick-connects | 1 | 0.70 | 60 |
| Thermal adhesive, 0.2 mm, k ≥ 2 W/mK | 1 | 0.41 | 40 |
| HV PTC coolant heater, 5 kW | 1 | 1.90 | 190 |
| 4-port coolant valve (radiator cross-connect + heater bypass) | 1 | 0.45 | 45 |
| Oil-to-water plate exchanger (inside the drive-unit allowance) | 1 | 0 | 0 |
| Hoses, 16 mm ID EPDM, 5.4 m, with clamps and P-clips | 1 | 0.95 | 35 |
| Coolant, 50/50 ethylene glycol and water | 3.9 L | 4.19 | 8 |
| Temperature sensors | 1 | 0.10 | 20 |
| Fire barrier: intumescent foam in the gaps without ribbons (about 8 L) | 1 | 2.40 | 70 |
| Pack vent valve with burst disc, plus mica plenum liners | 1 | 0.50 | 45 |
| **Total** | | **17.8** | **$1,035** (about $1,650 at 1k/yr) |
| *Option:* 2 kW battery chiller (e-compressor, condenser, chiller exchanger) | | +5–7 | +$600–900 |

**Against the mass roll-up:** the roll-up carries 2.8 kg (pump, hoses, 2 L of coolant) plus 2 × 1.15 kg of side radiators. The pack's "busbars, cooling ribbon, potting" sit inside its 16.3 kg internals allowance. The ribbons, adhesive and foam (5 kg) belong in that allowance. The rest, about 12.8 kg against 5.1 kg budgeted, is **about +7.7 kg** on the roll-up.

**Against the cost model:** EL034–EL037 thermal ($430 at 10k) plus EL039 cold conditioning ($90). This design is **about +$500 a bike.**

**Hydraulics** (`thermal/sizing.json`):

| | Battery loop | Drive loop |
|---|---|---|
| Flow | 15 L/min | 12 L/min |
| Pressure drop | 42 kPa | 33 kPa |
| Hydraulic power | 11 W | 7 W |
| Pump electrical draw | about 40 W | about 30 W |
| Detail | Ribbons laminar, Re 391, 20 kPa | Inverter 8 kPa, oil cooler 6 kPa |

Both are well inside a CWA50's curve: about 25 L/min at 53 kPa.

## Pack: air or liquid, and the case as a heat path

- **Air is ruled out.**
  - The cells sit in a sealed, structural, IP67 case with 2 mm gaps, so there is no air path through them.
  - The case can shed only about 10–15 W/K. In a 35 °C charge it carried 0.07 MJ of the 2.75 MJ generated, 2.7%.
  - Even at 125 mph it averages about 40 W, against up to 8.5 kW of cell heat in full-power pulls.
- **3 mm against 4 mm case walls:** no measurable difference. Charge time is 18.9 min either way; the case carries 0.076 against 0.073 MJ. Wall thickness is a structural choice, not a thermal one.
- **The case does help in the cold.** It is a good insulator for the pack, so a preheated pack holds its heat.

## Thermal runaway: propagation and venting

**The screen** (`thermal-propagation.py`): a 9 × 9 patch of cells, with the centre cell releasing a share of 248 kJ in 10 s. 40% retained gives a 560 °C peak in that cell; 60% retained gives about 840 °C. The table shows the hottest neighbour.

| Gap filler | Coolant flowing, 40% / 60% retained | No coolant (crash or pump fault), 40% / 60% retained |
|---|---|---|
| Air gap, no filler | 61 / 75 °C | 109 / **145 °C** |
| Silicone potting, k 0.2 | 63 / 77 °C | 92 / **120 °C** |
| Intumescent PU foam, k 0.08 | 61 / 74 °C | 103 / **137 °C** |
| Aerogel or mica sleeve, k 0.025 | 59 / 72 °C | 119 / **161 °C** |

**How to read it.** A neighbour starts to self-heat at about 120 °C, and a runaway trigger is about 170 °C.

**What the screen says:**
- **With the ribbon coolant flowing, there is no propagation in any case**, by a margin of 45+ K.
- **Without coolant the result is marginal.** The surprise is that better insulation alone does not fix it. The dominant path is the **copper parallel-group busbar** (about 0.2 W/K to each in-row neighbour), not the gap. With a very good insulator the heat that arrives through the busbar cannot spread any further.
- A hand bound, with all the trigger heat shared equally by 6 neighbours and nothing else, gives 127 / 172 °C. The model sits below it, as it should.

**Barrier and venting spec:**
1. **Fusible single-cell links.** Use wire bonds or laser-cut fuse tabs, at most about 0.03 W/K each, between every cell and its busbar. This breaks the busbar heat path and also stops the 5 parallel neighbours feeding a shorted cell.
2. **Gap filler.** Fill every non-ribbon gap with intumescent PU foam (k about 0.08, density about 0.3).
3. **Liners.** Line the lane ends and the case lid with 0.5 mm mica.
4. **Ribbon dielectric** rated to 2.5 kV hipot. The ribbon's aluminium is a heat sink only while coolant flows, so the BMS must keep the battery pump running after any thermal event.
5. **Vent path.**
   - Every cell vents toward the vent end. Each cell gives off about 25 L of gas at room conditions (about 1.5 L/Ah × 15.3 Ah), roughly 60 L hot, in 2–5 s.
   - That gas goes into a **vent plenum at least 8 mm wide** behind the cell ends, then to a **pack burst vent of 50 mm diameter** (about 2,000 mm²). Sizing: the gas needs about 180 mm² at a 20 kPa case overpressure, and the rest of the area lets particles through.
   - Put the vent on the pack's **rear-lower face**: about X595, Y−100, Z280 (saved). It should point down and back, under the motor and away from the rider and the HV cabinet.
   - A breathable membrane on the same valve stops pressure building up in normal use.
6. **Test.** This must be proven by a single-cell trigger test (nail or heater) on a lane module. The model does not include gas jets hitting neighbouring cells.

## Verdict table

| Item | Value | Required | Margin | Verdict |
|---|---|---|---|---|
| Pack cooling type | Liquid, side ribbons | Must remove 4–6 kW while charging | Case alone 0.05–0.15 kW | **Liquid required** |
| Hottest cell core, 35 °C DC charge | 51.7 °C | ≤55 °C | 3.3 K | PASS (by throttling) |
| 10–80% at 35 °C, no chiller | 18.9 min | ≤25 min (`powertrain-optimise.py`) | 6.1 min | PASS |
| 10–80% at 45 °C, no chiller | 30.7 min | ≤25 min | −5.7 min | FAIL; chiller option fixes it (14–15 min) |
| 10–80% at 0 °C with 5 kW heater | 20.9 min (14.6 preheated) | ≤25 min | 4.1 min | PASS |
| 10–80% at 0 °C, no heater | does not finish | ≤25 min | — | FAIL, so **the heater is required** |
| Pack spread, hottest core to mean (riding / charging) | 2–3 K / 3–9 K | ≤10 K | ≥1 K | PASS |
| Cell core, 87 kW sustained discharge | 62.6 °C | ≤60 °C | −2.6 K | Throttled by the BMS (unrealistic duty: about 140 mph until empty) |
| Winding: sprints / mountain / 125 mph | 122 / 99 / 128 °C | ≤170 °C (class H, 180 hot spot) | ≥42 K | PASS |
| Winding at 146 mph held | 180 °C after 3.7 min | ≤170 °C | — | **OPEN**: time-limited top speed; 130 mph sustained |
| Magnets, worst case | 124 °C | ≤140 °C (SH/UH grade) | 16 K | PASS |
| Inverter junction, worst case | 83 °C | ≤150 °C | 67 K | PASS (could use a smaller module) |
| Drive coolant at the inverter inlet | ≤78 °C (65 °C below 130 mph) | ≤65–70 °C (typical inverter) | −8 K at 140 mph | OPEN: confirm the supplier's coolant limit |
| Energy balance, all 41 runs | residual under 1e-12 % | close | — | PASS |
| Radiator fit in today's body | 0.009 m² max | 0.029 m² needed | — | FAIL, so the **side pods are needed** (CAD request 1) |
| Side-pod radiators against the frame / tyre sweep / fork | 17.7 / 68.9 / 105 mm | 10 / 20 / 10 | ≥7.7 mm | PASS (body skin not yet drawn) |
| Pumps, heater, valve, oil cooler fit | 16–40 mm | ≥10 mm | ≥6 mm | PASS |
| Pump capability | 42 kPa at 15 L/min | CWA50 about 53 kPa at 25 L/min | about 40% flow margin | PASS |
| Propagation with coolant flowing | ≤77 °C neighbour | <120 °C | 43 K | PASS (screen) |
| Propagation without coolant | 120–161 °C | <120 °C | — | **OPEN**: fusible links + vent plenum + test |
| Added mass / cost | +17.8 kg total (+7.7 vs roll-up) / about $1,035 (+$500 vs model) | — | — | Note for the mass and cost owners |

## Verification

1. **Energy balance closes in every run.** Heat generated + heater input − (heat to radiators + to the air + to the chiller) = heat stored in every node. The residual is below 1e-12 % in all 22 case runs (both radiator options) and all 35 sweep runs (`cases.json` → `energy_balance`). This proves the network conserves energy: no node leaks or creates heat.
2. **Hand checks against the model:**
   - **Range.** At 70 mph, aero 7.1 kW + rolling 1.7 kW = 8.8 kW at the wheel. Divided by about 0.91 (drive) plus 0.4 kW of accessories, that is about 10.2 kW from the pack. 31.0 kWh usable then lasts 3.04 h. **The model says 3.01 h.**
   - **Charge heat.** 3C is 45.9 A per cell. Resistance at 45 °C is 3.28 mΩ, so each cell makes 6.9 W and the pack 4.1 kW. **The model averages 4.6 kW** in the chiller run, where the cells run cooler at about 42 °C and resistance is higher.
   - **Adiabatic charge.** 3.45 MJ over 107 kJ/K is +32 K with no cooling at all. The model's 35 °C charge (38 → 51.7 °C at the hot spot, with throttling) sits inside that bound.
3. **Cell internal resistance (2-D finite difference against hand calculations).** Mesh convergence is 0.5% from 16×32 to 32×64 cells.

   | Conductivity across layers | FD mean | FD peak/mean | Hand: radial only | Hand: axial only | Hand: both in parallel |
   |---|---|---|---|---|---|
   | 0.2 W/mK | 0.436 K/W | 2.41 | 1.715 | 0.788 | 0.540 |
   | 0.6 W/mK (used) | 0.269 K/W | 2.65 | 0.572 | 0.788 | 0.331 |
   | 1.0 W/mK | 0.197 K/W | 2.67 | 0.343 | 0.788 | 0.239 |

   The 2-D result is below both 1-D limits and below their parallel combination, as it should be: heat can leave sideways and out of the ends at the same time.
4. **Motor continuous rating.** The spec asks for 85–90 kW continuous. The model at 87 kW (wheel), held for 20 min at 35 °C ambient, gives a 173 °C winding, 124 °C magnets and 94 °C oil, with drive coolant at 78 °C. With the 0.035 m² radiator tried earlier the winding was 166 °C. That is inside a 180 °C class-H system, so the RFQ resistances above are self-consistent.

---

## CAD change requests

All coordinates are in the **saved model frame** (generator Z + 40 mm). X forward, Y left, Z up, mm.

1. **Radiator side pods (required).** Widen the shroud each side over X 960–1180, Z 630–800 to an outer skin at Y ±315.
   - Inside each pod: a 210 × 140 × 32 mm core running from (X985, Y±160) to (X1157, Y±280), Z 640–780, plus a 30 mm slim fan on its inboard face.
   - Envelope: X967–1174, Y±135–307, Z640–780.
   - Inlet scoop in the shroud nose at X 1150–1200, Y ±150–220, Z 650–780.
   - Keep the existing side louvres (X1000–1140, Z650–770) as the hot-air exit; move them onto the pod's outer skin.
   - Replace `Side_radiator_±1` (X960–1070, Y±128–178).
   - Add checks: core and fan ≥10 mm to the upper rails (17.7 now), ≥20 mm to the tyre + fender lock sweep (68.9 now), ≥10 mm to the fork at lock (105 now).
2. **Service bay on the pack roof** (the space the HV cabinet left):
   - battery pump X593–657, Y−140…−50, Z673–737;
   - drive pump X593–657, Y50…140, Z673–737;
   - 5 kW PTC heater X598–653, Y−44…44, Z668–730;
   - 4-port valve X598–648, Y−188…−150, Z676–728.

   All of these pass at ≥16 mm.
3. **Oil-to-water exchanger** on the left of the gear case: X560–640, Y−150…−110, Z470–560 (30 mm to the rail). Oil ports go into the gear case.
4. **Pack coolant bulkheads** on the pack roof: inlet (X625, Y−40, Z653) and outlet (X625, Y+40, Z653), Ø20 mm quick-connects. Keep 40 mm clear above them for hose bends; the heater outlet is 15 mm away, so join them with a short hard pipe.
5. **Cooling ribbon space inside the pack.**
   - Raise the row spacing inside each two-row band so the gap along the line between cell centres is **2.5 mm** (ribbon 1.6 + adhesive 0.2 + dielectric about 0.1 on each side), not 2.0. That is DZ inside the band 24.25 → 24.82 mm, which adds about **4.6 mm** to the pack height (the pack top goes from 653.5 to about 658 saved).
   - Raise CLR, the gap between the cells and the case wall at the row ends, from 1.0 to **3.0 mm** so the ribbon can wrap round the end cells.
   - Effect: pack length +4 mm at each stepped end, or one cell per long row if the front clearance to the tyre cannot give. The pack-layout owner should decide.
6. **Vent plenum and burst vent.**
   - Widen the gap at one lane end (the −Y end, where the cells vent) from 2 mm to **8 mm**, with a mica liner. The pack outer width grows 388 → 394 mm and the lower covers need +6 mm on the left.
   - Add a Ø50 mm burst vent with a membrane on the pack's rear-lower face at **X595, Y−100, Z280** (saved), pointing down and back.
   - Keep a 60 mm dia × 80 mm deep clear zone behind it (the motor case is at X≥465; check).
7. **Hose corridors**, 16 mm ID, 26 mm OD with clips, ≥10 mm from moving parts:
   - Battery: left pod → valve → pack roof, along Y−185…−160 at Z about 700 between X 650 and 990.
   - Drive: right pod → inverter inlet (X1030, Y+60, Z760) → charger plate → down the right side at X 565–590, Y+150, Z 560–700 to the oil cooler, then back up along Y+185, Z about 700.
8. **Model note.** `components-electrical.csv` and `electrical-design.md` still describe the old 100s7p / EMRAX 208 / CM200. They should be brought into line with the 99s6p / IPM bike.

## What this does not prove

- **Not a supplier map.** The motor loss map, the inverter switching energy, and the 26120 cell's resistance and its temperature behaviour are scaled from public values. Swapping in supplier data could move the derate times and charge times by ±20–30%. The charge-time sensitivity to cell resistance, 15.6–20.7 min, is shown above.
- **Radiator airflow is assumed, not simulated.** Face velocity is taken as 0.25 × road speed, and 3.2 m/s with the fan at idle. The side scoop and exit have not been through CFD. The aero CFD (`cfd/`) has no cooling flow path yet. **This is the largest open item for the radiator sizing.**
- **Lumped, not 3-D.** The pack is 4 segments plus a sentinel cell. Local hot spots are not modelled: around busbars, at a manifold-starved ribbon pass, or at cells near the motor (the pack sits 21 mm from the motor case). A CFD/conduction model of one lane is the next step.
- **Charge profile.** Constant-current 3C capped by a temperature map. Real chargers taper with SOC and with station limits. Reversible (entropic) heat is ignored; that is about ±10% of charge heat.
- **Propagation is a screen, not a test.** The patch model covers gap conduction, radiation and busbar conduction. It does not cover the jet of hot vent gas and particles hitting neighbouring cells' ends, which is often what drives propagation in tests. UN 38.3 and a single-cell trigger test (SAE J2464 / GB 38031 style) are required.
- **Not modelled at all:**
  - stopping in hot traffic after a hard ride (idle drive loop on the fan only; checked only through the 5 min stop in case c);
  - the effect of altitude on the fans;
  - capacitor and busbar temperatures inside the inverter;
  - motor bearing and rotor-sleeve temperatures;
  - cell ageing;
  - ram-air for the battery loop at speed, beyond the 0.25 factor;
  - charging-inlet heating.
- **Coolant freeze and boil margins are not checked** beyond specifying 50/50 glycol (−37 °C).
