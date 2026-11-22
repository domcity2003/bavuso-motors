"""Range at a steady 70 mph for a given CdA, with the method and inputs of program/06-drive-performance.md.

Run from v1.0 (FreeCAD python):
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/aero-v1-range.py [CdA ...]
With no arguments it reads the CFD CdA from program/data/aero/aero-results.json.
Writes program/data/aero/range-70mph.json.
Method: the cruise_range() loop of program/tools/drive-range.py (copied here because that script writes its own
results file when imported), using program/tools/drive-lib.py unchanged: efficiency-map drivetrain, 23.76 kWh pack,
95 % to 5 % state of charge, 25 C pack, rho 1.225, Crr 0.015, 300 W auxiliaries, 240 kg bike + 90 kg rider.
"""
import importlib.util, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'aero')
sp = importlib.util.spec_from_file_location('drive_lib', os.path.join(HERE, 'drive-lib.py'))
dl = importlib.util.module_from_spec(sp); sp.loader.exec_module(dl)
drv = dl.Drive(126.0 / 35.0)
MPH = dl.MPH

def cruise_range(mph, cda, mass_extra=0.0, t_pack=25.0, t_wind=70.0, aux=dl.AUX_W):
    old_m = dl.M_TOT; dl.M_TOT = old_m + mass_extra
    try:
        v = mph * MPH; soc = dl.USABLE_SOC[1]; e_wheel = dist = 0.0; tot_loss = 0.0; dt = 20.0
        while soc > dl.USABLE_SOC[0]:
            pw = dl.road_force(v, cda) * v; bl = dl.belt_loss(pw); n = drv.rpm(v)
            T = (pw + bl) / (n * math.pi / 30.0)
            e = drv.electrical(T, n, soc, t_pack, t_wind, p_aux=aux)
            if e is None: break
            soc -= e['i_dc'] * dt / (dl.PACK_AH * 3600.0) * 100.0
            e_wheel += pw * dt; dist += v * dt
            tot_loss += (bl + e['cu'] + e['fe'] + e['p_inv'] + e['p_pack_loss'] + aux) * dt
        tot = e_wheel + tot_loss
        mi = dist / 1609.344
        return dict(mph=mph, cda=round(cda, 4), range_mi=round(mi, 1), wh_per_mi=round(tot / 3600.0 / mi, 1),
                    aero_share_of_wheel_power_pct=round(100 * 0.5 * dl.RHO * cda * v ** 3 / (dl.road_force(v, cda) * v), 1))
    finally:
        dl.M_TOT = old_m

if len(sys.argv) > 1:
    cdas = [float(a) for a in sys.argv[1:]]
else:
    R = json.load(open(os.path.join(OUT, 'aero-results.json')))
    cdas = [R['headline']['cda_m2']]
res = {'check_vs_06': cruise_range(70, 0.38), 'note_check': '06-drive-performance.md quotes 154 mi at CdA 0.38 and 140 mi at 0.43'}
res['at_cda'] = [cruise_range(70, c) for c in cdas]
res['sensitivity'] = {f'{c:.2f}': cruise_range(70, c)['range_mi'] for c in (0.33, 0.38, 0.43, 0.48)}
res['with_rev_E_mass_250.6kg'] = [cruise_range(70, c, mass_extra=10.57) for c in cdas]
res['inputs'] = dict(bike_kg=dl.BIKE_KG, rider_kg=dl.RIDER_KG, crr=dl.CRR, aux_W=dl.AUX_W, rho=dl.RHO, pack_kwh=dl.PACK_KWH,
                     usable_soc=dl.USABLE_SOC, source='program/tools/drive-lib.py + cruise_range of drive-range.py (unchanged)')
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, 'range-70mph.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
