"""V1 dynamics library: linearised Sharp-type motorcycle model with frame, fork and swingarm compliance.

This is the detailed-design/tools/dyn-model.py method (exact second-order Lagrangian expansion in sympy, validated
against the Meijaard 2007 benchmark bicycle) extended for rev D:
  * q = [y, psi, phi, delta] (lateral position, yaw, roll, steer) plus optional flexible coordinates:
      bf  : frame torsion, front assembly rotates about the longitudinal axis through the swingarm-pivot height
            (stiffness from the FEA head lateral stiffness: k = K_head * h^2, h = head height above the pivot);
      bk  : fork lateral bending, lower legs + front wheel rotate about the axis t (perpendicular to the steering
            axis, in the XZ plane) through the steering-axis point, in the steered frame;
      ya, th, ep : rear wheel carrier on a flexible single-sided swingarm: lateral axle displacement, toe (yaw about
            Z) and camber (roll about X). Stiffness is a cantilever beam fitted to the FEA lateral and yaw numbers
            (2x2 on ya, th) plus the FEA torsion for ep.
  * tyres: force elements, toroidal crown, slip + camber side force, aligning and twisting moments, first-order
    relaxation; vertical loads constant (static + aero load transfer). Pitch and heave frozen (same linear
    stiffness argument as the old model).
  * wind: a lateral aerodynamic force applied at a centre-of-pressure point on the rear frame (gust and sidewind).
Frame: X forward, Y left, Z up, origin at the rear contact point, SI units.

November 22, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.
"""
import numpy as np
import sympy as sp

G0 = 9.81


def _skew(k):
    return sp.Matrix([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])


def _rot2(axis, ang):
    K = _skew(axis)
    return sp.eye(3) + ang * K + ang ** 2 / 2 * K * K


class Model:
    def __init__(self, p):
        self.p = p
        fr = p.get('k_bf') is not None
        fk = p.get('k_bk') is not None
        rf = p.get('rear_flex') is not None
        self.fr, self.fk, self.rf = fr, fk, rf
        names = ['y', 'psi', 'phi', 'delta'] + (['bf'] if fr else []) + (['bk'] if fk else []) + (['ya', 'th', 'ep'] if rf else [])
        self.names = names
        n = len(names); self.n = n
        q = list(sp.symbols(' '.join(names))); qd = list(sp.symbols(' '.join(n_ + 'd' for n_ in names)))
        v = sp.Symbol('v'); FzS = {'R': sp.Symbol('FzR'), 'F': sp.Symbol('FzF')}
        GENS = q + qd

        def tr(e):
            e = sp.expand(e)
            if e == 0:
                return e
            P = sp.Poly(e, *GENS)
            return sum((c * sp.prod([g_ ** k for g_, k in zip(GENS, mon)]) for mon, c in P.terms() if sum(mon) <= 2), sp.S(0))

        def tm(M_):
            return M_.applyfunc(tr)
        Q = dict(zip(names, q))
        ez = sp.Matrix([0, 0, 1]); ey = sp.Matrix([0, 1, 0]); ex = sp.Matrix([1, 0, 0])
        eps = p['caster']
        s = sp.Matrix([-np.sin(eps), 0, np.cos(eps)])
        t = sp.Matrix([np.cos(eps), 0, np.sin(eps)])
        S = sp.Matrix(p['S']); Cf = sp.Matrix([0, 0, p.get('z_twist', 0.0)])
        RB = tm(_rot2(ez, Q['psi']) * _rot2(ex, Q['phi']))
        RFt = _rot2(ex, Q['bf']) if fr else sp.eye(3)
        RS = _rot2(s, Q['delta'])
        RT = _rot2(t, Q['bk']) if fk else sp.eye(3)
        self.fork_mode = fk
        O = sp.Matrix([0, Q['y'], 0])
        RH = tm(RB * tm(RFt * RS))
        RL = tm(RH * RT) if fk else RH
        if rf:
            RW = tm(_rot2(ez, Q['th']) * _rot2(ex, Q['ep']))
            RR_ = tm(RB * RW)
            dW = sp.Matrix([0, Q['ya'], 0])
        else:
            RR_ = RB; dW = sp.zeros(3, 1)

        def ddt(M_):
            out = sp.zeros(*M_.shape)
            for qi, qdi in zip(q, qd):
                out += M_.diff(qi) * qdi
            return out

        def pos_B(pt):
            return tm(O + RB * sp.Matrix(pt))

        def front_root(vec):     # vec measured from S in the steered frame -> world position
            return tm(O + RB * (Cf + RFt * (S - Cf + vec)))

        def pos_H(pt):
            return front_root(tm(RS * (sp.Matrix(pt) - S)))

        def pos_L(pt):
            return front_root(tm(tm(RS * RT) * (sp.Matrix(pt) - S)))

        def pos_Rw(pt):
            return tm(O + RB * (sp.Matrix(pt) + dW))

        def vel(r):
            return tm(ddt(r)) + v * ex

        def omega_body(Rm):
            W = Rm.T * tm(ddt(Rm))
            return tm(sp.Matrix([W[2, 1], W[0, 2], W[1, 0]]))

        def omega_world(Rm):
            W = tm(ddt(Rm)) * Rm.T
            return tm(sp.Matrix([W[2, 1], W[0, 2], W[1, 0]]))

        T = 0; Vp = 0
        rb = [('B', pos_B, RB), ('H', pos_H, RH)] + ([('L', pos_L, RL)] if fk else [])
        for key, posf, Rm in rb:
            b = p[key]; m = b['m']; c = b['c']; I = sp.Matrix(b['I'])
            r = posf(c); vv = vel(r); w = omega_body(Rm)
            T += tr(sp.Rational(1, 2) * m * (vv.T * vv)[0] + sp.Rational(1, 2) * (w.T * I * w)[0])
            Vp += m * G0 * r[2]
        self.contacts = {}
        for key, posf, Rm in (('R', pos_Rw, RR_), ('F', pos_L if fk else pos_H, RL)):
            wdat = p[key]; m = wdat['m']; Wc = wdat['centre']; Rw = wdat['R']; rho = wdat['rho']
            r = posf(Wc); vv = vel(r)
            Om = v / Rw
            w = omega_body(Rm) + Om * ey
            I = sp.diag(wdat['Ixx'], wdat['Iyy'], wdat['Ixx'])
            T += tr(sp.Rational(1, 2) * m * (vv.T * vv)[0] + sp.Rational(1, 2) * (w.T * I * w)[0])
            Vp += m * G0 * r[2]
            a = tm(Rm * ey)
            zc = tr(r[2] - (Rw - rho) * (1 - a[2] ** 2 / 2) - rho)
            Vp += -FzS[key] * zc
            wW = omega_world(Rm)
            vP = vv + wW.cross(sp.Matrix([0, 0, -Rw]))
            self.contacts[key] = dict(vP=vP, wW=wW, heading=-a[0], camber=a[2], vlat=vP[1] - v * (-a[0]))
        if p.get('rotor'):
            J, ratio = p['rotor']
            wB = omega_body(RB)
            T += J * ratio * (v / p['R']['R']) * wB[1]
        L = sp.expand(T - Vp)
        z0 = {s_: 0 for s_ in q + qd}
        Mq = sp.zeros(n, n); Gq = sp.zeros(n, n); Kq = sp.zeros(n, n)
        dLdqd = [L.diff(a_) for a_ in qd]; dLdq = [L.diff(a_) for a_ in q]
        for i in range(n):
            for j in range(n):
                Mq[i, j] = dLdqd[i].diff(qd[j]).subs(z0)
                Gq[i, j] = dLdqd[i].diff(q[j]).subs(z0)
                Kq[i, j] = dLdq[i].diff(q[j]).subs(z0)
        tyre = {}
        for key, c in self.contacts.items():
            vlat = sp.expand(c['vlat'])
            tyre[key] = dict(
                vlat_q=[vlat.diff(a_).subs(z0) for a_ in q], vlat_qd=[vlat.diff(a_).subs(z0) for a_ in qd],
                cam_q=[sp.expand(c['camber']).diff(a_).subs(z0) for a_ in q],
                Py=[sp.expand(c['vP'][1]).diff(a_).subs(z0) for a_ in qd],
                Pz=[sp.expand(c['wW'][2]).diff(a_).subs(z0) for a_ in qd])
        self.v = v
        args = (v, FzS['R'], FzS['F'])
        self.f = dict(M=sp.lambdify(args, Mq, 'numpy'), G=sp.lambdify(args, Gq, 'numpy'), K=sp.lambdify(args, Kq, 'numpy'))
        self.tyre = {k: {kk: sp.lambdify(v, sp.Matrix(vv_), 'numpy') for kk, vv_ in d.items()} for k, d in tyre.items()}

    def wind_vector(self, xcp, zcp):
        """Generalised force per unit lateral force (+Y) at a point (xcp, 0, zcp) on the rear frame: y + x psi - z phi."""
        w = np.zeros(self.n)
        w[0] = 1.0; w[1] = xcp; w[2] = -zcp
        return w

    def _structure(self, vel):
        """Stiffness and damping added outside the Lagrangian (elastic energy and structural damping)."""
        p = self.p; n = self.n; Kd = np.zeros((n, n)); Cd = np.zeros((n, n)); nm = self.names
        if self.fr:
            i = nm.index('bf'); Kd[i, i] += p['k_bf']; Cd[i, i] += p.get('c_bf', 0.0)
        if self.fk:
            i = nm.index('bk'); Kd[i, i] += p['k_bk']; Cd[i, i] += p.get('c_bk', 0.0)
        if self.rf:
            rf = p['rear_flex']; ia, it, ie = nm.index('ya'), nm.index('th'), nm.index('ep')
            EI, Ls = rf['EI'], rf['L']
            K2 = EI * np.array([[12 / Ls ** 3, 6 / Ls ** 2], [6 / Ls ** 2, 4 / Ls]])
            for a, ia_ in enumerate((ia, it)):
                for b, ib_ in enumerate((ia, it)):
                    Kd[ia_, ib_] += K2[a, b]
            Kd[ie, ie] += rf['k_ep']
            Cd[ia, ia] += rf.get('c_ya', 0.0); Cd[it, it] += rf.get('c_th', 0.0); Cd[ie, ie] += rf.get('c_ep', 0.0)
        cs = p.get('c_steer', 0.0)
        Cd[nm.index('delta'), nm.index('delta')] += cs(vel) if callable(cs) else cs
        return Kd, Cd

    def state_matrix(self, vel, Fz=None):
        p = self.p; n = self.n
        Fz = Fz or (p['R']['Fz'], p['F']['Fz'])
        FZ = dict(R=Fz[0], F=Fz[1])
        M = np.array(self.f['M'](vel, *Fz), float); Gm = np.array(self.f['G'](vel, *Fz), float); Km = np.array(self.f['K'](vel, *Fz), float)
        C = Gm - Gm.T
        Kd, Cd = self._structure(vel)
        rows_q = []; rows_qd = []; Bq = []
        for key in ('R', 'F'):
            w = p[key]; tk = self.tyre[key]
            vq = np.array(tk['vlat_q'](vel), float).ravel(); vqd = np.array(tk['vlat_qd'](vel), float).ravel()
            cq = np.array(tk['cam_q'](vel), float).ravel(); Py = np.array(tk['Py'](vel), float).ravel()
            rows_q.append(-w['Ka'] * FZ[key] * vq / vel - w['Kg'] * FZ[key] * cq); rows_qd.append(-w['Ka'] * FZ[key] * vqd / vel)
            Bq.append(Py)
        for key in ('R', 'F'):
            w = p[key]; tk = self.tyre[key]
            vq = np.array(tk['vlat_q'](vel), float).ravel(); vqd = np.array(tk['vlat_qd'](vel), float).ravel()
            cq = np.array(tk['cam_q'](vel), float).ravel(); Pz = np.array(tk['Pz'](vel), float).ravel()
            rows_q.append(w['Ma'] * FZ[key] * vq / vel - w['Mg'] * FZ[key] * cq); rows_qd.append(w['Ma'] * FZ[key] * vqd / vel)
            Bq.append(Pz)
        sig = [p['R']['sigma'], p['F']['sigma'], p['R']['sigma'], p['F']['sigma']]
        Bmat = np.array(Bq).T
        Minv = np.linalg.inv(M)
        lag = [k for k in range(4) if sig[k] > 0]; nolag = [k for k in range(4) if sig[k] <= 0]
        Ktot = -Km + Kd; Ctot = C + Cd
        for k in nolag:
            Ktot = Ktot - np.outer(Bmat[:, k], rows_q[k]); Ctot = Ctot - np.outer(Bmat[:, k], rows_qd[k])
        nl = len(lag); N = 2 * n + nl
        A = np.zeros((N, N))
        A[:n, n:2 * n] = np.eye(n)
        A[n:2 * n, :n] = -Minv @ Ktot
        A[n:2 * n, n:2 * n] = -Minv @ Ctot
        for j, k in enumerate(lag):
            A[n:2 * n, 2 * n + j] = Minv @ Bmat[:, k]
            A[2 * n + j, :n] = vel / sig[k] * rows_q[k]
            A[2 * n + j, n:2 * n] = vel / sig[k] * rows_qd[k]
            A[2 * n + j, 2 * n + j] = -vel / sig[k]
        self._last = dict(M=M, Minv=Minv, N=N, lag=lag)
        return A

    def input_matrix(self, vel, Fz, xcp, zcp):
        """Column b such that x' = A x + b * F_side (F_side = lateral force in +Y at the centre of pressure, N)."""
        A = self.state_matrix(vel, Fz)
        b = np.zeros(A.shape[0]); b[self.n:2 * self.n] = self._last['Minv'] @ self.wind_vector(xcp, zcp)
        return A, b

    def eig(self, vel, Fz=None):
        A = self.state_matrix(vel, Fz)
        return np.linalg.eig(A)
