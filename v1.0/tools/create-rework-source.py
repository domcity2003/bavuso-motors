"""Preserve original study and derive compact rework source; fail on stale anchors."""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'build-v1.py').read_text(encoding='utf-8-sig')
def replace(a,b):
    global s
    if a not in s:raise RuntimeError('Missing source anchor '+a[:80])
    s=s.replace(a,b)
replace("A.newDocument('Bavuso_V1_Development')","A.newDocument('Bavuso_Compact_Development')")
replace("D.Label='Bavuso V1.0 - ENGINEERING DEVELOPMENT'","D.Label='Bavuso compact rework - IN DEVELOPMENT'")
replace('wheelbase_mm=1640,pack_origin_mm=[570,-110,160],pack_outer_mm=[690,220,550]','wheelbase_mm=1480,pack_origin_mm=[580,-165,150],pack_outer_mm=[420,330,570]')
replace('seat_reference_mm=[470,0,850]','seat_reference_mm=[470,0,805]')
replace('grip_reference_mm=[1050,340,1120]','grip_reference_mm=[970,340,1060]')
replace('cell_max_catalog_dimensions_mm=[126.4,8.55,43.2]','cell_max_catalog_dimensions_mm=[8.55,126.4,43.2]')
replace('cell_pitch_mm=[132,10,50]','cell_pitch_mm=[10,144,50]')
replace("physical_cartridge='5 series columns X, 2 series rows Z, 7 parallel cells Y; 10s7p'","physical_cartridge='2 series columns Y, 5 series rows Z, 7 parallel cells X; 10s7p'")
replace("cartridge_placement='2 Y columns and 5 Z tiers; NOT electrical joining or insulation design'","cartridge_placement='5 X columns and 2 Z tiers; NOT electrical joining or insulation design'")
replace('[590,-94.1,750]','[600,-94.1,740]')
replace('box(940,-112,750,373,224,76.5)','box(620,-112,857,373,224,76.5)')
start=s.index('for tier in range(5):');end=s.index('outer=box(',start)
s=s[:start]+'''for tier in range(2):
  for column in range(5):
    module=tier*5+column+1;shapes=[]
    for row in range(5):
      for lane in range(2):
        series=(module-1)*10+row*2+lane+1
        for parallel in range(7):
          x=595+column*75+parallel*10;y=-135.2+lane*144;z=165+tier*260+row*50
          q=box(x,y,z,8.55,126.4,43.2);shapes.append(q);cells.append(q)
          cellmap.append(dict(cell_id=f'S{series:03d}P{parallel+1}',series_group=series,parallel_position=parallel+1,
                              cartridge=module,x_mm=x,y_mm=y,z_mm=z,length_mm=8.55,width_mm=126.4,height_mm=43.2))
    add(f'Cartridge_{module:02d}_10s7p',Part.makeCompound(shapes),'Energy','70 CATALOG MAX pouch bodies at30%SOC, rotated; physical joining/compression/cooling unresolved',cell_source,(.78,.57,.24))
''' + s[end:]
replace('outer=box(570,-110,160,690,220,550)','outer=box(580,-165,150,420,330,570)')
replace('inner=box(573,-107,163,684,214,544)','inner=box(583,-162,153,414,324,564)')
replace("wheel('Front',1640,299.9,120,299.9,True)","wheel('Front',1480,299.9,120,299.9,True)")
replace('fx=1640-125*math.sin','fx=1480-125*math.sin')
replace('y=side*145','y=side*195')
replace('pts=[(490,y,490),(570,y,760),(1280,y,735),(1344,side*35,850)]','pts=[(490,y,490),(580,y,760),(1050,y,780),(1184,side*35,850)]')
replace('lower=[(490,y,490),(575,y,140),(1265,y,140),(1344,side*35,850)]','lower=[(490,y,490),(575,y,130),(1015,y,130),(1184,side*35,850)]')
replace("(570,y,760),(-100,y,850)","(580,y,760),(-80,side*125,825)")
replace("(490,y,490),(160,y,825)","(490,y,490),(160,side*145,805)")
replace('(1320,side*100,985),(1640,side*100,299.9)','(1160,side*100,985),(1480,side*100,299.9)')
replace("tube('Head_tube',(1344,0,850),(1283,0,980),31,25)","tube('Head_tube',(1184,0,850),(1123,0,980),31,25)")
replace('box(1120,side*190-25,390,110,50,250)','box(1020,side*190-25,390,110,50,250)')
replace('(1220,0,1060),(1050,side*340,1120)','(1110,0,990),(970,side*340,1060)')
start=s.index('# Exterior lofts');end=s.index("notes=D.addObject",start)
s=s[:start]+'''# Smooth exterior study derived from selected minimal upright reference.
# These surfaces retain explicit styling status: no CFD/manufacturing claims.
def section(x,w,bottom,top):
    h=top-bottom;mid=(top+bottom)/2
    points=[V(x,0,top),V(x,w*.75,top-.06*h),V(x,w,top-.25*h),
            V(x,w,bottom+.25*h),V(x,w*.65,bottom),V(x,-w*.65,bottom),
            V(x,-w,bottom+.25*h),V(x,-w,top-.25*h),V(x,-w*.75,top-.06*h)]
    curve=Part.BSplineCurve();curve.interpolate(points,PeriodicFlag=True)
    return Part.Wire(curve.toShape())
envelope=Part.makeLoft([section(550,175,150,750),section(750,192,150,875),
                       section(990,194,170,930),section(1140,175,460,890),
                       section(1260,135,700,860)],True,False)
# Remove installation volumes to expose underlying packaging in section.
body=envelope.cut(outer)
add('Body_surface_DIRECTION_ONLY',body,'BodyStudy','PROPOSED flowing exterior; correct reference intent only, not wall-thickness/tooling/CFD definition',color=(.18,.2,.22),hide=True)
seat=Part.makeLoft([section(-80,80,815,865),section(150,145,805,875),
                   section(340,150,775,825),section(480,135,770,820),section(580,105,785,835)],True,False)
add('Seat_foam_STUDY',seat,'BodyStudy','PROPOSED shaped two-level saddle; broad fit, pan, foam and supports unresolved',color=(.12,.13,.14))
tail=Part.makeLoft([section(-130,50,785,820),section(120,150,770,835),section(360,143,755,790)],True,False)
add('Tail_body_STUDY',tail,'BodyStudy','Proposed compact tail shell; passenger rating not established',color=(.18,.2,.22))
# Sloped clear screen, blended upper fairing, wheel-cover and light references.
screen=Part.makeLoft([section(1240,170,845,850),section(1100,155,1150,1155)],True,False)
add('Windscreen_STUDY',screen,'BodyStudy','PROPOSED5mm swept screen; optical/mount/buffeting checks unresolved',color=(.6,.8,.85))
for side in [-1,1]:
    panel=Part.makeLoft([section(570,182,190,670),section(800,195,170,760),section(1000,190,270,790)],True,False)
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
''' + s[end:]
replace('1640mm wheelbase proposal: longer than B0, packaging trade, NOT owner approval','1480mm wheelbase COMPACT REWORK; geometry proposal, NOT owner approval')
replace("native=R/'cad/Bavuso-V1.0-development.FCStd';D.saveAs(str(native))","native=R/'cad/Bavuso-V1.0-rework.FCStd';D.saveAs(str(native))")
replace("R/'cad/Bavuso-V1.0-development.step'","R/'cad/Bavuso-V1.0-rework.step'")
replace("('cell-placement.csv',cellmap),('component-status.csv',records)","('cell-placement-rework.csv',cellmap),('component-status-rework.csv',records)")
replace("R/'geometry-audit.json'","R/'geometry-rework-audit.json'")
replace("if hasattr(o,'Shape'):","if o.Name in {r['id'] for r in records} and hasattr(o,'Shape'):")
replace('pivot_mm=[490,0,490]','pivot_mm=[540,0,470]')
replace('pivot=V(490,0,490);arm=math.hypot(490,490-311.9)','pivot=V(540,0,470);arm=math.hypot(540,470-311.9)')
replace('rx=490-math.sqrt(arm*arm-(rz-490)**2)','rx=540-math.sqrt(arm*arm-(rz-470)**2)')
s=s.replace('(490,y,490)','(540,y,470)').replace('(490,side*125,490)','(540,side*125,470)')
replace('(490,-180,490),(490,180,490)','(540,-180,470),(540,180,470)')
replace("sides=[-1,1] if front else[-1]","sides=[-1,1] if front else[1]")
replace('shock=cyl((340,0,780),(500,0,530),45)',"shock=cyl((400,150,679.392),(300,150,399.733),45)")
replace("add('Shock_visual',cyl((340,0,780),(500,0,530),24),'Chassis','VISUAL ONLY; Ka736 piston46mm is not outerbody; mounts and2.41 leverage unresolved',color=(.75,.65,.2))",'''upper=V(400,150,679.392);lower=V(300,150,399.733);axis=(lower-upper);axis.normalize()
add('Shock_body_STUDY',cyl(tuple(upper+axis*25),tuple(upper+axis*205),26),'Chassis','297mm mounted length and54mm catalogue stroke reference; body dimensions illustrative; not supplier CAD',color=(.6,.61,.63))
add('Shock_rod_STUDY',cyl(tuple(upper+axis*180),tuple(lower-axis*12),8),'Chassis','Illustrative damper shaft; spring/damper sizing not approved',color=(.78,.79,.8))
for name,eye in [('Upper',upper),('Lower',lower)]:
    add('Shock_'+name+'_eye_STUDY',cyl((eye.x,140,eye.z),(eye.x,160,eye.z),15,5),'Chassis','Illustrative eye and10mm reference hole; actual joint dimensions unknown')
helix=Part.makeHelix(18,180,34)
profile=Part.Wire(Part.makeCircle(4,V(34,0,0),V(0,1,0)))
spring=Part.Wire(helix.Edges).makePipeShell([profile],True,True)
spring.Placement=A.Placement(upper+axis*25,A.Rotation(V(0,0,1),axis))
add('Shock_spring_STUDY',spring,'Chassis','Visual coil only; required spring rate differs from KA736 stock130N/mm; see suspension study',color=(.75,.65,.2))''')
# Exact steering centerline relation to the proposed loaded-radius/trail study.
replace("tube('Head_tube',(1184,0,850),(1123,0,980),31,25)","tube('Head_tube',(1580-850*math.tan(math.radians(25)),0,850),(1580-980*math.tan(math.radians(25)),0,980),31,25)")
replace('(1160,side*100,985),(1480,side*100,299.9)','(1480-(985-299.9)*math.tan(math.radians(25)),side*100,985),(1480,side*100,299.9)')
# Lower fork castings and yoke/controls reserves make assembly interfaces visible.
anchor="notes=D.addObject('Spreadsheet::Sheet','DesignStatus')"
extra='''# Suspension/brake/control interfaces, all unsourced custom dimensions tagged.
for side in [-1,1]:
    axle=V(1480,side*100,299.9);up=V(-math.sin(math.radians(25)),0,math.cos(math.radians(25)))
    add(f'Fork_lower_casting_{side}'.replace('-','m'),cyl(tuple(axle),tuple(axle+up*310),29,21),'RunningGear','Proposed lower casting envelope; actual matched OEM casting CAD required')
    add(f'Front_caliper_reserve_{side}'.replace('-','m'),box(1325,side*90-22,310,85,44,130),'RunningGear','Kawasaki43080-0177/0178candidate body RESERVE, not measured geometry or approved carrier',color=(.25,.26,.28))
    add(f'Hand_grip_reserve_{side}'.replace('-','m'),cyl((970,side*290,1060),(970,side*410,1060),17),'RunningGear','Grip reference; actual dual-channel throttle and left grip unselected',color=(.08,.09,.1))
    add(f'Front_indicator_reserve_{side}'.replace('-','m'),box(1240,side*200-14,785,50,28,25),'BodyStudy','Lamp position reservation, actual approved unit unselected',color=(.87,.5,.12))
    add(f'Rear_indicator_reserve_{side}'.replace('-','m'),box(-120,side*190-14,765,45,28,25),'BodyStudy','Lamp position reservation; visibility and mounting unvalidated',color=(.87,.5,.12))
add('Rear_caliper_reserve',box(-130,85,310,85,50,95),'RunningGear','Kawasaki43080-0156candidate right-side installation reserve; actual holder and hose route required')
add('Display_reserve',box(1045,-70,970,70,140,50),'RunningGear','Instrument installation reserve; selected display and sightline unvalidated',color=(.15,.18,.2))
''' + anchor
replace(anchor,extra)
# The compact pack can move forward90mm, allowing motor/output coaxial with pivot.
replace('motor_axis_mm=[440,0,340]','motor_axis_mm=[540,0,470]')
replace('pack_origin_mm=[580,-165,150]','pack_origin_mm=[670,-165,150]')
replace('440-(b.XMin+b.XMax)/2','540-(b.XMin+b.XMax)/2')
replace('340-(b.ZMin+b.ZMax)/2','470-(b.ZMin+b.ZMax)/2')
replace('x=595+column*75+parallel*10','x=685+column*75+parallel*10')
replace('outer=box(580,-165,150,420,330,570)','outer=box(670,-165,150,420,330,570)')
replace('inner=box(583,-162,153,414,324,564)','inner=box(673,-162,153,414,324,564)')
replace('[600,-94.1,740]','[690,-94.1,740]')
replace('box(620,-112,857,373,224,76.5)','box(700,-112,857,373,224,76.5)')
replace("tube('Pivot_reference',(540,-180,470),(540,180,470),18,10)",'''stubs=[]
for side in [-1,1]:
    a=(540,side*110,470);b=(540,side*150,470)
    stub=cyl(a,b,20,15);stubs.append(stub)
    add(f'Independent_hollow_pivot_stub_{side}'.replace('-','m'),stub,'Chassis','Proposed40OD30ID fixed frame stub; rotor adapter passes separately, actual loads/fits not approved')
    bearing=cyl((540,side*125,470),(540,side*140,470),34,20)
    add(f'Pivot_6008_size_reference_{side}'.replace('-','m'),bearing,'Chassis','6008 dimensional reference40x68x15; load/life/oscillation/seal/retention selection open','https://cdn.skfmediahub.skf.com/api/public/0901d196802809de/pdf_preview_medium/0901d196802809de_pdf_preview_medium.pdf')
pivotStudy=add('Pivot_reference',Part.makeCompound(stubs),'Keepouts','Independent outboard pivots; no shaft through motor/stator',hide=True)''')
# A thin periodic spline loft is not a valid screen. Use a planar extruded panel.
replace("screen=Part.makeLoft([section(1240,170,845,850),section(1100,155,1150,1155)],True,False)",'''screenwire=Part.makePolygon([V(1240,-170,845),V(1240,170,845),V(1100,155,1150),V(1100,-155,1150),V(1240,-170,845)])
screen=Part.Face(screenwire).extrude(V(4.544,0,2.086))''')
# Coaxial drive keeps final center distance constant; no unsupported fixed-belt motion.
drive='''# Pitch geometry only, NOT a selected tooth profile or manufactured pulley.
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
''' + anchor
replace(anchor,drive)
# Separate body panels from the installation volumes: a skin cannot be a solid filler.
replace("envelope=Part.makeLoft([section(550,175,150,750),section(750,192,150,875),\n                       section(990,194,170,930),section(1140,175,460,890),\n                       section(1260,135,700,860)],True,False)\n# Remove installation volumes to expose underlying packaging in section.\nbody=envelope.cut(outer)",'''body_sections=[(550,195,150,750),(630,220,150,980),(850,225,150,990),
               (1050,215,250,990),(1170,185,500,900),(1260,145,700,860)]
envelope=Part.makeLoft([section(*q) for q in body_sections],True,True)
inside=Part.makeLoft([section(x,w-3,b+3,t-3) for x,w,b,t in body_sections],True,True)
body=envelope.cut(inside)
for side in [-1,1]:
    vent=box(1015,165 if side==1 else -250,385,130,85,260)
    body=body.cut(vent)''')
# Ruled lofts preserve smooth section profiles without uncontrolled between-section overshoot.
s=s.replace('],True,False)','],True,True)')
(R/'build-compact-rework.py').write_text(s,encoding='utf-8')
print('Compact source created; original study preserved')
