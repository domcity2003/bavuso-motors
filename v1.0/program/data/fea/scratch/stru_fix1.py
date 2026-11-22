p = r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('count', s.count(a), a[:70])
    s = s.replace(a, b)
rep("""        bi = node((540, V['piv_in'], PZ), merge=False); bo = node((540, V['piv_out'], PZ), merge=False)
        beam('BOSS', None, nodes[bi], circ(20, 'STRIG'), n=1, a_id=info['armpiv_R'], merge_b=False); beam('BOSS', None, nodes[bo], circ(20, 'STRIG'), n=1, a_id=info['armpiv_R'], merge_b=False)""",
"""        bi = beam('BOSS', None, (540, V['piv_in'], PZ), circ(20, 'STRIG'), n=1, a_id=info['armpiv_R'], merge_b=False)[-1]
        bo = beam('BOSS', None, (540, V['piv_out'], PZ), circ(20, 'STRIG'), n=1, a_id=info['armpiv_R'], merge_b=False)[-1]""")
rep("""            nr = node((Pr[0], -144.0, Pr[1]), merge=False); nm_ = node((Pm[0], -144.0, Pm[1]), merge=False)
            beam('BELTR' + nm, None, nodes[nr], circ(20, 'STRIG'), n=1, a_id=info['hub_pulley'], merge_b=False)
            beam('BELTM' + nm, None, nodes[nm_], circ(20, 'STRIG'), n=1, a_id=mc, merge_b=False)""",
"""            nr = beam('BELTR' + nm, None, (Pr[0], -144.0, Pr[1]), circ(20, 'STRIG'), n=1, a_id=info['hub_pulley'], merge_b=False)[-1]
            nm_ = beam('BELTM' + nm, None, (Pm[0], -144.0, Pm[1]), circ(20, 'STRIG'), n=1, a_id=mc, merge_b=False)[-1]""")
# C9a -> pivot slider
rep("('C9a_guard_21kN_upper_rail_node', info['ur0b_R'])", "('C9a_slider_21kN_pivot_node', info['pivnode_R'])")
rep("('C9b_guard_21kN_front_lug'", "('C9b_slider_21kN_front_lug'")
rep("('C9c_guard_21kN_rear_link_lug'", "('C9c_slider_21kN_rear_link_lug'")
open(p, 'w', encoding='utf-8').write(s)
