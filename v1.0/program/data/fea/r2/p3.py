from pathlib import Path
p = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'); s = p.read_text(encoding='utf-8')
a="            chain('UR0' + S, [piv, pc, p715, ur0b] if zn != GE['tj_z'] else [piv, pc, ur0b], rail)\n"
b="""            if V['yoke_leg']:
                chain('YKL' + S, [piv, pc], boxs(*V['yoke_leg'], 'ST4130'))
                chain('UR0' + S, [pc, p715, ur0b], pipe(*V['rail0'], 'ST4130'))
            else:
                chain('UR0' + S, [piv, pc, p715, ur0b] if zn != GE['tj_z'] else [piv, pc, ur0b], rail)
"""
assert s.count(a)==1; s=s.replace(a,b)
s=s.replace("zf_lug=532.0, yoke_box=None,","zf_lug=532.0, yoke_leg=None, yoke_box=None,")
p.write_text(s,encoding='utf-8')
