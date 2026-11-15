#!/bin/sh
# Bavuso V1.0 aero study: the whole pipeline in one command (Git Bash, from anywhere):
#   sh "detailed-design/tools/aero-run-all.sh" [case ...]
# Default cases: m1-coarse m2-medium m3-fine yaw+10 yaw-10   (about 10 h on 4 ranks)
# Steps: export the current CAD + rider to STL -> write each case -> mesh + solve (4 MPI ranks) -> aero-report.py.
# A case that already has a DONE marker is skipped; delete detailed-design/aero/run/<case> to re-run it.
# Re-running after the body changes: delete detailed-design/aero/run/ first, so every case is rebuilt.
set -e
V10="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$V10"
PY=../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe
CASES="${*:-m1-coarse m2-medium m3-fine yaw+10 yaw-10}"
[ -f detailed-design/aero/run/geometry/screen.stl ] || $PY detailed-design/tools/aero-export-geometry.py
for c in $CASES; do
  case $c in
    m1-coarse) args="--base 0.5   --iters 600";;
    m2-medium) args="--base 0.354 --iters 600";;
    m3-fine)   args="--base 0.25  --iters 450";;   # drag settles by ~250; 450 used in the Nov 14 study
    yaw+10)    args="--base 0.354 --iters 600 --yaw 10";;   # yaw on the mesh the convergence study picked (medium)
    yaw-10)    args="--base 0.354 --iters 600 --yaw -10";;
    *) echo "unknown case $c"; exit 1;;
  esac
  d=detailed-design/aero/run/$c
  [ -f $d/DONE ] && { echo "$c done, skipped"; continue; }
  $PY detailed-design/tools/aero-make-case.py $c $args
  chmod +x $d/Allrun
  echo "$(date) start $c"
  ../.tools/ofrun.sh $d ./Allrun > $d/allrun.out 2>&1
  echo "$(date) end $c"
done
$PY detailed-design/tools/aero-report.py
