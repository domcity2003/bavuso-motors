# Mass ledger audit and rebuild scheme

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

## The plain answer

- **The reconciled bike is 319.6 kg (704.7 lb), not 328.4 kg (723.9 lb).** That is 8.7 kg (19 lb) lighter on paper. It is still far from 400 lb: the gap to 400 lb is 304.7 lb.
- **The review named 3.4 kg of double counts. I found 15.7 kg of overstatement and 7.0 kg of understatement** (net -8.7 kg). The biggest single error is the on-board charger: 6.5 kg in the ledger, 3.0 kg or less in the catalogue.
- **Nothing here fixes weight.** Everything outside the pack is now 188.5 kg (415.7 lb) against the review's 195 kg (429 lb). The pack plus its internals is 131.1 kg (289 lb). The large gap the review described is real; the ledger cleanup only removes about 13 lb of it.
- **64% of the mass is still an estimate.** After I relabelled the cells as estimates (the 26120 cell is not on open sale), 211 kg of 320 kg rests on hand figures; 107 kg of that is the cells. About 75 of the 138 estimate lines can be swapped for a published supplier mass.
- **All four other review claims check out** (rear rotor 5 mm vs 6 mm, lower cover gap 1.99 mm, belt clearances 14.19 and 15.00 mm, and the ledger sum of 328.37 kg).
- **I did not edit any existing file.** New files are listed at the end.

| Item | Before | After | Change |
|---|---|---|---|
| Ledger total | 328.37 kg / 723.9 lb | **319.64 kg / 704.7 lb** | -8.73 kg / -19.2 lb |
| Pack (cells, case, internals) | 133.65 kg | 131.10 kg | -2.55 kg |
| Everything else | 194.72 kg | 188.54 kg | -6.18 kg |
| Lines | 210 | 211 (one added: EVCC) | |
| Lines changed | | 32 rows (26 distinct items, plus the cell relabel) | |

## 1. Reconciliation

### How I checked the ledger is current

I ran a copy of `tools/mass-rollup.py` (`program/tools/mass-rollup-recheck.py`, outputs in `program/data/run/`) against the saved CAD at commit 5f451ef. It reproduces `mass-rollup.csv` line for line and gives 328.37 kg. So the ledger matches the current CAD; any error is in the rules, not in a stale run. The header in `mass-rollup.json` still says "prepared 2026-11-05".

The review's page 2 figures also check out against the file: wheels and tires 18.5 kg (41 lb), motor and reduction 21 kg (46 lb), charger 6.5 kg (14 lb), two guard tubes 4.81 kg (10.6 lb), pack 133.65 kg (295 lb), and the three named allowances 1.4 + 1.2 + 0.8 = 3.4 kg.

### Corrections applied (largest first)

"Source" gives the evidence. Paths are relative to `v1.0/`.

| # | Item | Now | Reconciled | Change kg | Kind | Why |
|---|---|---|---|---|---|---|
| 1 | BROGEN PV1776 charger | 6.50 | 3.00 | **-3.50** | stale estimate | Catalogue lists 3 kg at most (`detailed-design/electrical/electrical-bom.csv`; `components-electrical.csv` V1-E007) |
| 2 | Pack internals plug | 16.00 | 13.45 | **-2.55** | stale plug | Was "optimiser pack mass minus cells and case". Rebuilt from the electrical BOM (7.26 kg excl. BMS) and thermal sizing (6.19 kg) |
| 3 | Coolant pump, hoses, 2 L coolant | 2.80 | 5.24 | **+2.44** | understated | 3.9 L of glycol is 4.19 kg, hoses 0.95, sensors 0.10 (`thermal-study.md` table). Pumps removed from this line because they are modelled |
| 4 | Radiator cores (2) | 3.80 | 1.61 | **-2.19** | double count | Ledger said "filled"; the coolant is in line 3. Dry core is 0.805 kg |
| 5 | HV cables and lugs | 2.20 | 3.72 | **+1.52** | understated | BOM: cable 2.12 + 10 connectors 1.20 + lugs and conduit 0.40 |
| 6 | VCU, keyless, horn | 0.70 | 2.10 | **+1.40** | rescope | Horn (0.4 kg) is modelled, so it leaves. Adds the distribution box 1.15, VCU 0.40, keyless 0.25, bonding 0.30 that were never carried |
| 7 | Side stand allowance | 1.40 | 0 | **-1.40** | double count | `Side_stand_retracted` is modelled (review item) |
| 8 | DC-DC allowance | 1.20 | 0 | **-1.20** | double count | HELLA 2.8 kg is modelled (review item) |
| 9 | LV wiring harness | 3.00 | 2.08 | **-0.92** | stale / overlap | BOM harness 2.4 kg, minus the modelled bar-harness legs 0.32 kg |
| 10 | Charge inlet allowance | 0.80 | 0 | **-0.80** | double count | `NACS_charge_inlet` is modelled (review item) |
| 11 | Steering bearings, stem nut, damper | 0.80 | 0.30 | -0.50 | double count | `Steering_damper_envelope` (1.1 kg) is modelled |
| 12 | Gear-case oil and exchanger | 0.90 | 0.45 | -0.45 | overlap | `Oil_cooler` (0.6 kg) is modelled; only the 0.5 L of oil stays |
| 13 | Front axle, spacers | 0.60 | 0.15 | -0.45 | overlap | The fork axle clamps are noted "half the axle too" |
| 14 | Radiator fans (2) | 0.70 | 1.10 | +0.40 | stale estimate | Sized fan with shroud is 0.55 kg each, not a 0.35 kg slim fan |
| 15 | NACS inlet (modelled) | 1.30 | 0.90 | -0.40 | overlap | Volex 0.9 kg; the "HV leads" are in the HV cable line |
| 16 | Front master cylinder | 0.35 | 0 | -0.35 | double count | Hand levers are noted "lever with radial master cylinder" |
| 17 | Rear disc | 0.85 | 1.17 | +0.32 | stale | Ledger says 267x6, CAD is 267x5 and already weighs 0.97 kg. Front discs match CAD volume. At 6 mm: 1.17 kg |
| 18 | Hand grips (2) | 0.70 | 0.40 | -0.30 | overlap | Note includes "switch housing"; `Switch_cube_*` is modelled |
| 19 | PTC heater | 1.60 | 1.90 | +0.30 | stale estimate | Sized part 1.90 kg |
| 20 | Cascadia CM200 | 6.50 | 6.75 | +0.25 | stale | Maker publishes 6.75 kg. The note quoting "11.3 kg (retailer)" conflicts |
| 21 | EVCC (added) | 0 | 0.20 | +0.20 | omitted | Native NACS needs it (Advantics, BOM) |
| 22 | Nose subframe and dash brackets | 1.30 | 1.15 | -0.15 | overlap | `Display_mount` is modelled |
| 23 | Coolant pumps (2) | 1.40 | 1.10 | -0.30 | stale | Sized as 1.10 kg for two |
| 24 | Panel bolts (2) | 0.10 | 0 | -0.10 | overlap | The 3.0 kg fastener allowance covers all bolts |
| 25 | 12 V battery | 1.00 | 0.90 | -0.10 | stale | Shorai LFX14A4 0.90 kg |
| 26 | GX14 contactors (2) | 0.90 | 1.00 | +0.10 | stale | Datasheet 0.5 kg each |
| 27 | Cells | 106.9 | 106.9 | 0 | relabel | Kept; source changed from supplier to estimate (not on open sale) |

Total decreases 15.66 kg, increases 6.93 kg, net -8.73 kg. The full line-by-line file is `program/data/mass-ledger-reconciled.csv` (columns: item, group, kg_now, kg_reconciled, action, reason, source_type, plus system and confidence).

### By system

Systems here are my regrouping (allowances moved to the system they serve).

| System | Now kg | Reconciled kg | Change |
|---|---|---|---|
| Energy (cells, case, pack internals) | 133.65 | 131.10 | -2.55 |
| Running gear | 52.57 | 51.29 | -1.28 |
| Chassis | 36.69 | 36.69 | 0 |
| Electronics (HV, LV, charging) | 33.23 | 29.78 | -3.45 |
| Body | 28.38 | 28.13 | -0.25 |
| Drive | 24.40 | 23.95 | -0.45 |
| Cooling | 11.35 | 12.00 | +0.65 |
| Protection (guards, sliders, stand) | 8.10 | 6.70 | -1.40 |
| **Total** | **328.37** | **319.64** | **-8.73** |

### Not applied: suspected overlaps and risks (kg are the size of the doubt)

I did not change these because I could not prove the scope from the files.

| Suspicion | kg | Direction |
|---|---|---|
| `Oil_cooler` (0.6) may already sit inside the 21 kg drive unit (thermal-study.md puts the exchanger there) | -0.6 | down |
| `Rear_caliper_reserve` note says "caliper + bracket" and `Rear_caliper_bracket` (0.3) is separate | -0.3 | down |
| `Shock_reservoir_STUDY` (0.6) may be inside `Shock_body_STUDY` "with valves" | -0.6 | down |
| ABS allowance 1.6 says "lines, fluid" but brake hoses, banjos and splitters are modelled (about 0.9 kg) | -0.3 | down |
| Left `Hand_lever` (0.45) is noted with a master cylinder; an EV has no clutch | -0.3 | down |
| Fan shroud inside the 0.55 kg fan vs modelled `Radiator_pod_shroud` (0.8 kg) | -0.4 | down |
| "Body brackets and fixings" 2.0 and "Fasteners" 3.0: 5.1 kg together (1.6% of the bike) is normal, but no BOM count exists | up to -2.0 | down |
| Rear carrier 0.10 vs front 0.25: CAD volume ratio implies about 0.15 | +0.05 | up |
| Cell swap to purchasable Molicel P60B (`supplier-parts.md`) | +7 (pack) | up |
| Wheel masses 3.4 and 4.2 kg: no maker publishes them; a spoked or cast set is heavier | up | up |
| Passenger pegs 1.0, rack 0.9: kept in the ledger, so the ledger is a two-up layout | -1.9 if solo | down |

### Other housekeeping the audit found

- **The bike has at least four mass figures in circulation.** `drive-study.md` uses 275.1 kg, the refreshed roll-up there 282.9 kg, `dynamics-study.md` and `thermal-study.md` use 287 kg, and the ledger says 328.4 kg. Every document should read from one number.
- Two dead rules: `Side_radiator_*` (1.15 kg) and `EMRAX_228_MV_LC_supplier_STEP` (13.5 kg) match no CAD solid. Harmless today; they would silently double count if a solid with that name returned.
- `Belly_skid_plate_STUDY` is labelled "4 mm" in the status file and ledger, but the generator builds 6 mm (`build-adventure.py` line 870) and the mass of 3.74 kg is correct for 6 mm. Label only.
- `Seat_two_level_STUDY` note says "CAD 15.7 L"; the current CAD is 14.8 L. Effect about -0.04 kg.
- The ledger has no row for the MSD, pyro fuse, charge contactors or precharge parts. I checked: they are inside the two junction-box placeholders (2.2 kg and 1.4 kg versus 2.35 and 1.5 kg in the BOM), within 0.3 kg, so I added nothing.
- Estimate values with a CAD solid that weighs wildly different from the number (implied density over 8 g/cm3, for example pegs 20, levers 39, side stand 13) mean the CAD is only a stand-in. Those masses cannot be checked from the model. Listed in `mass-ledger-estimates.csv`.

## 2. The estimate lines

138 of 210 original lines are tagged "estimate" (118 CAD stand-ins plus 20 allowances), carrying 129.7 kg. Each is classified in `program/data/mass-ledger-estimates.csv` (item, what it is based on, whether a supplier figure is possible, how, CAD-implied density). Summary of the 140 lines in that file (138 estimates plus the pack-internals plug and the added EVCC; the three removed allowances show as n/a):

| Family | Lines | Reconciled kg | Based on | Supplier figure possible? |
|---|---|---|---|---|
| Drive unit (IPM and gears) | 1 | 21.00 | `drive-study.md` spec: 14 kg motor + 7 kg reduction | **Partly.** Motor yes (EMRAX 228 LC 13.5 kg, Helix SPX177-45 13 kg are published); reduction no (RFQ or own design) |
| Allowances (wiring, coolant, fasteners, etc.) | 19 | 40.6 | Hand figures | Mostly yes (13 lines) from the electrical BOM and thermal sizing; 4 lines no (brackets, fasteners, paint, nose set) until a BOM exists |
| Fork, clamps | 12 | 10.82 | Guess for a 48 mm USD fork | Partly: WP, Showa, Ohlins sometimes publish fork mass |
| Wheels | 2 | 7.60 | Assumed forged 19x3.0 and 17x4.5 | Partly: no maker publishes it (`supplier-parts.md`); ask for quotes |
| Small custom parts (pegs, rack, seat, stand, bearings) | 17 | 7.00 | Hand figures | Partly: weigh from CAD volume once drawn; bearings are catalogue |
| Brakes | 13 | 6.86 | Typical caliper and disc values | Yes: catalogue calipers publish mass; discs from CAD volume |
| Rear tyre | 1 | 6.40 | Rule of thumb | Yes: buy the exact Metzeler 170/60R17 and weigh it |
| Cooling hardware | 7 | 5.66 | `thermal-study.md` sizing | Yes for pump, heater, valve; supplier quote for cores and fans |
| Controls and brake plumbing | 29 | 5.16 | Typical catalogue values | Yes, but under 0.1 kg lines are not worth chasing |
| Rear shock | 6 | 4.40 | Guesses | Yes: shock makers publish assembly mass |
| HV junction boxes | 2 | 3.60 | Placeholder for box and contents | Partly: sum of catalogue parts, boxes from CAD |
| Lamps, mirrors, horn | 19 | 2.65 | Typical masses | Partly: indicators, mirrors, horn catalogue; headlamp is a custom OE module |
| Belt drive | 3 | 2.50 | Guess | Partly: Gates publishes belt mass; pulleys from CAD |
| Named HV parts (CM200, BROGEN, Orion, GX14) | 5 | 12.25 | Placeholders | **Already published**; applied above |
| Steering damper | 1 | 1.10 | Guess | Yes: data sheet |

Totals by answer: **yes 75 lines (73.6 kg), partly 58 lines (56.9 kg), no 4 lines (7.2 kg)**. The best use of effort is the drive unit (21 kg), the fork and wheels (18.4 kg together), and the allowance lines. The 41 kg of allowances is where a real bill of materials will move the total most.

## 3. Proposed ledger scheme for the rebuild

### One parts ledger, one row per part

File: `parts-ledger.csv` (one source of truth; CAD and the mass roll-up read it, nobody types a mass anywhere else).

| Column | Rule |
|---|---|
| `id` | Stable, never reused: `BV-<system code>-<4 digits>`, for example `BV-DRV-0003` |
| `name` | Plain name |
| `system` | One of: ENG (energy), DRV (drive), ELC (electronics), THM (cooling), CHS (chassis), RUN (running gear), BOD (body), PRO (protection), ALW (allowance) |
| `make_buy` | `make` or `buy` (buy rows carry a manufacturer and part number in `notes`) |
| `status` | `concept`, `proposed`, `design-intent`, `released` (see below) |
| `material` | For make parts, for example 25CrMo4, 6082-T6 |
| `process` | For make parts, for example TIG-welded tube, CNC, injection moulded |
| `qty` | Multiplier for left/right pairs, so a pair is one row |
| `mass_kg` | Per piece |
| `mass_source` | One of `measured`, `supplier`, `calculated`, `estimate` (the program's four labels) plus a reference: URL, file and line, or CAD volume |
| `cost_usd` | Unit cost at the stated volume |
| `cost_source` | Same four labels plus reference |
| `drawing_id` | Blank until a drawing exists |
| `cad_solid` | Exact FreeCAD object name, or blank if not modelled (allowances) |
| `scope_tag` | Short unique tag for what the part physically is (`side_stand`, `dcdc`, `nacs_inlet`). **Two rows may not share a tag.** This is the double-count guard |
| `includes` / `excludes` | Free text, forced for any row whose mass spans several things (assemblies, allowances) |

Status meanings:

- **concept**: a placeholder that holds a place in the budget. The CAD may be an envelope.
- **proposed**: a named part or a sized design with an analysed basis; not yet on a drawing.
- **design-intent**: drawn, with material, process and mass from CAD volume or a supplier drawing.
- **released**: drawing issued and mass measured or confirmed by the supplier.

Rules: an allowance row is allowed only with `status = concept` and must list what it excludes. Once a part is modelled, its allowance row must be deleted in the same change (the tag guard enforces it). `mass_source = measured` only for a part that has been on a scale.

### Per-system budget check

A second file `budgets.csv`: `system, budget_kg, set_by, date`, one row per system, summing to the bike target the program chooses. A growth allowance is added per status so early numbers carry a margin (proposed starting values, to be agreed): concept +15%, proposed +10%, design-intent +5%, released +1%.

The check computes, per system: raw mass, growth-adjusted mass, budget, headroom (kg and %). Flags:

- **OVER**: adjusted mass is above budget. Check exits non-zero.
- **TIGHT**: adjusted mass is within 5% of budget.
- **UNSOURCED**: any row without `mass_source`, or with `estimate` above a set share of the system's mass.
- **DUPLICATE**: two rows with the same `scope_tag` or the same `cad_solid`.
- **ORPHAN**: a CAD solid with no row, or a row naming a solid that no longer exists (today this only prints to stderr).
- A bike-level line: total vs target in kg and lb, and the share of mass at each status and source label.

### Patch plan for `tools/mass-rollup.py` (describe only; not edited)

1. **Read `parts-ledger.csv` instead of the inline `RULES` and `ALLOWANCES` lists.** Keep the four methods (`kg`, `vol`, `shell`, `pack`) as a `method` column; densities move to a small `materials.csv`.
2. **Bind by explicit `cad_solid`, not by first-match prefix** (`'Front_disc_*'` style). Left/right pairs get `qty`. This removes the order-dependent match (the "first match wins" comment) that already needed a workaround.
3. **Fail on orphans.** An unmatched CAD solid or a ledger row with a missing solid raises an error (exit non-zero) instead of printing to stderr.
4. **Delete the `PACK_REST` plug.** The pack becomes explicit rows (busbars, ribbons, foam, vent, and so on). Keep the optimiser pack mass as a cross-check printed beside the bottom-up total, not as an input.
5. **Add the double-count guards**: unique `scope_tag`; allowance rows must name what they exclude; warn when an allowance text mentions a name that matches a modelled `scope_tag`.
6. **Add a CAD sanity warning**: for `vol` and `shell` rows nothing (the CAD is the mass); for `kg` rows warn when the CAD-implied density is above 8.0 or below 0.2 g/cm3, so a stand-in solid is visible.
7. **Replace the `S/C/E` tags** with `measured / supplier / calculated / estimate`, as the program brief requires, and print mass by label and status.
8. **Add the budget step** described above, writing `mass-budget-report.csv` and returning a non-zero exit code on OVER.
9. **Take output paths as arguments** (currently it overwrites `mass-rollup.csv` and `.json` in place), and stop hard-coding the "prepared" date.
10. **Regression test**: with the reconciled ledger loaded, the total must equal 319.64 kg within 0.01 kg, and the old ledger must still give 328.37 kg. The scripts I used (`program/tools/reconcile-ledger.py`, `mass-rollup-recheck.py`) can seed this.
11. Keep the CoG, unsprung and pitch-inertia outputs; move the unsprung share (`F1.0`, `R0.5`) into its own column.

## 4. Other review claims checked

I opened `cad/Bavuso-V1.0-adventure.FCStd` without saving.

| Claim | Verdict | Evidence |
|---|---|---|
| Rear rotor is 267 x 5 in CAD but the fade calculation uses 267 x 6 | **Confirmed** | `Rear_disc_p1` bounding box Y 66.0 to 71.0 mm (5.0 mm), diameter 267. `dynamics-study.md` and `braking-results.json` call for 267 x 6 (443 C peak, 7 K under the 450 C limit); the 240 x 5 case gave 506 C. Cause: `tools/build-adventure.py` line 335 builds both discs 5 mm thick, with the comment on line 332 saying 267x6 |
| Lower cover is 1.99 mm from the pack against 5.00 mm | **Confirmed** | `geometry-adventure-audit.json` check `lower_body_vs_pack` gap 1.99, required 5; my direct distance between `Lower_body_battery_covers_STUDY` and `Pack_case_structural_4mm_STUDY` is 1.992 mm. The audit shows 61 pass and 1 fail (62 checks) |
| Belt is 14.19 mm from the modelled rear tire | **Confirmed** | Shortest distance `Drive_belt_14mm_STUDY` to `Rear_nominal_tire` is 14.189 mm |
| Belt is 15.00 mm from the belt-side swingarm | **Confirmed** | Shortest distance to `Swingarm_m1` is 15.000 mm |
| Older report flagged 12 mm overlap | **Confirmed** | `supplier-parts.md` line 15: 12 mm with a real 170/60 tyre (CR-3). The saved CAD fixed it for the modelled tyre only |
| Ledger sums to 328.37 kg | **Confirmed** | Rerun of the roll-up and CSV sum |
| Three allowances total 3.4 kg | **Confirmed** | 1.4 + 1.2 + 0.8 |

One caveat on the belt: the modelled tyre is about 183 mm wide (Y +/-91.4 mm). A real 170/60 tyre can reach 95 mm per side at its maximum in-service width (`supplier-parts.md`), so against that tyre the clearance is about 11 mm (belt face at Y -106), not 14.19 mm. That still passes the 10 mm requirement but with little margin.

### CAD change request (for the owner of `build-adventure.py`)

- **CR-A, rear disc thickness**: line 335 builds both discs with `side*5`. Make the rear disc `side*6` (front stays 5). Carrier and bobbin offsets on lines 342 to 348 may need a 1 mm shift. Expect the rear disc mass to go to about 1.17 kg. Rerun `mass-rollup.py`.

## What this does not prove

- **The reconciled 319.6 kg is a better ledger, not a measured bike.** Nothing has been weighed. 211 kg of it is still estimate.
- **Most corrections lean on `thermal-study.md` and `electrical-bom.csv`, which are themselves planning estimates.** The BROGEN 3.0 kg is a catalogue maximum I did not re-open at the supplier's site; the Cascadia, Shorai, Volex and GX14 figures come from the repo's own supplier notes, not fresh web checks.
- **I did not verify** the 5 mm vs 6 mm rotor mass beyond CAD volume x steel, whether the 21 kg drive unit includes the oil exchanger, or any of the watch-list items.
- **The cell mass (180 g) and the 0.80 pack ratio are untouched.** The purchasable fallback cell is heavier by about 7 kg at pack level and is not in these numbers.
- **The growth percentages and the budget flags are my proposal.** The system budgets themselves depend on the target weight the program has not yet chosen.
- **The 32 rows changed include five that are 0.1 kg or less.** I did not re-derive densities for the CAD-volume lines (frame, panels, swingarm); those were taken as they stand.

## Files

- `program/03-mass-ledger.md` (this file)
- `program/data/mass-ledger-reconciled.csv`
- `program/data/mass-ledger-estimates.csv`
- `program/data/run/` (recheck output, CAD volumes, working JSON)
- `program/tools/` (`mass-rollup-recheck.py`, `reconcile-ledger.py`, `estimate-basis.py`, `dump-volumes.py`)
