# Bavuso V1 unit-cost model (current architecture)

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Script: `program/tools/cost-model-v1.py` (run from `v1.0` with FreeCAD python). Data: `program/data/cost-model-v1.csv` (one row per BOM line, then summary, tooling, NRE, sensitivities, levers) and `cost-model-v1.json`. Labels: **quote** = published price, **est** = my estimate, **calc** = computed. **No supplier was contacted and no price here is a quote.** The old `cost-model.csv` ($24.8k) priced an obsolete 490 lb bike and is not used.

## The plain answer

**On my assumptions the V1 costs about $27.8k to build at 10,000 bikes a year, which passes the $32k target (T9) by about $4.2k. At 1,000 a year it is about $36.7k and at 100 a year about $54.1k.** The margin at 10k is real but rests on volume price breaks I have not been quoted, mainly on the cells, motor and inverter. If those three stay at their 1,000-bike prices, the 10k cost is $30.6k, still under $32k.

The three volumes are not equal in confidence. The 10k case is a long way from today (a 10k/yr plant, 11 million cells a year) and every price there is an estimate.

| Per bike, USD | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Cells (1,100 x P60B) | 6,600 | 5,280 | 4,180 |
| Made parts (frame, arm, pack case, body, pulleys) | 5,867 | 3,576 | 2,618 |
| Purchased parts (motor, inverter, running gear, electronics, etc.) | 31,335 | 23,292 | 18,656 |
| **Material** | **43,802** | **32,148** | **25,453** |
| Direct labour (pack + bike) | 2,520 | 1,035 | 446 |
| Plant overhead (60% of labour) | 1,512 | 621 | 267 |
| End-of-line test + cell screening/pack test | 229 | 125 | 68 |
| Inbound logistics and duty | 1,517 | 857 | 571 |
| Scrap and yield loss | 334 | 160 | 82 |
| Warranty reserve | 1,752 | 1,029 | 713 |
| Tooling and capital, amortised over 5 years of volume | 2,468 | 727 | 206 |
| **Unit cost, ex-works** | **54,135** | **36,702** | **27,805** |
| Target T9 (10k) | | | 32,000 |

Unit cost excludes NRE (below), dealer margin, outbound freight and financing. At the $45k MSRP the 10k cost is 62% of MSRP; after a typical dealer or distribution cut the company margin is thin to moderate, not rich. That is my observation, not a model output.

## Verdict table

| Check | Result | Verdict |
|---|---|---|
| T9: $32k at 10k/yr | $27.8k (margin $4.2k) | pass on estimates |
| Same, with cell, motor and inverter prices frozen at 1k-bike level | $30.6k | pass, thin |
| Cells +30% | $29.1k | pass |
| Cells -30% | $26.5k | pass |
| Motor + inverter at volume-supplier prices | $23.9k | pass (sensitivity, not the base) |
| Labour $30 / $65 per hour | $27.5k / $28.3k | labour barely matters at 10k |
| Same at 1k/yr | $36.7k | above $32k; fine, T9 is a 10k target |

## Where the money goes at 10k (per bike)

| Group | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Drive (EMRAX 228, CM200DX, pulleys, belt, yoke) | 12,910 | 9,966 | 8,360 |
| Pack (cells, case, busbars, ribbons, BMS) | 10,037 | 7,619 | 5,934 |
| Electronics, charging, harness | 8,401 | 5,671 | 4,201 |
| Running gear (fork, shock, wheels, tyres, brakes, ABS) | 7,560 | 5,800 | 4,570 |
| Chassis (frame, cast arm, guards) | 2,443 | 1,570 | 1,171 |
| Body | 1,995 | 1,136 | 867 |
| Cooling | 455 | 385 | 350 |

**Motor plus inverter is $8.0k of the $27.8k at 10k, 29% of the cost.** The cells are $4.2k, the whole pack about $5.9k.

## Key inputs and where they come from

| Input | 100 / 1k / 10k | Basis |
|---|---|---|
| P60B cell | $6.00 / 4.80 / 3.80 | est. B2B listings $3.35 to $8.00 (hardware-shortlist.csv); P50B retail $7.50 at 1,000 pieces ([18650batterystore](https://www.18650batterystore.com/products/molicel-21700-p50b-5000mah-50a-battery), [batteryjunction](https://www.batteryjunction.com/molicel-inr21700-p50b)). I could not find a published P60B price. The 10k figure is about $176/kWh and assumes a direct contract; large-cell makers sell near $100-150/kWh but the P60B is a premium high-power cell |
| EMRAX 228 (LV winding) | $6,800 / 5,520 / 4,800 | est. No list price published; shortlist estimate $7,500. Low-volume supplier, so the curve is shallow |
| Cascadia CM200DX | $5,500 / 4,000 / 3,200 | est. A plain CM200 is listed at $7,202 retail ([fuel2electric](https://www.fuel2electric.com/cascadia-motion-cm200-inverter)); the old shortlist's $2,500 looks too low for a one-off, but is plausible for a volume deal |
| Pack case | 8.3 kg 3 mm sheet with 5 mm front wall | calc mass (09-structures.md); est price: sheet plus cut, form, weld, leak test |
| Frame | 25 kg 4130 tube, 14 / 9 / 5.5 h welding, coat | mass from 09-structures.md; price est |
| Swingarm | cast A356-T6, about 3.4 kg: $470 / 150 / 92 | est; sand cast at 100, low-pressure die at 10k |
| Fork, shock, wheels, brakes, ABS | OE-class prices at 10k, 1.3x to 1.7x at lower volume | est, from retail anchors listed in the CSV |
| Electronics | `elec-bom.csv` 10k price x 1.15; HV and LV harness raised to $380 and $320 | est |
| Assembly | bike 38 / 16 / 7.5 h, pack 18 / 7 / 2.4 h at $45/h loaded, plus 60% overhead | est |
| Warranty / logistics / scrap | 4.0 / 3.2 / 2.8% of material; 4.0 / 3.0 / 2.5% of purchased; 4 / 3 / 2% of made parts | est |

The BOM masses sum to about 285 kg, not 240 kg. This follows the current ledger (about 320 kg reconciled, Gate A table) rather than the T1 target, so the cost prices the heavy design as it stands; cutting mass to 240 kg would reduce some made-part cost but I did not credit it.

## One-off tooling and NRE (kept out of unit cost)

| USD | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Tooling and capital (parts tooling plus pack line, assembly line, EOL rig) | 1.23 M | 3.63 M | 10.29 M |
| NRE: engineering, specialists, prototypes, cell life testing, compliance | 8.83 M | 17.30 M | 32.40 M |

Tooling is amortised into unit cost. Largest tooling items at 10k: frame jigs and robot cell $1.0M, body injection and stamping moulds about $0.6M, pack assembly line $3.0M, vehicle assembly line $3.5M, cast arm die $0.2M, pack case weld fixtures $0.35M. NRE is **reused from the base column of `startup-costs.csv` (October study), not re-derived**; it is an order-of-magnitude figure. Over 5 years of volume it would add about $17,700 / $3,460 / $650 per bike at 100 / 1k / 10k. At 100 bikes a year the NRE is larger than the bike's whole unit cost, so V1 only works as a business at real volume or with outside funding.

## Sensitivities (unit cost, USD)

| Case | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Base | 54,135 | 36,702 | 27,805 |
| Cell price -30% | 51,966 | 35,004 | 26,476 |
| Cell price +30% | 56,303 | 38,400 | 29,134 |
| Motor + inverter at volume-supplier pricing (10k: motor $2,800, inverter $1,500) | 50,031 | 32,964 | 23,909 |
| Cells, motor, inverter frozen at 1k prices at 10k | 54,135 | 36,702 | 30,572 |
| Labour $30/h | 52,477 | 35,957 | 27,453 |
| Labour $65/h | 56,344 | 37,696 | 28,275 |
| Cells -30% and volume-supplier motor/inverter | 47,862 | 31,266 | 22,580 |

EMRAX and Cascadia are low-volume specialists. The base case keeps them at specialist prices ($8.0k together at 10k). The volume-supplier case (a YASA, Bosch or automotive-inverter class supplier) is a sensitivity only: it would save about $3.9k per bike but needs a different motor and inverter than the ones designed in, with new integration work.

## Cost-down levers at 10k

The target is met, so these are headroom rather than rescue, in $ per bike at 10k (computed by the script):

| Lever | Saving |
|---|---:|
| Motor to volume axial-flux supplier ($4,800 to $2,800) | 2,106 |
| Inverter to automotive volume supplier ($3,200 to $1,500) | 1,790 |
| Cells to $3.10 through a direct contract | 816 |
| Labour $45/h to $30/h | 352 |

Other levers I did not price: removing the SA504 stretch option from consideration (it is unpriced), a 6.6 kW charger is a cost increase (about $350), and cutting mass to the 240 kg target would trim pack case, frame and cell count only if the design changes.

## What this does not prove

- **No price here is a quote.** The cell, motor and inverter volume curves are my estimates. The cell price has no published P60B anchor; EMRAX has no published price; the CM200 retail anchor is for a one-off.
- **Volume assumptions are large.** The 10k case needs about 11 million cells a year, a 10k/yr assembly line and supplier contracts that do not exist today. A buyer of 1,100 cells will not see the 10k price.
- **The BOM is the current design at about 285 kg, not the 240 kg target.** Some lines are group estimates (body panels, electronics) rather than part-by-part drawings.
- **Reused numbers.** NRE comes from the October startup-costs study. Electronics prices come from `elec-bom.csv` with a 15% contingency.
- **Not included:** dealer margin, outbound freight, warranty beyond a percentage reserve, recalls, financing, working capital, facility, software licences, Supercharger network access (no public path, per `07-electrical.md`), certification fees beyond the NRE line, and tariffs beyond the logistics percentage.
- **Cast-arm and frame prices** assume the structures FEA holds. The arm bolt-on boss, the EMRAX yoke approval and the 3 mm versus 5 mm pack-case question are still open in `09-structures.md`; any rework would add cost.
- **Not checked:** an independent should-cost against a teardown of a comparable bike (for example Zero or Energica), which would be the best test of these totals.
