from pathlib import Path
p = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'); s = p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("    'ALFORK':", "    'AL7075': dict(E=71000, nu=0.33, fy=480, fu=540, note='7075-T6 machined plate (yoke option)'),\n    'ALFORK':")
rep("RHO = {'A356'", "RHO = {'AL7075': 2.81e-6, 'A356'")
rep("boxs(*V['yoke_leg'], 'ST4130')", "boxs(*V['yoke_leg'], V['yoke_mat'])")
rep("boxs(*V['yoke_box'], 'ST4130')", "boxs(*V['yoke_box'], V['yoke_mat'])")
rep("zf_lug=532.0,", "yoke_mat='ST4130', zf_lug=532.0,")
p.write_text(s,encoding='utf-8')
