"""Turn the aero-study OpenFOAM runs into numbers and pictures.
Run from v1.0: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe detailed-design/tools/aero-report.py
Reads every finished case in detailed-design/aero/run/*/ (DONE marker) and writes
  detailed-design/aero/aero-results.json   all numbers used in aero-study.md
  detailed-design/aero/*.png               convergence, mesh study, drag map, mid-plane speed / Cp
Conventions: X forward, Y left, Z up, origin at the rear tyre contact point. Air moves towards -X.
Drag (vehicle axis) = -Fx. Air-axis drag = force along the relative wind. CdA = air-axis drag / (0.5 rho Vair^2).
Moments from OpenFOAM are about the origin; they are transferred to the bike CoG (mass-rollup.json) here.
Forces are averaged over the last AVG iterations (steady RANS around a bluff body keeps oscillating).
"""
import json, re, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[2]
RUN=R/'detailed-design/aero/run';OUT=R/'detailed-design/aero';OUT.mkdir(exist_ok=True)
AVG=200
WB=1.4868
mr=json.loads((R/'mass-rollup.json').read_text())
COG=np.array([mr['cog_mm']['x_from_rear_axle'],0.0,mr['cog_mm']['height']])/1000
BIKE_KG=mr['total_kg']
PARTS=['screen','mirrors','bars_controls','fairing_tank','fork_fender','lower_body','swingarm_pegs','seat_tail',
       'rider_helmet','rider_torso_arms','rider_legs','wheel_front','wheel_rear']

def table(path):
    rows=[]
    for line in path.read_text().splitlines():
        if line.startswith('#') or not line.strip():continue
        rows.append([float(v) for v in re.sub(r'[()]',' ',line).split()])
    return np.array(rows)

def forces(case,name):
    A=table(case/'postProcessing'/f'forces_{name}'/'0'/'forces.dat')
    A=A[np.unique(A[:,0],return_index=True)[1]]
    return dict(t=A[:,0],Fp=A[:,1:4],Fv=A[:,4:7],F=A[:,1:4]+A[:,4:7],M=A[:,7:10]+A[:,10:13])

def cells(case):
    m=re.search(r'cells:\s+(\d+)',(case/'log.checkMesh').read_text());return int(m.group(1))

def case_result(case):
    cj=json.loads((case/'case.json').read_text())
    U=np.array(cj['U_air']);Va=np.linalg.norm(U);q=0.5*cj['rho']*Va**2;ehat=U/Va   # unit vector along the wind
    res=dict(case=case.name,yaw_deg=cj['yaw_deg'],base_cell_m=cj['base_cell_m'],cells=cells(case),air_speed_ms=round(Va,3),
             q_Pa=round(q,1),iterations=None,parts={})
    hist={}
    for name in ['total','bike_body','rider','wheels']+PARTS:
        f=forces(case,name);n=min(AVG,len(f['t'])//3)
        F=f['F'][-n:].mean(0);Fp=f['Fp'][-n:].mean(0);Fv=f['Fv'][-n:].mean(0);M=f['M'][-n:].mean(0)
        dair=float(F@ehat);dveh=-F[0]
        r=dict(drag_air_N=round(dair,2),CdA_m2=round(dair/q,4),drag_vehicle_axis_N=round(dveh,2),
               pressure_drag_N=round(float(Fp@ehat),2),viscous_drag_N=round(float(Fv@ehat),2),
               side_force_N=round(F[1],2),lift_N=round(F[2],2))
        if name=='total':
            res['iterations']=int(f['t'][-1])
            cda=(f['F']@ehat)/q;hist['cda']=(f['t'],cda)
            w=cda[-n:];prev=cda[-2*n:-n]
            r.update(CdA_std_window=round(float(w.std()),4),CdA_min_window=round(float(w.min()),4),CdA_max_window=round(float(w.max()),4),
                     drift_last_vs_previous_window_pct=round(100*(w.mean()-prev.mean())/w.mean(),2))
            My=M[1];Lf=-My/WB;Lr=F[2]-Lf                          # moments about the rear contact point
            Mcog=M-np.cross(COG,F)                                   # M_P = M_O - r_P x F
            r.update(front_axle_lift_N=round(Lf,1),rear_axle_lift_N=round(Lr,1),
                     yaw_moment_about_cog_Nm=round(Mcog[2],1),roll_moment_about_cog_Nm=round(Mcog[0],1),
                     pitch_moment_about_cog_Nm=round(Mcog[1],1),roll_moment_about_ground_Nm=round(M[0],1),
                     side_force_centre_x_m=round(M[2]/F[1],3) if abs(F[1])>5 else None,
                     side_force_centre_z_m=round(-M[0]/F[1],3) if abs(F[1])>5 else None,
                     moment_reference=f'CoG {COG.tolist()} m (mass-rollup.json, bike only)')
            hist['parts']={p:(forces(case,p)['t'],(forces(case,p)['F']@ehat)/q) for p in ('bike_body','rider','wheels')}
        res['parts'][name]=r
    # y+ at the final time
    yp=(case/'postProcessing/yPlus/0/yPlus.dat').read_text().splitlines()
    last=[l.split() for l in yp if l and not l.startswith('#')];tl=last[-1][0]
    res['yplus']={l[1]:dict(min=round(float(l[2]),2),max=round(float(l[3]),1),avg=round(float(l[4]),1)) for l in last if l[0]==tl}
    # mass balance
    fr=table(case/'postProcessing/flowRates/0/surfaceFieldValue.dat')
    inflow=abs(U[0])*7.0*3.99+abs(U[1])*13.5*3.99
    res['net_mass_flux_pct_of_inflow']=round(100*abs(fr[-1,1])/inflow,4)
    cont=re.findall(r'sum local = ([0-9.eE+-]+)',(case/'log.foamRun').read_text())
    res['continuity_sum_local_last']=float(cont[-1]) if cont else None
    et=re.findall(r'ExecutionTime = ([0-9.]+) s',(case/'log.foamRun').read_text())
    res['solver_hours']=round(float(et[-1])/3600,2) if et else None
    return res,hist,q,ehat

cases=sorted([p for p in RUN.iterdir() if (p/'DONE').exists()])
results={};hists={}
for c in cases:
    r,h,q,e=case_result(c);results[c.name]=r;hists[c.name]=(h,q,e)
    t=r['parts']['total'];print(f"{c.name:10s} cells {r['cells']:9d} CdA {t['CdA_m2']:.4f}  drift {t['drift_last_vs_previous_window_pct']}%  std {t['CdA_std_window']}")

# ---- mesh study (0 deg cases)
mesh=[(n,results[n]) for n in ('m1-coarse','m2-medium','m3-fine') if n in results]
study={'cases':[dict(case=n,cells=r['cells'],base_cell_m=r['base_cell_m'],CdA=r['parts']['total']['CdA_m2'],
                     front_lift=r['parts']['total']['front_axle_lift_N'],rear_lift=r['parts']['total']['rear_axle_lift_N']) for n,r in mesh]}
if len(mesh)==3:
    f1,f2,f3=[r['parts']['total']['CdA_m2'] for _,r in mesh[::-1]]   # f1 fine
    rr=math.sqrt(2)
    e21,e32=f2-f1,f3-f2          # medium-fine and coarse-medium changes
    study['change_medium_to_fine_pct']=round(100*(f1-f2)/f2,2);study['change_coarse_to_medium_pct']=round(100*(f2-f3)/f3,2)
    Rr=e21/e32 if abs(e32)>1e-12 else float('inf')   # convergence ratio (Roache): 0<R<1 monotonic convergence
    study['convergence_ratio_R']=round(Rr,3)
    if 0<Rr<1:
        p=math.log(1/Rr)/math.log(rr);ext=f1+(f1-f2)/(rr**p-1)
        study.update(behaviour='monotonic convergence',observed_order=round(p,2),richardson_CdA=round(ext,4),
                     GCI_fine_pct=round(100*1.25*abs((f1-f2)/f1)/(rr**p-1),2))
    else:
        study.update(behaviour='oscillatory' if Rr<0 else 'not converged (change grows with refinement; outside the asymptotic range, no Richardson estimate)',
                     spread_of_three_meshes_pct=round(100*(max(f1,f2,f3)-min(f1,f2,f3))/f1,2))
results['mesh_study']=study
print(json.dumps(study,indent=1))

# ---- range at 70 mph, energy model of tools/powertrain-optimise.py
RHO,G,CRR,ETA,AUX,USABLE,RIDER=1.225,9.80665,0.015,0.90,300,0.90,90
PACK=32.7
def whmi(cda,mph=70,kg=BIKE_KG):
    v=mph*0.44704;return ((0.5*RHO*cda*v**3+CRR*(kg+RIDER)*G*v)/ETA+AUX)/mph
best=results.get('m3-fine',results.get('m2-medium',results.get('m1-coarse')))
cda0=best['parts']['total']['CdA_m2']
rng={}
for lab,c in [('cfd_best_mesh',cda0),('cfd_plus_10pct_real_rider',cda0*1.10),('design_assumption_0.40',0.40),('target_0.38',0.38)]:
    w=whmi(c);rng[lab]=dict(CdA=round(c,4),Wh_per_mile=round(w,1),range_mi=round(PACK*1000*USABLE/w,1),
                            kWh_nominal_for_200mi=round(w*200/1000/USABLE,1),aero_share_of_wheel_power=round(0.5*RHO*c*31.2928**3/(0.5*RHO*c*31.2928**3+CRR*(BIKE_KG+RIDER)*G*31.2928),3))
rng['inputs']=dict(bike_kg=BIKE_KG,rider_kg=RIDER,pack_kWh=PACK,usable=USABLE,crr=CRR,eta=ETA,aux_W=AUX,rho=RHO,mph=70,
                   source='tools/powertrain-optimise.py wh_per_mile() constants; mass-rollup.json total_kg')
results['range_70mph']=rng
print(json.dumps(rng,indent=1))

# ---- pictures: convergence of every case, part history of the best 0-deg case, mesh study
fig,ax=plt.subplots(figsize=(10,4.8))
for n,(h,q,e) in hists.items():
    t,c=h['cda'];ax.plot(t,c,lw=1.1,label=n)
ax.axvspan(400,600,color='0.92',label='averaged window');ax.set_ylim(0.2,0.8);ax.grid(alpha=.3)
ax.set_xlabel('iteration');ax.set_ylabel('CdA (m², air axis)');ax.set_title('Drag area history, every case, 70 mph');ax.legend(fontsize=8,ncol=3)
fig.tight_layout();fig.savefig(OUT/'convergence.png',dpi=130);plt.close(fig)
if len(mesh)>=2:
    fig,ax=plt.subplots(figsize=(6,4))
    N=[r['cells'] for _,r in mesh];C=[r['parts']['total']['CdA_m2'] for _,r in mesh]
    ax.plot([n**(-1/3) for n in N],C,'o-');[ax.annotate(f'{n/1e6:.2f}M',(x**(-1/3),c),textcoords='offset points',xytext=(5,5)) for n,c,x in zip(N,C,N)]
    if 'richardson_CdA' in study:ax.plot([0],[study['richardson_CdA']],'k*',label='Richardson extrapolation');ax.legend()
    ax.set_xlabel('cells$^{-1/3}$ (0 = infinitely fine)');ax.set_ylabel('CdA (m²)');ax.set_xlim(left=0);ax.grid(alpha=.3)
    ax.set_title('Mesh sensitivity, 0° yaw');fig.tight_layout();fig.savefig(OUT/'mesh-study.png',dpi=130);plt.close(fig)

# ---- surface breakdown and flow pictures from the best 0-deg case
import vtk
from vtk.util.numpy_support import vtk_to_numpy
bc=RUN/best['case'];U0=best['air_speed_ms'];Q=best['q_Pa'];RHO_=1.225
def faces(part):
    f=sorted((bc/'VTK'/part).glob(f'{part}_[1-9]*.vtk'))[-1]
    r=vtk.vtkPolyDataReader();r.SetFileName(str(f));r.Update()
    nm=vtk.vtkPolyDataNormals();nm.SetInputData(r.GetOutput());nm.ComputeCellNormalsOn();nm.ComputePointNormalsOff()
    nm.SplittingOff();nm.ConsistencyOff();nm.AutoOrientNormalsOff();nm.Update();o=nm.GetOutput()
    cs=vtk.vtkCellSizeFilter();cs.SetInputData(o);cs.ComputeAreaOn();cs.Update()
    cc=vtk.vtkCellCenters();cc.SetInputData(o);cc.Update()
    A=vtk_to_numpy(cs.GetOutput().GetCellData().GetArray('Area'));n=vtk_to_numpy(o.GetCellData().GetNormals())
    c=vtk_to_numpy(cc.GetOutput().GetPoints().GetData());p=vtk_to_numpy(o.GetCellData().GetArray('p'))
    yp=o.GetCellData().GetArray('yPlus');yp=vtk_to_numpy(yp) if yp is not None else None
    return c,-RHO_*p*n[:,0]*A,A,yp
data={p:faces(p) for p in PARTS}
# sign check: summed face pressure drag vs forces function object (normals point into the body in OpenFOAM VTK)
chk={p:(round(float(d[1].sum()),1),best['parts'][p]['pressure_drag_N']) for p,d in data.items()}
sgn=1 if sum(a for a,b in chk.values())*sum(b for a,b in chk.values())>0 else -1
results['vtk_pressure_drag_check']={p:dict(vtk_sum_N=sgn*a,function_object_N=b) for p,(a,b) in chk.items()}
# area-weighted y+ distribution per part
ypd={}
for p,(c,d,A,yp) in data.items():
    if yp is None:continue
    o=np.argsort(yp);cw=np.cumsum(A[o])/A.sum()
    ypd[p]={f'p{k}':round(float(yp[o][np.searchsorted(cw,k/100)]),1) for k in (5,50,95)}
    ypd[p]['area_share_below_30_pct']=round(100*float(A[yp<30].sum()/A.sum()),1)
results['yplus_area_weighted']=ypd
# zones inside the large patches
ZONES=[('fairing_tank','Nose / headlamp / beak (X>1.30)',lambda c:c[:,0]>1.30),
       ('fairing_tank','Cockpit cheeks and dash (1.05<X<=1.30)',lambda c:(c[:,0]>1.05)&(c[:,0]<=1.30)),
       ('fairing_tank','Tank and radiator side vents (X<=1.05)',lambda c:c[:,0]<=1.05),
       ('lower_body','Pack front face and belly nose (X>0.95)',lambda c:c[:,0]>0.95),
       ('lower_body','Pack sides, motor covers (X<=0.95)',lambda c:c[:,0]<=0.95),
       ('seat_tail','Seat',lambda c:c[:,2]>0.86),('seat_tail','Tail, plate, rear hugger',lambda c:c[:,2]<=0.86)]
results['zones']=[dict(part=p,zone=z,pressure_drag_N=round(sgn*float(data[p][1][f(data[p][0])].sum()),1)) for p,z,f in ZONES]
# side-view drag map
X=np.concatenate([d[0][:,0] for d in data.values()]);Z=np.concatenate([d[0][:,2] for d in data.values()]);Dd=sgn*np.concatenate([d[1] for d in data.values()])
b=0.02;Hh,xe,ze=np.histogram2d(X,Z,bins=[np.arange(-0.45,1.95+b,b),np.arange(0,1.85+b,b)],weights=Dd);Hh=Hh.T/(b*b)/Q
fig,ax=plt.subplots(figsize=(12,8));lim=np.percentile(np.abs(Hh[Hh!=0]),98)
m=ax.imshow(np.ma.masked_equal(Hh,0),origin='lower',extent=(xe[0],xe[-1],ze[0],ze[-1]),cmap='RdBu_r',vmin=-lim,vmax=lim)
ax.set_facecolor('0.92');ax.set_title(f'Where the drag comes from ({best["case"]}, side view summed across the width)\nred adds drag, blue pushes the bike forward')
ax.set_xlabel('X (m, forward)');ax.set_ylabel('Z (m)');fig.colorbar(m,ax=ax,label='drag area per side-view area',shrink=.7)
fig.tight_layout();fig.savefig(OUT/'drag-map-side.png',dpi=130);plt.close(fig)
# mid-plane and plan slices
internal=sorted((bc/'VTK').glob(f'{bc.name}_[1-9]*.vtk'))[-1]
rd=vtk.vtkUnstructuredGridReader();rd.SetFileName(str(internal));rd.Update()
c2p=vtk.vtkCellDataToPointData();c2p.SetInputData(rd.GetOutput());c2p.Update();grid=c2p.GetOutput()
def slice_img(origin,ax0,ax1,ext,res=5e-3):
    nx,ny=int((ext[1]-ext[0])/res),int((ext[3]-ext[2])/res)
    g=np.zeros((ny*nx,3));I,J=np.meshgrid(np.arange(nx),np.arange(ny))
    g[:]=origin;g[:,ax0]=ext[0]+I.ravel()*res;g[:,ax1]=ext[2]+J.ravel()*res
    pts=vtk.vtkPoints()
    for p in g:pts.InsertNextPoint(p)
    pd=vtk.vtkPolyData();pd.SetPoints(pts)
    pr=vtk.vtkProbeFilter();pr.SetInputData(pd);pr.SetSourceData(grid);pr.Update();o=pr.GetOutput()
    valid=vtk_to_numpy(o.GetPointData().GetArray('vtkValidPointMask')).astype(bool)
    sp=np.linalg.norm(vtk_to_numpy(o.GetPointData().GetArray('U')),axis=1)/U0;cp=vtk_to_numpy(o.GetPointData().GetArray('p'))/(0.5*U0**2)
    sp[~valid]=np.nan;cp[~valid]=np.nan;return sp.reshape(ny,nx),cp.reshape(ny,nx)
def show(img,ext,title,fname,cmap,vmin,vmax,label,xl,yl):
    fig,ax=plt.subplots(figsize=(12,12*(ext[3]-ext[2])/(ext[1]-ext[0])+1))
    m=ax.imshow(img,origin='lower',extent=ext,cmap=cmap,vmin=vmin,vmax=vmax,interpolation='bilinear')
    ax.set_facecolor('0.15');ax.set_title(title);ax.set_xlabel(xl);ax.set_ylabel(yl)
    fig.colorbar(m,ax=ax,label=label,shrink=.8);fig.tight_layout();fig.savefig(OUT/fname,dpi=120);plt.close(fig)
ext=(-1.2,2.4,0.01,2.0)
sp,cp=slice_img((0,0,0),0,2,ext)
show(sp,ext,f'Mid-plane Y=0: air speed / free stream ({best["case"]}), air from the right','midplane-speed.png','turbo',0,1.3,'U/U∞','X (m)','Z (m)')
show(cp,ext,'Mid-plane Y=0: pressure coefficient Cp','midplane-cp.png','RdBu_r',-1.2,1.0,'Cp','X (m)','Z (m)')
sp,cp=slice_img((0,0.33,0),0,2,ext)
show(sp,ext,'Plane Y=0.33 m (through the hand / mirror line): air speed / free stream','y033-speed.png','turbo',0,1.3,'U/U∞','X (m)','Z (m)')
ext2=(-1.2,2.4,-0.9,0.9)
for z in (0.45,1.15):
    sp,cp=slice_img((0,0,z),0,1,ext2)
    show(sp,ext2,f'Plan view Z={z} m: air speed / free stream','top-speed-z%03d.png'%int(z*100),'turbo',0,1.3,'U/U∞','X (m)','Y (m, left)')
(OUT/'aero-results.json').write_text(json.dumps(results,indent=1))
print(json.dumps({k:results[k] for k in ('zones','yplus_area_weighted','vtk_pressure_drag_check')},indent=1))
print('written',OUT/'aero-results.json')
