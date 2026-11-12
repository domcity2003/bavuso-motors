"""Independent saved-native/STEP and coverage check; no physical approval."""
from pathlib import Path
import csv,json,math,hashlib,itertools,sys
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[1]
compact='--compact' in sys.argv
suffix='-rework' if compact else ''
stem='Bavuso-V1.0-rework' if compact else 'Bavuso-V1.0-development'
audit=json.loads((R/('geometry-rework-audit.json' if compact else 'geometry-audit.json')).read_text())
D=A.openDocument(str(R/'cad'/f'{stem}.FCStd'))
records=list(csv.DictReader((R/f'component-status{suffix}.csv').open(encoding='utf-8-sig')))
shapeobjs=[D.getObject(r['id']) for r in records]
assert all(o and o.Shape.isValid() for o in shapeobjs)
cells=[o for o in shapeobjs if o.Name.startswith('Cartridge_')]
assert len(cells)==10 and sum(len(o.Shape.Solids) for o in cells)==700
p=audit['parameters'];x,y,z=p['pack_origin_mm'];l,w,h=p['pack_outer_mm']
interior=Part.makeBox(l-6,w-6,h-6,A.Vector(x+3,y+3,z+3))
assert all(interior.isInside(v.Point,1e-6,True) for o in cells for v in o.Shape.Vertexes)
rows=list(csv.DictReader((R/f'cell-placement{suffix}.csv').open()))
assert len(rows)==700 and len(set(r['cell_id'] for r in rows))==700
for group,items in itertools.groupby(sorted(rows,key=lambda r:int(r['series_group'])),key=lambda r:int(r['series_group'])):
    items=list(items);assert len(items)==7 and sorted(int(i['parallel_position']) for i in items)==list(range(1,8))
# Full catalog-body AABBs, not centers, are mutually separated; no tabs implied.
cellboxes=[tuple(float(r[k]) for k in ['x_mm','y_mm','z_mm','length_mm','width_mm','height_mm']) for r in rows]
overlaps=0
for i,a in enumerate(cellboxes):
    for b in cellboxes[i+1:]:
        if all(min(a[k]+a[k+3],b[k]+b[k+3])-max(a[k],b[k])>1e-7 for k in range(3)):overlaps+=1
assert overlaps==0
selected=[D.getObject(r['id']) for r in records if r['group']!='Keepouts' and r['id']!='Body_surface_DIRECTION_ONLY']
total=sum(o.Shape.Volume for o in selected)
exchange=Part.read(str(R/'cad'/f'{stem}.step'))
nativecompound=Part.makeCompound([o.Shape for o in selected])
bbn,bbs=nativecompound.BoundBox,exchange.BoundBox
bbox_error=max(abs(getattr(bbn,k)-getattr(bbs,k)) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax'])
relative_volume_error=abs(exchange.Volume-total)/total
native_solids=sum(len(o.Shape.Solids) for o in selected)
print(json.dumps({'step_valid':exchange.isValid(),'native_sum':total,'step_volume':exchange.Volume,'relative_volume_error':relative_volume_error,'step_solids':len(exchange.Solids),'native_solids':native_solids,'bbox_error_mm':bbox_error}),flush=True)
# B-spline/affine tire surface integrals change slightly through STEP. Explicit
# 0.01% study-volume tolerance is combined with 0.01mm bounds and solid count.
# This is exchange-study QA, not part-drawing tolerance or manufacturing acceptance.
assert exchange.isValid() and relative_volume_error<=1e-4 and bbox_error<=.01 and native_solids==len(exchange.Solids)
# Broadphase reports ALL candidate body contacts in displayed engineering geometry.
# Many contacts are intended joints; boundingboxes overestimate actual contact.
contacts=[]
for i,a in enumerate(selected):
    for b in selected[i+1:]:
        aa,bb=a.Shape.BoundBox,b.Shape.BoundBox
        overlap=[min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))-max(getattr(aa,k+'Min'),getattr(bb,k+'Min')) for k in ['X','Y','Z']]
        if all(v>1e-5 for v in overlap):
            contacts.append({'a':a.Name,'b':b.Name,'aabb_overlap_xyz_mm':overlap,'disposition':'REVIEW; broadphase only, includes intentional joints and false positives'})
with (R/f'static-contact-candidates{suffix}.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['a','b','aabb_overlap_xyz_mm','disposition']);w.writeheader();w.writerows(contacts)
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'sources/EMRAX-208-LC-resolver-2022.step',next((R/'sources/CM200').glob('*.STEP')),R/'cad'/f'{stem}.step']}
result=dict(native_reopen=True,all_saved_shapes_valid=True,source_object_count=len(records),
 native_document_object_count=len(D.Objects),cell_count=700,series_groups=100,parallel=7,
 full_cell_body_inside_inner_case=True,cell_body_pair_overlaps=overlaps,
 step_reimport_valid=True,native_exported_volume_mm3=total,step_volume_mm3=exchange.Volume,
 step_relative_volume_error=relative_volume_error,study_volume_tolerance=1e-4,
 bounding_box_error_mm=bbox_error,study_bounds_tolerance_mm=.01,
 broadphase_contact_candidates=len(contacts),sha256=hashes,
 result='PASS_FILE_AND_DEFINED_GEOMETRY_CHECKS; NOT ENGINEERING RELEASE',
 limitations='No complete part BOM, global exact clash disposition, kinematics, structural/thermal/CFD or physical verification')
(R/f'cad/file-verification{suffix}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2),flush=True)
