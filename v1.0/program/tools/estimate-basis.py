"""Classify every 'estimate' (and allowance) ledger line: what the number rests on and whether a real supplier figure can replace it.
Reads program/data/run/ledger-work.json (from reconcile-ledger.py). Writes program/data/mass-ledger-estimates.csv.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/estimate-basis.py"""
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
L=json.load(open(R/'program/data/run/ledger-work.json'))
vol={r['name']:float(r['vol_cm3']) for r in csv.DictReader(open(R/'program/data/run/cad-volumes.csv'))}
# (regex, family, based_on, replaceable, how)
P=[
(r'^IPM_motor','Drive unit','drive-study.md spec: 14 kg motor + 7 kg two-stage reduction. No supplier part; CAD is an envelope.','partly','Motor: yes (EMRAX 228 LC 13.5 kg published; Helix SPX177-45 13 kg). Reduction gear: no, needs an RFQ or own design.'),
(r'^(Front|Rear)_pulley|^Drive_belt','Belt drive','Catalogue-style guess for 20T/62T 14 mm pulleys and a 30 mm carbon belt.','partly','Belt: Gates publishes belt mass per length. Pulleys: custom, so derive from CAD volume x density once designed.'),
(r'^Cascadia|^BROGEN|^Orion|^GX14','HV electronics (named parts)','Named supplier parts; ledger value was a placeholder or rounded.','yes','Published masses: CM200DX 6.75 kg, BROGEN <= 3 kg, Orion 1.47 kg, GX14 0.5 kg. Applied in the reconciled column.'),
(r'^HV_(upper|charge)_junction','HV boxes','Placeholder for box plus contents (BDU 0.9 + MSD, pyro, fuses; CJB 0.5 + two GX14).','partly','Sum of catalogue parts (electrical-bom.csv); the enclosures are custom, so mass comes from CAD volume x wall once drawn.'),
(r'^(Radiator_core|Radiator_fan|Coolant_|Oil_cooler)','Cooling hardware','thermal-study.md sizing table (planning estimates, not quotes).','yes','Pump: Pierburg CWA50 datasheet. Heater and valve: catalogue parts. Cores and fans: supplier quote (Mahle, Valeo, Spal class).'),
(r'^(Front|Rear)_nominal_tire','Tyres','Retail listings or rule of thumb. Metzeler data sheet lists no mass.','yes','Buy the exact tyre (Metzeler Tourance Next 2 120/70R19, 170/60R17) and weigh it.'),
(r'^(Front|Rear)_wheel','Wheels','Assumed forged aluminium 19x3.0 and 17x4.5. supplier-parts.md: no maker publishes the mass.','partly','Ask forged-wheel makers for the weight of the exact size; spoked or cast sets are heavier.'),
(r'^(Front|Rear)_(disc|caliper)|^Rear_caliper|^Front_disc_carrier','Brakes','Typical figures for 320 mm floating discs, radial 4-piston and 2-piston calipers.','yes','Catalogue calipers publish mass (Kawasaki 43080-0156 candidate in parts-register.csv, Brembo, Nissin). Discs: from CAD volume x steel.'),
(r'^Rear_disc_carrier','Brakes','Illustrative CAD carrier; 0.1 kg is lower than the front by more than the size ratio.','partly','CAD volume x 2.7 once the carrier is real.'),
(r'^Fork_|^Lower_triple|^Upper_triple','Fork and clamps','Engineer guess for a 48 mm USD fork (cartridge and oil in the outer tube).','partly','WP, Showa, Kayaba or Ohlins spec sheets sometimes list fork mass. Clamps: CAD volume x alloy.'),
(r'^Shock_','Rear shock','Semi-active damper body 2.0, spring 1.2, rod 0.3, reservoir 0.6, eyes 0.15. Guesses.','yes','Shock makers publish assembly mass (Ohlins, WP). Reservoir may already be inside the body figure (watch list).'),
(r'^Steering_damper','Steering damper','Guess for a semi-active rotary damper.','yes','Ohlins steering damper data sheet.'),
(r'^(Bar_|Hand_|Lever_|Switch_|Front_brake_|Front_master|Display|Harness_|Rear_brake_|Front_caliper_banjo|Rear_caliper_banjo)','Controls and brake plumbing','Typical catalogue values for bars, levers, perches, hoses, TFT.','yes','Catalogue parts publish mass (Magura, Brembo, Bosch/KTM TFT class). Small parts below 0.1 kg are not worth chasing.'),
(r'^(Headlamp|Taillamp|Plate_lamp|Front_indicator|Rear_indicator|Mirror_|Horn|Rear_reflector|Side_reflector|Fork_reflector)','Lamps, mirrors, horn','Typical LED lamp and mirror masses. Lamp is a custom OE module (parts-register.csv SP-14).','partly','Indicators, mirrors and horn: catalogue. Headlamp: supplier quote.'),
(r'^(Peg_|Rear_rack|Plate_hanger|Side_stand|Pivot_slider|Pivot_cover|Seat|Panel_bolts|Pivot_6008)','Small custom or standard parts','Hand figures for aluminium pegs, rack, hanger, seat foam and cover.','partly','Custom parts: CAD volume x density once designed. Bearings: SKF/NSK catalogue (6008 is 0.12 kg).'),
(r'^Display','Display','7 in TFT guess.','yes','Supplier data sheet.'),
]
A={
'Pack internals':('Plug to optimiser pack mass (cells/0.80 less cells and case).','yes','Replaced bottom-up by electrical-bom.csv and thermal sizing (13.45 kg).'),
'LV wiring harness':('Hand figure, 3.0 kg.','yes','elec-lv harness cut list gives 2.4 kg; a real cut list from a harness maker replaces it.'),
'HV cables and lugs':('Hand figure, 2.2 kg.','yes','Coroflex 630 g/m x 3.3 m plus PowerLok masses (3.72 kg).'),
'12 V lithium':('Hand figure.','yes','Shorai 0.90 kg.'),
'VCU, keyless':('Hand figure.','yes','AEM VCU200, PMU16, keyless module data sheets.'),
'Coolant pump, hoses':('Hand figure for a 2 L loop.','yes','Hose cut list x EPDM mass per metre; glycol volume from the loop.'),
'Gear-case oil':('Hand figure.','yes','Oil volume x density; exchanger mass from supplier.'),
'ABS module':('Bosch 10-class guess.','yes','Bosch MSC data sheet mass; lines are partly modelled.'),
'Rear brake pedal':('Hand figure.','partly','Catalogue master cylinder plus pedal from CAD.'),
'Passenger pegs':('Hand figure.','partly','CAD volume x density.'),
'Nose subframe':('Hand figure.','no','Only the designed bracket set can be weighed (CAD x density).'),
'Body brackets':('Hand figure, about 1% of bike mass.','no','Needs the finished BOM; derive from drawn brackets.'),
'Fasteners':('Hand figure, titanium where visible.','no','Fastener count from the BOM x catalogue mass per bolt.'),
'Front axle':('Hand figure.','yes','Axle and spacer drawing x steel.'),
'Rear axle':('Hand figure.','yes','Axle and spacer drawing x steel.'),
'Swingarm pivot':('Hand figure.','yes','Bolt catalogue.'),
'Steering bearings':('Hand figure.','yes','Bearing catalogue.'),
'Paint, decals':('Hand figure.','no','Powder-coat area x film mass; decals negligible.'),
'Side stand with switch':('Hand figure; duplicates the modelled stand.','n/a','Removed in the reconciled ledger.'),
'DC-DC converter':('Hand figure; duplicates the modelled HELLA unit.','n/a','Removed in the reconciled ledger.'),
'Charge inlet':('Hand figure; duplicates the modelled NACS inlet.','n/a','Removed in the reconciled ledger.'),
'EVCC':('Supplier figure.','yes','Advantics data sheet.'),
}
rows=[]
for o in L:
    if o['old_source']!='estimate' and o['group']!='Allowance' and o['action']!='add':continue
    n=o['item'];fam=basis=rep=how=None
    if o['group']=='Allowance' or o['action']=='add':
        for k,v in A.items():
            if n.startswith(k):fam='Allowance';basis,rep,how=v;break
    else:
        for pat,f,b,r_,h in P:
            if re.match(pat,n):fam,basis,rep,how=f,b,r_,h;break
    if not fam:fam,basis,rep,how='UNCLASSIFIED','','',''
    v=vol.get(n);imp=round(o['kg_now']*1000/v,2) if v else ''
    rows.append([n,o['system'],round(o['kg_now'],3),round(o['kg_reconciled'],3),fam,basis,rep,how,imp])
with open(R/'program/data/mass-ledger-estimates.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['item','system','kg_now','kg_reconciled','family','based_on','supplier_figure_possible','how','cad_implied_density_g_cm3'])
    w.writerows(rows)
fam={}
for r in rows:
    d=fam.setdefault((r[4],r[6]),[0,0.0]);d[0]+=1;d[1]+=r[3]
for k,v in sorted(fam.items(),key=lambda t:-t[1][1]):print('%-34s %-7s n=%3d kg=%6.2f'%(k[0],k[1],v[0],v[1]))
print('total lines',len(rows),'unclassified',[r[0] for r in rows if r[4]=='UNCLASSIFIED'])
tot={}
for r in rows:tot[r[6]]=tot.get(r[6],0)+r[3]
print({k:round(v,1) for k,v in tot.items()},{k:sum(1 for r in rows if r[6]==k) for k in tot})
