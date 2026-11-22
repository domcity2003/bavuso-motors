p = r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('count', s.count(a), a[:70])
    s = s.replace(a, b)
rep("    for name, n_ in [('C9a_slider_21kN_pivot_node', info['pivnode_R']), ('C9b_slider_21kN_front_lug'", "    for name, n_ in [('C9b_slider_21kN_front_lug'")
rep("if c7:\n    # screening crush", "if c7 and args.only != 'sizing':\n    # screening crush")
rep("c7 = {} if args.only in ('stiff', 'nopack') else", "c7 = {} if args.only in ('stiff', 'nopack') else")
rep("# stiffness: pivot stubs fixed at the bearing points", "if args.only == 'sizing':\n    OUT.mkdir(exist_ok=True); (OUT / ('results-%s.json' % tag)).write_text(json.dumps(results, indent=1)); raise SystemExit\n# stiffness: pivot stubs fixed at the bearing points")
open(p, 'w', encoding='utf-8').write(s)
