# Bavuso V1.0 baseline aerodynamics (CFD)

November 1, 2026, US Central. Prepared by Claude Opus 5.5. A computer simulation of the current integrated model with a seated rider. It is not a wind-tunnel measurement.

## The plain answer

- **Drag area (CdA) is 0.44 m²** at 100 km/h with an upright rider. That is in the same range as the best measured upright electric bikes: the Energica Ego+RS measured 0.50 m² upright in a wind tunnel, and the LiveWire One 0.57 m². Treat ours as 0.44–0.50 m², because a smooth simulated rider is always a bit cleaner than a real person in a jacket.
- **The bike makes most of the drag, not the rider.**

  | Part | Share of drag |
  |---|---:|
  | Bodywork and chassis | 68% |
  | Rider | 26% |
  | Wheels | 5% |

  The screen and body already shelter the rider well. The drag to win back is in the bodywork.
- **Lift is close to zero.** There is 27 N of net downforce. At speed the front does go light: drag pushes back above the ground and pitches the bike nose-up. The front tyre loses about 80 N at 100 km/h. That grows to about 450 N (about 45 kg) at 145 mph.
- **Range is the real problem.**
  - With today's 26.3 kWh pack, this shape gives about **150 miles at 70 mph**, not 200.
  - 200 miles needs about **34.5 kWh** at this drag area. That is about 30.5 kWh if the shape changes below bring it down to about 0.38 m².
  - This feeds straight into the battery cost study.
- **Top speed is fine.** Holding 145 mph takes about 75 kW at the wheel, and 150 mph about 83 kW. Both fit the planned 120–130 kW peak and 85–90 kW sustained motor.

## What was simulated

| Item | Setting |
|---|---|
| Software | OpenFOAM 12 (blueCFD-Core 2024-1), steady RANS, k-ω SST turbulence model, wall functions |
| Speed | 100 km/h (27.78 m/s), air density 1.204 kg/m³, dynamic pressure 464.6 Pa |
| Road and wheels | moving ground, both wheels spinning at road speed |
| Geometry | the integrated V1.0 model as built today (low-slung, about 130 mm ground clearance), plus a 50th-percentile male rider buck in the upright naked-bike posture |
| Mesh | 3.2 million cells, refined on the bike surfaces, run on 14 cores |
| Length | 800 iterations. Forces were averaged over the last 250. |

**Convergence.** Drag settled after about 250 iterations. Over the averaging window it varies by ±1.9 N, which is ±0.004 m² of drag area. The compute took about 3.6 hours. The laptop also slept for about 53 hours in the middle of the run, which did not affect the result.

Reproduce:
- Run `cfd/case-baseline/Allrun`.
- Then run `tools/cfd-report.py`.
- The numbers are in `cfd/results/aero-summary.json`.

## Results

| Part | Drag at 100 km/h | CdA | Lift (+ up) |
|---|---:|---:|---:|
| Whole bike and rider | 204.7 N | **0.441 m²** | −27.3 N |
| Bodywork and chassis | 139.7 N | 0.301 m² | −41.1 N |
| Rider | 54.1 N | 0.116 m² | +19.9 N |
| Wheels | 11.0 N | 0.024 m² | −6.1 N |

**How the drag splits.** 97% of the drag is pressure drag, from the shape. Only 3% is skin friction. That is normal for a motorcycle, and it means shape changes are what matter.

**Force on each axle at 100 km/h:**
- The front axle unloads by 82 N.
- The rear axle gains 109 N.

That comes mostly from drag acting about 0.6 m above the road. Every bike has this effect, and it grows with the square of speed.

**Drag power at the wheel:**

| Speed | Drag power |
|---|---:|
| 50 mph | 2.9 kW |
| 62 mph | 5.7 kW |
| 70 mph | 8.1 kW |
| 81 mph | 12.5 kW |
| 145 mph | 72 kW |

### Where the drag comes from

This is pressure drag added up by zone of the surface. The total of 199 N matches the solver's pressure drag to within 1%.

| Zone | Drag | Share |
|---|---:|---:|
| Mid body: pack sides, motor, footpegs, inner panel edges | 32.3 N | 16% |
| Screen, headlight, nose | 30.8 N | 15% |
| Tank, shroud, dash area | 30.3 N | 15% |
| Rider torso and arms | 23.2 N | 12% |
| Front fender and fork | 20.9 N | 11% |
| Rider legs and hips | 18.1 N | 9% |
| Pack and belly front face | 16.6 N | 8% |
| Helmet and shoulders | 11.3 N | 6% |
| Seat, tail, rear fender, plate | 6.4 N | 3% |
| Front wheel | 5.3 N | 3% |
| Rear wheel | 4.5 N | 2% |

Pictures are in `cfd/results/`:

| File | What it shows |
|---|---|
| `drag-map-side.png` | Where drag is made. Red adds drag. Blue pushes forward. |
| `midplane-speed.png` | Air speed on the centreline |
| `midplane-cp.png` | Surface and air pressure on the centreline |
| `top-speed-z045.png` and `top-speed-z095.png` | Plan views at knee and tank height |
| `convergence.png` | Drag history by part |

## What the pictures show

1. **Air gets inside the body.**
   - The plan view at 0.45 m shows air running between the side panels and the pack at about a third of road speed.
   - The centreline view shows air moving around the battery modules and motor.
   - Inside the shell it hits flat, blunt internal faces: the rear wall of the tank and the edges of the pack and panels. These show as the bright vertical red lines on the drag map.
   - These internal faces are a large part of the "mid body" and "tank" zones, together about 30% of all drag.
2. **The screen is a flat plate at about 45°.** It carries a strong stagnation line along its whole length. Air also jets through the gap between the screen base and the dash.
   - That jet is useful: it fills the low-pressure pocket behind the screen.
   - But the screen sends clean, fast air straight onto the helmet. The visor stagnation pressure is about Cp 1.0, which means wind noise and buffeting for a 5'9" rider.
3. **The front of the pack is a flat vertical wall** about 100 mm behind the front tyre. It sits in the tyre's spray and pressure field, so its front face carries high pressure.
4. **The front fender and fork legs** cost as much as the rider's legs.
5. **The tail barely matters (3%).** The wake behind the bike and rider is big, but almost all of it comes from the rider's back and the bike's mid-section, not the tail shape. Style the tail and luggage for looks and use.

## Shape recommendations, in order of payoff

These are directions, with expected gains. Each one must be checked in the next run before it is trusted.

| # | Change | Why | Expected gain |
|---:|---|---|---|
| 1 | **Close the shell.** Seal the gaps between the side panels and the pack/tank. Let cooling air in only through one ducted inlet, through the radiator, and out through a rearward-facing exit. | Removes the air hitting blunt faces inside the body | Largest. Roughly 5–10% of total drag |
| 2 | **Rework the screen and nose as one shape.** Curve the screen in side view and blend its base into the headlight nose. Keep a controlled vent gap at the base. Make it adjustable in height so the rider can lift the clean air above the helmet. | The screen and nose are 15% of drag. The helmet sits in the screen's jet. | 3–5% drag, plus a large comfort gain. Comfort is a must for a touring bike. |
| 3 | **Fair the front of the pack with the skid plate.** Make the bash plate a ramp that runs from the lower frame forward and up, angled about 30–40°. | A flat front face becomes a ramp. The adventure bike needs this armour anyway. | 2–4% |
| 4 | **Use a hugging front fender with fork-leg covers**, plus an optional high "beak" styled as part of the nose rather than a separate scoop. | The fender and fork are 11% today | 1–3% |
| 5 | **Hand guards and knee pockets** in the tank and side panels. | The rider's arms and legs are 21% of drag. Hand guards are standard adventure kit, and they can shield the hands and arms. | 1–3%, plus weather protection |
| 6 | **Leave the tail alone.** | 3% of drag | — |

**Realistic target.** About CdA 0.38–0.40 m², about 10–15% better than today, with the same comfortable upright posture. Do not plan on 0.30 m². That would take a racing tuck or a fully enclosed streamliner, and neither fits a do-anything bike.

### What the adventure version changes

- **Height.** The adventure role needs about 200–220 mm ground clearance, a 19-inch front wheel and longer suspension travel. That raises the bike about 80 mm.
- **Drag.** Expect drag to rise a few percent from the taller frontal area and the bigger gap under the belly. The recommendations above should more than pay that back.
- **Front-end lift.** The drag acts higher off the road, so the front-end unloading at speed grows slightly. Two counters:
  - a steering damper;
  - a nose shape that adds a little front downforce.
- **Next step.** A second, shorter run on the adventure-height shape with changes 1–4 applied, 400 iterations, about 2 hours of compute with the laptop kept awake. It will confirm the numbers.

## What this means for the battery and the cost study

The range model in `research/range-weight-budget.md` (70 mph, 400 lb bike, 10% reserve) gives:

| Drag area | Nominal pack for 200 mi at 70 mph | Range on today's 26.3 kWh pack |
|---|---:|---:|
| 0.44 m² (today) | 34.5 kWh | about 153 mi |
| 0.40 m² | 31.8 kWh | about 165 mi |
| 0.38 m² (target after changes) | 30.5 kWh | about 173 mi |

So even after the aero work, a true 200 highway miles needs **about 30–31 kWh**. That is about 15% more energy than the current pack, and it has to fit in a pack that sits higher for ground clearance. Two levers are left:
- higher energy per kilogram in the cells;
- a looser definition of the range goal, for example 200 miles at 65 mph, which needs about 26–27 kWh at 0.38 m².

The cost-down study sizes the battery to this number.

## Limits of this result

- **Steady RANS is a time-average model.** It predicts drag of bluff bodies like motorcycles to about ±10–15%, and it is much better at comparing two shapes than at absolute values. Wind-tunnel or coast-down testing of a prototype is still required.
- **The rider is a smooth buck.** It has no loose clothing and no real helmet shape. Real riders add drag.
- **Cooling airflow, radiators, mirror detail and indicators** are not modelled.
- **Only straight-ahead wind was simulated.** Crosswind (yaw) behaviour, which matters for highway stability, needs its own runs at 5–10° yaw.
- **The geometry is today's low-slung integrated model,** not the adventure-height version.
