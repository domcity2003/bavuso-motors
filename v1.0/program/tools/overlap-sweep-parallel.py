"""Broad interference sweep on the saved CAD model, run in parallel (rev E).
The sweep inside tools/build-adventure.py is serial and took many hours on the rev E shapes, so the final build runs with BAVUSO_NOSWEEP=1 and this
script does the same job on cad/Bavuso-V1.0-adventure.FCStd: every pair of visible parts (cells and keepouts excluded) with at least one part in
BodyStudy / Electronics / Energy / Cooling / Protection, bounding boxes touching, distance 0, then summed solid-by-solid common volume > 1 mm3.
Same intended-joint exclusions as the generator. Run (from v1.0):
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/overlap-sweep-parallel.py [workers] [out.csv]
"""
import sys, os, time, csv, itertools, multiprocessing as mp
from pathlib import Path
R = Path(__file__).resolve().parents[2]
FILE = str(R / 'cad/Bavuso-V1.0-adventure.FCStd')
G = {'BodyStudy', 'Electronics', 'Energy', 'Cooling', 'Protection'}

def skip(na, nb):
    s = na + nb
    if 'Mirror_stalk' in s and any(k in s for k in ('Mirror_body', 'Hand_grip', 'Bar_half')): return True
    if 'Mirror_glass' in s and 'Mirror_body' in s: return True
    if 'Seat_welt' in s and 'Seat_two_level' in s: return True
    if 'Seam_trim' in s: return True   # flush inserts in their panels
    if 'Crash_guard_mount' in s and any(k in s for k in ('Crash_guard_', 'Upper_rail', 'Lower_pack_rear_link', 'Lower_downlink', 'Upper_body', 'Lower_body',
            'Battery_side_panel', 'Motor_side_covers', 'Battery_installation_keepout', 'Pack_case')): return True
    if 'Handguard' in s and 'Bar_half' in s: return True
    return False

D = None; SW = None
def init():
    global D, SW
    import FreeCAD as A
    D = A.openDocument(FILE)
    SW = {o.Name: (o.InList[0].Name, o.Shape) for o in D.Objects if o.TypeId == 'Part::Feature' and o.InList and o.InList[0].Name != 'Keepouts' and not o.Name.startswith('Cell_lane')}

def work(pair):
    na, nb = pair
    (ga, sa), (gb, sb) = SW[na], SW[nb]
    t = time.time()
    if sa.distToShape(sb)[0] > 1e-6: return (na, nb, None, time.time() - t)
    v = sum(x.common(y).Volume for x in sa.Solids for y in sb.Solids if x.BoundBox.intersect(y.BoundBox))
    return (na, nb, v, time.time() - t)

if __name__ == '__main__':
    nw = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    out = sys.argv[2] if len(sys.argv) > 2 else str(R / 'program/data/run/overlap-sweep-revE.csv')
    init()
    names = list(SW)
    pairs = []
    for na, nb in itertools.combinations(names, 2):
        ga, sa = SW[na]; gb, sb = SW[nb]
        if not ({ga, gb} & G) or skip(na, nb): continue
        if sa.BoundBox.intersect(sb.BoundBox): pairs.append((na, nb))
    print(len(names), 'parts', len(pairs), 'pairs with touching boxes', flush=True)
    t0 = time.time(); rows = []; n = 0
    with mp.Pool(nw, initializer=init) as pool:
        for na, nb, v, dt in pool.imap_unordered(work, pairs, chunksize=1):
            n += 1
            if v is not None and v > 1.0:
                rows.append((na, nb, round(v, 1))); print('OVERLAP', na, nb, round(v), flush=True)
            if n % 200 == 0: print(f'{n}/{len(pairs)} pairs, {time.time()-t0:.0f}s', flush=True)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['a', 'b', 'overlap_mm3']); w.writerows(sorted(rows))
    print('done', len(rows), 'overlaps in', round(time.time() - t0), 's ->', out, flush=True)
