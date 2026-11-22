cd "C:/Users/DomBa/DOM/5_Projects/Bavuso Motors/v1.0/program/tools"
PY=../../../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe
S=../data/fea/startB.json
$PY fea-size-v1.py --start $S --name scBase --iters 7 --arm_t 4.0 --tmax 0.20 > ../data/fea/scratch/scBase.log 2>&1
$PY fea-size-v1.py --start $S --name scOD --iters 7 --arm_t 4.0 --tmax 0.10 > ../data/fea/scratch/scOD.log 2>&1
$PY fea-size-v1.py --start ../data/fea/startC.json --name scCast63 --iters 7 --arm_t 4.0 --tmax 0.13 > ../data/fea/scratch/scCast63.log 2>&1
$PY fea-size-v1.py --start $S --name scNoC9 --iters 7 --arm_t 4.0 --tmax 0.13 --skip C9 > ../data/fea/scratch/scNoC9.log 2>&1
