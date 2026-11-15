"""Export the CURRENT adventure model plus a seated 50th-percentile rider as STL surfaces for OpenFOAM.

Run from v1.0:
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/aero-export-geometry.py [model.FCStd]
Default model: cad/Bavuso-V1.0-adventure.FCStd (a snapshot copy is read, so a parallel rebuild cannot tear it).
Writes detailed-design/aero/run/geometry/<patch>.stl (metres, X forward, Y left, Z up, ground at Z=0) and
detailed-design/aero/geometry-manifest.json (model hash, object->patch map, rider joints, frontal area).

Each patch is one STL file, so OpenFOAM reports the force on every part group separately:
  screen, mirrors, bars_controls, fairing_tank, fork_fender, lower_body, swingarm_pegs, seat_tail,
  rider_helmet, rider_torso_arms, rider_legs, wheel_front, wheel_rear.
Simplifications (same as the Nov 1 baseline): cells and keep-out volumes are left out; supplier STEP parts that sit
inside the body (CM200 inverter, Orion BMS) become boxes of the same size; the rider is a smooth buck.
Rider: 50th-percentile male (1,755 mm), joint positions from the comfort-study.md link model on the hard points
read from the model itself (seat sit point, grip centre, peg), i.e. the same posture the comfort study scored.
"""
import sys, json, math, shutil, hashlib, zipfile, time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]/'.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin'))
import FreeCAD as A, Part, Mesh, MeshPart
import numpy as np
V=A.Vector
R=Path(__file__).resolve().parents[2]                     # v1.0
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else R/'cad/Bavuso-V1.0-adventure.FCStd'
RUN=R/'detailed-design/aero/run';GEO=RUN/'geometry';GEO.mkdir(parents=True,exist_ok=True)
LIN,ANG=0.8,0.30                                         # tessellation: 0.8 mm chord error, 0.3 rad angle

# ---- snapshot the model (another agent may be rebuilding it): copy, then check the zip reads cleanly
snap=RUN/'model-snapshot.FCStd'
for k in range(10):
    shutil.copy2(SRC,snap)
    try:
        with zipfile.ZipFile(snap) as z:
            if z.testzip() is None:break
    except zipfile.BadZipFile:pass
    time.sleep(30)
else:sys.exit('model file kept changing / unreadable')
sha=hashlib.sha256(snap.read_bytes()).hexdigest()
D=A.openDocument(str(snap))

def patch_of(n):
    """object name -> patch name (first rule that matches)"""
    rules=[('wheel_front',('Front_nominal_tire','Front_wheel','Front_disc')),
           ('wheel_rear',('Rear_nominal_tire','Rear_wheel','Rear_disc','Rear_pulley')),
           ('screen',('Windscreen',)),
           ('mirrors',('Mirror_',)),
           ('bars_controls',('Bar_','Hand_','Lever_perch','Switch_cube','Front_master','Front_brake_reservoir','Harness_','Upper_triple')),
           ('fork_fender',('Fork_','Lower_triple','Front_fender','Front_caliper','Front_brake_hose','Front_brake_splitter')),
           ('fairing_tank',('Upper_body','Headlamp','Front_indicator','Display_','Side_grille','Side_radiator','Cascadia','Orion','BROGEN','Head_tube','Upper_rail_2')),
           ('seat_tail',('Seat_','Tail_','Rear_rack','Taillamp','Plate_','Licence','Rear_indicator','Shock_top_bracket','Rear_hugger')),
           ('swingarm_pegs',('Swingarm','Peg_','Drive_belt','Front_pulley','Rear_caliper','Rear_brake','Shock_','Independent_hollow','Pivot_6008')),
           ('lower_body',('Lower_body','Battery_side','Belly_','Panel_bolts','Seam_trim','Motor_side','Pivot_cover','Pack_case',
                          'IPM_motor','HV_cabinet','GX14','Upper_rail','Lower_downlink','Lower_pack','Tail_brace'))]
    for p,keys in rules:
        if any(n.startswith(k) for k in keys):return p
    return None

def box_of(s):
    b=s.BoundBox;return Part.makeBox(b.XLength,b.YLength,b.ZLength,V(b.XMin,b.YMin,b.ZMin))

shapes={};objmap={};unmatched=[]
for g in ('Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy'):
    for o in D.getObject(g).Group:
        n=o.Name
        if n.startswith('Cell_') or not hasattr(o,'Shape') or o.Shape.isNull():continue
        s=o.Shape
        if 'supplier_STEP' in n:s=box_of(s)                 # thousands of faces, hidden inside the tank
        p=patch_of(n)
        if p is None:p='lower_body';unmatched.append(n)
        shapes.setdefault(p,[]).append(s);objmap.setdefault(p,[]).append(n)

# ---- hard points from the model itself (ground at Z=0)
def bbc(name):return D.getObject(name).Shape.BoundBox.Center
grip=bbc('Hand_grip_reserve_1');peg=bbc('Peg_rubber_1')
seat=D.getObject('Seat_two_level_STUDY').Shape
# seat sit point: top of the seat at X486 on the centreline
ln=Part.makeLine(V(486,0,2000),V(486,0,0));seat_z=max(v.Point.z for v in seat.section(ln).Vertexes) if seat.section(ln).Vertexes else 850.0

# ---- rider: comfort-study link model (tools/comfort-study.py), 50th male
H=1755.0
def law(a,b,c):return math.degrees(math.acos(max(-1,min(1,(a*a+b*b-c*c)/(2*a*b)))))
hip=np.array([486,0.051*H,seat_z-25+90])
ank=np.array([peg.x-.073*H-15,262.0,peg.z+12+25+.039*H])
th,sk,trunk,ua,fa=.245*H,.246*H,.288*H,.186*H,.200*H
d=np.linalg.norm(ank-hip);u=(ank-hip)/d;al=math.radians(law(th,d,sk))
f=np.array([1,0,0.]);w=f-f.dot(u)*u;w/=np.linalg.norm(w)
knee=hip+th*(math.cos(al)*u+math.sin(al)*w)
G=np.array([grip.x,grip.y,grip.z])
for lean10 in range(0,401):
    t=math.radians(lean10/10);sh=np.array([hip[0]+trunk*math.sin(t),.130*H,hip[2]+trunk*math.cos(t)])
    if np.linalg.norm(sh-G)<=ua+fa-.02*H:break
lean=lean10/10
sh_c=np.array([sh[0],200.0,sh[2]])                        # shoulder joint inside the torso surface
dg=np.linalg.norm(G-sh_c);u2=(G-sh_c)/dg;a2=math.radians(law(ua,dg,fa))
wd=np.array([0,0.8,-0.8]);wd-=wd.dot(u2)*u2;wd/=np.linalg.norm(wd)  # elbow bends down and out
elbow=sh_c+ua*(math.cos(a2)*u2+math.sin(a2)*wd)
ball=np.array([peg.x,250.0,peg.z+13+12])                  # ball of the boot on the peg rubber
toe=ball+np.array([45,0,-5])

def capsule(a,b,r):
    a,b=V(*a),V(*b);return Part.makeCylinder(r,(b-a).Length,a,b-a).fuse([Part.makeSphere(r,a),Part.makeSphere(r,b)])
def ellipsoid(c,ax,ay,az,tilt=0):
    m=A.Matrix();m.scale(ax,ay,az);s=Part.makeSphere(1).transformGeometry(m)
    s.rotate(V(0,0,0),V(0,1,0),tilt);s.translate(V(*c));return s
def mir(p):return (p[0],-p[1],p[2])
hz=hip[2];shz=sh[2];tilt=lean
torso_c=((hip[0]+sh[0])/2+15,0,(hz+shz)/2+20)
helmet_c=(sh[0]+35+math.sin(math.radians(lean))*200,0,shz+225)
rider={'rider_helmet':[capsule((sh[0]+10,0,shz-10),(sh[0]+25,0,shz+90),58),ellipsoid(helmet_c,170,135,150)],
       'rider_torso_arms':[ellipsoid(torso_c,125,190,(shz-hz)/2+35,tilt)],
       'rider_legs':[ellipsoid((hip[0]-15,0,hz+40),130,170,110)]}
for s in (1,-1):
    S=lambda p:(p[0],s*p[1],p[2])
    rider['rider_torso_arms']+=[capsule(S(sh_c),S(elbow),50),capsule(S(elbow),S(G),42),Part.makeSphere(50,V(*S(G)))]
    rider['rider_legs']+=[capsule(S(hip),S(knee),80),capsule(S(knee),S(ank),55),capsule(S(ank),S(toe),45)]
for k,v in rider.items():shapes[k]=v;objmap[k]=['rider buck']

# ---- tessellate and write ASCII STL in metres (solid name = patch name)
tri_all={}
for name,lst in shapes.items():
    P=[];T=[];off=0
    for s in lst:
        m=MeshPart.meshFromShape(Shape=s,LinearDeflection=LIN,AngularDeflection=ANG,Relative=False)
        pts=np.array([[p.x,p.y,p.z] for p in m.Points]);fc=np.array([f.PointIndices for f in m.Facets],dtype=int)
        if len(fc)==0:continue
        P.append(pts);T.append(fc+off);off+=len(pts)
    P=np.vstack(P)/1000.0;T=np.vstack(T)
    a,b,c=P[T[:,0]],P[T[:,1]],P[T[:,2]];n=np.cross(b-a,c-a);L=np.linalg.norm(n,axis=1);ok=L>1e-14
    a,b,c,n=a[ok],b[ok],c[ok],n[ok]/L[ok,None]
    with (GEO/f'{name}.stl').open('w') as fh:
        fh.write(f'solid {name}\n')
        for i in range(len(a)):
            fh.write(' facet normal %.5f %.5f %.5f\n  outer loop\n   vertex %.6f %.6f %.6f\n   vertex %.6f %.6f %.6f\n   vertex %.6f %.6f %.6f\n  endloop\n endfacet\n'
                     %(n[i,0],n[i,1],n[i,2],a[i,0],a[i,1],a[i,2],b[i,0],b[i,1],b[i,2],c[i,0],c[i,1],c[i,2]))
        fh.write(f'endsolid {name}\n')
    tri_all[name]=(a,b,c);print(f'{name:18s}{len(lst):4d} shapes {len(a):8d} triangles',flush=True)

# ---- frontal area: rasterise every triangle projected on the Y-Z plane at 2 mm pixels
from PIL import Image, ImageDraw
px=0.002;W,Hh=int(1.2/px),int(2.0/px)
def frontal(names):
    im=Image.new('1',(W,Hh),0);dr=ImageDraw.Draw(im)
    for nm in names:
        a,b,c=tri_all[nm]
        for t in zip(a,b,c):dr.polygon([((p[1]+0.6)/px,(p[2])/px) for p in t],fill=1)
    return float(np.asarray(im).sum())*px*px
areas={'total':frontal(tri_all),'bike_only':frontal([k for k in tri_all if not k.startswith('rider')]),
       'rider_only':frontal([k for k in tri_all if k.startswith('rider')])}
allpts=np.vstack([np.vstack(v) for v in tri_all.values()])
man=dict(prepared='2026-11-12 US Central, Claude Opus 5.5 (claude-opus-5-5)',source=str(SRC.relative_to(R)) if SRC.is_relative_to(R) else str(SRC),
         source_sha256=sha,source_mtime=time.strftime('%Y-%m-%d %H:%M',time.localtime(SRC.stat().st_mtime)),
         tessellation_mm=dict(linear=LIN,angular_rad=ANG),
         patches={k:dict(objects=objmap[k],triangles=int(len(tri_all[k][0]))) for k in tri_all},
         unmatched_objects_put_in_lower_body=unmatched,
         bounds_m=dict(min=allpts.min(0).round(4).tolist(),max=allpts.max(0).round(4).tolist()),
         frontal_area_m2={k:round(v,4) for k,v in areas.items()},
         rider=dict(stature_mm=H,trunk_lean_deg=lean,seat_sit_point_z_mm=round(seat_z,1),
                    hip=hip.round(0).tolist(),knee=knee.round(0).tolist(),ankle=ank.round(0).tolist(),shoulder=sh.round(0).tolist(),
                    elbow=elbow.round(0).tolist(),grip=G.round(0).tolist(),helmet_centre=[round(v) for v in helmet_c],peg=[round(peg.x),round(peg.y),round(peg.z)]))
(R/'detailed-design/aero').mkdir(exist_ok=True)
(R/'detailed-design/aero/geometry-manifest.json').write_text(json.dumps(man,indent=1))
print(json.dumps({k:man[k] for k in ('frontal_area_m2','bounds_m','rider','unmatched_objects_put_in_lower_body')},indent=1))
