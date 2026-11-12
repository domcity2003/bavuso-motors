"""Export the outside of the integrated model, plus a seated rider, as STL surfaces for OpenFOAM.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/export-cfd-geometry.py
Writes cfd/geometry/{bike,rider,wheel_front,wheel_rear}.stl in metres (X forward, Y left, Z up).

What is simplified, and why:
- Cells are left out (hidden inside the pack case).
- Supplier STEP parts (EMRAX, CM200, BMS) have thousands of faces and some inward-facing shells.
  They sit inside the bodywork, so each is replaced by a plain box or cylinder of the same size.
- The rider is a 50th-percentile male buck in the upright naked-bike posture, built from capsules
  and ellipsoids anchored to the seat, grip and peg reference points.
- Each wheel (tyre, rim, discs, carriers) is its own surface so the solver can spin it.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]/'.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin'))
import FreeCAD as A, Part
V=A.Vector
R=Path(__file__).resolve().parents[1]
D=A.openDocument(str(R/'cad/Bavuso-V1.0-integrated.FCStd'))
OUT=R/'cfd/geometry';OUT.mkdir(parents=True,exist_ok=True)

def box_of(s):
    b=s.BoundBox;return Part.makeBox(b.XLength,b.YLength,b.ZLength,V(b.XMin,b.YMin,b.ZMin))

def capsule(a,b,r):
    a,b=V(*a),V(*b)
    return Part.makeCylinder(r,(b-a).Length,a,b-a).fuse([Part.makeSphere(r,a),Part.makeSphere(r,b)])

def ellipsoid(c,ax,ay,az,tilt=0):
    """Ellipsoid centred at c with semi-axes ax, ay, az; tilt (deg) leans its Z axis forward about Y."""
    m=A.Matrix();m.scale(ax,ay,az)
    s=Part.makeSphere(1).transformGeometry(m)
    s.rotate(V(0,0,0),V(0,1,0),tilt);s.translate(V(*c));return s

def rider():
    """Seated rider: hip on the seat (486,0,800), hands on the grips (880,+-350,1045), balls of the feet on the pegs (500,+-190..305,380)."""
    parts=[ellipsoid((470,0,905),130,170,110),            # pelvis
           ellipsoid((565,0,1150),120,190,275,20.3),      # torso, 20 deg forward lean
           capsule((662,0,1385),(690,0,1480),55),          # neck
           ellipsoid((700,0,1585),170,135,150)]            # helmet
    for s in (1,-1):
        sh,el,gr=(640,s*185,1360),(720,s*265,1160),(875,s*330,1045)
        hip,kn,an,toe=(480,s*105,890),(790,s*215,760),(480,s*222,440),(600,s*226,392)
        parts+=[capsule(sh,el,50),capsule(el,gr,42),Part.makeSphere(50,V(*gr)),
                capsule(hip,kn,80),capsule(kn,an,55),capsule(an,toe,45)]
    return parts

def stl(name,shapes,tol=0.5):
    """ASCII STL in metres, one solid per file (the solid name becomes the OpenFOAM patch name)."""
    n=0
    with (OUT/f'{name}.stl').open('w') as f:
        f.write(f'solid {name}\n')
        for s in shapes:
            pts,tris=s.tessellate(tol)
            for i,j,k in tris:
                a,b,c=pts[i],pts[j],pts[k];nv=(b-a).cross(c-a)
                if nv.Length<1e-12:continue
                nv.normalize()
                f.write(f' facet normal {nv.x:.5f} {nv.y:.5f} {nv.z:.5f}\n  outer loop\n')
                for p in (a,b,c):f.write(f'   vertex {p.x/1000:.6f} {p.y/1000:.6f} {p.z/1000:.6f}\n')
                f.write('  endloop\n endfacet\n');n+=1
        f.write(f'endsolid {name}\n')
    print(f'{name}: {len(shapes)} shapes, {n} triangles',flush=True)

groups={k:[] for k in ('bike','wheel_front','wheel_rear')}
for g in ('Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy'):
    for o in D.getObject(g).Group:
        n=o.Name
        if n.startswith('Cell_column') or not hasattr(o,'Shape') or o.Shape.isNull():continue
        s=o.Shape
        if 'supplier_STEP' in n:
            if 'EMRAX' in n:   # 208 mm disc motor on a Y axis
                b=s.BoundBox;c=V(b.Center.x,b.YMin,b.Center.z)
                s=Part.makeCylinder(min(b.XLength,b.ZLength)/2,b.YLength,c,V(0,1,0))
            else:s=box_of(s)
        if n.startswith('Rear_') and any(k in n for k in ('tire','wheel','disc')):groups['wheel_rear'].append(s)
        elif n.startswith('Front_') and any(k in n for k in ('tire','wheel','disc')):groups['wheel_front'].append(s)
        else:groups['bike'].append(s)
for k,v in groups.items():stl(k,v)
stl('rider',rider())
