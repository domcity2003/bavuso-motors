"""Linearised motorcycle stability model (library). Used by dyn-stability.py.

Model (Sharp 1971 / Sharp-Evangelou-Limebeer 2004 family, simplified):
  * Bodies: rear frame (with rider rigidly attached), front frame (steered, non-spinning), front wheel,
    rear wheel (both spinning at v/R: gyroscopic terms), plus a counter-rotating motor rotor (EV specific).
  * Generalised coordinates q = [y, psi, phi, delta, beta]: lateral position and yaw of the rear frame,
    roll, steer, and an optional front-frame twist beta about an axis perpendicular to the steering axis
    through the steering head (lumped fork lateral bending + frame torsion, as Sharp & Alstead 1980 /
    SEL 2004). Forward speed v is constant (x = v t).
  * Tyres are force elements, not constraints: toroidal crown (radius rho), side force from slip and
    camber, aligning moment from slip, twisting moment from camber, each with a first-order relaxation
    length sigma (sigma = 0 means no lag). Vertical loads are constant (static + aero load transfer).
  * Pitch and heave are frozen and the ground reactions are applied as constant vertical forces at the
    geometric contact points; this gives exactly the same linear stiffness as the constrained system
    (the constraint tangent space has d(pitch) = 0 to first order, so the second variation of
    V - Fz * z_contact restricted to it is what we compute).
Equations are built from the exact second-order expansion of the Lagrangian (sympy, everything numeric
except v), so M, G and K are exact polynomials in v. Frame: X forward, Y left, Z up, origin at the rear
contact point, SI units.

Prepared November 12, 2026 (US Central) by Claude Opus 5.5 (claude-opus-5-5).
"""
import numpy as np
import sympy as sp

G0 = 9.81


def _skew(k):
    return sp.Matrix([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])


def _rot2(axis, ang):
    """Rotation about a unit axis, expanded to second order in the angle (exact enough for a Hessian at 0)."""
    K = _skew(axis)
    return sp.eye(3) + ang * K + ang ** 2 / 2 * K * K


class Model:
    """Build once per parameter set. p is a dict (see bavuso_params / benchmark_params in dyn-stability.py)."""

    def __init__(self, p):
        self.p = p
        self.twist = p.get('k_twist') is not None
        names = ['y', 'psi', 'phi', 'delta'] + (['beta'] if self.twist else [])
        self.names = names
        n = len(names)
        q = sp.symbols(' '.join(names));
        qd = sp.symbols(' '.join(n_ + 'd' for n_ in names))
        q = list(q); qd = list(qd)
        v = sp.Symbol('v'); FzS = {'R': sp.Symbol('FzR'), 'F': sp.Symbol('FzF')}
        self.n = n
        GENS = q + qd

        def tr(e):   # keep terms of total degree <= 2 in (q, qd): all a Hessian at 0 needs
            e = sp.expand(e)
            if e == 0:
                return e
            P = sp.Poly(e, *GENS)
            return sum((c * sp.prod([g_ ** k for g_, k in zip(GENS, mon)]) for mon, c in P.terms() if sum(mon) <= 2), sp.S(0))

        def tm(M_):
            return M_.applyfunc(tr)
        y, psi, phi, delta = q[:4]
        beta = q[4] if self.twist else 0
        ez = sp.Matrix([0, 0, 1]); ey = sp.Matrix([0, 1, 0]); ex = sp.Matrix([1, 0, 0])
        eps = p['caster']
        s = sp.Matrix([-np.sin(eps), 0, np.cos(eps)])          # steering axis, up
        t = sp.Matrix([np.cos(eps), 0, np.sin(eps)])           # twist axis, forward-up, perpendicular to s
        S = sp.Matrix(p['S'])
        RB = tm(_rot2(ez, psi) * _rot2(ex, phi))
        RT = _rot2(t, beta) if self.twist else sp.eye(3)
        RS = _rot2(s, delta)
        self.fork_mode = p.get('twist_mode') == 'fork'
        if self.fork_mode:     # fork lateral bending: twist in the steered frame, lower legs + wheel only
            RH = tm(RB * RS)
            RL = tm(RB * tm(RS * RT))
        else:                  # SEL-style: steering head twists relative to the main frame, whole front follows
            RH = tm(RB * tm(RT * RS))
            RL = RH
        O = sp.Matrix([0, y, 0])                               # + v t ex (enters velocities only)

        def ddt(M_):   # time derivative along the coordinates (no explicit time dependence except v t ex)
            out = sp.zeros(*M_.shape)
            for qi, qdi in zip(q, qd):
                out += M_.diff(qi) * qdi
            return out

        def pos_B(pt):
            return tm(O + RB * sp.Matrix(pt))

        def pos_H(pt):
            if self.fork_mode:
                return tm(O + RB * (S + RS * (sp.Matrix(pt) - S)))
            return tm(O + RB * (S + tm(RT * RS) * (sp.Matrix(pt) - S)))

        def pos_L(pt):
            if self.fork_mode:
                return tm(O + RB * (S + tm(RS * RT) * (sp.Matrix(pt) - S)))
            return pos_H(pt)

        def vel(r):
            return tm(ddt(r)) + v * ex

        def omega_body(Rm):   # body-frame angular velocity, from R^T Rdot
            W = Rm.T * tm(ddt(Rm))
            return tm(sp.Matrix([W[2, 1], W[0, 2], W[1, 0]]))

        def omega_world(Rm):
            W = tm(ddt(Rm)) * Rm.T
            return tm(sp.Matrix([W[2, 1], W[0, 2], W[1, 0]]))

        T = 0; V = 0
        # rigid bodies
        rb = [('B', pos_B, RB), ('H', pos_H, RH)] + ([('L', pos_L, RL)] if self.fork_mode else [])
        for key, posf, Rm in rb:
            b = p[key]; m = b['m']; c = b['c']; I = sp.Matrix(b['I'])
            r = posf(c); vv = vel(r); w = omega_body(Rm)
            T += tr(sp.Rational(1, 2) * m * (vv.T * vv)[0] + sp.Rational(1, 2) * (w.T * I * w)[0])
            V += m * G0 * r[2]
        # wheels
        self.contacts = {}
        for key, posf, Rm in (('R', pos_B, RB), ('F', pos_L, RL)):
            wdat = p[key]; m = wdat['m']; Wc = wdat['centre']; Rw = wdat['R']; rho = wdat['rho']
            r = posf(Wc); vv = vel(r)
            Om = v / Rw
            w = omega_body(Rm) + Om * ey
            I = sp.diag(wdat['Ixx'], wdat['Iyy'], wdat['Ixx'])
            T += tr(sp.Rational(1, 2) * m * (vv.T * vv)[0] + sp.Rational(1, 2) * (w.T * I * w)[0])
            V += m * G0 * r[2]
            a = tm(Rm * ey)                                      # spin axis in the world
            zc = tr(r[2] - (Rw - rho) * (1 - a[2] ** 2 / 2) - rho)  # lowest point of the torus, 2nd order
            V += -FzS[key] * zc
            # carrier-fixed material point at the contact: first-order lateral slip velocity and heading
            wW = omega_world(Rm)
            vP = vv + wW.cross(sp.Matrix([0, 0, -Rw]))
            heading = -a[0]
            camber = a[2]                                     # + = leaning right (toward -Y)
            vlat = vP[1] - v * heading
            self.contacts[key] = dict(vP=vP, wW=wW, heading=heading, camber=camber, vlat=vlat)
        # motor rotor gyro on the rear frame (counter-rotating, transverse axis)
        if p.get('rotor'):
            J, ratio = p['rotor']
            wB = omega_body(RB)
            T += J * ratio * (v / p['R']['R']) * wB[1]
        L = sp.expand(T - V)
        z0 = {s_: 0 for s_ in q + qd}
        Mq = sp.zeros(n, n); Gq = sp.zeros(n, n); Kq = sp.zeros(n, n)
        dLdqd = [L.diff(a_) for a_ in qd]
        dLdq = [L.diff(a_) for a_ in q]
        for i in range(n):
            for j in range(n):
                Mq[i, j] = dLdqd[i].diff(qd[j]).subs(z0)
                Gq[i, j] = dLdqd[i].diff(q[j]).subs(z0)
                Kq[i, j] = dLdq[i].diff(q[j]).subs(z0)
        # first-order tyre kinematics
        tyre = {}
        for key, c in self.contacts.items():
            vlat = sp.expand(c['vlat'])
            tyre[key] = dict(
                vlat_q=[vlat.diff(a_).subs(z0) for a_ in q], vlat_qd=[vlat.diff(a_).subs(z0) for a_ in qd],
                cam_q=[sp.expand(c['camber']).diff(a_).subs(z0) for a_ in q],
                # generalised-force partials: lateral partial velocity of the contact point, yaw partial rotation
                Py=[sp.expand(c['vP'][1]).diff(a_).subs(z0) for a_ in qd],
                Pz=[sp.expand(c['wW'][2]).diff(a_).subs(z0) for a_ in qd])
        self.v = v
        args = (v, FzS['R'], FzS['F'])
        self.f = dict(M=sp.lambdify(args, Mq, 'numpy'), G=sp.lambdify(args, Gq, 'numpy'), K=sp.lambdify(args, Kq, 'numpy'))
        self.tyre = {k: {kk: sp.lambdify(v, sp.Matrix(vv_), 'numpy') for kk, vv_ in d.items()} for k, d in tyre.items()}

    def state_matrix(self, vel, Fz=None):
        """A matrix for x = [q, qd, Fy_R, Fy_F, Mz_R, Mz_F]. Returns (A, index of q block size n)."""
        p = self.p; n = self.n
        Fz = Fz or (p['R']['Fz'], p['F']['Fz'])
        FZ = dict(R=Fz[0], F=Fz[1])
        M = np.array(self.f['M'](vel, *Fz), float); Gm = np.array(self.f['G'](vel, *Fz), float); Km = np.array(self.f['K'](vel, *Fz), float)
        # Lagrange: M qdd + (G - G^T) qd - K q = Q
        C = Gm - Gm.T
        Kn = -Km
        Cd = np.zeros((n, n)); Kd = np.zeros((n, n))
        idel = self.names.index('delta')
        cs = p.get('c_steer', 0.0)
        Cd[idel, idel] += cs(vel) if callable(cs) else cs     # callable = speed-scheduled (semi-active) damper
        if self.twist:
            ib = self.names.index('beta')
            Kd[ib, ib] += p['k_twist']; Cd[ib, ib] += p.get('c_twist', 0.0)
        # tyre steady-state forces as linear maps of q and qd, and their generalised-force projections
        keys = ['R', 'F']
        Fq = []; Fqd = []; Bq = []
        for key in keys:
            w = p[key]; tk = self.tyre[key]
            vq = np.array(tk['vlat_q'](vel), float).ravel(); vqd = np.array(tk['vlat_qd'](vel), float).ravel()
            cq = np.array(tk['cam_q'](vel), float).ravel()
            Py = np.array(tk['Py'](vel), float).ravel(); Pz = np.array(tk['Pz'](vel), float).ravel()
            Fz = FZ[key]
            # side force (+Y): -C_alpha * slip - C_gamma * camber ; slip = vlat / v
            Fq.append(-w['Ka'] * Fz * vq / vel - w['Kg'] * Fz * cq); Fqd.append(-w['Ka'] * Fz * vqd / vel)
            Bq.append(('F', Py))
        Mq_ = []; Mqd_ = []
        for key in keys:
            w = p[key]; tk = self.tyre[key]
            vq = np.array(tk['vlat_q'](vel), float).ravel(); vqd = np.array(tk['vlat_qd'](vel), float).ravel()
            cq = np.array(tk['cam_q'](vel), float).ravel()
            Pz = np.array(tk['Pz'](vel), float).ravel()
            Fz = FZ[key]
            # aligning moment (+Z) = +M_alpha * slip - M_gamma * camber (twisting moment toward the lean side)
            Mq_.append(w['Ma'] * Fz * vq / vel - w['Mg'] * Fz * cq); Mqd_.append(w['Ma'] * Fz * vqd / vel)
            Bq.append(('M', Pz))
        rows_q = Fq + Mq_; rows_qd = Fqd + Mqd_
        sig = [p['R']['sigma'], p['F']['sigma'], p['R']['sigma'], p['F']['sigma']]
        Bmat = np.array([b[1] for b in Bq]).T          # n x 4: generalised force per unit tyre force/moment
        Minv = np.linalg.inv(M)
        lag = [k for k in range(4) if sig[k] > 0]
        nolag = [k for k in range(4) if sig[k] <= 0]
        Ktot = Kn + Kd; Ctot = C + Cd
        for k in nolag:   # direct substitution
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
        return A

    def eig(self, vel, Fz=None):
        A = self.state_matrix(vel, Fz)
        lam, X = np.linalg.eig(A)
        return lam, X
