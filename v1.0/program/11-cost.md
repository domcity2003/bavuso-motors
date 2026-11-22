# Bavuso V1 unit-cost model (final parts list, rev E)

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Script: `program/tools/cost-model-v1.py` (run from `v1.0` with FreeCAD python). Data: `program/data/cost-model-v1.csv` (one row per cost line, with the BOM part numbers it prices, then groups, summary, tooling, NRE, sensitivities, levers) and `cost-model-v1.json`. Basis: `program/data/bom-v1-indented.csv`.

**Cost and BOM line up.** Every one of the BOM's level-3 part numbers is priced exactly once (the script stops if one is missed or doubled), and the priced mass is 257.322 kg, the same as the BOM and ledger total. Three small cost lines have no BOM row (belt guard and tensioner, TPMS and switches, consumables; $151 at 10k) and are flagged as allowances.

Labels: **est** = my estimate. **No supplier was contacted and no price here is a quote.** This replaces my earlier run, which priced the pre-final parts list ($27.8k at 10k) and the obsolete `cost-model.csv` ($24.8k).

## The plain answer

**The final V1 costs about $29.5k to build at 10,000 bikes a year, which passes the $32k target (T9) by about $2.5k. At 1,000 a year it is about $39.3k and at 100 a year about $58.0k.** The margin is smaller than before (it was $4.2k) because the final parts list added carbon wheels, a steel pivot yoke with cast nodes, a cast swingarm hub carrier, cell holders and a semi-active steering damper.

The pass depends on volume price breaks I have not been quoted. **If the cells, motor and inverter stay at their 1,000-bike prices at 10k, the cost is $32.3k, which just misses T9.** The carbon wheels alone cost about $1.1k per bike over forged ones at 10k.

| Per bike, USD | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Cells (1,100 x P60B) | 6,600 | 5,280 | 4,180 |
| Made parts (frame and yoke, cast arm, pack case, body, pulleys) | 4,934 | 3,018 | 2,234 |
| Purchased parts | 35,845 | 26,263 | 20,652 |
| **Material** | **47,379** | **34,561** | **27,066** |
| Direct labour (pack + bike) | 2,520 | 1,035 | 446 |
| Plant overhead (60% of labour) | 1,512 | 621 | 267 |
| End-of-line test, cell screening, pack test | 229 | 125 | 68 |
| Inbound logistics and duty | 1,698 | 946 | 621 |
| Scrap and yield loss | 296 | 143 | 74 |
| Warranty reserve | 1,895 | 1,106 | 758 |
| Tooling and capital, amortised over 5 years of volume | 2,508 | 735 | 207 |
| **Unit cost, ex-works** | **58,038** | **39,273** | **29,507** |
| Target T9 (10k) | | | 32,000 |

Unit cost excludes NRE, dealer margin, outbound freight and financing. At the $45k MSRP the 10k cost is 66% of MSRP, so the margin after a dealer or distribution cut is thin. That is my observation, not a model output.

## Verdict table

| Check | 10k result | Verdict |
|---|---:|---|
| T9: $32k at 10k/yr | $29.5k (margin $2.5k) | pass on estimates |
| Cells, motor, inverter frozen at 1k-bike prices | $32.3k | **fails by $0.3k** |
| Cells +30% / -30% | $30.8k / $28.2k | pass |
| Motor + inverter at volume-supplier prices (sensitivity, not base) | $25.6k | pass |
| Forged instead of carbon wheels | $28.4k | pass |
| Carbon-wheel OEM price +50% | $30.6k | pass |
| Labour $30/h / $65/h | $29.2k / $30.0k | pass; labour barely matters at 10k |
| Same bike at 1k/yr | $39.3k | above $32k; T9 is a 10k target |

## Where the money goes (per bike)

| Group | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Drive (EMRAX 228, CM200DX, 8M pulleys, belt, carrier) | 12,711 | 9,817 | 8,237 |
| Running gear (fork, shock, carbon wheels, brakes, ABS, damper, controls) | 10,658 | 7,816 | 5,857 |
| Pack (cells, case, internals, holders, BMS) | 10,427 | 7,839 | 6,079 |
| Electronics, charging, wiring | 8,810 | 6,003 | 4,494 |
| Chassis (frame, yoke, nodes, cast arm, guards) | 2,824 | 1,855 | 1,411 |
| Body | 1,309 | 705 | 520 |
| Cooling | 412 | 349 | 317 |
| Allowances with no BOM line | 228 | 178 | 151 |

Motor plus inverter is $8.0k of the $29.5k at 10k (27%). The carbon wheel set is $2.1k.

## Key inputs

| Input | 100 / 1k / 10k | Basis |
|---|---|---|
| P60B cell | $6.00 / 4.80 / 3.80 | est. B2B listings $3.35 to $8.00; P50B retail $7.50 at 1,000 ([batteryjunction](https://www.batteryjunction.com/molicel-inr21700-p50b), [18650batterystore](https://www.18650batterystore.com/products/molicel-21700-p50b-5000mah-50a-battery)). No published P60B price. 10k is about $176/kWh and needs a direct contract |
| EMRAX 228 (LV winding) | $6,800 / 5,520 / 4,800 | est. No list price published; low-volume supplier |
| Cascadia CM200DX | $5,500 / 4,000 / 3,200 | est. Plain CM200 listed at $7,202 retail ([fuel2electric](https://www.fuel2electric.com/cascadia-motion-cm200-inverter)) |
| Carbon wheels (BST class) | $4,410 / 3,045 / 2,100 | est. About $4.5k retail set (+$2.7k over forged); OEM price at 10k assumed 47% of retail |
| Frame + steel pivot yoke | 4130 tube, 25 kg class, weld hours scaled by mass; cast steel nodes about $32 each at 10k | est from `09-structures.md` |
| Cast swingarm and hub carrier | arm $470 / 150 / 92; carrier $62 at 10k | est; sand cast at 100/yr, low-pressure die at 10k |
| Pivot bearings (2 x 32012) | $96 at 10k incl. seals | est |
| Cell holders (3.1 kg PA66-GF30) | $42 at 10k, two large tools | est |
| Front discs 320 mm, Stylema calipers | $150 pair, $460 pair at 10k | est from retail anchors |
| Semi-active steering damper | $320 at 10k | est (Ohlins retail about $600) |
| Electronics | `elec-bom.csv` 10k price x 1.15; 6.6 kW BROGEN charger $700 | est |
| Assembly | bike 38 / 16 / 7.5 h, pack 18 / 7 / 2.4 h at $45/h plus 60% overhead | est |
| Warranty / logistics / scrap | 4.0 / 3.2 / 2.8% of material; 4.0 / 3.0 / 2.5% of purchased; 4 / 3 / 2% of made | est |

Every line's price source or basis, with URLs where I have them, is in the `source_or_basis` column of the CSV.

## One-off tooling and NRE (kept out of unit cost)

| USD | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Tooling and capital (parts tooling plus pack line, assembly line, EOL rig) | 1.25 M | 3.67 M | 10.36 M |
| NRE: engineering, specialists, prototypes, cell life, compliance | 8.83 M | 17.30 M | 32.40 M |

Tooling is amortised into unit cost. Largest 10k items: pack line $3.0M, vehicle line $3.5M, frame jigs and robot cell $1.0M, body and holder tools about $0.6M, pack case fixtures $0.35M, cast arm die $0.21M. NRE is **reused from the base column of `startup-costs.csv` (October study), not re-derived**. Over 5 years of volume it adds about $17,700 / $3,460 / $650 per bike at 100 / 1k / 10k.

## Sensitivities (unit cost, USD)

| Case | 100/yr | 1,000/yr | 10,000/yr |
|---|---:|---:|---:|
| Base | 58,038 | 39,273 | 29,507 |
| Cell price -30% | 55,870 | 37,575 | 28,177 |
| Cell price +30% | 60,206 | 40,971 | 30,836 |
| Motor + inverter at volume-supplier pricing (10k: $2,800 / $1,500) | 53,934 | 35,534 | 25,610 |
| Cells, motor, inverter frozen at 1k prices at 10k | 58,038 | 39,273 | 32,273 |
| Forged wheels instead of carbon | 55,203 | 37,489 | 28,401 |
| Carbon-wheel OEM price +50% | 60,419 | 40,890 | 30,612 |
| Labour $30/h | 56,383 | 38,529 | 29,155 |
| Labour $65/h | 60,244 | 40,264 | 29,975 |
| Cells -30% and volume-supplier motor/inverter | 51,766 | 33,836 | 24,281 |

EMRAX and Cascadia are low-volume specialists, so the base keeps them at specialist prices. The volume-supplier case is a sensitivity only: it saves about $3.9k per bike but needs a different motor and inverter than the ones designed in.

## Cost-down levers at 10k

T9 is met on the base case, but the margin is thin, so these matter. $ per bike at 10k, computed by the script:

| Lever | Saving |
|---|---:|
| Motor to a volume axial-flux supplier ($4,800 to $2,800) | 2,106 |
| Inverter to an automotive volume supplier ($3,200 to $1,500) | 1,790 |
| Carbon wheels to forged (set $2,100 to $1,050) | 1,106 |
| Cells to $3.10 through a direct contract | 816 |
| Labour $45/h to $30/h | 351 |

## What this does not prove

- **No price here is a quote.** The cell, motor, inverter and carbon-wheel prices and curves are my estimates. There is no published P60B or EMRAX price, and the CM200 anchor is a one-off retail price.
- **The 10k pass is fragile.** It needs about 11 million cells a year, a 10k/yr plant and supplier contracts that do not exist today. With cells, motor and inverter at 1k-bike prices it misses by $0.3k.
- **Many prices are group estimates.** Pack internals, body, electronics and chassis small parts were not priced from drawings or quotes. The four cast frame nodes carry zero mass in the BOM, so I priced them by count.
- **Reused numbers.** NRE comes from the October startup-costs study; electronics prices are `elec-bom.csv` with a 15% contingency.
- **Not included:** dealer margin, outbound freight, recalls, financing, working capital, facility, software licences, Supercharger network access (no public path, per `07-electrical.md`), certification fees beyond the NRE line, and tariffs beyond the logistics percentage.
- **Open engineering items would add cost:** the EMRAX housing approval for the load-bearing yoke, the cast-arm bolt-on boss, and P60B fast-charge cycle life. P60B at 3.80 USD assumes the cell passes.
- **Not checked:** an independent should-cost against a teardown of a comparable bike (Zero or Energica).
