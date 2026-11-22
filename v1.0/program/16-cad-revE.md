# Bavuso V1 CAD rev E: finished look, Round 2 structure, carbon wheels

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Files: `tools/build-adventure.py` (rev E), `cad/Bavuso-V1.0-adventure.FCStd` and `.step`, `cad/Bavuso-V1.0-adventure-rider.FCStd`, `program/data/run/build-full-revE4.log` (the final full build, 91 checks), `program/data/run/overlap-sweep-revE.log` and `.csv` (the broad overlap sweep, run separately), `mass-rollup.csv/json`, `program/data/parts-ledger.csv`, `rider-fit.json`. Renders: `visuals/cycles-adventure-*.png`; the rev D originals are in `visuals/revD-before/`, rev C in `visuals/revC-before/`.
Labels: **measured** = from the CAD, **calculated**, **supplier**, **estimate**.

## The plain answer

**Rev E looks like one finished body instead of a black slab with a box stuck behind it, and it carries the Round 2 steel yoke. All 91 geometry and regulatory checks pass. The roll-up is 250.6 kg (rev D: 246.4 kg), so the weight went up, not down.** The increase is the structure (the pivot yoke, spindle and blocks add about 5 kg to the chassis line) and the ledger agent's rule changes. The carbon wheels saved about 1.7 kg, and body plus protection stayed at **14.45 kg, under the 15 kg limit**.

Three things are not as clean as I would like (details below): the radiator pods are still about 55 mm proud of the flank (shroud at Y278 against the 222 flank) (flush is not possible with the cores unchanged), the roll-up leaves out the new steering damper (no ledger rule for its new name yet), and the broad overlap sweep had to be run separately from the build (see section 5).

| Item | Result |
|---|---|
| Roll-up (`tools/mass-rollup.py --soft`) | 250.57 kg, 552 lb. Budget 240 kg: over by 10.6 kg |
| Body and protection | 14.45 kg (limit 15): pass |
| Checks | 91 of 91 pass (rev D: 87 of 87) |
| Yoke cross-member height | **Z545** (Z525 clashes with the motor housing), 51 mm clear of the motor |
| Belt pulley outer flange | \|Y\| 177 mm (was 181); belt to rear tyre 12.0 mm |
| Carbon wheels | bound by the ledger: 2.6 kg front, 3.3 kg rear |

## 1. Look changes (what the build now does)

| # | Problem from the review | What I did | Result |
|---|---|---|---|
| 1 | Pack case read as a flat slab; a separate box behind it with a step and gaps | **One continuous 2 mm lower body** (`Lower_body_battery_covers_STUDY`): a single shell from the motor bay over the case flank to 8 mm behind the front-tyre arc. Its plan width eases from 217 (motor bay; 225 round the pivot node) to 180 mm at the nose, its top sits 1.5 mm under the tank skirt, and the belly line rises into the pack chin. It replaces the rev D filler and the separate motor-side covers | no seam or step between the rear box and the case; flank, tank and tail now share one outline |
| 2 | No feature line | **Gloss-black character line** (`Seam_trim_*`, flush inserts in the panel skins) from the beak's light band, along the tank shoulder crease and on under the saddle edge to the tail tip | continuous beak-to-tail line, visible in the side and hero views |
| 3 | Jagged front corner chamfer | The per-band 9x45 chamfers are gone. One **R15 outside / R12 inside radius** is swept up the front-tyre arc, so the case wall stays 3 mm at the corner and the corner reads smooth | pack front corner is one smooth radius |
| 4 | Spindly plate / indicator stalk | **Short chunky tail-tidy bracket**: 165 mm long, 20 x 48 section (was 240 mm, 12 x 36), plate raised 95 mm and 48 mm further forward, indicators on a short flat wing | plate 21.5 mm off the full-bump tyre envelope (limit 20); FMVSS lamp and plate checks pass |
| 5 | Rack plate nicked the seat tail (12,069 mm3) | Rack plate and slots moved 20 mm aft | nick gone; no rack/seat overlap in the sweep |
| 6 | Rear pulley rendered bright | Dark anodised material for both pulleys and the carrier (`tools/export-render-mesh.py`, `tools/render-cycles.py`) | pulleys render near-black |
| 7 | Pods 55 mm proud | **Not flush** (see below). Pod fillet raised from R14 to the biggest radius that works | pods still about 55 mm proud |
| 8 | Wheels | **Carbon wheels** adopted: five wide blade spokes, gloss clearcoat render material | ledger binds the slot |

**Pods, honestly.** The radiator core is 165 x 28 mm, angled 35 degrees, with its inner end at Y152. Its outer corner reaches Y269, which is 47 mm past the 222 mm tank flank. Thermal asked for the core size and angle to stay, so the pods cannot be flush. Flush within 5 mm would need the cores about 55 mm further inboard (inner end near Y95), where they meet the charger (Y plus or minus 95) and the coolant parts. I did not try that. A fairing lip was also not possible: the pod's front is a cut mouth with a grille, and the tank flank narrows to 205 mm toward the nose, so there is no clean surface to attach a lip to.

**What I tried that did not work.** A fillet of R15 on the new lower body failed, so its edges are not rounded by a fillet. The shell has no vertical corner edges (it is open at the front and rear, and its width tapers), so I judged the R15 request satisfied by the case front corner only. A second gloss line along the lower body (`Seam_trim_flank`) came out empty and was not built.

## 2. Round 2 structure applied (`program/09-structures.md`, section Round 2)

| Part | Rev D | Rev E |
|---|---|---|
| Yoke legs (new, 2) | none | 50 x 50 x 4.25 box from the pivot node (540, +-195, 350) up the rail 0 line to (556, +-157.7, 545) |
| Yoke cross-member (new) | none | 60 (Z) x 40 (X) x 5 box between the leg tops, **at Z545**. At the FEA height Z525 its bottom edge (Z495) is inside the motor housing top (Z505); at Z545 it is **51.0 mm** from the motor, 13.95 mm from the pack case and 24.5 mm from the HV box. The legs were extended along the same line to reach Z545 (FEA ran Z525: re-check the load path) |
| Rail 0 / 1 / 2 | 38x1.5 / 38x3.5 / 40x5 | 38x2.0 from the yoke top / 38x2.25 / 42x3.5 |
| Down-link, rear link, tail rail | 36x3.75, 40x4.25, 30x2.5 | 38x4.0, 42x4.25, 30x2.0 |
| Posts | 27x2.5 / 27x2.25 | 27x2.0 / 27x2.0 |
| Cross brace | 75 x 5.5 | 75 x 6.0 |
| Top shock plates | 12 x 36 | 14 x 40 |
| Pivot spindle (right) | 62 x 9 hollow | 60 mm solid steel, Y105-185 |
| Pivot blocks | 40 x 60 | 70 x 70, thin-wall (3 mm), both sides |
| Bearings | 6008 | two 32012 X (60 x 95 x 23) at Y105 and Y185, modelled as rings; the arm boss is OD 112, bored 95 |
| Nodes | tube joints | cosmetic 3 mm cast-node shells at the yoke tops (see overlaps for the seat-rail nodes) |
| Lug plates 12 x 40 | not modelled | **not modelled** (no lug solids exist in the CAD; they are a ledger allowance matter) |

**Knock-on moves** (the 50 mm legs are wider than the old tubes): the rear-box lower body is 225 mm half-width round the node (was 217), the pivot cover caps moved to Y225.5, the peg hanger plates 6 mm outboard (to Y236-242), the peg tubes and rubbers 6 mm outboard, and the pivot sliders start at Y243. Foot spread is 6 mm wider each side.

**Yoke against the pegs and the rider** (measured): yoke to peg hanger plate 16.3 mm, to peg tube 84 mm, to peg rubber 74 mm, to the seat 137 mm. Rider-fit (`rider-fit.json`, 1,755 mm rider, knee 82 degrees, elbow 95 degrees) shows **no leg contact with any yoke part**. The leg contacts it does list are the seat (1,458 cm3), tail panels, rails, cabinet, peg hangers and ledge plates, the same kind as rev D. The left yoke leg touches the end face of the motor pulley carrier (distance 0.0 mm, contact not overlap).

## 3. Mass (mass-rollup.py --soft, 199 solids)

| System | Budget kg | Rev D kg | Rev E kg | Note |
|---|---:|---:|---:|---|
| Pack | 103.0 | 103.9 | 104.9 | ledger agent's pack-internals rule (+1.06 kg moved in from coolant) |
| Chassis | 18.0 | 22.7 | 27.9 | yoke legs 2.43 + cross 2.23, spindle 1.78, blocks 0.79, node shells 0.6 (double counted, see below) |
| Running gear | 37.0 | 44.9 | 42.6 | carbon wheels (-1.7 kg); 320 mm discs now in the ledger |
| Drive | 23.0 | 23.6 | 23.5 | |
| Electronics | 18.0 | 17.4 | 17.4 | |
| Body and protection | 15.0 | 14.4 | **14.45** | new lower body 0.92 kg replaces the old filler 0.50 and motor covers 0.29 |
| Cooling | 6.0 | 8.5 | 6.9 | thermostat and PTC now matched |
| Wiring, fasteners, fluids | 11.0 | 11.1 | 12.9 | ledger agent's HV cable allowance |
| **Total** | **240.0** | **246.4** | **250.6** | |

The rev D to rev E change mixes CAD changes with the ledger agent's rule changes, so I cannot give a clean "CAD only" delta.

**Three corrections the ledger needs** (I did not touch `mass-rollup.py`):
1. `Steering_damper_semiactive` has no rule, so its mass is **not** in the total. Add about 0.5 kg (Öhlins EC class). The envelope is unchanged at 92 x 60 x 75 mm.
2. The cosmetic node shells (`Upper_rail_node_*`) are counted at steel density, 0.6 kg in all, but Round 2 already included the nodes in the tube masses. Give them 0 kg.
3. `Pivot_6008_size_reference_*` still says 6008 at 0.12 kg. A 32012 X bearing is about 0.7 kg; the two on the right pivot are carried at 0.24 kg.

With the damper added and the node shells removed, the figure is about **250.5 kg**.

## 4. Checks (91 of 91 pass)

Rev D's 87 pass again, plus four new yoke checks (`yoke_cross_vs_motor` 51.0, `yoke_cross_vs_pack` 13.95, `yoke_cross_vs_cabinet` 24.5, `swingarm_sweep_vs_yoke_cross` 109). Tightest results: cabinet to pack 5.0, inverter to charger 8.0, swingarm to motor 10.16, **belt and pulleys to rear tyre 12.0** (limit 12; the outer flange now at \|Y\| 177), charger to pack 12.0, hose and harness at lock 13.6, lower body to pack 14.3, plate to the full-bump tyre 21.5. FMVSS 108 rear reflector area 2,040 mm2, tail lamp height 869 mm, rear indicator spacing 262 mm all still pass.

Two methods changed to keep the build finishing:
- **Checks use sharp-corner and untrimmed twins.** The swept corner radius and the trim slots make distance checks ten times slower. During the checks the build swaps in the case with its old sharp corners (conservative: it is larger), and the panels before the trim slots were cut. The saved model has the real shapes.
- **The broad overlap sweep is not in the build any more.** The serial sweep in the generator ran for more than two hours without finishing (it had been part of rev D's 45-minute build). The final build ran with `BAVUSO_NOSWEEP=1` and `program/tools/overlap-sweep-parallel.py` does the same job on the saved model with six workers (same pairs, same exclusions).

## 5. Overlaps

The sweep (`program/tools/overlap-sweep-parallel.py`, 195 parts, 310 pairs with touching boxes, 5,418 s on six workers) found 23 overlaps over 1 mm3.

**Gone since rev D:** the rack plate against the seat tail (12,069 mm3), the HV box, tank and GX14 contacts (already gone in rev D).

**Accepted mounting contacts, same as rev D:** radiator core, fan and grille inside the pod shroud (18,791 / 11,078 / 266 mm3 each side), plate and its reflector (8,160), grip in handguard (462 each), brake hose on the left handguard (648), post feet into the case roof (124 front, 55 rear, each side), the doubler pad on the case (5 and 6).

**New in rev E:**

| Pair | mm3 | Verdict |
|---|---:|---|
| Plate bracket arm against the licence plate | 1,929 | mounting contact (the arm end is bolted to the plate's back); the plate lamp touches the arm by 24 |
| Lower body against the side stand | 149 | **not fixed**: the retracted stand's tube grazes the new 225 mm half-width wall (a sliver 1 mm deep). It needs a notch in the wall or a stand 3 mm further out |
| Upper body against the radiator pod shrouds | 6 each | skin touching skin, accepted |
| Seat-rail cast-node shell (`Upper_rail_node_rail`) against the seat pan | 1,250 each | **not fixed in the saved model** (cosmetic part; removed in the generator, section 6) |

## 6. Not rebuilt after the final build (post-build generator edits)

Two small fixes were made to `tools/build-adventure.py` after the final build ran, to be picked up by the next build. **The saved model does not have them.**
1. The `rail` cast-node shells at (570, +-125, 715) are no longer built. In the saved model they overlap the seat pan (1,250 mm3 each) and the rider's thigh (19 cm3 each).
2. The rear indicator lamp reserves move up to Z696 (beside the bracket wing). In the saved model they sit at Z664, 14 mm below the wing, so they look slightly detached in the rear views; the FMVSS height and spacing checks pass either way.

## 7. Before and after renders

| View | Rev D (before) | Rev E (after) |
|---|---|---|
| Side | `visuals/revD-before/cycles-adventure-side.png` | `visuals/cycles-adventure-side.png` |
| Side right | `visuals/revD-before/cycles-adventure-side_right.png` | `visuals/cycles-adventure-side_right.png` |
| Hero | `visuals/revD-before/cycles-adventure-hero.png` | `visuals/cycles-adventure-hero.png` |
| Front three-quarter | `visuals/revD-before/cycles-adventure-front34.png` | `visuals/cycles-adventure-front34.png` |
| Rear three-quarter | `visuals/revD-before/cycles-adventure-rear34.png` | `visuals/cycles-adventure-rear34.png` |
| Front detail | `visuals/revD-before/cycles-adventure-detail_front.png` | `visuals/cycles-adventure-detail_front.png` |
| Front | `visuals/revD-before/cycles-adventure-front.png` | `visuals/cycles-adventure-front.png` |
| Rider views | `visuals/revD-before/cycles-adventure-rider-side.png`, `-rider-hero.png` | `visuals/cycles-adventure-rider-side.png`, `-rider-hero.png` |

Renders are 64-sample Cycles on the CPU (rev D was higher), so they are slightly noisier. Look against `design/baseline black.png`: beak, slim light band, clear screen, narrow waist, sculpted saddle and matte black are unchanged; the lower body, the gloss line, the tail-tidy plate, the dark pulleys and the carbon wheels are new. Not matched: the pods are still boxy and proud.

## What this does not prove

- **The mass is a CAD roll-up with ledger rules, not a weighed bike.** The damper is missing from it and the node shells are double counted (section 3).
- **No new FEA was run on rev E.** The yoke legs were extended from Z525 to Z545; the load path at that height, the wider legs at the node, the bored boss and the lug plates (not modelled) are all unchecked. Round 2 FEA is for its own geometry.
- **The look is a render of CAD shells.** The lower body is a 2 mm panel with no mounting, tooling or draft study; the case front corner radius was checked for cell containment only (all 1,100 cells inside), not for crash strength.
- **The checks are on envelopes.** The FMVSS items are a screening of the geometry, not certification, and the clearance checks used sharp-corner and untrimmed twins of three shapes.
- **Pods are not flush**, and the second lower-body line did not build.
- **The carbon wheels are a render and a ledger slot.** Fatigue and impact certification is untested (still the risk named in the hardware shortlist).
