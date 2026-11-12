# Lower stepped pack — exact 700-cell proposal

October 25, 2026, US Central. Codex (GPT-6 family). **Discrete geometry study, not a qualified battery or build release.** Coordinates and all 700 cell identities are in [cell-layout-proposal.json](cell-layout-proposal.json).

The taller compact pack can be made lower without deleting cells: lay each pouch with its **8.55 mm thickness vertical**, place **two long-body columns across the bike**, and distribute the vertical seven-cell stacks among ten fore/aft columns. A stepped rear upper corner clears the motor/pivot region; a lower front roof keeps the upper front region available for rider/body packaging.

**Candidate outer extents: 515 mm fore/aft × 330 mm wide × 430 mm high**, spanning X560–1075, Y±165, Z150–580 mm. This is an actual stepped shape containing the proposed cells, not a smaller exterior hiding the former rectangular pack. Its extruded outer volume is about **61.695 L**, before subtracting shell material, cooling, insulation and hardware. Electrical reference remains **100s7p / 700 cells / 26.299 kWh typical / 25.704 kWh minimum**. No new usable-energy or life claim is earned by rearranging them.

## Discrete cell placement

Use the catalog-maximum body dimensions 126.4 × 43.2 × 8.55 mm at the stated 30% SOC manufacturing basis. Orient them **X43.2 / Y126.4 / Z8.55 mm**. That is a rigid rotation, not a scale change. Supplier-permitted orientation, terminal envelope, aged swelling, compression and cooling conditions remain unconfirmed.

Two transverse body origins are Y−135.2 and Y+8.8 mm, giving overall body extent Y±135.2 and a 17.6 mm gap between the two long-body columns. The outer ±165 mm enclosure leaves 29.8 mm per side before shell and functional hardware. No electrical-clearance credit is assigned to these raw gaps.

| Fore/aft cell minimum X, mm | Vertical layers in each transverse lane | Physical 7p groups per lane | Cells, both lanes | Highest cell body Z, mm |
|---:|---:|---:|---:|---:|
|575|14|2|28|293.55|
|626|21|3|42|363.55|
|675|42|6|84|573.55|
|725|42|6|84|573.55|
|775|42|6|84|573.55|
|825|42|6|84|573.55|
|875|42|6|84|573.55|
|925|35|5|70|503.55|
|975|35|5|70|503.55|
|1025|35|5|70|503.55|
|**Total**|**350 layer positions per lane**|**50 groups per lane**|**700**|—|

For each column and lane, start at Z155 mm and increment 10 mm per cell. Seven consecutive vertical layers form a physical seven-cell stack, nominally one 7p group. Thus there are **100 physical7p groups**, assignable to 100 series positions. The JSON labels S001–S100 and P1–P7 for count and traceability only; it does **not** release the electrical joining route or tell anyone how to assemble an energized pack.

The physical group scheme avoids a nominal parallel group split arbitrarily across distant columns. All layer counts are multiples of seven. Each seven-cell stack spans 68.55 mm before plates/support; spacing between consecutive seven-layer groups is 1.45 mm at this pitch, so there is **no generous hidden room for independent cartridges**. Shared versus separate restraints and thermal interfaces need actual engineering.

## Outer profile, including the motor cutout

In the XZ plane, use these ordered vertices and extrude across Y−165..165 mm:

```text
(560,150) → (1075,150) → (1075,515) → (922,515)
→ (922,580) → (670,580) → (670,374)
→ (623,374) → (623,344) → (560,344) → close
```

The rear roof rises in two steps around the motor. The first low region contains the 14-layer stacks; the next contains the 21-layer stacks. The middle carries 42 layers. The front roof drops to 515 mm because its three columns contain 35 layers. This low forward region and overall 580 mm pack top substantially improve the body/rider package compared with the previous 720 mm top.

The front-upper step is at **X922, not X920 mm**: the tall column beginning X875 ends at X918.2 mm, so a 920 mm step leaves only 1.8 mm before the outer wall. At X922 it leaves 3.8 mm; the lower front columns begin at X925. This detail shows why a stepped outline must be checked against complete cell bodies rather than drawn around their centers.

## Independent numerical checks

The JSON was generated using the project-local bundled Python runtime with ordinary geometry arithmetic. It is not a CAD-kernel verification. Checks include 700 unique cell IDs; 100 groups with seven cells each; cell full-body extents; distance of each cell rectangle to every axis-aligned outer-profile segment; and containment inside the proposed 3 mm shell region. The monotone stepped roof and the individual cell X positions allow full rectangular-body containment to be checked without relying only on cell centers.

The **minimum cell-to-outer-profile distance is 3 mm**, leaving **zero additional local clearance beyond the hypothetical 3 mm shell** at some faces. This matters: geometric containment is not a completed module interface. Electrical isolation, manufacturing tolerance, cooling, restraint and service may require increasing local space, moving cells or reshaping the case. The model must report this limitation rather than calling every empty interval a validated allowance.

### Motor and coaxial pivot

Use motor/pivot center **X540/Z470 mm**. The nominal 208 mm motor headline is insufficient for clearance: the imported supplier STEP bounding geometry calls for the more conservative **105.75 mm radius** screen used here. The rear roof levels were reduced from 347 / 377 to 344 / 374 mm to preserve room for that actual reference size.

For the conservative circular body versus the full outer polygon, the closest region is near the623/374 mm step corner. The calculated minimum gap is approximately **21.15 mm**. The560/344 mm corner is approximately21.83 mm away from the circle; the main rear vertical wall at670 is24.25 mm beyond the105.75 mm radius at motor-center height. These are ideal geometric gaps, not supplier-approved installation clearances.

A smaller concentric pivot tube is bounded by the same circle test. That does not define an outboard pivot bearing, housing, drive pulley, motor support or shaft load. With the case spanningY±165 mm, separate outboard supports need their real widths, bolts, seals, mounting plates and insertion/tool paths. An axis marker is not a support assembly. Actual supplier motor geometry and its fittings/rotor/mount envelope still require native-kernel checks at the proposed rotation and position.

### Front tire at full nominal bump

At 1,480 mm wheelbase, 125 mm axial front compression and 25° rake, the current simple model gives:

```text
front axle X =1480−125sin25° =1427.173 mm
front axle Z =299.9+125cos25° =413.188 mm
tire-cylinder rearmost X =1427.173−299.9 =1127.273 mm
pack front X =1075 mm
conservative longitudinal separation =52.273 mm
```

That X-separation conservatively clears this nominal tire cylinder regardless of the particular pack roof level. It does not include steering lock, fender/caliper/brake-hose travel, tire growth/load deformation, fork/yoke offsets, tolerances or compliance. All those remain necessary. The front profile does not extend to 1190 mm to recreate the old tire collision.

## What occupies the remaining space

The outer shape has about61.695 L compared with32.681 L of solid catalog cell bounding volume. Their difference is **not 29 L of unconstrained usable hardware space**: many gaps are thin/disconnected; any shell, support, insulation or joining makes some of them inaccessible.

| Function | Required next representation |
|---|---|
|Terminal/tab envelope|Actual supplier terminal geometry and allowed bend/joining orientation for these flat-lying cells; no decorative terminal stubs|
|Parallel-stack restraint|Seven-cell stack pressure faces, tolerance and life growth, load application, relaxation and replaceability; orientation requires supplier confirmation|
|Thermal system|Real heat path from cell faces/edges, cooling plates/manifolds and electrical insulation; quantified local heat/gradient/flow evidence|
|Series connections|Protected route between 100 groups, terminal access, joining qualification, resistance/heating and dielectric behavior; present labels are identifiers only|
|Protection/electronics|Real fuse/contactors/precharge/BMS/sensors/service disconnect and cable bend/support envelopes; dedicated supported bay, not assumed thin gaps|
|Case/vent/seal|Actual material, thickness, lid, joints, mounts, impact protection, drainage and vent paths away from rider; notch corners need structural analysis|
|Service/assembly|Fixture and cartridge/stack insertion sequence, inspection access and complete pack removal; no claim that the closed solid is manufacturable as drawn|

The lower front roof and the free region over the shorter rear stacks may help a dedicated electronics/service bay, but placing electronics there changes closure shape, heat protection and removal access. Count those volumes before accepting this outer profile as the complete pack-system boundary. The pack cannot simultaneously spend a cavity on cell growth, coolant, busbars and electronics.

## Mass and chassis implications

Pouch count/mass does not change. A thinner/lower silhouette does not automatically earn an 85% cell mass fraction. Unlike a plain rectangular shell, the stepped case introduces corners, cover seals, joining and load paths. No finished enclosure mass is assigned here; calculate it from the actual manufactured construction and include all internal systems. The existing under 400 lb calculation remains an unproven allocation.

The 330 mm pack width is a lower-body reservation, not a narrow-knee design claim. Its maximum height is 580 mm, with front 515 mm and rear 344 / 374 mm; that permits the upper rider/body region to be developed without the taller box but does not establish comfort. Show a clothed rider, seat/pan, pegs, brake pedal, controls, frame, shock and steering in the same assembly. If frame centerlines remainY±195 with 16 mm tube radius, nominal pack-to-tube gap is 14 mm before brackets and tolerances.

A lower pack changes CG/inertia and suspension/frame load paths. Update whole-bike mass properties only after real component masses and their positions exist. Reevaluate damping, ground/lean clearance, bottom impact protection and service support rather than treating lower CG as an unconditional handling improvement.

## CAD acceptance for the next iteration

Keep all 700 bodies and their identity mapping in the native assembly. Use the supplied polygon, not a rectangular box drawn across its motor cutout. Report full-body cell containment and actual local inner-wall clearances. Check the actual motor STEP, coaxial support geometry, full suspension/steering motion, frame/shock, brake/drive/hose interfaces and service sweeps. Mark the case walls and joining/cooling/restraint as proposed until those systems are designed.

This candidate demonstrates a specific way to preserve the energy while making the mechanical package lower and shorter. It closes a geometric avenue that the earlier arrangement missed. It does not close battery qualification, safety, mass, manufacturing or complete-bike release.

