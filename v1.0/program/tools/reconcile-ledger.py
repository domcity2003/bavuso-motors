"""Reconcile mass-rollup.csv line by line. Reads the ledger, applies the documented corrections, writes
program/data/mass-ledger-reconciled.csv. Read-only on all existing files.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/reconcile-ledger.py"""
import csv,re,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
rows=list(csv.DictReader(open(R/'mass-rollup.csv',encoding='utf-8')))
EB='detailed-design/electrical/electrical-bom.csv'
TH='detailed-design/thermal-study.md sized-parts table'
# item (or prefix*) -> (kg, action, reason, source_type, confidence)
C={
'Side stand with switch':(0,'remove','Double count: Side_stand_retracted (1.4 kg, "forged side stand with switch") is modelled. Review p2 item 1.','','high'),
'DC-DC converter 1 kW':(0,'remove','Double count: DCDC_converter_1p2kW (HELLA 2.8 kg) is modelled and electrical-detailed.md already says the 1.2 kg allowance is replaced. Review p2 item 2.','','high'),
'Charge inlet (NACS/CCS1)':(0,'remove','Double count: NACS_charge_inlet is modelled. Inlet lid and lock actuator are inside the Volex 0.9 kg figure. Review p2 item 3.','','high'),
'NACS_charge_inlet':(0.9,'restate','Volex NACS inlet 0.9 kg incl. door and lock actuator ('+EB+'). The ledger 1.3 kg said "with HV leads" but the leads are counted in the HV harness line.','supplier','medium'),
'BROGEN_PV1776_body':(3.0,'restate','Stale estimate. BROGEN catalogue p11 lists at most 3 kg ('+EB+'; components-electrical.csv V1-E007). The 6.5 kg was a placeholder (14 lb in the review).','supplier','high'),
'Cascadia_CM200_supplier_STEP':(6.75,'restate','Manufacturer published CM200DX mass 6.75 kg (cascadiamotion.com/cm-200; supplier-parts.md; components-electrical.csv V1-E005). The ledger note quoting "about 11.3 kg (retailer)" conflicts with the maker figure.','supplier','high'),
'GX14_main_*':(0.5,'restate','GX14 datasheet 0.5 kg each ('+EB+', Main contactors).','supplier','high'),
'Coolant_pump_*':(0.55,'restate','Thermal sizing: 2 pumps = 1.10 kg total ('+TH+'). Pierburg CWA50 class.','estimate','medium'),
'Coolant pump, hoses, 2 L coolant':(5.24,'split and restate','Modelled pumps (2 CAD parts) overlap this allowance, so pumps leave it. What remains: hoses 0.95 kg (16 mm EPDM, 5.4 m, clamps), 3.9 L of 50/50 glycol 4.19 kg (the old 2 L was too small) and sensors 0.10 kg ('+TH+').','estimate','medium'),
'Radiator_core_*':(0.805,'restate','Dry core with plastic tanks 0.805 kg each ('+TH+'). The ledger 1.9 kg was "filled", which double counts coolant now carried in the coolant line.','estimate','medium'),
'Radiator_fan_*':(0.55,'restate','190 mm BLDC fan with shroud 0.55 kg each (1.10 kg for two, '+TH+'). The ledger 0.35 kg was a 30 mm slim fan that does not match the sized part.','estimate','medium'),
'Coolant_PTC_heater_5kW':(1.9,'restate','Sized 5 kW HV PTC heater 1.90 kg ('+TH+').','estimate','medium'),
'Gear-case oil and oil-to-water exchanger':(0.45,'restate','Overlap with modelled Oil_cooler (0.6 kg). Only the oil stays here: about 0.5 L ATF-class, 0.45 kg. thermal-study.md counts the exchanger inside the drive unit. OPEN: if the 21 kg drive-unit figure already holds the exchanger, Oil_cooler (0.6 kg) is a third count.','estimate','medium'),
'Pack internals (busbars, cooling ribbon, potting, slave boards)':(13.45,'rebuild bottom-up','The old figure was a plug to the optimiser pack mass (cells/0.80 = 133.7 kg): 16.0 kg. Bottom-up: electrical internals excl. BMS 7.26 kg (busbars 4.66, fuse collectors 1.10, films 0.50, thermistor module 0.15, NTCs 0.15, tap harness 0.50, tap fuses 0.05, pass-throughs 0.15) plus thermal internals 6.19 kg (ribbons 2.18, adhesive 0.41, manifolds 0.70, fire-barrier foam 2.40, vent valve and liners 0.50). The BMS is separate (modelled).','calculated','medium'),
'LV wiring harness':(2.08,'restate','Electrical BOM: LV harness 2.4 kg finished (copper 1.05 kg). Modelled Harness_* bar legs (0.32 kg) sit inside it: 2.4 - 0.32 = 2.08. The old 3.0 kg also held the fuse box, now carried in the VCU/distribution line.','calculated','medium'),
'HV cables and lugs':(3.72,'restate','Electrical BOM HV harness: 3.3 m Coroflex 50 mm2 2.12 kg + 10 PowerLok halves 1.20 kg + lugs and conduit 0.40 kg = 3.72 kg. The old 2.2 kg left out the connectors.','calculated','medium'),
'12 V lithium battery':(0.9,'restate','Shorai LFX14A4-BS12 0.90 kg ('+EB+').','supplier','high'),
'VCU, keyless, horn':(2.10,'rescope','Horn_R28 (0.4 kg) is modelled, so the horn leaves this line (double count). Replaced by the LV items the ledger never carried: AEM VCU200 0.40, distribution box 1.15 (prototype ECUMaster PMU16; custom unit 0.5 at volume), keyless 0.25, bonding and HVIL 0.30 ('+EB+').','calculated','medium'),
'Steering bearings, stem nut, steering damper':(0.30,'restate','Double count: Steering_damper_envelope (1.1 kg) is modelled. Lower_triple_clamp is "forged clamp with stem". Leaves two bearings, stem nut and spacers, about 0.3 kg.','estimate','medium'),
'Front axle, spacers':(0.15,'restate','Overlap: Fork_axle_clamp_* notes say "axle foot (half the axle too)", so the whole axle is already in the two clamps. Only spacers stay.','estimate','medium'),
'Nose subframe, headlamp and dash brackets':(1.15,'restate','Display_mount (0.15 kg display bracket) is modelled, so the dash bracket leaves the allowance.','estimate','medium'),
'Panel_bolts_*':(0,'fold into fasteners','Panel bolts are fasteners; the 3.0 kg fastener allowance already covers all bolts. Removing the modelled 0.05 kg x 2 stops the double count.','','high'),
'Front_master_cylinder':(0,'remove','Hand_lever_* notes say "lever with radial master cylinder", so the brake master cylinder is already in the right lever. One cylinder exists.','','medium'),
'Hand_grip_reserve_*':(0.20,'restate','Note said "grip, throttle or switch housing" but Switch_cube_* (0.15 kg switch housing) is modelled separately. Grip and throttle tube only, 0.20 kg.','estimate','low'),
'Rear_disc_p1':(1.17,'restate','Stale. Ledger 0.85 kg is labelled 267x6, but the CAD solid is 267x5 and its volume (123.9 cm3) already weighs 0.97 kg in steel. The front discs match their CAD volume (155.6 cm3 = 1.22 kg vs 1.2). At the 6 mm the brake-fade run needs: 0.97 x 6/5 = 1.17 kg.','calculated','medium'),
'Cell_lane_*':(None,'keep, reclassify source','Mass unchanged. Relabelled estimate: the 26120 cell (180 g) is "not on open sale" (supplier-parts.md). The purchasable Molicel P60B fallback adds +5.6 kg of cells and about +7 kg of pack. Not applied.','estimate','low'),
}
ADD=[('EVCC ADVANTICS ADM-CS-EVCC','Allowance',0.2,'add','Omitted: charge communication controller 0.20 kg ('+EB+'). Native NACS needs it.','supplier','medium')]
def SYS(n,g):
    if g=='Energy' or n.startswith('Pack internals'):return 'Energy'
    if g=='Drive' or n.startswith('IPM') or n.startswith('Gear-case'):return 'Drive'
    if g=='Cooling' or n.startswith('Coolant pump'):return 'Cooling'
    if g=='Electronics' or any(n.startswith(k) for k in ('LV wiring','HV cables','12 V','VCU','DC-DC','Charge inlet','EVCC')):return 'Electronics'
    if g=='Protection' or n.startswith('Side stand'):return 'Protection'
    if g=='Chassis' or n.startswith('Swingarm pivot') or n.startswith('Passenger pegs'):return 'Chassis'
    if g=='BodyStudy' or any(n.startswith(k) for k in ('Nose subframe','Body brackets','Paint')):return 'Body'
    return 'Running gear'
def rule(n):
    for k,v in C.items():
        if (k.endswith('*') and n.startswith(k[:-1])) or k==n:return v
TAG={'supplier':'supplier','CAD':'calculated','estimate':'estimate'}
out=[]
for r in rows:
    n=r['item'];kg=float(r['kg']);v=rule(n)
    if v:
        new,act,why,st,conf=v
        if new is None:new=kg
        if not st:st=TAG[r['source']]
    else:new,act,why,st,conf=kg,'keep','',TAG[r['source']],''
    out.append(dict(item=n,group=r['group'],kg_now=kg,kg_reconciled=round(new,3),action=act,reason=why,source_type=st,
                    system=SYS(n,r['group']),confidence=conf,old_source=r['source'],method=r['method'],note=r['note']))
for n,g,kg,act,why,st,conf in ADD:
    out.append(dict(item=n,group=g,kg_now=0.0,kg_reconciled=kg,action=act,reason=why,source_type=st,system=SYS(n,g),confidence=conf,old_source='',method='allowance',note=''))
with open(R/'program/data/mass-ledger-reconciled.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['item','group','kg_now','kg_reconciled','action','reason','source_type','system','confidence'])
    for o in sorted(out,key=lambda o:(-abs(o['kg_reconciled']-o['kg_now']),-o['kg_now'])):
        w.writerow([o['item'],o['group'],round(o['kg_now'],3),o['kg_reconciled'],o['action'],o['reason'],o['source_type'],o['system'],o['confidence']])
now=sum(o['kg_now'] for o in out);rec=sum(o['kg_reconciled'] for o in out)
print('now %.2f reconciled %.2f delta %.2f  (%.1f lb -> %.1f lb)'%(now,rec,rec-now,now*2.20462,rec*2.20462))
sysd={}
for o in out:
    s=sysd.setdefault(o['system'],[0,0]);s[0]+=o['kg_now'];s[1]+=o['kg_reconciled']
for s,v in sorted(sysd.items(),key=lambda t:-t[1][1]):print('%-14s %7.2f %7.2f %+6.2f'%(s,v[0],v[1],v[1]-v[0]))
corr={}
for o in out:
    d=o['kg_reconciled']-o['kg_now']
    if abs(d)>1e-9:
        key=re.sub(r'_(m1|p1|1)$','',o['item'])
        corr[key]=corr.get(key,0)+d
print('--- corrections by |kg|')
for k,v in sorted(corr.items(),key=lambda t:-abs(t[1])):print('%+.2f %s'%(v,k))
print('sum of decreases %.2f, increases %.2f'%(sum(v for v in corr.values() if v<0),sum(v for v in corr.values() if v>0)))
print('sources now:',{k:round(sum(o['kg_now'] for o in out if o['old_source']==k),1) for k in('supplier','CAD','estimate','')})
rs={}
for o in out:rs[o['source_type']]=rs.get(o['source_type'],0)+o['kg_reconciled']
print('sources rec:',{k:round(v,1) for k,v in rs.items()})
print('lines: total',len(out),'estimate',sum(1 for o in out if o['old_source']=='estimate'),'allowance',sum(1 for o in out if o['group']=='Allowance'))
json.dump(out,open(R/'program/data/run/ledger-work.json','w'))
