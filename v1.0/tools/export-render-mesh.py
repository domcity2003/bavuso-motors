"""Export the integrated model as one OBJ (+MTL) for Blender Cycles rendering.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/export-render-mesh.py
Each visible part becomes an OBJ object; its material name says what it is made of (see kind()),
and tools/render-cycles.py turns those names into physical materials. Cells and keepouts are skipped.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]/'.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin'))
import FreeCAD as A
import os
R=Path(__file__).resolve().parents[1]
D=A.openDocument(str(R/f"cad/Bavuso-V1.0-{os.environ.get('BAVUSO_MODEL','integrated')}.FCStd"))

def kind(o):
    """Material key for a part, mirroring render-integrated.FCMacro."""
    n=o.Name
    if n.startswith('Rider_'):return 'rider'
    if 'tire' in n:return 'tyre'
    if 'hose' in n or 'Harness_bar' in n:return 'hose'
    if 'banjo' in n or 'splitter' in n or 'Rear_brake_junction' in n:return 'alu'
    if 'Mirror_glass' in n:return 'mirror'
    if 'Display_glass' in n:return 'lamp_lens'
    if 'reservoir' in n and 'Shock' not in n:return 'reservoir'
    if n.startswith(('Switch_cube','Lever_perch','Front_master_cylinder','Harness_connector')):return 'plastic'
    if 'indicator_stalk' in n:return 'plastic'
    if 'Fork_top_cap' in n:return 'gold'
    if 'reflector' in n:return 'reflector'
    if 'caliper_reserve' in n:return 'caliper'
    if 'Headlamp_installation' in n:return 'lamp_lens'
    if 'DRL' in n:return 'lamp_white'
    if 'projector' in n:return 'chrome'
    if 'grip' in n or 'Peg_rubber' in n:return 'rubber'
    if 'belt' in n.lower():return 'belt'
    if 'Seat' in n:return 'seat'
    if 'inner_tube' in n or 'Shock_rod' in n:return 'chrome'
    if 'disc' in n and 'carrier' not in n:return 'disc'
    if 'pulley' in n:return 'anodised'    # rev E: dark anodised pulleys (they rendered as bright aluminium)
    if 'Peg_bracket' in n or 'Hand_lever' in n:return 'alu'
    if 'Headlamp' in n or 'Plate_lamp' in n:return 'lamp_white'
    if 'Taillamp' in n:return 'lamp_red'
    if 'indicator' in n:return 'lamp_amber'
    if 'Windscreen' in n:return 'glass'
    if 'Licence' in n:return 'plate'
    if 'wheel_' in n and 'STUDY' in n:return 'carbon' if 'carbon' in n.lower() else 'wheel'   # rev E: carbon wheels (Front_wheel_carbon_BST_STUDY)
    if n.startswith('Seam_trim'):return 'gloss'
    if 'Mirror_body' in n or 'Display' in n:return 'plastic'
    if 'Panel_bolts' in n:return 'bolt'
    if n.startswith(('Upper_body','Lower_body','Tail_side','Motor_side','Front_fender','Rear_hugger')):return 'paint'
    if n.startswith(('Tail_undertray','Pivot_cover_cap','Rear_indicator_stalk')):return 'plastic'
    if n.startswith(('Battery_side','Belly_side')):return 'paint_texture'
    return 'dark_metal'

out=R/'cad/render'
out.mkdir(exist_ok=True)
objf=(out/'bavuso.obj').open('w');mtl=set()
objf.write('mtllib bavuso.mtl\n')
base=1;count=0
for g in ('Energy','Electronics','Drive','Chassis','RunningGear','BodyStudy','Cooling','Protection','RiderStudy'):
    if D.getObject(g) is None:continue   # RiderStudy exists only in the *-rider model (tools/rider-figure.py)
    for o in D.getObject(g).Group:
        if o.Name.startswith(('Cell_column','Cell_lane')) or not hasattr(o,'Shape') or o.Shape.isNull():continue
        k=kind(o);mtl.add(k)
        # finer tessellation on curved, visible parts
        tol=0.2 if k in ('hose','mirror','paint','tyre','seat','chrome','wheel','glass','paint_texture','caliper','disc') else 0.5
        pts,tris=o.Shape.tessellate(tol)
        objf.write(f'o {o.Name}\nusemtl {k}\n')
        for p in pts:objf.write(f'v {p.x:.3f} {p.y:.3f} {p.z:.3f}\n')
        for a,b,c in tris:objf.write(f'f {a+base} {b+base} {c+base}\n')
        base+=len(pts);count+=1
objf.close()
(out/'bavuso.mtl').write_text(''.join(f'newmtl {k}\nKd 0.1 0.1 0.1\n' for k in sorted(mtl)))
print('exported',count,'parts,',base-1,'vertices ->',out/'bavuso.obj')
