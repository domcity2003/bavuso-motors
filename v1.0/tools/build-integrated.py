"""V1.0 integrated development model. Run with bundled FreeCAD Python.

Builds on build-compact-rework.py (left untouched) and adds:
  - the lower stepped 700-cell pack from cell-layout-proposal.json
  - the EMRAX 208 placed by its rotor-axis transform (motor-pivot-interface.md)
  - the actual Orion BMS2 108 supplier solid, moved out from under the seat
  - a protected HV cabinet with GX14 drawing-outline contactors
  - bodywork, seat and tail shaped from design/baseline black.png
Real supplier imports and explicitly provisional custom geometry; not a build release.
"""
from pathlib import Path
import json, math, csv, itertools, os
import FreeCAD as A
import Part

R=Path(__file__).resolve().parents[1]
D=A.newDocument('Bavuso_Integrated_Development')
D.Label='Bavuso V1.0 integrated - IN DEVELOPMENT'
V=A.Vector
groups={}
records=[]
def group(name):
    g=D.addObject('App::DocumentObjectGroup',name);groups[name]=g;return g
for n in ['Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy','Keepouts']:group(n)
def add(name,shape,g,basis,source='',color=(.35,.38,.42),hide=False):
    o=D.addObject('Part::Feature',name)
    o.Label=name.replace('_',' ');o.Shape=shape
    for prop,value in [('Definition',basis),('Source',source),('ReleaseState','DEVELOPMENT - NOT FOR FABRICATION')]:
        o.addProperty('App::PropertyString',prop,'Bavuso');setattr(o,prop,value)
    o.addProperty('App::PropertyVector','RenderColor','Bavuso');o.RenderColor=V(*color)
    groups[g].addObject(o)
    records.append(dict(id=name,group=g,basis=basis,source=source,solids=len(shape.Solids),volume_mm3=shape.Volume,hidden=hide))
    return o
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(a,b,r,inner=0):
    a,b=V(*a),V(*b);d=b-a;s=Part.makeCylinder(r,d.Length,a,d)
    return s.cut(Part.makeCylinder(inner,d.Length,a,d)) if inner else s
frame_segs=[]
def tube(name,a,b,ro,ri,g='Chassis'):
    if g=='Chassis' and name.split('_')[0] in ('Upper','Lower','Tail'):frame_segs.append((a,b))
    return add(name,cyl(a,b,ro,ri),g,'PROPOSED centerline and section; material/joints/fatigue NOT qualified',color=(.1,.105,.11))
def sname(base,side):return f'{base}_{side}'.replace('-','m')

P=dict(wheelbase_mm=1480,motor_axis_mm=[540,0,470],pivot_mm=[540,0,470],rear_tire_radius_mm=311.9,
       front_tire_radius_mm=299.9,front_travel_mm=125,rear_vertical_travel_mm=130,rake_deg=25,
       steering_axis_lower_mm=[1206.954,0,800],steering_axis_upper_mm=[1132.345,0,960],
       seat_top_rider_mm=[486,0,800],grip_reference_mm=[880,350,1045],peg_reference_mm=[500,190,380],
       body_reference='design/baseline black.png; 1,480 mm wheelbase spans 1,097 px, so 1.35 mm/px',
       pack='cell-layout-proposal.json stepped profile, 100s7p, 700 cells')

# ---------------------------------------------------------------- energy: stepped pack
L=json.loads((R/'cell-layout-proposal.json').read_text(encoding='utf-8'))
# Revision to the proposal: the EMRAX STEP carries a square 6mm plate (solid 84, +-105.75 corners) that
# the 105.75mm circle screen missed; its corner reached X645.75/Z364.25 inside the 623/374 step.
# Move one 7p stack from column 2 (21->14 layers) to column 8 (35->42); rear roof becomes flat at 344
# and the front step moves from X922 to X972. Still 100 groups x 7 = 700 cells.
L['layers_per_column']=[14,14,42,42,42,42,42,42,35,35]
L['outer_xz_polygon_mm']=[[560,150],[1075,150],[1075,515],[972,515],[972,580],[670,580],[670,344],[560,344]]
cells_spec=[]
series=0
for col,(cx,layers) in enumerate(zip(L['column_x_mm'],L['layers_per_column'])):
    for lane,cy in enumerate(L['transverse_lane_origins_mm']):
        for layer in range(layers):
            if layer%7==0:series+=1
            cells_spec.append(dict(id=f'S{series:03d}P{layer%7+1}',series=series,parallel=layer%7+1,column=col,transverse_lane=lane,
                                   x_mm=cx,y_mm=cy,z_mm=L['z_origin_mm']+layer*L['z_pitch_mm'],size_xyz_mm=L['cell_orientation_xyz_mm']))
assert series==100 and len(cells_spec)==700
L['cells']=cells_spec
P['pack_revision']='one 7p stack moved column 2 -> 8; rear roof 344, front step X972 (motor plate clearance)'
poly=[V(x,0,z) for x,z in L['outer_xz_polygon_mm']]
face=Part.Face(Part.makePolygon(poly+[poly[0]]))
y0,y1=L['outer_y_min_max_mm'];wall=L['provisional_shell_thickness_mm']
def extrude_xz(f,ya,yb):
    s=f.copy();s.translate(V(0,ya,0));return s.extrude(V(0,yb-ya,0))
outer=extrude_xz(face,y0,y1)
inner_face=face.makeOffset2D(-wall,join=2)
inner=extrude_xz(inner_face,y0+wall,y1-wall)
case=add('Pack_case_stepped_3mm_STUDY',outer.cut(inner),'Energy',
         'PROPOSED 3mm stepped shell from lower-pack-layout-study.md; no lid, joints, mounts, vent or thermal qualification',
         color=(.45,.48,.5))
add('Battery_installation_keepout',outer,'Keepouts','Stepped outer battery boundary incl. motor cutout',hide=True)
cell_source='https://amprius.com/documents/Amprius_Product_Catalog.pdf#page=52'
cells=[];cellmap=[];bycol={}
for c in L['cells']:
    sx,sy,sz=c['size_xyz_mm'];q=box(c['x_mm'],c['y_mm'],c['z_mm'],sx,sy,sz)
    cells.append(q);bycol.setdefault(c['column'],[]).append(q)
    cellmap.append(dict(cell_id=c['id'],series_group=c['series'],parallel_position=c['parallel'],column=c['column'],
                        lane=c['transverse_lane'],x_mm=c['x_mm'],y_mm=c['y_mm'],z_mm=c['z_mm'],
                        length_mm=sx,width_mm=sy,height_mm=sz))
for col,shapes in sorted(bycol.items()):
    add(f'Cell_column_{col+1:02d}',Part.makeCompound(shapes),'Energy',
        f'{len(shapes)} CATALOG MAX pouch bodies lying flat; restraint/tabs/cooling unresolved',cell_source,(.78,.57,.24))

# ---------------------------------------------------------------- drive: supplier motor and inverter
motorraw=Part.read(str(R/'sources/EMRAX-208-LC-resolver-2022.step'))
ms=motorraw.copy()
# Source rotor axis is +X through Y=Z=0; +90 deg about Z sends it to vehicle +Y, then
# vehicleX=540-sourceY, vehicleY=sourceX-43.927, vehicleZ=470+sourceZ (motor-pivot-interface.md).
ms.Placement=A.Placement(V(540,-43.9269610015,470),A.Rotation(V(0,0,1),90)).multiply(ms.Placement)
add('EMRAX_208_LC_supplier_STEP',ms,'Drive','ACTUAL supplier STEP 2022; rotor axis on pivot X540/Z470, output face toward -Y (belt side)',
    'https://emrax.com/wp-content/uploads/2022/05/208_lc_resolver.step',(.8,.45,.17))
invraw=Part.read(str(next((R/'sources/CM200').glob('*.STEP'))))
def place_min(s,target,rotation=None):
    s=s.copy()
    if rotation:s.Placement=A.Placement(V(),rotation).multiply(s.Placement)
    b=s.BoundBox;s.translate(V(target[0]-b.XMin,target[1]-b.YMin,target[2]-b.ZMin));return s
# Electronics stack in the tank space above the lowered pack, bottom to top:
# charger Z590-666.5, inverter Z675-772, BMS Z780-852.6. Each level stays behind the steering sweep.
invs=place_min(invraw,[700,-94.1,675],A.Rotation(V(1,1,1),120))
add('Cascadia_CM200_supplier_STEP',invs,'Electronics','ACTUAL manufacturer CM200 CAD; middle level of the tank stack, rear end near motor phases; connector/service clearances unverified',
    'https://www.cascadiamotion.com/cm-200',(.2,.5,.65))
charger=box(700,-112,590,373,224,76.5)   # 7mm ahead of the tank rear wall
add('BROGEN_PV1776_body',charger,'Electronics','CATALOG body dimensions only, 10mm above pack roof; mounting, ports and revision unverified',
    'https://www.brogenmotors.com/wp-content/uploads/2024/06/Requirement_SheetOBC.pdf',(.3,.65,.45))

# Actual Orion BMS2 108-cell supplier solid, flat orientation from inspect-bms-and-protection.py.
bmsraw=Part.read(str(R/'models/Orion-BMS2-108-installed-proposal.step'))
bb=bmsraw.BoundBox;bms=bmsraw.copy();bms.translate(V(775-bb.XMin,-(bb.YMin+bb.YMax)/2,780-bb.ZMin))
add('Orion_BMS2_108_supplier_STEP',bms,'Electronics',
    'ACTUAL Orion 108-cell enclosure STEP, unscaled; moved from under-seat (17.7mm rear-tire bump margin) to top of tank stack under the cover; carrier/heatsink/harness not modeled',
    'https://www.orionbms.com/products/orion-bms-standard/',(.15,.35,.25))

# HV cabinet behind the pack, above the motor: X515-665, Y+-150, Z588-728 (hardware-installation.md, lowered 12mm for the seat).
cab_out=box(515,-150,588,150,300,140);cab_in=box(518,-147,591,144,294,134)
cabinet=add('HV_cabinet_2mm_STUDY',cab_out.cut(cab_in),'Electronics','PROPOSED covered HV cabinet; material, seals, interlock and mounts unresolved',color=(.55,.56,.58))
for nm,x in [('positive',528),('negative',598)]:
    add(f'GX14_main_{nm}_OUTLINE',box(x,-57.4,603,59.8,114.8,57.3),'Electronics',
        'GX14 manufacturer DRAWING outline only (114.8x59.8x57.3); supplier STEP not retrieved; reverse-break duty unconfirmed',
        'https://www.sensata.com/sites/default/files/a/sensata-gigavac-gx14-series-open-contactors-datasheet.pdf',(.75,.2,.15))
add('Main_fuse_branch_search_region',box(540,80,603,110,55,70),'Keepouts','Unselected main fuse/holder region; 30EV family is comparison only',hide=True)

# Heat exchangers moved inboard under the tank sides behind side grilles (baseline image vent at X1040-1100).
for side in [-1,1]:
    ya=128 if side==1 else -178
    add(sname('Side_radiator',side),box(960,ya,600,110,50,140),'Electronics','UNSIZED side heat-exchanger/fan reservation behind body grille',color=(.4,.45,.5))

# ---------------------------------------------------------------- running gear
def wheel(name,x,z,width,r,front):
    tor=Part.makeTorus((r+215.9)/2,(r-215.9)/2,V(x,0,z),V(0,1,0))
    m=A.Matrix();m.A22=width/(r-215.9)
    tor.translate(V(-x,0,-z));tor=tor.transformGeometry(m);tor.translate(V(x,0,z))
    add(name+'_nominal_tire',tor,'RunningGear','Nominal 120/70ZR17 front or 160/60ZR17 rear; no loaded radius/growth/tread geometry',color=(.09,.1,.11))
    # Cast 17in wheel: rim barrel with bead flanges, hub, five Y-pairs of tapered flat spokes (baseline style).
    rw=width*.68
    rim=cyl((x,-rw/2,z),(x,rw/2,z),214,204)
    for s in (-1,1):rim=rim.fuse(cyl((x,s*rw/2-(4 if s>0 else 0),z),(x,s*rw/2+(0 if s>0 else 4),z),226,212))
    hubw=96 if front else 120
    hub=cyl((x,-hubw/2,z),(x,hubw/2,z),58,12)
    spokes=[]
    for k in range(5):
        for dk in (-.17,.17):
            t=k*math.tau/5+dk;c,s_=math.cos(t),math.sin(t);pc,ps=-s_,c
            pts=[(x+52*c+11*pc,z+52*s_+11*ps),(x+206*c+7*pc,z+206*s_+7*ps),(x+206*c-7*pc,z+206*s_-7*ps),(x+52*c-11*pc,z+52*s_-11*ps)]
            f=Part.Face(Part.makePolygon([V(px,-9,pz) for px,pz in pts+[pts[0]]]));spokes.append(f.extrude(V(0,18,0)))
    add(name+'_wheel_STUDY',Part.makeCompound([rim,hub]+spokes),'RunningGear','ILLUSTRATIVE cast 10-spoke 17in wheel; OEM hub/offset CAD absent',color=(.1,.105,.11))
    discR=160 if front else 120
    for side in ([-1,1] if front else [1]):
        yd=side*(hubw/2+6)
        disc=cyl((x,yd,z),(x,yd+side*5,z),discR,discR-38)
        holes=[cyl((x+(discR-19)*math.cos(k*math.tau/36),yd-10,z+(discR-19)*math.sin(k*math.tau/36)),
                   (x+(discR-19)*math.cos(k*math.tau/36),yd+10,z+(discR-19)*math.sin(k*math.tau/36)),3.2)
               for k in range(36)]
        disc=disc.cut(Part.makeCompound(holes))
        carrier=cyl((x,yd,z),(x,yd+side*5,z),discR-36,40)
        for k in range(5):
            t=k*math.tau/5+.3;carrier=carrier.cut(cyl((x+(discR-80)*math.cos(t),yd-6,z+(discR-80)*math.sin(t)),
                                                     (x+(discR-80)*math.cos(t),yd+6,z+(discR-80)*math.sin(t)),20 if front else 14))
        add(name+f'_disc_{side:+d}'.replace('+','p').replace('-','m'),disc,
            'RunningGear',f'{2*discR}mm drilled disc; thickness/offset PROPOSED',color=(.66,.67,.68))
        add(name+f'_disc_carrier_{side:+d}'.replace('+','p').replace('-','m'),carrier,'RunningGear','Floating-disc carrier, illustrative',color=(.2,.21,.22))
wheel('Rear',0,311.9,160,311.9,False)
wheel('Front',1480,299.9,120,299.9,True)
rear_sweeps=[];front_sweeps=[]
arm=math.hypot(540,470-311.9)
for i in range(21):
    t=i/20
    rz=311.9+130*t;rx=540-math.sqrt(arm*arm-(rz-470)**2)
    rear_sweeps.append(cyl((rx,-80,rz),(rx,80,rz),311.9))
    fx=1480-125*math.sin(math.radians(25))*t;fz=299.9+125*math.cos(math.radians(25))*t
    front_sweeps.append(cyl((fx,-60,fz),(fx,60,fz),299.9))
rearSweep=add('Rear_bump_sampled_keepout',Part.makeCompound(rear_sweeps),'Keepouts','21 samples, 130mm vertical travel; growth/droop absent',hide=True)
frontSweep=add('Front_bump_sampled_keepout',Part.makeCompound(front_sweeps),'Keepouts','21 samples, 125mm at 25deg; steering sweep NOT included',hide=True)
# Steering sweep: fork legs sit 106mm off the steering axis; a 140mm cylinder bounds them at any lock.
sa=V(*P['steering_axis_lower_mm']);sb=V(*P['steering_axis_upper_mm']);sd=sb-sa;sd.normalize()
steer_lo=sa-sd*260;steer_hi=sa+sd*330
steerKeep=add('Steering_sweep_keepout',Part.makeCylinder(140,(steer_hi-steer_lo).Length,steer_lo,sd),'Keepouts',
              'Envelope of fork legs/clamps about steering axis at any lock; body is cut to it',hide=True)

# ---------------------------------------------------------------- chassis (Codex rework frame, rails re-routed for body/seat)
for side in [-1,1]:
    y=side*195
    for i,(a,b) in enumerate([((540,y,470),(580,y,740)),((580,y,740),(1050,y,780)),((1050,y,780),(1184,side*35,850))]):
        tube(sname(f'Upper_rail_{i}',side),a,b,16,13.5)
    # Lower rails beside the pack at Z250 instead of under it at Z130 (raises the frame off the ground line);
    # the down tube kinks at X1110/Z420 so it turns inboard only ahead of the pack front wall.
    yl=side*190   # 9mm outside the pack wall (Y+-165), 13mm inside the battery-cover skin
    for i,(a,b) in enumerate([((540,y,470),(575,yl,250)),((575,yl,250),(1015,yl,250)),((1015,yl,250),(1110,yl,420)),
                              ((1110,yl,420),(1184,side*35,850))]):
        tube(sname(f'Lower_rail_{i}',side),a,b,16,13.5)
    tube(sname('Tail_rail',side),(580,y,715),(-60,side*100,780),14,12)
    tube(sname('Tail_brace',side),(540,y,470),(160,side*144,740),14,12)
    # Box-section swingarm arm, 74x34 at the pivot tapering to 52x30 at the axle (loft of two sections).
    adir=V(0,side*125,311.9)-V(540,side*125,470);alen=adir.Length;adir.normalize();an=V(-adir.z,0,adir.x)
    if an.z<0:an=-an
    def sect(p,h,w):
        q=[p+an*(h/2)+V(0,w/2,0),p+an*(h/2)-V(0,w/2,0),p-an*(h/2)-V(0,w/2,0),p-an*(h/2)+V(0,w/2,0)]
        return Part.makePolygon(q+[q[0]])
    arm_=Part.makeLoft([sect(V(540,side*125,470)+adir*30,92,34),sect(V(0,side*125,311.9)-adir*30,58,30)],True)
    arm_=arm_.fuse(cyl((540,side*108,470),(540,side*142,470),38)).fuse(cyl((0,side*110,311.9),(0,side*140,311.9),32))
    add(sname('Swingarm',side),arm_,'Chassis','PROPOSED box-section swingarm arm; section/fatigue NOT qualified',color=(.13,.14,.15))
head_lo=sa-sd*30;head_hi=sa+sd*200
add('Head_tube',cyl(tuple(head_lo),tuple(head_hi),31,25),'Chassis','Head tube on steering axis; bearing seats unresolved')
add('Swingarm_cross_brace',cyl((380,-110,423),(380,110,423),20,16),'Chassis','PROPOSED cross tube ahead of the tyre (64mm off the tyre at rest)',color=(.13,.14,.15))
# Upside-down fork built in the steering frame: local Z along the steering axis from the lower axis point,
# local X forward-perpendicular. Tubes sit 36.1mm ahead of the axis (from the 1480mm wheelbase geometry).
steer_pl=A.Placement(sa,A.Rotation(V(0,1,0),-25))
def steer(shape):s=shape.copy();s.Placement=steer_pl.multiply(s.Placement);return s
off=36.1;w_axle=-568.5
for side in [-1,1]:
    yo=side*100
    add(sname('Fork_outer_tube',side),steer(cyl((off,yo,-215),(off,yo,240),28)),'RunningGear','USD outer tube, illustrative; supplier fork not selected',color=(.07,.07,.08))
    add(sname('Fork_inner_tube',side),steer(cyl((off,yo,-525),(off,yo,-210),22)),'RunningGear','USD chrome inner tube, illustrative',color=(.8,.81,.82))
    foot=steer(cyl((off,yo,-600),(off,yo,-410),27).fuse(Part.makeCylinder(30,70,V(off,yo-35,w_axle),V(0,1,0))))
    add(sname('Fork_axle_clamp',side),foot,'RunningGear','USD axle foot with caliper lugs, illustrative',color=(.09,.09,.1))
def clamp(w0,t):
    c=cyl((0,0,w0),(0,0,w0+t),36)
    for s in (-1,1):c=c.fuse(cyl((off,s*100,w0),(off,s*100,w0+t),36))
    return c.fuse(box(-10,-100,w0,off+20,200,t)).cut(Part.makeCompound([cyl((off,s*100,w0-1),(off,s*100,w0+t+1),28) for s in (-1,1)]))
add('Lower_triple_clamp',steer(clamp(-62,28)),'RunningGear','Lower triple clamp, illustrative',color=(.12,.12,.13))
add('Upper_triple_clamp',steer(clamp(205,22)),'RunningGear','Upper triple clamp, illustrative',color=(.12,.12,.13))
for s in (-1,1):add(sname('Bar_riser',s),steer(cyl((-14,s*40,227),(-14,s*40,262),14)),'RunningGear','Bar riser, illustrative',color=(.1,.1,.11))
stubs=[]
for side in [-1,1]:
    stub=cyl((540,side*110,470),(540,side*150,470),20,15);stubs.append(stub)
    add(sname('Independent_hollow_pivot_stub',side),stub,'Chassis','Proposed 40OD/30ID fixed frame stub; loads/fits not approved')
    add(sname('Pivot_6008_size_reference',side),cyl((540,side*125,470),(540,side*140,470),34,20),'Chassis','6008 dimensional reference only')
add('Pivot_reference',Part.makeCompound(stubs),'Keepouts','Independent outboard pivots',hide=True)
upper=V(400,150,679.392);lower=V(300,150,399.733);axis=(lower-upper);axis.normalize()
shock=cyl(tuple(upper),tuple(lower),45)
add('Shock_and_spring_keepout',shock,'Keepouts','297mm eye distance; 90mm OD reservation',hide=True)
add('Shock_body_STUDY',cyl(tuple(upper+axis*25),tuple(upper+axis*205),26),'Chassis','Illustrative body; not supplier CAD',color=(.6,.61,.63))
add('Shock_rod_STUDY',cyl(tuple(upper+axis*180),tuple(lower-axis*12),8),'Chassis','Illustrative damper shaft',color=(.78,.79,.8))
for name,eye in [('Upper',upper),('Lower',lower)]:
    add('Shock_'+name+'_eye_STUDY',cyl((eye.x,140,eye.z),(eye.x,160,eye.z),15,5),'Chassis','Illustrative eye')
helix=Part.makeHelix(18,180,34)
spring=Part.Wire(helix.Edges).makePipeShell([Part.Wire(Part.makeCircle(4,V(34,0,0),V(0,1,0)))],True,True)
spring.Placement=A.Placement(upper+axis*25,A.Rotation(V(0,0,1),axis))
add('Shock_spring_STUDY',spring,'Chassis','Visual coil only; spring rate per suspension study',color=(.75,.65,.2))

# ---------------------------------------------------------------- bodywork from baseline image
# Each panel is the overlap of two traced outlines: the side view (XZ, from the baseline image at
# 1.35 mm/px) extruded across the bike, and the plan view (XY half-widths) extruded vertically.
# This gives the flat, faceted panels of the reference; edges are then rounded where the kernel allows.
def spline(pts):
    c=Part.BSplineCurve();c.interpolate([V(*p) for p in pts]);return c.toShape()
def closed(edges):return Part.Face(Part.Wire(Part.__sortEdges__(edges)))
def side_face(top,bot):
    """top/bot: (x,z) lists rear->front. Top is smooth, bottom is straight panel lines."""
    e=[spline([(x,0,z) for x,z in top])]
    e+=Part.makePolygon([V(x,0,z) for x,z in bot]).Edges
    for a,b in [(top[0],bot[0]),(top[-1],bot[-1])]:
        if a!=b:e.append(Part.makeLine(V(a[0],0,a[1]),V(b[0],0,b[1])))
    return closed(e)
def plan_face(half):
    e=[spline([(x,w,0) for x,w in half]),spline([(x,-w,0) for x,w in half])]
    for x,w in [half[0],half[-1]]:
        if w>0:e.append(Part.makeLine(V(x,w,0),V(x,-w,0)))
    return closed(e)
def solid(top,bot,half):
    s=side_face(top,bot);s.translate(V(0,-400,0));s=s.extrude(V(0,800,0))
    p=plan_face(half);p=p.extrude(V(0,0,1400))
    return s.common(p)
def rounded(s,r):
    try:
        f=s.makeFillet(r,s.Edges)
        if f.isValid():return f
    except Exception:pass
    return s
def panel(top,bot,half,t=3,r=12,open_bottom=False,open_top=False,open_front=False,open_rear=False,section=None):
    # section(t): optional cross-section prism (inset by t) that shapes the panel in the Y-Z plane.
    sec=section or (lambda t:None)
    def cut_sec(sol,t):return sol.common(sec(t)) if section else sol
    out=rounded(cut_sec(solid(top,bot,half),0),r)
    it=[(x,z-t) for x,z in top];ib=[(x,z+t) for x,z in bot];ih=[(x,w-t) for x,w in half]
    if open_bottom:ib=[(x,z-80) for x,z in bot]
    if open_top:it=[(x,z+80) for x,z in top]
    def shift(rows,i,dx):rows[i]=(rows[i][0]+dx,rows[i][1])
    for rows in (it,ib,ih):
        shift(rows,0,-40 if open_rear else t);shift(rows,-1,40 if open_front else -t)
    inner=cut_sec(solid(it,ib,ih),t)
    return out.cut(rounded(inner,max(r-t,1)))
# Battery-bay cross-section: full 222mm half-width down to Z228 (just under the lower rails at Z250),
# then a bevel to 175mm at the Z135 belly, like the baseline's angled belly fairing. 350mm wide underneath
# instead of 444; the pack (+-165, bottom Z150) keeps >5mm to the bevel's inner skin.
def belly_section(t=0,hw=222,hb=175,zb=228,zbot=135):
    k=(hw-hb)/(zb-zbot);y0=hb-k*zbot    # bevel line extended down to Z0
    pts=[V(0,-y0,0),V(0,y0,0),V(0,hw,zb),V(0,hw,2000),V(0,-hw,2000),V(0,-hw,zb)]
    f=Part.Face(Part.makePolygon(pts+[pts[0]]))
    if t:f=f.makeOffset2D(t,join=2)
    f.translate(V(-1000,0,0));return f.extrude(V(4000,0,0))
# Tank cross-section: full width to Z800 (top of the upper rails, Z796), then the sides lean in to 165mm
# at the tank top (Z960) where the rider's knees go. Inside, only the +-140 steering sweep rises above Z800.
def tank_section(t=0,hw=222,ht=165,zb=800,ztop=960):
    k=(hw-ht)/(ztop-zb);yh=ht-k*(1300-ztop)    # lean line extended up to Z1300
    pts=[V(0,-hw,-100),V(0,hw,-100),V(0,hw,zb),V(0,yh,1300),V(0,-yh,1300),V(0,-hw,zb)]
    f=Part.Face(Part.makePolygon(pts+[pts[0]]))
    if t:f=f.makeOffset2D(t,join=2)
    f.translate(V(-1000,0,0));return f.extrude(V(4000,0,0))
# Panels are notched around every rail centerline: 22mm = 16mm tube + 6mm.
frame_notch=Part.makeCompound([cyl(a,b,22) for a,b in frame_segs])
# Lamp reservations are pockets in the panels, so the panels are cut around them.
lamps=dict(Taillamp_installation_STUDY=box(-186,-50,806,16,100,20))
for side in [-1,1]:
    lamps[sname('Front_indicator_reserve',side)]=box(1385,side*118-14,798,40,28,20)
    lamps[sname('Rear_indicator_reserve',side)]=box(-150,side*95-14,770,40,28,22)
lamp_cut=Part.makeCompound(list(lamps.values()))
# Re-trace (Oct 26) on a 50mm grid over the baseline. The image's wheel axles sit ~35mm below the model's,
# so traced Z values carry +35mm. Tank/battery split is the baseline's slanted seam, not a flat line.
seam=[(690,668),(800,645),(900,622),(1000,600),(1095,579)]
# Upper body: tall tank (top Z955), cockpit cheeks either side of the screen, beak nose with the headlamp,
# fairing front edge dropping to Z575 ahead of the battery box. Open underneath.
upper_body=panel(top=[(690,846),(712,890),(745,928),(800,950),(900,957),(1000,955),(1060,945),(1110,937),
                      (1170,962),(1215,985),(1258,972),(1300,948),(1360,922),(1410,900),(1462,872)],
                 bot=seam[:-1]+[(1090,580),(1140,575),(1165,582),(1192,602),(1245,662),(1272,716),(1298,777),
                                (1366,798),(1420,830),(1462,846)],
                 half=[(690,215),(760,220),(850,222),(1050,222),(1200,205),(1340,160),(1420,112),(1462,40)],
                 r=15,open_bottom=True,section=lambda t:tank_section(-t))   # closed rear wall: no view into the tank beside the seat
upper_body=upper_body.cut(steerKeep.Shape).cut(frame_notch)
headlamp=box(1400,-90,833,55,180,24)
upper_body=upper_body.cut(headlamp).cut(lamp_cut)
for side in [-1,1]:
    upper_body=upper_body.cut(box(1000,side*215-30,610,110,60,120))   # side grilles in front of radiators
add('Upper_body_fairing_tank_STUDY',upper_body,'BodyStudy',
    'PROPOSED 3mm shell traced from baseline image; open below, steering cavity, frame notches and grilles cut; tooling/CFD/fixings unresolved',color=(.11,.12,.13))
# Lower body: battery side covers and belly pan, open top, open rear onto the motor.
lower_body=panel(top=[(585,668)]+seam,
                 bot=[(585,140),(700,135),(1000,135),(1092,135),(1106,200),(1108,300)],
                 half=[(585,222),(900,222),(1060,220),(1108,195)],
                 r=10,open_top=True,open_rear=True,section=lambda t:belly_section(-t))
lower_body=lower_body.cut(frame_notch)
add('Lower_body_battery_covers_STUDY',lower_body,'BodyStudy',
    'PROPOSED 3mm battery side covers/belly pan; 444mm over lower frame rails, bevelled to 350mm at the belly; impact protection unresolved',color=(.13,.14,.15))
# Floor sits 9mm under the pack's rear-bottom corner.
motor_cover=panel(top=[(470,600),(585,668)],bot=[(470,160),(585,132)],half=[(470,215),(585,222)],
                  r=8,open_top=True,open_front=True,open_rear=True,section=lambda t:belly_section(-t))
motor_cover=motor_cover.cut(frame_notch)
for side in [-1,1]:motor_cover=motor_cover.cut(cyl((500,side*140,380),(500,side*240,380),18))   # peg mount bosses pass through
# Lower rear bulkhead closes the view into the pack's rear wall; stays below the motor (Z364), belt run (Z~383)
# and swingarm (Z~412) at X470.
motor_cover=motor_cover.fuse(rounded(box(470,-212,168,3,424,177).common(belly_section(-1)),1))
add('Motor_side_covers_STUDY',motor_cover,'BodyStudy',
    'PROPOSED 3mm motor side covers/belly behind the battery covers; swingarm and shock pass the open rear; cooling/belt access unresolved',color=(.12,.13,.14))
for side in [-1,1]:
    louvres=Part.makeCompound([box(1006,side*209-4,616+k*19,98,8,7) for k in range(6)]+[box(1000,side*187.5-1.5,610,110,3,120)])  # + dark backing plate
    add(sname('Side_grille_louvres',side),louvres,'BodyStudy','Louvres in the side grille ahead of the radiators',color=(.16,.17,.18))
    # Dark trim strip inside the slanted tank/cover seam so the filleted joint does not show daylight.
    trim=Part.Face(Part.makePolygon([V(700,0,652),V(1090,0,567),V(1090,0,591),V(700,0,676),V(700,0,652)])).extrude(V(0,4,0))
    trim.translate(V(0,side*205-2,0))
    add(sname('Seam_trim',side),trim.cut(lower_body).cut(upper_body),'BodyStudy','Seam closing strip inside the tank/battery-cover joint',color=(.05,.05,.055))
# Proud side panels traced from the baseline (X=(1310-px)*1.35, Z=(935-py)*1.35): the hexagonal battery
# cover with bolts, and the angled belly fairing below it. 4mm plates with chamfered edges sit on the shell.
def proud(pts,y_in,t=4,ch=2.5):
    f=Part.Face(Part.makePolygon([V(x,0,z) for x,z in pts+[pts[0]]]));s=f.extrude(V(0,t,0))
    try:
        e=[ed for ed in s.Edges if abs(ed.BoundBox.YMin-t)<1e-6 and abs(ed.BoundBox.YMax-t)<1e-6]
        s=s.makeChamfer(ch,e)
    except Exception:pass
    return s
# Front edges stop at X~1060 where the cover still has its full 222mm half-width.
batt_pts=[(1040,578),(670,652),(600,470),(626,330),(1045,330),(1065,500)]
belly_pts=[(1050,300),(640,300),(600,215),(640,152),(1045,152),(1060,215)]
for side in [-1,1]:
    parts=[]
    for pts,yin in [(batt_pts,222),(belly_pts,222)]:
        pnl=proud(pts,yin)
        if side==1:pnl.translate(V(0,yin+.5,0))
        else:
            pnl=pnl.mirror(V(0,0,0),V(0,1,0));pnl.translate(V(0,-yin-.5,0))
        if pts is belly_pts:
            # The belly plate wraps the bevel: a 4mm skin over the cover's cross-section, clipped to the outline.
            skin=belly_section(4.5).cut(belly_section(.5))
            pr=Part.Face(Part.makePolygon([V(x,0,z) for x,z in pts+[pts[0]]]));pr.translate(V(0,0 if side>0 else -400,0))
            pnl=rounded(skin.common(pr.extrude(V(0,400,0))),1.5)
        parts.append(pnl.cut(lower_body))   # the cover's plan spline bulges past 222mm in places; panels seat on it
    add(sname('Battery_side_panel',side),parts[0],'BodyStudy','Proud battery cover plate traced from baseline; fixings/seal unresolved',color=(.085,.09,.095))
    add(sname('Belly_side_panel',side),parts[1],'BodyStudy','Proud belly fairing plate traced from baseline',color=(.1,.105,.11))
    bolts=[cyl((x,side*226.5,z),(x,side*229.5,z),5.5) for x,z in [(1020,565),(690,630),(625,455),(650,350),(1025,350),(1045,470),(850,600),(850,345)]]
    add(sname('Panel_bolts',side),Part.makeCompound(bolts).cut(lower_body),'BodyStudy','M6 button-head positions, illustrative',color=(.25,.26,.27))
# Tail and under-seat side panels, open below and toward the tank; tail tip rises above the seat end like the baseline.
# Extra top points stop the spline swinging below Z776 over the tyre (full-bump tyre top is Z754 at X-22).
# Slim tail: underside rises over the tyre to the upswept tip (walls stay 30mm+ outboard of the tyre);
# the side cover drops to Z600 under the seat front, above the shock, and meets the motor cover's top line.
tail_body=panel(top=[(-190,860),(-175,852),(-150,840),(-120,830),(-60,826),(0,815),(100,800),(300,775),(560,760),(690,768)],
                bot=[(-180,782),(-100,770),(16,752),(150,727),(280,640),(330,600),(470,600),(585,668),(690,668)],
                half=[(-190,60),(-120,98),(16,135),(150,165),(300,200),(450,212),(560,215),(690,215)],
                r=10,open_bottom=True,open_front=True).cut(frame_notch).cut(lamp_cut)
# Thick stepped saddle: pillion pad Z889 stepping down at X284 to the rider dip at Z800 (traced +35mm).
seat=rounded(solid(top=[(-112,862),(-100,874),(-20,889),(100,881),(216,866),(270,856),(300,836),(351,815),
                        (420,803),(486,800),(560,802),(621,808),(682,838)],
                   bot=[(-112,822),(0,800),(300,768),(470,745),(620,745),(682,770)],
                   half=[(-112,95),(0,128),(150,140),(300,152),(470,165),(600,150),(682,115)]),20)
tail_body=tail_body.cut(seat)   # seat pan nests into the tail top
add('Tail_side_panels_STUDY',tail_body,'BodyStudy','PROPOSED 3mm subframe covers traced from baseline; passenger rating not established',color=(.11,.12,.13))
add('Seat_two_level_STUDY',seat,'BodyStudy','PROPOSED stepped rider/passenger saddle traced from baseline; foam/pan/fit unresolved',color=(.06,.065,.07))
add('Belly_skid_plate_STUDY',box(700,-150,128,320,300,4),'BodyStudy','PROPOSED 4mm skid plate under pack; ground clearance about 128mm topped-out',color=(.2,.21,.22))
# Screen, lamps, mirrors, controls.
sp=[V(1388,-118,898),V(1388,118,898),V(1128,145,1222),V(1128,-145,1222)]
screen=Part.Face(Part.makePolygon(sp+[sp[0]])).extrude(V(4.6,0,3.8)).cut(upper_body)   # base tucked into the fairing top
add('Windscreen_STUDY',screen,'BodyStudy','PROPOSED 6mm screen traced from baseline; optics/buffeting unresolved',color=(.6,.8,.85))
add('Headlamp_installation_STUDY',headlamp,'BodyStudy','Lamp reservation in nose; approved optical unit not selected',color=(.86,.9,.94))
add('Taillamp_installation_STUDY',lamps['Taillamp_installation_STUDY'],'BodyStudy','Tail stop lamp reservation',color=(.7,.08,.05))
# Fender hugs the tyre (12mm) from a forward beak at 55deg to a trailing skirt at 165deg, with side skirts.
def arc_wedge(cx,cz,a0,a1,R=420):
    pts=[(cx,cz)]+[(cx+R*math.cos(math.radians(a)),cz+R*math.sin(math.radians(a))) for a in range(a0,a1+1,5)]
    f=Part.Face(Part.makePolygon([V(x,-200,z) for x,z in pts+[pts[0]]]));return f.extrude(V(0,400,0))
frontFender=cyl((1480,-66,299.9),(1480,66,299.9),320,312)
for s in (-1,1):frontFender=frontFender.fuse(cyl((1480,s*66-(4 if s>0 else 0),299.9),(1480,s*66+(0 if s>0 else 4),299.9),320,288))
frontFender=frontFender.common(arc_wedge(1480,299.9,55,165))
add('Front_fender_STUDY',frontFender,'BodyStudy','Proposed fender on fork lowers; steering/bump mounts not validated',color=(.11,.12,.13))
rearHugger=cyl((0,-72,311.9),(0,72,311.9),334,324)
for s in (-1,1):rearHugger=rearHugger.fuse(cyl((0,s*72-(4 if s>0 else 0),311.9),(0,s*72+(0 if s>0 else 4),311.9),334,300))
rearHugger=rearHugger.common(arc_wedge(0,311.9,35,105))
add('Rear_hugger_STUDY',rearHugger,'BodyStudy','Proposed swingarm-mounted hugger; bump clearance follows wheel',color=(.11,.12,.13))
grip=V(*P['grip_reference_mm'])
for side in [-1,1]:
    tube(sname('Bar_half',side),(1083,side*40,1040),(grip.x,side*290,grip.z),11,8,'RunningGear')
    add(sname('Hand_grip_reserve',side),cyl((grip.x,side*290,grip.z),(grip.x,side*410,grip.z),17),'RunningGear','Grip reference; throttle unselected',color=(.08,.09,.1))
    tube(sname('Mirror_stalk',side),(grip.x+10,side*300,grip.z+10),(862,side*330,1150),6,3,'BodyStudy')
    # Angular mirror head like the baseline: 140 wide, 82 tall, wedge-tapered toward the rider.
    mir=Part.Face(Part.makePolygon([V(848,0,1140),V(878,0,1146),V(878,0,1216),V(848,0,1222),V(848,0,1140)])).extrude(V(0,140,0))
    mir=rounded(mir,6);mir.translate(V(0,280 if side>0 else -420,0))
    add(sname('Mirror_body',side),mir,'BodyStudy','Mirror head envelope; field of view unvalidated',color=(.07,.075,.08))
    tube(sname('Peg_reference',side),(500,side*145,380),(500,side*230,380),12,8,'RunningGear')
    add(sname('Peg_rubber',side),cyl((500,side*232,380),(500,side*305,380),13),'RunningGear','Rider peg with rubber, illustrative',color=(.06,.06,.065))
    hanger=Part.Face(Part.makePolygon([V(x,0,z) for x,z in [(418,448),(452,462),(528,398),(522,358),(488,360),(418,448)]])).extrude(V(0,6,0))
    hanger=rounded(hanger,2.5);hanger.translate(V(0,side*227-3,0))
    add(sname('Peg_bracket',side),hanger,'Chassis','Machined peg hanger plate, illustrative',color=(.62,.63,.64))
    add(sname('Hand_lever',side),rounded(box(grip.x+25,side*300-(4 if side>0 else 156),grip.z-12,12,160,8),3),'RunningGear',
        'Brake (right) / regen-or-rear (left) lever envelope',color=(.55,.56,.57))
    add(sname('Front_indicator_reserve',side),lamps[sname('Front_indicator_reserve',side)],'BodyStudy','Lamp reservation under nose',color=(.87,.5,.12))
    add(sname('Rear_indicator_reserve',side),lamps[sname('Rear_indicator_reserve',side)],'BodyStudy','Lamp reservation',color=(.87,.5,.12))
    add(sname('Front_caliper_reserve',side),rounded(box(1315,side*56-18,245,40,36,110),6),'RunningGear',
        'Radial 4-piston caliper envelope straddling the 320mm disc; Kawasaki 43080-0177/0178 candidate',color=(.16,.17,.18))
# Tail-tidy plate hanger: plate held above Z690 at X-260 so it stays 30mm off the rear tyre at full bump.
add('Plate_hanger_arm',rounded(box(-262,-22,770,135,44,10),3),'BodyStudy','Plate hanger arm under tail tip',color=(.08,.085,.09))
add('Licence_plate_US',box(-266,-89,700,4,178,102),'BodyStudy','US 7x4in motorcycle plate envelope',color=(.85,.86,.88))
add('Plate_lamp',box(-250,-20,760,14,40,8),'BodyStudy','Plate lamp reservation',color=(.9,.92,.95))
add('Bar_centre',cyl((1083,-40,1040),(1083,40,1040),11),'RunningGear','Bar centre section',color=(.1,.1,.11))
add('Rear_caliper_reserve',rounded(box(-131,50,262,45,38,100),6),'RunningGear','Kawasaki 43080-0156 candidate reserve',color=(.16,.17,.18))
add('Display_reserve',box(1188,-80,960,40,160,70),'RunningGear','Instrument reserve behind screen; mount to fairing, sightline unvalidated',color=(.15,.18,.2))
ratio=3.1;pitch=14.0;fr=20*pitch/(2*math.pi);rr=62*pitch/(2*math.pi)
for name,x,z,radius in [('Front',540,470,fr),('Rear',0,311.9,rr)]:
    # Belt plane Y-105..-83: inboard between tyre (Y-80) and swingarm arm (Y-108). The earlier plane at Y-211
    # ran through the three rails that meet at the pivot node (Y-195).
    pul=cyl((x,-105,z),(x,-83,z),radius-3,20)
    for yf in (-107,-83):pul=pul.fuse(cyl((x,yf,z),(x,yf+2,z),radius+5,20))   # belt-tracking flanges
    if name=='Rear':
        for k in range(6):
            t=k*math.tau/6;pul=pul.cut(cyl((x+75*math.cos(t),-115,z+75*math.sin(t)),(x+75*math.cos(t),-75,z+75*math.sin(t)),24))
    add(name+'_pulley_PITCH_STUDY',pul,'Drive','14mm 20:62 pulley, illustrative flanges; supplier not selected',color=(.55,.56,.57))
def hull2(c1,r1,c2,r2,n=72):
    """2D convex hull of two circles in XZ, as a face at Y=0."""
    pts=[(c[0]+r*math.cos(k*math.tau/n),c[1]+r*math.sin(k*math.tau/n)) for c,r in ((c1,r1),(c2,r2)) for k in range(n)]
    pts=sorted(set(pts));
    def half(ps):
        h=[]
        for p in ps:
            while len(h)>=2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1])-(h[-1][1]-h[-2][1])*(p[0]-h[-2][0])<=0:h.pop()
            h.append(p)
        return h
    lo=half(pts);up=half(pts[::-1]);ring=lo[:-1]+up[:-1]
    return Part.Face(Part.makePolygon([V(x,0,z) for x,z in ring+[ring[0]]]))
belt=hull2((540,470),fr+5,(0,311.9),rr+5).cut(hull2((540,470),fr,(0,311.9),rr))
belt.translate(V(0,-104,0));belt=belt.extrude(V(0,20,0))
add('Drive_belt_14mm_STUDY',belt,'Drive','Closed 14mm-pitch belt loop at rest position; length/tension not computed',color=(.05,.05,.05))

notes=D.addObject('Spreadsheet::Sheet','DesignStatus')
for i,t in enumerate(['BAVUSO V1.0 INTEGRATED - ENGINEERING DEVELOPMENT, NOT BUILD RELEASE',
 'Units mm; X forward, Y left, Z up; rear tire contact origin',
 'Stepped 700-cell pack 100s7p; tabs/thermal/restraint unresolved',
 'EMRAX 208, CM200, Orion BMS2 108 are actual supplier STEP; GX14 is drawing outline only',
 'Body traced from design/baseline black.png at 1.35 mm/px; styling study, no CFD or tooling',
 'See v1.0/integrated-build.md and geometry-integrated-audit.json'],1):notes.set(f'A{i}',t)
notes.setColumnWidth('A',900)
D.recompute()

# ---------------------------------------------------------------- checks
for o in D.Objects:
    if hasattr(o,'Shape') and o.TypeId=='Part::Feature':
        if not (o.Shape.isValid() and o.Shape.Volume>0):raise RuntimeError('Invalid shape '+o.Name)
assert len(cells)==700 and len({r['cell_id'] for r in cellmap})==700
cellcontain=all(inner.isInside(v.Point,1e-6,True) for s in cells for v in s.Vertexes)
assert cellcontain
visible=[o for o in D.Objects if o.TypeId=='Part::Feature' and o.InList and o.InList[0].Name!='Keepouts']
native=R/'cad/Bavuso-V1.0-integrated.FCStd';D.saveAs(str(native))
print('saved',native,flush=True)
if os.environ.get('BAVUSO_FAST'):os._exit(0)   # styling iteration: native model only, no STEP or checks
Part.export(visible,str(R/'cad/Bavuso-V1.0-integrated.step'))
O=lambda n:D.getObject(n).Shape
checks=[]
def check(label,a,b,minimum=0):
    # A few supplier-STEP solids have inward-facing shells, and solid distToShape then reports 0 ("inside")
    # 125mm from anything. So a 0 is re-measured face-to-face, solid pair by solid pair (face-to-face on the
    # whole assembly is far too slow). Overlap is checked separately below.
    d=a.distToShape(b)[0]
    if d<1e-6:
        d=min(Part.makeCompound(x.Faces).distToShape(Part.makeCompound(y.Faces))[0]
              for x in (a.Solids or [a]) for y in (b.Solids or [b]))
    if d<1e-6 and not a.BoundBox.intersect(b.BoundBox):
        # Some Orion STEP spline faces also return 0 face-to-face 460mm from the tyre (OCC extrema fault).
        # Boxes that do not meet give a guaranteed lower bound on the true gap.
        ba,bb_=a.BoundBox,b.BoundBox
        d=math.sqrt(sum(max(0,lo2-hi1,lo1-hi2)**2 for lo1,hi1,lo2,hi2 in
                        [(ba.XMin,ba.XMax,bb_.XMin,bb_.XMax),(ba.YMin,ba.YMax,bb_.YMin,bb_.YMax),(ba.ZMin,ba.ZMax,bb_.ZMin,bb_.ZMax)]))
    def inside(p,q):   # a solid of p wholly inside a solid of q: no face contact, so face distance misses it
        return any(y.isInside(x.Vertexes[0].Point,0.01,True) for x in p.Solids if x.Vertexes
                   for y in q.Solids if y.BoundBox.isInside(x.Vertexes[0].Point))
    touching=d<1e-6 or inside(a,b) or inside(b,a)
    ov=sum(x.common(y).Volume for x in (a.Solids or [a]) for y in (b.Solids or [b])
           if x.BoundBox.intersect(y.BoundBox)) if touching else 0.0
    ov=max(ov,0.0)
    checks.append(dict(check=label,gap_mm=round(d,2),overlap_mm3=round(ov,1),required_mm=minimum,passed=d>=minimum-1e-5 and ov<1e-5))
    print(json.dumps(checks[-1]),flush=True)
check('pack_vs_motor_supplier',outer,ms,20)
check('pack_vs_front_bump',outer,frontSweep.Shape,20)
check('motor_vs_rear_bump',ms,rearSweep.Shape,20)
check('pack_vs_pivot_stubs',outer,O('Pivot_reference'),20)
check('charger_vs_pack',charger,outer,10)
check('bms_vs_body_top',bms,upper_body,8)
check('lower_body_vs_pack',lower_body,outer,5)
check('bms_vs_inverter',bms,invs,5)
check('bms_vs_rear_bump',bms,rearSweep.Shape,20)
check('inverter_vs_charger',invs,charger,5)
check('charger_vs_steering_sweep',charger,steerKeep.Shape,10)
check('inverter_vs_steering_sweep',invs,steerKeep.Shape,10)
check('cabinet_vs_motor',cab_out,ms,10)
check('cabinet_vs_pack',cab_out,outer,3)
check('cabinet_vs_seat',cab_out,seat,10)
check('seat_vs_rear_bump',seat,rearSweep.Shape,20)
check('tail_vs_rear_bump',tail_body,rearSweep.Shape,20)
check('upper_body_vs_front_bump',upper_body,frontSweep.Shape,20)
check('lower_body_vs_front_bump',lower_body,frontSweep.Shape,20)
check('lower_body_vs_motor',lower_body,ms,10)
check('motor_cover_vs_motor',motor_cover,ms,10)
check('motor_cover_vs_rear_bump',motor_cover,rearSweep.Shape,20)
check('plate_vs_rear_bump',O('Licence_plate_US'),rearSweep.Shape,20)
check('plate_arm_vs_rear_bump',O('Plate_hanger_arm'),rearSweep.Shape,20)
check('cross_brace_vs_rear_bump',O('Swingarm_cross_brace'),rearSweep.Shape,20)
for side in [-1,1]:
    check(sname('radiator_vs_charger',side),O(sname('Side_radiator',side)),charger,5)
# Broad interference sweep: every body/electronics part against every other visible part.
# Cells are covered by the containment test; the solid pack boundary stands in for them here.
sweep=[(o.Name,o.InList[0].Name,o.Shape) for o in visible if not o.Name.startswith('Cell_column')]
sweep.append(('Battery_installation_keepout','Energy',outer))
interferences=[]
for (na,ga,sa_),(nb,gb,sb_) in itertools.combinations(sweep,2):
    if not ({ga,gb}&{'BodyStudy','Electronics','Energy'}):continue
    if {na,nb}=={'Battery_installation_keepout','Pack_case_stepped_3mm_STUDY'}:continue
    if not sa_.BoundBox.intersect(sb_.BoundBox):continue
    if 'Mirror_stalk' in na+nb and any(k in na+nb for k in ('Mirror_body','Hand_grip','Bar_half')):continue  # intended joints
    if sa_.distToShape(sb_)[0]>1e-6:continue
    # Whole-assembly booleans on the multi-solid supplier STEPs gave false volumes; sum solid by solid.
    v=sum(x.common(y).Volume for x in sa_.Solids for y in sb_.Solids if x.BoundBox.intersect(y.BoundBox))
    if v>1.0:interferences.append(dict(a=na,b=nb,overlap_mm3=round(v,1)));print('OVERLAP',na,nb,round(v),flush=True)
audit=dict(release_state='ENGINEERING DEVELOPMENT; no build authorization',parameters=P,
 actual_supplier_geometry=['EMRAX 208 LC 2022 STEP','Cascadia CM200 STEP','Orion BMS2 108-cell STEP'],
 drawing_outline_only=['Sensata GX14 main contactors'],
 solid_objects=len(visible),total_solids=sum(r['solids'] for r in records),
 cell_count=len(cells),all_cell_vertices_inside_inner_case=cellcontain,
 critical_pair_checks=checks,checks_passed=sum(c['passed'] for c in checks),checks_total=len(checks),
 interferences=interferences,
 exclusions=['steering lock beyond cylinder envelope','rear droop','tire growth','real fork/yoke/hub CAD','tab joining','wiring','hoses','mounts and fasteners','structure','CFD','rider fit buck','test validation'])
for file,rows in [('cell-placement-integrated.csv',cellmap),('component-status-integrated.csv',records)]:
    with (R/file).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(R/'geometry-integrated-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k not in ['parameters']},indent=2),flush=True)
