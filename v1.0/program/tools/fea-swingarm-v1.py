"""Single-sided swingarm shell model (CalculiX S4 shells, structured mesh) for the Bavuso V1: strength, fatigue, stiffness.

November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Model (model coordinates of tools/build-adventure.py, X forward, Y left, Z up, mm; ground at Z = -53.1):
  - hollow tapered box arm from the pivot (540, ya, 350) to the rear axle (0, ya, 271.9): outer W (Y) x H, wall t, mid-surface S4 shells,
    box from 30 mm behind the pivot to 30 mm before the axle, closed by 8 mm diaphragm plates that are ONE rigid body each with the
    pivot / axle boss (cast boss assumed rigid: the boss, bearing seats and axle bore are NOT resolved);
  - pivot = two bearing stations (Y_in, Y_out) carried by a rigid body referenced at the outer station: ref node fixed in X,Y,Z and the
    rotation node fixed about X and Z, free about Y (the shock closes the rotation). Bearing forces come from the constraint reactions;
  - A356 cross brace (beam) bolted to the inner wall at X380 through a rigid 35 mm patch, twin tower webs (beams) to the shock lower eye;
  - loads from the wheel free body: contact force, belt tight/slack spans (or the 11.3 kN shaft pull), wheel weight, rear brake; the
    shock force is solved from moment equilibrium about the pivot axis so that the arm is balanced by the bearings.
Cases mirror fea-frame-v1.py (static, rear bump 3 g, cornering both ways, belt design pull, launch, regen) plus a rear-brake case.
Stiffness: pivot rotation about Y locked, 1 kN lateral at the axle, 1 kNm torque about the arm axis and 1 kNm yaw about Z.
usage: python fea-swingarm-v1.py --variant <name> [--h 8] [--tag x]  (reads program/data/fea/<name>-sections.json and results-*.json of the frame run)
"""
import math, json, os, sys, argparse, subprocess, time
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; OUT = ROOT / 'program' / 'data' / 'fea'; RUN = OUT / 'run'
CCX = ROOT.parent / '.tools' / 'FreeCAD_1.1.4-Windows-x86_64-py311' / 'bin' / 'ccx.exe'
ap = argparse.ArgumentParser()
ap.add_argument('--variant', required=True); ap.add_argument('--h', type=float, default=8.0); ap.add_argument('--tag', default='')
ap.add_argument('--results', default='', help='frame results json (wheel loads); default results-<variant>-h12.json or any results-<variant>*')
ap.add_argument('--set', default='')
ap.add_argument('--patch_r', type=float, default=40.0, help='radius of the rigid patch where the brace is bolted to the inner wall (mm)')
ap.add_argument('--excl', type=float, default=0.0, help='exclusion radius around the brace attach for the stress read-out (0 = patch_r + 5)')
ap.add_argument('--rib', type=float, default=0.0, help='internal rib plate thickness at the brace station (0 = none)')
ap.add_argument('--dbl', type=float, default=1.0, help='wall thickness multiple over +-2 stations around the brace (1 = none)')
args = ap.parse_args()
RUN.mkdir(parents=True, exist_ok=True)
V = json.loads((OUT / (args.variant + '-sections.json')).read_text())
if args.set: V.update(json.loads(args.set))
ya = V['arm_y']; Wp, Hp, tw = V['arm_pivot']; Wa, Ha, _ = V['arm_axle']; Yin, Yout = V['piv_in'], V['piv_out']
brace_ro, brace_t = V['brace']; tow_t, tow_d = V['tower']
T_CAP = 8.0; E_AL = 70000.0; NU = 0.33
ARM_MAT = V.get('arm_mat', 'AL6061'); FY = dict(AL6061=240.0, A356=200.0)[ARM_MAT]; ARM_FAT = V.get('arm_fat', 22)
G = 9.81
# ---------------- geometry constants (same as fea-frame-v1.py)
LIFT = 53.1; RF, RR = 331.5, 325.0; PZ = 350.0; RZ = RR - LIFT; GROUND = -LIFT
RAKE = math.radians(25); FORK_OFF = 36.1; SA0 = np.array([1206.954, 0, 800.0]); FZ = RF - LIFT
W_AXLE = (FZ - SA0[2] - math.sin(RAKE) * FORK_OFF) / math.cos(RAKE); FX = SA0[0] + math.cos(RAKE) * FORK_OFF - math.sin(RAKE) * W_AXLE
P0 = np.array([540.0, ya, PZ]); A0 = np.array([0.0, ya, RZ]); L = np.linalg.norm(A0 - P0)
u = (A0 - P0) / L; an = np.array([-u[2], 0, u[0]]); an = an if an[2] > 0 else -an; ey = np.array([0, 1.0, 0])
S0, S1 = 30.0, L - 30.0
Rr = glob = None
# ---------------- frame-model wheel loads
cand = sorted(OUT.glob('results-%s*.json' % args.variant)) if not args.results else [OUT / args.results]
cand = [c for c in cand if 'sizing' not in c.name and 'nopack' not in c.name] or cand
FR = json.loads(cand[0].read_text()); Ff, Fr = FR['static_wheel_N']; hcg = FR['hcg_mm']; Mtot = (Ff + Fr) / G
WHEEL_KG = 14.1
d_r = 80 * math.sin(math.radians(45)); nz = 1.5 / math.cos(math.radians(45)); R_RP = 160.4; R_TY = RZ - GROUND
Cr, Cm = np.array([0, RZ]), np.array([540, PZ]); Dv = Cm - Cr; Lc = np.linalg.norm(Dv); gam = math.atan2(Dv[1], Dv[0]); cands = []
for sg in (1, -1):
    be = gam + sg * math.acos((160.4 - 44.6) / Lc); n_ = np.array([math.cos(be), math.sin(be)])
    Pr, Pm = Cr + 160.4 * n_, Cm + 44.6 * n_; d_ = (Pm - Pr) / np.linalg.norm(Pm - Pr); cands.append((n_[1], Pr, d_))
cands.sort(key=lambda c: -c[0]); TOP, BOT = cands[0], cands[1]
def spans(T1, T2, reverse=False):
    tt, ts_ = (BOT, TOP) if reverse else (TOP, BOT); L_ = []
    for c, T in ((tt, T1), (ts_, T2)): L_.append((np.array([c[1][0], -144.0, c[1][1]]), T * 1000 * np.array([c[2][0], 0, c[2][1]])))
    return L_
def pull(T1, T2):
    P = (T1 * np.array([TOP[2][0], 0, TOP[2][1]]) + T2 * np.array([BOT[2][0], 0, BOT[2][1]])) * 1000
    return [(np.array([0, -144.0, RZ]), P)]
PRE = spans(3.05, 3.05)
# case = (contact point, contact force, belt forces list, wheel-weight multiple)
def thrust(T1, T2, rev=False):
    Ft = (T1 - T2) * 1000 * R_RP / R_TY * (-1 if rev else 1); a_x = Ft / Mtot; dF = Mtot * a_x * hcg / FX
    return Ft, Fr + dF
Ft2, Fz2 = thrust(6.2, 1.3); Ft3, Fz3 = thrust(6.2, 1.3, True)
CASES = {
    'A1_static':        (np.array([0, 0, GROUND]), np.array([0, 0, Fr]), PRE, 1.0),
    'A5L_corner_left':  (np.array([0, -d_r, GROUND]), np.array([0, nz * Fr * d_r / hcg, nz * Fr]), PRE, nz),
    'A5R_corner_right': (np.array([0, d_r, GROUND]), np.array([0, -nz * Fr * d_r / hcg, nz * Fr]), PRE, nz),
    'A6_rear_bump_3g':  (np.array([0, 0, GROUND]), np.array([0, 0, 3 * Fr]), PRE, 3.0),
    'AD1_belt_design':  (np.array([0, 0, GROUND]), np.array([0, 0, Fr]), pull(9.4, 2.0), 1.0),
    'AD2_launch_peak':  (np.array([0, 0, GROUND]), np.array([Ft2, 0, Fz2]), spans(6.2, 1.3), 1.0),
    'AD3_regen_peak':   (np.array([0, 0, GROUND]), np.array([Ft3, 0, Fz3]), spans(6.2, 1.3, True), 1.0),
    'AR1_rear_brake':   (np.array([0, 0, GROUND]), np.array([-1500.0, 0, Fr]), PRE, 1.0),
}
def moment(r, F, about): return np.cross(r - about, F)
def axle_interface(case):
    """Force and moment the arm receives at the axle point A (wheel free body: contact + belt + weight; the hub passes no torque about Y)."""
    pt, Fc, belt, wm = CASES[case]
    forces = [(pt, Fc)] + belt + [(np.array([0, 0, RZ]), np.array([0, 0, -WHEEL_KG * G * wm]))]
    F = sum(f for _, f in forces); M = sum(moment(r, f, A0) for r, f in forces)
    if case == 'AR1_rear_brake': M = M.copy()   # brake torque reaction through the caliper bracket is added by the net moment of the rear contact force
    M[1] = 0.0 if case != 'AR1_rear_brake' else M[1]
    return F, M
def shock_geometry():
    uu = -u[:3]   # from axle toward pivot
    lo = np.array([540, PZ]) + 210 * np.array([u[0], u[2]]) + 120 * np.array([an[0], an[2]]); eye = np.array([lo[0], 0, lo[1]])
    top = np.array([V['geom']['shock_x'], 0, V['geom']['eye_z']]); es = (eye - top) / np.linalg.norm(eye - top)   # force on the arm at the lower eye, compression pushes toward the eye
    return eye, es
EYE, ES = shock_geometry()
lev = lambda: (EYE - P0)[2] * ES[0] - (EYE - P0)[0] * ES[2]
def shock_force(F, M):
    My = moment(A0, F, P0)[1] + M[1]   # moment about Y through the pivot from the axle loads
    return -My / lev()
# ---------------- mesh
h = args.h; nW = max(3, math.ceil(max(Wp, Wa) / h)); nH = max(4, math.ceil(max(Hp, Ha) / h)); nS = max(8, math.ceil((S1 - S0) / h))
nodes = {}; elems = []
def nid(p): i = len(nodes) + 1; nodes[i] = np.asarray(p, float); return i
def secdims(s):
    f = (s - S0) / (S1 - S0); return Wp + (Wa - Wp) * f, Hp + (Hp * 0 + Ha - Hp) * f
def ptat(s, i, j):
    W, H = secdims(s); hW, hH = (W - tw) / 2, (H - tw) / 2
    return P0 + u * s + ey * (hW * (2 * i / nW - 1)) + an * (hH * (2 * j / nH - 1))
ring_ij = [(i, nH) for i in range(nW + 1)] + [(nW, j) for j in range(nH - 1, -1, -1)] + [(i, 0) for i in range(nW - 1, -1, -1)] + [(0, j) for j in range(1, nH)]
sgrid = [S0 + (S1 - S0) * k / nS for k in range(nS + 1)]
ID = {}   # (k,i,j) -> node
for k, s_ in enumerate(sgrid):
    for (i, j) in ring_ij: ID[(k, i, j)] = nid(ptat(s_, i, j))
for k in range(nS):
    for a in range(len(ring_ij)):
        i1, j1 = ring_ij[a]; i2, j2 = ring_ij[(a + 1) % len(ring_ij)]
        elems.append(('BOX%d' % k, [ID[(k, i1, j1)], ID[(k, i2, j2)], ID[(k + 1, i2, j2)], ID[(k + 1, i1, j1)]]))
capnodes = {}
for k in (0, nS):
    for i in range(1, nW):
        for j in range(1, nH): ID[(k, i, j)] = nid(ptat(sgrid[k], i, j))
    capnodes[k] = [n for (kk, i, j), n in ID.items() if kk == k]
    for i in range(nW):
        for j in range(nH): elems.append(('CAP', [ID[(k, i, j)], ID[(k, i + 1, j)], ID[(k, i + 1, j + 1)], ID[(k, i, j + 1)]]))
# rigid references
pref = nid(np.array([540.0, Yout, PZ])); prot = nid(np.array([540.0, Yout, PZ]) + [0, 0, 0]); aref = nid(A0); arot = nid(A0)
# brace attach patch on the inner (i = 0) wall near X380
sb = (540 - 380) / L * L * 0 + (P0[0] - 380) / (-u[0]) if False else (540 - 380) / abs(u[0])
kc = int(np.argmin([abs(s_ - sb) for s_ in sgrid])); wmid = secdims(sgrid[kc]); hW_ = (wmid[0] - tw) / 2
attach = ptat(sgrid[kc], 0, nH // 2); aid = nid(attach + 0 * ey)
patch = [n for (k, i, j), n in ID.items() if i == 0 and abs(k - kc) <= 1 + int(args.patch_r // max(h, 1)) and np.linalg.norm(nodes[n] - attach) <= args.patch_r]
# brace and tower beams (A356) in the global frame
beams = []      # (elset, [n1,n2,n3], section)
def beam_chain(es, pts, first_id=None):
    ids = [first_id if first_id is not None else nid(pts[0])]
    for a, b in zip(pts[:-1], pts[1:]):
        m = nid((np.asarray(a) + np.asarray(b)) / 2); e = nid(b); beams.append((es, [ids[-1], m, e])); ids.append(e)
    return ids
az = lambda x: RZ + (PZ - RZ) * x / 540
bx = attach[0]; bz = attach[2]
br_ids = beam_chain('BRACE', [attach, np.array([bx, 26.0, bz]), np.array([bx, 0.0, bz]), np.array([bx, -26.0, bz]), np.array([bx, -36.0, bz])], first_id=aid)
yn = {26.0: br_ids[1], -26.0: br_ids[3]}
tw_ids = {}
for s_ in (-1, 1):
    top = nid(np.array([bx, 26.0 * s_, bz])) if False else br_ids[1 if s_ > 0 else 3]
    ids = beam_chain('TOWER%s' % ('R' if s_ > 0 else 'L'), [np.array([bx, 26.0 * s_, bz]), np.array([EYE[0], 26.0 * s_, EYE[2]])], first_id=top)
    tw_ids[s_] = ids[-1]
eye_id = nid(EYE)
for s_ in (-1, 1): beams.append(('BOLT', [tw_ids[s_], nid((nodes[tw_ids[s_]] + EYE) / 2), eye_id]))
# ---------------- writer
def write_inp(path, steps, extra=()):
    Ls = ['*HEADING', 'swingarm shell model', '*NODE'] + ['%d,%.4f,%.4f,%.4f' % (i, *p) for i, p in nodes.items()]
    for es in ('BOX', 'BOXD', 'CAP', 'RIB'):
        if not any(e[0] == es for e in elems): continue
        Ls.append('*ELEMENT,TYPE=S4,ELSET=%s' % es)
        Ls += ['%d,%s' % (i + 1, ','.join(map(str, e[1]))) for i, e in enumerate(elems) if e[0] == es]
    base = len(elems)
    for es in sorted(set(b[0] for b in beams)):
        Ls.append('*ELEMENT,TYPE=B32R,ELSET=%s' % es)
        for i, b in enumerate(beams):
            if b[0] == es: Ls.append('%d,%s' % (base + i + 1, ','.join(map(str, b[1]))))
    Ls += ['*MATERIAL,NAME=ARM', '*ELASTIC', '%g,%g' % (E_AL, NU), '*MATERIAL,NAME=A356', '*ELASTIC', '72000,0.33', '*MATERIAL,NAME=STL', '*ELASTIC', '205000,0.29']
    Ls += ['*SHELL SECTION,ELSET=BOX,MATERIAL=ARM', '%g' % tw, '*SHELL SECTION,ELSET=CAP,MATERIAL=ARM', '%g' % T_CAP]
    if any(e[0] == 'BOXD' for e in elems): Ls += ['*SHELL SECTION,ELSET=BOXD,MATERIAL=ARM', '%g' % (tw * args.dbl)]
    if any(e[0] == 'RIB' for e in elems): Ls += ['*SHELL SECTION,ELSET=RIB,MATERIAL=ARM', '%g' % args.rib]
    Ls += ['*BEAM SECTION,ELSET=BRACE,MATERIAL=A356,SECTION=PIPE', '%g,%g' % (brace_ro, brace_t), '0,0,1']
    for s_, nm in ((1, 'TOWERR'), (-1, 'TOWERL')): Ls += ['*BEAM SECTION,ELSET=%s,MATERIAL=A356,SECTION=RECT' % nm, '%g,%g' % (tow_t, tow_d), '0,1,0']
    Ls += ['*BEAM SECTION,ELSET=BOLT,MATERIAL=STL,SECTION=CIRC', '6', '0,0,1']
    Ls += ['*NSET,NSET=PCAP'] + ['%d' % n for n in capnodes[0]]
    Ls += ['*RIGID BODY,NSET=PCAP,REF NODE=%d,ROT NODE=%d' % (pref, prot)]
    Ls += ['*NSET,NSET=ACAP'] + ['%d' % n for n in capnodes[nS]]
    Ls += ['*RIGID BODY,NSET=ACAP,REF NODE=%d,ROT NODE=%d' % (aref, arot)]
    Ls += ['*NSET,NSET=BPATCH'] + ['%d' % n for n in patch]
    Ls += ['*RIGID BODY,NSET=BPATCH,REF NODE=%d,ROT NODE=%d' % (aid, nid_rot)]
    Ls += list(extra)
    for st in steps: Ls += st
    path.write_text('\n'.join(Ls) + '\n')
nid_rot = nid(attach)
nodes[nid_rot] = attach.copy()
elems = [(('BOXD' if (e[0].startswith('BOX') and abs(int(e[0][3:]) - kc) <= 2 and args.dbl > 1) else 'BOX') if e[0].startswith('BOX') else e[0], e[1]) for e in elems]
if args.rib > 0:
    for i in range(1, nW):
        for j in range(1, nH): ID[('rib', i, j)] = nid(ptat(sgrid[kc], i, j))
    gid = lambda i, j: ID[('rib', i, j)] if ('rib', i, j) in ID else ID[(kc, i, j)]
    for i in range(nW):
        for j in range(nH): elems.append(('RIB', [gid(i, j), gid(i + 1, j), gid(i + 1, j + 1), gid(i, j + 1)]))
def run_ccx(stem):
    env = dict(os.environ, OMP_NUM_THREADS=os.environ.get('FEA_THREADS', '2'), CCX_NPROC_EQUATION_SOLVER=os.environ.get('FEA_THREADS', '2')); t0 = time.time()
    p = subprocess.run([str(CCX), stem], cwd=RUN, env=env, capture_output=True, text=True); (RUN / (stem + '.log')).write_text(p.stdout + p.stderr)
    if 'Job finished' not in p.stdout: print(p.stdout[-3000:]); raise SystemExit('ccx failed')
    return time.time() - t0
def parse_frd(path):
    coords = {}; steps = []; lines = open(path).readlines(); i = 0
    while i < len(lines):
        s = lines[i]
        if s.startswith('    2C'):
            i += 1
            while not lines[i].startswith(' -3'):
                t = lines[i]; coords[int(t[3:13])] = np.array([float(t[13:25]), float(t[25:37]), float(t[37:49])]); i += 1
        elif s.startswith(' -4'):
            name = s.split()[1]; i += 1
            while lines[i].startswith(' -5'): i += 1
            data = {}
            while not lines[i].startswith(' -3'):
                t = lines[i]
                if t.startswith(' -1'): data[int(t[3:13])] = [float(t[13 + 12 * k:25 + 12 * k]) for k in range((len(t.rstrip()) - 13) // 12)]
                i += 1
            if name == 'DISP': steps.append({'U': data})
            elif name == 'STRESS': steps[-1]['S'] = data
        i += 1
    return coords, steps
def parse_dat(path):
    out = []; cur = None; kind = None
    for t in open(path):
        if 'S T E P' in t: cur = {'RF': {}}; out.append(cur); kind = None; continue
        tl = t.strip()
        if tl.startswith('forces'): kind = 'RF'; continue
        if tl.startswith(('displacements', 'stresses')): kind = None; continue
        if not tl or cur is None or kind is None: continue
        p = tl.split()
        try: cur['RF'][int(p[0])] = np.array([float(v) for v in p[1:4]])
        except ValueError: kind = None
    return out
def stress_arrays(S, ids):
    A = np.array([S[n] for n in ids]); T = np.zeros((len(A), 3, 3))
    T[:, 0, 0], T[:, 1, 1], T[:, 2, 2] = A[:, 0], A[:, 1], A[:, 2]; T[:, 0, 1] = T[:, 1, 0] = A[:, 3]; T[:, 1, 2] = T[:, 2, 1] = A[:, 4]; T[:, 0, 2] = T[:, 2, 0] = A[:, 5]
    tr = np.trace(T, axis1=1, axis2=2); D = T - tr[:, None, None] / 3 * np.eye(3); vm = np.sqrt(1.5 * np.sum(D * D, axis=(1, 2)))
    ev = np.linalg.eigvalsh(T); pm = np.where(np.abs(ev[:, 0]) > np.abs(ev[:, 2]), ev[:, 0], ev[:, 2])
    return vm, pm
# ---------------- run strength cases
tag = '%s-h%g%s' % (args.variant, h, ('-' + args.tag) if args.tag else '')
steps = []; info = {}
for name in CASES:
    F, M = axle_interface(name); Fs = shock_force(F, M); info[name] = dict(axle_F=F.round(0).tolist(), axle_M=M.round(0).tolist(), shock_N=round(Fs, 0))
    ld = ['*CLOAD,OP=NEW']
    for d in range(3):
        if abs(F[d]) > 1e-6: ld.append('%d,%d,%.6e' % (aref, d + 1, F[d]))
        if abs(M[d]) > 1e-6: ld.append('%d,%d,%.6e' % (arot, d + 1, M[d]))
        fe = Fs * ES[d]
        if abs(fe) > 1e-6: ld.append('%d,%d,%.6e' % (eye_id, d + 1, fe))
    steps.append(['*STEP', '*STATIC', '*BOUNDARY', '%d,1,3' % pref, '%d,1,1' % prot, '%d,3,3' % prot] + ld +
                 ['*NODE PRINT,NSET=PIVREF', 'RF', '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP'])
extra = ['*NSET,NSET=PIVREF', '%d' % pref, '%d' % prot]
stem = 'arm-' + tag; write_inp(RUN / (stem + '.inp'), steps, extra)
print('arm model: %d nodes, %d shell elems, %d beams, patch %d nodes, caps %d/%d' % (len(nodes), len(elems), len(beams), len(patch), len(capnodes[0]), len(capnodes[nS])))
tsol = run_ccx(stem)
coords, fsteps = parse_frd(RUN / (stem + '.frd')); dsteps = parse_dat(RUN / (stem + '.dat'))
# stress evaluation nodes: arm box nodes only (skip within 40 mm of the caps and the brace patch, rigid-boundary singularities)
sid = sorted(coords); X = np.array([coords[n] for n in sid]); sax = (X - P0) @ u
mask_arm = (sax > S0 + 40) & (sax < S1 - 40) & (np.linalg.norm(X - attach, axis=1) > (args.excl or args.patch_r + 5))
# expanded-shell nodes belong to arm box if inside the box envelope (beam nodes are separate): use distance in Y/an from centreline
rel = X - P0 - np.outer(sax, u); in_box = (np.abs(rel @ ey) < (max(Wp, Wa) / 2 + tw)) & (np.abs(rel @ an) < (max(Hp, Ha) / 2 + tw))
res = dict(variant=args.variant, h=h, V={k: V[k] for k in ('arm_pivot', 'arm_axle', 'arm_y', 'piv_in', 'piv_out', 'brace', 'tower', 'arm_mat', 'arm_fat')}, cases={}, ccx_s=round(tsol, 1), n_nodes=len(nodes), n_shell=len(elems))
S_all = {}
Dpiv = Yout - Yin
for (name, _), fs, ds in zip(CASES.items(), fsteps, dsteps):
    vm, pm = stress_arrays(fs['S'], sid); S_all[name] = (vm, pm)
    Fa, Ma = axle_interface(name); Fsh = info[name]['shock_N'] * ES; Rtot = -(Fa + Fsh); refp = np.array([540.0, Yout, PZ])
    Mtot = Ma + np.cross(A0 - refp, Fa) + np.cross(EYE - refp, Fsh); MR = -Mtot; Mrf = MR
    Fin = np.array([MR[2] / Dpiv, 0.0, -MR[0] / Dpiv]); Fout = Rtot - Fin
    res['cases'][name] = dict(axle_F_N=info[name]['axle_F'], axle_M_Nmm=info[name]['axle_M'], shock_N=info[name]['shock_N'],
                              arm_max_vm_MPa=round(float(vm[mask_arm & in_box].max()), 1), arm_max_vm_all_MPa=round(float(vm[in_box].max()), 1),
                              brace_tower_max_vm_MPa=round(float(vm[~in_box].max()), 1) if (~in_box).any() else None,
                              bearing_in_N=Fin.round(0).tolist(), bearing_out_N=Fout.round(0).tolist(), bearing_in_mag_N=round(float(np.linalg.norm(Fin)), 0), bearing_out_mag_N=round(float(np.linalg.norm(Fout)), 0),
                              yaw_residual_Nmm=round(float(Mrf[1]), 0))
    print(name, res['cases'][name]['arm_max_vm_MPa'], res['cases'][name]['brace_tower_max_vm_MPa'], 'shock', info[name]['shock_N'], 'brgs', res['cases'][name]['bearing_in_mag_N'], res['cases'][name]['bearing_out_mag_N'], 'My resid', res['cases'][name]['yaw_residual_Nmm'])
# strength: required SF on yield (1.5 static, 1.2 others)
res['sf'] = {n: round(FY / max(c['arm_max_vm_MPa'], 1e-6), 2) for n, c in res['cases'].items()}
res['sf_brace_tower'] = {n: round(200.0 / max(c['brace_tower_max_vm_MPa'] or 1e-6, 1e-6), 2) for n, c in res['cases'].items()}
# fatigue at every arm node (signed principal change vs static), spectrum of fea-fatigue-v1.py
import importlib.util
sp = importlib.util.spec_from_file_location('fat', str(HERE / 'fea-fatigue-v1.py')); FATm = importlib.util.module_from_spec(sp); sp.loader.exec_module(FATm)
dpm = lambda n: np.abs(S_all[n][1] - S_all['A1_static'][1])
def Nv(d, fat):
    d = FATm.GAM * d; knee = fat * (2e6 / 1e7) ** (1 / 3); out = np.full(d.shape, np.inf); m = d > 0
    hi = m & (d >= knee); lo = m & (d < knee); out[hi] = 2e6 * (fat / d[hi]) ** 3; out[lo] = 1e7 * (knee / d[lo]) ** 22; return out
def Dsum(fat, mask):
    spg_r = dpm('A6_rear_bump_3g') / 2.0; coL = dpm('A5L_corner_left') * 0.414 / 1.12; coR = dpm('A5R_corner_right') * 0.414 / 1.12
    d1, d2, d3 = dpm('AD1_belt_design'), dpm('AD2_launch_peak'), dpm('AD3_regen_peak'); br = dpm('AR1_rear_brake')
    D = np.zeros(len(sid)); parts = {}
    for a, n in FATm.BUMP0: D += n / Nv(2 * a * spg_r, fat)
    parts['bump'] = D.copy()
    for a, n in FATm.BRAKE0: D += n / Nv(a / 1.1 * 0.5 * br, fat)       # rear-brake share of the stops: half of the 1.5 kN lock case scaled by a/1.1
    for co in (coL, coR):
        for a, n in FATm.CORNER0: D += n / Nv(a * co, fat)
    for a, n in FATm.LAUNCH0: D += n / Nv(a * d2, fat)
    for a, n in FATm.REGEN0: D += n / Nv(a * d3, fat)
    for a, n in FATm.SHOCK0: D += n / Nv(a * d1, fat)
    return D
Dn = Dsum(ARM_FAT, mask_arm & in_box); sel = mask_arm & in_box
i = int(np.argmax(np.where(sel, Dn, -1))); res['fatigue'] = dict(FAT=ARM_FAT, worst_D=float('%.3g' % Dn[i]), at_mm=X[i].round(1).tolist(), at_s_mm=round(float(sax[i]), 0), verdict='pass' if Dn[i] <= 0.5 else 'FAIL',
                                                              D_if_welded_FAT22=float('%.3g' % Dsum(22, sel)[i]), D_if_cast_FAT40=float('%.3g' % Dsum(40, sel)[i]))
# stress by station (max vm over cases) for the report
stations = {}
for kk in range(0, 14):
    s_ = S0 + 40 + (S1 - S0 - 80) * kk / 13; m_ = sel & (np.abs(sax - s_) < 12)
    if m_.any(): stations['%d' % round(s_)] = round(float(max(S_all[n][0][m_].max() for n in S_all)), 1)
res['vm_by_station_mm_max_over_cases'] = stations
# mass
Wm = lambda s: secdims(s)
Hh = lambda s: secdims(s)[1]
ss = np.linspace(S0, S1, 200); area = []
for s_ in ss:
    W, H = secdims(s_); area.append(2 * ((W - tw) + (H - tw)) * tw)
res['mass_arm_box_kg'] = round(float(np.trapz(area, ss)) * 2.70e-6, 3); res['mass_caps_kg'] = round(2 * T_CAP * secdims(S0)[0] * secdims(S0)[1] * 2.70e-6, 3)
# ---------------- stiffness (rotation about Y locked at the pivot)
stp = []
def unit_case(Fv, Mv):
    ld = ['*CLOAD,OP=NEW'] + ['%d,%d,%.6e' % (aref, d + 1, Fv[d]) for d in range(3) if abs(Fv[d]) > 0] + ['%d,%d,%.6e' % (arot, d + 1, Mv[d]) for d in range(3) if abs(Mv[d]) > 0]
    return ['*STEP', '*STATIC', '*BOUNDARY', '%d,1,3' % pref, '%d,1,3' % prot] + ld + ['*NODE PRINT,NSET=AX', 'U', '*END STEP']
uvec = u.copy(); zv = np.array([0, 0, 1.0])
stp = [unit_case(np.array([0, 1000.0, 0]), np.zeros(3)), unit_case(np.zeros(3), 1.0e6 * uvec), unit_case(np.zeros(3), 1.0e6 * zv), unit_case(np.array([0, 0, 1000.0]), np.zeros(3)), unit_case(np.zeros(3), 1.0e6 * ey)]
ex2 = ['*NSET,NSET=AX', '%d' % aref, '%d' % arot]
stem2 = 'armstiff-' + tag; write_inp(RUN / (stem2 + '.inp'), stp, ex2); res['ccx_s_stiff'] = round(run_ccx(stem2), 1)
U = []; cur = None
for t in open(RUN / (stem2 + '.dat')):
    if 'S T E P' in t: cur = {}; U.append(cur); continue
    p = t.split()
    if len(p) == 4 and p[0].isdigit() and cur is not None:
        try: cur[int(p[0])] = np.array([float(v) for v in p[1:4]])
        except ValueError: pass
ur = lambda k: U[k][aref]; ro_ = lambda k: U[k][arot]
lat = 1000.0 / abs(ur(0)[1])
twist_u = abs(ro_(1) @ uvec); yaw = abs(ro_(2)[2]); camber = abs(ro_(0)[0])
res['stiffness'] = dict(lateral_kN_per_mm_at_axle=round(lat / 1000, 3), camber_deg_per_kN_lateral=round(math.degrees(abs(ro_(0)[0])), 4),
                        torsion_about_arm_axis_kNm_per_deg=round(1.0 / math.degrees(twist_u), 3) if twist_u else None,
                        yaw_about_Z_kNm_per_deg=round(1.0 / math.degrees(yaw), 3) if yaw else None,
                        vertical_kN_per_mm_at_axle_pivot_Y_locked=round(1.0 / abs(ur(3)[2]), 3),
                        roll_about_Y_note='pivot rotation about Y locked in these runs (shock-supported in service)')
# lateral stiffness at the wheel centre plane from the displacement of A under 1 kN lateral at the axle ref point: u_y; wheel-centre extra from camber lever ya
res['stiffness']['lateral_kN_per_mm_at_wheel_centre'] = round(1.0 / (abs(ur(0)[1]) + 0.0), 3)
(OUT / ('arm-%s.json' % tag)).write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
print(json.dumps(res['stiffness'])); print(json.dumps(res['fatigue'])); print('sf', res['sf']); print('mass', res['mass_arm_box_kg'], res['mass_caps_kg'])
