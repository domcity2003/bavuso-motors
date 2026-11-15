"""Thermal study: clearance check of the two radiator layouts (saved CAD coordinates).
Option A: core inside today's side reservation (fits the body as is).
Option B: canted core in a side pod (needs a body change), core + 30 mm pusher fan on its inboard/front face.
Checks frame, electronics, pack and other non-body parts (>=10 mm), tyre+fender lock sweep (>=20 mm),
fork/clamps at lock (>=10 mm). Body clearance is reported but Option B needs a new pod skin anyway.
Run: "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cad-pods.py
"""
import sys, json, math, pathlib, os
HERE = pathlib.Path(__file__).resolve().parent
os.environ['THERMAL_FIT_FAST'] = '1'
src = (HERE / 'thermal-cad-fit.py').read_text(); src = src[:src.index('results = {}')]
g = {'__file__': str(HERE / 'thermal-cad-fit.py'), '__name__': 'pods'}; exec(compile(src, 'thermal-cad-fit.py', 'exec'), g)
A, V, Part, clearances = g['A'], g['V'], g['Part'], g['clearances']

def plan_slab(ax, ay, length, ang_deg, thick, zl, zh, side=1, offset=0.0):
    """Slab whose face runs from plan point (ax,ay) at ang_deg from +X, thickness toward the rear/outboard normal."""
    b = Part.makeBox(length, thick, zh - zl, V(0, offset, zl))
    b.rotate(V(0, 0, 0), V(0, 0, 1), ang_deg); b.translate(V(ax, ay, 0))
    if side < 0:
        m = A.Matrix(); m.scale(1, -1, 1); b = b.transformGeometry(m)
    return b

out = {}
# Option A: forward-canted core in today's reservation volume (free-space probe: X950-1030, Y130-200, Z670-790)
for side in (1, -1):
    core = plan_slab(958, 142, 85, 40, 28, 680, 790, side)                 # 85 mm face, 28 mm core
    fan = plan_slab(958, 142, 85, 40, 22, 690, 780, side, offset=-22)      # 22 mm slim pusher, inboard/front face
    s = core.fuse(fan); bb = s.BoundBox
    out[f'A_side{side}'] = dict(face_m2=round(0.085 * 0.110, 4), bbox=[round(v) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], clear=clearances(s))
    print('A', side, out[f'A_side{side}'], flush=True)
# Option B: side pod, 210 mm x 150 mm core at 35 deg (face looks forward-inboard, air exits rear-outboard through the louvres)
for side in (1, -1):
    core = plan_slab(985, 160, 210, 35, 32, 640, 780, side)
    fan = plan_slab(985, 160, 210, 35, 30, 652, 768, side, offset=-30)
    s = core.fuse(fan); bb = s.BoundBox
    out[f'B_side{side}'] = dict(face_m2=round(0.210 * 0.140, 4), bbox=[round(v) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], clear=clearances(s, need_body=-1e9))
    print('B', side, out[f'B_side{side}'], flush=True)
(HERE.parent / 'thermal' / 'cad-pods.json').write_text(json.dumps(out, indent=1, default=str))
