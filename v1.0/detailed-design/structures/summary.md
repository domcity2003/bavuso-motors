Traceback (most recent call last):
  File "C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\detailed-design\tools\fea-summary.py", line 46, in <module>
    out[f.stem] = dict(worst=worst(res), stiffness=res.get('stiffness'), mass=res.get('member_mass_kg'), h=res['h'], n_nodes=res['n_nodes'])
                             ^^^^^^^^^^
  File "C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\detailed-design\tools\fea-summary.py", line 38, in worst
    pack_away=(pk[0], pk[1][0], round(FY['pack_seam'] / pk[1][0], 2)) if pk else None,
                                      ~~~~~~~~~~~~~~~~^~~~~~~~~~
ZeroDivisionError: float division by zero
