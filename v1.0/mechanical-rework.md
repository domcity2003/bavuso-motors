# Mechanical rework: integrate the intended Bavuso motorcycle

October 25, 2026, US Central. Codex, GPT-6 family. This is a specific mechanical development counterproposal after inspecting the current black appearance draft, `tools/build-v1.py` and the resulting body-study image. It is not an approved donor conversion or a released manufacturing design.

## What must change in the present CAD

The current 1,640 mm-wheelbase model is a packaging demonstrator shaped around a long rectangular battery. It has two genuine imported supplier models, but most of its visible motorcycle is still tube and envelope geometry. The result does not yet reproduce the owner's compact, composed, near-upright black design. A faceted box with a screen and wheels is insufficient evidence of a designed motorcycle.

Keep the owner's defining silhouette: medium clear screen, integrated front light, continuous restrained upper body, comfortable supported saddle, raised swept-back controls, enclosed central battery, double-sided swingarm and compact tail. Change internal architecture to support that silhouette before adding decorative surface detail.

Specific present limitations:

- Fork legs are uninterrupted tubes without a constrained upper/lower sliding assembly, yokes, axle clamps, travel stops or brake-carrier interfaces. A nominal rake angle does not supply a real front assembly.
- Frame rails have proposed sections but no resolved headstock/pivot/pack mount load paths, joints, crossmembers, suspension bosses or tool clearances.
- The floating shock cylinder has no working motion relationship or mounts. Its geometric fit never established the required spring/damper capability.
- Wheels/discs are illustrative. Calipers, carriers, hydraulic fittings, ABS encoders and actual attachment geometry are missing.
- Final-drive belt and shaft support are not mechanically resolved. Motor-to-wheel center distance changes substantially through suspension movement in the counterproposal below.
- Body, headlight, seat pan, foam, screen brackets, fenders and service openings are not developed assemblies. The current seat is a broad solid loft rather than the intended supportive rider interface.
- An imported motor's bounding-box center is not necessarily its rotor axis or mounting datum. Source geometry must be aligned using verified shaft and register features, not merely centered by its box.

The next CAD must therefore be an assembly of constrained mechanism parts and surfaces around those parts, with dimensions classified as supplier/measured or proposed. It should expose unresolved interfaces visibly, rather than implying that more generic solids close them.

## Compact chassis counterproposal

Use **1,480 mm wheelbase** as the next study, inside a 1,450–1,500 mm comparison range. It is proposed engineering geometry, not a dimension extracted from render pixels. X forward, Y left, Z up. All coordinates below are mm in the fixed-chassis study frame. The zero suspension pose is topped-out study geometry; it is not an established loaded road posture. Sag, chassis pitch and actual loaded tire radii must subsequently define the road condition.

| Datum | XYZ or definition | Purpose |
|---|---|---|
| Rear axle, zero pose | (0, 0, 311.9) | Nominal rear tire arithmetic |
| Front axle, zero pose | (1480, 0, 299.9) | Nominal front tire arithmetic |
| Swingarm pivot | (540, 0, 470), axis Y | 562.668 mm geometric pivot-to-axle radius |
| Motor rotor-axis proposal | (540, 0, 470), axis Y, coaxial with swingarm | Must map to actual rotor/stator datum in supplier STEP; independent frame-supported pivots |
| Battery team current reservation | X670–1090, Y±165, Z150–720 | 420 × 330 × 570 mm outer study shifted forward to clear coaxial motor; not complete pack qualification |
| Seat support reference | (470, 0, 805) | Rider buck starting point, not final loaded seat height |
| Grip references | (970, ±340, 1060) | Reach reduced from current long model |
| Rider peg references | (460, ±190, 360) | Mid-position starting points; ground/lean checks open |
| Lower steering-axis point | (1206.954, 0, 800) | Derived from proposed rake/trail |
| Upper steering-axis point | (1132.345, 0, 960) | Derived from same line, not a copied donor yoke |
| Right shock upper eye | (400, +150, 679.392) | Frame-mounted axis Y |
| Right shock lower eye, zero | (300, +150, 399.733) | On rigid swingarm, axis Y |

This is a coupled package. The 420 mm-long battery arrangement is being investigated separately with discrete cells. Its width/height, real cooling/protection/vent volume, frame support and mass are still engineering questions. For a roughly 211.5 mm motor diameter reference, X645.75 is its forward radial extent, leaving approximately 24.25 mm to the pack rear face. The front-bump envelope study's rear extent is approximately X1127.27, leaving 37.27 mm to the pack front face. These are headline/reservation distances, not complete mounting/service clearances. Imported motor protrusions, axle offsets, pivot bosses, supported output and pack attachments must be checked with real geometry and motion.

### Explicit steering geometry

For 25° rake from vertical and 100 mm trail using 299.9 mm nominal front radius, the steering axis meets the nominal ground at X1580. At height Z its X coordinate is:

```text
Xaxis = 1580 − Z × tan(25°)
combined perpendicular fork/axle offset
      = 299.9 × sin(25°) − 100 × cos(25°)
      = 36.112 mm
```

That offset must be distributed between the real yoke and axle casting geometry. Do not prescribe it again on top of an already-offset donor fork. The upper/lower fork clamp centers are derived by translating the steering-axis points by the actual perpendicular offset, then adding left/right fork spacing. Fork length, spacing, clamp lengths and axle boss details remain supplier/measured inputs.

Model each leg as separate outer tube, sliding tube, axle boss, top cap and dust/seal interfaces with an axial travel parameter. Upper and lower yokes share the steering axis and rotate together. The axle is constrained to both leg bosses. Full steering motion acts on the whole fork/wheel/caliper/fender assembly, not only the tire. Show positive stops and hose/sensor loops.

The zero-pose geometry is a transparent starting construction. Report trail and wheelbase again after static/rider sag and loaded tire radius; do not advertise the input 100 mm as a measured loaded value.

## Rear suspension that actually moves

Use a **single right-side direct-mounted shock** as the next mechanism study, instead of a floating center shock or an uncalculated rocker. The upper eye is fixed to the rear frame at (400,+150,679.392). The lower eye is on the swingarm at (300,+150,399.733). Eye distance is exactly 297 mm at zero pose. Both mounting pins have Y axes. The lower eye follows the same rigid rotation as the rear axle.

This is compatible with a **297 mm / 54 mm-stroke dimensional reference**, such as the published Öhlins KA736 family, but does not select that product's spring, damping, eye hardware, external dimensions or approved application. Its published 46 mm piston diameter is not a spring/body outside diameter. [Manufacturer dimensional reference](https://www.ohlins.com/motorcycle-suspension/street/kawasaki-z-650?v=kawasaki-ninja-650-2025)

| Rear wheel vertical movement from zero | Shock eye distance | Shock compression | Instantaneous wheel/shock travel ratio |
|---|---:|---:|---:|
| 0 mm | 297.000 mm | 0.000 mm | 2.669 |
| 26 mm | 287.238 mm | 9.762 mm | 2.657 |
| 52 mm | 277.427 mm | 19.573 mm | 2.642 |
| 78 mm | 267.551 mm | 29.449 mm | 2.623 |
| 104 mm | 257.595 mm | 39.405 mm | 2.600 |
| 130 mm | 247.546 mm | 49.454 mm | 2.574 |

The wheel path moves rearward to X−21.966 at full bump; it is not a purely vertical slide. The remaining 4.546 mm compared with a nominal 54 mm stroke is **geometric arithmetic only**, not proven bump-stop allowance or coil-bind margin. Supplier dimensions, manufacturing tolerances, dynamic deflection, droop and actual bump-stop engagement remain to be reconciled.

Machine-readable poses are [rear-suspension-kinematics.csv](rear-suspension-kinematics.csv), generated by [tools/rear-suspension-study.py](tools/rear-suspension-study.py). Twenty-one poses include axle and both-eye coordinates, shock axis unit vector/pitch, swingarm rotation, pin axes, travel ratio and remaining nominal stroke. The generator checks fixed arm/lower-eye radii, monotonic compression and the calculated endpoint.

Reserve a provisional 90 mm-diameter shock/spring envelope until actual supplier geometry exists. At Y150 its transverse inner edge would be Y105, nominally 25 mm beyond the centered rear tire's Y80 envelope. Its entire axis is behind the pack's revised rear X670 face. This solves the earlier central shock/pack conflict at the reservation level while keeping the shock below the saddle. Actual spring end fittings, preload adjuster, tire deflection and steering/roll service envelopes still need detailed checks.

Build actual separate eye lugs, a fixed body, translating rod, spring seats, bump stop and coil study around the moving axis. The spring length changes with suspension position; the upper eye stays fixed and lower eye follows the arm. Represent pin joints and bearings explicitly. Visible coil geometry is a parametric illustration until wire diameter, mean diameter, turns, rate, stress and coil-bind are sourced or designed.

### Spring and sag check: the stock spring is not selected

Use an illustrative **220 kg bike plus 90 kg rider/gear**, with 55% rear static load. This is a load example, not a new accepted mass or payload rating. The rear load is 1,672 N. The 130 N/mm published shock spring would give only about 18.25 N/mm local wheel rate at zero pose. Solving the nonlinear mechanism gives:

| Spring / installed preload | Curb sag, example | Loaded sag, example |
|---|---:|---:|
| 130 N/mm / 0 mm | 63.8 mm | 88.9 mm |
| 130 N/mm / 10 mm | 37.8 mm | 63.4 mm |
| 230 N/mm / 5 mm | 23.2 mm | 38.0 mm |
| 250 N/mm / 5 mm | 20.3 mm | 33.9 mm |
| 280 N/mm / 5 mm | 16.7 mm | 28.9 mm |

These cases include changing mechanical advantage and spring preload, but omit gas/friction/damping forces, chassis pitch, tire compliance and dynamic transfer. A plausible geometric stroke fit does **not** qualify a 130 N/mm damper package. The stronger example springs are not claimed available or approved for KA736. Select a supported damper/spring assembly for actual axle loads, ratio, sag and force/velocity/temperature duty; a different stroke/length or lower-leverage arrangement may be preferable. Preload does not change the coil spring rate.

For every load case calculate shock force and frame/swingarm bracket reactions; do not size mounts from rear wheel load alone. The one-sided shock imposes torsion on the swingarm/frame. Use a proper crossmember/triangulated mount and bearing alignment rather than welding a cantilever tab to an illustrative tube. Review spring stress/coil bind, bump-stop force, damper velocity, thermal fade and articulation.

## Preferred drive solution: motor coaxial with independent swingarm pivots

Prefer moving the motor rotor axis to **(540,0,470), coaxial with the swingarm pivot**, and shifting the compact pack forward from X580–1000 to **X670–1090**. This is the next concrete architecture study. With the final-drive input pulley on the pivot axis, its distance to the rear axle remains exactly **562.668 mm** through the rigid swingarm motion. It avoids an extra transmission stage while leaving initial radial motor/pack and front-bump/pack gaps as stated above. It does not establish the final belt width, pulley count, source mounting or installed mass.

Use **independent chassis-supported swingarm pivot bosses**, initially around Y±130 as an interface study. The swingarm must not use the motor bearings as its wheel-load support. The output pulley also needs a defined side-load reaction into the chassis/support structure; it must not silently apply unqualified belt load to motor bearings.

The mechanical section drawing must distinguish these three paths:

1. **Fixed stator path:** motor stator mount → qualified bracket → chassis.
2. **Wheel/swingarm path:** swingarm → pivot bearings → fixed pivot stubs/bosses → chassis, independently of motor rotation and its bearings.
3. **Rotating torque path:** motor rotor/output flange → supported adapter/output member → left final pulley → belt → rear pulley/wheel.

One possible arrangement uses a supported output through a hollow fixed left pivot stub, with the swingarm bearing outside the fixed stub. That is a design avenue, **not an assertion that EMRAX has a simple central 20 mm shaft or that chosen bearings fit**. Supplier rotor/stator flange geometry, adapter load path, bore diameters, bearing spans, fits, axial retention, seals, fixed-versus-rotating clearances, service removal, cable/coolant exit and assembly order must all be drawn. The actual imported assembly's axial protrusions must fit between the supports; the nominal 85 mm motor body is not its entire installation envelope.

The support/adapter can add mass even with a single-stage belt. Count it within the drive/chassis boundaries, obtain supplier approval for any residual motor shaft loads, and retain real motor cooling airflow. Do not label intersecting motor/pivot geometry “clear” merely because their axes are intended to coincide; the fixed and rotating parts need a valid sectioned construction.

### Fallback if coaxial support cannot be qualified

Keeping the earlier separated motor at (440,0,340) while using the new pivot makes motor-to-axle distance change **440.896→473.071 mm**, a **32.175 mm variation** over the rear motion. A fixed belt cannot simply stretch to accommodate that. A specially qualified tensioning arrangement or a pivot-coaxial supported jackshaft becomes necessary.

For a jackshaft fallback, a fixed-center 1:1 primary stage could connect the separated motor to a supported shaft on the pivot axis, followed by the roughly 3.1:1 final belt. Count both primary pulleys, primary belt/coupling, shaft bearings/housings/seals, final pulleys/belt and guards. Its extra-stage mass/power cost is a reason to prefer the coaxial-motor study, rather than hide that penalty.

Two hypothetical 97%-efficient stages combine to **94.09%**, rather than the prior single-stage 97% assumption. At the older CdA0.35/125 mph road-load point of 39.76 kW at the wheel, shaft demand becomes approximately **42.26 kW / 76.09 Nm** at 5,304 rpm, above the current 75 Nm continuous motor reference. Improved actual drag can reduce demand; real motor/inverter/transmission maps must replace rough efficiencies in either architecture. A fallback must not inherit unchanged range/power/mass claims automatically.

Put the **final belt and drive pulleys on the left, negative Y**. Put the **rear brake disc/caliper on the right, positive Y**. The previous CAD puts the rear disc on the same side as the intended belt; correct this. The generated owner render is not authoritative for these inconsistent mechanical details. The right shock sits forward of the rear brake, but caliper service and hose motion must still be modeled.

## Buildable assembly detail to add next

| Assembly | Concrete next CAD definition | What cannot be invented from current information |
|---|---|---|
| Headstock | Bearing-seat housing, stem, two yokes, clamp splits/bolts, steering stops and lock mount | Material, race fits, clamp forces and approved tightening |
| Fork | Separate sliding bodies, axle bosses, caps, fender and caliper mounts constrained to shared travel/steer | Exact donor leg length, yoke offset, bore/bolt interfaces and damping |
| Wheels | Rim profile, hub, actual bearing/spacer/seal stack, axle and retention | Supplier spoke shape, hub offsets, rim widths and load capacity |
| Front brakes | Two rotors, real caliper and carrier envelopes, pad slots, mount centers, fittings and hose route | Disc thickness/offset, caliper dimensions and supplier joint specifications |
| Rear brakes | Right-side rotor/caliper/carrier, axle antirotation interface, encoder and hose loop | Exact bracket stack and supported ABS calibration |
| Swingarm | Double-sided load-carrying members, transverse pivot housing, rear axle blocks, right shock mount, brace and drive clearances | Wall sections, welds, fatigue margins, fits and approved fasteners |
| Rear shock | Articulated eye/body/rod/spring assembly driven by the provided pose data | Actual eye bores/widths, external envelope, spring/damping and bump-stop behavior |
| Motor/output | Supplier model aligned by shaft/mount datum; mounting plate and supported output/jackshaft bearings | Shaft side-load capacity, coupling fit and motor supply revision |
| Chassis/pack | Headstock-to-pivot structure plus explicit pack attachment interfaces and removal sequence | Cell-case structural contribution and fully qualified materials/joints |
| Seat/pegs/bars | Pan, support rails, latch, separate foam/cover, supported pegs, risers, actual control clearances | Final anthropometric fit, pad comfort, passenger rating and loaded lean clearance |
| Lighting/screen | Optical module reservation, beam mounting/aiming bracket, screen stand-offs and structure | Approved lamp optics, headlight dimensions or measured buffeting |

Front brake calipers can initially occupy the trailing rotor quadrant, for example near X1360/Z350 with the front axle at X1480/Z299.9. This is an illustrative interface construction point, **not supplier caliper CAD**. Position real bracket holes and rotor faces from a matched assembly before calling it fitted. A model that gains plausible-looking calipers but still lacks the rotor/carrier relationship remains a concept model.

## Integrate the exterior with the mechanism

Use these as proposed construction zones rather than final styled coordinates:

- Main rider seat support around X260–620, support height around 780–805; separate padded surface and pan. Front seat nose narrows above the pack's rear/upper transition. Tail rises toward X−100 to260 but does not become a flat rectangular slab or imply a rated passenger seat.
- Nose/headlight study near X1285/Z795, with supplier optic and aiming bracket reserved separately. Verify clearance to front wheel/fender at bump and steering; the housing is not an approved light simply because its front looks like the render.
- Screen base near X1290/Z840 and top near X1120/Z1160, with real supporting brackets returning into the chassis/cockpit structure. Check bar/mirror motion, sightlines and helmet wake.
- Upper body connects headlight/cockpit to the seat nose through a few controlled curves, with left/right sections and curvature continuity. Lower battery body follows real case/cooling support; make removable panel joints before decorative chamfers.
- Side radiators/ducts require actual core/fan space, through-flow and hot-air exits. Louvers alone do not supply cooling. Keep tire spray and charging fault vents out of the ordinary cabin/rider flow path.
- Keep left/right split views and local cutaways so that panels are visibly supported. Add lamps, indicators, reflectors, mirrors, plate and stand in the proportions study rather than after “final styling.”

The 330 mm-wide pack means body width and leg/seat contact must be examined with an actual rider buck. Tapering a cosmetic surface cannot make a wide hard part disappear. Any later aerodynamic result must use that ordinary rider, real road equipment and cooling paths.

## What this rework has actually established

A 1,480 mm study now has an explicit steering construction, a calculable rear-wheel/shock mechanism, a spring-rate warning, and a defined single-stage coaxial drive architecture that keeps belt length constant through suspension motion. It identifies the coaxial fixed/rotating support interfaces and quantifies the extra transmission cost/power/mass trade if a jackshaft fallback is needed. The 21-pose suspension calculations are reproducible and internally checked. No complete body, structure, shaft, brake, spring or tire qualification follows merely from that arithmetic.

Prioritize rebuilding those mechanisms and a coherent exterior around the current discrete-cell package. Then inspect the whole assembly in side/front/top and rider-section views, actual motion and service states. The next meaningful review is the assembled motorcycle with working geometric relationships, not another count of anonymous valid solids.
