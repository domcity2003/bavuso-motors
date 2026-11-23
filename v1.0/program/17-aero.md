# Bavuso V1 rev E aerodynamics (CFD)

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
Geometry: `cad/Bavuso-V1.0-adventure.FCStd` (rev E) plus the 90 kg, 95th-percentile upright rider from `cad/Bavuso-V1.0-adventure-rider.FCStd` (hashes in `data/aero/geometry-manifest.json`). Method: OpenFOAM 12 (blueCFD), steady RANS k-omega SST, wall functions, moving road and rotating wheels, 70 mph = 31.29 m/s, 4 MPI ranks. Labels: **calculated** = CFD, **estimate** = my assumption.

## The plain answer

- **The drag area (CdA) of rev E with the rider is about 0.46 m² on the finest mesh, and it is still falling.** It misses target T3 (0.38 m²) by about 20%. The best estimate once the mesh error is taken out is 0.43 m² (calculated, GCI band below), which still misses T3 by 13%.
- **The 0.503 you saw was the coarsest mesh (0.9 M cells) and does not hold up.** It fell to 0.478 (1.7 M cells) and 0.460 (3.25 M cells).
- **Mesh convergence is NOT met.** The change between the two finest meshes is -3.7%, against a 2% goal. The three meshes fall in a regular pattern (observed order 2.1), so the extrapolated value is 0.430, but the grid convergence index (GCI) is 8.3%. Read the answer as 0.43 to 0.46 m².
- **Range at a steady 70 mph (method of 06, drive-lib as found: bike 257.5 kg + 90 kg rider, 23.76 kWh): about 132 mi at CdA 0.46 (139 mi at 0.43). At 77 mph: about 113 mi (120 mi).** 06 quoted 154 mi at CdA 0.38 on 240 kg; the same method at 257.5 kg gives 152 mi at 0.38. T3 (145 mi) therefore fails on the CFD CdA.
- **The old study said 0.385 with a 50th-percentile rider; this one is higher mainly because the rider is bigger.** Frontal area is 0.824 m² (bike 0.56, rider 0.51) against 0.766 before. The rider group alone is 0.10 m².
- **Crosswind (10° yaw, medium mesh, one side only):** side force 149 N, centre of pressure 1.04 m ahead of the rear axle and 0.67 m high, yaw moment about the CoG -46 N·m (nose pushed downwind), drag along the wind +23%.
- **Radiator pods: the CFD flow goes the wrong way.** See the table; this needs a CAD or duct decision.

## Verdict table

| Item | Result | Required | Status |
|---|---|---|---|
| CdA, 0° yaw, finest mesh m3 | 0.460 m² (Cd 0.56 on 0.824 m²); Richardson 0.430 | ≤ 0.38 (T3) | **fail** |
| Mesh convergence, 3 meshes | 0.503 / 0.478 / 0.460; -5.1% then -3.7%; GCI 8.3% | ≤ 2% between the two finest | **fail** (honest band 0.43 to 0.46) |
| Iteration convergence | window drift 0.4 to 0.96%, std 0.003 to 0.004 m² | < 1% | pass |
| Mass balance (net flux / inflow) | ≤ 0.001% | < 0.1% | pass |
| Range 70 mph at CdA 0.46 | 131.8 mi (138.8 at 0.43) | ≥ 145 mi (T3) | **fail** |
| Range 77 mph at CdA 0.46 | 113.4 mi (119.8 at 0.43) | none set | info |
| Side force slope Cy·A | 1.38 m²/rad, force 307 N at 77 mph with a 10 m/s side wind | 15-dynamics assumed 1.6 m²/rad, 349 N | assumption was 13% high |
| Centre of pressure | 1.04 m ahead of rear axle, 0.67 m high | assumed 0.80 m, 0.95 m | **differs** (see handover) |
| Radiator through-flow | outward, about 6.2 m/s, 0.13 m³/s per core | thermal assumed 0.25 x road speed, inward | **mismatch** |

## Mesh study (task 2)

Every length is tied to a base cell, so all refinement levels scale together. Base cell 0.50 / 0.37 / 0.274 m (ratio 1.35 in surface cell size: 7.8, 5.8, 4.3 mm at the finest surface level). **The cell-count ratio is lower: r = N^(1/3) is 1.23 and 1.25**, because the far-field and wake boxes do not refine. The GCI uses the cell-count ratio (the stricter choice). Procedure: Celik et al. 2008, safety factor 1.25.

| Mesh | Cells | CdA (m²) | Bike body | Rider | Wheels | Solver hours |
|---|---:|---:|---:|---:|---:|---:|
| m1 | 898,265 | 0.5033 | 0.347 | 0.125 | 0.031 | 0.8 |
| m2 | 1,676,311 | 0.4775 | 0.330 | 0.123 | 0.025 | 1.3 |
| m3 | 3,251,721 | 0.4599 | 0.341 | 0.098 | 0.021 | 2.1 (first 350 of 500 planned iterations) |

Observed order 2.07, convergence ratio 0.68 (monotonic), Richardson CdA 0.4295, GCI on the finest 8.3%. **A fourth mesh (about 6 M cells, base 0.203) was planned and not run**: it needed about 6 to 10 hours more on a shared laptop. The bike-body and rider parts move in opposite directions between m2 and m3, so the total is a sum of unsettled parts, and I would not claim better than the 0.43 to 0.46 band.

Run notes: m1 and m2 ran 500 iterations, m3 was stopped at 350 (drag settled by 150 to 250 in all cases; windows of 50 iterations on m3 read 0.453, 0.461, 0.458, 0.463). The solver wrote no fields for m3, so the pictures and pod numbers come from m2.

## Where the drag comes from (m3, N at 0° yaw; total 275.9 N)

Lower body 61, fairing and tank 45, screen 32, fork and fender 21, torso and arms 29, legs 17, helmet 13, front wheel 10, mirrors 13, seat and tail 11, bars 8, rear wheel 3, swingarm 7, radiator pods 6. Pressure drag is 98%. Pictures: `data/aero/drag-map-side.png`, `midplane-cp.png`, `midplane-speed.png`, `convergence.png`, `mesh-study.png` (m2).

## Yaw (task 3)

Only +10° (wind from the rider's left) was run, on m2 (1.68 M cells). The -10° case was dropped for time, so symmetry is assumed. At 0° the m2 side force is +3.7 N, which is the noise floor.

| Quantity | +10° (air speed 31.78 m/s, q 618 Pa) |
|---|---|
| Side force | -148.8 N (CyA = -0.241 m²; slope 1.38 m²/rad) |
| Yaw moment about CoG (bike + rider, 0.732 m, 0.667 m) | -46.3 N·m; CnA·L = -0.075 m³ |
| Centre of pressure | 1.043 m ahead of rear axle, 0.671 m high |
| Drag along the wind | 364.7 N, CdA 0.590 (+23.5% over 0°) |
| Lift / front axle load change | +33 N / +204 N unloaded at the front |

**For dynamics:** use slope CyA = 1.38 m²/rad, CP 1.04 m ahead of the rear axle (not 0.80) and 0.67 m high (not 0.95). The CP moves forward by 0.24 m, and 15-dynamics found the steering torque flips sign with the CP, so the gust case must be re-run.

## Radiator pods (task 5)

The mesh resolves the pods (4,000 cells in each core on m2; m1 agrees). The cores are porous zones with my resistance estimate (dP = 13 v + 2.2 v² Pa for 28 mm, **estimate**); the fans are left out of the flow.

| | m1 | m2 |
|---|---|---|
| Through-core velocity | 7.5 m/s outward | 6.2 m/s outward (0.20 x road speed) |
| Static pressure just outside the core | -177 to -234 Pa | -187 to -202 Pa |
| Static pressure just inside the core | +61 to +84 Pa | +50 to +57 Pa |
| Pressure difference (outer minus inner) | -261 to -295 Pa | -244 to -252 Pa |

**Mismatch with 10-thermal.md.** Thermal assumed air flows in through the pod mouth at 0.25 x road speed. In the CFD the pod sits in a suction zone (the flank flow accelerates around the 55 mm-proud pod), the inside of the body is pressurised through the open nose and screen gaps, and the air flows backwards through the cores. The speed is similar (0.20 x) but the direction is wrong, and a reversed flow brings in no cool air. This depends on the open-shell body and on the core resistance estimate, so it is a strong warning, not a proven result. See handover.

## Handover and CAD change requests

1. **Dynamics:** replace the assumed side-force numbers (above) and re-run the gust case.
2. **Thermal and CAD (radiator pods):** the pods need a closed duct from the grille to the core and a defined outlet to the low-pressure flank or belly, or the airflow assumption (0.25) cannot be used. Suggest the CAD agent close the body openings and re-run.
3. **Drag:** T3 is not met. The largest single items are the lower body (61 N), the fairing shell (45 N), the screen (32 N) and the mirrors (13 N). I did not test fixes.

## Reproduce

From `v1.0` in Git Bash: `sh program/tools/aero-v1-run.sh m1 m2 yaw+10 m3`, then `aero-v1-report.py`, `aero-v1-range.py <CdA>`, `aero-v1-yaw.py` (FreeCAD python). Scripts: `program/tools/aero-v1-export.py`, `aero-v1-make-case.py`, `aero-v1-run.sh`, `aero-v1-report.py`, `aero-v1-range.py`, `aero-v1-yaw.py`. Data: `program/data/aero/aero-results.json` (keys `cda`, `range_70_mi`, `range_77_mi` are the dossier inputs), `range-70mph.json`, `geometry-manifest.json`. Solver output: `program/data/aero/run/` (git-ignored).

## What this does not prove

- That 0.46 m² is the converged value: the finest two meshes differ by 3.7%, and the extrapolated 0.43 rests on the three meshes being in the asymptotic range.
- Anything about a real rider: the rider is the CAD's smooth buck with no clothing, helmet visor or gloves, and clothing would add drag.
- The open-shell body: the CAD shells are open, and air gets inside, which the real bike may not allow. This drives both the drag and the reversed pod flow.
- The radiator result: the core resistance, the missing fans and the lack of any measured core are all open.
- Yaw symmetry: -10° was not run, and the yaw numbers come from the medium mesh.
- Steady RANS misses unsteady shedding; no wind-tunnel or coast-down data exist.
- The range numbers use drive-lib as found (257.5 kg bike); a 0.4 kg change to 257.9 kg moves range by less than 1 mi.
