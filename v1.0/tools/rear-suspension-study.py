"""Bavuso direct right-side shock kinematics and illustrative spring study.

Python standard library. Geometry proposal, not validated suspension selection.
Output: rear-suspension-kinematics.csv. All positions are relative to one fixed
chassis datum; reference zero is mechanically topped-out study geometry.
"""
from pathlib import Path
import csv
import math
import json

ROOT = Path(__file__).resolve().parents[1]
PX, PZ = 540.0, 470.0
AX0, AZ0 = 0.0, 311.9
LX0 = 300.0
LY = 150.0
LZ0 = PZ + (AZ0-PZ)*(PX-LX0)/(PX-AX0)
UX, UY = 400.0, 150.0
LENGTH0 = 297.0
UZ = LZ0 + math.sqrt(LENGTH0**2-(UX-LX0)**2)
ARM = math.hypot(AX0-PX, AZ0-PZ)
ALPHA0 = math.atan2(AZ0-PZ, AX0-PX)
WHEEL_TRAVEL = 130.0
CATALOG_SHOCK_STROKE = 54.0


def pose(travel):
    az = AZ0 + travel
    ax = PX-math.sqrt(ARM**2-(az-PZ)**2)
    alpha = math.atan2(az-PZ, ax-PX)
    angle = alpha-ALPHA0
    x, z = LX0-PX, LZ0-PZ
    lx = PX+x*math.cos(angle)-z*math.sin(angle)
    lz = PZ+x*math.sin(angle)+z*math.cos(angle)
    dx, dz = UX-lx, UZ-lz
    length = math.hypot(dx, dz)
    return dict(wheel_vertical_travel_mm=travel, rear_axle_x_mm=ax, rear_axle_y_mm=0,
                rear_axle_z_mm=az, lower_eye_x_mm=lx, lower_eye_y_mm=LY, lower_eye_z_mm=lz,
                upper_eye_x_mm=UX, upper_eye_y_mm=UY, upper_eye_z_mm=UZ,
                eye_distance_mm=length, shock_compression_mm=LENGTH0-length,
                swingarm_rotation_from_zero_deg=math.degrees(angle),
                shock_axis_lower_to_upper_x=dx/length, shock_axis_lower_to_upper_y=0,
                shock_axis_lower_to_upper_z=dz/length,
                shock_axis_angle_from_forward_x_deg=math.degrees(math.atan2(dz, dx)),
                mounting_pin_axis_x=0, mounting_pin_axis_y=1, mounting_pin_axis_z=0)


def ratio(travel):
    h=.001
    derivative=(pose(travel+h)['eye_distance_mm']-pose(travel-h)['eye_distance_mm'])/(2*h)
    return -1/derivative


def spring_wheel_force(travel, spring_n_mm, preload_mm):
    return spring_n_mm*(preload_mm+pose(travel)['shock_compression_mm'])/ratio(travel)


def equilibrium_sag(wheel_force, spring_n_mm, preload_mm):
    if spring_wheel_force(0,spring_n_mm,preload_mm)>=wheel_force:
        return 0.0
    if spring_wheel_force(WHEEL_TRAVEL,spring_n_mm,preload_mm)<wheel_force:
        return None
    lo,hi=0.,WHEEL_TRAVEL
    for _ in range(60):
        mid=(lo+hi)/2
        if spring_wheel_force(mid,spring_n_mm,preload_mm)<wheel_force:lo=mid
        else:hi=mid
    return (lo+hi)/2


rows=[]
for i in range(21):
    travel=WHEEL_TRAVEL*i/20
    row=pose(travel)
    row['instantaneous_wheel_vertical_to_shock_ratio']=ratio(travel)
    row['remaining_catalog_stroke_mm']=CATALOG_SHOCK_STROKE-row['shock_compression_mm']
    row['status']='PROPOSED kinematics; dimensions and spring/damper not supplier-approved'
    rows.append(row)
assert abs(rows[0]['eye_distance_mm']-297)<1e-9
assert abs(rows[-1]['shock_compression_mm']-49.45401553310171)<1e-8
assert all(a['eye_distance_mm']>b['eye_distance_mm'] for a,b in zip(rows,rows[1:]))
assert all(row['remaining_catalog_stroke_mm']>0 for row in rows)
assert all(abs(math.hypot(row['rear_axle_x_mm']-PX,row['rear_axle_z_mm']-PZ)-ARM)<1e-8 for row in rows)
assert all(abs(math.hypot(row['lower_eye_x_mm']-PX,row['lower_eye_z_mm']-PZ)-math.hypot(LX0-PX,LZ0-PZ))<1e-8 for row in rows)
with (ROOT/'rear-suspension-kinematics.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

# Example load, NOT a new mass or payload rating. No damper/gas/friction force.
g=9.80665
curb_mass=220.
loaded_mass=curb_mass+90.
rear_fraction=.55
curb_force=curb_mass*g*rear_fraction
loaded_force=loaded_mass*g*rear_fraction
springs=[]
for spring,preload in ((130,0),(130,10),(230,5),(250,5),(280,5)):
    springs.append(dict(spring_n_mm=spring,preload_mm=preload,
        approximate_zero_sag_local_wheel_rate_n_mm=spring/ratio(0)**2,
        curb_sag_mm=equilibrium_sag(curb_force,spring,preload),
        loaded_sag_mm=equilibrium_sag(loaded_force,spring,preload)))
summary=dict(status='Kinematic and illustrative static-spring calculations only',
    upper_eye_xyz_mm=[UX,UY,UZ],lower_eye_zero_xyz_mm=[LX0,LY,LZ0],
    swingarm_pivot_xyz_mm=[PX,0,PZ],arm_radius_mm=ARM,
    full_wheel_bump_mm=WHEEL_TRAVEL,shock_compression_at_full_bump_mm=rows[-1]['shock_compression_mm'],
    remaining_catalog_stroke_mm=rows[-1]['remaining_catalog_stroke_mm'],
    wheel_to_shock_ratio_zero=ratio(0),wheel_to_shock_ratio_full_bump=ratio(130),
    example_curb_mass_kg=curb_mass,example_loaded_mass_kg=loaded_mass,
    example_rear_fraction=rear_fraction,example_loaded_rear_force_n=loaded_force,
    spring_examples=springs,
    exclusions='No gas force/friction/damping, frame pitch/load transfer, tire compliance, tolerances, bumpstop or real spring stress/coilbind. No supplier approval.')
print(json.dumps(summary,indent=2))
