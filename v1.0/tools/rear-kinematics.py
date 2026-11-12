"""Rear suspension kinematics for the adventure layout (plain Python, no FreeCAD).

What it answers:
  1. Anti-squat through the travel, from the belt's tension line (Foale's method). The EMRAX sits on the
     swingarm pivot, so the pivot height is the main lever on anti-squat.
  2. A pivot-height sweep: anti-squat vs how low the motor then hangs.
  3. A shock mount sweep for one central direct-mount shock: leverage ratio, progression, stroke, length,
     and clearance to the motor's real outline and to the rear tyre through the travel.
  4. Spring rate and preload range for 1-up and 2-up loaded, from assumed masses.

Coordinates are build-adventure.py model coordinates (X forward from the rear axle, Z up, ground at Z=-LIFT).
Run:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/rear-kinematics.py [pivot_z]
"""
import json,math,sys
from pathlib import Path

R=Path(__file__).resolve().parents[1]
LIFT=40.0;RR=311.9;RZ=RR-LIFT;PX=540.0;WB=1486.8;G=-LIFT
TRAVEL=170.0;SAG=0.30*TRAVEL                 # rider-on static is the model position; 30% sag is the ADV norm
RATIO=3.1;PITCH=14.0
RF_P=20*PITCH/(2*math.pi);RR_P=62*PITCH/(2*math.pi)    # pulley pitch radii, 20:62 14mm belt
MOTOR_R_DOWN=114.0+10                        # EMRAX housing below the axis (STEP) + 10mm guard

# ---- masses (assumptions, stated in the report) ----
# Bike mass and CoG from the CAD roll-up (tools/mass-rollup.py) when it exists; else the optimiser estimate.
_mr=R/'mass-rollup.json'
if _mr.exists():
    _m=json.loads(_mr.read_text())
    M_BIKE=_m['total_kg'];X_BIKE=float(_m['cog_mm']['x_from_rear_axle']);Z_BIKE=float(_m['cog_mm']['height'])
    M_UNSPRUNG_REAR=_m['unsprung_kg']['rear']
else:
    M_BIKE,X_BIKE,Z_BIKE,M_UNSPRUNG_REAR=222.5,786.0,473.0,22.0     # optimiser 490 lb and a hand split
RIDERS=dict(rider=(85.0,520.0,1090.0),passenger=(85.0,150.0,1150.0),luggage=(30.0,-100.0,750.0))
F_TARGET=1.75                                # rider-on rear natural frequency, Hz (ADV range 1.6-1.9)

def cog(loads):
    m=M_BIKE+sum(RIDERS[k][0] for k in loads)
    x=(M_BIKE*X_BIKE+sum(RIDERS[k][0]*RIDERS[k][1] for k in loads))/m
    z=(M_BIKE*Z_BIKE+sum(RIDERS[k][0]*RIDERS[k][2] for k in loads))/m
    return m,x,z
def rear_sprung_n(loads):
    m,x,_=cog(loads);return (m*(1-x/WB)-M_UNSPRUNG_REAR)*9.81

def axle(pz,zw):
    """Axle (x,z) when the axle is at height zw, swingarm pivot at (PX,pz), arm length set by the static axle."""
    L=math.hypot(PX,pz-RZ);return PX-math.sqrt(L*L-(zw-pz)**2),zw

def anti_squat(pz,zw,h):
    """Foale: line from the contact patch through C (tension line x swingarm line) vs the h/WB line, in %."""
    ax,az=axle(pz,zw);c1=(PX,pz);c2=(ax,az)
    ux,uz=c2[0]-c1[0],c2[1]-c1[1];D=math.hypot(ux,uz);ux,uz=ux/D,uz/D
    wx,wz=-uz,ux
    if wz<0:wx,wz=-wx,-wz                    # normal pointing up: the top run is the tension side
    a=(RF_P-RR_P)/D;b=math.sqrt(1-a*a)
    nx,nz=a*ux+b*wx,a*uz+b*wz
    t=RF_P/a                                 # along the swingarm line from the pivot (negative = ahead of it)
    cx,cz=c1[0]+t*ux,c1[1]+t*uz
    tan_a=(cz-G)/(cx-ax);tan_b=h/WB
    return 100*tan_a/tan_b,(cx,cz)

def wheel_positions(n=35):
    return [RZ-SAG+(TRAVEL)*i/(n-1) for i in range(n)]

def pivot_sweep(h):
    rows=[]
    for pz in range(470,319,-10):
        st=anti_squat(pz,RZ,h)[0]
        rng=[anti_squat(pz,z,h)[0] for z in wheel_positions()]
        rows.append(dict(pivot_z_model=pz,pivot_above_ground=pz-G,swingarm_angle_static_deg=round(math.degrees(math.atan2(pz-RZ,PX)),1),
                         swingarm_mm=round(math.hypot(PX,pz-RZ),1),anti_squat_static_pct=round(st),
                         anti_squat_range_pct=[round(min(rng)),round(max(rng))],
                         motor_housing_bottom_above_ground=round(pz-MOTOR_R_DOWN-G)))
    return rows

# ---- shock: one central coil-over (plane y=0), lower eye on a hump above the swingarm cross member ----
# Direct mount, no linkage (KTM PDS layout). The spring/body is a 45mm-radius cylinder from 30mm past each eye.
# EMRAX 228 STEP, max radius per 15deg sector (0=forward, 90=up): 114 housing, 158.5 at the square plate corners
MOTOR_PROFILE=[114,114,158.5,158.5,114,114,114,114,158.5,158.5,114,114,114,114,158.5,158.5,114,114,114,114,158.5,158.5,114,114]
SHOCK_R=45.0
# Pack outer rear face (model Z ranges -> X), from the build's band list at this pivot height.
PACK_REAR=[(198.0,489.0,675.0),(489.0,573.5,560.0)]
def pack_gap(q):
    return min((xlo-q[0] if zlo-SHOCK_R<=q[1]<=zhi+SHOCK_R else 1e9) for zlo,zhi,xlo in PACK_REAR)-SHOCK_R
def motor_r(ang):
    return MOTOR_PROFILE[int((math.degrees(ang)%360)//15)%24] if MOTOR_PROFILE else 155.5
def seg_point_gap(p,a,b,r_seg):
    ax,az=a;bx,bz=b;px,pz=p;dx,dz=bx-ax,bz-az;L2=dx*dx+dz*dz
    t=max(0.0,min(1.0,((px-ax)*dx+(pz-az)*dz)/L2))
    return math.hypot(px-ax-t*dx,pz-az-t*dz)-r_seg,(ax+t*dx,az+t*dz)
def central_clearances(pz,s,hoff,up):
    """Smallest gaps over the travel: spring cylinder to the motor's real outline, the rear tyre and the pack."""
    g_m=g_t=g_p=1e9
    for z in wheel_positions(18):
        lo=lower_eye(pz,z,s,hoff);d=(up[0]-lo[0],up[1]-lo[1]);n=math.hypot(*d)
        a=(lo[0]+d[0]/n*30,lo[1]+d[1]/n*30);b=(up[0]-d[0]/n*30,up[1]-d[1]/n*30)
        # motor: sample the segment, compare distance to axis with the outline radius in that direction
        for k in range(21):
            q=(a[0]+(b[0]-a[0])*k/20,a[1]+(b[1]-a[1])*k/20)
            ang=math.atan2(q[1]-pz,q[0]-PX);g_m=min(g_m,math.hypot(q[0]-PX,q[1]-pz)-motor_r(ang)-SHOCK_R)
            g_p=min(g_p,pack_gap(q))
        ax_=axle(pz,z);g_t=min(g_t,seg_point_gap(ax_,a,b,SHOCK_R)[0]-RR)
    return g_m,g_t,g_p
def lower_eye(pz,zw,s,hoff):
    """Lower eye at distance s from the pivot along the arm, hoff above its centreline, for wheel height zw."""
    ax,az=axle(pz,zw);ux,uz=(ax-PX),(az-pz);D=math.hypot(ux,uz);ux,uz=ux/D,uz/D
    nx,nz=-uz,ux
    if nz<0:nx,nz=-nx,-nz
    return PX+s*ux+hoff*nx,pz+s*uz+hoff*nz
def shock_curve(pz,s,hoff,up):
    zs=wheel_positions();ls=[math.hypot(*(a-b for a,b in zip(lower_eye(pz,z,s,hoff),up))) for z in zs]
    lr=[(zs[i+1]-zs[i-1])/(ls[i-1]-ls[i+1]) for i in range(1,len(zs)-1)]
    return zs,ls,lr
def dead_length(stroke):return 2*stroke+125   # eyes, seal head, piston, bump stop: typical piggyback coil-over

def shock_sweep(pz):
    best=[]
    for s in range(150,261,10):
        for hoff in (60,80,100,120):
            for ux in range(400,521,10):
                for uz in range(660,706,5):             # top eye hangs from a cross tube between the tail rails (Z~727)
                    zs,ls,lr=shock_curve(pz,s,hoff,(ux,uz))
                    if min(lr)<=0:continue
                    stroke=ls[0]-ls[-1];l_ext=ls[0]
                    lr_sag=lr[len(lr)*30//100];prog=lr[0]/lr[-1]-1
                    if not(55<=stroke<=85 and l_ext>=dead_length(stroke) and 0.03<=prog<=0.35 and 1.9<=lr_sag<=3.2):continue
                    lx,lz=lower_eye(pz,RZ,s,hoff);ang=math.degrees(math.atan2(uz-lz,ux-lx))
                    if not 35<=ang<=100:continue          # upright enough that most of the force is useful
                    g_m,g_t,g_p=central_clearances(pz,s,hoff,(ux,uz))
                    if g_m<15 or g_t<20 or g_p<15:continue
                    score=abs(prog-0.15)*4+abs(lr_sag-2.5)+abs(l_ext-dead_length(stroke))/100+hoff/400-min(g_m-15,g_t-20,g_p-15)/25   # favour the tightest margin
                    best.append((score,dict(lower_s=s,lower_hoff=hoff,upper=[ux,uz],stroke=round(stroke,1),eye_ext=round(l_ext,1),
                                            eye_static=round(ls[len(ls)*30//100],1),eye_bump=round(ls[-1],1),
                                            lr_ext=round(lr[0],2),lr_sag=round(lr_sag,2),lr_bump=round(lr[-1],2),
                                            progression_pct=round(100*prog),shock_angle_deg=round(ang),
                                            gap_spring_to_motor=round(g_m,1),gap_spring_to_tyre=round(g_t,1),gap_spring_to_pack=round(g_p,1),
                                            lower_eye_static=[round(lx,1),round(lz,1)])))
    best.sort(key=lambda t:t[0])
    return [b for _,b in best[:8]]

def springs(pz,sh):
    zs,ls,lr=shock_curve(pz,sh['lower_s'],sh['lower_hoff'],sh['upper'])
    i_sag=len(lr)*30//100;lr_s=lr[i_sag]
    f1=rear_sprung_n(['rider']);f2=rear_sprung_n(['rider','passenger','luggage'])
    m1=f1/9.81;kw=(2*math.pi*F_TARGET)**2*m1/1000         # wheel rate N/mm at sag
    ks=kw*lr_s**2                                          # spring rate at the shock
    # Spring force at the shock = wheel force x leverage (virtual work). Preload so that sag = SAG 1-up.
    sag_stroke=ls[0]-ls[i_sag+1]
    pre1=f1*lr_s/ks-sag_stroke
    pre2=f2*lr_s/ks-sag_stroke
    # Wheel force to reach full bump with 1-up preload (spring only, no bump rubber): integrate along travel.
    F=0.0;fs=[]
    for i in range(len(ls)):
        comp=ls[0]-ls[i]+pre1
        lr_i=lr[min(max(i-1,0),len(lr)-1)];fs.append(ks*comp/lr_i)
    return dict(sprung_rear_load_1up_N=round(f1),sprung_rear_load_2up_loaded_N=round(f2),
                wheel_rate_at_sag_N_per_mm=round(kw,1),spring_rate_N_per_mm=round(ks),spring_rate_kgf_per_mm=round(ks/9.81,1),
                preload_1up_mm=round(pre1,1),preload_2up_loaded_mm=round(pre2,1),preload_range_needed_mm=round(pre2-pre1,1),
                freq_1up_Hz=F_TARGET,freq_2up_loaded_Hz=round(math.sqrt(kw*1000/(f2/9.81))/(2*math.pi),2),
                wheel_force_at_full_bump_1up_N=round(fs[-1]),bump_force_ratio_1up=round(fs[-1]/f1,2),
                shock_static_force_1up_N=round(f1*lr_s),shock_static_force_2up_N=round(f2*lr_s))

if __name__=='__main__':
    m,x,h=cog(['rider']);m2,x2,h2=cog(['rider','passenger','luggage'])
    pz=float(sys.argv[1]) if len(sys.argv)>1 else 350.0   # the built pivot (BAVUSO_PIVOT_Z)
    out=dict(prepared='2026-11-03 US Central, Claude Opus 5.5',
             assumptions=dict(bike_kg=M_BIKE,bike_cog_x_mm=X_BIKE,bike_cog_h_mm=Z_BIKE,riders=RIDERS,unsprung_rear_kg=M_UNSPRUNG_REAR,
                              travel_mm=TRAVEL,sag_mm=SAG,belt='20:62 14mm',target_freq_Hz=F_TARGET),
             cog_1up=dict(mass_kg=round(m,1),x_mm=round(x),h_mm=round(h),rear_share_pct=round(100*(1-x/WB),1)),
             cog_2up_loaded=dict(mass_kg=round(m2,1),x_mm=round(x2),h_mm=round(h2),rear_share_pct=round(100*(1-x2/WB),1)),
             anti_squat_sensitivity_to_cog_h=[dict(h_mm=hh,static_pct=round(anti_squat(pz,RZ,hh)[0])) for hh in (600,650,700,750)],
             pivot_sweep=pivot_sweep(h))
    sh=shock_sweep(pz)
    out['pivot_z_used']=pz;out['shock_candidates']=sh
    if sh:
        spr=springs(pz,sh[0]);out['spring']=spr
        zs,ls,lr=shock_curve(pz,sh[0]['lower_s'],sh[0]['lower_hoff'],sh[0]['upper'])
        out['curve']=[dict(wheel_mm=round(z-(RZ-SAG)),eye_mm=round(l,1),lr=round(lr[min(max(i-1,0),len(lr)-1)],3),
                           anti_squat_pct=round(anti_squat(pz,z,h)[0])) for i,(z,l) in enumerate(zip(zs,ls))][::2]
    print(json.dumps(out,indent=1))
    (R/f'rear-kinematics-{int(pz)}.json').write_text(json.dumps(out,indent=1))
