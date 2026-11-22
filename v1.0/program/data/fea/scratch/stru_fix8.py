from pathlib import Path
base = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools')
def patch(fn, pairs):
    p = base / fn; s = p.read_text(encoding='utf-8')
    for a, b in pairs:
        assert s.count(a) == 1, (fn, s.count(a), a[:60]); s = s.replace(a, b)
    p.write_text(s, encoding='utf-8')
patch('fea-swingarm-v1.py', [
 ("ap.add_argument('--rib', type=float, default=6.0,", "ap.add_argument('--patch_r', type=float, default=40.0, help='radius of the rigid patch where the brace is bolted to the inner wall (mm)')\nap.add_argument('--excl', type=float, default=0.0, help='exclusion radius around the brace attach for the stress read-out (0 = patch_r + 5)')\nap.add_argument('--rib', type=float, default=0.0,"),
 ("ap.add_argument('--dbl', type=float, default=2.0,", "ap.add_argument('--dbl', type=float, default=1.0,"),
 ("np.linalg.norm(nodes[n] - attach) <= 40.0]", "np.linalg.norm(nodes[n] - attach) <= args.patch_r]"),
 ("(np.linalg.norm(X - attach, axis=1) > 45.0)", "(np.linalg.norm(X - attach, axis=1) > (args.excl or args.patch_r + 5))"),
 ("abs(k - kc) <= 3 and", "abs(k - kc) <= 1 + int(args.patch_r // max(h, 1)) and"),
])
