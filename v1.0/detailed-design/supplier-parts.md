# Bavuso V1.0: supplier parts (real bought-in parts vs the CAD)

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5).

Files: `detailed-design/supplier/parts-register.csv` (19 parts, with datasheet values, prices and URLs), `detailed-design/tools/supplier-compare.py` (reads `tools/build-adventure.py` as text, never edits it), and its outputs `detailed-design/supplier/compare-output.csv`, `compare-clearance-impact.csv` and `compare-summary.json`.

## The plain answer

**Most of the bought-in parts exist and are easy to buy. The real tyres are bigger than the CAD tyres, though, and that breaks three things in the layout.**

1. **Tyres (the big one).** The CAD draws "nominal" tyres. Metzeler's data book gives the real maximum size in service:
   - **Front 120/70 R19:** 663 mm across and 133 mm wide. The CAD has 650.6 and 120.
   - **Rear 170/60 R17:** 650 mm across and 190 mm wide. The CAD has a 160/60 at 623.8 and 160.
   - Even a real 160/60 is 638 × 178 mm, so changing tyre size does not fix this.
2. **The belt runs into the rear tyre.** The belt's inner face sits at Y −83 mm. In the CAD the tyre wall is at Y −80, a 3 mm gap. A real 170/60 reaches Y −95, so the belt **overlaps the tyre by 12 mm**. A real 160/60 overlaps by 6 mm. No check in the build script looks for this. **This is the one blocking problem.** Fixing it means moving the belt line and the left swingarm arm outboard about 22–25 mm (CR-3).
3. **About 21 mm of extra ride height fixes the rest.** Raise the whole bike 13.1 mm (`LIFT` 40 → 53.1) and put in the real tyre sizes. That keeps the swingarm, shock and rake exactly as they are. The fork gets 7.6 mm longer, and the clamp-to-tyre gap goes to about 28.8 mm (25 required). Four clearance checks still need small local fixes (CR-4 to CR-7). The cost is a seat 13 mm higher (840 → 853 mm), which is still normal for adventure bikes. Ground clearance rises to 229 mm.
4. **Motor.** The closest real motor I could find for sale is the **Helix SPX177-45**: 200 mm across, 13 kg, 150 kW and 120 Nm peak, 23,500 rpm.
   - The torque is fine: a 9.8:1 reduction instead of 7.8:1 gives the same torque at the wheel.
   - The good news: it is 20 mm smaller across than the envelope, so the pack-to-motor gap rises from 21.0 to about 31.0 mm.
   - The bad news: it is 163 mm long against 129 in the CAD, and there is no room for the extra 34 mm. Helix would need to build a shorter version, and they have not published the voltage it runs at. **This stays open.**
   - The inverter, the Cascadia CM200DX, is already a real part, and it covers the 400 A the drive needs.
5. **Cells.** The 26120-class cell in the CAD is not on open sale. **Molicel's P60B 21700 cell is.** Each cell holds 21.6 Wh, weighs 75 g and can supply 60 A.
   - A 100s15p pack (1,500 cells) gives 32.4 kWh at 420 V.
   - The cells weigh 112.5 kg, against 106.9 kg in the CAD: **+5.6 kg of cells, about +7 kg of pack.**
   - Five lanes of 70 mm cells fit the same 376 mm width. They need about 7% more side-view area.
   - At peak power each cell carries 24 A, well inside its 60 A rating.
   - Cells cost about $5k–11k per bike at today's listed prices.
6. **Things that fail a rule as drawn:**
   - **The mirror glass is too small.** It is 114 × 54 mm (6,156 mm²). US rules (FMVSS 111) need 8,065 mm² for a flat mirror. European rules (ECE R81) need the glass to hold a 78 mm circle.
   - **No certified headlamp module fits the 40 mm-tall, 90 mm-deep light band.** Off-the-shelf modules are about 95 mm tall and 124–162 mm deep. The band needs a custom lamp made for the bike, with its own tooling.
7. **Brakes, master cylinder, bars, inverter and wheels match real parts.** Two small changes are needed:
   - The front caliper mounts are 100 mm apart on the real Brembo Stylema (the CAD lugs are 109.5).
   - The real rear disc is 245 mm (the CAD has 240).
8. **Fork and shock have to be built to Bavuso's own spec**, which is normal for a bike maker. Real parts with similar numbers exist, so the specs are realistic.

## Verdict table

| Item | CAD value | Real part / requirement | Margin or delta | Verdict |
|---|---|---|---|---|
| Front tyre OD / width | 650.6 / 120 mm | Metzeler Tourance Next 2 120/70 R19: 663 / 133 | +12.4 / +13.0 | **fail**; fix with CR-1 |
| Rear tyre OD / width | 623.8 / 160 mm | Tourance Next 2 170/60 R17: 650 / 190 | +26.2 / +30.0 | **fail**; fix with CR-1 and CR-3 |
| Rims | 19×3.00 / 17×4.50 | 3.00–3.75 permitted (3.50 measuring) / 4.50 measuring | in range | pass |
| Tyre crown radius | about 104 / 159 mm (estimated from CAD) | not published | — | open |
| Belt to rear-tyre sidewall | 3.0 mm | ≥ 10 mm (my requirement) | **−12.0 mm (overlap)** with 170/60 | **fail, blocking**; CR-3 |
| Lower clamp to front tyre | 27.4 mm | 25 | 28.8 after CR-1 (21.2 without the lift) | pass with CR-1 |
| Front tyre to fork foot (sideways) | 12.5 mm | ≥ 10 | 6.0 with the 133 mm tyre | **fail**; CR-2 |
| Front body to steered tyre + fender | 22.1 mm | 20 | about 15.6 | **fail**; CR-4 |
| Frame (tail rail) to rear tyre | 25.0 mm | 20 | about 11.9 | **fail**; CR-5 |
| Shock tower to rear tyre | 22.5 mm | 20 | about 9.4 | **fail**; CR-6 |
| Plate / seat / tail / cross brace to rear tyre | 37.1 / 54.8 / 44.7 / 47.1 | 20 | 24.0 / 41.7 / 31.6 / 34.0 | pass |
| Fork: tube / travel | 48 mm / 170 mm | WP APEX 48; Marzocchi 50 @ 170 | 0 / 0 | pass (custom OE) |
| Fork: axle to top of outer tube | 824.7 mm | about 815 (Öhlins FGRT 301 765 @ 120, +50) | −9.7, an estimate | open |
| Front caliper mount | 109.5 mm (comment says 108) | Brembo Stylema 100 mm radial | −9.5 | **fail**; CR-8 |
| Front discs | 320 × 5, band 38 | Brembo 78B40870 320 × 5; Stylema band 32–34 | band −4 | pass with CR-8 |
| Rear disc / caliper | 240 mm / 2-piston | Brembo 68B407H1 245 × 5 / P34 (84 mm mount) | +5 OD | pass with CR-9 |
| Master cylinder | 19 mm class | Brembo 19RCS, 19 mm | 0 | pass |
| Shock 305 / 75 mm | ratio 0.246 | Öhlins STX46 KT122 406 / 100.5 (0.248, direct-mount PDS) | similar | open (custom OE) |
| Shock spring room | 88 OD (64 ID) | Öhlins 21040 springs, 51 ID | 13 mm spare | pass |
| Bars | 28.6 → 22.2 mm | Renthal Fatbar 28.6 / 22.2 | 0 | pass; bend made to drawing |
| Mirrors | 6,156 mm², 54 mm tall | ≥ 8,065 mm² (FMVSS 111); 78 mm circle (ECE R81) | −1,909 mm² / −24 mm | **fail**; CR-10 |
| Headlamp | 40 tall × 90 deep band | Hella Bi-LED L4565: ~94 lens, 124–162 deep | −54 / −34 | **fail as off-the-shelf**; custom lamp (CR-11) |
| Indicators | 40×28×20 / 36×30×22 reserves | Kellermann Atto DF Integral 22×12×6 (E-mark) | fits | pass (US DOT open) |
| Motor | 220 OD × 129, 150 Nm | Helix SPX177-45: 200 × 163, 120 Nm, 23.5k rpm | OD −20 (good), length **+34** | **open/blocking for that part**; CR-12 |
| Pack to motor | 21.0 mm | 20 | about 31.0 with a 200 mm motor | pass |
| Inverter | CM200 STEP | CM200DX: 200–480 V, 300 A continuous / 740 A peak, 6.75 kg | covers 400 A | pass |
| Cells | 26×120, 55 Wh, 180 g (not on open sale) | Molicel P60B 21700: 21.6 Wh, 75 g, 60 A | 100s15p = 32.4 kWh, +5.6 kg of cells | pass with CR-13 |
| Switchgear / grips | envelopes | not selected | — | open |

## What the real parts are, with numbers

Every value comes from the URL beside it. The full list is in `parts-register.csv`.

**Tyres.** Source: the Metzeler 2024 Technical Databook, table "Technical data to standard": https://intramoto.gr/wp-content/uploads/2024/04/METZELER-DATA.pdf

- **Tourance Next 2 120/70 R19 60V (IP 3960400):**
  - measuring rim 3.50, permitted 3.00–3.75;
  - maximum width in service 133 mm;
  - maximum diameter in service 663 mm;
  - rolling circumference 1,966 mm ±2%.
- **Tourance Next 2 170/60 R17 72V (IP 3960500):**
  - rim 4.50, permitted 4.50–5.50;
  - 190 mm wide, 650 mm across;
  - rolling circumference 1,921 mm.
- **Reference sizes:**
  - 160/60 ZR17 Sportec M5 (IP 1971300): 638 × 178 mm.
  - 90/90-21 Karoo 4: 707 × 103 mm.
- **Price:** about $220 front and about $265–286 rear, retail (https://www.motorcycletireco.com/tires/metzeler/tourance-next-2).
- **Michelin alternative:** the Anakee Adventure comes in the same two sizes (https://dealer.two-wheel.michelinman.com/wp-content/uploads/2023/12/2024_Adv_Touring_Brochure_ENG.pdf). Michelin's brochure gives no dimensions.
- **Tread profile radius:** none of the makers publishes it.
- **The brief vs the CAD:** the brief says the front is "21-inch class", but the CAD and `adventure-layout.md` model a 19-inch. I kept 19-inch. A 90/90-21 is 707 mm across, 56 mm more than the CAD, so a 21-inch front would be a much bigger change.

**Wheels.** Ducati's spoked tubeless set is 3.00×19 and 4.50×17, which matches the CAD sizes exactly. It costs $2,410.55 (https://www.omniaracing.net/en/ducati-performance-spoked-rims-300x19-and-450x17-for-ducati-multistrada-2021-p-271103.html). The Multistrada V4's cast wheels use the same sizes (https://www.cycleworld.com/ducati/multistrada-v4-s/). No maker publishes the wheel mass. Bavuso's hub, belt carrier and disc pattern make this a custom OE wheel built to those rim sizes.

**Fork.** No road fork with 170 mm of travel is sold off the shelf. The closest references:

- **Öhlins FGRT 301:** 48 mm, 765 mm long, 120 mm stroke, €3,975 (https://www.ohlins.eu/en/products/motorcycle/fgrt-301--4199/).
- **Marzocchi 50 mm on the Multistrada V4 S:** 170 mm travel (https://amcn.com.au/editorial/test-ducati-multistrada-v4-s/).
- **WP APEX 48 on the KTM 1290 Super Adventure S:** 200 mm travel (https://www.ktm.com/language-masters/en/digital-presskit/PressKit_KTM-1290-SUPER-ADVENTURE-S.pdf).

Nobody publishes the axle offset or the triple-clamp spacing; both go into Bavuso's spec to the supplier.

**Shock.** Also a custom OE part. The catalogue units nearest in shape:

- **Öhlins TTX GP HO 469:** 295 mm long, 60 mm stroke (https://www.ohlins.eu/en/products/motorcycle/ho-469--6323/).
- **Öhlins STX 46 KT 122:** 406 mm long, 100.5 mm stroke, €869. This is the direct-mount, no-linkage shock for the KTM 690 (https://www.ohlins.eu/en/products/motorcycle/kt-122--4458/). Its stroke-to-length ratio matches Bavuso's 75/305.
- **Öhlins 21040 springs:** 51 mm inside diameter × 160 mm long (https://www.alpharacing.com/en/oehlins-spring-51-160-95-n-mm/su-21040-31).

**Brakes.**

- **Front caliper, Brembo Stylema:** 4 × 30 mm pistons, 100 mm radial mount, 32–34 mm disc band, 625 g (https://hhrperformance.com/products/brembo-caliper-left-p4-30mm-stylema-cast-monobloc-100mm-radial-mount-front-titanium-grey). A pair costs €695–710 (Carpimoto) to $1,686 (MOTO-D).
- **Front disc, Brembo Serie Oro 78B40870:** 320 × 5.0 mm (https://www.oppracing.com/product_display/14428604-brembo-serie-oro-disc-320x50mm-serie-oro-floating-front-78b40870/).
- **Rear disc, 68B407H1:** 245 × 5 mm, 4 holes (https://www.carpimoto.com/en-US/42247_68B407H1-Brembo-Serie-Oro-Brake-Rotor-68B407H1.htm).
- **Rear caliper, Brembo P34:** 2 × 34 mm pistons, 84 mm mount (https://www.carpimoto.com/en-US/23744_20B85257-Brembo-Rear-Brake-Caliper-P2-34.htm).
- **Master cylinder, Brembo 19RCS:** 19 mm, $553–689 (https://www.motosport.com/brembo-corsa-corta-19rcs-brake-master-cylinder).

**Controls and lights.**

- **Bars, Renthal Fatbar:** 28.6 mm at the clamp, 22.2 mm at the ends, $134.95 (https://renthal.com/products/fatbar-826-01).
- **Headlamp, Hella Bi-LED L4565 90 mm module:** about a 94 mm lens, 124–162 mm deep, ECE approved (https://www.hella.com/australiansolutions/assets/documents_global/Hella-90mm-Module-Brochure-0224.pdf).
- **Indicators, Kellermann Atto DF Integral:** 22 × 12 × 6 mm, E-marked (https://www.kellermann-online.com/en/atto-df-integral/156.500).
- **Mirror rules:**
  - US (FMVSS 111 S10.1): a flat mirror needs at least 8,065 mm², a convex one at least 6,450 mm² (https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/subpart-B/section-571.111).
  - Europe (ECE R81): at least 69 cm², and the glass must hold a 78 mm circle. This comes from a secondary source (https://far-ecommerce.com/en/pages/guida-specchietti-moto-omologati).

**Motor and inverter.**

- **Helix SPX177-45** (https://www.ehelix.com/products/spx177/):
  - 150 kW / 120 Nm peak; 90 kW / 74 Nm continuous;
  - 23,500 rpm;
  - 13 kg;
  - 200 mm across, 163 mm long overall, 42 mm stator.
- **Cascadia CM200DX** (https://www.cascadiamotion.com/cm-200): 200–480 V; 300 A rms continuous and 740 A rms peak; 225 kW; 6.75 kg.
- **Rejected:**
  - YASA P400R: 305 mm across, at least 24 kg, and only 110 kW at 350 V (https://yasa.com/media/2021/05/yasa-p400rdatasheet-rev-14.pdf).
  - Cascadia iM-225W: 60 kg (https://www.cascadiamotion.com/im-225w).
  - EMRAX 228 MV: needs about 630 V (see `drive-study.md`).
- **Not checked:** Saietta, Zytek/Ricardo, BorgWarner HVH as a standalone motor, Golden Motor and QS. Golden Motor and QS are well below 130 kW.

**Cells.**

- **Molicel INR-21700-P60B** (https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P60B_80145.pdf):
  - 6.0 Ah (5.85 minimum), 21.6 Wh;
  - 60 A standard, 100 A maximum discharge;
  - 75 g maximum, 280 Wh/kg.
  - Business listings run $3.35–8.00 per cell. These are Alibaba sellers, not authorised distribution.
- **Molicel P50B fallback:**
  - 18.0 Wh, 50 A continuous, 70 g maximum;
  - 21.55 × 70.15 mm, 260 Wh/kg (https://files.batteryjunction.com/frontend/files/molicel/DataSheets/MOLICEL-P50B-Datasheet.pdf);
  - $7.50 each at 1,000+ (https://www.18650batterystore.com/products/molicel-21700-p50b-5000mah-50a-battery).
- **EVE 4695 (30 Ah, 425 g):** no public seller found (https://www.aboutenergy.io/voltt-battery-library/eve-energy-4695e).

## How the comparison was checked

- **The script reads the CAD; it doesn't re-type it.** `supplier-compare.py` pulls each value from `build-adventure.py` with a pattern match and stops if a pattern goes missing. It does not copy numbers by hand.
- **The derived numbers reproduce the audit file.** The script recomputes the front axle position the same way the generator does. Its trail is 111.86 mm, the same as the 111.9 in `geometry-adventure-audit.json`.
- **The lift arithmetic was checked by hand.** With RF 331.5 and LIFT 53.1:
  - the axle moves 7.6 mm down the fork;
  - the wheelbase becomes 1,490.0 mm (+3.2);
  - the trail becomes 114.7 mm.
  - Lower-clamp gap: 27.44 − 6.2 + 7.6 = 28.8 mm.
- **The belt overlap is real, not a modelling artefact.** The belt's straight runs pass from 143 to 556 mm from the rear axle, which crosses the tyre's 216–325 mm radius band. So the tyre's full width matters along the belt.
- **The clearance estimates are rough.** They are plain subtractions (each gap minus the growth in tyre radius, or in half-width where the tyre is steered). This is not a CAD rebuild. Checks that are rebuilt from RF/RR, such as the pack, the lower covers and the undertray, are marked as self-adjusting.

## CAD change requests

Every value below is for `tools/build-adventure.py`. **Another agent owns that file, so I have not edited it.**

- **CR-1, real tyres and ride height:**
  - Set `RF,RR=325.3,311.9` → **`331.5,325.0`** (Metzeler max in service: 663 / 650).
  - Set `LIFT=40.0` → **`53.1`**, raising everything sprung by 13.1 mm.
  - Set the tyre widths `wheel('Rear',0,RZ,160,…)` → **190** and `wheel('Front',FX,FZ,120,…)` → **133**.
  - Update the label text to "120/70R19 / 170/60R17".
  - This keeps the swingarm, shock and rake unchanged. The fork becomes 7.6 mm longer, the trail 114.7 mm and the wheelbase 1,490.0 mm. Seat and ground clearance rise 13.1 mm.
  - **Checks affected:**
    - lower clamp: 27.4 → about 28.8;
    - front body to steered tyre: 22.1 → about 15.6 (CR-4);
    - frame to rear tyre: 25.0 → about 11.9 (CR-5);
    - shock tower to tyre: 22.5 → about 9.4 (CR-6);
    - plate: 37.1 → about 24.0.
  - **Also widen the keep-out sweeps:**
    - rear sweep (lines 364 and 1085): `±80` → **`±95`**;
    - front sweep (line 366): `±60` → **`±66.5`**.
  - Without this, every rear check misses the real tyre's sidewalls.
- **CR-2, fork leg spacing:**
  - Set `yo=side*100` → **`side*105`** (210 mm between leg centres). The tyre-to-fork-foot gap goes from 6.0 to 11.0 mm.
  - Set the front fender half-width from 66 → **72**.
  - Add a check: tyre (133 mm wide) to fork feet sideways, at least 10 mm.
  - The steering keep-out (r 140) still holds: √(105² + 36.1²) + 28 = 139.0.
- **CR-3, belt line (blocking):**
  - Move the belt plane from Y −105..−83 → **Y −127..−105** (both pulleys, the belt and the flanges).
  - Move the left swingarm arm from `ya=125+8` → **`125+33`** (centre Y −158).
  - Move the left pivot stub and bearing out 25 mm: Y −110..−150 → **−135..−175**. That leaves 4 mm to the inside of the rail at Y −179, so the pivot node needs redrawing.
  - Extend the gear-case output shaft by 22 mm.
  - Add a check: belt to tyre sidewall, at least 10 mm.
  - The rear-suspension and drive owners must re-run their work: a wider arm changes its stiffness and the pivot loads.
- **CR-4, front body at lock:** add 6.5 mm to the clearance used for the shroud and the battery-cover front wall in the steered sweep. In practice, `x_cover(gap=22)` → **28.5** wherever the lock sweep decides the shape (Z < 430). Re-run `front_body_vs_tyre_fender_lock_sweep`, which needs 20 mm.
- **CR-5, tail rail:** raise the rear end of the tail rail from (−60, ±100, **790**) → **(−60, ±100, 798.5)**, which restores 20 mm. Re-check `frame_vs_rear_bump` and the seat and undertray shapes over the rail.
- **CR-6, shock tower:** trim the rear edge of the tower plates (or narrow the `stadium` width from 22) by **11 mm** so the tower stays at least 20 mm from the 325 mm tyre. If trimming cannot do it, the rear-suspension owner must move `SHOCK_S` from 210 → **199**, which changes the leverage curve.
- **CR-7, rear hugger:** set `cyl(...,334,324)` → **`347,337`** and its half-width from 72 → **103**. As drawn, its 324 mm inside radius sits inside the 325 mm tyre.
- **CR-8, front calipers:**
  - Set the radial lug half-angle from 19.5° → **17.75°** on the 164 mm radius, which gives the Stylema's 100 mm spacing.
  - Set the disc inner radius `discR-38` → **`discR-34`** (34 mm band).
  - Change the caliper reserve text to "Brembo Stylema 100 mm".
  - Check the 6-boss hub flange (bosses on R44) against the 78B40870 drawing before fixing it.
- **CR-9, rear brake:** set `discR` rear 120 → **122.5** (245 mm disc with 4 holes). Change the caliper text to "Brembo P34, 84 mm mount".
- **CR-10, mirrors:** make the glass `box(...,2.4,114,54)` → **2.4 × 130 × 80** with 10 mm corner radii, about 10,300 mm². That passes both FMVSS 111 and ECE R81. The head grows from 140 × 82 → **150 × 98**. Re-run `bars_at_lock_vs_tank_fairing_screen` (62.5 mm now, 30 required).
- **CR-11, headlamp:** keep the 40 mm band only as the visible lens of a custom OE lamp. Reserve **130 mm of depth** behind the lens (the band is 90 mm deep now) for the LEDs, heatsink and driver. Re-check the BMS, inverter and steering sweep against the deeper box. The fallback, two 94 mm Hella modules, needs an opening at least 96 mm tall.
- **CR-12, motor envelope (open):**
  - With the Helix SPX177-45: `IPM_R` 110 → **100** (pack gap about +10 mm).
  - The length must stay **at most 129 mm**. Bavuso has to ask Helix for a shorter build. The catalogue length of 163 mm would put the motor 22 mm into the right swingarm arm's sweep, which is 12 mm clear today.
  - Set the reduction from about 7.8 → **about 9.8**.
- **CR-13, cells:**
  - `CELL_R,CELL_L,CELL_WH,CELL_G` = **10.775, 70.15, 21.6, 75**.
  - `SERIES,PAR` = **100, 15**.
  - `PITCH` = **23.55**.
  - `LANES` = **(−152.3, −76.2, 0, 76.2, 152.3)**: the 5 lanes span 374.75 mm, inside today's 376.
  - `PER_LANE=SERIES*PAR//3` → **`//5`**.
  - Change `pack_summary` to "1500 × Molicel P60B 21700, 100s15p".
  - Expect the pack to grow about 7% in side-view area, probably one more band of cells. Re-check charger-to-pack (16.5 mm now, 10 required), pack-to-front-tyre, and the cell centroid height.

## What this does not prove

- **The clearance numbers after the changes are first-order subtractions, not a rebuild.** The CAD owner has to apply the change requests and re-run all 58 checks.
- **Tyre sizes are Metzeler's "maximum in service" values.** These are the right numbers for clearance, but a new tyre on the bench is a few mm smaller. Michelin and Pirelli dimensions were not found. No maker publishes the tread profile radius.
- **The fork length of about 815 mm is interpolated, not from a datasheet.** No fork maker publishes offsets, clamp spacing or masses for these parts.
- **The Helix motor's DC voltage, price and lead time are unknown.** It may be an 800 V design that cannot make full power at 360 V. Saietta, Zytek/Ricardo, BorgWarner HVH (as a standalone motor), Golden Motor and QS were not surveyed in detail.
- **Cell prices are retail and B2B listing snapshots, not quotes.** Pack mass assumes the drive study's 0.80 cells-to-pack ratio. Thermal behaviour and cycle life of the P60B at this duty are not checked.
- **Prices change.** No supplier quote was requested, and nothing was ordered.
- **Not covered:** headlamp optics and beam pattern, US DOT certification of the Kellermann indicators, mirror field of view, grips and switchgear dimensions, wheel and hub masses, belt part numbers and belt tension.
