# Bavuso Motors — product definition, development baseline B0

Revision B0 · October 25, 2026 · Codex, GPT-6 family · engineering development specification.

## What this package controls

The product is one compact electric road motorcycle for comfortable highway travel, with optional removable saddlebags and three current appearance references: matte black, matte silver and matte tan. The geometry in the images is visual intent, not source geometry. The latest [design notes](../design/design%20notes.md) supersede the white finish in the historical final-review folder. There is no second hybrid product in scope.

The deliverable is a traceable definition for engineering development. A build release requires the actual drawings, component configurations, harnesses, software and test evidence listed in the release register. An unresolved field means work remains; it does not grant a mechanic discretion to invent a specification. No released build configuration exists yet.

## Requirement hierarchy

1. Owner requirements retain their original meaning. Engineering targets cannot quietly weaken them.
2. Product decisions proposed here support layout work and remain explicitly provisional.
3. Supplier ratings describe a particular part and conditions, not vehicle qualification.
4. Screening calculations narrow options. Simulation and physical validation require their own records.
5. Assembly instructions may reference only a released configuration and approved workmanship documents.

The [requirements register](registers/requirements.csv) assigns a verification method and evidence needed to every requirement. The CSV is the controlled index; narrative gives rationale.

| Owner requirement | Working interpretation | What must establish it |
|---|---|---|
| 200 miles | 70 mph highway calculation baseline; ordinary comfortable posture | Defined test conditions, measured energy and road load, then full-distance test |
| 125+ mph | Strictly above 125 mph; 130 mph screening point is engineering headroom | Loaded low-SOC motor map, tire/drive suitability, thermal evidence and closed-course test |
| Tesla charging compatibility | Actual supported station use, including access and payment | Electrical/protocol qualification and authorized network tests; inlet shape alone is insufficient |
| Prefer under 400 lb | Complete ready-to-ride bike including cells, fluids and required equipment, rider excluded | Reconciled configuration-specific BOM and calibrated scale result |
| Highway comfort / confidence | 77 mph aero and comfort design speed; compact clean form, broad rider fit | Rider buck, aerodynamic forces and moments, handling and comfort test program |

Weight is the first goal the owner would discuss relaxing slightly. No replacement ceiling has been accepted. Estimated 433–446 lb is a feasibility gap, not the requirement.

## Working architecture

Use a narrow central high-energy pouch pack, single frame-mounted PMSM, one fixed reduction and a rear synchronous belt. Keep conventional front forks and a double-sided swingarm as the study architecture. Hydraulic brakes remain capable independently of regen. Include ABS and investigate a matched motorcycle stability-control system. Retain standards-based native NACS AC/DC charging, a separate onboard AC charger and EV charge controller, a traction controller, supervisory vehicle controller, BMS, isolated DC/DC and independent low-voltage energy reserve.

Two battery paths remain active until the measured drag and supplied cell data close them:

- **B0-A, energy-led reference:** 100s8p, 800 SA504 reference cells, 30.056 kWh typical nominal. Existing mass allocation 196.35 kg / 432.88 lb before allowance. At assumed CdA 0.33, still-air new-battery screening range is approximately 219 miles at 70 mph. This path presently misses preferred mass.
- **B0-B, aero-led investigation:** preserve 100 series groups but investigate 7p, 26.299 kWh typical nominal. Fewer cells reduce both mass and charge/discharge current capability. Success depends on a lower comfortable-rider drag area and real integration mass, not a smaller number on a specification sheet. The [trade sweep](research/configuration-trades.csv) quantifies the necessary drag for each mass case. It is not a selected pack.

Keeping series count constant isolates parallel-count trades from the winding/voltage issue; other series counts remain possible after motor, charger and station voltage reviews. The cell count does not establish approved module construction. Do not build a pack from this notation.

Current motor candidates are EMRAX 208 liquid-cooled MV and LV+100% windings. The older handoff's v1.5 continuous rating is superseded for current supplier comparison by v1.7, with 47 kW liquid-cooled continuous rating under stated conditions. LV+100% may improve loaded speed at low voltage at the expense of phase current. Published motor cooling still requires airflow. Product transition and application support must be resolved before procurement. See the mechanical system report for detailed comparison and sources.

## Proposed screening conditions, not additional owner commitments

Reference rider including gear is 90 kg. Initial range model uses level road, still air, air density 1.225 kg/m³, rolling coefficient 0.015, 90% battery-to-wheel efficiency and 300 W auxiliary load. Ninety percent of nominal energy is allocated to a trip. This is a combined availability assumption, not an approved battery SOC window. Minimum cell energy, degradation, cold weather, fan power and headwind require separate cases.

The 200-mile baseline is distinct from a 10–80% charging leg, which uses less energy, and from range at 77 or 125 mph. Range advertising conditions and end-of-life performance have not been selected. There is no established time-to-charge promise. Initial research considers roughly 30–50 kW DC, subject to cell/thermal/station limits, and up to 6.6 kW AC subject to a compatible charger. Support for 120 V charging remains an open charger requirement.

Proposed 60 kW shaft peak and 45 kW continuous are sizing targets, not achieved performance. At the older 0.35 drag reference, calculated demand at 125 mph is approximately 41 kW shaft and 74 Nm at a 3.1 ratio, leaving little continuous torque margin with the current motor sheet. All speeds require mapped efficiency, coolant/air conditions and loaded pack voltage.

## Appearance and human interface

Preserve the rising front screen, restrained angular body planes, narrow knee contact region, padded flatter saddle, relaxed swept-back bars, dark functional lower components and small upper-side BAVUSO wordmark. Engineer screen brackets, mirror fields, panel edges, lighting visibility and service fasteners rather than copying generated hardware. The rendered rear seat area does not confer a passenger rating.

Reserve rider adjustment through bar/lever setup and seat options, then verify actual reach, ground contact and joint angles. A low seat with excessive width can worsen ground reach. A calm silhouette does not prove stable crosswind behavior. A screen that reduces torso force can worsen helmet buffeting; evaluate both. Bag mounts must connect to a rated load path, not unsupported cosmetic panels. Base-range and mass tests exclude optional luggage unless that becomes the declared configuration.

Finish codes, gloss tolerance, resin/alloy, texture, physical color masters and badge artwork remain drawing-controlled outputs. Black/silver/tan references are not paint standards. All options use one common mechanical configuration unless a documented change establishes otherwise.

## Open product decisions and bounded assumptions

| Decision | Development assumption until resolved | Why it matters |
|---|---|---|
| Rider/payload/GVWR | Solo 90 kg is only a model case; no rated capacity | Frame, tires, brakes, suspension and support stand cannot be released without load envelope |
| Passenger | No passenger claim; preserve study space only | Rear structure, pegs, handles, seat and certification |
| Saddlebags | Removable accessory concept, capacity/rating open | Subframe, loaded CG, clearance, drag, stability |
| Top-speed duration and SOC | Map short and sustained cases; release duration open | Motor sizing, winding, cooling and low-SOC capability |
| Environment | Model nominal plus hot/cold/wet cases; qualification limits open | Pack heater/chiller, sealing and derating |
| Life/warranty | No service-life claim yet | Cell aging, fatigue spectra, repair strategy |
| Production quantity/price | Use configurable prototype parts; no target cost | Supplier access, custom tooling and manufacturing architecture |
| Market | US applicability review is first study; not global homologation | Equipment, labels, lighting, braking and administrative obligations |

Progress can continue on parametric packaging, supplier questions and component characterization. These assumptions must not be converted into released limits without review.

## Change control

Use identifiers BM-100 energy, BM-200 drive, BM-300 chassis, BM-400 brakes, BM-500 thermal, BM-600 low-voltage/control, BM-700 charging, BM-800 body/ergonomics and BM-900 assembly/quality. A custom item's future drawing number derives from that family; no identifier here asserts an actual manufactured part.

Each change record shall contain issue, proposed revision, affected part IDs and requirements, mass/CG/cost/energy impact, interface changes, evidence and disposition. Changes to cell, winding, ratio, wheel/tire, brake, frame, software limits or charge controls trigger cross-system review. Black/silver/tan are finish variants, not permission for separate untracked mechanical designs.
