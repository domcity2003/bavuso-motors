from pathlib import Path
base = Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools')
def patch(fn, pairs):
    p = base / fn; s = p.read_text(encoding='utf-8')
    for a, b in pairs:
        assert s.count(a) == 1, (fn, s.count(a), a[:60]); s = s.replace(a, b)
    p.write_text(s, encoding='utf-8')
patch('fea-swingarm-v1.py', [
# args
 ("ap.add_argument('--set', default='')", "ap.add_argument('--set', default='')\nap.add_argument('--rib', type=float, default=6.0, help='internal rib plate thickness at the brace station (0 = none)')\nap.add_argument('--dbl', type=float, default=2.0, help='wall thickness multiple over +-2 stations around the brace (1 = none)')"),
# box elements -> BOXD near the brace (needs kc, known after mesh; mark later)
 ("        elems.append(('BOX', [ID[(k, i1, j1)], ID[(k, i2, j2)], ID[(k + 1, i2, j2)], ID[(k + 1, i1, j1)]]))",
  "        elems.append(('BOX%d' % k, [ID[(k, i1, j1)], ID[(k, i2, j2)], ID[(k + 1, i2, j2)], ID[(k + 1, i1, j1)]]))"),
# after kc is known: rename elements, make rib
 ("nid_rot = nid(attach)\nnodes[nid_rot] = attach.copy()",
  """nid_rot = nid(attach)
nodes[nid_rot] = attach.copy()
elems = [(('BOXD' if (e[0].startswith('BOX') and abs(int(e[0][3:]) - kc) <= 2 and args.dbl > 1) else 'BOX') if e[0].startswith('BOX') else e[0], e[1]) for e in elems]
if args.rib > 0:
    for i in range(1, nW):
        for j in range(1, nH): ID[('rib', i, j)] = nid(ptat(sgrid[kc], i, j))
    gid = lambda i, j: ID[('rib', i, j)] if ('rib', i, j) in ID else ID[(kc, i, j)]
    for i in range(nW):
        for j in range(nH): elems.append(('RIB', [gid(i, j), gid(i + 1, j), gid(i + 1, j + 1), gid(i, j + 1)]))"""),
 ("    for es in ('BOX', 'CAP'):\n        Ls.append('*ELEMENT,TYPE=S4,ELSET=%s' % es)\n        Ls += ['%d,%s' % (i + 1, ','.join(map(str, e[1]))) for i, e in enumerate(elems) if e[0] == es]",
  "    for es in ('BOX', 'BOXD', 'CAP', 'RIB'):\n        if not any(e[0] == es for e in elems): continue\n        Ls.append('*ELEMENT,TYPE=S4,ELSET=%s' % es)\n        Ls += ['%d,%s' % (i + 1, ','.join(map(str, e[1]))) for i, e in enumerate(elems) if e[0] == es]"),
 ("    Ls += ['*SHELL SECTION,ELSET=BOX,MATERIAL=ARM', '%g' % tw, '*SHELL SECTION,ELSET=CAP,MATERIAL=ARM', '%g' % T_CAP]",
  "    Ls += ['*SHELL SECTION,ELSET=BOX,MATERIAL=ARM', '%g' % tw, '*SHELL SECTION,ELSET=CAP,MATERIAL=ARM', '%g' % T_CAP]\n    if any(e[0] == 'BOXD' for e in elems): Ls += ['*SHELL SECTION,ELSET=BOXD,MATERIAL=ARM', '%g' % (tw * args.dbl)]\n    if any(e[0] == 'RIB' for e in elems): Ls += ['*SHELL SECTION,ELSET=RIB,MATERIAL=ARM', '%g' % args.rib]"),
# bearing forces by statics
 ("    Rf = ds['RF'][pref]; Mrf = ds['RF'][prot]\n    Fin = np.array([Mrf[2] / Dpiv, 0.0, -Mrf[0] / Dpiv]); Fout = Rf - Fin",
  "    Fa, Ma = axle_interface(name); Fsh = info[name]['shock_N'] * ES; Rtot = -(Fa + Fsh); refp = np.array([540.0, Yout, PZ])\n    Mtot = Ma + np.cross(A0 - refp, Fa) + np.cross(EYE - refp, Fsh); MR = -Mtot; Mrf = MR\n    Fin = np.array([MR[2] / Dpiv, 0.0, -MR[0] / Dpiv]); Fout = Rtot - Fin"),
 ("yaw_residual_Nmm=round(float(Mrf[1]), 0))", "yaw_residual_Nmm=round(float(Mrf[1]), 0))"),
])
print('ok')
