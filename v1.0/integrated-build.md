# Bavuso V1.0 integrated model: build notes

Prepared October 26, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5). Picks up the compact rework Codex left unfinished on October 25.

**Status: engineering development model. Not a fabrication or riding release.**

## In one paragraph

`tools/build-integrated.py` builds one FreeCAD model containing three things:

- the real lower battery (700 cells, 100s7p),
- the real supplier CAD for the EMRAX 208 motor (on the swingarm pivot axis), the Cascadia CM200 inverter and the Orion BMS2,
- bodywork traced from `design/baseline black.png`.

It then checks the clearances that matter (battery, motor, tyres at full suspension travel, steering sweep, body) and writes an audit. `tools/render-integrated.FCMacro` renders the model to `visuals/`.

## How to run

```bash
"../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" -u tools/build-integrated.py > cad/integrated-build.log 2>&1
```

```bash
"../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/freecad.exe" tools/render-integrated.FCMacro
```

Set `BAVUSO_FAST=1` to save the native model only, without the STEP export or the checks (about 2 minutes instead of about 15). Use it for styling passes.

Outputs:

- `cad/Bavuso-V1.0-integrated.FCStd` and `.step`
- `geometry-integrated-audit.json`
- `cell-placement-integrated.csv`
- `component-status-integrated.csv`
- `visuals/integrated-*.png`

## Photoreal renders (Blender Cycles)

The FreeCAD renders above are quick previews. For lifelike images, export the model as a mesh, then render it in Blender:

```bash
"../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" tools/export-render-mesh.py
```

```bash
"../.tools/blender-5.2.3-windows-x64/blender.exe" -b -P tools/render-cycles.py -- 96 side,front34,rear34
```

- **Export.** `export-render-mesh.py` writes `cad/render/bavuso.obj`, one object per part, tagged with a material name such as paint, tyre, chrome, glass or lamp. It takes about 1 minute.
- **Render.** `render-cycles.py` turns those tags into physical materials (satin black paint, rubber, chrome, see-through screen, glowing lamps). It lights the bike in a white studio and writes `visuals/cycles-<view>.png`.
- **Arguments.** The first number is the sample count: 16 for a quick look, 96 for final. The views are `side`, `front34`, `rear34` and `front`.
- **Timing.** This PC has no supported GPU, so Cycles runs on the CPU, about 4 minutes per view at 96 samples.

## Tools installed for this work (October 26, 2026)

| Tool | Where | What it is for |
|---|---|---|
| Blender 5.2.3 portable | `../.tools/blender-5.2.3-windows-x64/` | Photoreal Cycles renders. Downloaded from an official mirror and checked against its SHA-256. |
| FreeCAD Render workbench (FreeCAD/FreeCAD-render) | FreeCAD `Mod/Render` | Material and lighting setup inside FreeCAD. It needs a separate renderer, so the Blender script above is used instead. |
| Curves workbench (tomate44/CurvesWB) | FreeCAD `Mod/CurvesWB` | Smooth surfaces (Gordon surfaces, blends) for future, rounder body panels. |
| FreeCAD MCP (neka-nat/freecad-mcp) | FreeCAD `Mod/FreeCADMCP` and `../.mcp.json` | Lets Claude drive a live FreeCAD window. To use it, restart Claude Code, open FreeCAD, choose the MCP Addon workbench and click "Start RPC Server". |

The add-ons sit in the portable FreeCAD's own `Mod` folder. The Claude desktop app redirects `%APPDATA%`, so a normal add-on install would be invisible to FreeCAD.

## What changed from Codex's compact rework, and why

| Area | Change | Reason |
|---|---|---|
| Battery | Moved one 7-cell stack from column 2 to column 8. Rear roof now Z344, front step at X972. | The EMRAX's square 6 mm mounting plate reaches corner (645.75, 364.25). Codex's 105.75 mm circle check missed it, and it overlapped the pack by 902 mm³. The gap is now 20.25 mm. |
| Electronics | Stacked in the tank: charger Z590–666, CM200 Z675–772, BMS Z780–853. | The charger overlapped the steering sweep by 765 cm³. Under the seat, the BMS had only 17.7 mm to the rear tyre at full bump. |
| Lower frame rails | Run at Y ±190 and Z250 beside the pack, kinking at X1110/Z420. | The original route went through the pack case and the battery covers. 9 mm to the pack wall, 13 mm inside the cover skin. |
| Belt drive | Belt plane moved inboard to Y −105…−83, between the tyre (−80) and the swingarm arm (−108). | Codex's plane at Y −211 ran through the three rails meeting at the pivot node. Because the motor is coaxial with the pivot, belt length stays constant through suspension travel. |
| Swingarm | Box-section arms (92 tall tapering to 58) plus a cross tube at X380. | Replaces two round tubes. The cross tube sits 64 mm off the tyre at rest. |
| Fork | Upside-down fork built on the true steering axis: tubes 36.1 mm ahead of the axis, triple clamps, risers. | Replaces two plain cylinders. |
| Wheels and brakes | Cast 10-spoke 17-inch wheels, 320 mm drilled front discs on carriers, 240 mm rear disc, calipers clear of the carriers. | Realism. |
| Body | Panels made by extruding the traced side view and plan view and keeping their overlap, then filleting and hollowing to 3 mm shells. | Replaced lofted shapes that came out broken. |
| Body cross-section | The battery covers bevel in below the lower rails, from 444 mm wide at Z228 to 356 mm at the belly. The tank sides lean in above the upper rails, from 444 mm at Z800 to about 340 mm at the top. The belly plates wrap the bevel. | The sides were flat and vertical, so the body read as a box from the front. The pack (±165 mm) and rails (±211 mm) set the full width only between Z228 and Z800. |
| Body detail | Proud bolted battery and belly panels, motor side cover with rear bulkhead, louvred grille, seam trim, stepped seat, upswept tail tip, US plate hanger. | Matches the baseline; nothing inside shows through. |
| Clearance checks | Measure surface to surface, and catch real overlaps with a separate volume test. | Two EMRAX supplier solids have inward-facing faces, so plain solid distance falsely reported 0 mm. |

## Check results

See `geometry-integrated-audit.json` for every value. All 27 critical clearance checks pass. "Bump" means the tyre at full suspension compression, sampled at 21 points through the travel.

| Check | Gap (mm) | Required (mm) |
|---|---|---|
| Pack to EMRAX supplier solid | 20.25 | 20 |
| Pack to front tyre (bump) | 52.27 | 20 |
| Motor to rear tyre (bump) | 126.83 | 20 |
| Pack to swingarm pivot stubs | 107.58 | 20 |
| Charger to pack | 10.00 | 10 |
| BMS to tank shell | 72.38 | 8 |
| BMS to CM200 inverter | 8.01 | 5 |
| BMS to rear tyre (bump) | 463.84 (bounding-box lower bound) | 20 |
| Charger to steering sweep | 37.82 | 10 |
| CM200 to steering sweep | 53.34 | 10 |
| CM200 to charger | 8.50 | 5 |
| Battery covers to motor | 117.93 | 10 |
| HV cabinet to motor / pack / seat | 12.25 / 9.43 / 17.0 | 10 / 3 / 10 |
| Battery covers to pack | 8.42 | 5 |
| Battery covers to front tyre (bump) | 24.20 | 20 |
| Tank and fairing to front tyre (bump) | 126.97 | 20 |
| Seat to rear tyre (bump) | 46.51 | 20 |
| Tail to rear tyre (bump) | 35.79 | 20 |
| Motor side cover to motor / rear tyre | 28.49 / 158.1 | 10 / 20 |
| Licence plate / hanger arm to rear tyre (bump) | 40.57 / 33.38 | 20 |
| Swingarm cross tube to rear tyre | 64.01 | 20 |
| Radiators to charger | 16.0 | 5 |

All 700 cell corners sit inside the pack's inner wall.

**How the checks work.** Some supplier STEP solids give false zero readings in OpenCASCADE:

- two EMRAX solids have inward-facing shells;
- some Orion spline faces return 0 mm from 460 mm away.

So a measurement of 0 is re-measured surface to surface, and if the two bounding boxes don't meet, the box gap is used as a guaranteed lower bound. Real overlaps are always measured as an intersection volume, solid by solid.

A broader sweep tests every body and electronics part against everything else visible. The mirror-stalk joints are intended and excluded.

## Open issues (not solved by this model)

- **Ground clearance** is about 128–135 mm here, measured at the skid plate with the suspension topped out. **Solved in the adventure model (Nov 3 2026):** 216 mm with an 840 mm seat. It also carries the optimised 32.7 kWh structural pack and the EMRAX 228. See `adventure-layout.md` and `tools/build-adventure.py`. This integrated model stays as the earlier reference.
- **Battery cover spline.** The covers' plan outline is a 5-point spline, which bows between its points; line 384 of the build script already notes the bulge past 222 mm. In the adventure model the same bow went 22 mm inward into the pack. It was fixed there by adding more points.
- **Aerodynamics (baseline CFD, Nov 1 2026):** CdA 0.44 m² with an upright rider. That gives about 150 mi at 70 mph on the current 26.3 kWh pack. See `aero-baseline-report.md`. Close the body shell, rework the screen and nose, and fair the pack front with the skid plate. Target 0.38–0.40 m².
- **Powertrain (optimised Nov 2 2026):** see `powertrain-cost-down.md` and `tools/powertrain-optimise.py`.
  - Best design: 32.7 kWh of fast-charge large cylinders (99s6p, 416 V) in a structural pack that carries frame loads, an axial-flux motor with a contract-built SiC inverter, and premium light parts.
  - About 490 lb, 200 mi at 70 mph with margin, 14 min 10–80%, about $24.8k delivered per bike at 10k/yr.
  - The pack is heavier than today's 85 kg, so frame, brakes and suspension must be sized for it.
  - The current EMRAX 208 is under-powered for the 145–150 mph target.
- **The body is still 444 mm wide at rail height** (Z228–800). The pack is 330 mm wide and the rails sit outside it, so going narrower there means moving the rails inboard or narrowing the pack.
- **The steering sweep cuts a cavity in the tank top.** The screen and dash hide it, but a proper headstock shroud is needed.
- **Belt installation.** The swingarm cross tube passes inside the belt loop, so the belt must go on before the brace (bolt-in brace) or be a split belt.
- **The belt gap is tight:** about 4 mm from the belt to the tyre sidewall, 3 mm from the belt to the arm, and 1 mm from the pulley flange to the arm. Confirm against the real tyre section and pulley drawings.
- **The pack layout deviates** from `cell-layout-proposal.json` (one stack moved). Update that file if this layout is accepted.
- **Not modelled or not checked:**
  - steering lock beyond the cylinder envelope
  - rear droop
  - tyre growth
  - wiring and hoses
  - mounts and fasteners
  - structure and fatigue
  - crosswind (yaw) CFD and the adventure-height shape (the straight-ahead baseline is done)
  - a rider fit buck (CFD uses a simple 50th-percentile buck)
- **Placeholders, not real parts:**
  - GX14 contactors (drawing outline only)
  - radiators (unsized)
  - charger (catalogue box)
  - all body panels, the fork, wheels, calipers and swingarm (illustrative)
