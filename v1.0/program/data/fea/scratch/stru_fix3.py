p = r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools\fea-frame-v1.py'
s = open(p, encoding='utf-8').read()
a = "# ------------------------------------------------------------------ case 7 (pack retention) and case 8 (stiffness): frame without suspension"
assert s.count(a) == 1
s = s.replace(a, "if args.only == 'nopack':\n    OUT.mkdir(exist_ok=True); (OUT / ('results-%s.json' % tag)).write_text(json.dumps(results, indent=1)); raise SystemExit\n" + a)
open(p, 'w', encoding='utf-8').write(s)
