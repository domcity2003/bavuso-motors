"""V1.0 development geometry. Run with bundled FreeCAD Python.
Real supplier imports and explicitly provisional custom geometry; not build release.
"""
from pathlib import Path
import json, math, csv, hashlib
import FreeCAD as A
import Part

R=Path(__file__).resolve().parents[1]
D=A.newDocument('Bavuso_V1_Development')
D.Label='Bavuso V1.0 - ENGINEERING DEVELOPMENT'
V=A.Vector
groups={}
records=[]
def group(name):
    g=D.addObject('App::DocumentObjectGroup',name);groups[name]=g;return g
for n in ['Energy','Drive','Chassis','RunningGear','BodyStudy','Keepouts']:group(n)
def add(name,shape,g,basis,source='',color=(.35,.38,.42),hide=False):
    o=D.addObject('PartDesign::Feature' if False else 'Part::Feature',name)
    o.Label=name.replace('_',' ');o.Shape=shape
    for prop,value in [('Definition',basis),('Source',source),('ReleaseState','DEVELOPMENT - NOT FOR FABRICATION')]:
        o.addProperty('App::PropertyString',prop,'Bavuso');setattr(o,prop,value)
    groups[g].addObject(o)
    if A.GuiUp:o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=not hide
    records.append(dict(id=name,group=g,basis=basis,source=source,solids=len(shape.Solids),volume_mm3=shape.Volume))
    return o
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(a,b,r,inner=0):
    a,b=V(*a),V(*b);d=b-a;s=Part.makeCylinder(r,d.Length,a,d)
    return s.cut(Part.makeCylinder(inner,d.Length,a,d)) if inner else s
def tube(name,a,b,ro,ri,g='Chassis'):
    return add(name,cyl(a,b,ro,ri),g,'PROPOSED centerline and section; material/joints/fatigue NOT qualified')
def normalize(s,target,rotation=None):
    s=s.copy()
    if rotation:s.Placement=A.Placement(V(),rotation).multiply(s.Placement)
    b=s.BoundBox;s.translate(V(target[0]-b.XMin,target[1]-b.YMin,target[2]-b.ZMin));return s

# Dimensions are proposals unless their individual source says otherwise.
P=dict(wheelbase_mm=1640,pack_origin_mm=[570,-110,160],pack_outer_mm=[690,220,550],
       motor_axis_mm=[440,0,340],pivot_mm=[490,0,490],rear_tire_radius_mm=311.9,
       front_tire_radius_mm=299.9,front_travel_mm=125,rear_vertical_travel_mm=130,
       rake_deg=25,proposed_trail_mm=100,seat_reference_mm=[470,0,850],
       grip_reference_mm=[1050,340,1120],peg_reference_mm=[500,200,380],
       cell_count=700,series=100,parallel=7,cartridges=10,
       cell_max_catalog_dimensions_mm=[126.4,8.55,43.2],
       cell_pitch_mm=[132,10,50],cell_tolerance_basis='30% SOC manufacturing size; NOT aged/swollen dimensions',
       physical_cartridge='5 series columns X, 2 series rows Z, 7 parallel cells Y; 10s7p',
       cartridge_placement='2 Y columns and 5 Z tiers; NOT electrical joining or insulation design')

# Actual manufacturer geometry. Do not silently scale any source.
motorpath=R/'sources/EMRAX-208-LC-resolver-2022.step'
motorraw=Part.read(str(motorpath))
rot=A.Rotation(V(0,0,1),90)
ms=motorraw.copy();ms.Placement=A.Placement(V(),rot).multiply(ms.Placement)
b=ms.BoundBox;ms.translate(V(440-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,340-(b.ZMin+b.ZMax)/2))
motor=add('EMRAX_208_LC_supplier_STEP',ms,'Drive','ACTUAL supplier STEP dated2022; ordered2026 revision/mount/shaft loads unverified','https://emrax.com/wp-content/uploads/2022/05/208_lc_resolver.step',(.8,.45,.17))
invpath=next((R/'sources/CM200').glob('*.STEP'))
invs=normalize(Part.read(str(invpath)),[590,-94.1,750],A.Rotation(V(1,1,1),120))
inverter=add('Cascadia_CM200_supplier_STEP',invs,'Drive','ACTUAL manufacturer CM200 CAD; DX variant and connector/service clearances unverified','https://www.cascadiamotion.com/cm-200',(.2,.5,.65))
charger=add('BROGEN_PV1776_body',box(940,-112,750,373,224,76.5),'Energy','CATALOG body dimensions only; mounting, ports, supply and selected revision unverified','https://www.brogenmotors.com/wp-content/uploads/2024/06/Requirement_SheetOBC.pdf',(.3,.65,.45))

# 700 discrete maximum-catalog-size pouch bodies. No invented tab detail.
cell_source='https://amprius.com/documents/Amprius_Product_Catalog.pdf#page=52'
cells=[];cellmap=[]
for tier in range(5):
  for lane in range(2):
    module=tier*2+lane+1;shapes=[]
    for row in range(2):
      for col in range(5):
        series=(module-1)*10+row*5+col+1
        for parallel in range(7):
          x=585+col*132;y=-75+lane*80+parallel*10;z=168+tier*108+row*50
          s=box(x,y,z,126.4,8.55,43.2);shapes.append(s);cells.append(s)
          cellmap.append(dict(cell_id=f'S{series:03d}P{parallel+1}',series_group=series,parallel_position=parallel+1,
                              cartridge=module,x_mm=x,y_mm=y,z_mm=z,length_mm=126.4,width_mm=8.55,height_mm=43.2))
    add(f'Cartridge_{module:02d}_10s7p',Part.makeCompound(shapes),'Energy','70 discrete CATALOG MAX bodies @30%SOC. Pitch allowances proposed; tab routes, compression, swelling and propagation unresolved',cell_source,(.78,.57,.24))
outer=box(570,-110,160,690,220,550)
inner=box(573,-107,163,684,214,544)
case=add('Pack_case_3mm_STUDY',outer.cut(inner),'Energy','PROPOSED 3mm closed shell; no lid, mounts, joints, vent or thermal qualification. Cells are separate',color=(.45,.48,.5))
packkeep=add('Battery_installation_keepout',outer,'Keepouts','PROPOSED outer battery boundary, not proof of completed pack',hide=True)

# Real tire-size nominal geometry, not manufacturer tread CAD.
def wheel(name,x,z,width,r,front):
    tor=Part.makeTorus((r+215.9)/2,(r-215.9)/2,V(x,0,z),V(0,1,0))
    tor=tor.transformGeometry(A.Matrix()) if False else tor
    # Elliptical radial section via affine scale gives nominal width; no loaded-tire prediction.
    m=A.Matrix();m.A22=width/(r-215.9)
    tor.translate(V(-x,0,-z));tor=tor.transformGeometry(m);tor.translate(V(x,0,z))
    add(name+'_nominal_tire',tor,'RunningGear','Nominal 120/70ZR17 front or160/60ZR17 rear; no loaded radius/growth/tread geometry',color=(.09,.1,.11))
    rim=cyl((x,-width*.34,z),(x,width*.34,z),215.9,198)
    hub=cyl((x,-35,z),(x,35,z),38,10)
    spokes=[]
    for k in range(5):
        t=k*math.tau/5
        spokes.append(cyl((x+32*math.cos(t),0,z+32*math.sin(t)),(x+200*math.cos(t),0,z+200*math.sin(t)),9))
    add(name+'_wheel_STUDY',Part.makeCompound([rim,hub]+spokes),'RunningGear','ILLUSTRATIVE wheel; OEM candidate hub/spokes/offset CAD absent; no fabrication use',color=(.25,.27,.29))
    discR=150 if front else 110
    sides=[-1,1] if front else[-1]
    for side in sides:add(name+f'_disc_{side:+d}'.replace('+','p').replace('-','m'),cyl((x,side*width*.52,z),(x,side*width*.52+4.5,z),discR,50),'RunningGear','300mm front /220mm rear OEM nominal diameter, thickness/offset PROPOSED; no holes/mounts',color=(.68,.69,.7))
wheel('Rear',0,311.9,160,311.9,False)
wheel('Front',1640,299.9,120,299.9,True)
# Sweep solid conservative tire cylinders at 21 suspension positions.
rear_sweeps=[];front_sweeps=[]
pivot=V(490,0,490);arm=math.hypot(490,490-311.9)
for i in range(21):
    travel=i/20
    rz=311.9+130*travel;rx=490-math.sqrt(arm*arm-(rz-490)**2)
    rear_sweeps.append(cyl((rx,-80,rz),(rx,80,rz),311.9))
    fx=1640-125*math.sin(math.radians(25))*travel;fz=299.9+125*math.cos(math.radians(25))*travel
    front_sweeps.append(cyl((fx,-60,fz),(fx,60,fz),299.9))
rearSweep=add('Rear_bump_sampled_keepout',Part.makeCompound(rear_sweeps),'Keepouts','21 samples; proposed pivot and130mm vertical travel; growth, droop/lateral compliance absent',hide=True)
frontSweep=add('Front_bump_sampled_keepout',Part.makeCompound(front_sweeps),'Keepouts','21 samples;125mm axial compression at25deg; steering sweep NOT included',hide=True)

# Custom chassis centerlines. Hollow tubes are a fabrication study, not approved structure.
for side in [-1,1]:
    y=side*145
    pts=[(490,y,490),(570,y,760),(1280,y,735),(1344,side*35,850)]
    for i in range(len(pts)-1):tube(f'Upper_rail_{side}_{i}'.replace('-','m'),pts[i],pts[i+1],16,13.5)
    lower=[(490,y,490),(575,y,140),(1265,y,140),(1344,side*35,850)]
    for i in range(len(lower)-1):tube(f'Lower_rail_{side}_{i}'.replace('-','m'),lower[i],lower[i+1],16,13.5)
    tube(f'Tail_rail_{side}'.replace('-','m'),(570,y,760),(-100,y,850),14,12)
    tube(f'Tail_brace_{side}'.replace('-','m'),(490,y,490),(160,y,825),14,12)
    tube(f'Swingarm_{side}'.replace('-','m'),(490,side*125,490),(0,side*125,311.9),24,20)
    tube(f'Fork_leg_{side}'.replace('-','m'),(1320,side*100,985),(1640,side*100,299.9),20.5,16,'RunningGear')
tube('Head_tube',(1344,0,850),(1283,0,980),31,25)
tube('Pivot_reference',(490,-180,490),(490,180,490),18,10)
shock=cyl((340,0,780),(500,0,530),45)
add('Shock_and_spring_keepout',shock,'Keepouts','297mm eye distance reference;90mm maximum OD reservation NOT supplier size; linkage geometry unresolved',hide=True)
add('Shock_visual',cyl((340,0,780),(500,0,530),24),'Chassis','VISUAL ONLY; Ka736 piston46mm is not outerbody; mounts and2.41 leverage unresolved',color=(.75,.65,.2))
for side in [-1,1]:
    add(f'Side_radiator_{side}'.replace('-','m'),box(1120,side*190-25,390,110,50,250),'Energy','UNSIZED side heat-exchanger/fan reservation; deliberate alternative to B0 front radiator',color=(.4,.45,.5))
    tube(f'Peg_reference_{side}'.replace('-','m'),(500,side*145,380),(500,side*230,380),12,8,'RunningGear')
    tube(f'Bar_half_{side}'.replace('-','m'),(1220,0,1060),(1050,side*340,1120),11,8,'RunningGear')

# Exterior lofts expose styling intent but have no engineering provenance.
def section(x,w,bottom,top):
    p=[V(x,-w,bottom),V(x,w,bottom),V(x,w,top),V(x,-w,top),V(x,-w,bottom)]
    return Part.makePolygon(p)
body=Part.makeLoft([section(540,124,155,730),section(900,146,155,885),section(1255,160,300,855),section(1390,115,650,810)],True,True)
body=body.cut(outer)
add('Body_surface_DIRECTION_ONLY',body,'BodyStudy','PROPOSED faceted shell; not finished styling, mold thickness, fit or CFD-ready surface',color=(.18,.2,.22),hide=True)
seat=Part.makeLoft([section(-100,105,840,880),section(200,160,840,910),section(570,145,815,870)],True,True)
add('Seat_foam_STUDY',seat,'BodyStudy','PROPOSED seat shape; pan/foam/support and human fit unvalidated',color=(.12,.13,.14))
screen=Part.makeLoft([section(1380,170,840,845),section(1230,160,1200,1205)],True,True)
add('Windscreen_STUDY',screen,'BodyStudy','PROPOSED5mm swept screen; visibility, optical quality, buffeting and brackets unresolved',color=(.6,.8,.85))

notes=D.addObject('Spreadsheet::Sheet','DesignStatus')
for i,t in enumerate(['BAVUSO V1.0 ENGINEERING DEVELOPMENT - NOT BUILD RELEASE',
 'Units mm; Xforward,Yleft,Zup; rearcontactorigin',
 '700catalog-max cell bodies100s7p; tab/thermal/clamping unresolved',
 'Motor/inverter actual manufacturer STEP; revision and mounting unresolved',
 '1640mm wheelbase proposal: longer than B0, packaging trade, NOT owner approval',
 'Custom chassis and OEM runninggear representations NOT production drawings',
 'See v1.0/README.md, geometry-audit.json and component-status.csv'],1):notes.set(f'A{i}',t)
notes.setColumnWidth('A',900)
D.recompute()
validity=[]
for o in D.Objects:
    if hasattr(o,'Shape'):
        valid=o.Shape.isValid() and o.Shape.Volume>0
        validity.append(dict(id=o.Name,valid=valid))
        if not valid:raise RuntimeError('Invalidshape '+o.Name)
assert len(cells)==700 and len(set(r['cell_id'] for r in cellmap))==700
cellcontain=all(inner.isInside(vertex.Point,1e-6,True) for s in cells for vertex in s.Vertexes)
assert cellcontain
# Exact kernel intersections for named broad component bodies, excluding intended contacting/joined bodies.
checks=[]
def check(label,a,b,minimum=0):
    distance=a.distToShape(b)[0];overlap=a.common(b).Volume
    checks.append(dict(check=label,gap_mm=distance,overlap_mm3=overlap,required_mm=minimum,passed=distance>=minimum-1e-5 and overlap<1e-5))
check('battery_vs_motor_supplier_geometry',outer,ms,20)
check('battery_vs_front_bump_samples',outer,frontSweep.Shape,20)
check('motor_vs_rear_bump_samples',ms,rearSweep.Shape,20)
check('battery_vs_shock_reservation',outer,shock,20)
check('battery_vs_pivot_tube',outer,D.getObject('Pivot_reference').Shape,20)
check('motor_vs_pivot_tube',ms,D.getObject('Pivot_reference').Shape,20)
check('battery_vs_inverter',outer,invs,20)
check('inverter_vs_charger',invs,charger.Shape,20)
for side in [-1,1]:
    rad=D.getObject(f'Side_radiator_{side}'.replace('-','m')).Shape
    check(f'radiator_{side}_vs_front_bump',rad,frontSweep.Shape,20)
native=R/'cad/Bavuso-V1.0-development.FCStd';D.saveAs(str(native))
visible=[D.getObject(r['id']) for r in records if r['group']!='Keepouts' and r['id']!='Body_surface_DIRECTION_ONLY']
Part.export(visible,str(R/'cad/Bavuso-V1.0-development.step'))
audit=dict(release_state='ENGINEERING DEVELOPMENT; no build authorization',parameters=P,
 actual_supplier_geometry=['EMRAX208LC2022','CM200manufacturerCAD'],
 solid_objects=len(validity),total_solids=sum(r['solids'] for r in records),shape_validity=validity,
 cell_count=len(cells),all_cell_vertices_inside_inner_case=cellcontain,critical_pair_checks=checks,
 checks_passed=sum(c['passed'] for c in checks),checks_total=len(checks),
 exclusions=['steering lock','rear droop','tire growth','real fork/yoke/hub dimensions','fullframe clash resolution','tab joining','wiring','hoses','mounts','structure','CFD','test validation'])
for file,rows in [('cell-placement.csv',cellmap),('component-status.csv',records)]:
    with (R/file).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(R/'geometry-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k not in ['shape_validity','parameters']},indent=2),flush=True)

