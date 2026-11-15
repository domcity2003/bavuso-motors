"""Bavuso V1.0 adventure: HV + LV connection schematic.

November 12, 2026, US Central. Claude Opus 5.5 (claude-opus-5-5).
Writes detailed-design/electrical/schematic.mmd (Mermaid source, renders on GitHub) and draws the same
block diagram with matplotlib to schematic.svg and schematic.png (no Graphviz/Mermaid CLI on this machine).
Run from v1.0 with the FreeCAD python (has matplotlib).
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R = Path(__file__).resolve().parents[2]
OUT = R / 'detailed-design' / 'electrical'

# node: (x, y, w, h, label, group)
N = {
 'L1': (0.5, 7.6, 2.6, 1.0, 'Lane 1  S001-S033\n33s6p 119 V nom\nmodules M11-M13', 'pack'),
 'L2': (0.5, 6.1, 2.6, 1.0, 'Lane 2  S034-S066\n(snake reversed)\nmodules M21-M23', 'pack'),
 'L3': (0.5, 4.6, 2.6, 1.0, 'Lane 3  S067-S099\n33s6p\nmodules M31-M33', 'pack'),
 'MSD': (3.6, 5.35, 2.2, 0.9, 'MSD + 400 A fuse\nAmphenol MSD08\n(link S066|S067, HVIL)', 'rjb'),
 'IVT': (3.6, 9.0, 2.2, 0.8, 'IVT-S-500-U3 shunt\nI + U1 pack U2 bus U3 inlet', 'rjb'),
 'KN': (3.6, 10.1, 2.2, 0.7, 'GX14 main- contactor', 'rjb'),
 'PYRO': (6.6, 3.9, 2.2, 0.75, 'Sensata STP500P\npyro breaker (pack+)', 'bdu'),
 'KP': (6.6, 5.0, 2.2, 0.7, 'GX14 main+ contactor', 'bdu'),
 'PRE': (6.6, 6.0, 2.2, 0.85, 'Precharge: LEV100 relay\n+ HSC100 220 ohm', 'bdu'),
 'BUSP': (9.4, 5.3, 0.35, 5.4, 'HV+\nbus', 'bus'),
 'BUSN': (9.95, 5.3, 0.35, 5.4, 'HV-\nbus', 'bus'),
 'F1': (11.0, 10.0, 1.8, 0.6, 'EV fuse 30 A', 'bdu'),
 'F2': (11.0, 9.1, 1.8, 0.6, 'EV fuse 10 A', 'bdu'),
 'F3': (11.0, 8.2, 1.8, 0.6, 'EV fuse 15 A', 'bdu'),
 'INV': (13.4, 6.4, 2.4, 1.0, 'SiC inverter 400 A\n(CM200DX envelope)', 'drive'),
 'MOT': (16.4, 6.4, 2.2, 1.0, 'Radial IPM motor\n130 kW / 150 Nm', 'drive'),
 'OBC': (13.4, 9.9, 2.4, 0.8, 'OBC BROGEN PV1776\n6.6 kW', 'chg'),
 'DCDC': (13.4, 8.9, 2.4, 0.8, 'DC-DC 1 kW class\n(HELLA HV DC/DC)', 'lv'),
 'HTR': (13.4, 8.0, 2.4, 0.7, 'Pack PTC heater (opt.)', 'chg'),
 'CJB': (13.4, 3.2, 2.4, 1.3, 'CJB: 2 x GX14 DC charge\n+ 2-pole AC relay\n(interlocked)', 'chg'),
 'INLET': (16.4, 3.4, 2.2, 0.9, 'NACS inlet\nVolex 1000 V 500 A', 'chg'),
 'EVCC': (16.4, 1.9, 2.2, 0.8, 'ADVANTICS\nADM-CS-EVCC', 'ctl'),
 'IMD': (6.6, 1.4, 2.2, 0.8, 'Bender iso175\ninsulation monitor', 'ctl'),
 'BMS': (0.5, 2.8, 2.6, 1.0, 'Orion BMS2 108\n9 groups x 11 taps\n+ TEM (67 NTC)', 'ctl'),
 'VCU': (3.6, 1.2, 2.2, 1.0, 'VCU (AEM VCU200)\ncontactor + pyro drive\nHVIL, keyless gate', 'ctl'),
 'BAT12': (11.0, 1.2, 1.8, 0.8, '12 V LiFePO4\nShorai LFX14A4', 'lv'),
 'PDM': (13.4, 0.7, 2.4, 1.6, 'LV PDM (smart fuses)\nlights, dash, ABS,\npumps, fans, grips,\nUSB, keyless', 'lv'),
}
COL = {'pack': '#f4c27a', 'rjb': '#f2a59b', 'bdu': '#f2a59b', 'bus': '#d9534f', 'drive': '#9cc3e6', 'chg': '#a8d5a2', 'lv': '#e6e6a8', 'ctl': '#cbb7e3'}
E = [  # from, to, kind (hv/lv/can/sense), label
 ('L1', 'L2', 'hv', 'S033|S034 top link'), ('L2', 'MSD', 'hv', 'S066'), ('MSD', 'L3', 'hv', 'S067'),
 ('L3', 'PYRO', 'hv', 'pack+ 50 mm2'), ('PYRO', 'KP', 'hv', ''), ('KP', 'BUSP', 'hv', ''), ('PYRO', 'PRE', 'hv', ''), ('PRE', 'BUSP', 'hv', ''),
 ('L1', 'IVT', 'hv', 'pack- 50 mm2'), ('IVT', 'KN', 'hv', ''), ('KN', 'BUSN', 'hv', 'HV- 50 mm2'),
 ('BUSP', 'INV', 'hv', 'DC 2x50 mm2'), ('INV', 'MOT', 'hv', 'U V W 3x50 mm2'),
 ('BUSP', 'F1', 'hv', ''), ('F1', 'OBC', 'hv', '4 mm2'), ('BUSP', 'F2', 'hv', ''), ('F2', 'DCDC', 'hv', '2.5 mm2'),
 ('BUSP', 'F3', 'hv', ''), ('F3', 'HTR', 'hv', ''),
 ('BUSP', 'CJB', 'hv', 'DC chg 2x50 mm2'), ('CJB', 'INLET', 'hv', 'DC+/- (shared AC pins)'), ('CJB', 'OBC', 'hv', 'AC L/N'),
 ('DCDC', 'PDM', 'lv', '16 mm2 13.5 V'), ('BAT12', 'PDM', 'lv', '10 mm2'),
 ('BMS', 'L1', 'sense', '100 taps 22 AWG'), ('INLET', 'EVCC', 'lv', 'CP/PP, lock, NTC'),
 ('VCU', 'KN', 'lv', 'coil'), ('VCU', 'KP', 'lv', 'coil'), ('VCU', 'PRE', 'lv', 'coil'), ('VCU', 'PYRO', 'lv', 'squib'),
 ('IMD', 'BUSN', 'sense', ''), ('IMD', 'BUSP', 'sense', ''),
 ('VCU', 'BMS', 'can', 'CAN1'), ('VCU', 'IMD', 'can', 'CAN1'), ('VCU', 'BAT12', 'can', ''), ('VCU', 'EVCC', 'can', 'CAN1'),
]
EC = {'hv': '#c0392b', 'lv': '#7f6000', 'can': '#2e7d32', 'sense': '#6a1b9a'}

def anchor(n, other):
    x, y, w, h = N[n][:4]
    ox, oy = N[other][0] + N[other][2] / 2, N[other][1] + N[other][3] / 2
    cx, cy = x + w / 2, y + h / 2
    if abs(ox - cx) * h > abs(oy - cy) * w:
        return (x + w if ox > cx else x, cy)
    return (cx, y + h if oy > cy else y)

fig, ax = plt.subplots(figsize=(19, 12))
for k, (x, y, w, h, lab, g) in N.items():
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03', fc=COL[g], ec='#333', lw=1))
    ax.text(x + w / 2, y + h / 2, lab, ha='center', va='center', fontsize=7.6)
for a, b, kind, lab in E:
    p, q = anchor(a, b), anchor(b, a)
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-', color=EC[kind], lw=2.2 if kind == 'hv' else 1.2,
                                                    ls='--' if kind in ('can', 'sense') else '-'))
    if lab:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.08, lab, fontsize=6.3, color=EC[kind], ha='center')
for g, (x0, y0, x1, y1, t) in {'pack': (0.3, 4.4, 3.3, 8.8, 'Structural pack 99s6p, 594 x 26120, 416 V max'),
                               'rjb': (3.4, 4.9, 6.0, 11.0, 'RJB (rear, below pivot)'),
                               'bdu': (6.4, 3.7, 13.0, 11.0, 'BDU (tank rear bay)')}.items():
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ls=':', ec='#555'))
    ax.text(x0 + 0.05, y1 - 0.25, t, fontsize=8, style='italic')
for i, (k, c) in enumerate(EC.items()):
    ax.plot([0.4, 0.9], [0.5 - 0.3 * i, 0.5 - 0.3 * i], color=c, lw=2, ls='--' if k in ('can', 'sense') else '-')
    ax.text(1.0, 0.45 - 0.3 * i, {'hv': 'HV power', 'lv': '12 V power / discrete', 'can': 'CAN', 'sense': 'sense'}[k], fontsize=8)
ax.set_xlim(0, 19); ax.set_ylim(-0.6, 11.3); ax.axis('off')
ax.set_title('Bavuso V1.0 adventure - HV/LV connection schematic (Nov 12, 2026, Claude Opus 5.5). Block level, not a wiring drawing.', fontsize=11)
fig.savefig(OUT / 'schematic.svg'); fig.savefig(OUT / 'schematic.png', dpi=130)

with open(OUT / 'schematic.mmd', 'w') as f:
    f.write('%% Bavuso V1.0 adventure HV/LV schematic, Nov 12 2026, Claude Opus 5.5\nflowchart LR\n')
    for k, (x, y, w, h, lab, g) in N.items():
        f.write(f'  {k}["{lab.replace(chr(10), "<br/>")}"]\n')
    for a, b, kind, lab in E:
        arrow = '-.-' if kind in ('can', 'sense') else '---'
        f.write(f'  {a} {arrow}' + (f'|{lab}|' if lab else '') + f' {b}\n')
print('written', OUT / 'schematic.svg')
