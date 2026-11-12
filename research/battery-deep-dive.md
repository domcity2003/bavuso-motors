# Bavuso Motors: battery technology and design study

Research date: October 25, 2026, US Central. Prepared by Codex (GPT-6 family).

Scope: public manufacturer specifications, laboratory research, and calculations for Bavuso's actual mission. This is an engineering literature and specification review, not a cell test, procurement quote, or validated vehicle design. Supplier claims are identified as such. No supplier has been contacted and no purchases have been made.

## Main finding

**Yes, we can optimize a battery specifically for this motorcycle.** The useful opportunity is a carefully chosen cell, an unusually light complete pack, thermal management, and a vehicle shape that reduces the energy the battery must supply. Developing new electrode chemistry is a separate, much more demanding research program.

The initial 220 Wh/kg complete-pack assumption is a reference case, not the ceiling of current technology. Newer high-energy cells make the outlook more promising than that single case suggested. However, the best energy-density, charge-speed and longevity figures often belong to different cells. They cannot be combined into an imaginary best-of-everything battery.

For this study, the owner's latest requirements are:

- 200 miles on a charge, with **70 mph as the highway range calculation baseline**.
- **77 mph for aerodynamics, rider comfort and wind-stability design**; also calculate consumption at that speed.
- 125+ mph top speed, evaluated separately from the range trip.
- Tesla charging compatibility.
- Less than 400 pounds including the battery, with comfortable, compact, minimal styling.

Our most promising battery research direction is **high-energy nickel-based lithium-ion, including silicon-rich anodes, in a compact pack sized for moderate continuous discharge and occasional higher power**. An Amprius SA504-class cell deserves particular scrutiny, alongside a conventional cylindrical reference and a more conservative balanced pouch reference. This is a shortlist for investigation, not a supplier selection.

## 1. What a battery has to optimize

Energy and power are different. Kilowatt-hours (kWh) measure the energy available for the trip. Kilowatts (kW) measure how quickly the battery supplies or accepts it. Wh/kg measures energy per mass; Wh/L measures energy per volume. A bike can meet its mass budget and still fail to fit a comfortable rider package.

A lithium-ion cell moves lithium ions between two electrodes through an electrolyte, while electrons travel through the external circuit. The separator keeps the electrodes from directly touching. Its performance depends on the complete combination of electrodes, electrolyte, separator and construction. [University of Washington battery explanation](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/), [EPA battery chemistry overview](https://www.epa.gov/hw/lithium-ion-battery-recycling)

The engineering tradeoff is not just 'how much lithium can we fit?' We must store energy, move ions and electrons fast enough, remove heat, accommodate expansion, prevent internal failures, and repeat the process for years. The supporting components consume mass and space without contributing directly to stored energy.

For Bavuso, we should evaluate delivered trip energy per kilogram of the complete installed pack under the actual load and temperature, alongside charging time and degradation. Bare-cell capacity measured slowly in a laboratory is an input to that evaluation, not the final answer.

## 2. The numerical target, worked backward

The [range/weight study](range-weight-budget.md) estimates the following at 70 mph, with 90% of nominal energy available for the trip and a 90 kg allowance for everything outside the battery:

| Combined bike/rider drag area | Nominal energy for 200 miles | Complete-pack density needed at the 400 lb ceiling |
|---|---:|---:|
| 0.30 m²: ambitious low drag | 25.2 kWh | 276 Wh/kg |
| 0.40 m²: improved | 31.8 kWh | 348 Wh/kg |
| 0.50 m²: upright reference | 38.5 kWh | 421 Wh/kg |

The available pack mass is about 91.4 kg / 201.6 lb. The rest-of-bike allowance and drag values are unvalidated engineering assumptions. In particular, 0.30 m² is an ambitious target for comfortable riding, below the tucked values in the previously cited wind-tunnel study. [Kirca and McGordon, Table II](https://wrap.warwick.ac.uk/id/eprint/180779/1/WRAP-Effect-rider-position-energy-consumption-23.pdf)

At 77 mph, the corresponding capacities rise to 29.3, 37.3 and 45.3 kWh. Designing comfort around 77 mph does not change the 70 mph range baseline. Neither calculation is sufficient to substantiate an advertised range without a defined, repeatable test.

We also need room for aging. A simplified pack delivering 200 miles when new would deliver about 160 miles at 80% remaining energy capacity, all else equal. Maintaining the original trip energy at that condition would require 25% more initial capacity, not 20%. This is a sensitivity example, not a new requirement or life prediction.

## 3. Bare cells versus the complete pack

Define `f = mass of packaged cells / mass of complete battery pack`. Then, to first order:

```text
nominal pack Wh/kg = cell Wh/kg × f
available trip Wh/kg = nominal pack Wh/kg × available-energy fraction
```

These are separate factors: packaging lowers energy per kilogram; charge buffers and reserve lower the fraction of that energy allocated to a trip. Do not subtract either twice.

For screening, compare f = 0.75, 0.80 and 0.85. These are assumptions to test, not measured pack performance or promises. At f = 0.80, every 80 kg of cells carries 20 kg of additional pack equipment. At f = 0.85, only 15% of pack mass remains for all supporting equipment.

That equipment includes enclosure, cell supports or compression hardware, cooling interfaces, connections, monitoring, contactors, protection, insulation, sealing and mechanical protection. Automotive cell-to-pack technology demonstrates that integration matters, but a small motorcycle cannot inherit a car pack's integration figures automatically. CATL has published Qilin system densities up to 255 Wh/kg; its newer technology page lists up to 265 Wh/kg for NMC Qilin. [2022 Qilin announcement](https://www.catl.com/en/news/1013.html), [CATL technology page](https://www.catl.com/en/research/technology/)

At 80% cell mass fraction, the required bare-cell densities for the three Bavuso cases become approximately **345, 435 and 526 Wh/kg**. At 85%, they become **325, 410 and 495 Wh/kg**. That is why bodywork and cell selection must be developed together.

## 4. Concrete cell candidates and what their numbers mean

All values below are manufacturer disclosures, not independently reproduced results. Listing a cell publicly does not establish that Bavuso can buy samples or production quantities. Minimum orders, pricing, lead time and application approval remain unknown.

| Candidate | Published cell specific energy | Relevant disclosed capability | Implication |
|---|---:|---|---|
| Molicel P50B | 265 Wh/kg on current product page | High-power cell; 5C charge advertised | Useful power/charging reference; relatively heavy for range |
| Molicel P60C | 284 Wh/kg | Up to 5C charge and 100 A discharge advertised | Power-focused comparison; commercial delivery timing unverified |
| Molicel M65A | 322 Wh/kg advertised | 6.5 Ah; 26 A discharge; standard 6.5 A charge | More relevant energy-focused cylindrical reference |

Sources: [P50B](https://www.molicel.com/inr-21700-p50b/), [P60C](https://www.molicel.com/inr-21700-p60c/), [M65A product page](https://www.molicel.com/inr-21700-m65a/), [M65A datasheet v0.1](https://www.molicel.com/cn/wp-content/uploads/Product-Data-Sheet-of-INR-21700-M65A-80153-0.1_250805.pdf).

M65A deserves a conservative calculation too: its typical 23.4 Wh divided by maximum 74.5 g gives **314 Wh/kg**, rather than 322. That is not necessarily a contradiction: maximum cell weight and advertised typical specific energy need not describe the same specimen. We screen both values. Its published standard charge is 1C; this does not establish a maximum charge rating above 1C.

Three informative pouch examples from [Amprius's Q3 2026 catalog](https://amprius.com/documents/Amprius_Product_Catalog.pdf):

| Model; PDF page | Cell Wh/kg | Continuous discharge | Maximum charge | Stated cycling to 80% state of health |
|---|---:|---:|---:|---|
| SA02; 4 | 340 at 1C discharge | 3C | 1C | 700 cycles, +1C/-1C, 100% depth |
| SA504; 52 | 390 | 6C | 2C | 500 cycles, +1C/-1C, 100% depth; 400 at +1C/-3C |
| SA107; 32 | 450 at 0.1C discharge | 1C | 0.5C | 125 cycles, +0.2C/-0.2C, 100% depth; preliminary |

These figures illustrate why the highest Wh/kg entry is not automatically the best candidate. Cycling conditions differ, and the SA504 figures do not establish its life under repeated maximum-rate charging. Pouch mechanics and cooling still require validation.

The screening recommendation is to compare **M65A, SA02 and SA504**, using P50B/P60C as power-focused controls. We do not yet have evidence to call any of them a qualified motorcycle cell.

## 5. Does an improved cell actually close the weight budget?

The following calculations apply 80% cell mass fraction to several disclosed cell densities. They assume the ambitious CdA 0.30 case requiring 25.2 kWh, 90 kg outside the pack, and a new battery. They do not apply power, charging, cost, availability or life qualification filters.

| Cell density used | Assumed complete-pack density | Bike mass for the modeled 200-mile trip |
|---|---:|---:|
| 265 Wh/kg | 212 Wh/kg | 461 lb |
| 314 Wh/kg | 251 Wh/kg | 420 lb |
| 340 Wh/kg | 272 Wh/kg | 403 lb |
| 375 Wh/kg | 300 Wh/kg | 384 lb |
| 390 Wh/kg | 312 Wh/kg | 377 lb |
| 450 Wh/kg | 360 Wh/kg | 353 lb |

Cases exceeding 400 pounds fail the budget. Their mass figures hold the original road load fixed; a heavier finished bike would need slightly more energy than shown. The 450 case illustrates mass arithmetic only, not a suitable cell choice.

At 85% cell mass fraction, a 340 Wh/kg cell produces a nominal 289 Wh/kg pack. In the low-drag scenario, the calculation is approximately **87.3 kg pack + 90 kg other components = 391 lb**. That is a plausible research hypothesis to investigate, not proof of feasibility. There is little room for underestimated hardware, weather or aging.

The middle aerodynamic case remains harder: even a 390 Wh/kg cell at 85% cell mass fraction yields only 331.5 Wh/kg at pack level, below the required 348. We need better integration, lower non-pack mass, less drag or better cells in combination.

Run [battery-screening.ps1](battery-screening.ps1) to reproduce 72 sensitivity cases in [battery-screening-results.csv](battery-screening-results.csv). The screening arithmetic was executed and checked; this is not an electrochemical simulation.

Volume needs its own budget. As an illustration, starting from the SA504's published 860 Wh/L and assuming cells occupy 70% of the complete enclosure volume gives about 602 Wh/L at pack level. The 25.2 kWh case would then occupy about **42 liters**; the 31.8 kWh case about **53 liters**. This is a packaging sensitivity, not a layout: the source measures cell volume at 30% charge, and actual swelling, compression and clearances must be accommodated. A mass-efficient pack can still be too wide, tall or awkwardly shaped for the bike.

## 6. The underlying limits, and what can improve

### Electrode chemistry: higher capacity is not a whole-battery multiplier

Silicon can store much more lithium per gram than graphite, but it can expand by roughly 300% during lithiation. Expansion can fracture particles and disrupt their electrical connections. New surfaces consume more lithium and electrolyte as the protective interphase reforms. Material architecture, binders, coatings and electrolyte chemistry must work together to control these effects. [DOE silicon-anode explanation](https://www.energy.gov/cmei/success-stories/articles/eere-success-story-battery-company-puts-new-nanowire-technology)

Replacing graphite does not multiply whole-cell energy by silicon's capacity advantage: the positive electrode, electrolyte, current collectors and package remain. High-nickel cathodes and silicon-containing anodes are a relevant route to higher cell energy, but actual cell construction determines the result. [Natural Resources Canada battery benchmarking](https://natural-resources.canada.ca/funding-partnerships/benchmarking-canadian-battery-ecosystem)

**Our opportunity:** select and manage a proven silicon-containing cell, then potentially work with a supplier on an application-specific version. We cannot turn an existing sealed graphite cell into a silicon cell through software or pack wiring.

### Electrode thickness: range competes with fast charging

Thicker electrodes can increase the proportion of active material relative to foil and separator, improving specific energy. But they lengthen transport paths and increase concentration gradients. At high charge rates, lithium may deposit as metal rather than entering the anode as intended. Electrode architecture must balance energy and charge capability. [Quarti et al., electrode design study](https://doi.org/10.1002/elsa.202100161), [Berkeley Lab fast-charge research](https://batterygroup.lbl.gov/fast-charge)

Research directions include lower-tortuosity electrode structures, channels through thick electrodes, improved electrolytes and particle designs. These are genuine cell-manufacturing changes. They cannot be implemented merely by commanding more current from a charger. [NREL electrode-architecture research presentation](https://www.nrel.gov/docs/fy23osti/82342.pdf)

**Our opportunity:** avoid paying a mass penalty for extreme discharge capability the bike does not need, while retaining the charging and low-charge power it does need. Supplier electrode optimization may be useful after measured mission data establish that tradeoff.

### Thermal behavior: a charging stop is a different operating condition

Electrical resistance produces heat, and electrochemical heat also matters. Temperature differences across a pack can limit performance even when its average temperature appears acceptable. Thermal characterization at cell and module levels is necessary to size cooling. [National-laboratory thermal characterization research](https://research-hub.nlr.gov/en/publications/li-ion-battery-thermal-characterization-for-thermal-management-de/)

For Bavuso, moving at highway speed and sitting still at a charging station present different cooling conditions. My design recommendation is to compare liquid cold plates or other conductive cooling with a forced-air heat-rejection system, including its mass and electrical demand. Do not assume a road-speed air stream will exist during a fast charge.

Preconditioning and charge control should follow measured limits for the selected cell. Heating can improve charging kinetics, but excessive temperature also accelerates degradation. The correct temperature strategy is chemistry- and usage-dependent; 'keep it as cold as possible' is not a sufficient specification.

### Aging and battery management: useful optimization, bounded gains

An aging-aware BMS can estimate state of charge, state of health, available power and thermal limits more accurately. Balancing can recover energy stranded by unequal group charge levels, but cannot recreate lost active material or make a genuinely smaller-capacity group hold more energy.

A 2026 University of Michigan study found that silicon/graphite behavior and its vulnerable charge threshold changed with aging; it proposed adaptive diagnostics and thermal management. The reported approach is best suited to lower-power charging, so it is a research lead, not evidence that we can fast-charge a motorcycle twice as quickly or double its range. [Michigan study explanation](https://news.engin.umich.edu/2026/07/smarter-diagnostics-could-extend-the-lives-of-silicon-ev-batteries/)

Increasing our assumed available-energy fraction from 90% to 95% increases modeled range by only **5.6%**. Removing reserve is therefore insufficient to close a large energy gap, and may trade away longevity or operating margin. We should measure usable energy rather than assume that a large software unlock exists.

### Mechanical integration: remove duplicated mass, account for the replacement structure

A structural enclosure could share loads with the chassis, reducing duplicated components. But any claimed savings must include the extra enclosure strength, cell protection and changed service requirements. The cells themselves should not be assumed to carry chassis loads. Never credit the same structural mass reduction to both the pack and frame budgets.

Cylindrical cells offer many small building blocks and mechanically defined cans. Pouches can offer efficient shapes and fewer large connections, but require support, swelling allowance and often controlled compression. Neither format wins automatically. Compare complete installed assemblies in the actual bike envelope, including thermal paths, tabs, clearances and protection.

## 7. Power is probably easier than energy; charging may be the deciding tradeoff

At 70 mph, the low-drag model consumes about 7.9 kW from a 25.2 kWh nominal battery. The middle case consumes 10.0 kW from 31.8 kWh. Both correspond to an energy-based load ratio of approximately 0.315 per hour. At 125 mph, the three aerodynamic cases require about 38-62 kW to hold speed in still air, or roughly 1.5-1.6 times their respective nominal kWh capacities per hour.

These ratios are useful first screens, not exact cell-current C-rates: voltage changes with charge state and load. Acceleration, low-charge voltage sag, cold conditions, gearing and thermal endurance need additional assessment. Nevertheless, they show why a range-sized pack may not need the most extreme racing discharge cell. A 2-3C-capable energy-focused cell is worth screening against the actual power trace.

C-rate is defined by current relative to amp-hour capacity: 1C is 6.5 A for a 6.5 Ah cell. At nominal voltage, 1C is approximately 25 kW for a 25 kWh pack. Charging and discharging limits are separate.

For the low-drag 25.2 kWh case, replenishing 10-80% represents approximately 17.7 kWh:

| Illustrative charging stop | Ideal average battery power | Energy-equivalent rate |
|---|---:|---:|
| 30 minutes | 35 kW | 1.4C |
| 20 minutes | 53 kW | 2.1C |
| 10 minutes | 106 kW | 4.2C |

These are energy/time calculations without losses or taper, not charge-time predictions. Actual constant-current C-rates and energy rates differ with voltage. A 2C current rating does not guarantee a 20-minute 10-80% session. The owner has not selected a charging-time target; these examples expose its consequences.

## 8. Tesla compatibility and voltage architecture

Tesla distinguishes supported non-Tesla vehicles, accessible sites and connector arrangements. Adding a NACS-shaped inlet does not establish network access, protocol interoperability or battery compatibility. Tesla Superchargers and Tesla AC charging equipment also impose different vehicle-side requirements. [Tesla non-Tesla Supercharging support](https://www.tesla.com/support/charging/supercharging-other-evs), [Tesla NACS specification announcement](https://www.tesla.com/blog/opening-north-american-charging-system)

The pack must be considered alongside the intended stations' supported output-voltage range, communication, charging controls and current limits. A low-voltage pack may require additional power conversion for particular stations. We have not verified station support for a Bavuso motorcycle, and this report does not claim access.

Study an automotive-like voltage architecture rather than choosing it solely from existing motorcycle convention. As simple arithmetic, 50 kW requires 125 A at 400 V, or 62.5 A at 800 V. Higher voltage can reduce current in external cables and some associated losses. But rearranging the same cells into more series groups does not increase their total stored energy or inherently reduce per-cell heating at equal total power. Voltage is an integration choice, not a battery-density breakthrough.

My starting recommendation is to compare a roughly 400 V architecture with alternatives using actual charging hardware and cell configurations. That is an investigation direction, not an approved pack voltage or station-compatibility conclusion.

## 9. Which chemistry developments matter to us?

| Direction | Assessment for Bavuso |
|---|---|
| High-energy nickel-based lithium-ion, including silicon blends | Most relevant near-term development path; screen specific cells |
| LFP/LMFP | Worth a cost/life reference, but density is a serious obstacle under our mass/range constraint |
| Sodium-ion | Attractive for other priorities; current disclosed density is poorly matched to this particular lightweight long-range bike |
| Lithium-metal / solid-state | Serious development path; require full-cell, pack, lifetime and supply evidence |
| Lithium-sulfur | Longer-term research track; practical full-cell durability and packaging remain essential questions |

For scale, CATL disclosed 175 Wh/kg for its Naxtra sodium-ion product. Farasis's cell portfolio lists up to 240 Wh/kg for LFP/LMFP and up to 380 Wh/kg for its highest-performance NCM tier. Farasis's tier headline is not an individually qualified cell with all relevant specifications. [CATL Naxtra](https://www.catl.com/en/news/6401.html), [Farasis cell portfolio](https://www.farasis-energy.com/en/products/cells/)

Lithium-metal and solid-state are real research programs, not automatic answers. Stellantis reported validation of Factorial's 375 Wh/kg, 77 Ah cells, over 600 cycles and 15-90% charging in 18 minutes, while describing an automotive demonstration program. These are OEM/supplier-reported results, not evidence that a small motorcycle project can buy a qualified pack today. [Stellantis/Factorial announcement](https://www.media.stellantis.com/em-en/corporate/press/stellantis-and-factorial-energy-reach-key-milestone-in-solid-state-battery-development)

QuantumScape's published 2024 QSE-5 B-sample was 301 Wh/kg and 844 Wh/L, illustrating why 'solid-state' does not automatically imply 500 Wh/kg. Its disclosed measurement conditions included C/5 discharge at 25°C and specific packaging/pressure conditions. Ducati subsequently demonstrated a modified V21L with QuantumScape cells in 2025. That is important motorcycle prior art, but not a production road-bike specification. [QuantumScape B-sample disclosure](https://www.quantumscape.com/a-first-look-at-the-qse-5-b-sample/), [Ducati research announcement](https://www.ducati.com/us/en/news/ducati-s-electric-research-continues-with-the-v21l-prototype-and-solid-state-batteries)

Amprius announced a 500 Wh/kg SiCore platform in September 2026 with commercial availability expected in Q4 2026, optimized for low-rate aviation uses. The release is a development/supply expectation, not proof of our required combination of motorcycle power, charge speed and durability. [September 2026 announcement](https://ir.amprius.com/news-events/press-releases/detail/174/amprius-introduces-sicore500-high-energy-density-cells-for-unmanned-aviation)

For lithium-sulfur, researchers must address sulfur loading, lean electrolyte, shuttle effects and cycle life under practical conditions. High active-material energy alone cannot establish a competitive complete pack. [PNNL/DOE practical Li-S research](https://www1.eere.energy.gov/vehiclesandfuels/downloads/2024_AMR/BAT282_Lu_2024_p.pdf)

## 10. What laptop-based work can accomplish

We can make a serious start without manufacturing a new cell:

1. Build a mission profile with 70 mph range operation, 77 mph design operation, acceleration, 125+ mph capability and representative ambient conditions. Determine actual current and cooling requirements for candidate capacities and voltages.
2. Replace generic cell ratings with measured voltage, resistance, capacity, thermal and aging maps. Model cell-to-cell variability and low-charge power limitations.
3. Design candidate pack layouts and weigh all their parts, then compare cylindrical and pouch options in the bike envelope.
4. Model charge sessions with realistic taper and stationary cooling. Compare charging-time choices without changing the owner's range, speed or mass goals.
5. Plan a small-cell and submodule test program through an appropriately equipped laboratory to validate the models before a complete traction pack is built.

PyBaMM provides physics-based battery models and thermal/degradation capabilities; Argonne's BatPaC supports bottom-up battery design/cost tradeoffs. They are useful tools, but uncalibrated parameters cannot validate an unfamiliar proprietary cell. BatPaC's mature high-volume cost assumptions also do not represent a custom first prototype. Neither tool was installed or run for this report. [PyBaMM project](https://github.com/pybamm-team/PyBaMM), [Argonne BatPaC](https://www.anl.gov/partnerships/batpac-battery-manufacturing-cost-estimation)

True cell development would additionally require electrochemical expertise, electrode fabrication, controlled assembly, formation, characterization, repeatability and scale-up. AI can help search materials, optimize models and prioritize experiments, but cannot establish a chemistry breakthrough without those experiments.

## 11. Recommended next engineering decision

Pursue two pack studies before choosing a chemistry or buying cells:

- **Conventional reference:** an M65A-class cylindrical design, with conservative energy and mass data, to establish a credible baseline.
- **Higher-energy candidate:** an SA504-class pouch design, with SA02 as a more balanced comparison, to see whether real cooling, mechanics, life and sourcing preserve its mass advantage.

First-pass research objective: investigate roughly **25-27 kWh nominal and 280-300+ Wh/kg at complete-pack level**, coupled to the ambitious low-drag vehicle case. These are screening targets inferred from the model, not new owner requirements or selected specifications. The middle-drag design needs a materially stronger battery result.

For each candidate, obtain the full cell specification and clarification of energy at relevant rates, DC resistance versus charge/temperature, continuous and pulse current limits, charge curves, swelling/compression requirements, thermal properties, cycle and calendar life, dimensional tolerances, supply terms and cost. Maximum-rate performance and long-life performance must be demonstrated for the same cell and use profile.

The valuable question is now specific: **can an integrated pack preserve enough of a suitable high-energy cell's advantage to deliver at least about 276 Wh/kg, with the required power and charging behavior, while the rest of the motorcycle meets its mass and aerodynamic assumptions?** That is a testable engineering program. We have promising candidates and a quantitative target, but not a qualified battery solution yet.

Cost remains unresolved. Reducing the required kWh reduces the amount of cell material and hardware we need, but a premium high-energy cell may cost more per kWh. The relevant comparison includes cells, pack parts, assembly, development, testing and expected replacements. We should compare quoted prototype and volume costs separately; a mass-market automotive $/kWh figure is not a price for a small custom motorcycle pack.
