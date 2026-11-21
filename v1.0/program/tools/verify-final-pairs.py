"""Targeted re-check of the part pairs that were edited after the full 64-check build (cabinet resize, pivot cap restore,
battery plate notch, waist ledge). Run from v1.0 with FreeCAD python. Prints overlap volume (mm3) and gap (mm)."""
import sys,json,itertools
import FreeCAD as A,Part
D=A.openDocument('cad/Bavuso-V1.0-adventure.FCStd')
O=lambda n:D.getObject(n).Shape
def pair(a,b):
    sa,sb=(O(a) if isinstance(a,str) else a),(O(b) if isinstance(b,str) else b)
    d=sa.distToShape(sb)[0]
    v=sum(x.common(y).Volume for x in sa.Solids for y in sb.Solids if x.BoundBox.intersect(y.BoundBox)) if d<1e-6 else 0.0
    return round(d,2),round(v,1)
names=[o.Name for o in D.Objects if o.TypeId=='Part::Feature']
res={}
cab='HV_cabinet_2mm_STUDY'
for other in ['Upper_post_rear_m1','Upper_post_rear_1','Upper_body_fairing_tank_STUDY','Upper_rail_1_m1','Upper_rail_1_1','Seat_two_level_STUDY','Pack_case_structural_4mm_STUDY','Lower_body_battery_covers_STUDY','Tail_side_panels_STUDY','Cascadia_CM200_supplier_STEP','OBC_3p3kW_envelope']:
    res[f'{cab} vs {other}']=pair(cab,other)
for side in ('m1','1'):
    for t in ('Upper_rail_0','Lower_pack_rear_link','Tail_brace'):
        res[f'{t}_{side} vs Pivot_cover_cap_{side}']=pair(f'{t}_{side}',f'Pivot_cover_cap_{side}')
    res[f'Lower_pack_rear_link_{side} vs Battery_side_panel_{side}']=pair(f'Lower_pack_rear_link_{side}',f'Battery_side_panel_{side}')
    res[f'Pivot_slider_{side} vs Peg_bracket_{side}']=pair(f'Pivot_slider_{side}',f'Peg_bracket_{side}')
res['Lower_body vs Waist_ledge_plates']=pair('Lower_body_battery_covers_STUDY','Waist_ledge_plates')
res['Motor_side_covers vs Waist_ledge_plates']=pair('Motor_side_covers_STUDY','Waist_ledge_plates')
# cabinet contactors inside the box
for n in names:
    if n.startswith('GX14_main_'):res[f'{n} vs cabinet']=pair(n,cab)
for k,v in res.items():print(f'{k:70s} gap={v[0]:8} overlap={v[1]}')
json.dump({k:{'gap_mm':v[0],'overlap_mm3':v[1]} for k,v in res.items()},open('program/data/run/final-pair-recheck.json','w'),indent=1)
