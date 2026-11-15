"""Comfort study v2 (Nov 14, 2026): lower seat, rider pocket moved forward, bars re-placed.
Same rider model as tools/comfort-study.py (posture() copied unchanged), current CAD numbers (LIFT 53.1).
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/comfort-study-v2.py  -> comfort-study-v2.json
"""
import json, math, itertools
from pathlib import Path
R=Path(__file__).resolve().parents[1]
LIFT=53.1
RIDERS={'5th female':1520,'50th male':1755,'95th male':1880}
SEAT=(486,810+LIFT);GRIP=(901,352,1088+LIFT);PEG=(420,275,300+LIFT);PEG_END_Y=311
TARGET=dict(knee=(80,115),hip=(90,140),elbow=(95,150),trunk_fwd=(0,15))
def law(a,b,c):return math.degrees(math.acos(max(-1,min(1,(a*a+b*b-c*c)/(2*a*b)))))
def posture(H,seat,grip,peg):
    hip=(seat[0],0.051*H,seat[1]-25+90);sh_len=.288*H;ua,fa=.186*H,.200*H
    ank=(peg[0]-.073*H-15,peg[1],peg[2]+12+25+.039*H);th,sk=.245*H,.246*H
    d=math.dist(hip,ank);knee=law(th,sk,min(d,th+sk-1))
    u=[(a-b)/d for a,b in zip(ank,hip)];alpha=math.radians(law(th,d,sk))
    f=[1,0,0];dot=sum(a*b for a,b in zip(f,u));w=[a-dot*b for a,b in zip(f,u)];wn=math.sqrt(sum(a*a for a in w));w=[a/wn for a in w]
    kp=[hip[i]+th*(math.cos(alpha)*u[i]+math.sin(alpha)*w[i]) for i in range(3)]
    hx,hy,hz=hip;best=None
    for lean10 in range(0,401):
        t=math.radians(lean10/10);sh=(hx+sh_len*math.sin(t),.130*H,hz+sh_len*math.cos(t));dg=math.dist(sh,grip)
        if dg<=ua+fa-.02*H:best=(lean10/10,sh,dg);break
    if best is None:best=(40.0,sh,dg)
    lean,sh,dg=best;elbow=law(ua,fa,min(dg,ua+fa-1))
    trunk=[s-h for s,h in zip(sh,hip)];thigh=[k-h for k,h in zip(kp,hip)]
    hipang=math.degrees(math.acos(sum(a*b for a,b in zip(trunk,thigh))/(math.dist(sh,hip)*th)))
    return dict(knee=round(knee,1),hip=round(hipang,1),elbow=round(elbow,1),trunk_fwd=round(lean,1),knee_point=[round(v) for v in kp])
def score(p):return sum(max(0,TARGET[k][0]-p[k],p[k]-TARGET[k][1]) for k in TARGET)
def ground_reach(H,seat_z,half_w):
    """inseam (0.47H, boots +30) minus the path over the seat edge to the ground beside the bike, straight leg. >0 = flat foot margin"""
    return .47*H+30-math.hypot(seat_z-0,max(0,half_w+60-.051*H))
out=dict(current={n:posture(H,SEAT,GRIP,PEG) for n,H in RIDERS.items()})
rows=[]
for ds,sx,pz,px,gz,gx in itertools.product(range(-50,1,10),range(0,81,20),range(0,31,10),range(-40,21,20),range(-40,21,20),range(-80,21,20)):
    seat=(SEAT[0]+sx,SEAT[1]+ds);peg=(PEG[0]-px,PEG[1],PEG[2]-pz);grip=(GRIP[0]+gx,GRIP[1],GRIP[2]+gz)
    lean=math.degrees(math.atan2(peg[2],PEG_END_Y));stand=grip[0]-peg[0]
    if lean<45 or not(280<=stand<=470) or peg[0]<400:continue
    ps={n:posture(H,seat,grip,peg) for n,H in RIDERS.items()}
    s=sum(score(p) for p in ps.values())
    # prefer: low seat (5th female ground reach, narrow nose 130 half-width), trunk ~5-10 deg (relaxed ADV, not bolt upright)
    reach5=ground_reach(1520,seat[1],130)
    s+=0.15*max(0,-reach5)+0.3*sum(max(0,5-p['trunk_fwd'])+max(0,p['trunk_fwd']-12) for p in ps.values())
    s+=0.01*(abs(ds)*0+abs(sx)+pz+abs(px)+abs(gz)+abs(gx))
    rows.append(dict(seat_drop=ds,sit_fwd=sx,peg_down=pz,peg_back=px,grip_up=gz,grip_fwd=gx,seat_height=round(seat[1]),
                     lean_clearance_deg=round(lean,1),stand_reach_mm=round(stand),reach5_mm=round(reach5),score=round(s,2),postures=ps))
rows.sort(key=lambda r:r['score'])
print('CURRENT');[print(' ',n,p) for n,p in out['current'].items()]
print('reach5 current',round(ground_reach(1520,SEAT[1],228)))
for r in rows[:10]:
    print({k:v for k,v in r.items() if k!='postures'})
    for n,p in r['postures'].items():print('     ',n,{k:p[k] for k in TARGET})
# best per seat height
print('\nBEST PER SEAT DROP')
for ds in range(-50,1,10):
    r=min((r for r in rows if r['seat_drop']==ds),key=lambda r:r['score'])
    print(ds,{k:v for k,v in r.items() if k!='postures'},{n:(p['knee'],p['elbow'],p['trunk_fwd']) for n,p in r['postures'].items()})
out['top']=rows[:20];(R/'comfort-study-v2.json').write_text(json.dumps(out,indent=1))
