"""Supplier-parts comparison: CAD (tools/build-adventure.py, read-only) vs real purchasable parts.

November 12, 2026, US Central. Prepared by Claude Opus 5.5 (claude-opus-5-5).

Reads the CAD generator as TEXT (regex), never imports or edits it. Pulls the running-gear and
bought-in dimensions, compares them with datasheet values for the selected real parts, and prints
every mismatch with its delta in mm. It also gives a FIRST-ORDER estimate of how the tyre and motor
changes move the clearance checks in geometry-adventure-audit.json (a subtraction, not a CAD rebuild).

Run from v1.0:  python detailed-design/tools/supplier-compare.py
Outputs: detailed-design/supplier/compare-output.csv, compare-clearance-impact.csv, compare-summary.json
"""
import csv, json, math, re, sys
from pathlib import Path

V10 = Path(__file__).resolve().parents[2]
SRC = (V10 / 'tools' / 'build-adventure.py').read_text(encoding='utf-8')
AUDIT = json.loads((V10 / 'geometry-adventure-audit.json').read_text(encoding='utf-8'))
OUT = V10 / 'detailed-design' / 'supplier'
OUT.mkdir(parents=True, exist_ok=True)


def grab(pattern, cast=float, group=1, flags=0):
    m = re.search(pattern, SRC, flags)
    if not m:
        raise SystemExit(f'pattern not found in build-adventure.py: {pattern}')
    return cast(m.group(group))


def line_with(token):
    for ln in SRC.splitlines():
        if token in ln:
            return ln
    raise SystemExit(f'line not found: {token}')


# ------------------------------------------------------------------ CAD values (parsed)
cad = {}
cad['RF'], cad['RR'] = (float(x) for x in re.search(r'^RF,RR=([\d.]+),([\d.]+)', SRC, re.M).groups())
cad['LIFT'] = grab(r'^LIFT=([\d.]+)', flags=re.M)
cad['FRONT_TRAVEL'], cad['REAR_TRAVEL'] = (float(x) for x in re.search(r'^FRONT_TRAVEL,REAR_TRAVEL=(\d+),(\d+)', SRC, re.M).groups())
cad['RAKE_deg'] = grab(r'RAKE=math\.radians\(([\d.]+)\)')
cad['FORK_OFF'] = grab(r'FORK_OFF=([\d.]+)')
sa0 = re.search(r'^SA0=\(([\d.]+),([\d.]+)\)', SRC, re.M).groups()
cad['SA0_x'], cad['SA0_z'] = float(sa0[0]), float(sa0[1])
m = re.search(r"wheel\('Rear',0,RZ,(\d+),RR,False,(\d+)\)", SRC); cad['rear_width'], cad['rear_rim_in'] = float(m[1]), float(m[2])
m = re.search(r"wheel\('Front',FX,FZ,(\d+),RF,True,(\d+)\)", SRC); cad['front_width'], cad['front_rim_in'] = float(m[1]), float(m[2])
m = re.search(r'ws=([\d.]+) if front else ([\d.]+)', SRC); cad['front_rim_w_in'], cad['rear_rim_w_in'] = float(m[1]) / 25.4, float(m[2]) / 25.4
m = re.search(r'discR=(\d+) if front else (\d+)', SRC); cad['front_disc_R'], cad['rear_disc_R'] = float(m[1]), float(m[2])
cad['disc_band'] = grab(r'disc=cyl\(\(x,yd,z\),\(x,yd\+side\*5,z\),discR,discR-(\d+)\)')
cad['disc_thk'] = grab(r'disc=cyl\(\(x,yd,z\),\(x,yd\+side\*(\d+),z\)')
cad['hub_boss_r'] = grab(r'fl_=cyl\(\(x,yf-3,z\),\(x,yf\+3,z\),(\d+),')
m = re.search(r'hubw=(\d+) if front else (\d+)', SRC); cad['front_hubw'], cad['rear_hubw'] = float(m[1]), float(m[2])
cad['fork_leg_y'] = grab(r'yo=side\*(\d+)')
ln = line_with("'Fork_inner_tube'"); cad['fork_inner_r'] = float(re.search(r',(\d+)\)\),\'RunningGear\'', ln)[1])
ln = line_with("'Fork_outer_tube'"); m = re.search(r'cyl\(\(off,yo,(-?\d+)\),\(off,yo,(\d+)\),(\d+)\)', ln)
cad['fork_outer_bot'], cad['fork_outer_top'], cad['fork_outer_r'] = float(m[1]), float(m[2]), float(m[3])
cad['fork_foot_r'] = grab(r'foot=cyl\(\(off,yo,w_axle-31\.5\),\(off,yo,w_axle\+158\.5\),([\d.]+)\)')
cad['caliper_lug_half_deg'] = grab(r'for a in \(180-([\d.]+),180\+')
cad['caliper_lug_r'] = cad['front_disc_R'] + grab(r'FX\+\(160\+(\d+)\)\*math\.cos')
cad['lower_clamp_w0'] = grab(r"steer\(clamp\((-?\d+),\d+\)\),'RunningGear','Lower")
cad['steer_keep_r'] = grab(r"Part\.makeCylinder\((\d+),\(steer_hi-steer_lo\)")
cad['SHOCK_STROKE'] = grab(r'^SHOCK_STROKE=([\d.]+)', flags=re.M)
cad['SHOCK_EYE_EXT'] = grab(r'^SHOCK_EYE_EXT=([\d.]+)', flags=re.M)
cad['shock_body_r'] = grab(r"axis\*\(12\+body_len\)\),(\d+)\),'Chassis'")
cad['spring_helix_r'] = grab(r'makeHelix\(spring_len/7\.5,spring_len,(\d+)\)')
cad['spring_wire_r'] = grab(r'Part\.makeCircle\((\d+),V\(38,0,0\)')
cad['bar_centre_r'] = grab(r"'Bar_centre',cyl\(\(BAR_C\[0\],-40,BAR_C\[1\]\),\(BAR_C\[0\],40,BAR_C\[1\]\),([\d.]+)\)")
cad['bar_end_r'] = grab(r'14\.3 if i==0 else ([\d.]+)')
cad['grip_r'] = grab(r"'Hand_grip_reserve',side\),cyl\(tuple\(bp\[2\]-gd\*5\),tuple\(bp\[2\]\+gd\*125\),(\d+)\)")
m = re.search(r"'Mirror_glass',side\),box\(825\.6,\(280 if side>0 else -420\)\+13,1204,([\d.]+),(\d+),(\d+)\)", SRC)
cad['mirror_w'], cad['mirror_h'] = float(m[2]), float(m[3])
m = re.search(r'headlamp=nose_solid\.common\(box\(1392,-200,816,(\d+),(\d+),(\d+)\)\)', SRC)
cad['headlamp_depth'], cad['headlamp_w'], cad['headlamp_h'] = float(m[1]), float(m[2]), float(m[3])
m = re.search(r"Front_indicator_reserve',side\)\]=box\(1385,side\*118-14,794,(\d+),(\d+),(\d+)\)", SRC)
cad['front_ind'] = tuple(float(x) for x in m.groups())
m = re.search(r'IPM_C,IPM_R=([\d.]+),([\d.]+)', SRC); cad['IPM_R'] = float(m[2])
m = re.search(r'IPM_Y0,IPM_Y1,GC_Y0=(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)', SRC); cad['IPM_len'] = float(m[2]) - float(m[1])
m = re.search(r'CELL_R,CELL_L,CELL_WH,CELL_G=([\d.]+),([\d.]+),([\d.]+),([\d.]+)', SRC)
cad['CELL_R'], cad['CELL_L'], cad['CELL_WH'], cad['CELL_G'] = (float(x) for x in m.groups())
m = re.search(r'SERIES,PAR=(\d+),(\d+)', SRC); cad['SERIES'], cad['PAR'] = int(m[1]), int(m[2])
cad['PITCH'] = grab(r'^PITCH=([\d.]+)', flags=re.M)
m = re.search(r'pul=cyl\(\(x,(-?\d+),z\),\(x,(-?\d+),z\)', SRC); cad['belt_y_out'], cad['belt_y_in'] = float(m[1]), float(m[2])
cad['arm_ya'] = grab(r'ya=(\d+)\+\(8 if side<0 else 0\)'); cad['arm_left_extra'] = 8.0
m = re.search(r'ratio=[\d.]+;pitch=([\d.]+);fr=(\d+)\*pitch/\(2\*math\.pi\);rr=(\d+)\*pitch', SRC)
belt_pitch, z_f, z_r = float(m[1]), int(m[2]), int(m[3])
cad['PZ'] = 350.0  # default BAVUSO_PIVOT_Z in the generator
m = re.search(r'rearHugger=cyl\(\(0,-(\d+),RZ\),\(0,\d+,RZ\),(\d+),(\d+)\)', SRC)
cad['hugger_half'], cad['hugger_ro'], cad['hugger_ri'] = float(m[1]), float(m[2]), float(m[3])
cad['fender_half'] = grab(r'frontFender=cyl\(\(FX,-(\d+),FZ\)')

# Derived CAD geometry (same formulas as the generator)
rake = math.radians(cad['RAKE_deg'])
FZ = cad['RF'] - cad['LIFT']
W_AXLE = (FZ - cad['SA0_z'] - math.sin(rake) * cad['FORK_OFF']) / math.cos(rake)
cad['axle_below_SA0_along_axis'] = -W_AXLE
cad['fork_axle_to_outer_top'] = cad['fork_outer_top'] - W_AXLE
cad['fork_axle_to_lower_clamp'] = cad['lower_clamp_w0'] - W_AXLE
cad['trail'] = (cad['RF'] * math.sin(rake) - cad['FORK_OFF']) / math.cos(rake)
cad['caliper_lug_spacing'] = 2 * cad['caliper_lug_r'] * math.sin(math.radians(cad['caliper_lug_half_deg']))
cad['spring_od'] = 2 * (cad['spring_helix_r'] + cad['spring_wire_r'])
cad['spring_id'] = 2 * (cad['spring_helix_r'] - cad['spring_wire_r'])
cad['pack_kwh'] = cad['SERIES'] * cad['PAR'] * cad['CELL_WH'] / 1000
cad['cells_kg'] = cad['SERIES'] * cad['PAR'] * cad['CELL_G'] / 1000
# Crown (tread profile) radius of the CAD section: circle through the crown points (r, y) used by wheel()
def crown_radius(R, width, rim_in):
    bead = rim_in * 25.4 / 2; h = R - bead
    pts = [(bead + .86 * h, width * .40), (bead + .96 * h, width * .24), (R, 0.0)]
    (x1, y1), (x2, y2), (x3, y3) = pts
    # circle centred on y=0 through (R,0) and (x1,y1): centre at r=c, radius R-c
    c = (x1 ** 2 + y1 ** 2 - R ** 2) / (2 * (x1 - R))
    return R - c
cad['front_crown_R'] = crown_radius(cad['RF'], cad['front_width'], cad['front_rim_in'])
cad['rear_crown_R'] = crown_radius(cad['RR'], cad['rear_width'], cad['rear_rim_in'])

# ------------------------------------------------------------------ real parts (datasheet values + URLs)
METZ = 'https://intramoto.gr/wp-content/uploads/2024/04/METZELER-DATA.pdf'   # Metzeler 2024 Technical Databook, "Technical data to standard"
real = dict(
    front_tyre=dict(part='Metzeler Tourance Next 2 120/70 R19 M/C 60V TL (IP 3960400)', dia=663, width=133, rim_meas=3.50, rim_range=(3.00, 3.75),
                    circ=1966, src=METZ),
    rear_tyre=dict(part='Metzeler Tourance Next 2 170/60 R17 M/C 72V TL (IP 3960500)', dia=650, width=190, rim_meas=4.50, rim_range=(4.50, 5.50),
                   circ=1921, src=METZ),
    rear_tyre_160=dict(part='Metzeler Sportec M5 160/60 ZR17 (69W) (IP 1971300), size reference only', dia=638, width=178, src=METZ),
    front_tyre_21=dict(part='Metzeler Karoo 4 90/90-21 54T (IP 4148600), 21-in reference', dia=707, width=103, src=METZ),
    wheels=dict(part='Ducati Performance spoked tubeless 3.00x19 / 4.50x17 (96380141BD), Multistrada V4', front_w=3.00, rear_w=4.50,
                src='https://www.omniaracing.net/en/ducati-performance-spoked-rims-300x19-and-450x17-for-ducati-multistrada-2021-p-271103.html'),
    fork_ref=dict(part='Ohlins FGRT 301 (48 mm USD, R&T)', inner=48, length=765, stroke=120, price_eur=3974.55,
                  src='https://www.ohlins.eu/en/products/motorcycle/fgrt-301--4199/'),
    fork_oe=dict(part='Marzocchi 50 mm USD (Ducati Multistrada V4 S OE), 170 mm travel', inner=50, travel=170,
                 src='https://amcn.com.au/editorial/test-ducati-multistrada-v4-s/'),
    caliper=dict(part='Brembo Stylema 4x30 mm monobloc, 100 mm radial (220D02010 kit)', mount=100, band=(32, 34),
                 src='https://hhrperformance.com/products/brembo-caliper-left-p4-30mm-stylema-cast-monobloc-100mm-radial-mount-front-titanium-grey'),
    front_disc=dict(part='Brembo Serie Oro 78B40870 floating 320 x 5.0 mm', dia=320, thk=5.0,
                    src='https://www.oppracing.com/product_display/14428604-brembo-serie-oro-disc-320x50mm-serie-oro-floating-front-78b40870/'),
    rear_disc=dict(part='Brembo Serie Oro 68B407H1 fixed 245 x 5 mm, 4 holes, ID 83', dia=245, thk=5.0,
                   src='https://www.carpimoto.com/en-US/42247_68B407H1-Brembo-Serie-Oro-Brake-Rotor-68B407H1.htm'),
    rear_caliper=dict(part='Brembo P34 2x34 mm, 84 mm mount', mount=84,
                      src='https://www.carpimoto.com/en-US/23744_20B85257-Brembo-Rear-Brake-Caliper-P2-34.htm'),
    master=dict(part='Brembo 19RCS Corsa Corta 110C74010', bore=19,
                src='https://www.motosport.com/brembo-corsa-corta-19rcs-brake-master-cylinder'),
    shock_ref=dict(part='Ohlins STX 46 Adventure KT 122 (KTM 690 PDS, direct mount)', length=406, stroke=100.5,
                   src='https://www.ohlins.eu/en/products/motorcycle/kt-122--4458/'),
    shock_ref2=dict(part='Ohlins TTX GP HO 469', length=295, stroke=60, src='https://www.ohlins.eu/en/products/motorcycle/ho-469--6323/'),
    spring=dict(part='Ohlins 21040-xx shock spring 51 ID x 160', id=51, src='https://www.alpharacing.com/en/oehlins-spring-51-160-95-n-mm/su-21040-31'),
    bar=dict(part='Renthal Fatbar 826 (28.6 clamp, 22.2 ends)', clamp=28.6, ends=22.2, width=805, src='https://renthal.com/products/fatbar-826-01'),
    mirror_rule=dict(fmvss_flat_mm2=8065, fmvss_convex_mm2=6450, ece_circle=78, ece_area_mm2=6900,
                     src='https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/subpart-B/section-571.111 ; https://far-ecommerce.com/en/pages/guida-specchietti-moto-omologati'),
    headlamp=dict(part='Hella Bi-LED L4565 90 mm module (ECE)', lens=94.4, depth_min=124, depth_max=161.7,
                  src='https://www.hella.com/australiansolutions/assets/documents_global/Hella-90mm-Module-Brochure-0224.pdf'),
    indicator=dict(part='Kellermann Atto DF Integral (rear, E-mark)', dims=(22, 12, 6), src='https://www.kellermann-online.com/en/atto-df-integral/156.500'),
    motor=dict(part='Helix SPX177-45 radial PM', od=200, length=163, mass=13, t_peak=120, p_peak=150, rpm=23500, t_cont=74, p_cont=90,
               src='https://www.ehelix.com/products/spx177/'),
    inverter=dict(part='Cascadia Motion CM200DX', v=(200, 480), i_cont=300, i_peak=740, mass=6.75, src='https://www.cascadiamotion.com/cm-200'),
    cell=dict(part='Molicel INR-21700-P60B', d=21.55, l=70.15, wh=21.6, ah=6.0, g=75, i_std=60, wh_kg=280,
              src='https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P60B_80145.pdf'),
    cell_alt=dict(part='Molicel INR-21700-P50B', d=21.55, l=70.15, wh=18.0, g=70, i_cont=50,
                  src='https://files.batteryjunction.com/frontend/files/molicel/DataSheets/MOLICEL-P50B-Datasheet.pdf'),
)

rows = []
def row(item, cad_v, real_v, part, src, note='', tol=0.5):
    d = None if (cad_v is None or real_v is None) else real_v - cad_v
    status = 'match' if d is not None and abs(d) <= tol else ('MISMATCH' if d is not None else 'info')
    rows.append(dict(item=item, cad=None if cad_v is None else round(cad_v, 2), real=None if real_v is None else round(real_v, 2),
                     delta_mm=None if d is None else round(d, 2), status=status, real_part=part, source=src, note=note))

ft, rt = real['front_tyre'], real['rear_tyre']
row('Front tyre outside diameter (mm)', 2 * cad['RF'], ft['dia'], ft['part'], ft['src'], 'max diameter in service per databook; CAD = nominal ETRTO 120/70-19')
row('Front tyre radius (mm)', cad['RF'], ft['dia'] / 2, ft['part'], ft['src'])
row('Front tyre section width (mm)', cad['front_width'], ft['width'], ft['part'], ft['src'], 'max width in service on 3.50 measuring rim')
row('Front rim width (in)', cad['front_rim_w_in'], ft['rim_meas'], ft['part'], ft['src'], f"3.00 is inside the permitted {ft['rim_range']} range", tol=0.01)
row('Rear tyre outside diameter (mm)', 2 * cad['RR'], rt['dia'], rt['part'], rt['src'], 'CAD models 160/60; brief and benchmark bikes use 170/60')
row('Rear tyre radius (mm)', cad['RR'], rt['dia'] / 2, rt['part'], rt['src'])
row('Rear tyre section width (mm)', cad['rear_width'], rt['width'], rt['part'], rt['src'], 'max width in service on 4.50 measuring rim')
row('Rear tyre 160/60 alt: diameter (mm)', 2 * cad['RR'], real['rear_tyre_160']['dia'], real['rear_tyre_160']['part'], METZ)
row('Rear rim width (in)', cad['rear_rim_w_in'], rt['rim_meas'], rt['part'], rt['src'], tol=0.01)
row('Front tyre crown radius (mm, CAD estimate)', cad['front_crown_R'], None, 'not published by Metzeler/Michelin/Pirelli', '', 'measure a sample')
row('Rear tyre crown radius (mm, CAD estimate)', cad['rear_crown_R'], None, 'not published', '', 'measure a sample')
row('Fork inner tube diameter (mm)', 2 * cad['fork_inner_r'], 48, 'WP APEX 48 / Ohlins FGRT 48 class', real['fork_ref']['src'], 'Marzocchi OE on Multistrada V4 is 50 mm')
row('Fork travel (mm)', cad['FRONT_TRAVEL'], real['fork_oe']['travel'], real['fork_oe']['part'], real['fork_oe']['src'])
est_len = real['fork_ref']['length'] + (cad['FRONT_TRAVEL'] - real['fork_ref']['stroke'])
row('Fork axle to top of outer tube (mm)', cad['fork_axle_to_outer_top'], est_len, 'FGRT 301 765 mm @120 stroke, +50 mm for 170 (interpolated, not a datasheet)', real['fork_ref']['src'], 'ESTIMATE')
row('Front tyre to fork foot, lateral (mm)', cad['fork_leg_y'] - cad['fork_foot_r'] - cad['front_width'] / 2,
    cad['fork_leg_y'] - cad['fork_foot_r'] - ft['width'] / 2, 'with real 133 mm width', ft['src'], 'no CAD check covers this; want >=10')
row('Front caliper radial mount spacing (mm)', cad['caliper_lug_spacing'], real['caliper']['mount'], real['caliper']['part'], real['caliper']['src'], 'CAD comment says 108')
row('Front disc diameter (mm)', 2 * cad['front_disc_R'], real['front_disc']['dia'], real['front_disc']['part'], real['front_disc']['src'])
row('Front disc thickness (mm)', cad['disc_thk'], real['front_disc']['thk'], real['front_disc']['part'], real['front_disc']['src'])
row('Front disc band height (mm)', cad['disc_band'], real['caliper']['band'][1], real['caliper']['part'], real['caliper']['src'], 'Stylema pad suits 32-34 mm band')
row('Rear disc diameter (mm)', 2 * cad['rear_disc_R'], real['rear_disc']['dia'], real['rear_disc']['part'], real['rear_disc']['src'])
row('Master cylinder bore (mm)', 19, real['master']['bore'], real['master']['part'], real['master']['src'], 'CAD text: 19 mm class')
row('Shock eye-to-eye extended (mm)', cad['SHOCK_EYE_EXT'], None, 'custom OE length; nearest catalogue: TTX GP 295/60, STX46 406/100.5', real['shock_ref']['src'])
row('Shock stroke / length ratio', cad['SHOCK_STROKE'] / cad['SHOCK_EYE_EXT'], real['shock_ref']['stroke'] / real['shock_ref']['length'],
    real['shock_ref']['part'], real['shock_ref']['src'], 'plausibility only', tol=0.02)
row('Shock spring ID (mm)', cad['spring_id'], real['spring']['id'], real['spring']['part'], real['spring']['src'], 'CAD reservation (88 OD) is conservative')
row('Bar clamp diameter (mm)', 2 * cad['bar_centre_r'], real['bar']['clamp'], real['bar']['part'], real['bar']['src'], tol=0.1)
row('Bar end diameter (mm)', 2 * cad['bar_end_r'], real['bar']['ends'], real['bar']['part'], real['bar']['src'], tol=0.1)
mr = real['mirror_rule']
row('Mirror glass area (mm2)', cad['mirror_w'] * cad['mirror_h'], mr['fmvss_flat_mm2'], 'FMVSS 111 S10.1 flat mirror minimum', mr['src'], 'convex option needs 6450 mm2', tol=0)
row('Mirror glass height vs 78 mm circle (mm)', cad['mirror_h'], mr['ece_circle'], 'ECE R81 L-category', mr['src'], tol=0)
hl = real['headlamp']
row('Headlamp opening height (mm)', cad['headlamp_h'], hl['lens'], hl['part'], hl['src'], 'off-the-shelf certified module needs ~95 mm', tol=0)
row('Headlamp depth (mm)', cad['headlamp_depth'], hl['depth_min'], hl['part'], hl['src'], 'module depth 124-162 mm', tol=0)
mo = real['motor']
row('Motor OD (mm)', 2 * cad['IPM_R'], mo['od'], mo['part'], mo['src'])
row('Motor overall length (mm)', cad['IPM_len'], mo['length'], mo['part'], mo['src'], 'no room: right arm sweep is 12 mm from the motor end')
row('Motor peak torque (Nm)', 150, mo['t_peak'], mo['part'], mo['src'], 'ratio 7.8 -> 9.8 keeps wheel torque; 23.5k rpm covers it')
ce = real['cell']
row('Cell diameter (mm)', 2 * cad['CELL_R'], ce['d'], ce['part'], ce['src'])
row('Cell length (mm)', cad['CELL_L'], ce['l'], ce['part'], ce['src'])
row('Cell energy (Wh)', cad['CELL_WH'], ce['wh'], ce['part'], ce['src'])
row('Cell mass (g)', cad['CELL_G'], ce['g'], ce['part'], ce['src'])

# ------------------------------------------------------------------ belt vs rear tyre (no CAD check exists)
fr = z_f * belt_pitch / (2 * math.pi) + 5; rrb = z_r * belt_pitch / (2 * math.pi) + 5
RZ = cad['RR'] - cad['LIFT']; c = math.hypot(540, cad['PZ'] - RZ)
# outer tangents: distance from the rear axle along each straight run ranges from the rear tangent point to the front one
run_len = math.sqrt(c ** 2 - (rrb - fr) ** 2)
r_far = math.hypot(run_len, rrb)        # distance from rear axle at the front tangent point
belt_inner = abs(cad['belt_y_in'])
belt = dict(belt_runs_radius_from_rear_axle=[round(rrb, 1), round(r_far, 1)], tyre_zone=[round(cad['rear_rim_in'] * 25.4 / 2, 1), round(rt['dia'] / 2, 1)],
            belt_inner_face_y=belt_inner, cad_tyre_half_width=cad['rear_width'] / 2, real_tyre_half_width=rt['width'] / 2,
            gap_cad=belt_inner - cad['rear_width'] / 2, gap_real=belt_inner - rt['width'] / 2,
            gap_real_160=belt_inner - real['rear_tyre_160']['width'] / 2)
row('Belt inner face to rear tyre sidewall (mm)', belt['gap_cad'], belt['gap_real'], rt['part'], rt['src'], 'BLOCKING: negative = overlap; want >=10')

# ------------------------------------------------------------------ first-order clearance impact
dRf = ft['dia'] / 2 - cad['RF']; dRr = rt['dia'] / 2 - cad['RR']; dWf = (ft['width'] - cad['front_width']) / 2; dWr = (rt['width'] - cad['rear_width']) / 2
dRm = mo['od'] / 2 - cad['IPM_R']
gap = {c_['check']: c_ for c_ in AUDIT['critical_pair_checks']}
# basis: P = rebuilt from RF/RR/x_cover etc. (self-adjusting); F = fixed geometry, loses the radius growth (CR-1/CR-2 raise the sprung mass so only radius growth counts)
impact_map = [
    ('pack_vs_motor_supplier', -dRm, 'F', 'motor OD 220->200'),
    ('pack_vs_front_bump', 0, 'P', 'pack bands follow x_cover(RF)'),
    ('lower_body_vs_front_bump', 0, 'P', 'cover front wall follows x_cover(RF)'),
    ('frame_vs_front_bump', -dRf, 'F', 'head tube/rails fixed; downlink lug follows the pack'),
    ('lower_clamp_vs_front_bump', -dRf, 'F', 'needs CR-1 fork +4 mm'),
    ('front_body_vs_tyre_fender_lock_sweep', -max(dRf, dWf), 'F', 'steered sweep, radius and width both grow'),
    ('frame_vs_tyre_fender_lock_sweep', -max(dRf, dWf), 'F', ''),
    ('upper_body_vs_front_bump', -dRf, 'F', ''),
    ('charger_vs_front_bump', -dRf, 'F', ''),
    ('frame_vs_rear_bump', -dRr, 'F', 'tail rail end'),
    ('seat_vs_rear_bump', -dRr, 'F', ''),
    ('tail_vs_rear_bump', -dRr, 'F', ''),
    ('undertray_vs_rear_bump', 0, 'P', 'undertray built from RR+dr'),
    ('rear_indicators_vs_rear_bump', -dRr, 'F', ''),
    ('plate_vs_rear_bump', -dRr, 'F', ''),
    ('plate_arm_vs_rear_bump', -dRr, 'F', ''),
    ('cross_brace_vs_rear_bump', -dRr, 'F', ''),
    ('motor_cover_vs_rear_bump', -dRr, 'F', ''),
    ('shock_vs_rear_tyre_same_position', -dRr, 'F', ''),
    ('shock_tower_vs_rear_tyre', -dRr, 'F', 'tower plates sit ahead of the tyre'),
    ('motor_vs_rear_bump', -dRr, 'F', ''),
]
impact = []
for name, delta, basis, note in impact_map:
    g0 = gap[name]['gap_mm']; req = gap[name]['required_mm']; g1 = g0 + delta
    impact.append(dict(check=name, gap_now=g0, delta=round(delta, 1), gap_est=round(g1, 1), required=req,
                       verdict='pass' if g1 >= req else 'FAIL', basis=basis, note=note))
# lower clamp after CR-1 (fork 4 mm longer)
lc = next(i for i in impact if i['check'] == 'lower_clamp_vs_front_bump'); lc_after = lc['gap_est'] + 4.0

# Pack with P60B: 100s15p, 5 lanes
S, Pp, lanes = 100, 15, 5
pitch_new = ce['d'] + 2.0
area_old = cad['PITCH'] ** 2 * math.sqrt(3) / 2; area_new = pitch_new ** 2 * math.sqrt(3) / 2
per_lane_old = cad['SERIES'] * cad['PAR'] / 3; per_lane_new = S * Pp / lanes
lane_span = lanes * ce['l'] + (lanes - 1) * 6.0
pack = dict(layout=f'{S}s{Pp}p', cells=S * Pp, kwh=round(S * Pp * ce['wh'] / 1000, 2), full_v=round(S * 4.2), cells_kg=round(S * Pp * ce['g'] / 1000, 1),
            pack_kg_est=round(S * Pp * ce['g'] / 1000 / 0.80, 1), cad_kwh=round(cad['pack_kwh'], 2), cad_cells_kg=round(cad['cells_kg'], 1),
            cad_pack_kg=round(cad['cells_kg'] / 0.8, 1), peak_A_per_cell_130kW_360V=round(130000 / 360 / Pp, 1), pitch=pitch_new,
            lanes=[round((i - (lanes - 1) / 2) * (ce['l'] + 6.0), 1) for i in range(lanes)], lane_span=lane_span,
            cad_lane_span=3 * cad['CELL_L'] + 2 * 8, side_area_ratio=round(per_lane_new * area_new / (per_lane_old * area_old), 3),
            cell_cost_usd=[round(S * Pp * 3.35), round(S * Pp * 7.50)])

# ------------------------------------------------------------------ output
with open(OUT / 'compare-output.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open(OUT / 'compare-clearance-impact.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(impact[0])); w.writeheader(); w.writerows(impact)
summary = dict(generated='2026-11-12 US Central, Claude Opus 5.5', cad_parsed={k: (round(v, 2) if isinstance(v, float) else v) for k, v in cad.items()},
               deltas=dict(front_radius=round(dRf, 2), rear_radius=round(dRr, 2), front_half_width=dWf, rear_half_width=dWr, motor_radius=dRm),
               trail_new_R_rake25=round((ft['dia'] / 2 * math.sin(rake) - cad['FORK_OFF']) / math.cos(rake), 1),
               lower_clamp_after_CR1=round(lc_after, 1), belt=belt, pack=pack,
               fork_foot_gap_at_leg_y105=round(105 - cad['fork_foot_r'] - ft['width'] / 2, 1))
(OUT / 'compare-summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')

print('CAD vs real parts (delta = real - CAD)')
print(f"{'item':48s} {'CAD':>9s} {'real':>9s} {'delta':>8s}  status")
for r in rows:
    f_ = lambda v: '' if v is None else f'{v:9.2f}'
    d_ = '' if r['delta_mm'] is None else f"{r['delta_mm']:8.2f}"
    print(f"{r['item'][:48]:48s} {f_(r['cad'])} {f_(r['real'])} {d_:>8s}  {r['status']}")
print('\nFirst-order clearance impact (sprung mass raised per CR-1/CR-2, so only tyre growth counts)')
for i in impact:
    print(f"  {i['check']:40s} {i['gap_now']:7.1f} -> {i['gap_est']:7.1f} (req {i['required']}) {i['verdict']:4s} [{i['basis']}] {i['note']}")
print(f"\nLower clamp after CR-1 (+4 mm fork): {lc_after:.1f} mm vs 25")
print('Belt:', json.dumps(belt))
print('Pack:', json.dumps(pack))
print('Trail with 663 mm front at 25 deg:', summary['trail_new_R_rake25'])
