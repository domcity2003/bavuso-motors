from pathlib import Path
import json
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[1]
D=A.openDocument(str(R/'cad/Bavuso-V1.0-rework.FCStd'))
out=R/'cad/step-diagnostics';out.mkdir(exist_ok=True)
rows=[]
for name in ['EMRAX_208_LC_supplier_STEP','Cascadia_CM200_supplier_STEP','Pack_case_3mm_STUDY','Cartridge_01_10s7p']:
    o=D.getObject(name)
    if o is None:continue
    path=out/(name+'.step');Part.export([o],str(path));s=Part.read(str(path))
    row=dict(id=name,native_volume=o.Shape.Volume,exchange_volume=s.Volume,
             delta=s.Volume-o.Shape.Volume,native_valid=o.Shape.isValid(),exchange_valid=s.isValid())
    rows.append(row);print(json.dumps(row),flush=True)
(out/'results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')

