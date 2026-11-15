"""Bavuso V1.0 steady-turn steering torque from the linear model (dyn-model.py, dyn-stability.py parameters).

A steady turn at yaw rate r is the particular solution x(t) = x0 + x1 t + x2 t^2/2 of xdot = A x + b tau with
y(t) = c t + v r t^2/2, psi = r t and roll, steer, twist and tyre forces constant. Matching powers of t gives
x1 = A x0 + b tau (9 unknowns: roll, steer, twist, lateral drift c, four tyre states, tau). The t and t^2
terms vanish by yaw/translation invariance, which the script checks numerically.
Linear model: valid for moderate lean (results quoted at 0.3 g lateral, about 17 deg).

Run from v1.0 with the FreeCAD python. Output: detailed-design/dynamics/steer-torque.json
Prepared November 13, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; OUT = HERE.parents[0] / 'dynamics'
spec = importlib.util.spec_from_file_location('st', HERE / 'dyn-stability.py'); st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)


def steady(md, p, kmh, ay_g=0.3):
    v = kmh / 3.6; Fz = st.fz_at(p, kmh)
    A = md.state_matrix(v, Fz); n = md.n; N = A.shape[0]
    M = np.array(md.f['M'](v, *Fz), float)
    b = np.zeros(N); b[n:2 * n] = np.linalg.solve(M, np.eye(n)[md.names.index('delta')])
    r = ay_g * 9.81 / v
    iy, ips = 0, md.names.index('psi')
    # unknown vector u: x0 entries for phi, delta, (beta), qdot_y (= c), tyre states, and tau
    free = [md.names.index('phi'), md.names.index('delta')] + ([md.names.index('beta')] if 'beta' in md.names else [])
    free += [n + iy] + list(range(2 * n, N))
    x0_fixed = np.zeros(N); x0_fixed[n + ips] = r
    x1 = np.zeros(N); x1[ips] = r; x1[n + iy] = v * r     # y-acceleration
    # x1 = A x0 + b tau ; x1 also has x1[iy] = c (unknown) -> move to the left side
    Mat = np.zeros((N, len(free) + 1)); rhs = x1 - A @ x0_fixed
    for j, k in enumerate(free):
        Mat[:, j] = A[:, k]
    Mat[iy, free.index(n + iy)] -= 1.0      # row y: c = x0[n+iy]
    Mat[:, -1] = b
    u, *_ = np.linalg.lstsq(Mat, rhs, rcond=None)
    resid = np.linalg.norm(Mat @ u - rhs)
    x0 = x0_fixed.copy()
    for j, k in enumerate(free): x0[k] = u[j]
    x1c = x1.copy(); x1c[iy] = x0[n + iy]
    x2 = np.zeros(N); x2[iy] = v * r
    inv = np.linalg.norm(A @ x1c - x2) + np.linalg.norm(A @ x2)
    return dict(kmh=kmh, ay_g=ay_g, roll_deg=math.degrees(x0[md.names.index('phi')]),
                steer_deg=math.degrees(x0[md.names.index('delta')]), tau_Nm=u[-1],
                tau_into_turn_Nm=u[-1] * np.sign(r), residual=resid, invariance_error=inv,
                kinematic_steer_deg=math.degrees(p['wheelbase'] * r / v * math.cos(st.CASTER) ** -1))


if __name__ == '__main__':
    res = {}
    for load in ('solo', 'twoup'):
        p = st.params(load); md = st.dm.Model(p); p['c_steer'] = 0.0; md.p = p
        rows = [steady(md, p, k) for k in (30, 50, 70, 100, 130, 160)]
        res[load] = rows
        for r in rows:
            print(f"{load} {r['kmh']:4.0f} km/h 0.3 g: roll {r['roll_deg']:6.1f} deg, steer {r['steer_deg']:6.2f} deg "
                  f"(kinematic {r['kinematic_steer_deg']:.2f}), torque {r['tau_into_turn_Nm']:+6.2f} Nm  [resid {r['residual']:.1e}, inv {r['invariance_error']:.1e}]")
    (OUT / 'steer-torque.json').write_text(json.dumps(res, indent=1))
