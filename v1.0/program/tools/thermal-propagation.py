"""Bavuso V1 thermal: thermal-runaway propagation screen for the P60B 21700 pack (task 4).
Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/thermal-propagation.py
Writes program/data/thermal/propagation.json
Method reused from detailed-design/tools/thermal-propagation.py: a 9 x 9 patch of the side-view hex lattice, centre cell releases a retained share of its
runaway heat over 10 s, neighbours couple through gap filler (conduction + radiation if open), in-row busbar/bond path, and (new here) the ribbon's
in-band lateral path and its coolant sink when flowing. Hottest neighbour is compared with 120 C (self-heating onset, margin) and 170 C (trigger).
"""
import importlib.util, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'data', 'thermal')
sp = importlib.util.spec_from_file_location('tl', os.path.join(HERE, 'thermal-lib.py')); tl = importlib.util.module_from_spec(sp); sp.loader.exec_module(tl)

PITCH, D, LC = 0.0236, 0.0216, 0.0702
R = D / 2
S_SHAPE = 2 * math.pi * LC / math.acosh((PITCH ** 2 - 2 * R * R) / (2 * R * R))      # cylinder-cylinder conduction shape factor, m
A_FACE = 2 * math.pi * R * LC / 6
SIGMA = 5.67e-8
C_CELL = 75.0
T0 = 40.0                         # pack at 40 C when the cell fails (hot day)
GAP = 2.0e-3
CELL_WH = 21.6
G_COOL = 1.0 / tl.R_CW            # W/K per cell to flowing coolant (can -> ribbon -> coolant)
G_CASE = 0.05
G_RIB_LAT = 0.30                  # W/K between neighbours that share a ribbon (Al 1.2 mm serpentine, in series with two contact films) [est]
def k_eff(barrier_t, k_b, k_f=0.08):
    return GAP / (barrier_t / k_b + (GAP - barrier_t) / k_f) if barrier_t > 0 else k_f
FILLERS = {   # name: (k W/mK, opaque to radiation)
    'air gap, no filler': (0.04, False),
    'intumescent PU foam k0.08': (0.08, True),
    'foam + 0.5 mm aerogel sheet': (k_eff(0.5e-3, 0.02), True),
    'foam + 1.0 mm aerogel sheet': (k_eff(1.0e-3, 0.02), True),
    '2 mm aerogel, full gap (k0.025)': (0.025, True),
}
BUS = {'strip busbar (0.2 W/K)': 0.20, 'wire-bond fuse links (0.005 W/K)': 0.005}

def edges(N):
    E = []
    for i in range(N):
        for j in range(N):
            off = [(0, 1), (1, 0)] + ([(1, -1)] if i % 2 == 0 else [(1, 1)])   # hex neighbours counted once (rows are i)
            for a, b in off:
                if 0 <= i + a < N and 0 <= j + b < N: E.append(((i, j), (i + a, j + b)))
    return E
def run(filler, retained, wh_kj, bus, coolant, lat=G_RIB_LAT, N=9, t_end=1500.0, dt=0.25):
    k, opaque = FILLERS[filler]
    Q = CELL_WH * wh_kj * 1e3 * retained; t_rel = 10.0
    T = np.full((N, N), T0); c = N // 2
    E = edges(N); ia = np.array([e[0][0] * N + e[0][1] for e in E]); ib = np.array([e[1][0] * N + e[1][1] for e in E])
    g_cond = np.array([k * S_SHAPE + (bus if e[0][0] == e[1][0] else 0.0) +
                       (lat if (e[0][0] // 2 == e[1][0] // 2) else 0.0) for e in E])
    Tf = T.ravel().copy(); n = Tf.size
    t = 0.0; peak_nb = T0; peak_tr = T0
    nb = [i for i in range(n) if False]
    cc = c * N + c
    nbrs = [int(ib[m]) if ia[m] == cc else int(ia[m]) for m in range(len(E)) if ia[m] == cc or ib[m] == cc]
    while t < t_end:
        Tk = Tf + 273.15
        g = g_cond.copy()
        if not opaque:
            g = g + 0.8 * SIGMA * A_FACE * (Tk[ia] ** 2 + Tk[ib] ** 2) * (Tk[ia] + Tk[ib]) * 0.5
        flow = g * (Tf[ia] - Tf[ib])
        q = np.zeros(n); np.add.at(q, ia, -flow); np.add.at(q, ib, flow)
        rib = np.where(Tf < 300.0, G_COOL if coolant else 0.0, 0.0)
        q -= rib * (Tf - T0) + G_CASE * (Tf - T0)
        if t < t_rel: q[cc] += Q / t_rel
        Tf = Tf + q / C_CELL * dt; t += dt
        peak_tr = max(peak_tr, Tf[cc]); peak_nb = max(peak_nb, max(Tf[m] for m in nbrs))
        if t > 120 and max(Tf[m] for m in nbrs) < peak_nb - 5: break
    return round(peak_tr), round(peak_nb, 1)

out = []
cases = [(0.4, 4.5), (0.6, 4.5), (0.8, 7.0)]      # (retained fraction, kJ/Wh): central, high retained, worst credible
for filler in FILLERS:
    for bus_n, bus in BUS.items():
        for ret, kjwh in cases:
            for cool in (True, False):
                pt, pn = run(filler, ret, kjwh, bus, cool)
                v = 'PASS (<120)' if pn < 120 else ('MARGINAL (120-170)' if pn < 170 else 'PROPAGATES (>170)')
                r = dict(filler=filler, busbar=bus_n, retained=ret, kJ_per_Wh=kjwh, coolant_flowing=cool, trigger_peak_C=pt, hottest_neighbour_C=pn, verdict=v)
                out.append(r); print(r, flush=True)
# what carries the heat? ribbon in-band lateral path swept, foam + wire bonds, coolant OFF (crash / pump fault), 40 C start
lat_sweep = []
for lat in (0.30, 0.10, 0.03, 0.0):
    for ret, kjwh in cases:
        pt, pn = run('intumescent PU foam k0.08', ret, kjwh, 0.005, False, lat=lat)
        lat_sweep.append(dict(ribbon_lateral_W_per_K=lat, retained=ret, kJ_per_Wh=kjwh, hottest_neighbour_C=pn))
        print('lat', lat_sweep[-1], flush=True)
hand = {f'ret {f}/{kj} kJ/Wh': round(T0 + CELL_WH * kj * 1e3 * f / 6 / C_CELL) for f, kj in cases}
# vent sizing
gas_stp_l = 1.5 * tl.CELL_AH                       # L at STP per cell [est: 1.5 L/Ah]
gas_hot_l = gas_stp_l * (273 + 450) / 273          # at ~450 C vent temperature
dp, rho_hot, cd, t_vent = 20e3, 0.45, 0.6, 3.0     # Pa case overpressure limit, kg/m3 hot gas, discharge coefficient, vent time s
v_j = math.sqrt(2 * dp / rho_hot)
a_cell = gas_hot_l / 1000 / t_vent / (cd * v_j) * 1e6
vent = dict(gas_stp_L_per_cell=gas_stp_l, gas_hot_L_per_cell=round(gas_hot_l, 1), jet_velocity_ms=round(v_j), vent_area_mm2_one_cell=round(a_cell, 1),
            vent_area_mm2_one_group_of_11=round(a_cell * 11, 0), vent_area_mm2_one_lane_275=round(a_cell * 275, 0))
json.dump(dict(runs=out, ribbon_lateral_sweep=lat_sweep, hand_adiabatic_bound_C=hand, shape_factor_m=S_SHAPE, G_cool_W_per_K=G_COOL, vent=vent), open(os.path.join(OUT, 'propagation.json'), 'w'), indent=1)
print('hand bound', hand); print(vent)
