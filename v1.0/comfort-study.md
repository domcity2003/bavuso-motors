# Bavuso V1.0 adventure: rider comfort study

Prepared November 11, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
- **Tool:** `tools/comfort-study.py`
- **Data:** `comfort-study.json`
- **Applied to:** `tools/build-adventure.py`

## Update, November 12, 2026: bars up, seat reshaped

*Claude Opus 5.5 (claude-opus-5-5).* After the first pass, Dominic said the seat "looks really uncomfortable and too high up for the handle bars".

**Diagnosis.** Measured against the baseline image, the seat height itself is right: the baseline's seat sits about as far below the tank top and the bars as ours does. Two other things were wrong:
- **The bars were low for a bike this tall.** The grips sat only 229 mm above the seat. The standing reach (grip to peg, measured flat) was 502 mm, past my 470 mm working limit.
- **The seat was a slab.** It was a flat-topped extrusion with vertical sides and one 20 mm fillet, about 65 mm of foam at the sit point.

**Bar sweep.** I re-ran the posture model with the grips 0 to 80 mm up and 0 to 40 mm back, for all three rider sizes:

| Grip change | Grip above seat | Standing reach | Elbows (5th F / 50th M / 95th M) | Score |
|---|---|---|---|---|
| none | 229 mm | 502 mm | 132° / 114° / 108° | 10.5 |
| 30 up, 20 back | 259 mm | 482 mm | 119° / 104° / 99° | 10.5 |
| **50 up, 20 back (applied)** | **279 mm** | **482 mm** | **116° / 101° / 96°** | **10.5** |
| 60 up, 30 back | 289 mm | 472 mm | 111° / 97° / 93° | 12.6 |
| 80 up, 40 back | 309 mm | 462 mm | 105° / 93° / 88° | 19.4 |

The score is the number of degrees outside the target bands, summed over all three riders. It doesn't move until the 95th-percentile rider's elbow drops below 95°. **50 up, 20 back** is the highest bar that keeps every rider's elbows in the band. It cuts the standing reach by 20 mm. The seated leg angles are unchanged.

**Seat.** The seat is now lofted through crowned cross-sections: a domed top, rolled edges, and sides tucking in to a pan 82% as wide as the top. Both pads get a piped welt along the top edges. The narrower pan clears the tail rails, so it drops 13 mm under the rider, giving about **78 mm of foam** at the sit point (was ~65 mm). That closes the earlier foam item. Directly over the shock-top cross tube the pan has a 48 mm wide moulded channel, which leaves about 66 mm of foam in that strip. The seat top and the 850 mm seat height are unchanged.

**What the bar move touched.** The mirrors moved with the bars. Two new checks were added:
- the controls at full lock against the tank, fairing and screen (30 mm, for gloved hands);
- the brake hose and harness at lock against the body.

Both pass in the full build: controls 62.5 mm, hose and harness 13.6 mm. The dash has its own 15 mm check (19.9 mm), since no hand goes between the risers. All 58 checks pass. The results are in `adventure-layout.md`.

## The plain answer

**The bike was uncomfortable because the legs were folded too tight.** The footpegs sat almost directly under the seat's lowest point, only 420 mm below it. An average man's knee closed to about **61°**, close to a squat. A tall rider got about 56°. The arms and back were fine, because the bars already put the rider upright.

**The fix, now in the CAD:**
- **Pegs:** 80 mm lower and 80 mm further back, now 340 mm above ground and 420 mm ahead of the rear axle.
- **Seat:** 10 mm higher, now **850 mm**, the same seat height BMW lists for the R1300GS.
- **Bars:** the grip points stay almost where they were (42 mm further forward, 6 mm lower). The old bar was two straight tubes running from the top clamp diagonally back to the grips. It is now a real 28.6 mm bar on pull-back risers: a straight centre run, then about a 29° sweep back to the grips.

| Rider | Knee, before → after | Hip (trunk to thigh) | Elbow | Trunk |
|---|---|---|---|---|
| 5th-percentile woman (1.52 m) | 73° → **94°** | 126° → 138° | 115° → **133°** | upright |
| 50th-percentile man (1.76 m) | 61° → **78°** | 125° → 136° | 102° → **114°** | upright |
| 95th-percentile man (1.88 m) | 56° → **72°** | 124° → 135° | 97° → **108°** | upright |

Angles are interior: 180° is a straight joint, and a bigger knee angle means a less folded leg.

**What it costs:**
- **Lean angle before a peg touches:** 54° → 48°. That is still in the adventure-class norm of about 45–50°, and the pegs fold up anyway.
- **Standing reach:** the grip-to-peg reach grows from 380 to about 500 mm, longer than my 470 mm working limit. A standing rider leans forward a little more. If the seating buck shows standing off-road is awkward, the fix is about 30 mm taller risers; it doesn't affect seated comfort.

## How it was measured

- **Rider model:** a stick-figure rider in three body sizes. Segment lengths are standard fractions of height: thigh 0.245 H, shin 0.246 H, trunk 0.288 H, upper arm 0.186 H, forearm to grip 0.200 H.
- **Hips:** the hip joint sits 90 mm above the compressed seat, on the seat's lowest point.
- **Feet:** the ball of the boot sits on the peg.
- **Upper body:** the rider sits upright and leans forward only if the arms can't otherwise reach. That matches the design-notes intent: near upright, shoulders relaxed, elbows softly bent.

**Sweep:** 8,460 feasible combinations of four things:

| Variable | Range |
|---|---|
| Peg height | 0 to 80 mm down |
| Peg fore/aft | 160 mm forward to 120 mm back |
| Seat | −10 to +10 mm |
| Bar position | 0 to +60 mm up, −60 to +20 mm fore/aft |

**Constraints:**
- peg lean clearance at least 45°;
- standing grip-to-peg reach 280–470 mm;
- seat no higher than 850 mm;
- pegs no further back than X400 (swingarm and heel).

**Scoring:** degrees outside the comfort band, summed over all three riders.

**Comfort bands used (working targets):**

| Joint | Band |
|---|---|
| Knee | 80–115° |
| Hip | 90–140° |
| Elbow | 95–150° |
| Trunk | 0–15° forward of vertical |

These are the usual upright/touring ranges. The numeric tables in the motorcycle-posture papers below are behind logins, so I could not check these bands against them line by line. Treat them as engineering targets, not cited values.

**What the sweep found:**
- **Lowering and moving the pegs back** is the only lever that matters. Lowering opens the knee directly. Moving back lets the shin angle back instead of standing vertical.
- **The seat** helps a little; each +10 mm gives about +1.3° at the knee.
- **Bars** don't affect leg comfort, so they stay where they are.
- **The best-scoring point** also pulled the bars back 20 mm and the pegs back another 20 mm. It scored 12.0 against 13.9 and gave less than 2° more knee. I kept the simpler change.
- **No feasible point** gets the 95th-percentile rider to 80° at the knee without a seat above 850 mm. Tall riders get a high-seat option (+30 mm) instead.

## Other comfort findings

| Item | Finding | Status |
|---|---|---|
| **Seat foam** | The rider pad was only about 55 mm thick. Long-distance seats use about 70–90 mm. | Raised to about 65 mm with the +10 mm top. For 75–80 mm, the seat pan must drop about 15 mm in its centre, between the tail rails. The rails are 1 mm from the pan edge at X470, so this is detail design. |
| **Knee width** | The bike is 414–444 mm wide where the knees sit, set by the 388 mm-wide pack. The knees grip the tank/cover sides, as on a GS. | Accepted. Narrowing it means a narrower pack. |
| **Wind** | Air leaving the screen top (rising about 20°) clears the chest of every rider. An average or tall rider's helmet sits in steady direct air. A 5th-percentile rider's helmet sits right in the turbulent edge, which means buffeting. | Recommend a screen with about 60 mm of height adjustment so short riders can move the edge clear. Not yet modelled. |
| **Arms and back** | Upright trunk for all three riders. With the new bar, elbows sit at 108–133°: softly bent, not stretched. | Bar rebuilt (above). |

## What changed in the CAD

- **`P` reference points:** `seat_top_rider_mm` is now [486, 0, 810] (model) = 850 above ground; `peg_reference_mm` is now [420, 190, 300] = 340 above ground.
- **Seat:** the rider pad is 10 mm higher (X351–621). The pillion pad is unchanged.
- **Peg hangers:** the plates now run from the swingarm-pivot node down and back to the new peg, outboard of the swingarm (Y ±224–230).
- **Peg-boss holes in the motor covers:** moved to the new peg axis.
- **Bar:** pull-back risers on the top clamp, the bar clamp at X1015 / Z1115 above ground, the grips swept back about 29° and down about 11°. The levers sit parallel to the grips.
- **Checks:** all clearance checks were re-run by the full build. The results are in `geometry-adventure-audit.json`, including `swingarm_sweep_vs_pegs`.

## Next steps

1. Build an adjustable seating buck and confirm these angles with real riders of different sizes in riding gear. This model is geometry only: no soft tissue, no boots, no pressure mapping.
2. Detail the seat pan for 75–80 mm of foam, and offer a +30 mm tall seat.
3. Add an adjustable screen (about 60 mm of travel).

Sources:
- [University of Waterloo: digital human model of motorcycle riding posture (Davidson & Fischer, Ergonomics 2024)](https://uwaterloo.ca/health/news/better-way-ride-motorcycle). Taller riders flex their ankles, knees, hips and elbows more to reach the controls.
- [Arunachalam, Singh & Karmakar, comfortable riding posture, IIT Guwahati (Int. J. Industrial Ergonomics 2021)](https://gyan.iitg.ac.in/items/7cc6c9bf-7a1a-43c0-9036-9cb572b00177). Full text is login-gated; not used for numbers.
- [Lundin et al., rider posture variability, Traffic Injury Prevention 2024](https://research.chalmers.se/en/publication/541710). Downloaded, but the text layer could not be read here.
- [BMW R1300GS technical data](https://www.bmwmotorcycles.com/en/models/adventure/r1300gs/technicaldata.html): 850 mm seat height
- Segment-length fractions: Drillis & Contini, as tabulated in Winter, *Biomechanics and Motor Control of Human Movement*
