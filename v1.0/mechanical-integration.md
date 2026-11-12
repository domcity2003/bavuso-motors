# V1.0 mechanical integration decisions

October25,2026. Custom Bavuso remains the product. This is a development configuration, not a donor conversion, road release or a procurement authorization. The [B0 mechanical specification](../documentation/systems/mechanical-chassis.md), [interface register](../documentation/registers/interfaces.csv) and [manufacturing traveler](../documentation/manufacturing/assembly-service-quality.md) still supply the system-level requirements. The new geometry changes the packaging proposal, not the owner's goals.

## Physical package we can now inspect

X points forward, Y left, Z up; rear tire contact is the nominal origin. All dimensions below are proposed millimeters unless explicitly called catalog data.

| Item | V1 proposal | Evidence/status |
|---|---|---|
| Wheelbase | 1,640 | Longer than1,420B0; accommodates proposed pack and sampledbump. NOT approved handling geometry or a faithful dimensional reconstruction of the render |
| Pack outside boundary | x570–1260,y±110,z160–710 |690×220×550;83.49L; not a complete installed pack |
| Motor body center |440,0,340 | Actual2022manufacturer LCresolverSTEP; must verify current supplied revision |
| Swingarm pivot |490,0,490 | Proposed; moved out of pack and motor; bearings/shaft/mounts unresolved |
| Seat reference |470,0,850 | Reference only; lofted seat varies in height. No broad-rider ergonomic claim |
| Grip reference |1050,±340,1120 | Proposed relaxed-bar location; no actual handlebar/lever switchgear selected |
| Foot reference |500,±200,380 | Proposed; loaded ground clearance/lean and body fit untested |
| Front suspension travel |125axial | OEM family reference; V1 applies25degree simplified axis |
| Rear wheel travel |130vertical | Simplified arc about proposed pivot; no working shock linkage |

**Do not freeze the long wheelbase to preserve the current box.** It is a diagnostic fit solution. Before it becomes a product dimension, compare a staggered/split pack, more width low in the bike, shifted electronics, actual swelling/thermal package and original compact appearance. A longer wheelbase changes turning circle, weight transfer, frame loads and rider perception. Taller seat/long reach are not acceptable substitutes for the requested broad fit; an adjustable seating buck remains required.

## Real components versus illustrative CAD

Two models are actual supplier files: [EMRAX208LCresolverSTEP](https://emrax.com/wp-content/uploads/2022/05/208_lc_resolver.step) and the [CascadiaCM200download](https://www.cascadiamotion.com/cm-200). They have not been scaled. Source coordinate axes are rotated/translated into the vehicle frame. The motor import includes protrusions beyond its headline85mm body length. This is why a cylinder is an inadequate final installation definition. Neither source proves an exact currently orderable configuration or the load capacity of its installed mounts.

The wheels, discs, fork, swingarm, frame, screen, seat and fairing in this file are explicitly **custom study geometry**. Naming a real replacement part does not make an illustrative wheel its exact CAD. No 3D manufactured frame part is released. The case is an unqualified closed3mm shell, not a lid/seal/vent assembly.

## Running gear: identifiable hardware route

Preserve matched front wheel, fork/yokes, bearings, spacers, axle, brakes, master cylinder, tone ring/sensor and hydraulic equipment from one inspected model/VIN configuration. Do likewise for the rear wheel, carrier, bearings, spacers, disc, caliper/bracket and speed sensor. Mixed model-year OEM catalogs below establish identities only; matching suffixes do not establish interchangeability. A2025Ninja650ABS assembly set is a reasonable prototype sourcing route;2026references are comparisons pending matching service data. Production supply agreements have not been established.

| Function | Actual catalog candidate | Required before installation |
|---|---|---|
| Front wheel |Kawasaki41073-0702-QT | Measure rim width, hub/rotor offsets, bearing seats and runout |
| Front axle |41068-0616,20×209 | Retain matching collars, nut/clamp and service torque from exact manual |
| Front wheel bearings |92045-0820×2,20×42×12 | Full OEM tolerance/retention/seal stack |
| Rear wheel |41073-0704-QT | Offset/rim width/cush drive inspection; custom belt conversion not established |
| Rear axle |41068-0617,20×339.9 | Matching bearing/collar/adjuster/dropout stack |
| Rear hub coupling |42033-0570 | Retain cush drive; motor belt adapter loads not validated |
| Rear wheel bearings |92045-0821×2,20×47×14 | Carrier has separate bearing; not a complete bearing BOM |
| Fork legs |44071-1201-32A /44071-1203-32A | Installed length/travel stops/offsets and spring/damping qualification |
| Front discs |41080-0666-11I×2 |300mm diameter; offset, thickness, wear limit and bolts from exact service data |
| Front calipers |43080-0177-DJ /43080-0178-DJ | Matching brackets/pads/master/hoses/ABS; no arbitrary hydraulic ratio |
| Rear disc/caliper |41080-0667 /43080-0156-DJ |220mm disc; retain holder, pads, bracket and master geometry |
| Rear shock alternative |ÖhlinsKA736 |297mm eyes,54mm stroke;2025application; spring/damping/linkage must be engineered for Bavuso |

Manufacturer sources: [Ninja front wheel catalog](https://www.kawasaki.com/en-us/ownercenter/downloaddiagrampdf/332428?modelcode=EX650RSFNL&modelyear=2025), [Ninja rear wheel catalog](https://www.kawasaki.com/en-us/ownercenter/downloaddiagrampdf/344791?modelcode=EX650PSFAL&modelyear=2025), [Ninja front brake catalog](https://www.kawasaki.com/en-us/ownercenter/downloaddiagrampdf/332432?modelcode=EX650RSFNL&modelyear=2025), [Z650forkcatalog](https://www.kawasaki.com/en-us/owner-center/parts/331603/2025/ER650NSFAN), [shared-family rear brake identities](https://www.kawasaki.com/en-us/ownercenter/downloaddiagrampdf/331601?modelcode=ER650NSFAN&modelyear=2025), [KA736supplierapplication](https://www.ohlins.com/en-us/motorcycle-suspension/street/kawasaki-z-650?v=kawasaki-ninja-650-2025). Source text and drawings must be frozen at actual procurement.

OEM ABS is not a plug-and-play safety proof on a new frame, different mass/CG, altered wheelbase and electric regeneration. Sensor/tone-ring identity, ECU power/network behavior without ICEelectronics, calibration access and fail behavior require supplier engagement and instrumented testing. If there is no supported ABS integration path, this blocks the intended product rather than becoming a reason to claim a validated non-ABS substitute.

## Drive and suspension work remaining

Keep belt drive as the owner concept path. The rear OEM wheel was designed for a chain carrier; using it requires a separately engineered pulley/carrier/bearing load path. No tooth count, belt length, pitch, width, tension or motor-shaft pulley overhang has been selected. The motor and pivot are not coaxial in this proposal. Belt center distance changes through the swingarm arc; compute the full curve and Gates-approved tension strategy before selecting or drawing the belt. Do not connect two circles in the CAD and call the drive solved.

The297mm shock study line does not form a functioning rear suspension.130/54≈2.41 is an average wheel/shock travel ratio reference, not the required linkage curve. Linkage pivots, ratio progression, spring preload/rate, damper speed/temperature, sag, bump stop, hard bottom-out and bearing articulation all remain open. The CAD shock cylinder is only a keepout;46mm published piston diameter is not spring outside diameter.

The steering study uses25degree rake and100mm requested screening trail, but fork placement has not been solved from real yoke/axle offsets. Calculate actual trail from the released centerlines and loaded tire radius; verify full steering lock at every front travel position. Do not inherit the donor's100mm trail by copying its brochure value.

## Structural and mass consequences

Frame tubes are hollow geometry with proposed sections, not a material/weld specification. Grade, heat treatment, weld procedure, fixture, distortion allowance, weld access, fatigue life, crash/curb loads, motor reaction and pack retention must be analyzed before generating fabrication drawings. Engine-as-stressed-member assumptions from an ICEdonor do not transfer to this custom frame.

The pack case is already a useful reality check. Its nominal shell volume is3,861,456mm³. At an assumed aluminum density2,700kg/m³, it weighs **10.426kg before lid hardware, joints, mounts, coating or reinforcement**. Together with68.11kg typical cell mass this consumes78.536kg. The earlier85%cell-fraction target allows80.129kg for the entire pack, leaving just1.593kg for all remaining thermal, electrical, restraint and service functions. That target is not supported by this physical layout. A2mm wall or composite alternative cannot earn weight savings until impact, fatigue, sealing, heat and fire/service performance are established.

No updated complete ready-to-ride mass is claimed. Use the old calculated399lb result only as a conditional feasibility scenario, never as the mass of this CAD. Imported supplier shapes may contain duplicated/compound surfaces; material volumes of arbitrary CAD models are not automatically trustworthy purchased masses.

## Next controlled mechanical deliverables

1. Measure or obtain supplier-controlled CAD for the matched running-gear set, all bearings/bolts/spacers and shock. Freeze exactyear/VIN/variant before machining interfaces.
2. Produce three discrete-cell pack options including real tabs, aged expansion, restraint, cooling, HV hardware, venting and service access. Compare mass/fit and1260mm front boundary before retaining1640mm wheelbase.
3. Make a rider buck using the image intent, then resolve seat/bar/peg fit at broad rider sizes, stand-over width and screen visibility.
4. Solve steering and rear linkage/drive kinematics with installed hardware dimensions, tire growth and compliance margins.
5. Finish load cases and whole frame/pack/motor mount structure, then drawings with materials, tolerances, inspection limits and approved joint torque/locking processes.
6. Build bench fixtures and a non-ridden rolling assembly before powered or high-speed tests. The staged [verification plan](../documentation/verification/verification-plan.md) governs that sequence.
