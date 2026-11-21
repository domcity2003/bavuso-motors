#!/usr/bin/env python
"""Bavuso V1 electrical: pack, protection, precharge, charge-time and motor-matching calculations.
Run from v1.0 with the FreeCAD python:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/elec-pack.py
Writes program/data/elec-pack.json and program/data/elec-power-table.csv.
Every input is labelled datasheet / supplier / calculated / estimate in the INPUTS dict.
"""
import json, math, csv, os
import numpy as np

OUT = os.path.join("program", "data")

# ------------------------------------------------------------------ inputs
S, P = 100, 11
INPUTS = {
    "cell_Ah_typ": (6.0, "datasheet Molicel INR-21700-P60B (6000 mAh typ, 5850 min)"),
    "cell_Wh_typ": (21.6, "datasheet"),
    "cell_V_nom": (3.6, "datasheet (Gate A rounds the pack to 370 V = 3.7 V/cell)"),
    "cell_V_max": (4.2, "datasheet"),
    "cell_V_min": (2.5, "datasheet charge/discharge cut-off 2.5 V (cycle test window); table says 1.8 V absolute"),
    "cell_mass_kg": (0.075, "datasheet, 75 g max"),
    "cell_I_chg_std_A": (6.0, "datasheet standard charge 6.0 A"),
    "cell_I_chg_max_A": (30.0, "datasheet maximum charge 30 A (70 C cut-off); 5C"),
    "cell_I_dis_std_A": (60.0, "datasheet"),
    "cell_I_dis_max_A": (100.0, "datasheet"),
    "cell_R_dc_mohm": (12.8, "datasheet DC impedance at 50% SOC"),
    "cell_R_ac_mohm": (6.5, "datasheet AC impedance at 30% SOC"),
    "R_interconnect_mohm": (6.0, "estimate: busbars + wire bonds for 100 series links (prior design: 5.2 mohm for 99 links)"),
    "R_external_mohm": (2.5, "estimate: MSD fuse 0.4 + pyro 0.1 + 2 contactors 0.8 + shunt 0.1 + 2 m of 50 mm2 0.75 + lugs"),
    "gx14_carry_A": (350.0, "supplier Gigavac GX14 datasheet: 350+ A, 12-800 V, 0.5 kg"),
    "main_fuse_A": (400.0, "design choice: EV fuse 400 A / >=500 VDC in the service plug (rating to confirm on real fuse curve)"),
    "pyro_break_kA": (22.0, "supplier Sensata STP500P class (prior study); 500 A, 22 kA break at 500 V"),
    "dc_link_uF": (715.0, "prior study: 650 uF CM200 + 65 uF estimates for charger, DC-DC, Y-caps"),
    "precharge_ohm": (220.0, "design choice (prior study sweep)"),
    "eta_drive": (0.93, "estimate: motor 96% x inverter 97%"),
}
g = lambda k: INPUTS[k][0]

# OCV vs SOC for a high-power NMC 21700 (ESTIMATE, typical shape; not from the datasheet)
SOC = np.array([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100.0])
OCV = np.array([3.00, 3.30, 3.40, 3.52, 3.60, 3.66, 3.73, 3.81, 3.90, 3.99, 4.09, 4.20])
ocv = lambda soc: float(np.interp(soc, SOC, OCV))

R_cell_pack = g("cell_R_dc_mohm") * S / P / 1e3            # ohm
R_pack = R_cell_pack + (g("R_interconnect_mohm") + g("R_external_mohm")) / 1e3
R_pack_ac = g("cell_R_ac_mohm") * S / P / 1e3 + (g("R_interconnect_mohm") + g("R_external_mohm")) / 1e3

res = {"inputs": {k: {"value": v[0], "basis": v[1]} for k, v in INPUTS.items()}}

# ------------------------------------------------------------------ pack totals
n_cells = S * P
E_kWh = n_cells * g("cell_Wh_typ") / 1000
res["pack"] = {
    "series": S, "parallel": P, "cells": n_cells,
    "capacity_Ah": P * g("cell_Ah_typ"),
    "energy_kWh_gross": round(E_kWh, 2),
    "V_nominal_datasheet_3p6": S * 3.6, "V_nominal_gateA_3p7": S * 3.7,
    "V_max": S * g("cell_V_max"), "V_min_2p5": S * g("cell_V_min"),
    "cell_mass_kg": round(n_cells * g("cell_mass_kg"), 2),
    "R_pack_dc_mohm": round(R_pack * 1e3, 1), "R_pack_ac_mohm": round(R_pack_ac * 1e3, 1),
    "R_cells_only_mohm": round(R_cell_pack * 1e3, 1),
}
# Modules: ELV (<60 V DC) so they can be handled bare during assembly
mod_series = 10
res["modules"] = {
    "modules": S // mod_series, "per_module": f"{mod_series}s{P}p", "cells_per_module": mod_series * P,
    "V_nom": mod_series * 3.6, "V_max": mod_series * 4.2, "ELV_limit_V": 60,
    "energy_kWh": round(mod_series * P * g("cell_Wh_typ") / 1000, 2),
    "note": "10 series modules; module-to-module links are the only bolted high-current joints",
}

# ------------------------------------------------------------------ power <-> current
def solve_I(P_dc_W, soc, R=R_pack, regen=False):
    """Pack current for a given DC power at the pack terminals (discharge positive)."""
    Voc = S * ocv(soc)
    # P = (Voc - I R) I   ->  R I^2 - Voc I + P = 0
    disc = Voc**2 - 4 * R * P_dc_W
    if disc < 0:
        return float("nan"), float("nan")
    I = (Voc - math.sqrt(disc)) / (2 * R)
    return I, Voc - I * R

rows = []
for shaft_kW in (55, 90, 100, 110):
    for soc in (100, 80, 50, 20, 10):
        Pdc = shaft_kW * 1e3 / g("eta_drive")
        I, V = solve_I(Pdc, soc)
        heat_cells = I**2 * R_cell_pack
        rows.append({
            "shaft_kW": shaft_kW, "SOC_pct": soc, "pack_V_loaded": round(V, 1),
            "pack_I_A": round(I, 1), "cell_I_A": round(I / P, 1), "cell_C_rate": round(I / P / g("cell_Ah_typ"), 2),
            "ok_vs_350A_contactor": I <= g("gx14_carry_A"), "ok_vs_cell_60A": I / P <= g("cell_I_dis_std_A"),
            "cell_heat_kW": round(heat_cells / 1e3, 2), "total_pack_loss_kW": round(I**2 * R_pack / 1e3, 2),
        })
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "elec-power-table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
res["power_table_summary"] = [r for r in rows if r["SOC_pct"] in (100, 10)]

# max shaft power at the 350 A DC-current cap (the contactor rating), per SOC
cap = g("gx14_carry_A")
res["max_shaft_kW_at_350A_cap"] = {}
for soc in (100, 80, 50, 20, 10):
    Voc = S * ocv(soc); V = Voc - cap * R_pack
    res["max_shaft_kW_at_350A_cap"][soc] = round(V * cap * g("eta_drive") / 1e3, 1)

# ------------------------------------------------------------------ motor / inverter matching (EMRAX 228 datasheet v1.7)
emrax = {  # winding: (V for peak power, peak Arms, cont Arms LC, Kt Nm/A)
    "HV": (830, 235, 120, 0.98), "MV": (630, 360, 180, 0.64), "LV": (250, 920, 470, 0.24),
    "LV+43%": (360, 650, 330, 0.34), "LV+100%": (500, 460, 240, 0.48), "HV+42%": (830, 165, 85, None)}
res["emrax228_windings_datasheet"] = {k: {"V_for_peak": v[0], "peak_Arms": v[1], "cont_Arms": v[2]} for k, v in emrax.items()}
# Kt for LV+43 from the datasheet torque/current: 220 Nm / 650 A
Kt = 220 / 650
w_peak = 5500 * 2 * math.pi / 60
res["motor_match"] = {
    "choice": "EMRAX 228 LV+43% (360 V for peak power), liquid or combined cooled",
    "why": "pack is 250-420 V (loaded floor about 330 V at 10% SOC under peak). MV needs 630 V and HV 830 V, so they cannot reach peak power on this bus (same conclusion as drive-study.md). LV+43% needs 360 V and 650 Arms.",
    "Kt_Nm_per_A": round(Kt, 3),
    "peak_phase_current_Arms": 650, "continuous_phase_current_Arms": 330,
    "torque_at_300Arms_Nm": round(Kt * 300, 0),
    "power_at_300Arms_5500rpm_kW": round(Kt * 300 * w_peak / 1e3, 1),
    "power_at_455Arms_5500rpm_kW": round(Kt * 455 * w_peak / 1e3, 1),
    "inverter_H100_150A_cont": "FAILS: 150 Arms continuous gives %.0f Nm, i.e. %.0f kW at 5500 rpm (<55 kW target); 450 A peak gives %.0f kW" % (
        Kt * 150, Kt * 150 * w_peak / 1e3, Kt * 450 * w_peak / 1e3),
    "inverter_CM200DX_300A_cont_740A_peak": "PASSES: 300 Arms continuous gives %.0f kW at 5500 rpm; 740 A peak > 650 A motor peak" % (Kt * 300 * w_peak / 1e3),
    "verdict": "Cascadia CM200DX (6.75 kg, 50-480 V, 300 Arms cont / 740 Arms peak) is the inverter. The emDrive H100 (3.5 kg) cannot supply this motor's current."
}

# ------------------------------------------------------------------ protection: short circuit and fuse coordination
Voc_full = S * g("cell_V_max")
Isc_max = Voc_full / R_pack_ac      # optimistic-for-fault: fastest AC-impedance case
Isc_min = Voc_full / R_pack         # DC-impedance case
res["short_circuit"] = {
    "bolted_Isc_kA_range": [round(Isc_min / 1e3, 2), round(Isc_max / 1e3, 2)],
    "main_fuse_A": g("main_fuse_A"), "fuse_multiple_at_min_Isc": round(Isc_min / g("main_fuse_A"), 1),
    "pyro_break_kA": g("pyro_break_kA"), "margin_pyro_over_max_Isc": round(g("pyro_break_kA") * 1e3 / Isc_max, 1),
    "GX14_make_break_note": "contactor opens only below about 350 A; all higher currents are cleared by pyro or fuse",
    "peak_vs_fuse": "DC current is capped at 350 A in VCU/inverter (matches GX14 carry); 350 A is %.2f x the 400 A fuse (below the usual 1.3 x no-blow)" % (350 / 400),
    "continuous_vs_fuse_derated": "worst continuous 55 kW at 10%% SOC is about %.0f A against 0.8 x 400 = 320 A" % (solve_I(55e3 / g("eta_drive"), 10)[0]),
    "pyro_trip_rules": ["> 650 A for 20 ms", "> 480 A for 40 s", "crash flag (IMU / ABS unit) within 20 ms", "BMS hard fault latched"],
}

# ------------------------------------------------------------------ per-cell fuse wire (Al wire bond), adiabatic opening + 1-D steady conduction
rho0, alpha = 2.82e-8, 0.0039      # aluminium
cv = 2.43e6                        # J/m3K
k_al = 237.0
Tm, Ta = 600.0, 25.0               # wire open temperature (below 660 C melt), start temperature
def adiabatic_t(I, d_m):
    A = math.pi * d_m**2 / 4
    J = I / A
    # integral of cv dT / (rho(T) J^2)
    T = np.linspace(Ta, Tm, 400)
    rho = rho0 * (1 + alpha * (T - 20))
    return float(np.trapz(cv / (rho * J**2), T))
def steady_dT(I, d_m, L=3e-3):
    A = math.pi * d_m**2 / 4
    J = I / A
    return rho0 * 1.5 * J**2 * L**2 / (8 * k_al)    # rho at about +120 K
Rc = g("cell_R_dc_mohm") / 1e3
Rac = g("cell_R_ac_mohm") / 1e3
sweep = []
for d_mm in (0.25, 0.30, 0.40, 0.50, 0.60):
    d = d_mm / 1e3; A = math.pi * d**2 / 4
    Rw = rho0 * 1.5 * 3e-3 / A                       # one 3 mm wire, hot
    # shorted cell: 10 healthy neighbours feed it through their own wires (two wires in series per path: + end and - end)
    I_short = g("cell_V_max") / ((Rac + 2 * Rw) / (P - 1) + 2 * Rw)
    I_neigh = I_short / (P - 1)
    t_short = adiabatic_t(I_short, d)
    t_neigh = adiabatic_t(I_neigh, d)
    I_peak_cell = g("gx14_carry_A") / P
    sweep.append({"wire_dia_mm": d_mm, "wire_R_mohm": round(Rw * 1e3, 2), "I_shorted_cell_wire_A": round(I_short),
                  "t_open_shorted_ms": round(t_short * 1e3, 3), "I_neighbour_wire_A": round(I_neigh),
                  "t_neighbour_melt_ms": round(t_neigh * 1e3, 1), "selectivity_x": round(t_neigh / t_short, 1),
                  "steady_rise_at_32A_K": round(steady_dT(I_peak_cell, d), 1),
                  "steady_fuse_estimate_A": round(math.sqrt(8 * k_al * (Tm - 100) / (rho0 * 2.0 * 3e-3**2)) * A)})
chosen = [s for s in sweep if s["selectivity_x"] >= 10 and s["steady_rise_at_32A_K"] <= 40][0]
res["cell_fuse_wire"] = {"sweep": sweep, "rules": ["selectivity >= 10x", "steady rise <= 40 K at 31.8 A per-cell peak", "smallest passing diameter"],
                         "chosen": chosen,
                         "decision": "YES, per-cell fusing: one Al wire bond (about %.2f mm) per cell end, 2,200 bonds. Wire diameter to be settled by pulse and fusing tests, not by this model." % chosen["wire_dia_mm"],
                         "caveat": "adiabatic model: conservative for neighbours surviving, optimistic for opening speed. Cell resistance is the datasheet value; weld/bond resistance is an estimate."}

# ------------------------------------------------------------------ precharge
C = g("dc_link_uF") * 1e-6; Rp = g("precharge_ohm"); Vpk = S * g("cell_V_max")
tau = Rp * C
res["precharge"] = {
    "C_uF": g("dc_link_uF"), "R_ohm": Rp, "tau_s": round(tau, 3), "t_95pct_s": round(3 * tau, 2),
    "start_current_A_at_420V": round(Vpk / Rp, 2), "start_power_W": round(Vpk**2 / Rp), "energy_in_resistor_J": round(0.5 * C * Vpk**2),
    "shorted_bus_abort_energy_J": round(Vpk**2 / Rp * 0.5),
    "rule": "close main + contactor when bus >= pack - 21 V; if not within 0.5 s abort and latch fault; weld-check precharge relay",
    "active_discharge": "bus must fall below 60 V within 3 s of contactor opening (inverter active discharge; to be specified with Cascadia). Passive 70 kohm bleed alone is 88 s.",
}

# ------------------------------------------------------------------ isolation
res["isolation"] = {
    "monitor": "Bender ISOMETER iso175C class (or IR155-class automotive IMD) on the HV bus; BMS isolation check as cross-check",
    "ISO6469-3_limit_DC_ohm_per_V": 100, "ISO6469-3_limit_AC_connected_ohm_per_V": 500,
    "threshold_at_420V_DC_kohm": 100 * 420 / 1e3, "threshold_at_420V_AC_kohm": 500 * 420 / 1e3,
    "set_warning_kohm": 500, "set_fault_kohm": 210,
    "why_210": "the OBC makes the bus conductively linked to an AC circuit while plugged in, so the stricter 500 ohm/V figure (210 kohm at 420 V) is used in all modes",
    "dc_charge_note": "station and bike monitors must not run at the same time: bike IMD pauses during CableCheck / station isolation test",
}

# ------------------------------------------------------------------ fast charge (CC at a per-cell cap, voltage-limited)
def charge_sim(I_cell_cap, soc0=10, soc1=80, R=R_cell_pack, dt=1.0):
    soc = soc0; t = 0.0; Ah_pack = P * g("cell_Ah_typ"); Wh = 0.0; heat_Wh = 0.0; Ipk = 0
    while soc < soc1:
        Voc = ocv(soc)
        I_lim_v = max((g("cell_V_max") - Voc) / (g("cell_R_dc_mohm") / 1e3), 0)   # per cell, terminal V <= 4.2 V
        Ic = min(I_cell_cap, I_lim_v)
        I = Ic * P
        soc += I * dt / 3600 / Ah_pack * 100
        Vt = S * (Voc + Ic * g("cell_R_dc_mohm") / 1e3)
        Wh += Vt * I * dt / 3600; heat_Wh += I**2 * R_pack * dt / 3600; t += dt; Ipk = max(Ipk, I)
    return t / 60, Wh / 1e3, heat_Wh / 1e3, Ipk
charge = []
for cap in (8, 10, 12.5, 14, 16, 20, 25):
    tmin, kWh_in, kWh_heat, Ipk = charge_sim(cap)
    charge.append({"cell_cap_A": cap, "C_rate": round(cap / g("cell_Ah_typ"), 2), "pack_cap_A": cap * P,
                   "time_10_80_min": round(tmin, 1), "station_energy_kWh": round(kWh_in, 1),
                   "avg_station_kW": round(kWh_in / (tmin / 60), 1), "peak_station_kW": round(Ipk * S * 4.2 / 1e3, 0),
                   "pack_heat_kWh": round(kWh_heat, 2), "avg_heat_kW": round(kWh_heat / (tmin / 60), 2)})
res["dc_charge_sweep"] = charge
res["dc_charge_choice"] = {
    "cap_A_per_cell": 12.5, "C": 2.08, "reason": "meets 10-80% in about 20 min (T6 target) at 2C, a 40% of the 30 A datasheet maximum; lowest cell stress that hits the target; heat about 2 kW avg",
    "caveat": "P60B datasheet does not state cycle life at 2C fast charge, and the charge chart is at 25 degC. Cold-weather derate and life are open until cell test data exists.",
}
# AC charging
for kw in (3.3, 6.6):
    eta = 0.92
    res.setdefault("ac_charge", {})[f"{kw}kW"] = {
        "10_90_h": round(0.8 * E_kWh / (kw * eta), 1), "0_100_h": round(E_kWh * 1.0 / (kw * eta), 1),
        "AC_current_at_240V_A": round(kw * 1e3 / 240, 1)}
res["ac_charge"]["120V_12A_kW"] = 1.44
res["ac_charge"]["120V_12A_10_80_h_at_1.3kW"] = round(0.7 * E_kWh / 1.3, 1)

# ------------------------------------------------------------------ heat
res["heat_notes"] = {
    "cell_heat_at_55kW_shaft_10pctSOC_kW": rows[[i for i, r in enumerate(rows) if r['shaft_kW'] == 55 and r['SOC_pct'] == 10][0]]["cell_heat_kW"],
    "cell_heat_at_100kW_shaft_80pctSOC_kW": rows[[i for i, r in enumerate(rows) if r['shaft_kW'] == 100 and r['SOC_pct'] == 80][0]]["cell_heat_kW"],
    "comment": "the pack is the largest electrical heat source: pass these to the cooling agent",
}

# ------------------------------------------------------------------ interconnect estimate (mass)
plates = 2 * (S + 1)
plate_mass_g = 11 * (23.0 * 23.0) * 0.8 * 2.70e-3       # 11 cells of footprint 23x23 mm, 0.8 mm Al
res["interconnect_mass_kg"] = {
    "group_plates": round(plates * plate_mass_g / 1e3, 2),
    "module_links_and_series_links": round(S * 0.020, 2),
    "wire_bonds_2200": round(2200 * 1.0e-6 * 3, 3),
    "basis": "estimate: Al plates 0.8 mm per parallel group, 20 g series links; Al wire 0.4 mm x 3 mm is about 1 mg each, 2,200 bonds (negligible)",
}
res["interconnect_mass_kg"]["total"] = round(sum(v for k, v in res["interconnect_mass_kg"].items() if k != "basis"), 2)

with open(os.path.join(OUT, "elec-pack.json"), "w") as f:
    json.dump(res, f, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))

# ------------------------------------------------------------------ hand checks (printed)
print("pack:", res["pack"])
print("R_pack mohm: hand check", g("cell_R_dc_mohm") * S / P + 8.5, "script", res["pack"]["R_pack_dc_mohm"])
I, V = solve_I(100e3, 50)
print("hand: 100 kW DC at 50%% SOC: I=%.1f V=%.1f  P=%.1f kW" % (I, V, I * V / 1e3))
print("max shaft kW at 350 A cap:", res["max_shaft_kW_at_350A_cap"])
print("short circuit:", res["short_circuit"]["bolted_Isc_kA_range"])
for s in sweep: print(s)
print("chosen wire:", chosen["wire_dia_mm"])
print("precharge:", res["precharge"])
for c in charge: print(c)
print(res["ac_charge"])
print(res["motor_match"]["inverter_H100_150A_cont"]); print(res["motor_match"]["inverter_CM200DX_300A_cont_740A_peak"])
print("interconnect kg:", res["interconnect_mass_kg"])
for r in rows:
    if r["SOC_pct"] in (100, 10): print(r)
