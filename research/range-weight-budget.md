# Bavuso Motors: first range and weight budget

Date: October 25, 2026 (US Central). Prepared by Codex (GPT-6).

## Finding

The original goals remain unchanged: 200-mile range, 125+ mph top speed, Tesla charging compatibility, under 400 pounds, and comfortable highway riding with minimal styling and confident wind response. Full electric propulsion only.

This first calculation identifies a substantial range/weight gap for highway riding using the reference battery assumptions below. It does not establish that the goals are impossible. It identifies what aerodynamic performance and complete-pack energy density would need to improve. The owner has set **70 mph as the range-calculation baseline**, and **77 mph for aerodynamic, comfort, and wind-stability design work**. The other speed cases remain for comparison. A predicted range is not a validated advertising claim.

At 70 mph, a 200-mile trip needs approximately 25-39 kWh nominal across the aerodynamic cases studied. At an assumed complete-pack density of 220 Wh/kg, that means approximately 253-385 pounds of battery, before the rest of the motorcycle. A separate placeholder allowance of 198 pounds for everything outside the pack leaves only about 202 pounds for the pack at the 400-pound ceiling.

The strongest initial research direction is therefore the combination of reduced aerodynamic drag in a comfortable posture, improved battery energy per kilogram, and a light complete vehicle. Increasing battery size alone does not close this budget.

## Evidence versus assumptions

Published evidence:

- Molicel advertises its P50B high-power cell at **260 Wh/kg**. This is bare-cell performance, not the density of a finished motorcycle pack. [Manufacturer announcement](https://www.molicel.com/newsroom/molicel-showcased-groundbreaking-ultra-high-power-cell-inr-21700-p50b-at-ces-2024-redefining-the-ev-hypercar-industry-with-mcmurtry/)
- Enepaq's P50B module datasheet lists **183-226 Wh/kg** at module level; it also requires installation in an enclosure. A module still excludes some complete-vehicle battery equipment. This provides a concrete example of packaging reducing the bare-cell number. [Module datasheet, revision B, September 2025](https://enepaq.com/wp-content/uploads/2025/09/Datasheet_with_P50B_rev_B2025-09-05.pdf)
- Kirca and McGordon's wind-tunnel study measured combined motorcycle-and-rider drag area, CdA, of **0.500 m² upright and 0.347 m² tucked** on an Energica Ego+RS, and **0.569 m² upright and 0.423 m² tucked** on a LiveWire. Those measurements are evidence that posture matters, not measurements of a future Bavuso. [University of Warwick manuscript, Table II](https://wrap.warwick.ac.uk/id/eprint/180779/1/WRAP-Effect-rider-position-energy-consumption-23.pdf)

Study assumptions, all subject to replacement with measurements or supplier evidence:

| Input | Assumption |
|---|---:|
| Motorcycle mass | 400 lb / 181.44 kg, used as a ceiling |
| Rider plus gear | 90 kg / 198 lb, additional to bike mass |
| Air density | 1.225 kg/m³ |
| Rolling resistance coefficient | 0.015 |
| Battery-to-wheel efficiency | 90% |
| Electrical accessories and auxiliaries | 300 W |
| Nominal battery energy available for the trip | 90% |
| Complete-pack energy density reference | 220 Wh/kg |
| Everything outside the battery pack | 90 kg / 198 lb |
| Road and weather | Flat, steady speed, mild conditions, no wind unless stated |

The 90% available-energy factor is a combined unavailable-capacity/reserve allowance. It is not an additional allowance for battery aging. The 220 Wh/kg complete-pack case is an engineering assumption, not a supplier quote or validated design; given the module figures above, it is an aggressive integration assumption for P50B-based hardware.

Aerodynamic scenarios:

- **CdA 0.50 m²:** a useful reference near a measured upright sport-bike case.
- **CdA 0.40 m²:** improved aerodynamics; not yet demonstrated with Bavuso's intended comfortable posture.
- **CdA 0.30 m²:** an ambitious development case, below even the tucked values in the cited study. Achieving it without compromising comfort is unproven.

## Calculation

The standard drag equation is `F_drag = 0.5 × air_density × CdA × air_speed²`. [NASA explanation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/)

The model adds rolling resistance and drivetrain losses:

```text
F_roll = rolling_coefficient × (bike_mass + rider_mass) × gravity
P_battery = (F_drag + F_roll) × ground_speed / efficiency + auxiliary_power
Wh/mile = P_battery_in_watts / ground_speed_in_mph
Nominal_kWh_for_200_miles = Wh/mile × 200 / 1000 / available_fraction
Pack_mass_kg = nominal_kWh × 1000 / complete_pack_Wh_per_kg
```

Ground speed determines miles traveled and mechanical work per second. Air speed determines aerodynamic force. They differ in the headwind case.

Reproduce with [range-weight-model.ps1](range-weight-model.ps1); the complete numeric output is in [range-weight-scenarios.csv](range-weight-scenarios.csv). PowerShell calculations were executed successfully and independently compared with JavaScript calculations. Energy-to-range consistency and increasing consumption with speed were checked.

## Battery needed for 200 miles

Values below are nominal pack capacity, including the 10% combined unavailable-energy/reserve allowance:

| Steady riding speed | CdA 0.30, ambitious | CdA 0.40, improved | CdA 0.50, reference |
|---|---:|---:|---:|
| 55 mph | 17.9 kWh | 22.0 kWh | 26.1 kWh |
| 65 mph | 22.6 kWh | 28.3 kWh | 34.0 kWh |
| **70 mph: range baseline** | **25.2 kWh** | **31.8 kWh** | **38.5 kWh** |
| 75 mph | 28.1 kWh | 35.7 kWh | 43.3 kWh |
| 77 mph: aerodynamic/comfort design speed | 29.3 kWh | 37.3 kWh | 45.3 kWh |

At 70 mph, the estimated consumption is respectively 113, 143, and 173 Wh/mile. At the 220 Wh/kg pack assumption, the battery masses are respectively 253, 319, and 385 pounds. For the same pack, reducing steady speed from 77 to 70 mph increases modeled range by approximately 16-18% across these scenarios.

These battery requirements are calculated at the 400-pound bike ceiling. When the resulting pack plus other parts exceeds that ceiling, the case fails the weight budget. Adding that larger pack to the same chassis would also increase rolling resistance; the table is not a self-consistent specification for a heavier finished bike.

At 55 mph, the ambitious 0.30 case fits this simplified mass/energy budget at about 378 pounds including the placeholder 198-pound non-pack allowance. That does not validate comfort, wind response, top speed, charging hardware, or a real build at that weight. It illustrates the sensitivity to speed and shape.

## Working backward from 400 pounds

The following allowances are planning placeholders, not measured components, selected parts, or a bill of materials:

| Everything outside the pack | Mass allowance |
|---|---:|
| Frame, swingarm, structural hardware | 20 kg |
| Wheels, tires, brakes | 25 kg |
| Suspension and steering | 14 kg |
| Motor, inverter, final drive | 13 kg |
| Bodywork, seat, cockpit | 6 kg |
| Charging hardware, low-voltage equipment, cooling outside pack | 7 kg |
| Other wiring, fittings, fasteners | 5 kg |
| **Total outside pack** | **90 kg / 198 lb** |
| **Pack allowance at 400-pound ceiling** | **91.4 kg / 201.6 lb** |

The pack allowance includes its enclosure, cells, internal connections, BMS, switching/protection and pack thermal hardware; the non-pack rows must avoid counting those twice. These allowances could prove too light, particularly the powertrain and charging/cooling rows. They have no explicit contingency, so a practical design must target below the ceiling.

At 220 Wh/kg that pack holds about **20.1 kWh nominal / 18.1 kWh available**. At 70 mph its modeled range is:

| Aerodynamic case | Range with this pack | Complete-pack density needed for 200 miles at same mass |
|---|---:|---:|
| CdA 0.30 | 160 miles | 276 Wh/kg |
| CdA 0.40 | 126 miles | 348 Wh/kg |
| CdA 0.50 | 105 miles | 421 Wh/kg |

For the middle case, reducing the non-pack allowance to 80 kg lowers the required pack density to approximately 314 Wh/kg; increasing it to 100 kg raises it to approximately 391 Wh/kg. These are sensitivity calculations, not evidence that those vehicle masses can be achieved.

Alternatively, keeping the 220 Wh/kg pack and 90 kg non-pack budget would require approximately **CdA 0.223 m²** for 200 miles at 70 mph under these idealized conditions. That is substantially below the cited production-bike measurements with riders, including their tucked cases. It is a research challenge, not an achieved design.

## Top speed and weather cross-checks

At 125 mph, modeled battery power needed merely to hold speed on level pavement in still air is approximately **38, 50, or 62 kW** for CdA 0.30, 0.40, or 0.50 respectively. This is not motor nameplate power, an acceleration allowance, proof of thermal endurance, or a guarantee of 125+ mph. The selected motor, inverter, gearing and battery must deliver suitable power at the required speed and operating conditions. Aerodynamic behavior at 125 mph also remains unmeasured.

At 70 mph with a 10 mph direct headwind, the middle case rises from 143 to approximately **180 Wh/mile**. The 20.1 kWh pack then provides approximately **101 miles**, versus 126 miles in still air. This calculation addresses headwind energy consumption; it does not assess crosswind handling. The separate 77 mph comfort and stability requirement remains in force.

## Highway comfort and wind stability

Goal 5 is a requirement for relaxed, confident highway riding without a bulky touring-bike shape. It is not a promise of immunity to every gust. Straight-ahead low drag alone cannot establish that behavior. Crosswind research examines lateral forces and rolling/yawing moments, which require separate evaluation. [University of Birmingham research](https://research.birmingham.ac.uk/en/publications/a-numerical-investigation-of-the-flow-around-a-motorbike-when-sub/)

The design work should evaluate the rider and bike together: natural posture, wind pressure and helmet buffeting, bodywork shape under angled wind, weight distribution, steering geometry, tires and suspension. Avoid assuming that simply placing the battery low or adding weight guarantees stability. A successful form must perform in both frontal drag and crosswind response, followed by physical validation.

## Research priorities from this budget

1. **Find a comfortable aerodynamic form.** Compare compact fairing and windscreen concepts with realistic rider sizes and postures. Quantify both drag and crosswind forces/moments before selecting a shape. Do not assume a racing tuck for highway comfort.
2. **Screen actual battery candidates.** Compare complete-pack density, power, fast-charge capability, cycle life, temperature behavior, cost and supplier availability together. Use supplier datasheets and independent evidence; a record cell-energy headline is insufficient to establish motorcycle suitability.
3. **Replace mass placeholders with parts and packaging estimates.** Include Tesla charging requirements and thermal equipment before claiming a weight margin.

This model excludes hills, acceleration cycles, tire/suspension dynamics, rain, cold-weather effects, aging, passengers, luggage, battery voltage sag and power/thermal limits. It does not predict city-cycle range or cost. Charging compatibility is still an unresolved goal; no connector, pack voltage or station access has been selected or validated.
