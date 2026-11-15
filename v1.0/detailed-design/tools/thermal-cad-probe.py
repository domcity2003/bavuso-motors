"""Thermal study: free-space probe for radiators in the front stack (saved CAD coordinates, +40 mm Z).
Marks a grid point free if it is >=10 mm from every non-body part, >=4 mm inside the body skin (a ray outboard
meets the skin), and >=20 mm from the front tyre+fender lock sweep (conservative disc model from thermal-cad-fit.py).
Writes detailed-design/thermal/cad-probe.json (free points, right side; the bike is symmetric here except the inverter).
Run: "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cad-probe.py
"""
import sys, json, pathlib, importlib.util, math
sys.argv = [sys.argv[0]]
HERE = pathlib.Path(__file__).resolve().parent
import os; os.environ['THERMAL_FIT_FAST'] = '1'
src = (HERE / 'thermal-cad-fit.py').read_text()
src = src[:src.index('results = {}')]           # reuse the model loading + clearance helpers only
g = {'__file__': str(HERE / 'thermal-cad-fit.py'), '__name__': 'probe'}; exec(compile(src, 'thermal-cad-fit.py', 'exec'), g)
V, Part = g['V'], g['Part']; static, body, steer = g['static'], g['body'], g['steer']; inside_body = g['inside_body']
pts = []
import time; t0=time.time()
for x in range(950, 1131, 20):
    for y in range(110, 211, 10):
        for z in range(630, 811, 20):
            p = V(x, y, z); v = Part.Vertex(p); ok = True
            for n, s in static.items():
                bb = s.BoundBox
                if not (bb.XMin - 10 <= x <= bb.XMax + 10 and bb.YMin - 10 <= y <= bb.YMax + 10 and bb.ZMin - 10 <= z <= bb.ZMax + 10): continue
                if v.distToShape(s)[0] < 10: ok = False; break
            if not ok: continue
            if not (inside_body(p) and inside_body(V(x, y + 4, z)) and inside_body(V(x, y, z + 6))): continue   # >=4 mm under the side skin
            if v.distToShape(steer)[0] < 20: continue
            pts.append((x, y, z))
print('free points', len(pts))
print('probe time', round(time.time()-t0), 's')
for x in range(950, 1131, 20):
    sl = [(y, z) for (xx, y, z) in pts if xx == x]
    if sl:
        ys = sorted({y for y, _ in sl}); zs = sorted({z for _, z in sl})
        print(f'X{x}: {len(sl)} pts, Y {ys[0]}..{ys[-1]}, Z {zs[0]}..{zs[-1]}')
        for y in ys:
            zz = sorted(z for yy, z in sl if yy == y); print(f'     Y{y}: Z {zz}')
(HERE.parent / 'thermal' / 'cad-probe.json').write_text(json.dumps(pts))
