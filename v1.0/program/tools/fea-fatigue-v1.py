"""Fatigue of the welded joints (Miner, IIW nominal-stress) for the Bavuso V1 solo structure, from fea-frame-v1.py stress changes.

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
Same method as detailed-design/tools/fea-fatigue.py (IIW-2259-15, FAT at 2e6 cycles, slope 3 to the 1e7 knee then 22,
gamma_Mf 1.25 on stress, Miner D <= 0.5, no mean-stress correction for welded details).
Spectrum: the old road-load spectrum (bumps, braking, cornering; 160,000 km) plus a DRIVE spectrum for the belt/thrust loads:
launches at 20/40/60/80/100 % of peak torque (1e6/2e5/5e4/1e4/2e3 events), regen at half those counts, and 1e3 belt shocks at the 11.3 kN design pull.
Stress per unit load = (case - C1 static)/unit; the belt preload is in C1 so only the change counts.
usage: python fea-fatigue-v1.py results-<tag>.json [spectrum_multiplier] [arm_fat]
"""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE.parents[1] / 'program' / 'data' / 'fea'
GAM = 1.25; D_ALLOW = 0.5

BUMP0 = [(0.10, 2.0e7), (0.20, 3.0e6), (0.35, 3.0e5), (0.50, 5.0e4), (0.75, 5.0e3), (1.00, 1.0e3), (1.50, 1.0e2), (2.00, 1.0e1)]
BRAKE0 = [(0.3, 2.0e5), (0.6, 1.0e4), (0.9, 1.0e3), (1.1, 1.0e2)]
CORNER0 = [(1.0, 5.0e4)]                                      # per lean direction
LAUNCH0 = [(0.2, 1.0e6), (0.4, 2.0e5), (0.6, 5.0e4), (0.8, 1.0e4), (1.0, 2.0e3)]
REGEN0 = [(a, n / 2) for a, n in LAUNCH0]
SHOCK0 = [(1.0, 1.0e3)]

def fat_of(m, V, arm_fat):
    if m.startswith('SAR'): return arm_fat, 'Al box arm (welded 6061 FAT 22; cast/forged A356/6082 FAT 40)'
    if m in ('SAX', 'STW'): return 40, 'A356-T6 cast tower/brace node, bolted, no weld (FAT 40)'
    if m.startswith('PACK'): return 28, 'Al 6082 case seam/bolt-hole net section (FAT 28)'
    if m == 'STB' and V.get('forged_shock_bridge'): return 56, 'forged steel bridge, integral clevis, no weld (FAT 56)'
    if (m.startswith(('UR2', 'DL', 'GUS')) or m == 'HT') and V.get('cast_headstock'): return 63, 'cast steel headstock, full-penetration butt weld on 60 mm spigot (FAT 63)'
    if m == 'STB': return 36, 'steel plate fillet to cross tube (FAT 36)'
    if m.startswith('LUG'): return 45, 'steel lug block welded to tube end (FAT 45)'
    if m.startswith(('STUB', 'PIV')): return 45, 'machined stub welded to the pivot block (FAT 45)'
    if V.get('node_fat'): return V['node_fat'], 'steel tube on cast/forged node, full-penetration butt weld (scenario FAT %s)' % V['node_fat']
    return 45, 'steel 4130 thin-wall tube TIG joint (FAT 45)'

def N_of(dsig, fat):
    d = GAM * dsig
    if d <= 0: return math.inf
    knee = fat * (2e6 / 1e7) ** (1 / 3)
    return 2e6 * (fat / d) ** 3 if d >= knee else 1e7 * (knee / d) ** 22

def compute(R, X=1.0, arm_fat=None):
    V = R['V']; arm_fat = arm_fat or V.get('arm_fat', 22)
    dl = R['delta_vs_C1']
    g = lambda c: {k: v[0] for k, v in dl[c]['members'].items()}
    spg_f = {k: v / 2.0 for k, v in g('C2_front_bump_3g').items()}
    spg_r = {k: v / 2.0 for k, v in g('C6_rear_bump_3g').items()}
    br = {k: v / 1.1 for k, v in g('C3_braking_1.1g').items()}
    coL = {k: v * 0.414 / 1.12 for k, v in g('C5L_corner_lean_left').items()}
    coR = {k: v * 0.414 / 1.12 for k, v in g('C5R_corner_lean_right').items()}
    d1, d2, d3 = g('D1_belt_design_11.3kN'), g('D2_launch_peak_torque'), g('D3_regen_peak_torque')
    for src, dst, f in [('C2_front_bump_3g', spg_f, 0.5), ('C6_rear_bump_3g', spg_r, 0.5), ('C3_braking_1.1g', br, 1 / 1.1),
                        ('C5L_corner_lean_left', coL, 0.414 / 1.12), ('C5R_corner_lean_right', coR, 0.414 / 1.12),
                        ('D1_belt_design_11.3kN', d1, 1), ('D2_launch_peak_torque', d2, 1), ('D3_regen_peak_torque', d3, 1)]:
        for k, v in dl[src]['pack_lug_edge'].items():
            if k.startswith('PACK'): dst[k + '@lug'] = v[0] * f
    sc = lambda L: [(a, n * X) for a, n in L]
    rows = []
    for m in sorted(set(spg_f) | set(spg_r)):
        fat, why = fat_of(m, V, arm_fat); D = 0.0; parts = dict(bump=0, brake=0, corner=0, drive=0)
        for spg in (spg_f.get(m, 0), spg_r.get(m, 0)):
            for a, n in sc(BUMP0): parts['bump'] += n / N_of(2 * a * spg, fat)
        for a, n in sc(BRAKE0): parts['brake'] += n / N_of(a * br.get(m, 0), fat)
        for co in (coL, coR):
            for a, n in sc(CORNER0): parts['corner'] += n / N_of(a * co.get(m, 0), fat)
        for a, n in sc(LAUNCH0): parts['drive'] += n / N_of(a * d2.get(m, 0), fat)
        for a, n in sc(REGEN0): parts['drive'] += n / N_of(a * d3.get(m, 0), fat)
        for a, n in sc(SHOCK0): parts['drive'] += n / N_of(a * d1.get(m, 0), fat)
        D = sum(parts.values())
        r1g = 2 * max(spg_f.get(m, 0), spg_r.get(m, 0))
        rows.append(dict(member=m, FAT=fat, detail=why, range_per_pm1g_MPa=round(r1g, 1), miner_D=float('%.3g' % D),
                         parts={k: float('%.3g' % v) for k, v in parts.items()}, verdict='pass' if D <= D_ALLOW else 'FAIL',
                         life_x_design=('inf' if D == 0 else round(D_ALLOW / D, 2))))
    rows.sort(key=lambda r: -r['miner_D'])
    return rows

if __name__ == '__main__':
    R = json.loads((OUT / sys.argv[1]).read_text())
    X = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    af = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rows = compute(R, X, af)
    res = dict(source=sys.argv[1], gamma_Mf=GAM, D_allow=D_ALLOW, spectrum_x=X, welded=rows)
    outp = OUT / ('fatigue-' + sys.argv[1].replace('results-', '').replace('.json', '') + ('-x%g' % X if X != 1 else '') + '.json')
    outp.write_text(json.dumps(res, indent=1))
    for r in rows[:16]: print('%-9s FAT%-3d range/1g %6.1f  D %.3g (%s) %s' % (r['member'], r['FAT'], r['range_per_pm1g_MPa'], r['miner_D'], r['parts'], r['verdict']))
