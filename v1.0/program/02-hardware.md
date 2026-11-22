# Bavuso V1 hardware sourcing (light re-architecture)

> **Superseded in part (Nov 22, 2026).** This document predates the final V1 numbers; the authority is `00-V1-final-spec.md`. Final: 257.9 kg / 569 lb (T1 <= 260 kg, 2.1 kg headroom), pack 100s11p 108.0 kg, 360 V, 23.76 kWh gross, CAD rev E, cost $29.5k at 10k/yr. All of it is analysis or estimate; nothing is built or weighed. Stale here: the EMRAX 188 + emDrive H100 drive (final EMRAX 228 LC LV+43% + Cascadia CM200DX, 23.65 kg); 100s10p, 21.6 kWh, 93.75 kg, 370 V (final 100s11p, 23.76 kWh, 108.0 kg, 360 V); the single 3.8:1 belt (final 8MGT 35T/126T, 3.60:1, 62 mm); 0-60 of 4.5-5 s (final 4.15 s); the 328.4 kg starting bike; dual 300 mm front discs (final 320 x 5 front, 267 x 5 rear).


November 21, 2026, US Central. Prepared by Claude Sonnet 5.5 (claude-sonnet-5-5) for the Bavuso V1 program.

Data: `program/data/hardware-shortlist.csv` (one recommended row plus one alternate per slot; `REC:` / `ALT:` / `STRETCH:` prefixes). Today's masses come from `mass-rollup.csv` (328.4 kg bike). Every number is labelled supplier (published), calculated, or estimate in the CSV.

## The plain answer

**A recommended set of real parts weighs about 163 kg, against 241 kg for the same lines today: 77 kg lighter. Of that, 37 kg is lighter hardware and 40 kg is a smaller battery (21.6 kWh instead of 32.7 kWh).**

The biggest single wins:
1. **Motor and drive: 31.5 kg down to 14.5 kg (-17 kg).** Swap the high-speed radial motor and 2-stage gearbox for an EMRAX 188 axial-flux motor (7.9 kg, published) on a single-stage belt, with a smaller inverter. The catch is peak power: 60 kW and 100 Nm, so 0-60 mph is slower than the old 2.7-3.0 s goal (my rough hand estimate is 4.5-5 s; not simulated).
2. **HV and charging electronics: 21.6 kg down to 12.9 kg (-8.7 kg)** by merging junction boxes, using a 3.3 kW instead of 6.6 kW charger, and deleting a duplicated DC-DC line.
3. **Cooling: 10.8 kg down to 6.0 kg (-4.8 kg).** One shared loop instead of two radiators and two pumps.
4. **Chassis parts: about -7 kg** (fork, shock, tyres, brakes, ABS), mostly estimates.

**The pack is the weight driver, and the cell choice matters more than any other part.** At 21.6 kWh the Molicel P60B pack is about 94 kg. An Amprius SA504 pouch pack would be about 71 kg (-23 kg more) but it is a sample-grade cell with 500-cycle life and no published price. I recommend P60B now, and keeping SA504 as the one stretch option if the target must be at or below about 225 kg.

**Cooling: the motor can run on air at cruise but not at top speed.** The EMRAX 188 air-cooled is rated 27 kW continuous; 125 mph needs about 41 kW at the shaft (`detailed-design` analysis). The inverter and pack need liquid anyway, so I put the motor on the same loop.

## Verdict table (recommended set versus today)

Today's "equivalent lines" are the `mass-rollup.csv` items listed in the last column.

| System | Recommended pick | New kg | Today kg | Change kg | Today's lines |
|---|---|---:|---:|---:|---|
| Cells + pack structure | Molicel P60B 100s10p, 21.6 kWh, structural case | 93.75 | 133.65 | -39.9 | Cell lanes, pack internals, 4 mm case (32.7 kWh) |
| Motor, inverter, reduction | EMRAX 188 CC + emDrive H100 + 1-stage belt | 14.5 | 31.5 | -17.0 | IPM envelope, CM200, pulleys, belt, gear oil, oil cooler |
| Cooling | Single shared loop | 6.0 | 10.75 | -4.75 | Radiators, fans, PTC, pumps, valve, coolant allowance |
| Charger, DC-DC, BMS, HV box, cables, inlet | 3.3 kW OBC, 0.8 kW DC-DC, Orion BMS2, one HV box, Volex NACS | 12.9 | 21.63 | -8.7 | OBC, 2 DC-DC lines, BMS, 2 junction boxes, 2 GX14, cables, inlets, cabinet |
| Fork | 43 mm USD, 170 mm | 6.8 | 8.8 | -2.0 | Outer and inner tubes, axle clamps |
| Rear shock | Ohlins STX 46 class | 3.0 | 4.4 | -1.4 | Body, spring, reservoir, rod, eyes |
| Wheels | Forged 19x3.0 / 17x4.5 | 7.6 | 7.6 | 0.0 | Front and rear wheel |
| Tyres | 110/80R19 + 150/70R17 | 9.1 | 10.9 | -1.8 | Nominal tyres |
| Brakes | Dual 320 mm + Stylema, 267 x 5 rear (final, rev E) | 8.58 | 9.68 | -1.1 | Discs, calipers, levers, hoses, masters |
| ABS | Bosch ABS 10 class | 1.1 | 1.6 | -0.5 | ABS allowance |
| **Total** | | **163.3** | **240.5** | **-77.2** | |
| Total without the pack | | 69.6 | 106.9 | -37.3 | |

If the target pack is a different size, scale the pack line: P60B pack is about 4.34 kg per kWh (18 kWh = 78 kg; 28 kWh = 122 kg). SA504 pouch is about 3.29 kg per kWh (18 kWh = 59 kg; 28 kWh = 92 kg).

## 1. Cells

| Cell | Wh | Mass | Cell Wh/kg | Discharge / charge | Source | Role |
|---|---:|---:|---:|---|---|---|
| Molicel P60B (21700) | 21.6 | 75 g max | 288 | 60 A std, 100 A max / charge not confirmed | [datasheet](https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P60B_80145.pdf) | Recommended |
| Molicel P50B (21700) | 18.0 (TDS 17.5) | 70 g | 257 | 60 A (80 C cut-off) / 5 A std, 25 A max (5C) | [datasheet](https://files.batteryjunction.com/frontend/files/molicel/DataSheets/MOLICEL-P50B-Datasheet.pdf) | Alternate, charge proven |
| Amprius SA504 (pouch) | - | - | 390 | 6C / 2C, 500 cycles | [catalogue](https://amprius.com/documents/Amprius_Product_Catalog.pdf) | Stretch |
| Molicel M65A (21700) | 23.4 | 74.5 g | 314 | 26 A / 1C standard charge only | from `research/battery-deep-dive.md` | Rejected for fast charge |
| Samsung 50S (21700) | about 18 | 70-72 g | about 250 | 25 A / 6 A max charge listed | [retailer sheet](https://www.imrbatteries.com/content/samsung_50S.pdf) | Rejected: 1.2C charge, weak cycle life |

Pack-level estimate for a structural-case pack: cells / 0.80 gives **about 230 Wh/kg for P60B** (288 x 0.80) and about 304 Wh/kg for SA504 at 0.78. The 0.80 fraction is today's CAD ratio (106.9 kg cells in a 133.65 kg pack); it is not a tested figure.

Check against the targets: 100s at 3.7 V is 370 V nominal. At 65 kW peak the draw is about 176 A, which is 17.6 A per cell for 10 parallel groups, well inside the 60 A rating. Fast-charge: at 2C (about 43-48 kW) each cell sees about 12 A, which is the number to confirm on the P60B datasheet. If P60B is limited to about 1C, switch to P50B (84 kg of cells, +9 kg).

Price: P60B is 3.35-8.00 USD per cell on B2B listings (not authorised distribution), so about 6,000 USD per pack; SA504 is unpublished (my estimate 11-17k USD).

## 2. Motor, inverter, reduction

| Option | Mass | Peak / continuous | Notes | Role |
|---|---:|---|---|---|
| EMRAX 188 CC | 7.9 kg | 60 kW / 37 kW (34 liquid, 27 air); 100 / 56 Nm; 8000 rpm | [datasheet v1.5](https://emrax.com/wp-content/uploads/2024/02/EMRAX_188_datasheet_v1.5.pdf) | Recommended |
| EMRAX 228 | 13.2 kg | 124 kW / 75 kW; 220 / 130 Nm; 6500 rpm | local copy of datasheet v1.7; 370 V suitability must be checked (earlier study found the MV winding needs about 630 V) | Alternate for 75 kW+ |
| Helix SPX177-45 | 13 kg | 150 kW / 90 kW; 120 Nm | [Helix](https://www.ehelix.com/products/spx177/); voltage unpublished | Not needed at this power |
| Emsiso emDrive H100 | 2.2 kg listed (3.5 planning) | 150 A / 450 A; 52 / 78 kVA | [datasheet copy](https://git.fasttube.de/FaSTTUBe/scruti-documents/raw/branch/main/electrical-scrutineering/Inverter%20emDrive%20H100.pdf); voltage class unconfirmed | Recommended inverter |
| Cascadia CM200DX | 6.75 kg | 300 A / 740 A rms; 50-480 V | [Cascadia](https://www.cascadiamotion.com/cm-200) | Alternate inverter (proven) |

- Ratio: 125-130 mph is about 1,750 wheel rpm, so a motor at about 6,800 rpm needs about 3.8:1. That is one belt stage (belt 0.5 + pulleys 2.6 = 3.1 kg), replacing today's gearbox + belt + oil system. A single stage also removes the gear oil, exchanger and oil cooler (1.5 kg in the ledger).
- 188 mm diameter is smaller than the 228 mm envelope today, which should ease pack-to-motor clearance (to be checked in CAD).
- Not found: any lighter off-the-shelf 400 V motor-plus-inverter drive unit at 55-75 kW. Searches for Parker, Magelec, Saietta, YASA (YM360 is 24 kg), Piktronik (75 kg at 171 V) and Roypow gave nothing lighter that fits. EMRAX is the practical choice.
- Benchmark: the LiveWire S2 Del Mar makes 63 kW from a 10.5 kWh pack at 198 kg running order ([LiveWire](https://www.livewire.com/s2-del-mar)), so 55-75 kW in a 210-250 kg bike is normal ground.

## 3. Charging and HV electronics

- **Inlet:** Volex NACS (SAE J3400, 1000 V, 500 A, 1.3 kg) already in the design; [datasheet](https://www.volex.com/media/z3rmrwl5/volex-nacs-ev-charging-inlet.pdf). Keep it, with the ADVANTICS EVCC controller (0.3 kg).
- **DC fast charge:** goes straight to the pack through two dedicated contactors. No charger mass is needed for DC. A 3.3 kW AC charger (about 3.5 kg, class estimate; no specific part verified) covers home charging; BROGEN 6.6 kW (6.5 kg) is the alternate. 10-90% on AC is about 6.5 h with 3.3 kW; say so openly in the spec.
- **HV box:** four Gigavac GX14 contactors (0.45 kg each) plus fuse, precharge and busbars in one box, 2.7 kg versus 5.5 kg now.
- **BMS:** Orion BMS2 stays (1.5 kg in ledger).
- **Ledger issue:** the ledger counts a 1.2 kW DC-DC converter (2.8 kg, HELLA) and also a "DC-DC converter 1 kW" allowance (1.2 kg). This looks like a double count; the program lead should confirm.

## 4. Chassis hardware

All masses here are estimates; makers do not publish fork or shock masses.
- **Fork:** an OE-spec 43 mm USD fork at 170 mm travel saves about 2 kg over today's 48 mm legs. The lighter bike (210-250 kg) justifies it. Aftermarket Ohlins FGRT 301 (EUR 3,974 retail) is only a price reference; it has 120 mm travel.
- **Shock:** Ohlins STX 46 / TTX class (KT 122 retail EUR 869, [Ohlins](https://www.ohlins.eu/en/products/motorcycle/kt-122--4458/)). Dropping semi-active valves is the main saving.
- **Wheels:** no saving from aluminium; forged alloy stays at 7.6 kg per set. Carbon (BST class) would save about 1.7 kg for about 4.5k USD per set. Not verified; low confidence.
- **Tyres:** 110/80R19 + 150/70R17 saves about 1.8 kg and also helps the belt-to-tyre clash found earlier (the 170 mm tyre overlaps the belt by 12 mm). Check the speed rating against 125+ mph (V rating is 149 mph).
- **Brakes:** Brembo Stylema is 0.625 kg without pads ([Brembo](https://www.bremboparts.com/africa/en/catalogue-bike/caliper/220D02010)) versus 0.85 kg in the ledger. Dual 320 mm front discs are now the final choice (CAD rev E, ledger, cost; fade analysis in `15-dynamics.md`); the 300 mm option is dropped.
- **ABS:** Bosch ABS 9 hydraulic unit is 0.65 kg ([Bosch datasheet](https://www.bosch.co.jp/tms2015/en/products/pdf/2WP_ProductDataSheet_ABS9_base_plus_EN_lowres_20151030.pdf)); ABS 10 is described as 30% lighter ([Autocar Pro](https://autocarpro.in/news-international/bosch-motorcycle-abs-goes-production-kawasaki-suzuki-22471)). Total with sensors and lines about 1.1 kg (my estimate). Regen braking must be blended with ABS; that is a software and homologation task, not a parts one.

## 5. Cooling

- Motor alone: EMRAX 188 air-cooled gives 27 kW continuous with about 0.4 m3/min of air per kW. That covers cruise at 70 mph (about 12-14 kW) with ram air.
- At 125 mph (about 41 kW shaft) the motor needs the liquid or combined option (34-37 kW), and even that holds only briefly. Peak 60 kW is rated for 2 minutes.
- The inverter (emDrive H100 is liquid cooled; CM200 needs 12 L/min) and the pack on fast charge (4-6 kW of heat; earlier study says air cooling cannot work) both need liquid. So one shared loop at 6.0 kg is the lightest sensible answer; fully passive is not viable.

## Risks (ranked)

1. **Performance.** 60 kW and 100 Nm with a 3.8:1 belt is thin for a premium bike and for 125 mph sustained. The alternate EMRAX 228 (+5.3 kg) gives 124 kW but its 370 V behaviour is unverified.
2. **Cell charge rate.** P60B charging limits are not confirmed; the P50B fallback costs +9 kg.
3. **Inverter data.** The H100 datasheet is a university-team copy; 2.2 kg looks low and the voltage class is unconfirmed. CM200DX is the safe fallback (+3.25 kg).
4. **Fork, shock, wheel and tyre masses** are estimates, not datasheet values.
5. **Price.** The recommended parts sum to about 27k USD at retail and estimate prices. This is not an at-scale cost and should not be compared to the 30-35k target.

## What this does not prove

- No supplier was contacted; no quote exists for any part. Prices are retail listings or my estimates, and several are guesses.
- Web search returned few datasheets. Masses for the fork, shock, tyres, wheels, 3.3 kW charger, DC-DC, BMS, cables and cooling parts are estimates, not published figures.
- Performance (0-60, top speed), thermal limits and brake stopping distance were not simulated. The 4.5-5 s 0-60 figure is a rough hand estimate.
- Fit in the CAD (the 188 mm motor, a different belt ratio, tyre clearances, pack shape) was not checked.
- The pack mass uses today's 0.80 cell fraction; a real 21700 structural pack could be heavier.
- No CAD change requests from this file; the layout consequences (smaller motor, no gearbox, one HV box, one radiator) go to the layout agent.
