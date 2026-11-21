"""V1.0 adventure layout (rev B). Run with bundled FreeCAD Python.

Starts from build-integrated.py (the V1.0 road-height model, left untouched) and changes what the
adventure-crossover role and the optimised powertrain (powertrain-cost-down.md) need:
  - structural pack: 594 fast-charge 26120-class cylinders, 99s6p, 32.7 kWh, three transverse lanes;
    the pack outline is generated from the clearances (motor, front tyre at full bump, ground), not drawn
  - pack floor raised 48 mm inside the chassis and the sprung mass raised 40 mm: about 215 mm ground clearance
  - 120/70ZR19 front, 160/60ZR17 rear; 180 mm fork travel, 170 mm rear wheel travel
  - drive (drive-study.md): radial IPM motor envelope 75 deg above the pivot, 2-stage reduction with its output
    and the belt pulley on the swingarm pivot axis. BAVUSO_DRIVE=emrax228 rebuilds the earlier EMRAX 228 layout
    (supplier STEP, coaxial on the pivot) with an -emrax228 suffix
  - lower frame rails removed: the pack carries the loads between a head-tube down-link pair and the pivot node
Everything is modelled in the V1.0 chassis frame (so the traced body keeps its numbers) with the ground at
Z=-LIFT; the whole model is moved up by LIFT before saving, so the files use the usual rear-contact origin.
Real supplier imports and explicitly provisional custom geometry; not a build release.
"""
from pathlib import Path
import json, math, csv, itertools, os
import FreeCAD as A
import Part

R=Path(__file__).resolve().parents[1]
D=A.newDocument('Bavuso_Adventure_Development')
D.Label='Bavuso V1.0 adventure layout - IN DEVELOPMENT'
V=A.Vector
groups={}
records=[]
def group(name):
    g=D.addObject('App::DocumentObjectGroup',name);groups[name]=g;return g
for n in ['Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy','Cooling','Protection','Keepouts']:group(n)
import time as _time;_T0=_time.time();_TRACE=os.environ.get('BAVUSO_TRACE')
def add(name,shape,g,basis,source='',color=(.35,.38,.42),hide=False):
    if _TRACE:print(f'[{_time.time()-_T0:7.1f}s] {name}',flush=True)
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
def stadium(p,q,r,y0,y1):
    """XZ slot (two circles r joined by tangents) between points p and q, extruded from y0 to y1."""
    p=V(p[0],0,p[1]);q=V(q[0],0,q[1]);d=q-p;d.normalize();n=V(-d.z,0,d.x)*r
    f=Part.Face(Part.makePolygon([p+n,q+n,q-n,p-n,p+n])).extrude(V(0,y1-y0,0));f.translate(V(0,y0,0))
    return f.fuse(cyl((p.x,y0,p.z),(p.x,y1,p.z),r)).fuse(cyl((q.x,y0,q.z),(q.x,y1,q.z),r)).removeSplitter()
def rounded(s,r):
    try:
        f=s.makeFillet(r,s.Edges)
        if f.isValid():return f
    except Exception:pass
    return s
frame_segs=[]
def tube(name,a,b,ro,ri,g='Chassis'):
    if g=='Chassis' and name.split('_')[0] in ('Upper','Lower','Tail'):frame_segs.append((a,b,ro))
    return add(name,cyl(a,b,ro,ri),g,'PROPOSED centerline and section; material/joints/fatigue NOT qualified',color=(.1,.105,.11))
def sname(base,side):return f'{base}_{side}'.replace('-','m')

# Adventure layout. Ground is at Z=-LIFT in these coordinates (see module docstring).
LIFT=53.1                                   # 40 + 13.1: the bigger real rear tyre keeps the rear axle where it was in the frame
RF,RR=331.5,325.0                           # Metzeler Tourance Next 2 max in-service: 120/70R19 663x133, 170/60R17 650x190 (supplier-parts.md)
FRONT_TRAVEL,REAR_TRAVEL=170,170         # 180 front left the lower clamp 17mm off the 19in tyre at full bump
REAR_SAG=0.30*REAR_TRAVEL                   # rider-on static is the model position; droop below it
RAKE=math.radians(25);FORK_OFF=36.1         # tube axis 36.1mm ahead of the steering axis (V1.0 value)
SA0=(1206.954,800.0)                        # steering axis lower reference point (sprung, unchanged)
RZ=RR-LIFT                                  # rear axle height in model coordinates
PZ=float(os.environ.get('BAVUSO_PIVOT_Z','350'))   # swingarm pivot = motor axis (model Z). At 470 anti-squat was 175%; see rear-kinematics.py
TAIL_RAIL_END=827.0   # Nov 14: tail rail rear end 10 up (its front node is lower now) so it stays 20+ mm off the tyre at full bump
RAIL_LIFT=lambda x:(TAIL_RAIL_END-817.0)*max(0.0,568-x)/628   # tail top and pillion rise with the rail
WAIST_Z,POCKET_Z=590.0,530.0   # pocket: behind the pack's stepped top (Z<=330 at X650) the covers drop to Z530 from X615 (knee pocket); Nov 20: side covers stop here under the thighs (X435-675); the narrower tail panels come down to meet them
FZ=RF-LIFT
W_AXLE=(FZ-SA0[1]-math.sin(RAKE)*FORK_OFF)/math.cos(RAKE)          # front axle along the steering frame
FX=SA0[0]+math.cos(RAKE)*FORK_OFF-math.sin(RAKE)*W_AXLE
TRAIL=(RF*math.sin(RAKE)-FORK_OFF)/math.cos(RAKE)
front_centres=[(FX-FRONT_TRAVEL*math.sin(RAKE)*i/20,FZ+FRONT_TRAVEL*math.cos(RAKE)*i/20) for i in range(21)]
def front_gap(x,z):
    """XZ distance from a point to the front tyre at any point of its travel (tyre as a 325mm disc)."""
    return min(math.hypot(x-a,z-b) for a,b in front_centres)-RF
def x_cover(z,gap=22.0):
    """Furthest-forward X at height z that keeps `gap` from the front tyre over its whole travel."""
    lo,hi=850.0,1112.0
    if front_gap(hi,z)>=gap:return hi
    for _ in range(40):
        m=(lo+hi)/2
        if front_gap(m,z)>=gap:lo=m
        else:hi=m
    return lo
P=dict(wheelbase_mm=round(FX,1),motor_axis_mm=[540,0,PZ],pivot_mm=[540,0,PZ],rear_tire_radius_mm=RR,
       front_tire_radius_mm=RF,front_travel_mm=FRONT_TRAVEL,rear_vertical_travel_mm=REAR_TRAVEL,rake_deg=25,
       trail_mm=round(TRAIL,1),sprung_lift_vs_v1_mm=LIFT,tyres='120/70R19 front, 170/60R17 rear (Metzeler Tourance Next 2 class)',
       steering_axis_lower_mm=[1206.954,0,800],steering_axis_upper_mm=[1132.345,0,960],
       seat_top_rider_mm=[530,0,779],grip_reference_mm=[917,351,1059],peg_reference_mm=[420,190,270],   # comfort-study.md (Nov 14 update): seat 31 down / 44 fwd, pegs 30 down, grips 15 fwd / 30 down
       note_coordinates='values here are model coordinates; add sprung_lift_vs_v1_mm for height above ground',
       body_reference='design/baseline black.png; 1,480 mm wheelbase spans 1,097 px, so 1.35 mm/px',
       pack='structural, 594 x 26120-class cylinders, 99s6p, three transverse lanes')

# ---------------------------------------------------------------- energy: structural cylinder pack
# Cells lie across the bike (axis +Y) in three lanes, hex-packed in the side view. The pack is built in
# bands of two cell rows. For each band the rear limit keeps the case 20mm off the EMRAX 228 (r118.8) and
# the front limit keeps the battery cover 22mm off the front tyre at every point of its travel.
CELL_R,CELL_L,CELL_WH,CELL_G=13.0,120.0,55.0,180.0       # 26120 class, modelled at 305 Wh/kg (powertrain-cost-down.py)
SERIES,PAR=99,6;PER_LANE=SERIES*PAR//3
PITCH=28.0;DZ=PITCH*math.sqrt(3)/2                       # 2mm between cells for the cooling ribbon / spacer
WALL=4.0;CLR=1.0                                         # structural walls; cell-to-wall insulation gap
LANES=(-132.6,0.0,132.6)                                 # 12.6mm between lanes: room for the tapered Al busbars (electrical-detailed.md)
YI=LANES[-1]+CELL_L/2+7.3;YO=YI+WALL                     # inner/outer half-width; 7.3mm end gap (busbar return + crush space)
PACK_FLOOR=198.0                                         # outer case bottom (V1.0: 150)
COVER_SKIN=11.4                                          # pack-to-cover gap 8.4 + 3mm skin (V1.0 values)
RW=CELL_R+CLR+WALL                                       # cell centre to case outer face
# The EMRAX 228 STEP reaches 155mm from its axis (accessories), not just its 118.8mm housing, so the rear
# limit comes from the supplier solid itself: its tessellated points in the side view (the pack spans the
# motor's whole width), kept 21mm away (20 + 1 for tessellation).
# Default drive is the drive-study choice (drive-study.md): a radial IPM motor above the pivot, driving a pulley
# on the pivot axis through a gear stage. Envelopes only. BAVUSO_DRIVE=emrax228 keeps the earlier supplier-STEP
# EMRAX layout; its outputs get an -emrax228 suffix.
DRIVE=os.environ.get('BAVUSO_DRIVE','ipm')
SUFFIX=('' if DRIVE=='ipm' else '-'+DRIVE)+os.environ.get('BAVUSO_TAG','')   # BAVUSO_TAG=-preview: styling builds that don't overwrite the release model
motorraw=Part.read(str(R/'sources/EMRAX-228-MV-LC-2025.step'))
ms=motorraw.copy()
# Source rotor axis is +X, output shaft toward +X (mount face X0, housing to X-89.8, shaft to X+45.1).
# -90 deg about Z sends +X to vehicle -Y (belt side): vehicleX=540+sourceY, vehicleY=-sourceX-59.9, vehicleZ=PZ+sourceZ.
# The shaft end then sits at Y-105, the outer face of the belt pulley.
ms.Placement=A.Placement(V(540,-59.9,PZ),A.Rotation(V(0,0,1),-90)).multiply(ms.Placement)
if DRIVE=='ipm':
    # Motor 220 OD x 129 long (Y-33..96), axis 135 from the pivot at 75 deg (up and slightly forward; the
    # angle sweep in drive-study.md). Its length is set by the swingarm: the right arm's inner face is at Y108
    # and its sweep passes 25mm from the pivot axis, so the motor ends 12mm inside it. Gear case Y-80..-33
    # joins the motor pinion to the output gear on the pivot axis; the belt pulley (Y-105..-83) stays on that
    # axis, so belt length and anti-squat are unchanged.
    IPM_C,IPM_R=135.0,110.0;IPM_ANG=math.radians(float(os.environ.get('BAVUSO_IPM_ANG','75')))
    IPM_Y0,IPM_Y1,GC_Y0=-33.0,96.0,-80.0
    mx,mz=540+IPM_C*math.cos(IPM_ANG),PZ+IPM_C*math.sin(IPM_ANG)
    motor_body=cyl((mx,IPM_Y0,mz),(mx,IPM_Y1,mz),IPM_R)
    gear_case=Part.makeCompound([cyl((540,GC_Y0,PZ),(540,IPM_Y0,PZ),75),cyl((mx,GC_Y0,mz),(mx,IPM_Y0,mz),95)])
    d_=V(mx-540,0,mz-PZ);d_.normalize();n_=V(-d_.z,0,d_.x)
    web=Part.Face(Part.makePolygon([V(540,0,PZ)+n_*75,V(mx,0,mz)+n_*95,V(mx,0,mz)-n_*95,V(540,0,PZ)-n_*75,V(540,0,PZ)+n_*75])).extrude(V(0,IPM_Y0-GC_Y0,0))
    web.translate(V(0,GC_Y0,0))
    ms=motor_body.fuse(gear_case).fuse(web).removeSplitter()
# Mesh vertices alone miss the middle of long straight edges (the gear-case web), so edges are sampled too.
motor_xz=[(p.x,p.z) for p in ms.tessellate(0.5)[0]]+[(p.x,p.z) for e in ms.Edges for p in e.discretize(Distance=2.0)]
def band_limits(zlo,zhi):
    xlo=590.0                                  # 16mm upper rails rise at X540-570 behind the pack
    for px,pz in motor_xz:
        d=max(0.0,zlo-pz,pz-zhi)
        if d<21:xlo=max(xlo,px+math.sqrt(21**2-d**2))
    xhi=min(x_cover(z) for z in [zlo+k*(zhi-zlo)/8 for k in range(9)])-COVER_SKIN
    return xlo,xhi
rows=[];bands=[];n=0;k=0
while n<PER_LANE:
    z0=PACK_FLOOR+RW+2*k*DZ;zlo,zhi=z0-RW,z0+DZ+RW
    xlo,xhi=band_limits(zlo,zhi);used=[]
    for r in (0,1):
        z=z0+r*DZ;x=xlo+RW+((PITCH/2) if r else 0);xs=[]
        while x<=xhi-RW and n<PER_LANE:xs.append(x);x+=PITCH;n+=1
        if xs:rows.append((z,xs));used.append((z,xs))
    bands.append(dict(xlo=min(x for _,xs in used for x in xs)-RW,xhi=max(x for _,xs in used for x in xs)+RW,
                      zlo=zlo,zhi=used[-1][0]+RW));k+=1
assert n==PER_LANE
FCH=9.0   # 9x45 front vertical corner chamfer of the case (lower-cover clearance; aero-study.md CR-1)
CH=8.0   # 8x45 bottom-edge chamfer so the case stays inside the 47 deg lean line of the chamfered covers (dynamics-study.md)
def band_solid(b,inset):
    bx=box(b['xlo']+inset,-YO+inset,b['zlo']+inset,b['xhi']-b['xlo']-2*inset,2*(YO-inset),b['zhi']-b['zlo']-2*inset)
    if b is bands[0]:bx=bx.cut(_corner_cut(YO-CH-PACK_FLOOR-inset*math.sqrt(2)))   # only the bottom band reaches the floor edge
    c=b['xhi']+YO-FCH-inset*math.sqrt(2)   # front vertical corners: removes x+|y| > c
    for sy in (-1,1):
        w=Part.makeBox(200,200,1200);w.rotate(V(0,0,0),V(0,0,1),-45);w.translate(V(c-YO-20,YO+20,-100))   # face on x+y=c
        if sy<0:w=w.mirror(V(0,0,0),V(0,1,0))
        bx=bx.cut(w)
    return bx
def _corner_cut(c):   # removes y-z > c (and its mirror): a 45 deg chamfer along the case's bottom outer edges
    z1=PACK_FLOOR-60;tri=[V(0,c+z1,z1),V(0,c+z1+300,z1),V(0,c+z1+300,z1+300)]
    f=Part.Face(Part.makePolygon(tri+[tri[0]]));f.translate(V(-500,0,0));w=f.extrude(V(3000,0,0))
    return Part.makeCompound([w,w.mirror(V(0,0,0),V(0,1,0))])
outer=band_solid(bands[0],0).fuse([band_solid(b,0) for b in bands[1:]]).removeSplitter()
inner=band_solid(bands[0],WALL).fuse([band_solid(b,WALL) for b in bands[1:]]).removeSplitter()
case=add('Pack_case_structural_4mm_STUDY',outer.cut(inner),'Energy',
         'PROPOSED 4mm structural shell, outline generated from motor/front-tyre/ground clearances; carries head-tube and pivot loads; '
         'wall sizing, lid, joints, vent and crash qualification NOT done',color=(.45,.48,.5))
add('Battery_installation_keepout',outer,'Keepouts','Stepped outer battery boundary incl. motor cutout',hide=True)
cell_source='https://enduro21.com/en/news/stark-future-partners-with-eve-energy-for-next-generation-battery-cells'
cells=[];cellmap=[];bylane={}
# Series numbering: each lane holds 33 groups of 6, numbered along a row-by-row snake.
for li,ly in enumerate(LANES):
    seq=[(z,x) for i,(z,xs) in enumerate(rows) for x in (xs if i%2==0 else xs[::-1])]
    for j,(z,x) in enumerate(seq):
        q=Part.makeCylinder(CELL_R,CELL_L,V(x,ly-CELL_L/2,z),V(0,1,0));cells.append((q,x,z,ly));bylane.setdefault(li,[]).append(q)
        g=li*SERIES//3+j//PAR+1
        cellmap.append(dict(cell_id=f'S{g:03d}P{j%PAR+1}',series_group=g,parallel_position=j%PAR+1,lane=li+1,
                            x_mm=round(x,2),y_mm=ly,z_mm=round(z+LIFT,2),diameter_mm=2*CELL_R,length_mm=CELL_L))
assert len(cells)==SERIES*PAR and len({r['cell_id'] for r in cellmap})==SERIES*PAR
for li,shapes in sorted(bylane.items()):
    add(f'Cell_lane_{li+1}',Part.makeCompound(shapes),'Energy',
        f'{len(shapes)} 26120-class cylinder bodies (26x120), axis across the bike; cell not yet sold to outside buyers; '
        'busbars, cooling ribbon and potting unresolved',cell_source,(.78,.57,.24))
pack_kg=SERIES*PAR*CELL_G/1000/0.80                    # cells / (0.74 module fraction + 0.06 structural), as the optimiser
P['pack_summary']=dict(cells=SERIES*PAR,layout=f'{SERIES}s{PAR}p',nominal_kwh=round(SERIES*PAR*CELL_WH/1000,1),
    full_v=round(SERIES*4.2),estimated_mass_kg=round(pack_kg,1),bands=[{k:round(v,1) for k,v in b.items()} for b in bands],
    outer_bbox_mm=[round(v,1) for v in (outer.BoundBox.XMin,outer.BoundBox.XMax,outer.BoundBox.YMin,outer.BoundBox.YMax,
                                        outer.BoundBox.ZMin+LIFT,outer.BoundBox.ZMax+LIFT)],
    cell_centroid_height_mm=round(sum(z for _,_,z,_ in cells)/len(cells)+LIFT,1),
    cell_centroid_x_mm=round(sum(x for _,x,_,_ in cells)/len(cells),1))

# ---------------------------------------------------------------- drive: supplier motor and inverter
if DRIVE=='emrax228':
    add('EMRAX_228_MV_LC_supplier_STEP',ms,'Drive',f'ACTUAL supplier STEP 2025 (with accessories); rotor axis on pivot X540/Z{PZ:.0f}, shaft toward -Y (belt side)',
        'https://emrax.com/wp-content/uploads/2025/06/Emrax_228_MV_1UVW_LC_with_accessories.step',(.8,.45,.17))
else:
    add('IPM_motor_and_gear_case_ENVELOPE',ms,'Drive',f'SPEC ENVELOPE, not a supplier part: radial IPM 150 Nm/16k rpm/130 kW, 220 OD x 129 (Y{IPM_Y0:.0f}..{IPM_Y1:.0f}), '
        f'axis 135mm from the pivot at {math.degrees(IPM_ANG):.0f} deg; 2-stage reduction ~7.8:1, output and pulley on the pivot X540/Z{PZ:.0f}',
        'drive-study.md',(.8,.45,.17))
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

# HV cabinet on the pack roof behind the charger: X550-690, Y+-150, Z580-710. With the motor lowered to
# the pivot (PZ) nothing sits under it; it moved forward 35mm and down 20mm to clear the central shock.
gx14_src='https://www.sensata.com/sites/default/files/a/sensata-gigavac-gx14-series-open-contactors-datasheet.pdf'
if DRIVE=='ipm':
    # The IPM sits where this cabinet was. Below the pivot, between the gear case (Y-33) and the right arm
    # (Y108), behind the pack's bottom step and above the belly line, nothing is left now that the motor is
    # not coaxial: the cabinet moves there (X445-580, Y-20..95, Z205-358), contactors stacked one above the other.
    cab_out=box(445,-20,205,135,115,153);cab_in=box(448,-17,208,129,109,147)
    gx14=[('positive',(452,-12,212)),('negative',(452,-12,276))];gx14_dims=(114.8,59.8,57.3)
    fuse_box=box(452,52,212,110,38,120)
else:
    cab_out=box(550,-150,580,140,300,130);cab_in=box(553,-147,583,134,294,124)
    gx14=[('positive',(556,-57.4,586)),('negative',(626,-57.4,586))];gx14_dims=(59.8,114.8,57.3)
    fuse_box=box(570,80,586,110,55,70)
cabinet=add('HV_cabinet_2mm_STUDY',cab_out.cut(cab_in),'Electronics','PROPOSED covered HV cabinet; material, seals, interlock and mounts unresolved',color=(.55,.56,.58))
for nm,(x,y,z) in gx14:
    add(f'GX14_main_{nm}_OUTLINE',box(x,y,z,*gx14_dims),'Electronics',
        'GX14 manufacturer DRAWING outline only (114.8x59.8x57.3); supplier STEP not retrieved; reverse-break duty unconfirmed',gx14_src,(.75,.2,.15))
add('Main_fuse_branch_search_region',fuse_box,'Keepouts','Unselected main fuse/holder region; 30EV family is comparison only',hide=True)

# Heat exchangers: the old unsized 110x50 side cores are replaced by the side-pod radiators sized in thermal-study.md (added below).

# ---------------------------------------------------------------- running gear
def revolve_rz(pts,x,z,closed=True,smooth=False):
    """Solid of revolution about the wheel axis (Y through x,z) from a (radius, y) profile."""
    P3=[V(x+r,y,z) for r,y in pts]
    if smooth:
        e=[spline([(p.x,p.y,p.z) for p in P3])];e.append(Part.makeLine(P3[-1],P3[0]));w=Part.Wire(e)
    else:w=Part.makePolygon(P3+[P3[0]])
    return Part.Face(w).revolve(V(x,0,z),V(0,1,0),360)
def at_angle(shape,x,z,deg):
    s=shape.copy();s.rotate(V(x,0,z),V(0,1,0),-deg);return s     # +deg = counter-clockwise seen from +Y
def spline(pts):
    c=Part.BSplineCurve();c.interpolate([V(*p) for p in pts]);return c.toShape()
PLAIN_TYRE={}
def wheel(name,x,z,width,r,front,rim_in):
    bead=rim_in*25.4/2
    ws=76.2 if front else 114.3                          # 19x3.00 front, 17x4.50 rear bead-seat widths
    h=r-bead
    # Tyre: revolved section (bead, sidewall bulge, rounded adventure crown), then a staggered diagonal
    # groove pattern cut 4-5mm into the crown, as on a road-biased adventure tyre.
    sec=[(bead,-ws/2),(bead+16,-(ws/2+9)),(bead+.38*h,-width/2),(bead+.66*h,-width*.485),(bead+.86*h,-width*.40),
         (bead+.96*h,-width*.24),(h+bead,0),(bead+.96*h,width*.24),(bead+.86*h,width*.40),(bead+.66*h,width*.485),
         (bead+.38*h,width/2),(bead+16,ws/2+9),(bead,ws/2)]
    tyre=revolve_rz(sec,x,z,smooth=True)
    PLAIN_TYRE[name]=tyre.copy()     # ungrooved section, for the steering sweep
    prof=spline([(x+a,b,z) for a,b in sec])
    def r_at(y):    # crown radius at lateral offset y
        ln=Part.makeLine(V(x+bead+.6*h,y,z),V(x+r+30,y,z));return prof.distToShape(ln)[1][0][0].x-x
    cutters=[];N=36 if front else 40
    if os.environ.get('BAVUSO_NOGROOVE'):N=0     # styling previews only: skips the slow groove booleans
    for k in range(N):
        for side in (-1,1):
            for y0,y1,depth in ((side*6,side*(width*.30),4.5),(side*(width*.27),side*(width*.46),4.0)):
                if (k%2==0)!=(side>0) and abs(y0)<10:continue     # centre grooves alternate sides
                ra,rb_=r_at(y0),r_at(y1)
                ang=k*360/N+(0 if side>0 else 180/N)+(3 if abs(y0)>10 else 0)
                da=math.radians(9 if abs(y0)<10 else 6)                   # groove runs diagonally across the crown
                pa=V(x+(ra-depth),y0,z);pb=V(x+(rb_-depth)*math.cos(da),y1,z+(rb_-depth)*math.sin(da))
                qa=V(x+ra+12,y0,z);qb=V(x+(rb_+12)*math.cos(da),y1,z+(rb_+12)*math.sin(da))
                w2=V(0,0,1.6)
                pts=[pa-w2,pb-w2,pb+w2,pa+w2];top=[qa-w2,qb-w2,qb+w2,qa+w2]
                cut=Part.makeLoft([Part.makePolygon(pts+[pts[0]]),Part.makePolygon(top+[top[0]])],True)
                cutters.append(at_angle(cut,x,z,ang))
    if cutters:tyre=tyre.cut(Part.makeCompound(cutters))
    add(name+'_nominal_tire',tyre,'RunningGear',f'{"120/70ZR19" if front else "160/60ZR17"} section on a {rim_in}x{ws/25.4:.2f} rim with an '
        'illustrative road-adventure groove pattern; loaded radius/growth not modelled',color=(.09,.1,.11))
    # Cast wheel: J-flange rim with a drop centre, hub with bearing bosses and disc flanges, ten tapered spokes
    # lofted from a wide hub root to a slim rim root (baseline style).
    fl=ws/2+7
    rim=revolve_rz([(bead+17,-fl),(bead+17,-(ws/2+2)),(bead+3,-ws/2),(bead,-(ws/2-12)),(bead-14,-20),(bead-14,20),
                    (bead,ws/2-12),(bead+3,ws/2),(bead+17,ws/2+2),(bead+17,fl),(bead-3,fl),(bead-8,ws/2-6),
                    (bead-21,16),(bead-21,-16),(bead-8,-(ws/2-6)),(bead-3,-fl)],x,z)
    hubw=96 if front else 120
    hub=revolve_rz([(12,-hubw/2),(34,-hubw/2),(34,-hubw/2+9),(46,-hubw/2+12),(52,-18),(52,18),(46,hubw/2-12),
                    (34,hubw/2-9),(34,hubw/2),(12,hubw/2)],x,z)
    for s in (-1,1) if front else (1,):    # disc mounting flange with six bosses
        yf=s*(hubw/2-4)
        fl_=cyl((x,yf-3,z),(x,yf+3,z),44,30)
        for k in range(6):
            t=k*math.tau/6;fl_=fl_.fuse(cyl((x+44*math.cos(t),yf-3,z+44*math.sin(t)),(x+44*math.cos(t),yf+3,z+44*math.sin(t)),9))
        hub=hub.fuse(fl_)
    def sect(t,rho,a,b,yoff):
        c=V(x+rho*math.cos(t),yoff,z+rho*math.sin(t));v=V(-math.sin(t),0,math.cos(t));Y=V(0,1,0)
        pts=[]
        for i in range(16):
            ph=i*math.tau/16;cp,sp_=math.cos(ph),math.sin(ph)
            pts.append(c+v*(a*math.copysign(abs(cp)**.45,cp))+Y*(b*math.copysign(abs(sp_)**.45,sp_)))
        bs=Part.BSplineCurve();bs.interpolate(pts,PeriodicFlag=True);return Part.Wire(bs.toShape())
    spokes=[]
    for k in range(10):
        t=k*math.tau/10+math.radians(9)
        spokes.append(Part.makeLoft([sect(t,40,13,15,0),sect(t+math.radians(2),bead*.55,8.5,10,0),
                                     sect(t+math.radians(5),bead-6,6.5,8,0)],True,False))
    add(name+'_wheel_STUDY',Part.makeCompound([rim,hub]+spokes),'RunningGear',
        f'ILLUSTRATIVE cast/forged 10-spoke {rim_in}x{ws/25.4:.2f} wheel: J-flange rim with drop centre, hub with disc flanges; OEM hub/offset CAD absent',color=(.1,.105,.11))
    discR=160 if front else 133.5   # rear 267x6 (dynamics-study.md: 240 reached 506 C in the R78 fade test)
    for side in ([-1,1] if front else [1]):
        yd=side*(hubw/2+6)
        disc=cyl((x,yd,z),(x,yd+side*5,z),discR,discR-38)
        holes=[]
        for row,(rr_,n_) in enumerate(((discR-11,40),(discR-21,40),(discR-31,40))):
            for k in range(n_):
                t=(k+row*.5)*math.tau/n_+row*.05
                holes.append(cyl((x+rr_*math.cos(t),yd-10,z+rr_*math.sin(t)),(x+rr_*math.cos(t),yd+10,z+rr_*math.sin(t)),2.6))
        disc=disc.cut(Part.makeCompound(holes))
        carrier=cyl((x,yd,z),(x,yd+side*5,z),discR-36,40)
        for k in range(6):
            t=k*math.tau/6+.3;carrier=carrier.cut(cyl((x+(discR-80)*math.cos(t),yd-6,z+(discR-80)*math.sin(t)),
                                                     (x+(discR-80)*math.cos(t),yd+6,z+(discR-80)*math.sin(t)),20 if front else 14))
        # Floating-disc bobbins on the carrier/disc joint.
        bob=[cyl((x+(discR-38)*math.cos(k*math.tau/10),yd-side*1.5,z+(discR-38)*math.sin(k*math.tau/10)),
                 (x+(discR-38)*math.cos(k*math.tau/10),yd+side*6.5,z+(discR-38)*math.sin(k*math.tau/10)),5.5) for k in range(10)]
        carrier=carrier.fuse(Part.makeCompound(bob)).cut(disc)
        add(name+f'_disc_{side:+d}'.replace('+','p').replace('-','m'),disc,
            'RunningGear',f'{2*discR}mm floating disc, three staggered drill rows; thickness/offset PROPOSED',color=(.66,.67,.68))
        add(name+f'_disc_carrier_{side:+d}'.replace('+','p').replace('-','m'),carrier,'RunningGear','Floating-disc carrier with 10 bobbins, illustrative',color=(.2,.21,.22))
def caliper(x,z,yd,side,discR,half_deg,pistons):
    """Radial monobloc caliper straddling the disc behind the axle: an arc-shaped body with a disc slot,
    piston bulges on the outboard face and a bridge bolt."""
    a0,a1=180-half_deg,180+half_deg;ro,ri=discR+15,discR-44
    arc=[(x+ro*math.cos(math.radians(a)),z+ro*math.sin(math.radians(a))) for a in [a0+k*(a1-a0)/12 for k in range(13)]]
    arc+=[(x+ri*math.cos(math.radians(a)),z+ri*math.sin(math.radians(a))) for a in [a1-k*(a1-a0)/12 for k in range(13)]]
    yi,yo_=yd-side*14,yd+side*(5+17)
    f=Part.Face(Part.makePolygon([V(px,0,pz) for px,pz in arc+[arc[0]]])).extrude(V(0,yo_-yi,0));f.translate(V(0,yi,0))
    body=rounded(f,4)
    for k in range(pistons):
        a=math.radians(a0+(k+.5)*(a1-a0)/pistons);pr=discR-18
        body=body.fuse(cyl((x+pr*math.cos(a),yo_-side*2,z+pr*math.sin(a)),(x+pr*math.cos(a),yo_+side*4,z+pr*math.sin(a)),15))
    slot_lo,slot_hi=sorted((yd-side*2,yd+side*7))
    slot=cyl((x,slot_lo,z),(x,slot_hi,z),discR+5)
    bridge=cyl((x+(discR+9),yi-side*2,z),(x+(discR+9),yo_+side*2,z),4.5);bridge.rotate(V(x,0,z),V(0,1,0),-180)
    return body.cut(slot).fuse(bridge)
wheel('Rear',0,RZ,180,RR,False,17)
wheel('Front',FX,FZ,130,RF,True,19)   # widths near max in-service so the sweeps built from them are conservative
rear_sweeps=[];front_sweeps=[]
arm=math.hypot(540,PZ-RZ)
def rear_axle(rz):return 540-math.sqrt(arm*arm-(rz-PZ)**2),rz
for i in range(21):
    t=i/20
    # Droop to 51mm (30% sag) below static, bump to 170mm above it. Real bump is +119 (shock stroke); +170 is kept
    # as a conservative envelope for the body/frame checks.
    rz=RZ-REAR_SAG+(REAR_TRAVEL+REAR_SAG)*t;rx=rear_axle(rz)[0]
    rear_sweeps.append(cyl((rx,-95,rz),(rx,95,rz),RR))
    fx,fz=front_centres[i]
    front_sweeps.append(cyl((fx,-66.5,fz),(fx,66.5,fz),RF))
rearSweep=add('Rear_bump_sampled_keepout',Part.makeCompound(rear_sweeps),'Keepouts',f'21 samples, droop {REAR_SAG:.0f}mm to bump {REAR_TRAVEL}mm from static; growth absent',hide=True)
frontSweep=add('Front_bump_sampled_keepout',Part.makeCompound(front_sweeps),'Keepouts',f'21 samples, {FRONT_TRAVEL}mm at 25deg from static; steering sweep NOT included',hide=True)
def arm_z(x):return RZ+(PZ-RZ)*x/540            # swingarm centreline height at X (pivot to rear axle)
# Steering sweep: fork legs sit 106mm off the steering axis; a 140mm cylinder bounds them at any lock.
sa=V(*P['steering_axis_lower_mm']);sb=V(*P['steering_axis_upper_mm']);sd=sb-sa;sd.normalize()
steer_lo=sa-sd*260;steer_hi=sa+sd*330
steerKeep=add('Steering_sweep_keepout',Part.makeCylinder(140,(steer_hi-steer_lo).Length,steer_lo,sd),'Keepouts',
              'Envelope of fork legs/clamps about steering axis at any lock; body is cut to it',hide=True)

# ---------------------------------------------------------------- chassis (Codex rework frame, rails re-routed for body/seat)
# Nov 14 (comfort): the rail node at the seat front moves 43 mm inboard (Y+-152) and 25 mm down, so the frame under the
# rider's thighs is 368 mm across the tubes (was 428). The upper rail runs from there back out to Y+-195 at X1050.
# Nov 20 (thighs still pressed into the waist): node pulled in again to Y+-125, 310 mm across the tubes.
RAIL_NODE_Y,TAIL_RAIL_END_Y=125.0,104.0
def urail_y(x):return RAIL_NODE_Y+(195-RAIL_NODE_Y)*(x-570)/480
def urail_z(x):return 715.0+65*(x-570)/480
for side in [-1,1]:
    y=side*195;yn=side*RAIL_NODE_Y
    # The pivot node is low now (PZ), so the pack wraps over the motor; the rail rises nearly vertically
    # behind the pack's top steps (X>=590) instead of leaning forward into them.
    # Sizes from detailed-design/structural-fea.md (4130): 44x3.5 / 38x3 / 45x4; the head joint moves up to w=120 on the axis.
    for i,(a,b,ro,ri) in enumerate([((540,y,PZ),(570,yn,715),22,18.5),((570,yn,715),(1050,y,780),19,16),((1050,y,780),(1156.2,side*35,908.8),22.5,18.5)]):
        tube(sname(f'Upper_rail_{i}',side),a,b,ro,ri)
    # Posts from the upper rail down to machined pads on the pack roof (FEA CR-7): triangulate each side loop.
    for nm,xr,xp in (('front',960,950),('rear',700,712)):   # front post 40 aft of the FEA X1000 so the side-pod radiator clears it
        tube(sname(f'Upper_post_{nm}',side),(xr,side*urail_y(xr),urail_z(xr)-14),(xp,side*(165 if nm=='rear' else 178),576.5),16,13.5)
    # No lower rails: the structural pack is the lower frame. A down-link pair runs from the head tube to
    # lugs on the pack front face, and a rear link pair from the pivot node down to the pack's rear step.
    # The links stop short of the case; the bolted lugs between them are not modelled.
    zf_lug=470.0   # was 400: a higher lug runs the link further back and outboard past the steered tyre (lock sweep, Nov 11)
    bf=next(b for b in bands if b['zlo']<=zf_lug<=b['zhi'])
    tube(sname('Lower_downlink',side),(1184,side*39,850),(bf['xhi']+22,side*184,zf_lug),20,16.5)   # 40x3.5 (FEA); lugs out to +-184 keep 20mm off the tyre
    # Head gusset (FEA CR-5): 10mm plate, 60 wide, from the upper-rail head joint to 35% down the down-link.
    g0=V(1156.2,side*37,908.8);g1=V(1184,side*39,850)+(V(bf['xhi']+22,side*184,zf_lug)-V(1184,side*39,850))*.35
    gp=[(g0.x,g0.z),(1184,850),(g1.x,g1.z),(g0.x-30,g0.z-60)]
    add(sname('Head_gusset',side),Part.Face(Part.makePolygon([V(x_,side*37-5,z_) for x_,z_ in gp+[gp[0]]])).extrude(V(0,10,0)),'Chassis',
        '10mm 4130 head gusset (structural-fea.md CR-5)',color=(.1,.105,.11))
    # Rear link: pivot node straight forward to a lug on the pack's rear face beside the motor.
    zr_lug=PZ+36
    br=next(b for b in bands if b['zlo']<=zr_lug<=b['zhi'])
    tube(sname('Lower_pack_rear_link',side),(540,y,PZ),(br['xlo']-17,side*175,zr_lug),22,18.5)   # 44x3.5 (FEA CR-8)
    tube(sname('Tail_rail',side),(568,yn,692),(-60,side*TAIL_RAIL_END_Y,TAIL_RAIL_END),19,16)   # 38x3 (FEA CR-9); rear end up 8.5 for the 170/60 tyre   # 10mm higher than V1.0: 20mm off the tyre at full bump
    tube(sname('Tail_brace',side),(540,y,PZ),(160,side*144,740),14,12)
    # Box-section swingarm arm, 74x34 at the pivot tapering to 52x30 at the axle (loft of two sections).
    # Belt-side (left) arm sits 8mm further out: at Y-108 its inner face was 3mm from the EMRAX output hub (Y-105).
    ya=125+(33 if side<0 else 0)   # belt side out 25 more for the moved belt plane (supplier CR-3)
    adir=V(0,side*ya,RZ)-V(540,side*ya,PZ);alen=adir.Length;adir.normalize();an=V(-adir.z,0,adir.x)
    if an.z<0:an=-an
    def sect(p,h,w):
        q=[p+an*(h/2)+V(0,w/2,0),p+an*(h/2)-V(0,w/2,0),p-an*(h/2)-V(0,w/2,0),p-an*(h/2)+V(0,w/2,0)]
        return Part.makePolygon(q+[q[0]])
    arm_=Part.makeLoft([sect(V(540,side*ya,PZ)+adir*30,135,34),sect(V(0,side*ya,RZ)-adir*30,75,30)],True)   # 6061-T6, 4.5/4.0 wall (FEA CR-13)
    arm_=arm_.fuse(cyl((540,side*(ya-17),PZ),(540,side*(ya+17),PZ),38)).fuse(cyl((0,side*(ya-15),RZ),(0,side*(ya+15),RZ),32))
    add(sname('Swingarm',side),arm_,'Chassis','PROPOSED box-section swingarm arm; section/fatigue NOT qualified',color=(.13,.14,.15))
head_lo=sa-sd*30;head_hi=sa+sd*200
add('Head_tube',cyl(tuple(head_lo),tuple(head_hi),31,25),'Chassis','Head tube on steering axis; bearing seats unresolved')
add('Swingarm_cross_brace',cyl((380,-118,arm_z(380)),(380,110,arm_z(380)),30,25),'Chassis','PROPOSED 50x5 cross tube ahead of the tyre; carries the shock tower; bolt-in (inside the belt loop)',color=(.13,.14,.15))
# Upside-down fork built in the steering frame: local Z along the steering axis from the lower axis point,
# local X forward-perpendicular. Tubes sit 36.1mm ahead of the axis; the axle sits W_AXLE down the axis.
steer_pl=A.Placement(sa,A.Rotation(V(0,1,0),-25))
def steer(shape):s=shape.copy();s.Placement=steer_pl.multiply(s.Placement);return s
off=FORK_OFF;w_axle=W_AXLE
for side in [-1,1]:
    yo=side*105   # legs out 5 for the 133-wide tyre (supplier CR-2)
    add(sname('Fork_outer_tube',side),steer(cyl((off,yo,-215),(off,yo,240),28)),'RunningGear','USD outer tube, illustrative; supplier fork not selected',color=(.07,.07,.08))
    add(sname('Fork_inner_tube',side),steer(cyl((off,yo,w_axle+43.5),(off,yo,-210),24)),'RunningGear','USD 48mm chrome inner tube, illustrative; 170mm travel',color=(.8,.81,.82))
    # Axle foot: clamp barrel, split axle boss with pinch bolts, and two radial-mount lugs (108mm spacing) to the
    # caliper behind the disc.
    foot=cyl((off,yo,w_axle-31.5),(off,yo,w_axle+158.5),27.5).fuse(cyl((off,yo-side*30,w_axle),(off,yo+side*34,w_axle),31))
    for dz in (-14,14):foot=foot.fuse(cyl((off+20,yo+side*8,w_axle+dz+side*0),(off+38,yo+side*8,w_axle+dz),6))   # pinch bolts
    foot=steer(foot)
    for a in (180-19.5,180+19.5):
        p=V(FX+(160+4)*math.cos(math.radians(a)),0,FZ+(160+4)*math.sin(math.radians(a)))
        lug=stadium((FX-10,FZ+(18 if a<180 else -18)),(p.x,p.z),10,*((70,82) if side>0 else (-82,-70)))
        foot=foot.fuse(lug)
    add(sname('Fork_axle_clamp',side),foot,'RunningGear','USD axle foot with pinch bolts and radial caliper lugs (108mm), illustrative',color=(.09,.09,.1))
    add(sname('Fork_top_cap',side),steer(cyl((off,yo,240),(off,yo,252),22).fuse(cyl((off,yo,252),(off,yo,258),9))),'RunningGear',
        'Fork cap with preload/rebound adjuster, illustrative',color=(.7,.55,.25))
    add(sname('Fork_reflector',side),steer(rounded(box(off-8,yo+side*25-(0 if side>0 else 4),w_axle+95,16,4,34),1.5)),'RunningGear',
        'Side reflector (amber), illustrative',color=(.9,.5,.1))
def clamp(w0,t):
    c=cyl((0,0,w0),(0,0,w0+t),36)
    for s in (-1,1):c=c.fuse(cyl((off,s*105,w0),(off,s*105,w0+t),36))
    return c.fuse(box(-10,-105,w0,off+20,210,t)).cut(Part.makeCompound([cyl((off,s*105,w0-1),(off,s*105,w0+t+1),28) for s in (-1,1)]))
add('Lower_triple_clamp',steer(clamp(-62,28)),'RunningGear','Lower triple clamp, illustrative',color=(.12,.12,.13))
add('Upper_triple_clamp',steer(clamp(205,22)),'RunningGear','Upper triple clamp, illustrative',color=(.12,.12,.13))
# Bar: 28.6mm tapered bar on pull-back risers. Risers lean back from the top clamp to the bar clamp at X1015/Z1062;
# the bar runs out nearly straight, then bends back ~29 deg and down ~11 deg to the grips (comfort-study.md).
BAR_DX,BAR_DZ=15,-30   # Nov 14 comfort update: grips 15 fwd / 30 down with the 31 mm lower seat
BAR_C=(995+BAR_DX,1125+BAR_DZ)   # was (995,1125): Nov 11 (seat/bar look + standing reach): grips 50 up, 20 back vs the comfort-study bar -> 279mm above the seat
def bar_pts(side):   # bar centre end, bend corner, grip start
    return [V(BAR_C[0],side*40,BAR_C[1]),V(980+BAR_DX,side*210,1120+BAR_DZ),V(930+BAR_DX,side*300,1100+BAR_DZ)]
for s in (-1,1):
    rb=steer_pl.multVec(V(-14,s*40,227))
    add(sname('Bar_riser',s),cyl((rb.x,rb.y,rb.z),(BAR_C[0],s*40,BAR_C[1]-12),14).fuse(cyl((BAR_C[0],s*25,BAR_C[1]),(BAR_C[0],s*55,BAR_C[1]),17)),
        'RunningGear','Pull-back bar riser with clamp, illustrative',color=(.1,.1,.11))
stubs=[]
for side in [-1,1]:
    stub=cyl((540,side*110,PZ),(540,side*150,PZ),20,15);stubs.append(stub)
    add(sname('Independent_hollow_pivot_stub',side),stub,'Chassis','Proposed 40OD/30ID fixed frame stub; loads/fits not approved')
    add(sname('Pivot_6008_size_reference',side),cyl((540,side*125,PZ),(540,side*140,PZ),34,20),'Chassis','6008 dimensional reference only')
add('Pivot_reference',Part.makeCompound(stubs),'Keepouts','Independent outboard pivots',hide=True)
# Rear shock: one central direct-mount coil-over, no linkage (KTM PDS layout), chosen by tools/rear-kinematics.py.
# Lower eye on a tower 210mm behind the pivot and 120mm above the arm line; top eye hangs from a cross tube
# between the tail rails. Lowering the pivot to PZ freed this space above the motor.
import importlib.util as _ilu
_sp=_ilu.spec_from_file_location('rear_kinematics',str(R/'tools/rear-kinematics.py'));RK=_ilu.module_from_spec(_sp);_sp.loader.exec_module(RK)
SHOCK_S,SHOCK_HOFF,SHOCK_TOP=210.0,120.0,(482.0,642.0)   # Nov 14: top eye 18 lower (bridge under 63 mm of seat foam) and 8 back (shock 18 mm off the motor, needs 15)
SHOCK_STROKE=75.0                                         # spec: 73.5 used + 1.5 on the bump stop
SHOCK_EYE_EXT=305.0                                        # spec, rounded up from 303.9 at full droop
def shock_lower(rz):
    return RK.lower_eye(PZ,rz,SHOCK_S,SHOCK_HOFF)
SHOCK_EYE_EXT=float(math.ceil(math.hypot(SHOCK_TOP[0]-shock_lower(RZ-REAR_SAG)[0],SHOCK_TOP[1]-shock_lower(RZ-REAR_SAG)[1])))   # spec = full-droop eye length, rounded up
upper=V(SHOCK_TOP[0],0,SHOCK_TOP[1]);lx,lz=shock_lower(RZ);lower=V(lx,0,lz)
axis=lower-upper;axis.normalize()
def shock_env(lo):
    lo=V(lo[0],0,lo[1]);ax=lo-upper;ax.normalize()
    return cyl(tuple(upper+ax*30),tuple(lo-ax*30),45)
add('Shock_and_spring_keepout',shock_env((lx,lz)),'Keepouts',f'{(upper-lower).Length:.0f}mm eye distance at sag; 90mm OD spring reservation',hide=True)
body_len=SHOCK_EYE_EXT-SHOCK_STROKE-45
add('Shock_body_STUDY',cyl(tuple(upper+axis*12),tuple(upper+axis*(12+body_len)),25),'Chassis',
    'Damper body envelope (50mm OD); spec in rear-suspension.md, supplier not selected',color=(.6,.61,.63))
add('Shock_rod_STUDY',cyl(tuple(upper+axis*(12+body_len-10)),tuple(lower-axis*14),9),'Chassis','18mm damper shaft envelope',color=(.78,.79,.8))
for name,eye in [('Upper',upper),('Lower',lower)]:
    add('Shock_'+name+'_eye_STUDY',cyl((eye.x,-20,eye.z),(eye.x,20,eye.z),16,6),'Chassis','Eye with 12mm bolt, spherical bearing')
spring_len=(lower-upper).Length-60-30
helix=Part.makeHelix(spring_len/7.5,spring_len,38)
spring=Part.Wire(helix.Edges).makePipeShell([Part.Wire(Part.makeCircle(6,V(38,0,0),V(0,1,0)))],True,True)
spring.Placement=A.Placement(upper+axis*60,A.Rotation(V(0,0,1),axis))
add('Shock_spring_STUDY',spring,'Chassis','Visual coil: 88mm OD, 12mm wire; rate ~107 N/mm per rear-kinematics.py',color=(.75,.65,.2))
add('Shock_reservoir_STUDY',cyl((405,-60,680),(405,60,680),22),'Chassis','Remote reservoir under the seat (hose not modelled)',color=(.6,.61,.63))
# Shock tower on the swingarm: twin 8mm plates from the cross brace to the lower eye.
brace_c=(380,arm_z(380))
tower=Part.makeCompound([stadium(brace_c,(lx,lz),22,sy*36 if sy<0 else 22,sy*22 if sy<0 else 36) for sy in (-1,1)])   # A356 casting, 14mm webs (FEA CR-14)
tower=tower.cut(cyl((0,-120,RZ),(0,120,RZ),RR+21))   # trimmed to stay 20 off the 650mm tyre (supplier CR-6)
add('Swingarm_shock_tower',tower,'Chassis','PROPOSED twin 8mm plates, brace to shock lower eye; section/fatigue NOT qualified',color=(.13,.14,.15))
# Top mount: cross tube between the tail rails at X490 (rail Y+-183, Z724) and twin plates down to the eye.
t_=(568-SHOCK_TOP[0])/628;yt=RAIL_NODE_Y-(RAIL_NODE_Y-TAIL_RAIL_END_Y)*t_;zt=692+(TAIL_RAIL_END-692)*t_
# Forged box bridge (structural-fea.md CR-10), Nov 14: laid flat, 80 long x 45 tall x 5 wall (section modulus 15.9 cm3,
# >= the 70x40x4 upright's 14.5), its top level with the rail centres, so the seat pan passes 10 mm over it.
add('Tail_shock_cross_tube',box(SHOCK_TOP[0]-40,-yt,zt-45,80,2*yt,45).cut(box(SHOCK_TOP[0]-35,-yt-1,zt-40,70,2*yt+2,35)),'Chassis',
    'Forged 4130 box shock bridge 80x45x5 laid flat (structural-fea.md CR-10, re-sectioned Nov 14)',color=(.1,.105,.11))
SHOCK_TUBE=(SHOCK_TOP[0],zt)   # X and top Z of the bridge, for the seat-pan relief
for sy in (-1,1):   # diagonals from the bridge to the pivot nodes (CR-12)
    tube(sname('Shock_bridge_diagonal',sy),(SHOCK_TOP[0],sy*60,zt-22),(540,sy*180,PZ+30),12.5,10)
add('Shock_top_bracket',Part.makeCompound([stadium((SHOCK_TOP[0],zt-22),SHOCK_TOP,18,sy*34 if sy<0 else 22,sy*22 if sy<0 else 34) for sy in (-1,1)]),
    'Chassis','PROPOSED twin 8mm plates, cross tube to shock top eye',color=(.13,.14,.15))
# Swingarm rotation about the pivot (= motor axis) to a given rear axle height, for sweeps of arm-mounted parts.
arm_static=V(0,0,RZ)-V(540,0,PZ)
def arm_rot(rz):
    rx,_=rear_axle(rz);tgt=V(rx,0,rz)-V(540,0,PZ)
    phi=math.atan2(tgt.z,tgt.x)-math.atan2(arm_static.z,arm_static.x)
    pl=A.Placement(V(0,0,0),A.Rotation(V(0,1,0),-math.degrees(phi)),V(540,0,PZ))
    assert (pl.multVec(V(0,0,RZ))-V(rx,0,rz)).Length<0.01
    return pl
REAR_POS=[RZ-REAR_SAG+REAR_TRAVEL*k/8 for k in range(9)]   # droop to real bump (+119 above static; the shock stroke ends there)

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
def solid(top,bot,half,sec=None):
    s=side_face(top,bot);s.translate(V(0,-400,0));s=s.extrude(V(0,800,0))
    if sec:s=s.common(sec)    # cross-section before plan: the other order returned an empty solid for the lower covers
    p=plan_face(half);p=p.extrude(V(0,0,1400))
    return s.common(p)
def panel(top,bot,half,t=3,r=12,open_bottom=False,open_top=False,open_front=False,open_rear=False,section=None,inner_bot=None):
    # section(t): optional cross-section prism (inset by t) that shapes the panel in the Y-Z plane.
    # inner_bot: explicit inner bottom/front line, for a front wall that climbs (z+t would not thicken it).
    sec=section or (lambda t:None)
    out=rounded(solid(top,bot,half,sec(0)),r)
    it=[(x,z-t) for x,z in top];ib=list(inner_bot) if inner_bot else [(x,z+t) for x,z in bot];ih=[(x,w-t) for x,w in half]
    if open_bottom:ib=[(x,z-80) for x,z in bot]
    if open_top:it=[(x,z+400) for x,z in top]   # far above: a steep top edge (knee pocket) made the +80 spline dip and leave a skin across the bike
    def shift(rows,i,dx):rows[i]=(rows[i][0]+dx,rows[i][1])
    for rows in (it,ib,ih):
        shift(rows,0,-40 if open_rear else t)
        if not (rows is ib and inner_bot):shift(rows,-1,40 if open_front else -t)
    inner=solid(it,ib,ih,sec(t))
    shell=out.cut(rounded(inner,max(r-t,1)))
    if not (inner.Volume>0 and shell.Volume<0.5*out.Volume):raise RuntimeError('panel came out solid, not a shell')
    return shell
# Battery-bay cross-section. With the lower rails gone the covers only have to clear the pack (+-194):
# 414mm wide (V1.0: 444), near-vertical sides with a small bevel into the Z183 belly. The belly sits
# 15mm under the Z198 pack floor; the skid plate hangs below it.
BELLY_Z=183.0
def belly_section(t=0,hw=217,hb=191,zb=211.5,zbot=BELLY_Z):   # covers +10 for the 408mm pack; bevel on the lean line (dynamics-study.md CR-5)
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
def _notch(extra):   # one fused solid of every frame tube grown by 'extra' (a compound of overlapping cylinders made the cut fail)
    cs=[cyl(a,b,ro+extra) for a,b,ro in frame_segs];return cs[0].multiFuse(cs[1:]).removeSplitter()
frame_notch=_notch(6)   # tube + 6mm
# Lamp reservations are pockets in the panels, so the panels are cut around them.
lamps=dict(Taillamp_installation_STUDY=box(-186,-50,806,16,100,20))
for side in [-1,1]:
    lamps[sname('Front_indicator_reserve',side)]=box(1290,side*205-14,680,40,28,20)   # 410mm apart, 125 below the lamp band (FMVSS 108 / R53)
    lamps[sname('Rear_indicator_reserve',side)]=box(-318,116 if side>0 else -146,664,36,30,22)   # on the plate hanger, 262mm apart
lamp_cut=Part.makeCompound(list(lamps.values()))
# Re-trace (Oct 26) on a 50mm grid over the baseline. The image's wheel axles sit ~35mm below the model's,
# so traced Z values carry +35mm. Tank/battery split is the baseline's slanted seam, not a flat line.
seam=[(690,668),(800,645),(900,622),(1000,600),(1095,579)]
# Upper body: tall tank (top Z955), cockpit cheeks either side of the screen, beak nose with the headlamp,
# fairing front edge dropping to Z575 ahead of the battery box. Open underneath.
UB_TOP=[(690,846),(725,866),(770,897),(820,925),(870,945),(920,956),(1000,955),(1060,945),(1110,937),
        (1170,962),(1215,985),(1258,972),(1300,948),(1360,922),(1410,900),(1462,872)]
# Front re-trace (Nov 11, close crop of the baseline): the side shroud now drops to a point at Z532 beside the fork,
# over the battery cover's front corner (its walls sit at Y+-205+, outside the tyre and fender at any lock), and the
# beak is deeper, 812 at the tip (was 846), so the lamp unit can be a real 40mm-tall lens instead of a slit.
UB_BOT=seam[:-1]+[(1060,587),(1105,560),(1150,532),(1185,538),(1215,580),(1248,645),(1275,712),(1300,762),(1345,772),
                  (1395,790),(1435,803),(1462,812)]
UB_HALF=[(690,215),(760,220),(850,222),(1050,222),(1200,205),(1340,160),(1420,112),(1462,40)]
# Nov 12 surfacing pass ("see how much smoother the reference is"): panels were the side outline extruded across
# the bike, cut by a constant section, so every side was a flat wall. crowned_panel() keeps the traced side outline
# and plan width exactly (so every clearance is unchanged) and lofts a cross-section along X instead: a crowned top,
# rounded shoulders, a crisp shoulder crease, and a lower tuck that meets the next panel flush.
def _span(face,x,axis):
    bb=face.section(Part.makeLine(V(x,0,-900) if axis=='z' else V(x,-900,0),V(x,0,3000) if axis=='z' else V(x,900,0))).BoundBox
    return (bb.ZMin,bb.ZMax) if axis=='z' else (0.0,bb.YMax)
def _xsec(x,prof,zt,zb,w,N=64):
    # one half-curve (flat tangent at the crown) mirrored, so the section is exactly symmetric and peaks on the centreline
    half=prof(w,zt,zb)
    ghost=[V(x,-half[1][0],half[1][1])]   # mirrored neighbour, so the curve leaves the crown level
    c=Part.BSplineCurve();c.interpolate(ghost+[V(x,y,z) for y,z in half]+[V(x,.4*half[-1][0],zb)])
    u0=c.parameter(V(x,0,half[0][1]))
    pts=c.toShape(u0,c.LastParameter).discretize(N//2+1)          # top centre .. bottom
    ring=pts+[V(x,0,zb)]+[V(x,-p.y,p.z) for p in reversed(pts)][:-1]
    bs=Part.BSplineCurve();bs.interpolate(ring,PeriodicFlag=True);return Part.Wire(bs.toShape())
def crowned_panel(top,bot,half,prof,t=3,r=12,open_bottom=False,open_front=False,step=25.0,tuck=lambda x:1.0):
    sf=side_face(top,bot);pf=plan_face(half)
    x0,x1=max(top[0][0],bot[0][0]),min(top[-1][0],bot[-1][0])
    n=max(8,int((x1-x0)/step));xs=[x0+.3+(x1-x0-.6)*i/n for i in range(n+1)]
    outer_w,inner_w=[],[]
    for x in xs:
        zb,zt=_span(sf,x,'z');w=_span(pf,x,'y')[1]
        wo=_xsec(x,lambda w_,zt_,zb_:prof(w_,zt_,zb_,tuck(x)),zt,zb,w);outer_w.append(wo)
        inner_w.append(_xsec(x,lambda w_,zt_,zb_:prof(w_,zt_,zb_,tuck(x)),zt-t,zb-5,w-t))   # same profile, t smaller; runs below the bottom so it opens
    def rs(w,N=48):   # same point count on every section, so the loft can match them (unmatched sections made it hang)
        bs=Part.BSplineCurve();bs.interpolate(w.discretize(N+1)[:-1],PeriodicFlag=True);return Part.Wire(bs.toShape())
    # _xsec already gives every section the same point count, so the loft matches them
    def loft(ws):
        l=Part.makeLoft(ws,True,False);return l if l.Volume>0 else l.reversed()
    out=loft(outer_w).common(solid(top,bot,half))   # no fillet: it fails on lofted edges; the sections are already rounded
    il=loft(inner_w)
    if open_front:   # carry the last inner section on forward so the front stays open
        il=il.fuse(Part.Face(inner_w[-1]).extrude(V(80,0,0)))
    # the sections already follow the outline, so trim the inner loft by the same outline and keep t-thick end walls
    ends=box(x0+t,-900,-900,(x1-x0-2*t)+(80 if open_front else 0),1800,3000)
    inner=il.common(solid(top,bot,half)).common(ends)
    shell=out.cut(inner)
    if open_bottom:   # slab under the bottom line, raised by the wall thickness, removes the bottom skin
        pts=[(bot[0][0]-60,bot[0][1]+t)]+[(x,z+t) for x,z in bot]+[(bot[-1][0]+60,bot[-1][1]+t),(bot[-1][0]+60,-400),(bot[0][0]-60,-400)]
        slab=Part.Face(Part.makePolygon([V(x,-500,z) for x,z in pts+[pts[0]]])).extrude(V(0,1000,0))
        shell=shell.cut(slab)
    if not (inner.Volume>0 and shell.Volume<0.5*out.Volume):raise RuntimeError('crowned panel came out solid, not a shell')
    return _heal(shell),_heal(out)
def _heal(s):
    # lofted BSpline skins come out of the booleans with 'self-intersecting wire' faults; a STEP write/read
    # rebuilds the face curves and gives a valid solid that later cuts accept
    if s.isValid():return s
    import tempfile,os
    fn=os.path.join(tempfile.gettempdir(),'bavuso_heal_%d.step'%os.getpid());s.exportStep(fn);r=Part.read(fn);os.remove(fn)
    r=r.Solids[0] if len(r.Solids)==1 else r
    if not r.isValid():raise RuntimeError('crowned panel still invalid after STEP heal')
    return r
def tank_prof(w,zt,zb,k=1.0):
    h=zt-zb;zc=zb+min(.60*h,max(.45*h,h-150))   # shoulder crease ~60% up, never more than 150 below the top
    return [(0,zt),(.50*w,zt-.012*h),(.72*w,zt-.04*h),(.85*w,zt-.09*h),(.93*w,zt-.16*h),(.975*w,zc+.30*(zt-zc)),
            (.993*w,zc+.10*(zt-zc)),(w,zc),(.992*w,zc-.12*(zc-zb)),(.97*w,zc-.55*(zc-zb)),(.945*w,zb+.08*(zc-zb)),(.935*w,zb)]
def tidy(s,tag):   # booleans on lofted skins can leave tiny defects; repair them and say where
    if s.isNull():raise RuntimeError('boolean returned a null shape at '+tag)
    if _TRACE:print(f'[{_time.time()-_T0:7.1f}s] tidy {tag}',flush=True)
    if s.isValid():return s
    t=s.copy();t.fix(1e-4,1e-5,1e-2)
    if not t.isValid():
        t=Part.Solid(Part.Shell(t.Faces)) if len(t.Solids)<=1 else t
    print('tidy',tag,'valid after fix:',t.isValid(),flush=True);return t
upper_body,ub_outer=crowned_panel(UB_TOP,UB_BOT,UB_HALF,tank_prof,r=15,open_bottom=True);upper_body=tidy(upper_body,'crowned')
upper_body=tidy(upper_body.cut(steerKeep.Shape),'steer');upper_body=tidy(upper_body.cut(frame_notch),'notch')
# Headlamp: a full-width light band through the beak (smoked lens) with a DRL blade along its top edge. Both are
# the nose's own outer surface clipped to a horizontal band, so they sit flush with the fairing like the baseline's
# slim LED eye. The band replaces the earlier 55x180x24 lamp reservation box at the same place.
nose_solid=ub_outer   # the lens and DRL take the crowned nose surface
headlamp=nose_solid.common(box(1392,-200,816,90,400,40))
drl=nose_solid.common(box(1392,-200,857,90,400,5))
upper_body=tidy(upper_body.cut(box(1392,-200,816,90,400,46)),'nosebox');upper_body=tidy(upper_body.cut(lamp_cut),'lamp')
def xz_prism(pts,y0,y1):
    f=Part.Face(Part.makePolygon([V(x,0,z) for x,z in pts+[pts[0]]])).extrude(V(0,abs(y1-y0),0));f.translate(V(0,min(y0,y1),0));return f
# Side vents in front of the radiators, slanted to follow the shroud's front edge as in the baseline.
VENT=[(1000,610),(1090,610),(1140,730),(1050,730)]
def vent_x(z):return 1000+(z-610)*50/120
for side in [-1,1]:
    upper_body=tidy(upper_body.cut(xz_prism(VENT,side*185,side*245)),'vent')
ub_obj=add('Upper_body_fairing_tank_STUDY',upper_body,'BodyStudy',
    'PROPOSED 3mm shell traced from baseline image; open below, steering cavity, frame notches and grilles cut; tooling/CFD/fixings unresolved',color=(.11,.12,.13))
# Lower body: battery side covers and belly pan, open top, open rear onto the motor. Its front wall follows
# the front tyre's travel envelope 22mm off (x_cover), and the seam line is cut short where it meets that wall.
# Above Z480 the wall keeps 30mm (not 22) off the straight-ahead tyre: with the bars turned 20 deg at full bump the
# tyre's rear shoulder swings toward the wall's top corner and read 14.7mm there (lock sweep, Nov 11).
def x_wall(z):return x_cover(z,22.0+8.0*min(1.0,max(0.0,(z-315.0)/20.0)))  # 22 mm up to the pack front-top corner (Z307), 30 mm from Z335 (steered tyre at bump, pinch ~Z340)
xe=1095.0
for _ in range(8):
    ze=600-(xe-1000)*21/95;xe=x_wall(ze)
front_wall=[(x_wall(z),z) for z in [BELLY_Z]+list(range(215,int(ze)-14,35))]+[(xe,ze)]
lower_body=panel(top=[(585,WAIST_Z),(600,WAIST_Z),(615,POCKET_Z),(675,POCKET_Z)]+seam[:-1]+[(xe,ze)],
                 bot=[(585,BELLY_Z),(700,BELLY_Z),(1000,BELLY_Z)]+front_wall,
                 inner_bot=[(585,BELLY_Z+3),(700,BELLY_Z+3),(1000,BELLY_Z+3)]+[(x-3,max(z,BELLY_Z+3)) for x,z in front_wall],
                 half=[(585,217),(680,217),(780,217),(880,217),(980,217),(1080,217),(1112,208),(1120,196)],   # dense points: a sparse spline sagged 22mm inward into the pack
                 r=10,open_top=True,open_rear=True,section=lambda t:belly_section(-t))
lower_body=lower_body.cut(frame_notch)
lower_body=lower_body.cut(solid(UB_TOP,UB_BOT,UB_HALF).common(box(1040,-300,400,200,600,300)))   # front seam: the tank skin laps the cover
add('Lower_body_battery_covers_STUDY',lower_body,'BodyStudy',
    'PROPOSED 3mm battery side covers/belly pan; 414mm wide, front wall follows the front-tyre travel envelope; impact protection unresolved',color=(.13,.14,.15))
# Floor rises to the belly line behind the pack.
MC_X=435 if DRIVE=='ipm' else 470               # IPM: the covers reach back over the low HV cabinet
motor_cover=panel(top=[(MC_X,WAIST_Z),(585,WAIST_Z)],bot=[(MC_X,200),(585,BELLY_Z)],half=[(MC_X,215),(585,217)],
                  r=8,open_top=True,open_front=True,open_rear=True,section=lambda t:belly_section(-t))
motor_cover=motor_cover.cut(frame_notch)
for side in [-1,1]:motor_cover=motor_cover.cut(cyl((420,side*140,270),(420,side*240,270),18))   # peg mount bosses pass through
# No rear bulkhead: with the motor on the lowered pivot, the swingarm arms pass through where it stood.
waist_ledge=Part.makeCompound([rounded(box(x0,(182 if sy>0 else -212),z0-3,l,30,3),1) for sy in (-1,1) for x0,l,z0 in ((530,68,WAIST_Z),(617,58,POCKET_Z))])   # between the tail wall (<=182) and the cover's inner face (>=213)
add('Waist_ledge_plates',waist_ledge,'BodyStudy','3mm plates closing the cover top between the tail panel and the cover wall under the thighs (Nov 20)',color=(.12,.13,.14))
add('Motor_side_covers_STUDY',motor_cover,'BodyStudy',
    'PROPOSED 3mm motor side covers/belly behind the battery covers; swingarm and shock pass the open rear; cooling/belt access unresolved',color=(.12,.13,.14))
# Round cap over the swingarm pivot / motor axis on each motor cover, as in the baseline: a 92mm ring with a recessed face and centre boss.
for side in [-1,1]:
    y0=side*222.5      # on the motor cover, now 10 further out
    cap=cyl((540,y0,PZ),(540,y0+side*6,PZ),46).cut(cyl((540,y0+side*4,PZ),(540,y0+side*7,PZ),32)).fuse(cyl((540,y0,PZ),(540,y0+side*5,PZ),16))
    add(sname('Pivot_cover_cap',side),cap,'BodyStudy','Pivot/motor-axis cover cap on the motor cover, illustrative',color=(.07,.075,.08))
for side in [-1,1]:
    slats=[xz_prism([(vent_x(z)+5,z),(vent_x(z)+85,z),(vent_x(z+7)+85,z+7),(vent_x(z+7)+5,z+7)],side*205,side*213) for z in [616+k*19 for k in range(6)]]
    louvres=Part.makeCompound(slats+[xz_prism(VENT,side*186,side*189)])   # + dark backing plate
    # (Nov 14) the tank-side grille is covered by the radiator pod now; its louvres are in the pod mouth.
    # Dark trim strip inside the slanted tank/cover seam so the filleted joint does not show daylight.
    trim=Part.Face(Part.makePolygon([V(700,0,652),V(1090,0,567),V(1090,0,591),V(700,0,676),V(700,0,652)])).extrude(V(0,4,0))
    trim.translate(V(0,side*210-2,0))
    trim=trim.cut(box(960,-300,400,300,600,400))   # the radiator pod covers the seam ahead of X960
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
# Raised with the belly: the belly plate starts 14mm above the Z183 belly line.
batt_pts=[(1040,578),(705,630),(674,522),(600,470),(626,340),(1045,340),(1060,500)]
belly_pts=[(1050,322),(640,322),(600,255),(640,197),(1045,197),(1060,255)]
for side in [-1,1]:
    parts=[]
    for pts,yin in [(batt_pts,217),(belly_pts,217)]:
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
    bolts=[cyl((x,side*211.5,z),(x,side*214.5,z),5.5) for x,z in [(1020,565),(700,612),(625,455),(650,360),(1025,360),(1040,470),(850,600),(850,355)]]
    add(sname('Panel_bolts',side),Part.makeCompound(bolts).cut(lower_body),'BodyStudy','M6 button-head positions, illustrative',color=(.25,.26,.27))
# Tail and under-seat side panels, open below and toward the tank; tail tip rises above the seat end like the baseline.
# Extra top points stop the spline swinging below Z776 over the tyre (full-bump tyre top is Z754 at X-22).
# Re-traced Nov 11 from a close crop of the baseline (X=(1310-px)*1.35, Z=(935-py)*1.35+25): the side cover under
# the seat drops in a wedge to Z512 at X600, over the motor-cover top, so only the lower half of the shock shows
# below it as in the baseline; its front edge rises beside the battery plate's rear edge. Half-width 220 there keeps
# the inner face 6mm outside the rails (195+16), so the rails need no slot through the wall; the tail tip is widened
# (124 at X-60) to clear the tail-rail ends.
TAIL_TOP=[(-190,860),(-175,852),(-150,844),(-120,842),(-60,841),(0,831),(100,814),(300,771),(430,746),(560,742),(620,749),(690,758)]   # deck under the seat 5mm over the raised 38mm tail rails
TAIL_TOP=[(x,z+(RAIL_LIFT(x) if True else 0)) for x,z in TAIL_TOP]
TAIL_BOT=[(-180,782),(-100,770),(16,752),(150,705),(283,612),(400,580),(470,588),(540,WAIST_Z-5),(600,WAIST_Z-5),(615,POCKET_Z-5),(688,POCKET_Z-5)]
TAIL_HALF=[(-190,62),(-120,110),(-60,128),(16,141),(150,168),(300,198),(400,200),(470,192),(540,180),(600,178),(640,178),(690,182)]   # Nov 20: waist 356 wide under the thighs (Nov 14: 376, before: 450); tip +4 for the tail-rail ends
tail_body=panel(top=TAIL_TOP,bot=TAIL_BOT,half=TAIL_HALF,r=10,open_bottom=True,open_front=True)
tail_body=tail_body.cut(_notch(2)).cut(lamp_cut)
# Undertray: closes the tail from below. A 3mm skin 25-28mm outside the rear tyre's whole travel envelope (the
# check asks 20), kept 1.5mm inside the side walls and above their lower edge; frame tubes pass through 1mm-clearance
# holes. Behind X-85, where the tail's lower edge sits above that skin, a flat 3mm floor follows the edge instead.
def tyre_env(dr):
    cs=[cyl((rear_axle(z)[0],-260,z),(rear_axle(z)[0],260,z),RR+dr) for z in [RZ-REAR_SAG+(REAR_TRAVEL+REAR_SAG)*i/20 for i in range(21)]]
    return cs[0].multiFuse(cs[1:]).removeSplitter()
tail_in=solid([(x,z-4.5) for x,z in TAIL_TOP],TAIL_BOT,[(x,w-4.5) for x,w in TAIL_HALF])
ring=tyre_env(28).cut(tyre_env(25)).common(tail_in).common(box(-85,-300,0,345,600,1200))
fl=[(-183,782.5),(-140,779),(-100,778),(-85,778)]   # front edge 22mm off the 180 tyre at full bump
floor_=solid([(x,z+3) for x,z in fl],fl,[(x,w-4.5) for x,w in TAIL_HALF])
tube_holes=_notch(1)
# Plate hanger: a cast arm from inside the tail tip down and back to the plate, a bracket behind the plate, the plate
# lamp above it and the rear indicators on short stalks (262mm apart; FMVSS 108 asks 229mm). 20mm+ off the tyre at full bump.
hanger_line=((-150,797),(-318,662))
plate_hanger=stadium(*hanger_line,9,-32,32).fuse(box(-338,-25,600,16,50,70))
undertray=Part.makeCompound([s for s in (ring.cut(tube_holes),floor_.cut(stadium(*hanger_line,12,-36,36))) if s.Volume>1])
# Thick stepped saddle: pillion pad Z889 stepping down at X284 to the rider dip at Z800 (traced +35mm).
# Nov 11 (seat "looks uncomfortable"): lofted through crowned sections instead of an extruded slab: domed top, rolled
# edges, sides tucking in to a pan 82% as wide. The narrower pan clears the tail rails (Y166 inner at X470), so it drops
# 13mm under the rider: foam at the rider's sit point is ~78mm (was ~65; touring seats use 70-90).
# Nov 14 ("flat bench, legs hang over it"): a dished rider pocket 31 mm lower with its floor at X530, a 60 mm step
# up to the pillion behind it, and a nose that narrows to ~250 mm between the thighs before climbing onto the tank.
SEAT_TOP=[(-112,862),(-100,874),(-20,889),(100,881),(216,866),(270,856),(300,838),(330,812),(370,794),(430,784),(490,780),
          (540,779),(590,783),(630,795),(660,815),(690,848),(720,872),(745,888),(762,898)]   # rider pad +10 (comfort-study.md); nose rides up the tank (Nov 12)
SEAT_TOP=[(x,z+(RAIL_LIFT(x) if x<=300 else 0)) for x,z in SEAT_TOP]
SEAT_BOT=[(-112,822),(0,800),(300,768),(400,728),(450,712),(580,712),(640,735),(682,770),(762,790)]
SEAT_HALF=[(-112,92),(-60,118),(0,138),(100,161),(200,183),(260,192),(300,182),(360,177),(430,176),(490,172),(540,163),(590,149),(640,135),(690,124),(730,114),(762,96)]
# Nov 12 (seat "still does not look comfortable"): the 330mm seat sat sunk in the 440mm tail like a cushion in a tub,
# with the tail walls up to ~40mm below its top. Now the seat is as wide as the tail (3mm proud) and its upholstered
# sides ARE the top of the side profile, as in the baseline: ~60mm of visible side, rolled edge, flat-crowned top.
# The pan edge rides 8mm over the subframe rails; a centre pan between the rails drops to SEAT_BOT for foam depth.
def rail_top(x):   # top of the subframe rail (tail rail behind X568, upper rail ahead) under the seat edge
    return 711.0+(568-x)*(TAIL_RAIL_END-692)/628 if x<=568 else 734.0+(x-570)*65/480   # 38mm rails (FEA), Nov 14 node at Z715/Y152
def rail_y(x):return RAIL_NODE_Y-(RAIL_NODE_Y-TAIL_RAIL_END_Y)*(568-x)/628 if x<=568 else urail_y(x)
def lerp(pts,x):
    for (x0,v0),(x1,v1) in zip(pts,pts[1:]):
        if x0<=x<=x1:return v0+(v1-v0)*(x-x0)/(x1-x0)
    return pts[0][1] if x<pts[0][0] else pts[-1][1]
def seat_section(x,shrink=1.0):
    zt,w=lerp(SEAT_TOP,x),lerp(SEAT_HALF,x)*shrink;ze=min(max(rail_top(x)+8,782 if x>=690 else 0),zt-40);d=zt-ze   # nose base 10 over the inverter (Z772)
    zt=ze+d*(.55+.45*shrink);d=zt-ze;c=min(.75*d,48)   # c: depth of the rolled top edge
    prof=[(0,zt),(.40*w,zt-.05*c),(.70*w,zt-.18*c),(.86*w,zt-.38*c),(.95*w,zt-.65*c),(.995*w,zt-c),(w,ze+.3*(d-c)),(.975*w,ze+2),(.86*w,ze)]
    pts=[V(x,y,z) for y,z in prof]+[V(x,.4*w,ze),V(x,-.4*w,ze)]+[V(x,-y,z) for y,z in reversed(prof[1:])]
    c=Part.BSplineCurve();c.interpolate(pts,PeriodicFlag=True);return Part.Wire(c.toShape())
SEAT_X=[-112,-104,-80,-20,60,150,230,276,300,326,356,400,450,500,540,580,620,655,690,720,745,756,762]
seat=Part.makeLoft([seat_section(x,.72 if x in (-112,762) else .9 if x in (-104,756) else 1.0) for x in SEAT_X],True,False)
seat=seat if seat.isValid() and seat.Volume>0 else seat.reversed()
# Centre pan between the rails (8mm off their inner faces): drops to SEAT_BOT under the rider for ~78mm of foam.
def pan_sec(x):
    b=min(rail_y(x)-(14 if x<=568 else 16)-8,.8*lerp(SEAT_HALF,x));zb=lerp(SEAT_BOT,x);zu=min(rail_top(x)+8,lerp(SEAT_TOP,x)-40)+6
    return Part.makePolygon([V(x,y,z) for y,z in [(-b+12,zb),(b-12,zb),(b,zb+12),(b,zu),(-b,zu),(-b,zb+12),(-b+12,zb)]])
seat=seat.fuse(Part.makeLoft([pan_sec(x) for x in (330,380,440,486,540,590)],True,True)).removeSplitter()
# Pan relief over the shock-top cross tube: the dropped pan (Z732) would sit 6 mm into it. A 48 mm wide channel
# moulded into the pan keeps 10 mm over the bracket plates (14 over the tube) and 10 mm fore/aft, and leaves ~66 mm of foam over it (78 elsewhere).
seat=seat.cut(box(SHOCK_TUBE[0]-50,-200,600,100,400,SHOCK_TUBE[1]+10-600))   # +14: the bracket plates stand 4 mm proud of the tube
seat=seat.cut(_notch(1))   # pan relieved 1 mm round the tail rails (Nov 20: rails pulled in to +-104..125 grazed the pan)
# Piped welt along each top edge, rider and pillion pads, as on a stitched production seat (short segments + spheres).
welts=[]
for xs in ((-96,270),(322,735)):
    for sy in (-1,1):
        pts=[V(x,sy*.985*lerp(SEAT_HALF,x),lerp(SEAT_TOP,x)-.8*min(.75*(lerp(SEAT_TOP,x)-min(rail_top(x)+8,lerp(SEAT_TOP,x)-40)),48)) for x in range(xs[0],xs[1]+1,12)]
        welts+=[Part.makeCylinder(2.6,(b-a).Length,a,b-a) for a,b in zip(pts,pts[1:])]+[Part.makeSphere(2.6,p) for p in pts]
seat_welt=Part.makeCompound(welts)
# The seat nose laps over the tank's rear slope (as in the baseline) instead of butting into a wall: the tank shell
# is cut where the nose sits. The BMS below starts at X775, 13mm ahead of the nose tip.
upper_body=tidy(upper_body.cut(seat),'seat');ub_obj.Shape=upper_body
ub_proxy=solid(UB_TOP,UB_BOT,UB_HALF)   # plain outline solid: cuts against the crowned BSpline skin hang, and these trims only need the outline
seat_welt=seat_welt.cut(ub_proxy)   # the piping runs into the tank skin where the nose laps over it
tail_body=tail_body.cut(seat).cut(box(SHOCK_TUBE[0]-50,-160,600,100,320,SHOCK_TUBE[1]+10-600))   # seat pan nests into the tail top; no skin in the bridge channel (inside the walls: +-200 cut a see-through window in each side, fixed Nov 20)
add('Tail_side_panels_STUDY',tail_body,'BodyStudy','PROPOSED 3mm subframe covers traced from baseline; passenger rating not established',color=(.11,.12,.13))
add('Seat_two_level_STUDY',seat,'BodyStudy','PROPOSED stepped rider/passenger saddle traced from baseline; foam/pan/fit unresolved',color=(.06,.065,.07))
add('Seat_welt',seat_welt,'BodyStudy','Piped welt along the seat top edges, illustrative',color=(.05,.05,.055))
undertray=undertray.cut(tail_body)   # trims the 8 mm3 where the skin met the wall's inner fillet
add('Tail_undertray_STUDY',undertray,'BodyStudy','PROPOSED 3mm undertray/inner fender, 25mm outside the rear tyre travel envelope; drainage and fixings unresolved',color=(.08,.085,.09))
# Rear rack over the tail tip (the baseline has one): 8mm aluminium plate with two slots, on two posts down to the tail top.
tail_outer=rounded(solid(TAIL_TOP,TAIL_BOT,TAIL_HALF),10)
rack=rounded(box(-222,-88,868,108,176,8),3)
for sy in (-1,1):rack=rack.cut(box(-204,20 if sy>0 else -60,860,72,40,20))
for sy in (-1,1):rack=rack.fuse(cyl((-150,sy*68,870),(-150,sy*68,800),7).cut(tail_outer))
add('Rear_rack_STUDY',rack,'BodyStudy','PROPOSED aluminium luggage/grab rack on two posts; load rating and subframe mounts unresolved',color=(.1,.105,.11))
skid=box(430,-175,176,660,350,6)   # 6mm 5083, X430-1090 (compliance-and-validation.md CR-6): the 4mm plate collapsed at 4.9 kN
add('Belly_skid_plate_STUDY',skid,'BodyStudy','PROPOSED 4mm aluminium skid plate under the belly; sets the static ground clearance',color=(.2,.21,.22))
# Screen, lamps, mirrors, controls.
sp=[V(1388,-118,898),V(1388,118,898),V(1128,145,1222),V(1128,-145,1222)]
screen=Part.Face(Part.makePolygon(sp+[sp[0]])).extrude(V(4.6,0,3.8)).cut(ub_proxy)   # base tucked into the fairing top
add('Windscreen_STUDY',screen,'BodyStudy','PROPOSED 6mm screen traced from baseline; optics/buffeting unresolved',color=(.6,.8,.85))
add('Headlamp_installation_STUDY',headlamp,'BodyStudy','Full-width LED light band (smoked lens) flush with the beak; approved optical unit not selected',color=(.05,.05,.06))
add('Headlamp_DRL_blade',drl,'BodyStudy','DRL light blade along the top of the lamp band; optics not selected',color=(.95,.95,.97))
add('Taillamp_installation_STUDY',lamps['Taillamp_installation_STUDY'],'BodyStudy','Tail stop lamp reservation',color=(.7,.08,.05))
# Fender hugs the tyre (12mm) from a forward beak at 55deg to a trailing skirt at 165deg, with side skirts.
def arc_wedge(cx,cz,a0,a1,R=420):
    pts=[(cx,cz)]+[(cx+R*math.cos(math.radians(a)),cz+R*math.sin(math.radians(a))) for a in range(a0,a1+1,5)]
    f=Part.Face(Part.makePolygon([V(x,-200,z) for x,z in pts+[pts[0]]]));return f.extrude(V(0,400,0))
# Nov 11, from the tyre-plus-fender lock sweep (checks below): the fender is 10mm off the tyre (was 12-20) so it clears
# the lower clamp by 11mm at full bump (was 7), and its rear skirt ends at 125 deg (was 165): the 165-deg tail came
# within 1mm of the battery cover's front wall at full bump, and the 140-deg one within 15mm of the down-links.
frontFender=cyl((FX,-72,FZ),(FX,72,FZ),RF+16,RF+10)
for s in (-1,1):frontFender=frontFender.fuse(cyl((FX,s*72-(4 if s>0 else 0),FZ),(FX,s*72+(0 if s>0 else 4),FZ),RF+16,RF-12))
frontFender=frontFender.common(arc_wedge(FX,FZ,55,125))
add('Front_fender_STUDY',frontFender,'BodyStudy','Proposed fender on fork lowers; steering/bump mounts not validated',color=(.11,.12,.13))
rearHugger=cyl((0,-100,RZ),(0,100,RZ),347,337)   # supplier CR-7: clears the 650x190 tyre
for s in (-1,1):rearHugger=rearHugger.fuse(cyl((0,s*100-(4 if s>0 else 0),RZ),(0,s*100+(0 if s>0 else 4),RZ),347,313))
rearHugger=rearHugger.common(arc_wedge(0,RZ,35,105))
add('Rear_hugger_STUDY',rearHugger,'BodyStudy','Proposed swingarm-mounted hugger; bump clearance follows wheel',color=(.11,.12,.13))
grip=V(*P['grip_reference_mm'])
for side in [-1,1]:
    bp=bar_pts(side)
    # Nov 14: one continuous bent bar (a ~70 mm bend) instead of two straight tubes meeting at a ball.
    u0=bp[1]-bp[0];u0.normalize();gd_=bp[2]-bp[1];gd_.normalize()
    a_=bp[1]-u0*55;b_=bp[1]+gd_*45;m_=(a_+b_)*.25+bp[1]*.5
    cv=Part.BSplineCurve();cv.interpolate(Points=[a_,m_,b_,bp[2]],InitialTangent=u0,FinalTangent=gd_)
    pipe=Part.Wire(cv.toShape()).makePipeShell([Part.Wire(Part.makeCircle(11.1,a_,u0))],True,True)
    bar=Part.makeCompound([cyl(tuple(bp[0]),tuple(a_-u0*20),14.3),Part.makeCone(14.3,11.1,20,a_-u0*20,u0),pipe])
    add(sname('Bar_half',side),bar,'RunningGear','28.6mm tapered bar half: straight centre run, bent back ~29 deg / down ~11 deg to the grip; illustrative',color=(.1,.105,.11))
    gd=bp[2]-bp[1];gd.normalize()
    add(sname('Hand_grip_reserve',side),cyl(tuple(bp[2]-gd*5),tuple(bp[2]+gd*125),17),'RunningGear','Grip on the bar-end axis; throttle unselected',color=(.08,.09,.1))
    tube(sname('Mirror_stalk',side),(bp[1].x-10,bp[1].y+side*20,bp[1].z+12),(842,side*330,1200),6,3,'BodyStudy')
    # Angular mirror head like the baseline: 140 wide, 82 tall, wedge-tapered toward the rider.
    mir=Part.Face(Part.makePolygon([V(828,0,1180),V(858,0,1186),V(858,0,1276),V(828,0,1282),V(828,0,1180)])).extrude(V(0,150,0))   # 150x100 head for the legal glass
    mir=rounded(mir,12);mir.translate(V(0,280 if side>0 else -420,0))
    add(sname('Mirror_glass',side),box(825.6,(280 if side>0 else -420)+10,1191,2.4,130,80),'BodyStudy','Mirror glass, illustrative',color=(.7,.72,.75))
    add(sname('Mirror_body',side),mir,'BodyStudy','Mirror head envelope; field of view unvalidated',color=(.07,.075,.08))
    tube(sname('Peg_reference',side),(420,side*187,270),(420,side*237,270),12,8,'RunningGear')   # inner end clear of the belt-side arm sweep
    pg=rounded(box(392,239 if side>0 else -311,261,56,72,16),3)
    for xt in (394,436):pg=pg.fuse(box(xt,239 if side>0 else -311,276,10,72,4))   # cleats
    add(sname('Peg_rubber',side),pg,'RunningGear','Wide 56x72 serrated adventure peg, folding; illustrative',color=(.06,.06,.065))
    hanger=Part.Face(Part.makePolygon([V(x,0,z) for x,z in [(545,382),(562,350),(545,320),(432,254),(406,268),(418,290),(545,382)]])).extrude(V(0,6,0))
    hanger=rounded(hanger,2.5).cut(stadium((520,334),(462,296),8,-1,7))   # machined lightening slot
    hanger.translate(V(0,side*233-3,0))   # outside the pivot cap (Y222.5-228.5)
    add(sname('Peg_bracket',side),hanger,'Chassis','Machined peg hanger plate, illustrative',color=(.62,.63,.64))
    fwd=V(gd.y,-gd.x,0)*side;fwd.normalize()   # forward of the grip, in the bar plane
    add(sname('Hand_lever',side),cyl(tuple(bp[2]+fwd*32+gd*5),tuple(bp[2]+fwd*40+gd*150),5),'RunningGear',
        'Brake (right) / regen-or-rear (left) lever envelope',color=(.55,.56,.57))
    add(sname('Front_indicator_reserve',side),rounded(lamps[sname('Front_indicator_reserve',side)],8),'BodyStudy','Lamp reservation under nose',color=(.87,.5,.12))
    add(sname('Rear_indicator_reserve',side),rounded(lamps[sname('Rear_indicator_reserve',side)],9),'BodyStudy','Lamp reservation',color=(.87,.5,.12))
    add(sname('Front_caliper_reserve',side),caliper(FX,FZ,side*54,side,160,19.5,4),'RunningGear',
        'Radial 4-piston caliper envelope straddling the 320mm disc; Kawasaki 43080-0177/0178 candidate',color=(.16,.17,.18))
add('Plate_hanger_arm',plate_hanger,'BodyStudy','Cast plate hanger from inside the tail tip, with plate bracket; 20mm+ off the tyre at full bump',color=(.08,.085,.09))
_pl=box(-342,-89,520,4,178,102);_pl=_pl.makeFillet(8,[e for e in _pl.Edges if abs(e.Length-4)<.01])
add('Licence_plate_US',_pl,'BodyStudy','US 7x4in motorcycle plate envelope',color=(.85,.86,.88))
add('Plate_lamp',box(-346,-20,624,8,40,9),'BodyStudy','Plate lamp reservation above the plate',color=(.9,.92,.95))
for side in [-1,1]:
    tube(sname('Rear_indicator_stalk',side),(-300,side*32.5,675),(-300,side*116,675),5,0,'BodyStudy')
add('Bar_centre',cyl((BAR_C[0],-40,BAR_C[1]),(BAR_C[0],40,BAR_C[1]),14.3),'RunningGear','Bar centre section (28.6mm)',color=(.1,.1,.11))
add('Rear_caliper_reserve',caliper(0,RZ,66,1,133.5,22,2),'RunningGear','2-piston caliper shaped to the Kawasaki 43080-0156 candidate reserve',color=(.16,.17,.18))
add('Rear_caliper_bracket',stadium((0,RZ+10),(-110,RZ+40),14,88,96),'RunningGear','Floating caliper bracket on the axle, torque-arm stop on the swingarm; illustrative',color=(.12,.12,.13))
# ---- Brake hydraulics, switchgear and harness (Nov 11 realism pass). Every production bike shows these; their
# absence was the main thing that read as "CAD model". Routing is PROPOSED (clips, P-clamps and hose lengths for the
# full travel are not validated); hoses are 10mm OD braided with a black cover, harness legs 7mm.
def hose(name,pts,r,basis,g='RunningGear',color=(.03,.03,.035)):
    pts=[p if isinstance(p,A.Vector) else V(*p) for p in pts]
    sp=Part.BSplineCurve();sp.interpolate(pts)
    prof=Part.Wire(Part.makeCircle(r,pts[0],sp.tangent(sp.FirstParameter)[0]))
    return add(name,Part.Wire(sp.toShape()).makePipeShell([prof],True,True),g,basis,color=color)
def Ls(x,y,z):return steer_pl.multVec(V(x,y,z))     # point in the steering frame (moves with bars, clamps and fork)
for side in (-1,1):
    bp=bar_pts(side)
    gd=bp[2]-bp[1];gd.normalize();fwd=V(gd.y,-gd.x,0)*side;fwd.normalize();up=V(0,0,1)
    add(sname('Lever_perch',side),cyl(tuple(bp[2]-gd*10),tuple(bp[2]-gd*34),18).fuse(cyl(tuple(bp[2]-gd*12+fwd*14),tuple(bp[2]-gd*12+fwd*36),9)),
        'RunningGear','Lever perch clamp with pivot boss, illustrative',color=(.05,.05,.055))
    sw=cyl(tuple(bp[2]-gd*38),tuple(bp[2]-gd*62),18).fuse(rounded(Part.makeBox(22,24,16,bp[2]-gd*62-fwd*11+V(0,0,-30)),3))
    add(sname('Switch_cube',side),sw,'RunningGear','Handlebar switch housing (indicators/horn/lights left, start/mode right), illustrative',color=(.04,.04,.045))
    # Switch harness leg: under the bar, then down behind the steering head to a connector on the back of the top
    # clamp (inside the steering keep-out, where the body is already cut away).
    add(sname('Harness_connector',side),steer(rounded(box(-62,side*30-12 if side>0 else side*30-12,188,22,24,24),3)),'RunningGear',
        'Switch-harness connector on the top clamp, illustrative',color=(.05,.05,.055))
    hose(sname('Harness_bar',side),[bp[2]-gd*50+V(0,0,-34),V(985+BAR_DX,side*196,1078+BAR_DZ),V(1040,side*110,1050),Ls(-50,side*60,240),Ls(-51,side*30,212)],3.5,
         'Switch harness leg to the steering-head connector; routing PROPOSED',color=(.02,.02,.022))
    if side<0:
        # Front brake: radial-pull master cylinder on the right perch with a remote reservoir on top.
        e0=bp[2]+fwd*34-gd*8;e1=bp[2]+fwd*34-gd*62
        add('Front_master_cylinder',cyl(tuple(e0),tuple(e1),12).fuse(cyl(tuple(bp[2]+fwd*34-gd*30),tuple(bp[2]+fwd*18-gd*30),10)),
            'RunningGear','Front brake master cylinder (19mm bore class), illustrative; supplier not selected',color=(.05,.05,.055))
        rv=bp[2]+fwd*12-gd*30+up*14
        add('Front_brake_reservoir',cyl(tuple(rv),tuple(rv+up*38),15).fuse(cyl(tuple(rv+up*38),tuple(rv+up*43),16.5)),
            'RunningGear','Brake fluid reservoir with cap, illustrative',color=(.12,.12,.13))
        add('Front_master_banjo',cyl(tuple(e1+gd*4),tuple(e1-gd*10),8),'RunningGear','Banjo fitting',color=(.6,.61,.62))
        # Bar to a splitter on the front of the lower clamp, down the front of the clamps (clear of the dash).
        hose('Front_brake_hose_upper',[e1-gd*8,e1-gd*20+V(0,0,-6),Ls(62,-92,246),Ls(84,-82,175),Ls(88,-80,40),Ls(88,-55,-30),Ls(88,-12,-42)],5,
             'Front brake hose, master cylinder to the clamp splitter; routing PROPOSED')
        spl=steer(rounded(box(76,-22,-58,24,44,20),3).fuse(box(54,-6,-52,24,12,8)))
        add('Front_brake_splitter',spl,'RunningGear','Hose splitter on the lower clamp, illustrative',color=(.6,.61,.62))
    # Per caliper: from the splitter, behind the outer tube (P-clipped at its foot), then a free loop to a banjo
    # on the caliper's outer face that clears the axle-foot lugs.
    cf=V(FX+150*math.cos(math.radians(170)),side*84,FZ+150*math.sin(math.radians(170)))
    hose(sname('Front_brake_hose_caliper',side),[Ls(88,side*20,-48),Ls(80,side*70,-75),Ls(40,side*138,-125),Ls(28,side*140,-205),
         V(1328,side*132,520),V(1335,side*112,410),cf+V(0,side*10,22),cf],5,'Front brake hose, splitter to caliper; travel slack not validated')
    add(sname('Front_caliper_banjo',side),cyl(tuple(cf+V(0,-side*10,0)),tuple(cf+V(0,side*4,0)),8),'RunningGear','Banjo bolt',color=(.6,.61,.62))
# Rear brake: banjo on the caliper's outer face, over the axle boss, along the top of the left arm, then a service
# loop up to a hard-line junction on the left tail brace (the hard line along the frame is not modelled).
rc=V(-116,88,RZ-20.5)
hose('Rear_brake_hose',[rc+V(0,6,0),rc+V(-12,16,25),V(-95,118,RZ+46),V(-20,125,RZ+50),V(60,125,arm_z(60)+40),V(200,125,arm_z(200)+46),
     V(360,125,arm_z(360)+52),V(430,125,arm_z(430)+55),V(462,145,428),V(474,166,414)],5,'Rear brake hose, caliper to frame junction; arm-travel loop not validated')
add('Rear_caliper_banjo',cyl(tuple(rc+V(0,-2,0)),tuple(rc+V(0,10,0)),8),'RunningGear','Banjo bolt',color=(.6,.61,.62))
add('Rear_brake_junction',rounded(Part.makeBox(22,14,20,V(462,160,404)),2),'RunningGear','Hose-to-hard-line junction on the tail brace, illustrative',color=(.6,.61,.62))
# 7in TFT on a bracket off the top clamp, above the fork caps, so it steers with the bars. The earlier fairing-mounted
# reserve (X1188-1228, Z960-1030) overlapped the fork tubes by 109 mm3 at straight-ahead and ~117 cm3 at full lock; the
# interference sweep skipped it because both sat in RunningGear (found Nov 11).
add('Display_reserve',steer(rounded(box(30,-90,272,28,180,104),5)),'RunningGear','7in TFT housing on the top clamp, faces the rider at the steering-axis tilt; supplier not selected',color=(.15,.18,.2))
add('Display_glass',steer(box(28.6,-82,280,1.6,164,88)),'RunningGear','TFT cover glass',color=(.02,.02,.03))
add('Display_mount',steer(box(34,-22,226,20,44,47)),'RunningGear','Display bracket on the top clamp, illustrative',color=(.1,.1,.11))
ratio=3.1;pitch=14.0;fr=20*pitch/(2*math.pi);rr=62*pitch/(2*math.pi)
for name,x,z,radius in [('Front',540,PZ,fr),('Rear',0,RZ,rr)]:
    # Belt plane Y-105..-83: inboard between tyre (Y-80) and swingarm arm (Y-116 since Nov 3). The earlier plane at Y-211
    # ran through the three rails that meet at the pivot node (Y-195).
    pul=cyl((x,-127,z),(x,-105,z),radius-3,20)   # moved out 22 (supplier-parts.md CR-3): the real 170/60 reaches Y-95
    for yf in (-129,-105):pul=pul.fuse(cyl((x,yf,z),(x,yf+2,z),radius+5,20))   # belt-tracking flanges
    if name=='Rear':
        for k in range(6):
            t=k*math.tau/6;pul=pul.cut(cyl((x+75*math.cos(t),-137,z+75*math.sin(t)),(x+75*math.cos(t),-97,z+75*math.sin(t)),24))
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
belt=hull2((540,PZ),fr+5,(0,RZ),rr+5).cut(hull2((540,PZ),fr,(0,RZ),rr))
belt.translate(V(0,-126,0));belt=belt.extrude(V(0,20,0))
add('Drive_belt_14mm_STUDY',belt,'Drive','Closed 14mm-pitch belt loop at rest position; length/tension not computed',color=(.05,.05,.05))

notes=D.addObject('Spreadsheet::Sheet','DesignStatus')
for i,t in enumerate(['BAVUSO V1.0 ADVENTURE LAYOUT (REV B) - ENGINEERING DEVELOPMENT, NOT BUILD RELEASE',
 'Units mm; X forward, Y left, Z up; rear tire contact origin',
 'Structural pack 594 x 26120-class cylinders, 99s6p, 32.7 kWh; busbars/cooling/potting unresolved',
 ('EMRAX 228' if DRIVE=='emrax228' else 'IPM motor/gear case is a spec envelope; CM200')+' (inverter envelope), Orion BMS2 108 are actual supplier STEP; GX14 is drawing outline only',
 'Body traced from design/baseline black.png at 1.35 mm/px, lower covers re-shaped for the pack; styling study',
 'See v1.0/adventure-layout.md and geometry-adventure-audit.json'],1):notes.set(f'A{i}',t)
notes.setColumnWidth('A',900)
D.recompute()


# ---------------------------------------------------------------- detailed-design additions (Nov 13-14; see detailed-design/*.md)
# Cooling (thermal-study.md): side-pod radiators, 210x140x32 cores angled in plan, 30mm fans behind, pod shrouds to Y+-315.
RAD_ANG=math.degrees(math.atan2(120,172))
pods=[]
for side in [-1,1]:
    core=box(0,0,596,191,32,154);core.rotate(V(0,0,0),V(0,0,1),RAD_ANG);fan=box(15,-30,606,171,30,134);fan.rotate(V(0,0,0),V(0,0,1),RAD_ANG)
    if side<0:core=core.mirror(V(0,0,0),V(0,1,0));fan=fan.mirror(V(0,0,0),V(0,1,0))
    core.translate(V(1006,side*172,0));fan.translate(V(1006,side*172,0))
    add(sname('Radiator_core',side),core,'Cooling','Side-pod radiator 191x154x32 (0.029 m2, same face area as 210x140; under the upper rail), angled 35 deg in plan (thermal-study.md CR-1)',color=(.25,.26,.27))
    add(sname('Radiator_fan',side),fan,'Cooling','30mm slim fan behind the core, illustrative',color=(.05,.05,.05))
    # Pod = plan outline (flares to Y315) intersected with a side profile (raked front edge like the tank vents, top edge
    # following the tank line), edges rounded, then hollowed to a 3mm skin with an open, louvred front.
    pl=[(962,222),(990,300),(1060,318),(1165,312),(1182,285),(1182,222)]
    sp=[(1000,580),(1172,580),(1192,690),(1160,792),(1010,794),(985,730),(965,640)]   # top raised for the taller core
    def pod(dp,ds):
        pp=[(x,side*y) for x,y in pl];w=Part.makePolygon([V(x,y,0) for x,y in pp+[pp[0]]])
        f=Part.Face(w) if dp==0 else Part.Face(Part.Wire(Part.Face(w).makeOffset2D(-dp).OuterWire))
        a=f.extrude(V(0,0,900));a.translate(V(0,0,300))
        w2=Part.makePolygon([V(x,0,z) for x,z in sp+[sp[0]]]);f2=Part.Face(w2) if ds==0 else Part.Face(Part.Wire(Part.Face(w2).makeOffset2D(-ds).OuterWire))
        b=f2.extrude(V(0,1000,0));b.translate(V(0,-500,0))
        return a.common(b)
    po=rounded(pod(0,0),14)
    shell=po.cut(pod(3,3))
    shell=shell.cut(xz_prism([(960,630),(1005,588),(1035,588),(1000,700)],side*190,side*400))      # open raked front: the grille sits there
    shell=shell.cut(box(900,(222-40) if side>0 else -222,580,320,40,200))   # open where it meets the tank side
    grille=Part.makeCompound([xz_prism([(968+k*6.5,640+k*11),(988+k*6.5,640+k*11),(988+k*6.5,646+k*11),(968+k*6.5,646+k*11)],side*224,side*300) for k in range(5)])
    add(sname('Radiator_pod_grille',side),grille.common(pod(0,0)),'BodyStudy','Louvred grille in the pod mouth',color=(.16,.17,.18))
    pods.append(shell)
    # the tank flank is open inside the pod's side silhouette, where the core's inboard end passes into the tank
    w2=Part.makePolygon([V(x,0,z) for x,z in sp+[sp[0]]]);f2=Part.Face(Part.Wire(Part.Face(w2).makeOffset2D(-6).OuterWire))
    win=f2.extrude(V(0,70,0));win.translate(V(0,158 if side>0 else -228,0))
    upper_body=tidy(upper_body.cut(win),'podwin')
    add(sname('Radiator_pod_shroud',side),shell,'BodyStudy','3mm side-pod shroud over the radiator, open front for the grille (thermal-study.md CR-1)',color=(.11,.12,.13))
# Pack-roof service bay and oil cooler (thermal CR-2/3), saved coordinates minus 40. Pumps sit outboard of the upper junction box.
for nm,b in [('Coolant_pump_battery',(593,86,633,64,64,64)),('Coolant_pump_drive',(864,116,633,64,64,64)),
             ('Coolant_PTC_heater_5kW',(772,-132,724,86,35,64)),('Coolant_4port_valve',(598,-164,636,50,38,52)),
             ('Oil_cooler',(580,-150,430,80,40,90))]:
    add(nm,box(*b),'Cooling','Thermal service-bay envelope (thermal-study.md CR-2/3); position to be confirmed by interference sweep',color=(.3,.31,.33))
# Electrical boxes (electrical-detailed.md CR-5..8), saved coordinates minus 40.
for nm,b in [('HV_upper_junction_box',(603,-105,605,80,187,120)),('HV_charge_junction_box',(730,116,592,130,60,120)),
             ('DCDC_converter_1p2kW',(735,-180,582,190,60,130))]:
    add(nm,box(*b),'Electronics','Electrical envelope (electrical-detailed.md); position to be confirmed by interference sweep',color=(.2,.21,.22))
nacs=box(860,127,805,68,95,84)
ub_obj.Shape=upper_body
add('NACS_charge_inlet',nacs,'Electronics','Volex NACS inlet 1000V/500A behind a flap in the tank flank (electrical-detailed.md CR-7)',color=(.15,.15,.16))
upper_body=tidy(upper_body.cut(nacs.copy()),'nacs');ub_obj.Shape=upper_body
# Steering damper (dynamics-study.md CR-2): semi-active rotary damper on the top clamp, behind the axis.
add('Steering_damper_envelope',steer(box(-95,-30,227,80,60,45)),'RunningGear','Semi-active steering damper >=28 Nm.s/rad, speed-scheduled (dynamics-study.md)',color=(.75,.6,.2))
# Crash protection (compliance-and-validation.md CR-1..3), re-routed over and outside the radiator pods.
guards=[]
for side in [-1,1]:
    pts=[(930,251,792),(990,301,826),(1075,346,826),(1080,349,690),(1045,333,430),(900,277,330),(700,263,330),(600,251,360)]
    segs=[cyl((a[0],side*a[1],a[2]),(b[0],side*b[1],b[2]),14,11.5) for a,b in zip(pts,pts[1:])]+[Part.makeSphere(14,V(p[0],side*p[1],p[2])) for p in pts]
    g=Part.makeCompound(segs);guards.append(g)
    mounts=[((930,251,792),(930,186,764)),((1045,333,430),(1062,200,466)),((600,251,360),(600,190,364))]   # to upper rail, pack front lug, rear link
    add(sname('Crash_guard_mount',side),Part.makeCompound([cyl((a[0],side*a[1],a[2]),(b[0],side*b[1],b[2]),10,7.5) for a,b in mounts]),'Protection',
        'Guard mount stubs bolted to the upper rail, pack front lug and rear link through grommeted cover holes (holes not modelled)',color=(.08,.08,.085))
    add(sname('Crash_guard',side),g,'Protection','28x2.5 25CrMo4 crash guard, 21.3 kN anchors (compliance CR-1; routed outside the radiator pods)',color=(.08,.08,.085))
    add(sname('Pivot_slider',side),cyl((540,side*236,PZ),(540,side*270,PZ),25),'Protection','POM pivot slider puck on an M10 (compliance CR-3)',color=(.05,.05,.05))
    _,b1,b2=bar_pts(side);gd=b2-b1;gd.normalize();fw=V(gd.y,-gd.x,0)*side;fw.normalize();up=V(0,0,1)
    hp=[b2+gd*g_+fw*f_+up*u_ for g_,f_,u_ in [(127,0,0),(132,0,0),(175,10,0),(182,75,5),(120,112,8),(-20,115,5),(-110,60,-5),(-110,0,-14)]]
    hg=[Part.makeCylinder(11,(b-a).Length,a,b-a) for a,b in zip(hp,hp[1:])]+[Part.makeSphere(11,p) for p in hp[1:-1]]
    add(sname('Handguard',side),Part.makeCompound(hg),'Protection',
        'Aluminium handguard backbone 22x3 (compliance CR-2)',color=(.1,.1,.11))
# Legal fit-out (compliance CR-10..13).
add('Rear_reflector_red',box(-344,-30,578,6,60,22),'BodyStudy','60mm red rear reflector (FMVSS 108)',color=(.6,.05,.05))
for side in [-1,1]:
    add(sname('Side_reflector_red',side),cyl((-80,side*134,760),(-80,side*137,760),18),'BodyStudy','Red side reflector',color=(.6,.05,.05))
add('Horn_R28',cyl((1045,-224,525),(1045,-259,525),45),'Electronics','R28 class I horn below the left radiator pod, outboard of the battery plate (compliance CR-11)',color=(.12,.12,.12))
add('Side_stand_retracted',cyl((560,236,258),(330,240,230),12,0),'RunningGear','Side stand, retracted, with interlock switch (compliance CR-12)',color=(.08,.08,.085))

# ---------------------------------------------------------------- checks (model coordinates, ground at Z=-LIFT)
for o in D.Objects:
    if hasattr(o,'Shape') and o.TypeId=='Part::Feature':
        if not (o.Shape.isValid() and o.Shape.Volume>0):raise RuntimeError('Invalid shape '+o.Name)
# Every cell sits inside the inner case: its band's inner box holds the whole circle with CLR to spare by
# construction, and spot points on each cylinder are confirmed inside the fused inner solid.
cellcontain=all(inner.isInside(V(x+dx,ly+dy,z+dz),1e-6,True) for _,x,z,ly in cells
                for dx,dz in ((CELL_R,0),(-CELL_R,0),(0,CELL_R),(0,-CELL_R)) for dy in (-CELL_L/2+.01,CELL_L/2-.01))
assert cellcontain
visible=[o for o in D.Objects if o.TypeId=='Part::Feature' and o.InList and o.InList[0].Name!='Keepouts']
UNSPRUNG=('Front_','Rear_','Fork_','Swingarm','Shock_','Drive_belt')
SPRUNG_EXCEPT=('Front_indicator','Rear_indicator','Front_pulley')
sprung=[o for o in visible if not o.Name.startswith(UNSPRUNG) or o.Name.startswith(SPRUNG_EXCEPT)]
low=min(sprung,key=lambda o:o.Shape.BoundBox.ZMin)
layout=dict(static_ground_clearance_mm=round(low.Shape.BoundBox.ZMin+LIFT,1),lowest_sprung_part=low.Name,
            seat_height_static_mm=round(P['seat_top_rider_mm'][2]+LIFT,1),peg_height_mm=round(P['peg_reference_mm'][2]+LIFT,1),
            seat_to_peg_mm=P['seat_top_rider_mm'][2]-P['peg_reference_mm'][2],
            wheelbase_mm=round(FX,1),trail_mm=round(TRAIL,1),rake_deg=25,
            swingarm_mm=round(arm,1),swingarm_angle_static_deg=round(math.degrees(math.atan2(PZ-RZ,540)),1),
            shock_eye_to_eye_mm=round((upper-lower).Length,1))
eyes=[(upper-V(shock_lower(z)[0],0,shock_lower(z)[1])).Length for z in REAR_POS]
h1=RK.cog(['rider'])[2]
layout['rear_suspension']=dict(layout='central direct-mount coil-over, no linkage',pivot_above_ground_mm=PZ+LIFT,
    eye_droop_static_bump_mm=[round(eyes[0],1),round((upper-lower).Length,1),round(eyes[-1],1)],stroke_used_mm=round(eyes[0]-eyes[-1],1),
    leverage_mean=round(REAR_TRAVEL/(eyes[0]-eyes[-1]),2),wheel_travel_mm=REAR_TRAVEL,sag_mm=REAR_SAG,
    anti_squat_static_pct=round(RK.anti_squat(PZ,RZ,h1)[0]),
    anti_squat_range_pct=[round(min(RK.anti_squat(PZ,z,h1)[0] for z in REAR_POS)),round(max(RK.anti_squat(PZ,z,h1)[0] for z in REAR_POS))],
    cog_height_rider_on_mm=round(h1))
print(json.dumps(layout),flush=True)
print(json.dumps(P['pack_summary']),flush=True)
fast=bool(os.environ.get('BAVUSO_FAST'))
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
interferences=[]
if not fast:
    frame=Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith(('Upper_rail','Lower_','Tail_','Head_tube'))])
    check('pack_vs_motor_supplier',outer,ms,20)
    check('pack_vs_front_bump',outer,frontSweep.Shape,20)
    check('motor_vs_rear_bump',ms,rearSweep.Shape,20)
    check('pack_vs_pivot_stubs',outer,O('Pivot_reference'),20)
    check('pack_vs_swingarm',outer,Part.makeCompound([O('Swingarm_m1'),O('Swingarm_1')]),20)
    check('charger_vs_pack',charger,outer,10)
    check('charger_vs_front_bump',charger,frontSweep.Shape,20)
    check('frame_vs_front_bump',frame,frontSweep.Shape,20)
    check('frame_vs_rear_bump',frame,rearSweep.Shape,20)
    check('lower_clamp_vs_front_bump',O('Lower_triple_clamp'),frontSweep.Shape,25)
    check('bms_vs_body_top',bms,upper_body,8)
    check('lower_body_vs_pack',lower_body,outer,5)
    check('skid_vs_pack',skid,outer,10)
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
    check('undertray_vs_rear_bump',undertray,rearSweep.Shape,20)
    check('rear_indicators_vs_rear_bump',Part.makeCompound([O(sname('Rear_indicator_reserve',sd)) for sd in (-1,1)]),rearSweep.Shape,20)
    check('upper_body_vs_front_bump',upper_body,frontSweep.Shape,20)
    check('lower_body_vs_front_bump',lower_body,frontSweep.Shape,20)
    # Front tyre plus fender over the fork travel at steering lock. Lock is taken as 35 deg each way (stop not yet
    # designed) and combined with full bump, the worst case. The triple clamps turn with the fork, so they are not in it.
    fend=O('Front_fender_STUDY');steer_sweep=[]
    for i in (0,5,10,15,20):
        up=FRONT_TRAVEL*i/20;t_=Part.makeCompound([PLAIN_TYRE['Front'].copy(),fend.copy()])   # real 120/70 section: a cylinder's square shoulder overstates the steered-tyre pinch
        t_.translate(V(-math.sin(RAKE)*up,0,math.cos(RAKE)*up))
        for ang in (-35,-20,0,20,35):steer_sweep.append(t_.transformGeometry(A.Placement(V(),A.Rotation(sd,ang),sa).toMatrix()))
    steerSweep=Part.makeCompound(steer_sweep)
    check('crash_guards_vs_tyre_fender_lock_sweep',Part.makeCompound(guards),steerSweep,20)
    check('crash_guards_vs_lower_covers_and_pods',Part.makeCompound(guards),Part.makeCompound([lower_body]+pods),10)
    check('radiator_pods_vs_tyre_fender_lock_sweep',Part.makeCompound(pods+[O(sname('Radiator_core',sd)) for sd in (-1,1)]),steerSweep,20)
    check('horn_vs_tyre_fender_lock_sweep',O('Horn_R28'),steerSweep,20)
    check('front_body_vs_tyre_fender_lock_sweep',Part.makeCompound([upper_body,lower_body,headlamp,drl]+
          [O(sname(n,s)) for n in ('Front_indicator_reserve','Battery_side_panel','Belly_side_panel') for s in (-1,1)]),steerSweep,20)
    check('frame_vs_tyre_fender_lock_sweep',Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith(('Upper_rail','Lower_downlink','Head_tube'))]),steerSweep,20)
    # Bars at full lock (+-35 deg): hands, levers, master cylinder and switches vs the tank/fairing, screen and dash.
    # 30mm so a gloved hand is not pinched (Nov 11, bars raised 50 / back 20).
    barset=Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith(('Bar_','Hand_','Switch_cube','Lever_perch','Front_master','Front_brake_reservoir'))])
    barLock=Part.makeCompound([barset.transformGeometry(A.Placement(V(),A.Rotation(sd,a),sa).toMatrix()) for a in (-35,-20,20,35)])
    check('bars_at_lock_vs_tank_fairing_screen',barLock,Part.makeCompound([upper_body,O('Windscreen_STUDY')]),30)
    # The dash sits between the risers, where no hand goes: 15 mm rigid-to-rigid (screen on rubber mounts) is enough.
    dash=Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith('Display_')])
    check('dash_at_lock_vs_fairing_screen',Part.makeCompound([dash.transformGeometry(A.Placement(V(),A.Rotation(sd,a),sa).toMatrix()) for a in (-35,-20,20,35)]),
          Part.makeCompound([upper_body,O('Windscreen_STUDY')]),15)
    # Hoses and harness legs steer with the bars: they stay inside the 140mm steering keep-out the body is cut to.
    lines_=Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith(('Front_brake_hose_upper','Harness_bar','Harness_connector','Front_brake_splitter'))])
    lineLock=Part.makeCompound([lines_.transformGeometry(A.Placement(V(),A.Rotation(sd,a),sa).toMatrix()) for a in (-35,-20,0,20,35)])
    check('brake_hose_harness_at_lock_vs_body',lineLock,Part.makeCompound([upper_body,lower_body,O('Windscreen_STUDY'),headlamp]),8)
    check('lower_body_vs_motor',lower_body,ms,10)
    check('motor_cover_vs_motor',motor_cover,ms,10)
    check('motor_cover_vs_rear_bump',motor_cover,rearSweep.Shape,20)
    check('plate_vs_rear_bump',O('Licence_plate_US'),rearSweep.Shape,20)
    check('plate_arm_vs_rear_bump',O('Plate_hanger_arm'),rearSweep.Shape,20)
    check('cross_brace_vs_rear_bump',O('Swingarm_cross_brace'),rearSweep.Shape,20)
    # Central shock through the real travel (droop to the end of the stroke). Frame-fixed parts are checked
    # against the swept envelope; the tyre and the swingarm move with the lower eye, so they are paired by position.
    shockSweep=Part.makeCompound([shock_env(shock_lower(z)) for z in REAR_POS])
    add('Shock_sweep_keepout',shockSweep,'Keepouts','Spring/body envelope at 9 positions, droop to end of stroke',hide=True)
    # Shock vs motor is measured directly: the EMRAX housing solid has inward-facing faces and OCC reports
    # 0mm (with zero overlap) for points nowhere near the shock. The envelope is a 45mm cylinder about a known
    # axis, so the gap is the distance from every motor mesh vertex and triangle centre to that axis, less 45.
    mv,mt=ms.tessellate(0.3)
    mpts=list(mv)+[(mv[a]+mv[b]+mv[c])*(1/3) for a,b,c in mt]
    def seg_gap(p,a,b):
        ab=b-a;t=max(0.0,min(1.0,(p-a).dot(ab)/ab.dot(ab)));return (p-(a+ab*t)).Length
    g=1e9
    for z in REAR_POS:
        lo=V(shock_lower(z)[0],0,shock_lower(z)[1]);ax_=lo-upper;ax_.normalize()
        a_,b_=upper+ax_*30,lo-ax_*30
        g=min(g,min(seg_gap(q,a_,b_) for q in mpts)-45)
    checks.append(dict(check='shock_vs_motor',gap_mm=round(g,2),overlap_mm3=0.0,required_mm=15,passed=g>=15,
                       method='mesh points (0.3mm) to envelope axis; OCC solid distance unreliable on this STEP'))
    print(json.dumps(checks[-1]),flush=True)
    check('shock_vs_pack',shockSweep,outer,15)
    check('shock_vs_cabinet',shockSweep,cab_out,10)
    check('shock_vs_charger',shockSweep,charger,10)
    check('shock_vs_seat',shockSweep,seat,10)
    check('shock_vs_frame',shockSweep,Part.makeCompound([O(o.Name) for o in visible if o.Name.startswith(('Upper_rail','Lower_','Tail_rail','Tail_brace'))]),10)
    check('shock_vs_reservoir',shockSweep,O('Shock_reservoir_STUDY'),10)
    tyre_at=lambda z:cyl((rear_axle(z)[0],-95,z),(rear_axle(z)[0],95,z),RR)
    armset=Part.makeCompound([O('Swingarm_m1'),O('Swingarm_1')])
    def paired(label,minimum,other):
        best=None
        for z in REAR_POS:
            d=shock_env(shock_lower(z)).distToShape(other(z))[0]
            best=d if best is None else min(best,d)
        checks.append(dict(check=label,gap_mm=round(best,2),overlap_mm3=0.0,required_mm=minimum,passed=best>=minimum-1e-5))
        print(json.dumps(checks[-1]),flush=True)
    paired('shock_vs_rear_tyre_same_position',20,tyre_at)
    paired('shock_vs_swingarm_arms_same_position',10,lambda z:armset.transformGeometry(arm_rot(z).toMatrix()))
    check('shock_tower_vs_rear_tyre',O('Swingarm_shock_tower'),tyre_at(RZ),20)
    # Arm-mounted parts rotate about the pivot, which is the motor axis: sweep them and check the frame side.
    armparts=Part.makeCompound([armset,O('Swingarm_cross_brace'),O('Swingarm_shock_tower')])
    armSweep=Part.makeCompound([armparts.transformGeometry(arm_rot(z).toMatrix()) for z in (REAR_POS[0],RZ,REAR_POS[-1])])
    check('swingarm_sweep_vs_motor',armSweep,ms,10)
    check('swingarm_sweep_vs_pack',armSweep,outer,20)
    check('swingarm_sweep_vs_pegs',armSweep,Part.makeCompound([O(sname('Peg_reference',sd)) for sd in (-1,1)]),5)
    check('swingarm_sweep_vs_motor_cover',armSweep,motor_cover,10)
    check('swingarm_sweep_vs_cabinet',armSweep,cab_out,10)
    check('cabinet_vs_rear_bump',cab_out,rearSweep.Shape,20)
    check('cabinet_vs_motor_cover',cab_out,motor_cover,5)
    check('cabinet_vs_skid',cab_out,skid,10)
    for side in [-1,1]:
        check(sname('radiator_vs_charger',side),O(sname('Radiator_core',side)),charger,5)
    # Broad interference sweep: every body/electronics part against every other visible part.
    # Cells are covered by the containment test; the solid pack boundary stands in for them here.
    sweep=[(o.Name,o.InList[0].Name,o.Shape) for o in visible if not o.Name.startswith('Cell_lane')]
    sweep.append(('Battery_installation_keepout','Energy',outer))
    for (na,ga,sa_),(nb,gb,sb_) in itertools.combinations(sweep,2):
        if not ({ga,gb}&{'BodyStudy','Electronics','Energy','Cooling','Protection'}):continue
        if {na,nb}=={'Battery_installation_keepout','Pack_case_structural_4mm_STUDY'}:continue
        if not sa_.BoundBox.intersect(sb_.BoundBox):continue
        if 'Mirror_stalk' in na+nb and any(k in na+nb for k in ('Mirror_body','Hand_grip','Bar_half')):continue  # intended joints
        if 'Mirror_glass' in na+nb and 'Mirror_body' in na+nb:continue
        if 'Seat_welt' in na+nb and 'Seat_two_level' in na+nb:continue
        if 'Crash_guard_mount' in na+nb and any(k in na+nb for k in ('Crash_guard_','Upper_rail','Lower_pack_rear_link','Lower_downlink','Upper_body','Lower_body',
                                                                       'Battery_side_panel','Motor_side_covers','Battery_installation_keepout','Pack_case')):continue  # bolted mounts through grommets
        if 'Handguard' in na+nb and 'Bar_half' in na+nb:continue   # clamped to the bar
        if sa_.distToShape(sb_)[0]>1e-6:continue
        # Whole-assembly booleans on the multi-solid supplier STEPs gave false volumes; sum solid by solid.
        v=sum(x.common(y).Volume for x in sa_.Solids for y in sb_.Solids if x.BoundBox.intersect(y.BoundBox))
        if v>1.0:interferences.append(dict(a=na,b=nb,overlap_mm3=round(v,1)));print('OVERLAP',na,nb,round(v),flush=True)

# ---------------------------------------------------------------- lift to the ground origin, save, export
for o in D.Objects:
    if o.TypeId=='Part::Feature':o.Placement=A.Placement(V(0,0,LIFT),A.Rotation()).multiply(o.Placement)
D.recompute()
native=R/f'cad/Bavuso-V1.0-adventure{SUFFIX}.FCStd';D.saveAs(str(native))
print('saved',native,flush=True)
if fast:os._exit(0)   # styling iteration: native model only, no STEP or checks
Part.export(visible,str(R/f'cad/Bavuso-V1.0-adventure{SUFFIX}.step'))
audit=dict(release_state='ENGINEERING DEVELOPMENT; no build authorization',parameters=P,layout=layout,
 actual_supplier_geometry=(['EMRAX 228 MV LC 2025 STEP'] if DRIVE=='emrax228' else [])+['Cascadia CM200 STEP (inverter envelope)','Orion BMS2 108-cell STEP'],
 drawing_outline_only=['Sensata GX14 main contactors'],
 spec_envelopes=[] if DRIVE=='emrax228' else ['IPM motor + 2-stage gear case (drive-study.md)'],
 solid_objects=len(visible),total_solids=sum(r['solids'] for r in records),
 cell_count=len(cells),all_cell_points_inside_inner_case=cellcontain,
 critical_pair_checks=checks,checks_passed=sum(c['passed'] for c in checks),checks_total=len(checks),
 interferences=interferences,
 exclusions=['steering lock beyond cylinder envelope','tire growth','real fork/yoke/hub CAD','busbars and cooling',
             'wiring','hoses','mounts, lugs and fasteners','structure','shock supplier CAD (envelope per rear-suspension.md)','CFD of this shape',
             'rider fit buck','test validation'])
for file,rows_ in [(f'cell-placement-adventure{SUFFIX}.csv',cellmap),(f'component-status-adventure{SUFFIX}.csv',records)]:
    with (R/file).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows_[0]));w.writeheader();w.writerows(rows_)
(R/f'geometry-adventure{SUFFIX}-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k not in ['parameters']},indent=2),flush=True)
