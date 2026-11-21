"""Export every visible solid of cad/Bavuso-V1.0-adventure.FCStd to program/data/cad-parts.csv
(name, system, make_buy, material, volume_mm3, bbox). Run with the bundled FreeCAD python from v1.0."""
import csv,re
from pathlib import Path
import FreeCAD as A
R=Path(__file__).resolve().parents[1]
BUY=('EMRAX','Cascadia','Orion','GX14','Cell_lane','Front_nominal','Rear_nominal','Front_wheel','Rear_wheel','Front_disc','Rear_disc',
     'Front_caliper','Rear_caliper_reserve','Fork_','Shock_','Coolant_','Radiator_core','Radiator_fan','NACS','Horn','Licence','Display_',
     'Steering_damper','Hand_grip','Hand_lever','Mirror_','Front_master','Front_brake_res','OBC','DCDC','Headlamp','Taillamp','Windscreen')
MAT=[('Cell_lane','Li-ion cells (P60B 21700)'),('Pack_case','aluminium 6xxx, 4 mm'),('Upper_rail|Upper_post|Lower_downlink|Lower_pack|Tail_rail|Tail_brace|Shock_bridge|Head_tube|Head_gusset|Tail_shock|Independent|Crash_guard','4130 / 25CrMo4 steel'),
     ('Swingarm','aluminium 6061/A356'),('Belly_skid|Battery_side|Belly_side|HV_cabinet|Rear_rack|Plate_hanger|Handguard|Peg_bracket|Rear_pulley|Front_pulley','aluminium'),
     ('tire','rubber'),('Windscreen','polycarbonate'),('Seat','foam / vinyl'),('Drive_belt','carbon-cord polyurethane'),
     ('Tail_side|Tail_undertray|Lower_body|Upper_body|Motor_side|Waist|fender|hugger|Radiator_pod|Seam|grille','painted composite/PP, 2.5 mm'),
     ('EMRAX','copper/aluminium/steel (supplier)'),('Cascadia|Orion|OBC|DCDC','electronics (supplier/class)')]
def mat(n):
    for pat,m in MAT:
        if re.search(pat,n):return m
    return 'mixed / see basis'
d=A.openDocument(str(R/'cad/Bavuso-V1.0-adventure.FCStd'))
rows=[]
for o in d.Objects:
    if o.TypeId!='Part::Feature' or not o.InList:continue
    g=o.InList[0].Name
    if g=='Keepouts':continue
    mb='buy' if o.Name.startswith(BUY) else 'make'
    rows.append([o.Name,g,mb,mat(o.Name),round(sum(abs(x.Volume) for x in o.Shape.Solids),1),o.Definition[:120]])
out=R/'program/data/cad-parts.csv'
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['name','system','make_buy','material','volume_mm3','basis']);w.writerows(sorted(rows,key=lambda r:(r[1],r[0])))
print(len(rows),'parts ->',out)
