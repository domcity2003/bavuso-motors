# Bavuso V1 thermal design (rev C cooling concept)

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Scripts (run from `v1.0` with FreeCAD python): `program/tools/thermal-lib.py` (model), `thermal-cases.py` (duty cases), `thermal-radiator.py` (radiator and fan sweep, mass bill), `thermal-propagation.py` (runaway screen), `thermal-checks.py` (balances, hand checks, convergence, hydraulics). Data: `program/data/thermal/` (`cases.json`, `checks.json`, `propagation.json`, `radiator-sweep.csv/.json`, `series-*.csv` time histories).
Labels: **supplier** = published datasheet, **calc** = computed, **est** = my estimate. Methods reused from `detailed-design/tools/thermal-*.py` (RK4 lumped network, e-NTU radiator, sentinel hottest cell, energy accumulators) and the motor, inverter and pack models in `program/tools/drive-lib.py`. Cell charge profile is the 3C-cap, 250 kW NACS profile of `06-drive-performance.md`.

## The plain answer

**The rev C cooling loop works for everything the bike must do at 25 C, but it does not make 125 mph on a 38 C day, and the 6 kg cooling mass budget does not close.**

- **125 mph for the whole pack at 25 C: passes.** Hottest cell core 50.7 C (limit 55 C BMS, 60 C cell), motor coolant inlet 45.9 C (EMRAX limit 50 C), winding 86 C (limit 100 C).
- **125 mph at 38 C: needs a derate.** Coolant reaches the EMRAX 50 C inlet limit after 10.6 min, the cell core passes 55 C after 17.2 min, and the hottest core ends at 60.9 C (can 59.6 C, so right at the 60 C limit). Gate A's "pack about 57 C, no chiller" is optimistic by 2 to 4 K in this more detailed model. The derate Gate A allows is therefore real: hold about 105 mph for the whole pack at 38 C (95 mph if the EMRAX 50 C inlet limit is treated as hard).
- **DC fast charge 10-80%:** 17.1 min at 25 C, 23.0 min at 35 C (passes the 25 min target). It fails slightly if the bike arrives hot (42 C start at 35 C ambient: 27.4 min). Cells stay at or below 48.9 C core in all of these.
- **Cold charge at -10 C with the 3 kW PTC: 25.4 min, a marginal miss.** A 5 kW heater gives 21.6 min. Pre-heating on the ride in (0.79 kWh, 3% of the pack) gives 14.0 min. Without a heater the pack never charges.
- **Radiator: keep the rev C cores (2 x 165 x 128 x 28 mm).** They are not oversized. A 15% smaller core (2 x 152 x 118 x 28 mm) saves only 0.2 kg and is right at the limit if the ram-air factor is as low as 0.2. No CAD change to the radiators.
- **Cooling mass is 7.1 kg on this bill, 6.8 kg with a wax thermostat instead of the 4-port valve.** The budget of 6.0 kg closes only if the 1.1 kg of coolant in the pack ribbons and manifolds is booked with the ribbons in pack internals. Details in section 5.
- **Thermal runaway:** with coolant flowing, a single cell failure does not spread in the central cases. With no coolant, or in the worst credible case, it can. The gap filler hardly matters; the ribbon and busbar paths dominate, so the rules are wire-bond links, slotted ribbons and a vent of 490 mm2 per parallel group (section 4).

## Verdict table

| # | Check | Result | Limit | Verdict |
|---|---|---|---|---|
| 1 | 125 mph, 25 C, 95 to 5% SOC (27.5 min): cell core / can / spread | 50.7 / 49.0 C / 3.0 K | 55 C BMS, 60 C cell, 10 K | **Pass** |
| 2 | Same: coolant into motor / inverter / charger plate | 45.9 / 48.4 / 49.7 C | 50 / 65 (est) / 60 (est) C | **Pass** (4 K on the motor) |
| 3 | Same: winding / inverter case | 86.2 / 72.5 C | 100 C (supplier) | **Pass** |
| 4 | 130 mph governed top speed, 25 C (24.6 min) | core 53.2, inlet 47.5, winding 91 C | as above | **Pass** |
| 5 | 125 mph, 38 C | core 60.9 (can 59.6), inlet 57.3, winding 98.1 C | as above | **Fails to hold; derate** (50 C inlet after 10.6 min, core 55 C after 17.2 min) |
| 6 | Hot-day sustained speed, whole pack | 105 mph (pack limits), 95 mph (EMRAX 50 C inlet hard) | none required by Gate A | **Derate allowed** |
| 7 | Repeated hard mountain riding, 90 s cycle, 101 min to 5% | 25 C: core 39 C. 38 C: core 50.9 C, inlet 50.2 C | 55 C / 50 C | **Pass** (38 C at the inlet limit) |
| 8 | 25 min climb at 7.5% plus regen descent, 38 C | core 44.9, inlet 45.2, inverter case 59.6 C | | **Pass** |
| 9 | DC 10-80%, 25 C | 17.1 min, core 46.7 C, spread 3.2 K | 25 min, 55 C | **Pass** |
| 10 | DC 10-80%, 35 C | 23.0 min, core 48.6 C | 25 min | **Pass** (2 min) |
| 11 | DC 10-80%, 35 C ambient, arriving at 42 C | 27.4 min | 25 min | **Fail by 2.4 min** |
| 12 | DC 10-80%, 45 C | 40.9 min, coolant inlet 50.5 C | not claimed | Info |
| 13 | DC 10-80%, 35 C, 2C cell cap (fallback) | 27.4 min | 25 min | Info: 2C cap misses at 35 C |
| 14 | DC 10-80%, -10 C cold soak, 3 kW PTC | 25.4 min, spread 5.6 K | 25 min | **Marginal miss** |
| 15 | Same, 5 kW / 2 kW / none | 21.6 / 29.9 min / never | | Info |
| 16 | Same, pre-heated to 20 C on the ride | 14.0 min | | **Pass** |
| 17 | AC 3.3 kW, 10-80% at 38 C | 5.5 h, everything at 44 C | | **Pass** |
| 18 | Radiator at the worst case (125 mph, 25 C) | rev C passes with 4.1 K on coolant inlet | | **Keep rev C** |
| 19 | Cooling mass | 7.11 kg (6.81 with thermostat) | 6.0 kg | **Over by 0.8 to 1.1 kg** |
| 20 | Runaway, coolant flowing, central cases | neighbour 74 to 104 C | under 120 C | **Pass** |
| 21 | Runaway, no coolant or worst credible case | 134 to 249 C | under 120 C | **Marginal / propagates; test needed** |
| 22 | Energy balances | thermal closure within 0.016%; electrical within 0.001% | | **Pass** |

## 1. The model

One lumped RK4 network (dt 0.5 s, shown converged from 0.25 s to 2 s: identical to 0.1 K and 0.1 min) with:
- **Pack:** 1,100 P60B cells. Each ribbon (28 serpentine ribbons: 7 per lane x 4 lanes, one between each pair of cell rows, 39 cells each) is split into 5 segments along the coolant path. Each segment has a cell-core node, a can node and e-NTU coupling to the coolant. Plus a case node, and a **sentinel hottest cell** (last coolant segment, 10% more heat, 25% more cooling-path resistance).
- **Cell heat:** 12.8 mohm DC [supplier] x the resistance-vs-SOC and temperature curves of the drive model x 1.08 (busbars) x 1.10 (diffusion polarisation over minutes, est). At 18 A (3C) and 10% SOC, 6.96 kW for the pack (hand check equal).
- **Core to can** 0.32 K/W (2-D finite difference on the P60B dimensions, converged to 0.4% between 16x32 and 24x48 grids) x 1.3 arc penalty; core hot spot is 2.5x the mean core rise. **Can to coolant** 0.34 K/W adhesive and dielectric + 0.33 K/W ribbon (laminar, Nu 5.4, 8 ports 7.5 x 0.8 mm). Total 5.4 K from core to coolant at 5 W per cell.
- **Loop:** one pump, 22 L/min split 10 L/min to the pack and 12 L/min to the drive branch (CM200DX wants 12 L/min [supplier shortlist], EMRAX minimum is 6 L/min [supplier]). Order on the drive branch: motor, then inverter, then charger/DC-DC plate. PTC heater and radiator bypass valve upstream of the split; the radiator is bypassed whenever the heater is on.
- **Radiator:** e-NTU cross-flow, UA 3,400 W/K per m2 of face at 5 m/s (32 mm core, scaled with depth^0.9; est, Kays and London class as in `thermal-study.md`). Face velocity = **0.25 x road speed** (pod scoop, **est, needs CFD**) or the fan flow when stopped.
- **Motor, inverter, charger:** motor lumped 8.5 kJ/K and 0.0217 K/W winding to coolant (from the datasheet liquid-cooled continuous rating, as in drive-lib); inverter case 3 kJ/K and 25 K/kW; charger plate 0.8 kJ/K. Losses from drive-lib (motor copper and iron, CM200DX loss curve).
- **Charging:** 3C cell cap, 4.2 V per cell taper, my derating map (0 A at 0 C, half at 10 C, full 20 to 40 C, linear to zero at 55 C, as in `drive-charge.py`), keyed to the hottest can and coldest cell.

## 2. Cell, pack, motor, inverter and charger results (rev C radiator)

| Case | Time | Cell core mean / hot spot | Can max | Spread | Coolant in: motor / inverter / charger | Winding | Inverter case |
|---|---|---|---|---|---|---|---|
| DC 25 C | 17.1 min | 45.2 / 46.7 | 45.6 | 3.2 K | 43.5 / 43.5 / 43.4 | 42.5 | 43.2 |
| DC 35 C | 23.0 min | 47.8 / 48.6 | 48.0 | 2.0 K | 46.8 / 46.8 / 46.8 | 46.6 | 46.7 |
| DC 35 C, arrive 42 C | 27.4 min | 48.1 / 48.9 | 48.3 | 1.4 K | 47.2 | 47.1 | 47.2 |
| 125 mph 25 C | 27.5 min | 48.5 / 50.7 | 49.0 | 3.0 K | 45.9 / 48.4 / 49.7 | 86.2 | 72.5 |
| 125 mph 38 C | 27.7 min | 59.2 / 60.9 | 59.6 | 2.2 K | **57.3 / 59.8 / 61.1** | 98.1 | 84.0 |
| 130 mph 25 C | 24.6 min | 50.6 / 53.2 | 51.2 | 3.5 K | 47.5 / 50.2 / 51.6 | 91.4 | 76.2 |
| Hard riding 25 C | 101 min | 38.2 / 39.0 | 38.3 | 0.9 K | 37.8 / 38.7 / 39.4 | 53.6 | 54.9 |
| Hard riding 38 C | 102 min | 50.4 / 50.9 | 50.5 | 0.7 K | 50.2 / 51.1 / 51.9 | 66.3 | 67.3 |
| Mountain 38 C | 40 min | 44.9 / 44.9 | 45.1 | 0.6 K | 45.2 / 45.8 / 46.5 | 54.6 | 59.6 |
| Cold -10 C, 3 kW PTC | 25.4 min | 37.1 / 41.1 | 38.1 | 5.6 K | 32.6 | 29.6 | 31.4 |
| Cold -10 C, pre-heated | 14.0 min | 39.7 / 43.6 | 40.7 | 5.6 K | 35.2 | 33.0 | 34.4 |

Limits: cell **60 C** [supplier], BMS target 55 C, spread 5 K goal and 10 K limit [est]; EMRAX 228 LC coolant inlet **50 C** and 6 L/min minimum [supplier datasheet v1.7], winding sensor **100 C** [supplier]; CM200DX inlet 65 C [est: the supplier says current capacity depends on coolant temperature, gives no curve]; charger/DC-DC plate 60 C [est].

What stands out:
- **Pack spread is small (0.5 to 3.5 K).** Short parallel ribbons keep the coolant rise to 11.5 K at 3C only because the heat of a ribbon (249 W) is spread over 28 ribbons; the biggest gradient is inside the cell (core hot spot about 1.5 K above the mean core at 5 W).
- **Cold charging spread is 5.6 K** (cells at -10 C warmed from the coolant side), inside 10 K.
- **The EMRAX 50 C inlet limit binds before any cell limit** on a hot day. It is stated at 30 C ambient; ask EMRAX whether 55 to 60 C inlet is allowed with the winding sensor at 100 C. If yes, the hot-day pack limit becomes the only limit.
- **The charger/DC-DC plate** sits last in the drive branch and reaches 61.1 C at 125 mph and 38 C. Put it first, or on the pack branch.
- **Pump and flow:** at 22 L/min the loop needs about 74 kPa (including a 26 kPa balancing orifice on the pack branch, because the motor jacket, inverter and charger plates are in series on the other branch). That is 27 W hydraulic, about 108 W electrical, and is at the edge of a CWA50-class pump (25 L/min at 53 kPa). Get the real pressure drops of the EMRAX jacket and CM200DX plate; if they are lower, the loop is comfortable.

## 3. Radiator sizing

Requirements used (`thermal-radiator.py`): **R1** 125 mph, 95 to 5% SOC, 25 C: coolant inlet to the motor 50 C or less, cell core 55 C or less, winding 100 C or less, inverter inlet 65 C or less. **R2** DC 10-80% at 35 C in 25 min or less, core 55 C or less. Hot-day 125 mph is excluded (derate allowed by Gate A). 42 designs: core depth 28 or 40 mm, three fans, seven face areas.

- **R1 sets the size and only the core's area x depth matters** (ram air does the work at speed); the fan changes nothing at 125 mph.
- **R2 passes for every design** (20.1 to 23.9 min at 35 C). The fan has a small effect there (slim 23.0 min, big 21.0 min for the rev C core). The cells' own heat capacity does most of the work in a 20 min stop, so bigger fans are not worth their mass.
- **Smallest design that passes both: 2 x 152 x 118 x 28 mm (0.0359 m2) with the slim fans.** Radiators plus fans 1.40 kg against 1.56 kg for rev C, saving about 0.2 kg including the coolant it holds. A 40 mm deep core does not beat it (2 x 138 x 107 x 40 mm weighs 1.44 kg).
- **But its margin is thin.** Coolant inlet at R1: 48.4 C (smaller core) against 45.9 C (rev C). The ram-air factor (0.25) is my estimate. At 0.20 the smaller core gives 50.4 C and fails; at 0.15 even rev C gives 50.4 C and fails marginally. At 0.35, rev C is 43.2 C.

| Ram factor | Rev C inlet 25 C / 38 C | Smaller core inlet 25 C / 38 C |
|---|---|---|
| 0.15 | 50.4 / 61.6 | 53.1 / 64.1 |
| 0.20 | 47.8 / 59.1 | 50.4 / 61.6 |
| **0.25 (used)** | **45.9 / 57.3** | **48.4 / 59.7** |
| 0.35 | 43.2 / 54.7 | 45.6 / 56.9 |

- **Holding 125 mph at 38 C needs a much bigger radiator, not a chiller.** A core 1.7x the rev C area and 40 mm deep (2 x 215 x 167 x 40 mm, radiators 2.29 kg, about +1.2 kg and wider pods) gives coolant 47.7 C, cell core 53.2 C, winding 88.9 C and charger plate 51.5 C at 125 mph and 38 C. A 1.3x, 40 mm core is not enough (50.4 C inlet, 55.4 C core). I do not recommend it: it costs mass and pod width for a case Gate A already treats as a derate.

**Recommendation: keep the rev C radiator halves (165 x 128 x 28 mm each, 0.042 m2 total, slim fans). The smaller 152 x 118 x 28 mm core is only worth taking after the pod CFD confirms a ram factor of at least 0.25, and then it saves 0.2 kg.**

## 4. Thermal runaway propagation (`thermal-propagation.py`)

Method as in the earlier study, rebuilt for 21700: a 9 x 9 patch of the side-view hex lattice (23.6 mm pitch, 2 mm gaps, 70.2 mm long cells, 75 J/K each, pack at 40 C). The centre cell releases a share of its runaway heat over 10 s: 21.6 Wh x 4.5 kJ/Wh (Feng et al.), 40% or 60% retained in the cell (the rest leaves with the vented gas), plus a worst credible case of 7 kJ/Wh with 80% retained. Heat reaches neighbours through the gap filler (conduction, radiation if open), the in-row bond or busbar, and the aluminium ribbon shared by the two rows of a band (0.3 W/K est); a flowing ribbon is a sink (1.5 W/K per cell). The hottest neighbour is compared with 120 C (self-heating onset with margin) and 170 C (trigger).

| Condition (60% retained unless noted) | Coolant flowing | No coolant (crash or pump fault) |
|---|---|---|
| Foam, strip busbar, 40% retained | 82 C pass | 104 C pass |
| Foam, strip busbar | 104 C pass | 136 C marginal |
| Foam, **wire-bond fuse links** | 92 C pass | 134 C marginal |
| Worst credible (80% retained, 7 kJ/Wh), wire bonds | 150 C marginal | 235 C **propagates** |
| Worst credible, strip busbar | 173 C **propagates** | 240 C **propagates** |

- **The gap filler barely matters.** Air gap, foam, foam plus 0.5 or 1.0 mm aerogel, and full 2 mm aerogel all land within 6 K of each other (for example 136 to 141 C at 60% with no coolant and a strip busbar). Heat goes through the busbar and the ribbon, not the gap.
- **The ribbon's own lateral conduction is the biggest lever.** Cutting the in-band ribbon path from 0.30 to 0.10, 0.03 and 0 W/K drops the 60% no-coolant neighbour from 134 to 118, 102 and 92 C, and the worst case from 235 to 202, 169 and 148 C.
- **Hand bound** (all trigger heat shared by 6 neighbours, nothing lost): 126 C (40%), 170 C (60%), 309 C (80%, 7 kJ/Wh). The model sits below it, as it should.
- **Vent sizing** (est): about 1.5 L/Ah gives 9 L at room conditions, about 24 L hot, per cell. At 20 kPa case overpressure and 3 s that is **44 mm2 per cell, 490 mm2 for a failed parallel group of 11**. A whole 275-cell lane would need 12,000 mm2, which is not buildable; the design relies on stopping propagation at the group.

**Barrier and vent specification (screening level, not a test result):**
1. Cell-to-busbar links as **wire-bond fuse links** (rev C has 2,200 bonds), not strip.
2. **Slot or segment the ribbon** so the in-band lateral conductance is at most 0.03 W/K, or use a lower-conductivity ribbon in the cross-bike direction.
3. Intumescent foam (k 0.08) in non-ribbon gaps and 0.5 mm mica on lane ends; do not spend mass on aerogel in the gap.
4. **Four burst vents, one per lane, each at least 600 mm2 (about 28 mm diameter), opening at 15 to 20 kPa, ducted to the belly**, fed from the 10 mm lane-to-lane plenum behind the positive ends. (The earlier pack vent at 50 mm diameter on one face is for a 15 Ah cell; here per-lane vents are better.) Keep the vent path away from the pump, motor and the inlet.
5. BMS keeps the pump running after any thermal event; the ribbon is only a heat sink while coolant flows.
6. **Prove it with a single-cell nail or heater trigger test on a lane module.** The model has no gas jets, ejecta or hot-particle ignition of neighbours.

## 5. Mass and cooling parts

Bill for the **rev C radiator** (supplier-less estimates; the ribbons are in pack internals):

| Item | kg |
|---|---:|
| Radiator cores and tanks, dry (2 x 165 x 128 x 28) | 1.06 |
| Slim fans x2 | 0.50 |
| Pump (22 L/min, 74 kPa) | 0.55 |
| 4-port valve (radiator bypass) | 0.45 |
| 3 kW PTC heater | 1.14 |
| Hoses (1.6 m of 14 mm trunk, 2.2 m of 12 mm branches) and clamps | 0.59 |
| Temperature sensors | 0.10 |
| Coolant, 2.55 L of 50/50 glycol (ribbons 0.81, radiators 0.38, hoses 0.50, manifolds 0.25, motor 0.20, rest 0.41) | 2.72 |
| **Total** | **7.11** |

With the smaller radiator it is 6.91 kg. A wax thermostat instead of the valve saves 0.30 kg (6.81 kg; 6.61 kg with the smaller core). The 3 kW PTC at 1.14 kg is an estimate scaled from 1.9 kg for 5 kW; a thin-film unit could be lighter. **The 6.0 kg budget is exceeded by 1.1 kg; it closes (5.7 kg with the thermostat) only if the ribbon and manifold coolant, 1.1 L or 1.1 kg, is booked with the ribbons in pack internals.** The CAD roll-up counts 9.0 kg for cooling today (it includes the oil cooler and its own coolant allowance), so this bill is 1.9 kg lighter than the roll-up.

## 6. Energy balance and hand checks

| Check | Result |
|---|---|
| Thermal closure (heat generated + heater = to radiator + to air + stored), all 35 cases | within 0.016% |
| Drive electrical (battery OCV power = wheel work + belt + motor + inverter + pack I2R + auxiliaries), 125 mph 25 C | 80.06 MJ both sides, residual 0.00% (wheel 71.5 MJ; losses: belt 0.78, motor 3.04, inverter 1.59, pack 2.63, aux 0.50) |
| Same, hard-riding 25 C | 31.01 MJ both sides, residual 0.00% |
| DC charge 10-80% 25 C: station = chemical + cell heat + external I2R | 17.95 kWh = 17.11 + 0.79 + 0.05 kWh, residual 0.00%. 17.1 kWh stored against 16.6 kWh (70% of 23.76 kWh nameplate); drive study gave 17.98 kWh station |
| Cell heat at 18 A, 10% SOC, 25 C | 6,961 W by hand and by model |
| Heat in the 25 C charge | adiabatic rise 30 K against 20.2 K in the model; the radiator takes 23% of the heat, the rest of the difference is lag in cell-to-coolant transfer |
| Radiator at 125 mph (14 m/s face, coolant 45 C, air 25 C) | e-NTU 3,355 W, counterflow LMTD upper bound 3,443 W (cross-flow should be a little below, as found) |
| Heat to the coolant at 125 mph, start of run | cells 1.56 kW, motor 1.83 kW, inverter 0.96 kW, DC-DC 0.02 kW, pump 0.05 kW = 4.4 kW. Drive study: pack 1.7-2.7 kW (end of run, higher resistance), motor 1.9 kW, inverter 1.0 kW |
| Time step and grid | charge and hot-day results identical from dt 0.25 s to 2 s; cell FD resistance 0.329, 0.323, 0.322 K/W on three grids |
| Sensitivity of the 35 C charge to cell resistance | x0.8: 20.6 min; x1.0: 23.0 min; x1.25: 25.8 min (fails 25 min) |

Against the drive study (`06`): charge times here are 1.6 to 3 min longer (17.1 against 15.5 min at 25 C; 23.0 against 20.1 min at 35 C) because the detailed model carries a 1.19 resistance factor and keys the derate to the hottest can; the hot-day pack is 2 to 4 K hotter (60.9 against 57 C) because resistance rises as SOC falls, which the lumped model underplayed.

## CAD change requests (for the owner of `build-adventure.py`)

| # | Change | Exact numbers | Why |
|---|---|---|---|
| T1 | **Radiator halves: no change.** Keep two cores 165 x 128 x 28 mm (0.042 m2), slim fans | Optional later: 152 (long) x 118 (tall) x 28 mm each, only if CFD shows face velocity of at least 0.25 x road speed. Saves 0.17 kg of core and 0.04 L of coolant | Section 3 |
| T2 | **Pack ribbons (not in CAD yet):** 28 serpentine aluminium multiport ribbons, 7 per lane x 4 lanes, one between each pair of cell rows, in the 2 mm row gap | 70 mm wide (across the bike, the cell length) x 1.2 mm thick, 8 ports of 7.5 x 0.8 mm, 0.60 m run each, 39 cells touched; dielectric coating 50 um; pack-roof inlet and outlet manifolds. Slot the ribbon between cells so lateral conduction is at most 0.03 W/K | Cooling, runaway |
| T3 | **Hoses and plumbing order** | 14 mm ID trunk about 1.6 m (pump to PTC to split), 12 mm ID branches about 2.2 m total. Drive branch order: **motor, inverter, charger and DC-DC plate**; the charger plate is last and reaches 61.1 C on the hot day, so either put it first or accept a derate; pack branch with a balancing orifice | Coolant inlet limits |
| T4 | **PTC and valve** | Keep the 3 kW PTC envelope (70 x 30 x 55) and the valve (50 x 38 x 52). Option for 0.3 kg: replace the 4-port valve by a wax thermostat bypass | Cold charge, mass |
| T5 | **Pack vents** | Four burst vents, one per lane, each at least 600 mm2 (28 mm diameter) at the positive-end plenum (10 mm lane gap), ducted to the belly skid, opening 15 to 20 kPa, plus a separate breather | Runaway |
| T6 | **Pump** | One pump of about 22 L/min at 74 kPa (27 W hydraulic); CWA50 class is at the edge, so get EMRAX jacket and CM200DX plate pressure drops before selecting | Hydraulics |

## Decisions for the program lead

1. **Hot-day derate rule** (Gate A allows it): cap at 105 mph, or time-limit 125 mph to about 10 min, whenever ambient is 35 C or more and the coolant inlet exceeds 50 C or a cell core estimate exceeds 55 C. Ask EMRAX whether a 55 to 60 C inlet is allowed; if so the 10.6 min becomes about 17 min.
2. **Cold charge:** accept 25.4 min with 3 kW (marginal) or move to 5 kW (+0.8 kg, 21.6 min), or require pre-heating from the navigation route (14.0 min for 0.79 kWh).
3. **Cooling mass:** either raise the cooling budget to about 6.8 kg, or move the ribbon coolant to pack internals and take the wax thermostat.
4. **Chiller:** still not needed. It would only fix the 38 C 125 mph case and the 42 C-arrival charge, both of which Gate A already treats as derate cases.

## What this does not prove

- **Radiator performance rests on my ram-air factor (0.25 x road speed) and a class-level core conductance.** No CFD of the pod, no measured core, no fan curve against the real core pressure drop. The fan flows (0.035, 0.06, 0.09 m3/s) are estimates.
- **The cell heat uses an assumed resistance multiplier (1.19) and a cell-internal conductivity (0.6 and 25 W/mK) from the literature.** The P60B datasheet (v0.1) gives DC and AC resistance only at 50% and 30% SOC. No calorimeter data. A cell resistance 25% higher moves the 35 C charge from 23.0 to 25.8 min.
- **The charge derate map is mine**, not the cell maker's. P60B charge life at 3C or above is unconfirmed (see `06`).
- **EMRAX inlet limit (50 C) is a datasheet number at 30 C ambient;** the rotor surface limit (80 C) is not modelled because no rotor thermal data is published. The motor is one lumped node.
- **CM200DX coolant limits and current derating, charger and DC-DC plate limits are estimates;** the supplier gives no curve.
- **The pressure drops of the motor jacket, inverter and charger plates are estimates;** the pump choice depends on them.
- **Runaway screen:** 2-D patch, estimated heat release (4.5 and 7 kJ/Wh), estimated ribbon lateral conductance, no gas jets, ejecta or particle ignition, no venting model coupling. It is a screen, not a UN R136 result. Wire-bond heat paths and burst vent sizing are first estimates.
- **Duty cycles are mine** (a 90 s hard-ride cycle, a 7.5% climb). The pack starts each case at ambient temperature; real riding starts warm, which hurts the hot-day cases and helps the cold ones.
- **The rev C CAD does not contain ribbons, manifolds, hoses or vents;** mass and volumes come from my sizing, not from the CAD roll-up.
- Nothing here was bench-tested. Hot-case fan noise and fan power (50 to 180 W) were not assessed against the 12 V budget.
