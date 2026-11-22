"""V1 dynamics step 6: gust stability and sidewind sensitivity at 77 mph, rev D.

Linear model of dynamics-v1-model.py (frame + fork + swingarm flex) with the recommended speed-scheduled steering damper from
dynamics-v1-damper.py. A lateral aerodynamic force F = 0.5 rho (V^2 + w^2) * (Cy_beta A) * atan(w / V) acts at a centre of pressure
(x_cp from the rear axle, z_cp above ground) on the rear frame. ASSUMED numbers (aero will refine them):
Cy_beta*A = 1.6 m2/rad (about 2.3 per rad on 0.7 m2 frontal area with rider), x_cp = 0.80 m, z_cp = 0.95 m.
  1) steady sidewind: lean angle, steer angle and the rider steering torque needed to hold a straight line;
  2) hands-off transient: side gust (ramp 0.3 s to w and hold, and a 1-cosine gust of 1.5 s): lateral position, roll, steer;
  3) sensitivity to Cy_beta*A, x_cp, z_cp and load case; eigenvalues at 77 mph.
Outputs: program/data/dynamics/gust-results.json, gust-response.png.
Run from v1.0 with the FreeCAD python (needs dynamics-v1-damper.py results). November 22, 2026, US Central.
Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import importlib.util, json, math
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_are
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stab', HERE / 'dynamics-v1-stability.py'); st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
OUT = st.OUT
RHO = 1.2; V_MPH = 77.0; V = V_MPH * st.MPH
CYA, XCP, ZCP = 1.6, 0.80, 0.95
DMP = json.loads((OUT / 'damper-results.json').read_text())
SCH = DMP['recommended']['schedule']
SCHED = st.sched(SCH['c_low'], SCH['c_high'], SCH['v1'], SCH['v2'])


def side_force(w, v=V, cya=CYA):
    return 0.5 * RHO * (v * v + w * w) * cya * math.atan2(w, v)


def system(case, v=V, xcp=XCP, zcp=ZCP, sched=SCHED):
    p = st.params(case, c_steer=sched)
    md = st.get_model(p, (case, True, True, True))
    Fz = st.fz_at(p, v * 3.6)
    A, bF = md.input_matrix(v, Fz, xcp, zcp)
    n = md.n; Minv = md._last['Minv']
    bT = np.zeros(A.shape[0]); bT[n:2 * n] = Minv[:, md.names.index('delta')]
    return md, p, A, bF, bT


def steady(md, A, bF, bT, F):
    """Straight-line steady state under side force F: y = 0, all velocities zero. Unknowns: other q, tyre states, rider steer torque."""
    n = md.n; N = A.shape[0]; nm = md.names
    qi = [i for i in range(n) if i != 0]
    unk = qi + list(range(2 * n, N))
    rows = list(range(n, N))
    M = np.hstack([A[np.ix_(rows, unk)], bT[rows].reshape(-1, 1)])
    sol = np.linalg.solve(M, -bF[rows] * F)
    q = {nm[i]: sol[k] for k, i in enumerate(qi)}
    return dict(roll_deg=math.degrees(q['phi']), steer_deg=math.degrees(q['delta']), heading_deg=math.degrees(q['psi']), torque_Nm=float(sol[-1]))


def simulate(A, bF, F_of_t, T=4.0, dt=0.002):
    N = A.shape[0]
    big = np.zeros((N + 1, N + 1)); big[:N, :N] = A; big[:N, N] = bF       # zero-order-hold step incl. the cyclic y coordinate (A is singular)
    E = expm(big * dt); Ad = E[:N, :N]; Bd = E[:N, N]
    x = np.zeros(N); ts = np.arange(0, T + dt / 2, dt); out = np.zeros((len(ts), N))
    for i, t in enumerate(ts):
        out[i] = x
        x = Ad @ x + Bd * F_of_t(t)
    return ts, out


def metrics_from(md, ts, X):
    nm = md.names; n = md.n
    y = X[:, 0]; psi = X[:, nm.index('psi')]; phi = X[:, nm.index('phi')]; dl = X[:, nm.index('delta')]
    yaw_rate = X[:, n + nm.index('psi')]
    idx = lambda t: int(round(t / (ts[1] - ts[0])))
    return dict(lat_dev_m={f'{t:g}s': float(y[idx(t)]) for t in (0.5, 1.0, 1.5, 2.0, 3.0)},
                heading_deg_at_1s=math.degrees(psi[idx(1.0)]), peak_roll_deg=math.degrees(np.max(np.abs(phi))),
                peak_steer_deg=math.degrees(np.max(np.abs(dl))), peak_yaw_rate_deg_s=math.degrees(np.max(np.abs(yaw_rate))),
                roll_deg_at_1s=math.degrees(phi[idx(1.0)]), roll_deg_at_2s=math.degrees(phi[idx(2.0)]))


def lqr_gain(md, A, bT, y_tol=0.3, psi_tol_deg=3.0, phi_tol_deg=8.0, tau_max=10.0):
    """An idealised rider: optimal steering-torque feedback (LQR) that keeps lateral position, heading and roll small. No delay, full state."""
    N = A.shape[0]; n = md.n; nm = md.names
    Q = np.zeros((N, N)); Q[0, 0] = 1 / y_tol ** 2; Q[nm.index('psi'), nm.index('psi')] = 1 / math.radians(psi_tol_deg) ** 2
    Q[nm.index('phi'), nm.index('phi')] = 1 / math.radians(phi_tol_deg) ** 2
    for i in range(N):
        Q[i, i] += 1e-6
    P = solve_continuous_are(A, bT.reshape(-1, 1), Q, np.array([[1 / tau_max ** 2]]))
    K = (bT.reshape(1, -1) @ P) * tau_max ** 2
    return K.ravel()


def simulate_rider(md, A, bF, bT, K, F_of_t, T=6.0, dt=0.002):
    Acl = A - np.outer(bT, K); N = A.shape[0]
    big = np.zeros((N + 1, N + 1)); big[:N, :N] = Acl; big[:N, N] = bF
    E = expm(big * dt); Ad = E[:N, :N]; Bd = E[:N, N]
    x = np.zeros(N); ts = np.arange(0, T + dt / 2, dt); out = np.zeros((len(ts), N)); tau = np.zeros(len(ts))
    for i, t in enumerate(ts):
        out[i] = x; tau[i] = -K @ x
        x = Ad @ x + Bd * F_of_t(t)
    return ts, out, tau, float(np.max(np.real(np.linalg.eigvals(Acl)[np.abs(np.linalg.eigvals(Acl)) > 1e-6])))


def ramp(F, tr=0.3):
    return lambda t: F * min(max(t / tr, 0.0), 1.0)


def onecos(F, T=1.5):
    return lambda t: F * 0.5 * (1 - math.cos(2 * math.pi * t / T)) if 0 <= t <= T else 0.0


if __name__ == '__main__':
    res = dict(inputs=dict(V_mph=V_MPH, rho=RHO, CyA_m2_per_rad=CYA, x_cp_m=XCP, z_cp_m=ZCP, schedule=SCH, c_steer_at_77_Nms_rad=float(SCHED(V)),
                           sign_note='roll + = lean toward -Y; wind from -Y blows toward +Y (positive F); lateral position + = toward +Y'))
    res['eig_77mph'] = {}
    for case in st.CASES:
        for lab, sch in (('no damper', 0.0), ('scheduled damper', SCHED)):
            p = st.params(case, c_steer=sch); md = st.get_model(p, (case, True, True, True))
            ms = st.modes_at(md, p, V_MPH)
            osc = sorted([m for m in ms if m['l'].imag > 1e-6 and abs(m['l'].imag) / 2 / math.pi < 100], key=lambda m: abs(m['l'].imag))
            res['eig_77mph'][f'{case}, {lab}'] = [dict(f_hz=m['l'].imag / 2 / math.pi, zeta=-m['l'].real / abs(m['l']), re=m['l'].real) for m in osc]
            print(case, lab, [(round(d['f_hz'], 2), round(d['zeta'], 3)) for d in res['eig_77mph'][f'{case}, {lab}']][:6])
    res['steady'] = {}
    for case in ('solo', 'solo_luggage'):
        md, p, A, bF, bT = system(case)
        res['steady'][case] = {}
        for w in (5.0, 10.0, 15.0):
            res['steady'][case][f'{w:g} m/s ({w/st.MPH:.0f} mph)'] = dict(F_N=side_force(w), **steady(md, A, bF, bT, side_force(w)))
        print(case, {k: (round(v['roll_deg'], 2), round(v['steer_deg'], 2), round(v['torque_Nm'], 2)) for k, v in res['steady'][case].items()})
    res['transient'] = {}
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    for case in ('solo', 'solo_luggage'):
        md, p, A, bF, bT = system(case)
        res['transient'][case] = {}
        for lab, f in (('ramp 8 m/s', ramp(side_force(8.0))), ('ramp 12 m/s', ramp(side_force(12.0))), ('1-cosine 10 m/s, 1.5 s', onecos(side_force(10.0)))):
            ts, X = simulate(A, bF, f)
            res['transient'][case][lab] = metrics_from(md, ts, X)
            m = res['transient'][case][lab]
            print(case, lab, 'dev@1s %.2f m, roll peak %.1f, steer peak %.1f, yaw rate %.1f' % (m['lat_dev_m']['1s'], m['peak_roll_deg'], m['peak_steer_deg'], m['peak_yaw_rate_deg_s']))
            if lab == 'ramp 12 m/s':
                nm = md.names
                ax[0].plot(ts, X[:, 0], label=case); ax[1].plot(ts, np.degrees(X[:, nm.index('phi')]), label=case); ax[2].plot(ts, np.degrees(X[:, nm.index('delta')]), label=case)
    for a, t in zip(ax, ('lateral position, m (hands off)', 'roll, deg', 'steer, deg')):
        a.set_title(f'{t}: 12 m/s (27 mph) gust at {V_MPH:g} mph'); a.set_xlabel('s'); a.grid(alpha=.3)
    ax[0].legend(); fig.tight_layout(); fig.savefig(OUT / 'gust-response.png', dpi=110)
    # idealised rider (LQR steering torque): what a competent rider has to do to stay in line
    res['rider_lqr'] = {}
    for case in ('solo', 'solo_luggage'):
        md, p, A, bF, bT = system(case)
        K = lqr_gain(md, A, bT)
        res['rider_lqr'][case] = {}
        for lab, w in (('ramp 8 m/s', 8.0), ('ramp 12 m/s', 12.0)):
            ts, X, tau, maxre = simulate_rider(md, A, bF, bT, K, ramp(side_force(w)))
            nm = md.names
            res['rider_lqr'][case][lab] = dict(peak_lat_dev_m=float(np.max(np.abs(X[:, 0]))), lat_dev_end_m=float(X[-1, 0]), peak_roll_deg=math.degrees(np.max(np.abs(X[:, nm.index('phi')]))),
                                                peak_steer_deg=math.degrees(np.max(np.abs(X[:, nm.index('delta')]))), peak_torque_Nm=float(np.max(np.abs(tau))),
                                                closed_loop_max_real_part=maxre)
            print('LQR rider', case, lab, {k: round(v, 2) for k, v in res['rider_lqr'][case][lab].items()})
    res['sensitivity'] = {}
    for case in ('solo', 'solo_luggage'):
        res['sensitivity'][case] = {}
        for lab, kw in (('base', {}), ('CyA 0.8', dict(cya=0.8)), ('CyA 2.4', dict(cya=2.4)), ('x_cp 0.60 m', dict(xcp=0.60)), ('x_cp 1.00 m', dict(xcp=1.00)),
                        ('z_cp 0.75 m', dict(zcp=0.75)), ('z_cp 1.10 m', dict(zcp=1.10))):
            kw = dict(kw); cya = kw.pop('cya', CYA)
            md, p, A, bF, bT = system(case, **kw)
            F = side_force(10.0, cya=cya)
            ts, X = simulate(A, bF, ramp(F))
            m = metrics_from(md, ts, X)
            ss = steady(md, A, bF, bT, F)
            res['sensitivity'][case][lab] = dict(F_N=F, lat_dev_1s_m=m['lat_dev_m']['1s'], roll_deg_at_1s=m['roll_deg_at_1s'], peak_steer_deg=m['peak_steer_deg'],
                                                 steady_roll_deg=ss['roll_deg'], steady_steer_deg=ss['steer_deg'], steady_torque_Nm=ss['torque_Nm'])
            print(case, lab, {k: round(v, 2) for k, v in res['sensitivity'][case][lab].items()})
    res['speed_sweep_10ms'] = {}
    for case in ('solo', 'solo_luggage'):
        res['speed_sweep_10ms'][case] = {}
        for mph in (40, 60, 77, 100, 125):
            v = mph * st.MPH
            md, p, A, bF, bT = system(case, v=v)
            F = side_force(10.0, v=v)
            res['speed_sweep_10ms'][case][str(mph)] = dict(F_N=F, **steady(md, A, bF, bT, F))
    (OUT / 'gust-results.json').write_text(json.dumps(res, indent=1, default=str))
