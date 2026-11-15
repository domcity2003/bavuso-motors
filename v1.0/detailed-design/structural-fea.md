# Bavuso V1.0: structural FEA of the primary structure

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5). Final runs and the safety agent's crash-guard case were added November 13.

- **Scripts:** `detailed-design/tools/fea-frame.py` (model, load cases, CalculiX runs), `fea-handcheck.py`, `fea-fatigue.py`, `fea-convergence.py`, `fea-summary.py`.
- **Outputs:** `detailed-design/structures/`. Solver files are in `structures/run/`, which git ignores.
- **Design variables:** `final-sections.json` is the resized design. The baseline is the CAD as it stands today.

## The plain answer

**The frame in the current CAD is not strong or stiff enough. The resized version passes every load case, the fatigue target and the stiffness target, for about 17 kg more structure.**

1. **Today's CAD fails 10 of 12 strength cases and the stiffness target.**
   - **Stiffness:** the frame twists **1.4 kNm/deg**, against a target of at least 3.
   - **Braking:** at 1.1 g, the head-tube end of the upper rails reaches **729 MPa** in a 435 MPa steel. That is 1.7 times what the steel can take.
   - **Rear shock:** at a 3 g rear bump, the 28 mm tube that holds the top of the shock reaches **1,056 MPa**, 2.4 times yield.
   - **Fatigue:** 32 of 61 welded details fail.
   - **Why:** each side is one untriangulated loop of 32 × 2.5 tube, and both the rails and the down-links meet the head tube at a single point.
2. **The battery pack case is not the weak link.** In normal riding its stress stays under 25 MPa. The tubes carry the frame loads; the pack works as a stiff box between them.
   - Its hard case is crash retention: 20 g pushes 21 kN of cells into the front wall. With the changes below, the worst pack stress is 115 MPa at a step corner, against 140 MPa at a weld seam.
   - That needs a **5 mm front wall** (now 4 mm) and **10 mm pads under the lugs**.
3. **The fix is triangulation plus heavier tubes in a few places.**
   - Two posts per side from the upper rail down to the pack roof.
   - The upper rails move up the head tube, with a gusset to the down-link.
   - The shock top mount becomes a forged box bridge, with diagonals down to the pivot nodes.
   - Heavier tubes where the load is.
   - A deeper swingarm, with the shock tower and cross brace as one A356 casting.
4. **What the fix gives:**
   - **Torsional stiffness: 6.8 kNm/deg**, 2.3 times the target, from 1.4.
   - **Lateral stiffness: 4.6 kN/mm**, from 1.4.
   - Every case has margin to yield of at least 1.05. A crash load at yield needs 1.0; the riding loads need 1.2 to 1.5 and get at least 1.20.
   - Every welded detail reaches **Miner damage ≤ 0.48 against an allowed 0.5** over 160,000 km. Life is about 2 times the design life, and the frequent low loads stay under the 10-million-cycle fatigue knee.
5. **Cost:** frame, swingarm and pack-case structure go from **25.3 kg to about 42.4 kg** (+17.1 kg), which takes the bike from **287 to about 304 kg** ready to ride. The weight is mostly where the stiffness comes from: thicker rails, posts, gussets and the shock bridge.
6. **Crash-guard request:** 21 kN outward at three mounts.
   - **Upper-rail node:** passes, safety factor **1.06**. It needs the shock diagonals to pass.
   - **Pack front lug:** passes, **1.22**.
   - **Rear-link lug:** passes, **1.05**.
   - With the CAD as it stands, these points reach 1,000–1,600 MPa and would bend.

## Verdict table (final resized design, 12 mm pack mesh)

SF is the margin to yield.

| Item | Value | Required | Margin | Verdict |
|---|---|---|---|---|
| C1 static 1 g two-up (482 kg), worst member | 59 MPa (front post) | SF ≥ 1.5 | SF 7.4 | pass |
| C2 front bump 3 g | 125 MPa (upper rail) | SF ≥ 1.2 | 3.5 | pass |
| C3 braking 1.1 g, front only | 270 MPa (upper rail at head) | SF ≥ 1.2 | 1.61 | pass |
| C4 braking + 2 g bump | 276 MPa (upper rail at head) | SF ≥ 1.2 | 1.58 | pass |
| C5 45° lean × 1.5 dynamic, offset contact | 126 MPa (front post); 120 MPa A356 brace | SF ≥ 1.2 | 3.5 / 1.67 | pass |
| C6 rear bump 3 g (shock 17.5 kN) | 167 MPa, A356 cross brace | SF ≥ 1.2 | **1.20** | pass, no spare margin |
| C7a pack 20 g longitudinal (26.2 kN) | pack 115 MPa at the front step corner (92 MPa on the front wall); rear link 114 MPa | SF ≥ 1.0 (seam value 140 MPa) | 1.22 / 3.8 | pass |
| C7b pack 8 g lateral (10.5 kN) | rear link 219 MPa; side wall 122 MPa at a step corner | SF ≥ 1.0 | 2.0 / 1.15 | pass |
| C7c pack 5 g vertical | 67 MPa (floor) | SF ≥ 1.0 | 2.1 | pass |
| C9a guard 21 kN at upper-rail node | 410 MPa (tail rail) | SF ≥ 1.0 at yield | **1.06** | pass |
| C9b guard 21 kN at pack front lug | 358 MPa (rear link) | SF ≥ 1.0 | 1.22 | pass |
| C9c guard 21 kN at rear-link lug | 413 MPa (rear link) | SF ≥ 1.0 | **1.05** | pass |
| Torsional stiffness, head to pivot | 6.8 kNm/deg | ≥ 3 (own target) | 2.3× | pass |
| Lateral stiffness at the head | 4.6 kN/mm | ≥ 1.5 (own target) | 3.0× | pass |
| Fatigue, worst welded detail (cast headstock rail joint) | Miner D 0.48 | D ≤ 0.5 (IIW) | life ≈ 2× design | pass |
| Fatigue, swingarm arm (FAT 22 Al weld) | D 0.23 | D ≤ 0.5 | 2.2× | pass |
| Fatigue, pack case at lug pads (FAT 28) | D < 0.002 | D ≤ 0.5 | very large | pass |
| Lug bolts, 4 × M10 10.9 per lug: slip, worst riding case | slip SF 4.7 | ≥ 1.3 | 3.6× | pass |
| Lug bolts, crash-guard case C9b | slip SF 1.13; shear SF 7.4 | no shear failure | joint may slip, bolts hold | pass |
| Lug bolts, fatigue (VDI 2230) | amplitude ≤ 1.1 MPa vs 51 | SF ≥ 1.5 | > 45 | pass |
| Fatigue on a 10× harsher spectrum (all off-road) | D up to ~4.8 | D ≤ 0.5 | — | **open**: needs measured road loads |
| Fatigue on a 2× harsher spectrum | D up to ~0.97 | D ≤ 1.0 (no factor) | — | marginal |

The baseline (the CAD as it is today) is in the section "Baseline: why the current CAD fails".

## Model

### Geometry

Every dimension is read from `tools/build-adventure.py` (lines 376–488). The model uses the generator's coordinates, before the +40 mm lift.

| Part | CAD today | How it is modelled |
|---|---|---|
| Upper rails | 3 segments, pivot node (540, ±195, 350) → (570, ±195, 740) → (1050, ±195, 780) → head (1184, ±35, 850), 32 × 2.5 | Beams |
| Down-links | Head → front pack lug (1067, ±180, 470), 32 × 2.5 | Beams |
| Rear links | Pivot node → rear pack lug (664, ±175, 380), 32 × 2.5 | Beams |
| Tail rails and braces | 28 × 2 | Beams |
| Shock-top cross tube | 28 × 3 at X 490, between the tail rails at Y ±183 | Beams |
| Head tube | 62 × 6 | Beam |
| Pivot stubs | 40 × 5 | Beams |
| Swingarm | Box arms 92 × 34 tapering to 58 × 30 (wall not set in CAD; 3 mm assumed), 50 × 5 cross brace at X 380, twin 8 mm tower plates to the lower shock eye (315, 439) | Beams |
| Shock | Pin-ended link between the eyes | Truss |
| Fork | Steering frame, rake 25°, offset 36.1 mm, clamps rigid on the head tube | Beams |

- **Elements:** all frame tubes are CalculiX B32R beams. CalculiX expands them internally into 20-node bricks.
- **Pack case:** a closed stepped box of S4 shells, X 590–1088, Y ±194, Z 198–574, 4 mm thick.
  - The outline comes from the 8 cell bands in `geometry-adventure-audit.json`.
  - Band edges were snapped together where they lie within 15 mm, so the steps are within ±6 mm of the CAD.
- **Lugs:** steel 30 × 40 blocks onto a rigid patch of radius 35 mm, standing in for a bolted boss with 4 × M10.
- **Swingarm pivot:** each arm is tied to its frame stub in translation only, at Y −133 and +125. Together the two ties act as a hinge about Y, so the shock carries the full moment.

### Masses

- All 174 lines of `mass-rollup.csv` are applied, each to its nearest structural node.
- The pack and anything sitting on it (pack, charger, inverter) are spread over the case by area.
- Unsprung masses go to the axles.
- **Rider:** 85 kg, split 65% seat, 30% pegs, 5% bars.
- **Pillion:** 80 kg. **Luggage:** 30 kg on the rack.
- **Total:** 482 kg, centre of mass 603 mm ahead of the rear axle and 573 mm above the ground. Static wheel loads are 1,919 N front and 2,810 N rear.

### How the loads are balanced

- For cases 1–6 the tyre contact forces are given.
- The script solves the six rigid-body accelerations of the whole bike that balance them (a manual "inertia relief"). Each mass gets its own inertial force, m(g − a − α × r).
- The supports are minimal: front contact x, y, z; rear contact y, z; lower head bearing y. They only stop free-body motion. Every case prints their reactions to show they are not carrying load (see Verification).

### Materials (design yield; welded values where a weld is present)

| Part | Material | Yield / UTS used | Note |
|---|---|---|---|
| Frame tubes, headstock, lugs | AISI 4130 normalised | 435 / 670 MPa | 435 is the TIG-welded heat-affected-zone value; the parent tube is ≥ 517 MPa (AMS 6360). |
| Swingarm arms | 6061-T6, re-solution-treated and aged after welding | 240 / 290 MPa | **This must be specified.** As-welded 6061 is only about 110 MPa. |
| Shock tower + cross brace (final design) | A356-T6 casting, bolted to the arms | 200 / 260 MPa | One part, with no welds in the high-moment zone. |
| Pack case | 6082-T6 plate/extrusion, friction-stir welded | 250 parent / 140 at seams | Stresses away from the lug pads are checked against 140. |
| Bolts | M10 class 10.9 | proof 830 MPa | Preload 38 kN (VDI 2230, μ_thread 0.12, 90% utilisation). |

## Load cases and why

| # | Case | Contact loads (two-up, 482 kg) | Basis |
|---|---|---|---|
| C1 | Static 1 g | F 1.92 kN, R 2.81 kN | Weight. Required SF 1.5 on yield, because it is always present. |
| C2 | Front bump, 3 g | Front 3 × static (5.76 kN) | The 3 g front bump is the standard frame "ultimate road" case: 3 × static wheel load for a pothole or kerb strike (Foale, *Motorcycle Handling and Chassis Design*, ch. 9). |
| C3 | Hard braking, 1.1 g, front only | Fx −5.20 kN, Fz 3.92 kN front, 0.80 kN rear | Load transfer = μ·h/wheelbase; 1.1 g is the stoppie limit with this centre of mass (≈1.22 g). Putting all the braking on the front puts the largest moment on the head tube (Cossalter, *Motorcycle Dynamics*, ch. 1 and 5). |
| C4 | Braking + bump | C3 front plus 2 × static vertical, and a 25% rearward impact component | A pothole during an emergency stop: the combined case frame designers usually check. |
| C5 | 45° lean, × 1.5 dynamic | Each wheel 1.5/cos 45° = 2.12 × static in the bike plane | Steady lean gives 1/cos φ = 1.41 g in the bike plane (Cossalter §1.6); the 1.5 factor covers bumps mid-corner. The contact patch moves 57 mm (rear) and 42 mm (front) toward the inside of the turn, and a small lateral force keeps the resultant through the centre of mass. This twists the frame and swingarm. |
| C6 | Rear bump, 3 g, through the shock | Rear 3 × static (8.43 kN) | Same basis as C2. The shock force is 17.5 kN; the bump stop must carry it. |
| C7 | Pack inertia: 20 g longitudinal, 8 g lateral, 5 g vertical | 26.2 / 10.5 / 6.6 kN | UN R100 Rev. 3 mechanical-shock levels for M1 cars (20 g / 8 g), used here as crash-retention practice; 5 g vertical is a hard landing. The cells (106.9 kg) bear on the wall they are thrown against; the other 26.8 kg of the pack is spread over the case. The head tube and pivot nodes are held fixed. |
| C8 | Stiffness | 1 kNm torque about X at the head, or 1 kN lateral | Pivot stubs fixed at the bearing points; no fork, swingarm or shock. This follows the test-rig practice of the Padova frame tests (fixed at the pivot, loaded at the steering head). |
| C9 | Crash guard (safety agent's request) | 21 kN outward (+Y), one step each at (a) the upper-rail node (570, 195, 740), (b) the front pack lug, (c) the rear-link lug | Head and pivot held fixed, as in C7. Required: no yield (SF ≥ 1.0). The model is linear, so an inward load gives the same stress magnitudes. |

**Stiffness target.** I could not retrieve a primary published number for adventure-bike frames in this session; the PDFs found were not readable here.
- I set **≥ 3 kNm/deg** torsion and **≥ 1.5 kN/mm** lateral at the head.
- These are the lower end of the range commonly quoted for modern road frames in the chassis literature (Foale; Cossalter's group, e.g. the WIT Press frame rig paper below).
- Treat these targets as a judgement call. They need checking against a measured benchmark bike.

## Baseline: why the current CAD fails

Results at 12 mm mesh, nominal beam stress (axial plus shear).

| Case | Worst member | Stress MPa | SF on yield | Verdict |
|---|---|---|---|---|
| C1 static | shock-top cross tube | 374 | 1.16 | **FAIL** (needs 1.5) |
| C2 front bump | down-link | 552 | 0.79 | **FAIL** |
| C3 braking 1.1 g | upper rail at head | 729 | 0.60 | **FAIL** |
| C4 braking + bump | upper rail at head | 799 | 0.54 | **FAIL** |
| C5 cornering | shock-top cross tube | 794 | 0.55 | **FAIL** |
| C6 rear bump | shock-top cross tube | 1,056 | 0.41 | **FAIL** (tower plates 719 MPa in 6061) |
| C7a 20 g | rear link 351; pack front wall 183 | — | 1.24; 0.77 at seam | **FAIL** at the seam |
| C7b 8 g | rear link | 622 | 0.70 | **FAIL** |
| C7c 5 g | rear link | 196 | 2.2 | pass |
| C9a / b / c guard | tail rail / rear link / rear link | 1,599 / 1,001 / 1,137 | 0.27 / 0.43 / 0.38 | **FAIL** |
| Torsion | 1.38 kNm/deg | — | 0.46 of target | **FAIL** |
| Lateral | 1.37 kN/mm | — | 0.91 of target | **FAIL** |
| Fatigue | 32 of 61 welded details over D = 0.5; worst is the 6061 shock tower, D ≈ 1,100 | | | **FAIL** |

**Where the twist goes.** The strain energy in the torsion test shows which members give way.
- The down-links take 55% of it and the upper rails 21%.
- Each side is a four-bar loop with no diagonal: head → rail → pivot → rear link → pack → down-link → head.
- Torque can only pass through it by bending tubes.
- Thicker tubes alone hardly help: walls three times thicker gave 0.80 kNm/deg; a rigid pack gave 0.66.
- What works is **adding the diagonal**: posts from rail to pack, plus spreading the head joint. Together they doubled stiffness before any tube was resized.

## The resized design (what changed and why)

The swept options are in `fea-frame.py --only stiff --set ...`, all at a 24 mm mesh.

| Configuration | Torsion kNm/deg | Lateral kN/mm |
|---|---|---|
| CAD today | 1.38 | 1.37 |
| Pack made rigid (40 mm walls) | 0.66 | 1.42 |
| Down-links and rear links 32 × 8 | 0.80 | 1.92 |
| Upper rails 32 × 8 | 0.71 | 1.42 |
| Rails moved up the head tube only | 0.75 | 1.30 |
| **Two posts per side, rail to pack roof** | 0.84 | 2.17 |
| Posts + rails moved up (w = 185) | 2.66 | 2.06 |
| Posts + rails up + 38 × 3 links | 3.47 | 2.72 |
| **Final** (all changes below) | **6.8** | **4.6** |

The first sweep, at that point the "rigid pack" figure (0.66), was run while the near-rigid connectors were still ordinary steel. Those soft connectors made the absolute numbers about 2× too low, but they do not change the ranking. The final numbers use 100× stiff connectors and a stiff test lever; see Verification.

- **Braking (C3/C4) sized the head end.** Upper rails at the head go to 45 × 4, down-links to 40 × 3.5, plus a 10 mm gusset. The fatigue of frequent mild stops also set the headstock: it becomes a cast steel headstock with 60 mm spigots and full-penetration butt welds, IIW FAT 63 in place of FAT 45 fillets.
- **The rear bump (C6) and fatigue sized the shock top.**
  - The 28 mm cross tube is replaced by a **70 × 40 × 4 forged steel box bridge** with an integral clevis.
  - It gets **two 25 × 2.5 diagonals** from Y ±60 on the bridge down to the pivot nodes. These also rescued the crash-guard case C9a.
  - The shock tower and cross brace become **one A356-T6 casting**, 2 × 14 × 85 tower webs and a 60 × 5 brace section, bolted to the arms. The welded 6061 tower would sit at FAT 18 and could not pass fatigue at any practical size.
- **The 8 g lateral and crash-guard cases (C7b, C9c) sized the rear links:** 44 × 3.5.
- **Fatigue sized the swingarm arms:** at the 6061 FAT 22 welds they go to 135 × 34 × 4.5 at the pivot, tapering to 75 × 30 × 4 at the axle.
- **Pack retention (C7a) sized the pack front wall:** 5 mm. Bending in the stepped front wall under 20 g of cells was 105 MPa mid-panel at 4 mm, which leaves no margin to the 140 MPa seam value at the step corners.

## Fatigue

**Method.** Nominal-stress approach of IIW-2259-15 (Hobbacher 2016), with aluminium details per IIW and EN 1999-1-3.
- **S–N curve:** FAT is the stress range at 2 million cycles. Slope 3 down to the knee at 10⁷ cycles, then slope 22 below it, as IIW recommends for variable-amplitude loading.
- **Mean stress:** no correction, because as-welded joints carry residual stress near yield.
- **Safety factor on stress:** γ_Mf = 1.25.
- **Pass criterion:** Miner damage D ≤ 0.5, the IIW recommendation for variable-amplitude loading.
- **Stress per g:** the stress change per g of extra wheel load comes straight from the FEA: (C2 − C1)/2 for the front, (C6 − C1)/2 for the rear, C3/1.1 for braking, and the steady part of C5 for cornering.

**Road-load spectrum (assumption).**
- **Design life:** 160,000 km (100,000 mi), 25% unpaved.
- **Shape:** a log-linear vertical spectrum per axle, the "straight-line" shape used for vehicle durability (Heuler & Klätschke 2005).
- **Bumps** (extra wheel load ± a g : cycles): ±0.1 g: 2×10⁷; ±0.2: 3×10⁶; ±0.35: 3×10⁵; ±0.5: 5×10⁴; ±0.75: 5×10³; ±1.0: 10³; ±1.5: 100; ±2.0: 10.
- **Braking** (stops): 0.3 g: 2×10⁵; 0.6 g: 10⁴; 0.9 g: 10³; 1.1 g: 100.
- **Cornering:** 10⁵ corners at 45° lean.
- **This spectrum is my assumption, not a measurement.** The sensitivity is shown below, and the spectrum needs instrumented-ride data from a proving ground.

| Detail (final design) | FAT | Range per ±1 g, MPa | Miner D | Verdict |
|---|---|---|---|---|
| Upper rail at head (cast headstock spigot weld) | 63 | 50.5 | 0.48 | pass |
| Front post, rail to pack | 45 | 58 | 0.45 | pass |
| Swingarm arm behind the brace (6061 weld) | 22 | 45.7 | 0.23 | pass |
| Upper rail mid (rail to post) | 45 | 66 | 0.40 | pass |
| Down-link at headstock | 63 | 51 | 0.27 | pass |
| Shock-top bridge | 45 | 85.9 | 0.16 | pass |
| Tail rail at the bridge | 45 | 90.8 | 0.19 | pass |
| Shock tower (A356 cast) | 40 | 85 | 0.25 | pass |
| Shock top plates (integral forged clevis) | 56 | 80.9 | 0.07 | pass |
| Pack case at lug pads (FSW or bolt-hole net section) | 28 | ≤ 9 | < 0.002 | pass |
| Steel lug blocks: Goodman, Kf 2.5 at holes | Se 94 MPa | mean 2, amplitude 4 | SF > 20 | pass |
| M10 lug bolts (VDI 2230, σ_ASV 51 MPa) | — | ≤ 1.1 MPa at ±2 g | SF > 45 | pass |

**How sensitive this is to the spectrum** (`fatigue-final-h12-x2.json`, `-x10.json`):
- **2× the cycle counts:** the worst D is about 0.97. That passes with no extra factor, but fails the 0.5 target.
- **10× the cycle counts:** the worst D is about 4.8, a fail. That is a bike ridden hard off-road for its whole life.
- **What this means:** the design has about 2× life margin on this spectrum and no more. The real spectrum decides this. **This is the largest open risk in the structure.**

**Why the joints control the design.** 4130 thin-wall tube welds and 6061 welds have low fatigue strength (FAT 45 and FAT 22). So the frame is sized by fatigue at the joints, not by peak strength: most members sit at SF 1.6–3.5 on yield but D ≈ 0.4–0.5 on fatigue.

## Lugs and bolts (frame to pack)

**Lug forces.** These are taken from the stresses at the lug section in the FEA.

| Case | Front lug, each | Rear lug, each |
|---|---|---|
| C3 braking | 3.4 kN axial, 3.6 kN shear, 47 Nm | 0.9 kN |
| C7a 20 g | — | 12.3 kN axial (tension) |
| C7b 8 g | — | 4.3 kN shear, 56 Nm |
| C9b guard at front lug | 18.9 kN shear, 245 Nm | — |

**Bolt design: 4 × M10 10.9 per lug on a 60 × 50 pattern, preload 38 kN, friction coefficient 0.15.**
- **Riding cases:** the joint does not slip, with SF ≥ 4.7.
- **Crash-guard case C9b:** slip SF 1.13, so the joint holds by friction, just. If it does slip, the bolt shear SF is 7.4.
- **Bearing:** a 4 mm wall is too thin for a bolted boss (82 MPa per bolt at 13 kN). So every lug and post sits on a **10 mm machined pad of radius 60 mm** on the case.

**Hand check of the bolt group.** An eccentric load of 13.1 kN at 20 mm on 4 × M10 gives per-bolt forces:

| Method | Bolts 1 and 2 | Bolts 3 and 4 |
|---|---|---|
| Elastic method (hand) | 4,536 N | 2,551 N |
| FEA, shell plate with bolt beams | 4,536 N | 2,551 N |

The two agree. Thread shear is 56.5 MPa against an allowable of 600 MPa.

## Verification (what was checked, and the result)

1. **Beam bending of a tube (hand vs FEA).** A 400 mm cantilever of 32 × 2.5 tube under 1 kN.

   | Quantity | Hand | FEA |
   |---|---|---|
   | Stress 100 mm from the root | M/Z = 189.1 MPa | B32R beam 189.1; S4 shell tube 191.6 (+1.3%) |
   | Tip deflection | 4.10 mm (bending only), 4.14 with shear | B32R 4.09; shell 4.18 |

2. **Bolt shear (hand vs FEA).** A centred 13.1 kN load gives 3,275 N per bolt by hand and 3,275 N in FEA. The eccentric case above also matches to the newton.
3. **Shock force through the swingarm (hand vs FEA).**
   - The lever ratio 540/231.6 = 2.33 gives 6.1 kN at static two-up by hand. The FEA gives 6,060 N.
   - This also proves the pivot behaves as a hinge.
   - The first model had a bug where the pivot carried moment (2.3 kN). It was found by this check and fixed.
4. **Equilibrium.**
   - **C7:** the reaction totals are 26,232 N (= 133.7 kg × 20 g) and 10,493 N (= 133.7 kg × 8 g).
   - **C1–C6:** the support reactions equal the specified contact forces, and the extra roll stop at the head carries 0.0 N.
5. **Mesh convergence on the critical part (the pack case),** three meshes of 24, 12 and 6 mm (3,500 / 11,500 / 39,000 nodes), in `convergence-revised.json`.

   | Pack stress (MPa) | 24 mm | 12 mm | 6 mm |
   |---|---|---|---|
   | C7a front-wall mid-panel | 100.9 | 104.2 | 105.4 (converged, Δ 1.2%) |
   | C7a 99th percentile | 90.0 | 94.4 | 94.8 |
   | C7b side-wall centre | 55.8 | 58.8 | 57.8 |
   | C7a peak | 130 | 144 | 174 |

   - The smooth-region stresses have converged.
   - The peak sits at a sharp re-entrant step corner or the edge of a rigid lug patch. It grows with refinement, as a singularity should, so it is **not** a design value.
   - The real case will have 5–8 mm inside radii at the steps. Peak stress there needs a local solid sub-model (not done).
   - Beam results do not depend on the shell mesh: frame member stresses agree to 1% across the three meshes, and torsion is 6.856 / 6.859 kNm/deg at 12 and 6 mm.
6. **The stiffness rig itself.** In the first stiffness runs, the steel test lever and the stand-in head-joint stubs took 54% of the strain energy. That made the frame look 2× softer than it is. They were made 100× stiffer, and the reported numbers use that version.

**Not checked:**
- buckling of the thin tubes (axial loads are low, but no linear buckling run was done);
- weld toe hot-spot stress;
- the lug patch with real bolt holes;
- contact and slip in the bolted joints;
- dynamic or modal behaviour;
- plastic collapse in crash.

## CAD change requests (for `tools/build-adventure.py`, model coordinates)

Tubes are given as outer diameter × wall in mm, 4130 unless stated.

| # | Part | Now | Change to | Mass change, both sides |
|---|---|---|---|---|
| 1 | Upper rail vertical leg `Upper_rail_0` (540, 350 → 570, 740) | 32 × 2.5 | **44 × 3.5** (`tube(...,22,18.5)`) | +0.9 kg |
| 2 | Upper rail `Upper_rail_1` (570, 740 → 1050, 780) | 32 × 2.5 | **38 × 3.0** | +0.7 kg |
| 3 | Upper rail `Upper_rail_2` (1050, 780 → head) | 32 × 2.5, ends at (1184, ±35, 850) | **45 × 4.0**, ends higher on the head tube at steering-axis station w = 120 mm, i.e. (1156.2, ±35, 908.8) | +1.1 kg |
| 4 | Down-links `Lower_downlink` | 32 × 2.5 | **40 × 3.5**, same end points. ⚠ +4 mm radius cuts tyre clearance from 22 to about 18 mm against the required 20: move the front lug out to **Y ±184** (was ±180) and the head end to **Y ±39**. | +1.1 kg |
| 5 | **New** head gusset | — | 10 mm 4130 plate, 60 mm wide, from the upper-rail head joint to the down-link at 35% of its length | +1.9 kg |
| 6 | **New** headstock | head tube plus fillet-welded rails | **Investment-cast 4130 (or forged) headstock**, 62 × 6 bore, with 60 mm spigots for the rails and down-links; full-penetration butt welds on backing rings | ~0 (replaces tube ends) |
| 7 | **New** posts, rail to pack roof (×2 per side) | — | **32 × 2.5**, from `Upper_rail_1` at X 1000 to the pack roof at (990, ±178, 573.5), and from X 700 to (712, ±178, 573.5); each with a steel lug and 4 × M10 into a pad | +1.3 kg |
| 8 | Rear links `Lower_pack_rear_link` | 32 × 2.5 | **44 × 3.5** | +0.5 kg |
| 9 | Tail rails `Tail_rail` | 28 × 2.0 | **38 × 3.0** | +1.7 kg |
| 10 | Shock-top cross tube `Tail_shock_cross_tube` | 28 × 3 tube | **Forged 4130 box bridge, 70 high × 40 deep × 4 wall**, with integral clevis. The seat-pan relief channel grows from 48 to about 60 mm wide and the bridge stands about 28 mm higher. ⚠ Check the seat foam over it (now about 66 mm). | +1.7 kg |
| 11 | Shock top bracket plates | 2 × 8 mm | **2 × 12 mm × 70 mm deep**, integral to the bridge | +0.6 kg |
| 12 | **New** shock-bridge diagonals | — | **25 × 2.5**, from (490, ±60, 724) to the pivot nodes (540, ±195, 350). They clear the reservoir by about 25 mm and the motor (Y ≤ 96) laterally. | +1.1 kg |
| 13 | Swingarm arms | 92 × 34 → 58 × 30 (wall unset) | **135 × 34 × 4.5 at the pivot → 75 × 30 × 4.0 at the axle**, 6061-T6, re-solution-treated and aged after welding. ⚠ Check the arm against the pegs and motor cover at full bump (the bottom edge drops 22 mm at the pivot). | +1.0 kg |
| 14 | Swingarm brace + shock tower | 50 × 5 brace + 2 × 8 mm 6061 plates, welded | **One A356-T6 casting**: brace section equivalent to a 60 × 5 tube, tower webs 2 × 14 × 85, bolted to the arms (2 × M10 per side) | +0.9 kg |
| 15 | Pack case front wall (all front-facing step risers) | 4 mm | **5 mm** | +0.5 kg |
| 16 | Pack case lug and post pads (8 places) | 4 mm | **10 mm machined pad, radius 60 mm**, M10 inserts | +1.8 kg |
| 17 | Lug bolts | not specified | **4 × M10 × 1.5, class 10.9, preload 38 kN, on a 60 × 50 pattern** per lug; isolating washers between steel and aluminium | — |

**Total structural mass change:** about +17 kg. Frame, swingarm and pack case go from 25.3 to about 42.4 kg; the bike from 287 to about 304 kg ready to ride.

Two cost-downs to study once instrumented loads exist:
- a closed-section cast-aluminium pivot and shock node in place of items 9–12 (likely −3 kg);
- 4 mm walls on the cast headstock spigots in place of the gusset (−1 kg).

## Sources

- IIW, A. Hobbacher, *Recommendations for Fatigue Design of Welded Joints and Components*, 2nd ed., Springer 2016. https://doi.org/10.1007/978-3-319-23757-2
- EN 1999-1-3, Eurocode 9: Design of aluminium structures, Part 1-3: structures susceptible to fatigue.
- VDI 2230 Part 1 (2015), systematic calculation of highly stressed bolted joints.
- Heuler, P., Klätschke, H., "Generation and use of standardised load spectra and load–time histories", *Int. J. Fatigue* 27 (2005) 974–990. https://doi.org/10.1016/j.ijfatigue.2005.01.012
- UN Regulation No. 100 Rev. 3, Annex 8C mechanical shock. https://unece.org/transport/vehicle-regulations-wp29/standards/addenda-1958-agreement-regulations-81-100. The 20 g / 8 g M1 levels were not re-verified against the text in this session.
- V. Cossalter, *Motorcycle Dynamics*, 2nd ed. (2006): load factor 1/cos φ, load transfer.
- T. Foale, *Motorcycle Handling and Chassis Design* (2002): load cases, frame stiffness.
- Frame stiffness test rig, constraint at the steering head or pivot. https://www.witpress.com/Secure/elibrary/papers/CMEM05/CMEM05050FU.pdf, and https://research.unipd.it/retrieve/e14fb267-7c79-3de1-e053-1705fe0ac030/paper-sav274.pdf
- Yamaha, head-pipe and pivot torsion in cornering. https://global.yamaha-motor.com/jp/design_technology/technical/pdf/chapters/YMC-TR59_TechPaper_01.pdf
- Elastoplastic frame load levels (1.0 kNm torque in competition, 1.8 kNm off-road bending). https://graz.pure.elsevier.com/files/77962676/Investigate_the_elastoplastic_deformation_behaviour_of_a_motorcycle_frame_under_different_mechanical_load_configurations.pdf

## What this does not prove

- **The road-load spectrum is assumed.** Fatigue passes with about 2× margin on it, but fails on a 10× harsher (all-off-road) spectrum. Measured wheel-force or strain data from a mule bike is needed before release.
- **The model has no welds, holes, corner radii or fillets.** Weld toes, bolt holes and step corners were covered by detail classes and nominal stress, not by hot-spot or solid sub-models. The peak stresses in the pack corners are mesh-dependent and were not used as design values.
- **Several parts are modelled as idealised beams:** the pivot node casting, the lug blocks and the shock-bridge clevis. They need their own solid FEA once drawn.
- **No buckling, crash plasticity or dynamic analysis was run:** no modal analysis, no wobble or weave coupling with frame compliance, no drop test.
- **The stiffness target (≥ 3 kNm/deg) is my judgement.** No published adventure-bike measurement was retrieved in this session.
- **Some items were not analysed:** the fork and triple clamps (supplier parts), the axles, the wheel bearings and the bump stop.
- **The proposed geometry changes need a CAD clash re-check:** tube upsizes, posts, diagonals, the bridge and the swingarm depth. Two known tight spots are flagged in the change table: down-link to tyre, and seat foam over the bridge.
- **The resized design was not re-run at 6 mm.** The pack mesh study was done on the pre-final design, which had a 4 mm front wall and no connected shock diagonals. The pack stresses it checks are local to the case and essentially unaffected by those changes, but that is an inference, not a run.

## Re-check needed after the November 14 seat and ergonomics change

*Claude Opus 5.5 (claude-opus-5-5), November 15, 2026, US Central.* The comfort change (comfort-study.md) moved two structural items. Neither has been re-run here:
- **Upper rails:** the front joint pulled in to Y ±152 (from ±195–214) and 18 mm lower, at Z715. The rails run from that joint to Y ±195 at the head end. The tail rails now start at that joint and end 10 mm higher, at Z827.
- **Shock bridge:** now an 80×45×5 box laid flat, at X482, with the top eye 18 mm lower and 8 mm further back. Its section modulus is 15.9 cm³, at least the 14.5 cm³ of the old upright 70×40×4 box. The shock line of action changed slightly (leverage 2.33, was 2.34).

The frame load cases and bridge bending should be repeated on the new geometry before any of these numbers are quoted as current.
