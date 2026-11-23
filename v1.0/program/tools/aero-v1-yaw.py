"""Yaw coefficients from the single yaw+10 case (the -10 case was not run: compute budget). Run after aero-v1-report.py.
Adds a 'yaw_plus10' block to program/data/aero/aero-results.json. Moments about the bike+rider CoG used in 15-dynamics.md."""
import json, math
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'data/aero/aero-results.json'
R = json.loads(p.read_text())
r = R['yaw+10']; t = r['parts']['total']; q = r['q_Pa']; beta = math.radians(10)
V77 = 77 * 0.44704; w = 10.0
slope = abs(t['side_force_N']) / q / beta
y = dict(case='yaw+10 on mesh m2 (1.68 M cells)', air_speed_ms=r['air_speed_ms'], q_Pa=q, side_force_N=t['side_force_N'],
         CyA_m2=round(t['side_force_N'] / q, 4), CyA_slope_per_rad_m2=round(slope, 3),
         yaw_moment_about_cog_Nm=t['yaw_moment_about_cog_Nm'], CnA_L_m3=round(t['yaw_moment_about_cog_Nm'] / q, 4),
         cp_ahead_of_rear_axle_m=t['cp_x_ahead_of_rear_axle_m'], cp_height_m=t['cp_height_m'],
         drag_along_wind_N=t['drag_air_N'], CdA_air_axis=t['CdA_m2'], drag_rise_vs_0deg_pct=round(100 * (t['drag_air_N'] / q / R['m2']['parts']['total']['CdA_m2'] - 1), 1),
         lift_N=t['lift_N'], front_axle_lift_N=t['front_axle_lift_N'], roll_moment_about_cog_Nm=t['roll_moment_about_cog_Nm'],
         gust_77mph_10ms_force_N=round(0.5 * 1.225 * (V77 ** 2 + w ** 2) * slope * math.atan(w / V77), 0),
         assumed_in_15_dynamics=dict(CyA_slope=1.6, cp_ahead_of_rear_axle_m=0.80, cp_height_m=0.95, force_N=349),
         note='only +10 deg run; minus 10 not run, symmetry assumed. Zero-yaw side force on m2 is +3.7 N (asymmetry floor).')
R['yaw_plus10'] = y
p.write_text(json.dumps(R, indent=1)); print(json.dumps(y, indent=1))
