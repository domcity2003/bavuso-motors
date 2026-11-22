# Bavuso V1: structures (frame, single-sided swingarm, pack case)

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Scripts (`program/tools/`): `fea-frame-v1.py` (model and load cases), `fea-fatigue-v1.py`, `fea-size-v1.py` (sizing loop), `fea-swingarm-v1.py` (arm shell model), `fea-handcheck-v1.py`, `fea-summary-v1.py`. Results and solver files: `program/data/fea/` (`results-final-h*.json`, `arm-final-h*.json`, `sweep-*.csv`, `run/`). The old `detailed-design/tools/fea-*.py` are untouched. Labels: calculated = FEA or hand calculation; estimate = my assumption.

## The plain answer

**The V1 chassis does not fit 18 kg. The lightest design I found that passes every check weighs about 23.4 kg as modelled, and roughly 25 kg once pads, bosses and bolts are added. The cast-node option brings the model to 21.3 kg (not re-verified at the fine mesh).** That is 5 to 7 kg over the Gate A budget.

Four findings drive this:

1. **The belt on the left and a single-sided arm on the right is the hard part.** The belt pulls the wheel forward 274 mm away from the arm. That loads the arm sideways (2.9 kNm at the 11.3 kN design pull) and pushes 36 to 45 kN onto the pivot bearings. The CAD's 46 mm-wide pivot and 6008 bearings cannot take that.
2. **If the belt loop is closed through the frame, the frame fails badly.** With the carrier stub at the left node as drawn, the tail rails reach 670 MPa in plain static loading (yield 435). **The fix is to make the motor housing and the pivot stubs one load-bearing yoke**, so the belt tension stays inside the motor/arm loop. All results below assume this. EMRAX has not confirmed its housing can do it.
3. **Fatigue sets the tube walls, not peak strength.** Walls on the rails, down-links and headstock are all at Miner D of 0.4 to 0.49. The rev C tubes (32 x 2.5 and similar) are too thin; the solo case lowers the loads but not enough.
4. **The arm must be cast or forged.** A welded 6061 arm (FAT 22) fails fatigue by a wide margin; a cast A356 arm passes. At 4 mm wall the arm weighs 1.8 kg plus bosses.

## Load cases (solo, 240 kg bike scaled from the ledger, 90 kg rider, 25 kg luggage; no passenger)

Total 355 kg, 1,574 N front / 1,909 N rear static, CoG 574 mm above ground. Belt preload (3.05 kN per span, 6.1 kN on each shaft) is in every case.

| Case | Load | Required SF on yield |
|---|---|---|
| C1 | static 1 g | 1.5 |
| C2 / C6 | front / rear bump 3 g | 1.2 |
| C3 / C4 | braking 1.1 g front only; plus 2 g bump | 1.2 |
| C5L / C5R | 45 deg lean x 1.5, **both directions** (the arm is not symmetric) | 1.2 |
| D1 | belt design pull 11.3 kN (9.4 / 2.0 kN spans), static contact | 1.2 (this load already has a 1.5 factor; 1.0 would be the lenient reading) |
| D2 / D3 | peak-torque launch (6.2 / 1.3 kN spans, 0.69 g) / peak regen | 1.2 |
| C7a-d | pack inertia 20 g long., 8 g lat., 5 g and 10 g vertical | 1.0, pack seams 140 MPa |
| C9b, C9c | 21 kN outward crash slider at front / rear link lug | 1.0 |
| Arm only | rear brake 1.5 kN | 1.2 |

The C9a case (pivot) was dropped because the pivot nodes are the supports; the pivot slider is hand-checked only (see not proved). Fatigue uses the earlier road spectrum (160,000 km) plus a drive spectrum: launches at 20 to 100 % of peak torque (1e6 down to 2e3 events), regen at half those counts, 1e3 belt shocks. Method IIW nominal stress, FAT 45 tube welds, 63 cast headstock, 56 forged bridge, 40 cast A356, gamma 1.25, D at most 0.5.

## CAD change request (apply to `tools/build-adventure.py`)

Tube is outer diameter x wall in mm (4130). "CAD" is the rev C value.

| Part | CAD | Change to | Note |
|---|---|---|---|
| Upper rail 0 (pivot node to seat front) | 38 x 2.5 | **38 x 1.5** | strength is 0.4 of limit; 2.0 is wiser (+0.3 kg, not run) |
| Upper rail 1 (seat rail) | 32 x 2.5 | **38 x 3.5** | in the thigh zone; check the waist |
| Upper rail 2 (to head tube) | 38 x 3.0 | **40 x 5.0** | |
| Upper posts front / rear | 25 x 2.0 | **27 x 2.5 / 27 x 2.25** | feet at Y +-148 (not 160); pad radius 45, not 60 |
| Down-link | 32 x 2.5 | **36 x 3.75** | +2 mm radius: re-check the 20 mm tyre gap |
| Rear pack link | 32 x 2.5 | **40 x 4.25** | sized by the 21 kN rear slider |
| Tail rail | 30 x 2.0 | **30 x 2.5** | |
| Tail brace | 25 x 1.5 | 25 x 1.5 | **end point error**: it ends at (160, +-144, 740), 52 mm off the tail rail. Move to (160, +-111.4, 779.7) |
| Shock-bridge diagonals | 22 x 1.5 | 22 x 1.5 | |
| Shock bridge box | 80 x 45 x 4 | **80 x 45 x 2.0** | |
| Head tube (cast headstock) | 56 x 3 (ID 50) | **56 x 3.5** (ID 49, bore the cup seats to 50) | |
| Head gusset | 6 mm | **4 mm** | |
| Top shock plates | 12 x 36 | 12 x 36 | |
| Pivot stub, right | 40 / 30, Y110-150 | **62 OD x 9 wall, Y105 to 185**, bearings at Y105 and Y185 (span 80) | bearing selection: tapered rollers, about 34 kN each at design |
| Left carrier stub | 40 / 30, Y-186 to -192 | keep; add the **load-bearing yoke** | motor housing bolted between left stub and right stub |
| Swingarm (cast A356-T6, single-sided) | 130 x 46 to 80 x 40, 4.25 | **box 117 x 54 at the pivot to 102.5 x 57 at the axle, 4.0 wall**, centre Y +138.5 (inner face stays at Y110 at the axle), 8 mm end plates, pivot boss spans Y105-185 | cast; welded 6061 fails |
| Cross brace (A356) | 54 x 4 | **76 x 5.5**, Y-36 to the arm wall | local boss and rib at the bolt-on are needed |
| Shock tower webs | 10 x 44 (radius 22) | **14 x 66** (stadium radius 33) | |
| Lug bolts, pads | | 4 x M10 10.9 per lug as before | lug and pad weights are estimates |
| Pack case | 4 mm | see pack section | |

## Verdict table (final design, 12 mm pack mesh, solo)

SF = yield / worst nominal stress in a frame member (arm and tower in A356, 200 MPa).

| Case | Worst member | Stress MPa | SF | Required | Verdict |
|---|---|---|---|---|---|
| C1 static | arm, near pivot | 103 | 1.94 | 1.5 | pass |
| C2 front bump | arm | 106 | 1.90 | 1.2 | pass |
| C3 braking | upper rail 2 | 259 | 1.68 | 1.2 | pass |
| C4 braking + bump | upper rail 2 | 266 | 1.64 | 1.2 | pass |
| C5L / C5R | cross brace / arm | 123 / 128 | 1.63 / 1.56 | 1.2 | pass |
| C6 rear bump (shock 11.5 kN) | cross brace | 164 | 1.22 | 1.2 | pass, no spare |
| D1 belt design | arm axle end | 167 (shell model 156-160) | 1.20 (shell 1.25-1.28) | 1.2 | pass, no spare |
| D2 / D3 | arm | 134 / 108 | 1.49 / 1.84 | 1.2 | pass |
| C7a 20 g | rear post | 329 | 1.32 | 1.0 | pass for tubes; **pack front 167 MPa vs 140 seam: fails at 4 mm** |
| C7b 8 g | rear link | 254 | 1.71 | 1.0 | pass; pack front 126 |
| C7c / C7d 5 g / 10 g | rear link | 55 / 110 | 7.9 / 3.95 | 1.0 | pass |
| C9b front slider 21 kN | rear link | 409 | 1.06 | 1.0 | pass |
| C9c rear slider 21 kN | rear link | 427 | 1.02 | 1.0 | pass, no spare |
| Fatigue, worst weld (down-link at headstock) | | D 0.49 | | 0.5 | pass; upper rail 1 0.47, rail 2 0.41, post 0.41, bridge 0.40 |
| Fatigue, cast arm (beam model) | | D about 0.05 | | 0.5 | pass if cast (shell model: 0.02 to 0.7 depending on mesh near the rigid ends; see below) |
| Fatigue, welded 6061 arm | | D 0.64 to 5 | | 0.5 | **fail** |
| Torsion, head to pivot | 4.4 kNm/deg | | | at least 3 (my target) | pass |
| Lateral, head | 1.3 kN/mm | | | at least 1.5 (my target) | **below my target**; the old study had 4.6. Not a strength failure |
| Pivot bearings, design 11.3 kN, span 80 mm | in 43.6 kN, out 33.4 kN | | | | needs about 50 mm tapered rollers. At the CAD span of 36 mm: 85 and 74 kN, impossible |

The belt loop yoke result is the 11.3 kN belt case with the yoke; without it the tail rail reaches 1,388 MPa.

## Swingarm (shell model: S4, 12 mm mesh; rigid pivot boss and axle boss; two-bearing pivot)

| Item | Result | Comment |
|---|---|---|
| Lateral stiffness at the axle | 1.01 kN/mm (1.006, 1.011, 1.018, 1.020 at 16, 12, 8, 6 mm) | converged to 1.5 % |
| Torsion about the arm axis | 1.48 kNm/deg | converged |
| Yaw about Z (toe) | 1.73 kNm/deg | |
| Vertical at the axle | 3.1 kN/mm | pivot rotation locked |
| Benchmark | lateral 0.8 to 1.6 kN/mm, torsion 1 to 2 kNm/deg, quoted from Cossalter in a student racing-swingarm FEA report | secondary source, not a measured production arm |
| Strength SF (arm, away from the bolt-on) | 1.25 to 1.28 worst (belt design), 1.5 to 2.2 elsewhere | converged across meshes |
| Fatigue at the brace bolt-on | D about 4 at the 4 mm wall (FAT 40) | **unreinforced bolt-on fails**: needs a cast boss and rib. Not designed |
| Shock force static | 4,154 N hand, 4,063 N frame FEA, 4,154 N arm model | agree |

## Mass

| Group | kg (modelled) |
|---|---|
| Upper rails 0, 1, 2 (pair) | 1.0 + 2.9 + 2.0 |
| Down-links | 2.5 |
| Tail rails and braces | 2.2 + 1.0 |
| Rear links, posts | 0.9 + 0.9 |
| Swingarm box (cast) | 1.8 |
| Cross brace and tower | 0.6 + 0.6 |
| Pivot stub, pivot block | 0.9 + 0.3 |
| Head tube, gusset | 1.0 + 0.75 |
| Shock bridge, plates, diagonals | 0.9 + 0.5 + 0.6 |
| Lug blocks (8) | 1.8 |
| **Modelled chassis** | **23.4** |
| Not modelled: 8 pack pads (about 0.8), arm boss and end plates (about 0.5), bolts, bearings | about +1.5 |

Sweep (all through `fea-size-v1.py`, 36 mm mesh, then the chosen one re-run fine): CAD tube diameters 23.3 kg; diameters free to grow 22.5 kg (chosen, with fatigue touch-ups at the fine mesh, 23.4); **cast or forged steel nodes (FAT 63) 21.3 kg (not re-verified)**; no crash-slider cases at all 22.65 kg (the 21 kN sliders cost only 0.7 kg). Lug blocks (1.8 kg), the pivot stub (1.2 kg) and the gusset (0.75 kg) are rough.

**Ways toward 18 kg**, in order of value: cast steel nodes at the joints (-2 kg), thin-wall lug brackets in place of 30 x 40 steel blocks (about -1 kg), accepting a smaller fatigue spectrum after measured ride data (the 2x harsher spectrum would need more mass, not less), and a second look at the belt architecture (arm on the belt side, or a motor-in-pivot casing built to carry the loop).

## Pack case: 3 mm against 4 mm

| Item | 4 mm | 3 mm | 3 mm, front wall 4 mm |
|---|---|---|---|
| Case mass (calculated) | 9.6 kg | 7.4 kg | 7.7 kg |
| Worst case-wall stress, riding cases C1-C6, D (away from lugs) | 34 MPa | 50 MPa | 50 MPa |
| 5 g / 10 g vertical drop | 44 / 88 | 79 / 158 | 94 / 187 |
| 8 g lateral, 20 g forward (front wall; seam value 140) | 126 / 167 | 198 / 270 | 163 / 157 |
| 10 kN crush, 100 mm patch, no cell backing | 587 | 1,040 | 1,040 |
| Frame lateral stiffness | 1.30 kN/mm | 0.97 | 0.98 |

**3 mm is fine for riding loads and fatigue** (50 MPa against a FAT 28 seam; damage far below 0.01). **It is not enough for crash retention (20 g) or the 10 g drop on the floor, and 4 mm is not either at the front wall** (167 against 140). The 20 g case needs a 5 mm front wall (as the earlier study found) or cell-holder cross ribs. The crush numbers ignore the cells, which back the walls, so they are an upper bound, not a pass or fail. The 3 mm option saves 2.2 kg but costs 25 % of lateral stiffness. My pick: 3 mm sides, top and rear with a 5 mm front wall and floor ribs, about 7.9 kg, once a cell-backed crush analysis exists.

## Mesh and hand checks

- Frame model: stiffness 4.462 / 4.445 / 4.478 kNm/deg at 24, 12 and 6 mm (27,055 nodes at 6 mm); member stresses identical to 0.1 %. Lateral 1.35 / 1.31 / 1.33.
- Pack front wall under 20 g: 143 / 167 / 176 MPa at 24 / 12 / 6 mm. It keeps growing at the re-entrant corners, as a singularity should; use as a flag, not a number.
- Arm: stiffness converged (above); strength field converged; peak stresses beside the rigid ends and the bolt-on patch are not (fatigue D from 0.02 to 0.7 by mesh).
- Hand checks (`handcheck-final.json`): shock force 4,154 N vs 4,063 N FEA (2 %); belt moment 2.87 kNm = 11.3 kN x 254 mm; bearing force 35.9 kN each at 80 mm span vs 33 to 44 kN FEA; arm section modulus about Z 23,000 mm3 gives 125 MPa from the belt moment alone, 160 MPa in FEA with the vertical load; 38 x 3 cantilever 37 MPa per 1 kN at 100 mm, matching the old study's beam check.
- Model bugs found and fixed: arm pivot initially welded (shock force 1.7 kN instead of 4.1), orphan nodes under the belt loads, and ill-oriented rigid beams. After the fixes the hinge check above passes.

## What this does not prove

- **The yoke.** Closing the belt loop through the EMRAX housing is my assumption. EMRAX publishes no housing or shaft limit. If it cannot, the frame needs far more mass (tail rail 1,388 MPa at 11.3 kN in the frame-only path).
- **The pivot and bearings.** Bearing loads are reaction forces; no bearing life, no stub-to-yoke joint, no pivot slider load (21 kN) check.
- **Rigid bosses.** The pivot boss, axle boss, hub and axle stub are rigid in the model. The brace bolt-on and its reinforcement are not designed; the unreinforced value fails.
- **Fatigue spectrum** is my assumption (earlier study, plus a drive spectrum); a 2x harsher one fails. Welds, bolt holes and tube joints use nominal stress and detail classes, not hot-spot or solid sub-models.
- **Belt motor-end load** all enters at the left stub; the real split with the motor mounts is unknown. Motor torque reaction (220 Nm) is not applied as a separate load.
- **Front lug and rear lug are 11 mm outside the 333 mm case** (Y178 vs 166.7); I modelled a bracket to Y144.7. Needs a bracket design.
- Not run: buckling, crash plasticity, modal or wobble coupling, fork, triple clamps, axles, wheel bearings. Mass-rollup snapshot used (`mass-rollup-snapshot.csv`, scaled to 240 kg); an unscaled run at the 255 kg roll-up (370 kg total) raises stresses 3 to 4 % (rail 2 braking 270 MPa, bridge bump 209 MPa, cross brace 169 MPa), so the pass margins above hold, but C6 (SF 1.2 required) drops to about 1.18 on the cross brace: the design only closes at 240 kg.
- Crash sliders replace guard tubes in the latest CAD; C9b/c are kept as a conservative stand-in for slider loads.
- Sizing loop oscillates at the last 0.25 mm step on the tower and tail rail; the chosen walls were hand-fixed and then checked at 12 mm.
