# Bavuso V1 vehicle dynamics (rev D)

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Scripts (`program/tools/`, run each from `v1.0` with the FreeCAD python, in this order): `dynamics-v1-extract.py` (CAD shapes), `dynamics-v1-massprops.py`, `dynamics-v1-stability.py`, `dynamics-v1-damper.py`, `dynamics-v1-braking.py`, `dynamics-v1-lean.py`, `dynamics-v1-gust.py`, with the library `dynamics-v1-model.py` and the check script `dynamics-v1-validate.py`. Data and plots: `program/data/dynamics/` (logs in `run/`). The method and the model core are the Nov 12-13 study (`detailed-design/dynamics-study.md`), refitted to rev D and extended. Labels: **measured** = from the CAD, **supplier**, **calculated**, **estimate**.

## The plain answer

**Rev D handles well enough on paper, but it needs a steering damper that changes with speed. Without one, the handlebar wobble at 15 to 85 mph is unstable.** Everything else passes or is close.

1. **Wobble (the 7 to 8 Hz shake of the bars) is the one real stability problem.** With the frame, fork and swingarm flexing, hands off the bars and no damper, it is unstable from 15 to 82 mph with a rider (weakest damping ratio ζ = -0.11 at 35 mph) and to 85 mph with luggage (ζ = -0.15). Above 90 mph it is stable. Weave (the 3 Hz sway) is stable at every speed above 25 mph; its weakest point is 130 mph (ζ 0.07 rider, 0.04 with luggage).
2. **A fixed damper cannot fix both.** Enough damping for wobble (about 20 Nm·s/rad) pulls weave at 130 mph to zero or below. **A speed-scheduled (semi-active) damper does:** 25 Nm·s/rad up to 50 mph, falling to 3 Nm·s/rad by 95 mph. With it every mode is stable from 15 to 130 mph in all three load cases. The thinnest numbers are 0.039 (wobble) and 0.028 (weave) with luggage, so T8 ("damping positive in all modes") is met, but only with thin margin. The target I used elsewhere (ζ ≥ 0.05) is met by the rider-only case, not by the luggage case.
3. **Mass properties are consistent with the ledger.** The roll-up CG is 798 mm ahead of the rear axle and 535 mm high; my part-by-part CG is 798.5 and 535.5. With the rider the weight split is 49 / 51 (front / rear); with 25 kg of luggage it is 45 / 55.
4. **Braking is fine.** A 1.0 g stop takes 39.4 m from 60 mph and 63.8 m from 77 mph (counting 0.2 s of lever build-up). The front wheel lifts the rear at 1.14 g with the rider and 1.20 g loaded. The 0-60 launch (3.95 s, 0.70 g peak) leaves the front tyre carrying 37% of its static load, so there is no wheelie risk. The front discs reach 362 to 375 °C in a 125-to-0 mph stop; the working limit is about 450 °C.
5. **Lean clearance is limited by the belt-side pulley, not the pegs or covers.** Loaded in a steady turn, the pegs touch at 45.2 to 45.6° and every hard part on the swingarm side holds out to 52.8 to 53.4°. On the belt side the **rear pulley's outer flange touches at 47.5 to 47.7°**, only 2.1 to 2.4° after the pegs. My rule is 3°. **This needs a small CAD change (see below).**
6. **Gusts at 77 mph are manageable.** For a 10 m/s (22 mph) sidewind the rider leans about 9.7° into it and holds the bars with about 5 Nm (2 Nm with luggage). Hands off, an 8 m/s side gust moves the bike 0.36 to 0.39 m sideways in the first second, which is inside the time a rider needs to react. The side-force numbers are my assumption; aero will replace them.

## Verdict table

| Item | Result | Criterion | Status |
|---|---|---|---|
| Mass properties vs roll-up | CG 798.5 / 535.5 mm vs 798 / 535 | within 2 mm | **Pass** |
| Wobble, no damper (rider / rider + luggage) | ζ -0.112 at 35 mph / -0.147 at 32 mph, unstable 15-82 / 15-85 mph | ζ > 0 | **Fail without a damper** |
| Weave, no damper | ζ 0.074 / 0.037 at 130 mph (weakest) | ζ > 0 | Pass |
| Wobble and weave with scheduled damper (25, then 3 Nm·s/rad) | rider 0.071 / 0.060, luggage 0.039 / 0.028 (weakest) | ζ > 0 (T8); ζ ≥ 0.05 is my comfort target | **Pass (T8), thin** |
| Other modes (fork, frame, swingarm, below 100 Hz) | ζ ≥ 0.017, all stable | ζ > 0 | Pass (damping is an assumption) |
| Capsize | real root +0.50 1/s at 130 mph (doubling time 1.4 s) | slow, rider-correctable | Pass (normal) |
| Stop from 60 / 77 mph at 1.0 g | 39.4 / 63.8 m (36.7 / 60.4 m without build-up); ABS-realistic 0.945 g: 41.5 / 67.3 m | well inside the UN R78 split limit (86 m at 100 km/h; ours 42 m) | Pass |
| Stoppie limit | 1.14 g (rider), 1.20 g (luggage) | above 1.0 g | Pass (+14% / +20%) |
| Wheelie at the 0-60 3.95 s launch | 0.70 g peak vs 1.10 g limit (rider); 0.65 vs 0.99 g (luggage) | no wheelie | Pass (+58% / +53%) |
| Front disc, 125-0 mph, one stop at 0.9 g | 362 / 375 °C | ≤ 450 °C | Pass |
| Front disc, three stops at 0.6 g, 1 km apart | 444 / 460 °C | ≤ 450 °C | **Marginal** (luggage case 10 K over) |
| Rear disc 267 x 5, same three stops | 355 / 426 °C; R78 rear fade 312 °C | ≤ 450 °C | Pass |
| Lean, pegs (loaded) | 45.6° rider / 45.2° luggage | 45-50° | Pass |
| Lean, hard parts, swingarm (+Y) side | 53.4° / 52.8° (covers) | ≥ pegs + 3° and > 46.4° grip lean | Pass |
| Lean, hard parts, belt (-Y) side | 47.7° / 47.5° (pulley outer flange) | ≥ pegs + 3° = 48.6° / 48.2° | **Short by 0.9° / 0.7°; beyond grip lean by 1.2°** |
| Sidewind 10 m/s at 77 mph | roll 9.7° / 8.8°, steering torque 5.1 / 2.1 Nm | ≤ 10 Nm (my screen) | Pass, but depends on the assumed centre of pressure |

## 1. Mass properties (calculated from the CAD and the roll-up)

Source: `program/data/dynamics/mass-properties.json` and `.csv`. Each part keeps the rotational inertia of its CAD solid, scaled to its ledger mass (209 of 248 kg are shaped this way); the 39 kg of allowances (wiring, fasteners, fluids, and similar) are point masses. The mass roll-up changed from 246.4 to **247.9 kg** (thermostat, PTC heater and disc updates) while I worked; I used the 247.9 kg snapshot taken at 05:02 US Central (`run/mass-rollup-snapshot.csv`). The rider is 90 kg, 1,755 mm, built from the joint positions in `rider-fit.json` with standard segment masses (estimate). Luggage is a 25 kg box at X -100, Z 880 mm on the rack (**my assumption**; the rack plate is at X -129, Z 924). The CAD is the rider-on static position, which I use for all three cases (the rear preload adjuster is assumed to keep ride height).

| Quantity | Bike alone | Bike + 90 kg rider | + 25 kg luggage |
|---|---:|---:|---:|
| Mass, kg | 247.9 | 337.9 | 362.9 |
| CG ahead of rear axle, mm | 798.5 | 732.4 | 675.1 |
| CG height, mm | 535.5 | 666.8 | 681.5 |
| CG lateral offset, mm | 2.0 | 1.5 | 1.4 |
| Weight on front / rear | 53.6 / 46.4 % | 49.2 / 50.8 % | 45.3 / 54.7 % |
| Roll inertia Ixx, kg·m² | 14.4 | 42.9 | 44.9 |
| Pitch inertia Iyy, kg·m² | 42.6 | 72.8 | 90.7 |
| Yaw inertia Izz, kg·m² | 33.2 | 41.1 | 58.4 |
| Product Ixz, kg·m² | -2.8 | +5.0 | +9.1 |

All inertias are about the CG of each case. Steering geometry (measured from the CAD and `build-adventure.py`): **wheelbase 1,490.0 mm**, rake 25°, fork offset 36.1 mm, **trail 114.7 mm** measured on the ground (103.9 mm normal to the steering axis), tyre radii 331.5 / 325 mm. The old study's 1,483.9 mm wheelbase came from a different front tyre; rev D is 1,490 mm.

**Check against the roll-up:** total 247.93 kg vs 247.9; CG x 798.5 vs 798; height 535.5 vs 535; lateral 2.0 vs 2.0; front share 53.6% vs 53.6%. The roll-up's own pitch inertia (point masses) is 38.3 kg·m²; with real part shapes I get 42.6 (11% more, as expected when parts have extent).

## 2. Weave and wobble, 10 to 130 mph

**Model** (`dynamics-v1-model.py`): Sharp-type linear model, exact second-order Lagrangian, with the frame, fork and swingarm all flexible. Degrees of freedom: lateral position, yaw, roll, steer, **frame torsion**, **fork bending**, and the **rear wheel carrier on the swingarm** (lateral, toe, camber). Tyres have slip and camber force, aligning moment and relaxation length. The rider is rigid and hands-off (worst case).

| Stiffness input | Value | Source |
|---|---|---|
| Frame, at the head | 1.3 kN/mm lateral = **361 kNm/rad** (x head height 0.527 m above the pivot, squared) | FEA, `09-structures.md` (calculated); the torsion figure 4.4 kNm/deg (252 kNm/rad) is run as a sensitivity |
| Swingarm lateral / yaw / torsion | 1.01 kN/mm, 1.73 kNm/deg, 1.48 kNm/deg | FEA (calculated). A cantilever fitted to the lateral number gives yaw 100 kNm/rad against FEA's 99: they agree |
| Fork lateral bending | 30 kNm/rad | **estimate** (published enduro fork 28, Taraborrelli thesis); the fork is not designed. 40 is the target for the supplier spec |
| Tyres | cornering 13 / 11 per rad, relaxation 0.20 / 0.25 m, crown 65 / 90 mm | literature mid-range; **estimate**, swept |
| Structural damping | about 2% of critical | estimate |

**Checks:** the rigid core reproduces the Meijaard 2007 benchmark bicycle (weave 4.2924 vs 4.2924 m/s, capsize 6.0249 vs 6.0243 m/s, eigenvalues within 0.0006 1/s). The rigid rev D model equals the old validated model exactly. With frame, fork and swingarm made very stiff the flexible model reduces to the rigid one (slow roots within 0.0008 1/s). See `validation-meijaard.json` and `validation-rev-d.json`.

### Without a damper (hands off): `stability-modes.csv`, `stability-baseline.png`

| Case | Weave weakest ζ (25-130 mph) | Wobble weakest ζ (15-130 mph) | Wobble unstable range | Weave / wobble frequency near 77 mph |
|---|---|---|---|---|
| Bike alone (no rider; not a riding case) | +0.113 at 120 mph | -0.019 at 40 mph | 15-72 and 117-130 mph | 3.3 / 7.5 Hz |
| Bike + rider | +0.074 at 130 mph | **-0.112 at 35 mph** | 15-82 mph | 3.3 / 8.3 Hz |
| Rider + 25 kg luggage | +0.037 at 130 mph | **-0.147 at 32 mph** | 15-85 mph | 2.9 / 8.1 Hz |

- The rigid-frame version of the rider case is wobble-unstable only above 92 mph (ζ -0.07 at 130 mph); compliance moves the instability to low and medium speed and stabilises it above 90 mph. Every motorcycle model shows this.
- Weave and the slow capsize root are always unstable below about 25 mph (the rider handles this). Capsize at 130 mph is +0.50 1/s.
- Other modes below 100 Hz (swingarm lateral near 43 Hz, fork and frame modes near 50 and 85 Hz; a toe mode near 190 Hz is not reported): all stable, ζ ≥ 0.017.

### Sensitivity, rider case, no damper (wobble weakest ζ)

| Change | Wobble ζ | Weave ζ at 130 mph |
|---|---|---|
| Baseline | -0.112 | 0.074 |
| Frame stiffness 252 kNm/rad (torsion FEA) / 120 | -0.113 / -0.116 | 0.073 / 0.067 |
| Fork 20 / 40 kNm/rad | -0.143 / -0.085 | 0.064 / 0.082 |
| Rigid swingarm | -0.112 | 0.076 |
| Tyre cornering stiffness x0.7 / x1.3 | -0.088 / -0.128 | 0.062 / 0.091 |
| Relaxation length x1.5 / x0.5 | -0.138 / -0.085 | 0.053 / 0.094 |
| Rider's arms add 4 Nm·s/rad | -0.078 | 0.056 |

The frame number matters little (the FEA stiffness is high enough). **The fork matters most**, then tyre properties. The swingarm's flexibility has no visible effect on weave or wobble at these stiffnesses. Tyre choice therefore needs a stability sign-off.

### Steering damper: `damper-results.json`, `damper-schedule.png`

Fixed damping fails because the two modes pull in opposite directions (weakest ζ, rider / luggage, wobble then weave):

| Fixed damper, Nm·s/rad | Wobble, rider | Wobble, luggage | Weave at 130 mph, rider | Weave at 130 mph, luggage |
|---|---|---|---|---|
| 0 | -0.112 | -0.147 | +0.074 | +0.037 |
| 12 | -0.016 | -0.050 | +0.023 | +0.002 |
| 20 | +0.040 | +0.006 | -0.002 | -0.016 |

I searched speed schedules (c at low speed, falling linearly to c at high speed) over all three cases. **No schedule reaches ζ ≥ 0.03 in all of them. The best is 25 Nm·s/rad up to 50 mph, falling to 3 Nm·s/rad at 95 mph and above**; it reaches ζ ≥ 0.02 in all three cases. Results with that schedule (weakest ζ, 15-130 mph for wobble, 25-130 mph for weave):

| Case | Wobble | Weave | Where |
|---|---|---|---|
| Bike alone | +0.023 | +0.080 | wobble at 130 mph |
| Bike + rider | **+0.071** | **+0.060** | wobble at 33 mph, weave at 130 mph |
| Rider + luggage | **+0.039** | **+0.028** | wobble at 28 mph, weave at 130 mph |

At 77 mph with the schedule (the schedule gives about 11.8 Nm·s/rad at 77 mph) weave is ζ 0.18-0.20 at 3.2 / 2.8 Hz and wobble 0.076 / 0.055 at 8.4 / 8.2 Hz.

Sensitivity of the worst case with the schedule: frame 252 or 120 kNm/rad +0.025 / +0.022; fork 20 kNm/rad +0.018 (luggage); **fork 40 kNm/rad improves both riding cases (rider 0.088 / 0.067, luggage 0.057 / 0.035)**; tyre cornering stiffness x0.7 gives luggage weave +0.009; relaxation x1.5 gives +0.010. The riderless case with a 40 kNm/rad fork is -0.024 at 130 mph; it is not a riding case.

## 3. Braking and launch: `braking-results.json`, `braking-thermal.png`

Hand calculation (Cossalter, Limpert). Tyre μ 1.05 and ABS efficiency 90% (estimates).

| | Bike alone | Rider | Rider + luggage |
|---|---:|---:|---:|
| Rear lifts (stoppie) at | 1.29 g | **1.14 g** | **1.20 g** |
| Front tyre alone reaches | 0.90 g | 0.97 g | 0.92 g |
| Rear-only braking limit, dry / wet (μ 0.5) | 0.35 / 0.20 g | 0.36 / 0.21 g | 0.39 / 0.22 g |
| Ideal front share of braking at 0.5 / 0.8 / 1.0 g | 72 / 82 / 90 % | 72 / 85 / 94 % | 68 / 82 / 91 % |
| Rear tyre load left at 1.0 g (share of static) | 23% | 12% | 16% |
| Wheelie limit under drive | 1.49 g | 1.10 g | 0.99 g |
| Launch peak (220 Nm x 3.6 at the tyre, 2.38 kN) | 0.94 g | 0.70 g | 0.65 g |
| Front load at launch peak (share of static) | 37% | 37% | 34% |
| Rear μ needed at launch | 1.22 | 0.88 | 0.79 |

- **Split:** at 1.0 g the rear tyre carries only 12 to 16% of its static load, so the rear brake can do almost nothing at the limit. The ideal front share rises from 62% at 0.3 g to 94% at 1.0 g. A fixed split cannot follow that; ABS with rear-lift mitigation (IMU) is required. Front-only braking reaches 0.97 g (rider) before the stoppie limit; the rear contributes only the last 0.03 g. This confirms the Nov 12 recommendation.
- **Stop distance at 1.0 g** (the same in all loads, since decel is the input): 60 mph 39.4 m, 77 mph 63.8 m including 0.2 s of build-up (36.7 and 60.4 m without it). Real ABS stops at 0.945 g (90% of μ 1.05): 41.5 and 67.3 m. Reaching 1.0 g needs a tyre μ of at least 1.0, so the real stop depends on the tyre. UN R78 split-system laden limits (0.1V + 0.0076V², V in km/h) are 33.4 m at 60 km/h and 86 m at 100 km/h, and our 1.0 g stop from 100 km/h is about 42 m; I did not recompute R78 for 60 and 77 mph.
- **Wet regen:** a rear-only decel of 0.25 g (the regen cap in `06-drive-performance.md`) is above the rear-only wet limit of 0.21 g (rider), so regen must be limited on low-grip surfaces by the ABS/IMU.
- **Launch:** peak 0.70 g (3.95 s to 60 mph, average 0.69 g); with luggage 0.65 g (4.24 s per the drive study). The front keeps 34 to 37% of its static load; wheelie limit is 1.10 g / 0.99 g. Dry traction limit is 1.01 g (rider), so the bike is torque-limited, not traction- or wheelie-limited, on dry roads. No wheelie control needed for the standard launch. Rear suspension squat or jacking is not included here.
- **Discs** (the front 320 x 5 mm CAD disc is 1.21 kg each from its volume; the ledger slot still says 0.95 kg): lumped model with convection, radiation, aero drag and rolling resistance, energy balance checked (adiabatic 255 K vs simulated 228 K for one stop, the gap is cooling during the 8.5 s stop).

| 125 to 0 mph, start at 60 °C | Front disc peak | Rear 267 x 5 disc peak |
|---|---:|---:|
| Rider, one stop, 0.9 g (front share 89%) | 362 °C | 146 °C |
| Rider + luggage, one stop, 0.9 g | 375 °C | 180 °C |
| Rider, three stops at 0.6 g, 1 km apart | 444 °C | 355 °C |
| Rider + luggage, three stops at 0.6 g | **460 °C** | 426 °C |
| UN R78 heat fade (rear only, 80 km/h x 10, laden) | | 312 °C |

The 450 °C limit is an estimate for stainless discs with sintered pads. The old study's rear-disc problem (240 x 5 mm, 506 °C) is gone: 267 x 5 mm passes with room (312 °C), because the loaded mass is lower (363 kg against 487 kg two-up). Caliper and fluid temperature, pad μ against temperature, and regen are not modelled.

## 4. Steady lean and cornering clearance: `lean-results.json`, `lean-clearance.csv`

Method: the bike rolls about the line through the tyre crown centres (crown radius 65 mm front, 90 mm rear, **estimates**); every tessellation vertex of every CAD solid is tested (46,000 points, 118 parts; tessellation and decimation error under 2 mm, which is under 0.5° of lean). **Loaded** means a steady turn at load factor 1/cos(lean): the suspension compresses (the fork is re-fitted to rev D loads at 7.25 N/mm per leg, 200 mm air column, 34 mm preload, 1.79 Hz; the rear is 109 N/mm at leverage 2.33 as before) and tyres squash. Wheels and discs are excluded. **This time the belt, pulley and swingarm are included; the old study left them out.** (I found and fixed a bug in the old swingarm drop formula, which put the largest drop at the axle instead of the pivot.)

| Side | First part (loaded, rider) | Angle | Class |
|---|---|---:|---|
| Both | Peg rubber (folding pegs) | **45.6°** (45.2° with luggage) | soft |
| +Y (swingarm side) | retracted side stand | 48.1° | soft |
| +Y | battery cover / motor cover corner (Y196, Z262) | **53.4°** (52.8°) | hard |
| -Y (belt side) | **rear pulley outer flange (Y-181, Z159)** | **47.7°** (47.5°) | hard |
| -Y | belt | 50.3° | hard |
| Upright (no compression) | pegs 49.2°; pulley 48.6°; covers 60.3° | | |

- **Grip lean** is 46.4° at μ 1.05 (38.7° wet at 0.8; 50.2° at μ 1.2).
- **Crown radius** 45/60 mm gives pulley 44.9°; 85/110 mm gives 49.9° (so the answer carries about ±2.5° of tyre uncertainty).
- **Verdict:** the pegs touch first on both sides and the swingarm side is clear. On the belt side the pulley touches only 2.1° after the peg (rule: 3°) and 1.3° beyond grip lean. This is not a failure of strength, but a ground strike of the belt drive in a hard corner is a drive-train failure, not a scrape, so I want the margin.
- **Fix sizing** (pulley outer face to flange bottom Z159, loaded rider / luggage): outer face at |Y| 181 (now) 47.7 / 47.6°; 170: 50.5 / 50.3°; 160: 53.2 / 53.1°. An outer face at |Y| ≤ 177 gives 48.6° (peg + 3°). Dropping the outer flange (teeth OD, Z165) gains 1.3° at the same Y.

## 5. Gusts and sidewind at 77 mph: `gust-results.json`, `gust-response.png`

Linear model with the scheduled damper. **Assumed (aero will replace): side force slope Cy_β·A = 1.6 m²/rad (about 2.3 per rad on 0.7 m² with the rider), centre of pressure 0.80 m ahead of the rear axle and 0.95 m high.** F = ½ρ(V²+w²)·Cy_β·A·atan(w/V). A 10 m/s sidewind gives 349 N at 77 mph.

**Steady sidewind, holding a straight line (rider hands on the bars):**

| Wind at 77 mph | Force | Lean (into the wind), rider / luggage | Steering torque, rider / luggage |
|---|---:|---|---|
| 5 m/s (11 mph) | 87 N | 4.7° / 4.2° | 2.4 / 1.0 Nm |
| 10 m/s (22 mph) | 349 N | 9.7° / 8.8° | 5.1 / 2.1 Nm |
| 15 m/s (34 mph) | 784 N | 15.4° / 14.1° | 8.1 / 3.3 Nm |

Steering angle change is under 0.4°. At 10 m/s the lean rises with speed (5.7° at 40 mph to 15.3° at 125 mph, rider) while torque stays within about 5 Nm. **Hand check:** lean from a simple moment balance (F·z_cp / m·g·h) is 8.6°, or 8.9° with the tyre crown correction, against 9.7° from the model, within 10%.

**Hands off (the bike is not rider-controlled, so I only read the first second or two):** the bike first rolls downwind and slides.

| Gust | Sideways at 0.5 / 1.0 / 2.0 s, rider | Roll at 1.0 s | Luggage, at 1.0 s |
|---|---|---|---|
| Ramp to 8 m/s in 0.3 s | 0.04 / 0.39 / 2.8 m | 6.6° | 0.36 m, 4.3° |
| Ramp to 12 m/s | 0.06 / 0.61 / 4.4 m | 10.4° | 0.56 m, 6.7° |
| 1-cosine, 10 m/s over 1.5 s | 0.01 / 0.25 / 2.0 m | 5.7° | 0.24 m, 3.7° |

Beyond about 1.5 s hands off, the capsize mode (doubling time 1.4 s) takes over, which is why a rider has to act; I do not read numbers past 2 s. An idealised rider (optimal steering torque on lateral position, heading and roll, no delay; indicative only) stays within 1.3 to 1.4 m of the line for the 8 m/s gust with a peak torque of 14 to 18 Nm and 10 to 11° of lean.

**Sensitivity at 10 m/s (rider / luggage):** side force x0.5 or x1.5 scales lean and torque in proportion (4.8° / 14.5°, 2.5 / 7.6 Nm for the rider). **The centre of pressure matters most for steering torque.** Moving it rearward from 0.80 m to 0.60 m raises the rider torque from 5.1 to 11.3 Nm; moving it forward to 1.00 m reverses the torque (-1.2 Nm). Height 0.75 / 1.10 m changes the lean by -2 / +1.5°. The sign change means the torque the rider feels flips with the centre of pressure, so the aero study should place it before any gust criterion is called closed.

## CAD change requests

1. **Belt-side pulley (needed).** Move the rear pulley and belt plane inboard so the **outer flange face is at |Y| ≤ 177 mm** (now 181); 170 mm gives 50.3° and 5° margin over the pegs. That moves the inner flange face from Y-107 to about Y-96 to -103, which uses the gap to the 190 mm rear-tyre keepout (the CAD tyre is ±81 mm wide, so the real gap stays 15 mm or more). Alternative: remove the outer flange of the rear sprocket (+1.3°); that needs Gates's agreement on belt tracking.
2. **Steering damper provision.** The CAD's `Steering_damper_envelope` (1.1 kg) must be a **semi-active or speed-scheduled rotary damper**: at least 25 Nm·s/rad (specify 30 for headroom) up to 50 mph, falling to about 3 Nm·s/rad by 95 mph, speed from the ABS/VCU. A plain fixed damper cannot meet T8 (section 2). The lead should check the cost, mass and the envelope against the part chosen.
3. **Fork supplier specification.** Lateral twist stiffness at the lower clamp **≥ 40 kNm/rad** (estimate was 30), measured as in Taraborrelli. This is the largest single lever on the damping margin with luggage.
4. **Ledger.** Front discs are 1.21 kg each from the CAD volume (320 x 5 mm); the ledger slot is 0.95 kg. Rear disc 267 x 5 mm is fine (no 6 mm needed).
5. **Rear tyre radius.** The CAD uses 325 mm; the drive study uses a rolling radius of 0.3145 m. I used the CAD for geometry and the drive study's 2.38 kN for launch force. The two should be aligned.

## Decisions I made that the lead may want to change

- Luggage CG (X -100, Z 880 mm): moving it forward or lower would help the luggage case, which is the weakest.
- Weave is reported from 25 mph and wobble from 15 mph (all modes are checked from 15 mph, but weave and capsize below about 25 mph are always unstable on a motorcycle and are the rider's job).
- Fork bending stiffness 30 kNm/rad (estimate), crown radius 65 / 90 mm and relaxation 0.20 / 0.25 m (estimates).

## What this does not prove

- **No rider.** The rider is a rigid body with hands off. The arms add steering inertia and damping (a 4 Nm·s/rad guess improves the rider case's weakest wobble by 0.03). A hands-off test at 20 to 90 mph, with and without luggage, is the deciding experiment (V39 in `14-dvpr.md`).
- **The fork is not designed.** Its stiffness (30 kNm/rad, estimate) and the tyre properties (literature mid-range values, not measured adventure-tyre data) move wobble and weave by 0.03 to 0.06 each. The damper schedule was tuned to these assumptions; a different tyre or fork needs a re-run.
- **Swingarm, frame and structural damping.** Stiffnesses are FEA figures for the loads FEA ran, in single-stiffness lumped form (frame torsion, fork bending, swingarm cantilever), not a full flexible-body model. The belt-side swingarm that did not package is not modelled; the flexibility is that of the right-side arm. The 2% structural damping is an estimate and no tyre damping exists in the model, so modes above about 40 Hz are not meaningful.
- **Linear and straight-running only.** No stability analysis in a corner (cornering weave is often worse), no braking-in-a-turn, no kickback, no pitch and heave coupling, no aero lift or yaw moment beyond the assumed side force. The damper is evaluated hands-off at constant speed.
- **Mass.** The roll-up is ledger data (97% of running gear and all cooling are estimates, ±8 kg); the rider is a segment model and the luggage position is my assumption. The CAD pose is used for bike-alone and loaded cases alike.
- **Braking.** Hand calculations. ABS efficiency 90% and tyre μ 1.05 are assumptions. No dynamic pitch, fork dive, rear-wheel lift dynamics, hydraulics (master cylinder sizing and lever force were not re-checked for rev D), caliper or fluid heating. The 450 °C limit is an estimate. UN R78 stops were not re-derived beyond the 100 km/h and 60 km/h limits.
- **Lean clearance.** Steady turn with a load-factor model; crown radii and tyre radial stiffness are estimates. It ignores boot, bump compression in a corner, and the 3 mm sampling of the tessellation. The pulley is checked as a rigid body in its static position; belt and pulley deflection are not modelled. A side-stand corner or peg bracket may differ from the CAD stand-ins.
- **Gust.** The side force and its centre of pressure are my assumptions, not CFD. A true gust includes a changing yaw moment and the rider's reaction, which are only crudely represented. My pass criteria (10 Nm steering torque, 0.5 m hands-off deviation in a second) are screening numbers, not a standard; REQ-012 leaves the acceptance criteria open.
- **Nothing was tested on a bike.** All numbers are for a model of a CAD design.
