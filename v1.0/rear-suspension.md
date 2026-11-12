# Bavuso V1.0 adventure: rear shock and rear kinematics

Prepared November 3, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5). Updated November 5 for the IPM drive (`drive-study.md`). The final belt pulley is still on the pivot axis, so the geometry below is unchanged. Anti-squat is now 125% at sag (108–135% across the travel), because the rider-on CoG is 637 mm instead of 643. The central shock clears the new motor by 21.6 mm. Tools: `tools/rear-kinematics.py` (sweeps, plain Python) and `tools/build-adventure.py` (CAD and clearance checks).

## The plain answer

**The rear uses one central shock bolted straight to the swingarm, with no linkage.** This is the layout KTM uses on the 1290 Super Adventure (WP PDS / APEX). The specification:

- 305 mm eye to eye at full extension, 75 mm stroke.
- About 109 N/mm spring (updated Nov 5 for the IPM drive's mass; it was 107 on Nov 4 and 97 before that).
- Semi-active damping with an electronic hydraulic preload adjuster of about 20 mm.
- **Units of this class:** WP APEX SAT and Öhlins TTX AR-X 40.

To make it work, **the swingarm pivot, and the motor on it, came down 120 mm, to 390 mm above ground.** That fixed a problem the shock study turned up. At the old pivot height, anti-squat was about 175%, so the rear would jack up hard under power. It is now **124% at sag, and 107–133% across the travel**, the normal band for a strong road-and-trail bike. My earlier note in `adventure-layout.md` said "about 100%". That was wrong, and it is corrected there.

The battery still holds all 594 cells. Ground clearance (216 mm) and seat height (840 mm) are unchanged.

## Why anti-squat was the real problem

Anti-squat is how the rear suspension reacts to acceleration:

- **100%:** the drive force exactly cancels the weight shifting onto the rear, so the bike stays level.
- **Below 100%:** the rear squats.
- **Above 100%:** the rear lifts. The suspension then stiffens up under power, the tyre loses grip on bumps, and the front gets light sooner.

Here the motor sits on the swingarm pivot, so the belt geometry is fixed by the gearing. Anti-squat therefore depends almost only on the **pivot height**. The drive force at the tyre acts at ground level, and its lever about the pivot is the pivot's height above ground. The belt's own lever is the tyre radius divided by the gear ratio, which is a fixed 100.6 mm.

| Pivot above ground | Swingarm angle | Anti-squat at sag | Across the travel | Motor bottom above ground |
|---|---|---|---|---|
| 510 mm (before) | 20.1° | 175% | 150–190% | 387 mm |
| 450 mm | 14.3° | 149% | 129–161% | 327 mm |
| 410 mm | 10.3° | 132% | 114–143% | 287 mm |
| **390 mm (chosen)** | **8.2°** | **124%** | **107–133%** | **267 mm** |
| 370 mm | 6.1° | 115% | 99–124% | 247 mm |

**Why stop at 390 mm.** Below that, the swingarm runs nearly flat, and at full bump it would rise well above horizontal. The motor would also come down toward the belly line. 390 mm keeps anti-squat a little above 100%, so the bike stays settled when it launches hard (3 s 0–60), and stays near 100% at full bump. Fully loaded two-up, the centre of gravity rises to about 753 mm and anti-squat falls to about 106%.

**Sensitivity to CoG height** (rider on, pivot 390): 600 mm → 133%, 650 mm → 123%, 700 mm → 114%, 750 mm → 106%. My CoG estimate of 644 mm is a hand roll-up, not a measurement (see assumptions).

## The shock layouts considered

| Layout | Prior art | Verdict |
|---|---|---|
| **Central direct mount on a swingarm hump** | KTM 1290 Super Adventure (WP PDS / APEX, 200–220 mm) | **Chosen.** Loads are symmetric, it's the simplest hardware, and semi-active shocks with automatic preload exist for it. It became possible once the motor came down: the space above and behind the motor opened up. |
| One shock offset on the right arm (the old placeholder) | Ducati Scrambler | Puts about 0.5 kN·m of twist through the swingarm at peak load, which means a heavier cross member and some rear-wheel steer under load. |
| Twin shocks, one per arm | Triumph Scrambler 1200 XE (twin Öhlins, 250 mm) | Works and looks good. But semi-active twin units with automatic preload are rare, and that feature is what a premium adventure bike is expected to have. |
| Central shock with a linkage | Honda Africa Twin | No room. The motor on the pivot fills the space a linkage needs below the swingarm. |

## Chosen geometry

All values are in model coordinates (X forward from the rear axle; Z up, with the ground at Z = −40).

| Item | Value |
|---|---|
| Swingarm pivot / motor axis | X540, Z350 (390 mm above ground) |
| Swingarm length, static angle | 545.6 mm, 8.2° |
| Lower eye | On a twin-plate tower above the 50×5 cross brace, 210 mm behind the pivot and 120 mm above the arm line. Static position (315, 439). |
| Upper eye | (490, 660), on twin plates hung from a new cross tube between the tail rails at X490 |
| Eye to eye: droop / static / end of stroke | 303.9 / 282.1 / 230.5 mm |
| Stroke used | 73.5 mm, for 170 mm of wheel travel |
| Leverage ratio | 2.34 at droop, 2.33 at sag, 2.27 at bump (3% rising) |
| Shock angle at sag | 52° from horizontal |
| Spring gap through the travel | Sweep tool, conservative outline: 22.6 mm to the motor, 24.8 mm to the tyre, 57.5 mm to the pack. CAD (real geometry): 50.1 mm to the motor, 48.4 mm to the tyre, 89.4 mm to the pack. |

**Leverage curve.** The leverage is almost constant, because a direct mount on a near-flat swingarm gives very little progression. So the progression has to come from inside the shock: position-sensitive damping in the last 20–25% of stroke (as in KTM's PDS), plus a hydraulic or elastomer bump stop. That is a line in the supplier specification, not a geometry problem.

## Spring and preload

**Assumptions:**

- Bike 275.1 kg ready to ride, CoG at X806 and 505 mm high, rear unsprung 19.0 kg: from the CAD roll-up in `mass-rollup.md` (Nov 4). The first pass used the optimiser's 222.5 kg; the rider-on CoG height came out the same (643 vs 644 mm), so anti-squat did not change.
- Rider 85 kg, passenger 85 kg, luggage 30 kg.
- Rear unsprung mass 22 kg.
- Rider-on rear ride frequency of 1.75 Hz, inside the 1.6–1.9 Hz adventure range.

| Item | Value |
|---|---|
| Sprung load on the rear: rider / two-up with luggage | 1,592 N / 2,655 N |
| Wheel rate at sag | 19.6 N/mm |
| **Spring rate** | **about 109 N/mm (11.2 kgf/mm)**, 88 mm OD, 12 mm wire |
| Spring preload, rider only, for 51 mm sag (30%) | 13 mm |
| Extra preload to keep 51 mm sag two-up with luggage | 22.7 mm |
| **Preload adjuster specified** | **20 mm, electronic hydraulic** (KTM APEX SAT and Öhlins TTX AR-X 40 both offer about 20 mm). Two-up loaded sag then becomes about 58 mm (34%), which is fine for touring. |
| Ride frequency two-up loaded | 1.35 Hz (soft but normal; the semi-active damping covers it) |
| Static shock force: rider / two-up loaded | 3.7 kN / 6.2 kN |
| Spring-only wheel force at the end of stroke | 2.6 × rider-on static. The bump stop must lift this past about 3.5×. |

## Shock specification for supplier quotes

| Item | Value |
|---|---|
| Type | Mono, direct mount, semi-active damping (compression and rebound), electronic hydraulic preload |
| Length | 305 mm eye to eye at full extension, 75 mm stroke |
| Eyes | 12 mm bolt with spherical bearings, 40 mm wide clevis on both ends |
| Spring | Linear about 109 N/mm, 88 mm OD maximum, swappable |
| Reservoir | Remote, on a hose. Its space is reserved under the seat at X430, Z705. |
| Damping | Position-sensitive last 20–25% (PDS-style) plus a hydraulic bump stop |
| Preload range | 20 mm or more, auto-levelling from a ride-height sensor |
| Candidate suppliers | WP (APEX SAT), Öhlins (TTX AR-X 40 / Smart EC 2.0), Marzocchi, ZF Sachs |

## What changed in the CAD

| Area | Change |
|---|---|
| Pivot and motor | Lowered 120 mm (`PZ` = 350; set by `BAVUSO_PIVOT_Z`). The battery bands re-flow around the motor automatically. The pack now wraps over the motor and is 24 mm taller (to 613.5 mm above ground). The cell centroid rises 25 mm, to 424 mm. |
| Frame | The upper rails rise almost vertically from the pivot node (to X570) so they clear the pack's top steps. The pack's rear limit moved to X590 for the same reason. The rear pack link now runs straight forward from the pivot node to a lug on the pack's rear face. A new tail cross tube at X490 carries the shock top. |
| Swingarm | Cross brace upsized to 50×5 to carry the shock tower. The brace still sits inside the belt loop, so it bolts in. A twin-plate shock tower runs from the brace to the lower eye. |
| HV cabinet | Moved to X550–690, Z580–710 (forward 35 mm, down 20 mm) behind the charger, clear of the shock. The contactors and fuse moved with it. |
| Motor cover | Its rear lower bulkhead was removed, because the swingarm arms now pass through where it stood. |
| Pegs | Peg tube now starts at Y ±158 to clear the swingarm arm and pivot stub. |
| Left swingarm arm | Moved out 8 mm (centre Y −133), clear of the EMRAX output hub. The cross brace was lengthened to match. |
| Checks | Rear tyre sweep now covers droop too, not just bump. New checks: the shock envelope swept against motor, pack, cabinet, charger, seat, frame and reservoir; the shock against the tyre and swingarm at matched positions; the tower against the tyre; and the swingarm sweep against motor, pack, pegs and motor cover. |

## Check results

The full build passes **47 of 47** checks, and the interference sweep finds no overlaps. All values are in `geometry-adventure-audit.json`. The new and changed checks:

| Check | Gap (mm) | Required (mm) |
|---|---|---|
| Shock envelope (88 mm spring, droop to end of stroke) to motor | 50.1 | 15 |
| Shock to pack / cabinet / seat / frame | 89.4 / 42.0 / 82.2 / 112.7 | 15 / 10 / 10 / 10 |
| Shock to remote reservoir | 16.9 | 10 |
| Shock to rear tyre / swingarm arms, at matching positions | 48.4 / 105.8 | 20 / 10 |
| Shock tower to rear tyre | 22.5 | 20 |
| Swingarm sweep (arms, brace, tower) to motor | 11.0 | 10 |
| Swingarm sweep to pack / motor cover / pegs | 97.0 / 52.5 / 8.0 | 20 / 10 / 5 |
| Rear tyre (now droop to bump) to frame / seat / tail | 27.0 / 44.0 / 39.1 | 20 |
| Charger to pack (pack is taller now) | 16.5 | 10 |
| Cabinet to pack | 6.5 | 3 |

**Two fixes during the run:**

1. **The first shock-to-motor result was false.** It read 0 mm with no overlap, and the reported contact point was inside the motor, nowhere near the shock. It's the same fault in the EMRAX supplier solid that the integrated model ran into. The check now measures from 0.3 mm mesh points on the motor to the shock's axis instead.
2. **The swingarm sweep found a real tight spot.** The belt-side arm's inner face was 3 mm from the motor's output hub. The gap is axial and the two share an axis, so it never changes with travel, but it was too tight to build. The left arm moved out 8 mm (to Y −116), which also gives the belt more room.


## Open issues

- **CoG height:** the Nov 4 CAD mass roll-up gives 643 mm with a rider on, against the 644 mm assumed, so the pivot height stands. Re-run `tools/mass-rollup.py` then `tools/rear-kinematics.py` after any big layout change.
- **Shock tower and cross brace** carry 3–6 kN static and roughly 3× that at peak. They need FEA and a fatigue check. The bolt-in brace also needs a joint design.
- **The pack got 24 mm taller.** The charger now sits 16.5 mm above it, not 40.8 mm. The thermal and service access paths need a look.
- **Not covered:** shock supplier CAD, the reservoir hose route, the ride-height sensor, damping curves, and a bump-stop curve.
