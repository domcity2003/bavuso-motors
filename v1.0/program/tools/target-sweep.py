"""Bavuso V1 target sweep: range vs weight vs drag vs pack density vs rest-of-bike mass.

Run from v1.0 with FreeCAD python:
  ../.tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe program/tools/target-sweep.py

Road-load model = review page 5 / research/range-weight-budget.md:
  P_wheel = (0.5*rho*CdA*v^2 + Crr*m*g)*v ; P_batt = P_wheel/0.90 + 300 W
  usable = 90% of gross ; rider 90 kg ; flat still air.

Mass model (the part that is new):
  pack_kg   = gross_kWh*1000 / pack_Wh_per_kg
  bike_kg   = pack_kg + rest_kg
  rest_kg   = rest_ref + K_SEC*(pack_kg - PACK_REF)   (secondary-mass compounding)
rest_ref is the mass outside the pack for a bike carrying a PACK_REF (100 kg) pack.
K_SEC = 0.15: frame, swingarm, wheels, tyres, brakes, fork and shock (about 55 kg of the
rest) are sized by loaded mass (bike + rider); 55 / ~330 kg loaded ~= 0.17, rounded down
because minimum-gauge limits stop part of it scaling. So each kg of pack saved also saves
about 0.15 kg elsewhere (and costs 0.15 kg per kg added).
The model solves bike mass and gross kWh together (rolling resistance depends on mass).
"""
import csv
import os
import itertools
import numpy as np

RHO, CRR, G, ETA, AUX, USABLE, RIDER = 1.225, 0.015, 9.80665, 0.90, 300.0, 0.90, 90.0
MPH = 0.44704
PACK_REF, K_SEC = 100.0, 0.15


def p_wheel(v_mph, cda, m_tot):
    v = v_mph * MPH
    return (0.5 * RHO * cda * v ** 2 + CRR * m_tot * G) * v


def p_batt(v_mph, cda, m_tot):
    return p_wheel(v_mph, cda, m_tot) / ETA + AUX


def wh_per_mile(v_mph, cda, m_tot):
    return p_batt(v_mph, cda, m_tot) / v_mph


def solve(range_mi, cda, whkg, rest_ref, rider=RIDER, v=70.0):
    """Fixed point: bike mass <-> gross kWh."""
    bike = 200.0
    for _ in range(200):
        gross = range_mi * wh_per_mile(v, cda, bike + rider) / 1000.0 / USABLE
        pack = gross * 1000.0 / whkg
        rest = rest_ref + K_SEC * (pack - PACK_REF)
        new = pack + rest
        if abs(new - bike) < 1e-6:
            bike = new
            break
        bike = new
    return dict(gross=gross, pack=pack, rest=rest, bike=bike, whmi=wh_per_mile(v, cda, bike + rider))


def range_for(gross, cda, whkg, rest_ref, rider=RIDER, v=70.0):
    pack = gross * 1000.0 / whkg
    bike = pack + rest_ref + K_SEC * (pack - PACK_REF)
    return gross * USABLE * 1000.0 / wh_per_mile(v, cda, bike + rider), bike


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(here, "..", "data")
    os.makedirs(data, exist_ok=True)
    ranges = list(range(100, 221, 10))
    cdas = [0.33, 0.35, 0.37, 0.39, 0.41, 0.43]
    whkgs = [200, 220, 240, 260, 280]
    rests = [105, 115, 125, 135, 145, 160]
    rows = []
    for r, c, w, rs in itertools.product(ranges, cdas, whkgs, rests):
        s = solve(r, c, w, rs)
        rows.append([r, c, w, rs, round(s['gross'], 2), round(s['pack'], 1), round(s['rest'], 1),
                     round(s['bike'], 1), round(s['bike'] * 2.20462), round(s['whmi'], 1)])
    with open(os.path.join(data, "target-sweep.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["range70_mi", "CdA_m2", "pack_Wh_per_kg", "rest_ref_kg", "gross_kWh", "pack_kg",
                     "rest_kg_after_compounding", "bike_kg_wet", "bike_lb_wet", "Wh_per_mile_at_70"])
        wr.writerows(rows)
    print("rows", len(rows))

    # sanity: reproduce review numbers (no compounding involved)
    wh = wh_per_mile(70, 0.377, 328.37 + 90)
    print("check review p5: 200 mi, CdA .377, 328.4 kg -> %.2f kWh gross (review: 32.7)" % (200 * wh / 1000 / USABLE))
    wh = wh_per_mile(70, 0.330, 181.44 + 90)
    print("check review p3: 200 mi, CdA .330, 181.4 kg -> %.2f kWh gross (review: 27.2)" % (200 * wh / 1000 / USABLE))

    CDA, WHKG, REST = 0.38, 230, 130
    print("\nCENTRAL CdA %.2f, %d Wh/kg, rest_ref %d kg" % (CDA, WHKG, REST))
    print("range  gross  pack  rest  bike_kg bike_lb  dKg_per_10mi")
    prev = None
    for r in range(80, 221, 10):
        s = solve(r, CDA, WHKG, REST)
        d = "" if prev is None else "%.1f" % (s['bike'] - prev)
        print("%4d %6.1f %5.1f %5.1f %6.1f %6.0f   %s" % (r, s['gross'], s['pack'], s['rest'], s['bike'], s['bike'] * 2.20462, d))
        prev = s['bike']

    print("\nPOWER at 125/130 mph, bike 230 kg + 90 kg rider")
    for c in (0.33, 0.38, 0.43):
        for v in (125, 130):
            pw = p_wheel(v, c, 320) / 1000
            print("CdA %.2f %d mph: wheel %.1f kW, battery %.1f kW (with +15%% for grade/wind: %.1f kW)" %
                  (c, v, pw, pw / ETA + 0.3, 1.15 * pw / ETA + 0.3))
    print("\nC-rate for steady 125 mph (CdA .38) and 90 kW peak; 10-80% time")
    pb = p_wheel(125, 0.38, 320) / 1000 / ETA + 0.3
    for gross in (18, 20, 22, 24, 26, 28, 32):
        print("gross %2d kWh: 125 mph cruise %.1f kW = %.2fC | 90 kW = %.1fC | 10-80%% at avg 2C: %.0f min, 3C: %.0f min" %
              (gross, pb, pb / gross, 90.0 / gross, 0.7 * 60 / 2, 0.7 * 60 / 3))
    print("\nMiles added in a 20-min stop (about 135 Wh/mi at 70 mph incl. aux, 90% charge-side ignored)")
    for gross in (20, 24, 28):
        for c in (2.0, 3.0):
            e = min(0.7 * gross, c * gross * 20 / 60)
            print("gross %d kWh, avg %.0fC: %.1f kWh in 20 min -> %.0f mi" % (gross, c, e, e * 1000 / 135.0))

    # ---- recommended point: 23 kWh gross, 100 kg pack at 230 Wh/kg, 240 kg wet incl. 12 kg margin ----
    print("\nRECOMMENDED POINT: 23.0 kWh gross, bike fixed at 240.0 kg (margin counted as real mass)")
    E, BIKE = 23.0, 240.0
    for c in (0.33, 0.36, 0.38, 0.40, 0.43):
        wh = wh_per_mile(70, c, BIKE + 90)
        print("  CdA %.2f: %.0f Wh/mi, 70 mph range %.0f mi; 75 mph %.0f mi; 77 mph %.0f mi" % (
            c, wh, E * USABLE * 1000 / wh,
            E * USABLE * 1000 / wh_per_mile(75, c, BIKE + 90) / 1.0 * 75 / 75,
            E * USABLE * 1000 / wh_per_mile(77, c, BIKE + 90)))
    wh2 = wh_per_mile(70, 0.38 + 0.06, BIKE + 8 + 90 + 80)
    print("  two-up (+80 kg, +8 kg structure, CdA +0.06): %.0f mi" % (E * USABLE * 1000 / wh2))
    print("  density sensitivity at 240 kg fixed mass: 200 Wh/kg -> pack %.0f kg (+%.0f kg vs 230); 245 -> %.0f kg" % (
        E * 1000 / 200, E * 1000 / 200 - E * 1000 / 230, E * 1000 / 245))
    print("  extremes (rest_ref 140 incl. margin, CdA .38, 230 Wh/kg):")
    s = solve(200, 0.38, 230, 140)
    print("    200 mi: %.1f kWh, pack %.0f kg, bike %.0f kg = %.0f lb" % (s['gross'], s['pack'], s['bike'], s['bike'] * 2.20462))
    for target_kg in (181.44,):
        lo, hi = 1.0, 400.0
        for _ in range(60):
            mid = (lo + hi) / 2
            r, b = range_for(mid * 0.0 + (mid), 0.38, 230, 140)
            if b > target_kg:
                hi = mid
            else:
                lo = mid
        r, b = range_for(lo, 0.38, 230, 140)
        print("    400 lb (181.4 kg): %.1f kWh gross -> %.0f mi at 70 mph" % (lo, r))
    r, b = range_for(23.0, 0.38, 230, 140)
    print("    23 kWh via model: %.0f mi, %.0f kg" % (r, b))
    print("  secondary-mass effect: 1 kWh = %.2f kg pack + %.2f kg compounding" % (1000 / 230, K_SEC * 1000 / 230))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
    rr = np.arange(80, 221, 5)
    for cda, ls in ((0.33, ':'), (0.38, '-'), (0.43, '--')):
        ax[0].plot(rr, [solve(r, cda, 230, 130)['bike'] * 2.20462 for r in rr], ls, label="CdA %.2f" % cda)
    ax[0].axhline(400, color='r', lw=0.8)
    ax[0].text(82, 408, "400 lb owner preference", color='r', fontsize=8)
    ax[0].axvline(160, color='g', lw=0.8, alpha=.6)
    ax[0].set_xlabel("range at 70 mph (mi)")
    ax[0].set_ylabel("bike mass, wet (lb)")
    ax[0].set_title("Mass needed for a range\n(230 Wh/kg pack, rest-of-bike 130 kg)")
    ax[0].legend()
    ax[0].grid(alpha=.3)
    for w in (200, 230, 260, 280):
        ax[1].plot(rr, [solve(r, 0.38, w, 130)['bike'] * 2.20462 for r in rr], label="%d Wh/kg" % w)
    ax[1].axhline(400, color='r', lw=0.8)
    ax[1].axvline(160, color='g', lw=0.8, alpha=.6)
    ax[1].set_xlabel("range at 70 mph (mi)")
    ax[1].set_title("Pack density (CdA 0.38, rest 130 kg)")
    ax[1].legend()
    ax[1].grid(alpha=.3)
    for rs in (105, 120, 130, 145, 160):
        ax[2].plot(rr, [solve(r, 0.38, 230, rs)['bike'] * 2.20462 for r in rr], label="rest %d kg" % rs)
    ax[2].axhline(400, color='r', lw=0.8)
    ax[2].axvline(160, color='g', lw=0.8, alpha=.6)
    ax[2].set_xlabel("range at 70 mph (mi)")
    ax[2].set_title("Rest-of-bike mass (CdA 0.38, 230 Wh/kg)")
    ax[2].legend()
    ax[2].grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(os.path.join(data, "target-sweep.png"), dpi=130)
    print("chart written")
