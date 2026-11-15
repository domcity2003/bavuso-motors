"""Vehicle dynamics: pull mass-distribution shapes and lean-clearance points out of the saved CAD.

Reads cad/Bavuso-V1.0-adventure.FCStd (saved model: X forward from the rear axle, Y left, Z up, mm,
ground at Z=0) and writes detailed-design/dynamics/cad-extract.json with, per visible solid:
  - volume, centre of volume, and the volume inertia tensor about that centre (OCC MatrixOfInertia,
    unit density). dyn-massprops.py scales it by (roll-up mass / volume) so each part keeps its own
    rotational inertia instead of being a point mass.
  - a decimated cloud of outboard/low tessellation vertices (|Y|>60 mm, Z<800 mm) for the lean-angle check.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/dyn-cad-extract.py
Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import json, sys
from pathlib import Path
import FreeCAD

R = Path(__file__).resolve().parents[2]
doc = FreeCAD.openDocument(str(R / 'cad' / 'Bavuso-V1.0-adventure.FCStd'))
GROUPS = {'Energy', 'Electronics', 'Drive', 'Chassis', 'RunningGear', 'BodyStudy', 'Keepouts'}
out = {}
for o in doc.Objects:
    if o.Name in GROUPS or not hasattr(o, 'Shape') or o.Shape.isNull():
        continue
    if 'keepout' in o.Name.lower() or o.Name in ('Pivot_reference', 'Main_fuse_branch_search_region'):
        continue
    s = o.Shape
    rec = dict(label=o.Label)
    try:
        vol = s.Volume
        if vol > 1.0:
            solids = s.Solids
            if len(solids) == 1:
                c = solids[0].CenterOfMass; I = solids[0].MatrixOfInertia
            else:  # compound of solids: combine about the common centre (parallel axis)
                c = FreeCAD.Vector(0, 0, 0); vt = 0
                for so in solids:
                    c += so.CenterOfMass * so.Volume; vt += so.Volume
                c = c * (1.0 / vt)
                I = [[0.0] * 3 for _ in range(3)]
                for so in solids:
                    Ii = so.MatrixOfInertia; d = so.CenterOfMass - c; v = so.Volume
                    dd = [d.x, d.y, d.z]; d2 = d.x ** 2 + d.y ** 2 + d.z ** 2
                    for i in range(3):
                        for j in range(3):
                            I[i][j] += Ii.A[4 * i + j] + v * ((d2 if i == j else 0.0) - dd[i] * dd[j])
                rec.update(volume=vol, centre=[c.x, c.y, c.z], inertia=I)
                raise StopIteration
            rec.update(volume=vol, centre=[c.x, c.y, c.z],
                       inertia=[[I.A[4 * i + j] for j in range(3)] for i in range(3)])
    except StopIteration:
        pass
    except Exception as e:  # shells etc.
        rec['inertia_error'] = str(e)
    # lean-clearance cloud
    try:
        pts, _ = s.tessellate(2.0)
        keep = {}
        for p in pts:
            if abs(p.y) > 60 and p.z < 800:
                k = (round(p.x / 10), round(p.y / 3), round(p.z / 3))
                keep[k] = (round(p.x, 1), round(p.y, 1), round(p.z, 1))
        rec['lean_points'] = list(keep.values())
    except Exception as e:
        rec['tess_error'] = str(e)
    bb = s.BoundBox
    rec['bbox'] = [bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax]
    out[o.Name] = rec
dst = R / 'detailed-design' / 'dynamics' / 'cad-extract.json'
dst.write_text(json.dumps(out))
print('objects', len(out), '->', dst)
