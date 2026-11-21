#!/usr/bin/env python
"""Bavuso V1 electrical: 12 V loads, harness runs (HV + LV), electronics BOM, mass and cost vs budget.
Run from v1.0 with the FreeCAD python. Reads program/data/elec-pack.json (run elec-pack.py first).
Writes program/data/elec-lv-loads.csv, elec-harness.csv, elec-bom.csv, elec-summary.json.
Basis labels: supplier / datasheet / calculated / estimate. All lengths are ESTIMATES (the V1 layout is not frozen):
they scale from the routes measured in the CAD for the previous design (detailed-design/electrical/hv-cables.csv), +-30%.
"""
import csv, json, os

D = os.path.join("program", "data")
pack = json.load(open(os.path.join(D, "elec-pack.json")))

# ------------------------------------------------------------------ 12 V loads (W) : name, riding-night, DC-charging, 1-s peak, basis
loads = [
    ("LED headlamp low beam", 22, 0, 22, "estimate"),
    ("LED high beam (adds)", 0, 0, 18, "estimate"),
    ("DRL / light band", 6, 0, 6, "estimate"),
    ("Tail + brake (avg)", 5, 0, 10, "estimate"),
    ("Indicators (avg, flashing)", 6, 0, 12, "estimate"),
    ("Plate lamp", 1, 0, 1, "estimate"),
    ("Horn", 0, 0, 25, "estimate"),
    ("TFT dash", 12, 3, 12, "estimate"),
    ("VCU", 8, 8, 10, "estimate"),
    ("BMS + IVT-S + iso monitor", 9, 9, 10, "estimate"),
    ("Inverter logic", 10, 0, 12, "estimate"),
    ("EVCC + inlet latch", 3, 10, 15, "estimate"),
    ("OBC / DC-DC control", 4, 6, 6, "estimate"),
    ("Contactor coils (4 + precharge)", 10, 8, 14, "supplier: GX14 coil 2.8 W each with economiser"),
    ("Keyless + telematics + TPMS rx", 8, 4, 8, "estimate"),
    ("ABS ECU (idle)", 5, 5, 5, "estimate"),
    ("ABS pump (event)", 0, 0, 300, "estimate: Bosch pump class"),
    ("Coolant pump", 50, 50, 50, "estimate"),
    ("Radiator fan", 40, 60, 60, "estimate (single fan, shared loop)"),
    ("Heated grips (comfort option)", 60, 0, 60, "estimate"),
    ("Steering lock / seat latch (momentary)", 0, 0, 40, "estimate"),
]
tot = [sum(l[i] for l in loads) for i in (1, 2, 3)]
with open(os.path.join(D, "elec-lv-loads.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["load", "riding_night_W", "dc_charging_W", "peak_1s_W", "basis"]); w.writerows(loads)
    w.writerow(["TOTAL", *tot, "calculated"])
dcdc_kw = 0.8
usable = 0.9 * dcdc_kw * 1000
lv = {"riding_night_W": tot[0], "dc_charging_W": tot[1], "peak_1s_W": tot[2],
      "dcdc_rating_W": 800, "dcdc_usable_W_at_50C_derate": usable,
      "margin_over_riding_pct": round((usable / tot[0] - 1) * 100),
      "battery_assist_A_at_peak": round(max(0, tot[2] - usable) / 12.5, 1),
      "battery": "LiFePO4 4.5 Ah, 59 Wh, 0.9 kg (Shorai LFX14A4 class, supplier)",
      "limp_home_min_on_essentials": round(59 * 0.7 / (22 + 8 + 9 + 10 + 12 + 10 + 12 + 5) / 1 * 60),
      "standby_days_15mA": round(4.5 * 0.7 / 0.015 / 24, 1)}

# ------------------------------------------------------------------ HV and LV harness
# kg/m: 50 mm2 shielded 0.63 (supplier Coroflex FHLR2GCB2G), others estimate
kgm_hv = {"50": 0.63, "35": 0.46, "4": 0.10, "2.5": 0.075, "6b": 0.06}
runs = []
def hv(i, name, frm, to, gauge, n, L, amp_note):
    runs.append(dict(id=i, domain="HV", run=name, from_=frm, to=to, gauge_mm2=gauge, wires=n, length_each_m=L,
                     mass_kg=round(kgm_hv[gauge.split()[0]] * n * L, 3), basis="length estimate; kg/m " + ("supplier" if gauge == "50" else "estimate"), note=amp_note))
hv("H01", "Pack + to HV box (pyro, main +)", "pack lid stud via MSD side", "HV box", "50", 1, 0.50, "350 A peak, 180 A cont")
hv("H02", "Pack - to HV box (shunt, main -)", "pack rear stud", "HV box", "50", 1, 0.40, "same")
hv("H03", "HV box to inverter DC+", "HV box", "CM200DX DC+", "50", 1, 0.35, "same")
hv("H04", "HV box to inverter DC-", "HV box", "CM200DX DC-", "50", 1, 0.35, "same")
hv("H05", "Motor phases U V W", "CM200DX", "EMRAX 228 terminals", "50", 3, 0.40, "650 A rms peak, 300 A rms cont; phases must stay short")
hv("H06", "Inlet to HV box, DC+/L1", "NACS inlet", "HV box charge contactors / AC relays", "35", 1, 0.80, "DC charge <=150 A; AC 14-28 A on the same pin")
hv("H07", "Inlet to HV box, DC-/L2", "NACS inlet", "HV box", "35", 1, 0.80, "same")
hv("H08", "AC relays to onboard charger", "HV box", "OBC AC in", "4", 2, 0.50, "28 A max at 6.6 kW")
hv("H09", "OBC DC out to pack bus", "OBC", "HV box", "4", 2, 0.50, "<=20 A")
hv("H10", "DC-DC HV input", "HV box", "DC-DC", "2.5", 2, 0.50, "10 A fuse")
hv("H11", "Coolant PTC heater", "HV box", "heater", "2.5", 2, 0.50, "15 A fuse")
hv("H12", "Bonding straps, housings to frame", "8 HV housings", "frame", "6b", 8, 0.30, "<0.1 ohm")
hv_cable = sum(r["mass_kg"] for r in runs)
n_big = 12; n_small = 14; n_lug = 8
hv_conn = round(n_big * 0.12 + n_small * 0.04 + n_lug * 0.03, 2)
runs.append(dict(id="H13", domain="HV", run="Connectors: 12 PowerLok-300 class halves, 14 small shielded halves, 8 lugs", from_="", to="", gauge_mm2="", wires="", length_each_m="",
                 mass_kg=hv_conn, basis="estimate (PowerLok half 0.12 kg from prior BOM)", note="conduit/sleeve included below"))
hv_sleeve = round(0.10 * hv_cable, 2)
runs.append(dict(id="H14", domain="HV", run="Orange conduit, clips, glands (10% of cable)", from_="", to="", gauge_mm2="", wires="", length_each_m="", mass_kg=hv_sleeve, basis="estimate", note=""))
hv_total = round(hv_cable + hv_conn + hv_sleeve, 2)

# LV: kg per metre per wire (ISO 6722 FLRY-B class, estimate)
kgm_lv = {"0.35": 0.0050, "0.5": 0.0065, "1.0": 0.0126, "1.5": 0.0175, "4": 0.045, "10": 0.110}
def lvr(i, name, frm, to, gauge, n, L, note=""):
    runs.append(dict(id=i, domain="LV", run=name, from_=frm, to=to, gauge_mm2=gauge, wires=n, length_each_m=L,
                     mass_kg=round(kgm_lv[gauge] * n * L, 3), basis="estimate", note=note))
lvr("L01", "12 V battery + to power unit (100 A fuse)", "battery", "PDU", "10", 1, 0.5)
lvr("L02", "12 V battery - to chassis", "battery", "frame", "10", 1, 0.4)
lvr("L03", "DC-DC 12 V out to PDU (80 A fuse)", "DC-DC", "PDU", "10", 1, 0.9, "800 W / 12.5 V = 64 A")
lvr("L04", "ABS pump and valve feed", "PDU", "ABS unit", "4", 2, 0.8, "30 A")
lvr("L05", "Front trunk: headlamp, DRL, dash, switch cubes, horn, ABS front sensor, grips", "PDU", "front end", "0.5", 18, 2.2)
lvr("L06", "Rear trunk: tail, brake, indicators, plate, ABS rear sensor, TPMS", "PDU", "tail", "0.5", 14, 1.6)
lvr("L07", "Cooling: pump + fan power", "PDU", "pump, fan", "1.0", 4, 1.0)
lvr("L08", "HV box control: coils, precharge, pyro firing, HVIL, shunt CAN", "PDU", "HV box", "0.5", 16, 0.9)
lvr("L09", "Inlet: latch, lamp, 2 pin NTCs, CP/PP", "PDU / EVCC", "inlet", "0.5", 10, 1.2)
lvr("L10", "CAN1 powertrain (twisted pair + shield, 3 m, 8 nodes)", "bus", "bus", "0.35", 3, 3.0, "120 ohm terminations at the two ends, stubs <0.3 m")
lvr("L11", "CAN2 chassis (twisted pair + shield, 4 m, 8 nodes)", "bus", "bus", "0.35", 3, 4.0, "")
lvr("L12", "Keyless LF antennas + telematics antennas", "modules", "antennas", "0.5", 8, 0.8, "coax allowance included at 8 x 0.8 m")
lvr("L13", "Heated grips", "PDU", "grips", "1.5", 4, 1.2)
lvr("L14", "Pack: BMS sense wires (100 x 22 AWG, 0.9 m avg), thermistors", "pack", "BMS", "0.35", 160, 0.9, "inside the pack; counted with pack internals")
lv_runs = [r for r in runs if r["domain"] == "LV" and r["id"] != "L14"]
lv_wire = sum(r["mass_kg"] for r in lv_runs)
lv_loom = round(0.80 * lv_wire, 2)      # connectors, seals, loom, tape, clips
runs.append(dict(id="L15", domain="LV", run="Connectors (TE DT/DTM class), seals, loom, tape, clips (80% of wire; matches the 2.08 kg LV ledger line)", from_="", to="", gauge_mm2="", wires="", length_each_m="", mass_kg=lv_loom, basis="estimate", note=""))
lv_total = round(lv_wire + lv_loom, 2)
pack_sense = [r for r in runs if r["id"] == "L14"][0]["mass_kg"]
with open(os.path.join(D, "elec-harness.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(runs[0].keys())); w.writeheader(); w.writerows(runs)

# ------------------------------------------------------------------ BOM: id, item, qty, kg_each, usd_proto_each, usd_10k_each, bucket, basis
# bucket E = counts in the 18 kg electronics budget; D = drive budget (20 kg); P = pack budget (103 kg); W = wiring budget (11 kg)
bom = [
    ("BMS Orion BMS2-108 (100 groups)", 1, 1.47, 700, 450, "E", "supplier mass (spec sheet); price retail/estimate"),
    ("BMS thermistor expansion module", 1, 0.15, 250, 120, "E", "estimate"),
    ("HV box enclosure, busbars, bonding (one box)", 1, 1.05, 300, 120, "E", "estimate (0.7 box + 0.35 bars)"),
    ("Main + DC-charge contactor Gigavac GX14 (K1,K2,K4,K5)", 4, 0.50, 260, 130, "E", "supplier mass 0.5 kg"),
    ("Precharge relay + 220 ohm resistor", 1, 0.25, 60, 25, "E", "estimate"),
    ("Pyrotechnic cut-off (Sensata STP500P class)", 1, 0.40, 350, 140, "E", "mass estimate; 22 kA break from prior study"),
    ("Current shunt sensor (IVT-S class, 500 A)", 1, 0.20, 230, 90, "E", "mass estimate"),
    ("AC relay pair (charge routing, interlocked)", 1, 0.30, 90, 40, "E", "estimate"),
    ("EV branch fuses (30 A OBC / 10 A DC-DC / 15 A heater)", 3, 0.05, 25, 10, "E", "estimate"),
    ("Isolation monitor (iso175 / IR155 class)", 1, 0.15, 360, 120, "E", "estimate"),
    ("NACS inlet Volex (J3400, 1000 V, 500 A) + lid", 1, 1.60, 300, 150, "E", "supplier mass 1.3 + 0.3 lid"),
    ("EVCC (ADVANTICS ADM-CS-EVCC class)", 1, 0.30, 300, 150, "E", "estimate"),
    ("Onboard charger 3.3 kW, universal 100-264 V input", 1, 3.50, 900, 550, "E", "class estimate, no part verified"),
    ("DC-DC 0.8 kW, HV to 12 V", 1, 1.50, 250, 150, "E", "estimate (HELLA 1.2 kW is 2.8 kg, supplier)"),
    ("VCU (AEM VCU200 proto, custom at scale)", 1, 0.40, 1100, 200, "E", "estimate"),
    ("Power distribution unit (smart fuses)", 1, 0.80, 1400, 150, "E", "ECUMaster PMU16 is 1.15 kg; custom 0.8 est"),
    ("TFT dash 6.5 in", 1, 0.75, 450, 180, "E", "estimate"),
    ("Keyless module + LF antennas + fob", 1, 0.25, 250, 80, "E", "estimate"),
    ("Telematics / gateway", 1, 0.15, 150, 45, "E", "estimate"),
    ("12 V LiFePO4 battery 4.5 Ah", 1, 0.90, 120, 60, "E", "supplier mass (Shorai LFX14A4)"),
    ("LED headlamp with DRL band", 1, 0.90, 350, 120, "E", "estimate"),
    ("Tail / brake lamp", 1, 0.35, 80, 30, "E", "estimate"),
    ("Indicators, LED", 4, 0.06, 30, 10, "E", "estimate"),
    ("Plate lamp + reflectors", 1, 0.10, 20, 6, "E", "estimate"),
    ("Horn", 1, 0.25, 20, 8, "E", "estimate"),
    ("Small sensors (TPMS x2, stand, brake switches)", 1, 0.25, 80, 40, "E", "estimate"),
    ("Inverter Cascadia CM200DX (50-480 V, 300/740 Arms)", 1, 6.75, 2500, 1300, "D", "supplier mass (drive budget, not electronics)"),
    ("Pack: busbar plates, series links, wire bonds", 1, pack["interconnect_mass_kg"]["total"], 1500, 300, "P", "estimate (pack budget)"),
    ("Pack: BMS sense harness + fuses + thermistors", 1, round(pack_sense + 0.10 + 0.15, 2), 400, 100, "P", "estimate (pack budget)"),
    ("Pack: manual service disconnect + 400 A fuse (MSD08 class)", 1, 0.40, 130, 60, "P", "mass estimate"),
    ("HV cables, connectors, sleeves", 1, hv_total, 1000, 300, "W", "calculated from elec-harness.csv"),
    ("LV harness incl. connectors and loom", 1, lv_total, 600, 200, "W", "calculated from elec-harness.csv"),
]
rows = []
for it, q, kg, c1, c2, b, basis in bom:
    rows.append(dict(item=it, qty=q, kg_each=round(kg, 3), kg_total=round(kg * q, 2), usd_proto_each=c1, usd_proto_total=c1 * q,
                     usd_10k_each=c2, usd_10k_total=c2 * q, budget=b, basis=basis))
with open(os.path.join(D, "elec-bom.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def sumb(b, k): return round(sum(r[k] for r in rows if r["budget"] == b), 2)
summ = {
    "electronics_E_kg": sumb("E", "kg_total"), "electronics_budget_kg": 18.0,
    "electronics_E_usd_proto": sumb("E", "usd_proto_total"), "electronics_E_usd_10k": sumb("E", "usd_10k_total"),
    "inverter_D_kg": sumb("D", "kg_total"), "inverter_usd_10k": sumb("D", "usd_10k_total"),
    "pack_electrical_P_kg": sumb("P", "kg_total"), "pack_electrical_usd_10k": sumb("P", "usd_10k_total"),
    "HV_cable_kg": hv_total, "LV_harness_kg": lv_total, "wiring_W_kg": sumb("W", "kg_total"), "wiring_budget_kg": 11.0,
    "wiring_usd_10k": sumb("W", "usd_10k_total"),
    "hv_cable_total_m": round(sum(r["length_each_m"] * r["wires"] for r in runs if r["domain"] == "HV" and r["gauge_mm2"] not in ("", "6b")), 1),
    "lv": lv,
}
summ["electronics_E_minus_inlet_evcc_12Vbatt_kg"] = round(summ["electronics_E_kg"] - 1.6 - 0.3 - 0.9, 2)
summ["total_electrical_usd_10k_all_buckets"] = round(summ["electronics_E_usd_10k"] + summ["inverter_usd_10k"] + summ["pack_electrical_usd_10k"] + summ["wiring_usd_10k"])
json.dump(summ, open(os.path.join(D, "elec-summary.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
print("HV cable kg %.2f conn %.2f sleeve %.2f ; LV wire %.2f loom %.2f ; pack sense %.2f" % (hv_cable, hv_conn, hv_sleeve, lv_wire, lv_loom, pack_sense))
