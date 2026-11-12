# Hardware installation — actual BMS and protection integration

October 25, 2026. Development work for the compact coaxial-drive candidate. This document distinguishes actual supplier solids, published dimensions and proposed cabinet/service geometry. It does not release electrical pinouts, fuse ratings or a complete harness. It supplements rather than silently overwrites the earlier pack-layout options.

## Actual Orion BMS2 geometry

The manufacturer archive already downloaded into the project contains three enclosure models. The inspection script selects **108 cell Final Assembly.STEP**, extracts it without scaling and checks the actual solid assembly. Source: [Orion BMS2 product/download page](https://www.orionbms.com/products/orion-bms-standard/), [official 108-cell outline](https://www.orionbms.com/downloads/drawings/orionbms2_mechanical_108.pdf).

Run [inspect-bms-and-protection.py](tools/inspect-bms-and-protection.py) with the bundled FreeCAD Python. Results are saved in [bms-installation-audit.json](bms-installation-audit.json), and the placed supplier solid in [Orion-BMS2-108-installed-proposal.step](models/Orion-BMS2-108-installed-proposal.step). A later `--vehicle` audit is optional and slow; proxy checks are not presented as a complete vehicle clearance test.

| Property | Inspection result |
|---|---|
| Source SHA-256 | `bf4c1566499cbfe724786638e5bec52e4fa819e01c55babd0937bf53eb6fac65` |
| Actual source assembly | 67 solids; valid imported shape |
| Raw source bounding box | X−120.665…121.475779; Y−50.764200…21.838920; Z±85.296628 mm |
| Raw bounding dimensions | 242.140779 × 72.603120 × 170.593256 mm |
| Flat orientation | Rotate +90° about source X; no scaling |
| Flat installed dimensions | **242.140779 longitudinal × 170.593256 transverse × 72.603120 high mm** |
| Imported solid volume | 478,593.386 mm³; **not a material mass** |

The originally suggested underseat search window X200…450, Y±85, Z695…760 is **too small**: actual model width exceeds it by 0.593 mm and height by 7.603 mm, before mounts or harness. Do not substitute the drawing's enclosure-height dimension for the whole STEP assembly envelope.

### Proposed position and sampled clearances

The first placed test used X205…447.140779, Y±85.296628, Z700…772.603120 mm. Actual BMS solids against simplified keepouts gave:

| Keepout | Shortest solid gap | Finding |
|---|---:|---|
| Rear tire, nominal cylindrical proxy | 127.036 mm | No proxy interference |
| Rear tire, 130 mm vertical bump cylindrical proxy | **17.728 mm** | No overlap, but below the current proposed 20 mm layout criterion |
| Nominal right-side shock, 90 mm OD cylinder proxy | 27.017 mm | No nominal proxy interference; reservoir/adjusters/mounts absent |

These are shortest distances, not merely vertical differences between bounding boxes. A vertical separation estimate overstated the bump margin. A practical next position is **Z705 minimum**, keeping X205 and Y centered; its top is Z777.603. This raises the BMS toward the seat, so **seat pan, compression of padding, subframe tubes, bracket fasteners, connector mates and harness must be checked before accepting it**. The script supports `--x` and `--z` to reproduce these proposed changes. The JSON records whichever position was actually run, including its limitations.

The tire proxies are filled cylinders, not the full swept production tire/guard/suspension. The shock proxy covers only the proposed nominal body segment. Neither check closes rear droop/bump through a full swingarm arc, tire growth, actual shock adjustments, service access or structural attachment. Root vehicle CAD integration must check the actual supplier BMS with those surrounding solids.

### Mounting and thermal boundary

Use the actual model/outline mounting features and the intended heatsink arrangement. Add a removable carrier, controlled fasteners, environmental cover and loom strain relief as separate modeled parts. A hidden flat plate through the heatsink is not acceptable. The wiring manual identifies isolation/wiring rules and heat-dissipation requirements; protect the unit from spray and from pack fault exhaust. Connector withdrawal and access to the ground lug/status indication need service space.

A **108-channel BMS is not automatically sufficient just because there are 100 series groups**. Orion notes that disconnects/high-resistance links and cell-tap bank rules can require unused positions and a larger unit. Freeze the series/disconnect map first, run the supplier wiring generator/review, then confirm the exact BMS size. No customer harness is released from the imported STEP. [Orion BMS2 wiring manual](https://www.orionbms.com/manuals/pdf/orionbms2_wiring_manual.pdf)

## GX14 contactors — actual source dimensions, CAD retrieval status

The manufacturer GX14 drawing was obtained from its distributor mirror after the manufacturer server blocked a direct download. Local source: [manufacturer datasheet via TTI](sources/GX14-manufacturer-datasheet-TTI-mirror.pdf), with [rendered dimension page](sources/GX14-dimension-page.png). Original reference: [Sensata GX14 sheet](https://www.sensata.com/sites/default/files/a/sensata-gigavac-gx14-series-open-contactors-datasheet.pdf).

The drawing gives **114.8 mm overall terminal-to-terminal length, 59.8 mm overall width, 57.3 mm overall height**, power-stud centers 84.6 mm apart, 55.9 mm principal body width, M10×1.5 power connections and 5.3 mm mounting holes on the illustrated 44.5 mm pattern. The mounting-hole orientation must be taken from the actual drawing, not inferred from these scalar dimensions. Published typical mass is 0.5 kg per contactor. These facts support an outline/installation study, not a released detailed solid.

Manufacturer-hosted content on [Sensata's TraceParts catalog](https://www.traceparts.com/en/product/sensata-technologies-gx14?CatalogPath=SENSATA_2027184975%3ASENSATA_2027184975.100.030&Product=90-16062025-063827) and [DigiKey GX14 model listing](https://www.digikey.com/en/models/17867467) identifies a **GX14.stp** model. **It was not retrieved in this work.** Access/download mechanisms did not yield a direct usable supplier STEP. Do not label a reconstructed cylinder/outline as that supplier model or calculate material mass from it.

For a 12 V development LV system, **GX14BAB** is a specific study ordering combination from the manufacturer suffix table: 12 V coil, 38 cm flying leads, normally-open auxiliary contact. It is a candidate only. Confirm intended feedback diagnostics, coil driver transients, supply margin and bidirectional interruption duty before procurement. Four such family-reference units would nominally be 2 kg before busbars, supports, covers and wiring. An integrated routing module could change the count.

Critically, the GX14 manufacturer describes preferred breaking current direction and asks for confirmation of reverse interruption suitability. Drive/regen and DC charging are bidirectional at the pack. That must be reviewed against the actual switching fault cases; the continuous ampere rating alone cannot close it. Do not apply an extra generic suppression diode without checking the manufacturer's coil-suppression instructions, because it can delay opening. Terminal torque in the supplier sheet is not automatically the torque for every added lug/busbar stack or mounting joint.

## Proposed protected HV cabinet

The coaxial layout under investigation moves the motor/pivot to approximately X540/Z470 and the pack to **X670…1090, Y±165, Z150…720 mm**. Keep this as a named new candidate, not an unrecorded change to the older X580 pack option.

Investigate a separate, covered HV service cabinet **X520…670, Y±150, Z600…740 mm**, with its rear/side service access designed around actual frame and body. This is a **150×300×140 mm search region**, not a selected enclosure or proof the contents fit. The region sits above the nominal motor body and behind the pack, but actual motor fittings, frame tubes, seat supports, cooling hoses and cable bends still need direct checks. Its material, mounts, seals and mass must be added once to the pack-versus-vehicle mass tree.

A dimension-based main-contactor pair can be studied with the long axes transverse:

| Item | Proposed minimum corner X/Y/Z | Body/outline X/Y/Z | Scope |
|---|---|---|---|
| Main positive contactor | 528 / −57.4 / 615 | 59.8 / 114.8 / 57.3 | GX14 drawing outline only; not downloaded STEP |
| Main negative contactor | 598 / −57.4 / 615 | Same | Distinct return isolation path |
| Main fuse branch search region | X540…650 / Y80…135 / Z610…680 | Unselected actual fuse/holder | Do not install a 125 A example in place of a main fuse |
| Precharge/discharge branch | Remaining rear/side region after actual parts are selected | Unselected | Pulse resistor, switching, protection and measurement space required |
| Measurement/isolated control boundary | Separate shielded wall/side region | Unselected | Actual current/isolation sensors and connector access required |

The pair's bare outline ends at Z672.3, leaving room within the search region to investigate lugs, insulation/terminal covers and tool access. Its fore/aft body gap is only 10.2 mm; **no qualified dielectric/thermal clearance is implied**. Cable lug stacks and leads can overrun the bare outline. Do not pack the cabinet by bounding boxes alone.

DC inlet isolation and positively interlocked AC/DC routing remain separate functions. Putting a main pair in this cabinet does not also place the charge pair, fuse branches, manual disconnect and every sensor. A second inlet/routing enclosure or an integrated supplier routing product must be modeled and counted explicitly. Do not duplicate main and charge hardware accidentally across pack and vehicle assemblies.

### Power and control boundary

Proposed power order: cell string → coordinated pack fuse and defined manual isolation → main positive/negative switching → vehicle HV bus. Controlled precharge charges the connected bus capacitance before normal main closure. Independent charge-inlet switches isolate the inlet; the native shared AC/DC pins route only to the appropriate OBC input or DC branch. Pack current, bus voltage and inlet current/voltage must remain observable in all relevant states.

The cabinet needs a removable touch-protected cover, interlock, strain-relieved cables, bonded case as required, guarded live studs, segregated LV connections, labeling and a verified service-discharge/voltage-measurement route. HV creepage/clearance, insulation systems and openings are to be calculated from the actual voltage/transient/material/environment requirements. No generic 10 mm gap is released as a standard. Coil control and fault-permission ownership follow the [electrical architecture](../documentation/systems/electrical-energy.md), with no independent controllers fighting over a coil.

## Fuse, connectors and EVCC evidence

**Fuse:** the primary [Littelfuse 30EV datasheet](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-30ev?assetguid=e7778bbf-1084-4761-b2cd-788d317ad864) gives a real 500 V family spanning 150–300 A, with 93 mm overall outline, 30 mm diameter body, 52 mm body length and 75 mm mounting-center reference; M6/M8 versions differ. The 300 A item is a geometric/current-range comparison, **not a selected main-fuse rating**. Voltage/transients, actual available fault current, minimum breaking current, temperature, conductor withstand and time-current/I²t coordination must select the part. The smaller 25EV1K 70–125 A examples and obsolete old EV1K drawings cannot silently supply a traction fuse for the 70 kW/250 V study. No supplier fuse STEP was retrieved; outline modeling must carry that status.

**Connectors:** TE's [2141227-1 HVP800 page](https://www.te.com/en/product-2141227-1.html) exposes an official STEP download and controlled drawing, but the download server denied this request. A complete mated pair and cable tooling remain unselected. Current metadata on this mixed power/interlock product page is not sufficient to infer power-terminal current capability. Use the full drawing/application specification and thermal derating. The CM200 requires its specified supplier connector/cable system; an arbitrary TE header does not replace the inverter's Rosenberger connection interface. No real connector solid is claimed installed from this search.

**EVCC:** ADVANTICS' [manufacturer documentation](https://documentation.advantics.fr/adm-cs-evcc/index.html) establishes an actual NACS-capable controller. Its public legacy description supplies approximately 114.3×116.8 mm plan dimensions but not a complete installation envelope here. **No complete STEP or height was obtained**, so a plausible third dimension is not invented. Place it only after its exact current hardware drawing, mates, mount and service access are available; its LV/PLC/CAN harness needs segregation from noisy motor-phase routing. EVCC communication does not provide the inlet power-routing cabinet or Tesla authorization.

## What is ready to integrate now

The **actual Orion108 supplier STEP**, its tested orientation and bounds, and its parameterized installed STEP are ready for insertion into the working FreeCAD assembly. The JSON exposes the initial placement failure rather than hiding it. Cabinet and contactor proposals are dimension-based development work pending true supplier solids and surrounding-geometry checks. The major remaining electrical installation parts are still unselected or incomplete: exact BMS channel/disconnect topology, all mated harnesses, HV fuse/coordination, precharge/discharge, LV converter/battery/distribution, EVCC full body, inlet/routing, contactor duty approval and thermal plumbing.

Continue by importing the actual BMS into the root assembly, correcting its interference/margin with real seat/subframe parts, selecting current contactor/fuse/connector CAD without inventing models, and converting the cabinet search into fully located parts with guard, fastener, tool and cable clearance. No physical electrical test or energized pack qualification was completed here.
