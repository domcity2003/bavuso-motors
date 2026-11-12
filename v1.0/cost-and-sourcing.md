# Bavuso cost, sourcing and capital model — V1.0 planning study

October 25, 2026, US Central. Prepared by Codex, GPT-6 family. USD unless explicitly stated. **These are unquoted development scenarios, not supplier quotations, a validated production BOM, a retail price, or a financing commitment.** No suppliers were contacted and no orders were placed.

## What the current design implies

The present high-energy cell and specialist drive choices create a potentially expensive motorcycle. Public information supports several individual price anchors, but does not establish the dominant raw-cell price, configured motor price, approved component package, or manufacturing yield. An automotive fleet-average battery price cannot be substituted for the price of SA504 cells.

The model keeps the current **700 SA504 cells / 100s7p / 26.299 kWh reference**, EMRAX208LC configured motor and CM200DX inverter candidate. It does not quietly replace them with inexpensive high-volume alternatives. The 800-cell energy reference requires another 100 cells and resized pack hardware: at the assumed cell unit prices alone that adds $4,000 / $3,000 / $2,000 in the respective base volume cases, before resulting structure, freight and yield costs.

| Assumed annual production capacity | Purchased/made components, base | Recurring delivered cost, low / base / high | Illustrative prelaunch and ramp cash, low / base / high |
|---|---:|---:|---:|
| 100 bikes/year | $65,539 | $44,915 / **$79,821** / $161,207 | $9.7M / **$16.7M** / $32.3M |
| 1,000 bikes/year | $50,445 | $34,196 / **$59,377** / $126,248 | $27.1M / **$46.8M** / $93.1M |
| 10,000 bikes/year | $35,910 | $24,150 / **$41,183** / $96,920 | $110.6M / **$188.4M** / $410.2M |

These ranges deliberately remain wide. “Base” means the middle planning assumption selected here, **not the most likely supplier outcome**. Low and high scenarios combine assumptions; they are not confidence intervals. Their precision in CSV calculations supports reconciliation and does not imply price accuracy. Actual quotations could invalidate the bands, especially cells, supported ABS, charging access, custom pack qualification and specialist motor continuity.

The large 10,000/year cash case assumes inventories for a substantial fraction of full rated annual production before useful credit terms are known. It does not predict that all inventory must be bought on day one or that the first year sells 10,000 bikes. A staged ramp, purchase releases, supplier credit and customer payment timing can change cash substantially. Manufacturing capacity, actual production and sales are separate quantities.

## The next laptop-to-hardware stages cost much less than launching a company

**The $16.7M base launch case is not the amount needed to take the next engineering step.** It funds an assumed two-year staffed development and production launch, not a single model, bench experiment or prototype. Start with bounded work and stop or change architecture when evidence fails a gate.

The following early stages have separate line budgets in `startup-costs.csv` under `Stage0A` and `Stage0B`. All are unquoted allowances. They are **nested within** corresponding work in a later full program and must not be added to the full-launch cash totals again. Stage0B is additional to Stage0A, with later design/integration hours distinct from the earlier feasibility hours.

| Early stage | Low / base / high cash planning envelope | What the envelope actually buys |
|---|---:|---|
| **Stage0A: feasibility, non-ridden buck and limited-energy module benches** | $71,875 / **$163,125** / $355,000 | Paid architecture/package work, rider/package mockup, limited cell/module samples and fixtures, instrumentation rental, qualified bench labor and independent review; 25% contingency |
| **Stage0B: one custom engineering prototype and small bench campaign, incremental after A** | $176,524 / **$379,135** / $829,280 | One provisional full hardware set with prototype fabrication premium, additional detailed integration/build engineering, outsourced motor/charge/structural rig time, workshop/handling arrangements; 25% contingency |
| A plus B, if both authorized and pursued | $248,399 / **$542,260** / $1,184,280 | Combined early development envelope; no claim all five goals or road-use release are achieved |

Stage0A base line items are $75,000 for 600 engineering hours at $125/hour, $6,000 for a non-ridden buck, $12,000 for limited-energy samples/coupons, $15,000 for 120 bench-engineering hours, $10,000 for instrumentation/fixture rentals and $12,500 for 100 independent-review hours. Its $130,500 subtotal receives a $32,625 uncertainty reserve. Owner-led unpaid work can reduce immediate cash expense but does not remove the engineering work or its competence requirements. No personal unpaid labor rate is presumed.

Stage0B base hardware allowance is **1.5 × $65,539 = $98,309 rounded**, using the 100/year component planning subtotal as a reference and a prototype fabrication premium. It adds $150,000 for 1,200 integration/build-engineering hours at $125/hour, $35,000 for a limited outsourced bench campaign and $20,000 for temporary workshop/handling/insurance scope, then 25% reserve. That is not a complete fixed-price prototype quote: actual custom-part drawings, application-approved purchases, instrumentation and revisions could cost more or fail to produce a viable vehicle. Parts bought or fixtures retained from an earlier stage must receive explicit transfer/reuse credit in the actual project ledger.

Stage0A produces **no ridden vehicle** and no complete high-voltage drive bench. Stage0B is a budget envelope for one engineering prototype and limited tests, not permission to ride it, a promise it can be built from today's documents, or a completed range/braking/durability/compliance campaign. A physical engineering prototype must pass its applicable design/readiness gates before energized or ridden testing. Full road-product release remains later work.

The owner need not commit to either whole stage at once. The first concrete spending gate is actual supplier availability/application data and scoped quotations, followed by a measured package and reviewed test plan. Those gates can prevent buying a large quantity of expensive cells before fit, mass and economics are credible.

## Inspectable files and accounting rules

- [cost-model.csv](cost-model.csv): all **158 existing component-index records**, allocated to 42 sourcing/cost bundles without adding parent and child functions twice, plus eight explicit recurring production-process rows.
- [startup-costs.csv](startup-costs.csv): 18 development/capital/working-capital rows per capacity scenario, 54 launch rows, plus 12 early-stage rows, with assumptions and double-count controls.
- [cost-summary.json](cost-summary.json): machine-readable totals, assumptions, coverage and early-stage envelopes.
- [tools/build-cost-model.py](tools/build-cost-model.py): standard-library Python calculator/audit. Edit the bundle-owner cost inputs and fixed prelaunch estimates in the CSVs, then run this script to rebuild process charges, inventory, reserves, early-stage lines and JSON totals. Its explicit rate arrays control process scenarios. It verifies scope coverage and arithmetic, not physical or commercial feasibility.
- The existing [component index](../documentation/registers/component-index.csv) remains the scope reference. This cost file covers its recorded functions; it does not prove every future leaf part, terminal or fastener has already been selected.

For each bundle, one row owns its full amount and other covered records show zero with the explicit meaning **included in the named bundle**. Zero in such a row does not mean the function is free. A duplicated motor reference is charged at canonical EL016, not also at M-038. Display and switchgear references are similarly reconciled. Frame, brake and suspension fasteners sit inside their functional bundles; body clips and inserts sit inside body; pack internal connections and vehicle harnesses have distinct boundaries.

For any volume suffix, sum `usd_VOLUME_low/base/high` only where `base_included=True`. Optional accessory, passenger, refrigeration, development-mule and reusable-shop-tool records are excluded from that sum. The CSV preserves their scope so omission is visible. Reusable fixtures are funded in startup rather than charged as a new fixture on every bike.

The base assumes **one color per bike**. RE025/026/027 represent black/silver/tan choices inside one finish budget, not three complete coating processes installed together. Color batch sizes, rejects and changeover costs remain unquoted.

## Public price evidence and what it does not establish

| Item | Public evidence reviewed | Use and limitation |
|---|---|---|
| Orion BMS2 108-series configuration | **$1,285 MSRP**, single quantity; harnesses/current sensors excluded; manufacturer says volume pricing begins at five | Bare-unit anchor only. Volume assumptions $1,100/$900 are unquoted, and accessories remain in pack sensing/protection budget. [Manufacturer](https://www.orionbms.com/products/orion-bms-standard/) |
| CM200DX | **$8,699** retail listing | Distribution price reference, not a configured OEM contract or guaranteed stock. The $7,500/$6,000 volume cases are assumptions. [Stealth EV listing](https://stealthev.com/product/cascadia-motion-cm200-inverter/) |
| ADM-CS-EVCC | **€900 bare / €1,150 with sensor**, tax excluded; store explicitly calls these sample/evaluation prices | Model uses bare-controller scope and budgets sensors separately. $1.10/€ is an explicit planning conversion assumption, not a current FX quote. Production discounts and shipment costs require a quote. [Manufacturer store](https://store.advantics.fr/charge-controllers/24-ev-charge-controller-ccs.html) |
| EMRAX configured motor | Manufacturer provides a configuration/quotation process; production quantities and delivery need confirmation | No public configured Bavuso price was established. All $7,000/$6,000/$4,500 motor figures are estimates. Published payment procedure includes advance wire payment and delivery confirmation; actual contract must be obtained. [Manufacturer sales support](https://emrax.com/support/sales-support/) |
| Öhlins KA736 | US manufacturer page indexed **$768.90**, out of stock; application shown for 2025 Ninja650 | Reference for one damper family only, not a Bavuso suspension quotation or verified 2026 fit. Rear-suspension bundle includes additional linkage/hardware and relies on an unquoted volume sourcing plan. [Manufacturer](https://www.ohlins.com/en-us/motorcycle-suspension/street/kawasaki-z-650?v=kawasaki-ninja-650-2025) |
| SA504 | Manufacturer catalog provides technical information but no reviewed raw-cell production price | Supply, lot acceptance, MOQ, application approval and prices are all open. [Amprius catalog](https://amprius.com/documents/Amprius_Product_Catalog.pdf) |
| SA504 small finished pack | Dan-Tech lists **€1,029 for a 6s2p, 451 Wh pack**, with 14–21 working-day indication on the listing and volume quote invitation from 15 | Roughly €2,282/kWh for that small finished product. It is not a bare-cell price, not Bavuso's HV pack and not proof of compatible modules. Do not multiply it into a supposed supplier quote. [Pack manufacturer's store](https://shop.danenergy.com/products/premium-high-density-amprius-sa504-li-ion-pouch-battery-22ah-20-4v-133a) |

An unqualified reseller lists SA504 at $69 but sold out, with technical fields inconsistent with the manufacturer's sheet. That is not accepted as approved sourcing. It illustrates the exposure: **700 × $69 = $48,300 for cells alone**, not $48,300 for a complete motorcycle. Source identity, authenticity, custody and current application data matter more than a cart price. [Reseller listing, rejected as qualified supply evidence](https://shlizone.com/products/hot-sell-amprius-sa504-pouch-cell-11-05ah-for-drone)

### Cell price sensitivity — the first commercial gate

| Capacity scenario | Assumed raw-cell USD each: low / base / high | Cells per bike: low / base / high |
|---|---:|---:|
| 100/year | $20 / $40 / $80 | $14,000 / $28,000 / $56,000 |
| 1,000/year | $15 / $30 / $70 | $10,500 / $21,000 / $49,000 |
| 10,000/year | $10 / $20 / $60 | $7,000 / $14,000 / $42,000 |

**Every number in that table is unquoted.** The assumed progression tests the economics of a volume agreement; it does not assert that Amprius offers those prices or discounts. Annual demand is 70,000 / 700,000 / 7,000,000 installed cells before development samples, rejects and service stock, equivalent to approximately 2.63 / 26.30 / 262.99 MWh of nominal installed energy. Confirm actual capacity allocation and road-vehicle support.

Each $1 change in raw-cell price changes purchased cost by $700 per bike before freight, yield, duties and reserve. A $10/cell price error changes purchased cost by $7,000. Resolving this quote is more useful than optimizing a $20 bracket.

## Production sourcing plan

The CSV gives a candidate sourcing route, MOQ status and lead-time basis for every covered record. Supplier routes are invitations to investigate, not awarded vendors. Most lead times are **planning allowances after correct drawings/configuration**, not observed promises. Any component can take longer or be refused for the application.

| Sourcing package | Required purchasing evidence before committing |
|---|---|
| SA504 and pack integration | Authorized supply and application acceptance; current controlled datasheet; cell matching and test data; transport documentation; actual lot MOQ; traceability; agreed rejects; warranty; capacity allocation; shipping mode |
| Motor and inverter | Exact winding/cooling/sensor/shaft/firmware configuration; compatibility maps; connectors and cables; current product lifecycle; duty/thermal acceptance; quantity tiers; service availability |
| Forks, wheels, axles, suspension | One matched interface family; full drawings and masses; source continuity; load/rim/tire compatibility; calibrated dampers; wear parts; production support rather than assuming donor retail parts become an OEM supply contract |
| Brakes and ABS | Matched hydraulic/sensor package; supported application/calibration and regen interface; software/licensing/NRE; supply agreement and safety-related traceability |
| NACS inlet, routing, EVCC and OBC | Voltage/current/configuration; AC/DC sequencing and locking; actual station interoperability; conformance and software support; 120 V input if adopted; no assumed Tesla network-access fee or guaranteed eligibility |
| Frame, swingarm and body | Released parts, materials, joints, tolerances, process, first-article inspection, fixtures/tool ownership, repairability, production rate, scrap responsibilities and engineering-change terms |
| Harness, protection and thermal | Exact connector/contact/fuse/contactor configuration; lead lengths and routing; electrical coordination; pressure/flow/thermal drawings; environmental tests and service parts |
| Lamps, display and controls | Approved functions and installation constraints; supported firmware/diagnostics; environmental/EMC data; color/finish and replacement-source continuity |

No invented MOQ is used as a contractual fact. Public evidence shows Orion's quantity-five pricing threshold, EVCC sample ordering and EMRAX's online order limit; it does not establish production MOQ for the bike. Separate economic order quantity from a supplier's MOQ, annual commitment and release quantity.

The illustrative volume reductions could require custom tooling, binding orders or changed manufacturing processes. If a cheaper design changes material, mass, temperature capability or supplier configuration, requalify it and change the BOM. Cost targets cannot grant engineering credit.

### The battery enclosure is still an uncosted design problem inside a cost allowance

The current CAD review's 3 mm closed aluminum shell at 690 × 220 × 550 mm has approximately **10.43 kg shell mass before hardware**. With 68.11 kg typical cells, the 80.13 kg 85%-cell-fraction pack target leaves only about **1.59 kg** for all remaining pack functions in that particular shell study. That is not a credible completed cooling/protection/compression/electronics BOM. Its cost bundle is an engineering allowance, not evidence a qualified complete pack can be bought or fabricated for $800–$1,500. Actual enclosure process, joining, pressure plates, seals, protection and cooling could alter both mass and cost substantially.

## Landed cost, operations and logistics

The recurring model adds these explicit charges after the component subtotal:

| Addition | Base assumptions at 100 / 1,000 / 10,000 yearly |
|---|---|
| Inbound freight, packaging, DG handling, brokerage and insurance | 4% / 3% / 2.5% of purchased/made component subtotal |
| Import duty stress allowance | 2.5% of component subtotal: assumed 50% imported × 5% weighted rate; **not a tariff ruling or current HTS rate** |
| Scrap/yield/rework material | 4% / 3% / 2% of component subtotal |
| Final assembly labor | 40 h × $65 / 24 h × $60 / 12 h × $55 burdened labor per bike |
| Recurring end-of-line testing | $250 / $160 / $110 per bike |
| Factory operating allocation | $1,000 / $650 / $450 per bike |
| Outbound domestic crate/freight allowance | $500 / $400 / $350 per bike |
| Warranty/service sensitivity reserve | 4% / 3.5% / 3% of manufacturing-through-test subtotal including factory allocation; delivery excluded from reserve base |

Quoted made-part prices include their fabrication labor; final assembly hours cover pack/vehicle integration, not a second full frame-fabrication labor charge. Hours, automation, inspection takt and first-pass yield require time studies. Purchased-part process costs must be separated from internal labor if work is brought in-house. Factory allocation excludes startup engineering, depreciation and postlaunch corporate sales/admin costs.

For actual landed cost, assign origin, ship-from location, currency, Incoterm, customs classification, duty/tax treatment, freight mode, package size/mass, dangerous-goods treatment, insurance, brokerage, payment terms and incoming inspection to **each purchase order**. Supplier nationality is not necessarily manufacturing origin. Duties can apply to a customs value different from this simplified subtotal. The CSV import line is a sensitivity placeholder to replace after qualified review, not legal guidance.

Loose cells, finished batteries and batteries installed in equipment can require different shipping treatment. Establish carrier and qualified dangerous-goods classification/packaging/documentation from the actual item and route. Battery transport qualification and test-summary records must be verified; a cell catalog certification does not establish every vehicle shipment. Plan separate damaged/defective returns and service-pack storage/transport. [PHMSA lithium-battery resources](https://www.phmsa.dot.gov/lithiumbatteries)

Build receiving quarantine, lot serial traceability, humidity/temperature-controlled storage as specified, controlled shelf life, incoming cell checks, protected storage/segregation, kitting, production stock rotation and service-stock processes into the real operation. The budget includes provisional handling/quality capital, but does not define a certified facility. No logistics provider or building has been selected.

## Startup cash: development, factory readiness and working capital

Assume a **24-month prelaunch program**, leased facilities, outsourced cell manufacturing, and purchased major power electronics. No land purchase, dedicated cell factory or global dealer real estate is included. No promise of a 24-month completion schedule is made.

Internal program labor assumes 18 / 35 / 65 full-time-equivalent staff for two years at $180,000 loaded annual cost each. These are staffing scenarios, not wage survey facts or hiring plans. They include engineering, controls, systems, program and industrialization work. Additional specialist budgets cover distinct contracted scopes and must not also fund the same labor a second time.

`startup-costs.csv` separately includes external specialists; prototype/destructive builds; cell aging/module tests; vehicle test/compliance/retests; frame/body/pack tooling; end-of-line rigs; facility deposits/fitout; handling/lifts/fixtures; quality/traceability/supplier development; legal/IP/insurance setup; service launch/spares; and 24 months of nonengineering business runway. Each needs scoped supplier or employment/facility inputs before funding approval.

The prelaunch subtotal receives 15% / 25% / 40% low/base/high uncertainty reserve. Inventory and collection-gap assumptions are separate rather than contingency applied a second time. Product-network acceptance is not assumed obtainable by paying a generic certification fee.

| Base annual-capacity case | Development, factory readiness and reserve | Inventory and collection/ramp cash | Combined |
|---|---:|---:|---:|
| 100/year | $15.33M | $1.38M | $16.71M |
| 1,000/year | $33.19M | $13.66M | $46.85M |
| 10,000/year | $69.75M | $118.69M | $188.44M |

This separation is why capacity planning and payment terms materially change launch financing. A smaller initial inventory release should be modeled against the actual monthly ramp, not assumed to preserve full-rate availability automatically.

Working capital formulas:

```text
production inventory cash = annual capacity × stock weeks / 52
                          × (component cost + inbound + import allowance)
stock weeks = 8 / 10 / 12 for the three capacity scenarios

additional ramp/collection buffer = annual capacity × gap weeks / 52
                                 × recurring delivered cost
gap weeks = 2 / 3 / 4
```

These buffers deliberately assume no supplier credit or customer deposits. The inventory line represents stock/WIP material before completion; the separate gap represents later finished-bike/collection timing. Actual stage durations and cash-conversion cycles must replace them to prevent overlapping buffers. Deposits paid toward inventory are part of its eventual purchase cost and must **not** be added as a second full material expense. Inventory is cash tied up, not a second COGS charge in addition to the per-bike costs.

This is startup/ramp financing scope, not a lifetime business plan. It excludes financing interest, investor transaction costs, owner income taxes, sales-tax collection/remittance, full worldwide homologation, a company-owned global retail network, major battery recalls beyond the provisional reserve, and costs from yet-unadopted passenger or climate requirements. It includes ordinary early business setup/runway but does not forecast postlaunch SG&A or distribution margin. Every excluded item needs a decision or separate model before a final investment case.

## Options and the commercial decisions they force

The base cost excludes saddlebags, passenger additions, an active battery chiller and mule-only chain conversion. Their provisional hardware costs remain visible in the CSV. Chiller inclusion also changes cooling electrical loads, mass, tooling, warranty and qualification; adding its hardware dollar row does not establish hot-weather charge capability. Passenger hardware does not purchase a passenger rating.

If raw-cell and specialist-drive quotations resemble these higher bands, the present design is a premium engineering project. A mainstream retail-price target would require a separate costed architecture comparison: lower-cost qualified cells and resulting mass, different motor/inverter suppliers, reduced required energy through measured aero, or owner-approved product trades. Those alternatives may be worthwhile, but cannot be credited with keeping every current performance and mass assumption unchanged.

Before choosing a retail price, establish delivered COGS, engineering/tooling recovery, distribution/service costs, warranty experience, corporate expenses and desired margin. This model deliberately does not invent customer willingness to pay or a profitable MSRP.

## Next evidence that will narrow the model

1. Configured and application-approved SA504 price tiers, supply commitment, rejects/warranty and transport terms; run cell-price sensitivity before other cost optimization.
2. Supported motor/inverter configuration and lifecycle quotations, including mating hardware, licensing and application engineering.
3. Complete realistic pack mechanical/HV/thermal design and integration quote, replacing the mass-fraction shortcut.
4. Matched brake/ABS, running gear and charging quotations with NRE/MOQ/lead-time terms.
5. A leaf BOM from actual CAD/harnesses and supplier drawings, with every assembly and alternative reconciled.
6. Time studies, yield trials, tooling/process quotations, actual facility/insurance/logistics terms and a monthly cash-conversion ramp.

Until those are in hand, the useful output is the exposed cost structure and RFQ priority. The 158-row scope check is complete; engineering release and economic feasibility are not established.
