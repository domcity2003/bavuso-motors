"""Seat a 50th-percentile male rider figure on the built bike, for renders and a leg-fit check.
Run: BAVUSO_MODEL=adventure ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/rider-figure.py
Reads cad/Bavuso-V1.0-<model>.FCStd, writes cad/Bavuso-V1.0-<model>-rider.FCStd (group RiderStudy) and
rider-fit.json. The posture follows tools/comfort-study-v2.py (same segment fractions and hip/ankle rules), with
two additions a stick model leaves out: the knees splay out until they sit on the side covers instead of inside them,
and the figure has flesh (capsules sized for a rider in riding gear), so overlaps with the bike read as leg contact.
Coordinates: the saved model is lifted, so Z here is height above ground.
"""
import os, json, math
from pathlib import Path
import FreeCAD as A, Part
from FreeCAD import Vector as V
R=Path(__file__).resolve().parents[1]
MODEL=os.environ.get('BAVUSO_MODEL','adventure')
D=A.openDocument(str(R/f'cad/Bavuso-V1.0-{MODEL}.FCStd'))
H=float(os.environ.get('BAVUSO_RIDER_H','1755'))
KNEE_Y=float(os.environ.get('BAVUSO_KNEE_Y','280'))   # knee-centre half-spread the splay stops at
def obj(prefix):return [o for o in D.Objects if o.Name.startswith(prefix) and hasattr(o,'Shape') and not o.Shape.isNull()]
seat=obj('Seat_two_level_STUDY')[0].Shape
def seat_top(x):
    s=seat.section(Part.makeLine(V(x,0,2000),V(x,0,0)))
    return max(v.Z for v in s.Vertexes) if s.Vertexes else None
tops=[(seat_top(x),x) for x in range(420,661,10)];tops=[t for t in tops if t[0]]
sz,sx=min(tops)                                     # the pocket floor is where the rider sits
grips={1 if o.Shape.BoundBox.Center.y>0 else -1:o.Shape.BoundBox.Center for o in obj('Hand_grip_reserve')}
pegs={1 if o.Shape.BoundBox.Center.y>0 else -1:o.Shape.BoundBox for o in obj('Peg_rubber')}
ua,fa,th,sk,tr=.186*H,.200*H,.245*H,.246*H,.288*H
hipz=sz-25+90
# trunk: upright unless the arms cannot reach (comfort-study rule)
lean=0.0
for l10 in range(0,401):
    t=math.radians(l10/10);sh=V(sx+tr*math.sin(t),.130*H,hipz+tr*math.cos(t))
    if (sh-grips[1]).Length<=ua+fa-.02*H:lean=l10/10;break
def law(a,b,c):return math.degrees(math.acos(max(-1,min(1,(a*a+b*b-c*c)/(2*a*b)))))
J={};parts=[]
def capsule(a,b,ra,rb):
    d=b-a;L=d.Length
    return [Part.makeCone(ra,rb,L,a,d),Part.makeSphere(ra,a),Part.makeSphere(rb,b)]
for side in (-1,1):
    hip=V(sx,side*.051*H,hipz)
    pb=pegs[side];ball=V(pb.Center.x,pb.Center.y,pb.ZMax)
    ank=V(ball.x-.073*H-15,ball.y,ball.z+25+.039*H)
    d=(ank-hip).Length;u=(ank-hip);u.normalize()
    al=math.radians(law(th,d,sk))
    for k10 in range(0,61):      # splay the knee outward until it clears the side covers (knee centre |Y| >= 280)
        f=V(1,side*k10/10,0);f.normalize();w=f-u*(f.dot(u));w.normalize()
        knee=hip+u*(th*math.cos(al))+w*(th*math.sin(al))
        if abs(knee.y)>=KNEE_Y:break
    t=math.radians(lean);sh=V(sx+tr*math.sin(t),side*.130*H,hipz+tr*math.cos(t))
    g=grips[side];dg=(g-sh).Length;mid=(sh+g)*.5;sg=g-sh;sg.normalize()
    bend=V(0,side*.6,-1);bend=bend-sg*(bend.dot(sg));bend.normalize()
    hh=math.sqrt(max(0,ua*ua-(dg/2)**2));elb=mid+bend*hh
    J[side]=dict(hip=hip,knee=knee,ankle=ank,ball=ball,shoulder=sh,elbow=elb,grip=g)
    parts+=capsule(hip,knee,88,62)+capsule(knee,ank,58,44)+capsule(sh,elb,52,44)+capsule(elb,g,44,38)+[Part.makeSphere(48,g)]
    boot=Part.makeBox(ball.x+60-(ank.x-75),110,ank.z+70-ball.z,V(ank.x-75,ball.y-55,ball.z+2))
    parts.append(boot.makeFillet(18,boot.Edges))
# torso: ellipse sections up the trunk line, shoulders wider than hips
def ell(z,rx,ry):
    x=sx+(z-hipz)*math.tan(math.radians(lean));c=V(x,0,z)
    return Part.Wire(Part.Ellipse(V(x,ry,z),V(x+rx,0,z),c).toShape())
shz=hipz+tr*math.cos(math.radians(lean))
torso=Part.makeLoft([ell(hipz-40,120,170),ell(hipz+120,105,150),ell(hipz+300,120,175),ell(shz-20,100,205),ell(shz+40,70,120)],True,False)
parts.append(torso)
nb=V(sx+(shz+40-hipz)*math.tan(math.radians(lean)),0,shz+40)
parts+=[Part.makeCylinder(55,90,nb,V(0,0,1)),Part.makeSphere(140,nb+V(25,0,215))]   # neck and helmet
grp=D.getObject('RiderStudy') or D.addObject('App::DocumentObjectGroup','RiderStudy')
for i,p in enumerate(parts):
    o=D.addObject('Part::Feature',f'Rider_{i:02d}');o.Shape=p;grp.addObject(o)
# leg fit: overlap of thighs/shins/boots with the bike, by part (a little is contact on foam or a panel; a lot is a clash)
legs=Part.makeCompound([p for p in parts if p.BoundBox.ZMax<hipz+100])
fit={}
for o in D.Objects:
    if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith('Rider_') or not o.Visibility:continue
    if o.TypeId!='Part::Feature' or not o.Shape.BoundBox.intersect(legs.BoundBox):continue
    try:v=sum(a.common(b).Volume for a in legs.Solids for b in o.Shape.Solids if a.BoundBox.intersect(b.BoundBox))
    except Exception:continue
    if v>1000:fit[o.Name]=round(v/1000,1)
r=lambda v:[round(c) for c in v]
out=dict(rider_height_mm=H,sit_point_above_ground=[round(sx),round(sz,1)],trunk_lean_deg=lean,
         joints={('left' if s>0 else 'right'):{k:r(v) for k,v in j.items()} for s,j in J.items()},
         knee_deg=round(law(th,sk,(J[1]['ankle']-J[1]['hip']).Length),1),
         elbow_deg=round(law(ua,fa,(J[1]['grip']-J[1]['shoulder']).Length),1),
         leg_overlap_cm3_by_part=dict(sorted(fit.items(),key=lambda kv:-kv[1])))
(R/'rider-fit.json').write_text(json.dumps(out,indent=1))
print(json.dumps(out,indent=1))
D.saveAs(str(R/f'cad/Bavuso-V1.0-{MODEL}-rider.FCStd'))
print('saved rider model')
