# Motor, independent swingarm pivot and output carrier

October 25, 2026, US Central. Codex, GPT-6 family. **Source-geometry audit and proposed mechanical section; not a manufacturing release.** This report inspects the actual EMRAX 2022 STEP rather than treating an 85 mm-long cylinder as the motor. The [JSON report](motor-pivot-interface.json) preserves its SHA-256, source geometry, hole axes, transform and simplified load examples. The root CAD generator has not been edited by this work.

## Conclusions for the next assembly

The coaxial motor/pivot architecture is mechanically plausible, but requires **three independent paths**: fixed stator reaction, independently supported swingarm/wheel loads, and rotating output torque through its own supported shaft. The motor is an **outrunner**: its external rotor rotates. A frame clamp around the round outer housing would immobilize or damage it. A cross-bike fixed pivot shaft cannot simply pass through the motor's center; the source assembly includes shaft/sensor hardware there.

Use the front rotor flange to drive a separately supported output, put the belt on the left, and place a fixed stator mounting structure on the right. The motor's internal bearings must not silently become suspension or belt-load supports. A misalignment-capable coupling must separate the motor rotor from the two-bearing external shaft, otherwise four radial bearings and frame deflection can impose an uncontrolled load path.

The proposed 30 mm shaft / 55 mm-bearing bore / 70 mm carrier / 90 mm swingarm bearing envelope is a credible **section study**. Its original output-bearing positions need revision: the overhung pulley magnifies bearing reactions and the published 6006 ratings do not demonstrate adequate life. Keep the parts identifiable and measured, but do not label the original bearing arrangement sized or approved.

## Actual STEP findings

Source: `sources/EMRAX-208-LC-resolver-2022.step`, header timestamp **2022-05-09T07:48:25**, supplied assembly name `208_lc_resolver`; **93 solids**. Its source-coordinate main rotor axis is **X through Y=Z=0**. Bounds are X−18 to105.853922 mm and Y/Z±105.75 mm. The complete assembly is approximately123.854 mm axially, beyond the headline85 mm motor body. Included fittings, sensor parts and an additional plate must not be discarded merely to fit the package.

The following are **CAD observations**, not a current supplied-part tolerance drawing:

| Feature | Observed source geometry | Interpretation / restriction |
|---|---|---|
| Front/output face | Source X−18 plane | Front rotor attachment side, away from coolant/phase/resolver |
| Output face outer circle | Ø94 | Basic CAD face extent; no fit implied |
| Output pilot bore | Ø56 | Candidate locating bore; current tolerance, depth and datum require supplier drawing |
| Output bolt circle | Ø75, six axes60° apart | Clocking22.5°+60°k in sourceYZ, measured from+Y toward+Z |
| Output modeled minor cylinders | Radius3.4 mm in central hub, with clearance/counterbore geometry in adjacent rotor part | Consistent with an M8-family interface; **thread/depth is not inferred from CAD** |
| Rear stator plane | Source X67 | Stationary mounting datum candidate |
| Rear stator bolt circle | Ø78 | Six evenly spaced available locations may be selected at0/60/120/180/240/300° in this STEP |
| Rear modeled minor cylinders | Sixteen radius3.4 mm axes on the78 mm circle | Other angular positions coexist with fittings; sixteen observed holes does not mean use every hole |
| Sensor/stator spacer | Source X67–72.5, thickness5.5 mm | Preserve sensor/fitting stack; do not replace by an arbitrary flat plate |
| Additional included plate | Source X72.5–78.5, thickness6 mm; radial extent105.75 | Delivered/optional/customer scope not established from STEP names; request explicit disposition |
| Sensor/shaft region | Included geometry extends centrally to around X103.7 and fittings to105.854 | No clear empty through-bore is assumed |

Source solid/face indexes in the JSON are **zero based**, tied to this exact file hash, and cannot be used as permanent topological names after remodeling or STEP revisions. The observed front face is solid69/face161; the stator face is solid35/face9. Features are corroborated by analytic cylinder/plane geometry, not a screenshot estimate.

### Placement into the motorcycle

For comparison with the current centered import, rotate source+X to vehicle+Y using+90° aboutZ and translate:

```text
vehicleX = 540 − sourceY
vehicleY = sourceX − 43.9269610015
vehicleZ = 470 + sourceZ
```

This places the rotor/pivot axis at vehicleX540/Z470, with front output toward **negative vehicleY**, as wanted for the left belt. It places the observed output plane atY−61.927, stator plane atY+23.073, spacer rear atY+28.573 and included plate rear atY+34.573. Source assembly extremes become approximatelyY±61.927. These are axial-placement coordinates, not assertions that its bounding-box midpoint is a mounting face.

The JSON gives individual front-hole and stator-hole points after that transform. If the motor is clocked about its rotor axis for better coolant/phase routing, transform the entire pattern and fittings together. Do not rotate a bolt pattern independently of its source motor.

## Current supplier instructions versus old CAD

The manufacturer's currently linked **installation manual v1.7**, indexed pages12–13, identifies front flange output and rear optional ESO. For208 front FSI it lists a7 mm flange, six grade10.9 M8×25 fasteners, supplied wedge washers and40 Nm; custom front flanges use the factory thickness and positive locking, locate in the bore with a g6 shaft fit, and must not intrude into the motor. Rear stator mounting uses at least six evenly spaced grade10.9 bolts, M8×1.25 with16–22 mm protrusion measured from its defined surface;208 spacer thickness is5.5 mm. These **supplier configuration instructions are not a released Bavuso joint record**. [EMRAX v1.7 manual](https://emrax.com/wp-content/uploads/2026/01/RAZV_ZS_EMRAX_Users_Manual_v1.7.pdf)

Do not combine a legacy drawing's engagement limits, 2022 CAD bore and current torque table into an unreviewed fabrication instruction. Freeze the actual motor configuration/revision, washer stack, current mounting drawings and supplied FSI option. Current manual information was available through indexed manufacturer text; direct full-PDF retrieval timed out during this review. The older v1.6 was readable, but is not used to silently supersede v1.7.

The public shaft-options document distinguishes factory front flanged adapters from rear extended shafts, and notes sensor packaging implications for rear output. This supports investigating a front-output adapter; it does not approve a customer shaft design or all sensor combinations. [Manufacturer shaft options](https://emrax.com/wp-content/uploads/2025/06/emrax_shafts_expl.pdf)

## Proposed section: four distinct assemblies

| Assembly | Mechanical role | Proposed definition for detailed CAD |
|---|---|---|
| Right stator plate | React motor torque into frame, hold motor datum | Six-hole sourcedPCD78 pattern, current spacer retained, structurally braced to chassis, access around resolver/fittings |
| Left fixed carrier | React output bearing and left swingarm-bearing forces into frame | Machined bearing cartridge, frame flange/brace and independent70 mm pivot journal; not connected to rotating motor casing |
| External output shaft and coupling | Carry torque to pulley while allowing motor/output alignment relief | Motor-side front flange or factoryFSI, qualified misalignment coupling, separate30 mm output shaft with two supported bearings, pulley and controlled retention |
| Swingarm pivot system | Carry wheel/shock/brake loads independently of motor | Left bearing around fixed carrier and separate right fixed stub; arm bearing retention/seals; frame crossmember defines both axes |

The right pivot stub terminates outside the motor and its sensor envelope. There is no full fixed axle passing through the rotor. The left carrier's output shaft rotates inside it; the swingarm bearing is outside it and moves only with suspension. Those motions must appear as separate CAD parts/joints, not a fused shaft/tube/arm solid.

### Coupling and axial stack

With the comparison placement above, the front flange atY−61.927 and an inner output bearing centeredY−110 leave only about41.6 mm from the flange to that bearing's near face, before any flange thickness, adapter or coupling. A7 mm adapter consumes part of it. **A coupling has not been selected or proven to fit this interval.** Draw the complete factoryFSI/custom flange, coupling hubs, flexible element, shaft engagement, bolts, tool path and bearing shoulder. Move the axial motor position, bearing, pulley or frame if a real coupling requires it.

An integral rigid shaft bolted directly to the rotor and located by two further bearings does not provide alignment relief merely because it has a slip fit somewhere. Use a supported coupling architecture with specified angular/parallel/axial capability, torque/speed rating, torsional stiffness and environmental protection. Its permissible misalignment is not permission for loose belt tracking. Define a single locating bearing and a deliberate floating strategy for external shaft thermal expansion; do not preload the entire motor/external stack accidentally.

## Bearings: verified dimensions and reference ratings

The requested SKF standard product pages were not text-readable, but manufacturer-hosted catalog extracts were available. Ratings below apply to the stated catalog entries, not every seal/clearance suffix or another brand with the same basic size.

| Candidate | Size mm | DynamicC / staticC0 | Catalog mass | Role and caution |
|---|---|---:|---:|---|
| SKF6006 |30×55×13 |13.8 /8.3 kN |0.12 kg | External output comparison; open bearing requires a sealing/lubrication solution |
| SKF61814 |70×90×10 |12.4 /13.2 kN |0.14 kg | Swingarm pivot envelope; oscillating service needs its own selection method |

[SKF6006 manufacturer catalog](https://cdn.skfmediahub.skf.com/api/public/0901d1968097689a/pdf_preview_medium/0901d1968097689a_pdf_preview_medium.pdf), [SKF61814 manufacturer catalog](https://cdn.skfmediahub.skf.com/api/public/0901d19680416a2b/pdf_preview_medium/0901d19680416a2b_pdf_preview_medium.pdf).

For output bearings, choose a seal/grease/clearance suffix against actual speed, temperature, water and contamination. For pivot bearings, motor speed is irrelevant: the outer ring follows limited suspension oscillation. False brinelling, lubrication replenishment, fretting, shock and combined axial/radial load can govern. A favorable rotating-bearing L10 does not close pivot durability.

### The proposed overhang needs improvement

Initial output bearing centersY−110 and−165, pulley planeY−211 give55 mm bearing span and46 mm pulley overhang. For a simplified radial belt resultantF:

```text
outer bearing reaction = F × (1 + 46/55) = 1.83636F
inner bearing reaction = −F × 46/55     = −0.83636F
```

At4 kN belt resultant the outer reaction is7.345 kN, already close to the8.3 kN static catalog rating before shock, axial force or an agreed static safety factor. At6 kN it is11.018 kN, above that rating. A150 Nm torque with a hypothetical40 mm pitch radius requires3.75 kN tension **difference**; this is not the complete resultant, because installation tension and span directions also matter.

Move the outer output bearing towardY−195 if the frame permits, retaining the inner atY−110. Span becomes85 mm, overhang16 mm, outer reaction1.18824F:4.753 kN at4 kN belt force and7.129 kN at6 kN. This is an improvement, **not a completed bearing selection**. Straddling the pulley can reduce overhang further but widens the assembly and complicates service/guarding. Obtain the sized pulley/belt loads before freezing either stack.

At constant4 kN belt resultant and5,304 rpm, the simple unmodified SKF6006 L10 calculation for the outer bearing gives approximately21 hours for the initial stack and77 hours for the revised stack. These intentionally severe **constant-load examples are not predicted vehicle life**: real torque/speed/load distributions may be very different. They demonstrate why the bearing's headline speed rating or static survival is insufficient. Integrate the actual duty spectrum, reliability, lubrication, contamination, fits and shaft deflection before selection.

### Nominal shaft/carrier stress screens

For a **solid30 mm shaft**,150 Nm torque gives28.29 MPa nominal torsional shear. At4 kN radial load and46 mm overhang, nominal bending stress at the outer-bearing section is69.42 MPa; simple von Mises combination is84.97 MPa. Moving the bearing to16 mm overhang reduces bending to24.14 MPa and that combination to54.63 MPa. No notch, spline, keyway, press-fit, residual stress, alternating bending, thermal effect or fatigue factor is included. These numbers cannot select material or shaft diameter by themselves.

A70 OD /55 ID carrier has7.5 mm radial wall and second moment about0.729×10^6 mm⁴. For an illustrative4 kN load acting131 mm from a fixed root, nominal tube bending is about25 MPa. The real root/cap/bolt pattern, swingarm/shock reactions, torsional loading, bearing-seat distortion and frame flex are omitted. A70/55 straight tube100 mm long weighs about1.16 kg at assumed steel density7,850 kg/m³, versus0.40 kg at assumed aluminum density2,700 kg/m³, before shoulders, flange, caps or bolts. Aluminum does not automatically qualify: thermal expansion, fretting, bearing-seat fit/stiffness and fatigue need assessment.

The 55 mm internal diameter cannot be the entire straight through-bore if it must retain6006 outer rings: include qualified shoulders/end caps and bearing installation/removal access. Similarly, the external70 mm pivot journal needs suitable abutments, not an unsupported thin shoulder. Caps and locking nuts must clamp the intended ring/spacer stack, never transmit tightening force through the rolling elements.

### Lighter bearing avenues

JTEKT lists30×47×9 **6906-2RS**, C9.05/C0 5.00 kN,0.045 kg, and30×42×7 **6806-2RS**, C5.65/C0 3.40 kN,0.026 kg. They could reduce bearing/carrier mass, but their lower capacity does not support the initial overhung stack. Two6906-size bearings save roughly0.15 kg relative to the two0.12 kg6006 references; the housing reduction may matter more. Ratings and suffixes are manufacturer-specific. [6906 manufacturer](https://koyo.jtekt.co.jp/en/products/detail/print.php?pno=6906+2RS), [6806 manufacturer](https://koyo.jtekt.co.jp/en/products/detail/print.php?ClassKey=010-010-020&pno=6806+2RS).

If smaller output bearings permit a smaller carrier, reevaluate the outer pivot-bearing size and journal, rather than retaining70 mm solely because it appeared in the first sketch. A needle/tapered/other pivot arrangement may be useful for oscillating load and stiffness, but needs its own race hardness, axial-location, seal, preload and load analysis. No replacement bearing is selected here.

## Brackets, caps, fasteners and access

The stator bracket must leave rotor rotation clearance, resolver service access, coolant hose bends, phase cable termination and tool access to the six actual mounting positions. Do not cover the outrunner with a clamp ring or block required airflow. Clock the motor as an assembly if access requires it, then recheck body/fitting sweeps.

Use removable outboard carrier caps and planned bearing extraction directions. Provide a positive shaft retention arrangement and pulley-hub installation method that does not hammer load through the motor bearings. Draw socket/hex tool cylinders along every attachment axis and a physical shaft/pulley withdrawal route. Bolt head access to the rotor flange must be demonstrated with the fixed pivot/carrier installed, or explicitly occur earlier in the documented assembly sequence.

Proposed assembly logic to validate: locate the right stator support and left carrier datums; assemble motor/front flange and coupling input with specified access; install independent output shaft/bearings/coupling and align; assemble swingarm onto separate fixed journals and set its retention/clearance; install pulley/belt/guard and qualify alignment/tension; connect services and check all motions. This is a sequence hypothesis, not a mechanic's issued instruction. CAD must show that each step is physically possible, including removal without opening the motor.

## Remaining supplier and engineering questions

1. What exact currently supplied208LC winding, rotor/frontFSI, stator spacer, resolver kit and installation drawings correspond to this2022 geometry? Which included plate is supplied, optional or customer structure?
2. Confirm current pilot bore/tolerance/depth, output bolt circle/thread/depth/washer stack, stator datum/threads, permitted mounting loads, rotor axial travel and minimum dynamic clearance.
3. Obtain allowable radial/axial force and moment at the output versus speed/life, permitted coupling arrangement, and whether the proposed external support changes warranty or application approval.
4. Supply loaded torque-speed/efficiency/thermal maps across actual battery voltage and inverter current limits for MV and LV+100% candidates. Resolve sensor, switching and configuration compatibility.
5. Size the actual belt, tooth counts, installation tension, resultant load vectors, reversal/shock duty and required shaft stiffness, then repeat bearing/shaft/carrier/frame fatigue analysis.
6. Finish fixed/floating bearing fits, shaft/housing tolerances, material/heat treatment, cap/bolt/journal stress, corrosion/sealing, service procedure and qualified assembly alignment limits.

**Top-speed drive matching remains open.** The current LC reference75 Nm continuous versus roughly73.8 Nm shaft demand at the older125 mph/CdA0.35/3.1 ratio point leaves very little reference margin. A working coaxial mechanical layout does not establish voltage-limited torque, installed thermal capability or sustained speed. No supplier inquiry was sent by this work.

This audit gives the next CAD real rotor/stator interfaces, a defined independent-load architecture and a quantified reason to revise the output bearing stack. It does not turn a sourced hole pattern into a fully qualified motor-pivot assembly.
