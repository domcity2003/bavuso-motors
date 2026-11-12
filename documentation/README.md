# Bavuso Motors — engineering development package

**Baseline B0 · October 25, 2026 · Codex, GPT-6 family.** Prepared for the owner and an eventual engineering/mechanical team. No repository has been created and no external handoff has been sent.

This package turns the appearance drafts and earlier feasibility work into a structured product definition: requirements, system interfaces, component breakdowns, packaging reservations, alternatives, hazards, verification and manufacturing-release requirements. It is the current entry point; older research is retained for the development history.

**The vehicle is not yet defined well enough to reproduce or build exactly.** Required supplier data, dimensioned manufacturing parts, electrical schematics, validated software and physical evidence remain missing. This package makes those gaps identifiable and assignable instead of hiding them in guessed part numbers or assembly instructions. It is usable for engineering development; it is not a production release.

![Bavuso Motors current black appearance reference](../design/baseline%20black.png)

Current appearance set: [black](../design/baseline%20black.png), [silver](../design/baseline%20silver.png), [tan](../design/baseline%20tan.png). The latest [design notes](../design/design%20notes.md) control visual intent. Historical white concepts are not the current finish set. Visual development does not certify packaging, aero or comfort.

## Read in this order

| Document | Purpose |
|---|---|
| [Product specification](product-specification.md) | Owner requirements, proposed configuration and unresolved product choices |
| [Connected FreeCAD studio](cad-studio.md) | Installed free CAD environment, tested Python connection, native model and launcher |
| [Convergence and alternatives](research/convergence-and-alternatives.md) | Quantified battery/drag/mass paths and disposition of competing architectures |
| [Packaging and design integration](packaging.md) | Dimensioned reservations, known conflicts, human factors and aero experiments |
| [Architecture and interfaces](architecture-interfaces.md) | Subsystem boundaries, datum proposal, control ownership and exact interface deliverables |
| [Mechanical systems](systems/mechanical-chassis.md) | Drive matching, chassis, wheels, suspension, brakes, loads, joints and service |
| [Electrical and energy systems](systems/electrical-energy.md) | Cells, HV/LV, controls, charge routing, thermal limits and harness definition |
| [Verification plan](verification/verification-plan.md) | Evidence contract, staged tests and release gates |
| [Assembly, service and quality](manufacturing/assembly-service-quality.md) | Configuration control, incoming checks, traveler, inspections and maintenance documentation |

## Current conclusions that matter

The original 800-cell energy reference is still a useful comparison, but its estimated **433 lb before allowance / 446 lb with allowance** misses the preferred under-400 lb target. Most of that mass is an allocation, not a weighed BOM.

A newly quantified alternative uses **700 cells / 26.299 kWh**, better aerodynamic efficiency and tighter pack integration. The focused screening case assumes **85% pack cell mass fraction**, **95.5 kg outside the pack** and **CdA 0.30**. On a common allowance-inclusive mass basis it calculates approximately **208.6 miles at 70 mph and 399.05 lb**. These are conditional results, not achieved specifications: drag, integration, installed nonpack mass, charge performance and aging remain unproven. Only about 0.95 lb separates that assumed mass from 400 lb. Seven hundred cells at the published +2 g mass tolerance add 1.4 kg with the noncell hardware held fixed, raising the result to **402.14 lb**; combining this mass with minimum published cell energy gives approximately **203.7 miles** under the same otherwise favorable conditions. Do not advertise this as a solved motorcycle. The 30 kWh path remains active until evidence can select between them.

Current motor data changes the old handoff: the liquid-cooled EMRAX208 v1.7 reference is **47 kW / 75 Nm continuous**, with a product transition and mandatory airflow. The **LV+100% winding** is now a co-leading study because it may improve low-SOC speed capability. It has different phase-current requirements and is not an approved swap.

The first coordinate study reveals five reservation conflicts: pack/pivot, pack/linkage, motor/rear tire, radiator/front tire and motor/linkage. It has not fitted all parts under the render. Tesla network eligibility and actual charge interoperability remain open independently of NACS inlet fit. Stationary hot charging may require derating or refrigeration with additional power/mass.

## Registers and machine-readable artifacts

| Artifact | Contents |
|---|---|
| [Requirements](registers/requirements.csv) | 35 owner/proposed requirements with origin and required evidence |
| [Interfaces](registers/interfaces.csv) | 35 cross-system interfaces and required definitions |
| [Mechanical components](registers/mechanical-components.csv) | 86 assemblies/functions including bearings, seals, brackets and joint families |
| [Electrical components](registers/electrical-components.csv) | 42 assemblies/functions including HV protection, charge routing and LV recovery |
| [Road equipment, finish and accessories](registers/road-equipment-components.csv) | 30 additional or cross-referenced function records |
| [Unified component index](registers/component-index.csv) | Search index of the three component registers; not an additive procurement BOM |
| [Hazards](verification/hazard-analysis.csv) | Preliminary hazards, controls and needed evidence; not completed safety approval |
| [Release deliverables](registers/release-deliverables.csv) | Concrete missing documents/evidence required for reproducible build release |
| [Packaging conflicts](registers/packaging-conflicts.csv) | Detected reservation conflicts; clearance coverage is incomplete |
| [Configuration sweep](research/configuration-trades.csv) | 72 explicit cell-count/integration/aero screening cases |
| [Program summary](models/development-summary.json) | Reproducible selected outputs and register counts |

Registers enumerate known component and function families; they **do not claim every individual terminal, fastener or seal has been selected**. Assembly rows and child functions coexist. The unified index marks reference duplicates and requires leaf expansion before quantity or mass roll-up. Some optional and alternative entries are mutually exclusive. Blank mass and TBD quantities remain unresolved, never zero.

## Editable visual/model files

- [Side reservation drawing](visuals/package-side.svg), [3D OpenSCAD study](models/package-reservations.scad) and [coordinate JSON](models/package-reservations.json).
- Tested native [FreeCAD document](models/Bavuso-B0-package.FCStd) and [STEP exchange geometry](models/Bavuso-B0-package.step); see the [CAD studio instructions](cad-studio.md). These contain reservations and known conflicts, not released parts.
- [Mass/range screening figure](visuals/configuration-trades.png): conditional paths, not test results.
- [Generation script](tools/build-development-model.py) uses Python standard library; [figure script](tools/render-figures.py) uses Pillow. Run the generation script before rebuilding figures and auditing.
- [Audit script](tools/audit-package.py) checks links, register identifiers, reference counts and deterministic model outputs. It does not run engineering qualification tests.

## Specific work that blocks an exact build

1. **Supplier/application data:** actual supported cell, motor/winding, inverter, brakes/ABS and charging hardware; exact configurations, installation drawings, duty maps and quotes. Current catalog references are not confirmed supply.
2. **Product envelope:** payload/passenger rating, top-speed duration/SOC, weather/aging range conditions, ambient charge performance, life and production economics. The register preserves these as open decisions without silently inventing requirements.
3. **Integrated CAD and mass:** discrete cells and restraints, sculpted pack and chassis, all purchased bodies, full motion/service routes, actual material/process and leaf masses. Resolve the documented clashes and all other swept clearances.
4. **Detailed release engineering:** structure/joint fatigue, shaft/belt loads, braking and suspension, thermal network, HV protection, complete harness/pinouts, software/DBC/calibrations and inspection limits.
5. **Physical evidence:** cell/module qualification, drive bench, charge conformance, structural and brake tests, aero/handling/comfort correlation, whole-vehicle range/mass/performance and applicable compliance.

The [release register](registers/release-deliverables.csv) defines what the future engineer must actually produce, not simply a request to “verify everything.” Do not fill missing torques, fuse ratings, pinouts or cell clamping loads with plausible numbers to make the documents look complete.

## What was completed here

Reviewed all three baseline images and current visual notes; refreshed primary research on critical drive/charge/compliance issues; decomposed subsystems; generated the requirements/interfaces and capacity trade; made an editable coordinate/solid reservation model and exposed its conflicts; defined control/fault behavior, hazards, assembly/service records and verification gates. Source registers are [mechanical](research/mechanical-sources.md), [electrical](research/electrical-sources.md) and [compliance](research/compliance-sources.md). No physical test, supplier approval, structural analysis or CFD was completed. The audit result records documentation/model integrity only.
