# Bavuso V1 compliance: standards matrix

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Companion files: `13-dfmea.md` (risk table), `14-dvpr.md` (test plan and budget). Sources inside the program: `GATE-A-targets-locked.md`, `02-hardware.md`, `06-drive-performance.md`, `07-electrical.md`, `09-structures.md`, `10-thermal.md`. The older `detailed-design/compliance-and-validation.md` (Nov 12, a 328 kg bike with a different pack and motor) is out of date; I reused its regulation list and the NHTSA paperwork steps, and dropped its rev C CAD findings (turn-signal spacing, mirror size, tyre load) because the V1 CAD has not been re-checked against them.

## The plain answer

**V1 can be sold in the US with no emissions certification, but it has not been tested against a single standard. Everything below is paper.** The US route is self-certification: the maker states the bike meets every applicable FMVSS and files the paperwork with NHTSA. Nothing in the V1 design blocks that. The EU route (type approval) is a separate, larger job and stays "later".

Three things matter most:

1. **The battery is the compliance risk.** A 23.8 kWh, 100 kg pack needs UN 38.3 to ship, and its safety case (propagation, vents, crush) is the part that is least proven (`10-thermal.md`: it propagates in the worst case and with no coolant).
2. **Functional safety is a process, not a part.** The Orion BMS2 is not an ISO 26262 certified part. A proper hazard analysis, ASIL targets and fault-injection tests are needed before any production claim.
3. **Nothing here proves access to Tesla Superchargers.** A J3400 inlet is the connector; network authorisation is separate and open (`07-electrical.md`).

Status words: **met by design** = the design and a supplier document meet it on paper; **needs test** = the design should meet it but only a test proves it; **open** = a design decision, a document or a regulator answer is missing. "Evidence today" is always paper (supplier datasheet, calculation or simulation); no physical test exists. I did not read the paid standards (SAE, ISO, UL) and did not open the official URLs in this session (the fetch tool was blocked or redirected), so clause details come from public summaries and from the earlier study; confirm with a technical service before relying on them.

### Verdict summary

| Area | Rows | Met by design | Needs test | Open |
|---|---:|---:|---:|---:|
| US FMVSS and NHTSA paperwork | 15 | 4 | 2 | 9 |
| EPA / CARB | 3 | 0 | 0 | 3 |
| Battery | 7 | 0 | 6 | 1 |
| Charging | 7 | 2 | 3 | 2 |
| Functional safety | 4 | 0 | 0 | 4 |
| EU later | 9 | 0 | 0 | 9 |
| **Total** | **45** | **6** | **11** | **28** |

## 1. US vehicle rules (FMVSS, 49 CFR)

The motorcycle standards live in 49 CFR Part 571. Official text: `https://www.ecfr.gov/current/title-49/part-571` (each standard is `.../section-571.<number>`).

| Requirement | How V1 meets it | Evidence today | Status |
|---|---|---|---|
| **FMVSS 108** lamps and reflectors (`571.108`) | DOT-marked headlamp, tail/stop, four turn signals, plate lamp, red rear and side reflectors; the slim light band must sit in front of a certified lamp, not replace it | Lamp masses in `07-electrical.md` BOM; rev C failed spacing (front signals 236 mm apart vs 406 mm) and V1 CAD not re-checked | open (DFMEA D44) |
| **FMVSS 111** mirrors (`571.111`) | Two mirrors, glass at least the required area; fold-away | Rev C glass was 6,156 mm2 vs 8,065 mm2 flat; V1 not re-checked | open |
| **FMVSS 116** brake fluid (`571.116`) | DOT 4 fluid from a labelled supplier | Specified in the hardware shortlist class (not a named part) | met by design |
| **FMVSS 106** brake hoses (`571.106`, not in your list but mandatory) | DOT-marked hoses | Brake lines in the ledger; not named | met by design |
| **FMVSS 119** motorcycle tyres (`571.119`) | 110/80R19 and 150/70R17, V-rated (149 mph vs 130 mph governor); rear load margin large at the 355 kg solo gross | `02-hardware.md` (V rating); load index not checked against V1 GVWR | met by design (confirm load index) |
| **FMVSS 120** tyre selection and rims (`571.120`) | The standard's scope is vehicles other than passenger cars and, as I understand it, excludes motorcycles; motorcycle rim rules sit in 119 (rim marking, load rating) | Not confirmed in this session | open (confirm scope with NHTSA) |
| **FMVSS 122** motorcycle brake systems (`571.122`) | Dual 300 mm front discs, rear disc, Bosch ABS 10 class; friction brakes must pass with regen off; high-speed stop from 160 km/h; fade test | No stopping analysis from 125 mph (`02-hardware.md` fallback is 320 mm discs) | needs test (D34, D35) |
| **FMVSS 123** controls and displays (`571.123`) | ISO symbols, tell-tales (ABS, HV fault, ready), mph speedometer, left lever rear brake allowed on a bike with no clutch, side-stand interlock | Display and VCU in BOM; tell-tale list not written | needs test |
| **FMVSS 205** glazing (`571.205`) | Polycarbonate screen certified and marked by its supplier | Clear screen in the look target T10 | met by design (supplier certificate) |
| **49 CFR 567** certification label (`https://www.ecfr.gov/current/title-49/part-567`) | Label on the frame with GVWR and axle ratings; proposed GVWR about 355 kg (240 + 90 rider + 25 luggage, T7) | Label pad not in CAD | open |
| **49 CFR 566** manufacturer information (`.../part-566`) | File the maker's identity and VIN information within 30 days of starting manufacture (earlier study) | Administrative | open |
| **49 CFR 565** VIN (`.../part-565`) | World manufacturer identifier from SAE; stamped pad on the head tube | Not started | open |
| **Parts 573, 577, 579, 576** defects, recall, early warning and record keeping | Process, not design; small makers have reduced early-warning duties | None | open (process to set up) |
| **FMVSS 305** electric vehicle battery safety (`571.305`) | Applies to cars and trucks, not motorcycles, as I understand it | Not confirmed in this session | open (not applicable, confirm) |
| **FMVSS 141** quiet-car warning sound (`571.141`) | Motorcycles are excluded (earlier study) | Not confirmed in this session | open (confirm exclusion) |

## 2. EPA and CARB

| Requirement | How V1 meets it | Evidence today | Status |
|---|---|---|---|
| EPA exhaust and evaporative emissions (40 CFR 86 Subpart E, highway motorcycles; `https://www.epa.gov/vehicle-and-engine-certification`) | No combustion engine, so no exhaust or fuel-system emissions; EPA treats a battery-electric bike as having no tailpipe | Design: battery-electric only | open (get EPA's written "not subject" position when you file) |
| EPA motorcycle noise (40 CFR 205) | Electric bike far below limits; confirm the rule applies to EVs at all | Not measured | open |
| **California (CARB).** On-road motorcycles sold in California generally need a CARB Executive Order; zero-emission models have a short route and some labelling duties (`https://ww2.arb.ca.gov/`) | File a zero-emission motorcycle application when California sales begin; label content to be confirmed | I could not confirm the current CARB process or label text; from knowledge only | open |

## 3. Battery

| Requirement | How V1 meets it | Evidence today | Status |
|---|---|---|---|
| **UN 38.3** transport tests T1 to T8 (`https://unece.org/transport/dangerous-goods/un-manual-tests-and-criteria`) | Needed for the cell (ask Molicel for its report) and the pack, because a 23.8 kWh pack is a large battery | No report; P60B datasheet is version 0.1 | needs test (V17) |
| **49 CFR 173.185** shipping lithium batteries (`https://www.ecfr.gov/current/title-49/section-173.185`); UN3480 pack alone, UN3171 vehicle with battery | Pack shipped with state-of-charge and packaging limits; large-battery rules need a dangerous-goods specialist | None | open |
| **UL 2580** batteries for electric vehicles (`https://www.ul.com/` standards catalog) | Voluntary but expected by insurers and dealers; pack abuse and BMS safety evidence | None | needs test (V18) |
| **SAE J2464** EV battery abuse testing (`https://www.sae.org/standards/`) | Used as the abuse test basis: crush, short, overcharge, thermal ramp | None | needs test (V19) |
| **SAE J2929** safety standard for EV and hybrid propulsion batteries using lithium cells (`https://www.sae.org/standards/`) | Used as a design checklist for the pack: thermal propagation, vents, isolation, over-current protection | `10-thermal.md` propagation screen (model only); 490 mm2 per-group vent calculated | needs test (D01 to D04) |
| **ISO 6469-1 and -3** electric road vehicle safety (`https://www.iso.org/`) | Isolation 500 ohm/V (210 kohm fault set point), IPXXD boxes, bond below 0.1 ohm, HVIL, active discharge | Design values in `07-electrical.md`; active discharge not yet specified | needs test (V13) |
| **FCC Part 15** radio and electronics (`https://www.ecfr.gov/current/title-47/part-15`) | Keyless, telematics and inverter noise | No test | needs test (V46) |

## 4. Charging

| Requirement | How V1 meets it | Evidence today | Status |
|---|---|---|---|
| **SAE J3400** NACS connector (`https://www.sae.org/standards/`) | Volex J3400 inlet, 1,000 V, 500 A (supplier datasheet) | Supplier datasheet; J3400 text not read | met by design |
| **SAE J1772** pilot states and AC (`https://www.sae.org/standards/`) | J1772 control-pilot states A to F used for AC; EVCC reads them; AC and DC relays interlocked | Defined in `07-electrical.md`, not built | needs test (V23) |
| **ISO 15118-2/-20 and DIN SPEC 70121** DC communication | ADVANTICS-class EVCC; sessions without Plug and Charge first | EVCC is a class, not a verified part | needs test (V23) |
| **UL 2251** couplers and inlets (`https://www.ul.com/`) | Inlet sourced from a supplier listing J3400 and UL 2251 (Volex, per `07-electrical.md`) | Supplier claim, listing not verified | met by design |
| **UL 2202** EV charging system equipment and **UL 2231** personnel protection (`https://www.ul.com/`) | These cover the charging station and cord equipment, not the bike inlet. They matter only if V1 ships a portable cordset | V1 ships no cordset in the plan | open (decide whether to ship one) |
| Heat at the inlet: 137 A for 20 min through 35 mm2 | Inlet temperature sensor planned; cable is rated 161 A bundled | Hand calculation | needs test (V22) |
| Tesla Supercharger network access | A J3400 plug is not access; Tesla's manufacturer onboarding is vehicle-by-vehicle | No public path for a new motorcycle maker found (`07-electrical.md`) | open |

## 5. Functional safety

I have not done the hazard analysis; the ASIL values below are my **proposals** for it. ISO 26262-12 grades motorcycles with MSIL levels A to D; they correspond to ASIL.

| Function | Hazard | Proposed level | How V1 would meet it | Status |
|---|---|---|---|---|
| Throttle and torque control | Unintended or excessive drive torque | MSIL C (D if the hazard analysis finds low controllability at speed) | Dual throttle sensors, plausibility in VCU and inverter, safe state of torque to zero within the fault-tolerant time | open |
| Brakes and ABS | Loss of ABS; regen torque locking the rear wheel | MSIL B for ABS loss (base brakes stay hydraulic); MSIL C for regen lock-up | Hydraulic brakes independent of electronics; regen limited and blended; ABS warning lamp | open |
| BMS and contactors | Over-charge or over-temperature without a cut-off; welded contactor | MSIL C | Orion BMS2 is not a certified part; add an independent hardware over-voltage and over-temperature trip; weld check | open |
| Interlocks (stand, inlet lock, HVIL) | Drive away connected; inlet unlocks live | ISO 13849 performance level c as a design approach (non-electronic or simple electronic channels) | Mechanical plus electronic interlock | open |

References: ISO 26262 (`https://www.iso.org/standard/68383.html`, part 1; part 12 covers motorcycles), ISO 13849-1 (`https://www.iso.org/standard/73481.html`). ISO 26262 is not a US legal requirement; it is the development basis a buyer, insurer or investor will expect.

## 6. EU later

Not part of the V1 US launch. The earlier study's route (whole-vehicle type approval of an L3e-A3 under Regulation 168/2013) still holds. All rows below are open: V1 has no EU evidence and no EU design choices beyond what the US needs.

| Requirement | How V1 would meet it | Evidence today | Status |
|---|---|---|---|
| **Regulation (EU) 168/2013** framework (`https://eur-lex.europa.eu/eli/reg/2013/168/oj`) with delegated acts 3/2014 functional safety (`https://eur-lex.europa.eu/eli/reg_del/2014/3/oj`), 44/2014 construction (`.../44/oj`), 134/2014 environment and propulsion (`.../134/oj`) | Type approval through a technical service; conformity of production | None | open |
| **UN R136** electric power train of L-category vehicles (`https://unece.org/transport/vehicle-regulations-wp29`; EU text `https://eur-lex.europa.eu/eli/reg/2019/1120/oj/eng`) | Shock protection, isolation 100 ohm/V DC and 500 ohm/V AC, REESS vibration, thermal shock, mechanical shock, short, overcharge, over-discharge, over-temperature | Isolation design set point only; the propagation behaviour is the exposure | open |
| **UN R78** braking (UNECE regulation index above) | Category 3 bike with ABS; regen declared and tested | No brake analysis | open |
| **UN R53** installation of lighting devices (index above) | Lamp positions, angles, visibility | Same light-band question as FMVSS 108; the EU front signal spacing is also stricter | open |
| **UN R10** EMC (index above) | Drive and charge modes | None | open |
| **UN R81** mirrors | Glass fits a 78 mm circle | Rev C failed; V1 not re-checked | open |
| **UN R85** power measurement | Declared peak and 30-minute power | Dyno test planned | open |
| **UN R41** noise | Drive-by test | None | open |
| **EU Battery Regulation 2023/1542** (`https://eur-lex.europa.eu/eli/reg/2023/1542/oj`) | EV battery: carbon-footprint declaration, labelling, battery passport (earlier study dates the passport from February 2027) | None | open |

## What this does not prove

- Nothing here is a test result. The bike has not been built, so no standard has been run against it. "Met by design" means a supplier document and a paper design agree.
- I did not read any paid standard text and could not open the official pages; clause numbers and scope calls (FMVSS 120 and 305 scope, CARB labelling, EPA noise) are from the earlier study or from memory and may be wrong. Confirm each with NHTSA, EPA, CARB or a technical service.
- The ASIL levels are proposals; no hazard analysis, no safety concept and no FMEDA exist.
- The V1 CAD has not been checked against FMVSS 108, 111 or 123 geometry; the rev C failures may still apply.
- Supercharger access, Plug and Charge and UL listings of the inlet and EVCC are supplier claims or open questions.
