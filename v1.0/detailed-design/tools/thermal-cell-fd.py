"""Thermal study: 2-D (r,z) finite-difference check of the 26120 cell's internal thermal resistance.

Uniform heat generation in an anisotropic jelly roll (k_r across layers, k_a along layers), can and both end
caps held at one temperature (aluminium can, tabless caps). Gives mean-core-to-can and peak-to-can resistance,
with a mesh-convergence check and the two 1-D hand calculations as bounds.
Run: "../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe" detailed-design/tools/thermal-cell-fd.py
"""
import json, math, pathlib
import numpy as np
# scipy.linalg DLLs are blocked by this machine's application-control policy, so numpy's dense solver is used.

R_ROLL, L_ROLL = 0.0125, 0.116      # m: 26 mm can minus 0.5 mm wall; 120 mm minus caps/headspace

def solve(kr, ka, nr, nz, P=1.0):
    dr, dz = R_ROLL / nr, L_ROLL / nz
    rc = (np.arange(nr) + 0.5) * dr
    vol = 2 * math.pi * rc * dr * dz           # ring volumes
    q = P / (math.pi * R_ROLL ** 2 * L_ROLL)
    N = nr * nz; A = np.zeros((N, N)); b = np.zeros(N)
    idx = lambda i, j: i * nz + j
    for i in range(nr):
        for j in range(nz):
            k = idx(i, j); b[k] = q * vol[i]
            # radial faces
            if i > 0:
                g = kr * 2 * math.pi * (rc[i] - dr / 2) * dz / dr; A[k, k] += g; A[k, idx(i - 1, j)] -= g
            if i < nr - 1:
                g = kr * 2 * math.pi * (rc[i] + dr / 2) * dz / dr; A[k, k] += g; A[k, idx(i + 1, j)] -= g
            else:
                g = kr * 2 * math.pi * R_ROLL * dz / (dr / 2); A[k, k] += g      # to can at T=0
            for jj in (j - 1, j + 1):
                area = 2 * math.pi * rc[i] * dr
                if 0 <= jj < nz:
                    g = ka * area / dz; A[k, k] += g; A[k, idx(i, jj)] -= g
                else:
                    g = ka * area / (dz / 2); A[k, k] += g                      # to cap at T=0
    T = np.linalg.solve(A, b).reshape(nr, nz)
    Tmean = float(np.sum(T * vol[:, None]) / np.sum(vol) / nz)
    return Tmean, float(T.max())

out = {}
for kr in (0.2, 0.6, 1.0):
    ka = 25.0
    res = [solve(kr, ka, nr, nz) for nr, nz in ((8, 16), (16, 32), (32, 64))]
    radial_only = 1 / (8 * math.pi * kr * L_ROLL)
    axial_only = L_ROLL / (12 * ka * math.pi * R_ROLL ** 2)
    out[f'kr={kr}'] = dict(R_mean_K_per_W=[round(r[0], 4) for r in res], R_peak_K_per_W=[round(r[1], 4) for r in res],
                           peak_over_mean=round(res[-1][1] / res[-1][0], 3),
                           convergence_pct=round(100 * abs(res[-1][0] - res[-2][0]) / res[-1][0], 2),
                           hand_radial_only=round(radial_only, 4), hand_axial_only=round(axial_only, 4),
                           hand_parallel=round(1 / (1 / radial_only + 1 / axial_only), 4))
    print(kr, out[f'kr={kr}'])
p = pathlib.Path(__file__).resolve().parents[1] / 'thermal' / 'cell-fd.json'
p.write_text(json.dumps(out, indent=1)); print('wrote', p)
