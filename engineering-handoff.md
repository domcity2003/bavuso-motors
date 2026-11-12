# Bavuso Motors — engineering handoff v0.1

**October 25, 2026, US Central. Prepared by Codex (GPT-6 family).**

Purpose: give Dominic an engineering basis for shaping the motorcycle, challenge conventional component choices, and expose the decisions that still determine feasibility. This is a concept specification and research handoff. It is not a released design, a construction package, or evidence that the five goals have already been met together.

**Supersession note, October 25, 2026:** the current [B0 engineering development package](documentation/README.md) expands and supersedes this historical v0.1 where inconsistent. In particular current EMRAX208 v1.7 LC ratings are 47 kW / 75 Nm continuous and 86 kW for 30 seconds, with airflow and model-transition constraints. The older motor ratings below are retained as research history, not current selection authority. B0 adds the 100s7p capacity study and explicit packaging conflicts. No historical mass allocation becomes a measured BOM by being carried forward.

## 1. Engineering recommendation

Develop a **narrow, centrally packaged, approximately 30 kWh electric road motorcycle**, with one liquid-cooled permanent-magnet motor, one fixed reduction, standards-based DC charging through a native NACS inlet, and adjustable highway ergonomics. Target **CdA at or below 0.33 m² in the ordinary highway riding position**, with cooling airflow included. A 0.35 design remains useful for screening but leaves little range margin.

Do not design a 150 hp superbike and then try to give it long range. Our first-principles model requires about **40 kW at the rear wheel to hold 125 mph** at CdA 0.35. Investigate approximately **60 kW peak at the motor shaft**, with **45 kW continuous shaft capability** under defined thermal conditions. These are proposed sizing requirements, not confirmed supplier performance. The owner's 125+ mph target does not specify continuous duration; designing useful thermal capability avoids relying on a momentary advertised peak.

The strongest differentiation is reducing the energy needed to travel, integrating the pack efficiently, and making charging dependable. Developing a new cell chemistry is not a prerequisite. The leading cell reference is promising but still needs supply, durability, thermal and mechanical qualification.

**All goals are not yet closed.** The component allocation below yields approximately **433 lb before contingency, 446 lb with a modest development allowance**. An aggressive alternative reaches approximately **396 lb before allowance and 407 lb with it**, but requires both better pack integration and substantially lighter non-battery hardware. Neither is an accepted revision to the owner's weight requirement. Tesla network access is also unresolved. The research identifies a route worth developing; it does not prove a catalog-parts combination meets everything.

## 2. Requirements and what is actually known

Labels throughout: **Owner** = agreed objective; **Proposed** = engineering recommendation; **Reference** = published component data, not qualified for this vehicle; **Calculated** = model output; **Open** = needs a decision or evidence.

| Item | Specification / interpretation | Status |
|---|---|---|
| Range | 200 miles, 70 mph calculation baseline | Owner |
| Design cruising speed | 77 mph for comfort, airflow and stability work | Owner |
| Top speed | More than 125 mph; calculate 130 mph as development headroom | Owner / proposed headroom |
| Complete mass | Prefer less than 400 lb, battery and operating fluids included; rider excluded | Owner |
| First permissible trade discussion | Slightly more mass before conceding the other goals; no replacement ceiling agreed | Owner |
| Charging | Tesla stations, with actual access and successful charging demonstrated | Owner |
| Character | Comfortable highway riding, compact proportions, minimal appearance, broad rider appeal | Owner |
| Reference rider plus gear | 90 kg; evaluate other riders separately | Model assumption |
| Advertised range conditions | Temperature, payload, reserve, battery age and test procedure still to be defined | Open |
| Charging time | No owner limit; investigate 30–50 kW DC and 6.6 kW AC | Proposed |
| Acceleration, passenger and luggage rating | No owner requirements yet; do not infer them from “125+ mph” or “everyone” | Open |
| Price, warranty and production volume | Not set; architecture remains sensitive to all three | Open |

Use a solo rider as the first packaging case, while leaving passenger capability explicitly undecided. Broad appeal requires adjustable fit and testing across riders; it cannot mean a single geometry fits every human.

## 3. The calculations that drive the design

The reproducible model is [research/engineering-baseline.ps1](research/engineering-baseline.ps1), with [performance scenarios](research/engineering-performance.csv), [mass allocations](research/engineering-mass-budget.csv), and [summary values](research/engineering-summary.json). It supersedes earlier mass placeholders for this handoff; older research remains a historical comparison.

Model: level road, still air unless stated, air density 1.225 kg/m³, rolling coefficient 0.015, battery-to-wheel efficiency 90%, auxiliary load 300 W, 90 kg rider/gear, 196.35 kg reference bike, 30.056 kWh typical nominal energy. Allocate 90% of nominal energy to the trip. That combined reserve/unavailable-energy assumption is not an established SOC window and does not include separate aging or weather margins.

For ground speed v and headwind u:

```text
Fdrag = 0.5 × air density × CdA × (v + u)²
Frolling = rolling coefficient × total moving mass × gravity
Pbattery = (Fdrag + Frolling + Fgrade) × v / efficiency + auxiliary load
Wh/mile = battery watts / ground speed in mph
range = nominal Wh × available fraction × battery health / Wh per mile
```

This separates air speed from ground speed. A headwind changes drag; it does not increase distance traveled. The steady model omits transient acceleration, rotating inertia, temperature-dependent cells, speed-dependent tire losses and detailed motor maps.

| Total bike-and-rider drag area | 70 mph range | 77 mph range | Battery power holding 125 mph |
|---|---:|---:|---:|
| 0.30 m² | 236 mi | 203 mi | 38.5 kW |
| **0.33 m²** | **219 mi** | **188 mi** | **42.1 kW** |
| 0.35 m² | 209 mi | 179 mi | 44.5 kW |
| 0.37 m² | 200 mi, rounded; actually 199.7 | 171 mi | 46.9 kW |
| 0.40 m² | 187 mi | 160 mi | 50.4 kW |

The exact new-battery 200-mile boundary is **CdA 0.3694**, under these assumptions. That is a mathematical boundary with no additional cushion. At 90% battery health the boundary tightens to **0.3240**; at 80% health, **0.2786**. At CdA 0.35, 90% battery health gives approximately 188 miles. A 10 mph direct headwind reduces the new-battery result to approximately 168 miles. A 200-mile claim covering aging or adverse weather would require a different energy budget.

At 70 mph, reducing CdA by 0.01 saves approximately **0.662 kWh of required nominal capacity** for a 200-mile trip. Removing 10 kg saves approximately **0.162 kWh**. Weight matters to handling and the owner's goal, but drag is the stronger highway-range lever. Improving total drive efficiency from 90% to 93% at the 0.35 reference point saves only about 0.8 kWh of trip energy over 200 miles; it helps but cannot rescue a poor aerodynamic design.

### Challenge the benchmarks

Zero's current SR/S specification lists 518 lb curb mass, a 15.1 kWh nominal pack / 17.3 kWh maximum figure, belt drive and 6.6 kW AC charging. Its page contains differing city-range statements, so do not copy a single headline as a verified highway benchmark. The lesson is to compare nominal with nominal and stated highway tests with our 70 mph target. [Zero SR/S](https://zeromotorcycles.com/model/zero-srs)

Ducati's original V21L reference uses an 18 kWh, 110 kg pack, a 21 kg motor and a 5 kg inverter, with separate battery and drive cooling circuits. Its race-oriented design is useful integration prior art, not a weight floor for a lower-power road bike. Its 3.7 kg front-frame figure excludes much of the complete supporting structure. [Ducati V21L](https://www.ducati.com/ww/en/company/innovation/moto-e/prototype)

Full-scale wind-tunnel research measured CdA 0.500 upright and 0.347 tucked for an Energica; rider posture changed the results substantially. Our comfortable 0.33 target therefore represents a serious development challenge, not a small styling adjustment. [Kirca and McGordon, Warwick, Table II](https://wrap.warwick.ac.uk/id/eprint/180779/1/WRAP-Effect-rider-position-energy-consumption-23.pdf)

## 4. Battery: optimize the complete system

### Lead reference and boundaries

Retain Amprius SA504-class silicon-containing NMC pouches as the lead reference. Relevant published values are 37.57 Wh typical / 36.72 Wh minimum, 97.3 ±2 g, 3.4 V nominal, 4.2/2.5 V endpoints, 10.8 A typical / 21.6 A maximum charge, and 66.3 A continuous discharge. The 500-cycle result is at +1C/−1C to 80% health; it does not establish repeated 2C-charge life. Charge temperature is 0–45°C. Reference dimensions are 125.4 × 42.2 × 8.25 mm at 30% SOC, with tolerances. [Amprius Q3 2026 catalog, PDF page 52](https://amprius.com/documents/Amprius_Product_Catalog.pdf)

Do not equate supplier certifications with a qualified motorcycle pack. Sourcing, lot consistency, DC resistance, compression, swelling over life, crash behavior, calendar aging and automotive application support remain open. The existing [battery deep dive](research/battery-deep-dive.md) retains competing technologies and their limitations.

### Electrical calculation reference

| Property | Leading study configuration |
|---|---:|
| Series × parallel / total cells | 100 × 8 / 800 |
| Typical nominal energy | 30.056 kWh |
| Energy at published minimum Wh | 29.376 kWh |
| Nominal voltage | 340 V |
| Sum of cell voltage endpoints | 250–420 V; not a selected operating window |
| Typical / maximum pack charge current | 86.4 / 172.8 A before derating |
| Typical cell mass total | 77.84 kg |
| Pack at assumed 80% cell mass fraction | 97.30 kg |
| Pack at proposed 85% integration target | 91.58 kg |
| Trip energy at the 90% availability assumption | 27.05 kWh typical; 26.44 minimum-energy case |

The nominal Wh ratings require confirmation against the actual drive discharge rate and selected SOC window. The minimum-energy case alone lowers the 0.35 range result to roughly 204 miles; it does not include worst-case mass, cold weather or aging simultaneously.

**Recommended pack structure:** a replaceable, chassis-supported enclosure, with a small number of mechanically restrained cell groups, integrated cooling surfaces and serviceable electronics. Use structural enclosure stiffness where analysis justifies it; never make the pouch cells themselves the primary chassis load path. Avoid hundreds of individual heavy cell cartridges. Avoid promising a fully load-bearing pack before attachment, fatigue and crash analysis.

A pack's 80% cell mass fraction means 19.46 kg remains for its enclosure, internal support/compression, interconnects, internal cooling hardware, BMS, pack-side protection and internal wiring. It is an allocation, not a measured design. Improving to 85% allows only 13.74 kg for those functions and saves 5.72 kg. Reducing part duplication is valuable; deleting necessary protection is not an engineering solution.

### Mechanical packaging reference for the designer

Raw cell bounding volumes sum to approximately **34.93 L**. Do not mistake that for installed pack volume or infer finished dimensions from a supplier Wh/L headline.

One counting exercise groups 80 cells as 4 across × 2 along × 10 stacked. Bare dimensions are approximately 168.8 × 250.8 × 82.5 mm. Allowing a provisional **185 W × 275 L × 105 H mm** per mechanical group gives 5.34 L. Ten groups arranged two along and five high occupy approximately **185 W × 550 L × 525 H mm**, before a common outer enclosure and services. This is cell counting, not an approved module topology, compression prescription or wiring design.

For initial sketches, reserve a **600 L × 260 W × 560 H mm study envelope** for the whole battery region, including room to investigate structure, services and tolerances. Its 87.36 L is a deliberately generous reservation, not a calculated final package or a requirement to use a rectangular box. Shape it around the rider only after module access, coolant flow, venting, cell tolerances and growth are resolved. No finite-element, thermal or collision analysis establishes that the illustrated counting scheme fits safely inside it.

This envelope is the largest styling constraint. Keep the main mass between the axles, with a narrow knee region and protection from underside impacts. Put the motor near the swingarm pivot, not in the rear wheel. Route any fault venting away from rider contact zones and ordinary cooling intake paths. Preserve a pack-removal route that does not require destroying the frame or bodywork.

### Alternatives challenged

| Alternative | Decision and reason |
|---|---|
| LFP | Useful cost/life benchmark; its larger mass/volume at this energy conflicts with the present targets |
| Conventional high-energy cylindrical | Retain as sourcing benchmark; earlier screening adds too much mass at approximately 30 kWh |
| Extreme aviation energy-density cells | Do not select from Wh/kg alone; power, charge acceptance, life and mechanical boundary conditions must survive screening |
| Solid-state breakthrough | Monitor as a later option; no dependency in the present baseline |
| Swappable whole pack | Reject for this baseline: a roughly 90–100 kg pack is not conveniently hand-carried; interfaces and extra cases cost mass |
| Two removable packs | Can help service, but duplicates enclosure/connectors and does not remove stored-energy mass |
| Supercapacitor buffer | No demonstrated need: the lead pack's published discharge capability already exceeds proposed vehicle demand; adds mass and conversion hardware |
| Smaller pack plus better aero | The strongest energy-reduction alternative; preserve only if the comfortable rider/body design actually achieves the required drag |

The earlier “28 kWh alternative” is a capacity study, not a locked cell configuration. For example 96 × 8 of the same cell gives **28.854 kWh**, 326.4 V nominal and 403.2 V full endpoint; it also changes motor speed/voltage compatibility. Do not silently carry over the 100-series drive calculations. Select discrete cell counts only after the integrated trade study.

## 5. Motor, inverter and final drive

### Candidate and sizing logic

Use an **EMRAX 208 medium-voltage liquid-cooled configuration** as the motor engineering reference. Its v1.5 sheet specifies 10.3 kg, 208 mm diameter × 85 mm body length, 52 kW continuous and 86 kW two-minute peak under its stated conditions, 84/150 Nm continuous/peak and 7,000 rpm limiting speed. Peak rating requires 420 V for that winding. The liquid-cooled version is IP66; the lighter combined-cooled variant is IP21. Required cooling includes at least 6 L/min with a 50°C maximum inlet, and the manufacturer also requires air circulation. Do not enclose it without reviewing installation conditions. [EMRAX 208 v1.5](https://emrax.com/wp-content/uploads/2024/02/EMRAX_208_datasheet_v1.5.pdf)

This is a candidate, not a confirmed motor match. Obtain its current revision and torque/speed/efficiency maps across the actual pack voltage, including loaded low-SOC voltage. The headline voltage range does not guarantee useful power at all speeds. Rotor exposure, mounting, resolver fit, connectors and shaft support need installation drawings.

The **EMRAX 188 liquid-cooled** alternative weighs 7.9 kg but its sheet rates continuous power at 34 kW, below the roughly 41 kW shaft requirement calculated for 125 mph here. It may meet a brief top-speed requirement; reject it as the default if sustained top-speed capability is required. Its peak rating is not a substitute for endurance. [EMRAX 188 v1.5](https://emrax.com/wp-content/uploads/2024/02/EMRAX_188_datasheet_v1.5.pdf)

Start integration studies with the **Cascadia CM200DX** inverter: 50–480 V operation, 6.75 kg, 330 × 188 × 97 mm, 300 A continuous / 740 A peak phase current, with peak duration limited by the sheet. Its 225 kW electrical headline is unused capability here. Published cooling calls for 12 L/min. It is a documented reference that may be heavier than a production-specific unit; a smaller replacement must preserve voltage, phase-current, sensor, control and environmental compatibility. [CM200 sheet](https://www.cascadiamotion.com/images/catalog/DataSheets/CM200.pdf), [manufacturer product page](https://www.cascadiamotion.com/inverters)

Do not confuse DC battery amps with motor phase amps. Their relationship changes with speed, voltage and control modulation. The inverter's maximum voltage rating alone does not prove a motor/inverter pair.

### Working drive specification

| Parameter | Proposed requirement or calculated result |
|---|---|
| Arrangement | Single frame-mounted motor; single fixed reduction; no clutch or gear shifting |
| Shaft output target | Approximately 60 kW peak for a defined short duration; investigate 30 seconds initially |
| Continuous shaft design target | At least 45 kW at relevant speed, coolant and ambient conditions |
| Initial total ratio | Study 3.0–3.3:1; use 3.1:1 for the calculation reference |
| Rear tire calculation reference | 160/60-17 geometric diameter 623.8 mm; actual rolling radius must be measured |
| 125 mph reference speed | Approximately 1,711 wheel rpm / 5,304 motor rpm at 3.1:1 |
| 125 mph at CdA 0.35 | Approximately 39.8 kW wheel / 41.0 kW shaft, assuming 97% mechanical final-drive efficiency |
| Shaft torque at that point | Approximately 73.8 Nm |
| 150 Nm motor torque at 3.1:1 | Approximately 451 Nm wheel torque before tire/traction/control limits |
| HV load sizing envelope | Investigate 70 kW peak battery draw; approximately 206 A at 340 V or 280 A at 250 V |
| Regen | Controllable; subordinate to battery acceptance, tire grip and ABS/traction intervention |

The 90% total efficiency model and 97% final-drive assumption imply a motor/inverter efficiency allocation; do not multiply the 97% loss into the road-load calculation a second time. Detailed maps must replace both assumptions.

At 340 V, the motor sheet's nominal-load speed constant suggests roughly 6,440 rpm; at 280 V, roughly 5,300 rpm. That simple screen explains why the approximately 5,304 rpm top-speed point is sensitive to low SOC. It is not a loaded torque-speed simulation. Field weakening must be evaluated for current, heat and efficiency; do not assume it repairs every voltage shortfall. The design must specify the SOC range over which 125+ mph remains available.

### Challenge the transmission

Prefer a **supplier-sized synchronous belt** for the intended quiet, low-maintenance road product, while allowing chain drive on a development mule for ratio changes. Gates publishes motorcycle belt systems for this application. Do not assign a precise efficiency advantage without matching-load measurements. [Gates motorcycle drives](https://www.gates.com/us/en/innovations-and-solutions/urban-mobility-and-powersports-solutions/synchronous-belt-drives-for-motorcycles.html)

Investigate a direct single reduction before adding a gearbox. Pulley diameter, belt width, tooth loading, tension, debris protection and suspension movement may require a supported jackshaft. That support belongs in the drive mass and package. Motor bearings cannot be assumed to accept belt or chain side loads. Gates' design guidance also warns that excessive tension increases bearing and shaft loads. [Gates design manual](https://www.gates.com/content/dam/gates/home/knowledge-center/resource-library/catalogs/old-pc_carbon_manual17595_2011.pdf)

Reject a hub motor as the lead because it moves substantial mass into the wheel and makes suspension, service and wheel packaging harder. Reject dual motors, AWD and a two-speed gearbox unless measured traction or efficiency gains justify their complete-system mass and complexity. “Fewer parts” is useful only when the remaining components operate well across the real duty cycle.

## 6. Charging and electrical controls

Carry forward the [charging architecture study](research/charging-architecture.md). Use a native NACS/J3400 inlet with separate controlled AC and DC paths, an EVCC for station communication, an onboard AC charger, and BMS-controlled limits. DC station conversion occurs outside the bike.

Tesla access requires both interoperability and network authorization. Tesla describes different access categories and supported manufacturers; reviewed public information does not establish Bavuso access. Confirm onboarding and actual station voltage/current coverage before calling this goal met. Do not promise access merely because the plug fits. [Tesla support](https://www.tesla.com/support/charging/supercharging-other-evs)

Propose **50 kW maximum DC initially**, with routine charging closer to the cell supplier's typical current unless life testing supports more. At nominal voltage, typical pack current corresponds to approximately 29.4 kW; maximum current corresponds to approximately 58.8 kW. At 250 V, the same maximum current limits input to approximately 43.2 kW before thermal or station derating. None of these products is a full charge curve.

A 10–80% session stores approximately 21.04 kWh. At constant average net stored-energy rates of 30/40/50 kW, arithmetic times are **42.1/31.6/25.2 minutes**. Actual current limits, voltage progression, taper, losses and auxiliaries determine real results. Do not market those ideal times as measured performance. The 200-mile full-trip model also does not mean 200 miles between repeated 10–80% road-trip stops: that window contains only 70% of nominal energy versus the model's 90% trip allowance.

For AC, study a compact **6.6 kW charger** with 200–430 V output. BROGEN's PV1776 catalog reference is no more than 3 kg, 373 × 224 × 76.5 mm, liquid-cooled, and lists **176–264 V AC input**. It does not establish ordinary 120 V outlet support. Confirm revision, isolation, EMC, automotive use and cold-start behavior before adopting it. A universal-input charger is a separate sourcing decision; the earlier TC integrated alternative is heavier. [BROGEN catalog, PDF page 11](https://www.brogenmotors.com/wp-content/uploads/2024/06/Requirement_SheetOBC.pdf)

Continental's EVCC and ADVANTICS' ADM-CS-EVCC are integration references. ADVANTICS publishes vehicle CAN, session control, inlet lock and fault behavior. Its software documentation also describes Orion BMS integration, which is useful for a development mule. Confirm the complete native-NACS implementation and access path rather than assuming a CCS controller automatically supplies every required function. [ADVANTICS integration guide](https://documentation.advantics.fr/adm-cs-evcc/integration-guide.html)

**Challenge:** a bigger AC charger does not make DC fast charging faster. A 3.3 kW unit may save mass but approximately doubles ideal full-energy AC time from 4.6 to 9.1 hours. An external home charger could remove onboard conversion mass, but weakens ordinary AC-destination convenience and requires a separate interoperable product. Do not make that trade silently.

### Required control functions

Use a proven BMS for the mule, such as a suitably configured **Orion BMS 2 108-series-channel unit**, rather than inventing battery protection and charge control simultaneously. Confirm allowable unused-channel arrangements. Its published J1772/CHAdeMO features do not themselves supply NACS DC authorization. A production BMS can later use distributed automotive monitoring to reduce harness mass if reliability and fault coverage are retained. [Orion BMS 2](https://www.orionbms.com/products/orion-bms-standard/)

Monitor every series group, strategically placed cell temperatures, pack current, pack voltage, insulation, charge-inlet temperature and coolant state. An eight-cell parallel group cannot reveal each member's condition from one shared voltage reading; cell matching, connection design, temperature coverage and failure containment must address that limitation. Provide independent fault responses, plausibility checks and controlled torque removal.

Include pack protection, precharge, service isolation, high-voltage interlocks, current sensing, isolation monitoring and charge/drive exclusion. Size contactors, fuses and conductors using interruption ratings, temperature, prospective fault current and coordination, not just the proposed 280 A peak drive current. Commercial isolation-monitoring and HV contactor families demonstrate available functions, not an approved circuit. [Bender vehicle monitoring](https://www.bender.de/en/products/emobility/emobility-insulation-monitoring/isometer-iso175/), [Sensata contactor guide](https://www.sensata.com/sites/default/files/a/sensata-gigavac-contactors-selection-guide.pdf?cb=9e383952)

## 7. Thermal management: the hidden range and charging constraint

Use separate thermal control for the battery and the motor/inverter, with shared hardware only where analysis supports it. A single hot motor loop can undermine battery charge temperature control. Combine components intelligently; do not copy two complete automotive cooling systems by default.

Propose a battery control objective near **20–35°C**, with **less than 5°C cell-to-cell spread** as an initial development target. These are engineering objectives, not supplier limits or proven optimums. Maintain supplier temperature boundaries with measurement uncertainty and gradients accounted for. Include temperature-dependent charge limits, cold preconditioning and fan-assisted parked cooling.

Size from measured DC resistance, entropic heat and drive/charge profiles. The supplier's AC impedance is not a valid substitute for DC resistance in I²R thermal predictions. A sensitivity of 3–5% heat at 50 kW represents **1.5–2.5 kW**; it is an illustrative design load, not measured cell heat.

**Critical trade:** a radiator cannot cool below ambient temperature. At 40°C ambient, a 45°C cell charging boundary leaves very little thermal approach after cell-to-coolant and coolant-to-air gradients. Full-rate charging in hot weather may require active refrigeration or substantial derating. The present 5 kg external thermal allowance contains no refrigeration compressor/chiller. Adding one reopens mass, packaging and cost. A cold battery may also require heating before fast charging; the heat source and energy cost remain to be sized.

Keep two explicit thermal paths in the study: a light fan/radiator solution with measured hot-weather derating, and an actively refrigerated alternative only if required by the eventual charging promise. Neither has been proved. Research on coupled module and DC-resistance thermal modeling supports evaluating gradients during fast charging rather than only average pack temperature. [Xiao et al., SAE 2026-01-0399](https://doi.org/10.4271/2026-01-0399)

For highway comfort, route hot discharge air away from the rider's legs and keep fan noise out of the helmet wake. Cooling inlet/outlet pressure losses and cooling drag belong in the aero study. A sleek render with no workable cooling exit is not a finished aerodynamic solution.

## 8. Chassis, steering, suspension and tires

Start with a **fabricated metal chassis and a double-sided swingarm**, using the pack enclosure as a supported structural contributor only after analysis. Steel tube and fabricated aluminum should compete on complete mass, joints, fixtures, fatigue, corrosion, service and production volume. Material density alone does not choose the lighter structure. Avoid making a giant casting or carbon monocoque a prerequisite before volumes and repair strategy are known.

Use a conventional telescopic fork and adjustable rear shock. Advanced alternative front suspension is possible, but it introduces another major development program without yet resolving the dominant energy constraint. Likewise, semi-active suspension is not necessary to make a comfortable first bike; correct spring rates, damping, travel, seat and riding posture are.

**Proposed layout exploration ranges, not released geometry:**

| Parameter | Starting study range / instruction |
|---|---|
| Wheelbase | 1,400–1,450 mm |
| Rake / trail | 24–26° / 95–110 mm; assess together with real tire geometry and suspension travel |
| Wheels | 17-inch front and rear; preserve replacement-tire availability |
| Tire starting point | 120/70 front, 160/60 rear; compare narrower options only after load/grip/handling analysis |
| Suspension travel | Approximately 120–140 mm wheel travel; retain bump clearance with pack installed |
| Seat exploration | Approximately 780–820 mm, plus low-seat/fit alternatives; width matters as much as height |
| Ground clearance | Investigate at least approximately 150 mm static reference, then verify loaded/bump/lean clearance |
| Static distribution | Explore approximately 48–52% front with the reference rider, then verify dynamic loading |
| Payload | Unresolved; do not use the 90 kg range rider as the rated payload |

These ranges are design seeds, not proof of stability. Kawasaki's Ninja 500 provides a compact production reference at 1,374 mm wheelbase, 24.5° rake and approximately 91 mm trail; Zero's SR/S uses 1,450 mm and 94 mm trail. Neither geometry should be copied around a different battery mass distribution. [Kawasaki specification](https://www.kawasaki.com/en-us/products/ProductSpecSheetPDF/2025-ninja-500), [Zero specification](https://zeromotorcycles.com/model/zero-srs)

Michelin's Road 6 range includes the suggested 120/70ZR17 and 160/60ZR17 sizes. This demonstrates a mainstream tire route, not a completed tire selection. Verify rim widths, load/speed capability, pressure, clearances and actual rolling circumference with the selected tire maker. Do not assume a wider rear tire adds useful highway stability or that a narrower one automatically lowers total energy use. [Michelin Road 6](https://www.michelin.co.jp/motorbike/tyres/michelin-road-6)

Center mass for manageable pitch/yaw inertia, not simply the lowest possible CG. Loading, steering geometry, frame/swingarm flexibility, damping, tire behavior and aerodynamic moments interact. A steering damper can address particular oscillations but does not repair unstable vehicle geometry. Verify wobble/weave and transient response through the intended speed envelope, with different riders and loading cases.

## 9. Brakes and rider controls

Use independent front/rear hydraulic friction brakes, ABS, wheel-speed sensors and an IMU-based traction/stability strategy. Target a consistent lever response when regen becomes unavailable at high SOC, low temperature or a fault. Do not rely on regen to meet the friction-brake duty.

Begin the mechanical study with **dual approximately 300–320 mm front steel discs and a roughly 220–240 mm rear disc**. These are package reservations pending complete brake sizing. A single larger front disc is a legitimate mass-reduction candidate, but requires the full stopping, fade, wet and repeated-stop analysis before adoption. Kawasaki demonstrates single-disc production practice on a lighter performance class; it does not establish adequacy for this bike. [Kawasaki specification](https://www.kawasaki.com/en-us/products/ProductSpecSheetPDF/2025-ninja-500)

At the reference bike plus rider mass, translational kinetic energy at 125 mph is approximately **447 kJ**, before rotating parts. The brakes need a defined distribution and repeat-stop thermal budget; rotor diameter by itself cannot establish capacity. Choose matched master cylinder, calipers, pads, disc thickness and hydraulic ratios. Supplier application guidance distinguishes master cylinders for different disc/caliper combinations. [Brembo application guidance](https://www.brembo.com/en/news-archive/brembo-for-honda)

Bosch's motorcycle stability control demonstrates integrated braking and acceleration functions based on measured vehicle dynamics. It needs vehicle-specific integration and calibration; buying an IMU does not create cornering ABS. If a development mule initially uses simpler ABS, do not present that as completed production stability capability. [Bosch MSC](https://www.bosch-mobility.com/en/solutions/braking-systems/motorcycle-stability-control/)

Provide predictable throttle response, selectable regen, adjustable levers, cruise control, clear remaining-range/charging information and simple physical controls. Avoid turning phone connectivity or a large screen into a condition for basic riding or charging. These choices support the intended minimal product without removing useful function.

## 10. Component mass budget and the path below 400 lb

| Complete-vehicle allocation | kg | Evidence level |
|---|---:|---|
| Battery, complete | 97.30 | Calculated at assumed 80% cell mass fraction |
| Motor | 10.30 | Published reference |
| Inverter | 6.75 | Published reference |
| Reduction/final drive/support/guards | 5.00 | Allocation |
| Frame, subframe, swingarm | 16.00 | Allocation; excludes battery enclosure |
| Suspension, steering, yokes, damper | 10.00 | Allocation |
| Wheels, tires, bearings | 17.00 | Allocation; excludes brake rotors |
| Friction brakes, ABS, brake fluid | 7.00 | Allocation |
| AC charger | 3.00 | Supplier catalog ceiling; unqualified |
| Inlet, EVCC and charge routing | 2.00 | Allocation |
| DC/DC and LV battery | 2.00 | Allocation |
| External cooling, all coolant, hoses, fans, pumps | 5.00 | Allocation; excludes internal pack plates and refrigeration |
| Body, seat, controls, lighting, vehicle wiring | 11.00 | Allocation |
| Other mounts, fasteners, stand | 4.00 | Allocation; no component-internal duplication |
| **Reference total** | **196.35** | **432.9 lb** |
| Development allowance: 5% of non-cell mass | 5.93 | Deliberately visible; not a statistical confidence interval |
| **Total including allowance** | **202.28** | **445.9 lb** |

Only a few lines are sourced hardware masses; most still need a selected part or analyzed design. This is not a weighed bill of materials. Cell mass tolerance and multiple simultaneous worst cases are not fully covered by the modest allowance. The earlier 420–428 lb sensitivity used aggregate placeholders; this more explicit reference replaces it for current decisions.

To reach 400 lb at the current 97.3 kg pack, **everything outside the pack must fit within 84.14 kg**, versus the 99.05 kg allocation above, before contingency. That is a nearly 15 kg gap. At the improved 91.58 kg pack, the outside-pack allowance rises to **89.86 kg**, still without development margin.

The lightweight development target combines **85% cell mass fraction and 88 kg outside the pack**: approximately **395.9 lb**, increasing to **407.1 lb** with the same allowance method. It requires saving 11.05 kg outside the pack while keeping the larger motor reference. Possible contributors are a smaller compatible inverter, integrated charge/LV electronics, simpler structural load paths, optimized wheel/brake assemblies, and eliminating duplicated mounts/enclosures. None has an earned mass credit yet. Do not add optimistic savings from mutually incompatible components.

**Recommended priority:** first improve pack integration and the non-pack budget; second use demonstrated aero performance to revisit capacity; third discuss a small weight concession with the owner only when a reconciled design makes it concrete. Do not accept 446 lb merely because weight was identified as the first negotiable requirement.

## 11. What Dominic can design around now

Use [designer-brief.md](designer-brief.md) as the compact companion. It reserves engineering space while leaving visual identity open.

The design variables with the highest value are the comfortable rider envelope, front-wheel/fork airflow, helmet and shoulder flow, leg exposure, cooling inlet/outlet integration and rear wake. A small windshield alone is not a demonstrated route to CdA 0.33. Keep the pack and rider in the same iteration; do not freeze a silhouette and then force the battery into leftover space.

Report drag area for the **complete bike plus rider**, with mirrors, real tire shapes, cooling paths and accessories in their intended state. Frontal area and drag coefficient separately are diagnostic; the range model consumes their product. Include multiple rider sizes and ordinary riding clothes, not only a small rider in a racing tuck.

Analyze side force and yaw/roll/steering moments at 77 mph, including transient gusts. Proposed CFD/tunnel exploration: yaw 0°, ±5°, ±10° and ±15°, with crosswind transients and larger angles where route/wind assumptions require them. A 20 mph crosswind at 77 mph is about 14.6° apparent yaw. These are test conditions, not pass thresholds. Establish numerical handling and rider-effort acceptance criteria with vehicle dynamics analysis before declaring “gust stable.” Visual bulk and side projected area alone cannot establish that result.

For the owner-led aero work, I can supply the model, parameter sweeps and design constraints. The shape can be owner-led; the range and stability claims still need engineering verification. Comfort likewise requires a physical seating buck and riding feedback, not only attractive proportions.

## 12. Evidence needed before design release

| Gate | Work product | Decision it closes |
|---|---|---|
| Cell suitability | Current supplier drawing/specification, supply/quote, charge/discharge maps, DC resistance versus SOC/temperature, swelling/compression, life and calendar-aging evidence | Whether this pack is a credible product basis |
| Charging access | Confirmed Tesla onboarding route and station operating coverage; EVCC/inlet/OBC interface documentation | Whether the Tesla goal has a real path |
| Packaging | Parametric 3D layout, mechanical clearances, suspension/steering sweeps, rider buck and service paths | Whether components and comfortable rider fit a compact bike |
| Drive compatibility | Motor/inverter maps, actual rolling radius, ratio and low-SOC loaded speed analysis | Whether 125+ mph is available under stated conditions |
| Aero | Mesh/solver convergence and sensitivity, then tunnel/coastdown correlation; cooling and riders included | Whether the energy budget is defensible |
| Thermal | Measured cell/module heat and gradients; drive and stationary charging models, hot/cold tests | Whether charging/performance survives real temperatures |
| Structure/dynamics | Load cases, FEA, fatigue, attachment and crash protection; multi-body stability analysis | Whether lightweight structure and highway behavior are credible |
| Mass | Reconciled CAD mass plus weighed supplier parts, fluids, wiring and visible margin | Whether the weight objective is met or a specific concession is needed |
| Braking/controls | Brake sizing and fade tests; ABS/regen/fault coordination, hardware-in-loop and instrumented mule results | Whether deceleration and torque control work across states |
| Vehicle verification | Instrumented 70 mph range test and top-speed/durability tests under stated conditions at an appropriate facility | Whether the performance claims are earned |

Supplier questions can be drafted now; no supplier or Tesla outreach has been sent or is implied by this report. Critical unknowns such as price, warranty, passenger rating and acceptable hot-weather charging performance remain visible decisions rather than invented owner requirements.

For production planning, commission a jurisdiction-specific compliance matrix before freezing lights, controls, braking and pack interfaces. Relevant starting references include U.S. motorcycle braking and L-category electric-powertrain requirements; their applicability and current amendments must be checked for the intended market. This report has not completed certification analysis. [NHTSA FMVSS 122 test reference](https://www.nhtsa.gov/document/laboratory-test-procedure-fmvss-122-motorcycle-brake-systems), [UNECE electric vehicle regulation overview](https://unece.org/ev-hev-and-fc)

## 13. Immediate engineering sequence

1. Build a parametric package and mass model around the 30.056 kWh reference, the actual motor/inverter bodies, charging hardware and a comfortable rider. Use bounding boxes only for early space allocation; get installation drawings before hard points are frozen.
2. Work the low-SOC motor/ratio and hot-weather charging cases early. Either can invalidate a superficially attractive component match.
3. Iterate owner-led body/rider concepts against CdA 0.33 and a functioning thermal package. Keep range calculations updated as shape and mass change.
4. Replace every mass allocation with a component or analyzed structure. Then assess the smaller-capacity alternative and the preferred under-400 lb target together.
5. Qualify cells and integration on a controlled test program before a road vehicle build. Close the published-specification gaps with evidence, not added decimal places.

The package, maps and validation gates above are the remaining engineering work. This handoff gives a specific direction and a reviewable specification basis; it does not claim that those tasks have already been performed.
