# Bavuso Motors: working design direction

Date: October 25, 2026, US Central. Prepared by Codex (GPT-6 family).

## Owner priorities

Keep the existing goals: 200 miles using 70 mph as the highway range baseline; 125+ mph top speed; Tesla charging compatibility; preferably under 400 pounds; and comfortable, confident highway riding with minimal styling. Use 77 mph for comfort, aerodynamics and wind-stability design work.

**Weight is the first requirement the owner would consider relaxing slightly to preserve the others.** Under 400 pounds remains the preferred target. No revised weight ceiling is authorized, and the owner's willingness to consider a slight increase does not establish acceptance of 440 or 460 pounds. Weight and range figures below are engineering scenarios, not agreed production specifications.

## Preferred concept

**Current follow-on:** [engineering handoff v0.1](engineering-handoff.md) replaces the aggregate mass placeholders for current decisions with a component allocation of approximately 433 lb before contingency / 446 lb with allowance. It also identifies a mathematical lightweight target of approximately 396 lb before allowance / 407 lb with it, requiring unproven pack and non-pack improvements. The earlier 410 lb and 420–428 lb figures below are historical sensitivities, not the current complete allocation or accepted owner specifications.

Follow-on work: the [charging architecture study](research/charging-architecture.md) narrows the electrical reference to about 30 kWh at 340 V nominal / 420 V full charge, with standards-based DC charging and separate onboard AC charging. It identifies an approximately 420–428 lb mass sensitivity using typical cell mass and a revised charging/cooling allowance; the earlier 410 lb figure below remains the original, unvalidated reference. Tesla network access remains unresolved.

Proceed with a **compact electric road motorcycle with aerodynamic bodywork, a natural highway riding posture, and an approximately 30 kWh high-energy pouch-cell battery**. Keep a 28 kWh variation open to pursue the original weight preference.

This narrows the work from a broad chemistry search to an integrated vehicle concept. The unresolved questions should determine which of these two sizes survives. They should not automatically reopen every chemistry and vehicle architecture considered earlier.

| Area | Preferred working direction | What remains open |
|---|---|---|
| Battery | High-energy nickel-based lithium-ion pouch cells; SA504-class as the lead reference | Exact cell, supply, price, usable energy and qualification |
| Capacity | Approximately 30 kWh nominal | 28 kWh lighter variation; final discrete cell configuration |
| Electrical architecture | Investigate roughly 400 V class with DC charging | Exact series count and voltage window, station interoperability and access |
| Cooling | Study liquid/conductive cell cooling with heat rejection that works while stationary | Required hardware, temperature control, parasitic load and mass |
| Drive | Single motor with fixed reduction as the starting architecture | Motor/inverter, ratio, final drive, peak and continuous capability |
| Form | Compact aerodynamic bodywork around a comfortable rider; avoid bulky touring proportions | Actual dimensions, rider accommodation, drag, buffeting and crosswind behavior |
| Weight | Preserve the under-400 lb ambition; examine a slight overrun for the preferred capacity | Complete bill of materials, contingency and whether any concession is justified |

The SA504 reference is based on manufacturer-disclosed 390 Wh/kg, 6C continuous discharge and 2C maximum charge. Its published 500-cycle result uses +1C/-1C, not repeated maximum charging. It is a promising screening candidate, not a qualified or secured supply. [Amprius Q3 2026 catalog, PDF page 52](https://amprius.com/documents/Amprius_Product_Catalog.pdf)

Tesla compatibility remains a goal requiring an actual access/interoperability path, not merely a connector. Tesla identifies different site categories and manufacturer access arrangements; the current support page does not establish Bavuso access. Investigate this before committing the pack voltage. [Tesla support](https://www.tesla.com/support/charging/supercharging-other-evs)

## Two active variations

The following model uses **312 Wh/kg nominal at complete-pack level**, derived from a 390 Wh/kg cell and 80% cell mass fraction. It assumes 90 kg / 198 lb for everything outside the pack, 90 kg rider plus gear, 90% available trip energy, 90% drivetrain efficiency, 300 W auxiliaries, level road and still air. These are the same screening assumptions as the research, not verified component performance.

Unlike the earlier fixed-400 lb screening table, these calculations use each candidate's resulting bike mass in rolling resistance. No extra engineering contingency is included.

| Active variation | Nominal / available energy | Modeled complete bike | Range at 70 mph, CdA 0.33 | Range at 70 mph, CdA 0.35 |
|---|---|---:|---:|---:|
| **Preferred: 30 kWh** | 30 / 27 kWh | **410 lb** | 220 mi | 210 mi |
| **Lighter: 28 kWh** | 28 / 25.2 kWh | **396 lb** | 206 mi | 196 mi |

These drag areas are targets to investigate, not measured results for a comfortable Bavuso. For context, the previously surveyed wind-tunnel data measured 0.347 m² for a tucked rider on an Energica and 0.500 m² upright. Delivering 0.33-0.35 with comfortable ergonomics is a substantial open challenge. [Warwick research, Table II](https://wrap.warwick.ac.uk/id/eprint/180779/1/WRAP-Effect-rider-position-energy-consumption-23.pdf)

The 30 kWh candidate provides roughly 180 miles at 77 mph at CdA 0.35. That does not change the agreed 70 mph range baseline. At CdA 0.40, the same candidate falls to about 188 miles at 70 mph, so it does not meet the range target. Its modeled 125 mph holding power at CdA 0.35 is about 44 kW at the battery; motor speed, acceleration and thermal endurance still need separate validation.

Our reason for favoring 30 kWh is additional energy margin for a modest mass increase: about 14 lb versus the 28 kWh version under the same assumptions. About 410 lb is 2.6% above the original 400 lb boundary, **before contingency**. It is an example to evaluate under the owner's stated flexibility, not a newly approved weight requirement. The 28 kWh option remains viable if the complete parts budget and comfortable aerodynamics are sufficiently good.

The figures allocate only a 10% combined unavailable-energy/reserve allowance. They do not include separate margins for long-term aging, sustained headwind, cold weather or luggage. Range must ultimately be verified under stated conditions. We should not call 210 modeled miles a robust 200-mile product claim.

## Alternatives retained only as comparisons

With the same 30 kWh capacity and an assumed 80% cell mass fraction:

| Reference | Modeled bike mass | Role |
|---|---:|---|
| 340 Wh/kg balanced pouch class | 442 lb | Comparison if the lead cell fails sourcing or durability screening; requires a fresh tradeoff decision |
| M65A cylindrical, conservative 314 Wh/kg cell calculation | 462 lb | Conventional benchmark; poor fit for a merely slight weight concession at this capacity |

The cylindrical estimate uses 23.4 Wh divided by the M65A datasheet's maximum 74.5 g cell mass. [Molicel datasheet](https://www.molicel.com/cn/wp-content/uploads/Product-Data-Sheet-of-INR-21700-M65A-80153-0.1_250805.pdf)

Neither comparison is an active preferred variant. Solid-state, lithium-sulfur and extreme energy-density aviation cells remain background research rather than prerequisites for the current concept. Choosing a different supplier may become necessary, but the reason should be a demonstrated shortfall in the lead concept.

## Remaining work in decision order

1. **Charging architecture and cell qualification.** Establish a credible Tesla access path, supported station voltage window, charge protocol and required vehicle hardware. In parallel with that engineering work, establish whether the lead cell can meet power, temperature, life and supply requirements. Use published information and prepare supplier questions; no unsolicited outreach is authorized.
2. **Package and aerodynamic concept.** Lay out the 30 kWh pack and the comfortable rider envelope, with a 28 kWh alternative inside the same vehicle concept where possible. Include actual cooling and charging components. Evaluate frontal drag and crosswind forces/moments together. Do not achieve the range target by assuming a racing tuck.
3. **Powertrain and thermal sizing.** Use the resulting drag, mass and voltage to choose motor, inverter and reduction. Evaluate 125+ mph capability separately from the 200-mile trip. Size stationary charging cooling as well as highway cooling. Charging-time alternatives can be compared; no charging-time target has yet been adopted.
4. **Reconcile the complete budget.** Replace every placeholder with component estimates or measurements. Add a visible contingency and then decide whether the 28 kWh version meets the goals, or whether a justified slight weight increase is the better trade. If the gap is materially larger, revisit the concept rather than quietly redefining 'slightly.'

Each step should close an uncertainty in this preferred concept. Battery procurement, a detailed electrical design and physical construction follow qualification and a reconciled package; none has been completed or claimed here.

## Calculation files

Run [research/design-variants.ps1](research/design-variants.ps1) in PowerShell. It writes [research/design-variant-results.csv](research/design-variant-results.csv), including four aerodynamic cases for each active variant and comparison. The mass/range arithmetic is verified, while supplier and physical performance remain unvalidated.
