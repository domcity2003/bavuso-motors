# Parts ledger and Gate A budget check

> **Superseded in part (Nov 22, 2026).** The early sections describe the ledger at earlier states; the authority is `00-V1-final-spec.md`. Final: 257.9 kg / 569 lb against T1 <= 260 kg (the last section, 257.32 kg, is current except that the rear disc fix moved it to about 257.5). Stale here: the 240 kg budget check, the 277.75 kg and 247.93 kg runs, and the 252.93 kg rev E run against a 255 kg limit; "budget_pass" now means little because group budgets were re-set to the actuals (headroom 2.1 kg, 0 kg measured).


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

## The plain answer

**The mass system is built and tested. Run one command and it gives you every part's mass, each system against its Gate A budget, and a pass/fail flag.** It does not edit the CAD generator, and it did not touch the live `mass-rollup.csv` / `.json` (all test output is in `program/data/run/ledger-test/`).

- **One ledger.** `tools/mass-rollup.py` writes `program/data/parts-ledger.csv`, one row per part (id, name, system, make/buy, status, material, process, mass, mass source, cost, drawing, CAD solid, plus a few guard columns). `mass-rollup.csv` and `.json` are still written with the same columns and keys, so the FEA, dynamics and aero scripts keep working.
- **Double counts are removed.** With `--legacy` the script reproduces the reconciled old bike: **319.645 kg against 319.643 kg in `03-mass-ledger.md`**, every CAD line identical (only allowance rows were renamed or split).
- **Gate A budgets are enforced.** The report prints each system against its budget and the total against 240 kg. `budget_pass` is `false` on any overrun, and the exit code is 1.
- **Supplier masses are pre-loaded** for the shortlisted hardware and bind by name pattern, so renamed CAD solids still match. Anything that does not match is listed loudly and the exit code is 2.
- **On today's (old) CAD the V1 run fails, as expected**: 277.8 kg against 240, every system over budget, and 2 solids with no V1 rule (the old IPM motor box and gear-oil cooler).

| Test run | Total | Budget pass | Ledger clean | What it proves |
|---|---|---|---|---|
| Old CAD, `--legacy` | 319.64 kg | no (expected) | yes | The reconciliation is applied; matches `03-mass-ledger.md` to 0.002 kg |
| Old CAD, V1 mode | 277.75 kg | no (expected) | no | Slots bind to real CAD names; 2 unmatched solids shouted; 3 supplier rows added with no CAD solid |
| 20 invented new-style names | 193.47 kg | no (pack case over) | no | Renamed parts still bind; one unknown solid, 2 missing required parts and a short caliper count all reported |

## How it works

1. **Read the CAD** (read-only; the file is never saved). Each solid gets a volume, area and centroid. `--solids-csv` lets it run on a list of solids without FreeCAD, and `--dump-solids` writes that list.
2. **Bind every solid** to a mass source, in this order:
   1. **Supplier slot** (`program/data/supplier-masses.csv`): a regex on the solid name (case-insensitive). 29 slots cover P60B cells, EMRAX 228, inverter (H100 default, CM200 alternate), belt and pulleys, charger, DC-DC (two variants), BMS, EVCC, one HV box, NACS inlet, fork, shock, wheels, tyres, discs, carriers, calipers, rear bracket and ABS.
   2. **Rule** in `RULES` inside the script (glob patterns, volume x density, shell, or fixed mass). If two rules match, **the most specific wins** (exact name, then longest literal text), not file order. Equal-specificity ties are printed as `AMBIGUOUS`.
   3. **Nothing matches: UNMATCHED.** The solid is printed, listed in the json, and added to the ledger as a zero-mass `UNMATCHED` row.
3. **Slot modes.** `each` gives each matching solid the stated mass and checks the expected count (a short count adds the missing pieces as non-CAD rows and prints `SLOT COUNT`). `total` splits one assembly mass over all matching solids by volume (cells, fork, shock, HV box).
4. **Slots with no CAD solid** (and not satisfied by another variant in the same group) are carried as a ledger row marked `[NOT IN CAD: from supplier table]` and printed. The mass is not lost, and when the CAD part appears, its name binds and the fill row disappears.
5. **Allowances** (wiring, fluids, fasteners, brackets, pack internals) are rows with status `concept`, a stated `includes_excludes`, and a `watch` pattern: if a CAD solid appears that looks like the thing the allowance covers, the script prints `OVERLAP` so the double count is caught.
6. **Guards.** Rules and slots cannot share a `scope_tag`; two non-CAD rows cannot share one; a CAD solid cannot have two rows; `required` parts (pack case, head tube, swingarm) missing from the CAD are reported. For fixed-mass rows the script flags a CAD stand-in whose implied density is above 8 or below 0.2 g/cm3.
7. **Stable ids** `BV-<SYS>-<4 digits>` come from `program/data/parts-id-registry.csv` (key to id). Ids are never reused; new parts get the next number.
8. **Budget check** (`program/data/budgets.csv`): systems ENG, CHS, RUN, DRV, ELC, BOD+PRO, THM, ALW are summed against Gate A. A system is `OVER` above budget and `TIGHT` within 5%. The total is checked against 240 kg. The 12 kg margin is held back: `margin_kept` is true only at 228 kg or below. A growth-adjusted column (concept +15%, proposed +10%, design-intent +5%, released +1%) is printed for information and does not decide pass or fail.

System codes: ENG pack, DRV drive, ELC electronics, THM cooling, CHS chassis (frame, swingarm, subframe, shock mount), RUN running gear (fork, shock, wheels, tyres, brakes, ABS, controls, stand), BOD body, PRO protection (budgeted together with BOD), ALW wiring, fasteners and fluids.

### The json flags

`budget_pass` (every system and the total within budget), `ledger_clean` (no unmatched solids, duplicates or missing required parts), `overall_pass` (both). Detail is under `budget` and `integrity` (unmatched solids, duplicates, ambiguous matches, slot count mismatches, slots filled without CAD, allowance overlaps).

Exit code: 0 pass, 1 budget overrun, 2 ledger not clean (2 wins). `--soft` always exits 0.

## How to run

From `v1.0`:

```
../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/mass-rollup.py                        # V1 mode, writes the canonical files
../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/mass-rollup.py --out-dir <folder>     # write everything flat into a folder instead
... tools/mass-rollup.py --pick inverter=inverter_cm200          # use the CM200 when the CAD has no inverter yet
... tools/mass-rollup.py --legacy --out-dir <folder>             # old-bike reconciled ledger
... tools/mass-rollup.py --solids-csv solids.csv                 # no FreeCAD needed
... program/tools/ledger-regression.py <legacy parts-ledger.csv> # compare the legacy run with the reconciled ledger
```

Default outputs: `mass-rollup.csv`, `mass-rollup.json` (v1.0), `program/data/parts-ledger.csv`, `program/data/mass-budget-report.csv`, `program/data/parts-id-registry.csv`. A full CAD build is not needed or run; the script only reads the saved file.

## Corrections applied (the reconciled ledger)

All the corrections in `03-mass-ledger.md` are built into the rules and allowances: BROGEN 3.0 kg, pack internals rebuilt bottom-up (7.26 + 6.19 kg), coolant 5.24 kg and dry radiator cores, HV cables 3.72 kg, VCU/distribution 2.10 kg, LV harness 2.08 kg, EVCC added, the side-stand, DC-DC and charge-inlet allowances deleted, master cylinder, panel bolts and gear-oil overlaps removed, rear disc 1.17 kg and the Cascadia 6.75 kg. V1 mode also drops the passenger pegs (Gate A T7 is solo) and the gear oil (single-stage belt).

## Test output on the current saved CAD (the old bike)

`cad/Bavuso-V1.0-adventure.FCStd`, V1 mode (`program/data/run/ledger-test/v1/`):

```
system (Gate A)              budget      mass  headroom       %  w/growth  flag
Battery pack                  103.0    106.68     -3.68   -3.6%    118.02  OVER
Chassis                        18.0     31.74    -13.74  -76.3%     35.00  OVER
Running gear                   37.0     45.13     -8.13  -22.0%     50.25  OVER
Drive                          20.0     23.05     -3.05  -15.2%     25.36  OVER
Electronics                    18.0     18.67     -0.67   -3.7%     20.86  OVER
Body and protection            15.0     29.96    -14.96  -99.8%     34.45  OVER
Cooling                         6.0     11.40     -5.40  -90.0%     13.11  OVER
Wiring, fasteners, fluids      11.0     11.12     -0.12   -1.1%     12.79  OVER
TOTAL (T1)                    240.0    277.75    -37.75  -15.7%            OVER  (612.3 lb)
BUDGET_PASS = False   LEDGER_CLEAN = False
!! UNMATCHED CAD SOLIDS (2): IPM_motor_and_gear_case_ENVELOPE, Oil_cooler
!  Supplier slots with no CAD solid: motor_emrax228, evcc, abs_module
```

Reading it: the old CAD is the old bike, so everything is over. Note the V1 total (277.75 kg) is lower than the 319.64 kg legacy total mostly because the V1 hardware masses replace the old ones (cells 82.5 kg instead of 106.9, EMRAX 13.2 instead of the 21 kg IPM unit, 43 mm fork, and so on) while the old frame, body and cooling geometry are unchanged. It is not a forecast of the new design.

Useful early signals for the CAD architect, from this run:
- **Pack:** cells 82.5 kg (1100 x 75 g, a datasheet maximum) plus internals 13.45 kg leaves **7.05 kg for the case** at the 103 kg limit. The old 4 mm case is 10.73 kg. The pack internals figure was derived for a 594-cell pack and is not re-derived for 100s11p.
- **Drive:** EMRAX 13.2 + H100 3.5 + belt and pulleys 3.1 = 19.8 kg against 20 kg. With the CM200 it is 23.05 kg. The motor's published range is 12.9 to 13.5 kg.
- **Wiring, fasteners, fluids** is already at 11.1 kg with only allowances in it (HV cables 3.72 is the lever; the shortlist hopes for 1.5 with shorter runs).

## When the new CAD part list arrives

Send the list of CAD solid names (or just run `--dump-solids`). Then: (1) run; (2) every `UNMATCHED` solid gets a rule or a slot pattern; (3) every `NOT IN CAD` slot row becomes real once its solid is named; (4) every `OVERLAP` line either deletes an allowance or confirms it covers something different; (5) move rows from `concept` to `proposed` or `design-intent` as drawings appear; (6) the lead commits the canonical outputs.

## What this does not prove

- **No mass here is measured.** Only masses from datasheets (labelled supplier) and CAD volumes (calculated) are firmer than estimates; the supplier slots for fork, shock, wheels, tyres, discs, charger class, DC-DC, BMS, pulleys and ABS are estimates, as in `02-hardware.md`.
- **Cell mass is the 75 g datasheet maximum**, and the P60B 2C fast-charge rating is unconfirmed (Gate A risk 1).
- **The pack internals, coolant and HV cable rows are not re-sized for V1** (100s11p, single loop, new motor). They carry the reconciled old-bike numbers.
- **Name patterns are only tested on the old CAD names and 20 invented ones.** Real new names may need pattern changes; the script says so loudly when they do.
- **The growth percentages are a proposal** and do not drive pass or fail. A system within budget on raw mass can still be at risk.
- **Cost columns** are filled only for supplier-slot parts and are retail or estimate figures, not at-scale cost.
- **`by_source` keys in `mass-rollup.json` changed** to measured / supplier / calculated / estimate (the old labels were supplier/catalogue, CAD geometry, engineering estimate). No script in `detailed-design/tools` reads that key, but I did not check every script.
- The canonical `mass-rollup.csv` / `.json` were not regenerated; they still hold the old 328.4 kg ledger until the lead reruns.

## Files

- `tools/mass-rollup.py` (rewritten), `program/tools/ledger-regression.py`
- `program/data/budgets.csv`, `program/data/supplier-masses.csv`
- `program/data/run/ledger-test/` (legacy, v1, v1b, synthetic outputs, console logs, `solids-old-cad.csv`)

## Rev D update

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

**The plain answer: on the rev D CAD the ledger now reads 247.9 kg against 240 kg (ledger clean, budget still over), and 246.2 kg once the carbon wheels appear in the CAD.** The canonical `mass-rollup.csv` / `.json` and `parts-ledger.csv` were regenerated from the saved rev D model (no CAD rebuild).

| System | Budget kg | Rev D kg | Over (-) / under |
|---|---|---|---|
| Battery pack | 103.0 | 104.92 | -1.92 |
| Chassis | 18.0 | 22.56 | -4.56 |
| Running gear | 37.0 | 45.38 | -8.38 |
| Drive | 23.0 | 23.45 | -0.45 |
| Electronics | 18.0 | 17.44 | +0.56 |
| Body and protection | 15.0 | 14.35 | +0.65 |
| Cooling | 6.0 | 6.90 | -0.90 |
| Wiring, fasteners, fluids | 11.0 | 12.93 | -1.93 |
| **Total** | **240.0** | **247.93** | **-7.93** |

Drive budget is 23 kg in `budgets.csv` today (the 20 kg figure above was the first version).

What changed (all in `tools/mass-rollup.py` and `program/data/supplier-masses.csv`; backups in `program/data/run/*bak-before-revD`):

- **Coolant allowance 5.24 to 2.35 kg, not the 1.6 kg asked for.** `10-thermal.md` section 5 gives coolant 2.72 + hoses 0.59 + sensors 0.10. Of the coolant, 1.06 kg sits in the pack ribbons and manifolds, which that document says must be booked with the pack. So the loop allowance is 2.72 - 1.06 + 0.59 + 0.10 = 2.35 kg, and **pack thermal internals go from 6.19 to 7.25 kg** (+1.06). Net coolant change is -2.89 + 1.06 = -1.83 kg. Using 1.6 kg would have dropped about 0.75 kg of hoses, sensors and glycol; the shortlist's 1.6 covers "hoses and 2 L coolant" only. If the lead wants 1.6, change `coolant_fluid` to 1.6 (total 247.2 kg).
- **HV cables 3.72 to 5.53 kg (not 1.5).** `07-electrical.md` computes 5.53 kg: 8.4 m of cable plus 2.54 kg of connectors, lugs and conduit (12 large and 14 small connectors, 8 lugs). Lengths are +-30% estimates. A short-bus layout could save about 1 kg. The 0.74 kg inlet-to-HV-box leads may overlap the NACS slot (1.6 kg "with HV leads"); I did not remove it.
- **New rules:** `Coolant_thermostat_wax` 0.15 kg and `Coolant_PTC_heater_3kW` 1.14 kg (the 5 kW rule is now legacy-only); front discs 320x5 at 1.2 kg each (slot `disc_front`, was 0.95); swingarm shell wall 4.0 mm (was 4.25).
- **Carbon wheels adopted as slots** `wheel_front_carbon` 2.6 kg and `wheel_rear_carbon` 3.3 kg (shortlist ALT, BST class). They bind when a CAD wheel name contains `carbon` or `BST` together with `front_wheel`/`wheel_front` (or rear), in either word order. Until then the forged slots apply. Tested on a copy of the rev D solid list with the wheels renamed `Front_wheel_carbon_BST` / `Rear_wheel_carbon_BST`: total 246.23 kg (-1.70 kg), ledger clean, outputs in `program/data/run/ledger-revD-carbon-test/`.
- **Bug fixed:** `Motor_pulley_bearing_carrier` was matching the motor pulley slot and getting 0.5 kg as a second pulley. It now has its own 0.4 kg estimate rule (+DRV) and the pulley pattern excludes "carrier".

**Open flags:** Radiator cores are counted at 0.805 kg each (1.61 kg) against 1.06 kg in `10-thermal.md`, so cooling may be about 0.55 kg heavy. `evcc` and `abs_module` are still carried from the supplier table (no CAD solid). Rear disc is 267x5 in CAD but the slot is 245x5 at 0.85 kg.

### What this update does not prove

The coolant, HV cable and pack-internals rows are still concept-level estimates and the CAD may change them. The carbon wheel mass is an estimate; no maker publishes it, and certification is unresolved.

## Rev E

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

**The plain answer: on the rev E CAD the ledger reads 252.93 kg against the re-baselined 255 kg limit. `ledger_clean` is True, but `budget_pass` is False because the chassis is 4.78 kg over its 25 kg line.** The total passes with 2.07 kg to spare, which is less than the 3.5 kg margin the lead wants kept (design cap 251.5 kg).

| System | Budget kg | Rev E kg | Headroom |
|---|---|---|---|
| Battery pack | 105.0 | 104.91 | +0.09 |
| Chassis | 25.0 | 29.78 | -4.78 |
| Running gear | 45.0 | 43.08 | +1.92 |
| Drive | 23.5 | 23.45 | +0.05 |
| Electronics | 18.0 | 17.44 | +0.56 |
| Body and protection | 15.0 | 14.45 | +0.55 |
| Cooling | 7.0 | 6.90 | +0.10 |
| Wiring, fasteners, fluids | 13.0 | 12.93 | +0.07 |
| **Total** | **255.0** (margin 3.5) | **252.93** | **+2.07** |

Changes:
- **Budgets** (`budgets.csv`, backup in `program/data/run/`): the lead's allocation; the eight systems sum to 251.5 kg and the margin is 3.5 kg, total exactly 255.
- **Steering damper:** `Steering_damper_semiactive` 0.5 kg (estimate, Ohlins EC class; I did not check a published mass). It was the one unmatched solid.
- **Nodes zeroed:** `Upper_rail_node_*` (4 solids, 0.6 kg) set to 0. The Round 2 chassis table in `09-structures.md` (25.4 kg modelled) has no separate line for nodes; the CAD solids without nodes sum to 25.33 kg, which matches it.
- **Pivot bearings:** `Pivot_6008_*` is now 32012 X at 0.7 kg each. Round 2 specifies one pair on the single-sided arm pivot and the CAD has two bearing solids, so 1 pair = 1.4 kg (was 0.24 kg). The 0.7 kg is a planning figure; the catalogue mass is likely lower and should be checked.
- **Chassis booked to Round 2:** new allowance `chassis_unmodelled` 1.3 kg (pack mounting pads 0.8, arm boss and end plates 0.5), bringing the structure to about 26.6 kg against Round 2's 26.7 kg. Lug plates (0.44 kg) were not added: the CAD solids already match the 25.4 kg figure without them.

Why the chassis is still over: 25.33 structure + 1.3 unmodelled + 1.4 bearings + 1.75 existing allowances (nose subframe 1.15, pivot hardware 0.6) = 29.78 kg. The 25 kg line looks like it was set from the Round 2 structure alone, without the bearings and allowances.

### What this update does not prove
The damper and bearing masses and the 1.3 kg top-up are estimates. Nothing was weighed.

### Rev E, final pass (BOM and drawings gaps)

**The ledger total is now 257.32 kg (was 252.93), over the 255 kg limit by 2.32 kg. `ledger_clean` True, `budget_pass` False** (pack, chassis and drive over). `budgets.csv` was not touched by me.

- **Cell holders, BV-ENG-0102, 3.09 kg (calculated).** Method: hex pitch 23.6 mm gives 482 mm2 per cell; minus a 284 mm2 aperture; times 2.5 mm, 2 plates, 1.35 g/cm3 (PA66-GF30) = 2.69 g per cell; times 1,100 cells = 2.96 kg; plus 4% for borders and ribs. This equals the drawing's 0.773 kg x 4 lanes. The pack is 10 modules of 110 cells (07-electrical.md), so 0.309 kg per module; the mass follows the cell count, not the module count. The ENG pack is now 108.0 kg.
- **Swingarm hub carrier and bearings, 1.10 kg (calculated).** Nothing like it existed: `axle_rear` (1.0 kg) is axle, spacers and adjusters, and the 0.4 kg carrier is on the motor. Cast A356 housing 0.8 kg plus 2 bearings 0.3 kg. Full arm: shell, tower and brace 4.14 + boss and end plates 0.5 + carrier 1.1 = 5.7 kg, 6.7 kg with the axle. That sits inside the 5 to 8 kg range for single-sided arms (Ducati, MV, Triumph) you quoted; I did not check published masses.
- **Drive lines renamed** to Gates 8MGT-1760-62 (8 mm, 62 mm wide), 35T motor pulley and 126T rear pulley.
- **Rear pulley 2.1 to 2.3 kg (calculated).** Rim 8 mm radial (1.43 kg), 5 mm web with 8 holes (0.49), hub (0.28), flanges (0.1). The 9.1 kg CAD solid is a plain disc. The belt (0.5) and 35T pulley (0.5) masses are unverified.
