# Bavuso V1: independent review before the final dossier

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) as the independent reviewer for the Bavuso V1 program. I wrote none of the work under review. Companion data: `program/data/review-number-table.csv` (97 rows, one per headline number per document).

Reviewed: `GATE-A-targets-locked.md`, `01` to `16`, `18`, `BRIEF.md`, all of `program/data/` listed in the request, the 9 drawing sheets (text and structure only), two renders (`cycles-adventure-side.png`, `cycles-adventure-rider-hero.png`), and the Nov 21 outside review PDF (`Bavuso-V1.0-Concept-Freeze-Review.pdf`). Not reviewed: `17-aero.md` does not exist yet (aero is **pending**; a CFD case `data/aero/run/m1` was still iterating when I looked). I did not open the CAD, re-run FEA or thermal, or inspect the drawing sheets as a drafter would.
Labels: **recomputed** = I re-ran the program's own script; **read** = taken from the documents.

## The plain answer

**The design is a coherent, honestly caveated paper concept, but the document set is not yet safe to attach as one package.** The engineering got better between documents; the headline text did not follow it. Today a reader will find 240 kg, 252.9 kg, 250.6 kg and 257.3 kg in different files, a 103 kg pack that is 108 kg, a 370 V pack that is 360 V, and three different rear brake discs.

**The headline claims survive the heavier bike, by a thin margin.** I re-ran the drive model (`06`) at the final 257.3 kg:
- Range at 70 mph is **152.4 mi** (was 154.0 at 240 kg), at 77 mph **132.2 mi**. T3 (at least 145 mi) still passes, but only while CdA stays at or below **about 0.407**. CdA has never been measured or computed for this bike (aero is pending), so T3 is a calculation on an assumed input.
- 0-60 mph is **4.15 s** (was 3.95), 4.44 s with 25 kg of luggage. Top speed (135 mph limit) and 125 mph power are unchanged.

**The mass story needs plain wording.** Weight was the main problem. The target moved 240 kg, then 255 kg, then 260 kg while the design grew to 257.3 kg. That is a legitimate re-baseline, but the margin went from 12 kg (5%) to 2.7 kg (1.0%), the per-system budgets were reset to equal the actual numbers (so "budget pass" proves nothing), nothing has been weighed, 73 kg of the 257 kg is labelled estimate and 76 kg has concept status. Say so.

## Prioritised fix list

### Must-fix before the dossier

| # | Fix | Where | Why |
|---|---|---|---|
| M1 | Replace every 240 kg / 252.9 kg / 250.6 kg headline with **257.3 kg / 567 lb**, and rewrite the plain-answer text of Gate A, BRIEF framing, 01, 06, 14 | GATE-A top and mass table; BRIEF; 01; 05; 06; 09; 13; 14; 18 | Gate A still says "240 kg" and "matches the BMW R 1300 GS (523 lb)... lighter than the Energica Experia (573 lb)". At 567 lb V1 is 44 lb over the GS and about level with the Experia and 4% over the Zero DSR/X. The BRIEF framing text ("240 kg, about 150-mile bike") will be copied into the application |
| M2 | Add the 257.3 kg re-run to `06` and state T3 as "152 mi at an assumed CdA 0.38; fails above CdA 0.407" | 06; Gate A T3 | Section 2 below. The doc still shows 154 mi, 3.95 s, 133 mi |
| M3 | Fix T2: pack mass **108.0 kg** (not 103), nominal voltage **360 V** (not 370 V) | Gate A T2 and mass table | T2 is "not met as written"; Gate A's own decision log already says 360 V |
| M4 | Do not publish any aero or range claim as verified. Add a one-line status for `17-aero.md` (pending) and label range "calculated at assumed CdA" | Gate A T3; 01 REQ-004; dossier | The outside review's open item (7% mesh change against a 2% goal) is still open; no V1 CdA exists |
| M5 | Settle the brakes: one rear rotor size in ledger, BOM, cost and supplier slot (CAD and dynamics use **267 x 5**; ledger/BOM/cost say **245 x 5 at 0.85 kg**, 03/04 say 267 x 6), one front size (CAD **320 x 5**; 02, 12, 14 say 300 mm) | `supplier-masses.csv` slot, parts-ledger BV-RUN-0060, 12, 13, 14, cost CSV | This is the outside review's "rear rotor mismatch" in a new form; closed in the analysis, reopened in the parts list |
| M6 | Re-run structures at **257.3 kg** and with the yoke cross-member at **Z545 as built**, or state in the dossier that FEA is at 240 kg scaling | 09 Round 2 | The pass margins are thin and every one was run at 240 kg: rear-bump cross-brace SF 1.28 becomes **about 1.19 to 1.24** (limit 1.2); belt case D1 is 1.20 "no spare"; slider cases 1.08 to 1.18; fatigue D 0.49 against 0.50. `09` itself says "the design only closes at 240 kg" (about the earlier round) |
| M7 | Label or replace superseded documents so the dossier carries only current numbers | 02, 05 (early sections), 08, 12, 13, 14, 18, 04 | They still describe the EMRAX 188, 100s10p, a yoke through the EMRAX housing (D24, D30, test V08 $70k), "V1 CAD not re-checked against FMVSS 108/111/123" (rev D/E added a 91-check screen), `cost-model.csv` as the T9 basis, 300 mm discs |
| M8 | Pick one headline charge time and its conditions. The docs give 15.5, 17.1, 20.2 and 21.0 min for the same 10-80% at 25 C; Gate A says "about 20". Quote **about 20 min at 25 C, 23 min at 35 C, 25 min at -10 C with the heater, 41 min at 45 C**, and state that 5C or 2C cell charge life is unconfirmed (datasheet v0.1) | 06, 07, 10, Gate A T6 | `07` says the P60B risk is "retired on paper" while Gate A lists it as risk 1. Hot-climate charging is not in any dossier-facing text |
| M9 | Resolve the electrical contradictions before the BOM is used to order anything: DC current cap **350 A (07) vs 400 A (06)**; fuse 400 A at 0.88 of rating; HV cable **50 / 35 / 70 mm2** in four places; charger **3.3 kW in CAD vs 6.6 kW BROGEN in ledger and cost**; motor winding named **HV (ledger), MV (CAD solid), LV+43% (06, 07)** | 06, 07, ledger, cost, CAD names | 06's peak power and 0-60 at low charge use 400 A, which the contactors (350 A carry) do not allow; at 350 A, 10% SOC power is 96 kW, not 103 kW (both still pass T5) |
| M10 | State margin honestly: 2.7 kg (1.0%) against a first policy of 12 kg (5%); budgets re-fit to actuals; **0 kg measured**; the ledger's own growth rule gives about 287 kg | Gate A, dossier | Reviewer's reading of `mass-budget-report.csv`: every group is flagged TIGHT with 0.0 to 1.5 kg headroom |

### Should-fix

| # | Fix | Why |
|---|---|---|
| S1 | Re-run dynamics (15) on rev E at 257.3 kg (CG 788/530 mm, pulley flange moved 181 to 177 mm, stiffer frame) | 15 is rev D at 247.9 kg; the 177 mm flange gives 48.6 deg, exactly the "peg + 3 deg" rule with no spare; thinnest damping is 0.028 |
| S2 | Add a DFMEA row and a test for the semi-active steering damper failing in the unscheduled state | Without a damper, wobble is unstable 15-85 mph. The DFMEA lists the damper as "not analysed". Fail-safe behaviour is a safety claim the dossier should not leave open |
| S3 | Rebuild the saved CAD, or state that the saved model lacks two generator fixes | 16 section 6: node shells overlap the seat pan (1,250 mm3 each) and rear indicators float 14 mm low; side stand grazes the lower body (149 mm3). The CAD also still has no cell holders, lid, lug plates, motor mount, ribbons, hoses or vents |
| S4 | Reconcile CAD geometry with ledger masses or label the CAD as envelope | CAD swingarm is a filled box (8.3 kg Al) against 2.28 kg in the ledger; CAD rear pulley is a plain disc (9.1 kg) against 2.3 kg; motor carrier 0.79 vs 0.4 kg. Masses are design intent that the CAD does not show (18 sections 4.3 to 4.5) |
| S5 | Reconcile validation and startup cost: DVP&R **$7.04M US** (14), NRE **$32.4M at 10k** reused from an October file (11), older $10.9M | The outside review asked for this; it is only half done |
| S6 | Add the crash and pack-case evidence the DFMEA calls High: 5 mm front wall was adopted but only the 4 mm wall (167 MPa vs 140) was analysed; no cell-backed crush analysis | D07; 09 "pack case" section |
| S7 | Change or label the rider case | Gate A calls 90 kg / 1,755 mm a "95th-percentile male". That is close to the adult male average, not the 95th percentile. Either relabel or test a heavier, taller rider |
| S8 | Settle the unresolved overlaps in 03 (about 4 kg of suspected double counts not applied) and the fork, wheel, tyre, brake and cooling masses (97% to 100% estimates) | Keeps the 2.7 kg headroom honest in both directions |
| S9 | Check the drawing pack index page: in text extraction the scale and mass columns look shifted one row (sheet 1 blank, sheet 2 shows 16.990, which is sheet 1's mass). Likely a layout offset, not data, but I could not render the page | Cosmetic but visible on page 1 of the pack |

### Note only

- Competitor masses, kWh and prices come from search summaries (01 admits this); two sources conflict for several bikes.
- Unit cost is 66% of the $45k MSRP before dealer margin, freight, financing and NRE (about +$650/bike at 10k over 5 years). Still under $32k.
- `11` cost model: motor, inverter, cell and carbon-wheel prices are estimates, not quotes. With cells, motor and inverter at 1k-bike prices the 10k cost is $32.3k and misses T9.
- Frame lateral stiffness used in 15 (1.3 kN/mm) is the pre-yoke value; the later 1.67 kN/mm makes 15 conservative.
- 18's BOM assembly IDs and the lid / holder IDs are provisional, not in `parts-id-registry.csv`.
- Fork lateral stiffness (30 kNm/rad), tyre properties, gust centre of pressure and the 450 C disc limit are estimates in 15.

## 1. Did the Nov 21 outside review's findings close?

| Finding | Status | Evidence |
|---|---|---|
| **Double counts** (side stand 1.4, DC-DC 1.2, inlet 0.8 = 3.4 kg) | **Closed** | 03 removed all three and 11 more overlaps (-15.7 kg overstatement, +7.0 understatement); parts-ledger has no such allowance rows. About 4 kg of further suspected overlaps are listed but not applied (03 table) |
| **Rear rotor mismatch** (267 x 6 needed, 267 x 5 modelled) | **Partly closed** | 15 reruns the fade with 267 x 5: 355 / 426 C against a 450 C limit, so the analysis and CAD agree. But ledger, BOM, cost and supplier slot still say 245 x 5, 03/04 say 267 x 6 (M5). Front: CAD 320, three documents say 300 |
| **Aero mesh convergence** (0.413 to 0.385, 7% against 2%) | **Open** | `17-aero.md` does not exist. `data/aero` has a geometry manifest and one CFD case still iterating; no `aero-results.json`. The 0.38 CdA is an assumed input; `range-70mph.json` runs 0.40 as an input, not a result |
| **Cost staleness** ($24.8k at 490 lb) | **Closed on parts, open on validation** | 11 reprices the 257.3 kg final BOM ($29.5k at 10k, ledger and BOM tie to 0.0 kg). 14 still cites the old `cost-model.csv`; validation and startup cash not reconciled (S5) |
| **Appearance drift** (flat battery cover, pods, tail, guards) | **Partly closed, frozen with open items** | One continuous lower body replaces cover and filler; guard tubes gone; tail bracket shortened; gloss line added. Still open per 16 and Gate A: pods 55 mm proud, no R15 on the lower body, second flank line not built. In `cycles-adventure-side.png` the lower body still reads as a large flat slab and the pods as boxes |
| Other: lower cover gap 1.99 vs 5.0 mm | Closed | 5.2 mm in rev D, 14.3 mm in rev E |
| Other: belt to tyre overlap | Closed, **zero margin** | 12.0 mm against a 12 mm limit (tyre growth, tracking not included) |
| Other: wobble damping -0.13 / -0.19 | Closed with a damper | 15: scheduled damper gives positive damping, thinnest 0.028 (S1, S2) |
| Other: 30.7 min charge at 45 C | Better, not solved | 10: 40.9 min at 45 C without a chiller |
| Other: FMVSS lamps and mirrors "need fresh check" | Closed at envelope level | 91 checks in 16 include FMVSS 108/111/123 screens; 12 text not updated |

## 2. Numbers: where they disagree and which is right

Full table with all 97 rows: `program/data/review-number-table.csv`. The authority order I used: latest committed analysis, then ledger data, then older prose.

| Quantity | Value to use | Documents that disagree |
|---|---|---|
| Wet mass | **257.3 kg / 567 lb** (ledger, `mass-rollup.json`, `bom-v1-reconcile.json`) | Gate A headline and table 240; 01, 06, 09, 13, 14 at 240; 15 at 247.9; 16 at 250.6; 18 and 05 at 252.9 |
| Gross / usable energy | **23.76 / 21.4 kWh** | 01: 23.0 / 20.7; 02: 21.6 |
| Nominal voltage | **360 V** (250-420 V) | Gate A T2 370 V; 01 340 V |
| Pack mass | **108.0 kg** | Gate A T2 103; 01 100; 02 93.75 |
| Range 70 / 77 mph, CdA 0.38 | **152.4 / 132.2 mi** (recomputed) | 06 154 / 133; 01 146 / 125; Gate A about 150 |
| 0-60 mph | **4.15 s** (4.44 with luggage) | 06 3.95 (4.24); 02 4.5-5 |
| Top speed | **135 mph limit, governed 130** | 01 "125 verified" (nothing verified) |
| Peak / continuous power | **124 kW motor; 96 kW at 10% SOC and 350 A; continuous 61.6 kW (below 56 kW under 103 mph)** | 06 103 kW (400 A); 01 60 kW continuous |
| DC charge 10-80% (25 C) | **about 20 min** | 15.5 (06), 17.1 (10), 20.2 (07), 21.0 (06, 2C) |
| CdA | **0.38 assumed, unmeasured** | all documents treat it as a target; aero pending |
| Wheelbase | **1,490 mm** | drive-lib (06) 1,480 |
| CG (bike, rev E) | **788 mm ahead of rear axle, 530 mm high** | 15: 798 / 535; 06 uses an old 738 / 643 with rider |
| Front / rear disc | **320 x 5 / 267 x 5** | 02, 12, 14: 300; ledger, BOM, cost: rear 245 x 5; 03/04: 267 x 6 |
| Belt | **Gates 8MGT-1760-62, 35T / 126T, 3.60:1, 62 mm** (centre distance hand check agrees: 545.6 vs 545.9 mm) | 02 old single stage 3.8:1 |
| Chassis mass | **30.9 kg** (frame 17.0 + yoke 8.7 + swingarm 4.1 + hub carrier, pads, bearings, allowances) | Gate A budget 18; 09 25.4 modelled |
| Drive mass | **23.65 kg** | 06 23.1; 18 23.45 |
| Unit cost at 10k | **$29.5k (estimate)** | 01 and 14 cite $24.8k or the old file |

### Recomputed at 257.3 kg (method as in 06)
I ran `drive-lib.py` with the bike mass raised by 17.32 kg (240 to 257.32), keeping every other input of `06`, and a copy of `cruise_range` from `aero-v1-range.py`. The baseline reproduced 06 exactly (154.0 mi at 70 mph, 133.0 at 77). Scratch script: `...\scratchpad\recalc.py` (not in the repo).

| Case | 240 kg (06) | 257.3 kg | Change |
|---|---:|---:|---:|
| Range 70 mph, CdA 0.38 | 154.0 mi | **152.4 mi** | -1.6 |
| Range 70 mph, CdA 0.40 | 148.2 | 147.0 | -1.2 |
| Range 70 mph, CdA 0.41 | 145.1 | 143.9 | -1.2 |
| Range 70 mph, CdA 0.43 | 140.0 | 138.8 | -1.2 |
| Range 77 mph, CdA 0.38 | 133.0 | **132.2** | -0.8 |
| Range 125 mph, CdA 0.38 | 56.9 | 56.9 | 0 |
| 0-60 mph (SOC 90 to 20, 25 C) | 3.95 s | **4.15 s** | +0.20 |
| 0-100 km/h / 0-100 mph | 4.10 / 6.91 | 4.31 / 7.26 | +0.21 / +0.35 |
| 60-100 mph roll-on | 2.96 | 3.11 | +0.15 |
| 0-60 with 25 kg luggage | 4.24 | 4.44 | +0.20 |

- **T3 (at least 145 mi at 70 mph) holds at CdA 0.38** with 5% margin (152.4 mi). The break-even CdA is about **0.407** (0.40 gives 147.0, 0.41 gives 143.9). The outside review's range was 0.385 to 0.423, so part of the plausible CdA range fails.
- **0-60 claims hold.** It stays torque-limited (0.69 g launch). The wheelie and grip checks are unaffected. A hand check: 220 Nm x 3.60 x 0.985 / 0.3145 m = 2.48 kN on 347 kg gives about 0.70 g, and 26.8 m/s at 0.69 g gives 3.96 s before drag, which the model's 4.15 s includes.
- **Not recomputed:** thermal (mass has a negligible effect on road load at 125 mph), charging and regen. Regen energy recovery from 70 mph scales with mass and is not claimed anywhere.
- Real-world range is 15 to 20% lower than calculated (01's own statement), about 120 to 130 mi, with wind, hills and cold.

### Other hand checks that passed
Pack: 1,100 x 21.6 Wh = 23.76 kWh; 100 x 3.6 V x 66 Ah matches. Belt: 126 / 35 = 3.60; pitch diameters 89.13 and 320.86 mm; the 8MGT-1760 belt gives about 546 mm centre distance. Top speed at the 6,500 rpm limit is 134.9 mph. 125 mph wheel power at CdA 0.38 is about 43.5 kW. Cost sums to $29,507 and the cell line is $176/kWh. BOM and ledger tie at 257.3215 kg. Cost, BOM and ledger share part IDs.

## 3. Overclaims (stated as fact, really estimate or untested)

| Claim | Where | What it really is |
|---|---|---|
| "Range about 150 mi at 70 mph" | Gate A T3, 01, 06 | Calculation at an **assumed** CdA 0.38; no V1 CFD or coast-down; fails above CdA 0.407 |
| "125 mph verified" | 01 verdict table | Not verified. Model only; EMRAX torque curve beyond its 5,500 rpm datasheet corner is a fitted model; belt rated only to 4,000 rpm by Gates (extrapolated to 6,262 rpm) |
| "Passes at 25 C" thermal | 06, 10 | Lumped model, assumed ram-air factor 0.25 and core conductance; no CFD or bench; two models disagree (46 vs 50.7 C) |
| "P60B fast-charge risk retired on paper" | 07 | Datasheet v0.1; 5C charge life not on the datasheet and could not be read; Gate A still lists it as the first risk |
| "Every system within budget; budget_pass true" | Gate A, ledger | Budgets were re-set to actuals (pack 108.0 = 108; all other groups within 0.5 kg). Not evidence of control |
| "FEA passes every case" | 09 | At 240 kg scaling, 12 mm mesh, assumed fatigue spectrum, rigid bosses, nominal-stress welds, no buckling or crash plasticity, no motor mount or torque reaction; several SF at 1.18 to 1.26 against 1.2 |
| "91 of 91 checks pass" | 16 | Envelope clearances on sharp-corner and untrimmed twin shapes; the broad overlap sweep ran separately and found 23 overlaps; belt-tyre gap sits exactly on its limit |
| "Native NACS" | Gate A T6, 07 | A connector, protocol design and EVCC. Supercharger access and Plug and Charge are **not established** (07 says so; keep that sentence in the dossier) |
| "T8 met: damping positive in all modes" | 15 | Only with a speed-scheduled damper, thinnest 0.028; hands-off rigid rider; fork stiffness and tyre data estimated; no comfort or buffeting analysis; gust centre of pressure is an assumption |
| "Pack propagation passes" | 10 | Passes only with coolant flowing; with none or in the worst credible case cells reach 134 to 249 C. A 2-D screen, not UN R136 |
| "$29.5k unit cost passes T9" | 11 | Estimates only, no quote; the margin disappears if cells, motor and inverter stay at 1k prices |
| "Looks frozen at rev E" | Gate A T10 | Render of CAD shells; pods 55 mm proud, second line missing; matte slab in side view |
| Masses of the rear pulley (2.3), swingarm (2.28), motor carrier (0.4), fork (6.8), carbon wheels (5.9) | ledger | Design-intent or estimate; the CAD solids differ (9.1, 8.3, 0.79 kg); no maker publishes wheel masses |
| "V1.1 levers save about 10 kg" | Gate A | Not analysed; the levers are listed, not computed |
| 90 kg rider as "95th percentile" | Gate A T7 | Close to the adult male average |

## 4. Gaps in a credible V1 package

1. **Nothing measured.** No weighed part, no measured CdA, no test. The `by_source` split is 0 / 109.8 / 74.6 / 73.0 kg (measured / supplier / calculated / estimate).
2. **Aero document** (`17`) missing; no mesh convergence, no rider CdA, no cooling-duct pressure data, no side-force or centre of pressure for gust (15 needs it).
3. **Motor mounting and torque reaction.** No motor mount solid or design; motor housing, stator plate and the yoke interface are unmodelled; EMRAX has not confirmed shaft or housing loads. 220 Nm torque reaction was not applied in FEA.
4. **Crash and pack safety.** No cell-backed crush analysis, no tested vent, no propagation test; 5 mm front wall not analysed.
5. **Fork, triple clamps, axles, wheel bearings, carbon wheel fatigue and impact** not analysed; fork stiffness an estimate; wheel and tyre speed rating at 130 mph not evidenced.
6. **Controls and software.** No specification for BMS limits, regen and ABS blending, the NACS handshake, charge derating, speed governor, damper schedule, limp mode, or cybersecurity.
7. **Wiring and plumbing are not in the CAD** (harness, ribbons, manifolds, hoses, vents, busbars); lengths are +/-30% estimates.
8. **Cell holders, pack lid and seal, lug plates** are derived or unmodelled.
9. **Service, maintenance and end-of-life**: no service access study, belt tension procedure, pack repair or recycling plan.
10. **Supplier confirmation**: no quote, no datasheet confirmation from Molicel, EMRAX or Cascadia at the actual 360 V bus (07 and 06 both flag it).
11. **Process FMEA, hazard analysis (ISO 26262) and FMEDA** do not exist; ASIL levels are proposals.
12. **Rider fit** covers one 1,755 mm rider; no short or tall case.
13. **Noise (EPA), EMC, UN 38.3 and homologation dates**: planning only.
14. **Manufacturing drawings**: concept-level only (no GD&T, welds, threads, fits).

## 5. Target verdicts (T1 to T10)

| # | Target | Verdict | Evidence |
|---|---|---|---|
| T1 | Wet mass <= 260 kg | **Met-thin** | 257.3 kg (ledger = BOM = rollup); headroom 2.7 kg (1.0%); nothing weighed; 28% estimate, 29% calculated; ledger growth rule gives about 287 kg |
| T2 | Pack: P60B 100s11p, 23.8 kWh, 370 V, <= 103 kg | **Not met as written** | 23.76 kWh and 21.4 kWh usable are right; voltage is 360 V; pack is **108.0 kg** against 103. Passes against the re-based 108 kg budget |
| T3 | Range >= 145 mi at 70 mph, CdA <= 0.38 | **Met-thin, not verified** | 152.4 mi at 257.3 kg (recomputed); fails above CdA 0.407; CdA unknown; aero pending |
| T4 | 125 mph sustained, governed 130 | **Met-thin, not verified** | Speed limit 135 mph, 2.4x power margin; 25 C thermal passes in two models; at 38 C derates to about 105 mph; hot-day relief is in Gate A, not in 06 |
| T5 | >= 90 kW peak, >= 55 kW continuous | **Met-thin** | Peak 124 kW at high charge, 96 to 103 kW at 5-10% SOC (25 C), 81-86 kW cold at low charge; continuous 61.6 kW inverter-limited and below 56 kW under 103 mph; 350 vs 400 A cap unresolved |
| T6 | Native NACS, DC 10-80% <= 25 min, AC >= 3.3 kW | **Met-thin, not verified** | Charge 15.5 to 21 min at 25 C, 23.0 at 35 C, 25.4 at -10 C with 3 kW heater, 40.9 at 45 C, fails at 42 C arrival (27.4); cell charge life unknown; Supercharger access not established; AC unit conflict (3.3 vs 6.6 kW) |
| T7 | Solo 90 kg + 25 kg luggage | **Not verified** | FEA at 240 kg scaling; thin SFs; "95th percentile" label wrong; luggage mass modelled as a box on the rack |
| T8 | Comfort, 77 mph gust stability, positive damping | **Met-thin, not verified** | Damping positive only with a scheduled damper (0.028 thinnest); comfort and buffeting untested; gust inputs assumed; dynamics at rev D mass |
| T9 | Unit cost <= $32k at 10k/yr | **Met-thin (estimate)** | $29.5k; fails at $32.3k if cells, motor, inverter keep 1k prices; no quotes |
| T10 | Frozen appearance direction | **Met-thin** | Direction kept (beak, band, screen, waist, saddle, matte black); lower body, tail and cover cleaned up; pods, edge radii and second line open and logged to V1.1 |

Key: **met** = claim supported by analysis with margin; **met-thin** = passes on paper with little margin or on an assumption; **not met** = fails as written; **not verified** = no analysis or test on the exact claim. Nothing in V1 is met by test.

## What this does not prove

- This review does not prove the design is right or wrong. I read documents, ran one script, and looked at two renders. I did not open the CAD, rebuild it, re-run FEA, thermal or dynamics, or check the 9 drawing sheets as a drafter would.
- The 257.3 kg recomputation changes only the bike mass in the existing drive model. The model's own limits (estimated motor iron loss, efficiency map, pack resistance, 25 C pack, 300 W auxiliaries, flat still air) carry over. I did not check the model's equations beyond the hand checks listed above.
- `17-aero.md` did not exist and the CFD was still running. Anything about aero is a statement of absence, not a finding about the result.
- The sum of growth-adjusted mass (about 287 kg) is the ledger's own planning rule, not a forecast.
- The 95th-percentile and weight-class comparisons rest on my own recall of population and competitor figures, which I did not look up.
- A "met" or "not met" label is my judgement against the target text in Gate A as written on November 22, 2026.
