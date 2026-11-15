"""Hand-calculation checks of the CalculiX setup used by fea-frame.py.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).

Check 1 - beam bending of a tube: 400 mm cantilever of the 32 x 2.5 4130 frame tube, 1 kN tip load.
  Hand: sigma = F L / Z, deflection = F L^3 / (3 E I) (+ Timoshenko shear term).
  FEA (a): B32R PIPE beam, the element family used for every frame tube.
  FEA (b): S4 shell cylinder (mid-surface radius 14.75, t 2.5), tip load through a rigid end ring; stress read
           150-250 mm from the root (away from the clamp), so it is an independent element type.
Check 2 - bolt shear: a steel lug plate bolted to a 4 mm-thick aluminium pad with 4 x M10, loaded by 13.1 kN in shear
  (half the pack's 20 g longitudinal inertia, the front-lug share). Hand: tau = V/(n A_s), bearing = V/(n d t).
  FEA: the plate as S4 shells with four rigid bolt rings tied to a fixed base by stiff beams (the bolts, B32R CIRC r5);
  bolt shear force read from the bolt beams' expanded-brick shear stress.
Writes detailed-design/structures/handcheck.json.
"""
import math, json, os, subprocess
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
OUT = ROOT / 'detailed-design' / 'structures'; RUN = OUT / 'run'; RUN.mkdir(parents=True, exist_ok=True)
CCX = ROOT.parent / '.tools' / 'FreeCAD_1.1.4-Windows-x86_64-py311' / 'bin' / 'ccx.exe'
E, NU = 205000.0, 0.29

def run(stem, text):
    (RUN / (stem + '.inp')).write_text(text)
    p = subprocess.run([str(CCX), stem], cwd=RUN, env=dict(os.environ, OMP_NUM_THREADS='4'), capture_output=True, text=True)
    assert 'Job finished' in p.stdout, p.stdout[-2000:]

def frd_stress(path):
    coords, S, U = {}, {}, {}; mode = None
    for t in open(path):
        if t.startswith('    2C'): mode = 'C'; continue
        if t.startswith(' -4  DISP'): mode = 'U'; continue
        if t.startswith(' -4  STRESS'): mode = 'S'; continue
        if t.startswith(' -3'): mode = None; continue
        if t.startswith(' -1') and mode:
            n = int(t[3:13]); v = [float(t[13 + 12 * k:25 + 12 * k]) for k in range((len(t.rstrip()) - 13) // 12)]
            {'C': coords, 'U': U, 'S': S}[mode][n] = np.array(v)
    return coords, U, S

out = {}
# ---------------------------------------------------------------- check 1a: beam
ro, t, L, F = 16.0, 2.5, 400.0, 1000.0
ri = ro - t; I = math.pi / 64 * ((2 * ro) ** 4 - (2 * ri) ** 4); Z = I / ro; A = math.pi * (ro ** 2 - ri ** 2)
G = E / (2 * (1 + NU)); k_s = 0.5   # thin tube shear coefficient
sig_hand = F * L / Z; d_hand = F * L ** 3 / (3 * E * I); d_hand_t = d_hand + F * L / (k_s * G * A)
n = 16
L1 = ['*NODE'] + ['%d,%g,0,0' % (i + 1, L * i / (2 * n)) for i in range(2 * n + 1)]
L1 += ['*ELEMENT,TYPE=B32R,ELSET=EB'] + ['%d,%d,%d,%d' % (k + 1, 2 * k + 1, 2 * k + 2, 2 * k + 3) for k in range(n)]
L1 += ['*MATERIAL,NAME=ST', '*ELASTIC', '%g,%g' % (E, NU), '*BEAM SECTION,ELSET=EB,MATERIAL=ST,SECTION=PIPE', '%g,%g' % (ro, t), '0,0,1',
       '*NSET,NSET=TIP', '%d' % (2 * n + 1), '*BOUNDARY', '1,1,6', '*STEP', '*STATIC', '*CLOAD', '%d,3,%g' % (2 * n + 1, -F),
       '*NODE PRINT,NSET=TIP', 'U', '*EL FILE', 'S', '*END STEP']
run('hc-beam', '\n'.join(L1) + '\n')
d_fea = float([l for l in open(RUN / 'hc-beam.dat') if l.strip().startswith(str(2 * n + 1))][0].split()[3])
coords, U, S = frd_stress(RUN / 'hc-beam.frd')
# axial stress (SXX) at the section 100 mm from the root, where M = F*300
sec = [n_ for n_, c in coords.items() if abs(c[0] - 100.0) < 1e-6]
sig_fea_100 = max(abs(S[n_][0]) for n_ in sec); sig_hand_100 = F * 300 / Z
out['beam_B32R'] = dict(sigma_root_hand=round(sig_hand, 1), sigma_at_100mm_hand=round(sig_hand_100, 1), sigma_at_100mm_fea=round(sig_fea_100, 1),
                        tip_defl_hand_bending=round(d_hand, 3), tip_defl_hand_with_shear=round(d_hand_t, 3), tip_defl_fea=round(abs(d_fea), 3))
# ---------------------------------------------------------------- check 1b: shell tube
rm = ro - t / 2; nc, nl = 32, 80
nodes = []; nid = lambda i, j: 1 + i * nc + (j % nc)
L2 = ['*NODE']
for i in range(nl + 1):
    for j in range(nc):
        a = 2 * math.pi * j / nc; L2.append('%d,%g,%g,%g' % (nid(i, j), L * i / nl, rm * math.cos(a), rm * math.sin(a)))
tipc = nid(nl, 0) + nc + 10; rot = tipc + 1
L2 += ['%d,%g,0,0' % (tipc, L), '%d,%g,0,0' % (rot, L)]
L2 += ['*ELEMENT,TYPE=S4,ELSET=SH'] + ['%d,%d,%d,%d,%d' % (i * nc + j + 1, nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)) for i in range(nl) for j in range(nc)]
L2 += ['*NSET,NSET=ROOT'] + ['%d' % nid(0, j) for j in range(nc)] + ['*NSET,NSET=RING'] + ['%d' % nid(nl, j) for j in range(nc)]
L2 += ['*MATERIAL,NAME=ST', '*ELASTIC', '%g,%g' % (E, NU), '*SHELL SECTION,ELSET=SH,MATERIAL=ST', '%g' % t,
       '*RIGID BODY,NSET=RING,REF NODE=%d,ROT NODE=%d' % (tipc, rot), '*NSET,NSET=TIP', '%d' % tipc,
       '*BOUNDARY', 'ROOT,1,6', '*STEP', '*STATIC', '*CLOAD', '%d,3,%g' % (tipc, -F), '*NODE PRINT,NSET=TIP', 'U', '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP']
run('hc-shell', '\n'.join(L2) + '\n')
d_sh = float([l for l in open(RUN / 'hc-shell.dat') if l.strip().startswith(str(tipc))][0].split()[3])
coords, U, S = frd_stress(RUN / 'hc-shell.frd')
vals = [abs(S[k][0]) for k, c in coords.items() if abs(c[0] - 100.0) < 2.6 and k in S]
out['shell_S4'] = dict(sigma_at_100mm_hand_outer_fibre=round(sig_hand_100, 1), sigma_at_100mm_fea_max=round(max(vals), 1),
                       tip_defl_fea=round(abs(d_sh), 3), note='S4 expands to C3D8I through the 2.5 mm wall; stress at the outer fibre')
# ---------------------------------------------------------------- check 2: bolt shear in a 4-bolt lug
V, nb, d = 13100.0, 4, 10.0
As = 58.0; A_sh = math.pi * d ** 2 / 4
tau_thread = V / (nb * As); tau_shank = V / (nb * A_sh)
bear = V / (nb * d * 4.0)          # bearing on a 4 mm aluminium wall (no pad) - why the pad is needed
bear_pad = V / (nb * d * 10.0)
# FEA: 100 x 80 x 10 steel plate (S4), bolts at +-30 x +-25, each bolt a 20 mm stiff ring tied to a 25 mm long
# M10 beam fixed at its far end; shear load at the plate centre through a rigid patch.
nx, ny, W, H = 40, 32, 100.0, 80.0
pid = lambda i, j: 1 + i * (ny + 1) + j
L3 = ['*NODE'] + ['%d,%g,%g,0' % (pid(i, j), -W / 2 + W * i / nx, -H / 2 + H * j / ny) for i in range(nx + 1) for j in range(ny + 1)]
L3 += ['*ELEMENT,TYPE=S4,ELSET=PL'] + ['%d,%d,%d,%d,%d' % (i * ny + j + 1, pid(i, j), pid(i + 1, j), pid(i + 1, j + 1), pid(i, j + 1)) for i in range(nx) for j in range(ny)]
base = (nx + 1) * (ny + 1) + 100; extra = []; bolts = []
P = {pid(i, j): (-W / 2 + W * i / nx, -H / 2 + H * j / ny) for i in range(nx + 1) for j in range(ny + 1)}
for k, (bx, by) in enumerate([(-30, -25), (30, -25), (-30, 25), (30, 25)]):
    ring = [n_ for n_, (x, y) in P.items() if math.hypot(x - bx, y - by) <= 10.0]
    c, mid, end, rr = base + 10 * k, base + 10 * k + 1, base + 10 * k + 2, base + 10 * k + 3
    L3 += ['*NODE', '%d,%g,%g,0' % (c, bx, by), '%d,%g,%g,-12.5' % (mid, bx, by), '%d,%g,%g,-25' % (end, bx, by), '%d,%g,%g,0' % (rr, bx, by)]
    L3 += ['*ELEMENT,TYPE=B32R,ELSET=BOLT%d' % k, '%d,%d,%d,%d' % (5000 + k, c, mid, end)]
    extra += ['*NSET,NSET=R%d' % k] + ['%d' % n_ for n_ in ring] + ['*RIGID BODY,NSET=R%d,REF NODE=%d,ROT NODE=%d' % (k, c, rr)]
    bolts.append((5000 + k, end))
cen = [n_ for n_, (x, y) in P.items() if math.hypot(x, y) <= 12.0]
L3 += ['*NODE', '%d,0,0,0' % (base + 90), '%d,0,0,0' % (base + 91)]
extra += ['*NSET,NSET=CEN'] + ['%d' % n_ for n_ in cen] + ['*RIGID BODY,NSET=CEN,REF NODE=%d,ROT NODE=%d' % (base + 90, base + 91)]
L3 += ['*MATERIAL,NAME=ST', '*ELASTIC', '%g,%g' % (E, NU), '*SHELL SECTION,ELSET=PL,MATERIAL=ST', '10']
for k in range(4): L3 += ['*BEAM SECTION,ELSET=BOLT%d,MATERIAL=ST,SECTION=CIRC' % k, '5', '1,0,0']
L3 += extra + ['*NSET,NSET=ENDS'] + ['%d' % e for _, e in bolts]
L3 += ['*BOUNDARY', 'ENDS,1,6', '*STEP', '*STATIC', '*CLOAD', '%d,1,%g' % (base + 90, V), '*NODE PRINT,NSET=ENDS', 'RF', '*END STEP',
       '*STEP', '*STATIC', '*CLOAD,OP=NEW', '%d,1,%g' % (base + 90, V), '%d,3,%g' % (base + 91, V * 20.0), '*NODE PRINT,NSET=ENDS', 'RF', '*END STEP']
run('hc-bolts', '\n'.join(L3) + '\n')
rf = []; st = -1
for l in open(RUN / 'hc-bolts.dat'):
    if 'forces' in l: st += 1; rf.append([]); continue
    p = l.split()
    if st >= 0 and len(p) == 4: rf[st].append([float(v) for v in p[1:]])
fea_per_bolt = np.abs(np.array(rf[0])[:, 0])
ecc = np.linalg.norm(np.array(rf[1])[:, :2], axis=1)
# hand, elastic method: direct V/n plus torsion T r / sum r^2 perpendicular to the radius
Tq = V * 20.0; hand_ecc = []
for bx, by in [(-30, -25), (30, -25), (-30, 25), (30, 25)]:
    r2 = 4 * (30 ** 2 + 25 ** 2); fx = V / 4 - Tq * by / r2; fy = Tq * bx / r2; hand_ecc.append(math.hypot(fx, fy))
out['bolt_shear'] = dict(V_N=V, n_bolts=nb, hand_per_bolt_N=V / nb, fea_per_bolt_N=fea_per_bolt.round(1).tolist(),
                         fea_sum_N=round(float(fea_per_bolt.sum()), 1), tau_thread_hand_MPa=round(tau_thread, 1), tau_shank_hand_MPa=round(tau_shank, 1),
                         tau_fea_max_MPa=round(float(fea_per_bolt.max()) / As, 1), shear_strength_10_9_thread_MPa=0.6 * 1000,
                         eccentric_20mm_hand_per_bolt_N=[round(v, 1) for v in hand_ecc], eccentric_20mm_fea_per_bolt_N=ecc.round(1).tolist(),
                         bearing_on_4mm_wall_MPa=round(bear, 1), bearing_on_10mm_pad_MPa=round(bear_pad, 1))
(OUT / 'handcheck.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
