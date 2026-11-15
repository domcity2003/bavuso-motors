"""Thermal study: cell-to-cell thermal-runaway propagation screen for the 26120 hex pack.

A 9 x 9 patch of the side-view hex lattice (28 mm pitch, 2 mm gaps). The centre cell goes into runaway: its
retained heat (a fraction of the cell's runaway heat; the rest leaves with the vented ejecta) is released over
10 s. Every cell couples to its six neighbours through the gap (filler conduction + radiation) and, if the ribbon
bond survives and coolant flows, to the coolant. Reports the hottest neighbour against a 120 degC self-heating
onset (no-propagation criterion with margin) and 170 degC (runaway trigger).
Run: "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-propagation.py
"""
import json, math, pathlib
import numpy as np

C_CELL = 180.0              # J/K
T0 = 35.0
D, R, Lc = 0.028, 0.013, 0.120
S_SHAPE = 2 * math.pi * Lc / math.acosh((D * D - 2 * R * R) / (2 * R * R))   # m, cylinder-cylinder conduction shape factor
A_FACE = 2 * math.pi * R * Lc / 6                                             # m2 of can facing one neighbour
SIGMA = 5.67e-8
# Runaway heat: NMC cylinder calorimetry spans a few kJ per Wh of capacity (Feng et al.,
# Energy Storage Materials 10, 2018). 55 Wh x 4.5 kJ/Wh = 248 kJ total; 40-60 % is carried off by
# vented gas and ejecta (Golubkov 2014). Retained fraction is swept.
Q_TOTAL = 55 * 4.5e3     # J; chosen so the trigger cell peaks ~600-850 degC as measured for NMC cylinders

FILLERS = {   # gap filler: conductivity W/mK, blocks radiation?
    'air gap (no filler)': (0.04, False),
    'silicone potting k0.2': (0.20, True),
    'intumescent PU foam k0.08': (0.08, True),
    'aerogel/mica sleeve k0.025': (0.025, True),
}

G_BUS = 0.20   # W/K, Cu busbar strip 1.5x10 mm over 28 mm between in-row cells (parallel group)

def run(filler, retained, ribbon_ok, N=9, t_end=1500.0, dt=0.25):
    k, opaque = FILLERS[filler]
    T = np.full((N, N), T0); c = N // 2
    Qr = Q_TOTAL * retained; t_rel = 10.0
    G_rib = 2.9 if ribbon_ok else 0.0         # W/K per cell to coolant (1/(R_TIM+R_RIB)); bond assumed lost >300 degC
    G_case = 0.05
    def nbrs(i, j):
        off = [(0, -1), (0, 1), (-1, 0), (1, 0)] + ([(-1, -1), (1, -1)] if i % 2 == 0 else [(-1, 1), (1, 1)])
        return [(i + a, j + b) for a, b in off if 0 <= i + a < N and 0 <= j + b < N]
    peak_nb = T0; t = 0.0; peak_trig = T0
    nb_c = nbrs(c, c)
    while t < t_end:
        Tk = T + 273.15; dT = np.zeros_like(T)
        for i in range(N):
            for j in range(N):
                q = 0.0
                for a, b in nbrs(i, j):
                    g = k * S_SHAPE + (G_BUS if a == i else 0.0)     # same row = same parallel group busbar
                    if not opaque:
                        g += 0.8 * SIGMA * A_FACE * (Tk[i, j] ** 2 + Tk[a, b] ** 2) * (Tk[i, j] + Tk[a, b]) * 0.5
                    q -= g * (T[i, j] - T[a, b])
                rib = G_rib if T[i, j] < 300 else 0.0
                q -= rib * (T[i, j] - T0) + G_case * (T[i, j] - T0)
                if (i, j) == (c, c) and t < t_rel: q += Qr / t_rel
                dT[i, j] = q / C_CELL
        T += dT * dt; t += dt
        peak_trig = max(peak_trig, T[c, c]); peak_nb = max(peak_nb, max(T[a, b] for a, b in nb_c))
        if t > 120 and max(T[a, b] for a, b in nb_c) < peak_nb - 5: break
    return round(peak_trig, 0), round(peak_nb, 1)

out = []
for filler in FILLERS:
    for retained in (0.4, 0.6):  # fraction of the runaway heat that stays in the trigger cell
        for rib in (True, False):
            pt, pn = run(filler, retained, rib)
            r = dict(filler=filler, retained_fraction=retained, ribbon_cooling=rib, trigger_peak_C=pt,
                     hottest_neighbour_C=pn, verdict='PASS (<120)' if pn < 120 else ('MARGINAL (120-170)' if pn < 170 else 'PROPAGATES (>170)'))
            out.append(r); print(r, flush=True)
# hand check: adiabatic share - trigger heat split evenly over 6 neighbours, no other loss
hand = {f'retained {f}': round(T0 + Q_TOTAL * f / 6 / C_CELL, 0) for f in (0.4, 0.6)}
print('hand adiabatic neighbour bound (trigger heat shared by 6 neighbours, nothing else):', hand)
p = pathlib.Path(__file__).resolve().parents[1] / 'thermal' / 'propagation.json'
p.write_text(json.dumps(dict(runs=out, hand_adiabatic_bound_C=hand, shape_factor_m=S_SHAPE), indent=1)); print('wrote', p)
