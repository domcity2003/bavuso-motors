# Competitor landscape: who is closest to Bavuso

Researched 2026-10-30 (US Central) by Claude Sonnet 5.5, for the Bavuso engineering agent. Desk research from public web pages only. No supplier, company or customer was contacted. Nothing here is a Bavuso design decision.

Source tags: **[Official]** manufacturer page · **[Press]** news or review site · **[Agg]** aggregator or dealer listing (often wrong or stale) · **[Claim]** company claim with no independent test. Where sources disagree, both numbers are shown.

## 1. Bottom line

1. **One company is doing nearly what Bavuso is: Verge Motorcycles (Finland, TS Pro Gen 2).** It is a design-led electric motorcycle at $29,900 to about $35,000 with NACS-only charging, a 20.2 or 33.3 kWh pack, 124 mph, and a 200 kW fast-charge claim. It has not been proven. Its battery cells are disputed, and delivery dates have slipped.
2. **Everyone else is further away or has failed.** Damon (claimed 200 mph / 200 hp / 200 mi) has not delivered and its leadership resigned. Arc (£90k) and Energica (liquidated Oct 2024, relaunch status unclear) failed. Zero and LiveWire sell real bikes at $12k to $21k with smaller batteries and less range. LiveWire is losing money and moving downmarket.
3. **No product in the evidence claims 200 miles at 70 mph.** Verge's best highway claim is 196 miles at a steady 56 mph, on the 33.3 kWh pack. Its other table says 124 miles highway for the 20.2 kWh pack. Bavuso's range goal is stricter than anything claimed.
4. **Tesla/NACS access is no longer a differentiator.** Verge's page lists NACS as its connector.
5. **Price position matters more than before.** Verge sells at $29.9k. Bavuso's cost cap of about $30-35k per bike at scale implies a price of roughly $43-50k at a 30% margin (an assumption, not a Bavuso figure). That is $13-20k above the nearest rival, so the product has to earn that gap.

**Do the goals need to change?** Not the technical goals. The premium, status positioning needs a clearer reason to exist than "NACS, long range, light," because Verge already claims most of that. See section 6.

## 2. Comparison table

Bavuso column is from the repo README and `v1.0/cost-and-sourcing.md`. It is a development target, not a validated spec.

| | **Bavuso (target)** | **Verge TS Pro Gen 2** | Zero SR/F | LiveWire S2 Mulholland | Damon HyperSport | Arc Vector | Energica Experia | Lightning LS-218 |
|---|---|---|---|---|---|---|---|---|
| Status (Oct 2026) | Concept, no parts bought | Production reported (Apr 2026). Customer deliveries promised Q4 2026 after slipping from Mar 2026 | On sale | On sale | **No deliveries; leadership resigned** | **Liquidated Apr 2024** | Bankrupt Oct 2024; revival reported 2025, 2026 unconfirmed | Taking orders (unverified) |
| Price (US) | Target cost $30-35k; price not set | **$29,900** (20.2 kWh); $30,900 special ed.; about $34,900 with 33.3 kWh pack | $19,795 | $11,999 (launched $15,999) | $22k-45k listed, never delivered | £90k (about $117-128k) | about €30k [Agg] | $38,988+ |
| Battery | 26.3 kWh reference (700 Amprius SA504 cells); 30.1 kWh alternative | 20.2 or 33.3 kWh "solid-state" (Donut Lab) | 17.3 kWh | 10.5 kWh | not confirmed | 16.8 kWh, structural | not confirmed | 16-20 kWh (reported) |
| Weight | Under 400 lb preferred; current 433-446 lb | **518 lb** [Official]; 507 lb (230 kg) [Press, Nov 2025] | about 500 lb (227 kg) | about 432 lb | not confirmed | about 485 lb (220 kg) [Agg] | not confirmed | not confirmed |
| Power / top speed | 125+ mph | 136.8 hp / **124 mph** [Official] | about 110 hp / 124 mph [recall, unverified here] | 84 hp / 99 mph | 200 hp / 200 mph [Claim] | 95 kW / 124 mph | not confirmed | 218 mph (record) |
| Range claim | **200 mi at 70 mph** | City 217 or 370; highway 124 or 196 (56 mph) | 171-176 mi city [Press/Agg]; highway lower | about 117 km (about 73 mi) highway [Press] | 200 mi [Claim] | 270 mi max / 120 mi high speed | 261 mi city [Agg] | not confirmed |
| Fast charging | NACS/DC, target-driven | NACS only; 100 kW (20.2) or 200 kW (33.3) claimed | Tesla Tap Mini adapter, **AC only** | not confirmed | not confirmed | not confirmed | CCS; Tesla Magic Dock anecdotal | not confirmed |

## 3. Verge Motorcycles: the real comparison

### What Verge says [Official: vergemotorcycles.com/ts-pro, modified 2026-05-27]

- **Price:** from $29,900 (base). Special Edition from $30,900. Page says taxes and fees extra. The $34,900 figure for the larger pack is from press reports, not the page.
- **Battery:** 20.2 kWh or 33.3 kWh, "all solid-state by Donut Lab." Nominal vs usable kWh, Wh/kg and cell format are not stated. Power-battery warranty 5 years. Bike warranty 24 months.
- **Motor:** hubless rear-wheel "Donut Motor," 136.8 hp, 737 lb-ft (about 102 kW, about 1,000 Nm). No chain or belt.
- **Performance:** 124 mph top speed, 0-60 in 3.5 s.
- **Weight:** 518 lb on the page, 882 lb maximum laden. Electrek reported 507 lb (230 kg) at the Nov 2025 reveal. The newer figure is probably the production bike.
- **Dimensions:** wheelbase 63.3 in, seat height 30.7 in, rake 25°, ground clearance 5.5 in.
- **Chassis:** Öhlins / Wilbers fully adjustable suspension (front and rear split not stated). Front travel 4.72 in, rear 4.17 in. Brakes: dual Brembo M4.32 four-piston calipers on 12.6 in Galfer discs, Verge four-piston rear on a 14.96 in Galfer disc. Tires 120/70 R17 front, **240/45 R17** rear. ABS and traction control listed. Frame is not described beyond "modular architecture."
- **Charging:** **NACS only** on the page. DC "up to 200 kW" with the 33.3 kWh pack and "up to 100 kW" with the 20.2 kWh pack. Claims 186 mi added in under 10 minutes (33.3) or 124 mi (20.2). Start and end state of charge not stated. AC via onboard charger, rating not stated.
- **Delivery:** FAQ says TS Pro in the US and EU in **Q4 2026**, UK and other regions Q4 2027, TS Ultra Q4 2027.

### The range numbers contradict each other

The page has two sets of range figures and never says which pack each belongs to:

| Table location | City | Highway | Note |
|---|---|---|---|
| Spec table | 370 mi | **196 mi** | Matches the 33.3 kWh headline |
| Range section | 217 mi | **124 mi** | EU Annex VII figure 119 mi |

Highway means a **steady 56 mph** with a 165 lb rider in ideal conditions, per Verge. No EPA or WMTC figure is given, and the page says US/Canada regulation ranges have not been calculated. Press repeats "370 miles" as if it were a general range.

### Independent evidence on the battery

- **[Press]** An independent test at Finland's state lab VTT (Autopian, Feb 24 2026; CleanTechnica, Mar 25 2026) confirmed **fast charging**: a 26 Ah cell went from empty to 80% in about 4.5 minutes at 11C. Peak surface temperatures were 63 to 89 °C, and one run stopped at the 90 °C limit.
- **Not confirmed in those articles:** 400 Wh/kg energy density, chemistry, cycle life (claims range from 10,000 to 100,000 cycles), and cell mass. Donut Lab has not disclosed the chemistry. Three cells were tested.
- **[Press]** Several outlets report experts calling the claims doubtful. The SVOLT chairman reportedly called it a likely scam (Jan 2026). A third-party-test story reported by Tom's Hardware says the cells behave like ordinary lithium-ion. I did not verify those secondary reports myself.
- **[Press]** Pack detail from InsideEVs (Apr, year not shown, likely 2026): the standard pack is 192 cells of "94 Wh" each (about 18 kWh nominal, about 20 kWh maximum), configured 2P96S, around 400 V, and **air-cooled with PC-style fans**. The long-range pack is "roughly 30 kWh nominal," against 33.3 kWh in marketing. The article's "four modules" does not match 192 cells, so treat the layout as unreliable. Peak DC charging was about 100 kW and 10-80% about 11 minutes. No independent range test of the solid-state bike exists.
- **My arithmetic (not from a source):** 192 cells at 94 Wh is 18.0 kWh. If the 400 Wh/kg claim holds, those cells weigh about 45 kg. The bike's 518 lb (235 kg) total is plausible with that cell mass. If the cells are ordinary lithium-ion at about 250 Wh/kg, cell mass would be about 72 kg, which is hard to reconcile with the 518 lb figure. This is a consistency check only.

### Company risk [Press, partly allegation]

- Deliveries promised by Mar 31 2026 slipped, and new orders moved to Q4 2026.
- A whistleblower story (The Pack) says PwC could not finish its audit of the Estonian subsidiary's 2024 accounts. Donut Lab is a spin-off of Verge with a largely identical founding team. I did not verify this against filings.
- Production was reported at up to 350 units for 2026 by a low-authority blog. No official volume.
- Dealroom lists over €10M raised, last valuation in 2023. I found no 2026 funding or insolvency news.
- A 2024 ride review of the earlier TS Pro (Ultimate Motorcycling) criticized front-end behavior under hard throttle in Beast mode. No review of the Gen 2 solid-state bike was found.

### Read-across to Bavuso

- At $29.9k and about 518 lb with 20.2 kWh, Verge is cheaper than anything Bavuso can build at launch volume. Bavuso's own model shows $45k to $80k per bike at 100 a year.
- Verge's larger pack gives it more energy (33.3 kWh) than Bavuso's 26.3 kWh reference. If the cell claims were true, it would also weigh less per kWh than any cell Bavuso has costed.
- Bavuso's cell (Amprius SA504) has a manufacturer datasheet. Verge's does not. That is a real, usable difference, but only for buyers and reviewers who care about proof.
- **Decision gate for Bavuso:** independent range and weight results for the production TS Pro. Watch for first-delivery reviews, an EPA or WMTC range figure, and any chemistry disclosure.

## 4. Everyone else

### Damon Motorcycles (Canada), HyperSport / HyperFighter
- Claimed 200 hp, 200 mph, 200-mile range [Claim]. Listed at $22k-45k [Agg, sources disagree].
- **No road-legal production bike delivered.** Q1 2026 deliveries did not happen. CEO, CFO and board reportedly resigned in spring 2026. Website reported down. Earlier reports: 13 employees, lawsuits, DMN stock down about 70% since its 2024 listing. [Press: RideApart, Visordown, The Pack, Techcouver]
- Read-across: the closest *claimed* spec to Bavuso's top-speed and range goals belongs to a company that has not shipped.

### Arc Vector (UK)
- £90k (about $117-128k). 16.8 kWh structural battery pack, 95 kW, about 220 kg, claimed 270 mi max / 120 mi at high speed. [Press/Agg]
- Only **11 bikes delivered**. Entered voluntary liquidation April 2024. CEO blamed US distribution and the price. Had already been through administration in 2019. [Press: Visordown, RideApart, MCN]
- Read-across: the ultra-premium price did not create enough demand to fund the company.

### Energica (Italy)
- Experia about €30k, 261 mi city range claimed [Agg]. Judicial liquidation Oct 2024 (Ideanomics held 75%). Assets auctioned with a US$4.65M reserve. Reports of a 2025 revival with new funding and a 2026 relaunch, thinly sourced. [Press: MCN, Visordown, Corsedimoto]
- Can reportedly charge at some Tesla Supercharger Magic Dock stations over CCS (forum anecdote).

### Zero Motorcycles (US)
- Longest-running pure EV motorcycle maker. SR/F from $19,795, SR/S about $20,995 [Agg]. 17.3 kWh pack, about 500 lb. 15.6 kWh packs on the S/DS for MY26. 20th anniversary limited SR/F announced Sep 2026. [Press: Powersports Business, The Pack]
- Zero's Tesla adapter reaches only **Tesla destination/L2 chargers, not Superchargers**. [Press: RideApart]
- Highway range is well below the city figure (one guide says 70-80 mi at freeway speed on a performance e-bike). I did not find a Zero highway test in this pass.

### LiveWire (Harley-Davidson spin-off)
- S2 Mulholland: 10.5 kWh, 84 hp, about 99 mph, about 432 lb. Launched at $15,999, now listed at $11,999. [Press/Agg]
- Finances: 2025 revenue about $25.7M. A Q1 2026 summary projects a 2026 operating loss of $70-80M. [Agg/Press, unverified]
- Strategy: launched the **S4 Honcho minimotos at $4,999 and $5,499** (3.5 kWh, 59 mph, 125cc-equivalent) and bought Dust Moto in May 2026. [Press: Electrek, Motorcycle.com]
- Read-across: the best-resourced premium e-motorcycle brand is moving toward cheaper bikes.

### Others, briefly
- **Lightning LS-218:** $38,988, land-speed record claims, 16-20 kWh options reported [Agg]. Current delivery status unverified.
- **Ultraviolette F77 Mach 2 (India):** about Rs 2.99 lakh (about $3.4k), 7.1 or 10.3 kWh (sources disagree), up to 323 km claimed. No US launch found.
- **Stark VARG EX:** off-road bike, $13-17k, 7.2 kWh, 120 kg, 60 or 80 hp. Not a road competitor but shows what weight is possible.
- **Ducati:** only the V21L race bike confirmed. A rumored road electric is unconfirmed.
- Not researched in depth this pass: Royal Enfield Flying Flea, KTM Freeride E, Can-Am Pulse/Origin, Cake, Fuell, Tarform, Curtiss, Maeving, Ola, Oben, Matter, BMW CE 04, Kawasaki Ninja e-1.

## 5. NACS / Tesla charging

- **Verge:** NACS only on the TS Pro page. Press says it was first to adopt NACS (announced 2023).
- **Zero:** adapter for Tesla destination/L2 only, not Superchargers.
- **Energica:** CCS bike that can use Magic Dock stations (anecdotal).
- **LiveWire:** not established in this research.
- **Not established anywhere:** whether any motorcycle has been approved on the Tesla Supercharger network itself. The Bavuso docs already list Tesla network access as unresolved. Check Verge's page and any rider reports before claiming Bavuso would be first.

## 6. What this means for Bavuso's goals

1. **Keep the technical goals, but make them measurable.** "200 miles at 70 mph" is stricter than anyone's published claim. Verge's 196 miles is at 56 mph with a 33.3 kWh pack. State the goal as a number with a test cycle so it can be compared on equal terms.
2. **Weight is the clearest hardware gap.** Bavuso's 433-446 lb is lighter than Verge's 518 lb and similar to the LiveWire S2 (432 lb), while carrying more energy than the S2. That advantage depends on the SA504 cell data, which has a manufacturer datasheet.
3. **NACS is table stakes.** Treat it as required, not a selling point.
4. **Price needs a reason.** A $43-50k price (from the $30-35k cost cap) sits above Verge by $13-20k. At that level buyers compare against Verge, Zero and high-end combustion superbikes. The differentiation has to be visible: performance, design, proven range, finish.
5. **Premium e-motorcycle companies have failed or pivoted.** Arc, Energica and Damon failed or stalled. LiveWire is cutting prices and losing money. Zero survives at $20k. The common causes in the reporting are low volume, distribution and delivery delays. This applies to cost and launch planning, not to spec choices.
6. **Do not copy Verge's claims.** Its range page contradicts itself and its battery claims are unverified. Bavuso should keep separating verified, estimated and claimed numbers, as the current docs do.
7. **Watch list before locking specs:** Verge's first customer deliveries and reviews (Q4 2026), any EPA/WMTC range figure, Donut Lab chemistry disclosure, Damon's fate, and Energica's relaunch.

## 7. Known gaps in this research

- No review or measured range for the production Gen 2 TS Pro was found.
- Verge motor and pack masses, frame construction and AC charge rate are not published.
- Zero SR/F and SR/S power, top speed and DC-charge options were not confirmed from primary sources. The Zero 124 mph and about 110 hp figures in the table are from memory.
- Energica's 2026 operating status and LiveWire's DC-charging support were not confirmed.
- Many price and spec figures come from aggregators that disagree with each other. Use manufacturer pages for anything that drives a design decision.
- The Verge audit and whistleblower claims are allegations from secondary sources.

## 8. Sources

Verge and Donut Lab
- [Verge TS Pro (official page)](https://www.vergemotorcycles.com/ts-pro/)
- [InsideEVs: Verge TS Pro Gen 2 pack and cooling](https://insideevs.com/news/793256/verge-ts-pro-gen2-solid-state-cooling-pack-configuration/)
- [Electrek: Verge unveils new TS Pro (Nov 4 2025)](https://electrek.co/2025/11/04/verge-unveils-wild-looking-ts-pro-electric-motorcycle-with-hubless-motor-longer-range-and-faster-charging/)
- [Autopian: independent test of the Donut Lab battery (Feb 24 2026)](https://www.theautopian.com/the-battery-from-the-worlds-first-production-solid-state-ev-was-independently-tested-and-it-raises-more-questions-than-answers/)
- [CleanTechnica: Donut Lab specs proven, but not all (Mar 25 2026)](https://cleantechnica.com/2026/03/25/donut-lab-battery-specs-proven-but-not-all-of-them/)
- [Tom's Hardware: third-party tests](https://www.tomshardware.com/tech-industry/startups-miracle-solid-state-battery-actually-uses-lithium-ion-chemistry-according-to-third-party-tests-donut-lab-raised-usd25m-and-is-valued-at-usd1-25b-on-what-now-appear-to-be-debunked-claims)
- [The Pack: whistleblower and Verge delivery slip](https://thepack.news/whistleblower-questions-donut-labs-battery-promises-as-verge-motorcycles-deliveries-slip/)
- [RideApart: Verge delivery timing](https://www.rideapart.com/news/786637/verge-solid-state-battery-motorcycle-delayed/)
- [HiConsumption: TS Pro pricing](https://hiconsumption.com/motors/2026-verge-motorcycles-ts-pro-solid-state/)

Other makers
- [RideApart: Damon CEO, CFO and board resign](https://www.rideapart.com/news/789254/damon-motorcycles-ceo-cfo-board-resign-quit-ev/)
- [Visordown: Damon leadership resigns](https://www.visordown.com/news/damon-ceo-cfo-and-board-resign-leaving-electric-bike-brands-future-doubt)
- [Techcouver: Damon delivery delay (Mar 2025)](https://techcouver.com/2025/03/21/damon-motorcycles-deliver/)
- [MCN: Arc Motorcycles back in liquidation](https://motorcyclenews.com/news/2024/april/arc-motorcycles-liquidation)
- [RideApart: Arc Vector is no more](https://www.rideapart.com/news/717534/arc-vehicle-vector-ev-motorcycle-bankruptcy/)
- [MCN: Energica files for bankruptcy](https://motorcyclenews.com/news/2024/october/energica-files-for-bankruptcy)
- [Visordown: Energica comeback](https://www.visordown.com/news/italian-electric-motorcycle-maker-energica-secures-funding-begins-comeback-process)
- [LiveWire Q2 2026 results (Business Wire)](https://secure.businesswire.com/news/home/20260723076647/en/LiveWire-Group-Inc.-Reports-2026-Second-Quarter-Financial-Results)
- [Electrek: LiveWire S4 pricing](https://electrek.co/2026/06/09/harleys-livewire-reveals-surprisingly-low-pricing-on-new-s4-electric-motorcycles/)
- [Zero MY2026 launch](https://zeromotorcycles.com/stories/eicma-2025)
- [RideApart: Zero Tesla Tap Mini adapter](https://www.rideapart.com/news/716652/zero-motorcycles-ev-tesla-nacs-charging-adapter/)
- [Lightning LS-218 (manufacturer)](https://lightningmotorcycle.com/product/ls218/)
- [RideApart: Ultraviolette F77 Mach 2](https://www.rideapart.com/news/717769/ultraviolette-f77-mach2-launch-india/)
- [SlashGear: electric motorcycles and Superchargers](https://www.slashgear.com/1925219/can-you-charge-an-electric-motorcycle-at-a-tesla-supercharger)
