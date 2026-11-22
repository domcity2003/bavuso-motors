from pathlib import Path
base = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools')
def patch(fn, pairs):
    p = base / fn; s = p.read_text(encoding='utf-8')
    for a, b in pairs:
        assert s.count(a) == 1, (fn, s.count(a), a[:60]); s = s.replace(a, b)
    p.write_text(s, encoding='utf-8')
patch('fea-size-v1.py', [
 ("        ro, t = newV[name]; rf = grp[name][0]\n        f = min(1.4", "        ro, t = newV[name]; rf = grp[name][0]\n        if 0.92 <= rf <= 1.0: return\n        f = min(1.4"),
 ("            s = newV['struts'][k]; ro, t = s[2], s[3]; f = min(1.4, max(0.75, grp[nm][0] ** 0.9)); tn", "            s = newV['struts'][k]; ro, t = s[2], s[3]; f = min(1.4, max(0.75, grp[nm][0] ** 0.9)); f = 1.0 if 0.92 <= grp[nm][0] <= 1.0 else f; tn"),
])
patch('fea-fatigue-v1.py', [
 ("    return 45, 'steel 4130 thin-wall tube TIG joint (FAT 45)'", "    if V.get('node_fat'): return V['node_fat'], 'steel tube on cast/forged node, full-penetration butt weld (scenario FAT %s)' % V['node_fat']\n    return 45, 'steel 4130 thin-wall tube TIG joint (FAT 45)'"),
])
patch('fea-swingarm-v1.py', [("env = dict(os.environ, OMP_NUM_THREADS='4', CCX_NPROC_EQUATION_SOLVER='4')", "env = dict(os.environ, OMP_NUM_THREADS=os.environ.get('FEA_THREADS', '2'), CCX_NPROC_EQUATION_SOLVER=os.environ.get('FEA_THREADS', '2'))")])
print('patched')
