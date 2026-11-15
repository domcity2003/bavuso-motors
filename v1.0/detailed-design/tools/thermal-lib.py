"""Shared parameters and lumped-parameter thermal models for the Bavuso V1.0 thermal study.

Loaded by thermal-cases.py / thermal-charge-sweep.py with importlib (hyphenated file name).
Units: SI (W, J, K, kg, m, s) unless a name says otherwise. Temperatures in degC.
Every parameter carries its basis in a comment; see detailed-design/thermal-study.md for the citations.
"""
import math
import numpy as np

# ------------------------------------------------------------------ vehicle (mass-rollup.md, drive-study.md, aero report)
M_BIKE = 287.2          # kg ready to ride, Nov 12 roll-up
M_RIDER = 85.0
ROT = 1.05              # rotating-mass factor (drive-study)
CDA = 0.40              # m^2, aero target (baseline CFD 0.44; sensitivity run at 0.44)
CRR = 0.015
R_WHEEL = 0.305         # m rolling radius (drive-study)
RATIO = 7.8             # 2-stage reduction (drive-study supplier spec, 7.5-7.8)
GRIP_G = 1.0            # launch-control limit (drive-study)
G = 9.81

def rho_air(T_c=35.0, alt_m=0.0):
    p = 101325 * (1 - 2.25577e-5 * alt_m) ** 5.25588
    return p / (287.05 * (T_c + 273.15))

# ------------------------------------------------------------------ cells and pack (build-adventure.py, powertrain-cost-down.py)
N_S, N_P = 99, 6
N_CELL = N_S * N_P                 # 594
CELL_WH = 55.0                     # Wh (CELL_WH in the CAD generator)
CELL_AH = CELL_WH / 3.6            # 15.3 Ah
CELL_M = 0.180                     # kg
CELL_CP = 1000.0                   # J/kgK, cylindrical NMC cells measure ~900-1100 (Drake 2014; Loges 2016)
C_CAN = 18.0                       # J/K, 0.5 mm Al can + caps, ~20 g
C_CORE = CELL_M * CELL_CP - C_CAN  # J/K jelly roll
# Heat-generating resistance at 25 degC, 50 % SOC. Anchor: Molicel P50B 21700, 5 Ah, DC impedance 12.8 mOhm
# (datasheet) -> same chemistry scaled to 15.3 Ah = 4.2 mOhm; x1.2 for diffusion polarisation over minutes-long
# currents (a 10 s DCIR understates sustained heat). Sensitivity 3.5-6.5 mOhm in thermal-charge-sweep.py.
R25 = 5.0e-3
B_ARR = 2000.0                     # K, R(T)=R25*exp(B(1/T-1/298)): x1.9 at 0 degC, x0.72 at 40 degC

def r_cell(T_c, soc):
    f_soc = 1.0 + 0.6 * max(0.0, 0.2 - soc) / 0.2 + 0.15 * max(0.0, soc - 0.85) / 0.15
    return R25 * math.exp(B_ARR * (1.0 / (T_c + 273.15) - 1.0 / 298.15)) * f_soc

_SOC = np.array([0, .05, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0])
_OCV = np.array([3.00, 3.30, 3.45, 3.55, 3.62, 3.67, 3.72, 3.80, 3.90, 3.98, 4.08, 4.20])
def ocv(soc): return float(np.interp(soc, _SOC, _OCV))

def cell_current(P_pack, soc, T_c):
    """Cell current (A, + = discharge) for a pack terminal power (W, + = discharge)."""
    p = P_pack / N_CELL; E = ocv(soc); R = r_cell(T_c, soc)
    disc = E * E - 4 * R * p
    if disc < 0: disc = 0.0
    return (E - math.sqrt(disc)) / (2 * R)

# Cell internal thermal path. Jelly roll is anisotropic: ~0.2-1 W/mK across layers (radial), ~25-30 W/mK along
# layers (axial and tangential) (Drake et al., J. Power Sources 252, 2014). Mean-core-to-can resistance from the
# 2-D finite-difference check in thermal-cell-fd.py (k_r=0.6, k_a=25): R_CORE_CAN, max/mean ratio CORE_PEAK.
R_CORE_CAN = 0.27                  # K/W mean core to can, FD result at k_r=0.6, k_a=25 (thermal-cell-fd.py)
CORE_PEAK = 2.65                   # core hot-spot rise / mean rise (same FD run)
# Can to coolant through the side-cooling ribbon (Tesla-style serpentine, one ribbon per two-row band, so every
# cell touches one ribbon on a ~60 deg arc): adhesive 0.2 mm, k 2.0 W/mK, 1.43e-3 m2 -> 0.07 K/W;
# laminar ribbon channels Dh 1.9 mm, Nu~5, h~1050 W/m2K on ~3.5e-3 m2 per cell -> 0.27 K/W; partial-arc penalty
# on the core path is taken as x1.3 on R_CORE_CAN.
R_TIM = 0.07 + 0.15                # adhesive + dielectric layer (<=50 um polyimide or ~100 um filled coating, 2.5 kV hipot): the
                                   # ribbon touches cells of many series groups, so it must be insulated
R_RIB = 0.27
ARC_PENALTY = 1.3

# Pack case (CAD: 4 mm structural Al shell; the brief says 3 mm, both evaluated in thermal-cases.py)
CASE_AREA = 1.05                   # m^2 outer area, from the band outline in geometry-adventure-audit.json
CASE_T = 0.004
CASE_C = CASE_AREA * CASE_T * 2700 * 900   # J/K
G_CELL_CASE = 15.0                 # W/K: edge cells to wall through 1 mm insulation + mounts (estimate)

def g_case_air(v):
    """Case to ambient (W/K): it sits inside the 3 mm covers with an 8 mm gap; natural/radiative ~9 W/m2K
    plus a little forced flow under the covers at speed (estimate)."""
    return CASE_AREA * (9.0 + 0.15 * v)

# ------------------------------------------------------------------ coolant, loops, radiators
CP_C, RHO_C = 3400.0, 1065.0       # 50/50 ethylene glycol-water at ~40 degC
Q_BATT_LPM = 15.0                  # battery loop flow
Q_DRIVE_LPM = 12.0                 # drive loop flow (inverter wants ~8-12 L/min class)
def mcp(lpm): return lpm / 60000 * RHO_C * CP_C   # W/K
V_RIB_L = 1.5                      # L of coolant in ribbons + manifolds
V_BLOOP_L = 1.4                    # L outside the pack: radiator share, hoses, heater, pump, reservoir
V_DLOOP_L = 1.6                    # L drive loop: radiator, hoses, inverter, OBC plate, oil HX

N_SEG = 4                          # pack segments along the coolant path

# Radiator: brazed Al louvered-fin core, 32 mm deep. UA per m2 of face ~3400 W/K at 5 m/s face velocity
# (air-side area density ~1400 m2/m3, h~100 W/m2K, fin efficiency 0.85, coolant side ~10 % of resistance;
# Kays & London compact-HX surfaces). UA ~ v^0.5. Effectiveness: cross-flow, both fluids unmixed.
RAD_UA_5 = 3400.0
RAM = 0.25                         # face velocity / road speed with a ducted side scoop (to be confirmed by CFD)
V_FAN = 3.2                        # m/s face velocity at idle: 7.5 in puller, 366-437 CFM free air (SPAL listings), ~60 % through a core, over ~0.04 m2
FAN_W = 90.0                       # W per fan at full duty

def radiator_q(T_in, T_amb, area, v_face, C_cool, rho=1.16):
    if area <= 0 or v_face <= 0 or T_in <= T_amb: return 0.0
    C_air = rho * area * v_face * 1007.0
    UA = RAD_UA_5 * area * (v_face / 5.0) ** 0.5
    Cmin, Cmax = min(C_air, C_cool), max(C_air, C_cool)
    Cr = Cmin / Cmax; NTU = UA / Cmin
    eps = 1 - math.exp((NTU ** 0.22 / Cr) * (math.exp(-Cr * NTU ** 0.78) - 1)) if Cr > 1e-6 else 1 - math.exp(-NTU)
    return eps * Cmin * (T_in - T_amb)

# ------------------------------------------------------------------ motor (drive-study supplier spec) loss model
T_PEAK, P_PEAK, N_MAX = 150.0, 130e3, 16000.0
N_BASE = P_PEAK / T_PEAK * 60 / (2 * math.pi)       # 8,276 rpm
P_CU_PEAK = 6.5e3      # W copper loss at full current, 120 degC winding (sets ~95 % at the 130 kW corner)
P_FE16 = 3.0e3         # W iron loss at 16k rpm, full flux
P_MECH16 = 0.4e3       # W bearings + windage at 16k rpm

def motor_losses(T_nm, rpm, Tw):
    """Return (copper, stator iron, rotor, mechanical) losses in W and current fraction."""
    iq = abs(T_nm) / T_PEAK
    fw = max(0.0, (rpm - N_BASE) / (N_MAX - N_BASE))
    idd = 0.55 * fw ** 0.8 if rpm > N_BASE else 0.0
    i2 = iq * iq + idd * idd
    kac = 1 + 0.4 * (rpm / N_MAX) ** 2           # hairpin AC resistance
    cu = P_CU_PEAK * i2 * kac * (1 + 0.00393 * (Tw - 120)) / 1.0
    flux = 1.0 if rpm <= N_BASE else (N_BASE / rpm) ** 0.5
    fe = P_FE16 * (rpm / N_MAX) ** 1.5 * flux ** 2
    mech = P_MECH16 * (rpm / N_MAX) ** 2
    return cu, 0.85 * fe, 0.15 * fe + 0.03 * cu, mech, math.sqrt(i2)

# Motor thermal network (oil-cooled hairpin IPM, 14 kg) - these resistances are what the RFQ must ask for;
# they reproduce the spec's 85-90 kW continuous rating at 65 degC coolant (checked in thermal-cases.py).
C_W, C_S, C_R, C_O = 1300.0, 2990.0, 2070.0, 6700.0
R_WS, R_WO, R_SO, R_RO, R_RS = 0.030, 0.055, 0.012, 0.10, 0.25
OIL_LPM = 10.0
G_HX = 0.75 * min(OIL_LPM / 60 * 0.85 * 1900, mcp(Q_DRIVE_LPM))   # oil-water HX conductance, W/K

def gear_loss(P_shaft, rpm):
    return 0.012 * abs(P_shaft) + 150.0 * (rpm / N_MAX) ** 1.5

BELT_EFF = 0.975

# ------------------------------------------------------------------ SiC inverter (HybridPACK Drive G2 750 V class)
I_MAX_RMS = 400.0
RDS25 = 1.7e-3          # ohm per switch position (distributor listing gives 2.21 mOhm max)
F_SW, E_REF, I_REF, V_REF = 10e3, 0.014, 450.0, 400.0
R_JC = 0.07             # K/W per switch, junction to pin-fin base
R_CF_TOT = 0.05 / 6     # K/W, inverter base node to coolant (0.05 per switch, 6 in parallel)
C_INV = 1350.0          # J/K module + cold plate

def inverter_loss(i_frac, Vdc, Tj):
    I = i_frac * I_MAX_RMS
    cond = 3 * I * I * RDS25 * (1 + 0.004 * (Tj - 25))
    sw = 6 * F_SW * E_REF * (I * math.sqrt(2) / I_REF) * (Vdc / V_REF) / math.pi if I > 1 else 0.0
    return cond + sw + 40.0

AUX_W = 350.0           # LV loads while riding; DC-DC 93 % -> its heat goes to the drive loop
DCDC_EFF = 0.93
OBC_EFF = 0.94

# ------------------------------------------------------------------ duty-cycle profiles
def road_power(v, a, m, grade=0.0, rho=1.16, cda=CDA):
    return v * (m * ROT * a + 0.5 * rho * cda * v * v + CRR * m * G * math.cos(math.atan(grade)) + m * G * math.sin(math.atan(grade)))

def accel_profile(v0, v1, m, rho=1.16, grade=0.0, p_max=P_PEAK, dt=0.1):
    """Full-power acceleration; returns lists of (dt, v, a)."""
    out = []; v = v0
    while v < v1:
        vv = max(v, 0.5)
        f_motor = min(T_PEAK * RATIO * 0.96 / R_WHEEL, p_max * 0.96 * 0.955 / vv)   # 0.955 ~ motor+inverter eff
        f = min(GRIP_G * m * G, f_motor) - 0.5 * rho * CDA * vv * vv - CRR * m * G - m * G * grade
        a = f / (m * ROT)
        if a <= 0.01: break
        out.append((dt, v, a)); v += a * dt
    return out

def brake_profile(v0, v1, decel=0.6 * G, dt=0.1):
    out = []; v = v0
    while v > v1:
        out.append((dt, v, -decel)); v -= decel * dt
    return out

def hold(v, seconds, dt=1.0):
    return [(dt, v, 0.0)] * int(seconds / dt)

def to_arrays(segs, grade_fn=None, alt_fn=None):
    t = [0.0]; vs = []; acc = []; dist = [0.0]
    for dt, v, a in segs:
        vs.append(v); acc.append(a); t.append(t[-1] + dt); dist.append(dist[-1] + v * dt)
    vs.append(vs[-1]); acc.append(0.0)
    t, vs, acc, dist = map(np.array, (t, vs, acc, dist))
    gr = np.array([grade_fn(d) if grade_fn else 0.0 for d in dist])
    al = np.array([alt_fn(d) if alt_fn else 0.0 for d in dist])
    return dict(t=t, v=vs, a=acc, grade=gr, alt=al, dist=dist)

# ------------------------------------------------------------------ the coupled model
class Model:
    """Battery loop + pack (N_SEG segments, core/can/coolant nodes, case) and drive loop (inverter, motor 4-node,
    coolant) with radiators, fans, valve, optional heater and chiller. State also carries SOC and energy
    accumulators for the energy-balance check."""
    def __init__(self, T_amb=35.0, area_side=0.035, mode='drive', heater_w=0.0, chiller_w=0.0, T0=None,
                 soc0=1.0, m_total=None, profile=None, charge_c=3.0, case_t=CASE_T, r25=None, rib_r=None,
                 precondition=None, soc_stop=0.05, soc_target=0.80, cda=CDA, derate=True):
        self.Ta = T_amb; self.A = area_side; self.mode = mode; self.heater = heater_w; self.chiller = chiller_w
        self.m = m_total or (M_BIKE + M_RIDER); self.p = profile; self.cmax = charge_c; self.soc_stop = soc_stop
        self.soc_target = soc_target; self.cda = cda; self.derate = derate
        self.case_C = CASE_AREA * case_t * 2700 * 900
        self.r25 = r25 or R25; self.R_cc = R_CORE_CAN * ARC_PENALTY; self.R_cw = (rib_r or R_RIB) + R_TIM
        self.n_seg = N_SEG
        self.mb, self.md = mcp(Q_BATT_LPM), mcp(Q_DRIVE_LPM)
        T0 = T_amb if T0 is None else T0
        n = N_SEG
        # state layout
        self.iC = 0; self.iK = n; self.iQ = 2 * n; self.iCase = 3 * n; self.iBL = 3 * n + 1
        self.iSc = 3 * n + 2; self.iSk = 3 * n + 3          # sentinel (hottest) cell core/can
        self.iInv, self.iW, self.iS, self.iR, self.iO, self.iDL = range(3 * n + 4, 3 * n + 10)
        self.iSOC = 3 * n + 10
        self.iE = 3 * n + 11      # accumulators: gen, rad, amb, heater, chiller, (5)
        self.nx = self.iE + 5
        x = np.full(self.nx, float(T0)); x[self.iSOC] = soc0; x[self.iE:] = 0.0
        self.x0 = x
        self.caps = self._caps()
        self.precond = precondition
        self.log = []

    def _caps(self):
        n = N_SEG; c = np.zeros(self.nx)
        c[self.iC:self.iC + n] = C_CORE * N_CELL / n; c[self.iK:self.iK + n] = C_CAN * N_CELL / n
        c[self.iQ:self.iQ + n] = V_RIB_L / 1000 * RHO_C * CP_C / n
        c[self.iCase] = self.case_C; c[self.iBL] = V_BLOOP_L / 1000 * RHO_C * CP_C
        c[self.iInv] = C_INV; c[self.iW] = C_W; c[self.iS] = C_S; c[self.iR] = C_R; c[self.iO] = C_O
        c[self.iDL] = V_DLOOP_L / 1000 * RHO_C * CP_C
        return c        # sentinel excluded on purpose (a probe cell, not part of the energy sum)

    def r_cell(self, T, soc): return r_cell(T, soc) * self.r25 / R25

    def inputs(self, t):
        p = self.p
        if self.mode in ('charge', 'soak'):
            return 0.0, 0.0, 0.0, 0.0
        v = float(np.interp(t, p['t'], p['v'])); a = float(np.interp(t, p['t'], p['a']))
        gr = float(np.interp(t, p['t'], p['grade'])); al = float(np.interp(t, p['t'], p['alt']))
        return v, a, gr, al

    def rhs(self, t, x, record=False):
        n = N_SEG; d = np.zeros(self.nx)
        Tc = x[self.iC:self.iC + n]; Tk = x[self.iK:self.iK + n]; Tq = x[self.iQ:self.iQ + n]
        Tcase, TBL = x[self.iCase], x[self.iBL]; soc = min(max(x[self.iSOC], 0.0), 1.0)
        Tsc, Tsk = x[self.iSc], x[self.iSk]
        Tinv, Tw, Ts, Tr, To, TDL = (x[i] for i in (self.iInv, self.iW, self.iS, self.iR, self.iO, self.iDL))
        Ta = self.Ta
        v, a, gr, alt = self.inputs(t)
        rho = rho_air(Ta, alt)
        q_inv = q_cu = q_fe = q_rot = q_mech = q_gear = 0.0; P_batt = 0.0; heater = 0.0; chill = 0.0; q_dcdc = 0.0
        derate = 1.0; i_frac = 0.0
        fans_b = fans_d = 0.0
        if self.mode == 'drive':
            Pw = float(np.interp(t, self.p["t"], self.p["pw"])) if "pw" in self.p else road_power(v, a, self.m, gr, rho, self.cda)
            rpm = v / R_WHEEL * RATIO * 60 / (2 * math.pi)
            w = max(rpm * 2 * math.pi / 60, 1.0)
            if Pw >= 0:
                Ps = Pw / BELT_EFF; Ps = Ps + gear_loss(Ps, rpm)
            else:
                Ps = max(Pw * BELT_EFF, -45e3)          # regen cap (rear grip + charge); remainder is friction braking
                Ps = Ps + gear_loss(Ps, rpm)
            # thermal derate (motor winding 170, magnet 140, junction 150, cell core 60 degC)
            if self.derate:
                lim = min((180 - Tw) / 10, (150 - Tr) / 10, (160 - (Tinv + 30)) / 10, (62 - Tsc) / 4, 1.0)
                derate = min(1.0, max(0.25, lim))
            Ps = max(min(Ps, P_PEAK * derate), -45e3)
            T_nm = max(min(Ps / w, T_PEAK), -T_PEAK)
            q_cu, q_fe, q_rot, q_mech, i_frac = motor_losses(T_nm, rpm, Tw)
            q_gear = gear_loss(Ps, rpm)
            Vdc = N_S * ocv(soc)
            Tj = Tinv + 0  # base node; junction rise added in reporting
            q_inv = inverter_loss(i_frac, Vdc, Tinv + R_JC * 300)
            P_aux = AUX_W + 55
            P_elec = Ps + q_cu + q_fe + q_rot + q_mech - q_gear * 0 + q_inv   # gear loss already in Ps
            fans_b = 1.0 if TBL > 32 and v < 8 else 0.0
            fans_d = 1.0 if TDL > 55 and v < 8 else 0.0
            P_aux += FAN_W * (fans_b + fans_d)
            q_dcdc = P_aux * (1 / DCDC_EFF - 1)
            P_batt = P_elec + P_aux + q_dcdc
        elif self.mode == 'charge':
            # charge current allowed by hottest-cell temperature and SOC (BMS map; see report)
            Tm = Tsc
            cmap = float(np.interp(Tm, [-10, 0, 5, 10, 15, 20, 25, 47, 52, 56], [0, 0.1, 0.3, 0.5, 1.0, 2.0, 3.0, 3.0, 1.2, 0.0]))
            cmax = min(self.cmax, cmap)
            if soc >= self.soc_target: cmax = 0.0
            # preheat: heater on while the coldest core is below 25 degC
            if self.heater > 0 and min(Tc) < 25.0: heater = self.heater
            if self.chiller > 0 and Tsc > 38.0: chill = self.chiller
            I = cmax * CELL_AH
            Rc = self.r_cell(float(np.mean(Tc)), soc)
            P_batt = -N_CELL * (ocv(soc) * I + I * I * Rc)       # power into the cells (W, negative)
            # LV loads (pumps, fans, BMS) and heater are supplied by the station
            fans_b = 1.0 if TBL > Ta + 1 and heater == 0 else 0.0
            q_dcdc = 60.0
        elif self.mode == 'soak':
            pass
        if self.precond is not None and self.mode == 'drive':
            t_on, pw = self.precond
            if t >= t_on and min(Tc) < 25.0: heater = pw; P_batt += pw
        # ---- pack
        Rs = [self.r_cell(Tc[i], soc) for i in range(n)]
        I_cell = 0.0
        if self.mode == 'drive':
            I_cell = cell_current(P_batt, soc, float(np.mean(Tc)))
        elif self.mode == 'charge':
            I_cell = -(cmax * CELL_AH)
        q_cell = [I_cell * I_cell * Rs[i] for i in range(n)]
        Npc = N_CELL / n
        G_cc = Npc / self.R_cc; G_cw = Npc / self.R_cw
        mb = self.mb
        # battery loop: valve gives both radiators to the battery while charging; bypass while heating
        area_b = 2 * self.A if self.mode == 'charge' else self.A
        if heater > 0: area_b = 0.0
        v_face = max(RAM * v, V_FAN if fans_b else 0.0)
        q_rad_b = radiator_q(TBL, Ta, area_b, v_face, mb, rho)
        T_in = TBL - (q_rad_b + chill - heater) / mb
        q_case_cells = G_CELL_CASE * (np.mean(Tk) - Tcase)
        for i in range(n):
            qcc = G_cc * (Tc[i] - Tk[i]); qcw = G_cw * (Tk[i] - Tq[i])
            d[self.iC + i] = (q_cell[i] * Npc - qcc)
            d[self.iK + i] = (qcc - qcw - q_case_cells / n)
            Tup = T_in if i == 0 else Tq[i - 1]
            d[self.iQ + i] = (mb * (Tup - Tq[i]) + qcw)
        q_case_amb = g_case_air(v) * (Tcase - Ta)
        d[self.iCase] = q_case_cells - q_case_amb
        d[self.iBL] = mb * (Tq[-1] - TBL)
        # sentinel: last segment coolant, +10 % heat (parallel-group current spread), +25 % on the cooling path
        qs = 1.10 * I_cell * I_cell * self.r_cell(Tsc, soc)
        d[self.iSc] = (qs - (Tsc - Tsk) / self.R_cc) / C_CORE
        d[self.iSk] = ((Tsc - Tsk) / self.R_cc - (Tsk - Tq[-1]) / (1.25 * self.R_cw)) / C_CAN
        # ---- drive loop: radiator -> inverter -> OBC/DC-DC plate -> oil HX -> back (quasi-steady profile)
        md = self.md
        area_d = self.A if self.mode != 'charge' else 0.0
        q_obc = 0.0
        v_face_d = max(RAM * v, V_FAN if fans_d else 0.0)
        q_rad_d = radiator_q(TDL, Ta, area_d, v_face_d, md, rho)
        T_rad_out = TDL - q_rad_d / md
        q_inv_cool = (Tinv - T_rad_out) / R_CF_TOT
        q_inv_cool = q_inv_cool * (1 - math.exp(-1.0 / (R_CF_TOT * md))) / (1.0 / (R_CF_TOT * md))  # e-NTU of cold plate
        T_after_inv = T_rad_out + q_inv_cool / md
        T_hx_in = T_after_inv + (q_dcdc + q_obc) / md
        q_hx = G_HX * (To - T_hx_in)
        d[self.iInv] = q_inv - q_inv_cool
        q_ws = (Tw - Ts) / R_WS; q_wo = (Tw - To) / R_WO; q_so = (Ts - To) / R_SO
        q_ro = (Tr - To) / R_RO; q_rs = (Tr - Ts) / R_RS
        g_mamb = 3.0 + 0.4 * v
        q_m_amb = g_mamb * (To - Ta)
        d[self.iW] = q_cu - q_ws - q_wo
        d[self.iS] = q_fe + q_ws + q_rs - q_so
        d[self.iR] = q_rot - q_ro - q_rs
        d[self.iO] = q_mech + q_gear + q_wo + q_so + q_ro - q_hx - q_m_amb
        d[self.iDL] = q_inv_cool + q_dcdc + q_obc + q_hx - q_rad_d
        # if drive loop is idle while charging, it still exchanges with its radiator: fine (area_d=0 -> none)
        # ---- SOC
        d[self.iSOC] = -I_cell / (CELL_AH * 3600)
        # ---- energy accumulators
        q_gen = sum(q_cell) * Npc + q_inv + q_cu + q_fe + q_rot + q_mech + q_gear + q_dcdc + q_obc
        d[self.iE + 0] = q_gen
        d[self.iE + 1] = q_rad_b + q_rad_d
        d[self.iE + 2] = q_case_amb + q_m_amb
        d[self.iE + 3] = heater
        d[self.iE + 4] = chill
        # divide temperatures by capacitance
        for i in range(self.iE):
            if i in (self.iSc, self.iSk, self.iSOC): continue
            d[i] /= self.caps[i]
        if record:
            return dict(t=t, v=v, P_batt=P_batt, I_cell=I_cell, q_pack=sum(q_cell) * Npc, q_inv=q_inv,
                        q_motor=q_cu + q_fe + q_rot + q_mech, q_gear=q_gear, q_rad_b=q_rad_b, q_rad_d=q_rad_d,
                        q_case=q_case_amb, heater=heater, chill=chill, derate=derate, i_frac=i_frac,
                        Tj=Tinv + R_JC * q_inv / 6 * 1.15, q_cell_sent=qs, T_in=T_in,
                        core_peak=Tsc + (CORE_PEAK - 1) * (Tsc - Tsk), fans=fans_b + fans_d)
        return d

    def run(self, t_end, dt=0.25, stop_soc=True, save_every=4.0):
        """Fixed-step classical RK4 (scipy.integrate's LAPACK DLLs are blocked by this machine's application-control
        policy). dt 0.25 s is under a tenth of the fastest node time constant (ribbon coolant, ~0.7 s)."""
        x = self.x0.copy(); t = 0.0; T = [0.0]; Y = [x.copy()]; next_save = save_every
        while t < t_end - 1e-9:
            h = min(dt, t_end - t)
            k1 = self.rhs(t, x); k2 = self.rhs(t + h / 2, x + h / 2 * k1)
            k3 = self.rhs(t + h / 2, x + h / 2 * k2); k4 = self.rhs(t + h, x + h * k3)
            x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += h
            stop = (stop_soc and self.mode == 'drive' and x[self.iSOC] <= self.soc_stop) or                    (self.mode == 'charge' and x[self.iSOC] >= self.soc_target)
            if t >= next_save or stop or t >= t_end - 1e-9:
                T.append(t); Y.append(x.copy()); next_save += save_every
            if stop: break
        class S: pass
        self.sol = S(); self.sol.t = np.array(T); self.sol.y = np.array(Y).T
        return self.sol

    def energy_balance(self):
        x0, x1 = self.sol.y[:, 0], self.sol.y[:, -1]
        stored = float(np.sum(self.caps[:self.iE] * (x1[:self.iE] - x0[:self.iE])))
        gen, rad, amb, heat, chill = x1[self.iE:self.iE + 5]
        resid = gen + heat - rad - amb - chill - stored
        return dict(generated_MJ=gen / 1e6, heater_MJ=heat / 1e6, to_radiators_MJ=rad / 1e6, to_ambient_MJ=amb / 1e6,
                    chiller_MJ=chill / 1e6, stored_MJ=stored / 1e6, residual_MJ=resid / 1e6,
                    residual_pct_of_in=100 * resid / max(gen + heat, 1.0))

    def series(self, every=1):
        s = self.sol; rec = [self.rhs(t, s.y[:, k], record=True) for k, t in enumerate(s.t) if k % every == 0]
        y = s.y[:, ::every]
        n = N_SEG
        out = dict(t=np.array([r['t'] for r in rec]))
        for k in rec[0]:
            out[k] = np.array([r[k] for r in rec])
        out['T_core'] = y[self.iC:self.iC + n]; out['T_can'] = y[self.iK:self.iK + n]; out['T_cool'] = y[self.iQ:self.iQ + n]
        out['T_sent'] = y[self.iSc]; out['T_case'] = y[self.iCase]; out['T_BL'] = y[self.iBL]
        out['T_inv'] = y[self.iInv]; out['T_w'] = y[self.iW]; out['T_s'] = y[self.iS]; out['T_r'] = y[self.iR]
        out['T_o'] = y[self.iO]; out['T_DL'] = y[self.iDL]; out['soc'] = y[self.iSOC]
        return out
