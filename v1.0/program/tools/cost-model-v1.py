"""Bavuso V1 unit-cost model, keyed to the final BOM (program/data/bom-v1-indented.csv), at 100 / 1,000 / 10,000 bikes per year.

Run from v1.0:  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/cost-model-v1.py
Writes program/data/cost-model-v1.csv and program/data/cost-model-v1.json

Every level-3 BOM part number must be priced exactly once (the script stops otherwise), and the mass of each cost line
is taken from the BOM, so cost and BOM reconcile. Labels: est = my estimate (no supplier contacted); calc = computed here.
Price = piece price at 10k bikes/yr times a curve multiplier for 100 and 1k. Tooling is separate and amortised.
"""
import csv, json, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
BOM_CSV = os.path.join(DATA, "bom-v1-indented.csv")
VOLS = [100, 1000, 10000]
AMORT_YEARS = 5

CURVE = {                       # multiplier on the 10k piece price at (100, 1k, 10k)
    "oe": (1.55, 1.20, 1.0), "oe_prem": (1.70, 1.30, 1.0), "elec": (2.00, 1.35, 1.0), "gen": (1.30, 1.10, 1.0),
    "mach": (1.90, 1.30, 1.0), "body": (3.20, 1.50, 1.0), "carbon": (2.10, 1.45, 1.0), "flat": (1.0, 1.0, 1.0),
}
TOOL_SCALE = {"mach": (0.30, 0.60, 1.0), "body": (0.25, 0.60, 1.0), "none": (0, 0, 0)}

BASE = dict(
    cell_usd=(6.00, 4.80, 3.80),          # per P60B cell
    motor_usd=(6800.0, 5520.0, 4800.0),   # EMRAX 228 LV, low-volume supplier
    inv_usd=(5500.0, 4000.0, 3200.0),     # Cascadia CM200DX, low-volume supplier
    wheel_usd=(4410.0, 3045.0, 2100.0),   # carbon wheel set, OEM price estimate
    labour_rate=45.0,
    overhead_on_labour=0.60,
)
BAT_HOURS = (18.0, 7.0, 2.4)
BIKE_HOURS = (38.0, 16.0, 7.5)
EOL_HOURS = (2.0, 1.0, 0.5)
EOL_ENERGY = 1.0
CELL_QC = (120.0, 70.0, 40.0)
WARRANTY = (0.040, 0.032, 0.028)
LOGISTICS = (0.040, 0.030, 0.025)
SCRAP_MADE = (0.04, 0.03, 0.02)
SCRAP_CELL = (0.015, 0.010, 0.007)
EXTRA_TOOLING = {"Pack assembly line (wire bonder, fixtures, leak/HV test)": (250e3, 900e3, 3.0e6),
                 "Vehicle assembly line, jigs and fixtures": (150e3, 800e3, 3.5e6),
                 "End-of-line rig (dyno, brake, charge, HV safety)": (150e3, 500e3, 1.4e6)}


def load_bom():
    leaves = {}
    for r in csv.DictReader(open(BOM_CSV, encoding="utf-8-sig")):
        if r["level"] != "3":
            continue
        pn = r["part_number"]
        m = float(r["mass_ext_kg"] or 0)
        if pn in leaves and leaves[pn]["kg"] >= m:   # BV-ENG-0102 appears twice; the 0 kg provisional row is skipped
            continue
        leaves[pn] = dict(pn=pn, desc=r["description"], kg=m, mp=r["material_process"], mb=r["make_buy"])
    total = sum(float(r["mass_ext_kg"] or 0) for r in csv.DictReader(open(BOM_CSV, encoding="utf-8-sig")) if r["level"] == "0")
    return leaves, total


def mk(pns, item, p10k, curve, basis, src="", tool=0.0, tscale="none", mb="buy", notes="", qty=1, kg=None):
    return dict(pns=pns, item=item, qty=qty, kg=kg, p10k=p10k, curve=curve, basis=basis, src=src,
                tool=tool, tscale=tscale, mb=mb, notes=notes)


def metal_part(mass, usd_kg, bty, proc10k):
    return mass * usd_kg * bty + proc10k


def N(prefix, nums):
    return [f"BV-{prefix}-{n:04d}" for n in nums]


def build_bom():
    leaves, total_mass = load_bom()
    L = []
    A = L.append
    # ---------------- PACK
    A(mk(N("ENG", [2, 3, 4, 5]), "Molicel INR-21700-P60B cells, 100s11p (1,100)", 1.0, "cells", "est",
         "https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P60B_80145.pdf; B2B listings 3.35-8.00 USD/cell; P50B retail 7.50 at 1000",
         qty=1100, notes="piece price from cell_usd curve"))
    A(mk(N("ENG", [1, 101, 8, 9, 10, 11]), "Pack case: 3 mm Al tub, 5 mm front wall, lid, pads", metal_part(7.9, 4.6, 1.55, 165.0), "mach", "est",
         "09-structures.md; sheet 4.6 USD/kg x 1.55 buy-to-fly + 165 USD cut/form/weld/leak test", tool=350000, tscale="mach", mb="make"))
    A(mk(N("ENG", [6]), "Pack internals electrical: busbars, bonds, fuse collectors, tap harness, MSD", 680.0, "elec", "est",
         "elec-bom.csv busbar 300 + sense harness 100 + MSD 60 at 10k, scaled up for 2,200 wire bonds"))
    A(mk(N("ENG", [7]), "Pack internals thermal: ribbons, manifolds, gap filler, fire barrier (7.25 kg)", 386.0, "elec", "est", "prior 330 USD at 6.2 kg, scaled by mass"))
    A(mk(N("ENG", [102]), "Cell holders, PA66-GF30 plates, 4 modules (3.1 kg)", 42.0, "body", "est",
         "3.1 kg x 4.5 USD/kg + moulding; 19 mm apertures x 1,100", tool=120000, tscale="body", mb="make", notes="2 large multi-cavity tools"))
    A(mk(N("ELC", [18]), "BMS Orion BMS2 + thermistor module", 570.0, "elec", "est", "https://www.orionbms.com/downloads/documents/orionbms2_specifications.pdf; retail 700+250"))
    # ---------------- DRIVE
    A(mk(N("DRV", [1]), "EMRAX 228 axial-flux motor, LV+43% winding, liquid cooled", 1.0, "motor", "est",
         "No published price; shortlist estimate 7,500 USD; low-volume supplier", notes="piece price from motor_usd curve"))
    A(mk(N("DRV", [2]), "Cascadia CM200DX inverter", 1.0, "inv", "est",
         "https://www.fuel2electric.com/cascadia-motion-cm200-inverter (CM200 retail 7,202 USD, one unit)", notes="piece price from inv_usd curve"))
    A(mk(N("DRV", [6]), "Rear pulley 126T 8M, lightened, anodised (2.3 kg)", metal_part(2.3, 7.0, 1.9, 40.0), "mach", "est", "6082 bar + CNC", tool=15000, tscale="mach", mb="make"))
    A(mk(N("DRV", [4]), "Motor pulley 35T 8M", metal_part(0.5, 7.0, 2.0, 14.0), "mach", "est", "", mb="make"))
    A(mk(N("DRV", [3]), "Gates Poly Chain GT Carbon 8MGT-1760 belt", 110.0, "oe", "est", "gates.com; OEM price estimate"))
    A(mk(N("DRV", [7]), "Motor pulley bearing carrier, machined Al", 35.0, "mach", "est", "", tool=12000, tscale="mach", mb="make"))
    # ---------------- CHASSIS
    tubes = [pn for pn, l in leaves.items() if pn.startswith("BV-CHS") and l["mp"].startswith("25CrMo4")]
    A(mk(tubes, "Welded 25CrMo4 frame + load-bearing steel pivot yoke (tube, jig-welded, stress relieved, coated)", 0.0, "frame", "est",
         "09-structures.md; tube 9 USD/kg x 1.15-1.30, weld hours scaled by kg (14 / 9 / 5.5 h per 22 kg), coat/heat treat/stub machining",
         tool=1000000, tscale="mach", mb="make"))
    A(mk(N("CHS", [44, 45, 46, 47]), "Cast steel frame nodes (4 in BOM, mass booked inside the tubes)", 128.0, "mach", "est",
         "investment-cast steel, ~32 USD each at 10k incl. machining", tool=60000, tscale="mach", mb="make"))
    A(mk(N("CHS", [50]), "Pack mounting pads and arm boss/end plates (1.3 kg), machined", 95.0, "mach", "est", "", mb="make"))
    A(mk(N("CHS", [32]), "Nose subframe and headlamp brackets", 35.0, "mach", "est", "", mb="make"))
    A(mk(N("CHS", [21]), "Cast A356-T6 single-sided swingarm, machined", 92.0, "arm", "est",
         "LP die cast + T6 + CNC + X-ray sampling at 10k; sand cast at 100/yr", tool=210000, tscale="mach", mb="make"))
    A(mk(N("CHS", [51]), "Swingarm hub carrier (cast A356) with 2 wheel bearings", 62.0, "mach", "est", "cast + machined + bearings", tool=80000, tscale="mach", mb="make"))
    A(mk(N("CHS", [27]), "Swingarm shock tower, plate", 22.0, "mach", "est", "", mb="make"))
    A(mk(N("CHS", [23]), "Swingarm cross brace (cast boss and rib)", 28.0, "mach", "est", "09-structures.md: unreinforced bolt-on fails", mb="make"))
    A(mk(N("CHS", [33]), "Swingarm pivot bolt and hardware", 30.0, "gen", "est", ""))
    A(mk(N("CHS", [48, 49]), "Pivot bearings, 2 x 32012 tapered roller + seals", 96.0, "oe", "est", "SKF/Timken class; 32012 about 38 USD OEM each"))
    A(mk(N("PRO", [9, 10, 11, 12, 13, 14, 15, 16]), "Crash guard sliders and mounts, 25CrMo4", 75.0, "mach", "est", "", mb="make"))
    A(mk(N("PRO", [4, 8]), "Handguards (pair), 6082 bent tube", 46.0, "mach", "est", "", mb="make"))
    A(mk(N("PRO", [3, 7]), "Pivot sliders", 12.0, "gen", "est", ""))
    # ---------------- RUNNING GEAR
    A(mk(N("RUN", range(36, 44)), "43 mm USD fork, 170 mm, cartridge damping", 950.0, "oe_prem", "est", "Ohlins FGRT 301 retail EUR 3,975; OE ~25%"))
    A(mk(N("RUN", range(44, 50)), "Rear shock, Ohlins STX 46 class, remote reservoir", 520.0, "oe_prem", "est", "https://www.ohlins.eu/en/products/motorcycle/kt-122--4458/ retail EUR 869"))
    A(mk(N("RUN", [69, 70]), "Carbon composite wheels 19x3.00 / 17x4.50 (BST class), with bearings", 1.0, "wheels", "est",
         "BST-class set about 4,500 USD retail (+2.7k over forged, per coordinator); OEM estimate 2,100 at 10k (~47% of retail)", notes="piece price from wheel_usd curve"))
    A(mk(N("RUN", [52, 53]), "Tyres 110/80R19 + 150/70R17", 175.0, "oe", "est", "shortlist 260 retail pair"))
    A(mk(N("RUN", [54, 55]), "Front discs 320x5 floating (pair)", 150.0, "oe_prem", "est", "OE ~75 each"))
    A(mk(N("RUN", [58, 59]), "Brembo Stylema 220D02010 calipers (pair)", 460.0, "oe_prem", "est", "https://www.bremboparts.com/africa/en/catalogue-bike/caliper/220D02010; retail ~450 each, OE est 230"))
    A(mk(N("RUN", [56, 57]), "Front disc carriers (pair), machined Al", 56.0, "mach", "est", "", mb="make"))
    A(mk(N("RUN", [60]), "Rear disc 245x5", 28.0, "oe", "est", ""))
    A(mk(N("RUN", [61, 62, 63]), "Rear caliper P34 class, bracket, carrier", 85.0, "oe", "est", ""))
    A(mk(N("RUN", [64]), "Bosch ABS 10-class two-channel + sensors", 175.0, "oe_prem", "est", "shortlist 120 est; sensors added"))
    A(mk(N("RUN", [65]), "Rear brake pedal and master cylinder", 95.0, "oe", "est", ""))
    A(mk(N("RUN", [20, 21, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33]), "Front master cylinder (19RCS class), reservoir, hoses, banjos, splitters", 200.0, "oe", "est",
         "https://www.motosport.com/brembo-19rcs-brake-master-cylinder retail 553-689; OE est 140"))
    A(mk(N("RUN", [71]), "Steering damper, semi-active", 320.0, "oe_prem", "est", "Ohlins steering damper retail ~600 USD; electronic valve adds cost"))
    A(mk(N("RUN", [1]), "Lower triple clamp, forged + machined", 60.0, "mach", "est", "", tool=30000, tscale="mach", mb="make"))
    A(mk(N("RUN", [2]), "Upper triple clamp, forged + machined", 40.0, "mach", "est", "", tool=25000, tscale="mach", mb="make"))
    A(mk(N("RUN", [68]), "Steering bearings, stem nut", 28.0, "gen", "est", ""))
    A(mk(N("RUN", [66, 67]), "Axles, spacers, adjusters", 53.0, "gen", "est", ""))
    A(mk(N("RUN", [10, 16]), "Hand levers (pair)", 60.0, "oe", "est", ""))
    A(mk(N("RUN", [3, 4]), "Bar risers (pair)", 36.0, "gen", "est", ""))
    A(mk(N("RUN", [5, 11]), "Bar halves (pair)", 60.0, "gen", "est", ""))
    A(mk(N("RUN", [6, 12]), "Grips (pair)", 18.0, "gen", "est", ""))
    A(mk(N("RUN", [19, 28]), "Switch cubes (pair)", 76.0, "elec", "est", ""))
    A(mk(N("RUN", [18, 27]), "Lever perches (pair)", 16.0, "gen", "est", ""))
    A(mk(N("RUN", [35]), "Side stand", 26.0, "gen", "est", ""))
    A(mk(N("RUN", [9, 15]), "Peg brackets (pair)", 44.0, "mach", "est", "", mb="make"))
    A(mk(N("RUN", [7, 13]), "Pegs (pair)", 20.0, "gen", "est", ""))
    A(mk(N("RUN", [8, 14]), "Peg rubbers (pair)", 6.0, "gen", "est", ""))
    # ---------------- ELECTRONICS (elec-bom.csv 10k x 1.15 unless noted)
    A(mk(N("ELC", [16]), "BROGEN PV1776 6.6 kW onboard charger", 700.0, "elec", "est", "shortlist ALT 900 USD est; the BOM carries the 6.6 kW unit (3.3 kW class is about 550)"))
    A(mk(N("ELC", [23]), "NACS inlet (Volex J3400, 1000 V) + lid", 172.0, "elec", "est", "https://www.volex.com/media/z3rmrwl5/volex-nacs-ev-charging-inlet.pdf; elec-bom 150 x 1.15"))
    A(mk(N("ELC", [24]), "EVCC charge controller (ADVANTICS class)", 172.0, "elec", "est", "elec-bom 150 x 1.15"))
    A(mk(N("ELC", [26]), "VCU, power distribution unit, keyless, telematics, HVIL bonding", 546.0, "elec", "est", "elec-bom 200+150+80+45 x 1.15"))
    A(mk(N("ELC", [1]), "HV cabinet, 2 mm folded Al", 38.0, "mach", "est", "", tool=25000, tscale="mach", mb="make"))
    A(mk(N("ELC", [19, 20, 21, 22]), "HV box: 4 x Gigavac GX14, precharge, pyro fuse, shunt, iso monitor, relays, fuses", 1248.0, "elec", "est",
         "https://www.digikey.fr/en/products/detail/sensata-gigavac-clean-energy/GX14CBB/17867714; elec-bom 10k sum 1,085 x 1.15"))
    A(mk(N("ELC", [17]), "DC-DC 0.8 kW", 172.0, "elec", "est", "elec-bom 150 x 1.15"))
    A(mk(N("ELC", [25]), "12 V LiFePO4 battery", 69.0, "elec", "est", ""))
    A(mk(N("ELC", [2, 3]), "LED headlamp with DRL blade", 138.0, "elec", "est", ""))
    A(mk(N("ELC", [4]), "Tail / brake lamp", 35.0, "elec", "est", ""))
    A(mk(N("ELC", [5, 6, 7, 8]), "Indicators x4", 48.0, "elec", "est", ""))
    A(mk(N("ELC", [10, 11]), "Rear indicator stalks", 8.0, "gen", "est", ""))
    A(mk(N("ELC", [9]), "Plate lamp", 7.0, "gen", "est", ""))
    A(mk(N("ELC", [12, 13, 14]), "TFT dash 6.5 in, glass, mount", 207.0, "elec", "est", "elec-bom 180 x 1.15"))
    A(mk(N("ELC", [15]), "Horn", 9.0, "gen", "est", ""))
    # ---------------- COOLING
    A(mk(N("THM", [3, 5]), "Radiator cores (2)", 84.0, "gen", "est", "10-thermal.md: 2 x 165x128x28 mm"))
    A(mk(N("THM", [4, 6]), "Radiator fans (2)", 40.0, "gen", "est", ""))
    A(mk(N("THM", [1]), "Coolant pump", 48.0, "gen", "est", ""))
    A(mk(N("THM", [8]), "Wax thermostat", 12.0, "gen", "est", ""))
    A(mk(N("THM", [9]), "PTC heater 3 kW", 58.0, "gen", "est", ""))
    A(mk(N("THM", [7]), "Coolant, hoses, clamps, sensors", 75.0, "gen", "est", ""))
    # ---------------- WIRING / FASTENERS
    A(mk(N("ALW", [6]), "HV cables, connectors, conduit (35 mm2 set)", 380.0, "elec", "est", "elec-bom 300 x 1.25"))
    A(mk(N("ALW", [1, 2, 3, 4, 5]), "LV harness incl. connectors, bars and loom", 320.0, "elec", "est", "elec-bom 200 is light for this size"))
    A(mk(N("ALW", [8]), "Fasteners (titanium where visible)", 170.0, "gen", "est", ""))
    A(mk(N("ALW", [7]), "Body brackets and fixings", 55.0, "gen", "est", ""))
    # ---------------- BODY
    def body(pns, item, p, tool=0.0):
        A(mk(pns, item, float(p), "body", "est", "moulded/formed part + paint, my estimate", tool=tool, tscale="body" if tool else "none", mb="make"))
    body(N("BOD", [4]), "Lower body battery covers", 34, 80000)
    body(N("BOD", [3]), "Upper body fairing / tank cover", 48, 120000)
    body(N("BOD", [17]), "Tail side panels", 26, 70000)
    body(N("BOD", [25]), "Rear hugger", 12, 35000)
    body(N("BOD", [24]), "Front fender", 11, 28000)
    body(N("BOD", [20]), "Tail undertray", 11, 25000)
    body(N("BOD", [35, 37, 34, 36]), "Radiator pod shrouds and grilles", 30, 35000)
    body(N("BOD", [23]), "Windscreen, polycarbonate", 26, 45000)
    body(N("BOD", [5, 42, 43, 44, 45]), "Waist ledge plates and seam trims", 12, 15000)
    body(N("BOD", [18]), "Seat, two-level, with cover", 85, 40000)
    body(N("BOD", [22]), "Belly skid plate, Al", 38, 35000)
    for pns, item, pr in [(N("BOD", [21]), "Rear rack", 38), (N("BOD", [32]), "Plate hanger arm", 10), (N("BOD", [33]), "Licence plate", 6),
                          (N("BOD", [19]), "Seat welt", 2), (N("BOD", [38, 39, 40, 1, 2]), "Reflectors", 12), (N("BOD", [7, 8]), "Pivot cover caps", 6),
                          (N("BOD", [28, 31, 26, 29, 27, 30]), "Mirrors (pair)", 58), (N("BOD", [41]), "Paint, decals, rubber, misc", 55)]:
        A(mk(pns, item, float(pr), "gen", "est", ""))
    # ---------------- cost lines with NO BOM line (mass 0, flagged)
    A(mk([], "ALLOWANCE (no BOM line): belt guard and tensioner", 45.0, "gen", "est", "not in bom-v1-indented.csv", kg=0.0))
    A(mk([], "ALLOWANCE (no BOM line): TPMS x2, stand and brake switches, sensors", 46.0, "elec", "est", "elec-bom 'small sensors'; not in the BOM", kg=0.0))
    A(mk([], "ALLOWANCE (no BOM line): consumables, labels, grease, threadlock, brake fluid", 60.0, "gen", "est", "", kg=0.0))
    covered = {}
    for l in L:
        if l["pns"]:
            m = 0.0
            for pn in l["pns"]:
                if pn not in leaves:
                    raise SystemExit("cost line refers to a part number not in the BOM: " + pn)
                if pn in covered:
                    raise SystemExit(f"part number {pn} priced twice")
                covered[pn] = l["item"]
                m += leaves[pn]["kg"]
            l["kg"] = m
    missing = [pn for pn in leaves if pn not in covered]
    if missing:
        raise SystemExit("BOM leaves with no cost line: " + ", ".join(missing))
    bom_sum = sum(l["kg"] for l in L)
    return L, bom_sum, total_mass


def group_of(l):
    if not l["pns"]:
        return "Allowances (no BOM line)"
    pn = l["pns"][0]
    if pn == "BV-ELC-0018":
        return "Pack"
    return {"ENG": "Pack", "DRV": "Drive", "CHS": "Chassis", "PRO": "Chassis", "RUN": "Running gear", "ELC": "Electronics",
            "ALW": "Electronics", "THM": "Cooling", "BOD": "Body"}[pn.split("-")[1]]


def piece_price(line, vi, p):
    c = line["curve"]
    if c == "cells":
        return p["cell_usd"][vi]
    if c == "motor":
        return p["motor_usd"][vi]
    if c == "inv":
        return p["inv_usd"][vi]
    if c == "wheels":
        return p["wheel_usd"][vi]
    if c == "frame":
        m = line["kg"]
        hrs = (14.0, 9.0, 5.5)[vi] * m / 22.0
        return m * 9.0 * (1.30, 1.20, 1.15)[vi] + hrs * 55.0 * (p["labour_rate"] / 45.0) + (200.0, 180.0, 165.0)[vi]
    if c == "arm":
        return (470.0, 150.0, 92.0)[vi]
    return line["p10k"] * CURVE[c][vi]


BOM_LINES, BOM_SUM, LEDGER_TOTAL = build_bom()


def compute(p):
    res = {}
    for vi, v in enumerate(VOLS):
        cells = made = purchased = tool_total = 0.0
        for l in BOM_LINES:
            ext = piece_price(l, vi, p) * l["qty"]
            if l["curve"] == "cells":
                cells += ext
            elif l["mb"] == "make":
                made += ext
            else:
                purchased += ext
            tool_total += l["tool"] * TOOL_SCALE[l["tscale"]][vi]
        for t in EXTRA_TOOLING.values():
            tool_total += t[vi]
        mat = cells + made + purchased
        r = p["labour_rate"]
        pack_lab, bike_lab = BAT_HOURS[vi] * r, BIKE_HOURS[vi] * r
        overhead = (pack_lab + bike_lab) * p["overhead_on_labour"]
        eol = EOL_HOURS[vi] * r * 1.2 + EOL_ENERGY
        qc = CELL_QC[vi]
        logistics = LOGISTICS[vi] * (purchased + cells)
        scrap = SCRAP_MADE[vi] * made + SCRAP_CELL[vi] * cells
        warranty = WARRANTY[vi] * mat
        amort = tool_total / (AMORT_YEARS * v)
        total = mat + pack_lab + bike_lab + overhead + eol + qc + logistics + scrap + warranty + amort
        res[v] = dict(cells=cells, made=made, purchased=purchased, material=mat, pack_labour=pack_lab, bike_labour=bike_lab,
                      overhead=overhead, eol=eol, qc=qc, logistics=logistics, scrap=scrap, warranty=warranty,
                      tooling_total=tool_total, tooling_amort=amort, total=total)
    return res


def variant(**kw):
    p = copy.deepcopy(BASE)
    p.update(kw)
    return p


def main():
    base = compute(BASE)
    c7 = tuple(c * 0.7 for c in BASE["cell_usd"])
    c13 = tuple(c * 1.3 for c in BASE["cell_usd"])
    VM, VI = (5200.0, 3800.0, 2800.0), (3300.0, 2200.0, 1500.0)
    sens = {
        "cells -30%": compute(variant(cell_usd=c7)),
        "cells +30%": compute(variant(cell_usd=c13)),
        "motor+inverter at volume-supplier pricing (10k: motor 2,800 / inverter 1,500)": compute(variant(motor_usd=VM, inv_usd=VI)),
        "stress: cells, motor, inverter stay at 1k-bike prices at 10k": compute(variant(cell_usd=(6.0, 4.8, 4.8), motor_usd=(6800.0, 5520.0, 5520.0), inv_usd=(5500.0, 4000.0, 4000.0))),
        "labour rate 30 USD/h": compute(variant(labour_rate=30.0)),
        "labour rate 65 USD/h": compute(variant(labour_rate=65.0)),
        "forged wheels instead of carbon (10k set 1,050)": compute(variant(wheel_usd=(1785.0, 1365.0, 1050.0))),
        "cells -30% + volume-supplier motor/inverter": compute(variant(cell_usd=c7, motor_usd=VM, inv_usd=VI)),
        "carbon-wheel OEM price +50% (10k 3,150)": compute(variant(wheel_usd=(6615.0, 4568.0, 3150.0))),
    }
    nre = {v: {} for v in VOLS}
    with open(os.path.join(HERE, "..", "..", "startup-costs.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["cost_id"] in ("ENGINEERING", "SPECIALISTS", "PROTOTYPES", "CELL_LIFE", "COMPLIANCE"):
                nre[int(r["annual_volume_scenario"])][r["cost_id"]] = float(r["usd_base"])
    nre_tot = {v: sum(nre[v].values()) for v in VOLS}

    t10 = base[10000]["total"]
    levers = []
    def lev(name, **kw):
        levers.append((name, t10 - compute(variant(**kw))[10000]["total"]))
    lev("Motor 4,800 -> 2,800 USD (volume axial-flux supplier)", motor_usd=(6800, 5520, 2800))
    lev("Inverter 3,200 -> 1,500 USD (automotive inverter at volume)", inv_usd=(5500, 4000, 1500))
    lev("Carbon wheels -> forged (about 1,050 USD set at 10k)", wheel_usd=(1785.0, 1365.0, 1050.0))
    lev("Cells 3.80 -> 3.10 USD (direct supply contract, about 143 USD/kWh)", cell_usd=(6.0, 4.8, 3.10))
    lev("Assembly labour 45 -> 30 USD/h (lower-cost plant location)", labour_rate=30.0)

    hdr = ["section", "group", "part_numbers", "item", "qty", "make_buy", "mass_kg", "label", "unit_usd_100", "unit_usd_1k", "unit_usd_10k",
           "ext_usd_100", "ext_usd_1k", "ext_usd_10k", "tooling_usd_100", "tooling_usd_1k", "tooling_usd_10k", "source_or_basis"]
    rows = []
    gsum = {}
    for l in BOM_LINES:
        u = [piece_price(l, i, BASE) for i in range(3)]
        tl = [l["tool"] * TOOL_SCALE[l["tscale"]][i] for i in range(3)]
        g = group_of(l)
        for i in range(3):
            gsum.setdefault(g, [0, 0, 0])[i] += u[i] * l["qty"]
        rows.append(["BOM", g, " ".join(l["pns"]), l["item"], l["qty"], l["mb"], round(l["kg"], 4), l["basis"]] + [round(x, 2) for x in u] +
                    [round(x * l["qty"], 2) for x in u] + [round(x) for x in tl] + [(l["src"] + " " + l["notes"]).strip()])
    def sec(section, item, vals, label="calc", basis=""):
        rows.append([section, "", "", item, "", "", "", label, "", "", "", round(vals[100], 2), round(vals[1000], 2), round(vals[10000], 2), "", "", "", basis])
    for g, x in gsum.items():
        sec("GROUP", g, dict(zip(VOLS, x)))
    sec("SUMMARY", "Cells (included in material)", {v: base[v]["cells"] for v in VOLS})
    sec("SUMMARY", "Made parts", {v: base[v]["made"] for v in VOLS})
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
    sec("CONVERSION", f"Tooling and capital amortised over {AMORT_YEARS} yr of volume", {v: base[v]["tooling_amort"] for v in VOLS})
    sec("TOTAL", "UNIT COST (ex-works, incl. amortised tooling, excl. NRE)", {v: base[v]["total"] for v in VOLS})
    sec("TOTAL", "Target T9 at 10k", {100: 0, 1000: 0, 10000: 32000}, "target")
    sec("TOOLING", "One-off tooling and capital (parts tooling + 3 lines)", {v: base[v]["tooling_total"] for v in VOLS}, "est")
    for k in ("ENGINEERING", "SPECIALISTS", "PROTOTYPES", "CELL_LIFE", "COMPLIANCE"):
        sec("NRE", f"{k.title()} (reused from startup-costs.csv base; not re-derived)", {v: nre[v][k] for v in VOLS}, "est")
    sec("NRE", "NRE total", nre_tot)
    sec("NRE", "NRE per bike over 5 yr of volume (information, not in unit cost)", {v: nre_tot[v] / (AMORT_YEARS * v) for v in VOLS})
    for k, r in sens.items():
        sec("SENSITIVITY", "Unit cost: " + k, {v: r[v]["total"] for v in VOLS})
    for k, d in levers:
        rows.append(["LEVER", "", "", k, "", "", "", "calc", "", "", "", "", "", round(d), "", "", "", "saving per bike at 10k"])
    with open(os.path.join(DATA, "cost-model-v1.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    out = dict(bom_file="bom-v1-indented.csv", bom_mass_priced_kg=BOM_SUM, bom_mass_ledger_kg=LEDGER_TOTAL,
               base={str(v): base[v] for v in VOLS}, groups={g: x for g, x in gsum.items()},
               sens={k: {str(v): r[v]["total"] for v in VOLS} for k, r in sens.items()},
               levers=levers, nre_total={str(v): nre_tot[v] for v in VOLS})
    with open(os.path.join(DATA, "cost-model-v1.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("priced BOM mass", round(BOM_SUM, 3), "ledger total", round(LEDGER_TOTAL, 3), "cost lines", len(BOM_LINES))
    for v in VOLS:
        print(v, {k: round(x) for k, x in base[v].items()})
    for k, r in sens.items():
        print(k, [round(r[v]["total"]) for v in VOLS])
    for k, d in levers:
        print("LEVER", k, round(d))
    print("NRE", nre_tot)
    for k, x in gsum.items():
        print("GROUP", k, [round(y) for y in x])


if __name__ == "__main__":
    main()
