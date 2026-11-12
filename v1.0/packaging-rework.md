# Compact pack rework — preserve the cells, change the arrangement

October 25, 2026, US Central. Prepared by Codex (GPT-6 family). This is an independently calculated packaging proposal for replacing the long V1.0 battery arrangement. It is not a qualified module, electrical joining design or manufactured pack specification.

**Recommended next CAD layout:** rotate the pouch bodies, organize the same 700 cells into ten short, wide cartridges, and reserve **420 mm fore/aft × 330 mm wide × 570 mm high** for the complete pack study. The rework adopts **1,480 mm wheelbase** as its next engineering proposal for head/rider packaging, with the smaller 1,420–1,450 mm layouts retained as comparisons. This makes a compact layout geometrically plausible without reducing the 100s7p energy or concealing the existing 690 mm pack inside a fairing. No wheelbase change is an owner-approved requirement merely because it appears in CAD.

The existing 1,640 mm wheelbase was driven partly by one unnecessarily long pouch orientation. It should not become an unquestioned requirement. The compact layout still needs real tabs, cell restraint, cooling, enclosure, frame, drive, suspension and rider integration. It changes the packing problem; it does not finish it.

## Fixed basis and what can change

Keep all **700 SA504-reference cells**, **100 series × 7 parallel**, **26.299 kWh typical / 25.704 kWh minimum reference energy**, and **68.11 kg typical total cell mass**. Dimensions below use the previously sourced catalog maxima **126.4 × 43.2 × 8.55 mm**, stated at the catalog's 30% SOC basis. No aged-swelling or compression allowance has been established. Changing orientation does not change electrical energy, cell mass or supplier charge limits.

Total solid cell bounding volume is **32.681 L**. None of the proposed whole-pack volumes is a claim that all remaining volume is usable: separation, support, interface geometry, fault venting, manufacturing and service determine that.

The initial V1.0 arranges the long cell direction fore/aft. One cartridge has five long cells in X, two short cell rows in Z and seven parallel layers in Y. Ten such cartridges arranged two across/five high lead to the 690 × 220 × 550 mm pack reservation. The alternative uses the thin direction fore/aft, so each group of seven becomes a short compression stack instead of extending every cartridge over five long cells.

## Option A — short fore/aft, tall and moderately wider

Orient each cell body as:

| Vehicle direction | Cell dimension |
|---|---:|
| X fore/aft | 8.55 mm thickness |
| Y transverse | 126.4 mm long body dimension |
| Z vertical | 43.2 mm short body dimension |

One proposed **10s7p physical cartridge** is seven layers in X × two columns in Y × five rows in Z. The seven layers may represent one parallel group; the ten Y/Z positions represent ten series groups. This is a count/topology reference, **not an approved interconnect route**. Final terminal orientation and insulation may require changing it.

For the more useful first-CAD reservation, use provisional cell pitches **10 mm X / 144 mm Y / 50 mm Z**, and cartridge origins **75 mm apart in X / 260 mm apart in Z**. Arrange five cartridges fore/aft and two tiers vertically. The physical count is:

```text
per cartridge: 7 × 2 × 5 = 70 cells
whole pack:   5 fore/aft × 2 tiers = 10 cartridges
total:        70 × 10 = 700 cells
```

Exact bounding extents of the cell bodies, rather than pitch multiplied blindly by count:

```text
one cartridge X = (7−1) × 10 + 8.55 = 68.55 mm
one cartridge Y = (2−1) × 144 + 126.4 = 270.40 mm
one cartridge Z = (5−1) × 50 + 43.2 = 243.20 mm

all cells X = (5−1) × 75 + 68.55 = 368.55 mm
all cells Y = 270.40 mm
all cells Z = (2−1) × 260 + 243.20 = 503.20 mm
```

The proposed **420 × 330 × 570 mm** outer study region is **79.002 L**. The global differences between outer dimensions and bare-cell extents are **51.45 / 59.60 / 66.80 mm** respectively. They are available dimensional reservations, not validated hardware allowances.

The geometry provides 1.45 mm between adjacent broad cell faces at the chosen X pitch, 6.45 mm between successive seven-layer cartridge stacks, 17.6 mm between the two transverse long-body columns, 6.8 mm between cell rows vertically and 16.8 mm between the two cartridge tiers. These gaps must be allocated deliberately; they cannot each be promised simultaneously as cooling channel, electrical clearance, swelling accommodation and structure.

### Explicit candidate coordinates for CAD

Whole-pack outer region: **X580–1000, Y−165–165, Z150–720 mm**, in the existing rear-contact-origin coordinate system. The adopted rework moves the cell array toward the rear/bottom to preserve a larger fore/upper hardware study region:

```text
for module_foreaft m = 0..4
for module_tier    t = 0..1
for layer          p = 0..6
for column         c = 0..1
for row            r = 0..4

cell minimum corner:
X = 595.00 + 75m + 10p
Y = −135.20 + 144c
Z = 165.00 + 260t + 50r

cell size = (8.55, 126.40, 43.20) mm
```

Resulting full array extents: **X595.00–963.55, Y±135.20, Z165.00–668.20 mm**. A nominal 3 mm closed shell has inner bounds X583–997, Y±162, Z153–717 mm. Complete cell bodies fit that ideal cavity, leaving 12 mm minimum rear and bottom clearance and larger front/upper reservations. Those are geometric differences, not validated tab/cooling/restraint allowances. Show the actual hardware occupying them. Do not treat the named origin as a released mounting datum.

At 330 mm overall width, the enclosure extends 55 mm farther per side than the previous 220 mm box. Keep this width in the central/lower body. Check knees, pegs, rider calf movement, lean clearance, frame thickness and styling before accepting it. A narrower knee upper shape may be possible above the full cell array, but cannot remove occupied cell volume. A stepped/tapered enclosure needs a corresponding discrete-cell rearrangement.

### Tighter comparator, not preferred reservation

Using cell pitches 10 / 132 / 50 mm and cartridge pitches 70 X / 250 Z yields a **348.55 × 258.4 × 493.2 mm** array. A **400 × 310 × 550 mm** region would contain that array with global differences 51.45 / 51.6 / 56.8 mm. Its transverse central gap is only 5.6 mm and cartridge X gap only 1.45 mm. This is useful to bracket how the cell math drives volume, but is a weaker hardware/service reservation. Use the larger Option A study first rather than credit every small gap as qualified integration.

## Option B — lower top and longer fore/aft

If seat height, rider knee shape or cell orientation makes Option A poor, rotate the same bodies as **X43.2 / Y126.4 / Z8.55 mm**. One cartridge is five positions in X × two in Y × seven layers in Z, again 70 cells. Use provisional pitches 50 / 132 / 10 mm. Arrange two cartridges fore/aft at 250 mm pitch and five tiers at 70 mm pitch.

```text
one cartridge = 243.20 × 258.40 × 68.55 mm
all cells     = 493.20 × 258.40 × 348.55 mm
outer study   = 540.00 × 310.00 × 410.00 mm = 68.634 L
outer−cells   = 46.80 × 51.60 × 61.45 mm
```

All 700 cells remain present. This lowers pack top by 160 mm relative to Option A but adds 120 mm fore/aft. It may free upper volume for charge/LV equipment and a lower/narrower saddle, while consuming more front-wheel room. The lower electrical/cooling reservations are tighter, and spreading groups across five tiers affects service, support and joining. No CG advantage is earned until actual support/electronics masses are included.

For a first trial, put the outer pack at **X570–1110, Y±155, Z150–560 mm** and investigate **1,500 mm wheelbase**. At1,450 mm this reservation intrudes into the simple full-bump front-wheel envelope. Do not hide that intrusion with a shell. It could be shortened/repositioned only by a new cell/hardware arrangement and renewed checks.

## Compact wheelbase check

Retain the current motor-axis/pivot proposal initially: motor nearX440/Z340 and pivotX490/Z490 mm. Their exact supplier geometry, shock and frame interfaces still need all-part review. Option A begins atX580, so it does not require moving the pack toward the pivot to earn its shorter length.

For the current proposed front suspension approximation, the full axial compression is 125 mm at 25° from vertical:

```text
front axle at full bump:
X = wheelbase −125sin25° = wheelbase −52.827 mm
Z = 299.9 +125cos25° = 413.188 mm

conservative tire-cylinder rearmost X:
wheelbase −52.827 −299.9 = wheelbase −352.727 mm
```

| Wheelbase | Full-bump tire rearmost X | X gap to Option A pack end1000 | X gap to Option B pack end1110 |
|---|---:|---:|---:|
|1,420 mm|1,067.27 mm|67.27 mm|−42.73 mm|
|1,450 mm|1,097.27 mm|97.27 mm|−12.73 mm|
|1,480 mm|1,127.27 mm|127.27 mm|17.27 mm|
|1,500 mm|1,147.27 mm|147.27 mm|37.27 mm|

These are **conservative X-separation checks for the simple nominal-radius full-bump cylinder only**, not complete wheel clearance. They omit steering lock, brake/caliper/hose, fender, actual tire deformation/growth, yoke/fork offsets, tolerances, droop, compliance and any radiator/duct. Option A gives useful room at 1,420–1,450 mm before those checks; Option B points toward the upper end of the requested 1,420–1,500 range. A 37 mm scalar gap is not a universally approved dynamic clearance.

There is therefore no cell-volume reason to retain 1,640 mm wheelbase at this stage. There may still be chassis/rider/steering reasons to choose a particular geometry, but they should be demonstrated instead of inherited from the long box.

## Real hardware reservations that must now be modeled

| Function | Concrete layout investigation | Closure evidence |
|---|---|---|
|Cell broad-face restraint|Seven-layer stacks need defined pressure faces, controlled load application, growth accommodation and electrical isolation; identify per-stack or shared restraints|Supplier compression/growth data, tolerance stack, tested restraint and fatigue/relaxation behavior|
|Tabs/interconnects|Put true tab envelopes into the rotated geometry; investigate terminal-facing service channels and insulated series bridges with no uncontrolled crossing|Current cell drawing, joining/insulation process, electrical/mechanical/thermal validation and assembly access|
|Cooling|Investigate broad-face/interleaved plates or edge-cooling arrangement; show actual plate/manifold volumes and thermal paths|Measured cell heat/DCIR, cooling-contact characterization, gradients, flow/pressure and leak tests|
|HV equipment|Reserve dedicated fuse/contactors/precharge/current sensor/service-disconnect and protected cable exit bay, potentially outside the cell cavity inside the defined whole-pack system|Selected component dimensions, protection coordination, touch/isolation/service design|
|BMS/sense harness|Show accessible monitored connections, sensing boards and strain-protected routing; do not count open gaps as harness space without bends and fixing points|Exact channel architecture, harness/netlist and fault-detection evidence|
|Enclosure/lid/mounts|Design replaceable cover and sealed joints; include loads, bottom impact protection and tool paths; preserve frame-supported pack removal|Structural/retention and environment tests; approved joint/fluid/service processes|
|Fault venting|Reserve controlled outlets and path away from rider/charge access; avoid routing gases through ordinary cooling air or sealed electronics bay|Pack safety analysis and representative tests; no containment claim from geometry alone|
|Assembly|Demonstrate cartridge insertion, cell joining, inspection and closing order; distinguish workshop pack replacement from internal pack repair|Controlled build traveler, qualified fixtures/processes, inspection and repair policy|

The current catalog dimensions do not establish which rotated orientation is permitted mechanically or best for cooling/venting. The cell supplier must confirm orientation limits and thermal/mechanical conditions. No proposed cartridge is a purchasable validated module.

## Mass reconciliation — compact shape helps, but does not finish the target

For comparison only, assume a closed 3 mm aluminum shell at 2,700 kg/m³. This is not a released material/thickness or proof of structural adequacy:

| Outer study | Closed-shell mass | Mass remaining for every other noncell pack function at 85% cell fraction |
|---|---:|---:|
|Previous690 ×220 ×550 mm|10.426 kg|1.593 kg|
|Tight comparator400 ×310 ×550 mm|8.21 kg|3.81 kg|
|Recommended420 ×330 ×570 mm|9.04 kg|2.98 kg|
|Lower Option B540 ×310 ×410 mm|8.24 kg|3.78 kg|

The target complete pack at 85% fraction remains 80.129 kg including 68.11 kg cells. Option A improves footprint while leaving only about 2.98 kg for all cooling, interconnects, electronics, protection, restraints, seals and mounts under that optimistic target. That is **not a credible completed mass allocation**. Investigate the real enclosure/support architecture and complete BOM; accept no automatic 85% integration credit. Larger hardware reservations may add outer bay volume and case mass. Any mass concession belongs to an explicit owner decision.

## Decision and next CAD acceptance

Proceed with **Option A at 1,480 mm wheelbase**, keeping all 700 cells visible/selectable and their true rotated dimensions. Save the rework as a separate artifact preserving the original long-box study and its audit history. Draw the frame around actual pack/drive interfaces, not a long empty decorative enclosure. Move the charger/inverter, which were positioned for the longer model, into an integrated serviceable upper/front arrangement only after their real connector/coolant envelopes and rider reach are shown.

The proposed frame centerlines at Y±195 mm with 16 mm outer tube radius leave about **14 mm nominal side clearance** to the ±165 mm pack boundary. This is not a mounting design or an automatically acceptable clearance: include frame/pack tolerances, insertion path, movement and vibration isolation, if used. Actual brackets and fasteners consume space and mass. The new head/fork geometry must preserve intended rake/trail with actual yoke offsets, tire radius and loaded suspension, not only visually follow the render.

Deliver longitudinal, transverse and plan sections with cell and hardware colors; kinematic steering/suspension sweeps; interference reports including frame/motor/pivot/shock; cell-to-case and cell-pair spacing; actual assembly/removal paths; rider posture/knee envelope; and a reconciled pack mass estimate. Review Option B if Option A fails human fit or hardware routing. Keep selected exterior character, but revise the mechanical internals openly rather than wrapping unresolved geometry in an attractive body.

This rework supplies a compact mathematical arrangement and a specific next engineering layout. It preserves cell count and energy. It does not assert that 700 cells alone constitute a finished battery or that a newly shorter motorcycle is ready to build.

