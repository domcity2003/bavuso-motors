# Bavuso V1.0 adventure: aerodynamics study (CFD)

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5).
Runs: November 12–14, 2026, all finished. Geometry: `cad/Bavuso-V1.0-adventure.FCStd` as saved at 09:54 on Nov 12 (sha256 in `aero/geometry-manifest.json`).

## The plain answer

- **Drag area (CdA) is about 0.385 m² at 70 mph** on the finest mesh (3.47 M cells), with an average-size man sitting upright on the current adventure body.
  - The three meshes give 0.421, 0.413 and 0.385. The number has not fully settled, so **read the result as 0.38–0.41 m²** for a smooth dummy rider.
  - A real rider in a textile jacket adds roughly 10%. **Plan on about 0.42 m².**
  - **It compares well:**
    - It beats the Nov 1 baseline (0.44 m², older low-slung body), although this bike is taller.
    - It beats measured upright electric bikes: Energica Ego+RS 0.50 and LiveWire One 0.57 in a wind tunnel.
    - It beats what the Zero DSR/X adventure bike's published 70 mph range implies (about 0.50–0.59).
- **Range at a steady 70 mph on the 32.7 kWh pack:**
  - about **201 miles** with the CFD number;
  - about **186 miles** with a real jacketed rider.

  These come from the repo's own energy model. **So 200 miles is met only on paper.** The air takes about 81% of the energy at 70 mph, and every 0.01 m² of CdA is worth about 4 miles.
- **The top three drag sources** make up 55% of all drag (fine mesh):

  | Part | Drag | Share of total | What it is |
  |---|---|---|---|
  | Lower body | 47 N | 21% | 28 N of it is the flat, square-cornered battery-cover front face, 420 mm wide, right behind the front tyre |
  | Tank and fairing shell | 47 N | 20% | 28 N of it comes from air that gets inside the open shell and hits its internal walls |
  | Screen | 34 N | 15% | A flat plate at 51° from horizontal |

  The CAD changes below are estimated at 8–12% (CdA about 0.34–0.355). **That makes 200 miles at 70 mph hold with a real rider** (about 200–206 mi). The gain is an estimate. It must be checked by re-running this pipeline on the changed CAD (one command).
- **Crosswind, 10° yaw** (a 12 mph gust from the side at 70 mph, medium mesh):
  - side force 102–115 N, acting 0.28–0.39 m ahead of the CoG and 0.56–0.63 m above the road;
  - yaw moment about the CoG of 33–40 N·m. The nose is pushed downwind.
  - Drag along the wind rises about 32%.

  These are ordinary numbers for an upright bike with a fairing. They go to the dynamics study as inputs.
- **Lift is near zero overall,** but the bike pitches nose-up. At 70 mph the front axle unloads by about 111 N (11 kg), and the rear gains about 108 N. That is about 6% of the front static load, which is acceptable.

## Verdict table

| Item | Value | Required / reference | Margin | Status |
|---|---|---|---|---|
| CdA at 0° yaw, 70 mph (fine mesh) | 0.385 m² (mesh band 0.38–0.41) | ≤ 0.40 m² (sizing basis in `tools/powertrain-optimise.py`) | +4% (−3% at the medium mesh) | pass, not robust |
| CdA with a real rider (+10%) | about 0.42 m² | ≤ 0.40 m² | −6% | **fail** |
| Range at a steady 70 mph, 32.7 kWh, 288 kg + 90 kg rider | 201 mi (CFD), 186 mi (real rider) | 200 mi | +0.5% / −7% | **open: met only on paper** |
| Mesh convergence, 3 meshes (0.78 / 1.56 / 3.47 M cells) | 0.421 / 0.413 / 0.385; −1.9% then −6.9% | ≤ 2% between the last two meshes | −4.9 pt | **fail** (the bike-body force passes: −2.6%) |
| Force convergence (iteration noise) | ±0.6–1.0% (1σ); window drift 0.2–1.4% | drift < 1% | — | pass (medium marginal at 1.4%) |
| Mass balance (net flux / inflow) | ≤ 0.0015% | < 0.1% | large | pass |
| Force bookkeeping (13 parts summed vs total; surface integral vs solver per part) | 0.0 N; within 1 N on every large part | consistent | — | pass |
| y+ (area-weighted, fine mesh) | median 40–195 by part; 20% of lower-body and 42% of seat/tail area below 30 | 30–300 for wall functions | — | open (sheltered zones) |
| Front-axle unloading at 70 mph | 111 N (≈ 6% of the front static load with rider) | < 15% | large | pass |
| Side force / yaw moment at ±10° yaw (medium mesh) | −102 / +115 N; −40 / +33 N·m about the CoG | input for dynamics | — | open |
| ±10° symmetry | side force within 12% | about a mirror | — | pass (with note) |

## What was simulated

| Item | Setting |
|---|---|
| Software | OpenFOAM 12 (blueCFD-Core 2024-1), `foamRun` incompressibleFluid, steady RANS, k-ω SST, wall functions (no prism layers), 4 MPI ranks |
| Speed | 70 mph ground speed = 31.29 m/s; ρ 1.225 kg/m³; ν 1.5e-5 m²/s; q = 599.8 Pa at 0° |
| Road and wheels | moving ground at road speed. Wheels are rotating walls: 94.3 rad/s front, 97.8 rad/s rear, from rolling radii 0.332 / 0.320 m. Tyres sink 10 mm into the floor so the contact patch is not a knife edge. |
| Yaw | Fixed ground speed plus crosswind, as in `simulation-plan.md`. +10° is air at (−31.29, −5.52, 0) m/s, wind from the rider's left, 31.78 m/s. The sides are freestream boundaries so cross-flow can pass through. |
| Domain | X −8…5.5 m, Y ±3.5 m, Z 0.01…4 m. Blockage about 2.7%. |
| Geometry | Current adventure CAD: every body, chassis and running-gear part. Cells and keep-out volumes are left out. The inverter and BMS supplier STEP parts become boxes; they sit inside the tank. **The body shells are open, as in the CAD,** so air gets inside them. |
| Rider | 50th-percentile man, 1,755 mm, as a smooth buck (capsules and ellipsoids). Joints come from the `comfort-study.py` link model on the CAD's own hard points: sit point Z850, grips (901, ±351, 1129), pegs (420, ±268, 340). Upright trunk; helmet centre at Z1645. |
| Frontal area | 0.766 m² total: bike 0.50, rider 0.52, overlapping. So Cd ≈ 0.54. |
| Mesh family | Every level is scaled from the background cell, so meshes refine by √2 in every direction. Surfaces: level 5–6, so 15.6/7.8 mm (coarse), 11/5.5 mm (medium), 7.8/3.9 mm (fine). Boxes at levels 1–3 cover the near field and the wake (±0.9 m wide for yaw). |
| Run length | 600 iterations from a potential-flow start (fine mesh: 450, to save CPU while the machine was shared). Forces averaged over the last 200 (fine: 150). The drag settles by iteration 150–250 in every case. |

**Patches.** Each part group is its own patch, so the solver reports force by part: screen, mirrors, bars and controls, fairing and tank, fork and fender, lower body (pack covers and pack), swingarm and pegs, seat and tail, helmet, torso and arms, legs, front wheel, rear wheel.

### Reproduce: one command

From `v1.0` in Git Bash:

```
sh detailed-design/tools/aero-run-all.sh
```

- **What it does:**
  1. exports the current CAD and rider (`aero-export-geometry.py`, about 20 s);
  2. writes each case (`aero-make-case.py`);
  3. meshes and solves on 4 ranks (`.tools/ofrun.sh`);
  4. runs `aero-report.py`.
- **Cases and run time:** `m1-coarse`, `m2-medium`, `m3-fine`, `yaw+10`, `yaw-10`. About 10 h on an idle CPU, longer when the CPU is shared.
- **After the body is re-surfaced:**
  1. delete `detailed-design/aero/run/` (the old STLs and finished cases are skipped otherwise);
  2. run the same command;
  3. for a quick comparison, name only the case you need, for example `sh detailed-design/tools/aero-run-all.sh m2-medium` (about 2 h).
- **Where the results go:** `detailed-design/aero/aero-results.json` and the pictures in `detailed-design/aero/`. The geometry map is in `aero/geometry-manifest.json`.

## Results

### Forces at 0° yaw, 70 mph (fine mesh, 3.47 M cells; medium in brackets)

| Part | Drag (N) | CdA (m²) | Share | Lift (N, + up) |
|---|---:|---:|---:|---:|
| **Whole bike + rider** | **230.6** (247.7) | **0.385** (0.413) | 100% | +3.0 |
| Lower body: pack covers, pack, frame inside | 47.3 (48.0) | 0.079 | 21% | −62.6 |
| Fairing, tank, headlamp, radiators | 47.1 (45.1) | 0.079 | 20% | +54.2 |
| Screen | 33.7 (33.6) | 0.056 | 15% | −26.4 |
| Fork, front fender, calipers | 20.8 (19.7) | 0.035 | 9% | +4.9 |
| Seat, tail, plate, rear hugger | 17.6 (21.9) | 0.029 | 8% | +2.8 |
| Rider torso and arms | 14.5 (19.6) | 0.024 | 6% | +12.2 |
| Rider helmet and neck | 11.0 (12.2) | 0.018 | 5% | +15.6 |
| Front wheel | 10.8 (11.0) | 0.018 | 5% | −7.6 |
| Rider legs | 9.9 (10.5) | 0.017 | 4% | +1.6 |
| Mirrors (pair) | 8.7 (10.4) | 0.015 | 4% | +1.4 |
| Bars, grips, levers, switchgear | 4.8 (5.9) | 0.008 | 2% | +5.7 |
| Rear wheel | 2.3 (7.4) | 0.004 | 1% | +1.5 |
| Swingarm, belt, pegs, shock | 2.1 (2.4) | 0.004 | 1% | −0.3 |

- **Rider vs bike:** the rider is only 15% of the drag (35 N). The bike's bodywork shelters him. The bike body is 79% and the wheels 6%.
- **Pressure vs friction:** 97% of the drag is pressure drag (223 N), from the shape. Only 7 N is skin friction.
- **Axle loads:** front axle +110.9 N (lifts), rear −107.9 N (pressed down). Moments are taken about the rear contact point; the pitching moment about the CoG is −46 N·m.
- **Power to push the air** at 70 mph is 7.2 kW at the wheel.
- **Cd:** frontal area is 0.766 m², so Cd ≈ 0.50.

**Zones inside the big patches** (pressure drag, fine mesh):

| Zone | Drag (N) |
|---|---:|
| Inside the tank and fairing shell, and the radiator side vents (X ≤ 1.05 m) | 28.1 |
| Pack and cover front face, belly nose (X > 0.95 m) | 27.7 |
| Pack sides, motor covers (X ≤ 0.95 m) | 17.9 |
| Nose, headlamp, beak (X > 1.30 m) | 14.4 |
| Tail, licence plate and hanger, rear hugger | 9.1 |
| Seat | 8.9 |
| Cockpit cheeks and dash | 3.8 |

### What the pictures show

The pictures are in `detailed-design/aero/`:

| File | What it shows |
|---|---|
| `drag-map-side.png` | Where the drag is made, seen from the side |
| `midplane-speed.png`, `midplane-cp.png` | Air speed and pressure on the centreline |
| `y033-speed.png` | Air speed through the hand and mirror line |
| `top-speed-z045.png`, `top-speed-z114.png` | Plan views at knee and hand height |
| `convergence.png` | Drag history of every case |
| `mesh-study.png` | Drag area against mesh size |

1. **The battery covers end in a flat wall.**
   - In the plan view at knee height, the cover front at X≈1.06–1.11 m is a 420 mm-wide square wall.
   - It has a full stagnation zone, and the flow separates at its two square corners.
   - It sits in the front tyre's wake, but the tyre (120 mm) is much narrower than the wall (420 mm).
2. **Air gets inside the upper body.**
   - The centreline view shows flow entering under the screen and nose and through the side grilles.
   - Inside, it hits the blunt internal faces at X≈0.7 and X≈1.05 m. These are the vertical red lines on the drag map.
   - The Nov 1 baseline found the same problem, and the shell is still open.
3. **The screen is a flat plate.**
   - It carries a stagnation line along its whole face.
   - It throws a jet over the cockpit that lands on the helmet. The helmet is 11 N; the rider's chest and arms sit in the screen's shadow.
4. **The hands and mirrors sit in undisturbed air** (the plane through Y = 0.33 m).
   - Each mirror head leaves a full wake.
   - The hands and forearms get no shelter at all, because the bike has no hand guards.

### Force convergence

- The drag settles by iteration 150 on both meshes (`convergence.png`).
- In every case the drag settles by iteration 150–250 (`convergence.png`).
- **The averaged windows swing by:**

  | Mesh | 1σ | Range of CdA | Mean vs the previous window |
  |---|---:|---|---:|
  | Fine | ±0.0037 | 0.378–0.393 | −0.45% |
  | Medium | ±0.0027 | 0.406–0.418 | 1.4% |

  That is the normal slow wobble of steady RANS around a bluff body, not a trend. Treat ±0.005 m² as the iteration noise.
- **Mass balance:** the net flux through all open boundaries is ≤ 1.5e-5 of the inflow.

### Mesh sensitivity

| Mesh | Cells | Background cell | Surface cells | CdA | Bike body (N) | Rider (N) | Wheels (N) | Front axle lift |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Coarse | 0.78 M | 0.50 m | 15.6 / 7.8 mm | 0.421 | 172.9 | 60.9 | 18.9 | 118 N |
| Medium | 1.56 M | 0.354 m | 11 / 5.5 mm | 0.413 | 187.0 | 42.3 | 18.4 | 118 N |
| Fine | 3.47 M | 0.25 m | 7.8 / 3.9 mm | 0.385 | 182.1 | 35.4 | 13.1 | 111 N |

- **The total is not mesh-converged.** It fell 1.9% from coarse to medium and 6.9% from medium to fine. The change grows instead of shrinking: the convergence ratio is R = 3.5, where 0 < R < 1 is needed. So these meshes are outside the asymptotic range, and a Richardson extrapolation would be meaningless. None is quoted.
- **The bike-body patches are converged:**
  - the bike body went 187 → 182 N (−2.6%);
  - the screen, lower body, fairing and fork each moved ≤ 2 N.
- **What is still moving is the wake:**
  - the back of the rider (42 → 35 N);
  - the seat and tail (22 → 18 N);
  - the rear wheel (7 → 2 N), which sits in the rider's wake.

  These are base pressures set by how finely the wake is resolved. The wake box gets 44 mm cells on the medium mesh and 31 mm on the fine. Wakes behind bluff bodies usually recover pressure as the mesh refines, so **the next mesh would more likely lower CdA a little than raise it.**
- **Honest band: 0.38–0.41 m²**, with 0.385 the best single value.
  - A fourth mesh (about 7 M cells, 15–20 h on 4 ranks) or prism layers would narrow it.
  - So would a wake box refined one more level. That is the cheapest next step: about 1.5 M extra cells.
- **What this means for decisions:** the ranking of parts holds on all three meshes (lower body ≈ fairing/tank > screen > fork > tail/rider). So the CAD change requests stand.

### y+ (wall functions)

**Area-weighted y+ on the fine mesh:**

| Part | 5th pct | Median | 95th pct | Area below 30 |
|---|---:|---:|---:|---:|
| Screen | 35 | 67 | 139 | 1.7% |
| Fairing and tank | 31 | 91 | 200 | 4.8% |
| Lower body | 4 | 82 | 168 | 19.7% |
| Seat and tail | 0 | 41 | 220 | 41.9% |
| Helmet | 64 | 149 | 332 | 0.2% |
| Torso and arms | 72 | 195 | 407 | 0.2% |
| Wheels | 26–37 | 73–110 | 227–239 | 2–8% |

- **Most exposed surfaces sit in the log-law range** of the k-ω SST wall functions.
- **The sheltered, separated regions fall below 30:** the seat, the inner pack sides and the tail. There the flow is slow and separated, so friction is a tiny part of the drag (3% in total). The wall-function error there hardly moves the pressure drag, but it may move the wake. This is one reason the wake is the least certain part.
- **The highest y+ is about 900,** on the rider's knees and shoulders.

### Crosswind: ±10° yaw (medium mesh)

These runs used the medium mesh. At 0° the medium mesh read 7% higher than the fine, almost all of it in the wake. **So treat the yaw drag as about 5–7% high.** The side forces come mostly from the converged bike-body patches: fairing, lower body and front wheel. They should be good to about ±5%.

| | +10° (wind from the left) | −10° (wind from the right) |
|---|---:|---:|
| Air speed | 31.78 m/s (q 618 Pa) | 31.78 m/s (q 618 Pa) |
| Drag along the wind | 338.9 N, CdA 0.548 | 334.4 N, CdA 0.541 |
| Drag along the bike, which uses battery energy | 326.1 N | 319.3 N |
| Side force, + to the left | −102.4 N | +114.9 N |
| Lift | +1.6 N | −2.5 N |
| Front / rear axle lift | +163 / −162 N | +160 / −162 N |
| Yaw moment about the CoG, + nose left | −40.2 N·m | +32.5 N·m |
| Roll moment about the CoG / about the ground line | +12.8 / +64.6 N·m | −5.8 / −64.0 N·m |
| Where the side force acts (X from the rear axle, Z) | 1.19 m, 0.63 m | 1.08 m, 0.56 m |
| Iteration drift (window to window) | −0.26% | −0.24% |

CoG for the moments: (795, 0, 506) mm, from `mass-rollup.json` as updated on Nov 14. The bike only, with no rider.

**How to read it:**
- **The two directions mirror each other within about 12%.** The side force is 102 vs 115 N, and the yaw moment 40 vs 33 N·m. The bike is not symmetric: the belt and pulleys are on the left, the rear caliper and brake hose on the right. Part of the gap is also steady-RANS wake noise. **Use a mean of about 110 N side force and about 36 N·m yaw moment at 10°, ±10%.**
- **The side force acts ahead of the CoG**, 0.28–0.39 m ahead of X 0.795 m. So a gust pushes the nose downwind and leans the bike away from the wind.
- **Where it comes from** (+10° / −10°):

  | Part | Side force |
  |---|---:|
  | Fairing and tank | −45 / +46 N |
  | Lower body | −31 / +37 N |
  | Front wheel | −29 / +29 N |

  The rider pulls the other way (+7 / −13 N): his wake partly shelters the bike's back half.
- **Drag along the bike rises 29–32%.** At a steady 10° crosswind, a 70-mph ride uses about 25% more energy than in still air.
- **The forward centre of pressure** comes from the tall, slab-sided fairing, screen and lower body ahead of the CoG. That is normal for adventure bikes with fairings. The steer-torque and weave response belong to the dynamics study.

## Comparison with published bikes

| Bike, condition | CdA (m²) | How it was obtained | Source |
|---|---:|---|---|
| Energica Ego+RS, upright rider | 0.500 | wind tunnel | [Kirca & McGordon, Univ. of Warwick, Table II](https://wrap.warwick.ac.uk/id/eprint/180779/1/WRAP-Effect-rider-position-energy-consumption-23.pdf) |
| LiveWire One, upright rider | 0.569 | wind tunnel | same |
| Zero DSR/X (electric adventure, small screen) | about 0.50–0.59 | back-calculated by me: Zero's 85 mi at 70 mph on 15.2 kWh nominal / 17.3 kWh max, run through this repo's energy model (247 kg, 90% drive efficiency, 300 W aux). Rough. | [ADVPulse spec sheet](https://www.advpulse.com/adv-bikes/zero-dsrx-electric-adventure-motorcycle-first-look/), [Electrek](https://electrek.co/2022/09/13/zero-dsr-x-launched-as-worlds-first-long-range-electric-adventure-motorcycle/) |
| Scooter with rider | 0.49 | CFD and tunnel, academic | [ResearchGate, CFD on motorcycles](https://www.researchgate.net/publication/289187108_The_Role_of_CFD_on_the_Aerodynamic_Investigation_of_Motorcycles) |
| Range of all motorcycles | 0.18–0.70 | Cossalter, *Motorcycle Dynamics*, cited second-hand | [Altair two-wheeler aero notes](https://help.altair.com/hwdesktop/hwx/topics/motionview/aerodynamic_for_2wheelers_r.htm) |
| Bavuso V1.0, Nov 1 baseline (old low body) | 0.441 | this repo's CFD | `aero-baseline-report.md` |
| **Bavuso V1.0 adventure, this study** | **0.385 (band 0.38–0.41)** | this CFD (fine mesh) | this file |

**What the comparison says:**
- **I found no published wind-tunnel CdA for petrol adventure bikes** (R1300GS, Africa Twin, 1290 Adventure). Makers do not publish them.
- **Our 0.385–0.41 sits at the clean end** of the measured upright bikes. That is plausible for a large screen and fairing with a smooth simulated rider. Even with 10% added for a real rider (0.42), it is below every measured electric bike in the table.
- **A real rider in a textile jacket adds drag:** flapping fabric, a real helmet shape and gloves. **0.45 m² is a sensible pessimistic value.**

## Range at 70 mph

**The model:** `tools/powertrain-optimise.py` `wh_per_mile()`.
- Drag and rolling (Crr 0.015) at 70 mph, 90% battery-to-wheel efficiency and 300 W of accessories.
- 90% of the 32.7 kWh pack is usable.
- Bike 287 kg (`mass-rollup.json`) plus a 90 kg rider.

| CdA | Wh/mile | Range on 32.7 kWh | Nominal pack for 200 mi |
|---|---:|---:|---:|
| 0.385 (this CFD, fine mesh) | 146.5 | **201 mi** | 32.5 kWh |
| 0.413 (medium mesh, top of the band) | 155.0 | 190 mi | 34.4 kWh |
| 0.423 (fine +10% for a real rider) | 157.9 | **186 mi** | 35.1 kWh |
| 0.40 (sizing assumption) | 151.1 | 195 mi | 33.6 kWh |
| 0.35 (after changes 1–3, estimated, smooth rider) | 136.2 | 216 mi | 30.3 kWh |
| about 0.385 (after changes 1–3, with a real rider) | 146.5 | about 201 mi | 32.5 kWh |

- The bike is 288.2 kg (`mass-rollup.json`, updated Nov 14), plus a 90 kg rider.
- The air takes 81% of the wheel power at 70 mph, so drag is the range lever.
- 0.01 m² of CdA is worth about 4 miles.
- 10 kg of bike mass is worth only about 1 mile.

## Top 3 drag contributors and what to do

1. **Lower body: 47 N (21%).**
   - 28 N of it is the flat, square-cornered battery-cover front face. It sits 420 mm wide behind a 120 mm tyre.
   - Square front corners on a bluff box cost a lot. In Hoerner's *Fluid-Dynamic Drag* data, rounding the front edges to about 10–15% of the width removes most of the forebody drag.
2. **Fairing and tank: 47 N (20%).**
   - 28 N of it is air that gets inside the open shell, through the base of the screen, the side grilles and the open bottom. It hits the internal walls.
   - The Nov 1 baseline flagged the same leak. It is still open.
3. **Screen: 34 N (15%).**
   - It is a flat 6 mm plate, 51° from horizontal, with square edges.
   - It stagnates along its whole face and sends a jet onto the helmet.

Next in line:

| Part | Drag | Note |
|---|---:|---|
| Fork and fender | 21 N | |
| Seat and tail | 18 N | mesh-sensitive |
| Mirrors | 9 N | for a part this small, an outsized share |

## CAD change requests

Coordinates are saved-model mm (X forward from the rear axle, Y left, Z above ground). The gains are **estimates from the force breakdown and textbook bluff-body data, not simulated**. The "verify" column says how to check each one: re-run `aero-run-all.sh m2-medium` (about 2–3 h), and compare each patch with the medium-mesh baseline here, not with the fine mesh.

| # | Change | Exact numbers | Expected gain | Verify |
|---:|---|---|---|---|
| 1 | **Round the front corners of the battery covers** | Make the vertical front corners of `Battery_side_panel`/`Lower_body_battery_covers` **R60 outer** (now the 12 mm panel radius), from Z 240 to Z 700. To keep 3 mm clearance, chamfer the pack case's vertical front corners **20 × 20 mm** (X 1068–1088, Y ±174–194). Ask the pack/cells owner: the corner cells must clear it. Give the bottom front edge of the cover (Z 216–260) **R40**, without moving it forward: the front tyre's bump sweep is 22–30 mm away. | 8–12 N, about 3–5% | lower_body patch < 38 N (medium mesh; today 48 N) |
| 2 | **Close the upper-body shell** | **(a)** Fit a 2 mm closing tray under the tank/fairing from X 700 to X 1060, between Y ±200, along the top of the battery covers (Z ≈ 712), sealed to `Upper_body_fairing_tank` at Z 566–712. **(b)** Seal the gap between the screen base and the fairing to a deliberate **15 mm × 200 mm** vent. **(c)** Give the side radiators (X 960–1070, Y ±128–178, Z 640–780) a **closed duct**: inlet the side louvres (X 1000–1140); exit a rear-facing slot of **25 × 120 mm** each side at X 930–955, Z 650–770, ahead of the knees. Cooling flow must be sized by the thermal study; do not simply seal the radiators. | 10–15 N, about 4–6% | fairing_tank patch < 33 N (medium; today 45 N) |
| 3 | **Reshape the screen** | Keep the base at (1388, ±118, 938) and the top edge at Z 1262. **(a)** Move the top edge back from X 1128 to **X 1083**: rake 51° → **46°** from horizontal. **(b)** Curve it in side view, convex forward, **R 700 mm**. **(c)** Widen the top from 290 to **340 mm**, with the outer 25 mm each side wrapped back 20°. **(d)** Give it a **±30 mm** height adjustment, and a **10 mm** rear-facing lip on the top edge to lift the jet above the helmet. Re-check the 30 mm hand-at-lock clearance to the wider screen. | 4–8 N on the screen, about 2–3%; less helmet buffeting | screen patch < 28 N (today 34 N); helmet patch not higher |
| 4 | **Smaller, rounded mirror heads** | `Mirror_body`: 140 × 82 mm, flat back → **120 × 70 mm**, with a convex back (crown 20 mm, edge radius **R 25**). Keep the stalk end at (842, ±330, 1200 + 40 lift). Or mount the mirrors on the hand guards (#5) at Y ±330, Z ≈ 1230. Check the rear field of view (FMVSS 111 / ECE R81 area) before shrinking. | 3–4 N, about 1.5% | mirrors patch < 7 N (today 10 N) |
| 5 | **Add hand guards** (not in the CAD today) | 2.5 mm shells from the bar end (Y ±416) to the lever perch (Y ±262). Front face at X 1000–1015, Z 1085–1215, raked back 15°, open at the bottom. Mount at the bar end and the perch clamp. Run the bars-at-lock check against the screen and fairing (30 mm). | Drag about neutral (±1%): they shelter the hands and forearms but add their own area. The gain is weather, cold hands and fatigue. | torso_arms patch ≤ 20 N with the guards included |
| 6 | **Tail: small clean-ups** | Square off the last 20 mm of the tail tip (X −190…−170) so the flow leaves at a sharp edge, with no R12 roll-under. Close the gap between `Tail_undertray` and `Rear_hugger`. Keep the plate vertical (legal). | 2–4 N, about 1%. Low priority: this zone is mesh-sensitive and sits in the rider's wake. | seat_tail patch |

**Changes 1–3 together:** about 22–35 N. On the fine-mesh total that is 8–12% after allowing for overlap.
- It would give **CdA about 0.34–0.355 with the smooth rider, and about 0.38–0.39 with a real rider.**
- That is 200–206 miles at 70 mph with a real rider, or about 216 miles in the CFD.
- That beats adding 2.5 kWh of cells, which would cost money and add about 10 kg.

## What this does not prove

- **The absolute number.** Steady RANS with wall functions predicts the drag of bluff bodies like motorcycles to about ±10–15%. It is better at ranking two shapes than at absolute values. A wind tunnel or coast-down test of a prototype is still needed.
- **The rider.**
  - He is a smooth buck with no clothing flap, no real helmet shape and no gloves.
  - Only one rider size and posture was run: 50th-percentile man, upright.
  - The comfort study's 5th-percentile rider sits in the screen jet's edge. That is not simulated.
- **Cooling.** The radiators and cooling paths are solid blocks with no pressure-loss model. The internal-flow drag (26 N) is the open shell, not real cooling flow.
- **Wheels.** The spokes are solid rotating walls; there is no transient spoke pumping.
- **Mesh convergence.**
  - Three meshes do not agree to 2%. The total moved −6.9% on the last refinement, almost all of it in the wake: the rider's back, the tail and the rear wheel.
  - The bike-body forces are converged to 2.6%.
  - The absolute CdA is a band (0.38–0.41), not a point.
  - The yaw cases were run on the medium mesh only.
  - There are no prism layers, and y+ is below 30 on 20–42% of the sheltered areas.
- **Crosswind.** Only ±10° steady yaw was run. There are no gusts, no unsteady wake and no steering torque. The moments go to the dynamics study, which must judge stability.
- **The body is moving.** The body panels are being re-surfaced in parallel. This study is the model saved at 09:54 on Nov 12. Re-run the one command on the new body before trusting the CAD change requests' gains.
- **The range** uses the repo's simple steady-speed energy model (flat road, no wind, 90% efficiency, 300 W aux). It is not a measured or advertised range.
