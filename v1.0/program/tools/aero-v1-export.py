"""Export Bavuso V1 rev E (bike) + the 95th-percentile rider as STL surfaces for OpenFOAM.

Run from v1.0:
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/aero-v1-export.py
Bike: cad/Bavuso-V1.0-adventure.FCStd. Rider: group RiderStudy of cad/Bavuso-V1.0-adventure-rider.FCStd
(that file also holds the same bike; every shared object was checked identical, volume and centre).
Writes program/data/aero/run/geometry/<patch>.stl (metres, X forward, Y left, Z up, ground at Z=0)
and program/data/aero/geometry-manifest.json.
Method reused from detailed-design/tools/aero-export-geometry.py (Nov 12), updated to the rev E object names.
Simplifications: cells and keep-out volumes left out; supplier STEP parts (inverter, BMS, motor) become boxes of the
same size; the rider is the CAD's own smooth rider buck (no clothing).
"""
import sys, json, shutil, hashlib, zipfile, time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]/'.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin'))
import FreeCAD as A, Part, MeshPart
import numpy as np
V=A.Vector
R=Path(__file__).resolve().parents[2]
OUT=R/'program/data/aero';RUN=OUT/'run';GEO=RUN/'geometry';GEO.mkdir(parents=True,exist_ok=True)
LIN,ANG=0.8,0.30

def snap(src,dst):
    for k in range(10):
        shutil.copy2(src,dst)
        try:
            with zipfile.ZipFile(dst) as z:
                if z.testzip() is None:return hashlib.sha256(Path(dst).read_bytes()).hexdigest()
        except zipfile.BadZipFile:pass
        time.sleep(30)
    sys.exit('model unreadable')
SB,SR=RUN/'snap-bike.FCStd',RUN/'snap-rider.FCStd'
shaB=snap(R/'cad/Bavuso-V1.0-adventure.FCStd',SB);shaR=snap(R/'cad/Bavuso-V1.0-adventure-rider.FCStd',SR)
DB=A.openDocument(str(SB));DR=A.openDocument(str(SR))

# bike objects in the two files must be identical
ndiff=0
for o in DB.Objects:
    p=DR.getObject(o.Name)
    if p is None or not hasattr(o,'Shape') or o.Shape.isNull() or o.TypeId=='App::DocumentObjectGroup':continue
    if abs(o.Shape.Volume-p.Shape.Volume)>1e-3*max(1,abs(o.Shape.Volume)) or (o.Shape.BoundBox.Center-p.Shape.BoundBox.Center).Length>0.01:ndiff+=1
print('objects differing between bike and rider files:',ndiff)

def patch_of(n):
    if n.startswith(('Radiator_core','Radiator_fan')):   # one patch per side: 'neg' = Y<0 (right-hand side, name ends _m1)
        return ('rad_core' if n.startswith('Radiator_core') else 'rad_fan')+('_neg' if n.endswith('_m1') else '_pos')
    rules=[('wheel_front',('Front_nominal_tire','Front_wheel','Front_disc')),
           ('wheel_rear',('Rear_nominal_tire','Rear_wheel','Rear_disc','Rear_pulley')),
           ('screen',('Windscreen',)),
           ('mirrors',('Mirror_',)),
           ('rad_pod',('Radiator_pod',)),
           ('bars_controls',('Bar_','Hand_','Lever_perch','Switch_cube','Front_master','Front_brake_reservoir','Harness_','Upper_triple','Handguard','Steering_damper')),
           ('fork_fender',('Fork_','Lower_triple','Front_fender','Front_caliper','Front_brake_hose','Front_brake_splitter')),
           ('fairing_tank',('Upper_body','Headlamp','Front_indicator','Display_','Side_grille','Cascadia','Orion','Head_tube','Upper_rail_2','NACS','Horn_')),
           ('seat_tail',('Seat_','Tail_side','Tail_undertray','Tail_rail','Rear_rack','Taillamp','Plate_','Licence','Rear_indicator','Rear_reflector','Side_reflector','Shock_top_bracket','Rear_hugger')),
           ('swingarm_pegs',('Swingarm','Peg_','Drive_belt','Front_pulley','Motor_pulley','Rear_caliper','Rear_brake','Shock_','Independent_hollow','Pivot_6008','Side_stand')),
           ('lower_body',('Lower_body','Battery_side','Belly_','Panel_bolts','Seam_trim','Pivot_cover','Pack_case','EMRAX','HV_cabinet','GX14','Upper_rail','Upper_post','Lower_downlink','Lower_pack','Tail_brace','Head_gusset',
                          'Waist_ledge','Crash_guard','Pivot_slider','OBC','DCDC','Coolant_'))]
    for p,keys in rules:
        if any(n.startswith(k) for k in keys):return p
    return None
def skip(n):return n.startswith('Cell_') or 'keepout' in n or n=='Pivot_reference'
def box_of(s):
    b=s.BoundBox;return Part.makeBox(b.XLength,b.YLength,b.ZLength,V(b.XMin,b.YMin,b.ZMin))

shapes={};objmap={};unmatched=[];skipped=[]
for g in ('Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy','Cooling','Protection'):
    for o in DB.getObject(g).Group:
        n=o.Name
        if not hasattr(o,'Shape') or o.Shape.isNull():continue
        if skip(n):skipped.append(n);continue
        s=o.Shape
        if 'supplier_STEP' in n:s=box_of(s)
        p=patch_of(n)
        if p is None:p='lower_body';unmatched.append(n)
        shapes.setdefault(p,[]).append(s);objmap.setdefault(p,[]).append(n)

# rider: map the 31 CAD pieces to three force groups (checked against their bounding boxes)
legs={0,2,3,4,5,13,14,16,17,18,19,27};head={29,30}
arms=set(range(6,13))|set(range(20,27));torso={1,7,15,21,28}
rmap={}
for i in range(31):
    k='rider_helmet' if i in head else 'rider_legs' if i in legs else 'rider_torso_arms'
    rmap.setdefault(k,[]).append(f'Rider_{i:02d}')
assert set(sum(rmap.values(),[]))=={o.Name for o in DR.getObject('RiderStudy').Group}
for k,l in rmap.items():
    shapes[k]=[DR.getObject(n).Shape for n in l];objmap[k]=l

# wheel axles from the tyre bounding boxes
ax={}
for k,n in (('front','Front_nominal_tire'),('rear','Rear_nominal_tire')):
    b=DB.getObject(n).Shape.BoundBox;ax[k]=[round(b.Center.x/1000,4),0.0,round(b.Center.z/1000,4)]
print('axles (m):',ax)

tri_all={};
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

from PIL import Image, ImageDraw
px=0.002;W,Hh=int(1.2/px),int(2.0/px)
def frontal(names):
    im=Image.new('1',(W,Hh),0);dr=ImageDraw.Draw(im)
    for nm in names:
        a,b,c=tri_all[nm]
        for t in zip(a,b,c):dr.polygon([((p[1]+0.6)/px,(p[2])/px) for p in t],fill=1)
    return float(np.asarray(im).sum())*px*px
areas={'total':frontal(tri_all),'bike_only':frontal([k for k in tri_all if not k.startswith('rider')]),'rider_only':frontal([k for k in tri_all if k.startswith('rider')])}
allpts=np.vstack([np.vstack(v) for v in tri_all.values()])
man=dict(prepared='2026-11-22 US Central, Claude Sonnet 5.5 (claude-sonnet-5-5)',bike='cad/Bavuso-V1.0-adventure.FCStd',bike_sha256=shaB,
         rider='cad/Bavuso-V1.0-adventure-rider.FCStd (RiderStudy group)',rider_file_sha256=shaR,bike_objects_differing_between_files=ndiff,
         tessellation_mm=dict(linear=LIN,angular_rad=ANG),axles_m=ax,
         patches={k:dict(objects=objmap[k],triangles=int(len(tri_all[k][0]))) for k in tri_all},
         unmatched_objects_put_in_lower_body=unmatched,skipped_objects=skipped,
         bounds_m=dict(min=allpts.min(0).round(4).tolist(),max=allpts.max(0).round(4).tolist()),
         frontal_area_m2={k:round(v,4) for k,v in areas.items()})
(OUT/'geometry-manifest.json').write_text(json.dumps(man,indent=1))
print(json.dumps({k:man[k] for k in ('frontal_area_m2','bounds_m','axles_m','unmatched_objects_put_in_lower_body','skipped_objects')},indent=1))
