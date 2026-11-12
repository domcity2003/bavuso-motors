"""Find the best powertrain + weight package instead of comparing two fixed options.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/powertrain-optimise.py
Writes powertrain-optimum.csv (every feasible design), powertrain-frontier.csv and powertrain-frontier.png.

Every design must:
  - go 200 miles at a steady 70 mph even if the aero work only reaches CdA 0.40 m2 (target 0.38), with the pack sized to
    the bike's own weight
    (a lighter bike needs a smaller pack, which makes it lighter again);
  - charge 10-80 % in 25 minutes or less;
  - deliver 130 kW peak from the cells.
Among those it finds the lightest bike for each cost level (the frontier) and the point where extra weight saving
starts costing more than it is worth (the knee).
Costs use the same baseline and overhead method as powertrain-cost-down.py. All are planning estimates, not quotes.
"""
import csv, json, math, importlib.util
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cd',R/'tools/powertrain-cost-down.py');cd=importlib.util.module_from_spec(spec);spec.loader.exec_module(cd)

# Range model: same constants as research/range-weight-model.ps1
RHO,G,CRR,ETA,AUX,USABLE,RIDER=1.225,9.80665,0.015,0.90,300,0.90,90
CDA,CDA_CHECK,MPH=0.40,0.38,70     # design to the cautious drag area; report the target as upside
MAX_CHARGE_MIN=25

def wh_per_mile(bike_kg,cda=CDA,mph=MPH):
    v=mph*0.44704
    w=(0.5*RHO*cda*v**3+CRR*(bike_kg+RIDER)*G*v)/ETA+AUX
    return w/mph

# Cells: the study's set, plus the large cylinder at its makers' claimed 330 Wh/kg, plus silicon at a lower price
CELLS={c['key']:c for c in cd.CELLS}
CELLS['LCYL330']=dict(CELLS['LCYL'],key='LCYL330',name='Fast-charge large cylinder at claimed 330 Wh/kg',g=167.0,
                      ready='Makers\' prototype claim; needs production data')
CELLS['SA504@350']=dict(CELLS['SA504'],key='SA504@350',name='Amprius SA504 if quoted at $450 / $350 per kWh',
                        usd_kwh={1000:450,10000:350},ready='Hypothetical price; ask Amprius')
del CELLS['M58T'],CELLS['50S']          # fail fast charge or peak power at any useful size (see cost-down study)

# Pack construction: separate modules in a box, or cells bonded into a structural pack that carries frame loads
BUILDS={'module':dict(frac_add=0.00,frame_kg=0,usd={1000:0,10000:0}),
        'structural':dict(frac_add=0.06,frame_kg=-4,usd={1000:700,10000:400})}
# Lightweight parts packages (material cost per bike; estimates)
LIGHT={'none':dict(kg=0,usd={1000:0,10000:0},what='standard parts'),
       'premium':dict(kg=-7,usd={1000:4000,10000:3000},what='forged wheels, titanium fasteners, lithium 12 V, magnesium covers'),
       'carbon':dict(kg=-13,usd={1000:8500,10000:6500},what='premium + carbon bodywork, carbon subframe, carbon tank shroud')}
DRIVES={d['key']:d for d in cd.DRIVES if d['key'] in ('AXIAL+SiC','RADIAL')}

rows=[];slow=[]            # slow: designs that pass everything except the charge-time limit
for ck,c in CELLS.items():
    kind='pouch' if ck.startswith('SA504') else 'cyl'
    for bk,b in BUILDS.items():
        frac=c['frac']+b['frac_add']
        for lk,l in LIGHT.items():
            for dk,d in DRIVES.items():
                nonpack=cd.NONPACK_KG+d['motor_kg']-9.4+b['frame_kg']+l['kg']
                best=None
                for s in range(96,121):
                    if s*c['vmax']>cd.VMAX_LIMIT:break
                    for p in range(1,40):
                        n=s*p;kwh=n*c['wh']/1000
                        pack=n*c['g']/1000/frac;bike=nonpack+pack
                        rng=kwh*1000*USABLE/wh_per_mile(bike)
                        if rng<200:continue
                        chg=0.70*kwh/min(c['chg_c']*kwh,120)*60
                        if c['dis_c']*kwh<cd.PEAK_KW:break
                        if best is None or bike<best[4]:best=(s,p,n,kwh,bike,pack,rng,chg)
                        break                      # more parallel cells only adds weight
                if not best:continue
                target=slow if best[7]>MAX_CHARGE_MIN else rows
                s,p,n,kwh,bike,pack,rng,chg=best
                r=dict(cells=ck,build=bk,light=lk,drive=dk,series=s,parallel=p,cells_n=n,nominal_kwh=round(kwh,2),
                       full_v=round(s*c['vmax']),pack_kg=round(pack,1),bike_kg=round(bike,1),bike_lb=round(bike*2.20462),
                       range_mi_cda040=round(rng),range_mi_cda038=round(kwh*1000*USABLE/wh_per_mile(bike,CDA_CHECK)),
                       charge_10_80_min=round(chg,1),cell_ready=c['ready'])
                for v in cd.VOLS:
                    pt=kwh*c['usd_kwh'][v]+cd.PACK_FIXED[v]+n*cd.PACK_PER_CELL[kind][v]+d['usd'][v]
                    extra=b['usd'][v]+l['usd'][v]
                    r[f'bike_usd_{v}']=round(cd.OLD_DELIVERED[v]+(pt+extra-cd.OLD_PT[v])*(1+cd.OVERHEAD[v]))
                target.append(r)

HYPOTHETICAL=('LCYL330','SA504@350')
def frontier_of(data):
    """Lightest bike at each cost: walk designs from cheapest up and keep each one lighter than all cheaper ones."""
    out=[];lightest=1e9
    for r in sorted(data,key=lambda r:(r['bike_usd_10000'],r['bike_kg'])):
        if r['bike_kg']<lightest-0.05:out.append(dict(r));lightest=r['bike_kg']
    for a,b in zip(out,out[1:]):   # marginal cost of each step, dollars per pound saved
        b['usd_per_lb_saved']=round((b['bike_usd_10000']-a['bike_usd_10000'])/max(a['bike_lb']-b['bike_lb'],0.5))
    return out
frontier=frontier_of([r for r in rows if r['cells'] not in HYPOTHETICAL])
for r in frontier:r['evidence']='today'
upside=frontier_of(rows)
for r in upside:r['evidence']='if claims or price hold'
for name,data in (('powertrain-optimum.csv',rows+slow),('powertrain-frontier.csv',frontier+upside)):
    keys=list(dict.fromkeys(k for r in data for k in r))
    with open(R/name,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(data)
(R/'powertrain-optimum.json').write_text(json.dumps({'prepared':'2026-11-02 (US Central) by Claude Opus 5.5',
    'constraints':{'range_mi_at_70mph':200,'cda':CDA,'max_charge_10_80_min':MAX_CHARGE_MIN,'peak_kw':cd.PEAK_KW},
    'builds':BUILDS,'light':LIGHT,'frontier':frontier,'frontier_upside':upside},indent=1))

print(f"{len(rows)} feasible designs.")
for title,data in (('Frontier on today evidence',frontier),('Frontier if the 330 Wh/kg claim or a $350/kWh silicon price holds',upside)):
    print(title)
    for r in data:
        print(f"  {r['cells']:10}{r['build']:11}{r['light']:8}{r['drive']:10}{r['series']:4}x{r['parallel']:<3}{r['nominal_kwh']:6.1f} kWh"
              f"{r['bike_lb']:5} lb{r['range_mi_cda040']:5} mi ({r['range_mi_cda038']} @0.38){r['charge_10_80_min']:6} min"
              f"  ${r['bike_usd_1000']:>7,} / ${r['bike_usd_10000']:>7,}  {r.get('usd_per_lb_saved','')}")

fig,ax=plt.subplots(figsize=(10,6))
col={'LCYL':'#1f77b4','LCYL330':'#17becf','P50B':'#7f7f7f','SA504':'#d62728','SA504@350':'#ff9896'}
for ck in ('LCYL','LCYL330','P50B'):
    pts=[r for r in rows if r['cells']==ck]
    ax.scatter([r['bike_usd_10000']/1000 for r in pts],[r['bike_lb'] for r in pts],s=28,c=col[ck],label=CELLS[ck]['name'],alpha=.8)
ax.plot([r['bike_usd_10000']/1000 for r in frontier],[r['bike_lb'] for r in frontier],'k-',lw=1.5,label='best weight for the money, today')
ax.plot([r['bike_usd_10000']/1000 for r in upside],[r['bike_lb'] for r in upside],'k--',lw=1,label='if claims / lower silicon price hold')
for ck in ('SA504','SA504@350'):
    pts=[r for r in slow if r['cells']==ck]
    ax.scatter([r['bike_usd_10000']/1000 for r in pts],[r['bike_lb'] for r in pts],s=40,c=col[ck],marker='x',
               label=f"{CELLS[ck]['name']}: fails charge (28 min)")
ax.axvspan(30,35,color='0.92',zorder=0,label='cost cap $30-35k')
ax.set_xlabel('Delivered cost per bike at 10,000 bikes a year ($k)');ax.set_ylabel('Bike weight, ready to ride (lb)')
ax.set_title('Every design that does 200 mi at 70 mph, charges 10-80 % in 25 min or less, and makes 130 kW')
ax.grid(alpha=.3);ax.legend(fontsize=8,loc='upper right');fig.tight_layout();fig.savefig(R/'visuals/powertrain-frontier.png',dpi=130)
print('chart: visuals/powertrain-frontier.png')
