"""Validate dynamics-v1-model.py against the Meijaard et al. (2007) benchmark bicycle.

Meijaard, Papadopoulos, Ruina & Schwab, "Linearized dynamics equations for the balance and steer of a
bicycle: a benchmark and review", Proc. R. Soc. A 463:1955-1982 (2007), doi:10.1098/rspa.2007.1857.
Published results: weave speed v_w = 4.292382536 m/s, capsize speed v_c = 6.024262015 m/s, and the
reference matrices M0, C1, K0, K2 (Table 1 / eq. A.  ). The benchmark has knife-edge wheels that cannot
slip; our model has tyres. With crown radius 0, no camber stiffness and a very stiff, lag-free slip
stiffness the tyres become a penalty version of the no-slip constraint, so the slow eigenvalues must
converge to the benchmark. That checks the rigid-body part (inertia, gyroscopic, geometry and gravity terms).

Run from v1.0 with the FreeCAD python. November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import importlib.util, json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dynmodel', HERE / 'dynamics-v1-model.py'); dm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
OUT = HERE.parent / 'data' / 'dynamics'

# Benchmark reference matrices (Meijaard 2007, Table 2 / eq. 3.x), for the direct 4-state check.
M0 = np.array([[80.81722, 2.31941332208709], [2.31941332208709, 0.29784188199686]])
C1 = np.array([[0, 33.86641391492494], [-0.85035641456978, 1.68540397397560]])
K0 = np.array([[-80.95, -2.59951685249872], [-2.59951685249872, -0.80329488458618]])
K2 = np.array([[0, 76.59734589573222], [0, 2.65431523794604]])
VW, VC = 4.292382536, 6.024262015


def bench_eig(v):
    A = np.zeros((4, 4)); A[:2, 2:] = np.eye(2)
    Mi = np.linalg.inv(M0)
    A[2:, :2] = -Mi @ (9.81 * K0 + v * v * K2); A[2:, 2:] = -Mi @ (v * C1)
    return np.linalg.eigvals(A)


def bench_params(Ka=1e5):
    w, c, lam = 1.02, 0.08, math.pi / 10
    mB, mH, mR, mF = 85.0, 4.0, 2.0, 3.0
    xs = [(mB, 0.3), (mH, 0.9), (mR, 0.0), (mF, w)]
    mt = sum(m for m, _ in xs); xg = sum(m * x for m, x in xs) / mt
    FzF = mt * 9.81 * xg / w; FzR = mt * 9.81 - FzF
    tyre = dict(Kg=0.0, Ma=0.0, Mg=0.0, sigma=0.0, rho=0.0, Ka=Ka)
    return dict(
        caster=lam, S=[w + c, 0, 0],
        B=dict(m=mB, c=[0.3, 0, 0.9], I=[[9.2, 0, -2.4], [0, 11, 0], [-2.4, 0, 2.8]]),
        H=dict(m=mH, c=[0.9, 0, 0.7], I=[[0.05892, 0, 0.00756], [0, 0.06, 0], [0.00756, 0, 0.00708]]),
        R=dict(m=mR, centre=[0, 0, 0.3], R=0.3, Ixx=0.0603, Iyy=0.12, Fz=FzR, **tyre),
        F=dict(m=mF, centre=[w, 0, 0.35], R=0.35, Ixx=0.1405, Iyy=0.28, Fz=FzF, **tyre),
        k_twist=None, c_steer=0.0)


def slow_modes(lam, k=4):
    lam = lam[np.abs(lam) > 1e-6]
    return np.array(sorted(lam, key=lambda z: abs(z))[:k])


def crit_speed(fun, lo, hi):
    for _ in range(60):
        m = (lo + hi) / 2
        if fun(m) * fun(lo) > 0: lo = m
        else: hi = m
    return (lo + hi) / 2


if __name__ == '__main__':
    res = {}
    # 1) the reference matrices reproduce the published critical speeds (checks our eigen/bisection code)
    wv = lambda v: max(np.real(bench_eig(v))[np.abs(np.imag(bench_eig(v))) > 1e-9], default=-1)
    vw_ref = crit_speed(lambda v: max(np.real(z) for z in bench_eig(v) if abs(np.imag(z)) > 1e-9), 3.0, 5.5)
    vc_ref = crit_speed(lambda v: max(np.real(z) for z in bench_eig(v) if abs(np.imag(z)) < 1e-9), 5.0, 7.0)
    res['reference_matrices'] = dict(v_weave=vw_ref, v_capsize=vc_ref)
    print(f'reference matrices: weave {vw_ref:.6f} (pub {VW}), capsize {vc_ref:.6f} (pub {VC})')
    # 2) our tyre model in the no-slip limit
    for Ka in (1e3, 1e4, 1e5):
        md = dm.Model(bench_params(Ka))
        def slow(v):
            return slow_modes(md.eig(v)[0], 6)
        rows = []
        for v in (2.0, 4.0, 5.0, 6.0, 8.0):
            ours = slow(v); ref = bench_eig(v)
            # match each benchmark root to the nearest of ours
            err = max(min(abs(o - r) for o in ours) for r in ref)
            rows.append((v, err))
        osc = lambda v: max([np.real(z) for z in md.eig(v)[0] if abs(np.imag(z)) > 1e-6 and abs(z) < 30], default=-9)
        cap = lambda v: max([np.real(z) for z in md.eig(v)[0] if abs(np.imag(z)) < 1e-6 and abs(z) < 30 and abs(z) > 1e-6], default=-9)
        vw = crit_speed(osc, 3.0, 5.5); vc = crit_speed(cap, 5.0, 7.0)
        res[f'Ka_{Ka:g}'] = dict(v_weave=vw, v_capsize=vc, max_eig_error=[r[1] for r in rows])
        print(f'Ka={Ka:g}/rad: weave {vw:.4f} m/s ({(vw/VW-1)*100:+.2f}%), capsize {vc:.4f} ({(vc/VC-1)*100:+.2f}%), '
              f'max |eig error| over v=2..8: {max(r[1] for r in rows):.4f} 1/s')
    # eigenvalues at 5 m/s (Meijaard Table 3 gives 4 roots at v=5: -14.0786, -0.7751, -0.4134 +/- 4.4999i? see paper)
    md = dm.Model(bench_params(1e5))
    print('ours  @5 m/s:', np.round(slow_modes(md.eig(5.0)[0], 4), 4))
    print('bench @5 m/s:', np.round(np.sort_complex(bench_eig(5.0)), 4))
    OUT.mkdir(exist_ok=True)
    (OUT / 'validation-meijaard.json').write_text(json.dumps(res, indent=1))
