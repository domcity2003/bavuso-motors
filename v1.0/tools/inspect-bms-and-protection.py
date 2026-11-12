"""Inspect actual supplier geometry and candidate installation, no scaling.
Run with the local FreeCAD Python runtime. Does not edit the vehicle builder.
"""
from pathlib import Path
import json, zipfile, hashlib, argparse
import FreeCAD as A
import Part

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--vehicle', type=Path)
parser.add_argument('--x', type=float, default=205.0)
parser.add_argument('--z', type=float, default=705.0)
args = parser.parse_args()
archive = ROOT / 'sources/Orion-BMS2-manufacturer.zip'
folder = ROOT / 'sources/Orion-BMS2'
folder.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    members = [n for n in z.namelist() if n.endswith('108 cell Final Assembly.STEP')]
    if len(members) != 1:
        raise RuntimeError('Expected exactly one manufacturer108cellassembly')
    target = folder / 'Orion-BMS2-108-cell-manufacturer.STEP'
    target.write_bytes(z.read(members[0]))
shape = Part.read(str(target))

def bb(s):
    b=s.BoundBox
    return dict(min=[b.XMin,b.YMin,b.ZMin],max=[b.XMax,b.YMax,b.ZMax],
                size=[b.XLength,b.YLength,b.ZLength])

raw = bb(shape)
# No scaling: preserve supplier orientation initially; the fit search rotates
# axis-aligned frames only and reports all choices explicitly.
rotations = [A.Rotation(A.Vector(0,0,1),a) for a in (0,90,180,270)]
rotations += [A.Rotation(A.Vector(1,0,0),90).multiply(A.Rotation(A.Vector(0,0,1),a)) for a in (0,90,180,270)]
rotations += [A.Rotation(A.Vector(0,1,0),90).multiply(A.Rotation(A.Vector(0,0,1),a)) for a in (0,90,180,270)]
region_min = A.Vector(200,-85,695)
region_max = A.Vector(450,85,760)
region_size = region_max-region_min
candidates=[]
for i,rot in enumerate(rotations):
    placed=shape.copy()
    placed.Placement=A.Placement(A.Vector(),rot).multiply(placed.Placement)
    b=placed.BoundBox
    placed.translate(A.Vector(region_min.x-b.XMin,region_min.y-b.YMin,region_min.z-b.ZMin))
    b=placed.BoundBox
    fits=b.XMax<=region_max.x+1e-6 and b.YMax<=region_max.y+1e-6 and b.ZMax<=region_max.z+1e-6
    candidates.append(dict(index=i,rotation_quaternion=list(rot.Q),bounds=bb(placed),fits_named_region=fits,
                           remaining_xyz_mm=[region_max.x-b.XMax,region_max.y-b.YMax,region_max.z-b.ZMax]))
matches=[c for c in candidates if c['fits_named_region']]
# If none fit the tight region, preserve the common body attitude (largest
# dimension longitudinal, second transverse, smallest vertical) and center Y.
preferred=matches[0] if matches else min(candidates,key=lambda c:(round(c['bounds']['size'][2],6),round(c['bounds']['size'][1],6)))
rot=A.Rotation(*preferred['rotation_quaternion'])
installed=shape.copy()
installed.Placement=A.Placement(A.Vector(),rot).multiply(installed.Placement)
b=installed.BoundBox
installed.translate(A.Vector(args.x-b.XMin,-(b.YMin+b.YMax)/2,args.z-b.ZMin))

audit=dict(source_archive=str(archive.relative_to(ROOT)),source_member=members[0],
           source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
           source='https://www.orionbms.com/products/orion-bms-standard/',
           raw_bounds_mm=raw,shape_valid=shape.isValid(),solids=len(shape.Solids),
           geometric_volume_mm3=shape.Volume,
           geometric_volume_is_not_material_mass=True,
           named_region=dict(min=list(region_min),max=list(region_max)),
           tight_region_fit=bool(matches),orientations=candidates,
           installed_proposal=dict(rotation_quaternion=list(rot.Q),bounds=bb(installed),
                                   translation_min_x=args.x,translation_min_z=args.z),
           checks=[],limitations=['Connectors mates harness bends cooling mounting plate and cover not installed',
                                  'No proof108channels suffice for100groups with actual disconnect topology',
                                  'No fuse contactor pinout current threshold or electrical safety release'])
# Simple independent keepout checks. These are explicitly not the complete
# suspension, actual tire or selected shock supplier geometry.
def segment_cylinder(a,b,r):
    start=A.Vector(*a); end=A.Vector(*b); axis=end-start
    return Part.makeCylinder(r,axis.Length,start,axis)
proxies={
    'rear_tire_nominal_cylinder_proxy':Part.makeCylinder(311.9,160,A.Vector(0,-80,311.9),A.Vector(0,1,0)),
    'rear_tire_130mm_vertical_bump_proxy':Part.makeCylinder(311.9,160,A.Vector(0,-80,441.9),A.Vector(0,1,0)),
    'right_shock_90mmOD_nominal_proxy':segment_cylinder((300,150,399.733),(400,150,679.392),45),
}
for name,proxy in proxies.items():
    dist=installed.distToShape(proxy)[0]
    overlap=installed.common(proxy).Volume
    audit['checks'].append(dict(object=name,gap_mm=dist,overlap_mm3=overlap,
                               status='INTERFERENCE' if overlap>1e-3 else 'NO_PROXY_SOLID_INTERFERENCE',
                               limitation='Sampled proposed keepout only; no mounts harness or full kinematic qualification'))
if args.vehicle:
    doc=A.openDocument(str(args.vehicle.resolve()))
    for ob in doc.Objects:
        if not hasattr(ob,'Shape') or ob.Shape.isNull():
            continue
        n=ob.Name.lower()
        if any(token in n for token in ('shock','rear_tire','rear_wheel','seat','frame','cross','subframe','battery')):
            try:
                common=installed.common(ob.Shape).Volume
                dist=installed.distToShape(ob.Shape)[0]
                audit['checks'].append(dict(object=ob.Name,gap_mm=dist,overlap_mm3=common,
                                           status='INTERFERENCE' if common>1e-3 else 'NO_SOLID_INTERFERENCE_SAMPLED'))
            except Exception as e:
                audit['checks'].append(dict(object=ob.Name,error=str(e),status='NOT_CHECKED'))
    A.closeDocument(doc.Name)
out=ROOT/'models'
out.mkdir(exist_ok=True)
installed.exportStep(str(out/'Orion-BMS2-108-installed-proposal.step'))
(ROOT/'bms-installation-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:audit[k] for k in ('raw_bounds_mm','solids','shape_valid','tight_region_fit','installed_proposal')},indent=2))
print('Actual supplier body only; no material mass or full harness clearance claim.')
