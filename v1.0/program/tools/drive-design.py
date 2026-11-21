"""Bavuso V1 drive design: winding, inverter, gear ratio, pulleys, belt, tensions, bearing loads.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/drive-design.py
Writes program/data/drive-design.json
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
dl = _load('drive_lib', 'drive-lib.py')
OUT = os.path.join(HERE, '..', 'data', 'drive-design.json')
res = {}

# ============================================================ 1. winding choice
rows = []
for w, d in dl.WINDINGS.items():
    for vloaded in (300.0, 330.0, 360.0):
        mm = dl.MotorMap(w, i_lim=dl.INV['ipk'])
        best = max((mm.tmax(n, vloaded) * n * math.pi / 30.0, n) for n in range(500, 6501, 100))
        t_launch = mm.tmax(500, vloaded)
        n_corner = max(n for n in range(500, 6501, 100) if mm.tmax(n, vloaded) >= 0.97 * mm.tmax(500, vloaded))
        rows.append(dict(winding=w, v_loaded=vloaded, torque_low_speed=round(t_launch, 1), corner_rpm=n_corner,
                         peak_kw=round(best[0] / 1e3, 1), peak_kw_at_rpm=best[1], current_rms=round(min(d['ipk'], dl.INV['ipk']))))
res['winding_table'] = rows
print('winding  Vloaded  T_low  corner  peak_kW@rpm  I')
for r in rows:
    print(f"{r['winding']:8s} {r['v_loaded']:5.0f}  {r['torque_low_speed']:6.1f} {r['corner_rpm']:5d}  {r['peak_kw']:6.1f}@{r['peak_kw_at_rpm']}  {r['current_rms']}")

# ============================================================ 2. inverter shortlist verification (voltage / current class)
V_FULL = dl.ocv_pack(100.0)                       # 420 V
V_REGEN_MAX = V_FULL + 100.0 * dl.r_pack(100.0, 25.0)    # regen at 100 A into a full pack
V_LOW = dl.ocv_pack(5.0) - 400.0 * dl.r_pack(5.0, 25.0)  # 5% SOC under 400 A
I_PH_PEAK = dl.WINDINGS['LV+43%']['ipk']
inv_rows = [
    dict(part='Cascadia CM200DX', v_range='200-480 V op, 500 V trip', i_cont=300, i_peak=740, kg=6.75,
         v_ok=(dl.INV['vmin'] <= V_LOW and V_REGEN_MAX < dl.INV['vmax']), i_ok=I_PH_PEAK <= 740, source='cascadiamotion.com/cm-200 (fetched Nov 21, 2026)'),
    dict(part='Emsiso emDrive H100 150/450 (shortlist pick)', v_range='not published in anything fetched', i_cont=150, i_peak=450, kg=2.2,
         v_ok=None, i_ok=I_PH_PEAK <= 450, source='datasheet host blocked automated download (bot wall); not on the Poclain catalogue page'),
    dict(part='Poclain emDrive H20B 400 V class', v_range='12-420 V', i_cont=260, i_peak=400, kg=None,
         v_ok=V_FULL < 420, i_ok=I_PH_PEAK <= 400, source='poclain.com/electrification/emdrive-inverters'),
]
for r in inv_rows:
    print(r['part'], 'V ok', r['v_ok'], 'I ok', r['i_ok'])
res['inverter'] = dict(rows=inv_rows, v_full=V_FULL, v_regen_max=V_REGEN_MAX, v_low_5soc_400A=V_LOW,
                       motor_peak_arms=I_PH_PEAK, motor_cont_arms_lc=330, inverter_cont_arms=300,
                       cont_torque_nm_inverter_limited=round(118.0 * 300.0 / 330.0, 1))
print('V_full %.0f, regen max %.0f, V_low %.0f' % (V_FULL, V_REGEN_MAX, V_LOW))

# ============================================================ 3. gear ratio sweep (0-60, top speed, rpm margin)
sweep = []
for G in (3.2, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9):
    d = dl.Drive(G)
    r60 = dl.accel_run(d, 0, 60 * dl.MPH, soc=70)
    v130 = 130 * dl.MPH
    sweep.append(dict(G=G, zero_60=round(r60['t'], 2), rpm_130mph=round(d.rpm(v130)), top_mph_at_6500rpm=round(6500 / (G * 30 / math.pi) * dl.r_eff(58.0) / dl.MPH, 1)))
res['ratio_sweep'] = sweep
for s in sweep:
    print(s)

# ============================================================ 4. belt: Gates Poly Chain GT Carbon 8MGT (manual pp.52-55, 103-106)
# base rated hp for the small sprocket, from the 8mm tables.  columns: grooves -> hp at rpm [88,175,1750,3000,3450,4000]
RPMS = np.array([88, 175, 1750, 3000, 3450, 4000.0])
HP62 = {34: [6.79, 12.3, 95.1, 153.5, 173.6, 197.4], 36: [7.29, 13.2, 102.8, 166.1, 187.8, 213.7], 38: [7.80, 14.1, 110.6, 178.7, 202.0, 229.8],
        32: [6.27, 11.3, 87.3, 140.8, 159.1, 181.0]}
HP36 = {34: [3.94, 7.11, 55.2, 89.1, 100.8, 114.6], 35: [4.09, 7.38, 57.5, 92.8, 104.9, 119.3], 36: [4.23, 7.66, 59.7, 96.4, 109.0, 124.0], 38: [4.53, 8.20, 64.2, 103.7, 117.3, 133.4]}
M_8MM = {12: 0.33, 21: 0.57, 36: 0.97, 62: 1.68}      # Table 11 mass-per-length constant (lb tension per (kfpm)^2)
LEN_FACTOR = {1760: 1.17, 1792: 1.18, 1600: 1.14}
ADD_HP_RATIO = {4000: 14.8, 4500: 16.6, 5000: 18.5, 5500: 20.3}   # 62 mm, speed-down ratio >= 2.16 (p.55); 36 mm is about 0.58x

def pd_in(z, pitch=8.0):
    return z * pitch / math.pi / 25.4

def te_rated_lbf(z, width, rpm):
    """Rated effective tension (lbf) from the hp tables, interpolated between grooves; linear extrapolation above 4000 rpm (FLAGGED)."""
    tbl = HP62 if width == 62 else HP36
    zs = sorted(tbl)
    def hp_at(zz, r):
        v = np.array(tbl[zz])
        return np.interp(r, RPMS, v)
    pd = pd_in(z)
    def te(zz, r):
        p = pd_in(zz)
        vfpm = p * r / 3.82
        return hp_at(zz, r) * 33000.0 / vfpm
    r_eval = min(rpm, 4000.0)
    zl = max(k for k in zs if k <= z); zh = min(k for k in zs if k >= z)
    if zl == zh:
        t = te(zl, r_eval)
    else:
        f = (z - zl) / (zh - zl)
        t = te(zl, r_eval) * (1 - f) + te(zh, r_eval) * f
    if rpm > 4000.0:    # extrapolate Te(rpm) with the 3450->4000 slope
        zl_ = zl if zl == zh else zl
        t0 = (te(zl, 4000.0) * (1 - (0 if zl == zh else (z - zl) / (zh - zl))) + (te(zh, 4000.0) * (0 if zl == zh else (z - zl) / (zh - zl))))
        t1 = (te(zl, 3450.0) * (1 - (0 if zl == zh else (z - zl) / (zh - zl))) + (te(zh, 3450.0) * (0 if zl == zh else (z - zl) / (zh - zl))))
        slope = (t0 - t1) / 550.0
        t = t0 + slope * (rpm - 4000.0)
    return t

def stock_cd(L, D, d):
    b = L - 1.57 * (D + d)
    return (b + math.sqrt(b * b - 2.0 * (D - d) ** 2)) / 4.0

CD_CAD = math.hypot(540.0, 350.0 - (325.0 - 53.1))     # pivot (540, PZ=350) to rear axle (0, RR-LIFT); motor shaft on the pivot axis
print('CAD centre distance (pivot to rear axle):', round(CD_CAD, 1))

Z1, Z2, BELT_L, WIDTH, PITCH = 35, 126, 1760, 62, 8.0
G = Z2 / Z1
d_p, D_p = Z1 * PITCH / math.pi, Z2 * PITCH / math.pi
C = stock_cd(BELT_L, D_p, d_p)
gamma = math.asin((D_p - d_p) / (2 * C))
arc_small = 180.0 - 2 * math.degrees(gamma)
teeth_engaged = Z1 * arc_small / 360.0
v_belt_6500 = d_p / 1000.0 / 2 * 6500 * math.pi / 30.0
print(f'z1 {Z1} z2 {Z2} G {G:.4f} PD {d_p:.2f}/{D_p:.2f} mm  CD {C:.2f}  arc {arc_small:.1f} teeth {teeth_engaged:.1f}  belt speed @6500 rpm {v_belt_6500:.1f} m/s ({v_belt_6500*196.85:.0f} fpm)')

SF = 1.5      # on the 220 Nm peak torque (Gates Table 5: inverter-controlled AC motor, intermittent service, shock/regen reversals)
T_PEAK = 220.0
r1 = d_p / 2000.0
te_peak = T_PEAK / r1       # N
checks = []
for rpm in (500, 1000, 1750, 3000, 4000, 5000, 5500, 6000, 6500):
    t_nm = min(T_PEAK, dl.P_MOTOR_PEAK_W / (rpm * math.pi / 30.0))
    te_req = SF * t_nm / r1 / 4.44822                      # lbf
    cap = te_rated_lbf(Z1, WIDTH, rpm)
    lf = LEN_FACTOR[BELT_L]
    vfpm = pd_in(Z1) * rpm / 3.82
    add_hp = ADD_HP_RATIO.get(rpm, 14.8 if rpm < 4000 else 20.3) if rpm >= 4000 else 0.0
    cap_total = (cap * vfpm / 33000.0 + add_hp) * lf        # hp
    req_hp = te_req * vfpm / 33000.0
    checks.append(dict(rpm=rpm, belt_speed_fpm=round(vfpm), design_hp=round(req_hp, 1), rated_hp=round(cap_total, 1), margin=round(cap_total / req_hp, 2),
                       extrapolated=rpm > 4000))
res['belt_checks'] = checks
for c in checks:
    print(c)
min_margin = min(c['margin'] for c in checks)

# narrower belt alternatives (36 mm): what torque cap would they allow?
alt36 = []
for rpm in (1750, 4000, 5500):
    cap = te_rated_lbf(Z1, 36, rpm) * 4.44822 * LEN_FACTOR[BELT_L]
    alt36.append(dict(rpm=rpm, max_motor_torque_at_SF=round(cap / SF * r1, 1)))
res['alt_36mm_torque_cap'] = alt36
print('36 mm belt torque cap at SF', SF, alt36)

# tensions (Gates formulas 14, 17, 18 and Table 11)
def tensions(t_motor_nm, rpm, sf):
    te = sf * t_motor_nm / r1 / 4.44822          # lbf design effective tension
    S = pd_in(Z1) * rpm / 3820.0                  # thousands of fpm
    m = M_8MM[WIDTH]
    hp = te * (pd_in(Z1) * rpm / 3.82) / 33000.0
    tst = max(20.0 * hp / S + m * S * S, 145.0)  # 145 lbf = Table 11 minimum per span, 62 mm 8mm pitch
    tt = 1.25 * te + m * S * S
    ts = 0.25 * te + m * S * S
    ang = 2 * gamma
    pull = math.sqrt(tt ** 2 + ts ** 2 + 2 * tt * ts * math.cos(ang))
    return dict(te_N=te * 4.44822, tst_N=tst * 4.44822, tt_N=tt * 4.44822, ts_N=ts * 4.44822, pull_N=pull * 4.44822, centrifugal_each_N=m * S * S * 4.44822)
ten = {}
ten['peak_torque_SF1'] = tensions(T_PEAK, 3000, 1.0)
ten['design_SF1.5_corner'] = tensions(T_PEAK, 5500, SF)
ten['design_SF1.5_launch'] = tensions(T_PEAK, 500, SF)
ten['regen_peak_SF1'] = tensions(T_PEAK, 3000, 1.0)
ten['continuous_118Nm_5500rpm'] = tensions(118.0, 5500, 1.0)
tst_install = ten['peak_torque_SF1']['tst_N']
res['tensions'] = ten
for k, v in ten.items():
    print(k, {a: round(b) for a, b in v.items()})

# belt-line geometry for FEA (X forward, Z up; motor/pivot at (540, 350), rear axle at (0, 271.9) in generator coordinates)
ang_line = math.degrees(math.atan2(350.0 - (325.0 - 53.1), 540.0))
print('belt line elevation (rear axle to motor) deg', round(ang_line, 2), 'span angle +-', round(math.degrees(gamma), 2))

# belt length / mass
mass_belt = 0.164 * 62 / 36 * BELT_L / 1000.0                  # 8MGT 36 mm = 0.11 lb/ft = 0.164 kg/m (Gates long-length table), scaled to 62 mm
# sprocket masses (aluminium 7075, 62 mm belt, 68 mm face, ribbed web) [est]
def sprocket_kg(pd_mm, web_t=4.0, face=68.0, flange_t=3.0):
    od = pd_mm - 1.4
    root = od - 2 * 3.4
    rim_in = root - 2 * 6.0
    rim = math.pi / 4 * (root ** 2 - rim_in ** 2) * face
    fl = 2 * math.pi / 4 * ((od + 12) ** 2 - od ** 2) * flange_t
    web = math.pi / 4 * (rim_in ** 2 - (0.45 * rim_in) ** 2) * web_t * 0.45   # 55% of web area lightened
    hub = math.pi / 4 * (55 ** 2 - 30 ** 2) * 30.0 if pd_mm < 150 else math.pi / 4 * (110 ** 2 - 60 ** 2) * 20.0
    return (rim + fl + web + hub) * 2.81e-6
m_small, m_large = sprocket_kg(d_p), sprocket_kg(D_p)
print('masses: belt %.2f, small %.2f, large %.2f' % (mass_belt, m_small, m_large))

res['pulleys'] = dict(z_motor=Z1, z_rear=Z2, ratio=G, pitch_mm=PITCH, belt='Gates Poly Chain GT Carbon 8MGT-1760-62 (220 teeth, 62 mm)', belt_length_mm=BELT_L,
    pd_motor_mm=round(d_p, 2), pd_rear_mm=round(D_p, 2), od_motor_mm=round(d_p - 1.4, 1), od_rear_mm=round(D_p - 1.4, 1),
    flange_od_motor_mm=round(d_p - 1.4 + 12, 1), flange_od_rear_mm=round(D_p - 1.4 + 12, 1),
    center_distance_nominal_mm=round(C, 2), cad_center_distance_mm=round(CD_CAD, 2), arc_small_deg=round(arc_small, 1), teeth_in_mesh_small=round(teeth_engaged, 1),
    belt_speed_6500rpm_fpm=round(v_belt_6500 * 196.85), belt_speed_limit_fpm=6500, sf=SF, min_capacity_margin=min_margin,
    mass_kg=dict(belt=round(mass_belt, 2), pulley_motor=round(m_small, 2), pulley_rear=round(m_large, 2)),
    install_tension_per_span_N=round(tst_install), install_deflection_note='Gates formula 14 at peak torque, SF 1.0; measure with sonic tension meter; Table 11 minimum 645 N (145 lbf)',
    belt_line_deg=round(ang_line, 2), half_span_angle_deg=round(math.degrees(gamma), 2))

# gearing results
d = dl.Drive(G)
res['gearing'] = dict(G=G, rpm_125mph=round(d.rpm(125 * dl.MPH)), rpm_130mph=round(d.rpm(130 * dl.MPH)), top_mph_rpm_limited=round(6500 / (G * 30 / math.pi) * dl.r_eff(58.0) / dl.MPH, 1),
                      r_eff_low=round(dl.R_E0, 4), r_eff_130=round(dl.r_eff(58.1), 4))
print(res['gearing'])
json.dump(res, open(OUT, 'w'), indent=1, default=float)
print('wrote', OUT)
