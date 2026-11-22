# Bavuso V1 rev E: indented BOM and concept drawing pack

> **Superseded in part (Nov 22, 2026).** This document is a snapshot of the 252.93 kg ledger; the authority is `00-V1-final-spec.md`. Final: 257.9 kg / 569 lb (`bom-v1-reconcile.json` and `data/bom-v1-indented.csv` are the current BOM and tie to the ledger). Stale here: 252.9315 kg everywhere, the assembly masses, and the drawing-sheet mass columns; the lid and cell-holder IDs are provisional (not in `parts-id-registry.csv`); the drawing index page may show scale and mass columns shifted by one row.


November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Files: `program/data/bom-v1-indented.csv` (263 rows), `program/data/bom-v1-reconcile.json`, `drawings/` (9 sheets plus `V1-drawing-pack.pdf`), scripts `program/tools/bom-v1.py` and `program/tools/drawings-v1.py`, side data `program/data/drawings-derived.json` and `drawings-meta.json`. Inputs: `program/data/parts-ledger.csv` (read only), `cad/Bavuso-V1.0-adventure.FCStd` (rev E, read only).
Labels: **measured** = from the CAD solid, **calculated**, **supplier**, **estimate**.

## The plain answer

**The BOM adds up to the ledger exactly: 252.9315 kg from 220 part lines, against a ledger total of 252.9315 kg (difference 0.0000 kg; limit 0.1 kg).** It is a four-level tree (vehicle, 8 systems, 34 assemblies, 220 parts). Nine concept drawing sheets are done and combined in one PDF. Seven are for parts the CAD really models; two (the pack lid and the module cell holder) are derived concept shapes, because the CAD has no solid for them. **There is no motor mount in the CAD at all**, so the "motor mount" sheet is the motor-side pulley carrier, the only motor-side mounting part that exists.

The drawings are a communication aid, not a manufacturing release: no GD&T, no weld symbols, no surface finish, no threads or fits (section 5).

| Item | Result |
|---|---|
| BOM leaf sum vs ledger total | 252.9315 vs 252.9315 kg, diff 0.0000 (pass, limit 0.1) |
| BOM vs `mass-rollup.json` total (252.9, rounded) | diff 0.03 kg, rounding only |
| Part lines / assemblies / systems | 220 / 34 / 8 |
| Make / buy lines | 70 make (42.5 kg), 150 buy (210.4 kg) |
| Made parts that appear on a drawing | 43 of 70 lines, 34.2 of 42.5 kg (80 % by mass) |
| Drawing sheets | 9 (7 from CAD solids, 2 derived), A3, third-angle, ISO 2768-m |
| Ledger issues found | 6 (section 4) |

## 1. How the BOM is built

Levels: 0 vehicle (`BV-VEH-0001`), 1 system (`BV-SYS-0001` to `0008`), 2 assembly (`BV-ASM-nnnn`), 3 part (the ledger's own `BV-xxx-nnnn` IDs, unchanged). Assemblies are new IDs I assigned; they are not in `parts-id-registry.csv` and nobody has to adopt them, but the numbering is stable (`BV-ASM-0x..` where x is the system number).

Choices I made:
- **One line per ledger ID.** The ledger keeps every mirrored pair as two lines (`_m1` and `_1`), so I did not merge them into qty 2. That keeps every BOM line traceable to one ledger row. Side labels `(Y-)` and `(Y+)` are the CAD's sign of Y, not left or right.
- **Systems follow the roll-up's eight groups.** Ledger codes ENG, CHS, RUN, DRV, ELC, THM, ALW map one to one; BOD and PRO are merged into "Body and protection" (14.45 kg), as in the rev E report.
- **A ledger row the rules do not recognise falls into an "Other ... parts" assembly** (`BV-ASM-09xx`) instead of being dropped, so the total cannot silently lose mass. None did on this run.
- Mass each is the ledger mass divided by its qty (all qty are 1); extended is the ledger mass. Assembly and system masses are sums of their parts.
- **Pack case split.** The ledger carries the case and its lid as one solid (`BV-ENG-0001`, 7.8554 kg). For the drawings I split the roof slab out as the lid `BV-ENG-0101` (1.3242 kg, from the slab volume at 2.70 g/cm3), and the tub line is the ledger mass minus the lid (6.5312 kg). Net change zero.
- **Cell holders are shown but not counted** (section 3).
- Drawing number: the sheet's part number. Made parts inside a drawn assembly point at that assembly's sheet; the four case pads point at the tub sheet.

### Summary by system (all from the script)

| System | Part number | kg | Assemblies |
|---|---|---:|---|
| Pack | BV-SYS-0001 | 104.909 | cell lanes 82.50, case 7.90, internals 14.51 |
| Chassis | BV-SYS-0002 | 29.777 | frame 16.99, pivot yoke 8.65, swingarm 4.14 |
| Running gear | BV-SYS-0003 | 43.080 | fork 9.10, shock 3.00, wheels and tyres 16.15, brakes 8.69, controls 2.84, pegs and stand 2.80, steering damper 0.50 |
| Drive | BV-SYS-0004 | 23.450 | motor and inverter 19.95, belt and pulleys 3.10, carrier 0.40 |
| Electronics | BV-SYS-0005 | 17.437 | charging 4.90, HV 6.00, BMS 1.50, LV 2.10, lamps 1.74, display 1.20 |
| Body and protection | BV-SYS-0006 | 14.448 | upper 2.21, lower 2.16, seat and tail 5.73, pods 0.60, mirrors 0.86, fender 0.27, allowance 1.00, protection 1.63 |
| Cooling | BV-SYS-0007 | 6.900 | radiators and fans 2.71, coolant circuit 4.19 |
| Wiring, fasteners, fluids | BV-SYS-0008 | 12.930 | harness 7.93, fasteners and brackets 5.00 |
| **Vehicle** | BV-VEH-0001 | **252.932** | |

### Reconciliation proof

`bom-v1.py` sums the level-3 lines and compares them with the ledger sum, and with the level-1 sums:

| Check | Value |
|---|---:|
| Sum of ledger `mass_kg` (218 rows) | 252.9315 kg |
| Sum of BOM level-3 `mass_ext_kg` (220 lines: 218 ledger rows + lid + holder row at 0) | 252.9315 kg |
| Sum of BOM level-1 system masses | 252.9315 kg |
| Difference | 0.0000 kg (limit 0.1) |
| `mass-rollup.json` by system, ENG / RUN / CHS / DRV / ELC / ALW / BOD+PRO / THM | 104.91 / 43.08 / 29.78 / 23.45 / 17.44 / 12.93 / 14.44 / 6.90, each equal to the BOM system to the rounding shown |

The script exits with an error if the difference passes 0.1 kg. **The ledger agent is still working: the total moved from 250.57 kg (rev E report) to 252.93 kg while I worked** (new rows `BV-CHS-0050` 1.3 kg unmodelled pads and boss, `BV-RUN-0071` damper 0.5 kg, the rear brake pedal row and others). The numbers above are the state at 15:47 on November 22; re-run `bom-v1.py` after any ledger change and it will re-reconcile.

## 2. The drawing pack

Run `../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drawings-v1.py` from `v1.0` (about 40 seconds). **TechDraw page export needs the FreeCAD GUI, so it was not used for the page.** The script uses TechDraw's own headless hidden-line removal (`TechDraw.projectEx`) on the real solids and draws the edges, dimensions, balloons and title block with matplotlib (1 data unit = 1 mm on an A3 page). Edge geometry is therefore true CAD projection; the lines were not traced.

Each sheet has: three third-angle views (A side from -Y with the front to the right, B top above it, C front below-right) plus an iso at its own scale; overall dimensions (exact extents of the projected edges); numbered balloons on the bores the reports give; material, process and ledger mass; title block (Bavuso Motors, V1, part number, rev E, 2026-11-22, scale, mm, third-angle symbol, "Concept-level drawing - not for manufacture"); ISO 2768-m general tolerances.

| Sheet | Part number | File | Scale | Overall X x Y x Z (mm) | Mass (kg) | Source |
|---|---|---|---|---|---:|---|
| 1 | BV-ASM-0201 Welded frame with cast nodes | `BV-ASM-0201_frame-welded-assembly.pdf` | 1:10 | 1308 x 429 x 663 | 16.990 | 25 CAD solids; yoke shown grey |
| 2 | BV-ASM-0202 Pivot yoke | `BV-ASM-0202_pivot-yoke.pdf` | 1:5 | 95 x 439 x 273 | 8.651 | 11 CAD solids (legs, cross, nodes, blocks, spindles, bearing refs) |
| 3 | BV-ASM-0203 Swingarm (cast A356) | `BV-ASM-0203_swingarm-cast-A356.pdf` | 1:3 | 573 x 221 x 246 | 4.136 | arm, tower, brace |
| 4 | BV-ENG-0001 Pack case tub | `BV-ENG-0001_pack-case-tub.pdf` | 1:5 | 520 x 331 x 374 | 6.531 | case solid below Z625.1 |
| 5 | BV-ENG-0101 Pack lid | `BV-ENG-0101_pack-lid.pdf` | 1:3 | 494 x 331 x 3.05 | 1.324 | **derived**: roof slab of the case solid |
| 6 | BV-BOD-0004 Lower body panel | `BV-BOD-0004_lower-body-panel.pdf` | 1:10 | 615 x 450 x 407 | 0.922 | CAD solid |
| 7 | BV-DRV-0006 Rear pulley and hub | `BV-DRV-0006_rear-pulley-hub.pdf` | 1:3 | 332 x 70 x 332 | 2.100 | CAD solid (filled disc) |
| 8 | BV-DRV-0007 Motor-side carrier ("motor mount") | `BV-DRV-0007_motor-carrier.pdf` | 1:1.5 | 72 x 114 x 72 | 0.400 | CAD solid |
| 9 | BV-ENG-0102 Module cell holder, one module | `BV-ENG-0102_module-cell-holder.pdf` | 1:3 | 514 x 75 x 374 | 0.773 (not counted) | **derived** concept plates |

All files are in `drawings/`; `V1-drawing-pack.pdf` is an index page plus the nine sheets (10 pages).

Key bores and sizes called out (balloons or notes): pivot bore Ø95 and boss OD 112 (swingarm, found as circles in the solid); pivot spindle Ø60 and left stub Ø40/Ø30 (yoke); brace Ø75 x 6.0 and tower eye Ø66 (swingarm); four floor vents Ø28 (case); eight Ø70.6 lightening holes, bore Ø40, flange OD Ø331.9 and root Ø319.3 (pulley); OD 72 and bore Ø44 (carrier); 275 apertures Ø19 (holder). Tube sizes, wall thicknesses and the 5 mm front wall are in each sheet's notes and come from `16-cad-revE.md`, `09-structures.md` and `08-cad-revD.md`.

**How the two derived parts were made.**
- *Lid:* the case solid has a flat 3 mm roof at Z625.1 to 628.1. I cut the solid at Z625.1; above is the lid, below the tub. It has no flange, seal groove or bolt pattern because the CAD has none.
- *Cell holder:* one 25s11p module is one cell lane (275 cells of 21.6 x 70.2, axis along Y). The plates are two 2.5 mm PA66-GF30 plates, one at each cell end, with a Ø19 aperture over each of the 275 cell centres read from `Cell_lane_1`. Mass is plate volume at 1.35 g/cm3 (**estimate**).

## 3. What I could not find in the CAD or ledger

| Item | State | What I did |
|---|---|---|
| Motor mount | No solid and no ledger line. The motor housing is bolted between the two pivot stubs (09-structures), and the right stator plate is not modelled | Drew the only motor-side mounting part that exists, the pulley carrier `BV-DRV-0007` |
| Pack lid | Part of the one case solid, no separate ledger line | Derived `BV-ENG-0101` (provisional ID), net zero mass |
| Battery module holder | No solid. No ledger line (only DFMEA D06, "not designed in detail") | Derived `BV-ENG-0102` (provisional ID). It appears in the BOM at 0.0 kg so the total still reconciles; **the plates alone are about 0.77 kg per module, 3.1 kg for four** |
| Lug plates, pack mounting pads, arm boss | Not modelled (16-cad-revE); ledger has `BV-CHS-0050` 1.3 kg for them | Counted via the ledger line, not drawn |

## 4. Ledger and CAD findings (nothing changed; for the ledger agent and the lead)

1. **Cell holders have no mass anywhere.** `BV-ENG-0006/0007` list busbars, ribbons, manifolds and foam, not holders. If a real holder is 3 kg or more per pack, the pack is that much heavier than 104.9 kg, or the allowance is hiding it. Needs a decision.
2. **Drive descriptions in the ledger are stale.** `BV-DRV-0003/0004/0006` say 14 mm belt, 21T, 80T. The CAD and `06-drive-performance.md` use 8 mm pitch Gates 8MGT-1760-62, 35T / 126T (3.60:1). The masses are unaffected, but anyone ordering from the ledger would buy the wrong parts. The BOM shows the ledger text plus a note.
3. **The rear pulley mass is an estimate far from the CAD solid.** The CAD pulley is a filled disc, 9.1 kg in aluminium; the ledger says 2.1 kg for a webbed one. Both can be right, but the 2.1 kg is unproven.
4. **The motor carrier is light in the ledger.** CAD volume gives 0.79 kg in aluminium (2.3 kg in steel); the ledger carries 0.4 kg.
5. **Swingarm mass is a rule, not the geometry.** The CAD arm is a filled box (8.3 kg of aluminium by volume); the ledger's 2.278 kg is the 4.0 mm shell rule. The drawing shows the filled envelope and says so.
6. **Lower body wall.** The rev E report says 2 mm; the ledger process text still says 3 mm. The 0.922 kg follows CAD volume, so the mass is right but the text is wrong. Also, ledger process for `BV-CHS-0021` says "fabricated box" while the structures report and my drawing say cast A356.

## 5. What the drawings lack (be explicit when you attach them)

- **No GD&T**: no datum scheme, no flatness, position or runout.
- **No weld symbols or weld sizes**; no jig datums, tube cope or mitre details.
- **No surface finish, coating, anodise or paint call-outs.**
- **No threads, fits or tolerances** beyond the ISO 2768-m note on every sheet; the bearing seats (32012 X), spindle and axle fits are not given.
- **No section views, casting draft, ribs, wall-thickness map or machining allowances.** The swingarm and pulley are CAD envelopes, not designed castings.
- **No fasteners or bolt patterns** for the lid, case, lower body or carrier.
- Dimensions are the **overall extents of the projected CAD edges**; they are not design-intent dimensions. Several parts are tilted (swingarm, frame), so their extents are projected extents.
- Hidden lines are shown on the case, swingarm, pulley and carrier sheets only.
- Nobody has checked these sheets as a drafter would.

## 6. What this does not prove

- **The masses are the ledger's, not weighed, and 128 of the 220 lines are estimates** (79 calculated, 13 supplier). The BOM proves the parts add up to the ledger, not that the ledger is right.
- **The total will move.** The ledger changed during this task; the BOM is regenerated by script, but this document's tables are a snapshot of 252.93 kg.
- **The BOM is as complete as the ledger.** Anything the ledger has no row for (cell holders, motor mounts, lug plates, the parts inside the VCU and pack-internals allowances) is not in the BOM either.
- **Assembly structure is my grouping,** not a validated manufacturing BOM. No supplier part numbers beyond what the ledger names; "supplier / part ref" is the ledger name for buy lines.
- **The two derived parts are not design.** The lid and holder have provisional IDs that are not in the registry; the holder mass is an estimate and is not in the total.
- **The drawings are concept-level.** They show the rev E CAD, which has had no new FEA after the Round 2 yoke change (Z525 to Z545) and has envelope-level geometry for the swingarm, pulley and lower body.
- **TechDraw's native page export was not used** (it needs the GUI). The projection is TechDraw's, the sheet layout is mine.
