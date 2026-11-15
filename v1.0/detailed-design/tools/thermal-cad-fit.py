"""Thermal study: check that the proposed cooling hardware fits the saved CAD model.

Run from v1.0 with the bundled FreeCAD python:
  "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cad-fit.py

Reads cad/Bavuso-V1.0-adventure.FCStd (saved coordinates: generator +40 mm in Z). Does NOT modify the model.
Builds candidate solids for: two radiator cores + puller fans, battery and drive pumps, reservoirs, PTC heater,
oil-to-water exchanger, and hose centrelines, then measures their distance to every other part, to the front
tyre + fender swept over bump x steering lock (same sweep as build-adventure.py), and to the body shells.
Writes detailed-design/thermal/cad-fit.json.
"""
import sys, json, math, pathlib
sys.path.insert(0, str(pathlib.Path(sys.executable).parent))
import FreeCAD as A, Part
V = A.Vector
R = pathlib.Path(__file__).resolve().parents[2]
doc = A.openDocument(str(R / 'cad/Bavuso-V1.0-adventure.FCStd'))
O = {o.Name: o for o in doc.Objects if hasattr(o, 'Shape') and not o.Shape.isNull()}
LIFT = 40.0

def box(x, y, z, l, w, h): return Part.makeBox(l, w, h, V(x, y, z))
def cyl(a, b, r):
    a, b = V(*a), V(*b); d = b - a; return Part.makeCylinder(r, d.Length, a, d)

# ---- steering sweep of the real tyre + fender (as build-adventure.py: 5 bump x 5 lock positions)
RAKE = math.radians(25); FRONT_TRAVEL = 170
sa = V(1206.954, 0, 800 + LIFT); sb = V(1132.345, 0, 960 + LIFT); sd = sb - sa; sd.normalize()
# Fast, conservative stand-in for the real tyre+fender: a 120 mm-wide disc of radius RF+16 (fender 10-16 mm off the
# tyre), swept over 5 bump x 5 lock positions. The real 120/70 section is rounder, so this overstates the pinch.
RF = 325.3; FZ = RF - 40 + LIFT
FX = 1486.8
sweep = []
for i in (0, 5, 10, 15, 20):
    up = FRONT_TRAVEL * i / 20
    disc = cyl((FX - math.sin(RAKE) * up, -60, FZ + math.cos(RAKE) * up), (FX - math.sin(RAKE) * up, 60, FZ + math.cos(RAKE) * up), RF + 16)
    for ang in (-35, -20, 0, 20, 35):
        sweep.append(disc.transformGeometry(A.Placement(V(), A.Rotation(sd, ang), sa).toMatrix()))
steer = Part.makeCompound(sweep)

GROUPS = ('Energy', 'Electronics', 'Chassis', 'RunningGear', 'BodyStudy', 'Keepouts', 'Drive')
skip = {'Side_radiator_m1', 'Side_radiator_1', 'Battery_installation_keepout', 'Front_bump_sampled_keepout',
        'Rear_bump_sampled_keepout', 'Steering_sweep_keepout'}
body_names = [n for n in O if n.startswith(('Upper_body', 'Lower_body', 'Side_grille', 'Seam_trim', 'Battery_side_panel',
                                             'Panel_bolts', 'Belly_side_panel', 'Motor_cover', 'Windscreen'))]
static_all = {n: o.Shape for n, o in O.items() if n not in skip and n not in GROUPS and n not in body_names
          and o.Shape.Volume > 1 and not n.startswith(('Front_nominal_tire', 'Front_wheel', 'Front_fender', 'Fork_',
                                                       'Lower_triple', 'Upper_triple', 'Bar_', 'Hand_', 'Front_brake',
                                                       'Harness_bar', 'Switch', 'Lever', 'Front_master', 'Dash',
                                                       'Mirror', 'Headlamp', 'Front_indicator', 'Text', 'Label'))}
static = static_all   # bbox pre-filter in clearances() keeps this fast
print('static obstacles near the front:', len(static), flush=True)
steered = {n: o.Shape for n, o in O.items() if n.startswith(('Fork_', 'Lower_triple', 'Front_brake_hose_caliper'))}
steer_parts = Part.makeCompound([s.copy().transformGeometry(A.Placement(V(), A.Rotation(sd, ang), sa).toMatrix())
                                 for s in steered.values() for ang in (-35, -20, 0, 20, 35)])
body = {n: O[n].Shape for n in body_names}

def clearances(shape, need_static=10, need_body=4, need_steer=20):
    bb = shape.BoundBox; bb.enlarge(60)
    out = {}
    worst = None
    for n, s in static.items():
        if not bb.intersect(s.BoundBox): continue
        d = shape.distToShape(s)[0]
        if worst is None or d < worst[1]: worst = (n, d)
    out['static_min'] = (worst[0], round(worst[1], 1)) if worst else ('none within 60 mm', 99.0)
    wb = None
    for n, s in body.items():
        if not bb.intersect(s.BoundBox): continue
        d = shape.distToShape(s)[0]
        if wb is None or d < wb[1]: wb = (n, d)
    out['body_min'] = (wb[0], round(wb[1], 1)) if wb else ('none within 60 mm', 99.0)
    out['tyre_fender_lock_sweep'] = round(shape.distToShape(steer)[0], 1)
    out['fork_clamps_at_lock'] = round(shape.distToShape(steer_parts)[0], 1)
    out['pass'] = (out['static_min'][1] >= need_static and out['body_min'][1] >= need_body
                   and out['tyre_fender_lock_sweep'] >= need_steer and out['fork_clamps_at_lock'] >= need_static)
    return out

def inside_body(p):
    """True if a horizontal ray outboard from p meets the upper or lower body shell (p is under the skin)."""
    side = 1 if p.y >= 0 else -1
    ray = Part.makeLine(p, V(p.x, side * 500, p.z))
    for n in ('Upper_body_fairing_tank_STUDY', 'Lower_body_battery_covers_STUDY'):
        if n in body and ray.distToShape(body[n])[0] < 1e-6: return True
    return False

# ---- radiator candidates: core faces forward (normal +X, canted `cant` deg outboard), puller fan behind.
def radiator(side, xf, yi, yo, zl, zh, t=32.0, fan=45.0, cant=20.0):
    """Core from inner edge Y=yi to outer edge yo (magnitudes), front face at X=xf at the inner edge, height zl..zh.
    The outer edge is swept back by cant (deg) so the face looks forward-outboard toward the side scoop."""
    w = yo - yi
    core = box(0, 0, zl, t, w, zh - zl)
    fanb = box(-fan, 15, zl + 10, fan, w - 30, zh - zl - 20)   # fan shroud behind the core
    s = core.fuse(fanb)
    s.rotate(V(0, 0, 0), V(0, 0, 1), cant)    # positive cant turns the outer (+Y) edge rearward
    s.translate(V(xf - t, yi, 0))
    core.rotate(V(0, 0, 0), V(0, 0, 1), cant); core.translate(V(xf - t, yi, 0))
    if side < 0:
        m = A.Matrix(); m.scale(1, -1, 1); s = s.transformGeometry(m); core = core.transformGeometry(m)
    return s, core

results = {}
cands = []
import os, time
FAST = os.environ.get('THERMAL_FIT_FAST')
for xf in ((1090,) if FAST else (1070, 1090, 1110)):
    for (yi, yo) in ((110, 215),) if FAST else ((100, 215), (120, 215)):
        for (zl, zh) in ((650, 790),) if FAST else ((640, 800), (660, 780)):
            for cant in (20,) if FAST else (0, 25):
                cands.append((xf, yi, yo, zl, zh, cant))
best = None
for c in cands:
    xf, yi, yo, zl, zh, cant = c
    sh, core = radiator(1, xf, yi, yo, zl, zh, cant=cant)
    t0=time.time(); cl = clearances(sh); print(c, cl, f'{time.time()-t0:.0f}s', flush=True)
    face = (yo - yi) * math.cos(math.radians(cant)) * (zh - zl) / 1e6   # projected frontal area, m^2
    rec = dict(xf=xf, yi=yi, yo=yo, zl=zl, zh=zh, cant=cant, face_projected_m2=round(face, 4),
               core_area_m2=round((yo - yi) * (zh - zl) / 1e6, 4), **cl)
    results[str(c)] = rec
    if cl['pass'] and (best is None or rec['core_area_m2'] > best['core_area_m2']):
        best = rec
print('best radiator candidate (one side):', best)

# Margins of the best one, both sides, plus inside-skin test at the corners
out = dict(radiator_best=best, radiator_candidates=list(results.values()))
if best:
    for side in (-1, 1):
        sh, core = radiator(side, best['xf'], best['yi'], best['yo'], best['zl'], best['zh'], cant=best['cant'])
        bb = core.BoundBox
        corners = [V(bb.XMin + 5, side * (abs(bb.YMax if side > 0 else bb.YMin) - 5), z) for z in (bb.ZMin + 5, bb.ZMax - 5)]
        out[f'radiator_side_{side}'] = dict(bbox=[round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)],
                                            clear=clearances(sh), outer_corners_under_skin=[inside_body(p) for p in corners])

# ---- other parts (saved coordinates)
parts = {
    # battery-loop pump + PTC heater + reservoir: in the nose of the lower cover ahead of the pack's top-front step,
    # below the charger, above the front pack lugs
    'battery_pump_CWA50_class': cyl((1100, -60, 600), (1100, 60, 600), 32),
    'drive_pump_CWA50_class': cyl((1100, 70, 690), (1100, 150, 690), 30),
    'ptc_heater_5kW': box(1092, -60, 520, 50, 120, 60),
    'reservoir_shared_0p35L': box(1020, -40, 900, 60, 80, 70),
    'oil_to_water_hx': box(560, -150, 470, 80, 40, 90),
}
for n, s in parts.items():
    bb = s.BoundBox
    out[n] = dict(bbox=[round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], clear=clearances(s, need_body=3))
    print(n, out[n]['clear'])

(R / 'detailed-design/thermal').mkdir(parents=True, exist_ok=True)
(R / 'detailed-design/thermal/cad-fit.json').write_text(json.dumps(out, indent=1, default=str))
print('wrote detailed-design/thermal/cad-fit.json')
