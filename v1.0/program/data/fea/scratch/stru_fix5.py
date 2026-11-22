p = r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-size-v1.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, ('count', s.count(a), a[:70])
    s = s.replace(a, b)
rep("ap.add_argument('--arm_t'", "ap.add_argument('--skip', default='', help='comma list of case-name prefixes ignored for strength ratios (sensitivity)')\nap.add_argument('--tmax', type=float, default=0.13, help='max wall / OD before the OD grows by 2 mm (999 = never)')\nap.add_argument('--arm_t'")
rep("FIX = set(args.fix.split(',')) if args.fix else set()", "FIX = set(args.fix.split(',')) if args.fix else set()\nSKIP = tuple(args.skip.split(',')) if args.skip else ()")
rep("    for c, d in R['cases'].items():\n        for m, v in d['stress'].items():", "    for c, d in R['cases'].items():\n        if SKIP and c.startswith(SKIP): continue\n        for m, v in d['stress'].items():")
s = s.replace("0.13 * 2 * ro", "args.tmax * 2 * ro")
open(p, 'w', encoding='utf-8').write(s)
