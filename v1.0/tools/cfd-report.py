"""Turn the OpenFOAM baseline run into numbers and pictures.
Run: ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe tools/cfd-report.py [case folder]
Reads postProcessing/forces_*/0/forces.dat (+ moments.dat) and the foamToVTK output, and writes
cfd/results/aero-summary.json plus cfd/results/*.png (mid-plane speed and pressure, top-view speed,
convergence history).

Sign conventions: X forward, Z up, air moves towards -X at U. Drag is the force on the bike towards -X.
Forces are averaged over the last AVG iterations because steady RANS around a bluff body oscillates.
"""
import json, re, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]
CASE=Path(sys.argv[1]) if len(sys.argv)>1 else R/'cfd/case-baseline'
OUT=R/'cfd/results';OUT.mkdir(parents=True,exist_ok=True)
U,RHO,AVG=27.78,1.204,250
Q=0.5*RHO*U**2                  # dynamic pressure, Pa
WB,CX=1.480,0.74                # wheelbase and moment centre (mid-wheelbase, on the ground)

def table(path):
    """Numbers from an OpenFOAM .dat file, ignoring comments and brackets."""
    rows=[]
    for line in path.read_text().splitlines():
        if line.startswith('#') or not line.strip():continue
        rows.append([float(v) for v in re.sub(r'[()]',' ',line).split()])
    return np.array(rows)

def forces(name):
    d=CASE/'postProcessing'/f'forces_{name}'
    A=np.vstack([table(p) for p in sorted(d.glob('*/forces.dat'))])
    # OpenFOAM 12 columns: time, force (pressure xyz, viscous xyz), moment (pressure xyz, viscous xyz)
    Fp,Fv=A[:,1:4],A[:,4:7]
    return A[:,0],Fp+Fv,Fp,Fv,A[:,7:10]+A[:,10:13]

out={'prepared':'2026-11-01 (US Central) by Claude Opus 5.5','speed_kmh':100,'speed_ms':U,
     'rho':RHO,'dynamic_pressure_Pa':round(Q,1),'averaged_over_last_iterations':AVG}
hist={}
for part in ('total','bike','rider','wheels'):
    t,F,Fp,Fv,M=forces(part)
    a=F[-AVG:].mean(0);ap=Fp[-AVG:].mean(0);av=Fv[-AVG:].mean(0);am=M[-AVG:].mean(0)
    drag=-a[0]
    out[part]={'drag_N':round(drag,1),'CdA_m2':round(drag/Q,4),'pressure_drag_share':round(-ap[0]/drag,3) if drag else None,
               'side_force_N':round(a[1],1),'lift_N':round(a[2],1),'ClA_m2':round(a[2]/Q,4),
               'drag_std_last_N':round(float(F[-AVG:,0].std()),1),'iterations':int(t[-1])}
    if part=='total':
        # Axle lift: vertical forces plus the pitching moment about the ground point, split onto the axles.
        dl=-am[1]/CX                # (front - rear) lift
        out[part]['front_axle_lift_N']=round((a[2]+dl)/2,1)
        out[part]['rear_axle_lift_N']=round((a[2]-dl)/2,1)
        out[part]['drag_power_kW_at_100kmh']=round(drag*U/1000,2)
        for v in (80,100,130):
            s=v/3.6;out[part][f'drag_power_kW_at_{v}kmh']=round(drag/Q*0.5*RHO*s**3/1000,2)
    hist[part]=(t,-F[:,0]/Q)
(OUT/'aero-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

fig,ax=plt.subplots(figsize=(9,4.5))
for k,(t,c) in hist.items():ax.plot(t,c,label=k,lw=1.2)
ax.set_xlabel('iteration');ax.set_ylabel('CdA (m²)');ax.set_title('Drag area by part, 100 km/h')
ax.axvspan(hist['total'][0][-AVG],hist['total'][0][-1],color='0.9',label='averaged')
lo=min(np.percentile(c[len(c)//4:],1) for _,c in hist.values());hi=max(np.percentile(c[len(c)//4:],99) for _,c in hist.values())
ax.set_ylim(min(0,lo)-.05,hi*1.25);ax.legend(ncol=5,fontsize=8);ax.grid(alpha=.3)
fig.tight_layout();fig.savefig(OUT/'convergence.png',dpi=130);plt.close(fig)

# ---- flow pictures from the reconstructed latest time (foamToVTK)
import vtk
from vtk.util.numpy_support import vtk_to_numpy
vtkdir=CASE/'VTK'
internal=sorted(vtkdir.glob('*_[1-9]*.vtk'),key=lambda p:int(p.stem.rsplit('_',1)[1]))[-1]   # latest time, internal field
rd=vtk.vtkXMLUnstructuredGridReader() if internal.suffix=='.vtu' else vtk.vtkUnstructuredGridReader()
rd.SetFileName(str(internal));rd.Update()
grid=rd.GetOutput()
c2p=vtk.vtkCellDataToPointData();c2p.SetInputData(grid);c2p.Update();grid=c2p.GetOutput()

def slice_img(origin,normal,ax0,ax1,ext,res=2.5e-3):
    """Sample U and p on a regular grid in a plane; returns speed and Cp images (NaN inside the bike)."""
    nx,ny=int((ext[1]-ext[0])/res),int((ext[3]-ext[2])/res)
    pts=vtk.vtkPoints()
    for j in range(ny):
        for i in range(nx):
            p=list(origin);p[ax0]=ext[0]+i*res;p[ax1]=ext[2]+j*res;pts.InsertNextPoint(p)
    pd=vtk.vtkPolyData();pd.SetPoints(pts)
    pr=vtk.vtkProbeFilter();pr.SetInputData(pd);pr.SetSourceData(grid);pr.Update()
    o=pr.GetOutput();valid=vtk_to_numpy(o.GetPointData().GetArray('vtkValidPointMask')).astype(bool)
    Uv=vtk_to_numpy(o.GetPointData().GetArray('U'));pv=vtk_to_numpy(o.GetPointData().GetArray('p'))
    sp=np.linalg.norm(Uv,axis=1)/U;cp=pv/(0.5*U**2)      # p is kinematic (p/rho)
    sp[~valid]=np.nan;cp[~valid]=np.nan
    return sp.reshape(ny,nx),cp.reshape(ny,nx)

def show(img,ext,title,fname,cmap,vmin,vmax,label,xl,yl):
    fig,ax=plt.subplots(figsize=(12,12*(ext[3]-ext[2])/(ext[1]-ext[0])+1))
    m=ax.imshow(img,origin='lower',extent=ext,cmap=cmap,vmin=vmin,vmax=vmax,interpolation='bilinear')
    ax.set_facecolor('0.15');ax.set_title(title);ax.set_xlabel(xl);ax.set_ylabel(yl)
    fig.colorbar(m,ax=ax,label=label,shrink=.8);fig.tight_layout();fig.savefig(OUT/fname,dpi=130);plt.close(fig)

ext=(-1.2,2.4,0.01,1.9)
sp,cp=slice_img((0,0.0,0),None,0,2,ext)
show(sp,ext,'Mid-plane (Y = 0): air speed / road speed, 100 km/h, air from the right','midplane-speed.png','turbo',0,1.3,'U / U∞','X (m, forward)','Z (m)')
show(cp,ext,'Mid-plane (Y = 0): pressure coefficient Cp','midplane-cp.png','RdBu_r',-1.2,1.0,'Cp','X (m, forward)','Z (m)')
for z in (0.45,0.95):
    ext2=(-1.2,2.4,-0.8,0.8)
    sp,cp=slice_img((0,0,z),None,0,1,ext2)
    show(sp,ext2,f'Top view at Z = {z} m: air speed / road speed','top-speed-z%03d.png'%int(z*100),'turbo',0,1.3,'U / U∞','X (m, forward)','Y (m, left)')
print('pictures in',OUT)

# ---- where the drag comes from: pressure drag of every surface face, summed across the width
def faces(part):
    """Face centres (x, z), and each face's pressure drag in N, from the boundary VTK at the latest time."""
    f=sorted((vtkdir/part).glob(f'{part}_[1-9]*.vtk'),key=lambda p:int(p.stem.rsplit('_',1)[1]))[-1]
    r=vtk.vtkPolyDataReader();r.SetFileName(str(f));r.Update()
    nm=vtk.vtkPolyDataNormals();nm.SetInputData(r.GetOutput());nm.ComputeCellNormalsOn();nm.ComputePointNormalsOff()
    nm.SplittingOff();nm.ConsistencyOff();nm.AutoOrientNormalsOff();nm.Update();o=nm.GetOutput()
    cs=vtk.vtkCellSizeFilter();cs.SetInputData(o);cs.ComputeAreaOn();cs.Update()
    cc=vtk.vtkCellCenters();cc.SetInputData(o);cc.Update()
    A=vtk_to_numpy(cs.GetOutput().GetCellData().GetArray('Area'));n=vtk_to_numpy(o.GetCellData().GetNormals())
    c=vtk_to_numpy(cc.GetOutput().GetPoints().GetData());p=vtk_to_numpy(o.GetCellData().GetArray('p'))
    return c[:,0],c[:,2],-RHO*p*n[:,0]*A        # OpenFOAM face normals point into the body; drag is towards -X

ZONES=[  # (name, part, test on face centre x, z in metres); first match wins
 ('Helmet and shoulders','rider',lambda x,z:z>1.35),
 ('Rider torso and arms','rider',lambda x,z:(z>0.9)&(z<=1.35)),
 ('Rider legs and hips','rider',lambda x,z:z<=0.9),
 ('Screen, headlight, nose','bike',lambda x,z:(x>1.1)&(z>0.75)),
 ('Front fender and fork','bike',lambda x,z:(x>1.1)&(z<=0.75)),
 ('Pack and belly front face','bike',lambda x,z:(x>0.95)&(z<0.7)),
 ('Tank, shroud, dash area','bike',lambda x,z:(x>0.55)&(z>=0.7)),
 ('Mid body: pack sides, motor, pegs','bike',lambda x,z:(x>0.25)&(z<0.7)),
 ('Seat, tail, rear fender, plate','bike',lambda x,z:x<=0.55),
 ('Front wheel','wheel_front',lambda x,z:x==x),
 ('Rear wheel','wheel_rear',lambda x,z:x==x)]
data={p:faces(p) for p in ('bike','rider','wheel_front','wheel_rear')}
zones=[];left={p:np.ones(len(d[0]),bool) for p,d in data.items()}
for name,part,test in ZONES:
    x,z,d=data[part];m=left[part]&test(x,z);left[part]&=~m
    zones.append({'zone':name,'pressure_drag_N':round(float(d[m].sum()),1),'CdA_m2':round(float(d[m].sum())/Q,4)})
tot=sum(z['pressure_drag_N'] for z in zones)
for z in zones:z['share']=round(z['pressure_drag_N']/tot,3)
out['pressure_drag_by_zone']=zones
(OUT/'aero-summary.json').write_text(json.dumps(out,indent=2))
for z in zones:print(f"{z['zone']:36s}{z['pressure_drag_N']:8.1f} N {z['share']*100:6.1f} %")

X=np.concatenate([d[0] for d in data.values()]);Z=np.concatenate([d[1] for d in data.values()]);D=np.concatenate([d[2] for d in data.values()])
b=0.02;H,xe,ze=np.histogram2d(X,Z,bins=[np.arange(-0.45,1.95+b,b),np.arange(0,1.85+b,b)],weights=D)
H=H.T/(b*b)/Q                                   # drag area per m² of side view: dimensionless, sums to CdA
fig,ax=plt.subplots(figsize=(12,8));lim=np.percentile(np.abs(H[H!=0]),98)
m=ax.imshow(np.ma.masked_equal(H,0),origin='lower',extent=(xe[0],xe[-1],ze[0],ze[-1]),cmap='RdBu_r',vmin=-lim,vmax=lim)
ax.set_facecolor('0.92');ax.set_title('Where the drag comes from (side view, summed across the width)\nred adds drag, blue pushes the bike forward');ax.set_xlabel('X (m, forward)');ax.set_ylabel('Z (m)')
fig.colorbar(m,ax=ax,label='drag area per side-view area',shrink=.7);fig.tight_layout();fig.savefig(OUT/'drag-map-side.png',dpi=130);plt.close(fig)
print('drag map written')
