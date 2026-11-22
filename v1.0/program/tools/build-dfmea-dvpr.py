"""Builds program/data/dfmea-v1.csv and dvpr-v1.csv (and prints summary numbers).
Run from v1.0 with the FreeCAD python. All S/O/D values are engineering judgement on a paper design (no field data)."""
import csv, collections, os

def ap(S, O, D):
    """Conservative approximation of the AIAG-VDA 2019 Action Priority table (verify against the handbook).
    Chosen so that every severity 9-10 item with occurrence >=4 and weak detection is High."""
    if S <= 3: return "L"
    if S <= 6:
        if O >= 8: return "M"
        if O >= 6: return "M" if D >= 7 else "L"
        return "L"
    if S <= 8:
        if O >= 8: return "H" if D >= 3 else "M"
        if O >= 6: return "H" if D >= 5 else "M"
        if O >= 4: return "M" if D >= 5 else "L"
        return "M" if D >= 7 else "L"
    if O >= 6: return "H"
    if O >= 4: return "H" if D >= 5 else "M"
    if O >= 2: return "M" if D >= 3 else "L"
    return "L"

# key, system, item, failure mode, effect, S, cause, prevention today, detection today, O, D, action, tests
R = [
 # PACK
 ("cellshort","Pack","Cell (P60B 21700, 1,100)","Internal short leads to thermal runaway of one cell","Vent gas and heat; fire risk to rider","10","Manufacturing defect, dendrites, crush, fast-charge plating","Per-cell Al wire-bond fuse (0.19 ms model); 0.4 mm wire not final; BMS monitoring","Cell voltage and temperature sensing (1 NTC per few cells)","4","6","Single-cell trigger test on a lane module; set wire-bond size from pulse tests; cell lot incoming inspection","V02;V04;V01"),
 ("propag","Pack","Pack module barriers","Runaway spreads from one cell to neighbours","Whole pack fire, no time for rider to stop","10","Heat via ribbons and busbars (not gap filler); no coolant flowing; worst-case gas","Wire-bond links, slotted ribbon (<=0.03 W/K), mica on lane ends, pump kept on (screening model only)","None physical; model: 134-249 C neighbour in no-coolant and worst cases","5","7","Prove with trigger test (single cell, then group of 11) with and without coolant; adopt segmented ribbon in CAD; add propagation alarm (neighbour dT/dt)","V02;V03"),
 ("vent","Pack","Burst vents and plenum","Vent too small, blocked or not opening at 15-20 kPa","Case over-pressure, rupture, jet toward rider","10","Undersized area (490 mm2 per group calc), ice, mud, assembly error","Four 600 mm2 burst vents ducted to belly (spec only, not in CAD)","None (no test yet)","4","7","Design plenum and vents into CAD; burst-pressure and flow test; keep path clear of rider, pump and inlet","V03;V02"),
 ("ventpath","Pack","Vent exhaust routing","Hot gas reaches rider, inlet or pump","Burns, ignition of luggage, loss of coolant pump","9","Duct ends near inlet or luggage; fall-over","Routing rule: belly exit away from pump, motor and inlet","Design review only","3","6","CAD check of exit location in every tip-over pose; gas-jet test in propagation test","V02;V43"),
 ("bondfat","Pack","Wire-bond links (2,200) and ribbons","Bond lift-off or fatigue under vibration","Open parallel branch, hot spot, pack current imbalance, possible loss of power","7","Road vibration, thermal cycling, 160,000 km spectrum","Wire-bond design; slotted ribbon","Cell-group voltage drift in BMS (late)","4","6","Shaker test (R136 8A profile) on modules with resistance monitoring; bond pull tests in production","V05"),
 ("holder","Pack","Cell holders and lane structure","Cell moves or chafes against holder under shock","Can wear-through, short, venting","8","Holder creep, tolerance, thermal cycling","Not designed in detail (case 3-4 mm, holders per CAD)","None","4","6","Shock/vibration test of modules; holder material and tolerance review","V05;V16"),
 ("casefront","Pack","Pack case front wall and seams","Seam or wall fails in a 20 g frontal crash (FEA 167 MPa vs 140 allowable at 4 mm)","Pack shifts or opens, cell damage in crash","9","Thin wall, re-entrant corners","FEA found it; fix is 5 mm front wall plus floor ribs (not yet in CAD)","FEA only","5","5","Adopt 5 mm front wall and ribs; run cell-backed crash analysis; sled test of case","V20;V19"),
 ("skid","Pack","Pack floor and skid","Rock strike dents case into cells","Cell damage, runaway, loss of isolation","9","Bottom-out or rock; case 3-4 mm; cells 1-2 mm from wall in rev C","6 mm 5083 skid (old study); crush zone proposed","Quasi-static calc only","4","5","Cell-backed crush analysis, then rock-strike test; keep 10 mm crush zone","V19;V43"),
 ("fusei2t","Pack","Pack fuse and busbar","Short-circuit current (3.4-6.2 kA) not cleared safely; fuse I2t not checked","Busbar or cell damage, fire","9","No fuse curve selected","400 A fuse, pyro cut-off 22 kA class","None","3","6","Select fuse from curve; bench short-circuit at pack voltage","V14"),
 ("bmscut","Pack","BMS (Orion BMS2-108)","BMS fails to stop over-charge, over-discharge or over-temperature","Cell overcharge, plating, thermal runaway","10","Software/hardware fault; BMS is not ISO 26262 certified","Redundant voltage trip in hardware; contactor open command (to be defined)","BMS self-checks only","3","6","Hazard analysis with ASIL for pack; add independent hardware over-voltage and over-temperature cut; HIL fault injection","V15;V17"),
 ("sense","Pack","BMS sense harness (100 sense wires)","Sense wire open or high-resistance","BMS blind to a group, wrong SOC, late fault","8","Vibration, connector fretting","Fuses and connector boundary at MSD","BMS open-wire diagnostic","4","4","Include sense loop in vibration test; confirm Orion open-wire detection","V05"),
 ("coldplate","Pack","Cold charging (-10 C, 3 kW PTC)","Lithium plating from charging cold cells","Capacity loss, internal shorts over time","7","Rider ignores preheat; heater marginal (25.4 min)","Preheat on navigate-to-charger; charge current derate by temperature","Cell temperature sensors","5","6","Verify derate map and preheat on cold chamber; plating check by cell teardown","V34;V01"),
 ("hotpack","Pack","Hot-day 125 mph (38 C)","Cell reaches 60.9 C (limit 60 C)","Accelerated ageing, possible cell damage","8","Heat load and ram factor 0.25 is an estimate","Hot-day derate to about 105 mph after about 10 min","Pack temperature, BMS derate","4","4","Validate on climatic chassis dyno; confirm EMRAX allows >50 C inlet","V33;V25"),
 ("fastcharge","Pack","P60B at 2C charging","Fast-charge cycle life lower than needed","Faster fade, warranty cost","6","Datasheet v0.1 has no 2C life curve","12.5 A per cell (42% of the stated max)","None","6","7","Written cell charge-life data from Molicel; 1,000-cycle test with DC fast charge; P50B fallback (+9 kg)","V01;V34"),
 # HV
 ("isoloss","HV","HV bus isolation","Isolation loss (water, chafe, coolant leak)","Electric shock, false trips","10","Fording, damaged cable, connector seal","Isolation monitor (210 kohm fault), IPXXD boxes, HVIL","Isolation monitor continuous","4","4","Isolation and ingress tests; routing rules for chafe","V13;V21;V47"),
 ("contweld","HV","Contactors K1-K5 and HVIL","Contactor welded closed or HVIL loop open and undetected","Bus stays live after stop or crash","9","Switching under load, inrush","Weld check, opens only below 350 A, HVIL","Weld detection each cycle","3","4","Short-circuit and endurance of contactors at pack voltage","V14;V13"),
 ("discharge","HV","Active discharge (inverter bus)","Bus takes about 88 s to fall below 60 V (inverter bleed 70 kohm)","Shock risk for rescuers after crash","9","Active discharge not yet specified with Cascadia","None","None","5","5","Specify active discharge (below 60 V in 3 s) with Cascadia; measure","V13"),
 ("pyrofail","HV","Pyro cut-off","Does not fire on crash or hard fault","Pack stays connected into a damaged circuit","9","Sensor or logic fault, crash flag lost","Dual triggers (shunt, ABS/IMU crash flag, BMS latch)","Pyro continuity check","2","6","Fault injection and crash-pulse test of trigger chain","V15;V14"),
 ("pyrofalse","HV","Pyro cut-off","False trigger at speed","Instant loss of propulsion and regen at speed","7","Noise on shunt, IMU false crash flag","Thresholds 650 A/20 ms; 480 A/40 s","None","3","4","Calibrate thresholds on rig and in road tests; log events","V15;V50"),
 ("wading","HV","Pack breathing and connectors in water","Hot pack drawn into cold water, water pulled past seals","Isolation loss, corrosion, short","8","Pressure drop with no vent (about 10%)","Membrane vent with burst function (spec); IP67 below 550 mm","None","5","5","Hot-into-cold wading and IP67 test; route vents high","V21;V47"),
 # INVERTER / MOTOR
 ("invtemp","Inverter","CM200DX inverter","Overtemperature at coolant 65 C (limit is an estimate)","Torque derate or shutdown at speed","6","Hot day, hot loop","Derate in firmware; coolant order places inverter second","Case temperature sensor","4","4","Get Cascadia coolant derate curve; validate on dyno","V10;V33"),
 ("invtorque","Inverter","Torque control (CM200DX + VCU)","Unintended or excessive drive torque","Unwanted acceleration, loss of control","10","Software, sensor or CAN fault","Dual plausibility check in VCU and inverter","Cross-check of torque request vs feedback","3","4","Hazard analysis, ASIL assignment, HIL fault injection, vehicle fault tests","V15;V40"),
 ("peaksag","Inverter","LV+43% winding, 650 A peak","Inverter overcurrent trip at low-SOC high power","Sudden torque loss on overtake","7","650 A vs 740 A rating, voltage sag to about 300 V","Current limit 350 A DC; torque derate with SOC","Inverter fault flags","4","4","Dyno at 300-330 V and cold; confirm peak power at actual bus voltage","V10"),
 ("yoke","Motor/frame","Motor housing as load-bearing yoke","EMRAX housing cannot carry the belt-loop load (11.3 kN design pull)","Housing deformation, belt tension loss, or frame needs far more mass (tail rail 1,388 MPa without the yoke)","9","EMRAX publishes no housing limit; FEA assumed it is rigid","Assumption only; belt-side arm or motor-in-pivot casing considered as alternatives","FEA assumption","6","6","Ask EMRAX for housing and shaft loads; static proof of the housing under belt-loop load; decide belt-side arm option now if EMRAX declines","V08"),
 # BELT
 ("beltfail","Drive","Gates 8 mm belt","Belt breaks or tooth shear","Loss of drive; debris near tyre; regen lost","8","Shock load, misalignment, stone ingress, age","Sized for 11.3 kN design pull; guard","Torque-vs-speed plausibility","4","4","Belt durability rig with launch and regen reversals; guard design; spares and wear interval","V09"),
 ("beltalign","Drive","Belt tracking with single-sided arm","Arm flexes (lateral 1.0 kN/mm) and belt walks off or jumps teeth","Belt damage, tooth jump, noise","7","Lateral load, hub tolerance, wheel alignment","Flanged pulleys (to specify); tensioning procedure","None","5","5","Measure belt tracking on rig and in road tests under lean and bump; confirm flange design","V09;V31"),
 ("pulley","Drive","35T motor pulley and 126T rear pulley","Pulley fatigue, fretting or bolt loosening (30 m/s, 220 Nm)","Drive loss, possible wheel lock if pulley seizes","8","Cyclic torque, runout","Gates stock sizes for 8 mm pitch; no fatigue analysis yet","None","3","5","Rig durability including pulley-to-hub joint; retention torque check","V09"),
 # ARM / PIVOT
 ("armfat","Swingarm","Cast A356 arm, brace bolt-on","Fatigue crack at brace bolt-on (damage about 4 unreinforced)","Arm cracks, rear wheel alignment lost","9","Unreinforced bolt-on, casting porosity","Cast boss and rib required (not designed); X-ray casting inspection","FEA only","6","5","Design boss and rib; casting NDT plan; fatigue test of full arm to 1.5 lives","V06;V31"),
 ("pivot","Swingarm","Pivot bearings (right side 80 mm span)","Overload or short life (43.6 kN in, 33.4 kN out at design; CAD span of 36 mm gives 85/74 kN)","Bearing failure, pivot play, handling loss","9","Rev C 46 mm pivot and 6008 bearings cannot carry the load","FEA result; fix is 62 mm stub, 80 mm span, about 50 mm tapered rollers (CAD change request, not applied)","Hand and FEA","5","5","Apply CAD change; bearing life calculation; pivot rig test at 1.2x design plus the 21 kN slider case","V07;V31"),
 ("yokejoint","Swingarm","Pivot stub to yoke joint (belt-side move open item)","Joint fatigue or slip where belt loop closes through stubs and motor housing","Loss of rear axle alignment; crack in stub","9","Joint not designed; slider load 21 kN not checked","Open FEA item","None","5","6","Design the joint; test with V07/V08; reconsider arm on belt side if it fails","V07;V08"),
 ("cross","Swingarm","Cross brace and shock force path","Little margin: SF 1.22 on rear bump (required 1.2), falls to 1.18 at 255 kg","Brace yield, rear suspension misalignment","8","Mass growth beyond 240 kg","Mass target T1 enforced","FEA only","4","4","Hold T1; reinforce at bolt-on; include in frame fatigue test","V31;V38"),
 # FRAME
 ("framefat","Frame","Tube welds (down-link, rails, headstock)","Weld fatigue crack (Miner D 0.40-0.49 vs 0.5)","Frame crack, handling loss, possible separation","9","2x harsher real spectrum would fail; nominal-stress method","Wall sizes from sizing loop; CAD change request pending","FEA only","5","5","Rig test to 1.5 lives with crack monitoring; measure real road loads on a mule","V31;V50"),
 ("stiff","Frame","Frame lateral stiffness 1.3 kN/mm","Below the 1.5 kN/mm target; weave or wobble at 77-130 mph","Instability at speed, gust sensitivity","7","Single-sided arm, thin tubes, 3 mm case option lowers it by 25%","Torsion 4.4 kNm/deg passes","None","5","5","Modal and wobble test; adjust steering damper and trail; keep case at 4-5 mm","V32;V39"),
 # BRAKES
 ("fade","Brakes","Front brake (dual 300 mm, Stylema)","Fade or insufficient stopping from 125-130 mph","Longer stopping distance, FMVSS 122 high-speed test fail","9","No stopping analysis from 125 mph yet","Fallback to dual 320 mm (+0.95 kg)","None","5","5","Brake dyno then vehicle high-speed stop; decide 300 vs 320 mm before CAD freeze","V11;V41"),
 ("regenabs","Brakes","ABS and regen blending","Regen torque locks the rear wheel or reduces total deceleration","Rear wheel lock, fall","9","Blending software not written; ABS 10 class unit","Regen limited to dry grip (planned)","None","4","5","Calibrate on low-mu surfaces; regen off for the friction-only FMVSS 122 tests","V42;V41"),
 ("absloss","Brakes","ABS unit and sensors","Loss of ABS function","Wheel lock on slippery surface","8","Electrical fault, sensor dirt","ABS warning lamp (FMVSS 123 table 3)","Self-test","3","4","Fault injection on vehicle","V42;V40"),
 # CHARGING
 ("inletheat","Charging","NACS inlet and 35 mm2 cables at 137 A","Connector or cable overheats during 20 min DC charge","Melted inlet, fire","8","Poor contact, small cable (35 mm2 is 161 A bundled)","Inlet rated 500 A; temperature sensor planned","Inlet temp sensor (to add)","3","4","Thermal soak at 137 A and 40 C ambient with thermocouples; add inlet NTC to EVCC","V22"),
 ("relayacdc","Charging","AC relays and K4/K5","AC and DC paths closed at once","Station fault, shock, charger damage","9","Relay weld, logic fault","Mechanical and electronic interlock (defined, not built)","Weld check","2","5","Fault-injection test of the interlock","V23;V15"),
 ("interop","Charging","EVCC and J3400 session","Session fails or no Supercharger authorisation","Rider cannot fast charge on some stations","4","Not on Tesla's list; ISO 15118 cert not in place","Test on non-Tesla stations with adapter; apply to Tesla","None","7","5","Interoperability test against at least 6 station models; do not promise Supercharger access","V23"),
 # COOLING
 ("pump","Cooling","Coolant pump (22 L/min, about 74 kPa)","Pump failure or loss of flow","Overheating; the heat-sink effect that limits propagation is lost","8","Pump at edge of rating; air lock","BMS derates; pump kept on after thermal event","Flow and pump current","4","3","Pressure-drop measurement of EMRAX jacket and CM200DX plate; endurance run","V25;V26"),
 ("leak","Cooling","Hoses, manifolds and ribbons in pack","Coolant leak into pack or HV box","Isolation loss, short","9","Clamp or fitting failure, ribbon pinhole","Pack coolant 1.1 kg; leak sensing not specified","Isolation monitor (late)","3","5","Burst and leak tests on ribbons, hoses and manifolds; add pack leak sensor","V26;V13"),
 # SOFTWARE
 ("throttle","Software","Throttle (twist grip sensors)","Throttle sensor fault, stuck torque request","Unintended acceleration","10","Sensor or wiring fault","Dual sensors, plausibility in VCU and inverter","Disagreement detection","3","4","Hazard analysis; HIL and vehicle tests","V15;V40"),
 ("vcu","Software","VCU, CAN1/CAN2","VCU or CAN fault: torque lost or held","Loss of propulsion or stuck torque at speed","9","Software defect, bus fault","Two CAN buses, 120 ohm terminated","Watchdog","3","4","Safe-state design (torque to zero within the fault tolerant time); HIL","V15;V40"),
 # LIGHTING
 ("lights","Lighting","Front indicators and light band (FMVSS 108)","Lamp spacing and photometry do not comply (rev C fails; V1 design unchecked)","Failed certification; poor visibility","7","Styling light band replaces a lamp","Certified DOT lamp modules behind the band (planned)","None","5","3","Check CAD against 108 spacing before freeze; photometry on the real band","V44"),
 ("lv12","Lighting","12 V supply (DC-DC and 4.5 Ah battery)","DC-DC failure; 12 V battery flat after parking","Lights, ABS and VCU lost; about 28 min limp","8","DC-DC fault, parasitic drain (9 days standby)","Daily wake and top-up; limp-home","Voltage monitor","3","3","Limp-home test and standby drain test","V40;V50"),
 ("stoplamp","Lighting","Brake lamp logic under regen","No brake lamp when regen slows the bike","Rear-end collision","7","Stop lamp wired to levers only","Planned: lamp on regen deceleration","None","5","4","Define threshold (e.g. above 0.1 g); verify on vehicle","V44;V42"),
]

# DVPR rows: id, test, standard, samples, acceptance, closes_targets, closes_dfmea(keys from R), phase, cost_usd, weeks
V = [
 ("V01","Cell characterisation and 2C charge life (25, 0, -10 C)","IEC 62660-1/-2 plus Molicel written charge-life data","60 cells","Capacity and resistance match model inputs; >=80% SOH at the test life with 30% DC fast charge; no plating at -10 C with derate","T2;T6","cellshort;coldplate;fastcharge","component",120000,26),
 ("V02","Thermal propagation, lane module (single cell then group of 11, with and without coolant)","Internal target modelled on GB 38031-2020 8.2.7; SAE J2464 practice","3 modules","No external fire or explosion for >=5 min after warning; neighbour cells stay below 170 C; gas leaves by the belly vent","T2 safety","cellshort;propag;vent;ventpath","component",200000,8),
 ("V03","Burst vent opening pressure and flow","Rig, pressure ramp","6 vents","Opens at 15-20 kPa; >=600 mm2 free area each","T2 safety","propag;vent","component",40000,4),
 ("V04","Wire-bond fuse pulse and fusing","Pulse bench per cell datasheet currents","40 bond sets","Opens under shorted-cell current; neighbour bonds survive; no cell damage","T2 safety","cellshort","component",45000,4),
 ("V05","Module vibration and shock with resistance monitoring","UN R136 Annex 8A profile (confirm with lab); ISO 16750-3","3 modules","No open bond or cell movement; interconnect resistance change <10%","T2","bondfat;holder;sense","component",60000,4),
 ("V06","Cast swingarm static, fatigue and X-ray","ASTM E466-style; load cases from 09-structures.md","3 arms","No crack (dye penetrant) after 1.5 lives; casting porosity within class","T1;T8","armfat","component",140000,10),
 ("V07","Pivot bearing and stub rig (design load 1.2x, plus 21 kN slider)","Bearing life ISO 281; static proof","2 sets","No yield; L10 >= 160,000 km at spectrum; play within spec after test","T8","pivot;yokejoint","component",90000,8),
 ("V08","EMRAX housing yoke proof under belt-loop load","Static rig at 1.2 x 11.3 kN belt pull","2 housings","No yield or leak; deflection below the value used in FEA. Needs EMRAX cooperation","T1;T5","yoke;yokejoint","component",70000,6),
 ("V09","Belt, pulley and hub durability","Gates design manual; launch and regen reversals","2 drive sets","1.5 lives, no tooth shear; tension loss <15%; no pulley fretting; tracking within flange limits","T4;T5","beltfail;beltalign;pulley","component",140000,14),
 ("V10","Motor and inverter dyno (R85-style 30-min power) at 300-330 V and cold","UN R85 style; EMRAX/Cascadia data","2 sets","Peak >=90 kW at 330 V bus; continuous >=55 kW; no derate surprises vs model","T5","invtemp;peaksag","component",200000,10),
 ("V11","Brake dyno: fade and wear","SAE J2522-style","2 sets","300 mm discs pass fade at 125 mph energy, or move to 320 mm","T4","fade","component",130000,8),
 ("V13","HV electrical safety bench","ISO 6469-3; UN R136 Part I practice; IEC 60529 IPXXB/D","2 HV box sets","Isolation >=500 ohm/V (210 kohm); bond <0.1 ohm; bus <60 V within 3 s of opening; HVIL opens contactors","T2 safety","isoloss;contweld;discharge;leak","component",45000,3),
 ("V14","Short-circuit breaking: fuse, contactors, pyro","Bench at pack voltage, 3.4-6.2 kA prospective","3 sets","Fuse and pyro clear without arc or damage; contactors open below 350 A only; fuse I2t within busbar withstand","T2 safety","fusei2t;contweld;pyrofail","component",80000,6),
 ("V15","BMS, throttle and VCU hazard analysis, FMEDA and HIL fault injection","ISO 26262 (Part 12 motorcycles) approach; ISO 13849 for non-electronic channels","1 rig","All safety goals met; single faults reach safe state within the fault-tolerant time; ASIL table closed","T8","bmscut;pyrofail;pyrofalse;invtorque;relayacdc;throttle;vcu","component",250000,20),
 ("V16","Pack vibration and thermal shock","UN R136 Annex 8A/8B practice","2 packs","No leak, rupture, fire; isolation >=100 ohm/V","T2","holder","prototype",100000,8),
 ("V17","UN 38.3 pack-level (T1-T5, T7) plus cell summary","UN Manual of Tests and Criteria 38.3","4 packs","No leakage, venting, rupture or fire; no mass loss; OCV drop <10%","T2 transport","bmscut","prototype",180000,10),
 ("V18","UL 2580 pack abuse (voluntary)","UL 2580 / SAE J2464","3 packs","Report passes; no fire or explosion outside pack","T2","cellshort","prototype",250000,16),
 ("V19","Pack crush and rock strike","Internal target: 75 mm half-cylinder to 100 kN (SAE J2464 practice); 50 mm impactor at 3 g bottom-out","2 packs","No fire or explosion; no leakage after 1 h; dent <=12 mm","T2 safety","skid;casefront","prototype",150000,6),
 ("V20","Pack case crash retention (20 g)","Sled pulse test with dummy cells","2 cases","Seams intact; no cell exposure","T2 safety","casefront","prototype",60000,4),
 ("V21","Pack IP67, immersion and hot-into-cold wading","IEC 60529 IP67; hot pack 40 C into 10 C water","2 packs","No ingress; isolation held; no fire in salt immersion","T2","isoloss;wading","prototype",70000,4),
 ("V22","Inlet and cable thermal soak at 137 A","J3400 / UL 2251 style temperature rise","2 sets","Rise <=50 K at 40 C ambient for 30 min; no hot spots","T6","inletheat","component",30000,3),
 ("V23","Charging interoperability and conformance","DIN SPEC 70121 / ISO 15118-2; SAE J3400; J1772 pilot states","3 bikes, >=6 station models","Complete sessions at >=80% of stations; AC/DC interlock never allows both closed","T6","relayacdc;interop","prototype",120000,8),
 ("V25","Cooling loop bench and radiator ram-air check","Flow bench; wind tunnel ram factor","2 loops","74 kPa at 22 L/min; ram factor >=0.25; pump endurance 2,000 h","T4","hotpack;pump","component",60000,4),
 ("V26","Hose, manifold and ribbon burst and leak","Pressure test at 3x working","6 sets","No leak at 3x; no pinholes after vibration","T2 safety","pump;leak","component",20000,2),
 ("V30","Frame static proof and stiffness","Hydraulic rig; load cases C1-C6, D1-D3","2 frames","No yield; lateral >=1.5 kN/mm target or documented waiver; torsion >=3 kNm/deg","T1;T8","stiff","prototype",90000,6),
 ("V31","Frame and arm multi-axial fatigue to 1.5 lives","Road-load replay plus drive spectrum","2 chassis","No crack after 1.5 x 160,000 km equivalent; bolt preload loss <10%","T1;T8","armfat;pivot;beltalign;cross;framefat","prototype",350000,16),
 ("V32","Modal survey and wobble/weave check","Impact hammer, shaker","1 chassis","Frame modes >=2 Hz from wobble/weave and motor orders","T8","stiff","prototype",40000,2),
 ("V33","125 mph and 130 mph sustained at 25 C and 38 C","Climatic chassis dyno","2 bikes","25 C: 125 mph held, cell <55 C; 38 C: derates to about 105 mph, cell <60 C, EMRAX inlet within limit","T4","hotpack;invtemp","prototype",200000,6),
 ("V34","DC fast charge 10-80% at -10, 25, 35, 45 C","SAE J3400 station or emulator","3 bikes","<=25 min at 25 and 35 C; cold with preheat <=25 min; cell <55 C","T6","coldplate;fastcharge","prototype",150000,5),
 ("V35","Coastdown and constant-speed range at 70 and 77 mph","SAE J2263 adapted; chassis dyno","2 bikes","Range >=145 mi at 70 mph, 90 kg rider; measured CdA","T3","","prototype",80000,4),
 ("V36","Wind tunnel CdA with rider","Full-scale tunnel","1 bike","CdA <=0.38 m2","T3","","prototype",120000,3),
 ("V37","Acceleration and top speed","GPS-instrumented","2 bikes","0-60 mph <=4.0 s; 125 mph sustained; 130 mph governor","T4;T5","","prototype",50000,3),
 ("V38","Weigh the bike wet, ready to ride","Calibrated scales","every prototype","<=240 kg (529 lb)","T1","cross","prototype",2000,1),
 ("V39","Handling and high-speed stability, gusts at 77 mph","Proving ground","2 bikes","Weave and wobble damping positive in all modes; rider rating >=4/5","T8","stiff","prototype",150000,6),
 ("V40","Vehicle-level fault injection (throttle, VCU, ABS, 12 V loss)","Vehicle on rollers and track","2 bikes","Safe state in every case; limp-home >=25 min","T8","invtorque;absloss;throttle;vcu;lv12","prototype",80000,4),
 ("V41","Brake compliance pre-test, including high-speed stop","FMVSS 122 S6; 125 mph stop for design margin","2 bikes","Dry stop limits met (front only 37.3 m, rear only 53.9 m from 60 km/h); fade ratio met; regen off for friction tests","T4","fade;regenabs","prototype",150000,6),
 ("V42","ABS and regen blending on low-mu surfaces","Supplier calibration loops","2 bikes","No wheel lock above 15 km/h; regen never reduces total deceleration below demand","T8","regenabs;absloss;stoplamp","prototype",200000,8),
 ("V43","Tip-over and low-side slide","10 falls each side; 30 and 50 km/h slide","2 bikes","Pack never touches ground; isolation >=100 ohm/V; vent gas path clear","T2 safety","ventpath;skid","prototype",60000,3),
 ("V44","Lighting photometry and installation; reflectors; stop-lamp logic","FMVSS 108","1 set","All lamps meet photometry and spacing; stop lamp on regen","T10","lights;stoplamp","pre-production",60000,4),
 ("V45","Mirrors, controls and displays, tyres and rims, glazing, brake fluid audit","FMVSS 111, 123, 119, 120, 205, 116","1 bike","All items meet the standard or a supplier certificate is on file","T10","","pre-production",50000,4),
 ("V46","Vehicle EMC and radio","UN R10 practice; FCC Part 15","1 bike","Emissions and immunity under limits; keyless and telematics grants","T8","","pre-production",150000,6),
 ("V47","Climate, altitude and wading trips","Hot, cold, 4,000 m; 450 mm wading","2 bikes","No faults; isolation held after wading","T8","isoloss;wading","pre-production",120000,5),
 ("V50","Durability fleet: road and gravel","3 bikes x 30,000 km (reduced from the earlier plan)","3 bikes","No structural or HV fault; wear within limits; pyro false trips logged","T1;T8","framefat;pyrofalse;lv12","pre-production",450000,30),
 ("V51","Pre-production confirmation (brakes, lighting, EMC, charging)","Repeat key tests on production-intent bikes","5 bikes","Results match prototype within tolerance","T1-T10","","pre-production",300000,12),
 ("V52","US certification file: Part 565 VIN, 566 registration, 567 label, FMVSS self-certification","49 CFR 565, 566, 567, 571","1 file","Complete file; label and VIN pad on the frame","US launch","","pre-production",60000,8),
]
# Hardware lines (not tests) and EU add-on, kept in the DVPR csv with phase markers
H = [
 ("HW1","Prototype hardware: 3 hand-built mules","Build","3 bikes","n/a","T1-T10","","prototype",450000,20),
 ("HW2","Test packs (beyond the ones in bikes) and modules","Build","12 packs, 6 modules","n/a","T2","","prototype",264000,24),
 ("HW3","Pre-production builds: 8 bikes on soft tooling","Build","8 bikes","n/a","T1-T10","","pre-production",760000,16),
]
EU = [
 ("EU1","EU add-on: UN R136 REESS tests (vibration, thermal shock, mechanical shock, short, overcharge, over-discharge, over-temperature)","UN R136 Annex 8","3 packs","As R136","EU later","","EU add-on",450000,16),
 ("EU2","EU add-on: R78 braking, R53 lighting, R10 EMC witnessed tests, R81 mirrors, R41 noise","UN R78, R53, R10, R81, R41","2 bikes","As each regulation","EU later","","EU add-on",450000,16),
 ("EU3","EU add-on: L3e-A3 type approval, technical service, CoP","Regulation (EU) 168/2013","1 file","Approval granted","EU later","","EU add-on",350000,16),
]

here = os.path.dirname(os.path.abspath(__file__))
data = os.path.normpath(os.path.join(here, "..", "data"))
ids = {}
rows = []
cnt = collections.Counter()
for r in R:
    key, sysn = r[0], r[1]
    cnt[sysn] += 1
for i, r in enumerate(R, 1):
    ids[r[0]] = "D%02d" % i
# map tests to rows
tests_for = {k: [] for k in ids}
for t in V:
    for k in filter(None, t[6].split(";")):
        assert k in ids, k
        tests_for[k].append(t[0])
# check DFMEA links are consistent with DVPR links
out = []
hi = med = lo = 0
for r in R:
    key, sysn, item, fm, eff, S, cause, prev, det, O, D, act, tests = r
    S, O, D = int(S), int(O), int(D)
    a = ap(S, O, D)
    if a == "H": hi += 1
    elif a == "M": med += 1
    else: lo += 1
    linked = sorted(set(tests.split(";")) | set(tests_for[key]))
    for t in linked:
        assert any(v[0] == t for v in V), (key, t)
    status = "open" if a == "H" else ("needs test" if a == "M" else "needs test")
    out.append([ids[key], sysn, item, fm, eff, S, cause, prev, det, O, D, S*O*D, a, act if a != "L" else act, ";".join(linked), status])
with open(os.path.join(data, "dfmea-v1.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id","system","item","failure_mode","effect","severity","cause","prevention_today","detection_today","occurrence","detection","SxOxD","action_priority","recommended_action","dvpr_tests","status","basis"])
    for o in out:
        w.writerow(o + ["estimate (engineering judgement, no field data)"])
for r in out:
    assert not (r[12] == "H" and not r[14]), r[0]

tot = collections.Counter()
with open(os.path.join(data, "dvpr-v1.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id","test","standard_or_procedure","samples","acceptance","closes_target","closes_dfmea_rows","phase","cost_usd_estimate","duration_weeks","status"])
    for t in V + H + EU:
        dr = ";".join(ids[k] for k in filter(None, t[6].split(";")))
        w.writerow([t[0], t[1], t[2], t[3], t[4], t[5], dr, t[7], t[8], t[9], "planned"])
        tot[t[7]] += t[8]
        tot["testonly" if t in V else ("hw" if t in H else "eu")] += t[8]
print("DFMEA rows", len(out), "H", hi, "M", med, "L", lo)
print("DVPR tests", len(V), "hardware", len(H), "EU", len(EU))
for k, v in tot.items(): print(k, v)
print("US total", tot["testonly"] + tot["hw"])
# coverage: DFMEA rows with no test
print("rows without tests:", [ids[k] for k in ids if not tests_for[k]])
by = collections.Counter()
for o in out: by[(o[1], o[12])] += 1
print(dict(by))
for o in out: print(o[0], o[1], o[5], o[9], o[10], o[12], o[2][:30])
print({k: ids[k] for k in ids})
