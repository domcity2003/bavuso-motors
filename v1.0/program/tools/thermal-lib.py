"""Bavuso V1 thermal library (rev C: P60B 100s11p, 4-lane pack, ONE shared coolant loop, EMRAX 228 LC, CM200DX).

Loaded with importlib by the thermal-*.py scripts. Units SI, temperatures in degC.
Tags: [supplier] datasheet, [calc] computed, [est] my estimate. Methods reused from detailed-design/tools/thermal-lib.py
(RK4 lumped network, e-NTU radiator, sentinel hottest cell, energy accumulators) and the drive models in program/tools/drive-lib.py.
Loop topology (parallel branches off one pump):
   radiator -> [valve: bypass while heating] -> 3 kW PTC -> split:
      pack branch  : 28 serpentine ribbons in parallel (7 per lane x 4 lanes), 5 segments along each ribbon
      drive branch : EMRAX 228 jacket -> CM200DX cold plate -> charger/DC-DC plate -> back
Coolant is not a state inside the branches (small volumes, e-NTU per device); one lumped loop node carries the coolant and radiator mass.
"""
import importlib.util, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
dl = _load('drive_lib', 'drive-lib.py')
MPH = dl.MPH

# ---------------------------------------------------------------- cell / pack
N_CELL, N_S, N_P = 1100, dl.N_S, dl.N_P
CELL_AH = dl.CELL_AH
CELL_M = 0.075                     # kg [supplier max]
C_CELL = CELL_M * 1000.0           # J/K (cp 1000 J/kgK cylindrical NMC [est, Drake 2014])
C_CAN = 8.0                        # J/K steel can + caps [est]
C_CORE = C_CELL - C_CAN
N_RIB = 28                         # ribbons: 7 bands per lane x 4 lanes (14 rows per lane) [calc]
CELLS_PER_RIB = N_CELL / N_RIB     # 39.3
N_SEG = 5
HEAT_F = 1.08 * 1.10               # busbar overhead (drive-lib) x 1.10 diffusion polarisation over minutes [est]
C_PACK_OTHER = 9.5e3 + 3.0e3       # J/K: 4 mm Al case (0.98 m2) + busbars, plates, foam [est]
CASE_AREA = 0.98                   # m2 outer box 507 x 333 x 379 mm [calc from CAD box]
G_EDGE_CASE = 12.0                 # W/K edge cells to wall [est]
def g_case_air(v): return CASE_AREA * (9.0 + 0.15 * v)

def r_cell_heat(T, soc):
    """Heat-generating cell resistance incl. busbar overhead and diffusion factor (ohm)."""
    return dl.R_CELL_DC50 * float(np.interp(soc, dl.SOC_PTS, dl.RSOC_PTS)) * dl.r_temp(T) * HEAT_F
def r_term(T, soc):
    """Pack terminal resistance while charging (ohm), incl. 6 mohm fuse + contactors outside the pack."""
    return dl.N_S / dl.N_P * r_cell_heat(T, soc) + dl.R_PACK_EXTRA

# Cell internal path: 2-D finite difference, anisotropic jelly roll (kr 0.6, ka 25 W/mK [est, Drake 2014]); P60B dims [supplier]
R_ROLL, L_ROLL = 0.0103, 0.066
def cell_fd(kr=0.6, ka=25.0, nr=16, nz=32, P=1.0, r_roll=R_ROLL, l_roll=L_ROLL):
    dr, dz = r_roll / nr, l_roll / nz
    rc = (np.arange(nr) + 0.5) * dr; vol = 2 * math.pi * rc * dr * dz
    q = P / (math.pi * r_roll ** 2 * l_roll)
    N = nr * nz; A = np.zeros((N, N)); b = np.zeros(N); idx = lambda i, j: i * nz + j
    for i in range(nr):
        for j in range(nz):
            k = idx(i, j); b[k] = q * vol[i]
            if i > 0:
                g = kr * 2 * math.pi * (rc[i] - dr / 2) * dz / dr; A[k, k] += g; A[k, idx(i - 1, j)] -= g
            if i < nr - 1:
                g = kr * 2 * math.pi * (rc[i] + dr / 2) * dz / dr; A[k, k] += g; A[k, idx(i + 1, j)] -= g
            else:
                g = kr * 2 * math.pi * r_roll * dz / (dr / 2); A[k, k] += g
            for jj in (j - 1, j + 1):
                area = 2 * math.pi * rc[i] * dr
                if 0 <= jj < nz:
                    g = ka * area / dz; A[k, k] += g; A[k, idx(i, jj)] -= g
                else:
                    g = ka * area / (dz / 2); A[k, k] += g
    T = np.linalg.solve(A, b).reshape(nr, nz)
    return float(np.sum(T * vol[:, None]) / np.sum(vol) / nz), float(T.max())
_m, _p = cell_fd(nr=16, nz=32)
R_CORE_CAN = _m                    # K/W mean core to can [calc]
CORE_PEAK = _p / _m                # hot spot / mean rise
ARC_PENALTY = 1.3                  # ribbon touches ~60 deg of the can [est]
# can -> coolant: adhesive 0.2 mm k2 + 50 um dielectric (k 0.3) over a 60 deg arc (11.3 x 70.2 mm) + laminar ribbon ports
A_CONTACT = math.radians(60) * 0.0108 * 0.0702
R_TIM = 0.2e-3 / (2.0 * A_CONTACT) + 50e-6 / (0.3 * A_CONTACT)
RIB_PORTS, RIB_W, RIB_H, RIB_LEN = 8, 7.5e-3, 0.8e-3, 0.60       # ribbon 70 wide x 1.2 thick, 8 ports of 7.5 x 0.8 mm, 0.6 m serpentine [est design]
RIB_DH = 2 * RIB_W * RIB_H / (RIB_W + RIB_H)
H_RIB = 5.4 * 0.40 / RIB_DH                                       # laminar Nu 5.4, k 0.40 W/mK
RIB_WET = RIB_PORTS * 2 * (RIB_W + RIB_H) * RIB_LEN               # m2 per ribbon
R_RIB = 1.0 / (H_RIB * RIB_WET / CELLS_PER_RIB)                   # K/W per cell
R_CW = R_TIM + R_RIB

# ---------------------------------------------------------------- coolant and loop
CP_C, RHO_C = 3400.0, 1065.0       # 50/50 EG-water
def mcp(lpm): return lpm / 60000.0 * RHO_C * CP_C
Q_PACK_LPM, Q_DRIVE_LPM = 10.0, 12.0   # CM200DX 12 L/min [supplier shortlist]; EMRAX min 6 L/min [supplier]
C_LOOP = 3.0e3 * 3.4 + 1.2e3           # J/K: ~3 L coolant outside the cells/branch devices + hoses [est]
PUMP_HEAT_W = 50.0                 # pump electrical 80 W: ~20 W hydraulic + motor losses into the coolant [est]

# ---------------------------------------------------------------- limits
LIM = dict(cell_max=60.0, cell_bms=55.0, spread_max=10.0, spread_goal=5.0,
           motor_inlet=50.0, winding=100.0, inverter_inlet=65.0, charger_inlet=60.0)
# [supplier] P60B -20..60 C; EMRAX 228 LC min 6 L/min and max 50 C inlet (datasheet v1.7 cooling table), winding sensor 100 C.
# [est] CM200DX 65 C inlet (the supplier says current capacity depends on coolant temperature, no curve); charger/DC-DC 60 C.

# ---------------------------------------------------------------- radiator and fan
UA5_PER_M2 = 3400.0                # W/K per m2 face at 5 m/s, 32 mm deep (Kays & London class, as thermal-study.md) [est]
RHO_AIR = 1.16
RAM = 0.25                         # face velocity / road speed with the pod scoop [est; CFD needed]
FANS = {   # through-core flow per fan (m3/s), electrical W, mass kg
    'slim': dict(q=0.035, w=25.0, kg=0.25),     # 24 mm slim fan of the rev C CAD [est]
    'mid':  dict(q=0.060, w=45.0, kg=0.38),     # ~140 mm brushless [est]
    'big':  dict(q=0.090, w=90.0, kg=0.55),     # 7.5 in SPAL class, 366-437 CFM free air x 0.55 through a core (thermal-study.md)
}
class Rad:
    def __init__(self, h=0.128, w=0.165, d=0.028, n=2, fan='slim', ram=None):
        self.h, self.w, self.d, self.n, self.fan, self.ram = h, w, d, n, fan, (RAM if ram is None else ram)
        self.area = h * w * n
    @property
    def volume(self): return self.area * self.d
    def ua5(self): return UA5_PER_M2 * self.area * (self.d / 0.032) ** 0.9
    def mass(self): return 0.805 * (self.area / 0.0294) * (0.35 + 0.65 * self.d / 0.032)   # dry core + tanks, scaled from thermal-study.md
    def coolant_l(self): return 0.22 * self.volume * 1000 + 0.06 * self.n
    def fan_flow(self): return FANS[self.fan]['q'] * self.n * (0.028 / self.d) ** 0.5
    def q(self, T_in, T_amb, v_face, C_cool):
        if v_face <= 0 or T_in <= T_amb: return 0.0
        C_air = RHO_AIR * self.area * v_face * 1007.0
        UA = self.ua5() * (v_face / 5.0) ** 0.5
        Cmin, Cmax = min(C_air, C_cool), max(C_air, C_cool); Cr = Cmin / Cmax; NTU = UA / Cmin
        eps = 1 - math.exp((NTU ** 0.22 / Cr) * (math.exp(-Cr * NTU ** 0.78) - 1))
        return eps * Cmin * (T_in - T_amb)

# ---------------------------------------------------------------- drive-side parts
C_MOT, R_MOT = dl.C_MOTOR, dl.RTH_WINDING         # 8.5 kJ/K; 0.0217 K/W winding to coolant [calc from the LC S1 rating, drive-lib]
C_INV, R_INV = 3000.0, 1.0 / 40.0                 # inverter case node [est, as 06]
C_DC, R_DC = 800.0, 0.05                          # charger / DC-DC plate [est]
DCDC_EFF, OBC_EFF = 0.93, 0.94
HEATER_ON_BELOW = 20.0                            # BMS runs the PTC while the coldest can is below this
drv = dl.Drive(3.6)

def derate_charge(t_min, t_hot):
    """Charge-current fraction: cold side 0 at 0 C, 0.5 at 10, 1 at 20; hot side 1 to 40 C, 0 at 55 C (same map as drive-charge.py) [est]."""
    c = 0.0 if t_min <= 0 else (0.5 * t_min / 10 if t_min < 10 else (0.5 + 0.5 * (t_min - 10) / 10 if t_min < 20 else 1.0))
    h = 1.0 if t_hot <= 40 else (1.0 - (t_hot - 40) / 15.0 if t_hot < 55 else 0.0)
    return min(c, h)

class Sim:
    """mode 'drive' (profile fn(t)->(v m/s, a m/s2, grade)), 'charge' (DC), 'ac' (onboard charger)."""
    def __init__(self, rad, T_amb=25.0, mode='drive', profile=None, soc0=95.0, T0=None, heater_w=3000.0, c_cap=3.0,
                 soc_stop=5.0, soc_target=80.0, chg_p=250e3, chg_i=600.0, cda=dl.CDA, flow_scale=1.0, r_scale=1.0):
        self.rad, self.Ta, self.mode, self.prof = rad, T_amb, mode, profile
        self.heater_w, self.c_cap, self.soc_stop, self.soc_target = heater_w, c_cap, soc_stop, soc_target
        self.chg_p, self.chg_i, self.cda, self.rs = chg_p, chg_i, cda, r_scale
        self.mp, self.md = mcp(Q_PACK_LPM * flow_scale), mcp(Q_DRIVE_LPM * flow_scale); self.mt = self.mp + self.md
        self.m_r = self.mp / N_RIB
        T0 = T_amb if T0 is None else T0
        n = N_SEG
        self.i = dict(Tsc=2 * n, Tsk=2 * n + 1, Tcase=2 * n + 2, TL=2 * n + 3, Tinv=2 * n + 4, Tw=2 * n + 5, Tdc=2 * n + 6)
        self.nT = 2 * n + 7
        self.x0 = np.full(self.nT, float(T0))
        self.soc = soc0
        npc = N_CELL / n
        cap = np.zeros(self.nT)
        cap[0:n] = C_CORE * npc; cap[n:2 * n] = C_CAN * npc
        cap[2 * n + 2] = C_PACK_OTHER
        cap[2 * n + 3] = C_LOOP + rad.coolant_l() * RHO_C * CP_C / 1000 + rad.mass() * 900
        cap[2 * n + 4] = C_INV; cap[2 * n + 5] = C_MOT; cap[2 * n + 6] = C_DC
        self.cap = cap
        self.R_cc = R_CORE_CAN * ARC_PENALTY

    def loads(self, t, x):
        n = N_SEG; i = self.i
        Tc, Tk = x[0:n], x[n:2 * n]
        Tsk = x[i['Tsk']]
        Tcells = float(np.mean(Tc)); Tw = x[i['Tw']]
        L = dict(v=0.0, q_cell=0.0, q_inv=0.0, q_mot=0.0, q_dc=0.0, heater=0.0, i_cell=0.0, p_dc=0.0, p_wheel=0.0, derate=1.0,
                 p_station=0.0, p_ext=0.0, e_ok=True, i_dc=0.0, ocv_w=0.0, r_lib=0.0, belt=0.0)
        if self.mode == 'drive':
            v, a, gr = self.prof(t)
            pw = v * (dl.road_force(v, self.cda, gr) + (dl.M_TOT + dl.rot_mass(drv.G, max(v, 1.0))) * a)
            bl = dl.belt_loss(pw); ps = pw + bl
            n_rpm = drv.rpm(max(v, 0.3)); w = max(n_rpm * math.pi / 30.0, 1.0)
            T = max(min(ps / w, dl.T_PEAK), -dl.T_PEAK)
            e = drv.electrical(T, n_rpm, self.soc, Tcells, Tw, p_aux=dl.AUX_W)
            if e is None:
                L['e_ok'] = False; return L
            i_cell = e['i_dc'] / N_P
            L.update(v=v, i_cell=i_cell, i_dc=e['i_dc'], q_cell=N_CELL * i_cell ** 2 * r_cell_heat(Tcells, self.soc) * self.rs,
                     q_inv=e['p_inv'], q_mot=e['cu'] + e['fe'], q_dc=dl.AUX_W * (1 - DCDC_EFF), p_dc=e['p_dc'] + dl.AUX_W,
                     p_wheel=pw, belt=bl, T=T, rpm=n_rpm, i_rms=e['i_rms'], p_shaft=ps, p_ext=dl.R_PACK_EXTRA * e['i_dc'] ** 2,
                     ocv_w=dl.ocv_pack(self.soc) * e['i_dc'], r_lib=e['i_dc'] ** 2 * dl.r_pack(self.soc, Tcells))
        elif self.mode in ('charge', 'ac'):
            tmin = float(min(np.min(Tk), np.min(Tc)))
            e0 = dl.ocv_pack(self.soc); rk = r_term(Tcells, self.soc)
            if self.mode == 'charge':
                d = derate_charge(tmin, Tsk)
                i = min(self.c_cap * CELL_AH, dl.I_CHG_MAX) * d * N_P
                i = min(i, self.chg_i, self.chg_p / max(e0 + i * rk, 1.0))
                i = max(0.0, min(i, (N_S * 4.2 - e0) / rk))
                L['derate'] = d; q_dc = 60.0
            else:
                i = 3300.0 * OBC_EFF / max(e0, 1.0); q_dc = 3300.0 * (1 / OBC_EFF - 1) + 60.0
            if self.soc >= self.soc_target: i = 0.0
            i_cell = i / N_P
            L.update(i_cell=-i_cell, i_dc=-i, q_cell=N_CELL * i_cell ** 2 * r_cell_heat(Tcells, self.soc) * self.rs,
                     p_station=(e0 + i * rk) * i, ocv_w=-e0 * i, p_ext=dl.R_PACK_EXTRA * i * i, q_dc=q_dc)
            if self.heater_w > 0 and tmin < HEATER_ON_BELOW: L['heater'] = self.heater_w
        return L

    def rhs(self, x, L, v_air, fan_on, f_rad):
        n = N_SEG; i = self.i
        d = np.zeros(self.nT)
        Tc, Tk = x[0:n], x[n:2 * n]
        TL, Tinv, Tw, Tdc, Tcase = x[i['TL']], x[i['Tinv']], x[i['Tw']], x[i['Tdc']], x[i['Tcase']]
        Tsc, Tsk = x[i['Tsc']], x[i['Tsk']]
        rad = self.rad
        v_face = max(rad.ram * v_air, rad.fan_flow() / rad.area if fan_on else 0.0)
        q_rad = f_rad * rad.q(TL, self.Ta, v_face, self.mt)
        T_in = TL - q_rad / self.mt + L['heater'] / self.mt
        npc = N_CELL / n
        eps_p = 1 - math.exp(-((CELLS_PER_RIB / n) / R_CW) / self.m_r)
        Tq = T_in; q_cw_tot = 0.0
        qcell = L['q_cell'] / n
        gcc = npc / self.R_cc
        q_edge = G_EDGE_CASE * (float(np.mean(Tk)) - Tcase)
        Tq_in_last = T_in
        for k in range(n):
            q = eps_p * self.m_r * (Tk[k] - Tq) * N_RIB
            qcc = gcc * (Tc[k] - Tk[k])
            d[k] = qcell - qcc
            d[n + k] = qcc - q - q_edge / n
            q_cw_tot += q
            Tq_in_last = Tq
            Tq = Tq + q / self.mp
        qs = 1.10 * (L['q_cell'] / N_CELL)
        d[i['Tsc']] = (qs - (Tsc - Tsk) / self.R_cc)
        d[i['Tsk']] = ((Tsc - Tsk) / self.R_cc - (Tsk - Tq_in_last) / (1.25 * R_CW))
        md = self.md
        epm = 1 - math.exp(-1.0 / (R_MOT * md)); q_m = epm * md * (Tw - T_in); T1 = T_in + q_m / md
        epi = 1 - math.exp(-1.0 / (R_INV * md)); q_i = epi * md * (Tinv - T1); T2 = T1 + q_i / md
        epd = 1 - math.exp(-1.0 / (R_DC * md)); q_d = epd * md * (Tdc - T2)
        d[i['Tw']] = L['q_mot'] - q_m
        d[i['Tinv']] = L['q_inv'] - q_i
        d[i['Tdc']] = L['q_dc'] - q_d
        q_case_amb = g_case_air(v_air) * (Tcase - self.Ta)
        d[i['Tcase']] = q_edge - q_case_amb
        d[i['TL']] = q_cw_tot + q_m + q_i + q_d + L['heater'] + PUMP_HEAT_W - q_rad
        for k in range(self.nT):
            if k == i['Tsc'] or k == i['Tsk']: continue
            d[k] /= self.cap[k]
        d[i['Tsc']] /= C_CORE; d[i['Tsk']] /= C_CAN
        info = dict(q_rad=q_rad, q_case=q_case_amb, T_in=T_in, T1=T1, T2=T2, q_pack_cool=q_cw_tot, q_m=q_m, q_i=q_i, q_d=q_d, v_face=v_face)
        return d, info

    def run(self, t_end, dt=0.5, rec_every=10.0):
        x = self.x0.copy(); t = 0.0; i = self.i; n = N_SEG
        self.series = []; next_rec = 0.0; self.stop = 'time'
        gen_e = rad_e = case_e = heat_e = fan_e = 0.0
        def stored_of(xx): return float(np.sum(self.cap[:2 * n] * xx[:2 * n]) + np.sum(self.cap[i['Tcase']:] * xx[i['Tcase']:]))
        stored0 = stored_of(x)
        self.peak = dict(core_hot=-1e9, can_hot=-1e9, spread=0.0, T_in=-1e9, T1=-1e9, T2=-1e9, Tw=-1e9, Tinv=-1e9, Tdc=-1e9, TL=-1e9, tmin_can=1e9, i_cell=0.0, p_station=0.0)
        self.time_over = dict(inlet50=None, core55=None, core60=None, winding100=None)
        self.en = dict(station=0.0, ocv=0.0, wheel=0.0, belt=0.0, motor=0.0, inv=0.0, rlib=0.0, aux=0.0, cell_heat=0.0, ext=0.0, batt_terminal=0.0, fan_el=0.0, pump_el=0.0)
        while t < t_end - 1e-9:
            h = min(dt, t_end - t)
            L = self.loads(t, x)
            if not L['e_ok']: self.stop = 'power'; break
            v_air = L['v']
            fan_on = (v_air < 15.0 or self.mode in ('charge', 'ac')) and x[i['TL']] > self.Ta + 2.0
            fr = 0.0 if L['heater'] > 0 else 1.0
            f = lambda xx: self.rhs(xx, L, v_air, fan_on, fr)[0]
            k1 = f(x); k2 = f(x + h / 2 * k1); k3 = f(x + h / 2 * k2); k4 = f(x + h * k3)
            _, info = self.rhs(x, L, v_air, fan_on, fr)
            xn = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            gen = L['q_cell'] + L['q_inv'] + L['q_mot'] + L['q_dc'] + PUMP_HEAT_W
            gen_e += gen * h; rad_e += info['q_rad'] * h; case_e += info['q_case'] * h; heat_e += L['heater'] * h
            fan_p = FANS[self.rad.fan]['w'] * self.rad.n if fan_on else 0.0
            en = self.en
            en['fan_el'] += fan_p * h; en["pump_el"] += 80.0 * h
            en['station'] += L['p_station'] * h; en['ocv'] += L['ocv_w'] * h; en['wheel'] += L['p_wheel'] * h; en['belt'] += L['belt'] * h
            en['motor'] += L['q_mot'] * h; en['inv'] += L['q_inv'] * h; en['rlib'] += L['r_lib'] * h; en['cell_heat'] += L['q_cell'] * h
            en['ext'] += L['p_ext'] * h
            if self.mode == 'drive': en['aux'] += dl.AUX_W * h
            self.soc += -L['i_dc'] * h / (dl.PACK_AH * 3600.0) * 100.0
            x = xn; t += h
            Tc, Tk = x[:n], x[n:2 * n]
            core_hot = x[i['Tsc']] + (CORE_PEAK - 1) * (x[i['Tsc']] - x[i['Tsk']])
            spread = max(core_hot, float(np.max(Tc))) - float(np.min(Tc))
            p = self.peak
            p["core_mean"] = max(p.get("core_mean", -1e9), float(np.mean(Tc))); p["core_hot"] = max(p["core_hot"], core_hot); p['can_hot'] = max(p['can_hot'], x[i['Tsk']], float(np.max(Tk)))
            p['spread'] = max(p['spread'], spread); p['T_in'] = max(p['T_in'], info['T_in']); p['T1'] = max(p['T1'], info['T1']); p['T2'] = max(p['T2'], info['T2'])
            p['Tw'] = max(p['Tw'], x[i['Tw']]); p['Tinv'] = max(p['Tinv'], x[i['Tinv']]); p['Tdc'] = max(p['Tdc'], x[i['Tdc']]); p['TL'] = max(p['TL'], x[i['TL']])
            p['tmin_can'] = min(p['tmin_can'], float(np.min(Tk))); p['i_cell'] = max(p['i_cell'], abs(L['i_cell'])); p['p_station'] = max(p['p_station'], L['p_station'])
            to = self.time_over
            if to['inlet50'] is None and info['T_in'] > LIM['motor_inlet']: to['inlet50'] = t
            if to['core55'] is None and core_hot > 55: to['core55'] = t
            if to['core60'] is None and core_hot > 60: to['core60'] = t
            if to['winding100'] is None and x[i['Tw']] > LIM['winding']: to['winding100'] = t
            if t >= next_rec - 1e-9:
                self.series.append(dict(t=round(t, 1), soc=round(self.soc, 2), mph=round(v_air / MPH, 1), Tc_mean=round(float(np.mean(Tc)), 2), Tcore_hot=round(core_hot, 2),
                                        Tcan_hot=round(x[i['Tsk']], 2), Tcell_min=round(float(np.min(Tc)), 2), TL=round(x[i['TL']], 2), T_in=round(info['T_in'], 2),
                                        Tw=round(x[i['Tw']], 2), Tinv=round(x[i['Tinv']], 2), Tdc=round(x[i['Tdc']], 2), q_cell_W=round(L['q_cell']), q_mot_W=round(L['q_mot']),
                                        q_inv_W=round(L['q_inv']), q_rad_W=round(info['q_rad']), i_cell_A=round(L['i_cell'], 2), p_station_kW=round(L['p_station'] / 1e3, 1),
                                        derate=round(L['derate'], 3), heater_W=L['heater']))
                next_rec += rec_every
            if self.mode == 'drive' and self.soc <= self.soc_stop: self.stop = 'soc'; break
            if self.mode in ('charge', 'ac') and self.soc >= self.soc_target: self.stop = 'target'; break
        self.t_end = t; self.x = x
        stored = stored_of(x) - stored0
        resid = gen_e + heat_e - rad_e - case_e - stored
        self.balance = dict(generated_MJ=gen_e / 1e6, heater_MJ=heat_e / 1e6, to_radiator_MJ=rad_e / 1e6, to_case_air_MJ=case_e / 1e6, stored_MJ=stored / 1e6,
                            residual_MJ=resid / 1e6, residual_pct=100 * resid / max(gen_e + heat_e, 1.0))
        return self

    def summary(self):
        p, to = self.peak, self.time_over
        return dict(minutes=round(self.t_end / 60, 1), stop=self.stop, soc_end=round(self.soc, 1),
                    core_hot_max=round(p["core_hot"], 1), core_mean_max=round(p["core_mean"], 1), can_hot_max=round(p['can_hot'], 1), spread_max=round(p['spread'], 1),
                    coolant_inlet_max=round(p['T_in'], 1), inverter_inlet_max=round(p['T1'], 1), charger_inlet_max=round(p['T2'], 1),
                    winding_max=round(p['Tw'], 1), inverter_case_max=round(p['Tinv'], 1), loop_max=round(p['TL'], 1),
                    tmin_can=round(p['tmin_can'], 1), peak_cell_a=round(p['i_cell'], 1), peak_station_kw=round(p['p_station'] / 1e3, 1),
                    t_inlet50_min=None if to['inlet50'] is None else round(to['inlet50'] / 60, 1),
                    t_core55_min=None if to['core55'] is None else round(to['core55'] / 60, 1),
                    t_core60_min=None if to['core60'] is None else round(to['core60'] / 60, 1),
                    t_winding100_min=None if to['winding100'] is None else round(to['winding100'] / 60, 1),
                    balance={k: round(v, 4) for k, v in self.balance.items()})

# ---------------------------------------------------------------- duty profiles  (t) -> (v m/s, a m/s2, grade)
def steady(mph, grade=0.0):
    return lambda t: (mph * MPH, 0.0, grade)
def hard_ride_cycle():
    """90 s cycle of spirited mountain-road riding [est]: 8 s hard pull 40->90 mph, 22 s at 90, 10 s braking to 45 mph
    (regen capped at 0.25 g, program/06), 20 s at 50, 6 s pull 45->80, 24 s at 70."""
    segs = [(8, 40, 90), (22, 90, 90), (10, 90, 45), (20, 50, 50), (6, 45, 80), (24, 70, 70)]
    T = sum(s[0] for s in segs)
    def prof(t):
        tt = t % T; acc = 0.0
        for dur, a, b in segs:
            if tt < acc + dur:
                f = (tt - acc) / dur
                aa = max((b - a) * MPH / dur, -0.25 * dl.G0)
                return ((a + (b - a) * f) * MPH, aa, 0.0)
            acc += dur
        return (70 * MPH, 0.0, 0.0)
    return prof
def mountain_profile(t_climb=25 * 60):
    """25 min climb at 55 mph on a 7.5 % grade, then a descent at 45 mph on -7.5 % with regen."""
    return lambda t: (55 * MPH, 0.0, 0.075) if t < t_climb else (45 * MPH, 0.0, -0.075)
