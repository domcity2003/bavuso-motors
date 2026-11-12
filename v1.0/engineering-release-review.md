# V1.0 independent engineering and CAD release review

October 25, 2026, US Central. Prepared by Codex (GPT-6 family). Review basis: B0 package, V1.0 generator and initial geometry audit, calculation exports, component registers and selected black/silver/tan design direction. This review defines acceptance tests and limitations; it does not certify the development model.

**A realistic-looking V1.0 can be a valuable engineering development baseline. It becomes build-ready only when its part definitions, interfaces, drawings and test evidence support that claim.** V1.0 is a version label, not an engineering approval. Leave release state visible in the model and drawing title blocks.

## What the existing evidence establishes

The local FreeCAD connection record reports version 1.1.4, nine geometric primitives, eleven document objects, native reopen and valid STEP re-import with equal summed volume. This establishes a functioning CAD toolchain. It does not establish component installation, load paths, electrical protection, comfort or performance. See [connection test](../documentation/models/freecad-connection-test.json) and [CAD studio](../documentation/cad-studio.md).

The existing coordinate study is in millimeters, X forward/Y left/Z up with rear contact at the origin and a 1,420 mm wheelbase. The measured supplier references and conservative reservations are useful inputs. Tire radii, body envelopes, rider hard points and mounting coordinates remain study assumptions. The source has no real steering/suspension kinematic assembly, complete supplier installation geometry, rider surface or exterior aero surface. See [package inputs](../documentation/models/package-reservations.json).

The [existing conflict register](../documentation/registers/packaging-conflicts.csv) contains five incompatible B0 reservations:

| B0 finding | Specific correction required in V1.0 |
|---|---|
| Battery box contains proposed swingarm pivot | Repack discrete cells/modules or move pivot/pack with updated dynamics and structural interfaces; cutting a cosmetic notch in a 30 kWh box does not preserve its energy |
| Battery box overlaps shock/linkage reservation | Model actual shock/linkage motion and service access; reserve spring body and damper reservoir, not only centerline |
| Motor and rear tire envelopes intersect | Move motor or revise drive architecture; then check full tire/swingarm motion, shaft/pulley loads and support |
| Radiator and front tire envelopes intersect | Resolve nominal and combined steer/bump tire sweep; preserve actual fan, hose and cooling flow passages |
| Motor and shock/linkage envelopes intersect | Reconcile drive and suspension as one layout; check travel and assembly/removal sequence |

These are envelope conflicts, not validated collisions between detailed manufactured parts. Their presence prevents declaring B0 a working package. Their absence in a new report will not prove that every unmodeled part clears.

### V1.0 review update

The new [V1.0 generator](tools/build-v1.py) imports manufacturer motor/CM200 STEP geometry and models 700 discrete catalog-maximum cell bodies at their stated 30% SOC dimensional basis. It creates a 100s7p arrangement, proposed frame/running gear, a 3 mm enclosure shell and styling studies. The [current geometry audit](geometry-audit.json) reports **ten selected component/body and sampled-bump checks passing** their proposed 20 mm gap criterion, including motor versus pivot-tube clearance of about 36.11 mm. This is meaningful progress beyond B0; the 20 mm criterion is a layout proposal rather than a supplier-qualified universal clearance.

The package changes wheelbase from 1,420 to **1,640 mm** and the seat reference to **850 mm**. Those are substantial engineering proposals affecting compact appearance, rider reach, handling and ground access; neither is an owner-approved replacement requirement. The nominal rake/trail definitions also need verification against actual tire loading and yoke/fork offsets rather than relying only on a target value in a parameter dictionary.

The current script checks **every vertex of all 700 rectangular cell bodies inside the inner case**, replacing the initial weaker center-only check. That is a valid complete-body containment test for these convex rectangular bodies inside this convex rectangular cavity. Independent inspection of the coordinates gives cell extents X585–1239.4, Y−75–73.55 and Z168–693.2 mm, within the inner box X573–1257, Y−107–107 and Z163–707 mm. This establishes geometric fit of those ideal catalog bodies only; it does not reserve validated end-of-life swelling, tabs, busbars, compression plates, electrical barriers, cooling, vents or protection. Pairwise spacing and each added internal component still need explicit audit as the pack design develops.

The audit intentionally excludes steering lock, rear droop, tire growth, real fork/yoke/hub geometry, full-frame clashes, wiring/hoses/mounts, structure and CFD. Its initial object count also includes group shapes; it is not a count of manufactured parts. The motor STEP dates to 2022 and CM200 CAD does not establish the exact ordered DX suffix. These source/revision limits must remain visible. Faceted body/seat/screen solids are appearance studies, not finished rider-qualified or CFD-qualified surfaces.

## Feasibility audit of the main goals

| Owner objective | Current evidence | Finding and required closure |
|---|---|---|
| 200 miles at 70 mph | Reproducible road-load energy model | Conditional feasibility only. Comfortable rider/body CdA, real usable pack energy, losses and environmental claim conditions remain unmeasured |
| >125 mph | Road-load sizing and candidate drive references | Requires current motor/inverter maps at loaded low SOC, actual rolling radius, reduction ratio and approved duration/ambient; a 60 kW label cannot close the goal |
| Tesla charging | Candidate NACS electrical architecture | Network eligibility and successful authorized charging at supported station types remain open; connector geometry is insufficient |
| <400 lb preferred | Component allocations and pack-integration sensitivities | No weighed, manufactured BOM. Focused 100s7p study is 399.05 lb including its allowance at typical cell mass, but 402.14 lb with stated maximum cell mass. This is inadequate margin, even before unmodeled additions |
| 77 mph comfort/gust confidence and compact styling | Owner visual intent and starting geometry | Needs ergonomic buck, normal-rider aero, multibody stability/load cases and staged physical validation. Image proportions are not these results |

Mass figures above come from [development summary](../documentation/models/development-summary.json), not new measurements. The focused 100s7p calculation combines 85% cell mass fraction and 95.5 kg outside the pack, both unproven. Its minimum-cell-energy/max-cell-mass 70 mph range at assumed CdA 0.30 is about 203.7 miles; the corresponding 200-mile CdA boundary is about 0.3071. Its typical-cell 90%-health range is about 188.4 miles. The design has little slack for real-world variation. The smaller battery is an avenue to investigate, not an automatic replacement for the 100s8p baseline.

### Decisive current mass inconsistency

For the modeled 690 × 220 × 550 mm closed shell with a 684 × 214 × 544 mm cavity, the net material volume is 3,861,456 mm³. At an **assumed aluminum density of 2,700 kg/m³**, this is **10.426 kg**, before lid design, mounts, hardware, seals or any internal equipment. Typical cell mass is 68.11 kg. The 85%-cell-fraction pack target is 80.129 kg, leaving only **1.593 kg after this shell** for all compression/restraint, interconnections, insulation, cooling plates, BMS, contactors, fuse, sensing and internal wiring.

The current shell and optimistic pack integration allowance therefore do **not** constitute a credible completed pack mass design. The solution may involve a redesigned enclosure, different integration or more allowed mass; it cannot be closed by retaining an 85% label while adding uncounted hardware. The assumed alloy/density is not yet a released material specification. This is the highest-priority quantified reconciliation between the new CAD and the earlier mass model.

### Independent cost-register consistency check

The [cost model](cost-model.csv) contains 166 rows: all **158 existing component-index records exactly once** plus eight recurring-process rows. Independent comparison found no missing, extra or duplicate coverage IDs. For each production scenario, summing only `base_included=True` rows reproduced the report's recurring low/base/high figures. Base sums are **$79,821.42 / $59,377.22 / $41,183.01** at assumed annual capacities 100 / 1,000 / 10,000. The [startup register](startup-costs.csv) has 18 rows per scenario; its independent base sums are **$16,705,836 / $46,847,623 / $188,441,931**. These agree with the rounded [cost report](cost-and-sourcing.md).

This checks coverage and arithmetic only. The component index itself includes function-level records rather than a completed leaf BOM; zero-cost child rows mean included in a named bundle. Most dominant prices, lead times, production efficiency and capital assumptions are unquoted. All-record coverage does not establish purchasable exact parts, authentic supply, network access, final pack cost or commercially feasible retail pricing.

## What CAD quality V1.0 must provide

Use four explicit object classes: **supplier exact geometry**, **custom design**, **installation reservation**, and **reference/appearance only**. Every object carries class, source/drawing revision, internal part ID, mass basis and release status. Do not give a fitted shell the supplier's measured-mass status. Cosmetic bolts do not establish a joint design.

1. **A credible exterior:** recognizable selected silhouette with panels, screen, seat, upright swept-back bar and mid-position pegs; black/silver/tan configurations sharing the same mechanical core. Use fairing thickness only as a declared development assumption until process/material analysis supports it. Include real opening/closing/service boundaries and plausible mount zones. Do not lock the structure to every generative inconsistency in a render.
2. **A credible internal package:** individual energy-system groups with explicit cell count and reserved tab/interconnect/cooling/restraint spaces; known motor/inverter/OBC bodies plus connectors, coolant fittings, brackets and removal volumes; radiator/fan/pump/reservoir volumes; final drive support and guarding; LV source and protection equipment. If supplier dimensions are missing, the model shows the missing-data reservation visibly.
3. **A meaningful chassis:** distinct frame, swingarm, fork/yokes, shock/linkage, axles, wheels/tires, hydraulic brakes and controls. Sketches or primitives may communicate intent but must not masquerade as validated tube sections, bearings, axles or welds. Show connected load paths and every essential mount; exact sections/joints await calculations.
4. **A kinematic package:** steering and suspension controls plus combined limit configurations; loaded and unladen reference geometry; tire growth/deformation and hose/cable slack envelopes; belt tension/alignment over travel; seat/peg/bar variants; pack insertion/removal and tool access. Present interference checks by state, modeled scope and severity.
5. **A reviewable solid model:** coherent units/datums, valid solids or intentionally classified surfaces, no unintended duplicate parts, nonmanifold faces or negative volume; reliable native reopen and STEP re-import; body names/part numbers; coordinate axes and dimensioned sections. The model must rebuild from source, with scripts and dependency versions saved.
6. **An engineering mass view:** densities assigned only to real modeled material, not installation boxes. Keep measured purchased masses, calculated custom masses, fluid quantities, harness estimates and unallocated mass separate. Summing bounding-solid volumes is not vehicle mass. The assembly CG/inertia remains provisional until density/mass distributions are credible.

Before calling any custom part manufacturable, add dimensioned production drawings with datums/tolerances, material/condition/process/finish, threads/fits, weld/joint definitions, inspection criteria and revision. Before calling an assembly buildable, add the full BOM, joint schedule, harness/netlist, fluid schedule, software/calibrations and controlled assembly/service instructions. The [67-item release register](../documentation/registers/release-deliverables.csv) remains the governing closure list.

## Specific review gates for the new CAD artifact

| Gate | Required report | Pass condition | Present evidence |
|---|---|---|---|
| CAD-01 Definition | Native source + neutral export + manifest | Correct units; filenames/revisions; body IDs; all exact/reservation/appearance classes declared | Existing B0 toolchain passes basic exchange only |
| CAD-02 Static geometry | Full assembly sections and interference report | Every detected clash resolved or explicitly justified; omitted parts/clearances enumerated | V1.0 has ten selected checks passing; global part/interface scope remains incomplete |
| CAD-03 Movement | Combined suspension/steering/load sweeps | No unapproved interference or hose/cable/drive travel violation; numerical clearances released | Not yet evidenced |
| CAD-04 Energy package | Cell/group count and complete pack interface model | Real capacity fits with joining/restraint/cooling/protection/services and supplier mechanical limits | Cell-counting studies only |
| CAD-05 Service | Pack/tool/removal sweeps and independent review | Assembly and routine service possible using defined supports/tools without unapproved disassembly or protection bypass | Not yet evidenced |
| CAD-06 Loads | Structure, brake and drive calculations tied to model revisions | Approved load envelope, joint and fatigue design; part selection application limits satisfied | Starting references only |
| CAD-07 Aero readiness | Bike+rider simulation geometry and patch map | Air regions/blockage and known leaks controlled; cooling/mirrors/wheels included; posture defined | No qualified aero model yet |
| CAD-08 Evidence | Correlated analysis and subsystem/vehicle test records | Relevant verification gates passed for released configuration | No physical verification performed |

A development CAD handoff can be issued with CAD-01 complete and other gates clearly open. A manufacturing release cannot. Avoid labeling approved-looking dimensions as final merely because they are now drawn to several decimal places.

## Highest-value next engineering steps

Resolve the motor/tire/pivot/pack/shock layout as one geometry problem. Show at least two workable packaging alternatives before selecting: a shaped single enclosure with relocated shock, and another discrete-cell arrangement with a different motor/support position. Compare usable energy, case/support mass, rider knee width, seat height, service route, drive loads and front wheel sweep. Do not evaluate these options solely by total cell bounding volume.

Then confirm the supplier application data that could invalidate the preferred package: pouch swelling/compression and joining; current EMRAX thermal maps and shaft side loads; inverter resolver/current compatibility; charger exact input range and suffix; station operating voltage/network eligibility. Low-SOC top speed and stationary hot charging are decisive tests. Hold purchased-component mounting holes provisional until current installation drawings exist.

Use the visually realistic model as the shared place to expose tradeoffs. Its greatest value is connecting the owner's shape to measurable package and system decisions. A renderer cannot turn unselected brakes or missing harnesses into engineered hardware; a controlled CAD/BOM/test process can.

## Release disposition

**Recommended designation: V1.0 Engineering Development Model — not released for manufacture, energization or riding.** This designation allows a useful concrete artifact now and gives a team an exact list of what evidence earns the next release. It does not relax any owner goal or imply that unavailable supplier data have been obtained.

For the complete verification and manufacturing framework see [verification plan](../documentation/verification/verification-plan.md), [hazard analysis](../documentation/verification/hazard-analysis.csv), and [assembly/service/quality specification](../documentation/manufacturing/assembly-service-quality.md). For the proposed CFD route see [simulation plan](simulation-plan.md).
