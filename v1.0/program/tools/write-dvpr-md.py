"""Generates program/14-dvpr.md from program/data/dvpr-v1.csv. Run from v1.0 after build-dfmea-dvpr.py."""
import csv, collections

rows = list(csv.DictReader(open('program/data/dvpr-v1.csv', encoding='utf-8')))
def esc(s): return s.replace('|', '/')
def usd(x): return "${:,.0f}".format(int(x))
us = [r for r in rows if r['phase'] != 'EU add-on']
eu = [r for r in rows if r['phase'] == 'EU add-on']
tot = sum(int(r['cost_usd_estimate']) for r in us)
eut = sum(int(r['cost_usd_estimate']) for r in eu)
byp = collections.OrderedDict((p, 0) for p in ['component', 'prototype', 'pre-production'])
for r in us: byp[r['phase']] += int(r['cost_usd_estimate'])
hw = sum(int(r['cost_usd_estimate']) for r in us if r['id'].startswith('HW'))
tests = tot - hw
ncomp = len([r for r in us if r['phase'] == 'component'])
ntests = len([r for r in rows if r['id'].startswith('V')])

t = f"""# Bavuso V1 DVP&R (design verification plan and report)

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Data: `program/data/dvpr-v1.csv` ({len(rows)} lines: {ntests} tests, 3 hardware build lines, 3 EU add-on lines). Generators: `program/tools/build-dfmea-dvpr.py` and `write-dvpr-md.py`. Risk rows (D01 to D46) are in `13-dfmea.md`; targets T1 to T10 are in `GATE-A-targets-locked.md`; the standards behind each test are in `12-compliance.md`. The earlier plan is `detailed-design/compliance/dvpr.csv` (62 lines, for a different bike); I reused its test list, methods and unit costs where they still apply and cut the sample counts.

## The plain answer

**Verifying V1 for a US launch would take about {usd(tot)} and about 28 months, and nothing in it has been done.** That is {usd(tests)} of tests plus {usd(hw)} for three hand-built mules, 12 extra test packs and eight pre-production bikes. Every line is **planned**. The money is an estimate (planning figures scaled from the earlier study, not quotes; plausible range 0.7x to 1.5x, about $4.9M to $10.6M). The EU add-on (R136 pack tests, braking, lighting, EMC, type approval) is another {usd(eut)} and is excluded from the headline.

The plan is shaped by the biggest risks:
- **Test first what can kill the design cheaply.** The EMRAX housing yoke proof (V08, about $70k, 6 weeks) decides the chassis architecture; the pivot rig (V07) and cast-arm fatigue (V06) follow. Do these before building mules.
- **The battery chain is the critical path.** Cell 2C charge life (V01, 26 weeks), lane-module propagation (V02), then UN 38.3 (V17); no bike or pack ships to a lab without UN 38.3.
- **Every target T1 to T10 has a closing test** except T9 (cost), which follows from quotes. Every High risk in `13-dfmea.md` has at least one test.

Phases: **component** = parts and modules on rigs, before any bike exists; **prototype** = the three mules and early test packs; **pre-production** = eight soft-tooled bikes and production-intent confirmation.

## Summary

| Phase | Base cost | Notes |
|---|---:|---|
| Component | {usd(byp['component'])} | {ncomp} rig tests; weeks 0 to 30 |
| Prototype | {usd(byp['prototype'])} | includes 3 mules ($450k) and 12 test packs ($264k) |
| Pre-production | {usd(byp['pre-production'])} | includes 8 bikes ($760k) |
| **US total** | **{usd(tot)}** | tests {usd(tests)} + hardware {usd(hw)} |
| EU add-on (later) | {usd(eut)} | not in the headline |

### Which test closes which target

| Target | Closing tests |
|---|---|
| T1 mass 240 kg | V38 (weigh every prototype), V06, V30, V31 |
| T2 pack safety and transport | V01 to V05, V13 to V21, V26 |
| T3 range 145 mi at 70 mph, CdA 0.38 | V35, V36 |
| T4 125 mph sustained, 130 governed | V33, V37, V09, V11, V25, V41 |
| T5 90 kW peak, 55 kW continuous | V10, V37, V08, V09 |
| T6 charging 10-80% in 25 min, NACS | V22, V23, V34 |
| T7 solo plus 25 kg luggage | V30, V31 (loads from `09-structures.md`) |
| T8 comfort, stability, functional safety | V06, V07, V15, V30, V31, V32, V39, V40, V42, V46, V47, V50 |
| T9 cost | no test; follows from the BOM and quotes (`cost-model.csv`) |
| T10 look and lighting rules | V44, V45 |

## Test plan

| ID | Test | Standard or procedure | Samples | Acceptance | Closes (target; risk rows) | Phase | Est. cost | Weeks |
|---|---|---|---|---|---|---|---:|---:|
"""
for r in rows:
    if r['id'].startswith('V'):
        dr = r['closes_dfmea_rows'].replace(';', ', ')
        closes = r['closes_target'] + ('; ' + dr if dr else '')
        t += f"| {r['id']} | {esc(r['test'])} | {esc(r['standard_or_procedure'])} | {esc(r['samples'])} | {esc(r['acceptance'])} | {closes} | {r['phase']} | {usd(r['cost_usd_estimate'])} | {r['duration_weeks']} |\n"
t += "\n### Hardware builds and EU add-on\n\n| ID | Line | Samples | Phase | Est. cost | Weeks |\n|---|---|---|---|---:|---:|\n"
for r in rows:
    if r['id'].startswith(('HW', 'EU')):
        t += f"| {r['id']} | {esc(r['test'])} | {r['samples']} | {r['phase']} | {usd(r['cost_usd_estimate'])} | {r['duration_weeks']} |\n"
t += """
All status fields in the CSV read **planned**. There are no result or date columns because nothing has been run.

## Build-and-test timeline (weeks from go, about 28 months)

| Weeks | What happens |
|---|---|
| 0 to 6 | EMRAX written answer on the yoke; V08 yoke proof; V15 hazard analysis starts; V01 cell tests start; V03 and V04 vent and bond tests |
| 6 to 30 | Component rigs: V02 propagation, V05, V06 arm, V07 pivot, V09 belt, V10 dyno, V11 brake dyno, V13, V14, V22, V25, V26. Decision gate at week 14: yoke, pivot, vent and brake size confirmed, then freeze CAD for the mules |
| 12 to 32 | HW1: build three mules (20 weeks); HW2 test packs |
| 30 to 70 | Prototype tests: V16 to V21, V23, V30 to V43; V17 (UN 38.3) must finish before packs travel; V31 fatigue runs 16 weeks |
| 60 to 76 | HW3: eight pre-production bikes on soft tooling |
| 70 to 112 | V44 to V47, V50 (30 weeks, 3 bikes x 30,000 km), V51 confirmation |
| 108 to 118 | V52: US self-certification file, Parts 565, 566, 567 |
| After 118 | EU1 to EU3, about 16 weeks, only if the EU market is pursued |

Critical path: V01 cell data, V02 propagation, V17 UN 38.3, pre-production build, V50 durability, V52 filing. A failure of V08 (yoke) or V02 (propagation) re-opens the design and moves everything after it.

## What this does not prove

- Nothing here has been tested; every status is "planned". All costs and durations are planning estimates scaled from the Nov 12 study (a heavier bike with an EU launch), not quotes from a lab, track or technical service. I contacted no one.
- The headline excludes engineering salaries, tooling, fees outside the listed filings, insurance, facility build-outs and contingency beyond the 0.7x to 1.5x range. The earlier plan (about $10.9M, with EU approval, 24 packs, 12 DV2 bikes and 4 x 40,000 km fleets) is not directly comparable.
- Acceptance numbers come from the target documents and the earlier plan; some (V51 "within tolerance", the 2,000 h pump run) need the lab's own criteria. UN R136 and SAE J2464 procedures were not read in full.
- Sample counts are small (2 to 3 bikes, 1 to 4 packs). They support engineering decisions, not statistical reliability claims.
- No measured road-load data exist, so the 160,000 km spectrum in `09-structures.md` is still an assumption; real data may change V31.
"""
open('program/14-dvpr.md', 'w', encoding='utf-8').write(t)
print(tot, tests, hw, eut, dict(byp), ncomp)
