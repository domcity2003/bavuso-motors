# Bavuso V1 CAD architecture (rev C)

> **Superseded in part (Nov 22, 2026).** This document predates the final V1 numbers; the authority is `00-V1-final-spec.md`. Stale here: the 255.3 kg rev C roll-up and the "not yet at 240 kg" framing (final 257.9 kg, T1 <= 260 kg, CAD rev E in `16-cad-revE.md`); the 267 x 6 rear disc (final 267 x 5); the rev C layout and masses.


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Files: `tools/build-adventure.py` (rev C, evolved in place), `cad/Bavuso-V1.0-adventure.FCStd` and `.step`, `geometry-adventure-audit.json`, `program/data/cad-parts.csv` (every solid), `program/data/run/build-full.log` (full-build log with all checks), `program/data/run/final-pair-recheck.json`, `program/tools/verify-final-pairs.py`, `tools/export-cad-parts.py`. Renders: `visuals/cycles-adventure-*.png` and `visuals/cycles-adventure-rider-*.png`.
Labels: **measured** = taken from the CAD, **supplier** = published datasheet, **calculated**, **estimate**.

## The plain answer

**The adventure model now matches the Gate A hardware: a Molicel P60B 100s11p pack, an EMRAX 228 on the swingarm pivot, a single 3.60:1 belt, one HV box, one coolant loop and a solo-sized frame. All 64 geometry checks pass (100%).** The checks include the lower cover to pack gap (10.6 mm, was 1.99 mm) and belt to rear tyre (12.0 mm against a 190 mm wide envelope).

**It is not yet at 240 kg.** The current mass roll-up on this CAD gives **255.3 kg** (indicative, 177 estimate-based lines). The biggest overruns are body and protection (24.7 kg against 15), running gear (45.1 against 37) and cooling (8.95 against 6). The frame is close to its 18 kg budget (about 17 kg of tube and plate by my sum; the ledger counts 19.0 kg with pivots and brackets).

One decision needs the lead's eye: **the swingarm is now single-sided (right side only).** The 62 mm belt pushes a left arm to Y-209, into the frame pivot node, the pegs and the narrow-waist cover. An endless belt also cannot be fitted past a closed double-sided arm (drive CR-5). A single-sided arm solves both.

## What changed (priority order)

| # | Area | Before | Now |
|---|---|---|---|
| 1 | Pack | 594 x 26120 cells, 99s6p, three lanes, 388 mm wide | **1,100 x P60B 21700, 100s11p, four lanes (25 series groups of 11 each), 333 mm wide**, 4 mm structural case, 507 mm long (X590-1097), floor Z198 unchanged |
| 2 | Drive | radial IPM + 2-stage gearbox (ipm default) | **EMRAX 228 supplier STEP on the pivot (X540, Z350)**, 35T/126T 8 mm-pitch belt 62 mm wide (3.60:1), pulley bearing carrier, outboard carrier support at the left pivot node |
| 3 | Electronics | CM200 + 6.6 kW charger + 2 junction boxes + 1.2 kW DC-DC + cabinet | **Cascadia CM200DX (STEP), 3.3 kW charger envelope, ONE 4-contactor HV box, 0.8 kW DC-DC**; deleted both junction boxes and the oil cooler |
| 3 | Cooling | two 191x154x32 cores, two pumps, 5 kW PTC | **one shared loop**: two 165x128x28 radiator halves (0.042 m2, was 0.058 m2), one pump, one valve, 3 kW PTC |
| 4 | Running gear | 48 mm fork, 320 mm discs, rear disc 267x5 | **43 mm fork, 300x5 front discs, Stylema-class calipers on the 108 mm radial mount, rear rotor 267x6 (fixes the review mismatch)**, 110/80R19 + 150/70R17 drawn |
| 5 | Chassis | 34.9 kg ledger | solo tube table below; passenger grab rail gone, short rack mount kept |
| 6 | Body | 3 mm panels, 434 mm lower cover, thick plates | **2.5 mm panels and plates; lower cover 390 mm wide below the shoulder, flaring to the tank width above Z430-550**; skid 5 mm and 310 wide; crash guards 25x2; thinner plate arm |
| 7 | Checks | 62 checks, one at 1.99 mm | 64 checks, all pass; lower cover gap fixed by a pack limit that follows the cover's real front wall |

## Key dimensions

| Item | Value | Source |
|---|---|---|
| Wheelbase | 1,490.0 mm | measured (CAD) |
| Rake / trail | 25.0 deg / 114.7 mm | measured |
| Seat height, static | 832.1 mm (target about 830) | measured |
| Peg height / seat-to-peg | 323 mm / 509 mm (peg reference unchanged) | measured |
| Ground clearance, static | 229.1 mm (belly skid; unchanged) | measured |
| Swingarm length / static angle | 545.6 mm / 8.2 deg | measured |
| Rear wheel travel / shock eye distance | 170 mm / 263.1 mm at sag (stroke used 73.1 mm) | measured |
| Anti-squat | 122% static (105-132% over travel) | calculated by `rear-kinematics.py` |
| CoG height, rider on | 651 mm (rear-kinematics model, old masses); roll-up CoG at 537 mm height, 53.6/46.4 front/rear, bike only | calculated, indicative |
| Pack outer box | X590-1097 x Y+-166.7 x Z251-630 (saved, grounded coordinates) | measured |
| Pack cell centroid height | 436.6 mm in the saved frame (was 424 mm with the 3-lane pack; the 4-lane pack is a little taller) | measured |
| Pack mass | 103.1 kg by the cells/0.80 rule; ledger on CAD volumes 105.4 kg (case 9.4 kg, 4 mm) | calculated |
| Belt | 8MGT-1760-62, pitch radii 44.6 / 160.4 mm, centre distance 545.6 mm; plane Y-107 to -181 | supplier / calculated |
| Seat height, rider pocket | unchanged saddle shape | measured |

## Tube and plate table (solo load case; proposed, FEA must verify)

Mass is calculated from the CAD solid volume (steel 7.85, aluminium 2.70 g/cm3), per pair or each as shown. Previous sizes in brackets.

| Part | Proposed | Was | kg (pair) |
|---|---|---|---:|
| Upper rail 0 (pivot node to seat front) | 38 x 2.5 | 44 x 3.5 | 1.64 |
| Upper rail 1 (seat rail) | 32 x 2.5 | 38 x 4.5 | 1.78 |
| Upper rail 2 (to head tube) | 38 x 3 | 45 x 4 | 1.20 |
| Upper posts (2 each side) | 25 x 2 | 32 x 2.5 | 0.72 |
| Down-link | 32 x 2.5 | 40 x 3.5 | 1.54 |
| Rear pack link | 32 x 2.5 | 44 x 3.5 | 0.46 |
| Tail rail | 30 x 2 | 38 x 3.5 | 1.78 |
| Tail brace | 25 x 1.5 | 28 x 2 | 0.96 |
| Shock bridge diagonals | 22 x 1.5 | 25 x 2.5 | about 0.4 |
| Head tube | 56 OD x 50 ID (bearing bore kept) | 62 x 50 | 0.90 |
| Head gussets | 6 mm 4130 plate | 10 mm | 0.52 |
| Shock bridge (box) | 80 x 45 x 4 | 80 x 45 x 5 | 1.79 |
| Swingarm | **single-sided right arm**, box 130 x 46 at the pivot to 80 x 40 at the axle, 4.25 mm shell | two arms 120 x 34 | 2.08 (one arm) |
| Swingarm cross brace | 54 x 4 A356, Y-36 to +108 | 60 x 6, Y-118 to +110 | 0.24 |
| Shock tower | two 10 mm A356 webs | 14 mm | 0.35 |
| Pivot stubs | 40 OD / 30 ID | same | 0.20 |
| **Total (frame, arm, bridge)** | | | **about 17 kg** (ledger line sum 19.0 kg with pivot bearings and brackets) |

None of these sizes has been through the FEA again. The `detailed-design/structural-fea.md` loads were for a 328 kg bike and a two-up case; the arm in particular is now a cantilever.

## Geometry checks (full build, all pass)

64 of 64 pass. The tightest ones:

| Check | Gap (mm) | Required (mm) |
|---|---:|---:|
| Belt and rear pulley vs 190 mm wide rear tyre envelope | 12.0 | 12 |
| Frame vs front bump / rear bump | 22.0 / 22.2 | 20 |
| Pack vs motor (supplier STEP) | 21.0 | 20 |
| Shock tower vs rear tyre | 21.0 | 20 |
| Charger vs pack | 12.0 | 10 |
| HV box vs pack | 5.0 | 3 |
| Inverter vs charger | 8.0 | 5 |
| Lower cover vs pack | 10.6 | 5 |
| Belt vs pegs (new check) | 18.0 | 5 |

## Overlap list (broad sweep) and what is accepted

The sweep flagged these pairs; they are listed largest first. **Accepted** means it is a mounting contact modelled as a solid, not a clash.

| Pair | Overlap mm3 | Verdict |
|---|---:|---|
| Radiator core / pod shroud (each side) | 18,791 | Accepted: the core sits in the pod mouth; it existed before (25,475) and is smaller now |
| Radiator fan / pod shroud | 14,093 | Accepted, same reason (was 21,112) |
| Licence plate / rear reflector | 5,280 | Accepted: the reflector is on the plate (existed before) |
| Brake hose / handguard (left) | 1,080 | Accepted: routing detail, existed before; hose clip not designed |
| Grip / handguard (each side) | 486 | Accepted: handguard is clamped to the bar |
| Radiator pod grille / shroud | 276 | Accepted: grille is a part of the pod mouth |
| Rear post foot / pack case (each side) | 75 and 19 | Accepted: post feet sit on machined roof pads; the post end face is angled |

The earlier radiator/body overlaps with the tank (90 mm3) and lower cover (10 mm3) are gone. Overlaps found in the first full build (HV box against the rear post and tank wall, pivot cap against the frame tubes, rear link against the battery plate, waist ledge against the cover) were fixed by resizing and re-checked on the final model (all 0 mm3). **The final model was rebuilt without the slow checks after those edits**, and only the edited pairs were re-checked (`final-pair-recheck.json`). A fresh full run before release is advisable.

## Indicative mass from the current roll-up (mass-rollup.py --soft, 187 solids)

| System | Budget kg | Roll-up kg |
|---|---:|---:|
| Pack | 103.0 | 105.4 |
| Chassis | 18.0 | 19.0 |
| Running gear | 37.0 | 45.1 |
| Drive | 23.0 | 23.6 |
| Electronics | 18.0 | 17.4 |
| Body and protection | 15.0 | 24.7 |
| Cooling | 6.0 | 9.0 |
| Wiring, fasteners, fluids | 11.0 | 11.1 |
| **Total** | 240.0 | **255.3** (562.9 lb) |

Unmatched solid: `Coolant_PTC_heater_3kW` (115 cm3 box). The new `Motor_pulley_bearing_carrier` matched the pulley slot as a second solid. Slots with no solid: EVCC, ABS module. The roll-up reads cell mass from CAD volume with the old 26120 volume, so the ledger agent's slot rules matter more than this run's cell figure.

## What the lead should know about mass

- **Pack case is 9.4 kg at 4 mm**; the ledger wants about 7 kg. A 3 mm wall brings it to about 7.1 kg (CAD volume scales with wall). The wall is a structural question (the pack is the lower frame), so I did not change it.
- **Body and protection at 24.7 kg is the main gap.** Largest items: seat 2.6, skid 2.6 (5 mm), lower covers 2.0, crash guards 3.5 pair, upper body 1.5, headlamp 1.2, tail panels 1.2, hugger 1.0, rack 0.9. Fixed allowances (brackets, paint, fasteners) are in the same ledger system. Options not taken: guards removed or moved to the pivot only, 3 mm skid, a solo seat without the pillion step.
- Running gear is 97% estimates; the wheels, tyres and fork lines are placeholder masses.

## CAD change requests I did not do, or need a decision on

1. **Single-sided swingarm (done, needs the lead's approval).** Alternative: keep two arms and move the belt-side arm and frame pivot node out about 40 mm, which widens the motor cover to about 225 mm and the pegs by about 30 mm. I judged that worse.
2. **Rear tyre envelope.** My brief set a 190 wide envelope; the drive file assumed a 150/70 tyre with about 77 mm half-width (belt inner flange at Y-89). I used the stricter 190 envelope (flange at Y-107). If the 150 tyre is final, the belt can move 18 mm inboard.
3. **Cover width.** The lower cover steps from 390 mm (below Z430) to 434 mm (shoulder) so the tank, waist ledge and pods keep their old geometry. The motor cover, with the arm now on the right only, could also narrow. Not done.
4. **Inverter and HV box.** The HV box is 260 x 160 x 84 (program/07-electrical.md asks about 280 x 160 x 110); the rear post and the tank wall set that limit. HV cables are at 70 mm2 in the ledger, not modelled.
5. **Belt fitting.** The outboard carrier at the left pivot node must be detachable for the belt to slide on; only a short plug (Y186-192) is modelled.
6. **Pack vent path to the belly (07-electrical.md)** is not modelled. The belly skid sits 16 mm under the case.

## What this does not prove

- **The model is geometry only.** Tube sizes, the single-sided arm, the 2.5 mm panels and the 5 mm skid have no FEA or crash analysis behind them.
- Cell, charger, DC-DC, pump, valve, PTC and fork/shock/wheel masses are estimates; the charger, DC-DC and cooling parts are class envelopes, not selected parts.
- The final model had its slow checks run on the build just before the last edits, not on itself (see above).
- The pack was sized with a flat hex-packed row model, not a cell-by-cell thermal or busbar layout. Case wall thickness and vent path are not designed.
- The mass-rollup total is indicative: some rules still reflect the old design (cell-volume formula, 6.5 kg charger text).
- I could not read the review PDF page 4 (no PDF renderer on this machine), so the appearance-drift list was taken from the brief: beak, slim light band, clear screen, narrow waist, sculpted saddle, matte black, upright posture were all kept.
- The renders show the new shape but I did not do a side-by-side visual diff against the frozen concept.
