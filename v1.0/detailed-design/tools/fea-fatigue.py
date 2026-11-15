"""Fatigue of the welded joints, lugs and bolts from the fea-frame.py stress changes (Miner + Goodman).

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).

Method (nominal-stress approach, IIW-2259-15 "Recommendations for fatigue design of welded joints and components",
Hobbacher 2016; aluminium per the same document and EN 1999-1-3):
  - stress change per 1 g of extra wheel load at each member = (case - static) / g-increment, taken from the FEA
    (front bump C2 and rear bump C6 are +2 g increments; braking C3 is 1.1 g; cornering C5 steady part);
  - welded details: S-N curve Delta_sigma^3 N = FAT^3 * 2e6 down to the knee at 1e7, slope m2 = 22 below it
    (IIW variable-amplitude rule); no mean-stress correction (as-welded, residual stress at yield);
    partial factor gamma_Mf = 1.25 on stress (IIW 'fail-safe not assured, high consequence' band 1.15-1.40);
  - Miner damage summed over the spectrum blocks; pass if D <= 0.5 (IIW recommends D_allow 0.5 for variable amplitude);
  - non-welded steel lug blocks: modified Goodman with a Marin-corrected endurance limit and Kf 2.5 at bolt holes;
  - bolts: VDI 2230 endurance (sigma_ASV = 0.85 (150/d + 45), rolled before heat treatment) and slip check.
usage: python fea-fatigue.py results-<tag>.json
"""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE.parents[1] / 'detailed-design' / 'structures'
R = json.loads((OUT / sys.argv[1]).read_text())
GAM = 1.25; D_ALLOW = 0.5

# road-load spectrum over the design life (160,000 km = 100,000 mi, 25 % unpaved), per axle.
# Amplitude a in g of extra wheel load (stress range = 2 a sigma_per_g); counts are cycles over life.
# Log-linear ('straight-line') vertical spectrum shape as used for road-vehicle durability (Heuler & Klaetschke 2005,
# Int. J. Fatigue 27:974): 2.4e7 cycles over life, 2 g extra wheel load exceeded 10 times. SPECTRUM_X scales counts.
SPECTRUM_X = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
BUMP = [(a, n * SPECTRUM_X) for a, n in [(0.10, 2.0e7), (0.20, 3.0e6), (0.35, 3.0e5), (0.50, 5.0e4), (0.75, 5.0e3), (1.00, 1.0e3), (1.50, 1.0e2), (2.00, 1.0e1)]]
BRAKE = [(a, n * SPECTRUM_X) for a, n in [(0.3, 2.0e5), (0.6, 1.0e4), (0.9, 1.0e3), (1.1, 1.0e2)]]   # stops: range = a/1.1 * C3 change
CORNER = [(1.0, 1.0e5)]                                          # 45 deg steady corners: range = 0.414/1.12 * C5 change

# detail classes (FAT = stress range at 2e6 cycles, MPa)
def fat_of(member):
    m = member
    if m.startswith('SA') and m[2] in 'LR': return 22, 'Al 6061 box arm, welded pivot boss/axle plate (IIW Al transverse attachment)'
    if m in ('SAX', 'STW') and R['V'].get('tower_mat') == 'A356': return 40, 'A356-T6 cast tower/brace node, bolted, no weld (cast Al, conservative FAT 40)'
    if m in ('SAX', 'STW'): return 18, 'Al cross brace / shock tower fillet-welded to arm (IIW Al load-carrying fillet)'
    if m.startswith('PACK'): return 28, 'Al 6082 case: FSW/fusion seam or bolt-hole net section (IIW Al butt weld ground flush ~FAT 32; 28 used)'
    if m == 'STB' and R['V'].get('forged_shock_bridge'): return 56, 'forged steel bridge with integral clevis, machined bore (no weld; FAT 56 conservative for Kt~2)'
    if (m.startswith(('UR2', 'DL', 'GUS')) or m == 'HT') and R['V'].get('cast_headstock'): return 63, 'cast steel headstock, tube on 60 mm spigot, full-penetration circumferential butt weld on backing (IIW FAT 63-71; 63 used, stress taken at the node, conservative)'
    if m == 'STB': return 36, 'steel 8 mm plate, load-carrying fillet to cross tube (IIW cruciform, FAT 36)'
    if m.startswith('LUG'): return 45, 'steel lug block welded to tube end (IIW tube-to-plate fillet, FAT 45)'
    return 45, 'steel 4130 thin-wall tube, TIG fillet/fusion at a cluster or plate (IIW hollow-section joints FAT 40-50; 45 used)'

def N_of(dsig, fat):
    d = GAM * dsig
    if d <= 0: return math.inf
    knee = fat * (2e6 / 1e7) ** (1 / 3)
    return 2e6 * (fat / d) ** 3 if d >= knee else 1e7 * (knee / d) ** 22

dl = R['delta_vs_C1']
spg_f = {k: v[0] / 2.0 for k, v in dl['C2_front_bump_3g']['members'].items()}
spg_r = {k: v[0] / 2.0 for k, v in dl['C6_rear_bump_3g']['members'].items()}
br = {k: v[0] / 1.1 for k, v in dl['C3_braking_1.1g']['members'].items()}
co = {k: v[0] * 0.414 / 1.12 for k, v in dl['C5_corner_45deg_x1.5']['members'].items()}
# pack: hot spot just outside the lug patch
for src, dst, f in [('C2_front_bump_3g', spg_f, 0.5), ('C6_rear_bump_3g', spg_r, 0.5), ('C3_braking_1.1g', br, 1 / 1.1), ('C5_corner_45deg_x1.5', co, 0.414 / 1.12)]:
    for k, v in dl[src]['pack_lug_edge'].items():
        if k.startswith('PACK'): dst[k + '@lug'] = v[0] * f

rows = []
for m in sorted(set(spg_f) | set(spg_r)):
    fat, why = fat_of(m)
    D = 0.0
    for spg in (spg_f.get(m, 0), spg_r.get(m, 0)):
        for a, n in BUMP: D += n / N_of(2 * a * spg, fat)
    for a, n in BRAKE: D += n / N_of(a * br.get(m, 0), fat)
    for a, n in CORNER: D += n / N_of(a * co.get(m, 0), fat)
    knee = fat * (2e6 / 1e7) ** (1 / 3) / GAM
    r1g = 2 * max(spg_f.get(m, 0), spg_r.get(m, 0))
    rows.append(dict(member=m, FAT=fat, detail=why, range_per_pm1g_MPa=round(r1g, 1), knee_allow_MPa=round(knee, 1),
                     miner_D=float('%.3g' % D), verdict='pass' if D <= D_ALLOW else 'FAIL',
                     life_x_design=('inf' if D == 0 else round(D_ALLOW / D, 2))))
rows.sort(key=lambda r: -r['miner_D'])

# ---- steel lug blocks (unwelded side, bolt holes): modified Goodman at the +-1 g level that recurs 5e4 times
Su, Sy = 670.0, 435.0; Se = 0.5 * Su * 0.78 * 0.9 / 2.5
good = []
st1 = R['cases']['C1_static_1g_two_up']['stress']
for m in [k for k in st1 if k.startswith('LUG')]:
    sm = abs(st1[m][1]); sa = max(spg_f.get(m, 0), spg_r.get(m, 0)) * 1.0
    n = 1 / (sa / Se + sm / Su) if (sa or sm) else math.inf
    good.append(dict(member=m, mean_MPa=round(sm, 1), amp_MPa_at_1g=round(sa, 1), Se_notched_MPa=round(Se, 1), goodman_SF=round(n, 2)))

# ---- bolts: 4 x M10 10.9 per lug, pattern 60 x 50
FM = 38000.0; As = 58.0; mu = 0.15; phi = 0.15; sASV = 0.85 * (150 / 10 + 45)
bolts = []
c1 = R['cases']['C1_static_1g_two_up']['lugs']
for case in ('C2_front_bump_3g', 'C3_braking_1.1g', 'C4_braking_plus_bump', 'C6_rear_bump_3g', 'C5_corner_45deg_x1.5',
             'C7a_pack_20g_longitudinal', 'C7b_pack_8g_lateral', 'C7c_pack_5g_vertical',
             'C9a_guard_21kN_upper_rail_node', 'C9b_guard_21kN_front_lug', 'C9c_guard_21kN_rear_link_lug'):
    if case not in R['cases']: continue
    for k, L in R['cases'][case]['lugs'].items():
        Ft = abs(L['axial_N']) / 4 + L['M_bend_Nmm'] / (2 * 50.0); Vb = L['shear_N'] / 4
        slip_sf = mu * (FM - (1 - phi) * Ft) / Vb if Vb > 0 else math.inf
        tau = math.hypot(Vb, 0) / As; sig = (FM + phi * Ft) / As
        bolts.append(dict(case=case, lug=k, tension_per_bolt_N=round(Ft), shear_per_bolt_N=round(Vb), slip_SF=round(slip_sf, 2),
                          bolt_vm_if_slipped_MPa=round(math.sqrt(sig ** 2 + 3 * tau ** 2)), bolt_proof_MPa=830,
                          bolt_shear_capacity_SF=round(0.6 * 1000 * As / Vb, 1) if Vb else 'inf'))
fat_b = []
for k in c1:
    a2 = R['cases']['C2_front_bump_3g']['lugs'][k]; a6 = R['cases']['C6_rear_bump_3g']['lugs'][k]
    def ft(L): return abs(L['axial_N']) / 4 + L['M_bend_Nmm'] / 100.0
    dF = max(abs(ft(a2) - ft(c1[k])), abs(ft(a6) - ft(c1[k]))) / 2   # per 1 g
    sa = phi * dF * 2.0 / (2 * As)                                    # +-2 g (500 cycles) amplitude
    fat_b.append(dict(lug=k, bolt_stress_amp_at_pm2g_MPa=round(sa, 2), sigma_ASV_MPa=round(sASV, 1), SF=round(sASV / sa, 1) if sa else 'inf'))

res = dict(source=sys.argv[1], gamma_Mf=GAM, D_allow=D_ALLOW, spectrum=dict(bump_per_axle=BUMP, braking=BRAKE, cornering=CORNER),
           welded=rows, goodman_lugs=good, bolts_static=bolts, bolts_fatigue=fat_b)
outp = OUT / ('fatigue-' + sys.argv[1].replace('results-', '').replace('.json', '') + ('-x%g' % SPECTRUM_X if SPECTRUM_X != 1 else '') + '.json')
outp.write_text(json.dumps(res, indent=1))
for r in rows[:14]: print('%-10s FAT%-3d range/1g %6.1f  knee/g %5.1f  D %.3g  %s' % (r['member'], r['FAT'], r['range_per_pm1g_MPa'], r['knee_allow_MPa'], r['miner_D'], r['verdict']))
print(good); print(fat_b)
print(sorted(bolts, key=lambda b: b['slip_SF'])[:4])
