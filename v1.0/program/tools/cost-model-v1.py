"""Bavuso V1 unit-cost model (current architecture): 100 / 1,000 / 10,000 bikes per year.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/cost-model-v1.py
Writes program/data/cost-model-v1.csv and program/data/cost-model-v1.json

Labels: quote = published list/retail price; est = my estimate (no supplier contacted); calc = computed here.
Every price in USD per bike (per piece x qty). "p10k" is the piece price at 10,000 bikes/yr; other volumes use a
curve multiplier. Tooling is listed separately and amortised over 5 years of volume.
"""
import csv, json, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
VOLS = [100, 1000, 10000]
AMORT_YEARS = 5

# volume curves: multiplier on the 10k piece price at (100, 1k, 10k)
CURVE = {
    "oe":      (1.55, 1.20, 1.0),   # OE-class purchased parts (suspension, brakes, wheels)
    "oe_prem": (1.70, 1.30, 1.0),
    "elec":    (2.00, 1.35, 1.0),   # custom / low-volume electronics
    "gen":     (1.30, 1.10, 1.0),   # commodity purchased
    "mach":    (1.90, 1.30, 1.0),   # machined / fabricated made parts
    "body":    (3.20, 1.50, 1.0),   # low-volume composite/vacuum-form -> injection moulded
    "flat":    (1.0, 1.0, 1.0),
}
TOOL_SCALE = {"mach": (0.30, 0.60, 1.0), "body": (0.25, 0.60, 1.0), "none": (0, 0, 0)}

# ---------------------------------------------------------------- inputs that sensitivities change
BASE = dict(
    cell_usd=(6.00, 4.80, 3.80),          # per P60B cell at 100 / 1k / 10k bikes (est; see report)
    motor_usd=(6800.0, 5520.0, 4800.0),   # EMRAX 228 LV winding, low-volume supplier
    inv_usd=(5500.0, 4000.0, 3200.0),     # Cascadia CM200DX, low-volume supplier
    labour_rate=45.0,                      # USD/h loaded direct labour
    overhead_on_labour=0.60,               # plant overhead (energy, supervision, space) as share of labour
)
BAT_HOURS = (18.0, 7.0, 2.4)             # pack assembly h/pack
BIKE_HOURS = (38.0, 16.0, 7.5)           # bike assembly h/bike
EOL_HOURS = (2.0, 1.0, 0.5)
EOL_ENERGY = 1.0                         # USD of electricity per EOL (about 5 kWh in/out)
CELL_QC = (120.0, 70.0, 40.0)            # incoming cell screening + pack end-of-line test, USD/pack
WARRANTY = (0.040, 0.032, 0.028)         # share of material cost
LOGISTICS = (0.040, 0.030, 0.025)        # inbound freight, duty, handling, share of purchased parts
SCRAP_MADE = (0.04, 0.03, 0.02)          # share of made-part cost
SCRAP_CELL = (0.015, 0.010, 0.007)       # cell/pack yield loss, share of cell cost


def mk(group, item, qty, kg, p10k, curve, basis, src="", tool=0.0, tscale="none", mb="buy", notes=""):
    return dict(group=group, item=item, qty=qty, kg=kg, p10k=p10k, curve=curve, basis=basis, src=src,
                tool=tool, tscale=tscale, mb=mb, notes=notes)


def metal_part(mass, usd_kg, bty, proc10k):
    """made part at 10k: material (with buy-to-fly) + process"""
    return mass * usd_kg * bty + proc10k


def build_bom(p):
    L = []
    # ---------------- PACK
    L.append(mk("Pack", "Molicel INR-21700-P60B cells (1,100)", 1100, 0.075, 1.0, "cells", "est",
                "https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P60B_80145.pdf; "
                "B2B listings 3.35-8.00 USD/cell (hardware-shortlist.csv); P50B retail 7.50 at 1000 (batteryjunction/18650batterystore)",
                notes="piece price comes from cell_usd curve"))
    # pack case: 3 mm 5052/6061 sheet, 5 mm front wall, 8.3 kg
    case10k = metal_part(8.3, 4.6, 1.55, 165.0)   # laser cut, press-brake, TIG/FSW weld, leak test
    L.append(mk("Pack", "Pack case, 3 mm Al with 5 mm front wall, welded", 1, 8.3, case10k, "mach", "est",
                "program/09-structures.md (case mass 7.7-8.3 kg); sheet 4.6 USD/kg x 1.55 buy-to-fly + 165 USD process at 10k",
                tool=350000, tscale="mach", mb="make", notes="weld fixtures + brake dies, 10k tool set"))
    L.append(mk("Pack", "Busbars, series links, wire bonds, fuse collectors", 1, 11.8, 480.0, "elec", "est",
                "elec-bom.csv 300 USD at 10k + 2,200 wire bonds + collector plates; ledger 11.8 kg incl. internals", mb="make"))
    L.append(mk("Pack", "Cooling ribbons, manifolds, gap filler, fire barrier", 1, 6.2, 330.0, "elec", "est",
                "ledger BV-ENG-0007 6.19 kg; extruded Al ribbons + polymer manifolds, my estimate"))
    L.append(mk("Pack", "BMS sense harness, fuses, thermistors", 1, 0.97, 130.0, "elec", "est", "elec-bom.csv 100 USD at 10k x 1.3"))
    L.append(mk("Pack", "Manual service disconnect + 400 A fuse", 1, 0.4, 70.0, "gen", "est", "elec-bom.csv 60 USD at 10k"))
    L.append(mk("Pack", "BMS, Orion BMS2 (108 groups) + thermistor module", 1, 1.62, 520.0, "elec", "est",
                "https://www.orionbms.com/downloads/documents/orionbms2_specifications.pdf; retail 700+250, 10k est 450+120 less 0 (kept)"))
    # ---------------- DRIVE
    L.append(mk("Drive", "EMRAX 228 axial-flux motor, LV+43% winding, liquid cooled", 1, 13.2, 1.0, "motor", "est",
                "No list price published. Shortlist estimate 7,500 USD; EMRAX is a low-volume supplier",
                notes="piece price comes from motor_usd curve"))
    L.append(mk("Drive", "Cascadia CM200DX inverter (300/740 Arms)", 1, 6.75, 1.0, "inv", "est",
                "https://www.fuel2electric.com/cascadia-motion-cm200-inverter (plain CM200 listed 7,202 USD retail, 1 unit); shortlist 2,500 USD is an old estimate",
                notes="piece price comes from inv_usd curve"))
    L.append(mk("Drive", "Rear pulley 80T, CNC Al (hard anodised)", 1, 2.1, metal_part(2.1, 7.0, 1.8, 38.0), "mach", "est",
                "drive-design: 80T x 8 mm Gates; 6082 bar + 15 min CNC", tool=15000, tscale="mach", mb="make"))
    L.append(mk("Drive", "Motor pulley 21T (one; the ledger lists it twice)", 1, 0.5, metal_part(0.5, 7.0, 2.0, 14.0), "mach", "est",
                "drive-design", mb="make"))
    L.append(mk("Drive", "Gates carbon belt, 8 mm pitch", 1, 0.5, 110.0, "oe", "est", "gates.com Carbon Drive class; OEM price estimate"))
    L.append(mk("Drive", "Motor-arm yoke / pivot housing interface, machined Al", 1, 1.2, 105.0, "mach", "est",
                "09-structures.md: motor housing and pivot stubs form a load-bearing yoke", tool=40000, tscale="mach", mb="make"))
    L.append(mk("Drive", "Belt tensioner, guard, motor mounts, fasteners", 1, 0.8, 60.0, "gen", "est", ""))
    # ---------------- CHASSIS
    frame10k = metal_part(22.0, 9.0, 1.15, 5.5 * 55.0 + 105.0)   # 4130 tube + 5.5 h robot-assisted weld + coat/stress relief
    L.append(mk("Chassis", "Steel tube frame (25CrMo4/4130), TIG welded, coated, 25 kg incl. pads", 1, 25.0, frame10k, "frame", "est",
                "09-structures.md modelled 23.4 kg + 1.5; tube 9 USD/kg x 1.15 + 5.5 h weld at 10k (14 h at 100/yr) + coat/heat treat",
                tool=1000000, tscale="mach", mb="make", notes="frame labour hours curve in script"))
    L.append(mk("Chassis", "Cast A356-T6 single-sided swingarm, machined", 1, 3.4, 92.0, "arm", "est",
                "09-structures.md: cast A356 box arm; 10k = LP die cast + T6 + 20 min CNC + X-ray sampling; 100/yr = sand cast + full machining",
                tool=210000, tscale="mach", mb="make"))
    L.append(mk("Chassis", "Cast headstock + head tube/gusset", 1, 1.9, 48.0, "mach", "est", "09-structures.md (FAT 63 cast headstock)",
                tool=60000, tscale="mach", mb="make"))
    L.append(mk("Chassis", "Pack lug blocks (8) and pads, machined steel", 1, 2.3, 78.0, "mach", "est", "09-structures.md lug blocks 1.8 kg + pads 0.5", mb="make"))
    L.append(mk("Chassis", "Shock tower, cross brace, nose subframe, headlamp brackets", 1, 2.6, 85.0, "mach", "est", "ledger BV-CHS-0027/0023/0032", mb="make"))
    L.append(mk("Chassis", "Swingarm pivot: 2 tapered roller bearings (~50 mm), bolt, seals", 1, 1.4, 95.0, "oe", "est", "09-structures.md bearing need 44 kN each"))
    L.append(mk("Chassis", "Crash guards (pair) + mounts + sliders", 1, 4.0, 92.0, "mach", "est", "ledger BV-PRO", mb="make"))
    L.append(mk("Chassis", "Handguards (pair), 6082 bent tube", 1, 1.2, 46.0, "mach", "est", "ledger BV-PRO", mb="make"))
    # ---------------- RUNNING GEAR
    L.append(mk("Running gear", "43 mm USD fork, 170 mm travel, cartridge damping", 1, 6.8, 950.0, "oe_prem", "est",
                "Ohlins FGRT 301 retail EUR 3,975 (aftermarket); OE price ~25% of that, est"))
    L.append(mk("Running gear", "Rear shock, Ohlins STX 46 class, remote reservoir", 1, 3.0, 520.0, "oe_prem", "est",
                "https://www.ohlins.eu/en/products/motorcycle/kt-122--4458/ retail EUR 869"))
    L.append(mk("Running gear", "Forged Al wheels 19x3.00 / 17x4.50 with bearings", 1, 7.6, 1050.0, "oe_prem", "est", "shortlist 1,800 est for set; OE volume price"))
    L.append(mk("Running gear", "Tyres 110/80R19 + 150/70R17", 1, 9.1, 175.0, "oe", "est", "shortlist 260 retail pair; OE price"))
    L.append(mk("Running gear", "Front brakes: 2 x 300 mm discs, 2 x Brembo Stylema, carriers", 1, 3.65, 640.0, "oe_prem", "est",
                "https://www.bremboparts.com/africa/en/catalogue-bike/caliper/220D02010; shortlist 1,500 retail-ish"))
    L.append(mk("Running gear", "Rear brake: 245 mm disc, P34 caliper, carrier, bracket", 1, 1.7, 130.0, "oe", "est", "shortlist 350"))
    L.append(mk("Running gear", "Master cylinder (19RCS class), levers, hoses, rear pedal/master", 1, 3.2, 380.0, "oe", "est",
                "https://www.motosport.com/brembo-19rcs-brake-master-cylinder retail 553-689"))
    L.append(mk("Running gear", "Bosch ABS 10-class two-channel + sensors", 1, 1.1, 175.0, "oe_prem", "est", "shortlist 120 est; sensors added"))
    L.append(mk("Running gear", "Triple clamps (forged, machined), steering bearings, damper", 1, 3.4, 190.0, "mach", "est", "ledger BV-RUN-0001/0002/0068/0034", mb="make", tool=60000, tscale="mach"))
    L.append(mk("Running gear", "Bars, risers, grips, switch cubes, pegs, stand, axles, spacers", 1, 5.6, 360.0, "gen", "est", "ledger BV-RUN misc"))
    # ---------------- ELECTRONICS (elec-bom.csv 10k x 1.15 contingency unless noted)
    E = [
        ("HV box enclosure, busbars, contactors x4 (Gigavac GX14), precharge, pyro fuse, shunt, iso monitor", 5.9, 1.15 * (120 + 520 + 25 + 140 + 90 + 40 + 30 + 120), "https://www.digikey.fr/en/products/detail/sensata-gigavac-clean-energy/GX14CBB/17867714"),
        ("NACS inlet (Volex J3400, 1000 V) + lid", 1.6, 1.15 * 150, "https://www.volex.com/media/z3rmrwl5/volex-nacs-ev-charging-inlet.pdf"),
        ("EVCC (ADVANTICS class) charge controller", 0.3, 1.15 * 150, ""),
        ("Onboard charger 3.3 kW, 100-264 V", 3.5, 1.15 * 550, "class estimate; no part verified"),
        ("DC-DC 0.8 kW", 1.5, 1.15 * 150, ""),
        ("VCU (custom at scale)", 0.4, 1.15 * 200, "AEM VCU200 is prototype only"),
        ("Power distribution unit (smart fuses)", 0.8, 1.15 * 150, ""),
        ("TFT dash 6.5 in", 0.75, 1.15 * 180, ""),
        ("Keyless module, antennas, fob", 0.25, 1.15 * 80, ""),
        ("Telematics / gateway", 0.15, 1.15 * 45, ""),
        ("12 V LiFePO4 battery", 0.9, 1.15 * 60, ""),
        ("LED headlamp + DRL band, tail lamp, 4 indicators, plate lamp, horn", 2.3, 1.15 * (120 + 30 + 40 + 6 + 8), ""),
        ("Small sensors (TPMS x2, stand, brake switches)", 0.25, 1.15 * 40, ""),
        ("HV cables, connectors, sleeves (35 mm2 set)", 5.5, 380.0, "elec-harness.csv 5.5 kg; elec-bom 300 USD at 10k x 1.25"),
        ("LV harness incl. connectors and loom", 2.0, 320.0, "elec-harness.csv 2.0 kg; elec-bom 200 USD at 10k is light for a bike this size"),
    ]
    for name, kg, p, src in E:
        L.append(mk("Electronics", name, 1, kg, round(p, 1), "elec", "est", ("elec-bom.csv 10k price x 1.15; " + src).strip("; ")))
    # ---------------- COOLING
    L.append(mk("Cooling", "Radiator cores (2 x 165x128x28 mm), fans (2), shrouds", 1, 3.4, 160.0, "gen", "est", "10-thermal.md; ledger BV-THM"))
    L.append(mk("Cooling", "Pump, wax thermostat, 3 kW PTC heater, coolant, hoses, sensors", 1, 7.0, 190.0, "gen", "est", "10-thermal.md (wax thermostat replaces 4-port valve)"))
    # ---------------- BODY (piece price at 10k, tooling = 10k injection/stamp tooling)
    B = [
        ("Lower body / battery covers, painted PP/ABS", 1.96, 48, 110000),
        ("Upper fairing / tank cover, painted", 1.55, 52, 120000),
        ("Tail and side panels, painted", 1.19, 34, 85000),
        ("Rear hugger", 0.96, 20, 50000),
        ("Front fender", 0.46, 16, 35000),
        ("Tail undertray", 0.40, 12, 30000),
        ("Radiator pod shrouds + grilles", 0.75, 28, 45000),
        ("Motor side covers, seam trim, ledges, pivot caps", 0.40, 24, 35000),
        ("Windscreen, polycarbonate", 0.75, 28, 45000),
        ("Seat, two-level, with cover", 2.6, 85, 40000),
        ("Aluminium panels: belly skid, battery sides (2), belly sides (2)", 5.3, 110, 60000),
    ]
    for name, kg, p, t in B:
        L.append(mk("Body", name, 1, kg, float(p), "body", "est", "program/data/parts-ledger.csv masses; my estimate of moulded part + paint", tool=t, tscale="body", mb="make"))
    L.append(mk("Body", "Rear rack, mirrors, plate hanger, reflectors, seat welt", 1, 2.2, 125.0, "gen", "est", "ledger BV-BOD"))
    L.append(mk("Body", "Paint, decals, rubber, misc", 1, 1.0, 55.0, "gen", "est", ""))
    L.append(mk("Body", "Fasteners (titanium where visible), body brackets and fixings", 1, 5.0, 230.0, "gen", "est", "ledger BV-ALW-0007/0008"))
    return L


def piece_price(line, vi, p):
    c = line["curve"]
    if c == "cells":
        return p["cell_usd"][vi]
    if c == "motor":
        return p["motor_usd"][vi]
    if c == "inv":
        return p["inv_usd"][vi]
    if c == "frame":
        # material at 10k fixed; labour hours 14 / 9 / 5.5 at rate; coat/heat treat 105 -> 135 at low volume
        hrs = (14.0, 9.0, 5.5)[vi]
        return 22.0 * 9.0 * (1.30, 1.20, 1.15)[vi] + hrs * 55.0 * (p["labour_rate"] / 45.0) + (135.0, 120.0, 105.0)[vi]
    if c == "arm":
        return (470.0, 150.0, 92.0)[vi]
    return line["p10k"] * CURVE[c][vi]


def compute(p, tooling_extra=None):
    bom = build_bom(p)
    res = {}
    for vi, v in enumerate(VOLS):
        mat = made = cells = purchased = 0.0
        tool_total = 0.0
        for l in bom:
            ext = piece_price(l, vi, p) * l["qty"]
            if l["curve"] == "cells":
                cells += ext
            elif l["mb"] == "make":
                made += ext
            else:
                purchased += ext
            ts = TOOL_SCALE[l["tscale"]][vi]
            tool_total += l["tool"] * ts
        extra = {"Pack assembly line (wire bonder, fixtures, leak/HV test)": (250e3, 900e3, 3.0e6),
                 "Vehicle assembly line, jigs and fixtures": (150e3, 800e3, 3.5e6),
                 "End-of-line rig (dyno, brake, charge, HV safety)": (150e3, 500e3, 1.4e6)}
        for k, t in extra.items():
            tool_total += t[vi]
        mat = cells + made + purchased
        lab_rate = p["labour_rate"]
        pack_lab = BAT_HOURS[vi] * lab_rate
        bike_lab = BIKE_HOURS[vi] * lab_rate
        direct_lab = pack_lab + bike_lab
        overhead = direct_lab * p["overhead_on_labour"]
        eol = EOL_HOURS[vi] * (lab_rate * 1.2) + EOL_ENERGY
        qc = CELL_QC[vi]
        logistics = LOGISTICS[vi] * (purchased + cells)
        scrap = SCRAP_MADE[vi] * made + SCRAP_CELL[vi] * cells
        warranty = WARRANTY[vi] * mat
        tool_amort = tool_total / (AMORT_YEARS * v)
        total = mat + direct_lab + overhead + eol + qc + logistics + scrap + warranty + tool_amort
        res[v] = dict(cells=cells, made=made, purchased=purchased, material=mat, pack_labour=pack_lab, bike_labour=bike_lab,
                      overhead=overhead, eol=eol, qc=qc, logistics=logistics, scrap=scrap, warranty=warranty,
                      tooling_total=tool_total, tooling_amort=tool_amort, total=total)
    return bom, res


def variant(**kw):
    p = copy.deepcopy(BASE)
    p.update(kw)
    return p


def main():
    bom, base = compute(BASE)
    # ----- sensitivities
    sens = {}
    sens["cells -30%"] = compute(variant(cell_usd=tuple(c * 0.7 for c in BASE["cell_usd"])))[1]
    sens["cells +30%"] = compute(variant(cell_usd=tuple(c * 1.3 for c in BASE["cell_usd"])))[1]
    # volume-supplier equivalents (YASA/Bosch/Inverter OEM class), 10k only is the headline; lower volumes shown for completeness
    sens["motor+inverter at volume-supplier pricing (motor 2,800 / inverter 1,500 at 10k)"] = compute(variant(
        motor_usd=(5200.0, 3800.0, 2800.0), inv_usd=(3300.0, 2200.0, 1500.0)))[1]
    sens["stress: cells, motor, inverter stay at 1k-bike prices at 10k"] = compute(variant(cell_usd=(6.0, 4.8, 4.8), motor_usd=(6800.0, 5520.0, 5520.0), inv_usd=(5500.0, 4000.0, 4000.0)))[1]
    sens["labour rate 30 USD/h"] = compute(variant(labour_rate=30.0))[1]
    sens["labour rate 65 USD/h"] = compute(variant(labour_rate=65.0))[1]
    sens["cells -30% + volume-supplier motor/inverter"] = compute(variant(
        cell_usd=tuple(c * 0.7 for c in BASE["cell_usd"]), motor_usd=(5200.0, 3800.0, 2800.0), inv_usd=(3300.0, 2200.0, 1500.0)))[1]

    # ----- NRE (reused from startup-costs.csv base cases; engineering-level planning figures)
    nre = {v: {} for v in VOLS}
    with open(os.path.join(HERE, "..", "..", "startup-costs.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["cost_id"] in ("ENGINEERING", "SPECIALISTS", "PROTOTYPES", "CELL_LIFE", "COMPLIANCE"):
                nre[int(r["annual_volume_scenario"])][r["cost_id"]] = float(r["usd_base"])
    nre_tot = {v: sum(nre[v].values()) for v in VOLS}

    # ----- cost-down levers at 10k (each computed against base)
    t10 = base[10000]["total"]
    levers = []
    def lev(name, **kw):
        r = compute(variant(**kw))[1][10000]["total"]
        levers.append((name, t10 - r))
    lev("Cells 3.80 -> 3.10 USD (direct supply contract at 11M cells/yr, about 143 USD/kWh)", cell_usd=(6.0, 4.8, 3.10))
    lev("Motor 4,800 -> 2,800 USD (volume axial-flux supplier)", motor_usd=(6800, 5520, 2800))
    lev("Inverter 3,200 -> 1,500 USD (automotive SiC/IGBT inverter at volume)", inv_usd=(5500, 4000, 1500))
    lev("Assembly labour 45 -> 30 USD/h (lower-cost plant location)", labour_rate=30.0)

    # ---------------- write CSV
    rows = []
    hdr = ["section", "group", "item", "qty", "make_buy", "mass_kg", "label", "unit_usd_100", "unit_usd_1k", "unit_usd_10k",
           "ext_usd_100", "ext_usd_1k", "ext_usd_10k", "tooling_usd_100", "tooling_usd_1k", "tooling_usd_10k", "source_or_basis"]
    mass = 0.0
    for l in bom:
        u = [piece_price(l, i, BASE) for i in range(3)]
        tl = [l["tool"] * TOOL_SCALE[l["tscale"]][i] for i in range(3)]
        mass += l["kg"] * l["qty"]
        rows.append(["BOM", l["group"], l["item"], l["qty"], l["mb"], l["kg"], l["basis"]] + [round(x, 2) for x in u] +
                    [round(x * l["qty"], 2) for x in u] + [round(x) for x in tl] + [(l["src"] + " " + l["notes"]).strip()])
    def sec(section, item, vals, label="calc", basis=""):
        rows.append([section, "", item, "", "", "", label, "", "", "", round(vals[100], 2), round(vals[1000], 2), round(vals[10000], 2), "", "", "", basis])
    sec("SUMMARY", "Cells (incl. in material)", {v: base[v]["cells"] for v in VOLS})
    sec("SUMMARY", "Made parts (material + process)", {v: base[v]["made"] for v in VOLS})
    sec("SUMMARY", "Purchased parts", {v: base[v]["purchased"] for v in VOLS})
    sec("SUMMARY", "MATERIAL SUBTOTAL", {v: base[v]["material"] for v in VOLS})
    sec("CONVERSION", "Pack assembly labour", {v: base[v]["pack_labour"] for v in VOLS}, "est", f"{BAT_HOURS} h x {BASE['labour_rate']} USD/h")
    sec("CONVERSION", "Bike assembly labour", {v: base[v]["bike_labour"] for v in VOLS}, "est", f"{BIKE_HOURS} h x {BASE['labour_rate']} USD/h")
    sec("CONVERSION", "Plant overhead on labour (60%)", {v: base[v]["overhead"] for v in VOLS}, "est")
    sec("CONVERSION", "End-of-line test (labour + energy)", {v: base[v]["eol"] for v in VOLS}, "est", f"{EOL_HOURS} h at 1.2x rate")
    sec("CONVERSION", "Cell screening and pack end-of-line test", {v: base[v]["qc"] for v in VOLS}, "est")
    sec("CONVERSION", "Inbound logistics, duty, handling", {v: base[v]["logistics"] for v in VOLS}, "est", f"{LOGISTICS} of purchased+cells")
    sec("CONVERSION", "Scrap and yield loss", {v: base[v]["scrap"] for v in VOLS}, "est", f"made {SCRAP_MADE}, cells {SCRAP_CELL}")
    sec("CONVERSION", "Warranty reserve", {v: base[v]["warranty"] for v in VOLS}, "est", f"{WARRANTY} of material")
    sec("CONVERSION", f"Tooling and capital amortised over {AMORT_YEARS} yr of volume", {v: base[v]["tooling_amort"] for v in VOLS}, "calc")
    sec("TOTAL", "UNIT COST (ex-works, incl. amortised tooling, excl. NRE)", {v: base[v]["total"] for v in VOLS})
    sec("TOTAL", "Target T9 at 10k", {100: 0, 1000: 0, 10000: 32000}, "target")
    sec("TOOLING", "One-off tooling and capital total (parts tooling + 3 lines)", {v: base[v]["tooling_total"] for v in VOLS}, "est")
    for k in ("ENGINEERING", "SPECIALISTS", "PROTOTYPES", "CELL_LIFE", "COMPLIANCE"):
        sec("NRE", f"{k.title()} (reused from startup-costs.csv base; not re-derived)", {v: nre[v][k] for v in VOLS}, "est")
    sec("NRE", "NRE total", nre_tot)
    sec("NRE", "NRE per bike over 5 yr of volume (information, not in unit cost)", {v: nre_tot[v] / (AMORT_YEARS * v) for v in VOLS}, "calc")
    for k, r in sens.items():
        sec("SENSITIVITY", "Unit cost: " + k, {v: r[v]["total"] for v in VOLS})
    for k, d in levers:
        rows.append(["LEVER", "", k, "", "", "", "calc", "", "", "", "", "", round(d), "", "", "", "saving per bike at 10k"])
    with open(os.path.join(DATA, "cost-model-v1.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    out = dict(base={str(v): base[v] for v in VOLS}, sens={k: {str(v): r[v]["total"] for v in VOLS} for k, r in sens.items()},
               levers=levers, nre_total={str(v): nre_tot[v] for v in VOLS}, bom_mass_kg=mass)
    with open(os.path.join(DATA, "cost-model-v1.json"), "w") as f:
        json.dump(out, f, indent=1)
    # console
    print("BOM mass kg (sum of lines):", round(mass, 1))
    for v in VOLS:
        b = base[v]
        print(v, {k: round(x) for k, x in b.items()})
    for k, r in sens.items():
        print(k, [round(r[v]["total"]) for v in VOLS])
    for k, d in levers:
        print("LEVER", k, round(d))
    print("NRE", nre_tot)
    # group subtotals at 10k
    g = {}
    for l in bom:
        for i, v in enumerate(VOLS):
            g.setdefault(l["group"], [0, 0, 0])[i] += piece_price(l, i, BASE) * l["qty"]
    for k, x in g.items():
        print("GROUP", k, [round(y) for y in x])


if __name__ == "__main__":
    main()
