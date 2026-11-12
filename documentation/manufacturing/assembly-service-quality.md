# Manufacturing, assembly, service and quality specification

Development issue 0.1 — October 25, 2026, US Central. Codex (GPT-6 family).

This document defines the **manufacturing information and inspections that must exist** for reproducible construction. It does not supply unverified machining dimensions, weld procedures, fastener torques, HV connections or an energization procedure. Those values must be released on drawings/process sheets after engineering qualification. Blank safety-critical values are build holds. A mechanic must never be expected to infer them from the concept images or a supplier family name.

## 1. Configuration and part identity

Use a single controlled product structure with stable internal part numbers and revisions. Suggested convention: `BM-[system]-[four-digit item]`, revision separate. Align with the product specification: 100 energy, 200 drive, 300 chassis/running gear, 400 brakes, 500 thermal, 600 low-voltage/controls, 700 charging, 800 body/ergonomics and 900 assembly/quality. This is a proposed convention, not a statement that drawings already exist. Temporary M/EL/RE register IDs are cross-references, not released part numbers.

Each purchased line identifies manufacturer, exact orderable suffix, revision, quantity, units, approved distributor/source, installation drawing, mass evidence, compliance evidence, inspection class, storage/shelf-life and approved alternatives. A family name such as EMRAX 208 is not an orderable configuration. Each custom item needs its material condition, process, finish, critical dimensions/tolerances and acceptance evidence. Assemblies need an exploded view and complete child list. Count screws, inserts, bearings, spacers, seals, grommets, terminals, heat shrink, clips, coolant and adhesives, including consumables and single-use service parts.

Treat black, silver and tan as finish variants of one engineering core unless an engineering change creates a real structural/component difference. Finish variants require physical approved samples, coating system, substrate preparation, thickness/gloss/color tolerance and masking definition. Rendered colors do not identify paint codes. Serial records identify installed variant and color batch.

Every serialized bike has an **as-designed** record, **as-built** record and **as-maintained** record. A release manifest names the BOM revision, drawing set, harness/netlist revision, software/calibration hashes, supplier firmware, verified safety options, relevant deviations and test configuration. An engineering change evaluates interfaces, mass, safety, tooling, compliance, replacement compatibility and re-verification before approval.

## 2. Incoming acceptance

| Item class | Required receipt evidence | Physical checks and disposition |
|---|---|---|
| Cells | Exact part/revision; lot and individual traceability as available; authorized source; certificate of conformity; supplier acceptance and storage requirements; transport documentation | Packaging/handling damage, pouch dimensions/appearance and supplier-defined electrical incoming checks by battery laboratory; quarantine swelling/leakage/damage or unknown history. Sampling/limits remain supplier-agreed; do not invent an OCV/IR band |
| Motor/inverter/OBC/DC-DC | Ordered configuration, firmware/resolver/connector/cooling variant, serial, test report, installation drawing and restrictions | Mounting dimensions, connector identity, shaft/interface condition, mass, storage condition; controlled acceptance bench test where approved |
| Frame/swingarm/pack case | Material certificates, weld/heat-treatment records, dimensions and inspection reports | Datum-based critical geometry, weld inspection to released criteria, threaded inserts, flatness, bearing bores, coatings and protected bond areas |
| Wheels/tires/brakes/suspension | Exact suffix, rated application, lot/date, supplier fit/torque/service instructions, authenticity | Damage, runout/fit where specified, tire date/rating, seal integrity, correct brake friction pairing; no used or repaired safety-critical parts substituted without approval |
| Harness/connectors/HV components | Exact wire insulation/temp/voltage and contact/seal suffix; fuse/contactor ratings; crimp tooling qualification | Wire ID and lengths; pin-to-pin continuity against netlist; crimp inspection and sampled destructive pull/cross-sections to qualified process; insulation verification only to approved test method |
| Hose/fluid/adhesive/seal | Compatibility specification, batch, shelf life, supplier mixing/cure/storage instructions | Marking, contamination, damage, correct fittings, environmental conditioning; expired material quarantined |
| Lamps/displays/mirrors/screen | Ordered variant and relevant approval/marking, drawing and mounting restrictions | Optical/material damage, markings, correct handedness and orientation, no shading/finish substitutions |

No receipt test replaces design validation. Quality maintains a nonconformance record for anything outside the purchase/drawing specification. Reject, rework, repair and use-as-is dispositions need authorized engineering/quality signatures and impact assessment. A verbal instruction is not a controlled concession.

## 3. Manufacturing definition by process

**Fabricated frame and swingarm:** release datum/fixture strategy, tube or plate sections/material condition, joint preparations, weld symbols, qualified welding procedure and operator requirements, distortion controls, heat treatment if used, machined-after-weld features, inspection access, acceptance class and fatigue-sensitive details. The choice between steel and aluminum must follow the analyzed finished design and qualified production process. A guessed weld bead size or generic wall thickness is not acceptable.

**Battery enclosure/module supports:** specify cell restraint from supplier growth/compression data, electrical barriers, edge radii and abrasion protection, dimensional tolerance at operating temperature, cooling plate interface, sealing, pressure/venting path, service lid, impact protection, fastener sequence and inspection. Any bonded or welded cell tab/interconnect process requires qualified specimens and resistance/strength/corrosion criteria. No cell joining process is selected by this document.

**Machined axles, yokes, brackets and drive supports:** release datum references, alloy/condition, bearing/shaft fits, surface finish, thread specifications, runout/alignment limits, corner/fillet treatment, corrosion treatment, critical feature inspection and serialization requirements. Bearing preload and retention require system calculation plus supplier instructions. Do not assign general tolerance to a safety-critical fit that needs explicit control.

**Body panels/screen/seat:** choose process after production volume and materials are approved. Panel attachment must accommodate manufacturing tolerance and service cycles while controlling vibration and sharp edges. Define inserts, grommets, sealing/drainage, UV/chemical durability, screen optical quality, seat support/foam/cover and water management. All three finishes share the validated substrate/process unless a different finish is separately qualified.

**Wiring and hoses:** release harness board drawing, netlist, splice list, connector cavity table with seals/plugs, wire colors/IDs/cross-sections, shield/bond termination, lengths and tolerances, minimum bends, abrasion/heat protection, clip spacing and slack through motion. Release hose routings, fitting orientation, bend restrictions, clamp styles and fluid compatibility. Supplier maximum lengths and EMC restrictions govern routing. No pin numbers or wire gauges are approved in this issue.

## 4. Joint and fluid schedules — mandatory release records

For **every joint** record: joint ID, mating part revisions, fastener standard/material/grade, diameter/pitch/length, washer/spacer stack, female thread material/engagement, locking method, lubrication/coating condition, tightening method and sequence, approved torque/angle or measured preload, tool range/calibration, reuse limits, witness method and inspection frequency. Define friction variation and relaxation for critical joints. A bolt-marking photograph or paint witness is not proof of correct preload.

Critical examples include wheel axles, caliper/rotor mounts, steering stem/yokes, handlebar clamps, suspension pivots/shock, swingarm, motor/drive support, pulley retention, pack/frame mounts, stand pivot and brake banjo/hose fittings. Battery electrical joint requirements must additionally address contact resistance, coating, insulation and thermal cycling. Exact values remain unresolved until the actual joint is designed.

For **every fluid system** record approved fluid, capacity and fill condition, cleanliness, compatible wetted materials, fill/bleed equipment and method, leak/pressure test, operating pressure/temperature, expansion allowance, drain/recovery points and environmental disposal. Brake fluid and coolant are not interchangeable process materials. Record measured filled quantities and include their mass in the complete-vehicle mass.

## 5. Proposed assembly traveler structure

Sequence is a planning baseline; detailed packaging and process hazards may change it. Each step references its released work instruction, fixture/tool IDs, measured values/limits, operator/date and independent hold-point signoff. **HOLD** prevents progression until the listed evidence is accepted. Specialized pack assembly and energized work use separately approved qualified-person procedures and facilities.

| Station | Operations to define in released work instructions | Required evidence / hold point |
|---|---|---|
| A00 Build authorization | Identify serial/configuration; verify BOM/drawing/software revision; review concessions; confirm personnel/tools/facility | Kit is complete; no unresolved build-critical TBD; all tools calibrated; HOLD for configuration approval |
| A10 Chassis receipt/fixture | Inspect frame/swingarm; establish datums; verify steering/pivot/mount relationships | Dimensional report and weld/material records; discrepancy blocks assembly |
| A20 Running gear | Fit approved bearings/seals/steering/suspension/wheels; establish alignment and travel | Joint records; bearing settings; tire/rim match; wheel alignment/runout; motion inspection |
| A30 Brake system | Install matched hydraulic assemblies, approved routing and sensor mounts; qualified fluid fill/bleed | Correct friction pairing; hydraulic integrity and lever/pedal travel; independent critical-joint check; HOLD before rolling test |
| A40 Drive module | Fit motor, supported reduction/final drive and guards per released drawing | Shaft/belt alignment and tension at specified suspension positions; pulley retention; motor-side load acceptance; clearance report |
| A50 Cooling modules | Install radiators/fans/pumps/reservoirs/hoses and sensor hardware | Leak/flow verification to approved limits; connection polarity; drain/access; record coolant quantity and mass |
| A60 Vehicle harness/LV | Route harness, bonding, controllers, LV source, instruments and lights; check unpowered netlist | Pin/cavity verification and continuity; abrasion/strain/steering travel; no energized HV integration yet; software IDs recorded |
| A70 Pack acceptance | Receive separately qualified serialized complete pack; review module/cell genealogy, protection and enclosure acceptance | Pack test certificate and incoming status; no unapproved pack rework; HOLD for battery/electrical acceptance |
| A80 Pack mechanical installation | Use rated engineered support/fixture; secure pack and any required structural interfaces | Support route and lift condition documented; joint records; installed barriers/vent path; retention and removal access |
| A90 Charging/HV integration | Qualified controlled process only after electrical release; verify routing and connector configuration against drawings | Electrical safety release, isolation/bond/interlock evidence, no exposed/incorrect connections; HOLD before energy-bearing commissioning |
| A100 Body/rider equipment | Fit saddle, pegs, bars/levers, screen, panels, mirrors, inlet cover, stand and finish details | Full-lock/bump checks repeated with body fitted; labels visible; no masked drains/cooling/vents; all road equipment installed |
| A110 Controlled commissioning | Perform separately approved staged commissioning and diagnostic procedure at suitable facility | Raw logs; defined inhibits/fault response; configuration hash; independent signed release before powered motion |
| A120 End-of-line | Complete below tests; mass/axle load/geometry and visual audit | No missing mandatory result; defects closed or authorized; HOLD for test-use or delivery release |
| A130 Handover | Bind as-built dossier, warnings, service/owner information and allowed operating scope | Named reviewer approves specific use. Prototype test permission is not production certification |

No technician should consult the styling render to resolve mounting orientation, left/right handedness, absent spacers or wire routing. If an installation needs a decision not in the package, stop that operation, record the ambiguity and release a change.

## 6. End-of-line control plan

Production EOL verifies workmanship/configuration; design validation remains separate. The EOL procedure must define test voltage/energy, safe states, equipment and acceptance criteria from the qualified design. It cannot simply run every high-stress design test on each finished bike.

| Characteristic | Required record | Release condition |
|---|---|---|
| Identity | Vehicle/pack/motor/controller serials; software and calibration hashes; color/accessory configuration | Exact approved match |
| Mechanical completion | Critical-joint completion; alignment; free travel; tire fit/pressure; guards; stand; controls | All released limits satisfied; no open critical inspection |
| Braking | Leak/integrity and brake function checks; sensors/telltales; installation records | Released EOL limits met; no unresolved brake faults |
| LV and road equipment | Lamps, horn, display, stop/stand/charge interlocks and diagnostic communication | Correct function and identification |
| Electrical protection | Approved isolation/bond/interlock/precharge/contact feedback and discharge evidence | Pass thresholds established by electrical safety lead; test excludes incompatible electronics where procedure requires |
| Cooling | Leak, fan/pump command and measured response; fill/bleed; temp-sensor plausibility | Declared flow/pressure/temp response achieved |
| Powered function | Low-energy controlled drive/regen checks to approved procedure; charge handshake/function where specified | Correct direction, bounded torque and state transitions; no active unexplained faults |
| Mass and geometry | Complete and axle weights; key hard points and finish configuration | Reconcile design; goal miss is product decision, not production tolerance waiver |
| Cosmetic/label | Physical finish sample, surface defect criteria, label content/location and safety markings | Correct variant and legible permanent required labels |
| Final audit | Independent configuration review and disposition log | Authorized release for stated scope |

## 7. Service information deliverables

Every service procedure needs applicable serial/revisions; symptoms and diagnostic decision tree; required qualifications/tools; support/energy-isolation conditions; component access; exact drawing references; measured wear/damage criteria; consumables and one-time fasteners; joint settings; reassembly inspection; functional check; log entry and release authority. Publish no general pack-opening procedure for unqualified owners.

Provide separate manuals for rider operation, ordinary maintenance, qualified workshop service and emergency response. Rider instructions explain charging state, limits/derates, tire/loading information, fault warnings, stand/parking, wash/storage, long-trip charging planning and what to do after a crash or battery warning. Workshop instructions cover controlled pack replacement, coolant service, brake/suspension/wheel service, belt inspection/alignment/tension, electrical fault diagnosis, firmware updates/recovery and damaged component quarantine. Emergency information locates energy sources/isolation, lifting/cut exclusion zones and vent hazards using the final vehicle configuration; it must be reviewed with battery/electrical safety specialists.

Do not set calendar or mileage intervals without duty/wear evidence and supplier limits. A draft maintenance table should list tires, brake pads/discs/fluid/hoses, wheel/steering/pivot bearings, suspension, drive belt/pulleys, structural fasteners/inspection, cooling fluid/hoses, HV/LV connections, LV source, lights, stand and pack health. The initial release interval is the conservative validated/supplier-supported one; field data can support controlled revision.

Pack removal is a planned workshop lift, not a hand-swapping feature: the current allocation is approximately 97 kg. The released design must show the pack mass/CG, lifting attachments, fixture, support sequence, center-of-gravity changes and access with ordinary consumables. Test the actual route on a representative buck before promising a service time.

## 8. Supplier and production controls

Safety-critical suppliers need change notification, traceability and agreed acceptance limits. Qualify alternate sources by functional/form/fit/environmental and software compatibility, not catalog similarity. Store certificates and authorized drawings under appropriate distribution rights; a public repository may link restricted installation documents while the build package identifies how a qualified team obtains them. Secrets, firmware signing keys, credentials and payment/network certificates never belong in the public package.

Quality planning requires process failure analysis, measurement-system checks, gauge calibration, fixture validation, inspection sampling justified by risk, special-process qualification and retention policy. No Cpk, yield or zero-defect performance is claimed before production data exist. Close the loop from field failure to affected serials/lots, containment, root cause, engineering change, re-verification and any required regulatory reporting.

The practical reproducibility test is an independent appropriately equipped team assembling a representative bike using only the released files and authorized supplier information. Any undocumented clarification becomes a controlled correction. Until that audit and the [release register](../registers/release-deliverables.csv) are complete, this project remains development documentation rather than a build-anywhere kit.
