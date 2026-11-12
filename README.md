# Bavuso Motors

An electric motorcycle project aiming for long range, strong performance, practical charging, and a comfortable, minimal design with broad appeal—the Tesla of motorcycles.

## Initial design goals

1. **Range:** 200 miles on a charge, using 70 mph as the baseline for highway range calculations.
2. **Top speed:** 125+ mph.
3. **Charging:** Compatible with Tesla charging stations, so riders can travel farther from home.
4. **Weight:** Prefer under 400 pounds for the complete motorcycle, including its battery. Weight is the first requirement the owner would consider relaxing slightly if necessary to preserve the others; no revised maximum has been agreed.
5. **Comfort and design:** Comfortable on the highway, with 77 mph as the expected speed for aerodynamic, comfort, and wind-stability design work. Confident handling in gusts and crosswinds without becoming a big, bulky motorcycle. Cool, minimal styling designed to work for a broad range of riders.

These are development targets, not validated specifications. The 200-mile range target and 125+ mph top-speed target are separate requirements; sustained range at top speed has not been specified.

## Core challenge

Investigate battery size, weight, cost, energy storage, and power delivery. Use scientific research, calculations, and testing to determine what can meet the goals together.

## Engineering work

- **Start here: [engineering development package B0](documentation/README.md).** Current product/system definitions, component and interface registers, packaging conflict study, verification and manufacturing-release requirements. It supersedes earlier concept recommendations where revisions conflict. It is not a build release.
- **[Connected free CAD studio](documentation/cad-studio.md):** FreeCAD 1.1.4 installed locally and tested through its Python API. Open `Open Bavuso CAD.cmd` for the native reservation model. The model is editable engineering geometry with known unresolved conflicts.

- [Competitor landscape (2026-10-30)](research/competitor-landscape-2026-10-30.md): who is closest to Bavuso (Verge TS Pro is the nearest), their specs, prices, charging and company status, and what it means for the goals. Desk research from public sources; many figures unverified.
- [Product, brand and design research](research/design-strategy.md): market references, rider experience, mechanical design constraints, three design territories and the first drafting brief. Recommendations remain open for owner direction.
- [Engineering handoff v0.1](engineering-handoff.md): component-by-component challenge, proposed specifications, packaging reservations, drive sizing, complete mass allocation, and validation gates. This is the current concept baseline; it does not establish that all goals have been met.
- [Designer brief](designer-brief.md): compact engineering constraints for owner-led shape and rider-layout work.
- Reproduce the handoff calculations with `./research/engineering-baseline.ps1`; exports include the mass budget, 25 performance scenarios and a summary JSON.
- [Charging architecture study](research/charging-architecture.md): NACS/DC charging direction, Tesla access distinction, electrical pack reference, component candidates, and revised weight sensitivities.
- [Working design direction](design-direction.md): preferred architecture, two active battery-size variations, and the remaining decisions that determine the final configuration.
- Reproduce those variations with `./research/design-variants.ps1`. These calculations account for each candidate's estimated bike mass.
- [Battery technology deep dive](research/battery-deep-dive.md): cell candidates, physical limits, charging and lifetime tradeoffs, and optimization opportunities for Bavuso.
- Reproduce battery mass/integration sensitivity calculations with `./research/battery-screening.ps1`, after running the range model.
- [First range and weight budget](research/range-weight-budget.md): a calculation-based feasibility study, with assumptions separated from the goals.
- Reproduce the scenario calculations with `./research/range-weight-model.ps1` in PowerShell. Results are saved to `research/range-weight-scenarios.csv`.

## Big-picture engineering questions

- How do riding speed, rider posture, and weather affect the battery needed for 200 miles? Evaluate scenarios without replacing the owner's goals with a new range requirement.
- What battery energy and power would those conditions require, and what weight and cost budget would remain for the rest of the motorcycle?
- What does Tesla charging compatibility require, including station access, connector, charging protocol, electrical architecture, and thermal management?
- How should rider fit, comfort, aerodynamics, and styling work together?
- What existing motorcycles and battery technologies should we benchmark before choosing an architecture?
- What calculations, simulations, and experiments would establish feasibility before building a rideable prototype?

## Project status

Engineering development around the owner's black/silver/tan appearance references. The 30.056 kWh energy reference remains approximately 433 lb before allowance / 446 lb with it. A new 26.299 kWh aero-led alternative is quantified in the B0 package, but its assumed low drag and mass integration are unproven. Current EMRAX v1.7 ratings supersede the older handoff's motor ratings; two windings require mapped comparison. FreeCAD is now installed and a native reservation model/export has been tested; five conservative envelope conflicts remain in that first coordinate study. Under 400 lb remains the preferred owner goal. Supplier qualification, detailed CAD/drawings, physical tests and Tesla access remain open. No vehicle parts have been purchased and no build release exists.
