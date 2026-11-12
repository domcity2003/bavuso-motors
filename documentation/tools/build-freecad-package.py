"""Run inside the official FreeCAD Python environment, not ordinary Python.
Creates editable native reservation solids and STEP exchange geometry, not build CAD.
"""
from pathlib import Path
import json, math, sys
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'models/package-reservations.json').read_text(encoding='utf-8'))
out=ROOT/'models'
name='Bavuso_B0_Package'
if name in App.listDocuments(): App.closeDocument(name)
doc=App.newDocument(name)
assembly=doc.addObject('App::DocumentObjectGroup','Reservations')
assembly.Label='B0 RESERVATIONS - NOT RELEASED PARTS'
objects=[]
def status(obj,description):
    obj.addProperty('App::PropertyString','DefinitionStatus','Bavuso')
    obj.DefinitionStatus='UNVALIDATED RESERVATION - NOT MANUFACTURING GEOMETRY'
    obj.addProperty('App::PropertyString','Basis','Bavuso');obj.Basis=description
    assembly.addObject(obj);objects.append(obj)
for b in source['boxes']:
    obj=doc.addObject('Part::Box',b['id']);obj.Label=b['id']+' '+b['name']
    obj.Length=b['l'];obj.Width=b['w'];obj.Height=b['h']
    obj.Placement.Base=App.Vector(b['x'],b['y'],b['z'])
    status(obj,b['basis'])
    if App.GuiUp:
        obj.ViewObject.ShapeColor=tuple(int(b['color'][i:i+2],16)/255 for i in (1,3,5))
        obj.ViewObject.Transparency=55
# Envelope primitives preserve the model's conservative collision test definition.
for c in source.get('cylinders',[]):
    obj=doc.addObject('Part::Cylinder',c['id'])
    obj.Label=c['id']+' '+c['name']
    obj.Radius=c['r'];obj.Height=c['w']
    obj.Placement=App.Placement(App.Vector(c['x'],c['y']-c['w']/2,c['z']),App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0)))
    status(obj,c.get('basis','Solid conservative body/tire bounding envelope'))
    if App.GuiUp:obj.ViewObject.Transparency=65
pivot=source['points']['swingarm_pivot']
p=doc.addObject('Part::Sphere','PivotReference');p.Label='Swingarm pivot REFERENCE only';p.Radius=18;p.Placement.Base=App.Vector(*pivot)
status(p,'Proposed point; lies within the rectangular pack reservation')
notes=doc.addObject('Spreadsheet::Sheet','ReadMe')
for cell,text in {'A1':'BAVUSO B0 - DEVELOPMENT GEOMETRY','A2':'Units mm; X forward / Y left / Z up','A3':'Origin rear tire contact center at study ride height','A4':'Editable Part Box/Cylinder properties; regenerate from JSON to reset','A5':'These solids are reservations and known conflicts, not a fitted bike','A6':'No frame, cell modules, suspension motion or manufacturing drawings','A7':'See documentation/packaging.md and release-deliverables.csv'}.items():notes.set(cell,text)
notes.setColumnWidth('A',720)
doc.recompute()
for obj in objects:
    if not obj.Shape.isValid() or obj.Shape.Volume<=0:raise RuntimeError('Invalid CAD shape: '+obj.Name)
interferences=[]
for i,a in enumerate(objects):
    for b in objects[i+1:]:
        shared=a.Shape.common(b.Shape).Volume
        if shared>1e-6:
            interferences.append(dict(item_a=a.Name,item_b=b.Name,shared_reservation_volume_mm3=shared,
                                      status='Unresolved envelope interference; not a real-part fit evaluation'))
native=out/'Bavuso-B0-package.FCStd';step=out/'Bavuso-B0-package.step'
doc.saveAs(str(native))
Part.export(objects,str(step))
volume=sum(o.Shape.Volume for o in objects)
exchange=Part.read(str(step))
if not exchange.isValid():raise RuntimeError('STEP reimport invalid')
if not math.isclose(exchange.Volume,volume,rel_tol=1e-7):raise RuntimeError('STEP volume mismatch')
App.closeDocument(name)
reopened=App.openDocument(str(native))
if len(reopened.Objects)!=len(objects)+2:raise RuntimeError('Native document object count mismatch')
checks=dict(freecad_version=list(App.Version()),native_file=native.name,step_file=step.name,
            primitive_count=len(objects),native_document_object_count=len(reopened.Objects),
            native_reopen=True,all_shapes_valid=True,step_reimport_valid=True,
            reservation_interferences=interferences,
            summed_reservation_volume_mm3=volume,step_volume_mm3=exchange.Volume,
            status='CAD connection verified; reservation geometry only; known conflicts remain')
(out/'freecad-connection-test.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2));sys.stdout.flush()
