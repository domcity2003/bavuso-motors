"""0-60 mph and top speed for drive options, using the CAD mass roll-up (mass-rollup.json).

Straight-line time-step model. Wheel force is the smallest of:
  motor torque x ratio x driveline efficiency / tyre radius   (torque limit)
  power available x efficiency / speed                         (power limit: motor, inverter or pack)
  wheelie / traction limit held by launch control              (a <= g x b/h, capped at 1.0 g)
Then drag (CdA, upright rider) and rolling resistance come off. Rotating parts add 5% effective mass.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/acceleration-check.py
"""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'mass-rollup.json').read_text())
RIDER=(85.0,520.0,1090.0)
RHO,G,CRR,CDA=1.225,9.80665,0.015,0.40
TYRE_R=0.305                          # rolling radius of the 160/60ZR17 under load
MPH=0.44704

def run(name,torque,rpm_max,kw,ratio,eta,bike_kg,cog_x,cog_h,motor_kg_delta=0.0):
    bike=bike_kg+motor_kg_delta;M=bike+RIDER[0]
    b=(bike*cog_x+RIDER[0]*RIDER[1])/M/1000;h=(bike*cog_h+RIDER[0]*RIDER[2])/M/1000
    a_cap=min(1.0,b/h)*G                                   # launch control holds the front wheel down
    me=M*1.05;v=0.0;t=0.0;dt=0.002;t60=None
    vmax_rpm=rpm_max/60*2*math.pi*TYRE_R/ratio
    while t<40:
        F=min(torque*ratio*eta/TYRE_R,kw*1000*eta/max(v,0.1))
        res=0.5*RHO*CDA*v*v+CRR*M*G
        a=min((F-res)/me,a_cap) if v<vmax_rpm else 0.0
        if a<=1e-4:break
        v+=a*dt;t+=dt
        if t60 is None and v>=60*MPH:t60=t
    # top speed: power limit vs rpm limit
    vp=0
    for vv in [x*0.05 for x in range(1,2000)]:
        if kw*1000*eta>=0.5*RHO*0.38*vv**3+CRR*M*G*vv and torque*ratio*eta/TYRE_R>=0.5*RHO*0.38*vv*vv+CRR*M*G:vp=vv
    top=min(vp,vmax_rpm)
    return dict(option=name,rider_on_kg=round(M,1),wheel_force_N=round(torque*ratio*eta/TYRE_R),
                launch_g_cap=round(a_cap/G,2),zero_60_s=round(t60,2) if t60 else None,
                top_speed_mph=round(top/MPH),top_limited_by='rpm' if vmax_rpm<vp else 'power/drag',
                ratio=ratio,motor_mass_change_kg=motor_kg_delta)

if __name__=='__main__':
    bk,cx,ch=m['total_kg'],m['cog_mm']['x_from_rear_axle'],m['cog_mm']['height']
    rows=[
     run('EMRAX 228 MV, 20:62 belt (current CAD)',220,6500,124,3.1,0.95,bk,cx,ch),
     run('Same drive at the optimiser mass (222.5 kg)',220,6500,124,3.1,0.95,222.5,cx,ch),
     run('EMRAX 228, short gearing for launch (ratio 4.6)',220,6500,124,4.6,0.95,bk,cx,ch),
     run('EMRAX 268 MV, 130 kW pack limit, ratio 2.2',500,4500,130,2.2,0.95,bk,cx,ch,motor_kg_delta=8.4),
     run('High-speed radial IPM 300 Nm / 16k rpm, 2-stage ratio 7.3',300,16000,130,7.3,0.93,bk,cx,ch,motor_kg_delta=7.5),
    ]
    for r in rows:print(json.dumps(r))
    (R/'acceleration-check.json').write_text(json.dumps(dict(prepared='2026-11-04 US Central, Claude Opus 5.5',
        assumptions=dict(rider_kg=RIDER[0],cda_launch=CDA,cda_top=0.38,crr=CRR,tyre_rolling_radius_m=TYRE_R,
                         rotating_mass_add=0.05,launch_cap_g='min(1.0, b/h)',targets='0-60 about 3.0 s, 145-150 mph'),
        options=rows),indent=1))
