# Bavuso V1.0 detailed design: index

November 15, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5).

These are the engineering studies behind the adventure model (`cad/Bavuso-V1.0-adventure.FCStd`, built by `tools/build-adventure.py`). Each report says what was run, on which geometry, and what it does not cover.

| Study | Report | Inputs and scripts |
|---|---|---|
| Structure (frame, pack case, crash guard FEA) | `structural-fea.md` | `structures/` (CalculiX decks; result files are not in git) |
| Thermal (cells, motor, inverter, charging) | `thermal-study.md` | `thermal/` |
| Aerodynamics (OpenFOAM, 3 meshes, ±10° yaw) | `aero-study.md` | `aero/` (the `run/` folder of solver output, about 7 GB, is not in git) |
| Vehicle dynamics (stability, weave and wobble, braking) | `dynamics-study.md` | `dynamics/` |
| Electrical (HV and LV architecture, harness) | `electrical-detailed.md` | `electrical/` |
| Bought-in parts against the CAD | `supplier-parts.md` | `supplier/` |
| Safety, crash, homologation, validation plan | `compliance-and-validation.md` | `compliance/` |
| Shared brief given to the analysis agents | `BRIEF.md` | |

**Rider ergonomics** is covered in `../comfort-study.md` and `../rider-fit.json`.

**Geometry has moved since these studies ran.** The November 14 comfort change pulled the upper rails in, lowered the seat and re-sectioned the shock bridge. The November 20 waist change pulled the rail joint in again, to ±125. The FEA should be re-run on the new frame; `structural-fea.md` lists what changed. The aero runs used the November 12 model.

**Build status (Nov 20):** 61 of 62 clearance checks pass, and the mass is 326.7 kg. The one open check is the lower battery cover 1.99 mm from the pack, against a 5 mm target.
