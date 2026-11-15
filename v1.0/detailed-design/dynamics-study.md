# Bavuso V1.0: vehicle dynamics study

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5). Finished November 13, 2026, after the supplier tyre audit.

- **Scripts:** `detailed-design/tools/dyn-*.py`.
- **Raw outputs and plots:** `detailed-design/dynamics/`.
- **How to run:** run every script from `v1.0` with `../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe`.

## The plain answer

**The bike's geometry is right, and braking, cornering torque, suspension and wheelie behaviour all work. Two things need changes before release: steering wobble and lean clearance.**

1. **Wobble (the fast 5–9 Hz shake of the bars) is the one real dynamics risk.** Here is what the model predicts, with no rider hands on the bars:
   - **Rigid frame and fork:** wobble is stable up to about 150 km/h. Above that it is mildly unstable, which is the textbook result.
   - **Fork and frame twist modelled** (every real bike twists): wobble becomes **unstable between about 20 and 120–150 km/h**. The worst damping ratio is −0.13 solo and −0.19 two-up, at 40–60 km/h.

   A plain steering damper fixes the low-speed problem, but only at about 20 Nm·s/rad solo and about 25 two-up. Left that stiff at 200 km/h, the same damper drains the high-speed weave damping to about zero.

   **The optimum is a speed-scheduled (semi-active) steering damper:** about 22 Nm·s/rad below 90 km/h, fading to 5 Nm·s/rad above 140 km/h. This is the Honda HESD / Öhlins EC approach. Solo, it makes every mode stable from 20 to 200 km/h, with the weakest margin at ζ = 0.03. Two-up it is still neutral (ζ ≈ 0) at 50–130 km/h. Two-up therefore also needs either about 28 Nm·s/rad at low speed or a laterally stiffer fork, so the damper must be specified with headroom.

   The rider's hands add damping that this model leaves out, so these are worst-case (hands-off) numbers. It is still a release item.

2. **Lean clearance is short by about 3°.** The folding pegs touch first, at 46.6° solo in a loaded steady turn (50.5° parked upright). That is fine. But the **lower outer corners of the battery covers and motor side covers touch only 0.4° later (47.0°)**. Two-up, they touch at the same angle as the pegs (45.1°). Grip on dry tarmac allows about 46° of lean, so hard structure could reach the road. **Fix:** a 33 × 36 mm chamfer on the lower outer edge, plus a small one on the pack-case corner. That moves hard-part contact to ≥50° solo and ≥48° two-up.

3. **Brakes pass with margin, with two hardware changes:**
   - **Front:** twin 320 mm discs, radial 4-piston calipers, **18 mm** radial master (the CAD has 19 mm).
   - **Rear:** grow the disc from 240 × 5 to **267 × 6 mm**. The 240 mm disc reaches about 506 °C in the UN R78 rear heat-fade test.

   With these, the bike stops from **100–0 km/h in about 44 m** (ABS, dry, μ 1.05). That is half the R78 limit for split brake systems. The front discs peak at **340 °C after ten 130–0 km/h stops** two-up with no regen, against a working limit of about 450 °C.

4. **Suspension works with the specified parts:**
   - **Rear:** the 109 N/mm spring checks out: 1.66 Hz solo, 57 mm sag two-up with the 20 mm adjuster.
   - **Front (new specification):** 8.0 N/mm per leg, a 180 mm air column (set by oil level), and 33 mm of preload. That gives 1.80 Hz, 51 mm sag and 19 mm of fork left under a 0.94 g two-up stop.
   - **Wheelie and squat:**
     - Solo, full motor torque does not lift the front: 0.89 g against a 1.15 g limit.
     - Two-up it is close: 0.69 g against 0.79 g. The front is down to about 5% of the weight, so wheelie and launch control are required.
     - Anti-squat of 125% lifts the rear about 18–20 mm under full power. That is acceptable.

**The model was checked before it was trusted.** Its rigid-body core reproduces the Meijaard (2007) benchmark bicycle exactly:
- weave speed 4.2924 against 4.2924 m/s;
- capsize speed 6.0249 against 6.0243 m/s;
- eigenvalues within 0.0006 s⁻¹ at 2–8 m/s.

## Inputs and assumptions

| Item | Value used | Source |
|---|---|---|
| Masses and CoG | Solo: 372 kg, CoG 734 mm ahead of the rear axle and 640 mm high. Two-up (2 × 85 kg riders + 30 kg luggage): 487 kg, CoG 581 / 736 mm | `mass-rollup.csv` (287 kg bike); rider positions as in `tools/rear-kinematics.py` |
| Inertias | Each part's own inertia comes from its CAD solid, scaled to the roll-up mass (243 kg of parts). The remaining 44 kg are point masses, and riders are boxes. | `dyn-cad-extract.py`, `dyn-massprops.py` |
| Bodies | Rear frame with rider: 328 kg, Ixx 37.6, Izz 24.7, Ixz 9.2 kg·m². Steered body (fork, clamps, bars, TFT, mirrors, calipers): 20.4 kg. Front wheel: 10.8 kg, spin inertia 0.53 kg·m². Rear wheel: 12.6 kg, spin inertia 0.56 kg·m². | `dynamics/mass-properties.json` |
| Steering inertia about the steering axis | **0.94 kg·m²**; 0.82 with the TFT and mirrors moved to the fairing | `dyn-stability.py` |
| Motor rotor | 0.0124 kg·m², spinning 7.8× wheel speed in reverse (gear stage). It acts like **7.1 kg of extra mass in braking** and gives a small counter-gyro. | estimate; `drive-study.md` ratio |
| Geometry | Caster 25°, fork offset 36.1 mm, steering-axis point X1206.954 / Z840. Supplier-audit tyres: 120/70R19 at 663 mm OD (R 331.5), 170/60R17 at 650 mm OD (R 325). With these, **trail is 114.7 mm and wheelbase 1483.9 mm**. | `build-adventure.py`; orchestrator note of Nov 13 |
| Tyres (normalised per unit load) | **Front:** cornering stiffness 13/rad, camber 0.90/rad, pneumatic trail 25 mm, relaxation length 0.20 m, crown radius 60 mm. **Rear:** 11/rad, 0.85/rad, 30 mm, 0.25 m, 85 mm. Each was swept ±30–50%. | Cossalter, *Motorcycle Dynamics* 2nd ed. ch. 2 (typical radial ranges 11–18/rad, camber 0.8–1.0/rad); Sharp-Evangelou-Limebeer 2004 (Magic Formula motorcycle tyre sets); relaxation 0.1–0.3 m measured by Taraborrelli (Univ. Padova thesis, Fig. 36). I could not extract the exact SEL table values, so these are mid-range picks for a road-biased adventure radial. |
| Fork lateral stiffness | 30 kN·m/rad (lumped model), 25 kN·m/rad (fork-only model). Swept 15–45. | Taraborrelli thesis tables 10 and 13: enduro fork 28 bending / 15 twist; sport fork 35 / 22 kN·m/rad |
| **Frame torsional stiffness (ASSUMED)** | **60 kN·m/rad** (head to pivot), in series with the fork, giving a 20 kN·m/rad lumped twist at the steering head. Swept 20–300 and rigid. | Taraborrelli Table 3: measured frames 51–129 kN·m/rad. **The FEA agent's value should replace this.** |
| Aero load transfer | 80 N moved from front to rear at 100 km/h, scaling with v² (320 N at 200 km/h) | `aero-baseline-report.md` |
| Rider | Rigidly attached, hands off the bars (worst case for wobble) | modelling choice |

## 1. Linear stability: capsize, weave and wobble

### Model

The model is Sharp-1971 / Sharp-Evangelou-Limebeer-2004 type (`dyn-model.py`):
- **Bodies:** rear frame, steered frame, two spinning wheels (gyroscopic), and the counter-rotating motor rotor.
- **Degrees of freedom:** lateral position, yaw, roll, steer, plus a twist.
- **Twist:** lumped steering-head twist (SEL style) or fork-only bending.
- **Tyres:** forces with toroidal crowns, slip and camber side force, aligning and twisting moments, and first-order relaxation.
- **Derivation:** the equations come from the exact second-order Lagrangian (sympy), so they are exact linearisations.
- **Pitch and heave:** frozen, with the ground reactions as constant forces at the contact points. This gives the same linear stiffness as the constrained system (argument in the script header).

### Verification

| Check | Result |
|---|---|
| **Meijaard et al. 2007 benchmark bicycle** (published weave speed 4.292383 m/s, capsize speed 6.024262 m/s). Our tyres are made very stiff and lag-free, with zero crown, so they enforce no slip. | Weave **4.2924** m/s (+0.00%). Capsize **6.0249** m/s (+0.01%). Eigenvalues at 5 m/s: ours −14.0785, −0.7753 ± 4.4649i, −0.3229; benchmark −14.0784, −0.7753 ± 4.4649i, −0.3229. Maximum eigenvalue error over 2–8 m/s: 0.0006 s⁻¹. **Pass** (`dynamics/validation-meijaard.json`). |
| Benchmark reference matrices through our eigen/bisection code | 4.292383 / 6.024262 m/s. **Pass**. |
| Fork-bending model with infinite stiffness against the rigid model | Identical numbers. **Pass**. |
| Tyre and flexibility side, qualitative checks against Sharp 1971, Spierings 1981 and Cossalter | <ul><li>Rigid-frame wobble at 8–10 Hz, stable at low speed and destabilising at high speed.</li><li>Weave at 3–4 Hz at high speed, losing damping with speed.</li><li>A steering damper helps wobble and hurts high-speed weave.</li><li>Zero relaxation length removes low-speed wobble.</li><li>Lateral flexibility destabilises low-speed wobble.</li></ul>All reproduced. **I did not reproduce a published motorcycle eigenvalue set number for number.** |
| Steady-turn solver | Residual below 2e-10, invariance error below 7e-11 |

### Results (no steering damper unless stated)

Damping ratio ζ is how fast an oscillation dies away. Below 0 means it grows. I use **ζ ≥ 0.05 as the target** for weave and wobble across 20–200 km/h. Weave and capsize below about 25–30 km/h are always unstable on every motorcycle, and the rider handles them. Plots:
- `dynamics/stability-baseline.png`
- `dynamics/stability-flex-models.png`
- `dynamics/stability-damper.png`
- `dynamics/stability-semiactive.png`
- `dynamics/stability-frame-stiffness.png`

| Case | Weave: weakest ζ (where, frequency) | Wobble: weakest ζ (where, frequency) | Wobble unstable range |
|---|---|---|---|
| Solo, rigid frame and fork | +0.12 (200 km/h, 3.9 Hz) | −0.054 (200, 8.0 Hz) | 148–200 km/h |
| Solo, lumped twist 20 kN·m/rad (baseline) | +0.053 (200, 3.7 Hz) | **−0.131** (45, 5.6 Hz) | 20–120 |
| Solo, fork bending 25 kN·m/rad, frame rigid | +0.090 (200) | −0.135 (58, 6.8 Hz) | 20–145 |
| Two-up loaded, rigid | +0.12 (200, 3.5 Hz) | −0.036 (200, 8.0 Hz) | 128–200 |
| Two-up, lumped twist | +0.084 (200, 3.2 Hz) | **−0.187** (35, 4.9 Hz) | 20–125 |
| Two-up, fork bending 25 | +0.109 (200) | −0.193 (45, 6.1 Hz) | 20–152 |
| Capsize (all cases) | Real root of +0.42 to +0.48 s⁻¹ at 200 km/h (doubling time about 1.5 s): a slow lean-over the rider corrects without noticing. Normal. | | |

#### Sensitivity, solo, lumped twist

**Frame stiffness, with the fork at 30 kN·m/rad in series:**

| Frame stiffness (kN·m/rad) | Wobble weakest ζ |
|---|---|
| 20 | −0.148 |
| 40 | −0.138 |
| **60 (assumed)** | **−0.131** |
| 120 | −0.123 |
| 300 | −0.116 |

The fork dominates: a stiffer fork, 45 instead of 30 kN·m/rad, improves wobble ζ to −0.120 at frame 60 and to −0.105 at frame 120. **So the FEA frame number matters less than fork lateral stiffness.**

**Other levers:**

| Lever | Effect |
|---|---|
| Fork-only model, fork stiffness 15 / 25 / 40 kN·m/rad | Wobble ζ −0.162 / −0.135 / −0.098 |
| Trail 93 / 104 / **115** / 126 mm (by fork offset) | <ul><li>Wobble barely moves: −0.119 / −0.126 / −0.131 / −0.136.</li><li>High-speed weave improves with trail: ζ 0.029 / 0.042 / 0.053 / 0.063 at 200 km/h.</li><li>**Keep the current trail.** Do not cut it, because shorter trail hurts weave.</li></ul> |
| TFT and mirrors moved to the fairing (steering inertia −13%) | Negligible on its own (wobble −0.136 against −0.131). Not worth a styling change for dynamics alone. |
| Tyres | <ul><li>Cornering stiffness ×0.7: weave at 200 km/h drops to 0.033.</li><li>Relaxation length ×1.5: wobble worse (−0.144) and weave at 200 km/h at 0.032.</li><li>Camber stiffness: little effect on wobble.</li><li>Tyre choice is a real lever on weave, so **tyre fitment needs a stability sign-off.**</li></ul> |

#### Steering damping (solo / two-up, lumped twist)

| Total steering damping (Nm·s/rad) | Wobble weakest ζ | Weave ζ at 200 km/h |
|---|---|---|
| 0 | −0.131 / −0.187 | 0.053 / 0.084 |
| 6 | −0.084 / −0.137 | 0.035 / 0.076 |
| 10 | −0.055 / −0.107 | 0.025 / 0.071 |
| 15 | −0.022 / −0.071 | 0.013 / 0.065 |
| 20 | +0.009 / −0.038 | **0.003** / 0.060 |
| 25 | +0.035 / −0.007 | **−0.006** / 0.06 |
| **Semi-active, 22 below 90 km/h falling to 5 above 140 km/h** | **solo: wobble ≥ +0.020; with fork bending model ≥ +0.029** | **solo: weave ≥ 0.038 (lumped) / 0.072 (fork model)** |
| Semi-active, two-up | wobble about −0.02 to 0.00 at 50–130 km/h | 0.10 |

**What it means.** A fixed damper cannot fix both modes. One stiff enough for low-speed wobble (about 20 Nm·s/rad) leaves high-speed weave with almost no damping. A speed-scheduled damper fixes solo completely. Two-up it reaches neutral, so it needs more authority (about 28 at low speed) or a laterally stiffer fork (≥40 kN·m/rad).

The rider's arms add perhaps 3–10 Nm·s/rad of damping in real riding, which I have not modelled. So the hands-off two-up case is the one to confirm in a hands-off test.

### Steering torque in steady cornering (0.3 g lateral, about 19° of lean; `dyn-steer-torque.py`)

| Speed (km/h) | 30 | 50 | 70 | 100 | 130 | 160 |
|---|---|---|---|---|---|---|
| Solo (Nm, + = rider holds the bar into the turn) | −1.9 | +1.6 | +3.2 | +5.0 | +7.2 | +9.7 |
| Two-up | −1.4 | +2.4 | +4.1 | +6.0 | +8.2 | +10.8 |

These are light and progressive, in the normal range of a few newton-metres. The small negative value at walking pace means the bike tips in slightly on its own. The torque rising with speed is mostly gyroscopic, from the heavy 19-inch wheel and tyre. **Pass.** The model is linear, so numbers at full lean are not covered.

## 2. Braking (`dyn-braking.py`)

| Item | Solo | Two-up laden |
|---|---|---|
| Rear-wheel lift-off ("stoppie") deceleration | 1.17 g | 1.23 g (CoG further back) |
| Tyre limit (dry, μ 1.05, road-biased adventure radial) | 1.05 g | 1.05 g |
| Mean deceleration under ABS (90% of peak) | 0.94 g | 0.94 g |
| **100–0 km/h stopping distance** (includes 0.2 s brake build-up) | **44.4 m** | **44.4 m** |
| Front share of braking at that deceleration | 90% | 86% |

The tyre limits the stop before the rear lifts. ABS still needs **rear-lift mitigation** (IMU pitch-rate) on hard surfaces with stickier tyres (μ ≈ 1.2 gives about 1.1 g).

### Brake hardware and forces

The hardware is listed under CAD change requests. Effective disc radius is 142 mm. The pads are sintered at μ 0.45.

| Case | Line pressure | Lever / pedal force | Limit |
|---|---|---|---|
| Front lever only, solo, 0.94 g, 19 mm master (as in CAD) | 27.8 bar | 154 N | 200 N (UN R78 hand) |
| Front lever only, two-up, 0.94 g, 19 mm master | 36.4 bar | **201 N** (no margin) | 200 N |
| Same with **18 mm** master | 36.4 bar | about 181 N | 200 N |
| R78 front-only test, laden (4.4 m/s²) | 17.3 bar | 96 N | 200 N |
| R78 rear-only test, laden (2.9 m/s², needs rear μ 0.64) | 57 bar (12.7 mm master, pedal ratio 4) | 191 N | 350 N (foot) |

### Against the UN R78 Annex 3 limits for L3

FMVSS 122 was harmonised in 2012 with UN GTR No. 3, which uses the same test structure. I did not re-read the FMVSS text itself.

| Test | Limit | Bavuso | Pass? |
|---|---|---|---|
| Front-only dry stop from 60 km/h | S ≤ 0.1V + 0.0087V² = 37.3 m (MFDD ≥ 4.4 m/s²) | Front alone reaches far above 4.4 m/s² at 96 N | Pass |
| Rear-only dry stop | S ≤ 0.1V + 0.0133V² = 53.9 m (≥ 2.9 m/s²) | 2.9 m/s² at 191 N pedal | Pass |
| Split system, laden | S ≤ 0.1V + 0.0076V² = 33.4 m at 60 km/h / 86 m at 100 km/h | 16.6 m / 44.4 m | Pass, about 2× margin |
| Heat fade, front only (10 stops, 100 km/h, 3.25 m/s², 1 km gaps, laden) | Hot stop S2 ≤ 1.67 S1 − 0.067V | Disc peaks at 287 °C (pads still well inside the sintered range) | Pass (inferred from temperature; the hot-stop distance itself is not simulated) |
| Heat fade, rear only (10 stops, 80 km/h) | same | **240 × 5 mm disc: 506 °C (fail risk). 267 × 6 mm: 443 °C.** | **Change the rear disc** |

### Thermal check: ten stops from 130 km/h at 0.6 g, 1 km apart

The disc is modelled as one lump, with Limpert's convection correlations and radiation (`dynamics/braking-thermal.png`).

| Case | Front disc peak | Limit (stainless disc / sintered pad) | Margin |
|---|---|---|---|
| Two-up, no regen (full pack), 320 mm | **340 °C** | about 450 °C | 110 K |
| Two-up, 330 mm discs | 331 °C | | 119 K |
| Solo, no regen | 294 °C | | 156 K |
| Two-up, 20% regen on the rear | 280 °C | | 170 K |

**Energy check:**
- Energy per front disc on the first stop: 104 kJ.
- An adiabatic (no cooling) estimate gives a 175 K rise; the simulation gives 164 K. The difference is cooling during the 6 s stop. **Consistent.**
- The rotating parts store 17.2 kg-equivalent of energy, 7.1 kg of it the motor rotor. That is included.

320 mm discs are enough; 330 mm buys only 9 K. **Keep 320.**

### ABS and regen blending

1. **Bosch MSC-class cornering ABS** with rear-lift mitigation and (recommended) **partial integral braking**: the hand lever also applies some rear brake. That alone takes the two-up lever force from 201 N to about 175 N.
2. **Regen only on the rear.** Cap it at the rear tyre's available force from the IMU's dynamic load estimate, at about 0.15–0.2 g. Regen falls to zero when the pack is full or cold, so the friction brakes are sized with no regen (as above).
3. **ABS has priority.** The motor torque command must drop to zero, or follow ABS slip control, within one ABS cycle (about 10 ms). Motor torque responds in about 1 ms, so this is a software task, not a hardware one.
4. **Stop lamp:** turn it on when regen deceleration is high. The rule for cars (R13-H) is on above 1.3 m/s² and never below 0.7 m/s². **Confirm the current R78 / FMVSS 122 wording on regenerative braking.** The R78 version I read (2015) had none.
5. Engine-braking-style drag regen (throttle off) should stay ≤ 0.1 g on loose surfaces. It needs an off-road mode.

## 3. Steady cornering: lean clearance (`dyn-lean.py`, `dyn-lean-chamfer.py`)

**Method:**
- The bike rolls about the line through the tyre crown centres (60 / 85 mm crowns).
- Every vertex of every CAD part is tested.
- **Loaded** means a steady turn: at 45° the suspension carries 1.41 g and sits 30 mm (front) and 38 mm (rear) lower, tyres included. That case is the one that matters.
- The CAD still has the old tyre radii. The supplier tyres would lift the bike about 6–13 mm and gain about 1° of lean. **That gain is not counted.**

| First parts to touch | Solo, upright geometry | **Solo, loaded turn** | Two-up, loaded turn |
|---|---|---|---|
| Peg rubbers (folding, \|Y\| 305, Z 328) | 50.5° | **46.6°** | 45.0° |
| Battery-cover lower outer corners (\|Y\| 203, Z 223) | 52.6° | **47.0°** | **45.1°** |
| Motor side covers (\|Y\| 203, Z 223) | 53.2° | **47.0°** | **45.1°** |
| Belly side panels (\|Y\| 209, Z 237) | 53.5° | 48.0° | 46.1° |

- **Requirement:** pegs first, at about 45–50°. Hard structure at least 3° later, and beyond the grip limit of about 46° (tan⁻¹ 1.05).
- **Verdict:** pegs **pass**. Hard parts **fail**: there is only 0.4° (solo) or 0° (two-up) behind the pegs.
- **Fix, sized by the chamfer script:** a target of 50° solo and 48° two-up needs the outer lower edge at Z 223 no wider than \|Y\| 179 mm, and at \|Y\| 212 no lower than Z 259. That is a **33 mm wide × 36 mm high chamfer (about a 48° face)**. The pack case corner (\|Y\| 194, Z 238) sits about 1 mm outside the 48° line, so it needs a ≥ 10 × 45° chamfer or an R15 radius. The cells (outer lane at \|Y\| 188, Z 243) clear without change.
- **Side stand:** not in the CAD yet (only its mass is). When it is added, folded it must stay inside the same 50° line.

## 4. Load transfer, wheelie and squat (`dyn-suspension.py`)

Full motor torque at the wheel is 150 Nm × 7.8 × 0.93 / 0.318 m = **3,568 N**.

| | Solo | Two-up |
|---|---|---|
| Acceleration at full torque (rotating mass included) | 0.89 g | 0.69 g |
| Wheelie threshold (front unloads), g × CoG-x / CoG-h | 1.15 g | **0.79 g** |
| Front load left at full torque | 401 N (11%) | **236 N (5%)** |
| Rear tyre μ needed | 1.05 (traction-limited on most surfaces) | 0.75 |
| Rear rises under power (anti-squat 125%) | +17.5 mm | +20.3 mm |
| Front extends | 64 mm (tops out: static sag is 51 mm) | 74 mm (tops out) |

- **Solo:** passes, with a 22% margin to wheelie, and traction-limited. The 1.0 g launch-control cap in `drive-study.md` is consistent with this.
- **Two-up:** the margin is only 13%, and the front is nearly weightless with the fork topped out. Steering goes light and trail grows. **IMU wheelie control is required, and the two-up launch should be capped at about 0.6 g.**
- **Squat:** the rear jacking of 18–20 mm is acceptable and keeps the bike level. A full-extension top-out spring in the fork is advisable.

## 5. Suspension (`dyn-suspension.py`)

### Rear (check of `rear-suspension.md`)

The static loads come from this study's mass properties.

| Item | Value | Target | Status |
|---|---|---|---|
| Spring / leverage / wheel rate | 109 N/mm / 2.33 / 20.1 N/mm | | |
| Ride frequency, solo (tyre at 210 N/mm in series) | **1.66 Hz** | 1.6–1.9 Hz adventure | Pass |
| Two-up ride frequency | 1.29 Hz | ≥ 1.2 Hz | Pass (soft) |
| Solo preload for 51 mm sag (30%) | 13.6 mm at the spring | ≤ 20 mm | Pass |
| Two-up sag with +20 mm adjuster | 57 mm (34%) | ≤ 35% | Pass |
| Wheel hop frequency | 17.4 Hz | > 12 Hz | Pass |
| Damping at the shock (low speed), solo | compression about 5.0 kN·s/m (ζ 0.25), rebound about 10 kN·s/m (ζ 0.5) | | Specification for the semi-active shock |
| Two-up | 6.4 / 12.8 kN·s/m | | |

### Front (new; not sized before)

I swept spring rate (5–14 N/mm per leg), air column (110–260 mm) and preload (0–35 mm). The optimum matches the rear frequency as closely as possible while meeting all of these:
- 30% sag;
- preload ≤ 35 mm;
- two-up sag ≤ 40%;
- ≥ 15 mm left under a 0.94 g two-up stop;
- ≥ 40 mm left at 45° of lean.

| Item | Value |
|---|---|
| **Spring** | **8.0 N/mm per leg** (0.82 kgf/mm), both legs |
| **Air column** (oil level), equivalent | **180 mm** per leg; about 40 mm effective displacement diameter assumed |
| **Preload** | 33 mm (built-in spacer plus adjuster). This is at the high end, so a 9.0 N/mm spring is the alternative if the supplier wants ≤ 25 mm. |
| Sag solo / two-up | 51 mm (30%) / 54 mm (32%) |
| Ride frequency (tyre 175 N/mm in series) | 1.80 Hz (rear is 1.66) |
| Travel used: 0.94 g stop solo / two-up / 45° steady lean | 139 / 151 / 80 mm of 170 |
| Coil alone, without the air column, in the solo stop | would need 234 mm, so it would bottom. **The air-spring progression is essential.** |
| Damping (low speed, axial, whole fork) | compression about 830 N·s/m (ζ 0.25), rebound about 1,650 N·s/m (ζ 0.5) |
| Wheel hop frequency | 17.2 Hz |

## Verdict table

| Item | Value | Required | Margin | Status |
|---|---|---|---|---|
| Model check against the Meijaard benchmark | 4.2924 / 6.0249 m/s | 4.2924 / 6.0243 m/s | < 0.01% | **Pass** |
| Weave damping at 200 km/h, no damper, solo / two-up | ζ 0.053 / 0.084 (lumped twist); 0.090 / 0.109 (fork bending) | ζ ≥ 0.05 | +0.003 to +0.06 | **Pass (thin solo)** |
| Wobble, no damper, flexible fork and frame | ζ −0.13 solo / −0.19 two-up at 35–60 km/h | ζ ≥ 0.05 | −0.18 / −0.24 | **Fail** |
| Wobble with a semi-active damper (22 to 5 Nm·s/rad), solo | ζ ≥ +0.020 (lumped) / +0.029 (fork) | ≥ 0.05 | −0.02 to −0.03 | **Open** (positive, below target; rider arms not counted) |
| Wobble with semi-active damper, two-up | ζ about −0.02 to 0.00 | ≥ 0.05 | −0.07 | **Open**: needs a damper with about 28 Nm·s/rad at low speed, or fork ≥ 40 kN·m/rad |
| High-speed weave with the semi-active damper | ζ 0.038 / 0.072 solo, 0.10 two-up | ≥ 0.05 | −0.012 to +0.05 | **Open / pass** |
| Capsize | +0.42–0.48 s⁻¹ at 200 km/h | slow (doubling > 1 s) | 1.5 s | **Pass** |
| Steady-turn steering torque, 0.3 g | −1.9 to +10.8 Nm | ≤ about 15 Nm, no strong reversal | ≥ 4 Nm | **Pass** |
| 100–0 km/h stopping distance (ABS, dry) | 44.4 m | R78 split ≤ 86 m | 49% | **Pass** |
| Rear-lift (stoppie) limit | 1.17 g solo / 1.23 g two-up | above the tyre limit 1.05 g | 11–17% | **Pass**, rear-lift mitigation required |
| Front lever force, two-up 0.94 g front-only | 201 N (19 mm master) to 181 N (18 mm) | ≤ 200 N | −1 → +19 N | **Pass with the 18 mm master** |
| R78 front / rear / split dry stops | met at 96 N / 191 N pedal / 16.6 m | 200 N / 350 N / 33.4 m | large | **Pass** |
| Front disc temperature, ten 130–0 stops, two-up, no regen | 340 °C | ≤ about 450 °C | 110 K | **Pass** |
| Rear disc, R78 heat fade | 506 °C (240×5) / 443 °C (267×6) | ≤ about 450 °C | −56 / +7 K | **Fail → pass with the 267×6 disc** |
| Lean clearance, pegs (loaded) | 46.6° solo / 45.0° two-up | 45–50° | +1.6 / 0 | **Pass** |
| Lean clearance, hard parts (loaded) | 47.0° solo / 45.1° two-up | ≥ peg + 3° and > 46° grip lean | −2.6 / −2.9° | **Fail → pass with the chamfer** |
| Wheelie at full torque | 0.89 g against 1.15 g solo; 0.69 against 0.79 two-up | no wheelie without control | 22% / 13% | **Pass solo / open two-up** (wheelie control required) |
| Squat under power | rear +18 to +20 mm (jacks) | between −10 and +25 mm | ok | **Pass** |
| Rear spring 109 N/mm | 1.66 Hz, 51 / 57 mm sag | 1.6–1.9 Hz, ≤ 35% sag | ok | **Pass** |
| Front fork springing | 8.0 N/mm/leg + 180 mm air + 33 mm preload: 1.80 Hz, 19 mm reserve at 0.94 g two-up | 30% sag, ≥ 15 mm reserve | +4 mm | **Pass (new specification)** |

## CAD change requests

1. **Steering geometry: no change.**
   - Keep caster 25° and fork offset 36.1 mm.
   - With the supplier 120/70R19 (663 mm OD), trail becomes **114.7 mm** and wheelbase **1483.9 mm**. Accept both.
   - The sweep shows shorter trail costs high-speed weave and barely helps wobble.
   - Separately: the larger tyre (+6.2 mm radius) eats into the lower-clamp-to-tyre bump clearance. The CAD agent should re-check it.
2. **Steering damper provision (new):**
   - A **semi-active rotary steering damper** on the steering axis.
   - Peak damping **≥ 28 Nm·s/rad** below 90 km/h, scheduled down to about 5 Nm·s/rad above 140 km/h, using speed from the ABS/VCU.
   - Reserve an envelope of **80 × 60 × 45 mm on top of the upper triple clamp (X1131, Z1083 model), centred on the steering axis**. It needs a reaction tab on the head tube top (Head_tube Z1034) and working range over ±35° of lock.
   - Alternative: a linear damper, 75 mm stroke, from a frame tab on `Upper_rail_2` to the lower clamp. Either way it needs a 4-pin connector on the bar harness.
3. **Fork specification** (supplier):
   - 48 mm USD, 170 mm travel.
   - Spring 8.0 N/mm per leg (or 9.0 with less preload).
   - Air column 180 mm equivalent; preload 33 mm.
   - **Lateral twist stiffness ≥ 40 kN·m/rad**, measured as in Taraborrelli, about the lower clamp. Use a 25 mm hollow axle with pinch clamps, a lower clamp at least 40 mm tall, and as short a clamp spacing as the 170 mm travel allows.
   - Hydraulic bottoming control, and a top-out spring.
4. **Front brake:**
   - Keep twin **320 × 5 mm** floating stainless discs (`discR=160`, thickness 5).
   - Radial **4-piston monobloc**, 2 × 32 mm pistons per side, 108 mm mount (as in CAD).
   - **Radial master 18 mm bore** (CAD note says 19 mm), lever ratio about 5.4.
   - Sintered pads, μ about 0.45.
5. **Rear brake:**
   - Disc **240 × 5 to 267 × 6 mm**: `discR` 120 → **133.5** for the rear, thickness 6.
   - Floating single-piston 34 mm caliper (or 2 × 25 mm), with its bracket moved out by 13.5 mm radially.
   - Master **12.7 mm** bore, pedal ratio about 4.
   - Check that the caliper stays inside the 17-inch rim. Outer radius about 149 mm against the 216 mm bead seat: fine.
6. **Lean clearance chamfer:**
   - On `Lower_body_battery_covers_STUDY`, `Belly_side_panel_*` and `Motor_side_covers_STUDY`, cut the **lower outer edge along the line (\|Y\| 179, Z 223) to (\|Y\| 212, Z 259)**, saved-model coordinates, over X 580–1110.
   - **Pack case** (`Pack_case_structural_4mm_STUDY`) lower outer edge: a ≥ 10 × 45° chamfer or R15 at (\|Y\| 194, Z 238).
   - The pegs can stay at \|Y\| 305 / Z 328 with feelers.
7. **Side stand:** add it to the CAD. Folded, it must sit inside the 50° line: \|Y\| ≤ 179 + 0.9 (Z − 223) mm in saved-model coordinates near X 560.
8. **ABS module:** Bosch MSC-class cornering ABS with rear-lift mitigation, partial integral front-to-rear, a regen-blending interface, and a 6-axis IMU. This keeps the 1.6 kg allowance in the roll-up.

## What this does not prove

- **No rider model.** The rider is rigid and hands-off. Arms add steering inertia and damping, which usually help wobble. The wobble margins here are therefore worst case, but the *need* for a damper is not removed. **A hands-off test at 40–80 km/h, solo and two-up, is the deciding experiment.**
- **Frame flexibility.** The frame torsional stiffness is assumed at 60 kN·m/rad pending the FEA. The fork stiffness comes from published measurements of other forks. The two flexibility models (lumped head twist, fork-only bending) bound the answer but are not a validated flexible model. A two-axis model (frame torsion plus fork bending) with FEA stiffnesses is the next step. Swingarm lateral and torsional flexibility is not modelled, nor is rear-frame compliance at the pack joints.
- **Tyres.** Parameters are literature mid-range values, not measured adventure-tyre data. Relaxation length and cornering stiffness move weave damping by ±40%. No tyre damping or hysteresis, no Magic Formula load dependence and no large-camber nonlinearity are included.
- **Not a full Sharp/Limebeer benchmark.** The tyre side of the model was checked only qualitatively against published trends. The rigid-body side was checked number for number (Meijaard).
- **Linear and straight-running only.** No stability analysis in a turn (cornering weave is often worse), no braking-in-a-turn, no kickback over bumps, no aero side forces or lift.
- **Braking.** The calculations are hand calculations, with ABS efficiency assumed at 90% and no dynamic pitch or fork-dive geometry. The heat-fade "pass" is from disc temperature, not a simulated hot-stop distance. Caliper and fluid temperature (DOT 4 boiling) are not modelled. Pad μ against temperature is assumed constant.
- **Lean clearance.** It uses the current CAD (old tyre radii) and a steady-turn load factor. It ignores the rider's boot and bump compression in a corner. The side stand, pedal and peg-bracket details are not modelled.
- **Suspension.** Quasi-static only. No damping curves, no ride simulation over a road profile, no bump-stop curve. The air-spring area is assumed. Fork friction is ignored.
- **Mass properties.** They are only as good as the roll-up: ±8 kg overall, and 44 kg are point masses. The front-assembly mass (20.4 kg steered) is an estimate, and it drives wobble.

## Sources

- Meijaard, Papadopoulos, Ruina & Schwab, "Linearized dynamics equations for the balance and steer of a bicycle: a benchmark and review", *Proc. R. Soc. A* 463 (2007): https://doi.org/10.1098/rspa.2007.1857
- Sharp, "The stability and control of motorcycles", *J. Mech. Eng. Sci.* 13 (1971): https://doi.org/10.1243/JMES_JOUR_1971_013_051_02
- Sharp, Evangelou & Limebeer, "Advances in the modelling of motorcycle dynamics", *Multibody System Dynamics* 12 (2004): https://doi.org/10.1023/B:MUBO.0000049195.60868.A2 (Imperial repository: https://spiral.imperial.ac.uk/handle/10044/1/4326)
- Taraborrelli (supervisor A. Doria), PhD thesis, University of Padova: frame, fork and swingarm stiffness tables, and tyre relaxation length: https://www.research.unipd.it/retrieve/e14fb26f-a59c-3de1-e053-1705fe0ac030/Taraborrelli_tesi.pdf
- Spierings, "The effects of lateral front fork flexibility on the vibrational modes of straight-running single-track vehicles", *Vehicle System Dynamics* 10 (1981).
- UN Regulation No. 78 (braking, L-category), Annex 3, consolidated EU text: https://eur-lex.europa.eu/eli/reg/2015/78/oj
- FMVSS 122, 49 CFR 571.122 (harmonised with UN GTR No. 3 in 2012; text not re-read here): https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/subpart-B/section-571.122
- Cossalter, *Motorcycle Dynamics*, 2nd ed. (2006); Foale, *Motorcycle Handling and Chassis Design*; Limpert, *Brake Design and Safety*, 3rd ed. (disc convection correlations).
