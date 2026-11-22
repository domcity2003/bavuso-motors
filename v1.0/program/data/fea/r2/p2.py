from pathlib import Path
p = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'); s = p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("zf = 470.0; xf = pack_x_at(zf, True); lf = (xf + 22, 178 * s, zf); FYL = 144.7", "zf = V['zf_lug']; xf = pack_x_at(zf, True); FYL = 144.7; lf = (xf + 22, FYL * s, zf)")
rep("    yoke=None,", "    zf_lug=532.0, yoke_box=None, piv_blk=(40, 60), yoke=None,")
rep("rect(40, 60, 'ST4130'))\n            ys_", "rect(*V['piv_blk'], 'ST4130'))\n            ys_")
rep("ids_ = beam('PIV', piv, (540, -189.0, PZ), rect(40, 60, 'ST4130'))", "ids_ = beam('PIV', piv, (540, -189.0, PZ), rect(*V['piv_blk'], 'ST4130'))")
rep("beam('PX', info['pc_L'], info['pc_R'], pipe(V['pivot_cross'][2], V['pivot_cross'][3], 'ST4130'))", "beam('PX', info['pc_L'], info['pc_R'], boxs(*V['yoke_box'], 'ST4130') if V['yoke_box'] else pipe(V['pivot_cross'][2], V['pivot_cross'][3], 'ST4130'))")
p.write_text(s, encoding='utf-8')
