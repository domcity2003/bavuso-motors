# Mechanical systems definition — development baseline M0

October 25, 2026, US Central. Prepared by Codex, GPT-6 family. **Development specification; no mechanical assembly is released for manufacture or riding.**

This document translates the owner's current black/silver/tan design into engineering work packages. It replaces no owner goal. Sources are logged in [mechanical sources](../research/mechanical-sources.md); the [component register](../registers/mechanical-components.csv) decomposes the physical scope. A register row is an accounted-for function or assembly, not evidence that its design is complete. `TBD` is an explicit unresolved input, never permission for an assembler to improvise.

## 1. Architecture to develop

Use one frame-mounted liquid-cooled motor, one fixed reduction, a double-sided swingarm, telescopic fork, hydraulic friction brakes with matched ABS, cast/forged aluminum road wheels, and a replaceable chassis-supported pack enclosure. Start with fabricated metal chassis studies, comparing welded steel tube against welded/bolted aluminum using complete joints, fatigue, production quantity and inspection cost. A lighter raw material does not establish a lighter assembly. Keep the pouch cells outside the primary load path.

Develop a belt final drive for the road product. Use a chain only on a deliberately documented development mule when ratio experiments justify it. Do not carry mule handling, efficiency or mass results into a belt product without reconciliation. Avoid a hub motor's added rear unsprung mass, two-motor redundancy overhead, and a gearbox until a quantified requirement demands them.

The current approximately 433 lb allocation remains an allocation. Forks, yokes, bars, damper, springs and steering hardware share only 10 kg; chassis and swingarm share 16 kg; wheels, tires and bearings share 17 kg; drive support, reduction and guards share 5 kg. These are especially tight boundaries. Added brackets, bearing supports, remote preload devices or passenger equipment must be counted, not hidden in “integration.”

## 2. Appearance-to-engineering reconciliation

The inspected [silver baseline](../../design/baseline%20silver.png) shows compact full bodywork, swept bars, padded two-level seat, exposed front fork, visible rear shock and lower belt run, road wheels, mirrors, lamps and side apertures. Preserve that intent subject to these corrections:

| Render feature | Engineering consequence | Release evidence |
|---|---|---|
| Tall clear screen on slender supports | Aerodynamic pressure, vibration, optical distortion, screen-edge contact and mounting fatigue | Drawing, material/process, pressure/load spectrum, deflection and fatigue tests, rider sightline assessment |
| Large clean battery side | Under-panel space must contain real pack/frame/cooling and pack-removal route | Sectioned CAD with all installation and service envelopes |
| Motor-like circular cover near pivot | Neither output center nor bearings can be located by image | Loaded drive geometry and supplier installation drawing |
| Exposed belt and crowded rear hub | Require guards, brake/sensor clearances, debris rejection and rear-wheel removal | Suspension sweep and service demonstration |
| Visible long seat/tail | Does not authorize passenger loading | Defined solo/pillion/luggage load case and subframe tests |
| Apparently simple front brake | Far-side components and ABS are not reliably represented | Hydraulic schematic and complete matched BOM |
| Generous side cooling slots | Aperture appearance gives no flow or heat-rejection credit | Duct/radiator/fan pressure-flow model and tests |
| Narrow lower belly | Protect pack from bump/kerb/lean loads, preserve drain and service access | Swept-volume model, impact analysis and physical inspection |

Black/silver/tan share one mechanical design. Finish variants change coating/trim records, not geometry unless explicitly revision-controlled. Render pixels are not metrology.

## 3. Geometry, coordinate convention and CAD deliverables

For the mechanical model use a right-handed vehicle system: **X forward, Y left, Z up**. Put the origin on the ground vertically below the rear axle at the declared reference loaded condition; distinguish that condition from fully extended or curb. State rider mass, tire pressure, sag and load for every hard-point export. This convention is a proposal; if the central project datum differs, publish one transformation and use it consistently.

Existing studies explore 1,400–1,450 mm wheelbase, 24–26° rake from vertical, 95–110 mm trail, 780–820 mm seat height and 120–140 mm wheel travel. None is a manufacturing dimension. Use **1,420 mm / 25° / 105 mm** only as the nominal kinematic study point, aligned with the package reservation model. Tire radius, fork offset, axle offset, fork angle and sag must reconcile; they are not independent knobs. In a simplified rigid front end, trail = (front rolling radius × sin(rake) − total perpendicular fork/axle offset) / cos(rake). With nominal front geometric radius 299.9 mm, 25° rake and 105 mm trail imply roughly 31.6 mm combined offset. That calculation ignores loaded tire deformation and fork flex and does not select a yoke.

Every CAD release must contain: tire supplier envelopes including growth/deflection; wheels/rotors/calipers; fork extended/compressed bodies and travel stops; steering axis and full lock; swingarm/pivot/axle adjustment; shock and linkage at full travel; belt pitch paths; pack case and removable lid; motor's rotating and stationary exclusions; electronics connectors; hose/cable bend and movement envelopes; rider boots/knees/hands; lamps/mirrors/plate; stands; tools and removal routes. Include optional bags in a separate configuration.

Hard points to export in a machine-readable file: steering bearing centers, fork axes, axle centers, swingarm bearings, shock eyes/linkage pivots, output shaft, pack mounts, rider seat reference, pegs, grips, stand pivot/foot, lifting supports, luggage mounts, inlet center and lamp reference axes. Record XYZ, axis direction, reference condition, tolerance owner, revision and evidence. A point without a load direction or installation envelope is insufficient.

## 4. Drive selection: a current revision changes the trade

The current [EMRAX 208 v1.7 sheet](https://emrax.com/wp-content/uploads/2026/08/EMRAX_208_datasheet_v1.7.pdf) rates the liquid-cooled variant at 47 kW/75 Nm continuous and 86 kW for 30 seconds, not the older sheet's 52 kW/84 Nm and two-minute peak. LC mass is 10.3 kg, body Ø208 × 85 mm, protection IP66, speed limit 7,000 rpm. Cooling conditions include 6 L/min and maximum 50°C inlet; adequate airflow is also required. The maker flags a transition away from these legacy models. The sheet offers MV (420 V peak reference, 0.38 Nm/Arms, 220/400 Arms continuous/peak) and LV+100% (340 V, 0.30 Nm/Arms, 280/500 Arms). Their nominal-load speed constants are 18.94 and 24.10 rpm/V respectively. These are candidate winding references, not qualified operating maps or available order codes.

**Develop both MV and LV+100% winding studies before ordering.** At the existing 3.1 ratio, 125 mph needs approximately 5,304 motor rpm. At 280 V, the published nominal-load constants screen to 5,303 rpm MV and 6,748 rpm LV+100%. This makes the latter a useful low-SOC contender. It is not proof that it supplies the required torque at that speed; a speed constant is no substitute for voltage/current-limited maps. Its greater current per Nm can raise copper/inverter loss. Its 500 Arms peak demand exceeds the MV's but sits below the legacy CM200DX headline peak reference; 280 Arms continuous sits close to its 300 Arms reference. Matching requires actual temperature-dependent inverter limits, modulation convention, resolver and sensor compatibility, cable inductance, switching strategy and motor-temperature mapping. Do not issue a motor part number without winding, cooling, sensor, connector and shaft configuration suffixes.

The following arithmetic screens use published constants rather than a validated current/voltage map. They do not establish the feasible envelope. The inverter's 300/740 Arms figures are the **legacy project reference not independently refreshed in this review**; obtain the current sheet before relying on them.

| Screen | MV reference | LV+100% reference |
|---|---:|---:|
| Nominal-load speed at 340 V | 6,440 rpm | 8,194 rpm before 7,000 rpm limit |
| Nominal-load speed at 280 V | 5,303 rpm | 6,748 rpm |
| Phase current from 73.8 Nm / torque constant | 194.2 Arms | 246.0 Arms |
| Gap below published motor continuous current reference | 25.8 Arms | 34.0 Arms |
| Gap below legacy inverter 300 Arms continuous reference | 105.8 Arms | 54.0 Arms |
| Phase current screen for 150 Nm | 394.7 Arms | 500.0 Arms |
| Gap below legacy inverter 740 Arms peak reference | 345.3 Arms | 240.0 Arms |

At CdA 0.35 and the existing steady-road model, 125 mph requires about 39.76 kW wheel / 40.99 kW motor shaft / 73.8 Nm. Thus the updated 75 Nm continuous torque reference leaves only about **1.2 Nm** of nominal torque headroom. Current headroom alone cannot override the separate motor thermal torque limit. A 45 kW continuous design proposal does not prove that the candidate achieves 45 kW at this speed and ambient. A 130 mph development point needs another map check; quoting a 47 kW power headline alone is insufficient. Either qualify this point, improve actual drag, or select a different supplier/motor with complete maps. Do not silently lower performance.

Required supplier application package: drive duty cycle, loaded battery voltage and ripple vs SOC, torque/speed map, ambient/coolant conditions, motor installation airflow, fatigue loads, phase-current definitions, rotor inertia, mount/shaft drawing, output side-load limits and thermal sensor calibration. Obtain supply/lifecycle support and replacement options before freezing structure. No supplier request has been sent.

## 5. Reduction, shaft support and belt geometry

Keep 3.1:1 as the calculation reference, not a chosen pulley set. A tooth-count pair such as 20:62 merely yields the ratio; it does not establish tooth capacity, minimum pulley diameter, speed, wrap, belt width, availability or bending life. Gates currently offers motorcycle-specific Moto X5/X9 belts and Moto XF front sprockets, but does not establish a complete sized Bavuso drive from an online headline. Submit torque reversals, speed/time histogram, contamination, temperature, axle movement, alignment and life targets for application sizing. [Gates motorcycle systems](https://www.gates.com/us/en/innovations-and-solutions/urban-mobility-and-powersports-solutions/synchronous-belt-drives-for-motorcycles.html)

At 150 Nm motor torque and a hypothetical 40 mm input pitch radius, tight-side minus slack-side belt tension is 3,750 N. **Bearing radial load is not 3,750 N**: it depends on both belt spans, preload, directions and dynamics. Determine bearing reactions from a shaft free-body diagram with span forces and pulley overhang. Include torque reversals under regen, tire recontact and bumps. Do not apply the motor bearing numbers as permissible loads.

Preferred study: supported output shaft near swingarm pivot, connected to motor without transmitting belt radial load into unqualified motor bearings. Compare this with a directly supported motor-output pulley only if EMRAX explicitly approves loads. A jackshaft adds two bearings/housings, coupling, seals, shaft and tolerance stack; debit the 5 kg drive allocation. Coaxial swingarm/output geometry controls center-distance variation but complicates packaging; an offset motor is acceptable if full-travel belt length/tension variation is qualified. Do not invent a tensioner to fix unanalysed geometry.

Calculate pitch-center distance over every axle adjustment and suspension state. Determine minimum wrap/engaged teeth, pulley flange clearances, tracking under swingarm flex, stone ingress, guard clearances and replacement access. Use actual supplier belt installation/tension method and temperature correction. Establish wheel alignment from chassis datums; swingarm hash marks alone are not final inspection.

Bearing selection inputs: radial/axial spectrum, revolutions, shock/static loads, bearing span/overhang, housing/shaft temperatures, contamination, sealing, lubricant and reliability/life target. SKF's basic life form is L10 = (C/P)^p in million revolutions; speed converts it to hours. This is only a first fatigue screen, not an impact/seal/water-ingress qualification. [SKF rating-life reference](https://www.skf.com/binaries/pub12/Images/0901d196802809de-Rolling-bearings---17000_1-EN_tcm_12-121486.pdf)

Specify fixed/floating bearing strategy, fits and internal clearance with thermal expansion. Retention must not load a bearing through the wrong race during assembly. Shaft shoulders, splines/keyways, circlips, fretting, bending fatigue, pulley locking and overspeed containment require drawings and review. No generic shaft diameter is selected here.

## 6. Wheels, tires, suspension and steering

Candidate road tire family: MICHELIN Road 6 in front 120/70 ZR17 and rear 160/60 ZR17; manufacturer listings support those sizes. [Michelin](https://www.michelin.co.jp/motorbike/tyres/michelin-road-6) The actual SKU, approved rim widths, load/speed capacity, pressures, carcass construction and dynamic envelope must be obtained for the launch market and selected wheel. Do not choose pressure from another motorcycle or interpret sidewall maximum as vehicle operating pressure. Measure loaded rolling radius for speed/control calibration; tire circumference changes with load, wear and pressure.

For the first functional prototype, source a coherent front end and wheel/brake interface from a documented road-motorcycle supplier rather than mix caliper offset, fork spacing and rotor geometry. A donor assembly is a test reference, not automatically the production design. Record donor model/year/part revisions, condition and rated application; requalify increased loading and altered geometry. No particular donor is selected without dimensional data.

Rear shock selection depends on wheel/shock motion ratio r = wheel travel / shock travel. For locally constant r, wheel spring rate is approximately shock spring rate / r²; progressive geometry adds terms. Consequently “130 mm travel” does not select a shock stroke or spring. Model full leverage curve, tire force, bump-stop force, damper velocity, spring coil bind, top-out, bearing angular misalignment and adjuster/tool access. Evaluate direct-mounted shock first to reduce parts, but do not sacrifice rate progression or packaging to it.

Complete suspension definition includes sprung/unsprung masses at each end, static and rider sag, travel reserve for payload cases, spring/preload range, damper force-velocity curves across temperature, friction, bump stops, top-out control, oil/seal service and tire clearance at combined bump/steer. Values are not borrowed from another bike solely because curb weight looks similar. Include mass of preload hardware, linkage bearings/spacers and guards.

Steering must include matched stem/bearings/races, machined yokes, handlebar clamps, positive stops, lock provision, cable loops, hose restraint and anti-chafe. A damper is a tuning element, not compensation for unstable geometry or assembly error. Characterize wobble/weave modes over speed, payload, tire wear/pressure, luggage, braking and gusts; compare with physical dynamics tests by qualified riders on controlled facilities. “Heavy enough for wind” is not an acceptance criterion.

## 7. Brakes and rider controls

Reserve dual 300–320 mm front rotors and one 220–240 mm rear rotor while evaluating a lighter single-front-disc system through stopping, repeated-stop heat, stiffness and ABS qualification. Neither disc count is selected from rendering. The approximately 447 kJ translational kinetic energy at 125 mph for the reference 286.35 kg moving mass excludes rotating wheels/motor and descent energy. The rotor cannot be sized from energy alone: brake share, repeated stops, heat transfer, pad temperatures, fluid boiling, contact pressure and tire grip govern.

Select master cylinder, calipers, pads, disc diameter/thickness/offset, hoses, fluid, ABS valve block and wheel sensing as one compatible system. Brembo explicitly distinguishes master-cylinder applications for differing caliper/disc arrangements; its family names are not arbitrary styling choices. [Brembo application guidance](https://www.brembo.com/en/news-archive/brembo-for-honda) Calculate lever force/travel, hydraulic ratio, thermal expansion/knockback, hose volumetric compliance and residual-pressure behavior, then test.

Bosch publishes motorcycle ABS and MSC options including sensor-based dynamics control. [ABS](https://www.bosch-mobility.com/en/solutions/driving-safety/antilock-braking-system-2w/), [MSC](https://www.bosch-mobility.com/en/solutions/braking-systems/motorcycle-stability-control/) An ABS ECU purchased separately is not an integration calibration. Require supported hardware/software, wheel encoder geometry, tire circumference envelope, mounting orientation, diagnostic behavior, torque/regen coordination and tested fault response. A regen rejection must leave predictable independent friction braking. Do not rely on regeneration for stopping compliance.

Routing drawings must show wheel/fork motion, safe hose slack, minimum bend radii, clips, steering-stop exclusion, rotor heat zones and service bleed access. Brake fastener retention and tightening follow matched supplier specifications plus joint validation. Foot controls include pedal pivot bearings/bushings, return spring, stops, master pushrod alignment/free play, tip and brake-light sensing. Hand controls include lever reach, throttle return/plausibility, switch placement and gloved operation. No hydraulic pipe or fastener part number is released until interface dimensions are real.

## 8. Structure, load cases and verification inputs

Loads must be derived from a declared maximum operating mass, payload distribution and duty life. The 90 kg range-model rider is not the payload rating. Preliminary finite-element sensitivity can begin with the current mass model, but cannot qualify frame dimensions while gross vehicle mass and passenger/luggage use remain undefined.

| Case | Required inputs and model | Evidence before release |
|---|---|---|
| Maximum braking | Measured CG height, wheelbase, axle loads, deceleration and tire forces; front load transfer approximately m*a*h/L for simple level-road model | Instrumented braking and strain correlation; no rear load below zero in model without lift treatment |
| Acceleration/regen | Torque ramp, max tire force, swingarm/output coordinates, rotor inertia and backlash | Drivetrain shock/traction tests and mount strain |
| Pothole/kerb/bump | Tire response, speed, road profile, damper/bump-stop curves, wheel inertia | Nonlinear transient or correlated rig/road load history |
| Cornering + bump + braking | Combined loads, lean, structural flex, tire grip ellipse | Agreed combined-case matrix and measured response |
| Payload/luggage | Seat/peg/bag load locations and ratings, dynamic vertical/fore-aft loads | Subframe/attachment fatigue and handling tests |
| Parked side load | Stand ground friction/slope, wind load, charge-cable pull, luggage | Tip margin and stand/attachment strength tests |
| Pack retention/impact | Pack mass/inertia, inertia loads and strike/crash envelope; enclosure function | Attachment, crash/abuse and isolation evidence |
| Lifting/tie-down/recovery | Jack points, strapped transport, wheel removal and tow forces | Marked allowable supports and proof tests |
| Durability | Service distance/time, corrosion exposure, rough-road spectrum and reliability | Defined fatigue acceptance with inspected welded joints and tests |

Structural drawing release must specify material grade/condition, thickness, bend radii, weld procedure/joint details, local reinforcement, heat-affected-zone basis, post-weld machining/heat treatment where applicable, coating and corrosion compatibility. Tubes are not selected by diameter alone. Aluminum weld strength may differ substantially from parent temper; do not use parent yield everywhere. Battery mount stiffness and clearances must accommodate real thermal expansion without overconstraining the pack or opening seals.

Track static yield/ultimate and fatigue margins separately. A single global “safety factor 2” does not close buckling, weld fatigue, bearing seats, bolted joints or impact. Evaluate steering-head and swingarm stiffness jointly with dynamics rather than maximize stiffness everywhere.

## 9. Manufacturing, joints and service definition

Proposed assembly inspection datums: chassis center plane; steering bearing axis; swingarm pivot axis. Control their relationship and wheel planes after welding. Machine bearing seats after the required stress/heat process, not before an unqualified distortion step. Tolerances must come from functional stack-ups: belt alignment, caliper centering, rotor runout, bearing fit/preload and wheel tracking. Do not assign blanket ±0.1 mm across a welded frame.

For every safety-related joint, issue a joint record with stack material/thickness, fastener standard/grade/coating/length, engagement, washer/insert/nut type, clamp-load target, torque-angle or torque process, friction condition, reuse policy, locking feature, access, corrosion isolation and inspection. Derive tightening from supplier data and joint trials; do not fill a generic torque table with invented numbers. Bonding, riveting, welding and adhesive joints need their own process and rework criteria. Structural, brake, wheel and suspension fasteners are separate controlled items, not a mass allowance called “misc.”

Pack removal: isolate and verify through a released HV procedure before mechanical operations; use a stable rated lifting fixture at defined pack hard points, restrain CG throughout removal, disconnect services in prescribed order, preserve seals, and inspect/retest on reinstallation. A 90–100 kg pack is not a two-person casual lift. Define whether removal is downwards or sideways using CAD and an actual fixture study; body-panel removal must not leave the supported frame unstable. The rendering's apparent lower cover is not a chosen release route.

Document routine rear-wheel/tire replacement without opening the battery; belt replacement path; brake pad/rotor access; steering/swingarm bearing service; cooling fill/bleed/drain; shock/fork removal; lamp and body-panel replacement; corrosion inspection; crash/drop inspection; lifting and tie-down points. Service intervals remain TBD until supplier requirements and durability data exist. Include tool sizes, replacement seals, single-use fasteners and inspection limits in the eventual mechanic manual.

## 10. Mechanical release checklist

1. Freeze payload, passenger/luggage configuration, operating climate, top-speed duration/SOC and durability target with the owner.
2. Secure dimensioned component installation drawings, motor maps/current revision and supplier-supported brake/ABS interfaces. Source continuity must be documented.
3. Complete constrained package CAD and rider buck; extract real masses, centers of mass and all swept clearances. Resolve primary structure before styling surface freeze.
4. Select winding/inverter pair and supplier-sized transmission. Verify low-SOC torque/speed, thermal conditions, phase-current limits and shaft side loads.
5. Complete loads, structural/fatigue calculations, suspension kinematics and brake thermal/hydraulic models with independent review.
6. Issue controlled drawings, BOM, tolerances, joint records, process plans and assembly/service instructions. A mechanic must not need to invent any dimension or tightening value.
7. Build and inspect fixtures/subassemblies; correlate tests, revise models, then progress to a controlled prototype and vehicle validation. The present documentation records this work; it does not claim it has happened.

Unresolved quantities and exact selections are visible in the register. Mechanical completeness is achieved by closing those rows with evidence, not by replacing TBD with attractive numbers.
