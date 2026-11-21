"""Bavuso V1.0 primary-structure FEA (CalculiX beam + shell model).

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).

Geometry is read from tools/build-adventure.py (numbers copied below with the line they come from) and the
pack band outline in geometry-adventure-audit.json. The model is:
  - every frame tube, the head tube, swingarm arms, cross brace, shock tower/top bracket, pivot stubs, fork,
    axles and lugs as B32R beams (CalculiX expands them to C3D20R bricks);
  - the structural pack case as S4 shells (4 mm 6082-T6 in the CAD), stepped outline from the 8 cell bands;
  - frame-to-pack lugs as short steel beams onto rigid patches (bolted boss footprint, radius R_PATCH);
  - swingarm on two spherical (translation-tied) pivot points = hinge about Y; the shock is a pin-ended truss.
Loads: every mass of mass-rollup.csv plus rider, pillion and luggage as point loads (pack mass smeared over the
case by area). For cases 1-6 the tyre contact forces are given and the rigid-body accelerations that balance them
are solved (manual inertia relief), so the 3-2-1 supports carry ~0 (printed as a check).

usage:  python fea-frame.py [--h 12] [--variant baseline|revised] [--tag name]
Runs ccx with OMP_NUM_THREADS=4. Writes detailed-design/structures/results-<variant>-h<h>.json; ccx files in
detailed-design/structures/run/.
"""
import math, json, csv, os, sys, subprocess, argparse, time
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                       # v1.0
OUT = ROOT / 'detailed-design' / 'structures'
RUN = OUT / 'run'
CCX = ROOT.parent / '.tools' / 'FreeCAD_1.1.4-Windows-x86_64-py311' / 'bin' / 'ccx.exe'

ap = argparse.ArgumentParser()
ap.add_argument('--h', type=float, default=12.0, help='pack shell element size, mm')
ap.add_argument('--hb', type=float, default=25.0, help='beam element length, mm')
ap.add_argument('--variant', default='baseline')
ap.add_argument('--norun', action='store_true')
ap.add_argument('--set', default='', help='JSON overrides of the design variables')
ap.add_argument('--only', default='all', help='all | stiff')
args = ap.parse_args()

# ------------------------------------------------------------------ materials (MPa, t/mm^3 not needed)
MAT = {
    'ST4130': dict(E=205000, nu=0.29, fy=435, fu=670, note='AISI 4130 normalised tube (AMS 6360 min Fty 75 ksi=517; 435 used for TIG-welded HAZ)'),
    'AL6061': dict(E=69000, nu=0.33, fy=240, fu=290, note='6061-T6, swingarm re-solution-treated and aged after welding; 110 MPa if welded and NOT re-heat-treated'),
    'A356':   dict(E=72000, nu=0.33, fy=200, fu=260, note='A356-T6 casting (shock tower + brace node), no welds'),
    'AL6082': dict(E=70000, nu=0.33, fy=250, fu=290, note='6082-T6 plate/extrusion pack case; FSW seam HAZ ~140 MPa'),
    'STRIG':  dict(E=2.0e7, nu=0.29, fy=1e9, fu=1e9, note='near-rigid connector (head joint cluster, wheels, steerer, test lever): 100x steel modulus'),
    'ST109':  dict(E=205000, nu=0.29, fy=900, fu=1000, note='10.9 bolt / axle steel'),
    'ALFORK': dict(E=70000, nu=0.33, fy=1e9, fu=1e9, note='fork, stiffness only'),
}
RHO = {'A356': 2.68e-6, 'ST4130': 7.85e-6, 'AL6061': 2.70e-6, 'AL6082': 2.70e-6, 'ST109': 7.85e-6}   # kg/mm^3

# ------------------------------------------------------------------ design variables (baseline = CAD)
V = dict(
    rail=(16, 2.5), downlink=(16, 2.5), rearlink=(16, 2.5), tailrail=(14, 2.0), tailbrace=(14, 2.0),
    tailx=(14, 3.0), headtube=(31, 6.0), stub=(20, 5.0),
    arm_pivot=(34, 92, 3.0), arm_axle=(30, 58, 3.0),            # box width(Y), height, wall
    brace=(25, 5.0), tower=(8, 44), topbr=(8, 36),
    pack_t=4.0, pad_t=4.0, pad_r=60.0,
    lug=(30, 40),
    ur_head_w=None,        # steering-axis station (mm from SA0) where the upper rails meet the head tube; None = with the down-links (z850)
    dl_head_w=None,        # same for the down-links
    head_gusset=None,      # (thickness) plate web joining upper rail and down-link near the head, modelled as a RECT tie
    struts=None,           # [(x_on_upper_rail, x_on_pack_top, ro, t), ...] posts from the upper rail down to lugs on the pack roof
    front_t=None,          # pack front-face wall thickness (all front-facing risers); None = pack_t
    rail0=None,            # (ro, t) for the vertical upper-rail leg UR0 (pivot node to seat junction)
    cast_headstock=False,  # fatigue only: cast steel headstock with 60 mm spigots, full-pen butt welds (FAT 63)
    forged_shock_bridge=False,  # fatigue only: shock-top bridge with integral clevis (no plate-root weld)
    rail2=None,            # (ro, t) for the head-end upper-rail segment UR2; None = same as rail
    tailx_box=None,        # (height Z, depth X, wall): shock-top bridge as a box section instead of the tube
    shock_diag=None,       # (ro, t): pair of diagonals from the shock-top cross tube (Y+-60) down-back to the tail braces
    tower_mat='AL6061',    # shock tower + cross brace material ('A356' = one cast node bolted to the arms)
    geom=None,             # frame layout overrides (Nov 20): node_y, node_z, tj_z, tail_y, tail_z, shock_x, eye_z; None = Nov 12 CAD
    pivot_cross=None,      # (x, z, ro, t): cross tube between the two pivot nodes' rails at that point                                                 # steel lug block, width(Y) x depth
)
if args.variant != 'baseline':
    rv = json.loads((OUT / (args.variant + '-sections.json')).read_text())
    for k, v in rv.items():
        V[k] = tuple(v) if isinstance(v, list) else v
if args.set:
    for k, v in json.loads(args.set).items(): V[k] = tuple(v) if isinstance(v, list) else v

# ------------------------------------------------------------------ geometry from build-adventure.py
LIFT = 40.0; RF, RR = 325.3, 311.9; RAKE = math.radians(25); FORK_OFF = 36.1
SA0 = np.array([1206.954, 0, 800.0]); PZ = 350.0; RZ = RR - LIFT; FZ = RF - LIFT
W_AXLE = (FZ - SA0[2] - math.sin(RAKE) * FORK_OFF) / math.cos(RAKE)
FX = SA0[0] + math.cos(RAKE) * FORK_OFF - math.sin(RAKE) * W_AXLE
GROUND = -LIFT
def steer(lx, ly, lz):           # steering frame -> model (rotation -25 deg about Y)
    c, s = math.cos(RAKE), math.sin(RAKE)
    return np.array([SA0[0] + lx * c - lz * s, ly, SA0[2] + lx * s + lz * c])
SD = steer(0, 0, 1) - SA0
audit = json.loads((ROOT / 'geometry-adventure-audit.json').read_text())
BANDS = audit['parameters']['pack_summary']['bands']

# ------------------------------------------------------------------ model containers
nodes = {}; nkey = {}; elems = []          # elems: (id, type, nodes, elset)
elsets = {}; sections = {}                 # elset -> section dict
def node(p, merge=True):
    p = np.asarray(p, float); k = tuple(np.round(p, 2))
    if merge and k in nkey: return nkey[k]
    i = len(nodes) + 1; nodes[i] = p
    if merge: nkey[k] = i
    return i
def add_elem(t, ns, es):
    i = len(elems) + 1; elems.append((i, t, ns, es)); elsets.setdefault(es, []).append(i); return i
member_len = {}
def beam(es, a, b, sec, merge_a=True, merge_b=True, n=None, a_id=None):
    """B32R beam from a to b; returns the node ids along it."""
    if a_id is not None: a = nodes[a_id]
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.linalg.norm(b - a)
    n = n or max(1, math.ceil(L / args.hb))
    pts = [a + (b - a) * k / (2 * n) for k in range(2 * n + 1)]
    ids = [a_id if a_id is not None else node(pts[0], merge_a)] + [node(p, False) for p in pts[1:-1]] + [node(pts[-1], merge_b)]
    for k in range(n): add_elem('B32R', ids[2 * k:2 * k + 3], es)
    sections[es] = sec; member_len[es] = member_len.get(es, 0) + L
    return ids
def chain(es, pts, sec):
    out = []
    for a, b in zip(pts[:-1], pts[1:]): out += beam(es, a, b, sec)
    return out

def pipe(ro, t, mat): return dict(kind='PIPE', p=(ro, t), mat=mat)
def rect(a, b, mat): return dict(kind='RECT', p=(a, b), mat=mat)
def boxs(a, b, t, mat): return dict(kind='BOX', p=(a, b, t, t, t, t), mat=mat)
def circ(r, mat): return dict(kind='CIRC', p=(r,), mat=mat)

def lerp(a, b, t): return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t

# ------------------------------------------------------------------ pack shell mesh
def pack_mesh(h):
    zb = [BANDS[0]['zlo']] + [(BANDS[k + 1]['zlo'] + BANDS[k]['zhi']) / 2 for k in range(len(BANDS) - 1)] + [BANDS[-1]['zhi']]
    def cluster(vals, tol=15):
        s = sorted(set(vals)); groups = [[s[0]]]
        for v in s[1:]:
            (groups[-1].append(v) if v - groups[-1][0] <= tol else groups.append([v]))
        m = {}
        for g in groups:
            for v in g: m[v] = round(sum(g) / len(g), 1)
        return m
    mlo = cluster([b['xlo'] for b in BANDS]); mhi = cluster([b['xhi'] for b in BANDS])
    strips = [(zb[k], zb[k + 1], mlo[b['xlo']], mhi[b['xhi']]) for k, b in enumerate(BANDS)]
    def sub(vals):
        vals = sorted(set(vals)); out = [vals[0]]
        for a, b in zip(vals[:-1], vals[1:]):
            n = max(1, math.ceil((b - a) / h)); out += [a + (b - a) * k / n for k in range(1, n + 1)]
        return out
    YO = 194.0
    xs = sub([s[2] for s in strips] + [s[3] for s in strips]); zs = sub(zb); ys = sub([-YO, YO])
    def inside(xc, zc):
        for z0, z1, x0, x1 in strips:
            if z0 <= zc <= z1: return x0 <= xc <= x1
        return False
    ins = [[inside((xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2) for j in range(len(zs) - 1)] for i in range(len(xs) - 1)]
    E = []   # (n1..n4, face)
    for y in (-YO, YO):
        for i in range(len(xs) - 1):
            for j in range(len(zs) - 1):
                if ins[i][j]:
                    E.append(([(xs[i], y, zs[j]), (xs[i + 1], y, zs[j]), (xs[i + 1], y, zs[j + 1]), (xs[i], y, zs[j + 1])], 'side'))
    I, J = len(xs) - 1, len(zs) - 1
    def isin(i, j): return 0 <= i < I and 0 <= j < J and ins[i][j]
    for i in range(I + 1):          # walls at x = xs[i]
        for j in range(J):
            a, b = isin(i - 1, j), isin(i, j)
            if a != b:
                face = 'front' if a else 'rear'
                for k in range(len(ys) - 1):
                    E.append(([(xs[i], ys[k], zs[j]), (xs[i], ys[k + 1], zs[j]), (xs[i], ys[k + 1], zs[j + 1]), (xs[i], ys[k], zs[j + 1])], face))
    for j in range(J + 1):          # walls at z = zs[j]
        for i in range(I):
            a, b = isin(i, j - 1), isin(i, j)
            if a != b:
                face = 'top' if a else 'bottom'
                for k in range(len(ys) - 1):
                    E.append(([(xs[i], ys[k], zs[j]), (xs[i + 1], ys[k], zs[j]), (xs[i + 1], ys[k + 1], zs[j]), (xs[i], ys[k + 1], zs[j])], face))
    return strips, E
STRIPS, PE = pack_mesh(args.h)
def pack_x_at(z, front=True):
    for z0, z1, x0, x1 in STRIPS:
        if z0 <= z <= z1: return x1 if front else x0

GE = dict(node_y=195.0, node_z=740.0, tj_z=715.0, tail_y=100.0, tail_z=790.0, shock_x=490.0, eye_z=660.0)   # Nov 12 CAD
if V['geom']: GE.update(V['geom'])
def build(suspension=True):
    global nodes, nkey, elems, elsets, sections, member_len
    nodes, nkey, elems, elsets, sections, member_len = {}, {}, [], {}, {}, {}
    info = {}
    # pack shells
    shell_nodes = set(); elem_face = {}
    for quad, face in PE:
        ids = [node(p) for p in quad]; e = add_elem('S4', ids, 'PACK'); elem_face[e] = face; shell_nodes.update(ids)
    info['shell_nodes'] = sorted(shell_nodes); info['elem_face'] = elem_face
    rail, dl, rl = pipe(*V['rail'], 'ST4130'), pipe(*V['downlink'], 'ST4130'), pipe(*V['rearlink'], 'ST4130')
    J = circ(20, 'STRIG')
    ht_lo, ht_hi = SA0 - SD * 30, SA0 + SD * 200; w850 = (850 - 800) / SD[2]; ht_mid = SA0 + SD * w850
    wu = V['ur_head_w'] if V['ur_head_w'] is not None else w850; wd = V['dl_head_w'] if V['dl_head_w'] is not None else w850
    ws = sorted(set([-30, w850, wu, wd, 200]))
    ht = chain('HT', [SA0 + SD * w for w in ws], pipe(*V['headtube'], 'ST4130'))
    info['head'] = dict(lo=node(ht_lo), mid=node(ht_mid), hi=node(ht_hi))
    lugs = {}
    xf_pre = pack_x_at(470.0, True)
    for s in (-1, 1):
        S = 'L' if s < 0 else 'R'; y = 195 * s
        yn = GE['node_y'] * s; zn = GE['node_z']
        piv = (540, y, PZ); ur0b = (570, yn, zn); t715 = (GE['tj_z'] - PZ) / (zn - PZ); p715 = lerp(piv, ur0b, t715)
        if V['pivot_cross']:
            pc = lerp(piv, ur0b, (V['pivot_cross'][1] - PZ) / (zn - PZ)); info['pc_' + S] = pc
            chain('UR0' + S, [piv, pc, p715, ur0b] if zn != GE['tj_z'] else [piv, pc, ur0b], rail)
        else:
            chain('UR0' + S, [piv, p715, ur0b] if zn != GE['tj_z'] else [piv, ur0b], pipe(*V['rail0'], 'ST4130') if V['rail0'] else rail)
        ur1e = np.array([1050, y, 780.0]); ur1p = [np.array(ur0b, float)]
        for k, st in enumerate(V['struts'] or []):
            ur1p.append(lerp(ur0b, ur1e, (st[0] - 570) / 480))
        chain('UR1' + S, sorted(ur1p, key=lambda q: q[0]) + [ur1e], rail)
        for k, st in enumerate(V['struts'] or []):
            top = lerp(ur0b, ur1e, (st[0] - 570) / 480); zt_ = STRIPS[-1][1]
            foot = np.array([st[1], (st[4] if len(st) > 4 else 178.0) * s, zt_]); le = foot + np.array([0, 0, 17.0])
            beam('ST%d%s' % (k, S), top, le, pipe(st[2], st[3], 'ST4130'))
            ids = beam('LUGT%d%s' % (k, S), le, foot + np.array([0, 0, 4.0]), rect(*V['lug'], 'ST4130'), n=1)
            lugs['T%d%s' % (k, S)] = dict(ref=ids[-1], foot=foot, outer=ids[0])
        def hjoint(w):
            c = SA0 + SD * w; return c, c + np.array([-31 * math.cos(RAKE) * 0 + (1184 - ht_mid[0]), 35 * s, 0])
        cu, hu = hjoint(wu); cd, hj = hjoint(wd)
        beam('UR2' + S, (1050, y, 780), hu, pipe(*V['rail2'], 'ST4130') if V['rail2'] else rail)
        info['ur0b_' + S] = node(ur0b)
        beam('JNT', cu, hu, J)
        if wd != wu: beam('JNT', cd, hj, J)
        if V['head_gusset']:
            beam('GUS' + S, hu, lerp(hj, (xf_pre + 17, 180 * s, 470.0), 0.35), rect(V['head_gusset'], 60, 'ST4130'))
            # the gusset end is a node of the down-link (chain below)
        # front down-link and lug onto pack front face (build-adventure.py 386-388)
        zf = 470.0; xf = pack_x_at(zf, True); lf = (xf + 17, 180 * s, zf)
        chain('DL' + S, [hj, lerp(hj, lf, 0.35), lf], dl)
        pf = (xf + 4, 180 * s, zf); ids = beam('LUGF' + S, lf, pf, rect(*V['lug'], 'ST4130'), n=1)
        lugs['F' + S] = dict(ref=ids[-1], foot=np.array([xf, 180 * s, zf]), outer=ids[0])
        # rear link (390-392)
        zr = PZ + 30; xr = pack_x_at(zr, False); lr = (xr - 17, 175 * s, zr)
        beam('RL' + S, piv, lr, rl)
        pr = (xr - 4, 175 * s, zr); ids = beam('LUGR' + S, lr, pr, rect(*V['lug'], 'ST4130'), n=1)
        lugs['R' + S] = dict(ref=ids[-1], foot=np.array([xr, 175 * s, zr]), outer=ids[0])
        # tail (393-394) and shock cross tube (484-485)
        ta, tb = np.array([568, yn, GE['tj_z']]), np.array([-60, GE['tail_y'] * s, GE['tail_z']])
        t490 = (568 - GE['shock_x']) / 628; t160 = (568 - 160) / 628; t280 = (568 - 280) / 628
        chain('TR' + S, [p715, lerp(ta, tb, t490), lerp(ta, tb, t280), lerp(ta, tb, t160), tb], pipe(*V['tailrail'], 'ST4130'))
        tbe = lerp(ta, tb, t160); tbm = lerp(piv, tbe, (560 - PZ) / (tbe[2] - PZ)); info['tbm_' + S] = tbm
        beam('TB' + S, piv, tbe, pipe(*V['tailbrace'], 'ST4130'))
        # pivot node block + stub (444-448)
        ya = 125 + (8 if s < 0 else 0)
        beam('PIV', piv, (540, 150 * s, PZ), rect(40, 60, 'ST4130'))
        stub = beam('STUB' + S, (540, 150 * s, PZ), (540, ya * s, PZ), pipe(*V['stub'], 'ST4130'))
        info['pivot_' + S] = stub[-1]; info['pivnode_' + S] = node(piv)
        info['tail490_' + S] = node(lerp(ta, tb, t490)); info['tail280_' + S] = node(lerp(ta, tb, t280))
        info['tail160_' + S] = node(lerp(ta, tb, t160)); info['tailend_' + S] = node(tb)
    info['lugs'] = lugs
    if V['pivot_cross']:
        beam('PX', info['pc_L'], info['pc_R'], pipe(V['pivot_cross'][2], V['pivot_cross'][3], 'ST4130'))
    # tail shock cross tube and top bracket
    xs_ = GE['shock_x']; t_ = (568 - xs_) / 628
    yt = GE['node_y'] - (GE['node_y'] - GE['tail_y']) * t_; zt = GE['tj_z'] + (GE['tail_z'] - GE['tj_z']) * t_
    chain('TX', [(xs_, -yt, zt), (xs_, -60, zt), (xs_, -26, zt), (xs_, 0, zt), (xs_, 26, zt), (xs_, 60, zt), (xs_, yt, zt)], boxs(*V['tailx_box'][:2], V['tailx_box'][2], 'ST4130') if V['tailx_box'] else pipe(*V['tailx'], 'ST4130'))
    if V['shock_diag']:
        for s in (-1, 1):
            S = 'L' if s < 0 else 'R'
            beam('SD' + S, (xs_, 60 * s, zt), nodes[info['pivnode_' + S]], pipe(*V['shock_diag'], 'ST4130'))
    ez = GE['eye_z']; top_eye = np.array([xs_, 0, ez])
    for s in (-1, 1):
        beam('STB', (xs_, 26 * s, zt), (xs_, 26 * s, ez), rect(*V['topbr'], 'ST4130'))
        beam('BOLT', (xs_, 26 * s, ez), top_eye, circ(6, 'ST109'))
    info['top_eye'] = node(top_eye)
    if suspension:
        # fork in the steering frame (409-433)
        fk = pipe(26, 3, 'ALFORK'); cl = rect(40, 30, 'ALFORK')
        beam('STEER', steer(0, 0, -48), ht_lo, circ(15, 'STRIG')); beam('STEER', ht_hi, steer(0, 0, 216), circ(15, 'STRIG'))
        for s in (-1, 1):
            legs = chain('FORK', [steer(FORK_OFF, 100 * s, W_AXLE), steer(FORK_OFF, 100 * s, -48), steer(FORK_OFF, 100 * s, 216)], fk)
            beam('CLAMP', steer(FORK_OFF, 100 * s, -48), steer(0, 0, -48), cl)
            beam('CLAMP', steer(FORK_OFF, 100 * s, 216), steer(0, 0, 216), cl)
            beam('AXF', steer(FORK_OFF, 100 * s, W_AXLE), (FX, 0, FZ), circ(12.5, 'ST109'))
        info['front_axle'] = node((FX, 0, FZ))
        # swingarm (395-405): box arms tapering, cross brace, shock tower
        for s in (-1, 1):
            S = 'L' if s < 0 else 'R'; ya = 125 + (8 if s < 0 else 0)
            pa, pb = np.array([540, ya * s, PZ]), np.array([0, ya * s, RZ])
            ts = sorted(set([k / 12 for k in range(1, 13)] + [(540 - 380) / 540]))
            prev = node(pa, merge=False); info['armpiv_' + S] = prev; t0 = 0.0
            for k, t1 in enumerate(ts):
                w = lerp(V['arm_pivot'], V['arm_axle'], (t0 + t1) / 2)
                ids = beam('SA%s%02d' % (S, k), None, lerp(pa, pb, t1), boxs(w[0], w[1], w[2], 'AL6061'), n=1, a_id=prev)
                prev = ids[-1]; t0 = t1
            info['armaxle_' + S] = prev
        arm_z = lambda x: RZ + (PZ - RZ) * x / 540
        chain('SAX', [(380, -133, arm_z(380)), (380, -26, arm_z(380)), (380, 26, arm_z(380)), (380, 125, arm_z(380))], pipe(*V['brace'], V['tower_mat']))
        u = np.array([0 - 540, RZ - PZ]); u /= np.linalg.norm(u); nrm = np.array([-u[1], u[0]])
        if nrm[1] < 0: nrm = -nrm
        lo = np.array([540, PZ]) + 210 * u + 120 * nrm
        low_eye = np.array([lo[0], 0, lo[1]])
        for s in (-1, 1):
            beam('STW', (380, 26 * s, arm_z(380)), (lo[0], 26 * s, lo[1]), rect(*V['tower'], V['tower_mat']))
            beam('BOLT', (lo[0], 26 * s, lo[1]), low_eye, circ(6, 'ST109'))
        info['low_eye'] = node(low_eye)
        add_elem('T3D2', [info['top_eye'], info['low_eye']], 'SHOCK'); sections['SHOCK'] = dict(kind='TRUSS', p=(300,), mat='ST109')
        info['shock_axis'] = (top_eye - low_eye) / np.linalg.norm(top_eye - low_eye)
        beam('AXR', (0, -133, RZ), (0, 0, RZ), circ(12.5, 'ST109')); beam('AXR', (0, 0, RZ), (0, 125, RZ), circ(12.5, 'ST109'))
        info['rear_axle'] = node((0, 0, RZ))
    return info

# ------------------------------------------------------------------ inp writer
def section_lines(es, sec):
    if sec['kind'] == 'TRUSS':
        return ['*SOLID SECTION,ELSET=%s,MATERIAL=%s' % (es, sec['mat']), '%g' % sec['p'][0]]
    # local 1-direction: Y for members not along Y, else Z
    e0 = elems[elsets[es][0] - 1]; a, b = nodes[e0[2][0]], nodes[e0[2][-1]]; t = (b - a) / np.linalg.norm(b - a)
    n1 = np.array([0, 1.0, 0]) if abs(t[1]) < 0.9 else np.array([0, 0, 1.0])
    n1 = n1 - t * (n1 @ t); n1 /= np.linalg.norm(n1)
    return ['*BEAM SECTION,ELSET=%s,MATERIAL=%s,SECTION=%s' % (es, sec['mat'], sec['kind']),
            ','.join('%g' % v for v in sec['p']), '%.6f,%.6f,%.6f' % tuple(n1)]

def write_inp(path, steps, info, shell_t, extra=()):
    L = ['*HEADING', 'Bavuso V1.0 structure %s' % path.stem, '*NODE']
    L += ['%d,%.4f,%.4f,%.4f' % (i, *p) for i, p in nodes.items()]
    for t in ('B32R', 'S4', 'T3D2'):
        for es in elsets:
            ids = [e for e in elsets[es] if elems[e - 1][1] == t]
            if not ids: continue
            L.append('*ELEMENT,TYPE=%s,ELSET=%s' % (t, es))
            L += ['%d,%s' % (e, ','.join(map(str, elems[e - 1][2]))) for e in ids]
    for m, d in MAT.items():
        L += ['*MATERIAL,NAME=%s' % m, '*ELASTIC', '%g,%g' % (d['E'], d['nu'])]
    for es, sec in sections.items(): L += section_lines(es, sec)
    # pack shell thickness: pads around lugs get pad_t
    pad = shell_t['pad']; L.append('*ELSET,ELSET=PACKPAD'); L += ['%d' % e for e in pad] or []
    front = [e for e in elsets['PACK'] if e not in set(pad) and info['elem_face'].get(e) == 'front'] if V['front_t'] else []
    rest = [e for e in elsets['PACK'] if e not in set(pad) and e not in set(front)]
    L.append('*ELSET,ELSET=PACKWALL'); L += ['%d' % e for e in rest]
    if front: L += ['*ELSET,ELSET=PACKFRONT'] + ['%d' % e for e in front] + ['*SHELL SECTION,ELSET=PACKFRONT,MATERIAL=AL6082', '%g' % V['front_t']]
    L += ['*SHELL SECTION,ELSET=PACKWALL,MATERIAL=AL6082', '%g' % V['pack_t']]
    if pad: L += ['*SHELL SECTION,ELSET=PACKPAD,MATERIAL=AL6082', '%g' % V['pad_t']]
    # rigid lug patches
    rid = max(nodes) + 1
    for k, lg in info['lugs'].items():
        L.append('*NSET,NSET=PATCH_%s' % k); L += ['%d' % n for n in lg['patch']]
        L += ['*NODE', '%d,%.3f,%.3f,%.3f' % (rid, *nodes[lg['ref']])]
        L.append('*RIGID BODY,NSET=PATCH_%s,REF NODE=%d,ROT NODE=%d' % (k, lg['ref'], rid)); rid += 1
    L += list(extra)
    for st in steps: L += st
    path.write_text('\n'.join(L) + '\n')

def patches(info, R=35.0):
    sh = info['shell_nodes']; P = np.array([nodes[n] for n in sh])
    for k, lg in info['lugs'].items():
        d = np.linalg.norm(P - lg['foot'], axis=1); sel = [sh[i] for i in np.where(d <= R)[0]]
        if len(sel) < 6: sel = [sh[i] for i in np.argsort(d)[:6]]
        lg['patch'] = sel
    pad = []
    if V['pad_t'] != V['pack_t']:
        for e in elsets['PACK']:
            c = np.mean([nodes[n] for n in elems[e - 1][2]], axis=0)
            if any(np.linalg.norm(c - lg['foot']) <= V['pad_r'] for lg in info['lugs'].values()): pad.append(e)
    return dict(pad=pad)

# ------------------------------------------------------------------ masses
def shell_trib():
    tr = {}
    for e in elsets['PACK']:
        p = [nodes[n] for n in elems[e - 1][2]]
        A = 0.5 * np.linalg.norm(np.cross(p[2] - p[0], p[3] - p[1]))
        for n in elems[e - 1][2]: tr[n] = tr.get(n, 0) + A / 4
    return tr

def mass_points(info, two_up=True):
    """Return list of (node, kg). Pack mass smeared over case nodes by area."""
    rows = list(csv.DictReader(open(ROOT / 'mass-rollup.csv', encoding='utf-8')))
    pts = []; pack_kg = 0.0
    bb = (min(s[2] for s in STRIPS), max(s[3] for s in STRIPS), STRIPS[0][0], STRIPS[-1][1])
    skip = ('Rear_', 'Front_', 'Fork_', 'Swingarm', 'Shock_', 'Drive_belt')
    cand = [n for n in nodes if n not in set(info['shell_nodes'])]
    C = np.array([nodes[n] for n in cand])
    for r in rows:
        kg = float(r['kg']); x, y, z = float(r['x_mm']), float(r['y_mm']), float(r['height_mm']) - LIFT
        un = r['unsprung'].strip()
        if r['group'] == 'Energy' or (bb[0] - 30 <= x <= bb[1] + 30 and z <= bb[3] + 260 and r['group'] in ('Electronics', 'Allowance') and abs(y) < 200):
            pack_kg += kg; continue
        if un:
            frac = float(un[1:]); ax = info.get('rear_axle' if un[0] == 'R' else 'front_axle')
            if ax: pts.append((ax, kg * frac))
            kg *= (1 - frac)
            if kg <= 0: continue
        d = np.linalg.norm(C - np.array([x, y, z]), axis=1)
        if abs(y) < 60:   # split to the nearest node on each side
            for sgn in (-1, 1):
                m = np.where(np.sign(C[:, 1]) == sgn, d, 1e9); pts.append((cand[int(np.argmin(m))], kg / 2))
        else:
            pts.append((cand[int(np.argmin(d))], kg))
    pack_total = max(pack_kg, 133.7) + 0.0
    extra_pack = pack_kg  # everything that sits in/on the pack
    tr = shell_trib(); At = sum(tr.values())
    for n, a in tr.items(): pts.append((n, extra_pack * a / At))
    # rider 85 kg: 65% seat (tail rails at X~490), 30% pegs (pivot nodes), 5% bars (head)
    for S in 'LR':
        pts += [(info['tail490_' + S], 85 * 0.65 / 2), (info['pivnode_' + S], 85 * 0.30 / 2)]
    pts += [(info['head']['hi'], 85 * 0.05)]
    if two_up:
        for S in 'LR':
            pts += [(info['tail280_' + S], 80 * 0.85 / 2), (info['tail160_' + S], 80 * 0.15 / 2), (info['tailend_' + S], 30 / 2)]
    return pts, extra_pack

G = 9.81
def rigid_accel(pts, contacts):
    """contacts: list of (node, F[3] N). Returns a (m/s2), alpha (rad/s2), cg (mm)."""
    m = np.array([k for _, k in pts]); r = np.array([nodes[n] for n, _ in pts]) / 1000.0
    M = m.sum(); cg = (m[:, None] * r).sum(0) / M; rho = r - cg
    I = sum(mi * (np.dot(p, p) * np.eye(3) - np.outer(p, p)) for mi, p in zip(m, rho))
    F = sum(np.asarray(f) for _, f in contacts); Mo = sum(np.cross(nodes[n] / 1000.0 - cg, f) for n, f in contacts)
    a = np.array([0, 0, -G]) + F / M; al = np.linalg.solve(I, Mo)
    return a, al, cg * 1000, M

def load_lines(pts, contacts, a, al, cg):
    f = {}
    for n, mi in pts:
        rho = (nodes[n] - cg) / 1000.0
        F = mi * (np.array([0, 0, -G]) - a - np.cross(al, rho))
        f[n] = f.get(n, 0) + F
    for n, F in contacts: f[n] = f.get(n, 0) + np.asarray(F)
    L = ['*CLOAD,OP=NEW']
    for n, F in f.items():
        for d in range(3):
            if abs(F[d]) > 1e-9: L.append('%d,%d,%.6e' % (n, d + 1, F[d]))
    return L

# ------------------------------------------------------------------ frd / dat parsing
def parse_frd(path):
    _pairs_cache.clear()
    coords = {}; el = {}; steps = []; cur = None; mode = None
    with open(path) as fh:
        lines = fh.readlines()
    i = 0
    while i < len(lines):
        s = lines[i]
        if s.startswith('    2C'):
            i += 1
            while not lines[i].startswith(' -3'):
                t = lines[i]; coords[int(t[3:13])] = np.array([float(t[13:25]), float(t[25:37]), float(t[37:49])]); i += 1
        elif s.startswith('    3C'):
            i += 1
            while not lines[i].startswith(' -3'):
                t = lines[i]
                if t.startswith(' -1'):
                    eid = int(t[3:13]); el[eid] = []
                elif t.startswith(' -2'):
                    el[eid] += [int(t[3 + 10 * k:13 + 10 * k]) for k in range((len(t.rstrip()) - 3) // 10)]
                i += 1
        elif s.startswith(' -4'):
            name = s.split()[1]; ncomp = int(s.split()[2]); i += 1
            while lines[i].startswith(' -5'): i += 1
            data = {}
            while not lines[i].startswith(' -3'):
                t = lines[i]
                if t.startswith(' -1'):
                    data[int(t[3:13])] = [float(t[13 + 12 * k:25 + 12 * k]) for k in range((len(t.rstrip()) - 13) // 12)]
                i += 1
            if name == 'DISP': steps.append({'U': data})
            elif name == 'STRESS': steps[-1]['S'] = data
        i += 1
    return coords, el, steps

def parse_dat(path):
    """Returns list per step of dict: {'U': {node: vec}, 'RF': {node: vec}, 'S': {(elem,ip): vec}}"""
    out = []; cur = None; kind = None
    for t in open(path):
        if 'S T E P' in t: cur = {'U': {}, 'RF': {}, 'S': {}}; out.append(cur); kind = None; continue
        tl = t.strip()
        if tl.startswith('displacements'): kind = 'U'; continue
        if tl.startswith('forces'): kind = 'RF'; continue
        if tl.startswith('stresses'): kind = 'S'; continue
        if not tl or cur is None or kind is None: continue
        p = tl.split()
        try:
            if kind == 'S': cur['S'][(int(p[0]), int(p[1]))] = np.array([float(v) for v in p[2:8]])
            else: cur[kind][int(p[0])] = np.array([float(v) for v in p[1:4]])
        except ValueError:
            kind = None
    return out

def tensor(v): return np.array([[v[0], v[3], v[5]], [v[3], v[1], v[4]], [v[5], v[4], v[2]]])
def vm(v):
    s = tensor(v); d = s - np.trace(s) / 3 * np.eye(3); return math.sqrt(1.5 * np.sum(d * d))

# ------------------------------------------------------------------ post-processing helpers
def beam_axis(eid):
    ns = elems[eid - 1][2]; t = nodes[ns[-1]] - nodes[ns[0]]; return t / np.linalg.norm(t)
def member_of(eid): return elems[eid - 1][3]

SKIP = ('BOLT', 'JNT', 'STEER', 'AXF', 'AXR', 'WHEEL', 'CLAMP', 'FORK', 'LEVER')
_pairs_cache = {}
def pairs(el, coords, info):
    """Vectorised (element, expanded node) table: key per row, beam axis per row, distance to nearest lug foot."""
    k = id(el)
    if k in _pairs_cache: return _pairs_cache[k]
    keys, nid, axv, isb = [], [], [], []
    for eid, ens in el.items():
        if eid > len(elems): continue
        es = member_of(eid); t = elems[eid - 1][1]
        if t == 'T3D2' or es in SKIP: continue
        if t == 'B32R': key = es; ax = beam_axis(eid)
        else: key = 'PACK_' + info['elem_face'].get(eid, '?'); ax = np.zeros(3)
        for n in ens: keys.append(key); nid.append(n); axv.append(ax); isb.append(t == 'B32R')
    nid = np.array(nid); X = np.array([coords[n] for n in nid]); feet = np.array([lg['foot'] for lg in info['lugs'].values()])
    dmin = np.min(np.linalg.norm(X[:, None, :] - feet[None, :, :], axis=2), axis=1)
    r = dict(keys=np.array(keys), nid=nid, ax=np.array(axv), isb=np.array(isb), X=X, dmin=dmin)
    _pairs_cache[k] = r; return r

def _tens(Sarr):   # rows of 6 -> (n,3,3)
    T = np.zeros((len(Sarr), 3, 3)); T[:, 0, 0], T[:, 1, 1], T[:, 2, 2] = Sarr[:, 0], Sarr[:, 1], Sarr[:, 2]
    T[:, 0, 1] = T[:, 1, 0] = Sarr[:, 3]; T[:, 1, 2] = T[:, 2, 1] = Sarr[:, 4]; T[:, 0, 2] = T[:, 2, 0] = Sarr[:, 5]
    return T

def _values(P, Sarr):
    T = _tens(Sarr); ax = P['ax']
    sa = np.einsum('ni,nij,nj->n', ax, T, ax); tv = np.einsum('nij,nj->ni', T, ax) - sa[:, None] * ax
    nom = np.sqrt(sa ** 2 + 3 * np.sum(tv * tv, axis=1))
    tr = np.trace(T, axis1=1, axis2=2); D = T - tr[:, None, None] / 3 * np.eye(3)
    vmv = np.sqrt(1.5 * np.sum(D * D, axis=(1, 2)))
    ev = np.linalg.eigvalsh(T); pmax = np.where(np.abs(ev[:, 0]) > np.abs(ev[:, 2]), ev[:, 0], ev[:, 2])
    val = np.where(P['isb'], nom, vmv); sig = np.where(P['isb'], sa, pmax)
    return val, sig, sa, pmax

def _groupmax(P, val, mask, extra=None):
    res = {}
    for key in np.unique(P['keys'][mask]):
        m = mask & (P['keys'] == key); i = np.where(m)[0][np.argmax(val[m])]
        res[key] = (float(val[i]), float(extra[i]) if extra is not None else None, P['X'][i].round(1).tolist())
    return res

def evaluate(el, coords, S, info, exclude_patch=0.0):
    """Per elset: max nominal (beam: sqrt(sa^2+3tau^2) from the axial/shear components) or von Mises (shell)."""
    P = pairs(el, coords, info); Sarr = np.array([S[n] for n in P['nid']])
    val, sig, _, _ = _values(P, Sarr)
    mask = P['isb'] | (P['dmin'] >= exclude_patch)
    return _groupmax(P, val, mask, sig)

def lug_forces(el, coords, S, info, side_key):
    """Section resultants of a lug beam near its pack end from the expanded RECT brick (linear fit of axial stress,
    serendipity-weighted shear)."""
    lg = info['lugs'][side_key]
    eid = elsets['LUG' + side_key][0]
    ns = elems[eid - 1][2]; a, b = nodes[ns[0]], nodes[ns[-1]]; ax = (b - a) / np.linalg.norm(b - a)
    en = el[eid]; P = np.array([coords[n] for n in en]); s = (P - a) @ ax
    sel = [en[i] for i in range(len(en)) if abs(s[i] - s.min()) < 1e-3]     # section at the frame end
    # local axes
    e1 = np.array([0, 1.0, 0]); e1 -= ax * (e1 @ ax); e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
    c = np.mean([coords[n] for n in sel], axis=0)
    X = np.array([[1, (coords[n] - c) @ e1, (coords[n] - c) @ e2] for n in sel])
    sa = np.array([ax @ tensor(S[n]) @ ax for n in sel])
    coef = np.linalg.lstsq(X, sa, rcond=None)[0]
    bw, bd = V['lug']; A = bw * bd; I1 = bd * bw ** 3 / 12; I2 = bw * bd ** 3 / 12   # about e2 (width along e1) and e1
    N = coef[0] * A; M2 = -coef[1] * I1; M1 = coef[2] * I2
    corner = [abs(abs((coords[n] - c) @ e1) - bw / 2) < 0.5 and abs(abs((coords[n] - c) @ e2) - bd / 2) < 0.5 for n in sel]
    w = np.array([-1 / 12 if k else 1 / 3 for k in corner]) * A
    V1 = sum(wi * (e1 @ tensor(S[n]) @ ax) for wi, n in zip(w, sel)); V2 = sum(wi * (e2 @ tensor(S[n]) @ ax) for wi, n in zip(w, sel))
    F = N * ax + V1 * e1 + V2 * e2
    return dict(F_N=F.round(1).tolist(), axial_N=round(N, 1), shear_N=round(math.hypot(V1, V2), 1),
                M_bend_Nmm=round(math.hypot(M1, M2), 1), n_section_nodes=len(sel))

def run_ccx(stem):
    env = dict(os.environ, OMP_NUM_THREADS='4', CCX_NPROC_EQUATION_SOLVER='4')
    t0 = time.time()
    p = subprocess.run([str(CCX), stem], cwd=RUN, env=env, capture_output=True, text=True)
    log = (RUN / (stem + '.log')); log.write_text(p.stdout + p.stderr)
    if 'Job finished' not in p.stdout:
        print(p.stdout[-3000:]); raise SystemExit('ccx failed: ' + stem)
    return time.time() - t0

def mass_report():
    out = {}
    for es, L in member_len.items():
        sec = sections[es]
        if sec['mat'] not in RHO: continue
        k, p = sec['kind'], sec['p']
        if k == 'PIPE': A = math.pi * (p[0] ** 2 - (p[0] - p[1]) ** 2)
        elif k == 'BOX': A = p[0] * p[1] - (p[0] - 2 * p[2]) * (p[1] - 2 * p[2])
        elif k == 'RECT': A = p[0] * p[1]
        else: A = math.pi * p[0] ** 2
        out[es] = round(A * L * RHO[sec['mat']], 3)
    return out

# ====================================================================== main analysis
RUN.mkdir(parents=True, exist_ok=True)
tag = '%s-h%g' % (args.variant, args.h) + ('-' + args.only if args.only != 'all' else '')
info = build(True); sh = patches(info)
pts, pack_on = mass_points(info, True)
Mtot = sum(k for _, k in pts)
# static contact loads from the CoG
cgx = sum(nodes[n][0] * k for n, k in pts) / Mtot; cgz = sum(nodes[n][2] * k for n, k in pts) / Mtot
WB = FX; W = Mtot * G; hcg = cgz - GROUND
Ff = W * cgx / WB; Fr = W - Ff
crx = node((0, 0, GROUND)); crf = node((FX, 0, GROUND))
# offset contact points for cornering (tyre crown radius x sin45): rear 160 section ~80 mm, front 120 ~60 mm
d_r, d_f = 80 * math.sin(math.radians(45)), 60 * math.sin(math.radians(45))
crx_o = node((0, -d_r, GROUND)); crf_o = node((FX, -d_f, GROUND))
beam('WHEEL', (0, 0, RZ), (0, 0, GROUND), circ(40, 'STRIG')); beam('WHEEL', (FX, 0, FZ), (FX, 0, GROUND), circ(40, 'STRIG'))
beam('WHEEL', (0, 0, RZ), (0, -d_r, GROUND), circ(40, 'STRIG')); beam('WHEEL', (FX, 0, FZ), (FX, -d_f, GROUND), circ(40, 'STRIG'))
sh = patches(info)
# braking statics
Fzf_b = W * (cgx + 1.1 * hcg) / WB; Fzr_b = W - Fzf_b
DYN = 1.5; nz = DYN / math.cos(math.radians(45))
CASES = {
    'C1_static_1g_two_up':      [(crf, (0, 0, Ff)), (crx, (0, 0, Fr))],
    'C2_front_bump_3g':         [(crf, (0, 0, 3 * Ff)), (crx, (0, 0, Fr))],
    'C3_braking_1.1g':          [(crf, (-1.1 * W, 0, Fzf_b)), (crx, (0, 0, Fzr_b))],
    'C4_braking_plus_bump':     [(crf, (-1.1 * W - 0.25 * 2 * Ff, 0, Fzf_b + 2 * Ff)), (crx, (0, 0, Fzr_b))],
    'C5_corner_45deg_x1.5':     [(crf_o, (0, nz * Ff * d_f / hcg, nz * Ff)), (crx_o, (0, nz * Fr * d_r / hcg, nz * Fr))],
    'C6_rear_bump_3g':          [(crf, (0, 0, Ff)), (crx, (0, 0, 3 * Fr))],
}
watch = sorted(set([info['head']['lo'], info['head']['hi'], info['head']['mid'], info['pivot_L'], info['pivot_R'], info['front_axle'], info['rear_axle'],
                    info['top_eye'], info['low_eye']] + [lg['ref'] for lg in info['lugs'].values()]))
sup = [crf, crx, info['head']['lo']]
steps = []; meta = {}
for name, cont in CASES.items():
    a, al, cg, M = rigid_accel(pts, cont)
    meta[name] = dict(contacts={str(n): np.round(f, 1).tolist() for n, f in cont}, accel_g=(a / G).round(3).tolist(), alpha=al.round(3).tolist())
    # supports: front contact xyz, rear contact yz, lower head bearing y (only a roll stop); loads are self-balanced
    fn = [n for n, _ in cont]
    bc = ['*BOUNDARY', '%d,1,3' % fn[0], '%d,2,3' % fn[1], '%d,2,2' % info['head']['lo']]
    steps.append(['*STEP', '*STATIC'] + bc + load_lines(pts, cont, a, al, cg) +
                 ['*NODE PRINT,NSET=WATCH', 'U', '*NODE PRINT,NSET=SUPP', 'RF', '*EL PRINT,ELSET=SHOCK', 'S',
                  '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP'])
extra = ['*NSET,NSET=WATCH'] + ['%d' % n for n in watch] + ['*NSET,NSET=SUPP'] + ['%d' % n for n in sorted(set([crf, crx, crf_o, crx_o, info['head']['lo']]))]
# pivot hinge: arm pivot point tied to stub end in translation
for S in 'LR':
    for d in (1, 2, 3):
        extra += ['*EQUATION', '2', '%d,%d,1.0,%d,%d,-1.0' % (info['armpiv_' + S], d, info['pivot_' + S], d)]
stem = 'frame-' + tag
write_inp(RUN / (stem + '.inp'), steps, info, sh, extra)
nodes_main = dict(nodes); elems_main = list(elems); elsets_main = dict(elsets); info_main = info
print('model: %d nodes, %d elements, mass %.1f kg, CoG x %.0f z %.0f (model), Ff %.0f N, Fr %.0f N' % (len(nodes), len(elems), Mtot, cgx, cgz, Ff, Fr))
results = dict(variant=args.variant, h=args.h, V={k: v for k, v in V.items()}, mass_kg=round(Mtot, 1), cg_model_mm=[round(cgx), round(cgz)],
               static_wheel_N=[round(Ff), round(Fr)], braking_wheel_N=[round(Fzf_b), round(Fzr_b)], hcg_mm=round(hcg), cases={}, meta=meta,
               n_nodes=len(nodes), n_elems=len(elems), pack_mass_on_case_kg=round(pack_on, 1))
if args.norun: raise SystemExit
if args.only == 'stiff': CASES = {}
if CASES:
    results['ccx_s_frame'] = round(run_ccx(stem), 1)
    coords, el, fsteps = parse_frd(RUN / (stem + '.frd')); dsteps = parse_dat(RUN / (stem + '.dat'))
else: fsteps = dsteps = []
for (name, cont), fs, ds in zip(CASES.items(), fsteps, dsteps):
    r = evaluate(el, coords, fs['S'], info); r2 = evaluate(el, coords, fs['S'], info, exclude_patch=35 + 25)
    shock = [v for k, v in ds['S'].items()]
    d_ = info['shock_axis']; sF = float(np.mean([d_ @ tensor(np.asarray(v)[[0, 1, 2, 3, 5, 4]]) @ d_ for v in shock])) * 300 if shock else None
    U = ds['U']
    results['cases'][name] = dict(
        stress={k: [round(v[0], 1), round(v[1], 1), v[2]] for k, v in sorted(r.items())},
        pack_away_from_lugs={k: [round(v[0], 1), v[2]] for k, v in r2.items() if k.startswith('PACK')},
        shock_force_N=round(sF, 0) if sF else None,
        reactions_N={str(k): v.round(2).tolist() for k, v in ds['RF'].items()},
        disp_mm={'head_lo': U[info['head']['lo']].round(3).tolist(), 'head_hi': U[info['head']['hi']].round(3).tolist(),
                 'front_axle': U[info['front_axle']].round(3).tolist(), 'rear_axle': U[info['rear_axle']].round(3).tolist(),
                 'pivot_L': U[info['pivot_L']].round(3).tolist(), 'top_eye': U[info['top_eye']].round(3).tolist()},
        lugs={k: lug_forces(el, coords, fs['S'], info, k) for k in info['lugs']})
    # keep signed stress tensors at detail nodes for fatigue (per elset, per node)
def eval_delta(el, coords, S1, S0, info, rmin=0.0, rmax=1e9):
    """Max |stress change| per member between two cases: beam axial stress, shell largest-magnitude principal.
    Shell nodes are filtered by distance from the nearest lug foot (rmin..rmax)."""
    P = pairs(el, coords, info); D = np.array([np.array(S1[n]) - np.array(S0[n]) for n in P['nid']])
    _, _, sa, pmax = _values(P, D); val = np.where(P['isb'], np.abs(sa), np.abs(pmax))
    mask = P['isb'] | ((P['dmin'] >= rmin) & (P['dmin'] <= rmax))
    return {k: [round(v[0], 2), v[2]] for k, v in _groupmax(P, val, mask).items()}
if CASES:
    S0 = fsteps[0]['S']; results['delta_vs_C1'] = {}
    for name, fs in zip(CASES, fsteps):
        if name.startswith('C1'): continue
        results['delta_vs_C1'][name] = dict(members=eval_delta(el, coords, fs['S'], S0, info, 60.0),
                                            pack_lug_edge=eval_delta(el, coords, fs['S'], S0, info, 35.0, 35.0 + 1.5 * args.h))
if CASES: np.savez_compressed(RUN / ('stress-' + stem + '.npz'), **{name: np.array([[n] + fs['S'][n] for n in sorted(fs['S'])]) for name, fs in zip(CASES, fsteps)})
results['member_mass_kg'] = mass_report()
A_pack = sum(0.5 * np.linalg.norm(np.cross(nodes[elems[e - 1][2][2]] - nodes[elems[e - 1][2][0]], nodes[elems[e - 1][2][3]] - nodes[elems[e - 1][2][1]])) for e in elsets['PACK'])
results['pack_case_area_m2'] = round(A_pack / 1e6, 4)
def _area(e): p = [nodes[n] for n in elems[e - 1][2]]; return 0.5 * np.linalg.norm(np.cross(p[2] - p[0], p[3] - p[1]))
A_pad = sum(_area(e) for e in sh['pad']); A_front = sum(_area(e) for e in elsets['PACK'] if info['elem_face'].get(e) == 'front' and e not in set(sh['pad']))
results['pack_case_mass_kg'] = round((A_pack * V['pack_t'] + A_pad * (V['pad_t'] - V['pack_t']) + (A_front * (V['front_t'] - V['pack_t']) if V['front_t'] else 0)) * 2.70e-6, 2)
results['pack_pad_area_m2'] = round(A_pad / 1e6, 4); results['pack_front_area_m2'] = round(A_front / 1e6, 4)


# ------------------------------------------------------------------ case 7 (pack retention) and case 8 (stiffness): frame without suspension
info = build(False); sh = patches(info)
tr = shell_trib(); At = sum(tr.values())
cells_kg, rest_kg = 106.9, 133.7 - 106.9
def face_nodes(face):
    s = set()
    for e, f in info['elem_face'].items():
        if f == face: s.update(elems[e - 1][2])
    return s
def face_trib(face):
    t = {}
    for e, f in info['elem_face'].items():
        if f != face: continue
        p = [nodes[n] for n in elems[e - 1][2]]
        if face == 'side' and p[0][1] < 0: continue      # +Y lateral load bears on the +Y side wall only
        A = 0.5 * np.linalg.norm(np.cross(p[2] - p[0], p[3] - p[1]))
        for n in elems[e - 1][2]: t[n] = t.get(n, 0) + A / 4
    return t
steps7 = []; c7 = {} if args.only == 'stiff' else {'C7a_pack_20g_longitudinal': (0, 'front', 20), 'C7b_pack_8g_lateral': (1, 'side', 8), 'C7c_pack_5g_vertical': (2, 'bottom', 5)}
fix = sorted([info['head']['lo'], info['head']['mid'], info['head']['hi'], info['pivnode_L'], info['pivnode_R']])
for name, (d, face, ng) in c7.items():
    f = {}
    sgn = -1 if d == 2 else 1
    for n, a in tr.items(): f[n] = f.get(n, 0) + rest_kg * ng * G * a / At
    ft = face_trib(face); Af = sum(ft.values())
    for n, a in ft.items(): f[n] = f.get(n, 0) + cells_kg * ng * G * a / Af
    L = ['*CLOAD,OP=NEW'] + ['%d,%d,%.6e' % (n, d + 1, sgn * v) for n, v in f.items()]
    steps7.append(['*STEP', '*STATIC', '*BOUNDARY'] + ['%d,1,6' % n for n in fix] + L +
                  ['*NODE PRINT,NSET=FIX', 'RF', '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP'])
# C9: safety request - 21 kN outward (+Y, right side) crash-guard load at three mount points, same fixity
if c7:
    for name, n_ in [('C9a_guard_21kN_upper_rail_node', info['ur0b_R']), ('C9b_guard_21kN_front_lug', info['lugs']['FR']['outer']),
                     ('C9c_guard_21kN_rear_link_lug', info['lugs']['RR']['outer'])]:
        c7[name] = None
        steps7.append(['*STEP', '*STATIC', '*BOUNDARY'] + ['%d,1,6' % n for n in fix] + ['*CLOAD,OP=NEW', '%d,2,21000.0' % n_] +
                      ['*NODE PRINT,NSET=FIX', 'RF', '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP'])
extra7 = ['*NSET,NSET=FIX'] + ['%d' % n for n in fix]
stem7 = 'pack-retention-' + tag
write_inp(RUN / (stem7 + '.inp'), steps7, info, sh, extra7)
if c7:
    results['ccx_s_pack'] = round(run_ccx(stem7), 1)
    coords, el, fsteps = parse_frd(RUN / (stem7 + '.frd')); dsteps = parse_dat(RUN / (stem7 + '.dat'))
for name, fs, ds in zip(c7, fsteps, dsteps):
    r = evaluate(el, coords, fs['S'], info); r2 = evaluate(el, coords, fs['S'], info, exclude_patch=60)
    results['cases'][name] = dict(stress={k: [round(v[0], 1), round(v[1], 1), v[2]] for k, v in sorted(r.items())},
                                  pack_away_from_lugs={k: [round(v[0], 1), v[2]] for k, v in r2.items() if k.startswith('PACK')},
                                  reaction_total_N=np.round(sum(ds['RF'].values()), 1).tolist(),
                                  lugs={k: lug_forces(el, coords, fs['S'], info, k) for k in info['lugs']})

# stiffness: pivot stubs fixed at the bearing points, torque about X and lateral force at the head
lev = 200.0
hm = nodes[info['head']['mid']]
la = beam('LEVER', hm, hm + np.array([0, -lev, 0]), circ(30, 'STRIG')); lb = beam('LEVER', hm, hm + np.array([0, lev, 0]), circ(30, 'STRIG'))
sh = patches(info)
T = 1.0e6   # 1 kNm
fixp = [info['pivot_L'], info['pivot_R']]
steps8 = []
for nm, loads in [('torsion', ['%d,3,%.3f' % (la[-1], T / (2 * lev)), '%d,3,%.3f' % (lb[-1], -T / (2 * lev))]),
                  ('lateral', ['%d,2,1000.0' % info['head']['mid']])]:
    steps8.append(['*STEP', '*STATIC', '*BOUNDARY'] + ['%d,1,6' % n for n in fixp] + ['*CLOAD,OP=NEW'] + loads +
                  ['*NODE PRINT,NSET=W8', 'U', '*EL PRINT,ELSET=EALL,TOTALS=NO', 'ELSE', '*NODE FILE', 'U', '*EL FILE', 'S', '*END STEP'])
extra8 = ['*ELSET,ELSET=EALL'] + ['%d' % e[0] for e in elems if e[1] != 'T3D2'] + ['*NSET,NSET=W8'] + ['%d' % n for n in [la[-1], lb[-1], info['head']['mid'], info['head']['lo'], info['head']['hi']]]
stem8 = 'stiffness-' + tag
write_inp(RUN / (stem8 + '.inp'), steps8, info, sh, extra8)
results['ccx_s_stiff'] = round(run_ccx(stem8), 1)
ds = parse_dat(RUN / (stem8 + '.dat'))
uz = ds[0]['U'][la[-1]][2] - ds[0]['U'][lb[-1]][2]
theta = math.degrees(math.atan2(uz, 2 * lev))
uy = ds[1]['U'][info['head']['mid']][1]
def energy_split(path, step):
    en = {}; k = -1; on = False
    for t in open(path):
        if 'S T E P' in t: k += 1; on = False
        if 'internal energy' in t: on = True; continue
        if on and k == step:
            p = t.split()
            if len(p) == 2:
                e = int(p[0]); es = elems[e - 1][3]
                g = 'PACK_' + info['elem_face'][e] if es == 'PACK' else es.rstrip('LR') if not es.startswith('SA') else 'SA'
                g = g[:-1] if g[-1:].isdigit() and g.startswith(('ST', 'LUGT')) else g
                en[g] = en.get(g, 0) + float(p[1])
    tot = sum(en.values())
    return {g: round(100 * v / tot, 1) for g, v in sorted(en.items(), key=lambda kv: -kv[1]) if v / tot > 0.01}
results['stiffness_energy_share_pct'] = dict(torsion=energy_split(RUN / (stem8 + '.dat'), 0), lateral=energy_split(RUN / (stem8 + '.dat'), 1))
print(results['stiffness_energy_share_pct'])
results['stiffness'] = dict(torsion_kNm_per_deg=round(1.0 / theta, 3), head_twist_deg_per_kNm=round(theta, 4),
                            lateral_kN_per_mm=round(1.0 / uy, 3), lateral_head_defl_mm_per_kN=round(uy, 4))
OUT.mkdir(exist_ok=True)
(OUT / ('results-%s.json' % tag)).write_text(json.dumps(results, indent=1))
print(json.dumps(results['stiffness']))
for c, r in results['cases'].items():
    top = sorted(r['stress'].items(), key=lambda kv: -kv[1][0])[:6]
    print(c, r.get('shock_force_N'), ' | '.join('%s %.0f' % (k, v[0]) for k, v in top))
