# V1.0 simulation plan

October 25, 2026, US Central. Prepared by Codex (GPT-6 family).

**Current state:** CfdOF is installed at pinned commit `a90f60c2313ceba09c236c81f0693d93357d1614` in the project-local FreeCAD runtime; its headless module import succeeded. OpenFOAM and ParaView are not installed; no CFD case has run. Import success does not verify meshing, solver execution, graphical integration or numerical accuracy. This document proposes the next setup and analysis; it does not perform dependency installation.

## Is CfdOF useful here?

Yes, as a FreeCAD-based front end for preparing and comparing flow cases once a credible complete bike+rider exterior exists. The existing V1.0 model improves component packaging but its faceted body study, simplified wheels, absent rider and unmodeled cooling paths cannot substantiate aerodynamic performance. Running those shapes now would calculate those approximations, not the selected production appearance.

Use a tool checkout and benchmark first, then ranked shape comparisons, then physically correlated results. CfdOF cannot establish chassis stability, electrical safety, battery life or network eligibility. Aerodynamic moments feed a vehicle-dynamics analysis; a small drag coefficient cannot prove comfort or safe gust response.

## Official setup findings and recommended route

The [official CfdOF README](https://github.com/jaheyns/CfdOF) specifies FreeCAD≥1.0 and OpenFOAM Foundation 9–13 or OpenCFD 2006–2512. Dependencies include ParaView, cfMesh and HiSA; Gmsh≥4.15 is optional. Windows choices include BlueCFD-Core 2024-1, WSL or a container. It flags MinGW versions after 2212 for a `createPatch` issue. MPI enables parallel execution. It recommends writable dependency locations. The container route prefers Podman and also supports Docker Desktop; meshing/solver additions are bundled, while ParaView is separately configured. Its dependency checker and demos are the next verification steps. These published compatibility statements do not establish that the pinned local installation supports a particular runtime.

The installed pinned README was also checked locally: its FreeCAD, OpenFOAM, Gmsh and Windows-runtime statements match the compatibility information above.

[BlueCFD's release notice](https://bluecfd.github.io/Core/News/) identifies2024-1 as native Windows OpenFOAM 12, MSYS2 and ParaView 5.11.2. [OpenFOAM Foundation's current download page](https://openfoam.org/download/) offers version 14, which is outside CfdOF's stated 9–13 range. Newest is not automatically compatible.

**First route to evaluate:** the documented native Windows BlueCFD-Core 2024-1 combination for a small checkout. This avoids adding a container workflow solely for a first test. Review actual CPU/RAM/disk and install permissions before committing; no workstation capability survey is implied here. For larger runs, compare Linux/WSL or a container using a known-good case rather than assuming equivalent performance or filesystem behavior.

Record the installed CfdOF commit and its own dependency declarations, runtime distribution/version, mesher, MPI, ParaView and relevant build tools. Keep solver output in a deliberate writable location with sufficient scratch space. A simple dependency path reduces whitespace/permission ambiguity; moving the design source is unnecessary. Any administrator action, environment change or larger installer is a separate operation; none was performed in preparing this plan.

## Checkout gates

1. Preserve the dependency-check log identifying the selected runtime, mesher and viewer. An import-only result remains an import test.
2. Run a demo from the pinned workbench revision. Verify mesh generation, solver completion, nontrivial fields and post-processing. Investigate warnings rather than merely hiding them.
3. Validate a simple external-flow benchmark against appropriate published reference data at matched geometry/Reynolds number. Establish force units, trends and mesh sensitivity.
4. Reopen an exported case; inspect actual generated dictionaries, patch assignments, material properties, boundary conditions, integration directions and density. Compare serial/parallel outputs when parallel operation is introduced.
5. Save the generated case and every controlled manual edit. Regeneration must not silently erase engineering corrections. Document any required function absent from the GUI instead of assuming it is supported.

## Geometry required before bike CFD

Create a separate analysis configuration linked to the native CAD revision. Include bike and ordinary seated rider with helmet, clothing, boots/gloves; mirrors; fork/wheel/tire forms; screen/body/tail; real cooling inlet/outlet pathways; and relevant controls/drive forms. Model bags as separate variants. The render is a shape reference, not a dimensionally calibrated rider or CFD surface.

Remove accidental duplicate faces, self-intersections, inverted normals and unintended leaks. Intentionally closed surfaces must block the intended volume at the selected mesh resolution. Do not rely on coarse meshing to hide unintended holes. The assembly need not be one fused solid, but the fluid region and wall/porous patches must have a physically meaningful definition. Preserve real openings; capping a radiator opening to reduce drag invalidates the cooling configuration.

Define rider measurements, seat/bar/peg settings, posture and clothing assumptions. Include smaller/larger riders before broad-population conclusions. A race tuck cannot qualify normal highway range. Detail suppression needs sensitivity evidence: small lettering may be immaterial, while screen edges, helmet/shoulder gaps, tire rotation and cooling leakage can determine the answer.

## Coordinates and speeds

Maintain X forward/Y left/Z up. In the stationary bike frame with no atmospheric wind, air velocity is **U=(−Vground,0,0)** and road velocity is **(−Vground,0,0)**. If the solver workflow uses flow along+X, explicitly transform geometry, forces and wheel rotation signs together.

Using the current arithmetic tire radii 0.2999 m front and 0.3119 m rear, pure forward rolling requires rotation about **+Y**. Check that the bottom point of each rotating tire moves in the road direction. Replace these nominal radii with the selected tire's measured rolling geometry. Rotating-wall tire surfaces are an initial approximation; detailed spoke motion can require a different, possibly transient treatment.

| Ground speed | Velocity, m/s | Dynamic pressure at ρ = 1.225 kg/m³ | Front/rearω, rad/s |
|---|---:|---:|---:|
|70 mph range baseline|31.29280|599.78Pa|104.344 /100.330|
|77 mph comfort/gust baseline|34.42208|725.74Pa|114.779 /110.363|
|125 mph performance screen|55.88000|1,912.58Pa|186.329 /179.160|

These are direct calculations from mph×0.44704, q=½ρV² andω=V/r; they are not simulated forces. Incompressible flow is an appropriate starting assumption to investigate at these speeds/ordinary temperatures. HiSA's availability does not require using a high-speed compressible solver at 70 mph.

At zero yaw, integrate pressure and viscous force on **all bike+rider surfaces**. Drag magnitude is−Fx in the stated convention; **CdA=Drag/(½ρVair²)** in square meters. If also reporting Cd, declare the fixed reference frontal area. Changing reference area cannot create real drag reduction.

At77 mph ground speed with 20 mph direct wind from the bike's left, relative air is approximately **(−34.42208,−8.9408,0)m/s**, magnitude 35.57 m/s and yaw magnitude 14.56°. Road and wheel speed remain77 mph. For fixed ground speed with pure crosswind at angleβ, Uy=±Vground·tanβ and Vair=Vground/cosβ. A constant-total-air-speed yaw sweep is a different experiment and must be labeled. Report both airflow-axis drag and vehicle-axis longitudinal force; the latter governs work against ground travel.

Declare moment reference origin and sign: roll aboutX, pitch aboutY and yaw aboutZ. Transfer to the current vehicle CG for dynamics use. Steering torque needs integration of relevant steering-assembly loads about its actual steering axis; whole-bike yaw moment is not handlebar torque.

## Proposed initial case settings

These are engineering starting choices requiring case review, not validated settings or claims that every option is exposed in CfdOF.

| Item | Starting choice and sensitivity |
|---|---|
|Air|Declared density / viscosity at temperature; initially ρ = 1.225 kg/m³ andν≈1.5×10⁻⁵m²/s for calculation consistency, then actual test conditions|
|Flow|Steady incompressible RANS for mean-flow screening; runtime-compatible solver; unsteady treatment if wake/forces prevent meaningful steady convergence|
|Turbulence|k–ωSST as a conventional starting model; sensitivity to model, inlet turbulence and initialization|
|Domain|LetL be actual complete bike+rider length; start about 5L upstream, 10L downstream and 5L clear sides/top, then test expanded domain/blockage|
|Inlet/outlet|Freestream velocity/turbulence, appropriate pressure outlet and backflow treatment matched to the selected solver|
|Sides/top|Appropriate far-field/slip treatment; crosswind must not be blocked by an incompatible lateral boundary|
|Road/wheels|Moving road at ground speed; wheel treatment consistent with contact kinematics; fixed-floor cases labeled as tunnel comparisons|
|Cooling|Actual ducts/openings and calibrated heat-exchanger pressure loss; relevant fan state; unsized solid blocks cannot establish cooling flow/drag|

Use runtime-matched documentation: [OpenCFD turbulence models](https://doc.openfoam.com/2212/tools/processing/models/turbulence/) and [official OpenFOAM user guide](https://www.openfoam.com/documentation/user-guide). Distribution/release differences matter; dictionaries from a different runtime cannot be assumed compatible.

## Mesh, convergence and uncertainty

Choose wall-resolved or wall-function treatment intentionally with matching boundary conditions. A near-wall-resolved SST study can initially investigate y+ near 1 on important surfaces; an alternative wall-function mesh needs its own justified range. Inspect actual distributions and boundary-layer coverage, including failed layers, rather than accepting one average. [Official yPlus reference](https://doc.openfoam.com/2212/tools/post-processing/function-objects/field/yPlus/)

Use at least three systematically refined meshes with consistent shape-comparison refinement logic. Focus on screen/helmet/shoulders, wheel/fork, cooling openings and wake. Archive surface tessellation, cell counts, layer settings and full mesh-quality reports. The documented `checkMesh` utility checks mesh validity; it does not establish physical resolution. [Official utility reference](https://www.openfoam.com/documentation/user-guide/a-reference/a.2-standard-utilities)

Proposed initial screening acceptance, subject to case approval:

- Mass imbalance<0.1% of inlet mass flow using a method valid for lateral/cooling boundaries.
- Mean drag drift<1% over a declared tail window, with actual fluctuations reported. Residual reduction alone does not establish force convergence.
- Final-two-mesh CdA difference≤2% as a screening target, plus quantified discretization uncertainty where justified. Two similarly inadequate meshes cannot prove convergence.
- Domain and numerical-scheme sensitivity smaller than the design decision's meaningful difference, with actual values reported.
- Unsteady cases need time-step and averaging-window sensitivity, startup removal and sufficiently independent samples. Choose timestep/Courant limits and sample length from actual behavior, not a fixed decorative iteration count.

These are proposals, not universal CFD standards. A 1% design difference with 5% unresolved uncertainty is inconclusive. Steady RANS cannot establish helmet-buffeting amplitude, acoustics or transient-gust handling. Benchmark, sensitivity and physical correlation remain essential.

Do not promise laptop runtime or cell count before a small-case memory/time measurement. Budget disk and restart/checkpoint behavior. Detailed rotating-wheel, high-resolution transient bike+rider cases may require more computing resources than a laptop; a quantified simplified ranking model can still be useful.

## Practical case sequence

| Stage | Cases | Decision |
|---|---|---|
|A0|Pinned-tool demo and external-flow benchmark|Toolchain and force/units checks|
|A1|Full ordinary-rider bike at 70 / 77 mph, yaw 0; mesh/domain studies|Whether assumed CdA 0.30 / 0.33 is plausible for this exterior|
|A2|Two feasible screen heights×two screen treatments×two lower-front/side concepts, same rider/configuration|Eight-case shape ranking including drag, lift, cooling and helmet wake|
|A3|Selected shapes at 77 mph; yaw 0/±5/±10/±15°; declared ground/air-speed convention|Side forces, roll/yaw/steer moments and asymmetric response|
|A4|Rider/posture/settings, bags, permissible cooling states and geometry-detail sensitivity|Robustness rather than one favorable result|
|A5|Tunnel/coastdown/road-load correlation for same configuration|Bias/uncertainty and revised energy requirement|
|A6|Correlated aerodynamic maps into vehicle/rider dynamics, then controlled gust/comfort tests|Highway behavior and comfort evidence|

The 100s8p energy-led concept's engineering target is comfortable-rider CdA ≤ 0.33 m². The 100s7p mass-led path investigates approximately 0.30 m² with tighter energy margin. Keep configurations and uncertainty separate. No CFD presently establishes either target.

## Reproducible simulation handoff

Retain geometry/source hash and revision; units/axes; rider measurements/posture; omitted geometry; patch map; complete generated/edited dictionaries; runtime and mesher versions; all material/boundary/initial values; wall/road/wheel/cooling models; mesh quality/y+; residual/continuity/force histories; averaging method; mesh/domain/scheme studies; raw data needed to repeat results; and figures with honest scales. Label calculated, measured and inferred quantities separately.

The useful immediate output is a correct tool checkout and credible analysis geometry. Colorful flow imagery around an incomplete model is not performance evidence.

