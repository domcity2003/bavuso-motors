# Connected CAD studio — FreeCAD

October 25, 2026. **Installed and connection tested: official FreeCAD 1.1.4 Windows x86-64 portable, bundled Python 3.11.** No third-party MCP bridge, cloud account or paid license is required for the tested local workflow.

FreeCAD provides real-world-unit parametric solids, assemblies and drawing tools. Its license permits commercial work. It is an appropriate zero-cost starting CAD tool for Bavuso, although choosing it does not establish compatibility with the eventual team's preferred toolchain or replace engineering judgment. [Official features](https://www.freecad.org/features.php), [official commercial-use FAQ](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Frequently_asked_questions.md).

## How we are connected

The agent invokes FreeCAD's actual bundled Python environment and its `FreeCAD` and `Part` APIs. The checked-in script generates native editable geometry and STEP exchange geometry directly. This is a local programmatic connection, not screen scraping or an AI image conversion. FreeCAD also supports Python scripting as a documented interface. [Official scripting documentation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FreeCAD_Scripting_Basics.md).

The source script is [build-freecad-package.py](tools/build-freecad-package.py); [rebuild-cad.ps1](tools/rebuild-cad.ps1) locates the local runtime. Run from PowerShell:

```powershell
./documentation/tools/rebuild-cad.ps1
```

The CAD script reads [the coordinate JSON](models/package-reservations.json). Change those inputs through the model generator, rebuild the JSON, then rebuild CAD for reproducible changes. GUI changes to the generated document will be overwritten on regeneration; save exploratory manual revisions separately. Later production parts need native parametric sources and controlled drawings, not perpetual regeneration of bounding boxes.

## Open the studio

Double-click **Open Bavuso CAD.cmd** in the project root. It opens the native [Bavuso-B0-package.FCStd](models/Bavuso-B0-package.FCStd). The editable tree contains five box reservations, three cylindrical body/tire envelopes, a pivot reference and a notes sheet. Length, width, height, radius and placement are editable properties. These are independent primitives, not a constrained kinematic assembly or the final body surfaces.

The [STEP file](models/Bavuso-B0-package.step) is neutral exchange geometry for other CAD tools. STEP does not preserve the complete FreeCAD parametric editing history. Current solids include conservative tire cylinders and known overlaps and should never be sent to a machine shop as manufactured parts.

## Connection test performed

[Machine-readable result](models/freecad-connection-test.json) records the exact version and outputs. The test:

1. Imported FreeCAD/Part and constructed valid positive-volume solids.
2. Saved the native document and reopened it, checking object count.
3. Exported STEP, re-imported it and checked shape validity and summed volume agreement.

These checks passed. They establish functioning local CAD creation and exchange, not a correct vehicle package, released tolerances, structural strength, aero performance or manufacturability. The graphical application has now also been opened and inspected: Part workbench, standard mm/kg units, colored translucent reservations, fitted axonometric view and expanded component tree. The setup macro saves this presentation; [studio setup record](models/studio-setup.json) and [viewport image](visuals/freecad-studio.png) record the session.

## Runtime provenance and future repository

Downloaded from [official FreeCAD release 1.1.4](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4), archive `FreeCAD_1.1.4-Windows-x86_64-py311.7z`. Its SHA-256 matched the digest returned by the official GitHub release API:

```text
4828741fc91ee37fafcdb97a1abacb18b04ba451ac4372d9ff7a7349b36f4d6d
```

Runtime lives in the project's `.tools/FreeCAD_1.1.4-Windows-x86_64-py311/`; downloaded archive is in `.tools/freecad-download/`. This portable installation avoids an installer or file-association changes. The runtime is large and is a local dependency: exclude `.tools/` from a future source repository, retaining source scripts, version/hash manifest and retrieval instructions. No Git repository was initialized here.

Onshape's free tier requires public, noncommercial documents, and Fusion personal use is for qualifying noncommercial projects. Those free tiers are poor default license assumptions for developing Bavuso as a commercial product. Blender is useful for artistic body shaping/rendering alongside CAD; engineering solids and manufacturing drawings need their own source definition. [Onshape plans](https://www.onshape.com/en/pricing), [Fusion personal terms](https://www.autodesk.com/products/fusion-360/personal), [Blender commercial-use FAQ](https://www.blender.org/support/faq/).
