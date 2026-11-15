"""Size the lower-edge chamfer on the battery covers / belly / motor side covers so hard parts touch >= 3 deg
after the folding pegs (target 50 deg solo, 48 deg two-up, steady-turn compression). Uses dyn-lean.py's drop model.
Prepared November 13, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5)."""
import importlib.util, json, math
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('lean', HERE / 'dyn-lean.py'); ln = importlib.util.module_from_spec(spec); spec.loader.exec_module(ln)
out = {}
for case, deg in (('solo', 50.0), ('twoup', 48.0)):
    phi = math.radians(deg); df, dr, tf, tr, drs = ln.drops(phi, case)
    rows = []
    for x in (585.0, 800.0, 1000.0, 1108.0):
        rho = ln.RHO_R + (ln.RHO_F - ln.RHO_R) * x / ln.WB
        d = dr + (df - dr) * x / ln.WB
        ymax = lambda z: ((z - d - rho) * math.cos(phi) + rho) / math.sin(phi)
        rows.append(dict(x=x, ymax_at_z223=ymax(223), z_for_y212=d + rho + (212 * math.sin(phi) - rho) / math.cos(phi)))
    out[case] = dict(target_deg=deg, rows=rows)
    print(case, deg, [(r['x'], round(r['ymax_at_z223'], 1), round(r['z_for_y212'], 1)) for r in rows])
(ln.OUT / 'lean-chamfer.json').write_text(json.dumps(out, indent=1))
