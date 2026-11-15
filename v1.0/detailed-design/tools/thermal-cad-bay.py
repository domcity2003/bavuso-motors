"""Thermal study: clearance check for pumps, heater, valve, reservoir and oil cooler (saved CAD coordinates).
Service bay = the space the HV cabinet vacated on the pack roof, above the IPM motor, behind the charger.
Run: "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cad-bay.py
"""
import json, pathlib, os
HERE = pathlib.Path(__file__).resolve().parent
os.environ['THERMAL_FIT_FAST'] = '1'
src = (HERE / 'thermal-cad-fit.py').read_text(); src = src[:src.index('results = {}')]
g = {'__file__': str(HERE / 'thermal-cad-fit.py'), '__name__': 'bay'}; exec(compile(src, 'thermal-cad-fit.py', 'exec'), g)
box, cyl, clearances = g['box'], g['cyl'], g['clearances']
parts = {
    'battery_pump_CWA50': cyl((625, -140, 705), (625, -50, 705), 32),
    'drive_pump_CWA50': cyl((625, 50, 705), (625, 140, 705), 32),
    'ptc_heater_5kW': box(598, -44, 668, 55, 88, 62),
    'valve_4port_left': box(598, -188, 676, 50, 38, 52),
    # degas bottle: integrated in the right radiator's top tank inside the pod (Option B envelope), not checked separately
    'oil_to_water_hx': box(560, -150, 470, 80, 40, 90),
}
out = {}
for n, s in parts.items():
    bb = s.BoundBox
    out[n] = dict(bbox=[round(v) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], clear=clearances(s, need_body=3))
    print(n, out[n], flush=True)
(HERE.parent / 'thermal' / 'cad-bay.json').write_text(json.dumps(out, indent=1, default=str))
