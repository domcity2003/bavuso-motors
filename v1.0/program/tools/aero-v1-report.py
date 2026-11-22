"""Turn the Bavuso V1 rev E aero runs into numbers and pictures.
Run from v1.0: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/aero-v1-report.py
Reads every finished case in program/data/aero/run/*/ (DONE marker); writes program/data/aero/aero-results.json and *.png.
Conventions: X forward, Y left, Z up, origin at the rear tyre contact point. Air moves towards -X.
CdA = force along the relative wind / (0.5 rho Vair^2). Forces are averaged over the last AVG iterations.
Mesh study: Celik et al. 2008 (ASME J. Fluids Eng. 130, 078001) procedure, Fs = 1.25, h = cells^(-1/3).
"""
import json, re, math, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[2]
RUN = R / 'program/data/aero/run'; OUT = R / 'program/data/aero'
AVG = 150
RHO = 1.225
WB = 1.490                         # wheelbase, rev E (15-dynamics.md)
COG = np.array([0.7324, 0.0, 0.6668])   # bike + 90 kg rider CG, m from the rear contact point (15-dynamics.md, rev D snapshot)
man = json.loads((OUT / 'geometry-manifest.json').read_text())
WALL_PATCHES = [p for p in man['patches'] if not p.startswith(('rad_core', 'rad_fan'))]
PARTS = WALL_PATCHES

def table(path):
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith('#') or not line.strip(): continue
        rows.append([float(v) for v in re.sub(r'[()]', ' ', line).split()])
    return np.array(rows)

def forces(case, name):
    A = table(case / 'postProcessing' / f'forces_{name}' / '0' / 'forces.dat')
    A = A[np.unique(A[:, 0], return_index=True)[1]]
    return dict(t=A[:, 0], Fp=A[:, 1:4], Fv=A[:, 4:7], F=A[:, 1:4] + A[:, 4:7], M=A[:, 7:10] + A[:, 10:13])

def ncells(case):
    return int(re.search(r'cells:\s+(\d+)', (case / 'log.checkMesh').read_text()).group(1))

def case_result(case):
    cj = json.loads((case / 'case.json').read_text())
    U = np.array(cj['U_air']); Va = np.linalg.norm(U); q = 0.5 * cj['rho'] * Va ** 2; ehat = U / Va
    res = dict(case=case.name, yaw_deg=cj['yaw_deg'], base_cell_m=cj['base_cell_m'], cells=ncells(case), air_speed_ms=round(Va, 3),
               q_Pa=round(q, 1), radiator=cj.get('radiator'), parts={})
    hist = {}
    for name in ['total', 'bike_body', 'rider', 'wheels'] + PARTS:
        f = forces(case, name); n = min(AVG, len(f['t']) // 3)
        F = f['F'][-n:].mean(0); Fp = f['Fp'][-n:].mean(0); Fv = f['Fv'][-n:].mean(0); M = f['M'][-n:].mean(0)
        dair = float(F @ ehat)
        r = dict(drag_air_N=round(dair, 2), CdA_m2=round(dair / q, 4), pressure_drag_N=round(float(Fp @ ehat), 2),
                 viscous_drag_N=round(float(Fv @ ehat), 2), Fx_N=round(F[0], 2), side_force_N=round(F[1], 2), lift_N=round(F[2], 2))
        if name == 'total':
            res['iterations'] = int(f['t'][-1])
            cda = (f['F'] @ ehat) / q; hist['cda'] = (f['t'], cda)
            w = cda[-n:]; prev = cda[-2 * n:-n]
            r.update(CdA_std_window=round(float(w.std()), 4), CdA_min_window=round(float(w.min()), 4), CdA_max_window=round(float(w.max()), 4),
                     drift_last_vs_previous_window_pct=round(100 * (w.mean() - prev.mean()) / w.mean(), 2), window_iterations=n,
                     CdA_by_window_of_50=[round(float(cda[-k - 50:len(cda) - k].mean()), 4) for k in (150, 100, 50, 0) if len(cda) >= k + 50])
            # moments about the rear contact point (CofR = origin)
            Lf = -M[1] / WB; Lr = F[2] - Lf
            Mcog = M - np.cross(COG, F)
            r.update(front_axle_lift_N=round(Lf, 1), rear_axle_lift_N=round(Lr, 1), yaw_moment_about_rear_contact_Nm=round(M[2], 1),
                     roll_moment_about_rear_contact_Nm=round(M[0], 1), pitch_moment_about_rear_contact_Nm=round(M[1], 1),
                     yaw_moment_about_cog_Nm=round(Mcog[2], 1), roll_moment_about_cog_Nm=round(Mcog[0], 1), pitch_moment_about_cog_Nm=round(Mcog[1], 1),
                     cp_x_ahead_of_rear_axle_m=round(M[2] / F[1], 3) if abs(F[1]) > 5 else None,
                     cp_height_m=round(-M[0] / F[1], 3) if abs(F[1]) > 5 else None)
            hist['parts'] = {p: (forces(case, p)['t'], (forces(case, p)['F'] @ ehat) / q) for p in ('bike_body', 'rider', 'wheels')}
        res['parts'][name] = r
    yp = (case / 'postProcessing/yPlus/0/yPlus.dat').read_text().splitlines()
    last = [l.split() for l in yp if l and not l.startswith('#')]; tl = last[-1][0]
    res['yplus'] = {l[1]: dict(min=round(float(l[2]), 2), max=round(float(l[3]), 1), avg=round(float(l[4]), 1)) for l in last if l[0] == tl}
    fr = table(case / 'postProcessing/flowRates/0/surfaceFieldValue.dat')
    inflow = abs(U[0]) * 7.0 * 3.99 + abs(U[1]) * 13.5 * 3.99
    res['net_mass_flux_pct_of_inflow'] = round(100 * abs(fr[-1, 1]) / inflow, 4)
    et = re.findall(r'ExecutionTime = ([0-9.]+) s', (case / 'log.foamRun').read_text())
    res['solver_hours'] = round(float(et[-1]) / 3600, 2) if et else None
    return res, hist, q, ehat

cases = sorted([p for p in RUN.iterdir() if p.is_dir() and (p / 'DONE').exists()])
results = {}; hists = {}
for c in cases:
    r, h, q, e = case_result(c); results[c.name] = r; hists[c.name] = (h, q, e)
    t = r['parts']['total']
    print(f"{c.name:10s} cells {r['cells']:9d} CdA {t['CdA_m2']:.4f} drift {t['drift_last_vs_previous_window_pct']}% std {t['CdA_std_window']} Fy {t['side_force_N']}")

# ---------------------------------------------------------------- mesh study (Celik et al. 2008)
def celik(fs, Ns):
    """fs, Ns ordered fine -> medium -> coarse. Returns dict."""
    f1, f2, f3 = fs; N1, N2, N3 = Ns
    r21 = (N1 / N2) ** (1 / 3); r32 = (N2 / N3) ** (1 / 3)
    e21, e32 = f2 - f1, f3 - f2
    out = dict(r21=round(r21, 3), r32=round(r32, 3), f1=f1, f2=f2, f3=f3, change_fine_pct=round(100 * (f1 - f2) / f2, 2),
               change_coarse_pct=round(100 * (f2 - f3) / f3, 2))
    s = math.copysign(1, e32 / e21) if e21 != 0 else 1
    out['convergence_ratio_R'] = round(e21 / e32, 3) if e32 != 0 else None
    if e21 == 0 or e32 == 0 or s < 0:
        out['behaviour'] = 'oscillatory (change of sign between refinements): no Richardson extrapolation'
        out['spread_pct_of_fine'] = round(100 * (max(fs) - min(fs)) / f1, 2)
        return out
    p = 1.0
    for _ in range(200):
        q_ = math.log((r21 ** p - s) / (r32 ** p - s)); pn = abs(math.log(abs(e32 / e21)) + q_) / math.log(r21)
        if abs(pn - p) < 1e-6: p = pn; break
        p = pn
    out['behaviour'] = 'monotonic'
    out['observed_order_p'] = round(p, 2)
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    ea21 = abs((f1 - f2) / f1)
    out.update(richardson_CdA=round(f_ext, 4), approx_rel_error_fine_pct=round(100 * ea21, 2),
               extrapolated_rel_error_pct=round(100 * abs((f_ext - f1) / f_ext), 2),
               GCI_fine_pct=round(100 * 1.25 * ea21 / (r21 ** p - 1), 2))
    return out

seq = [n for n in ('m1', 'm2', 'm3', 'm4') if n in results]
study = dict(cases=[dict(case=n, base_cell_m=results[n]['base_cell_m'], cells=results[n]['cells'], CdA=results[n]['parts']['total']['CdA_m2'],
                         drift_pct=results[n]['parts']['total']['drift_last_vs_previous_window_pct'], std=results[n]['parts']['total']['CdA_std_window'],
                         bike_body_CdA=results[n]['parts']['bike_body']['CdA_m2'], rider_CdA=results[n]['parts']['rider']['CdA_m2'],
                         wheels_CdA=results[n]['parts']['wheels']['CdA_m2'],
                         front_lift=results[n]['parts']['total']['front_axle_lift_N'], rear_lift=results[n]['parts']['total']['rear_axle_lift_N'],
                         solver_hours=results[n]['solver_hours']) for n in seq])
study['successive_change_pct'] = {f'{seq[i]}->{seq[i+1]}': round(100 * (results[seq[i + 1]]['parts']['total']['CdA_m2'] - results[seq[i]]['parts']['total']['CdA_m2']) / results[seq[i]]['parts']['total']['CdA_m2'], 2) for i in range(len(seq) - 1)}
study['triples'] = {}
for i in range(len(seq) - 2):
    tri = seq[i:i + 3][::-1]   # fine, medium, coarse
    study['triples']['/'.join(tri)] = celik([results[n]['parts']['total']['CdA_m2'] for n in tri], [results[n]['cells'] for n in tri])
results['mesh_study'] = study
print(json.dumps(study, indent=1))

# ---------------------------------------------------------------- yaw
yaw = {}
if all(k in results for k in ('yaw+10', 'yaw-10')):
    rp, rn = results['yaw+10'], results['yaw-10']
    base_name = 'm2' if 'm2' in results else seq[0]
    r0 = results[base_name]
    for lab, r in (('+10', rp), ('-10', rn), ('0', r0)):
        t = r['parts']['total']; Va = r['air_speed_ms']; q = r['q_Pa']; beta = math.radians(abs(r['yaw_deg']))
        d = dict(case=r['case'], yaw_deg=r['yaw_deg'], air_speed_ms=Va, q_Pa=q, drag_along_wind_N=t['drag_air_N'], CdA_air_axis_m2=t['CdA_m2'],
                 Fx_vehicle_N=t['Fx_N'], side_force_N=t['side_force_N'], CyA_m2=round(t['side_force_N'] / q, 4),
                 lift_N=t['lift_N'], front_axle_lift_N=t['front_axle_lift_N'], rear_axle_lift_N=t['rear_axle_lift_N'],
                 yaw_moment_about_cog_Nm=t['yaw_moment_about_cog_Nm'], roll_moment_about_cog_Nm=t['roll_moment_about_cog_Nm'],
                 yaw_moment_about_rear_contact_Nm=t['yaw_moment_about_rear_contact_Nm'],
                 CnA_L_m3=round(t['yaw_moment_about_cog_Nm'] / q, 4), cp_x_ahead_of_rear_axle_m=t['cp_x_ahead_of_rear_axle_m'], cp_height_m=t['cp_height_m'])
        yaw[lab] = d
    # slope Cy_beta*A as defined in 15-dynamics.md: F = 0.5 rho (V^2+w^2) CyA_slope atan(w/V)
    sl = {}
    for lab, r in (('+10', rp), ('-10', rn)):
        t = r['parts']['total']; q = r['q_Pa']; beta = math.radians(abs(r['yaw_deg']))
        sl[lab] = dict(side_force_slope_CyA_per_rad_m2=round(abs(t['side_force_N']) / q / beta, 3),
                       yaw_moment_slope_CnAL_per_rad_m3=round(abs(t['yaw_moment_about_cog_Nm']) / q / beta, 3))
    yaw['slopes'] = sl
    yaw['mean_slope_CyA_per_rad_m2'] = round(np.mean([v['side_force_slope_CyA_per_rad_m2'] for v in sl.values()]), 3)
    yaw['mean_slope_CnAL_per_rad_m3'] = round(np.mean([v['yaw_moment_slope_CnAL_per_rad_m3'] for v in sl.values()]), 3)
    yaw['asymmetry_side_force_pct'] = round(100 * (abs(rp['parts']['total']['side_force_N']) - abs(rn['parts']['total']['side_force_N'])) / (0.5 * (abs(rp['parts']['total']['side_force_N']) + abs(rn['parts']['total']['side_force_N']))), 1)
    cps = [(r['parts']['total']['cp_x_ahead_of_rear_axle_m'], r['parts']['total']['cp_height_m']) for r in (rp, rn)]
    yaw['cp_mean_x_ahead_of_rear_axle_m'] = round(float(np.mean([c[0] for c in cps])), 3); yaw['cp_mean_height_m'] = round(float(np.mean([c[1] for c in cps])), 3)
    # side force at 77 mph, 10 m/s sidewind (15-dynamics.md gust case) using the mean slope, same functional form
    V77 = 77 * 0.44704; w = 10.0
    F77 = 0.5 * RHO * (V77 ** 2 + w ** 2) * yaw['mean_slope_CyA_per_rad_m2'] * math.atan(w / V77)
    yaw['gust_77mph_10ms_side_force_N_from_slope'] = round(F77, 0)
    yaw['assumed_in_15_dynamics'] = dict(CyA_slope=1.6, cp_ahead_of_rear_axle_m=0.80, cp_height_m=0.95, force_10ms_77mph_N=349)
results['yaw'] = yaw
print(json.dumps(yaw, indent=1))

# ---------------------------------------------------------------- headline: finest 0-degree case
if not seq: sys.exit('no 0-degree cases finished')
best_name = seq[-1]; best = results[best_name]
bt = best['parts']['total']
ms = study['triples'][list(study['triples'])[-1]] if study['triples'] else None
results['headline'] = dict(case=best_name, cells=best['cells'], cda_m2=bt['CdA_m2'], drag_N=bt['drag_air_N'],
                           richardson_CdA=ms.get('richardson_CdA') if ms else None, GCI_pct=ms.get('GCI_fine_pct') if ms else None,
                           frontal_area_m2=man['frontal_area_m2']['total'], Cd=round(bt['CdA_m2'] / man['frontal_area_m2']['total'], 3))

# ---------------------------------------------------------------- pictures: convergence, mesh study
fig, ax = plt.subplots(figsize=(10, 4.8))
for n, (h, q, e) in hists.items():
    t, c = h['cda']; ax.plot(t, c, lw=1.1, label=n)
ax.set_ylim(0.2, 0.8); ax.grid(alpha=.3); ax.axvspan(max(0, t[-1] - AVG), t[-1], color='0.92')
ax.set_xlabel('iteration'); ax.set_ylabel('CdA (m², air axis)'); ax.set_title('Drag area history, every case, 70 mph'); ax.legend(fontsize=8, ncol=3)
fig.tight_layout(); fig.savefig(OUT / 'convergence.png', dpi=130); plt.close(fig)
if len(seq) >= 2:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    N = [results[n]['cells'] for n in seq]; Cv = [results[n]['parts']['total']['CdA_m2'] for n in seq]
    h = [n_ ** (-1 / 3) for n_ in N]
    ax.plot(h, Cv, 'o-')
    for n_, hh, c in zip(N, h, Cv): ax.annotate(f'{n_/1e6:.2f}M', (hh, c), textcoords='offset points', xytext=(5, 5))
    for k, t_ in study['triples'].items():
        if 'richardson_CdA' in t_: ax.plot([0], [t_['richardson_CdA']], '*', ms=11, label=f'Richardson ({k})')
    ax.legend(fontsize=8); ax.set_xlabel('cells$^{-1/3}$ (0 = infinitely fine)'); ax.set_ylabel('CdA (m²)'); ax.set_xlim(left=0); ax.grid(alpha=.3)
    ax.set_title('Mesh sensitivity, 0° yaw'); fig.tight_layout(); fig.savefig(OUT / 'mesh-study.png', dpi=130); plt.close(fig)

# ---------------------------------------------------------------- VTK pictures and pod analysis (finest 0-degree case)
import vtk
from vtk.util.numpy_support import vtk_to_numpy
bc = RUN / best_name; U0 = best['air_speed_ms']; Q = best['q_Pa']
def faces(case, part):
    f = sorted((case / 'VTK' / part).glob(f'{part}_[1-9]*.vtk'))[-1]
    r = vtk.vtkPolyDataReader(); r.SetFileName(str(f)); r.Update()
    nm = vtk.vtkPolyDataNormals(); nm.SetInputData(r.GetOutput()); nm.ComputeCellNormalsOn(); nm.ComputePointNormalsOff()
    nm.SplittingOff(); nm.ConsistencyOff(); nm.AutoOrientNormalsOff(); nm.Update(); o = nm.GetOutput()
    cs = vtk.vtkCellSizeFilter(); cs.SetInputData(o); cs.ComputeAreaOn(); cs.Update()
    cc = vtk.vtkCellCenters(); cc.SetInputData(o); cc.Update()
    A = vtk_to_numpy(cs.GetOutput().GetCellData().GetArray('Area')); n = vtk_to_numpy(o.GetCellData().GetNormals())
    c = vtk_to_numpy(cc.GetOutput().GetPoints().GetData()); p = vtk_to_numpy(o.GetCellData().GetArray('p'))
    yp = o.GetCellData().GetArray('yPlus'); yp = vtk_to_numpy(yp) if yp is not None else None
    return c, -RHO * p * n[:, 0] * A, A, yp, n, p
data = {p: faces(bc, p) for p in PARTS}
chk = {p: (round(float(d[1].sum()), 1), best['parts'][p]['pressure_drag_N']) for p, d in data.items()}
sgn = 1 if sum(a for a, b in chk.values()) * sum(b for a, b in chk.values()) > 0 else -1
results['vtk_pressure_drag_check'] = {p: dict(vtk_sum_N=sgn * a, function_object_N=b) for p, (a, b) in chk.items()}
ypd = {}
for p, (c, d, A, yp, n, pp) in data.items():
    if yp is None: continue
    o = np.argsort(yp); cw = np.cumsum(A[o]) / A.sum()
    ypd[p] = {f'p{k}': round(float(yp[o][np.searchsorted(cw, k / 100)]), 1) for k in (5, 50, 95)}
    ypd[p]['area_share_below_30_pct'] = round(100 * float(A[yp < 30].sum() / A.sum()), 1)
results['yplus_area_weighted'] = ypd
X = np.concatenate([d[0][:, 0] for d in data.values()]); Z = np.concatenate([d[0][:, 2] for d in data.values()]); Dd = sgn * np.concatenate([d[1] for d in data.values()])
b = 0.02; Hh, xe, ze = np.histogram2d(X, Z, bins=[np.arange(-0.45, 1.95 + b, b), np.arange(0, 1.85 + b, b)], weights=Dd); Hh = Hh.T / (b * b) / Q
fig, ax = plt.subplots(figsize=(12, 8)); lim = np.percentile(np.abs(Hh[Hh != 0]), 98)
m = ax.imshow(np.ma.masked_equal(Hh, 0), origin='lower', extent=(xe[0], xe[-1], ze[0], ze[-1]), cmap='RdBu_r', vmin=-lim, vmax=lim)
ax.set_facecolor('0.92'); ax.set_title(f'Where the pressure drag comes from ({best_name}, side view summed across the width)\nred adds drag, blue pushes the bike forward')
ax.set_xlabel('X (m, forward)'); ax.set_ylabel('Z (m)'); fig.colorbar(m, ax=ax, label='drag area per side-view area', shrink=.7)
fig.tight_layout(); fig.savefig(OUT / 'drag-map-side.png', dpi=130); plt.close(fig)

internal = sorted((bc / 'VTK').glob(f'{bc.name}_[1-9]*.vtk'))[-1]
rd = vtk.vtkUnstructuredGridReader(); rd.SetFileName(str(internal)); rd.Update()
c2p = vtk.vtkCellDataToPointData(); c2p.SetInputData(rd.GetOutput()); c2p.Update(); grid = c2p.GetOutput()
def slice_img(origin, ax0, ax1, ext, res=5e-3):
    nx, ny = int((ext[1] - ext[0]) / res), int((ext[3] - ext[2]) / res)
    g = np.zeros((ny * nx, 3)); I, J = np.meshgrid(np.arange(nx), np.arange(ny))
    g[:] = origin; g[:, ax0] = ext[0] + I.ravel() * res; g[:, ax1] = ext[2] + J.ravel() * res
    pts = vtk.vtkPoints()
    for p in g: pts.InsertNextPoint(p)
    pd = vtk.vtkPolyData(); pd.SetPoints(pts)
    pr = vtk.vtkProbeFilter(); pr.SetInputData(pd); pr.SetSourceData(grid); pr.Update(); o = pr.GetOutput()
    valid = vtk_to_numpy(o.GetPointData().GetArray('vtkValidPointMask')).astype(bool)
    sp = np.linalg.norm(vtk_to_numpy(o.GetPointData().GetArray('U')), axis=1) / U0; cp = vtk_to_numpy(o.GetPointData().GetArray('p')) / (0.5 * U0 ** 2)
    sp[~valid] = np.nan; cp[~valid] = np.nan; return sp.reshape(ny, nx), cp.reshape(ny, nx)
def show(img, ext, title, fname, cmap, vmin, vmax, label, xl, yl):
    fig, ax = plt.subplots(figsize=(12, 12 * (ext[3] - ext[2]) / (ext[1] - ext[0]) + 1))
    m = ax.imshow(img, origin='lower', extent=ext, cmap=cmap, vmin=vmin, vmax=vmax, interpolation='bilinear')
    ax.set_facecolor('0.15'); ax.set_title(title); ax.set_xlabel(xl); ax.set_ylabel(yl)
    fig.colorbar(m, ax=ax, label=label, shrink=.8); fig.tight_layout(); fig.savefig(OUT / fname, dpi=120); plt.close(fig)
ext = (-1.2, 2.4, 0.01, 2.0)
sp, cp = slice_img((0, 0, 0), 0, 2, ext)
show(sp, ext, f'Mid-plane Y=0: air speed / free stream ({best_name}), air from the right', 'midplane-speed.png', 'turbo', 0, 1.3, 'U/U∞', 'X (m)', 'Z (m)')
show(cp, ext, 'Mid-plane Y=0: pressure coefficient Cp', 'midplane-cp.png', 'RdBu_r', -1.2, 1.0, 'Cp', 'X (m)', 'Z (m)')
ext2 = (0.7, 1.5, 0.0, 0.5)
sp, cp = slice_img((0, 0, 0.73), 0, 1, ext2, res=2.5e-3)
show(sp, ext2, 'Radiator pod, plan view Z=0.73 m (left side): air speed / free stream', 'pod-plan-speed.png', 'turbo', 0, 1.3, 'U/U∞', 'X (m)', 'Y (m, left)')
show(cp, ext2, 'Radiator pod, plan view Z=0.73 m (left side): pressure coefficient', 'pod-plan-cp.png', 'RdBu_r', -1.2, 1.0, 'Cp', 'X (m)', 'Y (m, left)')

# ---------------------------------------------------------------- radiator pods: through-flow and pressure difference (porous cores)
def foam_field(path):
    b_ = Path(path).read_bytes()
    i = b_.index(b'internalField'); head = b_[i:i + 200].decode('latin1')
    m = re.search(r'List<(\w+)>\s*(\d+)\s*\(', head)
    typ, n = m.group(1), int(m.group(2)); start = i + m.end()
    if b'format      binary' in b_[:400] or b'format binary' in b_[:400]:
        k = 3 if typ == 'vector' else 1
        return np.frombuffer(b_, dtype='<f8', count=n * k, offset=start).reshape(n, k)
    txt = b_[start:].decode('latin1').split(')\n;')[0]
    vals = np.array([float(v) for v in re.sub(r'[()]', ' ', txt).split()]); return vals.reshape(n, -1)
def latest(case):
    ts = sorted([p for p in case.iterdir() if p.is_dir() and re.fullmatch(r'\d+', p.name) and p.name != '0'], key=lambda p: int(p.name))
    return ts[-1]
pods = {}
def pod_analysis(case):
    td = latest(case)
    if not (td / 'C').exists(): return None
    C = foam_field(td / 'C'); P = foam_field(td / 'p')[:, 0] * RHO; Uc = foam_field(td / 'U')
    out = {}
    for side, sg in (('neg', -1), ('pos', 1)):
        n = np.array([-0.572, sg * 0.820, 0.0]); wv = np.array([0.820, -sg * 0.572, 0.0])
        P0 = np.array([0.990, sg * 0.175, 0.0])   # outer-face front corner, z along the core 0.663..0.791
        rel = C - P0; s = rel @ n; u = rel @ wv; z = C[:, 2]
        win = (u > 0.0) & (u < 0.165) & (z > 0.663) & (z < 0.791)
        cdim = {}
        zone = win & (s > -0.028) & (s < 0.0)
        up = win & (s > 0.004) & (s < 0.032); dn = win & (s < -0.032) & (s > -0.060)
        vn = (Uc[zone] @ n)    # through-core velocity, + means outward (reverse)
        out[side] = dict(cells_in_core=int(zone.sum()), mean_through_velocity_ms=round(float(-vn.mean()), 2) if zone.any() else None,
                         ram_factor_vs_70mph=round(float(-vn.mean() / 31.2928), 3) if zone.any() else None,
                         p_upstream_Pa=round(float(P[up].mean()), 1) if up.any() else None, p_downstream_Pa=round(float(P[dn].mean()), 1) if dn.any() else None,
                         cells_up=int(up.sum()), cells_down=int(dn.sum()))
        if up.any() and dn.any(): out[side]['pressure_difference_Pa'] = round(float(P[up].mean() - P[dn].mean()), 1)
        out[side]['volume_flow_m3s'] = round(float(-vn.mean() * 0.165 * 0.128), 4) if zone.any() else None
        # model dP check: dP = 13 v + 2.2 v^2 (the resistance put into the porous zone)
        if zone.any():
            v = -vn.mean(); out[side]['core_model_dP_Pa'] = round(13 * v + 2.2 * v * v, 1)
    return out
for n_, c_ in [(n, RUN / n) for n in results if n in ('m1', 'm2', 'm3', 'm4', 'yaw+10', 'yaw-10')]:
    try:
        pa = pod_analysis(c_)
        if pa: pods[n_] = pa
    except Exception as ex:
        pods[n_] = dict(error=str(ex))
results['pods'] = pods
print(json.dumps(pods, indent=1))
(OUT / 'aero-results.json').write_text(json.dumps(results, indent=1))
print('written', OUT / 'aero-results.json')
