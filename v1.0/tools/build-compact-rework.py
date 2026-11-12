"""V1.0 development geometry. Run with bundled FreeCAD Python.
Real supplier imports and explicitly provisional custom geometry; not build release.
"""
from pathlib import Path
import json, math, csv, hashlib
import FreeCAD as A
import Part

R=Path(__file__).resolve().parents[1]
D=A.newDocument('Bavuso_Compact_Development')
D.Label='Bavuso compact rework - IN DEVELOPMENT'
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
P=dict(wheelbase_mm=1480,pack_origin_mm=[670,-165,150],pack_outer_mm=[420,330,570],
       motor_axis_mm=[540,0,470],pivot_mm=[540,0,470],rear_tire_radius_mm=311.9,
       front_tire_radius_mm=299.9,front_travel_mm=125,rear_vertical_travel_mm=130,
       rake_deg=25,proposed_trail_mm=100,seat_reference_mm=[470,0,805],
       grip_reference_mm=[970,340,1060],peg_reference_mm=[500,200,380],
       cell_count=700,series=100,parallel=7,cartridges=10,
       cell_max_catalog_dimensions_mm=[8.55,126.4,43.2],
       cell_pitch_mm=[10,144,50],cell_tolerance_basis='30% SOC manufacturing size; NOT aged/swollen dimensions',
       physical_cartridge='2 series columns Y, 5 series rows Z, 7 parallel cells X; 10s7p',
       cartridge_placement='5 X columns and 2 Z tiers; NOT electrical joining or insulation design')

# Actual manufacturer geometry. Do not silently scale any source.
motorpath=R/'sources/EMRAX-208-LC-resolver-2022.step'
motorraw=Part.read(str(motorpath))
rot=A.Rotation(V(0,0,1),90)
ms=motorraw.copy();ms.Placement=A.Placement(V(),rot).multiply(ms.Placement)
b=ms.BoundBox;ms.translate(V(540-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,470-(b.ZMin+b.ZMax)/2))
motor=add('EMRAX_208_LC_supplier_STEP',ms,'Drive','ACTUAL supplier STEP dated2022; ordered2026 revision/mount/shaft loads unverified','https://emrax.com/wp-content/uploads/2022/05/208_lc_resolver.step',(.8,.45,.17))
invpath=next((R/'sources/CM200').glob('*.STEP'))
invs=normalize(Part.read(str(invpath)),[690,-94.1,740],A.Rotation(V(1,1,1),120))
inverter=add('Cascadia_CM200_supplier_STEP',invs,'Drive','ACTUAL manufacturer CM200 CAD; DX variant and connector/service clearances unverified','https://www.cascadiamotion.com/cm-200',(.2,.5,.65))
charger=add('BROGEN_PV1776_body',box(700,-112,857,373,224,76.5),'Energy','CATALOG body dimensions only; mounting, ports, supply and selected revision unverified','https://www.brogenmotors.com/wp-content/uploads/2024/06/Requirement_SheetOBC.pdf',(.3,.65,.45))

# 700 discrete maximum-catalog-size pouch bodies. No invented tab detail.
cell_source='https://amprius.com/documents/Amprius_Product_Catalog.pdf#page=52'
cells=[];cellmap=[]
for tier in range(2):
  for column in range(5):
    module=tier*5+column+1;shapes=[]
    for row in range(5):
      for lane in range(2):
        series=(module-1)*10+row*2+lane+1
        for parallel in range(7):
          x=685+column*75+parallel*10;y=-135.2+lane*144;z=165+tier*260+row*50
          q=box(x,y,z,8.55,126.4,43.2);shapes.append(q);cells.append(q)
          cellmap.append(dict(cell_id=f'S{series:03d}P{parallel+1}',series_group=series,parallel_position=parallel+1,
                              cartridge=module,x_mm=x,y_mm=y,z_mm=z,length_mm=8.55,width_mm=126.4,height_mm=43.2))
    add(f'Cartridge_{module:02d}_10s7p',Part.makeCompound(shapes),'Energy','70 CATALOG MAX pouch bodies at30%SOC, rotated; physical joining/compression/cooling unresolved',cell_source,(.78,.57,.24))
outer=box(670,-165,150,420,330,570)
inner=box(673,-162,153,414,324,564)
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
    sides=[-1,1] if front else[1]
    for side in sides:add(name+f'_disc_{side:+d}'.replace('+','p').replace('-','m'),cyl((x,side*width*.52,z),(x,side*width*.52+4.5,z),discR,50),'RunningGear','300mm front /220mm rear OEM nominal diameter, thickness/offset PROPOSED; no holes/mounts',color=(.68,.69,.7))
wheel('Rear',0,311.9,160,311.9,False)
wheel('Front',1480,299.9,120,299.9,True)
# Sweep solid conservative tire cylinders at 21 suspension positions.
rear_sweeps=[];front_sweeps=[]
pivot=V(540,0,470);arm=math.hypot(540,470-311.9)
for i in range(21):
    travel=i/20
    rz=311.9+130*travel;rx=540-math.sqrt(arm*arm-(rz-470)**2)
    rear_sweeps.append(cyl((rx,-80,rz),(rx,80,rz),311.9))
    fx=1480-125*math.sin(math.radians(25))*travel;fz=299.9+125*math.cos(math.radians(25))*travel
    front_sweeps.append(cyl((fx,-60,fz),(fx,60,fz),299.9))
rearSweep=add('Rear_bump_sampled_keepout',Part.makeCompound(rear_sweeps),'Keepouts','21 samples; proposed pivot and130mm vertical travel; growth, droop/lateral compliance absent',hide=True)
frontSweep=add('Front_bump_sampled_keepout',Part.makeCompound(front_sweeps),'Keepouts','21 samples;125mm axial compression at25deg; steering sweep NOT included',hide=True)

# Custom chassis centerlines. Hollow tubes are a fabrication study, not approved structure.
for side in [-1,1]:
    y=side*195
    pts=[(540,y,470),(580,y,760),(1050,y,780),(1184,side*35,850)]
    for i in range(len(pts)-1):tube(f'Upper_rail_{side}_{i}'.replace('-','m'),pts[i],pts[i+1],16,13.5)
    lower=[(540,y,470),(575,y,130),(1015,y,130),(1184,side*35,850)]
    for i in range(len(lower)-1):tube(f'Lower_rail_{side}_{i}'.replace('-','m'),lower[i],lower[i+1],16,13.5)
    tube(f'Tail_rail_{side}'.replace('-','m'),(580,y,760),(-80,side*125,825),14,12)
    tube(f'Tail_brace_{side}'.replace('-','m'),(540,y,470),(160,side*145,805),14,12)
    tube(f'Swingarm_{side}'.replace('-','m'),(540,side*125,470),(0,side*125,311.9),24,20)
    tube(f'Fork_leg_{side}'.replace('-','m'),(1480-(985-299.9)*math.tan(math.radians(25)),side*100,985),(1480,side*100,299.9),20.5,16,'RunningGear')
tube('Head_tube',(1580-850*math.tan(math.radians(25)),0,850),(1580-980*math.tan(math.radians(25)),0,980),31,25)
stubs=[]
for side in [-1,1]:
    a=(540,side*110,470);b=(540,side*150,470)
    stub=cyl(a,b,20,15);stubs.append(stub)
    add(f'Independent_hollow_pivot_stub_{side}'.replace('-','m'),stub,'Chassis','Proposed40OD30ID fixed frame stub; rotor adapter passes separately, actual loads/fits not approved')
    bearing=cyl((540,side*125,470),(540,side*140,470),34,20)
    add(f'Pivot_6008_size_reference_{side}'.replace('-','m'),bearing,'Chassis','6008 dimensional reference40x68x15; load/life/oscillation/seal/retention selection open','https://cdn.skfmediahub.skf.com/api/public/0901d196802809de/pdf_preview_medium/0901d196802809de_pdf_preview_medium.pdf')
pivotStudy=add('Pivot_reference',Part.makeCompound(stubs),'Keepouts','Independent outboard pivots; no shaft through motor/stator',hide=True)
shock=cyl((400,150,679.392),(300,150,399.733),45)
add('Shock_and_spring_keepout',shock,'Keepouts','297mm eye distance reference;90mm maximum OD reservation NOT supplier size; linkage geometry unresolved',hide=True)
upper=V(400,150,679.392);lower=V(300,150,399.733);axis=(lower-upper);axis.normalize()
add('Shock_body_STUDY',cyl(tuple(upper+axis*25),tuple(upper+axis*205),26),'Chassis','297mm mounted length and54mm catalogue stroke reference; body dimensions illustrative; not supplier CAD',color=(.6,.61,.63))
add('Shock_rod_STUDY',cyl(tuple(upper+axis*180),tuple(lower-axis*12),8),'Chassis','Illustrative damper shaft; spring/damper sizing not approved',color=(.78,.79,.8))
for name,eye in [('Upper',upper),('Lower',lower)]:
    add('Shock_'+name+'_eye_STUDY',cyl((eye.x,140,eye.z),(eye.x,160,eye.z),15,5),'Chassis','Illustrative eye and10mm reference hole; actual joint dimensions unknown')
helix=Part.makeHelix(18,180,34)
profile=Part.Wire(Part.makeCircle(4,V(34,0,0),V(0,1,0)))
spring=Part.Wire(helix.Edges).makePipeShell([profile],True,True)
spring.Placement=A.Placement(upper+axis*25,A.Rotation(V(0,0,1),axis))
add('Shock_spring_STUDY',spring,'Chassis','Visual coil only; required spring rate differs from KA736 stock130N/mm; see suspension study',color=(.75,.65,.2))
for side in [-1,1]:
    add(f'Side_radiator_{side}'.replace('-','m'),box(1020,side*190-25,390,110,50,250),'Energy','UNSIZED side heat-exchanger/fan reservation; deliberate alternative to B0 front radiator',color=(.4,.45,.5))
    tube(f'Peg_reference_{side}'.replace('-','m'),(500,side*145,380),(500,side*230,380),12,8,'RunningGear')
    tube(f'Bar_half_{side}'.replace('-','m'),(1110,0,990),(970,side*340,1060),11,8,'RunningGear')

# Smooth exterior study derived from selected minimal upright reference.
# These surfaces retain explicit styling status: no CFD/manufacturing claims.
def section(x,w,bottom,top):
    h=top-bottom;mid=(top+bottom)/2
    points=[V(x,0,top),V(x,w*.75,top-.06*h),V(x,w,top-.25*h),
            V(x,w,bottom+.25*h),V(x,w*.65,bottom),V(x,-w*.65,bottom),
            V(x,-w,bottom+.25*h),V(x,-w,top-.25*h),V(x,-w*.75,top-.06*h)]
    curve=Part.BSplineCurve();curve.interpolate(points,PeriodicFlag=True)
    return Part.Wire(curve.toShape())
body_sections=[(550,195,150,750),(630,220,150,980),(850,225,150,990),
               (1050,215,250,990),(1170,185,500,900),(1260,145,700,860)]
envelope=Part.makeLoft([section(*q) for q in body_sections],True,True)
inside=Part.makeLoft([section(x,w-3,b+3,t-3) for x,w,b,t in body_sections],True,True)
body=envelope.cut(inside)
for side in [-1,1]:
    vent=box(1015,165 if side==1 else -250,385,130,85,260)
    body=body.cut(vent)
add('Body_surface_DIRECTION_ONLY',body,'BodyStudy','PROPOSED flowing exterior; correct reference intent only, not wall-thickness/tooling/CFD definition',color=(.18,.2,.22),hide=True)
seat=Part.makeLoft([section(-80,80,815,865),section(150,145,805,875),
                   section(340,150,775,825),section(480,135,770,820),section(580,105,785,835)],True,True)
add('Seat_foam_STUDY',seat,'BodyStudy','PROPOSED shaped two-level saddle; broad fit, pan, foam and supports unresolved',color=(.12,.13,.14))
tail=Part.makeLoft([section(-130,50,785,820),section(120,150,770,835),section(360,143,755,790)],True,True)
add('Tail_body_STUDY',tail,'BodyStudy','Proposed compact tail shell; passenger rating not established',color=(.18,.2,.22))
# Sloped clear screen, blended upper fairing, wheel-cover and light references.
screenwire=Part.makePolygon([V(1240,-170,845),V(1240,170,845),V(1100,155,1150),V(1100,-155,1150),V(1240,-170,845)])
screen=Part.Face(screenwire).extrude(V(4.544,0,2.086))
add('Windscreen_STUDY',screen,'BodyStudy','PROPOSED5mm swept screen; optical/mount/buffeting checks unresolved',color=(.6,.8,.85))
for side in [-1,1]:
    panel=Part.makeLoft([section(570,182,190,670),section(800,195,170,760),section(1000,190,270,790)],True,True)
    # One common outer skin above is the style envelope; do not duplicate two full solids.
    if side==-1:break
frontFender=Part.makeCylinder(323,150,V(1480,-75,299.9),V(0,1,0)).cut(Part.makeCylinder(315,150,V(1480,-75,299.9),V(0,1,0)))
frontFender=frontFender.common(box(1220,-90,480,520,180,180))
add('Front_fender_STUDY',frontFender,'BodyStudy','Proposed fender; full steering/bump mounts not validated',color=(.18,.2,.22))
add('Headlamp_installation_STUDY',box(1210,-105,760,80,210,48),'BodyStudy','Lamp location reservation; approved lamp optical unit not selected',color=(.82,.88,.92))
add('Taillamp_installation_STUDY',box(-145,-65,790,22,130,20),'BodyStudy','Tail stop lamp location reservation; approved optical unit not selected',color=(.7,.08,.05))
for side in [-1,1]:
    tube(f'Mirror_stalk_{side}'.replace('-','m'),(1030,side*290,1080),(1010,side*400,1190),6,3,'BodyStudy')
    mirror=Part.makeEllipsoid(55,18,32,V(1010,side*415,1205)) if False else box(970,side*415-16,1175,95,32,55)
    add(f'Mirror_body_{side}'.replace('-','m'),mirror,'BodyStudy','Mirror body reserve; regulatory field of view/approved assembly unselected',color=(.17,.18,.20))
# Suspension/brake/control interfaces, all unsourced custom dimensions tagged.
for side in [-1,1]:
    axle=V(1480,side*100,299.9);up=V(-math.sin(math.radians(25)),0,math.cos(math.radians(25)))
    add(f'Fork_lower_casting_{side}'.replace('-','m'),cyl(tuple(axle),tuple(axle+up*310),29,21),'RunningGear','Proposed lower casting envelope; actual matched OEM casting CAD required')
    add(f'Front_caliper_reserve_{side}'.replace('-','m'),box(1325,side*90-22,310,85,44,130),'RunningGear','Kawasaki43080-0177/0178candidate body RESERVE, not measured geometry or approved carrier',color=(.25,.26,.28))
    add(f'Hand_grip_reserve_{side}'.replace('-','m'),cyl((970,side*290,1060),(970,side*410,1060),17),'RunningGear','Grip reference; actual dual-channel throttle and left grip unselected',color=(.08,.09,.1))
    add(f'Front_indicator_reserve_{side}'.replace('-','m'),box(1240,side*200-14,785,50,28,25),'BodyStudy','Lamp position reservation, actual approved unit unselected',color=(.87,.5,.12))
    add(f'Rear_indicator_reserve_{side}'.replace('-','m'),box(-120,side*190-14,765,45,28,25),'BodyStudy','Lamp position reservation; visibility and mounting unvalidated',color=(.87,.5,.12))
add('Rear_caliper_reserve',box(-130,85,310,85,50,95),'RunningGear','Kawasaki43080-0156candidate right-side installation reserve; actual holder and hose route required')
add('Display_reserve',box(1045,-70,970,70,140,50),'RunningGear','Instrument installation reserve; selected display and sightline unvalidated',color=(.15,.18,.2))
# Pitch geometry only, NOT a selected tooth profile or manufactured pulley.
ratio=3.1;pitch=14.0;front_radius=20*pitch/(2*math.pi);rear_radius=62*pitch/(2*math.pi)
for name,x,z,radius in [('Front',540,470,front_radius),('Rear',0,311.9,rear_radius)]:
    add(name+'_pulley_PITCH_STUDY',cyl((x,-225,z),(x,-197,z),radius,20),'Drive','14mm/20:62 mathematical ratio study; no available belt/tooth profile/width/shaft adapter selected',color=(.3,.32,.34))
dx=540;dz=470-311.9;distance=math.hypot(dx,dz);theta=math.atan2(dz,dx);phi=math.acos((rear_radius-front_radius)/distance)
points=[]
for sign in [-1,1]:
    ang=theta+sign*phi
    p1=V(rear_radius*math.cos(ang),-211,311.9+rear_radius*math.sin(ang))
    p2=V(540+front_radius*math.cos(ang),-211,470+front_radius*math.sin(ang))
    add(f'Belt_tangent_study_{sign}'.replace('-','m'),cyl(tuple(p1),tuple(p2),4),'Drive','Pitchline/tangent visualization only; not actual belt crosssection, integer length or guard',color=(.08,.09,.1))
notes=D.addObject('Spreadsheet::Sheet','DesignStatus')
for i,t in enumerate(['BAVUSO V1.0 ENGINEERING DEVELOPMENT - NOT BUILD RELEASE',
 'Units mm; Xforward,Yleft,Zup; rearcontactorigin',
 '700catalog-max cell bodies100s7p; tab/thermal/clamping unresolved',
 'Motor/inverter actual manufacturer STEP; revision and mounting unresolved',
 '1480mm wheelbase COMPACT REWORK; geometry proposal, NOT owner approval',
 'Custom chassis and OEM runninggear representations NOT production drawings',
 'See v1.0/README.md, geometry-audit.json and component-status.csv'],1):notes.set(f'A{i}',t)
notes.setColumnWidth('A',900)
D.recompute()
validity=[]
for o in D.Objects:
    if o.Name in {r['id'] for r in records} and hasattr(o,'Shape'):
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
native=R/'cad/Bavuso-V1.0-rework.FCStd';D.saveAs(str(native))
visible=[D.getObject(r['id']) for r in records if r['group']!='Keepouts' and r['id']!='Body_surface_DIRECTION_ONLY']
Part.export(visible,str(R/'cad/Bavuso-V1.0-rework.step'))
audit=dict(release_state='ENGINEERING DEVELOPMENT; no build authorization',parameters=P,
 actual_supplier_geometry=['EMRAX208LC2022','CM200manufacturerCAD'],
 solid_objects=len(validity),total_solids=sum(r['solids'] for r in records),shape_validity=validity,
 cell_count=len(cells),all_cell_vertices_inside_inner_case=cellcontain,critical_pair_checks=checks,
 checks_passed=sum(c['passed'] for c in checks),checks_total=len(checks),
 exclusions=['steering lock','rear droop','tire growth','real fork/yoke/hub dimensions','fullframe clash resolution','tab joining','wiring','hoses','mounts','structure','CFD','test validation'])
for file,rows in [('cell-placement-rework.csv',cellmap),('component-status-rework.csv',records)]:
    with (R/file).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(R/'geometry-rework-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k not in ['shape_validity','parameters']},indent=2),flush=True)

