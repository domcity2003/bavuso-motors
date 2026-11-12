"""Drive study: which motor + reduction gives about 3.0 s 0-60 mph AND 145-150 mph on this 416 V (99s) pack?

Each motor gets a torque-speed envelope at the pack's working voltage:
  EMRAX (axial flux, surface magnets, low inductance, so little field weakening), from datasheet v1.7 constants:
    full torque  min(T_peak, Kt x I_inverter)   up to  Kv_peak_load x V
    falling linearly to continuous torque at        Kv_nominal_load x V
    falling linearly to zero at                     Kv_no_load x V,   and never above the limiting speed
  Radial IPM (interior magnets): T_peak up to the corner, then constant power to max speed (field weakening).
Then for every gear ratio the launch is simulated (as tools/acceleration-check.py) and the best ratio that still
reaches 145 mph at the design voltage is kept.

Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/drive-study.py
"""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'mass-rollup.json').read_text())
BIKE,CX,CH=m['total_kg'],m['cog_mm']['x_from_rear_axle'],m['cog_mm']['height']
RIDER=(85.0,520.0,1090.0)
RHO,G,CRR,CDA_LAUNCH,CDA_TOP=1.225,9.80665,0.015,0.40,0.38
TYRE_R=0.305;MPH=0.44704
PACK_KW=130.0                 # pack/inverter power limit used for all options (optimiser peak target)
V_DESIGN=360.0                # 99s at ~50% charge under load (3.7 V open-circuit less IR drop)
V_FULL=416.0
TOP_MIN=145.0                 # mph
DRIVE_NOW_KG=21.0+6.5         # drive in the CAD roll-up: IPM + reduction 21 kg + 400 A SiC inverter 6.5 kg

# EMRAX datasheet v1.7 (emrax.com): Kv no-load / nominal / peak-load [rpm/V], Kt [Nm/Arms], peak A, T peak, T cont, limit rpm, kg
EMRAX={
 '228 MV (earlier CAD)':   dict(kv0=15.53,kvn=12.05,kvp=8.68, kt=0.64,ipk=360,tpk=220,tc=130,nmax=6500,kg=13.5,d=228),
 '228 LV+43%':            dict(kv0=28.19,kvn=21.64,kvp=15.32,kt=0.34,ipk=650,tpk=220,tc=130,nmax=6500,kg=13.5,d=228),
 '268 LV+100%':           dict(kv0=11.78,kvn=9.74, kvp=6.63, kt=0.88,ipk=650,tpk=500,tc=226,nmax=4500,kg=21.9,d=268),
 '268 LV+43%':            dict(kv0=16.49,kvn=13.62,kvp=9.27, kt=0.63,ipk=880,tpk=500,tc=226,nmax=4500,kg=21.9,d=268),
}
def emrax_T(p,V,i_inv):
    tcap=min(p['tpk'],p['kt']*i_inv);n1,n2,n0=p['kvp']*V,p['kvn']*V,p['kv0']*V
    def T(n):
        if n>p['nmax']:return 0.0
        if n<=n1:return tcap
        if n<=n2:return tcap+(min(p['tc'],tcap)-tcap)*(n-n1)/(n2-n1)
        return max(0.0,min(p['tc'],tcap)*(n0-n)/(n0-n2))
    return T
def ipm_T(tpk,kw,nmax):
    def T(n):
        if n>nmax:return 0.0
        return min(tpk,kw*1000/max(n*2*math.pi/60,1e-6))
    return T

def simulate(T,ratio,eta,drive_kg_delta):
    bike=BIKE+drive_kg_delta;M=bike+RIDER[0]
    b=(bike*CX+RIDER[0]*RIDER[1])/M/1000;h=(bike*CH+RIDER[0]*RIDER[2])/M/1000
    a_cap=min(1.0,b/h)*G;me=M*1.05
    def F(v):
        n=v/TYRE_R*60/(2*math.pi)*ratio
        return min(T(n)*ratio*eta/TYRE_R,PACK_KW*1000*eta/max(v,0.1))
    v=t=0.0;dt=0.002;t60=None
    while t<20 and v<60*MPH:
        a=min((F(v)-0.5*RHO*CDA_LAUNCH*v*v-CRR*M*G)/me,a_cap)
        if a<=1e-4:break
        v+=a*dt;t+=dt
    t60=t if v>=60*MPH else None
    top=0.0
    for k in range(1,1600):
        vv=k*0.05
        if F(vv)>=0.5*RHO*CDA_TOP*vv*vv+CRR*M*G:top=vv
        else:break
    return t60,top/MPH,a_cap/G

def best_ratio(T,eta,dkg,ratios):
    best=None
    for r in ratios:
        t60,top,cap=simulate(T,r,eta,dkg)
        if t60 is None or top<TOP_MIN:continue
        if best is None or t60<best[1]:best=(r,t60,top,cap)
    return best

rows=[]
for name,p in EMRAX.items():
    inv_a=p['ipk'];inv_kg=6.5 if inv_a<=400 else (9.0 if inv_a<=650 else 12.0)
    dkg=p['kg']+inv_kg-DRIVE_NOW_KG
    T=emrax_T(p,V_DESIGN,inv_a)
    b=best_ratio(T,0.95,dkg,[x/100 for x in range(150,500,5)])
    t_now=simulate(T,3.1,0.95,dkg)
    rows.append(dict(option=f'EMRAX {name}, belt only',motor='axial flux SPM',inverter_peak_A=inv_a,
        drive_kg_motor_plus_inverter=round(p['kg']+inv_kg,1),mass_change_vs_now_kg=round(dkg,1),
        full_torque_to_rpm_at_360V=round(p['kvp']*V_DESIGN),speed_limit_rpm_at_360V=round(min(p['nmax'],p['kv0']*V_DESIGN)),
        at_ratio_3_1=dict(zero_60_s=round(t_now[0],2) if t_now[0] else None,top_mph=round(t_now[1])),
        best_ratio_meeting_145mph=dict(ratio=b[0],zero_60_s=round(b[1],2),top_mph=round(b[2])) if b else 'cannot reach 145 mph at any ratio'))
# High-speed radial IPM with 2-stage reduction (gear + belt). Spec, not a catalogue part: tier-1 class motor.
for tpk,nmax in ((180,15000),(150,16000)):
    dkg=21.0+6.5-DRIVE_NOW_KG                              # motor + reduction 21 kg (optimiser RADIAL basis) + 400 A inverter
    T=ipm_T(tpk,PACK_KW,nmax)
    b=best_ratio(T,0.93,dkg,[x/10 for x in range(40,120)])
    rows.append(dict(option=f'Radial IPM {tpk} Nm / {nmax} rpm / 130 kW + 2-stage reduction',motor='radial IPM (field weakening)',
        inverter_peak_A=400,drive_kg_motor_plus_inverter=27.5,mass_change_vs_now_kg=round(dkg,1),
        best_ratio_meeting_145mph=dict(ratio=b[0],zero_60_s=round(b[1],2),top_mph=round(b[2])) if b else 'none'))
out=dict(prepared='2026-11-05 US Central, Claude Opus 5.5',
         assumptions=dict(bike_kg=BIKE,rider_kg=RIDER[0],pack_kw=PACK_KW,v_design=V_DESIGN,v_full=V_FULL,cda_launch=CDA_LAUNCH,cda_top=CDA_TOP,
                          tyre_rolling_radius_m=TYRE_R,launch_cap_g=1.0,eta_belt=0.95,eta_two_stage=0.93,
                          inverter_kg='6.5 (<=400 A), 9 (650 A), 12 (880 A): estimates from Leadrive 400 V 10 kg and BorgWarner 650 A ~7 kg'),
         options=rows)
(R/'drive-study.json').write_text(json.dumps(out,indent=1))
for r in rows:print(json.dumps(r))
