"""Bavuso V1 drive library: shared models for the drive-*.py scripts.

Run the scripts from v1.0 with FreeCAD python:
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drive-design.py

Every constant is tagged [supplier], [calc] or [est] (estimate = my engineering judgement, to be replaced
by measured data).  Sources:
  P60B     Molicel INR-21700-P60B product data sheet v0.1 (molicel.com)            [supplier]
  EMRAX    EMRAX 228 datasheet v1.7 (v1.0/sources/EMRAX-228-datasheet-v1.7.pdf)    [supplier]
  CM200DX  cascadiamotion.com/cm-200                                               [supplier]
  Gates    Poly Chain GT Carbon Drive Design Manual (gates.com), 8mm tables p.52-55 [supplier]
  Gate A   program/GATE-A-targets-locked.md (road-load model: rho 1.225, Crr 0.015, CdA 0.38, aux 300 W)
"""
import math
import numpy as np

MPH = 0.44704
G0 = 9.80665
RHO = 1.225

# ------------------------------------------------------------------ vehicle (Gate A)
BIKE_KG = 257.5   # Nov 22 final roll-up (mass-rollup.json; was 240.0 in the Nov 21 run)
RIDER_KG = 90.0
M_TOT = BIKE_KG + RIDER_KG
CDA = 0.38
CRR = 0.015
AUX_W = 300.0
# Rear tyre 150/70R17 (hardware shortlist). Free diameter = 17*25.4 + 2*0.70*150 = 641.8 mm. [calc]
TYRE_FREE_R = (17 * 25.4 + 2 * 0.70 * 150) / 2000.0   # 0.3209 m
R_E0 = 0.98 * TYRE_FREE_R                              # effective rolling radius at low speed [est]  0.3145
def r_eff(v):
    """Rolling radius grows about 1.5% from 0 to 60 m/s (centrifugal growth) [est]."""
    return R_E0 * (1.0 + 0.015 * min(v, 60.0) / 60.0)
# CoG (rider on) from mass-rollup.md: 738 mm ahead of rear axle, 643 mm high; wheelbase ~1480 mm.  [calc, old 283 kg roll-up]
COG_B, COG_H, WHEELBASE = 0.732, 0.667, 1.490  # Nov 22: rev D bike+rider per 15-dynamics (was 0.738, 0.643, 1.480)
# Rotating inertia reflected to the wheel (kg equivalent): wheels 2 x ~0.62 kg m2 / r^2 plus motor rotor [est]
I_WHEELS = 2 * 0.62
J_MOTOR = 0.0398 + 0.004   # EMRAX 228 LC rotor 0.0398 kg m2 [supplier] + pulley/shaft [est]

# ------------------------------------------------------------------ pack: Molicel P60B 100s11p
N_S, N_P = 100, 11
CELL_AH = 6.0            # typical [supplier] (min 5.85)
CELL_WH = 21.6           # typical [supplier]
CELL_KG = 0.075          # max [supplier]
I_CHG_STD, I_CHG_MAX = 6.0, 30.0   # A per cell [supplier]; 30 A = 5C, 70 C cell cut-off
I_DIS_CONT, I_DIS_MAX = 60.0, 100.0  # A per cell [supplier], 90 C cut-off for 60 A
R_CELL_DC50 = 12.8e-3    # DC impedance 50% SOC [supplier]; AC 6.5 mohm at 30% SOC
PACK_KWH = N_S * N_P * CELL_WH / 1000.0   # 23.76
PACK_AH = N_P * CELL_AH
PACK_CAP_J_PER_K = 95e3  # cells 82.5 kg x 0.9 + case/plates 18.75 kg x 0.9 + coolant [est]
SOC_PTS = np.array([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100.0])
OCV_PTS = np.array([3.00, 3.30, 3.40, 3.52, 3.60, 3.67, 3.74, 3.81, 3.89, 3.98, 4.08, 4.20])  # NMC/NCA-class 21700 [est]
RSOC_PTS = np.array([1.9, 1.55, 1.35, 1.15, 1.05, 1.0, 1.0, 0.98, 0.96, 0.95, 0.95, 0.95])      # R vs SOC multiplier [est]
R_PACK_EXTRA = 0.006     # fuse + 2 contactors + cabling [est]
R_PACK_INTERCONNECT = 1.08  # busbar / nickel strip overhead on cell resistance [est]
USABLE_SOC = (5.0, 95.0)   # 90% usable window (Gate A: 21.4 of 23.8 kWh)

def ocv_cell(soc):
    return np.interp(soc, SOC_PTS, OCV_PTS)

def r_temp(t_c):
    """Cell resistance multiplier vs temperature, 1.0 at 23 C (Arrhenius, Ea/k = 2200 K) [est]."""
    return math.exp(2200.0 * (1.0 / (t_c + 273.15) - 1.0 / 296.15))

def r_pack(soc, t_c=25.0):
    rc = R_CELL_DC50 * np.interp(soc, SOC_PTS, RSOC_PTS) * r_temp(t_c)
    return N_S / N_P * rc * R_PACK_INTERCONNECT + R_PACK_EXTRA

def ocv_pack(soc):
    return N_S * ocv_cell(soc)

def pack_current_for_power(p_w, soc, t_c):
    """DC current (A, discharge positive) that delivers p_w at the terminals (negative p = charging)."""
    e, r = ocv_pack(soc), r_pack(soc, t_c)
    disc = e * e - 4.0 * r * p_w
    if disc < 0:
        return None
    return (e - math.sqrt(disc)) / (2.0 * r)

# ------------------------------------------------------------------ motor: EMRAX 228 (all values datasheet v1.7)
# per winding: Kt Nm/Arms (peak), Ipk Arms (S2 30 s), Icont Arms (LC), R mohm phase (25 C), L uH (avg Ld/Lq),
# V_req volts for peak power, n_pk rpm at peak power, Kv_peak rpm/V at peak load
WINDINGS = {
    'HV':       dict(kt=0.98, ipk=235, icont=120, r=16.09e-3, l=177.5e-6, vreq=830, npk=4500, kvpk=5.65,  ppk=104),
    'MV':       dict(kt=0.64, ipk=360, icont=180, r=6.95e-3,  l=76.2e-6,  vreq=630, npk=5500, kvpk=8.68,  ppk=124),
    'LV':       dict(kt=0.24, ipk=920, icont=470, r=1.36e-3,  l=10.35e-6, vreq=250, npk=5500, kvpk=21.91, ppk=124),
    'LV+43%':   dict(kt=0.34, ipk=650, icont=330, r=2.55e-3,  l=21.1e-6,  vreq=360, npk=5500, kvpk=15.32, ppk=124),
    'LV+100%':  dict(kt=0.47, ipk=460, icont=240, r=5.31e-3,  l=41.4e-6,  vreq=500, npk=5500, kvpk=10.96, ppk=124),
    'HV+42%':   dict(kt=1.33, ipk=165, icont=85,  r=33.17e-3, l=355e-6,   vreq=830, npk=3200, kvpk=3.96,  ppk=73),
}
POLES = 10                 # pole pairs [supplier]
N_MAX_RPM = 6500           # limiting speed [supplier]
MOTOR_KG = {'AC': 12.9, 'LC': 13.5, 'CC': 13.2}   # [supplier]
MOTOR_CONT_NM_LC = 118.0   # continuous torque, LC, LV+43% [supplier] (CC 130, AC 83)
T_PEAK = 220.0             # Nm [supplier]
FE_KW_5500 = 1.2           # iron + magnet eddy + windage loss at 5500 rpm [est; calibrated so peak efficiency ~96% as the datasheet says]
FE_EXP = 1.8
RTH_WINDING = 50.0 / 2300.0   # K/W, winding to coolant: 2.3 kW total loss at 330 A / 5500 rpm gives 100 C with 50 C coolant [calc from LC S1 rating]
C_MOTOR = 8500.0           # J/K winding + stator + housing [est]
T_WINDING_LIMIT = 100.0    # datasheet sensor limit (100/80/120 C) [supplier]

def r_hot(w, t_c):
    return WINDINGS[w]['r'] * (1.0 + 0.00393 * (t_c - 25.0))

def psi_of(w):
    return WINDINGS[w]['kt'] / (1.5 * POLES * math.sqrt(2.0))

def _iq_max(n_rpm, vdc, w, i_rms_lim, kv_util, t_c=90.0):
    """Max torque at (n, vdc) for winding w with current limit and voltage limit k_v*Vdc/sqrt3 (dq model, Ld=Lq).
    Returns (torque Nm, I_rms total, id_pk)."""
    d = WINDINGS[w]
    psi, L, R = psi_of(w), d['l'], r_hot(w, t_c)
    om = POLES * n_rpm * math.pi / 30.0
    vlim = kv_util * vdc / math.sqrt(3.0)
    ipk = i_rms_lim * math.sqrt(2.0)
    ids = -np.linspace(0.0, ipk, 400)
    A = (om * L) ** 2 + R * R
    B = 2.0 * R * om * psi
    C = (R * ids) ** 2 + (om * psi + om * L * ids) ** 2 - vlim ** 2
    disc = B * B - 4.0 * A * C
    ok = disc >= 0
    iq = np.where(ok, (-B + np.sqrt(np.maximum(disc, 0))) / (2.0 * A), -1.0)
    iq = np.minimum(iq, np.sqrt(np.maximum(ipk ** 2 - ids ** 2, 0.0)))
    k = np.argmax(iq)
    if iq[k] <= 0:
        return 0.0, 0.0, 0.0
    return 1.5 * POLES * psi * iq[k], math.sqrt(ids[k] ** 2 + iq[k] ** 2) / math.sqrt(2.0), ids[k]

_KV_CACHE = {}
def calibrated_kv_util(w):
    """Voltage utilisation that reproduces the datasheet's 'voltage for peak power' corner (n_pk at V_req, full Ipk).
    This is conservative: it carries EMRAX's own margin (datasheet corner is about 0.7 of the ideal SVPWM limit)."""
    if w in _KV_CACHE:
        return _KV_CACHE[w]
    d = WINDINGS[w]
    lo, hi = 0.3, 1.2
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        t, _, _ = _iq_max(d['npk'], d['vreq'], w, d['ipk'], mid)
        full = 1.5 * POLES * psi_of(w) * d['ipk'] * math.sqrt(2.0)
        if t >= 0.999 * full:
            hi = mid
        else:
            lo = mid
    _KV_CACHE[w] = hi
    return hi

class MotorMap:
    """Torque-limit map T_max(n, Vdc) and current used, for one winding and one inverter current limit."""
    def __init__(self, w='LV+43%', i_lim=None, n_max=7200, kv_scale=1.0):
        d = WINDINGS[w]
        self.w = w
        self.i_lim = min(d['ipk'], i_lim) if i_lim else d['ipk']
        self.kv = calibrated_kv_util(w) * kv_scale
        self.ns = np.arange(0, n_max + 1, 100.0)
        self.vs = np.arange(200.0, 481.0, 20.0)
        self.T = np.zeros((len(self.ns), len(self.vs)))
        self.I = np.zeros_like(self.T)
        for i, n in enumerate(self.ns):
            for j, v in enumerate(self.vs):
                t, ir, _ = _iq_max(max(n, 1.0), v, w, self.i_lim, self.kv)
                self.T[i, j], self.I[i, j] = min(t, T_PEAK), ir
    def _interp(self, arr, n, v):
        n = min(max(n, 0.0), self.ns[-1])
        v = min(max(v, self.vs[0]), self.vs[-1])
        i = min(int(n // 100), len(self.ns) - 2)
        j = min(int((v - 200) // 20), len(self.vs) - 2)
        fn, fv = (n - self.ns[i]) / 100.0, (v - self.vs[j]) / 20.0
        return ((arr[i, j] * (1 - fn) + arr[i + 1, j] * fn) * (1 - fv) + (arr[i, j + 1] * (1 - fn) + arr[i + 1, j + 1] * fn) * fv)
    def tmax(self, n, v):
        return self._interp(self.T, n, v)
    def imax(self, n, v):
        return self._interp(self.I, n, v)

def motor_losses(torque, n_rpm, i_rms, t_wind=90.0, w='LV+43%'):
    """(copper W, iron+windage W)."""
    cu = 3.0 * r_hot(w, t_wind) * i_rms ** 2
    fe = FE_KW_5500 * 1000.0 * (max(n_rpm, 0.0) / 5500.0) ** FE_EXP + 40.0 * (max(n_rpm, 0.0) / 5500.0) ** 2
    return cu, fe

def motor_current(torque, w='LV+43%'):
    return abs(torque) / WINDINGS[w]['kt']

# ------------------------------------------------------------------ inverter: Cascadia CM200DX
INV = dict(vmin=200, vmax=480, trip=500, icont=300, ipk=740, ppk_kw=225, kg=6.75)
def inverter_loss(i_rms, p_mech_w, vdc):
    """Si IGBT inverter losses (W): fixed + conduction + switching [est, scaled to ~98% at 300 A, 350 V]."""
    return 120.0 + 3.4 * i_rms + 3.5e-3 * i_rms ** 2

def belt_loss(p_w):
    return 40.0 + 0.010 * abs(p_w)

# ------------------------------------------------------------------ road load
def road_force(v, cda=CDA, grade=0.0):
    return 0.5 * RHO * cda * v * v + CRR * M_TOT * G0 + M_TOT * G0 * grade

def rot_mass(G, v=20.0):
    r = r_eff(v)
    return I_WHEELS / r ** 2 + J_MOTOR * (G / r) ** 2

def traction_limit_a(mu):
    """Max forward acceleration (m/s2) from rear-tyre grip with load transfer; capped by the wheelie limit."""
    a_tr = mu * G0 * COG_B / (WHEELBASE - mu * COG_H)
    a_wh = G0 * COG_B / COG_H
    return min(a_tr, a_wh)


# ------------------------------------------------------------------ whole drivetrain
P_MOTOR_PEAK_W = 124e3     # datasheet S2 30 s peak [supplier]
I_PACK_CAP = 350.0         # BMS discharge limit, A (36 A per cell = 0.6 x the 60 A rating; 10-30 s pulses) [est]
ETA_BELT_PEAK = 0.985

class Drive:
    def __init__(self, G, winding='LV+43%', i_inv=None, kv_scale=1.0, mmap=None):
        self.G = G
        self.w = winding
        self.mmap = mmap or MotorMap(winding, i_inv if i_inv else INV['ipk'], kv_scale=kv_scale)
        self.i_cont = min(INV['icont'], WINDINGS[winding]['icont'])
    def rpm(self, v):
        return v / r_eff(v) * self.G * 30.0 / math.pi

    def electrical(self, torque, n_rpm, soc, t_pack, t_wind, i_rms=None, p_aux=0.0):
        """Given motor shaft torque (Nm, + drive / - regen) and speed, return dict of losses and DC side."""
        w_m = n_rpm * math.pi / 30.0
        p_mech = torque * w_m
        if i_rms is None:
            i_rms = motor_current(torque, self.w)
        cu, fe = motor_losses(torque, n_rpm, i_rms, t_wind, self.w)
        # DC-side bus voltage solved with pack resistance
        p_in_mot = p_mech + cu + fe
        vbus = ocv_pack(soc)
        p_dc = p_in_mot + inverter_loss(i_rms, p_in_mot, vbus)
        if p_mech < 0:   # regen: losses reduce what reaches the DC bus
            p_dc = p_mech + cu + fe + inverter_loss(i_rms, p_mech, vbus)
        i_dc = pack_current_for_power(p_dc + p_aux, soc, t_pack)
        if i_dc is None:
            return None
        vbus = ocv_pack(soc) - i_dc * r_pack(soc, t_pack)
        p_dc = (p_mech + cu + fe + inverter_loss(i_rms, p_mech + cu + fe, vbus)) if p_mech >= 0 else (p_mech + cu + fe + inverter_loss(i_rms, p_mech, vbus))
        i_dc = pack_current_for_power(p_dc + p_aux, soc, t_pack)
        if i_dc is None:
            return None
        vbus = ocv_pack(soc) - i_dc * r_pack(soc, t_pack)
        return dict(p_mech=p_mech, cu=cu, fe=fe, p_inv=inverter_loss(i_rms, p_mech, vbus), p_dc=p_dc, p_aux=p_aux, i_dc=i_dc, vbus=vbus,
                    i_rms=i_rms, p_pack_loss=i_dc ** 2 * r_pack(soc, t_pack))

    def max_torque(self, v, soc, t_pack, t_wind):
        """Peak motor torque at road speed v, solving for the loaded bus voltage; respects the 124 kW motor peak and the BMS cap."""
        n = self.rpm(v)
        vb = ocv_pack(soc) - 150.0 * r_pack(soc, t_pack)
        T = 0.0
        for _ in range(6):
            T = self.mmap.tmax(n, vb)
            if n > 1:
                T = min(T, P_MOTOR_PEAK_W / (n * math.pi / 30.0))
            i_used = self.mmap.imax(n, vb) if T >= self.mmap.tmax(n, vb) - 1e-6 else motor_current(T, self.w)
            e = self.electrical(T, n, soc, t_pack, t_wind, i_used)
            if e is None:
                T *= 0.7
                continue
            if e['i_dc'] > I_PACK_CAP:
                # scale torque back until the pack current cap holds
                lo, hi = 0.0, T
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    e2 = self.electrical(mid, n, soc, t_pack, t_wind)
                    if e2 is not None and e2['i_dc'] <= I_PACK_CAP:
                        lo = mid
                    else:
                        hi = mid
                T = lo
                e = self.electrical(T, n, soc, t_pack, t_wind)
            vb = e['vbus']
        return T, vb, e

    def wheel_force(self, torque, v):
        return torque * self.G * ETA_BELT_PEAK / r_eff(v)


def accel_run(drive, v0=0.0, v1=26.8224, soc=90.0, t_pack=25.0, t_wind=40.0, mu=1.0, cda=CDA, dt=0.01, p_cap_w=None, log=None):
    """Full-throttle run from v0 to v1 (m/s). Returns (time s, distance m, energy from pack kWh, peak DC current A, min bus V, final soc)."""
    v, t, x, e_j = v0, 0.0, 0.0, 0.0
    a_cap = traction_limit_a(mu)
    ipk, vmin = 0.0, 1e9
    q_wind = 0.0
    while v < v1 and t < 120.0:
        T, vb, e = drive.max_torque(max(v, 0.3), soc, t_pack, t_wind)
        F = drive.wheel_force(T, v)
        if v < 1.5:   # standing start: use the torque at 1.5 m/s (motor torque is constant there)
            pass
        m_eq = M_TOT + rot_mass(drive.G, max(v, 1.0))
        a = (F - road_force(v, cda)) / m_eq
        if a > a_cap:
            a = a_cap
            F_used = a * m_eq + road_force(v, cda)
            T = min(T, F_used * r_eff(v) / (drive.G * ETA_BELT_PEAK))
            e = drive.electrical(T, drive.rpm(max(v, 0.3)), soc, t_pack, t_wind)
        if e is not None:
            e_j += e['p_dc'] * dt
            ipk = max(ipk, e['i_dc'])
            vmin = min(vmin, e['vbus'])
            soc -= e['i_dc'] * dt / (PACK_AH * 3600.0) * 100.0
            t_wind += (e['cu'] + e['fe']) * dt / C_MOTOR
        v += a * dt
        t += dt
        x += v * dt
        if log is not None:
            log.append((t, v / MPH, a / G0, T, e['p_dc'] / 1e3 if e else 0.0, e['vbus'] if e else 0.0, drive.rpm(v)))
    return dict(t=t, x=x, e_kwh=e_j / 3.6e6, i_pk=ipk, v_min=vmin, soc=soc, t_wind=t_wind)
