# Bavuso V1.0 adventure layout: build notes

Prepared November 3, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5). This puts the optimised powertrain from `powertrain-cost-down.md` into the CAD and fixes the ground-clearance problem the integrated model left open.

**Status: engineering development model. Not a fabrication or riding release.**

> **Update, Nov 5 — new drive:** the default model now carries a **radial IPM motor with a 2-stage reduction** instead of the EMRAX 228. The EMRAX can't reach the speed targets on this pack's voltage; see `drive-study.md`. The motor body sits 75° above the pivot, and the reduction's output and the belt stay on the pivot axis. The HV cabinet moved below the pivot, into the space the EMRAX used to fill. The pack keeps 594 cells, its top stays at 613.5 mm, and its cell centroid is now 410 mm. **51 of 51 checks pass, with no interferences.** The EMRAX version is kept as `cad/Bavuso-V1.0-adventure-emrax228.FCStd` (`BAVUSO_DRIVE=emrax228`).

> **Update, later on Nov 3:** the rear-shock study lowered the swingarm pivot and motor by 120 mm, to fix anti-squat. The pack now wraps over the motor: it is 24 mm taller (238–613.5 mm above ground) and its cell centroid is at 424 mm. Swingarm geometry, the shock and the new checks are in `rear-suspension.md`. The numbers below are from before that change, unless marked.

## The plain answer

The bike now has **216 mm of ground clearance with an 840 mm seat**. That sits inside the 200–220 mm adventure target, and the seat is a normal height for the class (an R1300GS is 850 mm). The new **32.7 kWh pack (594 large cylinder cells, 99s6p, 416 V)** and the **EMRAX 228** motor, taken from the supplier's own CAD, both fit. The model passes **33 of 33 clearance checks**, with no part-to-part overlaps.

Three things made it fit:

1. **A taller, narrower, stepped pack.** It uses 26120-class cells laid sideways in three lanes. The pack steps back around the motor and in from the front tyre, so it fills the space the old rectangular pack wasted.
2. **The pack carries frame loads.** Its 4 mm case replaces the two lower frame rails. Those rails were what forced the low belly before.
3. **40 mm more ride height and 19/17 wheels.** The ride height comes from 170 mm of suspension travel front and rear.

## How to run

```bash
"../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" -u tools/build-adventure.py > cad/adventure-build.log 2>&1
```

```bash
BAVUSO_MODEL=adventure "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/freecad.exe" tools/render-integrated.FCMacro
```

- **Runtime.** The full build takes about 15 minutes. With `BAVUSO_FAST=1` it takes about 2 minutes, saving the model with no checks or STEP export.
- **Photoreal renders.** The Blender tools (`export-render-mesh.py`, `render-cycles.py`) accept `BAVUSO_MODEL=adventure` too, and write `visuals/cycles-adventure-<view>.png`.
- **Old model.** `tools/build-integrated.py` and its outputs are unchanged, so the earlier model can still be compared.

**Outputs:**

- `cad/Bavuso-V1.0-adventure.FCStd` and `.step`
- `geometry-adventure-audit.json`
- `cell-placement-adventure.csv`
- `component-status-adventure.csv`
- `visuals/adventure-*.png`

## Layout numbers

| Item | Adventure model | Integrated model (Oct 26) |
|---|---|---|
| Static ground clearance (skid plate) | **216 mm** | 128–135 mm |
| Seat height / peg height | 840 / 420 mm | 800 / 380 mm |
| Wheels | 120/70ZR19 front, 160/60ZR17 rear | 17 / 17 |
| Travel, front / rear | 170 / 170 mm | 125 / 130 mm |
| Rake / trail | 25° / 111.9 mm | 25° / (17-inch front, shorter) |
| Wheelbase | 1486.8 mm | 1480 mm |
| Swingarm length / static angle | 545.6 mm / 8.2° (pivot 390 mm above ground, Nov 3 update) | flatter (lower ride height) |
| Pack | 594 × 26120, 99s6p, 32.7 kWh, 416 V full | 700 × 21700, 100s7p, 26.3 kWh |
| Pack mass (cells / 0.80) | about 134 kg | about 85 kg |
| Cell centroid height | 399 mm above ground | about 330 mm |
| Motor | EMRAX 228 MV LC (supplier STEP) | EMRAX 208 |
| Lower frame rails | none (pack is structural) | two, at Y ±190 |
| Body width at the battery | 414 mm | 444 mm |

## What changed, and why

| Area | Change | Reason |
|---|---|---|
| **Ride height** | Whole chassis raised 40 mm (`LIFT`); pack floor sits 238 mm above ground, skid plate 216 mm. | Gives the adventure clearance. The rear-tyre bump position is unchanged, because the extra 40 mm of travel equals the lift. |
| **Front wheel** | 19-inch, 120/70. Front travel set at 170 mm, not 180. | 19/17 is the adventure standard: it rolls over obstacles better. At 180 mm the bigger tyre came within 17.4 mm of the lower triple clamp at full bump. At 170 mm the gap is 27.4 mm. A new check guards it (≥ 25 mm). |
| **Pack shape** | 3 lanes of sideways cylinders (Y −128 / 0 / 128), filled 2 rows at a time. Each band of rows stops 21 mm from the motor and 22 mm (plus case and skin) from the front tyre's whole travel path. | Uses the space between the wheels as fully as it can. The result is 351 mm tall and 388 mm wide, against 430 mm tall in the 7-high stacking. |
| **Motor clearance** | Pack bands keep clear of the motor's real tessellated outline. | The EMRAX 228 STEP reaches 155.5 mm from its axle because of its connector and coolant fittings, not just the 118.8 mm housing. A check against a circle would have cut 15 mm³ into it. |
| **Frame** | Lower rails removed. A down-link from the headstock to the pack's front lug, and a rear link from the swingarm pivot to the pack's rear lug. | The pack case carries the loads, like a car's skateboard pack. Down-link lugs moved out to Y ±180 to keep 21 mm from the front tyre at bump. The tail rail end was raised to Z790 to keep 26.8 mm from the rear tyre. |
| **Lower covers** | 414 mm wide, near-vertical sides, a belly at 15 mm under the pack, and a front wall that follows the front tyre's travel path. | Narrower than before (444 mm), because no rails sit outside the pack. |
| **Rear bodywork (Nov 11)** | Re-traced from a close crop of the baseline image. **Side cover:** the under-seat cover drops in a wedge to Z512 at X600, over the motor-cover top, 440 mm wide. **Undertray:** a new 3 mm skin, 25 mm outside the rear tyre's whole travel, closes the tail from below. **Rear end:** a rack over the tail tip; a cast plate hanger runs down and back to the plate, with the plate lamp and indicators on stalks. **Detail:** a round cap over the pivot, and a lightening slot in each peg hanger. | **Side cover:** it hides the motor-area box and the shock's upper half, like the baseline. Its inner face sits 6 mm outside the rails, so the wall no longer needs slots cut for them. **Undertray:** the open tail showed the frame tubes and the inside of the far wall. **Rear end:** this matches the baseline's tail. The rear indicators move from 190 mm to 262 mm apart; FMVSS 108 asks for at least 229 mm. |
| **Front bodywork (Nov 11)** | **Shroud:** the fairing's lower edge now runs down beside the fork to Z532 at X1150, instead of stopping square above the battery cover. **Nose:** the beak is deeper, with a 40 mm lamp band and a thin DRL strip above it. **Vents:** slanted side vents with angled louvres and a backing plate. **Fender:** a slimmer front fender (10–16 mm off the tyre, 55–125° of arc). **Clearance:** the battery-cover front wall keeps 22 mm from the tyre low down, ramping to 30 mm by Z430. The fork-side lug of the lower downlink moved up from Z400 to Z470. | **Shroud and nose:** the front was the blockiest part against the baseline. **Fender:** a probe found the old fender came within 1 mm of the battery cover at full bump. The old check only tested the bare tyre, so it missed this. **Clearance:** nothing had checked the tyre while steered. At 20° of steer and full bump, the tyre came 14.7 mm from the battery cover and 9.2 mm from the downlink. Two new checks now sweep the tyre plus fender over 5 bump positions × steer ±35°. A combined lock-and-bump case is conservative, because the steering damper and stops make full lock at full bump rare. |
| **Realism, bars and seat (Nov 12)** | **Added:** front and rear brake hoses with banjos and a splitter, the master cylinder and reservoir, switch housings, lever perches, wiring to the bars, a 7-inch dash on the top clamp, mirror glass, rounded indicator pods, and a stitched seat welt. **Bars:** grips 50 mm higher and 20 mm further back (see `comfort-study.md`). **Seat:** lofted crowned sections; the pan drops 13 mm under the rider, with a moulded channel over the shock-top cross tube. **Sweep:** the steered-tyre sweep now uses the real 120/70 tyre section, not a cylinder. | **Dash bug:** the old dash, mounted on the fairing, overlapped the fork tubes by 109 mm³ straight ahead and about 117 cm³ at full lock. The overlap sweep never compares two running-gear parts, so it missed this. The dash now turns with the bars. **Seat channel:** the dropped pan would have sat 6 mm into the cross tube. The channel keeps 10 mm over the bracket plates, and about 66 mm of foam remains over it (78 mm elsewhere). **Hose:** the first route came within 0 mm of the screen at full lock; it was rerouted behind the clamp. **Real tyre section:** the old cylinder's square shoulder overstated the pinch. With the real section the front-body gap at lock is 22.1 mm. |
| **Seat as body (Nov 12, later)** | The seat is now as wide as the tail (3 mm proud), with upholstered sides about 60 mm deep that form the top of the side profile. A centre pan sits between the rails. The nose laps over the tank, which was eased at the rear to about 35°. The tank shell is cut where the nose sits. | The 330 mm seat sat in a 440 mm tail like a cushion in a tub, against a steep tank wall. The baseline's seat is the top of the body and runs up onto the tank. |
| **Cover construction bug** | The plan outline now uses 8 points, not 5. | With 5 points, the spline curve bowed the side wall 22 mm inward (to Y 184.7) over X 585–797, cutting 0.5 L into the pack. The bow didn't show in the renders, only in the overlap check. The boolean order was also fixed (cross-section first, then the plan shape), and a guard now stops the build if a "shell" comes out solid. |

## Check results

All values are in `geometry-adventure-audit.json`. "Bump" means the tyre at full compression, sampled at 21 points along its travel.

| Check | Gap (mm) | Required (mm) |
|---|---|---|
| Pack to EMRAX 228 supplier solid | 20.9 | 20 |
| Pack to front tyre (bump) | 36.7 | 20 |
| Pack to swingarm / pivot stubs | 96.9 / 114.9 | 20 |
| Motor to rear tyre (bump) | 122.8 | 20 |
| Skid plate to pack | 18.0 | 10 |
| Lower covers to pack | 6.86 | 5 |
| Lower covers to front tyre (bump) | 21.0 | 20 |
| Frame to front / rear tyre (bump) | 21.0 / 26.8 | 20 |
| Lower triple clamp to front tyre (bump) | 27.4 | 25 |
| Charger to pack / front tyre (bump) | 40.8 / 48.4 | 10 / 20 |
| Charger / inverter to steering sweep | 37.8 / 53.3 | 10 |
| HV cabinet to motor / pack / seat | 14.7 / 51.5 / 15.0 | 10 / 3 / 10 |
| Seat / tail to rear tyre (bump) | 47.8 / 44.7 | 20 |
| Undertray / rear indicators to rear tyre (bump) | 25.0 / 60.6 | 20 |
| Plate / plate arm to rear tyre (bump) | 37.1 / 48.8 | 20 |
| Swingarm cross brace to rear tyre | 72.9 | 20 |
| Motor cover to motor | 33.5 | 10 |
| Front body / frame to tyre + fender, steer ±35° × bump (Nov 12) | 22.1 / 33.8 | 20 |
| Controls at full lock to tank, fairing, screen (Nov 12) | 62.5 | 30 |
| Dash at full lock to fairing, screen (Nov 12) | 19.9 | 15 |
| Brake hose and harness at lock to body (Nov 12) | 13.6 | 8 |
| Lower covers to pack (Nov 12) | 5.67 | 5 |
| Seat to rear tyre (bump), Nov 12 | 37.8 | 20 |

**Nov 12 full build: 58 of 58 checks pass, no interferences, mass roll-up 287.2 kg.** Every cell sits inside the pack's inner wall. The interference sweep (every body and electronics part against every other) finds nothing.

## What it means for the bike

- **Anti-squat (corrected Nov 3).** This note first said "about 100%". That was wrong: with the pivot at 510 mm above ground it was about 175%, so the rear would jack up under power. The pivot and motor were lowered to 390 mm, which gives 124% at sag (107–133% across the travel). See `rear-suspension.md`.
- **Higher CoG, but not high.** The cell mass sits 70 mm higher than before. Adventure bikes run higher CoGs than sportbikes by design. The whole-bike CoG still needs a proper mass roll-up to confirm.
- **Pack mass and frame.** The pack now weighs about 134 kg and carries frame loads, so the case, lugs and fixings become primary structure. They need real FEA, not just clearance checks.

## Open issues

- **Rear shock.** Resolved: central direct-mount semi-active shock, 305 mm eye to eye, 75 mm stroke. See `rear-suspension.md`.
- **Cell supply.** 26120-class fast-charge cells are not yet sold openly to outside buyers. The fallback is 4680 or 46-series cells: the same band-fill code works with a new radius and length.
- **Busbars, cooling plates and BMS harness** are not modelled inside the pack. The 2 mm cell gaps and 1 mm insulation gap are placeholders.
- **Pack lugs and case structure.** The links end at the case wall. The lugs, inserts and the load path through the case still need design and FEA.
- **CFD.** The adventure shape is taller and narrower, so CdA needs re-running (baseline 0.44 m², target 0.38–0.40).
- **Inverter.** The CM200 is still in the model as a space envelope; the chosen SiC inverter is smaller.
- **Margins.** Three margins are close to their limits: triple clamp 27.4 mm, frame and covers to the front tyre 21 mm, and pack to motor 20.9 mm. Real fork and tyre drawings could move them.
- **Not modelled:** steering lock beyond the cylinder envelope, rear droop, tyre growth, wiring, hoses, a rider fit buck, and test validation.
