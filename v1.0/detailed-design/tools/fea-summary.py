"""Verdict tables for structural-fea.md from the fea-frame.py / fea-fatigue.py outputs.

November 13, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).
usage: python fea-summary.py  (reads structures/results-*.json, writes structures/summary.json and prints markdown)
"""
import json, math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'structures'
FY = {'steel': 435.0, 'AL6061': 240.0, 'A356': 200.0, 'pack_parent': 250.0, 'pack_seam': 140.0}
REQ = {'C1': 1.5, 'C2': 1.2, 'C3': 1.2, 'C4': 1.2, 'C5': 1.2, 'C6': 1.2, 'C7': 1.0, 'C9': 1.0}
SKIP = ('PIV', 'LUGF', 'LUGR', 'LUGT', 'GUS')   # PIV/LUG blocks are stand-ins; checked separately (bolts, Goodman)

def mat(member, V):
    if member.startswith('PACK'): return 'pack'
    if member.startswith('SA') and member[2] in 'LR': return 'AL6061'
    if member in ('SAX', 'STW'): return V.get('tower_mat', 'AL6061') if V.get('tower_mat') != 'AL6061' else 'AL6061'
    return 'steel'

def worst(res):
    V = res['V']; rows = {}
    for case, r in res['cases'].items():
        tag = case.split('_')[0][:2]
        best = None
        for m, (val, sig, loc) in r['stress'].items():
            if m.startswith(SKIP): continue
            mt = mat(m, V)
            if mt == 'pack':
                # peak next to a lug sits in the 10 mm machined pad (parent metal); away from lugs use the seam value
                fy = FY['pack_parent']
            else:
                fy = FY[mt if mt in FY else 'steel']
            sf = fy / val if val else math.inf
            if best is None or sf < best[3]: best = (m, val, fy, sf)
        pa = r.get('pack_away_from_lugs', {})
        pk = max(pa.items(), key=lambda kv: kv[1][0]) if pa else None
        rows[case] = dict(member=best[0], stress=round(best[1], 1), yield_=best[2], SF=round(best[3], 2), req=REQ[tag],
                          verdict='pass' if best[3] >= REQ[tag] else 'FAIL',
                          pack_away=(pk[0], pk[1][0], round(FY['pack_seam'] / pk[1][0], 2)) if pk else None,
                          shock_N=r.get('shock_force_N'))
    return rows

out = {}
for f in sorted(OUT.glob('results-*.json')):
    res = json.loads(f.read_text())
    if not res.get('cases'): continue
    out[f.stem] = dict(worst=worst(res), stiffness=res.get('stiffness'), mass=res.get('member_mass_kg'), h=res['h'], n_nodes=res['n_nodes'])
(OUT / 'summary.json').write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print('\n### ' + k, v['stiffness'])
    print('| case | governing member | nominal stress MPa | yield MPa | SF | required | verdict | pack away from lugs (vs 140 seam) | shock N |')
    print('|---|---|---|---|---|---|---|---|---|')
    for c, r in v['worst'].items():
        pa = '%s %.0f (SF %.2f)' % r['pack_away'] if r['pack_away'] else ''
        print('| %s | %s | %.0f | %.0f | %.2f | %.1f | %s | %s | %s |' % (c, r['member'], r['stress'], r['yield_'], r['SF'], r['req'], r['verdict'], pa, r['shock_N'] or ''))
