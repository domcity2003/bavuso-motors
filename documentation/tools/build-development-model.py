"""Reproducible screening data and packaging reservations; not production CAD.
Python standard library only. Run from any directory. October 25, 2026.
"""
from pathlib import Path
import csv, json, math, html

ROOT = Path(__file__).resolve().parents[1]

def write_csv(name, rows):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

REQ = [
('200 mile highway range','Owner','200 mi at 70 mph baseline; claim conditions open','Vehicle energy','Measured road load, usable energy and full-distance test','Open'),
('125+ mph top speed','Owner','Strictly above 125 mph; duration/SOC conditions open','Drive/chassis','Mapped drive and closed-course speed/thermal test','Open'),
('Tesla charging','Owner','Actual authorized station use, not only connector fit','Charging','Network eligibility and successful approved-site AC/DC sessions','Open'),
('Complete bike mass','Owner preference','Less than 400 lb; no relaxed ceiling approved','Systems','Configuration-specific reconciled BOM and calibrated weighing','Open gap'),
('Highway comfort and wind confidence','Owner','77 mph design speed; quantified comfort/handling limits open','Chassis/aero','Rider trials, aero moments and closed-course handling','Open'),
('Broad rider fit','Owner intent','Adjustable comfortable ordinary upright posture; population bounds open','Human factors','Adjustable buck with measured rider sample and gear','Open'),
('Appearance variants','Owner direction','Common body in matte black/silver/tan; physical standards open','Body','Owner visual review and physical finish samples','Open'),
('Optional saddlebags','Owner direction','Discreet removable mounts; capacity/rating open','Chassis/body','Structural proof/fatigue, loaded handling/clearance/aero','Open'),
('Independent friction braking','Proposed safety function','Required stopping/fade with zero regenerative braking','Brakes','Applicable brake tests in regen unavailable cases','Open'),
('Unintended torque prevention','Proposed safety function','Demand plausibility, torque arbitration and fault response defined','Controls','Safety analysis, HIL and fault-injection evidence','Open'),
('HV protection','Proposed safety function','Touch/isolation/overcurrent protection across full fault envelope','Electrical','Coordination study and instrumented fault/environmental tests','Open'),
('Charge/drive exclusion','Proposed safety function','No propulsion while connected; safe AC/DC route selection','Charging/controls','Interlock/state-machine faults and physical integration tests','Open'),
('Thermal capability','Proposed','Cell/drive limits at speed and stationary charging; ambient envelope open','Thermal','Calibrated heat rejection model and thermal tests','Open'),
('Pack retention and fault containment','Proposed safety function','Impact/fatigue/vent/seal/swelling boundaries defined','Pack/chassis','Supplier cell data, structural analysis and pack tests','Open'),
('Dynamic clearance','Proposed','No contact throughout motion/tolerance envelope; numerical margins open','Packaging','Steer/bump/lean/drive/gear/service swept CAD and physical checks','Open'),
('Structural durability','Proposed','GVWR/duty spectrum must precede strength and fatigue limits','Chassis','Correlated FEA, coupons, weld/joint and rig tests','Open'),
('Serviceability','Proposed','Pack removal, fault isolation and normal service by defined equipment','Manufacturing/service','Dry-run access/removal and released service instructions','Open'),
('Road equipment','Proposed','Complete lamps/reflectors/mirrors/horn/instruments/plate equipment','Compliance/body','Jurisdiction matrix and installation compliance tests','Open'),
('Service life and battery retention','Product decision needed','Life, cycles, calendar aging and range retention limits unset','Systems/pack','Owner limits then supplier/vehicle aging evidence','Open'),
('Market compliance','Product decision needed','US-first study; sales markets and classification need confirmation','Compliance','Current applicability review and required compliance records','Open'),
('Configuration reproducibility','Proposed','Every installed part revision/calibration/finish and deviation traceable','Quality','Build configuration audit against serialized unit','Open'),
('Software release','Proposed','Versioned source/configuration, compatible firmware and reproducible artifacts','Controls','Reviewed releases, checksums, HIL/integration evidence','Open'),
('EMC','Proposed','No unsafe disturbance or excess emissions under applicable regime','Electrical','Harness-aware EMC precompliance and required final tests','Open'),
('Environmental durability','Proposed','Rain/wash/salt/vibration/temperature limits to be set','Systems','Rated component installation and vehicle environmental tests','Open'),
('Supply assurance','Proposed','Actual specified cell, motor and safety systems obtainable and supported','Procurement','Dated supplier confirmations/configured quotations','Open'),
('Low voltage reserve','Proposed','Critical controls and fault response survive defined DC/DC failures','Electrical','LV load/duration budget and brownout tests','Open'),
('120 V AC charging','Unresolved capability','Do not claim until exact OBC input supports it','Charging','Datasheet/configuration and charge tests at selected supply','Open'),
('Range claim definition','Product decision needed','Temperature, wind, payload, SOH, reserve and repeatability set before claim','Systems','Approved claim protocol and traceable evidence','Open'),
('Low-SOC drive capability','Proposed','Power/speed/derating across loaded voltage window, not nominal only','Drive/pack','Dynamometer map with loaded pack constraints','Open'),
('Brake thermal endurance','Proposed','Repeated stops at defined load/speed/interval without unacceptable fade','Brakes','Instrumented fade/recovery test and rotor/pad limits','Open'),
('Incoming traceability','Proposed','Cell lots, safety hardware, materials and firmware tied to build','Quality','Incoming acceptance and serialized traveler','Open'),
('Payload and GVWR','Product decision needed','Rated rider/luggage/passenger and axle loads unset','Systems/chassis','Owner decision plus load/tire/structure/brake reconciliation','Open'),
('Finish durability','Proposed','Paint/seat/panel durability and repair criteria unset','Body','Physical coupons, weathering, cleaning and abrasion tests','Open'),
('Diagnostics and security','Proposed','Gloved local fault indication; no remote/cloud dependency for safety','Controls','Threat/fault analysis and diagnostic access tests','Open'),
('Manufacturing definition','Proposed','Every custom part drawing/process/inspection and joint specification released','Manufacturing','First article and manufacturing readiness review','Open'),
]
requirements = [dict(id=f'R{i:03}',title=r[0],origin=r[1],requirement=r[2],owner=r[3],closure_evidence=r[4],status=r[5]) for i,r in enumerate(REQ,1)]
write_csv('registers/requirements.csv',requirements)

IF = [
('Pack','Frame','Mounting/retention','Mount coordinates, reaction loads, crash/fatigue, tolerance, isolation, removal'),
('Cells','Pack restraints','Compression/growth','Supplier pressure/flatness/swelling/temperature and aged-cell tolerances'),
('Pack','Thermal','Cold plates/ports','Flow resistance, thermal contact, coolant compatibility, leak isolation'),
('Pack','HV distribution','DC power','Operating/fault voltage/current, disconnect, coordination, terminals and insulation'),
('HV distribution','Inverter','Traction feed','DC-link capacitance, precharge, discharge, ripple and fault withstand'),
('Inverter','Motor','Three phase','Exact winding/current conventions, phase cables, sensor and switching compatibility'),
('Motor','Frame','Mounts/airflow','Register/bolt circle, shaft loads, rotor clearance, cooling air and service access'),
('Motor','Final drive','Torque/shaft','Adapter, support, belt radial load and fatigue, concentricity'),
('Final drive','Swingarm/rear wheel','Belt geometry','Tooth count, pitch, width, travel tension, alignment, guard clearance'),
('Swingarm','Frame','Pivot/linkage','Axis, bearings/seals, rear motion ratio, stiffness, service/removal'),
('Fork/yokes','Frame','Steering','Bearing fits, rake/trail, steering lock/stops, clamp joints'),
('Wheels','Axles','Rotating support','Bearing/spacer/seal stack, fits, retention and axle torque'),
('Tires','Wheels','Bead/load/speed','Approved rim widths, load/speed/radius/growth, TPMS if selected'),
('Calipers/rotors','Wheels/fork/swingarm','Friction braking','Offset, rotor attachment, carrier loads and swept clearance'),
('Master cylinders','Calipers/ABS','Hydraulics','Bore/ratio, pressure/volume, hose movement, fluid, bleeding'),
('ABS/IMU','VCU/inverter','Regen coordination','Wheel speeds, slip intervention, priorities, limits, loss-of-comms response'),
('Throttle/brake/stand','VCU','Rider/permission inputs','Redundancy, plausibility, default states, timing and diagnostics'),
('BMS','VCU/inverter/EVCC','Limits/status','SOC/SOH, cell/temperature/voltage/current limits, validity, timeouts'),
('NACS inlet','Charge routing','Shared AC/DC contacts','Selected inlet drawing, CP/PP/PE, locking, temperature, drainage and sequencing'),
('Charge routing','OBC','AC path','Input protection, isolation, voltage/frequency, conductive leakage and EMC'),
('Charge routing','HV distribution','DC path','Interlocks, polarity, weld detection and fault coordination'),
('EVCC','Station/BMS/VCU','Protocol/session','Protocol versions, permission sequence, limits and station compatibility'),
('HV distribution','DC/DC','LV supply','Operating window, startup, isolation, quiescent drain and protection'),
('LV battery','LV distribution','Reserve power','Chemistry, current/time budget, cold behavior, charging and fuse coordination'),
('Thermal','Motor/inverter/OBC','Drive heat rejection','Hot inlet limits, pressure drop, parallel/series routing, airflow'),
('Thermal','Body','Radiators/ducts','Pressure drop, inlet/exhaust, stationary fans, rain/debris and service'),
('Body/screen','Frame','Panels/brackets','Mount loads/fatigue, edge treatment, finish, fasteners and removal sequence'),
('Seat/bar/pegs','Rider','Human package','Anthropometry, adjustment, reach, support, clearance and local loads'),
('Bags','Subframe','Accessory retention','Rated load, mounting proof/fatigue, wheel/heat clearance and loaded CG'),
('Lighting/mirrors','Body/harness','Road visibility','Approved functions, fields/angles, adjustment, power and EMC'),
('Harness','Moving assemblies','Movement/environment','Bend/torsion, clips, chafe, water path, shield, full steering/travel'),
('Charger cable','Parked bike/stand','User handling','Cable reach/force, inlet position, tip stability and lock access'),
('Service tools','Pack/vehicle','Workshop isolation','Access, lifting points/load, zero-energy verification and discharge test provisions'),
('VCU/BMS/inverter/EVCC','Release configuration','Firmware/calibration','Compatibility matrix, versions/checksums, secure diagnostic access and recovery'),
('Manufacturing','Custom parts','Datum/inspection','Released CAD/drawings, materials/process, joint/torque specs and FAI'),
]
interfaces = [dict(id=f'IF{i:03}',side_a=a,side_b=b,interface=c,required_definition=d,status='Open - not released') for i,(a,b,c,d) in enumerate(IF,1)]
write_csv('registers/interfaces.csv', interfaces)

LB = 0.45359237
def load(mph,cda,bike,eta=.90,aux=300,wind=0):
    v=mph*.44704; air=(mph+wind)*.44704
    return (.5*1.225*cda*air*air+.015*(bike+90)*9.80665)*v/eta+aux
def cda_limit(energy,bike,health=1):
    v=70*.44704
    return ((energy*1000*.9*health/200*70-300)*.9/v-.015*(bike+90)*9.80665)/(.5*1.225*v*v)
trades=[]
for p in (6,7,8,9):
    n=100*p; cell=n*.0973; kwh=n*37.57/1000
    for fraction,outside,label in ((.8,99.05,'Reference allocations'),(.85,95.5,'Focused mass target - unproven'),(.85,88,'Aggressive integration - unproven')):
        mass=cell/fraction+outside; allowance=.05*(mass-cell)
        allowance_mass=mass+allowance
        # Positive cell-mass tolerance with hardware and allowance held fixed.
        # Do not scale enclosure/cooling mass upwards with heavier cell lots.
        max_cell_mass_increment=n*.002
        max_cell_mass=allowance_mass+max_cell_mass_increment
        for cda in (.28,.30,.33,.35,.40,.50):
            watts=load(70,cda,mass)
            allowance_watts=load(70,cda,allowance_mass)
            max_cell_mass_watts=load(70,cda,max_cell_mass)
            trades.append(dict(series=100,parallel=p,cells=n,typical_kwh=kwh,minimum_kwh=n*36.72/1000,
                basis=label,cell_fraction=fraction,nonpack_kg=outside,pack_kg=cell/fraction,bike_lb=mass/LB,
                bike_with_allowance_lb=(mass+allowance)/LB,cda=cda,range_70_mi=kwh*1000*.9/(watts/70),
                range_70_allowance_mass_mi=kwh*1000*.9/(allowance_watts/70),
                range_70_allowance_minimum_cell_wh_mi=n*36.72*.9/(allowance_watts/70),
                max_cell_mass_increment_kg=max_cell_mass_increment,
                bike_with_allowance_max_cell_mass_lb=max_cell_mass/LB,
                range_70_minimum_cell_wh_max_cell_mass_mi=n*36.72*.9/(max_cell_mass_watts/70),
                cda_max_200_minimum_cell_wh_max_cell_mass=cda_limit(n*36.72/1000,max_cell_mass),
                range_70_90pct_soh_mi=kwh*1000*.9*.9/(watts/70),
                range_70_minimum_cell_wh_mi=n*36.72*.9/(watts/70),
                cda_max_200_new=cda_limit(kwh,mass),cda_max_200_90pct_soh=cda_limit(kwh,mass,.9),
                typical_charge_a=p*10.8,maximum_charge_a=p*21.6,
                discharge_a_at_70kw_250v=280,cell_a_at_70kw_250v=280/p,
                meets_mass_with_allowance=(mass+allowance)/LB<400,
                meets_screened_range=kwh*1000*.9/(watts/70)>=200))
write_csv('research/configuration-trades.csv',trades)
assert len(trades)==72
assert abs(load(70,.35,196.35)-30.056*1000*.9/208.915688272072*70)<1e-6
assert cda_limit(30.056,196.35)>.36
assert load(77,.35,196.35)>load(70,.35,196.35)
for row in trades:
    assert row['range_70_mi']>row['range_70_allowance_mass_mi']
    assert row['range_70_allowance_mass_mi']>row['range_70_allowance_minimum_cell_wh_mi']
    assert row['range_70_allowance_minimum_cell_wh_mi']>row['range_70_minimum_cell_wh_max_cell_mass_mi']
    assert abs((row['bike_with_allowance_max_cell_mass_lb']-row['bike_with_allowance_lb'])*LB-row['cells']*.002)<1e-10
focused=next(row for row in trades if row['parallel']==7 and row['basis'].startswith('Focused') and row['cda']==.30)
assert abs(focused['range_70_allowance_mass_mi']-208.60662040095534)<1e-8
assert focused['bike_with_allowance_lb']<400<focused['bike_with_allowance_max_cell_mass_lb']

# X forward, Y left, Z up; rear contact origin. Values are layout experiments.
boxes=[
    dict(id='PKG01',name='Battery reservation',x=470,y=-130,z=160,l=600,w=260,h=560,color='#f0b34f',basis='Earlier 87.36 L reservation; not a validated pack'),
    dict(id='PKG02',name='Inverter reservation',x=700,y=-175,z=740,l=330,w=350,h=110,color='#65b6db',basis='Body plus installation allowance; orientation speculative'),
    dict(id='PKG03',name='OBC reservation',x=300,y=-150,z=750,l=390,w=300,h=100,color='#7dd3b0',basis='Compact charger body plus services; not selected'),
    dict(id='PKG04',name='Front radiator study',x=1080,y=-160,z=370,l=90,w=320,h=310,color='#ee8e9b',basis='Unsized heat exchanger/fan reservation'),
    dict(id='PKG05',name='Rear shock/linkage keepout',x=400,y=-90,z=420,l=190,w=180,h=290,color='#cfa4e8',basis='Unsolved linkage path; not supplier dimensions'),
]
points=dict(rear_axle=[0,0,311.9],front_axle=[1420,0,299.9],swingarm_pivot=[550,0,390],
            motor_axis=[350,0,335],seat_reference=[450,0,810],grip_reference=[950,340,1080],peg_reference=[410,180,350])
# Cylinders along Y use full circular side envelopes, not detailed tire toroids
# or manufacturer motor installation geometry. They reveal reservation clashes.
cylinders=[
    dict(id='PKG06',name='Motor body envelope',x=350,y=0,z=335,r=104,w=85),
    dict(id='PKG07',name='Rear tire envelope',x=0,y=0,z=311.9,r=311.9,w=160),
    dict(id='PKG08',name='Front tire envelope',x=1420,y=0,z=299.9,r=299.9,w=120),
]
package=dict(status='Reservation study only. Known conflicts intentional and unresolved.',units='mm',
    coordinates='X forward Y left Z up; rear contact origin',wheelbase=1420,points=points,boxes=boxes,cylinders=cylinders)
(ROOT/'models'/'package-reservations.json').write_text(json.dumps(package,indent=2),encoding='utf-8')

conflicts=[]
for i,a in enumerate(boxes):
    for b in boxes[i+1:]:
        overlap=[max(0,min(a[d]+a[s],b[d]+b[s])-max(a[d],b[d])) for d,s in (('x','l'),('y','w'),('z','h'))]
        if all(v>0 for v in overlap):
            conflicts.append(dict(item_a=a['id'],item_b=b['id'],issue='Reservation boxes overlap; not proof real parts collide',overlap_x_mm=overlap[0],overlap_y_mm=overlap[1],overlap_z_mm=overlap[2],status='Open'))
pack=boxes[0]; pivot=points['swingarm_pivot']
if all(pack[d]<=pivot[i]<=pack[d]+pack[s] for i,(d,s) in enumerate((('x','l'),('y','w'),('z','h')))):
    conflicts.append(dict(item_a='PKG01',item_b='Swingarm pivot',issue='Proposed pivot point lies inside rectangular battery reservation',overlap_x_mm='',overlap_y_mm='',overlap_z_mm='',status='Open - reshape pack or relocate architecture'))
def y_overlap(a_center,a_width,b_min,b_width):
    return min(a_center+a_width/2,b_min+b_width)-max(a_center-a_width/2,b_min)>0

for cylinder in cylinders:
    for box in boxes:
        if not y_overlap(cylinder['y'],cylinder['w'],box['y'],box['w']):
            continue
        dx=max(box['x']-cylinder['x'],0,cylinder['x']-(box['x']+box['l']))
        dz=max(box['z']-cylinder['z'],0,cylinder['z']-(box['z']+box['h']))
        nearest=math.hypot(dx,dz)
        if nearest<cylinder['r']:
            conflicts.append(dict(item_a=cylinder['id'],item_b=box['id'],
                issue=f'Cylinder/box reservations overlap with shared Y span; nearest side distance {nearest:.3f} mm < radius {cylinder["r"]:.3f} mm; not detailed part collision',
                overlap_x_mm='',overlap_y_mm='',overlap_z_mm='',status='Open - relocate or redefine package'))
for i,a in enumerate(cylinders):
    for b in cylinders[i+1:]:
        if not y_overlap(a['y'],a['w'],b['y']-b['w']/2,b['w']):
            continue
        distance=math.hypot(a['x']-b['x'],a['z']-b['z'])
        if distance<a['r']+b['r']:
            conflicts.append(dict(item_a=a['id'],item_b=b['id'],
                issue=f'Circular body/tire envelopes overlap with shared Y span; center distance {distance:.3f} mm < summed radii {a["r"]+b["r"]:.3f} mm; not detailed part collision',
                overlap_x_mm='',overlap_y_mm='',overlap_z_mm='',status='Open - relocate or redefine package'))
write_csv('registers/packaging-conflicts.csv',conflicts)
assert len(conflicts)==5
assert {(c['item_a'],c['item_b']) for c in conflicts}=={
    ('PKG01','PKG05'),('PKG01','Swingarm pivot'),
    ('PKG06','PKG05'),('PKG08','PKG04'),('PKG06','PKG07')}

# Simple OpenSCAD solids: no rendered body surfaces or manufacturing geometry.
scad=['// B0 packaging reservations, mm. NOT fabrication CAD. Generated by build-development-model.py.',
      '$fn=64;','module box(p,s,c){color(c,0.55) translate(p) cube(s);}',
      'module wheel(x,z,w,r){color([0.12,0.15,0.19]) translate([x,w/2,z]) rotate([90,0,0]) difference(){cylinder(h=w,r=r);translate([0,0,-1]) cylinder(h=w+2,r=r-35);}}',
      'wheel(0,311.9,160,311.9); wheel(1420,299.9,120,299.9);']
for b in boxes:
    rgb=[int(b['color'][i:i+2],16)/255 for i in (1,3,5)]
    scad.append(f'// {b["id"]}: {b["name"]}; {b["basis"]}')
    scad.append(f'box([{b["x"]},{b["y"]},{b["z"]}],[{b["l"]},{b["w"]},{b["h"]}],{rgb});')
scad += ['color("orange") translate([350,42.5,335]) rotate([90,0,0]) cylinder(h=85,d=208);',
         'color("red") translate([550,0,390]) sphere(r=25); // pivot center conflict',
         '// Add real CAD and swept motion before any fit claim.']
(ROOT/'models'/'package-reservations.scad').write_text('\n'.join(scad),encoding='utf-8')

# Coordinate-correct side projection, intentionally exposes unresolved volumes.
scale=.53; ox=210; ground=680
def sx(x):return ox+x*scale
def sy(z):return ground-z*scale
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="940" viewBox="0 0 1400 940">',
 '<rect width="1400" height="940" fill="#101923"/>',
 '<style>text{font-family:Arial,sans-serif;fill:#e8eef5} .small{font-size:16px} .label{font-size:19px;font-weight:bold}</style>',
 '<text x="50" y="52" font-size="32" font-weight="bold">BAVUSO / B0 PACKAGING STUDY</text>',
 '<text x="50" y="85" font-size="18" fill="#f4c66c">Dimensioned reservations, not a fitted motorcycle. Unresolved overlaps are shown.</text>',
 f'<line x1="35" y1="{ground}" x2="1330" y2="{ground}" stroke="#607587"/>']
for x,z,r in ((0,311.9,311.9),(1420,299.9,299.9)):
    svg.append(f'<circle cx="{sx(x)}" cy="{sy(z)}" r="{r*scale}" fill="none" stroke="#9aabb9" stroke-width="22"/>')
    svg.append(f'<circle cx="{sx(x)}" cy="{sy(z)}" r="4" fill="white"/>')
for b in boxes:
    svg.append(f'<rect x="{sx(b["x"])}" y="{sy(b["z"]+b["h"])}" width="{b["l"]*scale}" height="{b["h"]*scale}" fill="{b["color"]}" fill-opacity=".25" stroke="{b["color"]}" stroke-width="2"/>')
    svg.append(f'<text class="small" x="{sx(b["x"])+8}" y="{sy(b["z"]+b["h"])+24}">{b["id"]}</text>')
svg.append(f'<circle cx="{sx(350)}" cy="{sy(335)}" r="{104*scale}" fill="#e3c19d" fill-opacity=".35" stroke="#e3c19d"/>')
svg.append(f'<line x1="{sx(0)}" y1="{sy(311.9)}" x2="{sx(550)}" y2="{sy(390)}" stroke="#b8c6d6" stroke-width="6"/>')
svg.append(f'<circle cx="{sx(550)}" cy="{sy(390)}" r="12" fill="#ff6262"/>')
svg.append(f'<path d="M{sx(550)} {sy(390)} L{sx(700)} 430 L1150 430" fill="none" stroke="#ff6262"/>')
svg.append('<text x="1100" y="453" class="small" fill="#ff6262">Pivot inside pack box</text>')
svg.append(f'<line x1="{sx(0)}" y1="720" x2="{sx(1420)}" y2="720" stroke="#becfdd"/>')
svg.append(f'<text x="{sx(500)}" y="748" class="label">1420 mm wheelbase / study value</text>')
legend=[('PKG01','600 × 260 × 560 mm battery region'),('PKG02','Inverter plus installation reservation'),('PKG03','Charger plus installation reservation'),('PKG04','Unsized radiator/fan volume'),('PKG05','Shock/linkage movement reservation')]
for i,(key,desc) in enumerate(legend):
    yy=790+i*25
    svg.append(f'<text x="60" y="{yy}" class="small">{key} — {html.escape(desc)}</text>')
svg.append('<text x="790" y="805" class="small">Motor body: Ø208 × 85 mm reference</text>')
svg.append('<text x="790" y="835" class="small">No fork, rider, service or tire sweep clearance earned.</text>')
svg.append('<text x="790" y="865" class="small">Coordinates are inputs for engineering, not drawing dimensions.</text>')
svg.append('</svg>')
(ROOT/'visuals'/'package-side.svg').write_text('\n'.join(svg),encoding='utf-8')

# Plain data summary for programmatic review.
summary=dict(requirements=len(requirements),interfaces=len(interfaces),configuration_cases=len(trades),
    packaging_conflicts=len(conflicts),validation='Arithmetic and data consistency only; not physical verification',
    mass_gap_kg=196.35-400*LB,reference_mass_lb=196.35/LB,
    aero_led_focused=next(x for x in trades if x['parallel']==7 and x['basis'].startswith('Focused') and x['cda']==.30),
    aero_led_reference=next(x for x in trades if x['parallel']==7 and x['basis']=='Reference allocations' and x['cda']==.30),
    aero_led_stretch=next(x for x in trades if x['parallel']==7 and x['basis'].startswith('Aggressive') and x['cda']==.30))
(ROOT/'models'/'development-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
