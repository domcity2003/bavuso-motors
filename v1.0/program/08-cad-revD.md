# Bavuso V1 CAD rev D: mass and look

> **Superseded in part (Nov 22, 2026).** This is the rev D record; the current CAD is rev E (`16-cad-revE.md`) and the authority is `00-V1-final-spec.md`. Stale here: 246.4 kg (about 248 kg) and the 240 kg goal (final 257.9 kg, T1 <= 260 kg); the ledger slot saying 300 mm front discs (final 320 x 5 front, 267 x 5 rear); 87 checks (rev E has 91); aluminium wheels and the pre-yoke chassis (final carbon wheels, steel pivot yoke at Z545).


November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Files: `tools/build-adventure.py` (rev D), `cad/Bavuso-V1.0-adventure.FCStd` and `.step`, `program/data/cad-parts.csv`, `program/data/run/build-full-revD.log` (full build, all checks and the broad overlap sweep), `mass-rollup.csv/json`, `program/data/parts-ledger.csv`. Renders: `visuals/cycles-adventure-*.png` and `-rider-*.png`; the rev C originals are in `visuals/revC-before/`.
Labels: **measured** = from the CAD, **calculated**, **supplier**, **estimate**.

## The plain answer

**Rev D is 246.4 kg on the roll-up, against 255.3 kg for rev C. It does not reach 240 kg.** Two parts that the roll-up cannot count yet (3 kW PTC heater, wax thermostat: about 1.3 kg) and the 320 mm front discs (+0.5 kg, the ledger slot still says 300 mm) bring the honest figure to **about 248 kg**. **All 87 checks pass** (64 geometry checks from rev C, new checks for the pods, sliders and the FMVSS 108/111/123 screen).

The look changed a lot: the broad flat battery cover, the two proud plates and the exposed guard tubes are gone. The finished pack case is now the visible lower body.

**The lead's blocker, belt-side swingarm, is not done: it does not package.** Numbers are in section 5. I kept the arm on the right and the belt on the left, as in rev C. This needs the lead's decision.

## 1. Mass against budget (mass-rollup.py --soft, 188 solids)

| System | Budget kg | Rev C kg | Rev D kg | Note |
|---|---:|---:|---:|---|
| Pack | 103.0 | 105.4 | 103.9 | case 7.91 kg (was 9.41): 3 mm walls, 5 mm front, floor ribs, 4 mm lug pads, 4 vents |
| Chassis | 18.0 | 19.0 | 22.7 | FEA tube table applied (+3.7 kg); FEA books it at about 25 kg |
| Running gear | 37.0 | 45.1 | 44.9 | bar centre merged into the left half (-0.25); 320 mm discs not yet in the ledger |
| Drive | 23.0 | 23.6 | 23.6 | unchanged |
| Electronics | 18.0 | 17.4 | 17.4 | unchanged |
| Body and protection | 15.0 | 24.7 | 14.4 | under budget |
| Cooling | 6.0 | 9.0 | 8.5 | valve gone; thermostat and PTC unmatched (see below) |
| Wiring, fasteners, fluids | 11.0 | 11.1 | 11.1 | unchanged |
| **Total** | **240.0** | **255.3** | **246.4** | **about 248 with the unmatched parts and 320 mm discs** |

Rev D CoG: height 536 mm, 53.5 / 46.5 % front / rear (bike only, indicative).

### Where body and protection went (24.7 to 14.4 kg)

| Item | Rev C kg | Rev D kg |
|---|---:|---:|
| Lower cover + proud battery and belly plates | 4.2 | 0.5 (small motor-bay filler cover only) |
| Crash guard tubes and mounts | 4.1 | 0.9 (6 sliders: 2 per side on the frame lugs, plus the pivot pucks 0.1) |
| Skid plate | 2.6 | 1.15 (3 mm, 250 wide, was 5 mm, 310 wide) |
| Rear hugger / front fender / screen | 0.96 / 0.46 / 0.75 | 0.30 / 0.25 / 0.50 |
| Handguards | 1.2 (solid bars) | 0.6 (hollow 22x3) |
| Tank skirt (new, to the case roof) | | +0.15 |

### What I judged and did not take

- **Case as the visible lower body: taken.** Saves about 3 kg of cover and plates for about 0.7 kg of extra case. The case front now follows the tyre arc (24 mm off the tyre, 32 above Z335), with the empty wedge behind it as busbar and crush space.
- **Guard tubes replaced by sliders: taken.** Sliders are the outermost points (Y 292) beyond the radiator pods (278). Cost: a slider on a 70 mm stud is a cantilever; FEA's 21 kN slider case passes with 1.02 to 1.06 safety factors, so it has no spare.
- **Lighter wheels: not taken.** The shortlist already carries the forged 3.4 / 4.2 kg pair; no lighter listed part exists. The carbon alternative saves 1.7 kg for about 2,700 dollars and has a certification risk. It is the lead's call.
- **Handguards deleted (another 0.6 kg): not taken**, compliance asked for them.

## 2. Changes (what the build now does)

| # | Area | Change |
|---|---|---|
| 1 | Pack case | 3 mm wall, **5 mm front wall** (cavity front 2 mm back), three 3 mm floor ribs in the lane gaps, four 4 mm doubler pads at the lug stations, **four 28 mm burst-vent ports (615 mm2 each) in the floor**, one per lane, ducted to the belly gap above the skid. Cells sit 2 mm further back. Object name unchanged for downstream tools |
| 2 | Lower body | Gone, except a 0.5 kg filler between the motor cover and the case rear. Tank skirt hangs to 25 mm below the case roof |
| 3 | Protection | Crash tubes removed. Link-lug sliders, pivot pucks. Slim 3 mm skid |
| 4 | Frame (FEA table, 09-structures.md) | Rail 0 38x1.5, rail 1 38x3.5, rail 2 40x5, posts 27x2.5 and 27x2.25 with feet at Y148, down-link 36x3.75, rear link 40x4.25, tail rail 30x2.5, head tube bore 49, gusset 4 mm, bridge box wall 2 mm, shock tower webs 14 x 66 |
| 5 | Tail brace bug | End point now (160, +-111.4, 779.7) |
| 6 | Swingarm and pivot | Cast A356 box 117x54 to 102.5x57, centre Y138.5, inner face Y110 at the axle, pivot boss Y105-185; pivot stub 62 OD x 9 wall, Y105-185; cross brace 75x5.5 (FEA 76; 0.5 mm less to keep 10 mm to the motor) |
| 7 | Lugs | Brought onto the case: Y144.7 (was 178). Front lug raised from Z470 to Z532: at Z470 the thicker down-link was 12 mm from the steered tyre (limit 20) |
| 8 | Radiator pods | Cores 20 mm inboard (Y152, was 172) and pods 22 % shallower, so the sliders are outermost. **Core sizes and fans unchanged**, as thermal asked. Valve replaced by a 38x32x40 wax thermostat |
| 9 | Brakes | Front discs dual **320x5** (+0.5 kg, exactly the limit), rear rotor **267x5** (CAD and the brake calc agree) |
| 10 | Tail | 35 mm shorter, slimmer plate hanger (12 x 36 section), smaller rack plate, enlarged rear reflector (2,040 mm2) |
| 11 | Look | Cast-style swingarm edges, bolt heads on the case flank, hollow handguards, thinner fender and hugger |

## 3. Checks (87 of 87 pass)

Rev C's 64 pass again. The five that failed in the first rev D builds and how they were fixed: down-link vs steered tyre 12.0 mm (lug raised to Z532, now 23.4), swingarm vs motor 9.7 (cross brace radius, now 10.2), swingarm vs motor cover 7.5 (cover 195 to 198, now 10.5), filler cover vs case (notch, now 5.2), slider vs filler (a by-design pass-through, check now covers pods and horn only, 15.8).

New checks: `pods_inside_slider_tip_line`, `crash_sliders_vs_tyre_fender_lock_sweep` (49.8 mm), `crash_sliders_vs_pods_and_horn`, and the regulatory screen below. Tightest results now: pack to motor 21.0, belt to tyre envelope 12.0, charger to pack 12.0, lower cover to pack 5.2, cabinet to pack 5.0, swingarm to motor 10.2.

### Regulatory geometry screen (screening on envelopes, not certification)

| Rule | Value | Limit | Result |
|---|---|---|---|
| FMVSS 108 headlamp centre height | 885 mm | 559 to 1,372 | pass |
| FMVSS 108 tail/stop lamp height | 869 mm | 381 to 1,829 | pass |
| FMVSS 108 turn signals, height | 728 to 743 mm | 381 to 2,108 | pass |
| FMVSS 108 turn signal spacing, front / rear | 410 / 262 mm | at least 229 | pass |
| FMVSS 108 rear reflector height / area | 642 mm / 2,040 mm2 | 381 to 1,524 / at least 1,935 | pass (area was 1,320, **fixed**) |
| FMVSS 108 side reflectors height | 813 mm | 381 to 1,524 | pass |
| FMVSS 111 mirror glass area, each | 10,400 mm2 | at least 8,065 | pass |
| FMVSS 111 mirror height / outboard of the grip | 1,244 mm / 345 and 355 mm | 900 / 300 | pass (my design rules) |
| FMVSS 123 front brake master cylinder on the right | yes | right | pass |
| FMVSS 123 left lever present, kill/ignition switch on the right | yes | | pass |

**Not met or not checked (open list):** right-foot rear brake pedal is not modelled (ledger allowance only); ISO symbols and tell-tales are not drawn; lamps are envelopes (no DOT part, no photometry, no visibility angles); the light band is not yet in front of a certified lamp; reflector area limit is my reading and the compliance agent should confirm 1,935 mm2; plate lamp angles and the EU front signal spacing are not checked.

## 4. Overlaps (broad sweep, all accepted or listed)

Accepted as mounting contacts, as in rev C: radiator core, fan and grille inside the pod shroud (18,791 / 11,078 / 266 mm3), plate and its reflector (8,160), grip in handguard (462 each), brake hose on the left handguard (648), post feet into the case roof (149 and 61 each), the doubler pads touching the case (5). The rev C HV box, tank and GX14 overlaps are gone (the tank rear wall is opened around the HV box). **New, not fixed:** the rack plate nicks the seat tail by 12,069 mm3 (about 6 mm deep) because the tail got shorter and the seat did not. It needs the rack plate 20 mm rearward or the seat tip trimmed. I stopped at one more rebuild, which the lead had ruled out.

## 5. The belt-side swingarm does not package (decision needed)

The request was a left (belt-side) single-sided arm with the pulley outboard of it. The numbers:

| Item | Value |
|---|---|
| Arm on the belt side, inner face Y110, width 57 | outer face Y167; pivot boss out to Y185 |
| Pulley and 62 mm belt outboard of the boss and of the frame node (node tubes at Y195, outer face about 214) | belt inner flange at about Y-217 to -222, outer flange at about Y-285 to -290 (today Y-107 to -181) |
| Frame node, left motor cover, pivot cap, left peg hanger plate (Y-230 to -236) | all sit inside that belt zone; the whole left node would have to move out about 90 mm |
| Left peg: the belt bottom run passes at Z262 under peg height Z270 at X420, so the peg must clear the belt | rubber centre moves from Y-275 to about Y-381 against Y+275 on the right: **106 mm foot-spread asymmetry**; the alternative is moving the pegs 175 mm forward, past the motor |

The fallback (right arm, drive on the right) has the same numbers mirrored: the belt still has to sit outboard of the arm and the frame node. So both fail on the same clash. Options for the lead: (a) accept the asymmetric left node, pegs and a 90 mm wider left side; (b) a removable section on a two-bearing arm kept on the right with the belt inboard of the node but with the 2.9 kNm sideways moment kept and answered by a stiffer yoke; (c) put the belt inside the arm span (arm outboard of the belt, removable outer section) and re-route the frame node. I did not guess among these. **The FEA yoke and the 34-44 kN pivot bearing loads therefore stand as FEA reported them for the opposite-side layout.**

## 6. What the lead must do to get from about 248 kg to 240 kg

| Lever | kg | Where |
|---|---:|---|
| Coolant, hoses and sensors allowance 5.24 to the shortlist's 1.6 (single loop, 2 L) | -3.6 | ledger (`mass-rollup.py` ALLOW), thermal agent's 10-thermal.md moves 1.1 kg of ribbon coolant into pack internals |
| HV cable allowance 3.72 to the shortlist's 1.5 (shorter runs) | -2.2 | ledger |
| Swingarm shell rule 4.25 mm to FEA's 4.0 mm | -0.1 | ledger |
| Add rules: thermostat 0.15 kg, 3 kW PTC 1.14 kg, 320 mm front disc 1.2 kg each | +1.8 | ledger |
| Carbon wheels (shortlist ALT) | -1.7 | owner decision, +2,700 dollars |
| Chassis at 22.7 kg in the roll-up (FEA says 25): cast nodes (-2) and thin lugs (-1) from 09-structures.md | -3 | FEA owner |

The first three plus the added rules close to about 244 kg. The rest needs the carbon wheels or the cast nodes.

## CAD change requests for others

1. Ledger: rules for `Coolant_thermostat_wax`, `Coolant_PTC_heater_3kW` (both currently unmatched, mass not in the total), slot value for 320 mm front discs, and the swingarm 4.0 mm wall.
2. Thermal: confirm that moving the radiator cores 20 mm inboard (same size, same 35 degree angle) is acceptable; the pod mouth and vent geometry are unchanged.
3. Compliance: confirm the reflector area limit; list a rear brake pedal and tell-tale panel as design items.
4. Structures: the cross brace is 75x5.5, not 76x5.5; the lug brackets to Y144.7 are not designed; the left carrier yoke is not modelled.

## Before and after renders

| View | Rev C (before) | Rev D (after) |
|---|---|---|
| Side | `visuals/revC-before/cycles-adventure-side.png` | `visuals/cycles-adventure-side.png` |
| Hero | `visuals/revC-before/cycles-adventure-hero.png` | `visuals/cycles-adventure-hero.png` |
| Front three-quarter | `visuals/revC-before/cycles-adventure-front34.png` | `visuals/cycles-adventure-front34.png` |
| Rear three-quarter | `visuals/revC-before/cycles-adventure-rear34.png` | `visuals/cycles-adventure-rear34.png` |
| Other views (new run) | | `side_right`, `front`, `detail_front` |
| Rider views | | `cycles-adventure-rider-side.png`, `cycles-adventure-rider-hero.png` |

Look compared with `design/baseline black.png`: the lower body is now one slab with bolts and the tank skirt, as in the reference; no guard tubes; tidier tail. Not matched: the front vertical corner chamfer steps band by band (slightly jagged in the hero view), the rear pulley still renders as bright metal, the pods are still proud of the flank (about 55 mm), and the case flank is flat with no panel lines. Beak, light band, screen, narrow waist, sculpted saddle, matte black and the 832 mm seat are unchanged.

## What this does not prove

- **The mass is a CAD roll-up with ledger rules, not a weighed bike.** 97 % of running gear and all of cooling are estimates.
- **No new FEA was run on rev D.** The FEA numbers are for the geometry FEA saw; the 5 mm front wall, the lugs at Y144.7 and the front lug at Z532 are mine and are not re-analysed. The slider case has no spare.
- **The vents are ports, not a vent system:** no burst discs, ducts, or flow test; the 17 mm belly gap is assumed to work as a duct.
- **The regulatory screen is on envelopes.** It is not a certification and uses the limits as the compliance agent read them.
- **The belt-side arm was not built**, so the pivot bearing loads and the yoke assumption are unchanged.
- **Renders** are visual checks; I did not diff them pixel by pixel against the reference.
