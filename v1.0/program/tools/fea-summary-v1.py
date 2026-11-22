"""Verdict tables for the V1 structure (reads results-<variant>-h12.json). usage: python fea-summary-v1.py <variant>
November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program."""
import json, re, sys, importlib.util, collections
from pathlib import Path
H = Path(__file__).resolve().parent; OUT = H.parents[1] / 'program' / 'data' / 'fea'
var = sys.argv[1]; R = json.loads((OUT / ('results-%s-h12.json' % var)).read_text()); V = R['V']
sp = importlib.util.spec_from_file_location('fat', str(H / 'fea-fatigue-v1.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
fy = lambda m: 200.0 if m in ('SAX', 'STW') else (200.0 if m.startswith('SAR') else 435.0)
req = lambda c: 1.5 if c.startswith('C1') else 1.0 if c.startswith(('C7', 'C9')) else 1.2
rows = []
for c, d in R['cases'].items():
    best = None
    for m, v in d['stress'].items():
        if m.startswith(('PACK', 'YOKE', 'LUG', 'PIV')): continue
        sf = fy(m) / max(v[0], 1e-6)
        if best is None or sf < best[0]: best = (sf, m, v[0])
    pk = {k: v[0] for k, v in d.get('pack_away_from_lugs', {}).items()}
    rows.append((c, best, pk))
print('| Case | Worst member | Stress MPa | SF | Required | Verdict | Worst pack stress away from lugs (MPa, vs 140) |\n|---|---|---|---|---|---|---|')
for c, b, pk in rows:
    print('| %s | %s | %.0f | %.2f | %.1f | %s | %s |' % (c, b[1], b[2], b[0], req(c), 'pass' if b[0] >= req(c) else 'FAIL', ('%.0f' % max(pk.values())) if pk else '-'))
fr = F.compute(R)
print('\nFatigue worst 8:'); [print('| %s | FAT %s | D %.2f | %s |' % (r['member'], r['FAT'], r['miner_D'], r['verdict'])) for r in fr[:8]]
print('\nStiffness', R['stiffness'])
print('Bearing loads (frame model):', {c: d['bearing_RF_N'] for c, d in R['cases'].items() if c.startswith(('C1', 'D1', 'C6'))})
g = collections.defaultdict(float)
for k, v in R['member_mass_kg'].items():
    if k.startswith(('BOLT', 'SHOCK', 'YOKE', 'AXF', 'FORK')): continue
    g[re.sub(r'[LR]$', '', k) if not k.startswith('SAR') else 'SAR'] += v
print('Mass by member (kg):', {k: round(v, 2) for k, v in sorted(g.items(), key=lambda x: -x[1])}, 'total', round(sum(g.values()), 2))
print('pack case mass kg', R['pack_case_mass_kg'], 'area', R['pack_case_area_m2'])
