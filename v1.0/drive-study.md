# Bavuso V1.0 adventure: drive study (motor + reduction)

Prepared November 5, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
Tools: `tools/drive-study.py` (performance), `tools/build-adventure.py` with `BAVUSO_DRIVE=ipm` (packaging).
Data: `drive-study.json`, build logs `cad/adventure-ipm-fast-*.log` and `cad/adventure-ipm-full-{75,90}.log`.

## The plain answer

**Use a high-speed radial IPM motor (about 150–180 Nm, 15–16k rpm, 130 kW) with a 2-stage reduction of about 7.5:1 (gear stage, then belt), on an ordinary 400 A inverter.** It is the only option that reaches **both** targets (0–60 in 2.7–3.0 s and 147 mph) without a huge inverter. It was also already the cheapest drive in the cost optimiser (about $1.5k vs $3.6k per bike at 10k/yr).

**Put the motor body above and slightly ahead of the swingarm pivot (75° from horizontal).** The gearbox output and belt pulley stay on the pivot axis. That keeps the belt length constant and leaves the rear suspension work unchanged (anti-squat stays at 124%). This position also lowers the battery: the cell centroid drops 15 mm and the pack top stays where it was.

**Update, Nov 5: the packaging is resolved, and the IPM layout is now the main model.** All 51 of 51 checks pass, with no interferences (`geometry-adventure-audit.json`). To get there:

- **The motor is shorter, 129 mm instead of 175,** so it ends 12 mm inside the right swingarm arm's sweep.
- **The HV cabinet moved below the pivot,** into the space the EMRAX used to fill.
- **The pack-to-motor gap is now measured properly.** The battery shaping now samples along the gear case's straight edges; before, it checked only the corner points. The gap is 21.0 mm against 20 required.

The EMRAX layout is kept as `cad/Bavuso-V1.0-adventure-emrax228.FCStd`.

## Why the current motor fails

The CAD today carries the **EMRAX 228 MV**. It needs **about 630 V** to make its peak power, but this pack is 99s: 416 V full and about 360 V under load at half charge. At 360 V:

- full torque runs out at about 3,100 rpm;
- no-load speed is only about 5,600 rpm, short of its 6,500 rpm rating;
- on the current 3.1:1 belt that means **5.0 s 0–60 and about 114 mph**;
- gearing it tall enough for 145 mph (1.7:1) gives a 9.7 s 0–60.

*This corrects `mass-rollup.md`, which assumed the motor reaches 6,500 rpm and so showed 150 mph.*

**The deeper reason:** axial-flux motors like the EMRAX have surface magnets and very low inductance. They can barely field-weaken, which means they cannot trade voltage for speed. On a 360–416 V pack the only way to get both launch torque and top speed is the low-voltage winding with a very large current, 650–880 A. A radial IPM keeps constant power from its corner speed up to its top speed, so it needs about 400 A.

## The options compared

All runs use the CAD roll-up (275.1 kg bike + 85 kg rider), a 130 kW pack/inverter limit, 360 V, launch control at 1.0 g, CdA 0.40 at launch and 0.38 at top speed. The best ratio is the one with the quickest 0–60 that still reaches 145 mph.

| Drive | Best ratio | 0–60 | Top | Inverter peak | Motor + inverter | vs now |
|---|---|---|---|---|---|---|
| EMRAX 228 MV (in CAD now) | 1.7 (3.1 today) | 9.7 s (5.0 s today) | 145 (114 today) | 360 A | 20.0 kg | — |
| EMRAX 228 LV+43% | 3.2 | 4.9 s | 145 | 650 A | 22.5 kg | +2.5 kg |
| EMRAX 268 LV+100% | 1.75 | 4.0 s | 147 | 650 A | 30.9 kg | +10.9 kg |
| EMRAX 268 LV+43% | 2.2 | 3.2 s | 146 | **880 A** | 33.9 kg | +13.9 kg |
| **Radial IPM 180 Nm / 15k rpm, 2-stage** | **7.3** | **2.7 s** (grip-limited) | **147** | **400 A** | 27.5 kg | +7.5 kg |
| **Radial IPM 150 Nm / 16k rpm, 2-stage** | **7.8** | **3.0 s** | **147** | **400 A** | 27.5 kg | +7.5 kg |

### Scorecard

| | EMRAX 268 LV+43% | Radial IPM + 2-stage |
|---|---|---|
| 0–60 / top | 3.2 s / 146 mph, just makes it | 2.7–3.0 s / 147 mph |
| Mass | +13.9 kg | +7.5 kg |
| Inverter | 880 A at 400 V: a large, rare, heavy unit (est. 12 kg) | 400 A: the volume automotive class |
| Cost at 10k/yr (optimiser) | about $3.6k for the motor alone | about $1.5k motor + reduction |
| Supply | EMRAX is phasing out the current range for a next generation | Tier-1 e-drive suppliers build this class in volume; it needs a custom spec |
| Packaging | Coaxial on the pivot, but 268 mm diameter (40 mm larger) | Body off-axis; gearbox output on the pivot; arms and cabinet need rework (below) |
| Risk | Known part, but the drive is marginal and needs a high-current inverter | Custom part: needs a supplier and a validation programme |

**The 150 Nm / 16k rpm spec is the one to write to suppliers.** It meets 3.0 s exactly. The 180 Nm version is grip-limited at 2.7 s, so the extra torque buys little except margin for a heavier load.

## Packaging in the CAD

The motor was modelled as an envelope:

- a Ø220 × 175 mm body;
- a 2-stage gear case on the left (Ø150 output on the pivot, Ø190 at the motor);
- centres 135 mm apart.

Fast builds rotated it around the pivot (measured above ground):

| Motor position | Pack top | Cell centroid | Clearance | Cells |
|---|---|---|---|---|
| EMRAX baseline (coaxial) | 613.5 | 424.4 | 216 | 594 |
| −35° (low, forward) | 702 | 463.7 | **202.6**, motor is the lowest part | 594 |
| −15° | 726 | 483.1 | 216 | 594 |
| +10° (forward) | 710.5 | 485.8 | 216 | 594 |
| +45° | 702 | 432.4 | 216 | 594 |
| **+75°** | **613.5** | **409.0** | **216** | **594** |
| +90° (straight up) | 629 | 403.1 | 216 | 594 |

Ahead of the pivot, the motor takes the pack's best low space and pushes the cells up as much as 60 mm. Above the pivot, it frees the pack's lower-rear corner, so the cells sit lower than with the EMRAX.

### Full check suite

| Check | 90° | 75° | Fix |
|---|---|---|---|
| Central shock vs motor (15 mm needed) | **−2 mm, clash** | 25.3 mm ✓ | 75° clears it |
| Swingarm sweep vs motor (10 mm) | clash | clash | The motor body (Y −25…150) reaches the right arm (inner face at about Y 108). Give the motor a 150 mm active length, centred between the arms, and move the gear case outboard on the left. |
| HV cabinet vs motor (10 mm) | clash | clash | The cabinet (X 550–690, about 620–750 mm above ground) sits where the motor top now goes. Move it forward over the pack top. The 75° pack top is unchanged, so the space is there. |
| Pack vs motor (20 mm) | 19.6 mm | 9.5 mm | Step the pack's top-rear band back by about 10 mm (a few cells, or a chamfered corner). |
| All other checks | pass | pass (88 of 91) | |

**Result after the fixes (Nov 5):**

| Check | Gap | Required |
|---|---|---|
| Swingarm sweep vs motor | 12.0 mm | 10 |
| HV cabinet vs motor | 12.4 mm | 10 |
| Pack vs motor | 21.0 mm | 20 |
| Shock vs motor | 21.6 mm | 15 |
| Cabinet vs swingarm sweep (new check) | 13.0 mm | 10 |
| Cabinet vs side covers (new check) | 5.7 mm | 5 |
| Cabinet vs rear tyre at bump (new check) | 123 mm | 20 |
| Cabinet vs skid plate (new check) | 65 mm | 10 |

The pack keeps 594 cells. Its top stays at 613.5 mm, its cell centroid is 410.2 mm (−14 mm vs the EMRAX), and ground clearance is 216 mm. The trial runs are kept in `cad/ipm-trials/`.

**What the fixes cost:**

- **Motor length:** a 129 mm envelope is tight for 150 Nm at Ø220 mm. It needs an oil-cooled hairpin stator with short end turns, and suppliers must confirm it. The 180 Nm version is unlikely to fit, so 150 Nm is the spec.
- **The low cabinet:** it sits in the splash zone behind the belly pan, so it needs an IP67 seal and a drain. It is still 65 mm above the skid plate.

## What the switch changes elsewhere

- **Rear suspension:** no change, as long as the final belt pulley stays coaxial with the pivot. Anti-squat comes from the pivot height (390 mm) and the belt term R/ratio. Keep the final belt stage at about 3.1:1 and put about 2.4:1 in the gear stage, so the belt term stays near 100 mm.
- **Mass:** +7.8 kg, to 282.9 kg (624 lb) in the refreshed roll-up. Bike-only CoG height is 501 mm, rider-on 637 mm. The spring goes to 109 N/mm and anti-squat to 125%. The 265 kg target in `mass-rollup.md` then needs the charger and aluminium-frame levers plus about 8 kg more. Carbon bodywork would cover it.
- **Inverter:** the 400 A unit at about 6.5 kg stays as budgeted.
- **Cooling:** the gear stage adds an oil circuit. An oil-cooled IPM can share it with an oil-to-water exchanger.
- **Noise:** a 16k rpm gear mesh needs helical gears ground for low whine. That is normal for tier-1 e-drives.

## Supplier specification (draft)

| Item | Value |
|---|---|
| Motor | Radial IPM, oil-cooled |
| Peak torque | 150 Nm or more (180 Nm preferred) |
| Peak power | 130 kW at 360 V DC, held from about 8,300 rpm to 16,000 rpm |
| Continuous power | 85–90 kW |
| Maximum speed | 16,000 rpm |
| Envelope | Ø220 mm or less; 129 mm or less overall between end faces, excluding the gear case (set by the swingarm arms) |
| Mass | 14 kg or less (motor); 21 kg or less with the reduction |
| DC voltage | 300–420 V (99s, 416 V full) |
| Inverter | 400 A peak, SiC |
| Reduction | 2-stage, total 7.5–7.8:1: helical gear stage about 2.4:1 in a sealed case, then a belt stage about 3.1:1. Output coaxial with the swingarm pivot. |

Other leads, not modelled: the YASA P400 class (axial, about 370 Nm, 24 kg; quote-only, voltage rating unknown) and EMRAX's next-generation range (not yet published).

## Next steps

1. ~~Rebuild the IPM layout at 75° with all checks passing~~ (done Nov 5, 51/51).
2. ~~Make the IPM the main model and refresh the mass and rear-suspension figures~~ (done).
3. Detail the gear stage: centre distance 135 mm, about 2.4:1, a helical pair. Check that the gear and bearing sizes fit the 47 mm-wide case.
4. Send RFQs to tier-1 e-drive suppliers using the spec above.

Sources:
- [EMRAX 228 datasheet v1.7](https://emrax.com/wp-content/uploads/2025/03/EMRAX-228_datasheet_v1.7.pdf): Kv, Kt and peak currents per winding
- [EMRAX 268 datasheet v1.7 C](https://emrax.com/wp-content/uploads/2025/08/EMRAX-268_datasheet_v1.7_version_C.pdf)
- [EMRAX 228 product page](https://emrax.com/e-motors/emrax-228/)
- Optimiser drive costs: `powertrain-optimum.json`, `powertrain-cost-down.md`
- Inverter masses: Leadrive 400 V inverter (about 10 kg) and BorgWarner 650 A class (about 7 kg, 800 V), as gathered earlier in this study
