"""V1 dynamics step 1: pull mass-distribution shapes, lean-clearance points and tyre crowns from the rev D CAD.

Reads cad/Bavuso-V1.0-adventure.FCStd (read-only; saved model: X forward from the rear axle, Y, Z up, mm, ground Z=0)
and writes program/data/dynamics/cad-extract.json:
  per solid: volume, centre of volume, volume inertia tensor about that centre (unit density; scaled to ledger mass
  later), a decimated cloud of outboard/low tessellation vertices for the lean check, bounding box;
  plus a tyre crown-radius fit and the wheel/pivot/head positions.
Run from v1.0: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/dynamics-v1-extract.py
November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import json, math
from pathlib import Path
import FreeCAD

R = Path(__file__).resolve().parents[2]
doc = FreeCAD.openDocument(str(R / 'cad' / 'Bavuso-V1.0-adventure.FCStd'))
out = {}
for o in doc.Objects:
    if o.TypeId != 'Part::Feature' or not o.InList:
        continue
    if o.InList[0].Name == 'Keepouts' or 'keepout' in o.Name.lower():
        continue
    s = o.Shape
    if s.isNull():
        continue
    rec = dict(label=o.Label, group=o.InList[0].Name)
    try:
        solids = s.Solids
        vt = sum(so.Volume for so in solids)
        if vt > 1.0:
            c = FreeCAD.Vector(0, 0, 0)
            for so in solids:
                c += so.CenterOfMass * so.Volume
            c = c * (1.0 / vt)
            I = [[0.0] * 3 for _ in range(3)]
            for so in solids:
                Ii = so.MatrixOfInertia; d = so.CenterOfMass - c; v = so.Volume
                dd = [d.x, d.y, d.z]; d2 = d.x ** 2 + d.y ** 2 + d.z ** 2
                for i in range(3):
                    for j in range(3):
                        I[i][j] += Ii.A[4 * i + j] + v * ((d2 if i == j else 0.0) - dd[i] * dd[j])
            rec.update(volume=vt, centre=[c.x, c.y, c.z], inertia=I)
    except Exception as e:
        rec['inertia_error'] = str(e)
    try:
        pts, _ = s.tessellate(2.0)
        keep = {}
        for p in pts:
            if abs(p.y) > 60 and p.z < 800:
                k = (round(p.x / 10), round(p.y / 3), round(p.z / 3))
                keep[k] = (round(p.x, 1), round(p.y, 1), round(p.z, 1))
        rec['lean_points'] = list(keep.values())
        if o.Name in ('Front_nominal_tire', 'Rear_nominal_tire'):   # crown fit: max radius vs lateral offset
            cx, cz = s.BoundBox.Center.x, s.BoundBox.Center.z
            prof = {}
            for p in pts:
                r = math.hypot(p.x - cx, p.z - cz); yb = round(p.y / 4) * 4
                prof[yb] = max(prof.get(yb, 0), r)
            rec['tyre_profile'] = sorted(prof.items()); rec['tyre_centre'] = [cx, cz]
    except Exception as e:
        rec['tess_error'] = str(e)
    bb = s.BoundBox
    rec['bbox'] = [bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax]
    out[o.Name] = rec
dst = R / 'program' / 'data' / 'dynamics' / 'cad-extract.json'
dst.write_text(json.dumps(out))
print('objects', len(out), '->', dst)
