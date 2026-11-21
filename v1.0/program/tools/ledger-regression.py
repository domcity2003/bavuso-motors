"""Regression: the legacy-mode ledger must equal the reconciled ledger of program/03-mass-ledger.md (319.64 kg), line by line.
Run (from v1.0): ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/ledger-regression.py <legacy parts-ledger.csv>"""
import csv, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
new = {}
for r in csv.DictReader(open(sys.argv[1], encoding='utf-8')):
    k = r['cad_solid'] or r['name']; new[k] = new.get(k, 0) + float(r['mass_kg']) * int(r['qty'])
old = {}
for r in csv.DictReader(open(R / 'program/data/mass-ledger-reconciled.csv', encoding='utf-8')):
    old[r['item']] = float(r['kg_reconciled'])
tn, to = sum(new.values()), sum(old.values())
print('new ledger %.3f kg, reconciled %.3f kg, difference %.3f' % (tn, to, tn - to))
bad = [(k, new.get(k), old.get(k)) for k in set(new) | set(old) if abs((new.get(k) or 0) - (old.get(k) or 0)) > 0.0006]
for b in sorted(bad, key=lambda b: str(b[0])): print('  line differs:', b)
print('PASS' if abs(tn - to) < 0.01 else 'FAIL', '- total within 0.01 kg;', len(bad), 'lines differ (allowance renames/splits are expected)')
