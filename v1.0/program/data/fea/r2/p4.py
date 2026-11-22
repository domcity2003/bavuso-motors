from pathlib import Path
p = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-size-v1.py'); s = p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("('STUB', 'stub'),", "('STUB', 'stub'), ('YKL', 'yoke_leg'), ('PX', 'yoke_box'),")
rep("    if 'tailx_box' in grp and 'tailx_box' not in FIX:", """    for nm in ('yoke_leg', 'yoke_box'):
        if nm in grp and nm not in FIX and not 0.92 <= grp[nm][0] <= 1.0:
            a, b, t = newV[nm]; f = min(1.3, max(0.8, grp[nm][0] ** 0.9)); tn = max(3.0, quant(t * f))
            if tn > 8: a += 6; tn = 6.0
            newV[nm] = [a, b, tn]
    if 'tailx_box' in grp and 'tailx_box' not in FIX:""")
rep("'tailx_box', 'topbr', 'stub',", "'tailx_box', 'topbr', 'stub', 'yoke_leg', 'yoke_box',")
p.write_text(s,encoding='utf-8')
