#!/usr/bin/env python
"""Build the Bavuso V1 design dossier (and the 2-page summary) as HTML, then PDF.

Run from v1.0 with FreeCAD python (one command regenerates everything):
    ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/build-dossier.py
Options:  --no-pdf   write HTML and charts only (skip the Edge PDF step)

Outputs (v1.0/final/): Bavuso-V1-Design-Dossier.html / .pdf, Bavuso-V1-Summary.html / .pdf,
assets/ (charts, image copies). All paths inside the HTML are relative.

Authority for every number: program/00-V1-final-spec.md (checked at the end of the run, see
check_against_spec). Tables read program data files (CSV / JSON) where they exist.

AERO HOOK: the aero section reads program/17-aero.md and program/data/aero/aero-results.json.
If BOTH exist (json keys: cda, range_70_mi, range_77_mi; optional note) the dossier prints those
results; otherwise it prints the "validation in progress" text with the assumed CdA 0.38 and
152.4 / 132.2 mi. Re-run this script when aero finishes; nothing else needs editing
(the T3 verdict row says "see aero section" once results exist; review that wording then).
"""
import csv, json, os, re, shutil, subprocess, sys, html, tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]          # v1.0
PROG = ROOT / "program"
DATA = PROG / "data"
OUT = ROOT / "final"
ASSETS = OUT / "assets"
VIS = ROOT / "visuals"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

STAMP = "Rev E \u00b7 November 22, 2026"
ACCENT = "#B3121F"
INK = "#0B0B0C"
GREY = "#6B7078"
LIGHT = "#D9DBDF"

# ----------------------------------------------------------------------------- facts
# Every number here is copied from program/00-V1-final-spec.md (checked by check_against_spec).
F = dict(
    mass_kg="257.9", mass_lb="569", headroom="2.1", t1_kg="260", t1_lb="573",
    cg="787 mm ahead of the rear axle, 529 mm high", wheelbase="1,490 mm", seat="832 mm",
    kwh_gross="23.76", kwh_usable="21.4", volts="360", pack_kg="108.0",
    peak_kw="124", cont_kw="61.6", z60="4.15", z60_lug="4.44", z60_wet="5.47",
    z100kmh="4.31", z100mph="7.26", r60_100="3.12", top="135", gov="130", p125="43.5",
    chg="21", cost10="29.5", cost1="39.3", cost100="58.0", cost_stress="32.3",
    dvpr="7.04", months="28", cdA="0.38", r70="152.4", r77="132.2", cda_break="0.407",
    ledger_growth="287", ac_time="3.1",
)

NOW_FILES = {}


# ----------------------------------------------------------------------------- data loaders
def read_csv(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_aero():
    """Aero data hook (see module docstring)."""
    p17 = PROG / "17-aero.md"
    res = DATA / "aero" / "aero-results.json"
    A = dict(status="pending", cda=F["cdA"], r70=F["r70"], r77=F["r77"], note=None, body=None)
    if p17.exists() and res.exists():
        try:
            j = json.load(open(res, encoding="utf-8"))
            A.update(status="done", cda="%.3f" % float(j["cda"]), r70="%.1f" % float(j["range_70_mi"]),
                     r77="%.1f" % float(j["range_77_mi"]), note=j.get("note"))
            txt = p17.read_text(encoding="utf-8")
            m = re.search(r"## The plain answer\s*(.+?)(?:\n## |\Z)", txt, re.S)
            A["body"] = m.group(1).strip() if m else None
        except Exception as e:  # fall back to pending rather than print something wrong
            print("aero results unreadable, using pending text:", e)
    return A


AERO = load_aero()
AERO_PENDING_TEXT = ("Aerodynamic validation in progress: range calculated at an assumed CdA of 0.38 m\u00b2")


def esc(s):
    return html.escape(str(s), quote=False)


def md_inline(s):
    """Tiny markdown: **bold**, `code`."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


# ----------------------------------------------------------------------------- charts
def setup_mpl():
    names = {f.name for f in font_manager.fontManager.ttflist}
    fam = "Segoe UI" if "Segoe UI" in names else ("Arial" if "Arial" in names else "DejaVu Sans")
    plt.rcParams.update({
        "font.family": fam, "font.size": 9, "axes.edgecolor": GREY, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#E6E8EB", "grid.linewidth": 0.7, "axes.axisbelow": True,
        "figure.dpi": 100, "savefig.dpi": 220, "savefig.bbox": "tight", "savefig.facecolor": "white",
    })


def save(fig, name):
    p = ASSETS / name
    fig.savefig(p)
    plt.close(fig)
    return "assets/" + name


def chart_target_tradeoff():
    # three anchor points quoted in Gate A and 01-targets.md
    pts = [("Original goal A:\nunder 400 lb", 400, 74, "11 kWh, about 74 mi"),
           ("V1 (chosen)", 569, 131.8, "23.8 kWh, 132 mi (CFD drag)"),
           ("Original goal B:\n200 mi", 631, 200, "32 kWh, 631 lb")]
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.plot([p[1] for p in pts], [p[2] for p in pts], color=LIGHT, lw=2, zorder=1)
    for i, (n, lb, mi, lab) in enumerate(pts):
        c = ACCENT if i == 1 else INK
        ax.scatter([lb], [mi], s=70 if i == 1 else 45, color=c, zorder=3)
        ax.annotate(n.replace("\n", " ") + "\n" + lab, (lb, mi), textcoords="offset points",
                    xytext=(10, -24) if i == 0 else ((12, -34) if i == 1 else (-128, 2)), fontsize=8, color=c)
    ax.axhline(145, color=GREY, lw=0.8, ls="--")
    ax.text(392, 148, "T3 floor 145 mi", fontsize=7.5, color=GREY)
    ax.set_xlabel("Wet bike mass, lb"); ax.set_ylabel("Range at 70 mph, mi")
    ax.set_xlim(380, 660); ax.set_ylim(50, 215)
    return save(fig, "chart-target-tradeoff.png")


def chart_mass_history():
    steps = [("Nov 12\nconcept\nledger", 328.4), ("Nov 21\nreconciled\nledger", 319.6),
             ("Nov 21\nrev C CAD\n(P60B pack)", 255.3), ("Nov 22\nrev D", 246.4),
             ("Nov 22\nrev E", 250.6), ("Nov 22\nmass closed", 252.9),
             ("Nov 22\n+ holders,\nhub carrier", 257.3), ("Nov 22\nfinal", 257.9)]
    fig, ax = plt.subplots(figsize=(6.9, 2.3))
    x = list(range(len(steps)))
    y = [s[1] for s in steps]
    ax.plot(x, y, color=INK, lw=1.6, zorder=2)
    ax.scatter(x, y, color=[ACCENT if i == len(x) - 1 else INK for i in x], s=34, zorder=3)
    for xi, yi in zip(x, y):
        ax.annotate("%.1f" % yi, (xi, yi), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
    # target (T1) as it was re-baselined: 240 -> 255 -> 260
    ax.step([0, 3.5, 5.5, 7.5], [240, 240, 255, 260], where="post", color=GREY, lw=1.1, ls="--")
    ax.step([5.5, 7.5], [255, 260], where="post", color=GREY, lw=1.1, ls="--")
    ax.text(0.05, 233, "mass target T1: 240 kg, re-baselined to 255, then 260 kg", fontsize=7.5, color=GREY)
    ax.set_xticks(x); ax.set_xticklabels([s[0] for s in steps], fontsize=7)
    ax.set_ylabel("Wet mass, kg"); ax.set_ylim(225, 340)
    return save(fig, "chart-mass-history.png")


def chart_mass_groups(before, after):
    labels = list(before.keys())
    fig, ax = plt.subplots(figsize=(6.9, 1.8))
    w = 0.38
    xs = range(len(labels))
    ax.bar([i - w / 2 for i in xs], [before[k] for k in labels], w, color=LIGHT, label="Gate A day-one column")
    ax.bar([i + w / 2 for i in xs], [after[k] for k in labels], w, color=INK, label="Final V1 (ledger)")
    for i, k in enumerate(labels):
        ax.text(i + w / 2, after[k] + 1.2, "%.1f" % after[k], ha="center", fontsize=7)
    ax.set_xticks(list(xs)); ax.set_xticklabels([l.replace(" ", "\n", 1) for l in labels], fontsize=7.5)
    ax.set_ylabel("kg"); ax.legend(frameon=False, fontsize=8)
    return save(fig, "chart-mass-groups.png")


def chart_mass_budget(rows):
    names = [r["budget_group"].replace("Wiring, fasteners, fluids", "Wiring,\nfasteners,\nfluids").replace("Body and protection", "Body and\nprotection")
             .replace("Running gear", "Running\ngear").replace("Battery pack", "Battery\npack") for r in rows]
    bud = [float(r["budget_kg"]) for r in rows]
    raw = [float(r["raw_kg"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.9, 2.9))
    w = 0.38
    xs = list(range(len(names)))
    ax.bar([i - w / 2 for i in xs], bud, w, color=LIGHT, label="Budget (re-set to actuals)")
    ax.bar([i + w / 2 for i in xs], raw, w, color=INK, label="Actual (ledger)")
    ax.set_xticks(xs); ax.set_xticklabels(names, fontsize=7.2)
    ax.set_ylabel("kg"); ax.legend(frameon=False, fontsize=8)
    return save(fig, "chart-mass-budget.png")


def chart_cost_breakdown(groups, vols=("100", "1000", "10000")):
    order = ["Drive", "Pack", "Running gear", "Electronics", "Chassis", "Body", "Cooling", "Allowances (no BOM line)"]
    cols = [INK, ACCENT, "#4A4F57", "#8A8F98", "#B6BAC0", "#D2D5D9", "#E4E6E9", "#F0F1F3"]
    fig, ax = plt.subplots(figsize=(6.9, 2.6))
    labels = ["100 / yr", "1,000 / yr", "10,000 / yr"]
    left = [0, 0, 0]
    for g, c in zip(order, cols):
        vals = [groups[g][i] / 1000.0 for i in range(3)]
        ax.barh(labels, vals, left=left, color=c, label=g.replace(" (no BOM line)", ""), edgecolor="white", lw=0.5)
        left = [a + b for a, b in zip(left, vals)]
    ax.invert_yaxis()
    ax.set_xlabel("Unit cost before labour, overhead, warranty and tooling, $ thousand")
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.28))
    return save(fig, "chart-cost-breakdown.png")


def chart_cost_sens(rows):
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(6.9, 2.9))
    colors = [ACCENT if v > 32000 else INK for v in vals]
    ax.barh(names, [v / 1000.0 for v in vals], color=colors)
    ax.axvline(32.0, color=GREY, ls="--", lw=1); ax.text(32.1, len(names) - 0.55, "T9 $32k", fontsize=7.5, color=GREY)
    for i, v in enumerate(vals):
        ax.text(v / 1000.0 + 0.1, i, "%.1f" % (v / 1000.0), va="center", fontsize=7.5)
    ax.invert_yaxis(); ax.set_xlim(20, 35); ax.set_xlabel("Unit cost at 10,000 / yr, $ thousand")
    ax.tick_params(axis="y", labelsize=7.5)
    return save(fig, "chart-cost-sens.png")


def chart_range_cda():
    pts = [(0.38, 152.4), (0.40, 147.0), (0.41, 143.9), (0.43, 138.8), (0.46, 131.8)]
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=INK, lw=1.6, marker="o", ms=4)
    ax.axhline(145, color=GREY, ls="--", lw=1); ax.text(0.3805, 145.6, "T3 floor: 145 mi", fontsize=7.5, color=GREY)
    ax.axvline(0.407, color=ACCENT, lw=1); ax.text(0.4085, 150.2, "break-even\nCdA about 0.407", fontsize=7.5, color=ACCENT)
    if AERO["status"] == "done":
        ax.scatter([float(AERO["cda"])], [float(AERO["r70"])], color=ACCENT, s=60, zorder=4)
        ax.axvspan(0.43, 0.46, color=ACCENT, alpha=0.08, lw=0); ax.text(0.4315, 151.0, "CFD band\n0.43 to 0.46", fontsize=7.5, color=ACCENT)
        ax.annotate("CFD, finest mesh\nCdA 0.46, 132 mi", (float(AERO["cda"]), float(AERO["r70"])), xytext=(-78, 4), textcoords="offset points",
                    fontsize=8, color=ACCENT)
    else:
        ax.scatter([0.38], [152.4], color=ACCENT, s=60, zorder=4)
        ax.annotate("assumed CdA 0.38\n152.4 mi", (0.38, 152.4), xytext=(14, -4), textcoords="offset points", fontsize=7.5, color=ACCENT)
    ax.set_xlabel("CdA with rider, m\u00b2"); ax.set_ylabel("Range at 70 mph, mi")
    return save(fig, "chart-range-cda.png")


def chart_power_soc():
    soc = [100, 50, 20, 10, 5]
    p25 = [124, 109, 100, 93, 87]
    p5 = [115, 99, 86, 83, 81]
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    ax.plot(soc, p25, color=INK, marker="o", ms=4, lw=1.6, label="25 C pack")
    ax.plot(soc, p5, color=GREY, marker="o", ms=4, lw=1.6, ls="--", label="5 C pack")
    ax.axhline(90, color=ACCENT, lw=1); ax.text(62, 91.5, "T5 floor: 90 kW peak", fontsize=7.5, color=ACCENT)
    ax.invert_xaxis(); ax.set_xlabel("State of charge, %"); ax.set_ylabel("Peak shaft power, kW (350 A DC cap)")
    ax.set_ylim(70, 130); ax.legend(frameon=False, fontsize=8)
    return save(fig, "chart-power-soc.png")


def chart_charge_times():
    items = [("25 C, 2C cell cap (headline)", 21.0), ("35 C (3C-cap model)", 23.0),
             ("-10 C, 3 kW heater", 25.4), ("-10 C, pre-heated on the ride in", 14.0), ("45 C, no chiller", 40.9)]
    fig, ax = plt.subplots(figsize=(5.8, 2.4))
    ax.barh([i[0] for i in items], [i[1] for i in items], color=[ACCENT, INK, INK, INK, GREY])
    ax.axvline(25, color=GREY, ls="--", lw=1); ax.text(25.3, 4.35, "T6 limit 25 min", fontsize=7.5, color=GREY)
    for i, it in enumerate(items):
        ax.text(it[1] + 0.4, i, "%.1f" % it[1], va="center", fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("DC 10-80% charge time, min"); ax.tick_params(axis="y", labelsize=7.5)
    ax.set_xlim(0, 46)
    return save(fig, "chart-charge-times.png")


def chart_dfmea(rows):
    systems = []
    for r in rows:
        if r["system"] not in systems:
            systems.append(r["system"])
    cnt = {s: {"H": 0, "M": 0, "L": 0} for s in systems}
    for r in rows:
        cnt[r["system"]][r["action_priority"]] += 1
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    left = [0] * len(systems)
    for k, c in (("H", ACCENT), ("M", "#8A8F98"), ("L", LIGHT)):
        v = [cnt[s][k] for s in systems]
        ax.barh(systems, v, left=left, color=c, label={"H": "High", "M": "Medium", "L": "Low"}[k])
        left = [a + b for a, b in zip(left, v)]
    ax.invert_yaxis(); ax.set_xlabel("DFMEA rows"); ax.legend(frameon=False, fontsize=8)
    ax.tick_params(axis="y", labelsize=7.5)
    return save(fig, "chart-dfmea.png")


def chart_timeline():
    bars = [("Yoke proof, cell and vent tests", 0, 6), ("Component rigs (gate at week 14)", 6, 30),
            ("Build 3 mules, test packs", 12, 32), ("Prototype tests (UN 38.3 first)", 30, 70),
            ("8 pre-production bikes", 60, 76), ("Confirmation, 30,000 km durability", 70, 112),
            ("US self-certification file", 108, 118)]
    fig, ax = plt.subplots(figsize=(6.9, 2.0))
    for i, (n, a, b) in enumerate(bars):
        ax.barh(i, b - a, left=a, color=ACCENT if i in (0, 3) else INK, height=0.55)
        ax.text(b + 1.5, i, n, va="center", fontsize=7.5)
    ax.invert_yaxis(); ax.set_yticks([]); ax.set_xlim(0, 190)
    ax.set_xlabel("Weeks from go (about 28 months in total)")
    return save(fig, "chart-timeline.png")


# ----------------------------------------------------------------------------- html helpers
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Barlow:wght@400;500;600&family=Michroma&display=block');
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; }
:root { --ink: #0B0B0C; --grey: #6F6B66; --rule: #D8D4CE; --rosso: #B3121F; --paper: #FFFFFF; --warm: #F4F2EF;
  --disp: "Archivo", "Arial Narrow", "Segoe UI", Arial, sans-serif; --label: "Michroma", "Archivo", "Segoe UI", Arial, sans-serif;
  --body: "Barlow", "Segoe UI", Arial, sans-serif; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-family: var(--body); font-weight: 400; color: var(--ink); font-size: 10pt; line-height: 1.42;
  font-variant-numeric: tabular-nums lining-nums;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
b, strong { font-weight: 600; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page; background: #fff; }
.page:last-child { page-break-after: auto; break-after: auto; }
.hd { position: absolute; top: 0.38in; left: 0.75in; right: 0.75in; display: flex; justify-content: space-between;
  font-family: var(--label); font-size: 5.6pt; letter-spacing: 0.24em; text-transform: uppercase; color: var(--grey); border-bottom: 0.5pt solid var(--rule); padding-bottom: 6pt; }
.hd b { color: var(--ink); font-weight: 400; }
.ft { position: absolute; bottom: 0.36in; left: 0.75in; right: 0.75in; display: flex; justify-content: space-between;
  font-size: 7.4pt; color: var(--grey); border-top: 0.5pt solid var(--rule); padding-top: 5pt; letter-spacing: 0.04em; }
.bd { position: absolute; top: 0.78in; bottom: 0.72in; left: 0.75in; right: 0.75in; overflow: hidden; }
h1 { font-family: var(--disp); font-stretch: 118%; font-variation-settings: "wdth" 118; font-size: 20pt; line-height: 1.1; font-weight: 600; letter-spacing: -0.012em; margin: 0 0 6pt 0; }
h1 + .sub { color: var(--grey); margin: 0 0 12pt 0; font-size: 10pt; }
h2 { font-family: var(--label); font-size: 6.3pt; letter-spacing: 0.22em; text-transform: uppercase; color: var(--ink); margin: 14pt 0 6pt 0; font-weight: 400;
  padding-top: 6pt; border-top: 0.5pt solid var(--rule); }
h3 { font-family: var(--disp); font-stretch: 112%; font-size: 10pt; margin: 9pt 0 3pt 0; font-weight: 600; }
p { margin: 0 0 6pt 0; }
code { font-family: Consolas, monospace; font-size: 0.88em; padding: 0; color: #3A3835; }
.lead { font-size: 11.4pt; line-height: 1.45; margin-bottom: 9pt; font-weight: 400; }
.small { font-size: 7.8pt; color: var(--grey); line-height: 1.4; }
.rule { height: 1.2pt; background: var(--rosso); margin: 8pt 0 10pt 0; width: 0.5in; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 3pt 0 8pt 0; }
th { text-align: left; font-weight: 500; font-size: 6.9pt; letter-spacing: 0.12em; text-transform: uppercase; color: var(--grey);
  border-bottom: 0.8pt solid var(--ink); padding: 3pt 5pt 3pt 0; vertical-align: bottom; }
td { border-bottom: 0.4pt solid var(--rule); padding: 3pt 5pt 3pt 0; vertical-align: top; }
td.n, th.n { text-align: right; padding-right: 8pt; font-variant-numeric: tabular-nums; }
tr.tot td { font-weight: 600; border-top: 0.8pt solid var(--ink); border-bottom: none; }
tr.hl td { background: var(--warm); }
.tight td { padding: 2pt 4pt 2pt 0; font-size: 8pt; }
.fig { margin: 4pt 0 8pt 0; page-break-inside: avoid; }
.fig img { display: block; max-width: 100%; }
.fig .cap { font-size: 7.8pt; color: var(--grey); margin-top: 3pt; }
.cols2 { display: flex; gap: 0.25in; font-size: 9pt; line-height: 1.36; } .cols2 > div { flex: 1; min-width: 0; }
.cols3 { display: flex; gap: 0.2in; } .cols3 > div { flex: 1; min-width: 0; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.12in; }
.callout { border-left: 1.4pt solid var(--rosso); padding: 2pt 0 2pt 10pt; margin: 6pt 0 9pt 0; }
.callout.dark { border-left: none; border-top: 0.8pt solid var(--ink); border-bottom: 0.8pt solid var(--ink); padding: 8pt 0; font-size: 10.4pt; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-top: 0.8pt solid var(--ink); margin: 8pt 0 10pt 0; }
.kpi { padding: 8pt 8pt 7pt 0; border-bottom: 0.4pt solid var(--rule); }
.kpi .v { font-family: var(--disp); font-stretch: 118%; font-variation-settings: "wdth" 118; font-size: 17pt; font-weight: 500; letter-spacing: -0.015em; line-height: 1.1; }
.kpi .l { font-family: var(--label); font-size: 5.4pt; color: var(--rosso); letter-spacing: 0.16em; text-transform: uppercase; margin-top: 4pt; }
.kpi .s { font-size: 7.6pt; color: var(--grey); margin-top: 1pt; }
.pill { display: inline-block; padding: 0 5pt; border-radius: 1.5pt; font-size: 7pt; font-weight: 500; white-space: nowrap; letter-spacing: 0.02em; border: 0.6pt solid var(--ink); color: var(--ink); }
.pill.met { border-color: var(--ink); } .pill.thin { border-color: #9A958E; color: #4A4742; }
.pill.nv { border-color: var(--rule); color: var(--grey); } .pill.no { border-color: var(--rosso); color: var(--rosso); }
.tag { font-size: 6.8pt; letter-spacing: 0.06em; text-transform: uppercase; color: var(--grey); white-space: nowrap; }
ul { margin: 2pt 0 6pt 14pt; padding: 0; } li { margin: 0 0 2.5pt 0; }
.cover { background: #0B0B0C; color: #fff; }
.cover .heroband { position: absolute; top: 0; left: 0; right: 0; height: 6.8in; background: #ECECEE; overflow: hidden; }
.cover .heroband img { position: absolute; left: -1.1in; top: -0.3in; width: 11.4in; }
.cover .mark { position: absolute; left: 0.75in; top: 0.55in; font-family: var(--label); font-size: 9pt; letter-spacing: 0.5em; color: #0B0B0C; }
.cover .txt { position: absolute; left: 0.75in; right: 0.75in; top: 7.25in; }
.cover .wm { font-family: var(--label); font-size: 31pt; letter-spacing: 0.26em; color: #fff; margin: 0 0 10pt 0; font-weight: 400; line-height: 1.1; }
.cover .eyebrow { font-family: var(--label); font-size: 6.4pt; letter-spacing: 0.3em; text-transform: uppercase; color: #fff; margin-bottom: 14pt; padding-top: 10pt; border-top: 1.2pt solid var(--rosso); display: inline-block; }
.cover h1 { font-size: 15pt; line-height: 1.2; font-weight: 500; letter-spacing: 0; color: #E6E3DE; margin: 0 0 8pt 0; }
.cover .rev { font-size: 9.5pt; color: #9A958E; margin-bottom: 12pt; }
.cover .foot { position: absolute; left: 0.75in; right: 0.75in; bottom: 0.5in; font-size: 7.6pt; color: #8A857F; border-top: 0.5pt solid #34322F; padding-top: 7pt; display: flex; justify-content: space-between; }
.toc td { padding: 4pt 0; font-size: 9.4pt; } .toc td.p { text-align: right; color: var(--grey); width: 0.5in; }
.toc td.num { color: var(--rosso); width: 0.45in; font-weight: 500; }
.sheetimg { border: 0.5pt solid var(--rule); width: 100%; display: block; }
.mono { font-variant-numeric: tabular-nums; }
.twoimg img { width: 100%; display: block; }
.stamp { font-family: var(--label); font-size: 5.6pt; letter-spacing: 0.24em; text-transform: uppercase; color: var(--rosso); margin-bottom: 5pt; }
"""

CHECK_JS = r"""
<script>
window.addEventListener('load', function(){
  var rep=[]; document.querySelectorAll('.page').forEach(function(p,i){
    var b=p.querySelector('.bd'); if(b && b.scrollHeight>b.clientHeight+1){rep.push('OVERFLOW page '+(i+1)+' by '+(b.scrollHeight-b.clientHeight)+'px');}
  });
  var el=document.createElement('pre'); el.id='layout-report'; el.style.display='none'; el.textContent='LAYOUT:'+(rep.length?rep.join(' | '):'OK'); document.body.appendChild(el);
  var h=(location.hash||'').match(/p=(\d+)-(\d+)/);
  if(h){document.querySelectorAll('.page').forEach(function(p,i){ if(i+1<+h[1]||i+1>+h[2]) p.style.display='none'; });}
});
</script>
"""


class Doc:
    def __init__(self, title, label="Design Dossier"):
        self.title = title
        self.label = label
        self.pages = []      # dicts: section, title, html, toc

    def add(self, section, title, body_html, toc=False, num=None, toc_title=None):
        self.pages.append(dict(section=section, title=title, html=body_html, toc=toc, num=num, toc_title=toc_title))

    def render(self, cover_html=None, toc_builder=None):
        parts = []
        for i, pg in enumerate(self.pages, start=1):
            if pg.get("raw"):
                parts.append(pg["html"])
                continue
            parts.append(
                '<section class="page"><div class="hd"><span><b>Bavuso V1</b> &nbsp;%s</span><span>%s</span></div>'
                '<div class="bd">%s</div><div class="ft"><span>Bavuso Motors &middot; %s</span><span>%d</span></div></section>'
                % (esc(self.label), ("" if pg["section"].lower() == self.label.lower() else esc(pg["section"])), pg["html"], STAMP, i))
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s%s</body></html>'
                % (esc(self.title), CSS, "\n".join(parts), CHECK_JS))


def table(headers, rows, cls="", num_cols=(), widths=None, total_last=False, hl_rows=()):
    h = "<table class=\"%s\">" % cls
    if widths:
        h += "<colgroup>" + "".join('<col style="width:%s">' % w for w in widths) + "</colgroup>"
    h += "<thead><tr>" + "".join('<th class="%s">%s</th>' % ("n" if i in num_cols else "", esc(c)) for i, c in enumerate(headers)) + "</tr></thead><tbody>"
    for ri, r in enumerate(rows):
        c = ""
        if total_last and ri == len(rows) - 1:
            c = "tot"
        elif ri in hl_rows:
            c = "hl"
        h += '<tr class="%s">' % c + "".join(
            '<td class="%s">%s</td>' % ("n" if i in num_cols else "", v if isinstance(v, Raw) else md_inline(v))
            for i, v in enumerate(r)) + "</tr>"
    return h + "</tbody></table>"


class Raw(str):
    pass


def fig(src, cap, width=None, cls=""):
    st = ' style="width:%s"' % width if width else ""
    return '<div class="fig %s"><img src="%s"%s><div class="cap">%s</div></div>' % (cls, src, st, md_inline(cap))


def pill(verdict):
    cls = {"met": "met", "met-thin": "thin", "not met": "no", "not verified": "nv"}.get(verdict.lower(), "nv")
    return Raw('<span class="pill %s">%s</span>' % (cls, esc(verdict.capitalize() if verdict.lower() != "met-thin" else "Met, thin")))


def kpis(items):
    return '<div class="kpis">' + "".join(
        '<div class="kpi"><div class="v">%s</div><div class="l">%s</div><div class="s">%s</div></div>' % (v, l, s) for v, l, s in items) + "</div>"


def h2(t):
    return "<h2>%s</h2>" % esc(t)


def p(t, cls=""):
    return '<p class="%s">%s</p>' % (cls, md_inline(t))


def ul(items):
    return "<ul>" + "".join("<li>%s</li>" % md_inline(i) for i in items) + "</ul>"


def callout(t, dark=False):
    return '<div class="callout %s">%s</div>' % ("dark" if dark else "", md_inline(t))


def title(num, t, sub=None):
    s = '<div class="stamp">%s</div>' % esc(num) if num else ""
    return s + "<h1>%s</h1>" % esc(t) + ('<div class="sub">%s</div>' % md_inline(sub) if sub else "")


# ----------------------------------------------------------------------------- image prep
def crop_render(im, aspect=1.55, pad=0.07):
    """Crop a render to the dark / grey subject plus padding, at a fixed aspect ratio."""
    g = im.convert("L").point(lambda v: 255 if v < 178 else 0)
    bb = g.getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    x0 -= w * pad; x1 += w * pad; y0 -= h * pad; y1 += h * pad
    w, h = x1 - x0, y1 - y0
    if w / h < aspect:
        nw = h * aspect; x0 -= (nw - w) / 2; x1 = x0 + nw
    else:
        nh = w / aspect; y0 -= (nh - h) / 2; y1 = y0 + nh
    W, H = im.size
    if x0 < 0: x1 -= x0; x0 = 0
    if y0 < 0: y1 -= y0; y0 = 0
    if x1 > W: x0 -= x1 - W; x1 = W
    if y1 > H: y0 -= y1 - H; y1 = H
    return im.crop((int(max(0, x0)), int(max(0, y0)), int(min(W, x1)), int(min(H, y1))))


def prep_images():
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "drawings").mkdir(exist_ok=True)
    out = {}
    for key, name in [("hero", "cycles-adventure-hero"), ("side", "cycles-adventure-side"),
                      ("front34", "cycles-adventure-front34"), ("rear34", "cycles-adventure-rear34"),
                      ("rider", "cycles-adventure-rider-side"), ("riderhero", "cycles-adventure-rider-hero")]:
        src = VIS / (name + ".png")
        dst = ASSETS / (name + ".jpg")
        if src.exists():
            im = Image.open(src)
            if im.mode == "RGBA":
                bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
            im = im.convert("RGB")
            if key != "hero":
                im = crop_render(im)
            im.save(dst, quality=90)
            out[key] = "assets/" + dst.name
            if key == "hero":
                bot = im.crop((0, im.size[1] - 4, im.size[0], im.size[1])).resize((1, 1)).getpixel((0, 0))
                out["hero_bg"] = "#%02x%02x%02x" % bot
    for src, dst in [(DATA / "target-sweep.png", "target-sweep.png"),
                     (DATA / "elec-hv-single-line.svg", "elec-hv-single-line.svg"),
                     (DATA / "elec-lv-can.svg", "elec-lv-can.svg"),
                     (DATA / "elec-dc-session.svg", "elec-dc-session.svg"),
                     (DATA / "dynamics" / "damper-schedule.png", "dyn-damper-schedule.png"),
                     (DATA / "dynamics" / "stability-baseline.png", "dyn-stability-baseline.png"),
                     (DATA / "dynamics" / "gust-response.png", "dyn-gust-response.png"),
                     (DATA / "dynamics" / "braking-thermal.png", "dyn-braking-thermal.png")]:
        if src.exists():
            shutil.copy2(src, ASSETS / dst)
            out[dst] = "assets/" + dst
    return out


# ----------------------------------------------------------------------------- page content
def build(doc_imgs):
    I = doc_imgs
    budget = read_csv(DATA / "mass-budget-report.csv")          # quoted "Wiring, fasteners, fluids" handled by csv module
    mass_rows = [r for r in budget if r["budget_group"] != "TOTAL"]
    mass_tot = [r for r in budget if r["budget_group"] == "TOTAL"][0]
    cost = json.load(open(DATA / "cost-model-v1.json", encoding="utf-8"))
    dfmea = read_csv(DATA / "dfmea-v1.csv")
    dvpr = read_csv(DATA / "dvpr-v1.csv")
    bom = read_csv(DATA / "bom-v1-indented.csv")
    rollup = json.load(open(ROOT / "mass-rollup.json", encoding="utf-8"))
    assert abs(rollup["total_kg"] - float(F["mass_kg"])) < 0.05, "mass-rollup.json no longer 257.9"

    D = Doc("Bavuso V1: Electric Adventure-Touring Motorcycle, Design Dossier")

    # ---------------- cover
    cover = ('<section class="page cover" data-cover="1"><div class="heroband" style="background:%s"><img src="%s"></div>'
             '<div class="txt"><div class="wm">BAVUSO</div><div class="eyebrow">V1 Design Dossier</div>'
             '<h1>Electric adventure-touring motorcycle</h1>'
             '<div class="rev">Rev E design freeze, November 2026</div>'
             '<div style="font-size:9pt;color:#B9B4AD;max-width:5.6in">A paper design for a solo bike: '
             '%s kg (%s lb) wet, a %s kWh pack, native NACS charging. Nothing has been built or physically tested.</div></div>'
             '<div class="foot"><span>%s</span><span>Engineering analysis by AI engineering agents (Claude), directed by the owner</span></div></section>'
             % (I.get("hero_bg", "#ececee"), I.get("hero", ""), F["mass_kg"], F["mass_lb"], "23.8", STAMP))
    D.pages.append(dict(section="", title="Cover", html=cover, toc=False, raw=True))

    # ---------------- placeholder for TOC (page 2)
    D.add("Contents", "Contents", "@@TOC@@")

    # ---------------- executive summary
    aero_line = ("about %s mi at 70 mph, calculated at an assumed CdA of %s" % ("152", "0.38")) if AERO["status"] != "done" else \
        ("about %s mi at 70 mph at a CdA of %s" % (AERO["r70"], AERO["cda"]))
    body = title("01 Executive summary", "A deliberate compromise that can be built")
    body += '<div class="lead">Under 400 lb and 200 miles at 70 mph cannot both close with today\u2019s cells. A 400 lb bike carries about 11 kWh, enough for about 74 miles, and 200 miles needs about 32 kWh and a 631 lb bike. V1 is a <b>deliberate compromise</b> between the two.</div>'
    body += p("I chose a buildable bike: **about 258 kg / 569 lb, a 23.8 kWh pack, about 130 miles at 70 mph, 125 mph sustained and native NACS fast charging.** Range came in under my 145-mile target once the airflow analysis gave a real drag figure, and I say so in section 10. It is a V1 with a planned improvement path (section 11): better cells, lower drag, a lighter chassis and, later, a two-up variant.")
    body += kpis([("%s kg" % F["mass_kg"], "Wet mass, no rider", "%s lb; target at most 260 kg" % F["mass_lb"]),
                  ("%s kWh" % F["kwh_gross"], "Pack energy, gross", "%s kWh usable, %s V, 100s11p" % (F["kwh_usable"], F["volts"])),
                  ("%s mi" % AERO["r70"], "Range at 70 mph", "calculated at CdA %s%s" % (AERO["cda"], " (assumed)" if AERO["status"] != "done" else "")),
                  ("125 mph", "Sustained speed", "%s mph limit, governed at %s" % (F["top"], F["gov"])),
                  ("%s kW" % F["peak_kw"], "Peak motor power", "%s kW continuous" % F["cont_kw"]),
                  ("%s s" % F["z60"], "0-60 mph", "calculated, torque-limited"),
                  ("~%s min" % F["chg"], "DC charge 10-80%", "NACS inlet, 25 C, 2C cell cap"),
                  ("$%sk" % F["cost10"], "Unit cost at 10k / yr", "estimate, no quotes")])
    body += h2("What V1 is")
    body += p("V1 is a solo adventure-touring motorcycle. It has a Molicel P60B 21700 pack (100s11p, 1,100 cells) in a structural aluminium case that forms the lower body, an EMRAX 228 axial-flux motor with a Cascadia CM200DX inverter, and a single 8 mm Gates belt at 3.60:1. The frame is steel tube with cast nodes and a steel pivot yoke, with a cast single-sided swingarm. V1 is level with the Energica Experia (260 kg) and about 4% heavier than the Zero DSR/X (247 kg). It carries about 38% more energy than the DSR/X.")
    body += h2("How far the evidence goes")
    body += p("The design is **coherent and checked on paper**. The parts ledger, the bill of materials and the CAD roll-up agree on %s kg, and structures, thermal, dynamics, drive, electrical and cost models were run on it. **Nothing is built, weighed or tested**, supplier prices are estimates, and several margins are thin (mass headroom %s kg). **One target is missed: the CFD drag area is 0.43 to 0.46 m\u00b2 against the 0.38 the range target assumed, so range at 70 mph is about 132 to 139 mi against 145 (T3).** Sections 10 and 12 give the verdict on each target and the limits." % (F["mass_kg"], F["headroom"]))
    if AERO["status"] != "done":
        body += callout("**" + AERO_PENDING_TEXT + "** (152.4 mi at 70 mph, 132.2 mi at 77 mph). Treat range as a calculation, not a finding.")
    D.add("Executive summary", "Executive summary", body, toc=True, num="01")

    # ---------------- spec sheet
    spec_rows = [
        ("Wet mass, no rider", "%s kg / %s lb (headroom %s kg against T1 of 260 kg)" % (F["mass_kg"], F["mass_lb"], F["headroom"]), "calculated"),
        ("Centre of gravity (bike)", F["cg"], "calculated"),
        ("Wheelbase / seat height", "%s / %s" % (F["wheelbase"], F["seat"]), "measured (CAD)"),
        ("Pack", "Molicel P60B 21700, 100s11p, 1,100 cells, %s kg" % F["pack_kg"], "supplier / estimate"),
        ("Pack energy / voltage", "%s kWh gross, %s kWh usable (5-95%%); %s V nominal (250-420 V)" % (F["kwh_gross"], F["kwh_usable"], F["volts"]), "calculated"),
        ("Motor / inverter", "EMRAX 228 liquid-cooled, LV+43% winding, 220 Nm, 13.2 kg / Cascadia CM200DX, 300 A rms continuous, 6.75 kg", "supplier"),
        ("Peak / continuous power", "%s kW peak (350 A DC cap: 109 / 100 / 93 / 87 kW at 50 / 20 / 10 / 5%% charge, 25 C) / %s kW continuous" % (F["peak_kw"], F["cont_kw"]), "supplier cap / calculated"),
        ("Final drive", "Gates 8MGT-1760-62 belt, 62 mm, 35T / 126T, 3.60:1", "supplier / calculated"),
        ("0-60 mph", "%s s (%s s with 25 kg luggage; %s s on a wet road)" % (F["z60"], F["z60_lug"], F["z60_wet"]), "calculated"),
        ("0-100 km/h / 0-100 mph / 60-100 mph", "%s s / %s s / %s s" % (F["z100kmh"], F["z100mph"], F["r60_100"]), "calculated"),
        ("Top speed", "%s mph limit (6,500 rpm), governed at %s mph; 125 mph needs %s kW at the wheel" % (F["top"], F["gov"], F["p125"]), "calculated"),
        ("CdA", ("%s m\u00b2 assumed (aero pending)" % AERO["cda"]) if AERO["status"] != "done" else "%s m\u00b2 (CFD, finest of three meshes; extrapolated 0.43)" % AERO["cda"], "assumption" if AERO["status"] != "done" else "calculated"),
        ("Range at 70 / 77 mph", "%s / %s mi (flat, still air, 90 kg rider, 25 C). Real-world about 15 to 20%% lower%s" % (AERO["r70"], AERO["r77"], ("; fails T3 above CdA about " + F["cda_break"]) if AERO["status"] != "done" else "; misses T3 (145 mi)"), "calculated"),
        ("DC charging 10-80%", "about %s min at 25 C, 2C cell cap (23.0 min at 35 C, 25.4 min at -10 C with heater, 40.9 min at 45 C)" % F["chg"], "calculated"),
        ("AC charging / NACS", "BROGEN PV1776 6.6 kW (3.1 h for 10-90%); native J3400 inlet, DIN 70121 / ISO 15118 controller. Supercharger access not established", "supplier / design"),
        ("Brakes", "320 x 5 mm front discs, 267 x 5 mm rear disc; front discs 362-375 C in a 125-0 mph stop (limit about 450 C)", "measured (CAD) / calculated"),
        ("Frame / swingarm", "Steel-tube frame, cast steel nodes, steel pivot yoke (cross-member Z545), cast A356 single-sided arm", "measured (CAD)"),
        ("Wheels", "Carbon, 2.6 kg front and 3.3 kg rear", "estimate"),
        ("Steering damper", "Speed-scheduled semi-active, about 0.5 kg", "calculated / estimate"),
        ("Unit cost", "$%sk at 10k/yr; $%sk at 1k; $%sk at 100 ($%sk at 10k if cells, motor and inverter stay at 1k prices)" % (F["cost10"], F["cost1"], F["cost100"], F["cost_stress"]), "estimate"),
        ("Design rider case", "90 kg rider + 25 kg luggage, 1,755 mm (about the adult male average)", "assumption"),
        ("Validation plan", "about $%sM and %s months, all planned" % (F["dvpr"], F["months"]), "estimate"),
    ]
    body = title("02 Specification", "Specification sheet", "Every value is analysis or estimate, and the type column says which. Nothing is measured.")
    body += table(["Quantity", "Value", "Type"], [(a, b, Raw('<span class="tag">%s</span>' % esc(c))) for a, b, c in spec_rows],
                  cls="tight", widths=["24%", "61%", "15%"])
    body += p("Measured means from CAD geometry or a weighed part (no part is weighed). Supplier means a published datasheet or catalogue. Calculated means computed by the program\u2019s scripts or hand checks. Estimate and assumption mean judgement.", "small")
    D.add("Specification", "Specification sheet", body, toc=True, num="02")

    # ---------------- comparison
    comp = [
        ("Wet mass", "%s kg / %s lb" % (F["mass_kg"], F["mass_lb"]), "260 kg / 573 lb", "247 kg / 544 lb", "237 kg / 523 lb (fuelled)"),
        ("Energy (gross)", "%s kWh" % F["kwh_gross"], "22.5 kWh", "17.3 kWh", "Petrol, 19 L"),
        ("Rated range", "about %s mi at 70 mph (calculated)" % AERO["r70"][:3] if False else "%s mi at 70 mph (calculated, assumed CdA)" % AERO["r70"] if AERO["status"] != "done" else "%s mi at 70 mph (calculated)" % AERO["r70"],
         "130 mi at about 68 mph claimed; 120 real", "85 mi at 70 mph claimed; reviewers 70-100", "n/a"),
        ("Peak power", "%s kW" % F["peak_kw"], "not retrieved", "75 kW (100 hp)", "n/a"),
        ("Top speed", "%s mph limit, governed %s" % (F["top"], F["gov"]), "not retrieved", "112 mph", "n/a"),
        ("Charging", "Native NACS (J3400); DC 10-80%% about %s min" % F["chg"], "CCS inlet", "No DC fast charge", "n/a"),
        ("Price", "target MSRP about $45k; unit cost $%sk at 10k/yr" % F["cost10"], "UK GBP 25-28k", "$22,995", "n/a (petrol)"),
        ("Status", "Paper design, nothing built", "On sale", "On sale", "On sale"),
    ]
    body = title("02 Specification", "How V1 compares", "Against the Energica Experia, the Zero DSR/X and a petrol BMW R 1300 GS, the benchmark I named.")
    body += table(["", "Bavuso V1", "Energica Experia", "Zero DSR/X", "BMW R 1300 GS"], comp, cls="", widths=["15%", "27%", "20%", "19%", "19%"])
    body += p("Competitor figures come from published maker pages and independent reviews, summarised in `01-targets.md`. Several sources conflict, and rated ranges are measured at different speeds, so the columns are not like-for-like. V1 figures are calculations.", "small")
    body += h2("Reading the comparison")
    body += ul([
        "**Mass.** V1 is level with the Experia, about 4% (10 kg) heavier than the DSR/X and 44 lb over the petrol GS. It beats none of them on weight. It matches the electric class while carrying more energy.",
        "**Energy.** 23.76 kWh is about 38% more than the DSR/X (17.3 kWh) and about 6% more than the Experia (22.5 kWh).",
        "**Range.** A calculated 132 mi at 70 mph does not compare directly with maker claims. Real-world V1 range should be about 105 to 115 mi.",
        "**Charging.** V1 is designed around a native NACS inlet. The Experia uses CCS and the DSR/X has no DC fast charging. Supercharger network access is not established for V1.",
    ])
    body += h2("Why V1 gives up 400 lb")
    body += p("A 400 lb bike would be about 100 lb lighter than the Zero DSR/X but would carry only 11 kWh, enough for about 74 miles at highway speed. A premium bike should not be out-ranged by a cheaper one. So V1 gives up the 400 lb goal and keeps the range.")
    D.add("Specification", "Comparison", body, toc=False)

    # ---------------- how the design got here: sweep
    c1 = chart_target_tradeoff()
    body = title("03 How the design got here", "One target point from a sweep", "The program swept mass, cell density, drag and range, then picked a single point instead of either extreme.")
    body += p("My brief asked for a bike under 400 lb with 200 miles at 70 mph, 125 mph or more, native NACS charging and comfort in a 77 mph gust. The first job was to test whether those targets can coexist. They cannot with today\u2019s cells (about 230 Wh/kg at pack level).")
    body += ul(["**400 lb** leaves about 140 kg of bike outside the battery, which has room for about 11 kWh. That is roughly 74 miles at 70 mph.",
                "**200 miles** needs about 32 kWh and a 286 kg / 631 lb bike. That is heavier than every electric road bike and petrol adventure bike I benchmarked."])
    body += fig(c1, "Figure 3.1. The two original goals and the chosen V1 point. The anchor values are those quoted in Gate A and `01-targets.md`; the line only joins them.")
    if "target-sweep.png" in I:
        body += fig(I["target-sweep.png"], "Figure 3.2. The target sweep (`program/data/target-sweep.png`): the bike mass needed for a given 70 mph range, for different drag, pack density and rest-of-bike mass.", width="100%")
    body += p("Gate A locked a 23.8 kWh pack, a solo rider and ten targets (T1 to T10, section 10). The mass target started at 240 kg and was re-baselined twice as real parts replaced the first budgets (next page).")
    D.add("How the design got here", "Target sweep", body, toc=True, num="03", toc_title="How the design got here, target and mass")

    # ---------------- how the design got here: mass and decisions
    c2 = chart_mass_history()
    before = {"Pack": 131.1, "Chassis": 34.9, "Running gear": 44.9, "Drive": 23.6, "Electronics": 24.5, "Body": 30.8, "Cooling": 8.6, "Wiring etc.": 27.7}
    after = {"Pack": 108.0, "Chassis": 31.33, "Running gear": 43.23, "Drive": 23.65, "Electronics": 17.44, "Body": 14.45, "Cooling": 6.9, "Wiring etc.": 12.93}
    c3 = chart_mass_groups(before, after)
    body = title("03 How the design got here", "From 328 kg down to 258 kg", "Weight was the main problem. I re-architected the bike, and it grew back a little as real parts were booked.")
    body += fig(c2, "Figure 3.3. Roll-up mass through the program (git history of the ledger and CAD roll-ups). The dashed line is the mass target T1 as it was re-baselined (240, 255, then 260 kg).", width="92%")
    body += fig(c3, "Figure 3.4. Where the weight went, by system. The \u201cday-one\u201d bars are the Gate A table\u2019s \u201ctoday\u201d column (about 320 kg; the groups there sum to a little more because overlaps were removed later). The pack, body panels and wiring gave most of the saving.")
    body += h2("Key decisions from the Gate A log")
    dec = [
        ("Nov 21", "Inverter", "Cascadia CM200DX (6.75 kg) drives the EMRAX 228 LV winding; the lighter emDrive H100 gives only about 29 kW continuous on a 360 V pack. Belt ratio 3.60, 8 mm Gates belt."),
        ("Nov 21", "Hot day", "125 mph sustained at 25 C; on a 38 C day full speed for about 10 min, then a derate to about 105 mph. No chiller; keep the 3 kW heater and pre-heat on the way to a charger."),
        ("Nov 22", "Mass re-baseline", "A steel pivot yoke (single-sided arm, belt on the other side) and real catalogue running gear raised the roll-up; T1 re-set from 240 to 255 kg."),
        ("Nov 22", "Final mass", "BOM audit found cell holders (3.1 kg) and the arm\u2019s hub carrier (1.1 kg) missing: 257.9 kg, T1 now at most 260 kg."),
        ("Nov 22", "Steering damper", "Speed-scheduled semi-active damper; without it the model wobbles from 15 to 85 mph."),
        ("Nov 22", "Look frozen at rev E", "Pods 55 mm proud, no R15 on the lower body and a second flank line go to V1.1."),
    ]
    body += table(["Date", "Decision", "What and why"], dec, cls="tight", widths=["9%", "17%", "74%"])
    D.add("How the design got here", "Mass and decisions", body, toc=False)

    # ---------------- architecture: renders
    body = title("04 Architecture", "The bike", "Renders of the rev E CAD, with envelope-level geometry and a matte black finish.")
    body += '<div class="grid2">'
    for key, cap in [("side", "Side view"), ("front34", "Front three-quarter"), ("rear34", "Rear three-quarter"), ("rider", "With rider (1,755 mm, 90 kg)")]:
        if key in I:
            body += '<div class="fig"><img src="%s" style="width:100%%"><div class="cap">%s</div></div>' % (I[key], cap)
    body += "</div>"
    body += p("The look is frozen at rev E: beak, slim light band, clear screen, narrow waist, sculpted saddle and matte black, with one continuous lower body formed by the pack case. Three items move to V1.1. The radiator pods stand 55 mm proud of the flank, the lower body has no R15 edge radii yet, and the second flank line is not built. The CAD is an envelope model. It passes 91 of 91 geometry and regulatory-envelope checks, but it lacks many small parts (wiring, hoses, cell holders, lid) and two generator fixes.", "small")
    D.add("Architecture", "Renders", body, toc=True, num="04", toc_title="Architecture")

    # ---------------- architecture: layout + pack + drive
    body = title("04 Architecture", "Layout, pack and drive")
    body += h2("Layout")
    body += p("The solo seat sits at %s on a %s wheelbase. The centre of gravity is %s, with a front/rear split of 52.8 / 47.2 percent (no rider). Mass sits low because the pack is the largest single block and its structural case forms the lower body." % (F["seat"], F["wheelbase"], F["cg"]))
    body += h2("Pack")
    body += table(["Item", "Value"], [
        ("Cells", "Molicel INR-21700-P60B, 100s11p, 1,100 cells x 75 g = 82.5 kg"),
        ("Energy / voltage", "%s kWh gross, %s kWh usable (5-95%%), %s V nominal, 250-420 V" % (F["kwh_gross"], F["kwh_usable"], F["volts"])),
        ("Mass", "%s kg: cells 82.5, case 7.9, internals 14.5, cell holders 3.1" % F["pack_kg"]),
        ("Case", "3 mm aluminium tub with a 5 mm front wall, forming the lower body; four 25s11p lane modules; PA66-GF30 cell holders"),
        ("Charging", "DC 10-80%% about %s min at 25 C (2C cell cap, 12 A per cell, about 137 A at the pack)" % F["chg"]),
        ("Safety", "Per-cell wire-bond fuses, slotted ribbons, burst vents (490 mm\u00b2 per parallel group), coolant loop; propagation passes only with coolant flowing (screening model)"),
    ], cls="tight", widths=["20%", "80%"])
    body += h2("Drive")
    body += table(["Item", "Value"], [
        ("Motor", "EMRAX 228 liquid-cooled, LV+43%% winding (the only winding that makes full power at 360 V; draws 650 A rms), 220 Nm, %s kW peak, 13.2 kg" % F["peak_kw"]),
        ("Inverter", "Cascadia CM200DX, 300 A rms continuous / 740 A rms peak, 6.75 kg"),
        ("Final drive", "Single Gates 8MGT-1760-62 belt, 62 mm wide, 35T / 126T = 3.60:1, centre distance 545.9 mm; belt-to-tyre gap 12.0 mm against a 12 mm limit"),
        ("Performance", "%s s 0-60 mph; %s mph limit governed at %s; %s kW continuous (inverter-limited)" % (F["z60"], F["top"], F["gov"], F["cont_kw"])),
        ("Drive mass", "23.65 kg"),
    ], cls="tight", widths=["20%", "80%"])
    body += p("The belt on one side and a single-sided arm on the other is the hard structural problem, because the belt pulls the wheel forward 274 mm away from the arm. Section 5 shows how the steel pivot yoke carries that load.", "small")
    body += h2("Mass by system (ledger)")
    body += table(["System", "kg", "Share"], [
        (r["budget_group"], r["raw_kg"], "%.0f%%" % (100 * float(r["raw_kg"]) / float(mass_tot["raw_kg"]))) for r in mass_rows] + [("Total", mass_tot["raw_kg"], "100%")],
        cls="tight", num_cols=(1, 2), widths=["60%", "20%", "20%"], total_last=True)
    D.add("Architecture", "Layout, pack and drive", body, toc=False)

    # ---------------- architecture: chassis
    body = title("04 Architecture", "Chassis and running gear")
    body += table(["Item", "Value"], [
        ("Frame", "Steel-tube frame (25CrMo4 class), TIG-welded; rail 38 x 2.25, down-link 38 x 4.0 to 4.25, cast steel nodes at the head and pivot"),
        ("Pivot yoke", "Steel yoke with cross-member at Z545; legs 2.43 kg + cross-member 2.23 kg; pivot bearings 2 x 32012 X. It closes the belt loop inside the motor-and-arm structure, so belt tension does not go through the frame"),
        ("Swingarm", "Cast A356 aluminium single-sided arm with a cast hub carrier; about 5.7 kg for the full arm (in line with production single-sided arms)"),
        ("Chassis mass", "about 31 kg (frame 17.0 + yoke 8.7 + arm 4.1 + hub carrier, pads, bearings, allowances); the original budget was 18 kg"),
        ("Suspension", "Fork and monoshock (catalogue class, 6.8 kg fork); speed-scheduled semi-active steering damper, about 0.5 kg"),
        ("Wheels, tyres", "Carbon wheels 2.6 kg front and 3.3 kg rear (estimates); 110/80R19 and 150/70R17, V-rated (149 mph against a 130 mph governor)"),
        ("Brakes", "Two 320 x 5 mm front discs with Stylema-class calipers, 267 x 5 mm rear disc, ABS"),
    ], cls="tight", widths=["18%", "82%"])
    body += h2("Why the chassis weighs 31 kg and not 18 kg")
    body += p("The Gate A budget of 18 kg assumed a conventional frame. Fatigue, not peak strength, sets the tube walls. The arm must be cast, not welded, and the belt on one side forces a load-bearing yoke. That gives about 31 kg, which I accepted as part of the V1 compromise (T1 re-baselined). An aluminium yoke with a redesigned section is one of the V1.1 weight levers.")
    body += h2("Electrical system")
    body += table(["Item", "Value"], [
        ("HV bus", "360 V nominal pack; 350 A DC cap; four GX14 contactors (350 A carry); 450-A class fuse in the service disconnect; 500 A pyro; cables 50 mm\u00b2 DC bus, 35 mm\u00b2 inlet, 70 mm\u00b2 motor phases"),
        ("Charging", "Native J3400 inlet, DIN 70121 / ISO 15118 controller; BROGEN PV1776 6.6 kW on-board charger (3.0 kg); 150 kW-class DC stations"),
        ("BMS and control", "Orion BMS2-class BMS (not an ISO 26262 certified part), VCU, CAN network"),
        ("Electronics mass", "17.44 kg (budget 17.5)"),
    ], cls="tight", widths=["18%", "82%"])
    D.add("Architecture", "Chassis and running gear", body, toc=False)

    # ---------------- architecture: electrical
    body = title("04 Architecture", "Electrical diagrams", "High-voltage single-line diagram and a DC charging session (generated by `elec-diagrams.py`).")
    for key, cap in [("elec-hv-single-line.svg", "Figure 4.1. HV single-line diagram. The charger box still reads “OBC 3.3 kW”, a stale label: the booked unit is the 6.6 kW BROGEN PV1776."), ("elec-dc-session.svg", "Figure 4.2. DC charging session (NACS handshake, contactor closing and charge ramp).")]:
        if key in I:
            body += fig(I[key], cap, width="94%")
    D.add("Architecture", "Electrical", body, toc=False)

    # ---------------- validation: structures
    body = title("05 Validation", "Structures (09)", "Frame, pivot yoke, single-sided swingarm, pack case. Finite-element models (CalculiX, 12 mm mesh).")
    body += p("The solo load cases (90 kg rider + 25 kg luggage) carry belt preload: static 1 g, 3 g bumps, 1.1 g braking, 45-degree lean in both directions, belt design pull 11.3 kN, launch and regen torque, pack inertia (20 g longitudinal) and crash slider loads. Fatigue uses IIW nominal stress over a 160,000 km road spectrum plus drive events, with a Miner sum D of no more than 0.5.")
    body += h2("Round 3 result (yoke at Z545, bike scaled to 257.3 kg)")
    body += table(["Check", "Safety factor / D", "Required", "Verdict"], [
        ("C6 rear bump 3 g (cross brace)", "1.23", "1.2", Raw('<span class="pill thin">Pass, thin</span>')),
        ("D1 belt design pull (arm, beam model)", "1.19 (shell model about 1.25)", "1.2", Raw('<span class="pill thin">Marginal</span>')),
        ("C9c rear slider 21 kN", "1.08", "1.0", Raw('<span class="pill thin">Pass, thin</span>')),
        ("C9b front slider", "1.18", "1.0", Raw('<span class="pill thin">Pass</span>')),
        ("Fatigue, down-link at headstock", "D 0.57", "0.5", Raw('<span class="pill no">Fail</span>')),
        ("Fatigue, upper rail 1", "D 0.57", "0.5", Raw('<span class="pill no">Fail</span>')),
        ("Torsion / lateral stiffness at head", "5.0 kNm/deg / 1.68 kN/mm", "3 / 1.5", Raw('<span class="pill met">Pass</span>')),
    ], cls="tight", widths=["38%", "26%", "12%", "24%"])
    body += p("The fix is estimated, not re-run. The down-link goes from 38 x 4.0 to 38 x 4.25 (+0.13 kg), upper rail 1 from 38 x 2.25 to 38 x 2.5 (+0.20 kg) and the swingarm wall from 4.0 to 4.25 (+0.11 kg). That adds about 0.45 kg, to be confirmed at 12 mm before release. Those edits are not in the %s kg roll-up." % F["mass_kg"])
    body += h2("Findings that shaped the design")
    body += ul(["The belt on one side and a single-sided arm on the other pushes 36 to 45 kN onto the pivot bearings. The first 46 mm pivot with 6008 bearings could not take it. Closing the belt loop through the frame failed (670 MPa against 435 MPa yield), so the steel pivot yoke is the fix.",
                "A welded 6061 arm fails fatigue by a wide margin. A cast A356 arm passes.",
                "In the pack case, a 4 mm front wall reached 167 MPa against a 140 MPa seam limit. I adopted a 5 mm front wall, but only the 4 mm wall was analysed."])
    body += h2("Limits")
    body += p("FEA Round 3 re-ran the full frame and arm at the final 257.3 kg plus rider and luggage, with the yoke at its built position. Strength and fatigue pass after +0.45 kg of wall increases that were sized by scaling, not re-run. Several factors sit at 1.2 to 1.26 against 1.2. The model uses rigid bosses, nominal-stress welds and an assumed fatigue spectrum. It has no buckling or crash plasticity, no motor mount or torque reaction, and no cell-backed crush analysis. EMRAX has not confirmed the motor housing\u2019s role in the yoke. Fatigue of the carbon wheels, fork and axles was not analysed.", "small")
    D.add("Validation", "Structures", body, toc=True, num="05", toc_title="Validation, structures")

    # ---------------- validation: thermal
    c_ch = chart_charge_times()
    body = title("05 Validation", "Thermal (10)", "Lumped RK4 thermal network, e-NTU radiator, runaway screening model.")
    body += p("A lumped-parameter network covers the hottest cell, pack, motor, inverter and charger, with a radiator and fan model, over duty cycles from 25 C to 45 C and at -10 C. A 2-D screening model checks cell-to-cell propagation. There is no CFD and no bench data.")
    body += table(["Case", "Result", "Limit", "Verdict"], [
        ("125 mph, 25 C, 95 to 5% charge (27.5 min)", "cell core 50.7 C; motor inlet coolant 45.9 C; winding 86 C", "55 C BMS / 60 C cell; 50 C inlet; 100 C winding", Raw('<span class="pill met">Pass</span>')),
        ("130 mph governed, 25 C", "core 53.2 C, inlet 47.5 C, winding 91 C", "same", Raw('<span class="pill met">Pass</span>')),
        ("125 mph, 38 C", "inlet limit after 10.6 min, core 55 C after 17.2 min", "same", Raw('<span class="pill thin">Derate to about 105 mph</span>')),
        ("Mountain riding, 38 C", "core 50.9 C, inlet 50.2 C", "55 C / 50 C", Raw('<span class="pill thin">Pass, at the limit</span>')),
        ("DC 10-80%, 25 C / 35 C", "%s min / 23.0 min" % F["chg"], "25 min", Raw('<span class="pill met">Pass</span>')),
        ("DC 10-80%, 35 C, arriving hot (42 C)", "27.4 min", "25 min", Raw('<span class="pill no">Fail by 2.4 min</span>')),
        ("DC 10-80%, -10 C, 3 kW heater", "25.4 min (14.0 min pre-heated)", "25 min", Raw('<span class="pill thin">Marginal</span>')),
        ("Cell failure propagation", "no spread with coolant flowing; 134-249 C neighbour with no coolant or worst case", "170 C", Raw('<span class="pill thin">Only with coolant</span>')),
    ], cls="tight", widths=["27%", "33%", "22%", "18%"])
    body += fig(c_ch, "Figure 5.1. DC 10-80% charge time by condition. The 21 min headline uses the 2C cell cap; the other bars come from the thermal model\u2019s 3C-cap profile except where stated (at a 2C cap, 35 C takes 27.4 min).", width="82%")
    body += h2("Limits")
    body += p("The model is lumped, with an assumed ram-air factor of 0.25 and assumed core conductance. Two models disagree on the 25 C pack core (46 vs 50.7 C). There is no chiller, so hot days derate. The propagation result is a screen, not UN R136 testing. The charge life of the P60B above 2C is not on the datasheet (v0.1), so I do not claim the faster figures.", "small")
    D.add("Validation", "Thermal", body, toc="sub", toc_title="Thermal")

    # ---------------- validation: aero
    c_cda = chart_range_cda()
    body = title("05 Validation", "Aerodynamics (17)")
    if AERO["status"] != "done":
        body += callout("**" + AERO_PENDING_TEXT + ".** Range is %s mi at 70 mph and %s mi at 77 mph. No CdA has been measured or computed for V1." % (F["r70"], F["r77"]), dark=True)
        body += p("A CFD case on the rev E geometry (rider and bike) is running. No converged result exists, so this section carries an assumption, not a finding. The independent review noted that an earlier outside review found a 7% change in CdA across mesh refinement (0.413 to 0.385) against a 2% goal. That item is still open.")
        body += h2("What the assumption means")
        body += table(["Quantity", "Value at assumed CdA 0.38", "Note"], [
            ("Range at 70 mph", "%s mi" % F["r70"], "146 Wh/mi"),
            ("Range at 77 mph", "%s mi" % F["r77"], "169 Wh/mi"),
            ("Range at 125 mph", "56.9 mi", ""),
            ("Wheel power at 125 / 130 mph", "%s / 48.7 kW" % F["p125"], "continuous power 61.6 kW"),
            ("Range at CdA 0.43 (70 / 77 mph)", "138.8 / 119.8 mi", "plausible range from the outside review: 0.385 to 0.423"),
            ("T3 break-even CdA", "about %s" % F["cda_break"], "T3 (at least 145 mi at 70 mph) fails above this"),
        ], cls="tight", widths=["34%", "30%", "36%"])
    else:
        body += callout("**The drag area of V1 with its rider is 0.43 to 0.46 m\u00b2, not the 0.38 the range target assumed.** At 0.46 the bike does %s mi at 70 mph and %s mi at 77 mph, so T3 (145 mi) is missed by about 13 mi. The main cause is the larger design rider: frontal area is 0.824 m\u00b2 against 0.766 in the earlier study." % (AERO["r70"], AERO["r77"]), dark=True)
        body += p("I ran OpenFOAM (steady RANS, k-omega SST, moving road, rotating wheels) on the rev E bike with the 90 kg upright rider at 70 mph, on three meshes. CdA fell as the mesh got finer, so I quote the finest mesh and the extrapolated value as a band.")
        body += table(["Mesh", "Cells", "CdA, m\u00b2", "Note"], [
            ("Coarse", "0.90 M", "0.503", ""),
            ("Medium", "1.68 M", "0.478", "\u22125.1%"),
            ("Fine", "3.25 M", "0.460", "\u22123.7% (goal 2%)"),
            ("Extrapolated", "", "0.430", "GCI 8.3%"),
        ], cls="tight", widths=["22%", "18%", "20%", "40%"])
        body += table(["Quantity", "Result", "What it changes"], [
            ("Range at 70 / 77 mph, CdA 0.46", "%s / %s mi" % (AERO["r70"], AERO["r77"]), "T3 not met"),
            ("Range at 70 / 77 mph, CdA 0.43", "138.8 / 119.8 mi", "T3 still not met"),
            ("Wheel power at 125 mph", "about 52 kW (scaled from 43.5 kW)", "still under 61.6 kW continuous; thermal not re-run"),
            ("Side wind, 10 degrees yaw", "149 N; centre of pressure 1.04 m ahead of the rear axle, 0.67 m high", "dynamics assumed 0.80 m and 0.95 m; gust case to re-run"),
            ("Radiator pods", "flow goes outward through the cores, about 6.2 m/s", "thermal assumed inward ram air; pods need a closed duct"),
        ], cls="tight", widths=["30%", "38%", "32%"])
    body += fig(c_cda, "Figure 5.2. Range at 70 mph against CdA (257.3 kg re-run of the drive model; 25 C, flat, still air, 90 kg rider). The break-even CdA for the 145 mi target is about 0.407; the shaded band is the CFD result.", width="58%")
    body += h2("Still open in aero")
    body += ul(["A fourth mesh (about 6 M cells) to close mesh convergence, and the opposite-side yaw case.", "A closed duct for the radiator pods, then a thermal re-run with the real core flow.", "A dynamics re-run of the gust case with the CFD side force and centre of pressure.", "A wind-tunnel or coast-down check. Nothing here is measured."])
    D.add("Validation", "Aerodynamics", body, toc="sub", toc_title="Aerodynamics (pending)" if AERO["status"] != "done" else "Aerodynamics")

    # ---------------- validation: dynamics
    body = title("05 Validation", "Vehicle dynamics (15)", "Linear vehicle-dynamics model: weave, wobble, braking, launch, lean clearance, gusts. Run on rev D (247.9 kg).")
    body += callout("**Handlebar wobble is the one real stability problem.** With no damper it is unstable from 15 to 85 mph (damping ratio -0.11 to -0.15). A fixed damper that cures it removes weave damping at 130 mph. **A speed-scheduled semi-active damper fixes both** (25 Nm\u00b7s/rad up to 50 mph, falling to 3 by 95 mph). The thinnest margins with it are wobble 0.039 and weave 0.028 (with luggage).")
    body += table(["Item", "Result", "Criterion", "Verdict"], [
        ("Wobble and weave, scheduled damper", "weakest damping 0.028 (luggage case)", "positive (T8)", Raw('<span class="pill thin">Pass, thin</span>')),
        ("Stop from 60 / 77 mph at 1.0 g", "39.4 / 63.8 m", "inside UN R78", Raw('<span class="pill met">Pass</span>')),
        ("Stoppie limit / wheelie at launch", "1.14 g / no wheelie (0.70 g vs 1.10 g limit)", "above 1.0 g", Raw('<span class="pill met">Pass</span>')),
        ("Front disc, 125-0 mph", "362 / 375 C", "450 C", Raw('<span class="pill met">Pass</span>')),
        ("Front disc, three 0.6 g stops", "444 / 460 C", "450 C", Raw('<span class="pill thin">Marginal</span>')),
        ("Lean clearance, pegs", "45.2-45.6 degrees", "45-50 degrees", Raw('<span class="pill met">Pass</span>')),
        ("Lean, belt-side pulley flange", "48.6 degrees after the flange moved 181 to 177 mm", "pegs + 3 degrees", Raw('<span class="pill thin">Exactly at the rule</span>')),
        ("Sidewind 10 m/s at 77 mph", "lean 9.7 degrees, 5 Nm on the bars (CoP assumed 0.80 m; CFD gives 1.04 m, re-run open)", "10 Nm screen", Raw('<span class="pill thin">Pass, assumed CoP</span>')),
    ], cls="tight", widths=["30%", "34%", "17%", "19%"])
    if "dyn-damper-schedule.png" in I:
        body += fig(I["dyn-damper-schedule.png"], "Figure 5.3. Speed-scheduled damper (`damper-schedule.png`).", width="92%")
    body += h2("Limits")
    body += p("The model ran on rev D at 247.9 kg and was not re-run on rev E (the 177 mm pulley flange gives exactly the \u201cpegs + 3 degrees\u201d rule). The rider is rigid and hands-off. Fork stiffness, tyre properties, damping and the gust centre of pressure are estimates. There is no comfort or buffeting analysis. A failed damper (unscheduled state) is a safety case, now in DFMEA D48 and test V53.", "small")
    D.add("Validation", "Dynamics", body, toc="sub", toc_title="Vehicle dynamics")

    # ---------------- validation: drive
    c_pw = chart_power_soc()
    body = title("05 Validation", "Drive and performance (06)", "Drive model: pack resistance, EMRAX loss map, inverter, belt, tyre and road load. Re-run at the final mass (257.5 kg + 90 kg rider).")
    body += table(["Quantity", "Final V1", "Note"], [
        ("0-60 mph", "%s s" % F["z60"], "%s s with 25 kg luggage; %s s on a wet road (mu 0.7); torque-limited" % (F["z60_lug"], F["z60_wet"])),
        ("0-100 km/h / 0-100 mph", "%s s / %s s" % (F["z100kmh"], F["z100mph"]), "SOC 90, 25 C"),
        ("60-100 mph roll-on", "%s s" % F["r60_100"], ""),
        ("Top speed", "%s mph limit" % F["top"], "6,500 rpm limit, not power; governed at %s mph" % F["gov"]),
        ("Wheel power at 125 / 130 mph", "%s / 48.7 kW" % F["p125"], "2.4x power margin at 125 mph"),
        ("Peak / continuous power", "%s kW / %s kW" % (F["peak_kw"], F["cont_kw"]), "continuous is inverter-limited and below 56 kW under 103 mph"),
        ("Range, 70 / 77 mph", "%s / %s mi" % (AERO["r70"], AERO["r77"]), "at CdA %s%s" % (AERO["cda"], " (assumed)" if AERO["status"] != "done" else "")),
        ("DC charge 10-80%", "about %s min" % F["chg"], "25 C, 2C cell cap, 51 kW average"),
    ], cls="tight", widths=["30%", "22%", "48%"])
    body += fig(c_pw, "Figure 5.4. Peak shaft power against state of charge at the 350 A DC cap. T5 (at least 90 kW) holds above about 10% charge at 25 C and is not met on a cold, nearly empty pack unless pre-warmed.", width="80%")
    body += h2("Limits")
    body += p("Motor iron loss, the efficiency map, pack resistance and 300 W of auxiliaries are estimates, and the road is flat with still air. The EMRAX torque curve beyond its 5,500 rpm datasheet corner is a fitted model, and Gates rates the belt to 4,000 rpm (extrapolated to 6,262 rpm). The hand model in `07` gives 96 kW at 10% charge and the drive model gives 93 kW. Nothing here is verified by test.", "small")
    D.add("Validation", "Drive and performance", body, toc="sub", toc_title="Drive and performance")

    # ---------------- validation: electrical
    body = title("05 Validation", "Electrical (07)", "Pack, HV system, charging, LV loads and wiring.")
    body += table(["Item", "Result"], [
        ("Pack", "100s11p of P60B: 1,100 x 21.6 Wh = 23.76 kWh; 360 V nominal; 66 Ah"),
        ("Motor and inverter match", "Only the LV+43% winding makes full power at 360 V (650 A rms). The emDrive H100 gives about 29 kW continuous, so the Cascadia CM200DX was chosen at +3.25 kg (continuous power 61.6 kW, inverter-limited)"),
        ("DC cap and protection", "350 A cap; GX14 contactors 350 A carry; 450-A class fuse (a 400 A fuse would sit at 0.88 of rating against a 1.3x no-blow rule); fuse I2t against the busbar and cell-bond withstand is not checked"),
        ("Cables", "DC bus 50 mm\u00b2 (212 A bundled against 187 A worst continuous); inlet 35 mm\u00b2 (161 A against 137 A charge current); motor phases 70 mm\u00b2 or 2 x 35 mm\u00b2 (about +0.3 kg not yet booked in the ledger)"),
        ("Charging", "12.5 A per cell (2.08C, 137 A) gives 10-80% in about 20-21 min; 5C maximum on datasheet v0.1, no cycle life above 2C. AC 6.6 kW: 3.1 h for 10-90%"),
        ("NACS", "J3400 inlet and DIN 70121 / ISO 15118 charge controller are a design; **Supercharger access and Plug and Charge are not established**"),
        ("Mass / cost", "17.44 kg electronics; about $5.9k electrical parts at 10k"),
    ], cls="tight", widths=["22%", "78%"])
    if "elec-lv-can.svg" in I:
        body += fig(I["elec-lv-can.svg"], "Figure 5.5. 12 V and CAN block diagram (`elec-lv-can.svg`).", width="100%")
    body += h2("Limits")
    body += p("No supplier has confirmed performance at the actual 360 V bus. The P60B fast-charge life is unconfirmed, and a 2C cap reduces that risk without retiring it. The BMS limits, regen and ABS blending, NACS handshake, charge derating, speed governor and damper schedule have no controls specification yet. The ledger and CAD still carry stale labels for the motor winding (\u201cHV\u201d, \u201cMV\u201d) and charger (3.3 kW).", "small")
    D.add("Validation", "Electrical", body, toc="sub", toc_title="Electrical")

    # ---------------- mass
    c_mb = chart_mass_budget(mass_rows)
    body = title("06 Mass", "Mass, budget against actual", "Source: `program/data/mass-budget-report.csv`, `mass-rollup.json`, `parts-ledger.csv`, `bom-v1-reconcile.json`.")
    body += table(["System", "Budget kg", "Actual kg", "Headroom kg", "Headroom %", "Growth-adjusted kg", "Estimate share"],
                  [(r["budget_group"], r["budget_kg"], r["raw_kg"], r["headroom_kg"], r["headroom_pct"],
                    r["growth_adjusted_kg"] or "", ("%s%%" % r["estimate_share_pct"]) if r["estimate_share_pct"] else "") for r in mass_rows] +
                  [("Total", mass_tot["budget_kg"], mass_tot["raw_kg"], mass_tot["headroom_kg"], mass_tot["headroom_pct"], "about %s" % F["ledger_growth"], "")],
                  cls="tight", num_cols=(1, 2, 3, 4, 5, 6), total_last=True, widths=["26%", "11%", "11%", "13%", "12%", "16%", "11%"])
    body += p("Estimate share is the ledger\u2019s own flag per group. The pack shows 0% because its cells are supplier data, but the pack case and internals (about 25 kg) are estimates.", "small")
    body += fig(c_mb, "Figure 6.1. Budget against actual by system. The group budgets were re-set to the actuals when mass closed, so \u201cbudget pass\u201d shows the ledger is clean, not that mass is under control. Every group is flagged TIGHT.", width="92%")
    body += h2("Centre of gravity and sources")
    body += p("The bike CG is **787 mm ahead of the rear axle and 529 mm high**, with a front/rear split of 52.8 / 47.2 percent. Unsprung mass is 13.5 kg front and 19.3 kg rear. By source, **0 kg is measured**, about 110 kg is supplier data, 75 kg is calculated and 73 kg is estimated (28%). The ledger\u2019s own growth rule (+15% on concept parts, +10% proposed) would give about 287 kg. That is a planning reference, not a forecast.")
    body += callout("**The mass margin is thin.** Headroom against T1 is %s kg (about 0.8%%), against a first policy of 12 kg (5%%). Mass is an unmeasured pass, and the first weighed prototype is test V38." % F["headroom"])
    D.add("Mass", "Mass", body, toc=True, num="06", toc_title="Mass, budget against actual")

    # ---------------- cost I
    g = cost["groups"]
    c_cb = chart_cost_breakdown(g)
    base = cost["base"]
    body = title("07 Cost", "Unit cost", "Source: `11-cost.md`, `cost-model-v1.csv` and `.json`. Every price is an estimate; no supplier was contacted.")
    body += kpis([("$%sk" % F["cost10"], "Unit cost at 10,000 / yr", "target T9: at most $32k"),
                  ("$%sk" % F["cost1"], "At 1,000 / yr", ""), ("$%sk" % F["cost100"], "At 100 / yr", ""),
                  ("$%sk" % F["cost_stress"], "10k if cells, motor, inverter stay at 1k prices", "misses T9 by $0.3k")])
    rows = [("Cells (1,100 x P60B)", base["100"]["cells"], base["1000"]["cells"], base["10000"]["cells"]),
            ("Made parts (frame and yoke, cast arm, case, body, pulleys)", base["100"]["made"], base["1000"]["made"], base["10000"]["made"]),
            ("Purchased parts", base["100"]["purchased"], base["1000"]["purchased"], base["10000"]["purchased"]),
            ("Direct labour (pack + bike)", base["100"]["pack_labour"] + base["100"]["bike_labour"], base["1000"]["pack_labour"] + base["1000"]["bike_labour"], base["10000"]["pack_labour"] + base["10000"]["bike_labour"]),
            ("Plant overhead", base["100"]["overhead"], base["1000"]["overhead"], base["10000"]["overhead"]),
            ("Test, logistics, scrap, warranty", *[base[v]["eol"] + base[v]["qc"] + base[v]["logistics"] + base[v]["scrap"] + base[v]["warranty"] for v in ("100", "1000", "10000")]),
            ("Tooling and capital (5-year amortised)", base["100"]["tooling_amort"], base["1000"]["tooling_amort"], base["10000"]["tooling_amort"]),
            ("Unit cost, ex-works", base["100"]["total"], base["1000"]["total"], base["10000"]["total"])]
    body += table(["Per bike, USD", "100 / yr", "1,000 / yr", "10,000 / yr"], [(r[0],) + tuple("{:,.0f}".format(x) for x in r[1:]) for r in rows],
                  cls="tight", num_cols=(1, 2, 3), total_last=True, widths=["52%", "16%", "16%", "16%"])
    body += fig(c_cb, "Figure 7.1. Unit cost by system group at three volumes (material and purchased parts; labour, overhead, warranty and tooling excluded). Drive, pack and running gear are two thirds of the total.", width="95%")
    body += p("Unit cost excludes NRE, dealer margin, outbound freight, financing, working capital, Supercharger network access and certification fees beyond the NRE line. At a $45k MSRP the 10k unit cost is 66% of MSRP before dealer margin.", "small")
    D.add("Cost", "Unit cost", body, toc=True, num="07", toc_title="Cost")

    # ---------------- cost II
    sens = cost["sens"]
    srows = [("Base", base["10000"]["total"]),
             ("Cells +30%", sens["cells +30%"]["10000"]), ("Cells -30%", sens["cells -30%"]["10000"]),
             ("Labour $65/h", sens["labour rate 65 USD/h"]["10000"]), ("Labour $30/h", sens["labour rate 30 USD/h"]["10000"]),
             ("Carbon wheel price +50%", sens["carbon-wheel OEM price +50% (10k 3,150)"]["10000"]),
             ("Forged instead of carbon wheels", sens["forged wheels instead of carbon (10k set 1,050)"]["10000"]),
             ("Motor + inverter at volume-supplier prices", sens["motor+inverter at volume-supplier pricing (10k: motor 2,800 / inverter 1,500)"]["10000"]),
             ("Cells, motor, inverter at 1k prices", sens["stress: cells, motor, inverter stay at 1k-bike prices at 10k"]["10000"])]
    c_cs = chart_cost_sens(srows)
    body = title("07 Cost", "Sensitivities, levers and tooling")
    body += fig(c_cs, "Figure 7.2. Unit cost at 10,000 / yr under single changes. The pass is fragile. It needs volume price breaks nobody has quoted, around 11 million cells a year at a $3.80 cell.", width="95%")
    body += h2("Cost-down levers at 10k (dollars per bike)")
    body += table(["Lever", "Saving"], [(l[0], "{:,.0f}".format(l[1])) for l in cost["levers"]], cls="tight", num_cols=(1,), widths=["80%", "20%"])
    body += h2("One-off tooling and NRE (kept out of unit cost)")
    body += table(["USD", "100 / yr", "1,000 / yr", "10,000 / yr"], [
        ("Tooling and capital (parts tooling, pack line, vehicle line, test rigs)", "1.25 M", "3.67 M", "%.2f M" % (base["10000"]["tooling_total"] / 1e6)),
        ("NRE (engineering, specialists, prototypes, cell life, compliance)", "%.2f M" % (cost["nre_total"]["100"] / 1e6), "%.2f M" % (cost["nre_total"]["1000"] / 1e6), "%.2f M" % (cost["nre_total"]["10000"] / 1e6)),
    ], cls="tight", num_cols=(1, 2, 3), widths=["52%", "16%", "16%", "16%"])
    body += p("The NRE is reused from an October startup-cost study, not re-derived. The verification plan (section 9) is about $%sM and is not reconciled with it. The largest 10k tooling items are the pack line ($3.0M), the vehicle line ($3.5M) and frame jigs and robot cell ($1.0M)." % F["dvpr"], "small")
    body += h2("Key price assumptions")
    body += p("P60B is $3.80 at 10k (about $176/kWh; no published P60B price). EMRAX 228 is $4,800 and CM200DX $3,200 at 10k, both low-volume specialists and estimates. The carbon wheel set is $2,100 at 10k (47% of a $4.5k retail anchor). Assembly is 7.5 h at $45/h plus 60% overhead.", "small")
    D.add("Cost", "Sensitivities and tooling", body, toc=False)

    # ---------------- compliance + DFMEA
    comp_txt = (PROG / "12-compliance.md").read_text(encoding="utf-8")
    comp_rows = []
    for m in re.finditer(r"^\| ([A-Za-z/ &]+?) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", comp_txt, re.M):
        comp_rows.append((m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))
    tot = [r for r in comp_rows if r[0].startswith("Total")]
    comp_rows = [r for r in comp_rows if not r[0].startswith("Total")]
    tot_vals = [sum(int(r[i]) for r in comp_rows) for i in (1, 2, 3, 4)]
    body = title("08 Compliance and safety", "Compliance (12)", "Standards matrix: FMVSS / NHTSA, EPA / CARB, battery, charging, functional safety, EU (later).")
    body += p("**V1 can be sold in the US with no emissions certification, but it has not been tested against a single standard.** The US route is self-certification: the maker states the bike meets every applicable FMVSS and files with NHTSA. Nothing in the design blocks that. The EU route (type approval) is a separate, larger job and stays \u201clater\u201d. Everything below is on paper.")
    body += table(["Area", "Rows", "Met by design", "Needs test", "Open"], [r for r in comp_rows] + [("Total", *[str(v) for v in tot_vals])],
                  cls="tight", num_cols=(1, 2, 3, 4), total_last=True, widths=["40%", "12%", "18%", "15%", "15%"])
    body += p("The battery carries the compliance risk. A 23.8 kWh, 108 kg pack needs UN 38.3 to ship, and its safety case (propagation, vents, crush) is the least proven part of the design.")
    body += p("Functional safety is a process, not a part. The BMS is not ISO 26262 certified, so a hazard analysis, ASIL targets and fault-injection tests are needed before any production claim. Supercharger access is separate from the NACS connector and is still open. The rev D/E CAD ran a 91-check envelope screen covering FMVSS 108, 111 and 123 geometry for lamps, mirrors and tyres. It is not a certification test.")
    # DFMEA
    hi = [r for r in dfmea if r["action_priority"] == "H"]
    superseded = {"D24", "D30"}          # EMRAX-housing-as-yoke rows, replaced by the steel yoke (D47)
    top = sorted([r for r in hi if r["id"] not in superseded], key=lambda r: -int(r["SxOxD"]))[:8]
    c_df = chart_dfmea(dfmea)
    body += h2("Design FMEA (13): top risks")
    body += p("**%d rows: %d High, %d Medium, %d Low. None has been tested.** Two of the High rows (D24, D30) describe the earlier motor-housing yoke and are superseded by D47 (steel pivot yoke), so the list below leaves them out. Scores are engineering judgement on a paper design (AIAG-VDA style, S x O x D). Detection scores are poor because most controls are analysis only." % (
        len(dfmea), len(hi), sum(r["action_priority"] == "M" for r in dfmea), sum(r["action_priority"] == "L" for r in dfmea)))
    body += table(["ID", "Item and failure", "S", "O", "D", "Test"], [
        (r["id"], "%s: %s" % (r["item"], r["failure_mode"]), r["severity"], r["occurrence"], r["detection"], r["dvpr_tests"].replace(";", ", ")) for r in top],
        cls="tight", num_cols=(2, 3, 4), widths=["6%", "66%", "5%", "5%", "5%", "13%"])
    D.add("Compliance and safety", "Compliance and DFMEA", body, toc=True, num="08", toc_title="Compliance and safety")

    # ---------------- DFMEA detail page (chart + notes) merged into verification? keep separate small page
    body = title("08 Compliance and safety", "Risk picture", "DFMEA summary by system and what the top risks mean.")
    body += fig(c_df, "Figure 8.1. DFMEA rows by system and priority (`dfmea-v1.csv`).", width="85%")
    body += h2("What the High risks have in common")
    body += ul(["Battery fire safety covers a single-cell short, propagation, vent sizing and blockage, case crash strength (5 mm front wall adopted, only the 4 mm wall analysed) and rock strike. All need physical tests (V01 to V05, V18 to V21, V43).",
                "The belt loop covers the steel pivot yoke (D47), cast arm fatigue and the pivot bearings. The yoke test (V08, about $70k, 6 weeks) decides the chassis architecture and is first in the plan.",
                "Brakes cover 125 mph stopping and regen with ABS.",
                "Steering damper failure (D48) matters because wobble is unstable from 15 to 85 mph if the scheduled damper fails unscheduled. The defined fail-safe state is test V53.",
                "Active discharge is slow: the inverter bus takes about 88 s to fall below 60 V, and the specification calls for under 3 s (test V13)."])
    body += h2("Open compliance items")
    body += ul(["The Parts 565 / 566 / 567 filing and the FMVSS tests happen in the last phase (V52).",
                "Process FMEA, ISO 26262 hazard analysis and FMEDA do not exist yet, and ASIL levels are proposals.",
                "EPA noise, EMC, UN 38.3 and homologation dates are planning figures only."])
    D.add("Compliance and safety", "Risk picture", body, toc=False)

    # ---------------- DVP&R
    c_tl = chart_timeline()
    phases = {}
    for r in dvpr:
        phases[r["phase"]] = phases.get(r["phase"], 0) + int(float(r["cost_usd_estimate"] or 0))
    tot_dvpr = sum(phases.values())
    tests = [r for r in dvpr if r["id"].startswith("V")]
    body = title("09 Verification plan", "DVP&R (14)", "Design verification plan and report. Every line is planned and nothing has been done.")
    body += kpis([("$%sM" % F["dvpr"], "US verification budget", "about $4.9M to $10.6M plausible range"),
                  ("%s months" % F["months"], "To pre-production confirmation", "about 118 weeks to filing"),
                  ("%d" % len(tests), "Test lines", "each High DFMEA risk has a test"),
                  ("3 + 8", "Mules and pre-production bikes", "12 extra test packs")])
    body += p("The plan tests first what can kill the design cheaply: the steel yoke proof (V08), then the pivot rig (V07), cast-arm fatigue (V06), cell 2C charge life (V01, 26 weeks) and lane-module propagation (V02). A decision gate at week 14 confirms yoke, pivot, vent and brake size before the mules are built. UN 38.3 (V17) must finish before packs travel.")
    body += fig(c_tl, "Figure 9.1. Build-and-test timeline in weeks from go (`14-dvpr.md`).", width="74%")
    body += h2("Budget by phase (from dvpr-v1.csv)")
    ph_order = ["component", "prototype", "pre-production"]
    us_total = sum(phases.get(k, 0) for k in ph_order)
    rows = [(k.capitalize() + (" (includes 3 mules, 12 test packs)" if k == "prototype" else " (includes 8 bikes)" if k == "pre-production" else ""), "${:,.0f}".format(phases.get(k, 0))) for k in ph_order if k in phases]
    rows.append(("US total (three phases)", "${:,.0f}".format(us_total)))
    other = tot_dvpr - us_total
    if other > 0:
        rows.append(("EU add-on (later, not in the headline)", "${:,.0f}".format(other)))
    body += table(["Phase", "Cost"], rows, cls="tight", num_cols=(1,), widths=["70%", "30%"], hl_rows=(len(ph_order),))
    body += p("The headline is about $7.04M. The phase total here is $40k higher because it includes test V53 (steering-damper fail-safe), added on Nov 22. The plan is not reconciled with the $32.4M NRE in the cost model. Costs are planning figures scaled from an earlier study, not lab quotes.", "small")
    body += h2("Which test closes which target")
    body += table(["Target", "Closing tests", "Target", "Closing tests"], [
        ("T1 mass", "V38 (weigh every prototype), V06, V30, V31", "T6 charging", "V22, V23, V34"),
        ("T2 pack safety", "V01 to V05, V13 to V21, V26", "T7 load case", "V30, V31"),
        ("T3 range", "V35, V36 (coast-down, range)", "T8 comfort, stability", "V06, V07, V15, V30-V32, V39, V40, V42, V46, V47, V50, V53"),
        ("T4 125 mph", "V33, V37, V09, V11, V25, V41", "T9 cost", "no test; follows from quotes"),
        ("T5 power", "V10, V37, V08, V09", "T10 look", "V44, V45")],
        cls="tight", widths=["13%", "32%", "15%", "40%"])
    D.add("Verification plan", "DVP&R", body, toc=True, num="09", toc_title="Verification plan (DVP&R)")

    # ---------------- targets verdict
    T = [("T1", "Wet mass at most 260 kg", "met-thin", "257.9 kg, headroom 2.1 kg; nothing weighed; 28% estimate; the ledger\u2019s growth rule gives about 287 kg; group budgets were re-set to actuals"),
         ("T2", "Pack 100s11p, 23.8 kWh, 360 V, at most 108 kg", "met", "23.76 / 21.4 kWh, 360 V, 108.0 kg (revised Nov 22 from 370 V / 103 kg). Met on analysis; cells are supplier data, case and internals are estimates"),
         ("T3", "Range at least 145 mi at 70 mph", "not met", "%s mi at the CFD CdA of 0.46 (138.8 mi at the extrapolated 0.43); the target needs CdA about 0.407 or less; lower drag is the first V1.1 lever" % AERO["r70"]),
         ("T4", "125 mph sustained, governed 130", "met-thin", "135 mph limit; 25 C thermal passes in two models at CdA 0.38; at the CFD drag, 125 mph needs about 52 kW at the wheel against 61.6 kW continuous (thermal not re-run); at 38 C derates to about 105 mph; not verified"),
         ("T5", "At least 90 kW peak, 55 kW continuous", "met-thin", "124 kW at high charge; 93 kW at 10% charge and 87 kW at 5% (25 C); 86 kW or less cold at low charge; continuous 61.6 kW, below 56 kW under 103 mph"),
         ("T6", "Native NACS; DC 10-80% in 25 min or less; AC 3.3 kW or more", "met-thin", "about 21 min at 25 C and a 2C cap; 35 C and cold figures lean on a 3C cap the cell data does not confirm; AC 6.6 kW; Supercharger access not established; not verified"),
         ("T7", "Solo 90 kg rider + 25 kg luggage", "met-thin", "FEA Round 3 at 257.3 kg + rider + luggage passes after +0.45 kg of wall increases (sized by scaling, not re-run); not tested; the \u201c95th percentile\u201d label is wrong (about the adult male average)"),
         ("T8", "Comfort, 77 mph gust stability, positive damping", "met-thin", "positive damping only with the scheduled damper (0.028 thinnest); dynamics run at rev D mass; no comfort or buffeting analysis; not verified"),
         ("T9", "Unit cost at most $32k at 10k / yr", "met-thin", "$29.5k estimate; $32.3k with cells, motor and inverter at 1k prices; no quotes"),
         ("T10", "Frozen appearance direction", "met-thin", "direction kept; pods 55 mm proud, no R15 on the lower body, second flank line open (V1.1)")]
    body = title("10 Targets", "Targets T1 to T10 and the verdict on each", "From `00-V1-final-spec.md` and the independent review (`19-independent-review.md`).")
    body += table(["#", "Target", "Verdict", "Evidence"], [(a, b, pill(c), d) for a, b, c, d in T], cls="tight", widths=["5%", "24%", "13%", "58%"])
    body += p("Met means supported by analysis with margin. Met, thin means it passes on paper with little margin or on an assumption. Not met means it fails as written. Not verified means there is no analysis on the exact claim. **Nothing in V1 is met by test.**", "small")
    body += callout("**One target is met on analysis (T2), eight are met thinly and one is missed: T3, range.** The CFD drag area came in at 0.43 to 0.46 m\u00b2 against the 0.38 the range target assumed, which puts range at about 132 to 139 mi against 145. I kept the target as written and booked the miss rather than move the goalposts. The last fatigue fix (+0.45 kg of wall) was sized by scaling, and several claims rest on assumed inputs. That is a fair state for a paper design, and it is why the verification plan starts with the cheap tests that could kill the design.")
    D.add("Targets", "Targets T1 to T10", body, toc=True, num="10", toc_title="Targets T1 to T10, verdicts")

    # ---------------- roadmap
    body = title("11 Roadmap", "V1.1 and beyond", "A V1 with a planned improvement path.")
    body += table(["Step", "What changes", "What it buys", "Status"], [
        ("Better cells", "Higher-energy-density cells in the same case and mass", "More range at the same mass, or the same range at lower mass; relaxes the CdA break-even", "Market-dependent; needs cell qualification"),
        ("Lower drag", "Aero refinement from the CFD: screen, fairing and pod shapes, cooling-duct routing", "Back to CdA 0.38 restores about 152 mi at 70 mph", "CFD done: CdA 0.43 to 0.46 today"),
        ("Lighter chassis", "About 10 kg of identified levers: wheels and brakes (magnesium or forged package), a short HV bus, an aluminium yoke with a redesigned section, a cell-to-chassis pack with no case walls, flush radiator pods", "Mass and margin against T1 (listed, not computed)", "Not analysed"),
        ("Styling refinement", "Flush or smaller pods, R15 edge radii on the lower body, a second flank line", "Closes the open T10 items", "Logged for V1.1"),
        ("Two-up variant", "Passenger seat, rear subframe and suspension, higher gross mass", "A second use case on the same platform", "Later; solo is the V1 load case"),
    ], cls="", widths=["14%", "34%", "32%", "20%"])
    body += h2("Why this order")
    body += p("Cells and drag come first because they move range, the claim the bike is judged on, with no change to the architecture. The chassis levers move mass. They were identified in the Gate A log, but none has been analysed, so about 10 kg is a candidate list, not a promise.")
    body += p("Styling is cheap and visible but touches tooling, so I decide it before any hard tooling is cut. The two-up variant needs structures, dynamics and brakes re-run at a higher gross mass, so it follows a verified solo bike.")
    body += h2("Before V1.1 can start")
    body += ul(["A converged CdA (fourth mesh) and a wind-tunnel or coast-down check.", "Cell charge-life data from Molicel, and supplier confirmation from EMRAX and Cascadia at the 360 V bus.", "The first weighed parts and the yoke proof test (V08).", "A re-run of structures and dynamics at the final mass and geometry."])
    D.add("Roadmap", "Roadmap", body, toc=True, num="11", toc_title="Roadmap, V1.1 and beyond")

    # ---------------- status and limitations
    body = title("12 Status", "Status and limitations", "What exists, what does not, and where V1 is weakest.")
    body += callout("**This is a simulation- and analysis-based design. Nothing has been built or physically tested. Supplier prices are estimates and no supplier has quoted.** The design is coherent and carefully caveated, but it is not a verified product.", dark=True)
    body += h2("What exists")
    body += ul(["A CAD model (rev E, 91 of 91 envelope checks pass) and a 223-line bill of materials that ties to the parts ledger and mass roll-up at 257.9 kg.",
                "Structures, thermal, dynamics, drive, electrical, cost, compliance, DFMEA and DVP&R studies, and an independent review of all of them.",
                "Nine concept drawing sheets (not for manufacture)."])
    body += h2("What does not exist")
    body += ul(["No weighed part, no coast-down, no bench or crash test. The 257.9 kg is 0 kg measured.",
                "No measured drag. The CdA is CFD on three meshes that are not fully converged (0.43 to 0.46).",
                "No supplier quote or confirmation (Molicel, EMRAX, Cascadia), and the P60B fast-charge life above 2C is unknown.",
                "No Supercharger or Plug and Charge access. Native NACS is a connector and a protocol design.",
                "No controls specification (BMS limits, regen and ABS blending, NACS handshake, damper schedule, limp mode, cybersecurity).",
                "No wiring, hoses, ribbons or vents in the CAD; no motor mount or torque-reaction analysis; concept-level drawings (no GD&T, welds or fits).",
                "Structures not fully re-run at the final mass; dynamics not re-run on rev E."])
    body += h2("Known weak points")
    body += ul(["Mass headroom is 2.1 kg (0.8%). The belt-to-tyre gap has zero margin, and two fatigue checks need a small wall increase.",
                "T3 range is missed: about 132 mi at 70 mph against 145. Getting CdA back to about 0.40 closes it.",
                "Wobble is stable only with a speed-scheduled damper (0.028 thinnest margin).",
                "Cost passes by $2.5k on estimates, and misses by $0.3k if cells, motor and inverter stay at 1k prices.",
                "Competitor figures come from published pages, not from tests."])
    body += h2("About this document")
    body += p("Bavuso Motors prepared this dossier. AI engineering agents (Claude) carried out the engineering analysis under my direction, and an independent reviewer agent checked the work. Its findings are in `19-independent-review.md`. The authority for every number is `00-V1-final-spec.md`.", "")
    D.add("Status and limitations", "Status", body, toc=True, num="12", toc_title="Status and limitations")

    # ---------------- appendix: drawings
    drawings_dir = ASSETS / "drawings"
    meta = json.load(open(DATA / "drawings-meta.json", encoding="utf-8"))
    pn_name = {"BV-ASM-0201": "Welded main frame with cast nodes", "BV-ASM-0202": "Pivot yoke", "BV-ASM-0203": "Cast A356 swingarm",
               "BV-BOD-0004": "Lower body panel", "BV-DRV-0006": "Rear pulley hub", "BV-DRV-0007": "Motor carrier",
               "BV-ENG-0001": "Pack case tub", "BV-ENG-0101": "Pack lid (derived concept)", "BV-ENG-0102": "Module cell holder (derived concept)"}
    sheets = [k for k in pn_name if (drawings_dir / (k + ".png")).exists()]
    body = title("13 Appendix", "A. Concept drawing pack", "Nine A3 concept sheets, third-angle, ISO 2768-m. Full-resolution vector pack: `drawings/V1-drawing-pack.pdf`.")
    body += table(["Sheet", "Part number", "Part", "Scale", "Ledger mass (at sheet build)"], [
        (str(i + 1), k, pn_name[k], meta.get(k, {}).get("scale", ""), "%.2f kg" % meta.get(k, {}).get("mass_kg", 0)) for i, k in enumerate(pn_name)],
        cls="tight", num_cols=(4,), widths=["8%", "18%", "42%", "10%", "22%"])
    body += p("Concept-level, **not for manufacture**: no GD&T, weld symbols, surface finish, threads or fits. Seven sheets come from CAD solids and two (lid, cell holder) are derived concept shapes. Sheet masses are from an earlier ledger snapshot; the ledger, BOM and this dossier govern (the rolled-up total is 257.9 kg).", "small")
    if sheets:
        body += fig("assets/drawings/%s.png" % sheets[0], "Sheet 1: %s (%s)." % (pn_name[sheets[0]], sheets[0]), width="100%", cls="sheet")
    D.add("Appendix", "Drawing pack", body, toc=True, num="13", toc_title="Appendix A, concept drawing pack")
    # remaining sheets, two per page
    rest = sheets[1:]
    for j in range(0, len(rest), 2):
        pair = rest[j:j + 2]
        body = '<div class="stamp">13 Appendix &middot; A. Concept drawing pack (continued)</div>'
        for k in pair:
            body += fig("assets/drawings/%s.png" % k, "Sheet %d: %s (%s)." % (list(pn_name).index(k) + 1, pn_name[k], k), width="6.05in", cls="sheet")
        D.add("Appendix", "Drawing pack", body, toc=False)
    if not sheets:
        D.pages[-1]["html"] += p("Drawing sheet images are not available in `final/assets/drawings/`; see `drawings/V1-drawing-pack.pdf`.")

    # ---------------- appendix: BOM + index
    sys_rows = [(r["part_number"], r["description"], float(r["mass_ext_kg"])) for r in bom if r["level"] == "1"]
    asm = sorted([r for r in bom if r["level"] == "2"], key=lambda r: -float(r["mass_ext_kg"]))[:6]
    npart = sum(1 for r in bom if r["level"] == "3")
    body = title("13 Appendix", "B. Bill of materials summary", "Source: `bom-v1-indented.csv` (four levels: vehicle, systems, assemblies, parts); ties to the ledger at 257.9215 kg.")
    body += table(["System", "Description", "kg"], [(a, b, "%.2f" % c) for a, b, c in sys_rows] + [("", "Vehicle total (%d part lines, %d assemblies)" % (npart, sum(1 for r in bom if r["level"] == "2")), "%.2f" % sum(c for _, _, c in sys_rows))],
                  cls="tight", num_cols=(2,), total_last=True, widths=["16%", "70%", "14%"])
    # document index
    body += h2("C. Document index")
    docs = []
    for f in sorted(PROG.glob("[0-9][0-9]-*.md")) + [PROG / "BRIEF.md", PROG / "GATE-A-targets-locked.md"]:
        first = f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        txt = f.read_text(encoding="utf-8")
        status = "superseded in part" if "Superseded in part" in txt[:1500] else ("authority" if f.name.startswith("00-") else "")
        docs.append((f.name, first, status))
    docs.append(("17-aero.md", "Bavuso V1 aerodynamics", "done" if AERO["status"] == "done" else "pending"))
    docs = sorted(set(docs), key=lambda d: d[0])
    body += table(["File (program/)", "Title", "Status"], docs, cls="tight", widths=["24%", "52%", "24%"])
    D.add("Appendix", "BOM and document index", body, toc="sub", toc_title="Appendices B and C, BOM and document index")

    return D


def toc_html(D):
    rows = []
    for i, pg in enumerate(D.pages, start=1):
        if pg.get("toc"):
            sub = pg["toc"] == "sub"
            rows.append('<tr><td class="num">%s</td><td%s>%s</td><td class="p">%d</td></tr>' % (
                esc(pg.get("num") or ""), ' style="padding-left:14pt;color:#3B3F46"' if sub else "", esc(pg.get("toc_title") or pg["title"]), i))
    body = title("", "Contents")
    body += '<div class="rule"></div>'
    body += '<table class="toc"><tbody>%s</tbody></table>' % "".join(rows)
    body += h2("About this document")
    body += p("This dossier describes the Bavuso V1 electric adventure-touring motorcycle as a design. It covers what the bike is, why it has these numbers, how it was analysed and what the analysis does not prove. It is a design freeze at **Rev E, November 22, 2026**.")
    body += p("Bavuso Motors prepared it. AI engineering agents (Claude) carried out the engineering analysis under my direction.")
    body += p("Numbers carry one of four labels: measured, supplier, calculated or estimate. No part has been weighed and nothing has been tested, so no value comes from hardware. The single source for every number is `program/00-V1-final-spec.md`.")
    if AERO["status"] != "done":
        body += callout("**" + AERO_PENDING_TEXT + ".**")
    return body


# ----------------------------------------------------------------------------- summary (2 pages)
def build_summary(I, D_main):
    S = Doc("Bavuso V1: Summary", label="Summary")
    aero_note = AERO_PENDING_TEXT if AERO["status"] != "done" else ("Range uses the CFD drag area of %s m\u00b2" % AERO["cda"])
    # page 1
    b = ('<div style="display:flex;gap:0.25in;align-items:center;margin-bottom:10pt"><img src="%s" style="width:4.5in;flex:none;display:block">'
         '<div><div class="stamp">Bavuso Motors &middot; Summary</div>'
         '<h1 style="font-size:15pt;margin-top:4pt">Bavuso V1<br>Electric adventure-touring motorcycle</h1>'
         '<div style="color:#6F6B66;font-size:9.5pt">Rev E design freeze, November 22, 2026</div></div></div>') % (I.get("hero", ""),)
    b += '<div class="lead" style="font-size:10pt">Under 400 lb and 200 miles at 70 mph cannot both close with today\u2019s cells. A 400 lb bike carries only about 11 kWh (about 74 mi), and 200 mi needs about 32 kWh and a 631 lb bike. V1 is a <b>deliberate compromise</b>. I chose a buildable bike: <b>about 258 kg / 569 lb, 23.8 kWh, about 130 mi at 70 mph, 125 mph sustained and native NACS charging</b>, with a planned path to better range and lower mass.</div>'
    b += kpis([("%s kg" % F["mass_kg"], "Wet mass", "%s lb; T1 at most 260 kg" % F["mass_lb"]), ("%s kWh" % F["kwh_gross"], "Pack, gross", "%s kWh usable, %s V" % (F["kwh_usable"], F["volts"])),
               ("%s mi" % AERO["r70"], "Range, 70 mph", "calculated, CdA %s%s" % (AERO["cda"], " assumed" if AERO["status"] != "done" else "")), ("%s kW" % F["peak_kw"], "Peak power", "%s kW continuous" % F["cont_kw"]),
               ("%s s" % F["z60"], "0-60 mph", "calculated"), ("125 mph", "Sustained", "%s limit, governed %s" % (F["top"], F["gov"])),
               ("~%s min" % F["chg"], "DC 10-80%", "NACS, 25 C"), ("$%sk" % F["cost10"], "Unit cost, 10k/yr", "estimate")])
    b += table(["", "Bavuso V1", "Energica Experia", "Zero DSR/X", "BMW R 1300 GS"], [
        ("Wet mass", "%s kg / %s lb" % (F["mass_kg"], F["mass_lb"]), "260 kg / 573 lb", "247 kg / 544 lb", "237 kg / 523 lb"),
        ("Energy", "%s kWh" % F["kwh_gross"], "22.5 kWh", "17.3 kWh", "petrol"),
        ("Range at 70 mph", "%s mi (calculated)" % AERO["r70"], "130 mi claimed at 68 mph", "85 mi claimed", "n/a"),
        ("Charging", "Native NACS", "CCS", "no DC fast charge", "n/a")], cls="tight", widths=["16%", "26%", "22%", "20%", "16%"])
    b += p("Competitor figures from published pages (`01-targets.md`); V1 figures are calculations.", "small")
    if AERO["status"] != "done":
        b += callout("**" + AERO_PENDING_TEXT + "** (152.4 / 132.2 mi at 70 / 77 mph).")
    S.add("Summary", "Summary", b)
    # page 2
    b = title("", "What was designed and what it proves")
    b += cols2_summary()
    b += h2("Targets T1 to T10")
    short = [("T1", "Mass at most 260 kg", "met-thin", "257.9 kg; 2.1 kg headroom; nothing weighed"),
             ("T2", "Pack 100s11p, 23.8 kWh, at most 108 kg", "met", "23.76 kWh, 360 V, 108.0 kg"),
             ("T3", "Range at least 145 mi at 70 mph", "not met", "%s mi at the CFD CdA %s; needs about 0.407" % (AERO["r70"], AERO["cda"])),
             ("T4", "125 mph sustained", "met-thin", "135 mph limit; derate to about 105 mph at 38 C; not verified"),
             ("T5", "At least 90 kW peak, 55 kW continuous", "met-thin", "124 kW; 93 kW at 10% charge; 61.6 kW continuous"),
             ("T6", "NACS, DC 10-80% in 25 min or less", "met-thin", "about 21 min at 25 C; Supercharger access not established"),
             ("T7", "Solo 90 kg + 25 kg luggage", "met-thin", "FEA at final mass + rider + luggage; thin factors; not tested"),
             ("T8", "Comfort and stability", "met-thin", "stable only with the scheduled damper"),
             ("T9", "Unit cost at most $32k at 10k/yr", "met-thin", "$29.5k estimate; $32.3k at 1k cell, motor, inverter prices"),
             ("T10", "Frozen appearance", "met-thin", "pods, edge radii, second line open (V1.1)")]
    b += table(["#", "Target", "Verdict", "Evidence"], [(a, bb, pill(c), d) for a, bb, c, d in short], cls="tight", widths=["5%", "30%", "13%", "52%"])
    b += h2("Roadmap, V1.1 and beyond")
    b += p("Better cells add range at the same mass, and aero refinement lowers drag. A lighter chassis has about 10 kg of identified levers: wheels and brakes, a short HV bus, an aluminium yoke, a cell-to-chassis pack and flush radiator pods. Styling refinement (pods, edge radii) and a two-up variant follow.")
    b += callout("**This is a simulation- and analysis-based design.** Nothing has been built or physically tested, and supplier prices are estimates. %s. The full dossier (`Bavuso-V1-Design-Dossier.pdf`) carries the validation, cost, compliance and verification detail. Bavuso Motors prepared it, with AI engineering agents (Claude) doing the engineering analysis under my direction." % aero_note)
    S.add("Summary", "Summary", b)
    return S


def cols2_summary():
    return ('<div class="cols2"><div>' + h2("Design") + ul([
        "Pack: Molicel P60B 21700, 100s11p, in a structural aluminium case that forms the lower body (108.0 kg).",
        "Drive: EMRAX 228 and Cascadia CM200DX, 8 mm Gates belt at 3.60:1 (23.65 kg).",
        "Chassis: steel frame with cast nodes, steel pivot yoke, cast A356 single-sided arm (about 31 kg).",
        "Speed-scheduled semi-active steering damper; carbon wheels; 320 mm front discs."]) + h2("Analysis done") + ul([
        "Structures (FEA), thermal, dynamics, drive and electrical models; mass ledger tied to the BOM; independent review.",
        "Cost $29.5k at 10k/yr, $39.3k at 1k, $58.0k at 100 (estimates).",
        "91 of 91 CAD envelope checks; 45-row compliance matrix; 48-row DFMEA; $7.04M, 28-month verification plan."]) +
        '</div><div>' + h2("Mass, 328 to 258 kg") + ul([
        "Concept ledger 328.4 kg, reconciled 319.6 kg, rev C CAD 255.3 kg, final 257.9 kg.",
        "The pack, body panels and wiring gave most of the saving. The chassis grew to about 31 kg because the belt-on-one-side layout needs a steel yoke.",
        "Mass headroom is 2.1 kg, and the ledger\u2019s growth rule gives about 287 kg."]) + h2("Limits") + ul([
        "Range is calculated at an assumed CdA (break-even about 0.407).",
        "Real-world range is about 15 to 20% lower than calculated.",
        "No part weighed, no test run, no supplier quote.",
        "Supercharger access not established."]) + '</div></div>')


# ----------------------------------------------------------------------------- spec cross-check
def check_against_spec():
    """Verify that each headline value used in the dossier appears in 00-V1-final-spec.md."""
    spec = re.sub(r"\s+", " ", (PROG / "00-V1-final-spec.md").read_text(encoding="utf-8"))
    bad = []
    probes = {k: v for k, v in F.items()}
    probes.update({"rollup": "257.9", "wb": "1,490", "belt": "545.9", "rear disc": "267 x 5", "front disc": "320 x 5",
                   "z545": "Z545", "damper": "0.028", "cell": "100s11p", "esc": "3.60:1", "dc cap": "350 A", "fuse": "450 A",
                   "break-even": "0.407", "r70r77": "152.4 / 132.2", "cfd range": "131.8 / 113.4", "cfd cda": "0.43 to 0.46", "charge": "23.0 min at 35 C", "charge2": "25.4 min at -10 C",
                   "charge3": "40.9 min at 45 C", "peaks": "124 / 109 / 100 / 93 / 87"})
    skip = {"cost_stress", "z100kmh", "z100mph"}
    for k, v in probes.items():
        if k in ("cg", "seat", "wheelbase", "t1_lb", "chg", "months", "dvpr", "ledger_growth", "ac_time", "cost_stress", "cost1", "cost100", "cost10"):
            val = v
        else:
            val = v
        # normalise a few spec formats
        needle = val
        if k == "cost10":
            needle = "$29.5k"
        if k == "cost1":
            needle = "$39.3k"
        if k == "cost100":
            needle = "$58.0k"
        if k == "cost_stress":
            needle = "$32.3k"
        if k == "dvpr":
            needle = "$7.04M"
        if k == "months":
            needle = "28 months"
        if k == "ledger_growth":
            needle = "287 kg"
        if k == "chg":
            needle = "about 21 min"
        if k == "cg":
            needle = "787 mm ahead of the rear axle, 529 mm high"
        if k == "z100kmh":
            needle = "4.31 s"
        if k == "z100mph":
            needle = "7.26 s"
        if k == "ac_time":
            needle = "3.1 h"
        if k == "gov":
            needle = "governed at 130"
        if k == "top":
            needle = "135 mph"
        if k == "volts":
            needle = "360 V"
        if k == "mass_lb":
            needle = "569 lb"
        if k == "mass_kg":
            needle = "257.9 kg"
        if k == "headroom":
            needle = "2.1 kg"
        if k == "t1_kg":
            needle = "260 kg"
        if k == "t1_lb":
            needle = "573 lb"
        if k == "cdA":
            needle = "0.38"
        if k == "pack_kg":
            needle = "108.0 kg"
        if k == "peak_kw":
            needle = "124 kW"
        if k == "cont_kw":
            needle = "61.6 kW"
        if k == "kwh_gross":
            needle = "23.76 kWh"
        if k == "kwh_usable":
            needle = "21.4 kWh"
        if k == "r70":
            needle = "152.4"
        if k == "r77":
            needle = "132.2"
        if k == "p125":
            needle = "43.5 kW"
        if k == "z60":
            needle = "4.15 s"
        if k == "z60_lug":
            needle = "4.44 s"
        if k == "z60_wet":
            needle = "5.47 s"
        if k == "r60_100":
            needle = "3.12 s"
        if k == "cda_break":
            needle = "0.407"
        if needle not in spec:
            bad.append((k, needle))
    return bad


# ----------------------------------------------------------------------------- pdf
def to_pdf(html_path, pdf_path):
    ud = tempfile.mkdtemp(prefix="edge-dossier-")
    cmd = [EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=20000", "--user-data-dir=" + ud, "--print-to-pdf=" + str(pdf_path), html_path.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    ok = pdf_path.exists() and pdf_path.stat().st_size > 10000
    return ok, r.stderr[-400:]


def layout_report(html_path):
    ud = tempfile.mkdtemp(prefix="edge-dossier-")
    cmd = [EDGE, "--headless", "--disable-gpu", "--virtual-time-budget=20000", "--user-data-dir=" + ud, "--dump-dom", html_path.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240, encoding="utf-8", errors="replace")
    m = re.search(r"id=\"layout-report\"[^>]*>LAYOUT:([^<]*)", r.stdout)
    return m.group(1).strip() if m else "no report"


def pdf_pages(pdf_path):
    data = pdf_path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def main():
    no_pdf = "--no-pdf" in sys.argv
    OUT.mkdir(exist_ok=True)
    setup_mpl()
    I = prep_images()
    D = build(I)
    toc_pg = [pg for pg in D.pages if pg["html"] == "@@TOC@@"][0]
    toc_pg["html"] = toc_html(D)
    html_main = OUT / "Bavuso-V1-Design-Dossier.html"
    html_main.write_text(D.render(), encoding="utf-8")
    # cover has its own <section>: render() already includes raw cover
    S = build_summary(I, D)
    html_sum = OUT / "Bavuso-V1-Summary.html"
    html_sum.write_text(S.render(), encoding="utf-8")
    print("pages: dossier %d, summary %d" % (len(D.pages), len(S.pages)))
    print("aero status:", AERO["status"])
    bad = check_against_spec()
    print("spec cross-check:", "all %d headline values found in 00-V1-final-spec.md" % len(F) if not bad else "MISMATCH %s" % bad)
    if no_pdf:
        return
    for h, pdf, n in [(html_main, OUT / "Bavuso-V1-Design-Dossier.pdf", len(D.pages)), (html_sum, OUT / "Bavuso-V1-Summary.pdf", len(S.pages))]:
        print(h.name, "layout:", layout_report(h))
        ok, err = to_pdf(h, pdf)
        print(pdf.name, "ok" if ok else "FAILED " + err, "pdf pages:", pdf_pages(pdf) if ok else "-", "(html pages %d)" % n)


if __name__ == "__main__":
    main()
