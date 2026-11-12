"""Rider comfort study for the V1.0 adventure layout (seat / peg / grip triangle).
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/comfort-study.py
Writes comfort-study.json and prints the tables used in comfort-study.md.

Rider model: rigid links scaled from stature with the standard segment-length fractions (Drillis & Contini as
tabulated by Winter, Biomechanics and Motor Control of Human Movement): trunk hip->shoulder 0.288H, thigh 0.245H,
shank 0.246H, upper arm 0.186H, forearm + half hand (elbow -> grip centre) 0.200H, ankle height 0.039H,
ball of foot 0.073H ahead of the ankle (boot adds 25 mm under the sole, 15 mm to the toe), hip-joint half-width
0.051H, shoulder half-width 0.130H. Three riders: 5th-percentile female (1,520 mm), 50th male (1,755), 95th male (1,880).
The hip joint sits 90 mm above the compressed seat surface (25 mm foam compression), on the seat's lowest point.
The rider leans the trunk forward only as far as needed to keep the elbows from locking straight; otherwise sits
upright (the design-notes intent: near upright, shoulders relaxed, elbows softly bent).
All positions are above ground (model coordinates + 40 mm lift), X forward from the rear axle, Y left.
"""
import json, math, itertools
from pathlib import Path
R=Path(__file__).resolve().parents[1]

RIDERS={'5th female':1520,'50th male':1755,'95th male':1880}
# Current CAD (build-adventure.py P[...], lifted 40 mm): seat lowest point, grip centre, peg (foot on the rubber).
SEAT=(486,840);GRIP=(922,351,1079);PEG=(500,262,420);PEG_END_Y=305;FOAM_NOW=55
# Working comfort targets. Exact tables from the riding-posture literature were not retrievable (login-gated);
# these are the usual touring/upright ranges, interior angles (180 = straight).
TARGET=dict(knee=(80,115),hip=(90,140),elbow=(95,150),trunk_fwd=(0,15),foam_mm=(70,100))

def law(a,b,c):
    """interior angle opposite side c, triangle with sides a,b,c"""
    return math.degrees(math.acos(max(-1,min(1,(a*a+b*b-c*c)/(2*a*b)))))
def posture(H,seat,grip,peg):
    hip=(seat[0],0.051*H,seat[1]-25+90)
    sh_len=.288*H;ua,fa=.186*H,.200*H
    # ankle from the ball of the foot on the peg
    ank=(peg[0]-.073*H-15,peg[1],peg[2]+12+25+.039*H)
    th,sk=.245*H,.246*H
    d=math.dist(hip,ank)
    knee=law(th,sk,min(d,th+sk-1))
    # knee point: in the plane of hip, ankle and +X, bent forward
    hx,hy,hz=hip;ax,ay,az=ank
    u=[(a-b)/d for a,b in zip(ank,hip)]
    alpha=math.radians(law(th,d,sk))           # angle at hip between hip->ankle and thigh
    f=[1,0,0];dot=sum(a*b for a,b in zip(f,u));w=[a-dot*b for a,b in zip(f,u)];wn=math.sqrt(sum(a*a for a in w));w=[a/wn for a in w]
    kp=[hip[i]+th*(math.cos(alpha)*u[i]+math.sin(alpha)*w[i]) for i in range(3)]
    best=None
    for lean10 in range(0,401):              # trunk lean from vertical, 0.1 deg steps
        t=math.radians(lean10/10)
        sh=(hx+sh_len*math.sin(t),.130*H,hz+sh_len*math.cos(t))
        dg=math.dist(sh,grip)
        if dg<=ua+fa-.02*H:                    # arms not locked straight (elbow interior <= ~165 deg)
            best=(lean10/10,sh,dg);break
    if best is None:best=(40.0,sh,dg)
    lean,sh,dg=best
    elbow=law(ua,fa,min(dg,ua+fa-1))
    trunk=[s-h for s,h in zip(sh,hip)];thigh=[k-h for k,h in zip(kp,hip)]
    hipang=math.degrees(math.acos(sum(a*b for a,b in zip(trunk,thigh))/(math.dist(sh,hip)*th)))
    return dict(knee=round(knee,1),hip=round(hipang,1),elbow=round(elbow,1),trunk_fwd=round(lean,1),
                knee_point=[round(v) for v in kp],grip_from_shoulder_mm=round(dg))

def score(p):
    """degrees outside the target band, summed over joints"""
    s=0
    for k in ('knee','hip','elbow','trunk_fwd'):
        lo,hi=TARGET[k];s+=max(0,lo-p[k],p[k]-hi)
    return s

out=dict(current={},sweep=[])
print('CURRENT CAD (seat 840 at X486, peg Z420 at X500, grip Z1085 at X880, foam ~55 mm)')
for n,H in RIDERS.items():
    p=posture(H,SEAT,GRIP,PEG);out['current'][n]=p;print(f'  {n:11s}',p,'outside-band deg',round(score(p),1))
# Sweep: peg drop / peg rearward, seat height change, grip up/back. Constraints:
#  - peg lean clearance >= 45 deg (peg end touches the ground at atan(z/y)); ADV class is ~45-50
#  - standing: grip to peg horizontal 280-470 mm (bars reachable standing without hunching)
#  - seat height <= 850 (the R1300GS figure; ground reach for short riders)
#  - peg must stay ahead of X400 (swingarm/belt/heel) and is moved together with its hanger
rows=[]
for dz,dx,ds,gz,gx in itertools.product(range(0,81,10),range(-160,121,20),range(-10,11,5),range(0,61,20),range(-60,21,20)):
    peg=(PEG[0]-dx,PEG[1],PEG[2]-dz);seat=(SEAT[0],SEAT[1]+ds);grip=(GRIP[0]+gx,GRIP[1],GRIP[2]+gz)
    lean_clear=math.degrees(math.atan2(peg[2],PEG_END_Y))
    stand=grip[0]-peg[0]
    if lean_clear<45 or not(280<=stand<=470) or seat[1]>850 or peg[0]<400:continue
    ps={n:posture(H,seat,grip,peg) for n,H in RIDERS.items()}
    tot=sum(score(p) for p in ps.values())+0.02*(dz+abs(dx)+abs(ds)+gz+abs(gx))   # tie-break: smallest change
    rows.append(dict(peg_drop=dz,peg_back=dx,seat_change=ds,grip_up=gz,grip_fwd=gx,lean_clearance_deg=round(lean_clear,1),
                     stand_reach_mm=stand,score=round(tot,2),postures=ps))
rows.sort(key=lambda r:r['score'])
out['sweep']=rows[:25];out['targets']=TARGET
print('\nBEST 8 of',len(rows),'feasible points')
for r in rows[:8]:
    print({k:v for k,v in r.items() if k!='postures'})
    for n,p in r['postures'].items():print('     ',f'{n:11s}',{k:p[k] for k in ('knee','hip','elbow','trunk_fwd')})
# Single-lever comparison: how much each change alone buys for the 50th male.
print('\nSINGLE LEVERS, 50th male knee / hip')
for lab,peg,seat in [('peg -40 mm',(500,262,380),SEAT),('peg -60 mm',(500,262,360),SEAT),('peg 60 back',(440,262,420),SEAT),
                     ('seat +10',PEG,(486,850)),('peg -60, 60 back',(440,262,360),SEAT)]:
    p=posture(1755,seat,GRIP,peg);print(f'  {lab:18s} knee {p["knee"]:6.1f}  hip {p["hip"]:6.1f}')
(R/'comfort-study.json').write_text(json.dumps(out,indent=1))

# Recommended point (applied to build-adventure.py on Nov 11): pegs 80 down and 80 back, seat +10, bars unchanged.
REC_PEG=(PEG[0]-80,PEG[1],PEG[2]-80);REC_SEAT=(SEAT[0],SEAT[1]+10)
out['recommended']=dict(peg=REC_PEG,seat=REC_SEAT,grip=GRIP,lean_clearance_deg=round(math.degrees(math.atan2(REC_PEG[2],PEG_END_Y)),1),
                        stand_reach_mm=GRIP[0]-REC_PEG[0],postures={n:posture(H,REC_SEAT,GRIP,REC_PEG) for n,H in RIDERS.items()})
out['current_lean_clearance_deg']=round(math.degrees(math.atan2(PEG[2],PEG_END_Y)),1)
print('\nRECOMMENDED',{k:v for k,v in out['recommended'].items() if k!='postures'})
for n in RIDERS:
    a,b=out['current'][n],out['recommended']['postures'][n]
    print(f'  {n:11s} knee {a["knee"]:5.1f} -> {b["knee"]:5.1f}   hip {a["hip"]:5.1f} -> {b["hip"]:5.1f}   elbow {a["elbow"]:5.1f} -> {b["elbow"]:5.1f}   trunk {b["trunk_fwd"]}')
# Wind: flow leaves the screen top rising ~20 deg; where is it at the rider's eye station?
SCREEN_TOP=(1128,1222+40)
for n,H in RIDERS.items():
    hip_z=REC_SEAT[1]-25+90;eye=(REC_SEAT[0]+60,hip_z+.406*H)       # seated eye ~0.406H above the hip joint
    flow=SCREEN_TOP[1]+math.tan(math.radians(20))*(SCREEN_TOP[0]-eye[0])
    print(f'  wind {n:11s} eye Z{eye[1]:.0f}, deflected flow edge Z{flow:.0f} -> helmet {"in clean air" if flow>eye[1]+80 else "in the turbulent edge" if flow>eye[1]-80 else "in direct flow (chest sheltered)"}')
(R/'comfort-study.json').write_text(json.dumps(out,indent=1))
