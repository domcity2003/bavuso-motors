#!/usr/bin/env python
"""Bavuso V1 rev E concept drawing pack (9 sheets + combined PDF).

Run from v1.0 with FreeCAD's python:
    ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drawings-v1.py [--only BV-ENG-0001,...]
Takes about 10 to 25 minutes (opens the 199-solid model, hidden-line removal per view).

Method: TechDraw cannot export a page without the GUI, so this uses TechDraw's own headless
hidden-line projection (TechDraw.projectEx) on each solid, then draws the 2D edges, dimensions
and title block with matplotlib at 1 data unit = 1 mm on an A3 page.  Views are third-angle:
primary = view from the vehicle -Y side, top above it, front-end view to its right, iso upper right.

Reads: cad/Bavuso-V1.0-adventure.FCStd, program/data/parts-ledger.csv (via bom-v1.py).  Writes:
drawings/*.pdf, drawings/V1-drawing-pack.pdf, program/data/drawings-derived.json, program/data/drawings-features.json.
The CAD generator and the ledger are never touched.
"""
import sys, os, json, math, re, time, importlib.util, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FCBIN = os.path.abspath(os.path.join(ROOT, '..', '.tools', 'FreeCAD_1.1.4-Windows-x86_64-py311', 'bin'))
sys.path.append(FCBIN)
import FreeCAD, Part, TechDraw  # noqa: E402
from FreeCAD import Vector as V, Matrix  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, Circle as MCircle  # noqa: E402

spec = importlib.util.spec_from_file_location('bomv1', os.path.join(HERE, 'bom-v1.py'))
bom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bom)

FCSTD = os.path.join(ROOT, 'cad', 'Bavuso-V1.0-adventure.FCStd')
OUTDIR = os.path.join(ROOT, 'drawings')
DATADIR = os.path.join(ROOT, 'program', 'data')
os.makedirs(OUTDIR, exist_ok=True)
TODAY = '2026-11-22'
LID_Z = 625.1          # underside of the 3 mm roof slab of the case solid (measured)

# --------------------------------------------------------------------------- views
def unit(v):
    l = math.sqrt(sum(c * c for c in v))
    return tuple(c / l for c in v)

def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def make_view(n, up):
    n = unit(n)
    d = dot(up, n)
    up = unit(tuple(up[i] - d * n[i] for i in range(3)))
    r = cross(up, n)           # viewer right; r x up = n (toward viewer)
    return dict(n=n, u=up, r=r)

VIEWS = {
    'left': make_view((0, -1, 0), (0, 0, 1)),   # primary: viewer on the -Y side, front (+X) to the right
    'top':  make_view((0, 0, 1), (0, 1, 0)),
    'end':  make_view((1, 0, 0), (0, 0, 1)),    # viewer at the front looking back
    'iso':  make_view((1, -1.0, 0.85), (0, 0, 1)),
}

def project(shape, view):
    """Return (visible edges, hidden edges) as lists of 2D polylines (model mm in view coords) via TechDraw HLR."""
    v = VIEWS[view]
    M = Matrix(v['r'][0], v['r'][1], v['r'][2], 0, v['u'][0], v['u'][1], v['u'][2], 0, v['n'][0], v['n'][1], v['n'][2], 0, 0, 0, 0, 1)
    sh = shape.copy()
    sh.transformShape(M)
    res = TechDraw.projectEx(sh, V(0, 0, 1))
    vis = [e for i in (0, 1, 3) for e in res[i].Edges]
    hid = [e for i in (5, 6, 8) for e in res[i].Edges]
    return vis, hid

def polylines(edges, defl):
    out = []
    for e in edges:
        try:
            pts = e.discretize(Deflection=defl)
        except Exception:
            try:
                pts = [e.Vertexes[0].Point, e.Vertexes[-1].Point]
            except Exception:
                continue
        out.append([(p.x, p.y) for p in pts])
    return out

def extents(polys):
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    return min(xs), max(xs), min(ys), max(ys)

# --------------------------------------------------------------------------- derived geometry
def derive_lid_and_tub(case):
    big = 5000
    top = Part.makeBox(big, big, 100, V(-1000, -2500, LID_Z))
    bot = Part.makeBox(big, big, 1000, V(-1000, -2500, LID_Z - 1000))
    lid = case.common(top)
    tub = case.common(bot)
    return lid, tub

def derive_holder(doc):
    lane = doc.getObject('Cell_lane_1').Shape
    cs = [(s.CenterOfMass.x, s.CenterOfMass.y, s.CenterOfMass.z) for s in lane.Solids]
    ymin = min(s.BoundBox.YMin for s in lane.Solids)
    ymax = max(s.BoundBox.YMax for s in lane.Solids)
    R_CELL = 10.8
    m = R_CELL + 2.6
    x0 = min(c[0] for c in cs) - m; x1 = max(c[0] for c in cs) + m
    z0 = min(c[2] for c in cs) - m; z1 = max(c[2] for c in cs) + m
    t = 2.5
    plates = []
    for y in (ymin - t, ymax):
        p = Part.makeBox(x1 - x0, t, z1 - z0, V(x0, y, z0))
        holes = Part.makeCompound([Part.makeCylinder(9.5, t + 2, V(c[0], y - 1, c[2]), V(0, 1, 0)) for c in cs])
        plates.append(p.cut(holes))
    holder = Part.makeCompound(plates)
    cells = [(c[0], c[2]) for c in cs]
    return holder, dict(x0=x0, x1=x1, z0=z0, z1=z1, ymin=ymin - t, ymax=ymax + t, n=len(cs), cells=cells, r=R_CELL, ap=9.5)

# --------------------------------------------------------------------------- circle features
def find_circles(shape, dia, view, tol=0.2):
    """Circular edges of diameter dia whose axis is along the view normal; returns [(cx, cy, r)] in view model-mm coords."""
    v = VIEWS[view]
    out = []
    seen = set()
    for e in shape.Edges:
        try:
            cv = e.Curve
        except Exception:
            continue
        if not isinstance(cv, Part.Circle):
            continue
        if abs(2 * cv.Radius - dia) > tol:
            continue
        ax = (cv.Axis.x, cv.Axis.y, cv.Axis.z)
        if abs(dot(ax, v['n'])) < 0.99:
            continue
        c = (cv.Center.x, cv.Center.y, cv.Center.z)
        key = (round(dot(c, v['r']), 1), round(dot(c, v['u']), 1))
        if key in seen:
            continue
        seen.add(key)
        out.append((key[0], key[1], cv.Radius))
    return out

# --------------------------------------------------------------------------- sheet definitions
COMMON_LACKS = ('NOT DETAILED: no GD&T / datum scheme, no weld symbols or weld sizes, no surface-finish or coating call-outs, '
                'no thread / fit / tolerance call-outs beyond ISO 2768-m, no section views, no manufacturing draft or edge radii, '
                'no inspection plan. Dimensions are overall CAD envelopes (measured from the solid).')

SHEET_INFO = {
    'BV-ASM-0201': dict(
        name='frame-welded-assembly',
        material='25CrMo4 (4130-class) seamless steel tube; cast steel nodes (grade not selected)',
        process='TIG-welded tube frame; cast / forged nodes at the yoke tops (3 mm shells in CAD)',
        features=['Rail 0: 38 x 2.0 tube (from the yoke top)  |  Rail 1: 38 x 2.25  |  Rail 2: 42 x 3.5',
                  'Down-link 38 x 4.0  |  rear pack link 42 x 4.25  |  tail rail 30 x 2.0  |  posts 27 x 2.0',
                  'Head tube: OD 56 / ID 49 (measured in CAD), steering axis tilted',
                  'Shock top plates 14 x 40; swingarm pivot nodes at X540, Z403 (saved-model coords, Z lift +53.1)',
                  'Pivot yoke shown grey for context (drawing BV-ASM-0202); pack case not shown'],
        hidden=False, dim_note='Overall = frame tubes only (yoke excluded).',
        lacks='Frame jig datums, tube cope/mitre details, lug plates (not modelled in CAD) and bosses are not drawn.'),
    'BV-ASM-0202': dict(
        name='pivot-yoke',
        material='25CrMo4 steel box sections, 70 x 70 blocks, 60 mm solid spindle',
        process='welded box sections, machined spindle (bearings 2 x 32012 X not drawn)',
        features=['Yoke legs 50 x 50 x 4.25 box, node (540, +-195, 403) up to (556, +-157.7, 598) saved-model coords',
                  'Cross-member 60 (Z) x 40 (X) x 5 box at Z598 (generator Z545), 51 mm above the motor housing',
                  'Pivot spindle: 60 mm solid steel, Y105 to Y185 (+Y side); left carrier stub 40 OD / 30 ID, Y-192 to -186',
                  'Pivot blocks 70 x 70, 3 mm wall; two 32012 X bearing seats on the spindle (Y105, Y185)',
                  'FEA ran the cross-member at Z525; CAD is Z545 (generator): load path re-check open'],
        hidden=False, dim_note='',
        lacks='Stub-to-yoke joint, lug plates and bearing retention are not designed (open DFMEA item D30).'),
    'BV-ASM-0203': dict(
        name='swingarm-cast-A356',
        material='cast A356-T6 aluminium box arm (4.0 mm wall per FEA), 7xxx/6xxx tower plate and brace tube',
        process='low-pressure / gravity cast arm, machined bores; tower and brace fabricated',
        features=['Pivot boss OD 112, bore Ø95 (two 32012 X bearings), axis X540 Z403 (saved-model coords)',
                  'Boss spans Y105 to Y185; single-sided arm, inner face at Y110 at the axle end',
                  'Cross brace Ø75 x 6.0 tube (Ø63 bore), tower with Ø66 shock eye bores',
                  'CAD arm is a filled envelope; ledger mass uses a 4.0 mm shell rule (2.278 kg)'],
        hidden=True, dim_note='',
        lacks='Axle bore and adjuster, casting draft, ribs, wall-thickness map and machining allowances are not drawn.'),
    'BV-ENG-0001': dict(
        name='pack-case-tub',
        material='aluminium sheet (alloy not selected): 3 mm walls, 5 mm front wall, 3 mm floor ribs, 4 mm doubler pads',
        process='folded / welded sheet fabrication; four floor burst-vent ports',
        features=['Walls 3 mm; FRONT WALL 5 mm; three 3 mm floor ribs in the lane gaps; four 4 mm lug doubler pads',
                  'Four floor vent ports Ø28 (615 mm2 each), one per cell lane (axis Z)',
                  'Front corner R15 outside / R12 inside; cavity holds 1,100 cells in 4 lanes',
                  'Tub = case solid below Z625.1; lid is BV-ENG-0101 (split for drawing only)'],
        hidden=True, dim_note='',
        lacks='Weld seams, flange / seal groove, bolt pattern, bosses for BMS and mounts, and crush-structure details are not drawn.'),
    'BV-ENG-0101': dict(
        name='pack-lid',
        material='aluminium sheet 3 mm (alloy not selected)',
        process='laser-cut sheet; bolted and gasketed to the tub flange',
        features=['3 mm plate, roof of the case solid (Z625.1 to 628.1 saved-model coords)',
                  'Plan outline follows the case (R15 front corners)',
                  'PROVISIONAL part number: the ledger carries lid and tub as one part (BV-ENG-0001)',
                  'Bolt pattern, seal groove, post-foot bosses and stiffeners are not designed'],
        hidden=False, dim_note='',
        lacks='Fastener pattern, gasket and flange are not modelled; the lid is the roof slab sliced out of the case solid.'),
    'BV-BOD-0004': dict(
        name='lower-body-panel',
        material='painted PP/ABS thermoformed or moulded panel (rev E report: 2 mm; ledger text says 3 mm)',
        process='injection / thermoformed shell, painted; no mounting tooling or draft study',
        features=['One continuous shell from the motor bay over the pack flank to the front-tyre arc',
                  'Plan half-width 217 mm (motor bay), 225 round the pivot node, easing to 180 at the nose (overall 450 wide)',
                  'Top sits 1.5 mm under the tank skirt; belly line rises into the pack chin',
                  'Open at front and rear; no fillets (R15 request did not build)'],
        hidden=False, dim_note='',
        lacks='Wall thickness map, ribs, bosses, draft, parting lines and fastener positions are not drawn.'),
    'BV-DRV-0006': dict(
        name='rear-pulley-hub',
        material='aluminium (7075/6082 class), anodised dark',
        process='CNC machined, bolt-on flanges',
        features=['8M pitch, 126T, toothed face 68 mm wide (belt 62 mm), root OD 319.3',
                  'Flange OD Ø331.9 (bolt-on, +12 over teeth); eight Ø70.6 lightening holes',
                  'Central bore Ø40 (envelope; real hub / spline / bearing seat not designed)',
                  'CAD is a solid envelope (volume gives 9.1 kg in aluminium); ledger carries 2.1 kg for a webbed design',
                  'Ledger text says 80T 14 mm; CAD and drive report use 8 mm pitch 126T'],
        hidden=True, dim_note='',
        lacks='Tooth profile, hub, axle interface, web thickness, runout and balance are not drawn.'),
    'BV-DRV-0007': dict(
        name='motor-carrier',
        material='aluminium (7075/6082 class)',
        process='CNC machined bearing carrier on the motor flange',
        features=['OD Ø72, bore Ø44, length 114 (Y-174 to Y-60); axis X540 Z403 saved-model coords',
                  'Runs the pulley on its own two bearings so the EMRAX shaft bearings carry no belt pull',
                  'Spline to rotor, bearing seats, flange bolts (M8 x 6 on PCD 75 per EMRAX source) not drawn',
                  'The EMRAX 228 housing mounts and right stator plate are not modelled in CAD'],
        hidden=True, dim_note='',
        lacks='This is the only modelled motor-side mounting part; stator plate and motor mounts are not in the CAD at all.'),
    'BV-ENG-0102': dict(
        name='module-cell-holder',
        material='PA66-GF30 (flame-retardant), estimate',
        process='injection moulded; two end plates per module',
        features=['One 25s11p module = one cell lane: 275 cells Ø21.6 x 70.2, hex-packed in the X-Z plane',
                  'Two 2.5 mm plates, one at each cell end, 275 apertures Ø19 each; plate plan 514 x 374',
                  'Cells shown as thin grey circles / outlines (they are not part of this drawing mass)',
                  'CONCEPT GEOMETRY made for this drawing; not in CAD or the ledger'],
        hidden=False, dim_note='',
        lacks='Socket walls, snap features, busbar windows, tie rods and thermal ribbon routing are not designed; true mass is higher.'),
}

# --------------------------------------------------------------------------- page drawing
PAGE_W, PAGE_H = 420.0, 297.0
STRIP_TOP = 72.0
SCALES = [5, 2, 1, 1 / 1.5, 1 / 2, 1 / 2.5, 1 / 3, 1 / 4, 1 / 5, 1 / 10, 1 / 15, 1 / 20, 1 / 50]

def scale_label(s):
    if s >= 1:
        return '%.3g:1' % s if s != 1 else '1:1'
    return '1:%.3g' % (1 / s)

def fmt(v):
    return ('%.1f' % v).rstrip('0').rstrip('.') if abs(v - round(v)) > 0.05 else '%d' % round(v)

class Sheet:
    def __init__(self, pn, title, mass_kg, info, nsheet, total):
        self.pn, self.title, self.mass, self.info = pn, title, mass_kg, info
        self.n, self.total = nsheet, total
        self.fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, PAGE_W); self.ax.set_ylim(0, PAGE_H)
        self.ax.set_aspect('equal'); self.ax.axis('off')

    def line(self, x0, y0, x1, y1, lw=0.5, c='k', ls='-'):
        self.ax.plot([x0, x1], [y0, y1], color=c, lw=lw, ls=ls, solid_capstyle='butt')

    def text(self, x, y, s, size=7, ha='left', va='center', rot=0, weight='normal', c='k', style='normal', z=6):
        self.ax.text(x, y, s, zorder=z, fontsize=size, ha=ha, va=va, rotation=rot, fontweight=weight, color=c, fontstyle=style, family='DejaVu Sans')

    def draw_edges(self, polys, ox, oy, s, lw, c='k', ls='-', alpha=1.0):
        segs = [[(ox + p[0] * s, oy + p[1] * s) for p in pl] for pl in polys if len(pl) > 1]
        if segs:
            self.ax.add_collection(LineCollection(segs, colors=c, linewidths=lw, linestyles=ls, alpha=alpha))

    def hdim(self, x0, x1, y, yref, val, off=8, label=None):
        """horizontal dimension between paper x0,x1 placed at paper y; extension lines from yref."""
        d = -1 if y < yref else 1
        for x in (x0, x1):
            self.line(x, yref + d * 1.5, x, y + d * 1.5, 0.25)
        self.ax.annotate('', xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle='<|-|>', lw=0.4, color='k', mutation_scale=6, shrinkA=0, shrinkB=0))
        self.text((x0 + x1) / 2, y + 2.2 * (1 if y >= yref else 1), label or fmt(val), size=6.5, ha='center')

    def vdim(self, y0, y1, x, xref, val, label=None):
        d = -1 if x < xref else 1
        for y in (y0, y1):
            self.line(xref + d * 1.5, y, x + d * 1.5, y, 0.25)
        self.ax.annotate('', xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle='<|-|>', lw=0.4, color='k', mutation_scale=6, shrinkA=0, shrinkB=0))
        self.text(x - 2.0 * (1 if x >= xref else 1), (y0 + y1) / 2, label or fmt(val), size=6.5, ha='center', rot=90)

    def leader(self, tip, textpos, s, ha='left'):
        self.ax.annotate('', xy=tip, xytext=textpos, arrowprops=dict(arrowstyle='-|>', lw=0.4, color='k', mutation_scale=5, shrinkA=0, shrinkB=0))
        self.text(textpos[0], textpos[1], s, size=6.5, ha=ha, va='center')

    def view_label(self, x, y, s):
        self.text(x, y, s, size=7, weight='bold', ha='left')

    # ---- frame, notes, title block
    def furniture(self, scale_txt, iso_txt):
        a = self.ax
        a.add_patch(Rectangle((7, 7), PAGE_W - 14, PAGE_H - 14, fill=False, lw=1.0, ec='k'))
        a.add_patch(Rectangle((10, 10), PAGE_W - 20, PAGE_H - 20, fill=False, lw=0.4, ec='k'))
        top = STRIP_TOP
        self.line(10, top, PAGE_W - 10, top, 0.8)
        nx0, nx1 = 10, 212
        self.line(nx1, 10, nx1, top, 0.8)
        y = top - 4.5
        self.text(nx0 + 3, y, 'CONCEPT-LEVEL DRAWING — NOT FOR MANUFACTURE', size=8.5, weight='bold', c='#a00000')
        y -= 5.2
        self.text(nx0 + 3, y, 'General tolerances ISO 2768-m (linear and angular). Break sharp edges. Units mm. Third-angle: A seen from vehicle -Y (front right), B above, C from the front.', size=6.2)
        y -= 4.6
        self.text(nx0 + 3, y, 'KEY FEATURES AND NOTES', size=5.6, weight='bold', c='#555555')
        y -= 3.9
        for line in self.info['features']:
            for k, chunk in enumerate(wrap(line, 118)):
                self.text(nx0 + 3 + (3 if k else 0), y, chunk, size=5.9)
                y -= 3.45
        y -= 1.2
        for chunk in wrap(COMMON_LACKS + ' ' + self.info.get('lacks', ''), 128):
            self.text(nx0 + 3, y, chunk, size=5.3, c='#444444', style='italic')
            y -= 3.0
        tx0, tx1 = 212, PAGE_W - 10
        r1, r2, r3, r4 = top - 10, top - 21, top - 34, top - 44
        for yy in (r1, r2, r3, r4):
            self.line(tx0, yy, tx1, yy, 0.5)
        self.text(tx0 + 3, top - 5, 'BAVUSO MOTORS', size=11, weight='bold')
        self.text(tx1 - 3, top - 5, 'V1.0 Adventure   rev E', size=8, ha='right')
        self.text(tx0 + 3, top - 15.5, self.title.upper(), size=9, weight='bold')
        mid = tx0 + 70
        self.line(mid, r2, mid, r4, 0.4)
        self.text(tx0 + 3, r2 - 3.2, 'PART NO. (DRAWING NO.)', size=5, c='#555555')
        self.text(tx0 + 3, r2 - 8.5, self.pn, size=10.5, weight='bold')
        self.text(mid + 3, r2 - 3.2, 'MATERIAL / PROCESS', size=5, c='#555555')
        mp = wrap(self.info['material'] + '; ' + self.info['process'], 64)[:3]
        for k, ln in enumerate(mp):
            self.text(mid + 3, r2 - 6.4 - 3.2 * k, ln, size=5.5)
        cols = [tx0, tx0 + 36, tx0 + 66, tx0 + 98, tx0 + 148, tx1]
        for cx in cols[1:-1]:
            self.line(cx, r3, cx, r4, 0.4)
        labels = [('MASS (ledger)', ('%.3f kg' % self.mass) if self.mass is not None else 'n/a'),
                  ('SCALE', scale_txt), ('UNITS', 'mm'), ('DATE / REV', TODAY + '  /  E'), ('SHEET', '%d of %d' % (self.n, self.total))]
        for i, (k, v) in enumerate(labels):
            self.text(cols[i] + 2.5, r3 - 3.0, k, size=5, c='#555555')
            self.text(cols[i] + 2.5, r3 - 7.4, v, size=8, weight='bold')
        self.text(tx0 + 3, r4 - 3.2, 'THIRD-ANGLE', size=5.2, c='#555555')
        proj_symbol(self.ax, tx0 + 17, r4 - 10.5)
        self.text(tx0 + 40, r4 - 3.2, 'ISO 2768-m  |  ' + iso_txt + '  |  mass per parts-ledger.csv (see doc 18)', size=6.0)
        self.text(tx0 + 40, r4 - 7.4, 'Status: CONCEPT, unreleased. Geometry: rev E (cad/Bavuso-V1.0-adventure.FCStd).', size=5.6)
        self.text(tx0 + 40, r4 - 11.2, 'Drawn by Claude Sonnet 5.5 (claude-sonnet-5-5) from the CAD solids; not checked by a drafter.', size=5.6)
        self.text(tx0 + 40, r4 - 14.8, 'Dimensions are overall CAD envelopes; hidden lines ' + ('shown dashed.' if self.info['hidden'] else 'not shown.'), size=5.6)

def wrap(s, n):
    words, out, cur = s.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        out.append(cur)
    return out

def proj_symbol(ax, cx, cy):
    # third-angle: end view (two concentric circles) on the left, front view (frustum) on the right
    ax.add_patch(MCircle((cx - 6.5, cy), 3.6, fill=False, lw=0.5))
    ax.add_patch(MCircle((cx - 6.5, cy), 2.0, fill=False, lw=0.5))
    ax.plot([cx - 1.0, cx - 1.0], [cy - 3.6, cy + 3.6], lw=0.0)
    ax.add_patch(Polygon([(cx, cy - 3.6), (cx, cy + 3.6), (cx + 9, cy + 2.0), (cx + 9, cy - 2.0)], closed=True, fill=False, lw=0.5))
    ax.plot([cx - 8.5, cx + 11], [cy, cy], lw=0.3, ls='-.', color='k')

# --------------------------------------------------------------------------- build one sheet
def layout(ext, iso_ext):
    """Pick the largest scale s that fits; return s and the view placement (paper mm, lower-left of each view)."""
    Xe, Ye, Ze = ext
    zx0, zx1, zy0, zy1 = 14.0, 406.0, 80.0, 284.0
    gap = 26.0
    for s in SCALES:
        pw, ph, th, ew = Xe * s, Ze * s, Ye * s, Ye * s
        px, py = zx0 + 22, zy0 + 17
        tx, ty = px, py + ph + gap
        ex, ey = px + pw + gap, py
        if ty + th > zy1 - 2 or ex + ew > zx1 - 14:
            continue
        iso_x0 = ex + ew + 26
        if zx1 - iso_x0 >= 70:
            iso_y0, iw, ih = zy0 + 4, zx1 - iso_x0 - 4, zy1 - zy0 - 8
        else:
            iso_x0, iso_y0 = px + pw + gap * 0.8, ey + ph + gap * 0.6
            iw, ih = zx1 - iso_x0 - 6, zy1 - iso_y0
        if iw < 55 or ih < 45:
            continue
        return s, dict(primary=(px, py), top=(tx, ty), end=(ex, ey), iso_box=(iso_x0, iso_y0, iw, ih), pw=pw, ph=ph, th=th, ew=ew)
    raise RuntimeError('no scale fits')

def build_sheet(pn, title, main, context, info, mass, ann, nsheet, total, extra_ghost=None):
    t0 = time.time()
    out = {}
    for vk in ('left', 'top', 'end', 'iso'):
        vis, hid = project(main, vk)
        out[vk] = dict(vis=vis, hid=hid)
        if context is not None:
            cvis, _ = project(context, vk)
            out[vk]['ctx'] = cvis
    # first-pass polylines for extents (coarse)
    def exact_bb(edges):
        b = Part.makeCompound(edges).optimalBoundingBox(False, False)
        return (b.XMin, b.XMax, b.YMin, b.YMax)
    bb = {vk: exact_bb(out[vk]['vis']) for vk in out}
    Xe = bb['left'][1] - bb['left'][0]; Ze = bb['left'][3] - bb['left'][2]
    Ye = bb['top'][3] - bb['top'][2]
    isoe = (bb['iso'][1] - bb['iso'][0], bb['iso'][3] - bb['iso'][2])
    s, L = layout((Xe, Ye, Ze), isoe)
    defl = 0.15 / s
    sh = Sheet(pn, title, mass, info, nsheet, total)
    hidden = info['hidden']

    place = {}
    for vk in ('left', 'top', 'end'):
        ox0, oy0 = {'left': L['primary'], 'top': L['top'], 'end': L['end']}[vk]
        b = bb[vk]
        place[vk] = (ox0 - b[0] * s, oy0 - b[2] * s, b)
    # iso: own scale in the free box
    ix0, iy0, iw, ih = L['iso_box']
    siso = min(iw / isoe[0], ih / isoe[1]) * 0.86
    siso = min(siso, s * 1.6)
    bi = bb['iso']
    isox = ix0 + (iw - isoe[0] * siso) / 2 - bi[0] * siso
    isoy = iy0 + (ih - isoe[1] * siso) / 2 - bi[2] * siso
    place['iso'] = (isox, isoy, bi)

    for vk in ('left', 'top', 'end', 'iso'):
        ox, oy, b = place[vk]
        sc = siso if vk == 'iso' else s
        d = 0.15 / sc
        if 'ctx' in out[vk]:
            sh.draw_edges(polylines(out[vk]['ctx'], d * 2), ox, oy, sc, 0.2, c='#9a9a9a')
        if hidden and vk != 'iso':
            sh.draw_edges(polylines(out[vk]['hid'], d * 2), ox, oy, sc, 0.18, c='#777777', ls=(0, (3, 2)))
        sh.draw_edges(polylines(out[vk]['vis'], d), ox, oy, sc, 0.45 if vk != 'iso' else 0.35)
    if extra_ghost:
        extra_ghost(sh, place, s)

    # dimensions
    pxl, pyl = L['primary']; pw, ph = L['pw'], L['ph']
    sh.hdim(pxl, pxl + pw, pyl - 9, pyl, Xe)
    sh.vdim(pyl, pyl + ph, pxl - 9, pxl, Ze)
    tx0, ty0 = L['top']
    sh.vdim(ty0, ty0 + L['th'], tx0 - 9, tx0, Ye)
    ex0, ey0 = L['end']
    sh.hdim(ex0, ex0 + L['ew'], ey0 - 9, ey0, Ye)
    sh.vdim(ey0, ey0 + ph, ex0 + L['ew'] + 9, ex0 + L['ew'], Ze)
    sh.view_label(pxl, pyl - 17.5, 'VIEW A: SIDE (-Y)')
    sh.view_label(tx0, ty0 + L['th'] + 4.5, 'VIEW B: TOP')
    sh.view_label(ex0, ey0 - 17.5, 'VIEW C: FRONT')
    sh.view_label(ix0 + 2, min(isoy + bi[3] * siso + 7, 281), 'ISO VIEW (front-left-above), scale ' + scale_label(siso))

    # key-feature balloons: numbered circle on a short leader; the text goes in the notes block
    nb = 0
    notes = []
    for a in ann:
        vk = a['view']
        ox, oy, b = place[vk]
        circles = find_circles(a['shape'], a['dia'], vk)
        if not circles:
            print('  (no circle found for', a['text'], ')')
            continue
        nb += 1
        pick = circles[a.get('pick', 0) % len(circles)]
        ang = math.radians(a.get('ang', 40))
        tip = (ox + (pick[0] + pick[2] * math.cos(ang)) * s, oy + (pick[1] + pick[2] * math.sin(ang)) * s)
        bx, by = tip[0] + 9 * math.cos(ang), tip[1] + 9 * math.sin(ang)
        sh.ax.annotate('', xy=tip, xytext=(bx, by), arrowprops=dict(arrowstyle='-|>', lw=0.4, color='k', mutation_scale=5, shrinkA=0, shrinkB=0))
        sh.ax.add_patch(MCircle((bx, by), 2.6, fill=True, fc='white', ec='k', lw=0.5, zorder=5))
        sh.text(bx, by, str(nb), size=6.5, ha='center', weight='bold')
        notes.append('(%d) %s' % (nb, a['text']))
    sh.info = dict(sh.info)
    sh.info['features'] = list(sh.info['features']) + notes

    sh.furniture(scale_label(s), 'ISO view ' + scale_label(siso))
    ex = dict(Xe=Xe, Ye=Ye, Ze=Ze, scale=scale_label(s), iso_scale=scale_label(siso), secs=round(time.time() - t0))
    return sh, ex

# --------------------------------------------------------------------------- main
def main():
    only = None
    for i, a in enumerate(sys.argv):
        if a == '--only':
            only = set(sys.argv[i + 1].split(','))
    t0 = time.time()
    doc = FreeCAD.openDocument(FCSTD)
    print('model opened', round(time.time() - t0), 's', flush=True)
    G = lambda n: doc.getObject(n).Shape

    # ---- derived parts
    case = G('Pack_case_structural_4mm_STUDY')
    lid, tub = derive_lid_and_tub(case)
    lid_mass = lid.Volume * 2.70e-6
    holder, hinfo = derive_holder(doc)
    holder_mass = holder.Volume * 1.35e-6 / 2.0   # per plate? holder.Volume is both plates: one module = 2 plates
    holder_mass = holder.Volume * 1.35e-6
    derived = {'BV-ENG-0101': dict(mass_kg=round(lid_mass, 4), volume_mm3=round(lid.Volume), density_g_cm3=2.70),
               'BV-ENG-0102': dict(mass_kg=round(holder_mass, 4), volume_mm3=round(holder.Volume), density_g_cm3=1.35,
                                   note='per module, plates only, concept geometry; NOT counted in the ledger total')}
    json.dump(derived, open(os.path.join(DATADIR, 'drawings-derived.json'), 'w'), indent=1)
    print('derived', derived, flush=True)

    bom_rows, rec = bom.build(lid_mass, holder_mass)
    mass_of = {r['part_number']: float(r['mass_ext_kg'] or 0) for r in bom_rows if r['mass_ext_kg'] != ''}

    def solids_of(asm_key):
        names = []
        import csv
        for r in bom.load_ledger():
            sk, ak = bom.assign(r)
            if ak == asm_key and r['cad_solid'] and doc.getObject(r['cad_solid']) and doc.getObject(r['cad_solid']).Shape.Solids:
                names.append(r['cad_solid'])
        return names

    frame_names = solids_of('frame')
    yoke_names = solids_of('yoke')
    arm_names = solids_of('swingarm')
    print('frame', len(frame_names), 'yoke', len(yoke_names), 'arm', len(arm_names), flush=True)
    comp = lambda names: Part.makeCompound([G(n) for n in names])

    sheets = []   # (pn, title, shape, ctx, ann, ghost)
    sheets.append(('BV-ASM-0201', bom.SHEETS['BV-ASM-0201']['title'], comp(frame_names), comp(yoke_names), []))
    sheets.append(('BV-ASM-0202', bom.SHEETS['BV-ASM-0202']['title'], comp(yoke_names), None, [
        dict(shape=G('Independent_hollow_pivot_stub_1'), dia=60, view='left', text='Spindle Ø60 solid steel', dx=24, dy=34, ang=50),
        dict(shape=G('Independent_hollow_pivot_stub_m1'), dia=40, view='left', text='Left carrier stub OD Ø40 / ID Ø30', dx=-30, dy=-30, ang=215)]))
    sw = comp(arm_names)
    sheets.append(('BV-ASM-0203', bom.SHEETS['BV-ASM-0203']['title'], sw, None, [
        dict(shape=G('Swingarm_1'), dia=95, view='left', text='Pivot bore Ø95 (2 x 32012 X)', dx=-30, dy=48, ang=135),
        dict(shape=G('Swingarm_1'), dia=112, view='left', text='Boss OD Ø112', dx=40, dy=-44, ang=-45, pick=0),
        dict(shape=G('Swingarm_shock_tower'), dia=66, view='left', text='Shock eye bores Ø66 (tower)', ang=100),
        dict(shape=G('Swingarm_cross_brace'), dia=75, view='left', text='Cross brace Ø75 x 6.0 (bore Ø63)', ang=-70)]))
    sheets.append(('BV-ENG-0001', bom.SHEETS['BV-ENG-0001']['title'], tub, None, [
        dict(shape=case, dia=28, view='top', text='4 x Ø28 floor burst vents (one per lane)', dx=28, dy=-18, ang=30)]))
    sheets.append(('BV-ENG-0101', bom.SHEETS['BV-ENG-0101']['title'], lid, None, []))
    sheets.append(('BV-BOD-0004', bom.SHEETS['BV-BOD-0004']['title'], G('Lower_body_battery_covers_STUDY'), None, []))
    pul = G('Rear_pulley_PITCH_STUDY')
    sheets.append(('BV-DRV-0006', bom.SHEETS['BV-DRV-0006']['title'], pul, None, [
        dict(shape=pul, dia=40, view='left', text='Centre bore Ø40', dx=30, dy=36, ang=60),
        dict(shape=pul, dia=70.6, view='left', text='8 x Ø70.6 lightening holes', dx=36, dy=-26, ang=-30),
        dict(shape=pul, dia=331.9, view='left', text='Flange OD Ø331.9', dx=-36, dy=24, ang=150),
        dict(shape=pul, dia=319.3, view='left', text='Toothed root Ø319.3', dx=-36, dy=-26, ang=-150)]))
    car = G('Motor_pulley_bearing_carrier')
    sheets.append(('BV-DRV-0007', bom.SHEETS['BV-DRV-0007']['title'], car, None, [
        dict(shape=car, dia=72, view='left', text='OD Ø72', dx=24, dy=22, ang=45),
        dict(shape=car, dia=44, view='left', text='Bore Ø44', dx=-26, dy=-24, ang=-135)]))
    sheets.append(('BV-ENG-0102', bom.SHEETS['BV-ENG-0102']['title'], holder, None, [
        dict(shape=holder, dia=19, view='left', text='275 apertures Ø19 per plate', dx=34, dy=22, ang=45)]))

    def holder_ghost(sh, place, s):
        # thin grey cell outlines in the side view (cells are not part of the holder)
        ox, oy, b = place['left']
        for (cx, cz) in hinfo['cells']:
            sh.ax.add_patch(MCircle((ox + cx * s, oy + cz * s), hinfo['r'] * s, fill=False, lw=0.12, ec='#b0b0b0'))

    total = len(sheets)
    figs = {}
    meta = {}
    pack_path = os.path.join(OUTDIR, 'V1-drawing-pack.pdf')
    for i, (pn, title, shape, ctx, ann) in enumerate(sheets, 1):
        if only and pn not in only:
            continue
        info = dict(SHEET_INFO[pn])
        asm = bom.SHEETS[pn].get('asm')
        if asm:
            alw = 0.0
            for r in bom.load_ledger():
                if bom.assign(r)[1] == asm and not r['cad_solid']:
                    alw += float(r['mass_kg'] or 0)
            if alw > 0:
                info['features'] = list(info['features']) + ['Mass includes %.2f kg of ledger allowances that are not drawn (no CAD solid)' % alw]
        if asm:
            apn = bom.ASM[asm][0]
            mass = mass_of.get(apn)
        else:
            mass = mass_of.get(pn)
        if pn == 'BV-ENG-0102':
            mass = holder_mass
        print('sheet', i, pn, 'mass', mass, flush=True)
        ghost = holder_ghost if pn == 'BV-ENG-0102' else None
        sh, ex = build_sheet(pn, title, shape, ctx, info, mass, ann, i, total, ghost)
        # holder mass is the concept estimate, label it
        fname = '%s_%s.pdf' % (pn, info['name'])
        sh.fig.savefig(os.path.join(OUTDIR, fname), format='pdf')
        if os.environ.get('DRAW_PNG'):
            sh.fig.savefig(os.path.join(os.environ['DRAW_PNG'], pn + '.png'), dpi=90)
        figs[pn] = sh.fig
        ex.update(file=fname, mass_kg=mass)
        meta[pn] = ex
        print('  done', ex, flush=True)
    # combined pack: index page + all sheets in order (re-render from saved figures)
    if not only:
        with PdfPages(pack_path) as pdf:
            idx = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
            a = idx.add_axes([0, 0, 1, 1]); a.set_xlim(0, PAGE_W); a.set_ylim(0, PAGE_H); a.axis('off')
            a.text(20, 270, 'BAVUSO MOTORS  -  V1.0 Adventure  -  CONCEPT DRAWING PACK, REV E', fontsize=18, weight='bold')
            a.text(20, 258, TODAY + '.  Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.', fontsize=10)
            a.text(20, 248, 'CONCEPT-LEVEL DRAWINGS - NOT FOR MANUFACTURE.  Third-angle projection, millimetres, general tolerances ISO 2768-m.', fontsize=10, color='#a00000', weight='bold')
            y = 232
            a.text(20, y, 'Sheet   Part number     Title', fontsize=10, weight='bold', family='DejaVu Sans Mono')
            a.text(300, y, 'Scale', fontsize=10, weight='bold'); a.text(340, y, 'Mass (kg)', fontsize=10, weight='bold')
            for i, (pn, title, *_r) in enumerate(sheets, 1):
                y -= 9
                m = meta[pn]
                a.text(20, y, '%-7d %-14s %s' % (i, pn, title), fontsize=10, family='DejaVu Sans Mono')
                a.text(300, y, m['scale'], fontsize=10); a.text(340, y, ('%.3f' % m['mass_kg']) if m['mass_kg'] is not None else '-', fontsize=10)
            y -= 16
            for line in wrap('What these drawings are: three orthographic views plus an iso of each main made part, drawn from the rev E CAD solids with '
                             'hidden-line removal, with overall dimensions, key bores known from the reports, material, process and ledger mass. '
                             'What they are not: no GD&T, no weld symbols, no surface finish, no threads or fits, no section views, no draft or edge radii. '
                             + 'The pack lid (BV-ENG-0101) and the module cell holder (BV-ENG-0102) are derived concept geometry with provisional '
                             'part numbers; the CAD has no motor mount, lid or holder solid.', 150):
                a.text(20, y, line, fontsize=9); y -= 6
            pdf.savefig(idx); plt.close(idx)
            for pn, *_ in sheets:
                pdf.savefig(figs[pn])
    json.dump(meta, open(os.path.join(DATADIR, 'drawings-meta.json'), 'w'), indent=1)
    # regenerate the BOM with the lid / holder numbers
    if not only:
        bom.main()
    print('ALL DONE', round(time.time() - t0), 's', flush=True)


if __name__ == '__main__':
    main()
