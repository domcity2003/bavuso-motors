# Convergence study and alternatives

October 25, 2026. Screening calculations, not qualified performance. Reproduce [configuration-trades.csv](configuration-trades.csv) using [the Python model](../tools/build-development-model.py). The 72 cases hold 100 series groups and compare 6–9 parallel cells, three integration assumptions and six drag values. This deliberately isolates the parallel-count lever. It is not an exhaustive chemical, structural or aerodynamic optimization.

## Strongest new path to investigate

Our earlier 30.056 kWh / 433 lb allocation protects energy but misses the preferred mass by about 14.91 kg before allowance. The most useful competing path is **100s7p, 26.299 kWh**, provided comfortable total bike/rider drag is low enough. It keeps the same voltage reference while removing 100 cells. At the old 80% integration and unchanged 99.05 kg outside the pack, it gives approximately **406 lb before allowance / 419 lb with allowance**, with a modelled **208-mile** new-battery result at CdA 0.30. This still does not meet mass.

A more focused target than cutting all nonpack hardware to 88 kg is to investigate **85% cell mass fraction and 95.5 kg outside the pack**. On a common allowance-inclusive mass basis this gives **399.05 lb and 208.6 miles at 70 mph at CdA 0.30**, using typical new-cell energy and the existing availability assumption. Both integration inputs are engineering targets requiring a real weighed component design. Unlike the older aggressive case, it asks for approximately 3.55 kg outside-pack improvement from 99.05 kg, rather than 11.05 kg. It also requires a very tight 12.02 kg noncell pack allocation with the 700 cells. No integration credit is earned until the full enclosure/protection/cooling structure meets that allocation.

The margin does not survive the cell-mass bound alone: 700 cells at +2 g each add **1.4 kg**, producing **402.14 lb** when noncell hardware and the original development allowance stay fixed. At that increased mass and minimum published cell energy, the screening result is approximately **203.7 miles**; the 200-mile CdA boundary is approximately **0.3071 m²**. These are combined mass/energy sensitivity cases, not a probability estimate or full worst-case vehicle qualification. They exclude other adverse conditions such as aging, headwind and cold. The export distinguishes base-mass range, allowance-inclusive range and minimum-energy/maximum-cell-mass range; do not mix their mass bases when reporting a combined result.

For this 7p path the charge-current reference falls from 86.4/172.8 A to 75.6/151.2 A typical/maximum, so low-voltage 50 kW charging cannot be assumed. Maximum published charge-current arithmetic permits only 37.8 kW at the 250 V cell-endpoint sum, before thermal/life/station restrictions. The actual operating floor is unresolved. The 70 kW low-voltage discharge screen is 40 A per cell rather than 35 A at 8p; published discharge capability alone does not qualify heating or aging.

At CdA 0.30, even the smaller pack can model more than 200 miles when new, but the same calculation at 90% SOH falls below 200. If the owner later requires 200 miles after aging, or in a direct headwind, this architecture must be revisited. The model explicitly includes minimum published Wh and health cases instead of concealing that margin.

**Decision rule:** retain 8p as the energy reference and 7p as the leading weight investigation until the comfortable-rider drag and complete installed mass are evidenced. Do not select 7p merely because the model turns green. If physical drag is closer to 0.40–0.50, neither a cosmetic screen change nor optimistic integration closes all goals. The honest choices then involve more effective body/rider airflow control, a different energy source or cell, or an owner-approved product trade.

## Avenue disposition

| Avenue | Current disposition | Evidence that would reopen or close it |
|---|---|---|
| Optimize existing high-energy cells | Lead route | Supply, pack safety/life and integration tests |
| Invent a new chemistry | Research option, no production dependency | Independently reproduced cell performance, manufacturability and qualification |
| Solid state | Monitor | Orderable qualified cell with pack-level advantage |
| LFP | Cost/life reference | Whole-vehicle calculation meeting mass and range at actual energy density |
| Conventional cylindrical | Supply fallback | Qualified supplier plus sufficient system-level mass/volume performance |
| Extreme energy aviation pouch | Not selected on headline density | Road charge/life/fault/mechanical data and supply |
| 100s6p | Lower-mass sensitivity | Comfortable-rider drag sufficiently low at required energy margin |
| 100s7p | Leading lighter investigation | Low drag plus full BOM/mass/thermal and life qualification |
| 100s8p | Current energy reference | Close mass and package while retaining performance |
| 100s9p | Range sensitivity | Additional mass accepted or offset; not baseline |
| Change series count | Open integrated trade | Entire OBC/motor/inverter/station voltage window remains compatible |
| Add DC boost conversion | Only if demonstrated need | Station/drive benefit exceeds converter mass, cost and losses |
| Whole-pack hand swap | Reject at this energy | A practical handling method and interface without unacceptable mass |
| Two smaller service packs | Packaging alternative | Quantified additional cases/interconnects and actual removal benefit |
| Supercapacitor buffer | No demonstrated duty need | Measured cell/power duty limitation that a buffer solves economically |
| Motor MV winding | Current comparison | Loaded low-voltage speed/torque maps and thermal margin |
| Motor LV+100% winding | Co-leading comparison | Supplier maps and inverter phase-current/overspeed compatibility |
| Smaller EMRAX188 | Short-duration speed alternative only | Defined duration duty met under installed thermal conditions |
| Next-generation motor | Active sourcing contingency | Exact drawings/maps/cooling ratings/availability and mass |
| Hub drive | Disfavored for ride/unsprung mass | Measured dynamics and thermal benefit exceeding penalties |
| Two motors/AWD | No demonstrated need | Quantified traction benefit for owner use case worth mass/controls |
| Two-speed gearbox | No demonstrated net benefit | Drive-cycle/mapping gain exceeds mass, shift, reliability cost |
| Belt final drive | Study lead | Supplier-approved tooth count/width, loads, tension and bearing layout |
| Chain final drive | Development ratio tool/fallback | Documented production trade in NVH, maintenance and mass |
| Fully structural cell pack | Do not make cells chassis load path | Structural enclosure qualified independently of pouch cell strength |
| Frame-supported stiff enclosure | Lead structural investigation | Load cases, fatigue, retention, crash and service evidence |
| Carbon main structure | Not default | Whole lifecycle/repair/QA and real mass benefit versus metal |
| Single front rotor | Mass alternative | Complete matched hydraulic system meets stopping/fade duty |
| Dual front rotors | Initial reservation | Complete brake design and measured mass; not blindly copied |
| Battery radiator only | Ambient-limited option | Declared charge curve met in stationary hot conditions |
| Refrigeration/preconditioning | Explicit thermal alternative | Required capacity, package, power and mass justified |
| Upright smaller screen | Appearance baseline, drag unknown | Comfort/drag/moment evidence |
| More complete rider airflow management | High-value aero experiment | Achieve lower drag without unacceptable buffeting/size/handling |
| Active suspension/active aero | No established need | Measured benefit outweighs mass and failure modes |
| Native NACS | Functional lead | Shared AC/DC routing, conformance and real network authorization |
| Adapter-only access claim | Insufficient | Actual accepted vehicle/network compatibility and qualified adapter system |

This is a decision trail, not a claim every possible architecture has been proven inferior. New primary evidence can change a disposition through a documented trade review.

## Study limits

Mass allowance is 5% of noncell mass, retained for comparison, not a statistical confidence bound. The model uses constant rolling resistance and efficiency and does not include exact installed cooling/lighting loads. It uses typical cell mass; published ±2 g per cell implies a nontrivial lot-dependent mass change. The 85% integration target is not a supplier pack. Energy arithmetic does not establish cell usage window, pack compression, internal fault control or top-speed drive capability. Thermal and dynamic constraints are not optimized by this sweep.
