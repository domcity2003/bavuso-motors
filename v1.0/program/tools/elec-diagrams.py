#!/usr/bin/env python
"""Bavuso V1 electrical diagrams, generated as SVG (no dependencies).
Run from v1.0 with the FreeCAD python (or any python 3):  program/tools/elec-diagrams.py
Writes program/data/elec-hv-single-line.svg, elec-lv-can.svg, elec-dc-session.svg.
Numbers shown on the diagrams come from elec-pack.json / elec-summary.json when present.
"""
import json, os
D = os.path.join("program", "data")
pack = json.load(open(os.path.join(D, "elec-pack.json")))

HV, LV, CAN1, CAN2, INK, BOX, BOXHV = "#c2410c", "#b91c1c", "#1d4ed8", "#0f766e", "#1f2937", "#f3f4f6", "#fff1e6"

class Svg:
    def __init__(s, w, h, title):
        s.w, s.h, s.o = w, h, []
        s.o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="Segoe UI, Arial, sans-serif">')
        s.o.append('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
        s.o.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')
        s.text(24, 34, title, 22, bold=True)
    def text(s, x, y, t, size=13, bold=False, anchor="start", color=INK, italic=False):
        t = t.replace("&", "&amp;").replace("<", "&lt;")
        s.o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"' + (' font-weight="700"' if bold else '') + (' font-style="italic"' if italic else '') + f'>{t}</text>')
    def lines(s, x, y, arr, size=12, anchor="start", color=INK, dy=15):
        for i, t in enumerate(arr): s.text(x, y + i * dy, t, size, anchor=anchor, color=color)
    def box(s, x, y, w, h, title, sub=(), fill=BOX, stroke=INK, size=13, dash=False, sw=1.5):
        s.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"' + (' stroke-dasharray="6 4"' if dash else '') + '/>')
        n = 1 + len(sub); y0 = y + h / 2 - (n - 1) * 8 + 4
        s.text(x + w / 2, y0, title, size, bold=True, anchor="middle")
        for i, t in enumerate(sub): s.text(x + w / 2, y0 + 16 * (i + 1), t, size - 2, anchor="middle", color="#4b5563")
    def line(s, pts, color=INK, w=2.5, dash=False, arrow=False, both=False):
        p = " ".join(f"{a},{b}" for a, b in pts)
        s.o.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"' + (' stroke-dasharray="7 5"' if dash else '') +
                   (' marker-end="url(#a)"' if arrow else '') + (' marker-start="url(#a)"' if both else '') + ' stroke-linejoin="round"/>')
    def dot(s, x, y, r=5, color=INK): s.o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    def contactor(s, x, y, label, color=HV):   # draws a contactor symbol centred at x,y (horizontal flow)
        s.o.append(f'<circle cx="{x-9}" cy="{y}" r="3" fill="#fff" stroke="{color}" stroke-width="2"/><circle cx="{x+9}" cy="{y}" r="3" fill="#fff" stroke="{color}" stroke-width="2"/>'
                   f'<line x1="{x-9}" y1="{y-1}" x2="{x+8}" y2="{y-11}" stroke="{color}" stroke-width="2.5"/>')
        s.text(x, y + 22, label, 12, anchor="middle", bold=True)
    def fuse(s, x, y, label, w=34):
        s.o.append(f'<rect x="{x-w/2}" y="{y-7}" width="{w}" height="14" fill="#fff" stroke="{HV}" stroke-width="2"/><line x1="{x-w/2}" y1="{y}" x2="{x+w/2}" y2="{y}" stroke="{HV}" stroke-width="1.5"/>')
        s.text(x, y + 24, label, 12, anchor="middle", bold=True)
    def save(s, name):
        s.o.append("</svg>")
        open(os.path.join(D, name), "w", encoding="utf-8").write("\n".join(s.o))

# =================================================================== 1. HV single-line
g = Svg(1500, 800, "Bavuso V1: HV single-line diagram (one line stands for the + / - pair)")
g.text(24, 56, "Pack 100s11p, 360 V nominal (420 V max), 23.8 kWh. EMRAX 228 LV+43% on a Cascadia CM200DX. Native NACS inlet, DC and AC. All HV parts in one sealed box.", 13, color="#4b5563")
# pack
g.box(20, 300, 210, 170, "Traction pack", ["100s11p, 1,100 x P60B", "10 modules of 10s11p (36 V each)", "per-cell Al fuse wire (0.4 mm)", "23.8 kWh, 250-420 V"], fill=BOXHV, stroke=HV, sw=2)
g.box(20, 500, 210, 66, "BMS: Orion BMS2-108", ["100 cell groups, 3 connectors, NTCs"], fill="#eef2ff", stroke=CAN1)
g.line([(125, 500), (125, 470)], color=CAN1, w=2)
g.box(62, 436, 126, 26, "MSD + 400 A fuse", [], fill="#fff", stroke=HV, size=12)
# HV box outline
g.box(262, 70, 780, 690, "", [], fill="#fffaf5", stroke=HV, dash=True, sw=2)
g.text(278, 92, "HV box: one sealed IP67 box (pyro, contactors, shunt, precharge, fuses, AC relays)", 13, bold=True, color=HV)
Y = 380
g.line([(210, Y), (300, Y)], HV)
g.text(235, Y - 10, "50 mm2", 11, anchor="middle")
g.fuse(330, Y, "F1 pyro 500 A"); g.line([(347, Y), (400, Y)], HV)
g.box(400, Y - 18, 56, 36, "IVT-S", [], size=12, fill="#fff", stroke=HV); g.text(428, Y + 34, "shunt, I, U1 U2 U3", 11, anchor="middle")
g.line([(456, Y), (560, Y)], HV); g.dot(560, Y, 6, HV)
g.text(462, Y - 10, "pack-side bus", 11, color=HV)
g.line([(560, Y), (620, Y)], HV); g.contactor(650, Y, "K1/K2 main +/-"); g.line([(660, Y), (800, Y)], HV)
g.line([(585, Y), (585, 322), (610, 322)], HV); g.contactor(640, 322, "K3"); g.box(690, 308, 70, 28, "220 ohm", [], size=11, fill="#fff", stroke=HV); g.line([(660, 322), (690, 322)], HV); g.line([(760, 322), (775, 322), (775, Y)], HV)
g.text(640, 284, "precharge", 11, anchor="middle", color=HV)
g.dot(585, Y, 4, HV); g.dot(775, Y, 4, HV)
g.text(745, Y - 10, "50 mm2", 11, anchor="middle")
# inverter and motor
g.box(1060, 320, 160, 120, "Inverter", ["Cascadia CM200DX", "50-480 V, 300 A cont", "740 A rms peak"], fill=BOXHV, stroke=HV, sw=2)
g.line([(800, Y), (1060, Y)], HV)
g.text(1030, Y - 10, "DC bus", 11, anchor="end")
g.line([(1220, Y), (1290, Y)], HV, w=4)
g.text(1255, Y - 10, "U V W 50 mm2", 11, anchor="middle")
g.o.append(f'<circle cx="1360" cy="{Y}" r="60" fill="{BOXHV}" stroke="{HV}" stroke-width="2"/>')
g.text(1360, Y - 6, "EMRAX 228", 14, bold=True, anchor="middle"); g.text(1360, Y + 12, "LV+43%", 12, anchor="middle"); g.text(1360, Y + 28, "220 Nm, 124 kW", 11, anchor="middle", color="#4b5563")
# DC charge branch
g.box(40, 80, 170, 150, "NACS inlet (J3400)", ["Volex, 1000 V, 500 A", "DC+/L1  DC-/L2", "CP + PP, latch, 2 NTC", "EVCC (PLC, CAN)"], fill="#f0fdf4", stroke="#15803d", sw=2)
g.line([(210, 120), (300, 120)], HV); g.text(235, 112, "35 mm2", 11, anchor="middle")
g.contactor(335, 120, "K4/K5 DC charge"); g.line([(345, 120), (560, 120), (560, Y)], HV)
g.text(380, 111, "to pack-side bus: the inverter stays dead while charging", 11, color=HV)
# AC branch
g.line([(210, 200), (300, 200)], HV, dash=False); g.text(235, 192, "35 mm2", 11, anchor="middle")
g.contactor(335, 200, "AC relays"); g.line([(345, 200), (400, 200)], HV)
g.box(400, 178, 120, 44, "OBC 3.3 kW", ["100-264 V in"], fill=BOXHV, stroke=HV)
g.line([(520, 200), (545, 200)], HV); g.fuse(560, 200, "F2 30 A", 24); g.line([(572, 200), (600, 200)], HV, w=0)
g.line([(560, 200), (560, 120)], HV)
g.text(620, 170, "AC and DC share the same two pins: K4/K5 and the AC relays are", 11, color="#4b5563"); g.text(620, 184, "mechanically + electronically interlocked, never both closed", 11, color="#4b5563")
# lower branches
g.line([(560, Y), (560, 640)], HV)
g.dot(560, 480, 4, HV); g.line([(560, 480), (600, 480)], HV); g.fuse(615, 480, "F3 10 A", 24); g.line([(627, 480), (680, 480)], HV)
g.box(680, 456, 150, 48, "DC-DC 0.8 kW", ["HV to 12 V, CAN"], fill=BOXHV, stroke=HV)
g.line([(830, 480), (900, 480)], LV, w=2.5, arrow=True); g.box(900, 456, 150, 48, "12 V LiFePO4", ["4.5 Ah, 0.9 kg"], fill="#fef2f2", stroke=LV)
g.dot(560, 580, 4, HV); g.line([(560, 580), (600, 580)], HV); g.fuse(615, 580, "F4 15 A", 24); g.line([(627, 580), (680, 580)], HV)
g.box(680, 556, 150, 48, "Coolant PTC", ["3 kW, HV heater"], fill=BOXHV, stroke=HV)
# IMD
g.box(780, 650, 200, 52, "Isolation monitor", ["warn 500 k, fault 210 k"], fill="#fff", stroke=HV)
g.line([(865, 650), (865, Y)], HV, dash=True, w=1.5)
g.dot(865, Y, 4, HV)
g.text(780, 722, "measures HV+ and HV- to chassis; paused during", 11, color="#4b5563"); g.text(780, 736, "the station's CableCheck insulation test", 11, color="#4b5563")
# HVIL / control
g.line([(40, 760), (1480, 760)], "#7c3aed", w=2, dash=True)
g.text(24, 750, "HVIL loop (20 mA PWM): MSD > pack lid connector > HV box lid > inverter > OBC > DC-DC > heater > back to VCU. Open loop = contactors open, no pyro.", 12, color="#7c3aed", bold=True)
g.box(1090, 520, 380, 150, "Protection and control (VCU + BMS)", [
    "Fires pyro F1: >650 A for 20 ms, >480 A for 40 s, crash flag, hard fault",
    "Opens K1-K5 below 350 A only (GX14 350 A carry)",
    "DC current cap 350 A, charge cap 137 A (12.5 A per cell)",
    "Precharge: K3 until bus is within 21 V, abort at 0.5 s",
    "Weld check of K4/K5 through shunt U3 before the inlet unlocks"], fill="#f9fafb", stroke="#6b7280")
g.text(1090, 700, "Short circuit %.1f to %.1f kA (calculated); fuse and pyro break 20+ kA" % tuple(pack["short_circuit"]["bolted_Isc_kA_range"]), 12, color="#4b5563")
g.text(24, 785, "Legend: orange = HV (shielded, orange sleeve); red = 12 V; blue = BMS; green = charge inlet. K = GX14 contactor; F = fuse.", 12, color="#6b7280")
g.save("elec-hv-single-line.svg")

# =================================================================== 2. LV / CAN block diagram
l = Svg(1500, 780, "Bavuso V1: 12 V and CAN block diagram")
l.text(24, 56, "Two 500 kbit/s CAN buses, linear, 120 ohm at both physical ends, stubs under 0.3 m. VCU is the gateway between them.", 13, color="#4b5563")
YB1, YB2 = 125, 690
l.line([(60, YB1), (1440, YB1)], CAN1, w=5); l.text(60, YB1 - 10, "CAN1 powertrain, 500 kbit/s", 13, bold=True, color=CAN1)
l.line([(60, YB2), (1440, YB2)], CAN2, w=5); l.text(60, YB2 + 28, "CAN2 chassis, 500 kbit/s", 13, bold=True, color=CAN2)
for x in (60, 1440):
    for yy, c in ((YB1, CAN1), (YB2, CAN2)): l.o.append(f'<rect x="{x-8}" y="{yy-12}" width="16" height="24" rx="3" fill="#fff" stroke="{c}" stroke-width="2"/>')
l.text(60, YB1 + 34, "120 ohm", 10, anchor="middle", color=CAN1); l.text(1440, YB1 + 34, "120 ohm", 10, anchor="middle", color=CAN1)
c1 = [("Inverter", "CM200DX"), ("BMS", "Orion BMS2"), ("Shunt", "IVT-S"), ("Iso monitor", "IMD"), ("OBC", "3.3 kW"), ("EVCC", "NACS PLC"), ("VCU", "gateway + safety")]
for i, (n, s) in enumerate(c1):
    x = 230 + i * 170
    l.line([(x + 75, YB1), (x + 75, 160)], CAN1, w=2); l.box(x, 160, 150, 52, n, [s], fill="#eff6ff", stroke=CAN1)
vcu_x = 230 + 6 * 170
l.line([(vcu_x + 75, 212), (vcu_x + 75, YB2 - 0)], "#7c3aed", w=2.5, dash=False)
l.text(vcu_x + 82, 440, "VCU gateway", 11, color="#7c3aed", bold=True)
# middle zone: power chain
l.box(60, 330, 150, 60, "DC-DC 0.8 kW", ["from HV box, 10 A fuse"], fill=BOXHV, stroke=HV)
l.line([(135, 330), (135, YB1)], CAN1, w=2)
l.line([(210, 360), (320, 360)], LV, w=3, arrow=True); l.text(265, 350, "80 A", 11, anchor="middle")
l.box(320, 335, 150, 50, "12 V LiFePO4", ["4.5 Ah, 59 Wh"], fill="#fef2f2", stroke=LV)
l.line([(470, 360), (570, 360)], LV, w=3, arrow=True); l.text(520, 350, "100 A", 11, anchor="middle")
l.box(570, 300, 190, 120, "Power distribution unit", ["smart fuses, 16 channels", "CAN2 node, diagnostics", "keyed wake from keyless"], fill="#fef2f2", stroke=LV, sw=2)
loads = [("Lights", "headlamp, DRL, tail, indicators"), ("Cooling", "pump, fan"), ("HV box control", "coils, pyro firing, HVIL"), ("Inlet", "latch, lamp, pin NTCs"), ("Comfort", "heated grips, horn")]
for i, (n, s) in enumerate(loads):
    y = 262 + i * 44
    l.line([(760, 360), (830, 360), (830, y + 20), (880, y + 20)], LV, w=2, arrow=True)
    l.box(880, y, 210, 38, n, [], fill="#fff", stroke=LV, size=12)
    l.text(1100, y + 23, s, 11, color="#4b5563")
l.lines(570, 440, ["Loads: night riding 259 W,", "DC charge 163 W, 1 s peak 696 W", "(ABS pump 300 W); elec-lv-loads.csv"], 11, color="#4b5563")
# CAN2 nodes
c2 = [("ABS + IMU", "Bosch ABS 10 class"), ("TFT dash", "6.5 in"), ("Keyless", "LF + BLE"), ("Telematics", "LTE-M, GNSS"), ("PDU", "diagnostics"), ("TPMS rx", ""), ("Switch cubes", "LIN to VCU")]
for i, (n, s) in enumerate(c2):
    x = 230 + i * 170
    l.line([(x + 75, YB2), (x + 75, 640)], CAN2, w=2); l.box(x, 588, 150, 52, n, [s] if s else [], fill="#f0fdfa", stroke=CAN2)
l.text(24, 760, "Crash path: ABS/IMU crash flag > VCU > pyro fire in under 20 ms (hard-wired backup line from VCU to pyro driver). Key-off wake: keyless > PDU > VCU. Daily 10 min HV top-up of the 12 V battery.", 12, color="#6b7280")
l.save("elec-lv-can.svg")

# =================================================================== 3. DC session sequence
q = Svg(1500, 980, "Bavuso V1: DC fast-charge session at a NACS Supercharger (DIN 70121 / ISO 15118)")
cols = {"BMS": 150, "EVCC (bike)": 480, "Station SECC": 880, "Station power": 1250}
for n, x in cols.items():
    q.box(x - 85, 60, 170, 40, n, [], fill="#f3f4f6", size=13)
    q.line([(x, 100), (x, 940)], "#9ca3af", w=1.5, dash=True)
X = lambda n: cols[n]
def msg(y, a, b, t, color=INK, note=None, dashed=False):
    q.line([(X(a), y), (X(b), y)], color, w=2, arrow=True, dash=dashed)
    mx = (X(a) + X(b)) / 2
    q.text(mx, y - 7, t, 12, anchor="middle", color=color)
    if note: q.text(mx, y + 14, note, 10, anchor="middle", color="#6b7280", italic=True)
def band(y0, y1, label, color):
    q.o.append(f'<rect x="20" y="{y0}" width="1460" height="{y1-y0}" fill="{color}" opacity="0.10"/>')
    q.text(26, y0 + 15, label, 11, bold=True, color="#374151")
band(110, 205, "1 CONNECT", "#2563eb")
msg(150, "Station SECC", "EVCC (bike)", "Plug seated: PP + CP, state A to B (12 V to 9 V)", note="inlet latch locks; K4/K5 stay open")
msg(185, "EVCC (bike)", "BMS", "Wake: charge request, read pack V / SOC / limits")
band(205, 330, "2 COMMUNICATE", "#7c3aed")
msg(240, "EVCC (bike)", "Station SECC", "SLAC matching over control pilot (HomePlug Green PHY PLC)")
msg(272, "EVCC (bike)", "Station SECC", "SECC discovery (SDP), TCP (TLS only in ISO 15118)")
msg(304, "EVCC (bike)", "Station SECC", "supportedAppProtocol: DIN 70121 / ISO 15118-2 (-20 later)", note="Tesla's CAN-over-pilot is legacy; Superchargers speak both")
band(330, 440, "3 AUTHORISE", "#b45309")
msg(366, "EVCC (bike)", "Station SECC", "SessionSetup, ServiceDiscovery, PaymentSelection (EIM)")
msg(404, "Station SECC", "EVCC (bike)", "Authorised: account / app / vehicle ID (network rules)", color="#b45309", note="Plug&Charge needs ISO 15118 certificates. Access for Bavuso is NOT established (report section 3)")
band(440, 600, "4 PARAMETERS + CABLE CHECK", "#0f766e")
msg(476, "BMS", "EVCC (bike)", "Limits: Vmax 420 V, Imax 137 A (12.5 A/cell), target 80%")
msg(508, "EVCC (bike)", "Station SECC", "ChargeParameterDiscovery: EV max V/I/power, SOC")
msg(540, "EVCC (bike)", "Station SECC", "CableCheck: bike IMD paused, station tests isolation", note="station contactors close, 500 V test")
msg(578, "Station SECC", "EVCC (bike)", "CableCheck OK")
band(600, 700, "5 PRECHARGE + CLOSE", "#c2410c")
msg(628, "EVCC (bike)", "Station SECC", "PreCharge: EV bus voltage (shunt U3 vs pack U1)", note="station ramps its output to within 20 V of the pack")
msg(668, "EVCC (bike)", "BMS", "PowerDelivery(start): BMS permits, VCU closes K4/K5")
band(700, 850, "6 CHARGE", "#15803d")
msg(738, "EVCC (bike)", "Station SECC", "CurrentDemand: target V and I every 100-250 ms", note="start about 137 A, tapers with SOC / temperature")
msg(780, "Station SECC", "Station power", "Deliver V, I (up to 58 kW peak at 12.5 A/cell, 53 kW average)", color="#15803d")
msg(818, "BMS", "EVCC (bike)", "Derate on pack temperature or cell voltage; stop at 80%", dashed=True)
band(850, 940, "7 STOP", "#6b7280")
msg(876, "EVCC (bike)", "Station SECC", "PowerDelivery(stop), current ramps to near 0")
msg(906, "EVCC (bike)", "Station SECC", "WeldingDetection: K4/K5 open, U3 falls; SessionStop")
q.text(24, 962, "Then CP back to B, inlet unlocks only after weld check passes. A gap of 10-80% in about 20 min means the cell cap of 12.5 A (2.08 C) is held to about 80% SOC (calculated).", 12, color="#6b7280")
q.save("elec-dc-session.svg")
print("diagrams written")
