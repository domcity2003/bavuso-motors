"""Battery / motor / inverter cost-down study for a ~30.5 kWh pack (200 mi at 70 mph after the aero fixes).
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/powertrain-cost-down.py
Writes powertrain-cost-down.csv (every cell x drive combination) and powertrain-cost-down.json.

How a bike cost is found: start from Codex's Oct 25 delivered cost per bike (cost-summary.json) and swap the
powertrain groups (cells, pack hardware, BMS, motor, inverter) for the new choice. The change is grossed up by the
overhead that scales with material value in that model (inbound freight, import, scrap, warranty).
All prices are planning estimates anchored on public prices (see powertrain-cost-down.md); none is a quote.
"""
import csv, json, math
from pathlib import Path

R=Path(__file__).resolve().parents[1]
VOLS=(1000,10000)
TARGET_KWH=(30.0,32.0)          # nominal pack energy window (large cells come in coarse steps)
VMAX_LIMIT=460                  # full-charge pack volts; Tesla V3 Superchargers serve packs up to about 500 V
NONPACK_KG=95.5                 # everything outside the pack, from the engineering release review
PEAK_KW=130                     # peak battery power the cells must deliver

# Codex baseline (cost-model.csv, base case): the groups this study replaces, and the overhead that scales with them
OLD_DELIVERED={1000:59377.22,10000:41183.01}
OLD_PT={1000:21000+7500+6000+1800+1100+1100+600,      # CELLS INVERTER MOTOR PACK_HV BMS PACK_MECHANICAL THERMAL
        10000:14000+6000+4500+1300+900+800+430}
OVERHEAD={1000:(1513+1261+1513+1994)/50445,           # (INBOUND+IMPORT+SCRAP+WARRANTY) / material, per bike
          10000:(898+898+718+1189)/35910}

# Cells. wh and g are per cell; usd_kwh = cell price per kWh at 1k and 10k bikes a year (planning estimates);
# chg_c = practical average charge rate 10-80 % with a cooled pack; dis_c = continuous discharge rating.
CELLS=[
 dict(key='SA504',name='Amprius SA504 silicon pouch (current design)',wh=37.57,g=97.3,frac=0.80,cm3=43.7,
      usd_kwh={1000:798,10000:532},chg_c=1.5,dis_c=6,v=3.40,vmax=4.20,ready='Sampling; supply and price open',
      basis='Codex model $30/$20 per cell (unquoted); no public production price'),
 dict(key='P50B',name='Molicel P50B 21700 power cell',wh=18.0,g=70.0,frac=0.72,cm3=24.2,
      usd_kwh={1000:200,10000:150},chg_c=2.0,dis_c=12,v=3.60,vmax=4.20,ready='In volume production',
      basis='nkon bulk about EUR 4.5-4.8 ex-VAT (~$290/kWh); OEM contract discount assumed'),
 dict(key='50S',name='Samsung 50S 21700 power cell',wh=18.0,g=72.0,frac=0.72,cm3=24.2,
      usd_kwh={1000:170,10000:130},chg_c=1.0,dis_c=5,v=3.60,vmax=4.20,ready='In volume production',
      basis='Marketplace $1.10-2.47/cell at volume ($61-137/kWh); 6 A max continuous charge'),
 dict(key='M58T',name='LG M58T 21700 high-energy cell',wh=20.0,g=70.0,frac=0.72,cm3=24.2,
      usd_kwh={1000:150,10000:115},chg_c=0.6,dis_c=2.2,v=3.60,vmax=4.20,ready='In volume production',
      basis='Energy-cell pricing near BNEF NMC cell average ($74-79/kWh) plus small-buyer premium'),
 dict(key='LCYL',name='Fast-charge large cylinder (26120 / 46-series class)',wh=55.0,g=180.0,frac=0.74,cm3=63.7,
      usd_kwh={1000:210,10000:150},chg_c=3.0,dis_c=6,v=3.60,vmax=4.20,ready='Prototypes; EVE / A123 industrialising 2026-27',
      basis='Stark Future 26120 claims 330 Wh/kg, 10-15 min charge; modelled as a 26120 at 305 Wh/kg (55 Wh, 180 g), priced above 21700'),
]
# Pack hardware outside the cells: fixed part (BMS electronics, enclosure, cooling plate, sensing) + per-cell interconnect
PACK_FIXED={1000:1500,10000:1050}
PACK_PER_CELL={'pouch':{1000:0.60,10000:0.40},'cyl':{1000:0.35,10000:0.25}}

# Motor + inverter. usd = combined unit cost at 1k and 10k bikes a year.
DRIVES=[
 dict(key='E208+CM200',name='EMRAX 208 + Cascadia CM200DX (current)',usd={1000:13500,10000:10500},peak_kw=86,motor_kg=9.4,
      basis='Codex model; CM200 retail $7.2-8.7k',meets='No: about 86 kW peak, below the 120-130 kW target'),
 dict(key='E228+CM200',name='EMRAX 228 + Cascadia CM200DX',usd={1000:10800,10000:8600},peak_kw=124,motor_kg=13.5,
      basis='EMRAX 228 liquid-cooled about EUR 3,590 retail; CM200 per Codex',meets='Yes, borderline (124 kW peak)'),
 dict(key='AXIAL+SiC',name='Axial-flux motor (EMRAX 228 class) + contract-built SiC inverter',usd={1000:5500,10000:3600},peak_kw=130,motor_kg=13.5,
      basis='Motor at volume discount to retail; inverter from a SiC reference design built by a contract manufacturer',meets='Yes'),
 dict(key='RADIAL',name='Custom radial IPM motor + inverter from an e-drive tier-1',usd={1000:3000,10000:1500},peak_kw=130,motor_kg=21.0,
      basis='Brogen 100 kW kit listed $1,235 (2+ sets); DOE target $6/kW drive; Munro Model Y inverter about $520',meets='Yes, about 7 kg heavier'),
]

def layout(c):
    """Series x parallel that lands in the energy window with the lowest full-charge voltage under the limit."""
    best=None
    for s in range(96,121):
        if s*c['vmax']>VMAX_LIMIT:break
        p=math.ceil(TARGET_KWH[0]*1000/(s*c['wh']))
        kwh=s*p*c['wh']/1000
        if kwh<=TARGET_KWH[1] and (best is None or abs(kwh-30.5)<abs(best[2]-30.5)):best=(s,p,kwh)
    return best

def main():
    rows=[]
    for c in CELLS:
        s,p,kwh=layout(c);n=s*p
        cell_kg=n*c['g']/1000;pack_kg=cell_kg/c['frac'];bike_kg=NONPACK_KG+pack_kg
        chg_kw=min(c['chg_c']*kwh,120)      # cell limit, capped at 120 kW (about 300 A through the inlet at 400 V)
        t1080=0.70*kwh/chg_kw*60
        dis_ok=c['dis_c']*kwh>=PEAK_KW
        kind='pouch' if c['key']=='SA504' else 'cyl'
        for d in DRIVES:
            r=dict(cells=c['key'],cell_name=c['name'],drive=d['key'],drive_name=d['name'],series=s,parallel=p,cells_n=n,
                   nominal_kwh=round(kwh,2),nominal_v=round(s*c['v']),full_v=round(s*c['vmax']),
                   cell_wh_kg=round(c['wh']/c['g']*1000),pack_kg=round(pack_kg,1),
                   pack_litres=round(n*c['cm3']/1000/(0.65 if kind=='pouch' else 0.55)),   # cells fill ~55 % (round) / 65 % (pouch) of the box
                   bike_kg=round(bike_kg+d['motor_kg']-9.4,1),
                   bike_lb=round((bike_kg+d['motor_kg']-9.4)*2.20462),charge_kw=round(chg_kw),charge_10_80_min=round(t1080),
                   peak_power_ok=dis_ok and d['peak_kw']>=120,drive_meets=d['meets'],cell_ready=c['ready'])
            for v in VOLS:
                cells_usd=kwh*c['usd_kwh'][v];pack_usd=PACK_FIXED[v]+n*PACK_PER_CELL[kind][v]
                pt=cells_usd+pack_usd+d['usd'][v]
                r[f'cells_usd_{v}']=round(cells_usd);r[f'pack_hw_usd_{v}']=round(pack_usd);r[f'drive_usd_{v}']=d['usd'][v]
                r[f'powertrain_usd_{v}']=round(pt)
                r[f'bike_delivered_usd_{v}']=round(OLD_DELIVERED[v]+(pt-OLD_PT[v])*(1+OVERHEAD[v]))
            rows.append(r)

    with open(R/'powertrain-cost-down.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    out={'prepared':'2026-11-02 (US Central) by Claude Opus 5.5','status':'Planning estimates from public prices; not quotes',
         'target_kwh':TARGET_KWH,'baseline_delivered':OLD_DELIVERED,'baseline_powertrain':OLD_PT,'overhead_rate':OVERHEAD,
         'cells':CELLS,'drives':DRIVES,'pack_fixed':PACK_FIXED,'pack_per_cell':PACK_PER_CELL,'rows':rows}
    (R/'powertrain-cost-down.json').write_text(json.dumps(out,indent=1))
    print(f"{'cells':6}{'drive':12}{'kWh':>6}{'s x p':>9}{'V':>5}{'pack kg':>8}{'L':>5}{'bike lb':>8}{'10-80':>6}{'peak':>6}{'$1k/yr':>9}{'$10k/yr':>9}")
    for r in rows:
        print(f"{r['cells']:6}{r['drive']:12}{r['nominal_kwh']:6.1f}{r['series']:>5}x{r['parallel']:<3}{r['full_v']:5}{r['pack_kg']:8.0f}{r['pack_litres']:5}{r['bike_lb']:8}{r['charge_10_80_min']:6}{'ok' if r['peak_power_ok'] else 'NO':>6}{r['bike_delivered_usd_1000']:9,}{r['bike_delivered_usd_10000']:9,}")

if __name__=='__main__':main()
