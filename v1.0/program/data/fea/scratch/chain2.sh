cd "C:/Users/DomBa/DOM/5_Projects/Bavuso Motors/v1.0/program/tools"
PY=../../../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe
$PY fea-frame-v1.py --h 12 --variant final > ../data/fea/scratch/f12.log 2>&1
$PY fea-fatigue-v1.py results-final-h12.json > ../data/fea/scratch/f12fat.log 2>&1
$PY fea-frame-v1.py --h 12 --variant final3 > ../data/fea/scratch/f3.log 2>&1
$PY fea-frame-v1.py --h 12 --variant final3f4 > ../data/fea/scratch/f3f4.log 2>&1
$PY fea-frame-v1.py --h 24 --variant final > ../data/fea/scratch/f24.log 2>&1
$PY fea-frame-v1.py --h 6 --variant final > ../data/fea/scratch/f6.log 2>&1
$PY fea-frame-v1.py --h 12 --variant final --bike_kg 0 --tag unscaled > ../data/fea/scratch/fun.log 2>&1
echo done > ../data/fea/scratch/chain2.done
