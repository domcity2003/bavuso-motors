"""Bottom-up mass and centre-of-gravity roll-up of the adventure CAD (cad/Bavuso-V1.0-adventure.FCStd).

Every visible part gets a mass by one of four methods, each line tagged with where the number comes from:
  kg    fixed mass (supplier figure or engineering estimate) placed at the part's CAD centroid
  vol   CAD volume x material density (the CAD shape is close to the real part)
  shell CAD surface area x wall thickness x density (the CAD is a solid stand-in for a hollow section)
  pack  cells x cell mass at the cell centroid; case by volume; the rest of the pack to the optimiser's 133.7 kg
Things the CAD does not model (wiring, fasteners, 12 V, brake hydraulics...) are allowances at stated locations.

Coordinates in the saved file: X forward from the rear axle, Z = height above ground, Y left(-)/right(+).
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/mass-rollup.py
"""
import csv,json,math,sys
from pathlib import Path
import FreeCAD as A

R=Path(__file__).resolve().parents[1]
STEEL,ALU,PLASTIC,PC=7.85,2.70,1.05,1.20          # g/cm3; plastic = painted PP/ABS panel
WB=1486.8

# name (exact, or prefix ending in *) -> (method, value, unsprung share front/rear, source tag, note)
#   unsprung: ('F',share) or ('R',share) or None
RULES=[
 # ---- energy ----
 ('Cell_lane_*','pack',None,None,'S','594 x 180 g 26120-class cells'),
 ('Pack_case_structural_4mm_STUDY','vol',ALU,None,'C','4 mm aluminium structural case, CAD volume'),
 # ---- drive ----
 ('EMRAX_228_MV_LC_supplier_STEP','kg',13.5,None,'S','EMRAX 228 LC dry mass, emrax.com'),
 ('IPM_motor_and_gear_case_ENVELOPE','kg',21.0,None,'E','radial IPM 150 Nm/16k rpm about 14 kg + 2-stage reduction about 7 kg (optimiser RADIAL basis, drive-study.md)'),
 ('Front_pulley_PITCH_STUDY','kg',0.4,None,'E','20T 14 mm steel pulley'),
 ('Rear_pulley_PITCH_STUDY','kg',1.6,('R',1.0),'E','62T 14 mm aluminium pulley'),
 ('Drive_belt_14mm_STUDY','kg',0.5,('R',0.5),'E','14 mm pitch carbon belt, about 30 mm wide'),
 # ---- electronics ----
 ('Cascadia_CM200_supplier_STEP','kg',6.5,None,'E','contract SiC inverter (the chosen drive). CM200DX itself is about 11.3 kg (retailer)'),
 ('BROGEN_PV1776_body','kg',6.5,None,'E','6.6 kW on-board charger, catalogue body'),
 ('Orion_BMS2_108_supplier_STEP','kg',1.5,None,'E','Orion BMS2 108-cell; 40% lighter than the 2.4 kg original (Orion)'),
 ('HV_cabinet_2mm_STUDY','vol',ALU,None,'C','2 mm aluminium cabinet'),
 ('GX14_main_*','kg',0.45,None,'E','Gigavac GX14 main contactor'),
 ('Side_radiator_*','kg',1.15,None,'E','aluminium core + fan, unsized'),
 # ---- frame (chromoly tube, CAD tubes are hollow) ----
 ('Upper_rail_*','vol',STEEL,None,'C','32x2.5 chromoly'),
 ('Lower_downlink_*','vol',STEEL,None,'C','32x2.5 chromoly'),
 ('Lower_pack_rear_link_*','vol',STEEL,None,'C','32x2.5 chromoly'),
 ('Tail_rail_*','vol',STEEL,None,'C','28x2 chromoly'),
 ('Tail_brace_*','vol',STEEL,None,'C','28x2 chromoly'),
 ('Tail_shock_cross_tube','vol',STEEL,None,'C','28x3 chromoly'),
 ('Head_tube','vol',STEEL,None,'C','head tube'),
 ('Shock_top_bracket','vol',STEEL,None,'C','twin 8 mm plates'),
 ('Independent_hollow_pivot_stub_*','vol',STEEL,None,'C','pivot stub'),
 ('Pivot_6008_size_reference_*','kg',0.12,('R',0.5),'S','6008 bearing (catalogue 0.12 kg)'),
 ('Peg_bracket_*','kg',0.35,None,'E','machined aluminium hanger'),
 ('Peg_reference_*','kg',0.25,None,'E','rider peg'),
 ('Peg_rubber_*','kg',0.1,None,'E','peg rubber'),
 # ---- swingarm and shock ----
 ('Swingarm_1','shell',(ALU,3.5),('R',0.5),'C','fabricated box arm, 3.5 mm walls (CAD area x t)'),
 ('Swingarm_m1','shell',(ALU,3.5),('R',0.5),'C','fabricated box arm, 3.5 mm walls (CAD area x t)'),
 ('Swingarm_cross_brace','vol',ALU,('R',0.5),'C','50x5 aluminium tube'),
 ('Swingarm_shock_tower','vol',ALU,('R',0.5),'C','twin 8 mm aluminium plates'),
 ('Shock_body_STUDY','kg',2.0,('R',0.5),'E','semi-active damper body (with valves)'),
 ('Shock_spring_STUDY','kg',1.2,('R',0.5),'E','97 N/mm steel spring, 88 OD'),
 ('Shock_rod_STUDY','kg',0.3,('R',0.5),'E','damper shaft'),
 ('Shock_reservoir_STUDY','kg',0.6,None,'E','remote reservoir + hose'),
 ('Shock_Upper_eye_STUDY','kg',0.15,None,'E','eye and bearing'),
 ('Shock_Lower_eye_STUDY','kg',0.15,('R',1.0),'E','eye and bearing'),
 # ---- wheels, tyres, brakes ----
 ('Front_nominal_tire','kg',4.5,('F',1.0),'S','120/70R19 adventure tyre (Michelin Anakee retail listing ~4.5 kg)'),
 ('Rear_nominal_tire','kg',6.0,('R',1.0),'E','160/60ZR17 road/adventure tyre'),
 ('Front_wheel_STUDY','kg',3.4,('F',1.0),'E','forged aluminium 19x3.0 with bearings (premium package)'),
 ('Rear_wheel_STUDY','kg',4.2,('R',1.0),'E','forged aluminium 17x4.5 with bearings, cush hub'),
 ('Front_disc_carrier_*','kg',0.25,('F',1.0),'E','disc carrier'),   # before Front_disc_*: first match wins
 ('Front_disc_*','kg',1.2,('F',1.0),'E','320 mm floating disc'),
 ('Front_caliper_reserve_*','kg',0.85,('F',1.0),'E','radial 4-piston caliper'),
 ('Rear_disc_p1','kg',0.65,('R',1.0),'E','240 mm disc'),
 ('Rear_disc_carrier_p1','kg',0.1,('R',1.0),'E','disc carrier'),
 ('Rear_caliper_reserve','kg',0.6,('R',1.0),'E','2-piston caliper + bracket'),
 # ---- fork, steering, controls ----
 ('Fork_outer_tube_*','kg',2.6,None,'E','48 mm USD outer tube with cartridge and oil'),
 ('Fork_inner_tube_*','kg',1.0,('F',1.0),'E','inner tube'),
 ('Fork_axle_clamp_*','kg',0.8,('F',1.0),'E','axle foot (half the axle too)'),
 ('Fork_top_cap_*','kg',0.0,None,'E','fork cap/adjuster: included in the outer tube figure'),
 ('Fork_reflector_*','kg',0.01,('F',1.0),'E','side reflector'),
 ('Rear_caliper_bracket','kg',0.3,('R',1.0),'E','floating caliper bracket'),
 ('Lower_triple_clamp','kg',1.3,None,'E','forged clamp with stem'),
 ('Upper_triple_clamp','kg',0.7,None,'E','machined clamp'),
 ('Bar_*','kg',0.25,None,'E','bar section / riser'),
 ('Hand_grip_reserve_*','kg',0.35,None,'E','grip, throttle or switch housing'),
 ('Hand_lever_*','kg',0.45,None,'E','lever with radial master cylinder'),
 ('Display_reserve','kg',0.6,None,'E','7 in TFT'),
 ('Display_glass','kg',0.05,None,'E','TFT cover glass'),
 ('Display_mount','kg',0.15,None,'E','display bracket'),
 # ---- body ----
 ('Upper_body_fairing_tank_STUDY','vol',PLASTIC,None,'C','3 mm painted panel'),
 ('Lower_body_battery_covers_STUDY','vol',PLASTIC,None,'C','3 mm painted panel'),
 ('Motor_side_covers_STUDY','vol',PLASTIC,None,'C','3 mm panel'),
 ('Tail_side_panels_STUDY','vol',PLASTIC,None,'C','3 mm panel'),
 ('Battery_side_panel_*','vol',ALU,None,'C','proud bolted aluminium panel'),
 ('Belly_side_panel_*','vol',ALU,None,'C','proud bolted aluminium panel'),
 ('Belly_skid_plate_STUDY','vol',ALU,None,'C','4 mm aluminium skid plate'),
 ('Front_fender_STUDY','vol',PLASTIC,('F',1.0),'C','fork-mounted fender'),
 ('Rear_hugger_STUDY','vol',PLASTIC,('R',1.0),'C','swingarm-mounted hugger'),
 ('Windscreen_STUDY','vol',PC,None,'C','polycarbonate screen'),
 ('Seat_two_level_STUDY','kg',2.6,None,'E','foam (CAD 15.7 L at 0.05) + base and cover'),
 ('Seam_trim_*','vol',PLASTIC,None,'C','trim'),
 ('Side_grille_louvres_*','vol',PLASTIC,None,'C','grille'),
 ('Panel_bolts_*','kg',0.05,None,'E','panel bolts'),
 ('Mirror_body_*','kg',0.3,None,'E','mirror head'),
 ('Mirror_stalk_*','kg',0.08,None,'E','mirror stalk'),
 ('Headlamp_installation_STUDY','kg',1.2,None,'E','LED headlamp'),
 ('Headlamp_DRL_blade','kg',0.0,None,'E','DRL: included in the headlamp figure'),
 ('Taillamp_installation_STUDY','kg',0.25,None,'E','LED tail lamp'),
 ('Front_indicator_reserve_*','kg',0.05,None,'E','indicator'),
 ('Rear_indicator_reserve_*','kg',0.05,None,'E','indicator'),
 ('Plate_lamp','kg',0.05,None,'E','plate lamp'),
 ('Plate_hanger_arm','kg',0.45,None,'E','cast plate hanger with plate bracket'),
 ('Rear_indicator_stalk_*','kg',0.02,None,'E','indicator stalk'),
 ('Tail_undertray_STUDY','vol',PLASTIC,None,'C','3 mm undertray / inner fender'),
 ('Rear_rack_STUDY','kg',0.9,None,'E','aluminium rack'),
 ('Pivot_cover_cap_*','kg',0.04,None,'E','moulded cap'),
 ('Lever_perch_*','kg',0.12,None,'E','forged perch'),
 ('Switch_cube_*','kg',0.15,None,'E','switch housing'),
 ('Harness_*','kg',0.08,None,'E','bar harness leg and connector'),
 ('Front_master_cylinder','kg',0.35,None,'E','radial master cylinder'),
 ('Front_brake_reservoir','kg',0.1,None,'E','reservoir with fluid'),
 ('Front_master_banjo','kg',0.03,None,'E','banjo bolt'),
 ('Front_caliper_banjo_*','kg',0.03,None,'E','banjo bolt'),
 ('Rear_caliper_banjo','kg',0.03,None,'E','banjo bolt'),
 ('Front_brake_splitter','kg',0.08,None,'E','splitter'),
 ('Front_brake_hose_*','kg',0.18,None,'E','braided hose with fluid'),
 ('Rear_brake_hose','kg',0.15,None,'E','braided hose with fluid'),
 ('Rear_brake_junction','kg',0.05,None,'E','junction'),
 ('Mirror_glass_*','kg',0.05,None,'E','mirror glass'),
 ('Seat_welt','kg',0.05,None,'E','seat piping'),
 ('Licence_plate_US','kg',0.2,None,'S','US motorcycle plate'),
]
# Not in the CAD: (name, kg, (x,y,z), unsprung, source, note)
ALLOWANCES=[
 ('Pack internals (busbars, cooling ribbon, potting, slave boards)',None,'PACK_REST',None,'C','to the optimiser pack mass (cells/0.80)'),
 ('LV wiring harness',3.0,(760,0,700),None,'E','looms, connectors, fuse box'),
 ('HV cables and lugs',2.2,(640,0,520),None,'E','pack-cabinet-inverter-motor, charge inlet'),
 ('Charge inlet (NACS/CCS1)',0.8,(1000,120,850),None,'E','inlet and lid'),
 ('DC-DC converter 1 kW',1.2,(640,0,620),None,'E','in the cabinet area'),
 ('12 V lithium battery',1.0,(300,0,720),None,'E','under the seat (premium package)'),
 ('VCU, keyless, horn',0.7,(1200,0,880),None,'E','nose'),
 ('Coolant pump, hoses, 2 L coolant',2.8,(880,0,600),None,'E','motor, inverter, charger, pack loop'),
 ('Gear-case oil and oil-to-water exchanger',0.9,(560,0,430),None,'E','IPM drive only: about 0.5 L ATF-class oil shared by gears and motor cooling'),
 ('ABS module (Bosch 10 class), lines, fluid',1.6,(700,0,760),None,'E','under the tank'),
 ('Rear brake pedal and master cylinder',0.7,(520,200,430),None,'E','right side'),
 ('Passenger pegs and hangers',1.0,(150,0,520),None,'E',''),
 ('Side stand with switch',1.4,(560,-200,300),None,'E',''),
 ('Nose subframe, headlamp and dash brackets',1.3,(1330,0,900),None,'E',''),
 ('Body brackets and fixings',2.0,(850,0,700),None,'E',''),
 ('Fasteners (titanium where visible)',3.0,(750,0,600),None,'E','premium package'),
 ('Front axle, spacers',0.6,(1487,0,325),('F',1.0),'E',''),
 ('Rear axle, spacers, adjusters',1.0,(0,0,312),('R',1.0),'E',''),
 ('Swingarm pivot bolt and hardware',0.6,(540,0,390),('R',0.5),'E',''),
 ('Steering bearings, stem nut, steering damper',0.8,(1190,0,860),None,'E',''),
 ('Paint, decals, rubber, misc',1.0,(800,0,650),None,'E',''),
]
CELLS,CELL_G,PACK_KG=594,180.0,594*0.180/0.80

def match(name):
    for r in RULES:
        k=r[0]
        if (k.endswith('*') and name.startswith(k[:-1])) or k==name:return r
    return None

def main():
    d=A.openDocument(str(R/'cad/Bavuso-V1.0-adventure.FCStd'))
    lines=[];unmatched=[]
    cell_m=0.0;cell_c=A.Vector()
    for o in d.Objects:
        if o.TypeId!='Part::Feature' or not o.InList or o.InList[0].Name=='Keepouts':continue
        s=o.Shape;sol=s.Solids
        v=sum(abs(x.Volume) for x in sol)
        c=sum((x.CenterOfMass*abs(x.Volume) for x in sol),A.Vector())*(1/v) if v>0 else s.BoundBox.Center
        r=match(o.Name)
        if not r:unmatched.append(o.Name);continue
        _,meth,val,uns,src,note=r
        if meth=='kg':kg=val
        elif meth=='vol':kg=v/1000*val/1000
        elif meth=='shell':kg=s.Area/100*val[1]/10*val[0]/1000
        elif meth=='pack':kg=v/(math.pi*13**2*120)*CELL_G/1000;cell_m+=kg;cell_c+=c*kg
        lines.append(dict(item=o.Name,group=o.InList[0].Name,kg=kg,x=c.x,y=c.y,z=c.z,unsprung=uns,source=src,method=meth,note=note))
    cell_c=cell_c*(1/cell_m)
    case=next(l['kg'] for l in lines if l['item']=='Pack_case_structural_4mm_STUDY')
    for name,kg,pos,uns,src,note in ALLOWANCES:
        if pos=='PACK_REST':kg=PACK_KG-cell_m-case;pos=(cell_c.x,cell_c.y,cell_c.z)
        lines.append(dict(item=name,group='Allowance',kg=kg,x=pos[0],y=pos[1],z=pos[2],unsprung=uns,source=src,method='allowance',note=note))
    if unmatched:print('UNMATCHED (no mass rule):',unmatched,file=sys.stderr)

    M=sum(l['kg'] for l in lines)
    X,Y,Z=(sum(l['kg']*l[k] for l in lines)/M for k in 'xyz')
    unF=sum(l['kg']*l['unsprung'][1] for l in lines if l['unsprung'] and l['unsprung'][0]=='F')
    unR=sum(l['kg']*l['unsprung'][1] for l in lines if l['unsprung'] and l['unsprung'][0]=='R')
    # Pitch inertia about the CoG (point masses + nothing for part size: a lower bound)
    Iyy=sum(l['kg']*((l['x']-X)**2+(l['z']-Z)**2) for l in lines)/1e6
    groups={}
    for l in lines:
        g=l['group'];groups.setdefault(g,[0,0,0]);groups[g][0]+=l['kg'];groups[g][1]+=l['kg']*l['x'];groups[g][2]+=l['kg']*l['z']
    src={}
    for l in lines:src[l['source']]=src.get(l['source'],0)+l['kg']
    out=dict(prepared='2026-11-05 US Central, Claude Opus 5.5',model='cad/Bavuso-V1.0-adventure.FCStd',
             total_kg=round(M,1),total_lb=round(M*2.20462),
             cog_mm=dict(x_from_rear_axle=round(X),y=round(Y,1),height=round(Z)),
             front_rear_split_pct=[round(100*X/WB,1),round(100*(1-X/WB),1)],
             unsprung_kg=dict(front=round(unF,1),rear=round(unR,1)),
             pitch_inertia_point_mass_kgm2=round(Iyy,1),
             cells_kg=round(cell_m,1),pack_kg=round(PACK_KG,1),
             by_group={g:dict(kg=round(v[0],1),x=round(v[1]/v[0]),z=round(v[2]/v[0])) for g,v in sorted(groups.items(),key=lambda t:-t[1][0])},
             by_source={dict(S='supplier/catalogue',C='CAD geometry x density',E='engineering estimate')[k]:round(v,1) for k,v in src.items()},
             optimiser_reference_kg=222.5)
    with open(R/'mass-rollup.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['item','group','kg','x_mm','y_mm','height_mm','unsprung','source','method','note'])
        for l in sorted(lines,key=lambda l:-l['kg']):
            w.writerow([l['item'],l['group'],round(l['kg'],3),round(l['x']),round(l['y']),round(l['z']),
                        f"{l['unsprung'][0]}{l['unsprung'][1]}" if l['unsprung'] else '',
                        dict(S='supplier',C='CAD',E='estimate')[l['source']],l['method'],l['note']])
    (R/'mass-rollup.json').write_text(json.dumps(out,indent=1))
    print(json.dumps(out,indent=1))

main()
