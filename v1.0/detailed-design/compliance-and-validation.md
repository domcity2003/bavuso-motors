# Bavuso V1.0: safety, crash, homologation and validation plan

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5).

- **Scripts:** `detailed-design/tools/compliance-tipover.py`, `compliance-pack-protection.py`, `compliance-dvpr.py` (bundled FreeCAD python; scipy's hull is blocked on this machine, so the tip-over pose uses a grid search instead).
- **Data:** `detailed-design/compliance/requirements-matrix.csv` (52 requirements), `dvpr.csv` (62 lines), `tipover-results.json`, `pack-protection-results.json`, `dvpr-summary.json`.
- **CAD read:** `tools/build-adventure.py` as of Nov 12 (read only, not edited). Coordinates below are **model coordinates** (ground at Z = −40) unless marked "ground".

## The plain answer

**The bike can be made legal in the US and the EU. Nothing in the layout blocks it.** Today, though, the CAD fails four rule checks and three crash checks, and it has no validation evidence at all.

**Four rule failures, all cheap to fix:**

1. **Front indicators are too close together.** Their centres are 236 mm apart. The US rule (FMVSS 108) needs 406 mm, and they sit 2 mm from the headlamp, where 102 mm is needed. The EU rule (UN R53) fails too.
2. **The mirror glass is too small.** It measures 114 × 54 mm, which is 6,156 mm². The US needs 8,065 mm² (flat). The EU (UN R81) needs a 78 mm circle to fit inside the glass, and 54 mm is too short.
3. **Some legally required parts are missing from the CAD:** the rear and side red reflectors, the horn, the side stand, the VIN pad and the certification label.
4. **The rear tyre load margin is thin.** The 160/60ZR17 69W is rated for 325 kg, about 6% over the rear axle load at a 487 kg gross weight. The 170/60ZR17 72W named in the brief gives 16%.

**Three crash findings:**

1. **With no guards, a standing tip-over lands on the plastic belly.** The bike comes to rest on the brake lever tip, the peg bracket and the 3 mm belly cover. The 4 mm structural pack case is then **8 mm** from the asphalt. About **660 J** goes into that fall, and the lever tip hits at 4.4 m/s.
   - With the proposed guards it rests on the steel guard and the handguard instead. The pack stays **70 mm** off the ground, the levers 19 mm and the mirrors 44 mm.
2. **The cells have no crush zone.** Their ends sit **2 mm** inside the pack's side wall, and the bottom row sits **1 mm** above the floor. Any dent in the case reaches a cell.
   - The 4 mm skid plate collapses at about **4.9 kN** under a rock. A 3 g bottom-out with a rider is **11.4 kN**.
   - **Fix:** a 6 mm 5083 skid (collapses at 12.2 kN), a 10 mm crush zone inside the pack floor and side walls, and internal webs at most 150 mm apart.
3. **The pack case walls need internal webs.** Under the UN 38.3 shock test (15 g for a 134 kg pack), an unbraced 4 mm side wall reaches **370 MPa**. With webs every 150 mm it reaches about 100 MPa.

**Validation:**

- **Budget:** about **$10.9M** at the base case (range $7.6–16.3M). That is $8.1M of tests plus $2.8M of prototype bikes and packs.
- **Time:** about **120 weeks (28 months)** from the first mule build to US self-certification and EU type approval.
- **Funding gap:** that is about **3 times** what `startup-costs.csv` holds for prototypes, cell testing and compliance ($3.5M at 1,000 bikes a year).

## Verdict table

| Item | Value | Required | Margin | Result |
|---|---|---|---|---|
| Front turn-signal spacing (US) | 236 mm centres | ≥ 406 mm (FMVSS 108) | −42% | **Fail** |
| Front turn signal to headlamp (US) | ~2 mm | ≥ 102 mm edge to edge | — | **Fail** |
| Front indicators, inner edges (EU) | ~208 mm | ≥ 240 mm (UN R53, value to confirm) | −13% | **Fail** |
| Rear turn-signal spacing | 262 mm | ≥ 229 mm | +14% | Pass |
| Mirror glass area (US) | 6,156 mm² | ≥ 8,065 flat / 6,450 convex | −24% / −5% | **Fail** |
| Mirror glass height (EU) | 54 mm | must contain a 78 mm circle (R81) | −31% | **Fail** |
| Mirror centre outboard | 350 mm | ≥ 279 mm | +25% | Pass |
| Headlamp / tail-lamp height (ground) | 856–896 / 846–866 mm | 559–1372 / 381–1829 mm | in range | Pass (units not chosen) |
| Rear reflectors, horn, side stand, VIN, 567 label | absent | required | — | **Open (gap)** |
| Rear tyre load index at 487 kg GVWR (63% rear) | 325 kg (69W) | ≥ 307 kg | +6% | Pass, thin; 170/60 72W gives +16% |
| Rear brake on left lever (no clutch) | yes | allowed by FMVSS 123 S5.2.1 and R60 | — | Pass |
| Tip-over as CAD: pack-case height above ground at rest | 8 mm (belly cover touching) | > 0, no HV contact | — | **Fail** |
| Tip-over with guards: pack-case side above ground | 70 mm | > 0 | — | Pass (calc) |
| Tip-over with guards: lever / mirror clearance | 19 / 44 mm | > 0 | — | Pass (calc) |
| Tip-over energy, rider off | 512 J guarded (663 J as CAD); 720 J with 40 kg luggage | — | — | Design input |
| Guard collapse load (28 × 2.5 25CrMo4 loop, 400 mm span) | 14.2 kN | fuse below anchor strength | — | Design |
| Guard anchors: 2 × M10 10.9 each, shear | 69.6 kN | 21.3 kN (1.5 × collapse) | ×3.3 | Pass (calc; lug not checked) |
| Guard set after a free fall (all energy plastic) | up to 18 mm | ≤ 5 mm | — | **Open** (test DV-C01) |
| Skid plate 4 mm 5052: collapse vs 3 g bottom-out | 4.9 kN vs 11.4 kN | ≥ 1.0 | 0.43 | **Fail** |
| Skid plate 6 mm 5083-H321 | 12.2 kN | ≥ 11.4 kN | 1.07 | Pass (thin) |
| Skid plate elastic deflection at 1 g high-centre (6 mm) | 4.7 mm | < 16 mm gap | ×3.4 | Pass |
| Pack floor 4 mm 6061-T6, if the skid fails | 6.0 kN; 1 mm to cell | ≥ 11.4 kN | 0.53 | **Fail** → crush zone |
| Side wall 4 mm, UN 38.3 T4 (15 g), unbraced 375 mm span | 370 MPa | ≤ 160 MPa (6061-T6 / 1.5) | 0.43 | **Fail** |
| Side wall 4 mm with webs at ≤ 150 mm | 100 MPa | ≤ 160 MPa | ×1.6 | Pass |
| Floor 4 mm under 15 g, cooling plate/webs at 125 mm | 57 MPa | ≤ 160 MPa | ×2.8 | Pass |
| Side crush zone (cover gap + gap inside the wall) | 15 mm (2 mm inside the case) | ≥ 25 mm proposed (≥ 10 inside) | — | **Fail** |
| Static ground clearance (rider-on) | 216 mm | ≥ 200 mm | +8% | Pass |
| Skid clearance, front and rear at full bump | ~77 mm | > 0 | — | Pass |
| Breakover angle (flat skid) | 32.4° | ≥ 28° | +4° | Pass |
| Guard lean clearance, lower loop | ≈ 50° | ≥ 45° | +5° | Pass (calc) |
| Fording: IP67 needed below 550 mm | pack, HV cabinet, gear case, motor, hubs | IP67 + vents ≥ 650 mm | — | **Open** (no spec) |
| Validation budget | $10.9M base ($7.6–16.3M) | in `startup-costs.csv`: $3.5M | −$7.4M | **Open (funding)** |
| Validation duration | 120 weeks | — | — | Plan |

## 1. Requirements matrix

The full matrix is `compliance/requirements-matrix.csv`. It covers 52 requirements, each with what the rule demands, the part that meets it, the evidence in the repo, its status, the gap and the test that proves it.

| Status | Count |
|---|---|
| FAIL | 4, plus 3 crash fails |
| Gap | 6 |
| Partial | 9 |
| Met in CAD | 2 |
| Open | 25 |
| N/A | 2 |

**What it says, by area:**

### Lighting (FMVSS 108; EU UN R53 + R148/R149/R150)

- All lamp heights are legal.
- The full-width "light band" is styling. A certified DOT/E-marked LED module still has to sit behind it, and so far only reservations exist.
- **Fails:**
  - **Front indicator spacing and headlamp separation:** fix with CR-9.
  - **No rear red reflector and no red rear side reflectors:** fix with CR-10.
- The stop lamp has to light from either lever. If regen braking is strong, it should also light from regen deceleration.

### Mirrors (FMVSS 111 S10; EU UN R81)

The glass is too small for both markets. CR-5 fixes it.

### Brakes (FMVSS 122, category 3-3; EU UN R78, both derived from GTR 3)

There is no brake sizing study yet. The 60 km/h dry-stop limits are:

| Brakes used | Formula | Distance |
|---|---|---|
| Front only | S ≤ 0.1V + 0.0087V² | 37.3 m |
| Rear only | S ≤ 0.1V + 0.0133V² | 53.9 m |
| All controls (from 100 km/h) | S ≤ 0.0060V² | 60 m |

- **High-speed test:** at 160 km/h (Vmax ≥ 200 km/h), S ≤ 0.1V + 0.0067V².
- **Heat fade:** S2 ≤ 1.67·S1 − 0.067V.
- **ABS:** ABS tests apply, and ABS is mandatory on an EU L3e.
- **Regen:** the friction brakes must pass with regen off. Under R78, regen has to be declared and tested.
- **Hoses:** FMVSS 106 (brake hoses) is not in the brief but is mandatory.
- **Fluid:** FMVSS 116, DOT 4.

Source: [49 CFR 571.122](https://www.law.cornell.edu/cfr/text/49/571.122).

### Controls (FMVSS 123; EU UN R60)

- The left lever can legally be the rear brake on a bike with no clutch.
- Still missing:
  - side stand with a drive interlock;
  - mph speedometer;
  - Table 3 telltales;
  - ignition/key.

### Tyres and rims (FMVSS 119/120; EU R75)

- Fit 170/60ZR17 72W on a 17 × 5.00 rim, not the 160/60 in the CAD.
- The rim must be marked.

### Glazing (FMVSS 205)

The polycarbonate screen must be certified and marked AS-4 or AS-6 by the glazing supplier.

### Noise

- **US:** EPA motorcycle noise (40 CFR 205) is probably written for engines. Confirm that it applies to EVs; the bike will be far under 80 dBA either way. **FMVSS 141 (pedestrian warning sound) excludes motorcycles**, so the US has no minimum-sound rule.
- **EU:** UN R41 drive-by test under 134/2014 Annex IX. A pedestrian warning sound (AVAS) is optional for electric L-category bikes. Verify this in the annex text.
- **Emissions:** EPA/CARB exhaust and evaporative rules don't apply to a battery-electric bike.

### NHTSA paperwork

| Item | What it needs |
|---|---|
| Part 565 (VIN) | Apply for a WMI code from SAE. Reserve a stamping pad on the head tube. |
| Part 566 | Manufacturer filing, within 30 days after manufacturing starts. |
| Part 567 | Certification label on the frame, with GVWR and GAWRs. Proposed GVWR is 487 kg. |
| Parts 573/577/579 | Recall and early-warning reporting. |
| Hazmat (49 CFR 171–180) | UN 38.3 for shipping packs and bikes (UN3480 for a pack alone, UN3171 for a bike). |
| FCC Part 15 | Electronics emissions. |

### EU route

- Whole-vehicle type approval for an **L3e-A3** under 168/2013, with the delegated acts:
  - 3/2014 (functional safety);
  - 44/2014 (construction: stands, plates, handholds);
  - 134/2014 (environment and propulsion: R85 power, range, noise).
- Electrical safety by **UN R136**:
  - **Shock protection:** IPXXB everywhere, IPXXD where luggage could touch HV parts.
  - **Isolation:** ≥ 100 Ω/V on DC buses, ≥ 500 Ω/V on AC buses, and ≥ 1 MΩ at the charge coupler when unplugged.
  - **Water:** a water-ingress test.
- **REESS tests** (R136 Part II):
  - 6.2 vibration;
  - 6.3 thermal shock;
  - 6.4.1 drop test, which is N/A because the pack is fixed;
  - **6.4.2 mechanical shock for vehicles with a side or centre stand (a fall-down test);**
  - 6.6–6.9 electrical abuse;
  - fire test only for vehicles with a passenger compartment, so N/A.
- Acceptance for all of these: no electrolyte leak, rupture, fire or explosion, and isolation still ≥ 100 Ω/V. Source: [EUR-Lex 2019/1120, UN R136 text](https://eur-lex.europa.eu/eli/reg/2019/1120/oj/eng).
- **EMC:** UN R10 in drive and charging modes.
- **EU Battery Regulation 2023/1542:** this pack is an "EV battery" (an L-category traction battery over 25 kg). That brings a carbon-footprint declaration, labelling, due diligence and the **battery passport** (from Feb 2027).

### Battery standards named in the brief

- **UN 38.3** (transport) is mandatory in both markets. For a 134 kg "large battery", T4 shock is min(50 gn, √(30000/m)) = **15 gn, 11 ms**.
- **IEC 62133-2** covers portable cells and **ISO 6469** covers cars. For a motorcycle the correct test bases are **IEC 62660-1/-2/-3** (traction cells), **ISO 18243** (motorcycle Li-ion battery systems) and **ISO 13063** (motorcycle electrical safety).
- **UL 2271** is not law in the US, but dealers and insurers expect it.

**Not fully verified:**

- The numeric annex parameters of UN R136 (8A vibration levels, the exact 8D fall-down procedure, the 9B water test). The EUR-Lex page did not expose the annex text, so the DVP&R treats them as "per annex".
- The R53 front-indicator 240 mm value.
- EPA noise applicability to EVs.

Confirm these with the technical service.

**Crush is not an R136 test.** The regulation says it does not cover post-crash safety. I still set an internal pack-crush target (100 kN with a 75 mm half-cylinder, the GB 38031 / SAE J2464 practice), because the pack is a frame member low in the bike.

## 2. Crash and impact

### 2.1 Standing tip-over

**Method:**

- The bike is a rigid body with both tyres as tori, 287.2 kg, CoG 803 mm ahead of the rear axle and 501 mm high.
- It falls sideways with the bars straight ahead and settles on the pose of least potential energy among its outer hard points.
- Folding pegs and mirrors don't count as supports; their positions are only reported.
- **Hand check:** the energy equals m·g·Δh. For the guarded case, 287.2 × 9.81 × (0.501 − 0.319) = 513 J, against 512 J from the script. ✓
- **Roll inertia:** 25 kg·m² about the CoG is an assumption. Cossalter's data for large bikes is 15–30.

| Case | Rest lean | CoG at rest | Supports | Energy | Fastest contact |
|---|---|---|---|---|---|
| As CAD | 74° | 266 mm | brake lever tip, peg bracket, 3 mm belly cover | 663 J | lever tip 4.4 m/s |
| With CR-1…CR-3 | 79° | 319 mm | lower guard (two points), handguard bar end | 512 J (720 J with 40 kg luggage) | handguard 3.9 m/s; guard 1.3 m/s |

Without guards, the lever snaps and the pack case lies 8 mm under a crushed plastic cover. That fails R136 6.4.2 in spirit, because a dented pack wall has 2 mm to the cell caps.

With guards, every protected part sits clear of the ground:

| Part | Height above ground |
|---|---|
| Battery panels | 70 mm |
| Pivot slider | 28 mm |
| Mid-guard puck | 27 mm |
| Mirror | 44 mm |
| Shortened lever | 19 mm |

The radiators sit 44 mm inside the tank skin and well clear.

**Guard sizing:**

| Section (25CrMo4, Rp0.2 ≥ 435 MPa) | Collapse load, 400 mm loop span | Mass |
|---|---|---|
| 25.4 × 2.0 | 9.6 kN | 1.15 kg/m |
| **28 × 2.5 (chosen)** | **14.2 kN** | **1.57 kg/m** |
| 30 × 3.0 | 19.1 kN | 2.00 kg/m |

- **Mass:** about 2.6 m of tube per side, so about 8.5 kg for the pair with brackets and pucks.
- **The guard is the fuse.** The anchors are designed to 1.5 × the collapse load, **21.3 kN**, with no yield. Then a crash bends a cheap guard, never a pack lug.
- **Anchor placement:** the guard anchors to the **upper-rail node, the pack front lug and the rear-link lug**. These are existing primary structure, and the guard never touches a pack wall.
- **The FEA agent should add a 21 kN outward load at those three lugs.**

**Honest limit:**

- A steel tube stores only about 5 J elastically. A free (rider-off) fall puts about 250 J into the front guard, so it may take a set of up to about 18 mm unless the pucks, the tyres and the bodywork absorb part of it.
- Real adventure bikes behave the same way: rider-assisted drops leave no mark, and free falls sometimes bend the bars.
- **The acceptance target:** no set after a rider-assisted fall, ≤ 5 mm after a free fall, and only the pucks replaced. Test DV-C01 decides it.

### 2.2 Low-side slide

| Speed | Kinetic energy (bike only) | Slide distance (μ 0.35–0.5) | Slide time |
|---|---|---|---|
| 30 km/h | 10 kJ | 7–10 m | 1.7–2.4 s |
| 50 km/h | 27.7 kJ | 20–28 m | 2.8–4.0 s |
| 80 km/h | 70.9 kJ | 50–72 m | 4.5–6.5 s |

- **The first impact** (CoG dropping from 45° lean to rest) is about 100 J, which is less than a standing tip-over. **The issue in a slide is abrasion, not impact.**
- **The pucks wear away while the bike slides.** POM pucks with **20 mm of sacrificial depth** go at the guard's widest point, the pivot and (optionally) the tail.
- The pack must never touch the road, even with 15 mm of puck worn. With the guard geometry, the pack still sits about 55 mm clear.
- **Not calculated:** a puck wear rate. Test DV-C02 measures it.

### 2.3 Pack penetration and crush (bottom and sides)

**Load cases** (bike + 85 kg rider + 15 kg luggage = 387 kg):

- **S1, high-centring on a rock:** 1 g = 3.8 kN.
- **S2, bottom-out on a 50 mm rock:** 3 g = 11.4 kN.

**Method:** a plate under a point load collapses at P = 2π·Mp, with Mp = σy·t²/4 (the yield-line fan). The elastic numbers come from Roark, 7th ed., Table 11.4.

| Plate | Collapse load | S2 margin | Mass (extended plate) |
|---|---|---|---|
| CAD 4 mm 5052-H32 | 4.9 kN | **0.43** | 2.5 kg |
| **6 mm 5083-H321** | 12.2 kN | **1.07** | 3.7 kg |
| 8 mm 5083-H321 | 21.6 kN | 1.90 | 4.9 kg |
| 5 mm 7020-T6 | 11.0 kN | 0.96 | 3.2 kg |
| Pack floor 4 mm 6061-T6 (backup) | 6.0 kN | 0.53 | — |

**Choice: 6 mm 5083-H321, with two stamped longitudinal ribs and rubber-isolated mounts.**

- It is the lightest plate that passes, and 5083 tolerates dents and seawater.
- It adds +1.2 kg compared with the current plate extended.
- Its margin is thin (1.07), so the rock-strike test (DV-C03/P10) sets the final gauge. 8 mm is the fallback.

**The pack floor is the second layer.** Today the bottom cells are only 1 mm above the 4 mm floor (`CLR = 1`). A 10 mm crush and cooling zone under the bottom row (CR-8) means a dented skid never reaches a cell.

**Sides:**

- The cells lie across the bike, so **their caps face the side walls**, 2 mm away.
- Side intrusion therefore loads the cells along their axis, onto the terminal. That is the worst way to crush a cylindrical cell.
- **With the guards, no tip-over or slide load reaches the wall.**
- For a crash the guard doesn't cover, CR-7 widens the case 10 mm per side to make a 10 mm busbar/crush zone. The body width at the pack grows from 414 to 434 mm, still less than the V1.0 road model's 444 mm. The rider's knees are higher, at the tank, so they are unaffected.

**Inertia (UN 38.3 T4, 15 gn, 107 kg of cells, about 15.7 kN on one wall):**

| Wall | Stress | Allowable |
|---|---|---|
| 4 mm side, unbraced 375 mm span | 370 MPa | 160 MPa (6061-T6 / 1.5) |
| 4 mm side, webs every 150 mm | 100 MPa | 160 MPa |
| 4 mm floor, 125 mm bays | 57 MPa | 160 MPa |

**Hand check:** a 1 mm strip of the side wall as a simply supported beam over 150 mm gives M = qL²/8 = 278 N·mm and σ = 6M/t² = 104 MPa, against Roark's 100. ✓

- The same webs carry R136 vibration and the tip-over deceleration (about 15 g, the same order).
- They double as busbar bays and cooling-ribbon anchors (CR-8).

### 2.4 Ground clearance and fording

**Clearance:**

| Item | Value |
|---|---|
| Static clearance, rider-on | 216 mm |
| Skid clearance at full bump front and rear | ≈ 77 mm |
| Breakover angle (flat skid) | 32.4° |
| Lean before the lower guard touches | ≈ 50° (pegs about 51°, fold) |

**The HV cabinet is exposed.** It sits behind the skid, 245 mm above ground, and only a 3 mm plastic cover is underneath it. CR-6 extends the skid back to X430 to cover it.

**Fording:**

- **Rated depth: 450 mm of standing water at walking pace, plus 100 mm of bow wave.** Everything below **550 mm (ground)** must be IP67 (1 m for 30 min):
  - pack (case bottom at 238, top at 613.5);
  - HV cabinet (245);
  - gear case (315);
  - motor (410);
  - wheel bearings (312–325);
  - all HV and LV connectors below that line.
- The charger (630), radiators (640), inverter (715) and BMS (820) are above it, but in spray, so IP6K9K / IP67 still apply.
- **The real hazard is a hot pack driven into cold water.** A 40 °C pack plunged into 10 °C water loses about 10% of its internal pressure. Without a vent, that pressure drop pulls water past the seals.
- **Fix:** a pressure-equalising membrane vent with emergency burst function on the pack, plus breathers on the gear case and motor, all routed to **≥ 650 mm ground** (CR-14). Test DV-T05 proves it.

## 3. DVP&R, budget and timeline

The full plan is in `compliance/dvpr.csv`. It holds 58 tests plus 4 hardware lines. Each line has the method or standard, acceptance criteria, sample count, low/base/high cost, duration, start week, dependencies and the requirement IDs it closes. Costs are planning estimates (low = 0.7 ×, high = 1.5 × base), not quotes.

| Phase | Weeks | What happens | Base cost |
|---|---|---|---|
| DV0 | 0–16 | Seating buck and rider clinic, cell abuse characterization, functional-safety work starts | $0.25M |
| DV1 | 12–60 | 4 mules: brake dyno, motor dyno/R85, frame static and rig durability, proving-ground load data, wind tunnel, UN 38.3, R136 pack tests, propagation, crush, skid and guard tests | $4.6M |
| DV2 | 40–94 | 12 bikes: road simulator, brake compliance, ABS/regen calibration, climate, wading/IP, EMC, tip-over and low-side, lighting/mirrors, 160,000 km fleet, off-road durability, ride clinic | $4.6M |
| PV | 86–112 | 10 bikes from production tooling: confirmation repeats, range | $1.0M |
| Homologation | 104–120 | US self-certification file and Part 566/567; EU L3e-A3 type approval with witnessed tests and CoP | $0.41M |
| **Total** | **120 weeks ≈ 28 months** | | **$10.86M** (low $7.6M, high $16.3M) |

**Biggest lines:**

| Line | Cost |
|---|---|
| Prototype hardware | $2.76M |
| Battery tests | $1.52M |
| Road and rig durability | $1.44M |
| Structures | $0.92M |
| Brakes | $0.58M |
| Drive | $0.51M |

**Sample counts:**

- 4 DV1 mules, 12 DV2 bikes and 10 PV bikes.
- 24 test packs beyond the ones in vehicles, plus about 60 cells and 12 modules.

**Critical path:** cell characterization → pack thermal → UN 38.3 → R136 pack tests → DV2 vehicle tests → PV → type approval. The pack chain matters because no bike can be shipped to a lab without UN 38.3.

**Funding gap:** `startup-costs.csv` (1,000 bikes a year) holds only $1.8M for prototypes, $0.7M for cell testing and $1.0M for compliance, so **$3.5M against $10.9M needed**. Engineering salaries are separate in both.

## CAD change requests

All in model coordinates (ground = Z + 40), mm. Each mirrors to the right side (−Y). **New checks the CAD agent must add:**

- every guard part ≥ 20 mm from the front tyre and fender over the lock × bump sweep;
- guard ≥ 10 mm from the body;
- guard ≥ 80 mm from the rider's boot at the peg;
- handguard ≥ 30 mm from the tank and screen at full lock.

1. **CR-1 Front crash guard (each side).**
   - **Tube:** 28 × 2.5 25CrMo4, bend radius ≥ 2.5D, powder-coated.
   - **Centreline:** anchor A on the upper-rail node (1040, ±195, 770) → B (1075, ±271, 640) → C (1040, ±276, 430) → D (900, ±276, 250) → E (700, ±266, 250) → anchor F on the rear-link lug (575, ±190, 365), via a 6 mm bracket. Add a strut from C to the pack front lug (1067, ±197, 470).
   - **Anchors:** each with 2 × M10 10.9, designed to 21.3 kN.
   - **Pass-throughs:** grommets where the tube crosses the tank skin (Y ±222) and the lower cover (Y ±207).
2. **CR-2 Handguards and levers.**
   - **Handguard:** aluminium backbone, Ø22 × 3 6082-T6. Inner clamp on the bar at (980, ±215, 1120); bar-end clamp at (870, ±430, 1076), outer face Y ±445; forward loop to (955, ±440, 1072).
   - **Levers:** shorten both levers by 25 mm (150 → 125 mm along the grip), so they end inside the guard.
3. **CR-3 Pivot slider.** A Ø50 × 30 mm POM puck on an M10 into the pivot stub end, centre (540, ±247, 350), face at Y ±262. It passes through the pivot cap.
4. **CR-4 Pucks (optional tail slider).** POM pucks with 20 mm of sacrificial depth at B and C, faces at Y ±300 and ±305. Optional tail puck at (300, ±230, 660), face Y ±245, on a bracket from the tail rail at (300, ±154, 747).
5. **CR-5 Mirrors.** Glass ≥ 125 × 80 mm (flat; about 9,500 mm² with R10 corners) or convex R1000–1500 at ≥ 110 × 80. The head grows to about 150 × 100. Centre stays at Y ±350, Z ≈ 1230.
6. **CR-6 Skid plate.**
   - **Plate:** 6 mm 5083-H321 (was 4 mm), X430–1090, Y ±175, bottom Z176 (the gap to the pack becomes 16 mm).
   - **Ribs:** two stamped 12 mm ribs at Y ±80.
   - **Ends:** front lip upswept 35° from X1090 to about X1125; rear upswept 30° from X445 to X430, under the HV cabinet and gear case.
   - **Mounts:** six M8 rubber-isolated mounts on the pack and frame lugs.
   - **Checks to keep:** cabinet_vs_skid, and the new skid_vs_front_tyre sweep.
7. **CR-7 Pack side crush zone.**
   - Widen the case: YO 194 → 204, side wall 4 → 6 mm, so the inner gap from the cell end grows from 2 to 10 mm (YI = 198).
   - Lower covers ±207 → ±217; battery and belly panels ±222 → ±232.
   - Re-run lower_body_vs_pack and the front-tyre lock sweep.
8. **CR-8 Pack internals.**
   - A bottom crush and cooling zone: the bottom-row clearance goes from 1 to 10 mm (cells move up 9 mm; pack top 613.5 → 622.5 ground). Re-check charger_vs_pack ≥ 10.
   - Transverse 3 mm webs every ≤ 150 mm in X, tying both side walls and the floor.
9. **CR-9 Front indicators.** Centres at Y ±205, X ≈ 1300, Z 690 on the fairing cheeks: 410 mm apart and ≥ 102 mm from the lamp band (Z816–856).
10. **CR-10 Reflectors.** A red rear reflector, Ø60, at (−190, 0, 760). Red side reflectors on the tail sides at (−80, ±123, 760).
11. **CR-11 Horn.** An R28 class I horn at (1120, −170, 600), splash-shielded. This position is 180 mm from the steering axis, outside the 140 mm sweep; check it against the radiator and the tyre lock sweep.
12. **CR-12 Side stand.**
    - Pivot on a left bracket off the rear-link lug at (560, +200, 260). Foot at about (640, +330, −40), giving the bike about 8° of lean.
    - Stand-down interlock switch. A centre-stand option for touring.
13. **CR-13 Identification.** A VIN stamping pad on the head tube, right side, at (1180, −31, 850). A 75 × 50 mm pad for the Part 567 certification label and the EU statutory plate on the right upper rail at (1000, −195, 760).
14. **CR-14 Vents and breathers.** A pack membrane vent with burst disc on the pack top-rear at (720, 0, 573), with its tube routed to Z ≥ 700 under the seat. Gear-case and motor breathers routed to Z ≥ 700. Discharge pointed away from the rider and down-left.
15. **CR-15 Tyre.** Rear 170/60ZR17 72W on a 17 × 5.00 rim (CAD has 160/60 on 17 × 4.50). Update RR and the rear sweeps.

## What this does not prove

- **No physical test exists.** Every crash number is a hand calculation or a rigid-body estimate.
- **Tip-over pose:**
  - Bars straight ahead only. Parked bikes usually sit at full left lock, which moves the bar-end contact.
  - Tyre deflection, bodywork crushing and the rider's hand are all ignored.
  - The 25 kg·m² roll inertia is assumed.
  - The 50% share of energy into the guard is an assumption.
- **The guard was not checked for:** clearance against the steered tyre, the rider's boot and the bodywork in the full CAD; the strength of the frame and pack lugs (that belongs to the FEA agent); or puck wear rate.
- **Plate formulas:**
  - The skid collapse is a yield-line estimate. It ignores membrane stiffening, which helps, and a sharp edge cutting through, which hurts.
  - The rock size and the 3 g factor are design choices, not measured loads.
- **Pack:**
  - Cell axial crush tolerance, swelling, busbar layout and the case material (6061-T6 was assumed) are not from supplier data.
  - Thermal propagation is not analysed.
- **Regulations:**
  - The numeric parameters of UN R136 Annexes 8A, 8D and 9B, the R53 front-indicator spacing value and EPA noise applicability to EVs were not read from the source text. Confirm them with the chosen technical service.
  - Requirement status is checked against the CAD reservations, not real lamp, mirror or brake hardware.
- **Budget:** the costs are planning figures with no lab quotes. The 120-week timeline assumes no major redesign loop. A failed R136 or brake test typically adds 8–12 weeks.

## Sources

- FMVSS 122 (motorcycle brakes): https://www.law.cornell.edu/cfr/text/49/571.122
- FMVSS 111 S10 (motorcycle mirrors): https://www.law.cornell.edu/cfr/text/49/571.111
- NHTSA interpretations on motorcycle turn-signal spacing (16 in front centres, 4 in to the headlamp, 9 in rear): https://www.nhtsa.gov/interpretations/1985-0142, https://www.nhtsa.gov/interpretations/nht87-15, https://www.nhtsa.gov/interpretations/86-233
- UN R136 as published in the EU OJ (scope, 5.1.3 isolation, 6.2–6.9 REESS tests): https://eur-lex.europa.eu/eli/reg/2019/1120/oj/eng
- UN R136 secondary summary: https://www.batterydesign.net/legislation-rules-and-regulations/ece-r136/
- UN R136 documents index: https://globalautoregs.com/rules/203/documents?year=2014
- Roark's Formulas for Stress and Strain, 7th ed., Table 11.4. Cossalter, *Motorcycle Dynamics* (inertia ranges).
- Repo: `adventure-layout.md`, `mass-rollup.md`, `drive-study.md`, `electrical-design.md`, `engineering-release-review.md`, `startup-costs.csv`, `tools/build-adventure.py`.
