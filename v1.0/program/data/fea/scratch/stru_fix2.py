p = r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('count', s.count(a), a[:70])
    s = s.replace(a, b)
rep("    info['lugs'] = lugs\n", "    info['lugs'] = lugs\n    if V['yoke']:   # motor housing used as a load-bearing pivot yoke between the left carrier stub and the right pivot stub (belt loop closed through the motor)\n        beam('YOKE', None, nodes[info['pivot_R']], pipe(V['yoke'][0], V['yoke'][1], 'AL6082'), a_id=info['pivot_L'])\n")
rep("    arm_y=130.0,", "    yoke=None, arm_y=130.0,")
open(p, 'w', encoding='utf-8').write(s)
