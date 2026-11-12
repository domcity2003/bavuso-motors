# Bavuso V1.0 battery, motor and inverter cost-down study

November 2, 2026, US Central. Prepared by Claude Opus 5.5. Planning estimates anchored on public prices. **None of these numbers is a supplier quote.** No suppliers were contacted.

## The plain answer (updated after the optimisation, same day)

**The best design is a 490 lb bike that costs about $24.8k to build at 10,000 a year.** It goes 200 miles at 70 mph, charges 10–80% in about 14 minutes, and makes 130 kW. It is lighter than a BMW R 1300 GS (about 522 lb) and has more than twice the highway range of a Zero DSR/X (545 lb).

| Part | Choice |
|---|---|
| Cells | Fast-charge large cylinders (26120 / 46-series class), 99 in series × 6 in parallel, **32.7 kWh**, 416 V full |
| Battery case | **Structural**: the cells are bonded into a case that carries frame loads, so the frame can be lighter |
| Motor and controller | **Axial-flux motor** (EMRAX 228 class) with a contract-built silicon-carbide controller |
| Light parts | **Premium package**: forged wheels, titanium fasteners, a lithium 12 V battery and magnesium covers |

How the optimiser found it ([tools/powertrain-optimise.py](tools/powertrain-optimise.py), chart in `visuals/powertrain-frontier.png`):
- It tried every combination of cell, pack size, battery-case construction, lightweight package and motor. That gave 36 designs that meet all the hard requirements:
  - 200 miles at 70 mph even if the aero work only reaches CdA 0.40;
  - 25-minute charging or better;
  - 130 kW of peak power.
- For each one, the battery is sized to that bike's own weight.
- Then it kept the lightest bike at each cost and measured what each further pound costs.

**Each step down in weight, and what it costs per pound saved at 10k bikes a year:**

| Step | Bike | Cost at 10k/yr | Cost per lb saved |
|---|---:|---:|---:|
| Cheapest that meets the requirements: large cylinders, module pack, radial motor | 561 lb | $18.9k | — |
| + structural battery case | 525 lb | $19.3k | **$11** |
| + axial-flux motor | 505 lb | $21.5k | $113 |
| **+ premium light parts (recommended)** | **490 lb** | **$24.8k** | $221 |
| + carbon bodywork and subframe | 477 lb | $28.7k | $297 |

Why stop at 490 lb:
- **The carbon step** costs about $300 per pound saved, and it puts 1,000-a-year launch bikes at $41.6k. It's a better fit as a top "Carbon" edition than as the base bike.
- **Everything above it is cheap per pound and gives the bike its premium character.** The axial motor and the light parts are what a status bike is expected to have.

**Silicon cells (Amprius) lose for a reason other than cost.** They are the lightest option, 394–424 lb. But at the charge rate their datasheet allows, a 10–80% charge takes about 28 minutes, against 14 for the large cylinders. At today's assumed price they also put the bike at $35–42k at 10k/yr. Silicon only becomes the best answer if Amprius can show **both** about 2C+ charging **and** about $350/kWh. That needs a quote and test data.

**If the large cylinders reach their makers' claimed 330 Wh/kg** (I modelled 305), the same design weighs **466 lb** at the same cost.

**At the 1,000-a-year launch volume** the recommended bike is about $36.5k, about $1.5k over the cap. Launching without the premium-parts package ($32.0k, 505 lb) and adding it as volume grows keeps every stage under $35k.

What follows below is the first pass of this study. It compared the cells and motors one at a time, before the optimisation. Its cost evidence still stands.

## First pass

**Cost is no longer the problem. Weight is.**

- The current package costs $41.2k a bike at 10,000 bikes a year:
  - Amprius silicon cells, $14k a bike at 10k/yr in the Codex model;
  - EMRAX 208 motor;
  - Cascadia CM200 inverter.
- Swap the cells for mainstream cylindrical lithium-ion cells and the drive for an axial-flux motor with a contract-built inverter. The bike then lands at **about $21k delivered at 10k/yr and about $31k at 1k/yr**, with a bigger 30–32 kWh pack. That is under the $30–35k cap at both volumes. It leaves about $9–14k a bike at scale to spend on premium parts.
- The catch: at 30 kWh, mainstream cells make a heavy bike, **about 520–530 lb ready to ride**. Only the silicon cells keep it near 430 lb, and at today's assumed silicon price they cost about $12.8k a bike more.
- 520 lb is normal for the class.
  - BMW R 1300 GS: about 237 kg (522 lb)
  - Zero DSR/X: 247 kg (545 lb)

  But it breaks the original "under 400 lb" goal. **That goal and "200 miles at 70 mph" cannot both be met at this price with any cell on sale today.**

### Recommended package

| Part | Choice | Why |
|---|---|---|
| Cells | **Fast-charge large cylinder, 26120 or 46-series class**: about 300+ Wh/kg, 3C+ charging, about 96s6p, **31.7 kWh**, 403 V full. Suppliers to approach: EVE and Wanxiang A123, which are industrialising the 26120 for Stark Future's motorcycles. | Lightest mainstream option. 10–80% in about 14 min on a Tesla V3 Supercharger. About $150/kWh at volume. |
| Fallback cells, in production today | Molicel P50B 21700, 106s16p, 30.5 kWh | Same cost. About 55 lb heavier. 21-min charge. |
| Motor | **Axial-flux, EMRAX 228 class**: 124–130 kW peak, 13.5 kg | Meets the 120–130 kW target. Light. A genuine "next level" piece. |
| Inverter | **SiC inverter built to a reference design by a contract manufacturer** | About $1k at 10k/yr, against $6k for an off-the-shelf CM200 |
| Battery management system (BMS) | Custom, built on a standard cell-monitoring chip, with cell temperatures read by the same chips | Replaces $2.2k of BMS and sensing lines with about $300–400 |

Estimated result (rows LCYL + AXIAL+SiC in [powertrain-cost-down.csv](powertrain-cost-down.csv)):
- **$30,988 a bike at 1k/yr.**
- **$20,903 a bike at 10k/yr.**
- About 528 lb ready to ride, with 200 miles at 70 mph.

## What I changed and why

The Codex cost model (Oct 25) left the powertrain at $39.1k a bike at 1k/yr and $27.9k at 10k/yr:

| Group | 1k/yr | 10k/yr |
|---|---:|---:|
| Cells (700 Amprius SA504) | $21,000 | $14,000 |
| Inverter (CM200DX) | 7,500 | 6,000 |
| Motor (EMRAX 208) | 6,000 | 4,500 |
| Cell temperature sensing | 1,800 | 1,300 |
| BMS | 1,100 | 900 |
| Pack mechanical | 1,100 | 800 |
| Battery loop pump | 600 | 430 |

Three things drive the saving:

1. **Silicon cells cost 4–5 times mainstream cells.**
   - The model priced SA504 at about $532–798 per kWh.
   - Mainstream high-power cylindrical cells sell for about $290/kWh at hobby bulk. At industrial volume the evidence points to $60–140/kWh.
   - For 30 kWh, that is the difference between about $16k and about $4.5k of cells.
2. **The off-the-shelf drive is priced for race teams.**
   - A CM200 retails for $7–9k.
   - At car volumes an inverter of this power costs a few hundred dollars: Munro estimated the Tesla Model Y inverter at about $520.
   - A motorcycle-volume inverter from a contract manufacturer sits between those, about $1–2k.
3. **The $1,300–1,800 for temperature sensing was a placeholder.** Modern cell-monitoring chips read the cell temperatures directly.

The existing EMRAX 208 is also too small for the new speed targets (about 86 kW peak against 120–130 kW), so the drive had to change anyway.

## Results, all options

All bikes are sized to 30–32 kWh nominal, enough for 200 mi at 70 mph at CdA about 0.38 (see `aero-baseline-report.md`). Costs are the full delivered cost of the bike: Codex's whole-bike number with only the powertrain swapped. Weight uses the 95.5 kg non-pack allowance from the engineering release review.

| Cells | Drive | kWh | Pack | Bike weight | 10–80% charge | Peak power OK | $/bike at 1k/yr | $/bike at 10k/yr |
|---|---|---:|---:|---:|---:|:---:|---:|---:|
| SA504 silicon (current) | current EMRAX 208 + CM200 | 30.4 | 98 kg | 427 lb | 28 min | no | 60,062 | 41,285 |
| SA504 silicon | axial-flux + SiC | 30.4 | 98 kg | 436 lb | 28 min | yes | 51,066 | 33,674 |
| SA504 silicon | radial tier-1 | 30.4 | 98 kg | 453 lb | 28 min | yes | 48,255 | 31,357 |
| **Large fast-charge cylinder** | **axial-flux + SiC** | **31.7** | **140 kg** | **528 lb** | **14 min** | **yes** | **30,988** | **20,903** |
| Large fast-charge cylinder | radial tier-1 | 31.7 | 140 kg | 545 lb | 14 min | yes | 28,177 | 18,587 |
| Molicel P50B 21700 | axial-flux + SiC | 30.5 | 165 kg | 583 lb | 21 min | yes | 30,814 | 21,022 |
| Samsung 50S 21700 | axial-flux + SiC | 30.5 | 170 kg | 593 lb | 42 min | yes | 29,784 | 20,348 |
| LG M58T 21700 (energy cell) | axial-flux + SiC | 30.5 | 148 kg | 547 lb | 70 min | **no** | 29,029 | 19,795 |

Every combination, including the EMRAX 228 + CM200 option, is in [powertrain-cost-down.csv](powertrain-cost-down.csv).

### What rules options out

- **High-energy "range" cells (LG M58T type)** are cheap and fairly light. But they can't charge fast (70 min) or deliver 130 kW from a 30 kWh pack: at about 2.2C, about 66 kW. That fails the fast-charge goal and the speed goal.
- **The Samsung 50S** is limited to 6 A continuous charge, which gives a 42-minute stop. That is not good enough for road trips.
- **The current EMRAX 208** is under-powered for 145–150 mph and a 3-second 0–60.

## The weight decision (first pass; superseded by the optimisation above)

| Path | Bike | $/bike at 1k/yr | $/bike at 10k/yr |
|---|---:|---:|---:|
| Fast-charge large cylinder | about 528 lb | about $31k | about $21k |
| Silicon (SA504) | about 436 lb | about $51k | about $34k |

- Silicon saves about 92 lb for about $12.8k a bike at 10k/yr (about $140 per pound). At 1k/yr it breaks the cap.
- **Silicon only fits the cap if its price falls.** It needs to reach about **$420/kWh** at 10k/yr to stay under $30k a bike, or about $330/kWh at 1k/yr to stay under $35k. Today's model assumes $532–798/kWh.
- Amprius already sells 30 Ah SiCore cylindrical cells to Chinese two-wheeler makers ($21M order, March 2026). Worth asking them two things:
  - whether that cell, or a cylinder of the size we choose, can drop into the same pack design;
  - at what price.

**My recommendation:**
- Set the weight target to **about 500–530 lb ready to ride**, and lock the pack around a large fast-charge cylinder.
- Keep the module design open to a silicon cylinder, so a later "lightweight edition" is a cell swap, not a new bike.

A 520-lb adventure bike that does 200 highway miles, charges 10–80% in about 15 minutes at a Supercharger, and runs 145–150 mph is unmatched. The Zero DSR/X is heavier and does about 85 highway miles.

## What the recommended pack means for the shape lock

| Item | Value |
|---|---|
| Layout | 96 in series × 6 in parallel = 576 cells of about 55 Wh (26120 class) |
| Voltage | 346 V nominal, 403 V full. Compatible with Tesla V3 Superchargers and 400 V CCS. |
| Cell mass | About 104 kg |
| Pack mass | About 140 kg at a 74% cell-mass fraction |
| Pack volume | About 67 L, against the current 690 × 220 × 550 mm envelope of about 83 L |

- The pack fits the current envelope by volume. It is **about 55 kg heavier** than today's 85 kg SA504 pack.
- The frame, swingarm pivot area, brakes and suspension rates must be sized for about 240 kg ready to ride, plus rider and luggage. Expect the 95.5 kg non-pack allowance to grow by about 5–10 kg.
- **Use the spare volume to win ground clearance.** Make the pack shorter and taller rather than long and low. Large cylinders standing upright suit this.

## Price evidence used

| Item | Public evidence | Used in model (1k / 10k bikes a year) |
|---|---|---|
| Industry cell and pack prices | BNEF 2025: pack $108/kWh average, NMC packs $128/kWh, cells about $74–79/kWh ([BNEF](https://about.bnef.com/insights/commodities/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices/), [Battery Tech Online](https://www.batterytechonline.com/trends/battery-pack-prices-drop-8-to-record-108kwh-despite-rising-lithium-and-cobalt-costs-in-2025)) | Floor for the large-volume cases |
| Molicel P50B | 18.0 Wh, about 70 g, 25 A max charge, 60 A discharge ([Molicel datasheet](https://www.fsaeonline.com/content/Molicel-TDS--INR-21700-P50B-80122.pdf)). Bulk about €4.5–4.8 ex-VAT at nkon. | $200 / $150 per kWh |
| Samsung 50S | 6 A continuous charge, 72 g ([datasheet copy](https://www.imrbatteries.com/content/samsung_50S.pdf)). Marketplace $1.10–2.47 per cell in volume ([Alibaba listing](https://electronics.alibaba.com/product/samsung-cylinders)). | $170 / $130 per kWh |
| LG M58T | About 275–285 Wh/kg by forum calculation ([endless-sphere](https://endless-sphere.com/sphere/goto/post?id=1827778)), 12.5 A max discharge | $150 / $115 per kWh |
| 26120 fast-charge cylinder | Stark Future / EVE: 330 Wh/kg, 10-minute charge in prototypes, industrialising 2026 ([Enduro21](https://enduro21.com/en/news/stark-future-partners-with-eve-energy-for-next-generation-battery-cells)). Wanxiang A123 is a second source ([The Pack](https://thepack.news/stark-future-and-wanxiang-a123-partner-to-industrialise-26120-cell-for-high-performance-electric-motorcycles/)). | Modelled at 305 Wh/kg and 3C. $210 / $150 per kWh. |
| Amprius SA504 / SiCore | No public production price. $21M SiCore order from two- and three-wheeler makers ([Amprius](https://ir.amprius.com/news-events/press-releases/detail/161)). | Codex $798 / $532 per kWh, unchanged |
| EMRAX 228 | About €3,590 liquid-cooled, third-party reseller. 124 kW peak, 13.5 kg ([EMRAX 228](https://emrax.com/e-motors/emrax-228/)). EMRAX says the current range will be phased out for a next generation. | Axial-flux motor about $3,300 / $2,600 |
| Cascadia CM200DX | $7.2–8.7k retail. A Cascadia integrated module lists at $16,100 ([reach.dog](https://reach.dog/shop/legacy-ev/products/cascadia-motion-im-225-kit)). | $7,500 / $6,000 (Codex) |
| Volume inverters | Munro: Tesla Model 3 inverter about $810, Model Y about $522 ([Charged EVs](https://chargedevs.com/newswire/teardown-expert-sandy-munro-compares-tesla-nissan-jaguar-inverters/)). DOE 2025 target $2.7/kW ([DOE](https://www.energy.gov/eere/vehicles/articles/high-voltage-high-power-density-traction-drive-inverter-keystone-project-1)). | Contract-built SiC inverter about $2,200 / $1,000 |
| Chinese e-drive kits | Brogen 100 kW motor, gearbox and controller listed at $1,235 for 2+ sets (unverified marketplace listing) ([listing](https://bestsuppliers.com/products/3knczagkevao/brogen-high-efficiency-100kw-electric-drivetrain-electric-car-motor-conversion-kit-for-ev)) | Radial tier-1 drive $3,000 / $1,500 |
| Orion BMS 2 | 180-cell unit $1,680 list ([Orion](https://www.orionbms.com/manuals/pdf/orionbms2_purchasing_guide.pdf)) | Replaced by a custom BMS. Pack hardware is $1,500 / $1,050 fixed plus $0.25–0.60 per cell. |

## Limits and next steps

- **The cell prices are estimates, not quotes.** Moving the large-cylinder price by ±$50/kWh moves the bike by about ±$1.7k at 10k/yr. The recommendation holds even at $250/kWh.
- **The 26120 / 46-series cells are not yet in volume production for outside buyers.** The P50B fallback keeps the program alive if they slip.
- **Engineering costs are not in the unit cost:**
  - a custom inverter;
  - a BMS;
  - pack design and certification (UN 38.3, ECE R136 / FMVSS);
  - motor qualification.

  Together these are probably $2–5M up front. They belong in the launch-cash model.
- **Charging, the chiller and the onboard AC charger were not part of this study.** Those lines (about $2.9k a bike at 10k/yr) are the next cost-down targets.
- **Next actions:**
  - Request quotes from EVE, Wanxiang A123, Molicel and Amprius, on cylinder format, price at 1k and 10k bikes a year, and fast-charge cycle life.
  - Ask EMRAX about its next-generation motor and its price at volume.
  - Approach two SiC inverter contract manufacturers.
  - Then re-run `tools/powertrain-cost-down.py` with the quoted numbers.
