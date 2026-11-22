#!/bin/sh
# Bavuso V1 rev E aero study: run cases one after another (Git Bash, from anywhere):
#   sh program/tools/aero-v1-run.sh [case ...]        default: m1 m2 yaw+10 yaw-10 m3 m4
# Needs program/data/aero/run/geometry (run aero-v1-export.py first). A case with a DONE marker is skipped.
# Mesh family: base cell 0.500 / 0.370 / 0.274 / 0.203 m (ratio 1.35 each), all refinement levels relative to the base.
# 4 MPI ranks only (the machine is shared). Large output stays in program/data/aero/run (git-ignored).
V10="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$V10"
PY=../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe
CASES="${*:-m1 m2 yaw+10 yaw-10 m3 m4}"
[ -f program/data/aero/run/geometry/screen.stl ] || $PY program/tools/aero-v1-export.py
for c in $CASES; do
  case $c in
    m1)      args="--base 0.500 --iters 500";;
    m2)      args="--base 0.370 --iters 500";;
    m3)      args="--base 0.274 --iters 500";;
    m4)      args="--base 0.203 --iters 450";;
    yaw+10)  args="--base 0.370 --iters 500 --yaw 10";;
    yaw-10)  args="--base 0.370 --iters 500 --yaw -10";;
    m2-blocked) args="--base 0.370 --iters 500 --rad blocked";;
    *) echo "unknown case $c"; exit 1;;
  esac
  d=program/data/aero/run/$c
  [ -f "$d/DONE" ] && { echo "$c done, skipped"; continue; }
  $PY program/tools/aero-v1-make-case.py $c $args
  chmod +x "$d/Allrun"
  echo "$(date) start $c"
  ../.tools/ofrun.sh "$d" ./Allrun > "$d/allrun.out" 2>&1
  echo "$(date) end $c"
done
