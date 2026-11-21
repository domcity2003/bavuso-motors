# Parts ledger and Gate A budget check

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
