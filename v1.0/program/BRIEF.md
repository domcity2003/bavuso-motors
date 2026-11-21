# Bavuso V1 final-spec program: shared brief for all agents

November 21, 2026, US Central. Written by Claude Opus 5.5 (program lead). Read this before doing anything.

## Goal
Turn the Bavuso V1.0 adventure concept into a **finished, credible V1 design package**. The owner will attach it to applications, so it must be:
- coherent: every number agrees across documents;
- honest: say what is analysed, what is estimated and what is untested;
- professional.

**The main problem is weight.**
- Today the bike is 328.4 kg / 724 lb.
- The owner's brief prefers under 400 lb, plus 200 mi at 70 mph, 125+ mph, native NACS (Tesla) charging, and comfort and gust stability at 77 mph.
- It is a premium status and innovation product, with a unit cost at scale of about $30–35k or less.

A 400 lb bike and 200 mi at 70 mph do not both close with today's cells, so **the program will choose an optimum target** (one recommended point, not either/or extremes). The bike is then re-architected to that target.

Read the independent review first: `v1.0/Bavuso-V1.0-Concept-Freeze-Review.pdf`, which reviewed git 5f451ef. Earlier budget work is in `research/range-weight-budget.md`.

**Framing for the final write-up (owner's request):**
- Say plainly that V1 is a deliberate compromise. The owner gave up the original under-400 lb and 200-mile goals for a buildable 240 kg, about 150-mile bike.
- Present it as a V1 with a planned improvement path: better cells, lower drag, lighter chassis, and later a two-up variant.

## Where things are
- **Repo root:** `C:\Users\DomBa\DOM\5_Projects\Bavuso Motors`. Work from `v1.0`.
  - **Never commit, push or change git state.** The program lead does that.
- **CAD generator:** `tools/build-adventure.py`, about 1,300 lines of FreeCAD python, and the only geometry source.
  - Only an agent explicitly told it owns this file may edit it.
  - Everyone else writes **"CAD change requests"** with exact numbers.
- **Built model:** `cad/Bavuso-V1.0-adventure.FCStd`.
  - The saved model is lifted +53.1 mm in Z versus generator coordinates.
  - Axes: X forward, Y left, Z up, mm. PZ=350.
- **Mass:**
  - Ledger: `mass-rollup.csv`, `mass-rollup.json`.
  - Script: `tools/mass-rollup.py`.
  - Part status: `component-status-adventure.csv`.
- **Existing studies:**
  - `detailed-design/`: FEA, thermal, aero, dynamics, electrical, supplier, compliance. Its `README.md` is the index.
  - Layout, drive and suspension: `drive-study.md`, `rear-suspension.md`, `adventure-layout.md`.
  - Rider: `comfort-study.md`.
  - Cost: `cost-model.csv`, `cost-and-sourcing.md`, `powertrain-cost-down.md`.
  - Research: `research/` at the repo root.
- **Old variants are not live:** the files named `*rework*`, `*integrated*` and `*emrax228*`. Ignore them unless told otherwise.

## Tools
- **FreeCAD python, the only python on this machine:** `../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe`, run from `v1.0`.
  - It includes numpy, scipy, PIL and FEM.
  - `ccx.exe` (CalculiX) and `gmsh.exe` are in the same bin folder.
- **Other tools:**
  - OpenFOAM: `../.tools/blueCFD-Core-2024`, with helper `../.tools/ofrun.sh`.
  - Blender: `../.tools/blender-5.2.3-windows-x64`.
- **Full CAD build:** about 45 minutes. Use the Bash tool with `run_in_background` and wait for it; do not poll in a sleep loop.
- **CPU:** 16 cores, but other agents share the machine.
  - Use at most 4 threads for heavy solves.
  - **Never kill a process you did not start.** Check the command line first.

## Rules
- **Explain simply and lead with the plain answer.** The owner, Dominic, is a finance person who builds with AI, not an engineer.
  - Plain language with numbers.
  - Do not call him a founder or a software engineer.
- **Survey public prior art and real supplier data first.** Prefer real, purchasable parts with published masses and prices. Cite URLs. Label every number as one of: measured / supplier / calculated / estimate.
- **Verify before calling a result good.** Do hand checks, convergence checks and balance checks. Say what was not checked.
- **Never read or copy secrets** (.env, tokens, keys).
- **Report files:**
  - Stamp: "November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program."
  - Start with `## The plain answer`.
  - Include a verdict or summary table.
  - End with `## What this does not prove`.
- **Where files go:**
  - Program documents go in `program/`.
  - Scripts go in `program/tools/`.
  - Data goes in `program/data/`.
  - Large solver output goes in a `run/` subfolder.
- **Final reply to the program lead: under 250 words.** Give the headline numbers, the decisions you made or need, any CAD change requests in brief (full detail stays in your file), and any blockers. The lead has a tight context budget, so do not paste file contents.
