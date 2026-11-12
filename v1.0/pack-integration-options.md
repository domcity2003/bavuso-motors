# Compact pack integration — rotated 700-cell development

October 25, 2026. Prepared by Codex. **Lead layout is a concrete packaging proposal, not an approved pack construction design.** This study corrects the long battery region that drove the preceding CAD toward a 1,640 mm wheelbase. The working vehicle target returns to a proposed **1,480 mm wheelbase**, within the current 1,450–1,500 mm compact investigation. Wheelbase and packaging do not themselves prove stability, comfort or the owner's range/mass goals.

## Lead topology and coordinates

Keep **100s7p / 700 SA504 cells / 26.299 kWh typical nominal**. Rotate each cell so its long dimension runs across the bike, with thickness along the bike and width vertically. Use the published dimensional upper bounds at 30% SOC as the geometric starting point: **8.55 X × 126.4 Y × 43.2 Z mm**. Thickness growth over SOC/life and joining details remain unqualified. [SA504 supplier catalog, drawing AMP-TDS-SA504-R1, PDF page 52](https://amprius.com/documents/Amprius_Product_Catalog.pdf)

Define ten identical proposed **10s7p cartridges**. Each cartridge has seven parallel cells along X, two series positions along Y and five series rows along Z. Put five cartridges along X and two cartridge tiers along Z. This preserves the cell and series-group count exactly:

```text
10 cartridges × (2 Y series positions × 5 Z series rows) × 7 parallel cells
= 10 × 10 × 7 = 700 cells = 100s7p
```

Study pitches: parallel cells **10 mm X**, adjacent cartridges **75 mm X**, the two Y positions **144 mm Y**, series rows **50 mm Z**, cartridge tiers **260 mm Z**. These pitches allocate space for development; they are not qualified thermal/insulation/compression dimensions.

Coordinates use X forward, Y left, Z up and the rear tire contact origin, all in millimeters:

| Item | Proposed definition |
|---|---|
| Outer pack study box | X580…1000, Y−165…165, Z150…720 |
| Outer dimensions | **420 X × 330 Y × 570 Z mm**, 79.002 L |
| Cell minimum corner | X595, Y−135.2, Z165 |
| Cartridge X index | c=0…4; origin shift 75c |
| Cartridge tier | t=0…1; origin shift 260t vertically |
| Parallel cell index | p=0…6; origin shift 10p along X |
| Series Y index | s=0…1; origin shift 144s along Y |
| Series Z row | r=0…4; origin shift 50r vertically |
| Individual cell minimum corner | **(595+75c+10p, −135.2+144s, 165+260t+50r)** |
| Complete cell-body bounds | X595…963.55, Y−135.2…135.2, Z165…668.2 |
| Cell-body bounding dimensions | **368.55 X × 270.4 Y × 503.2 Z mm** |

The coordinate formula gives 5×2×7×2×5=700 distinct cells. A cartridge is indexed by (c,t); its ten series groups by (s,r). Seven cells sharing one (c,t,s,r) form the proposed parallel group. The released electrical mapping must specify group numbering, polarity, tab orientation and joins; the coordinate formula does not connect conductors. Old unrotated placement exports remain historical until the model and placement register are regenerated with this exact configuration.

```mermaid
flowchart LR
  B[Lower tier: five 10s7p cartridges] --> U[Upper tier: five 10s7p cartridges]
  U --> S[100 series groups total / 7 cells parallel per group]
  S --> P[Custom pack protection / measurement / service boundary]
```

The diagram counts groups, not a wiring sequence or a series-jumper route. A mechanically convenient series order must still satisfy clearances, service boundaries, assembly and measurement requirements.

## Where the space actually goes

Assuming a simple uniform 3 mm shell only for this dimensional audit, its inner faces are X583…997, Y±162 and Z153…717. Actual fasteners, lid seams and mounting bosses will change that interior.

| Nominal free region | Arithmetic clearance | Interpretation |
|---|---:|---|
| Rear cell end to inner wall | 12 mm | Shared joining/support/service space; not a released tab gap |
| Front cell end to inner wall | 33.45 mm | Possible manifold/interconnect/end-restraint development region |
| Outer Y cell ends to inner side walls | 26.8 mm each | Potential tab/insulation/cooling distribution; supplier drawing must establish tab direction |
| Bottom cell body to inner floor | 12 mm | Insulation, support and impact/thermal separation compete for it |
| Top cell body to inner lid | 48.8 mm | Potential low-profile harness/monitoring/vent region; not proof large contactors fit |
| Within each seven-cell parallel stack, X | 1.45 mm between catalog-maximum bodies | Compression, thermal and electrical layers must share it; life swelling not yet covered |
| Between cartridge bodies, X | 6.45 mm | Mechanical boundaries and interconnects compete for this gap |
| Center corridor between Y positions | 17.6 mm | Possible joining/sensing corridor; not automatically a coolant manifold plus HV busway |
| Between series rows, Z | 6.8 mm | Edge separation/interconnect/support space; unqualified |
| Between cartridge tiers, Z | 16.8 mm | Possible tier support/manifold route; must retain compression and service access |

**Each free region may only be spent once.** A 17.6 mm center corridor cannot simultaneously be credited at full width to a busbar, coolant tube, insulation wall and tool access. The next CAD revision needs separate solid bodies for each function, including tolerances and removal motion. Empty bounding-box clearance is not an installed design.

No supplier-approved SA504 face pressure, swelling allowance, tab bend or joining specification has been obtained. The 1.45 mm stack space is therefore a hypothesis, not a validated pouch integration method. Cell-facing surfaces should remain correctly supported without treating pouch cells as chassis members. Do not scale another cell model's clamping pressure to SA504.

## Comparison with the earlier geometry

The prior 690×220×550 mm pack region is replaced by a region **270 mm shorter, 110 mm wider and 20 mm taller**. The width is deliberate: distribute battery volume across the lower body rather than forcing a long narrow box between the steering head and motor. The 330 mm outer width must be reconciled with pegs, boot/knee access, cornering, frame members and the baseline exterior; it is not an approved rider-contact width.

This recovers longitudinal room for a 1,480 mm wheelbase investigation. It does not prove the fork at combined steer/bump, radiator/fan, wheel/tire, motor/pivot support or shock arrangement clear. The latest mechanical study proposes a pivot near X540/Z470 and a direct-mounted right-side shock behind the pack, upper eye approximately (400,150,679.392) and lower eye (300,150,399.733) at nominal position. Its 90 mm diameter study reservation lies approximately X255…445, so it avoids the earlier upper-rear pack conflict without requiring a pack notch. That reservation is not an actual selected shock body or proof of mount strength, full adjustment access or hose/reservoir clearance.

The pivot axis at X540 is only 40 mm behind the pack face X580; actual pivot bosses, frame attachments, cartridge removal and brackets must be modeled. The motor's nominal 104 mm body radius at X440 reaches X544, leaving 36 mm before the pack face, before real protrusions, brackets and service requirements. Preserve all 700 cells while resolving the complete supplier geometry and motion. Cell bodies stop at Z668.2; any subsequent case relief would consume functional monitoring/vent/lid space even where it misses cells. Do not trim the case silently to clear another part.

## Mass remains a hard integration problem

Using uniform 3 mm walls and assumed aluminum density 2,700 kg/m³:

```text
Outer volume = 420×330×570 mm³ = 79.002 L
Inner volume = 414×324×564 mm³ = 75.652704 L
Metal volume = 3.349296 L
Closed-shell mass = 9.043099 kg
```

The old shell calculation was 10.425931 kg, so this geometric change reduces the simple shell result by **1.382832 kg**. Neither shell is a validated structure or material/process selection. Lids, joints, mounts, seals and actual protection will alter the result.

At 68.11 kg typical cells and an 80.129 kg pack target, this shell leaves **2.976313 kg** for all remaining pack functions. That still does not constitute a credible completed 85%-cell-fraction pack. Under the less aggressive 80% cell fraction the noncell budget is 17.0275 kg; after the same shell, **7.984401 kg** remains. This is a more useful comparison, but it too requires a complete measured or analyzed leaf BOM.

For perspective, 700 full cell-face areas at 126.4×43.2 mm total about **3.822336 m²**. One 0.3 mm aluminum spreader per cell would calculate to **3.096092 kg**; at 0.5 mm, **5.160154 kg**, before coolant channels, headers, insulation or restraints. This is a material-area sensitivity, not a selected cooling architecture or a claim every cell needs that exact plate. It demonstrates why face cooling and pack mass cannot be resolved with a zero-mass cold-plate label.

Investigate shared cooled compression surfaces, cell grouping and a thinner optimized enclosure only with thermal/structural evidence. Do not count deletion of support, insulation or protection as an efficiency improvement. The under-400 lb goal remains unclosed; neither the compact pack shape nor the old 399 lb scenario closes it.

## Named hardware zones and explicit fit blockers

These are functional regions to develop around the compact pack. **They are not claims that all hardware fits.** Supplier bodies, connectors, bends, fasteners, shielding and service sweeps must be included before fixing coordinates.

| Zone | Intended contents | Concrete constraint and next work |
|---|---|---|
| PK-CELL | 700 cells and ten cartridge restraints | Use the exact formula and cell bounds above; add support, compression, growth and joint geometry |
| PK-MID | Center Y joining/sensing corridor | 17.6 mm body gap; draw polarity/jumpers and sensing first, then determine whether coolant can coexist without electrical exposure |
| PK-END | Pack front/rear end clearances | Only 12/33.45 mm to the ideal inner walls; show end restraints, insulation and manifolds rather than assuming contactors live here |
| PK-TOP | Low-profile pack-internal monitoring/vent/harness region | 48.8 mm above cell bodies before lid details; frame/seat/vent interfaces compete with it. BMS and temperature expansion still need real drawings |
| HV-SERVICE | Main contactors, fuse, manual disconnect, current/isolation measurement and bus distribution | No qualified complete location exists. Compare a dedicated protected front/end pod with pack-internal distributed functions; include its case, seals and mass exactly once |
| FRONT-DRIVE-ELECTRONICS | Candidate inverter and actual connector/cooling installation | Front-of-pack region is an investigation space; import the actual CM200 STEP and audit against full fork/tire/radiator sweeps |
| OBC | BROGEN candidate AC charger installation | Body is 373×224×76.5 mm before connections. Its real installation has not been fitted; do not place an invisible OBC inside cells or under the case |
| LV-CONTROL | LV battery/converter, VCU, fused distribution, display gateway | Keep away from pack vent exhaust and fault gases; establish boot/critical-load/standby requirements and actual bodies |
| CHARGE-INLET | Native NACS inlet, lock, temperature sensing, AC/DC routing | Cable reach, parked stability, drainage, routing isolation and safe release determine placement; port is not selected yet |
| COOL-BAT / COOL-DRIVE | Separate controlled temperature domains and all external equipment | Draw real cold plates/manifolds, pumps, fan/radiator bodies, hoses, bleed/fill, clearance and airflow; hot stationary charge remains unresolved |

One particularly important incompatibility: merely naming a front electronics cowl does not fit the **330×188×97 mm CM200** and **373×224×76.5 mm OBC** together. If both stand vertically with their thin dimensions fore/aft, their body-only X stack is 173.5 mm before spacing; placing them side by side needs at least 412 mm Y width before spacing; stacking vertically needs at least 703 mm Z height. Different orientations or separate zones can be studied, but the actual supplier solids and the front wheel/fork sweep must establish the answer. Do not reserve one small space for both and report it closed.

NX W90 remains a meaningful alternate inverter body/mass study, not a selected substitution. It could ease packaging, but requires current drawings, software/current/thermal matching and separate configuration control. Native charging still needs qualified inlet/routing and Tesla authorization. No hidden mass credit is earned by an attractive cowl.

## Alternative shapes and disposition

| Option | Countable cell allocation | Disposition |
|---|---|---|
| Lead rotated ten-cartridge layout | Five cartridges along X, two tiers Z; 700 cells; 420×330×570 mm outer study | First layout to integrate into compact vehicle, with tight pivot/motor interfaces and unresolved hardware zones |
| Short/tall grouping | Five X group bays × two Y positions × ten Z rows =100 groups | Similar compact length, different cartridge/support choices; useful comparison if shock relief or service removal improves |
| Lower staggered layout | Seven X bays × two Y positions × seven Z rows =98 groups, plus two additional groups | Can reduce overall cell height, increases length and creates nonrectangular module/support/jumper details; cannot omit the last fourteen cells |
| Balanced staggered layout | Six X bays × two Y positions × eight Z rows =96 groups, plus four groups | Further length/height trade; 100s7p retained only with all four extra groups and explicit custom packaging |
| Old narrow layout | Unrotated 700 bodies in long narrow region | Retain as historical comparison; do not extend wheelbase solely to avoid improving cell arrangement |

No shape wins from bounding volume alone. The best candidate is the one that closes cell support/heat/joining, real hardware installation, rider fit, structure, service, complete mass and dynamic clearances together.

## Concrete next closure work

1. Regenerate the exact rotated 700-cell assembly and export its group/cartridge mapping. Add independent all-body containment, intercell/intercartridge separation and every new internal-part interference check.
2. Draw one complete 10s7p cartridge using supplier-compatible tabs, insulation, restraint/compression and cooling. Resolve its electrical/group numbering and physical joining before duplicating it ten times. Catalog cell-body fit alone is insufficient.
3. Place actual drive/OBC bodies plus cable/coolant interfaces; select and model the HV service pod, BMS, LV equipment, inlet/routing and thermal equipment. Produce a clear unmatched-space list for anything not yet fitted.
4. Reconcile the behind-pack side-shock arrangement, pack removal path, underbody protection, frame attachments and full steering/suspension sweeps at the proposed compact wheelbase. Build the restraint/frame load paths around cells, not through pouch strength.
5. Replace pack and hardware allocations with a reconciled leaf BOM and geometry/material mass where defensible; identify every unknown. Update range and mass calculations for this actual configuration only after the physical system is represented.

The full cell qualification, electrical protection, software, structural/thermal evidence and physical vehicle tests in the [electrical definition](electrical-design.md) and broader engineering package remain necessary. This study provides a substantially more compact countable layout and precise integration tasks; it does not claim a completed vehicle.
