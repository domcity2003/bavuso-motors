# V1.0 electrical definition — BE-100S7P-CM-MV

October 25, 2026, US Central. This is the custom Bavuso candidate configuration behind the V1.0 CAD study. It is an engineering development definition, **not an energized-build release**. Actual supplier bodies, proposed custom geometry and unresolved functions have different evidence status. No parts have been purchased or commissioned.

## Configuration and energy

Use **700 Amprius SA504 cells, 100 series groups × 7 parallel cells**, EMRAX208 medium-voltage liquid-cooled motor and Cascadia CM200DX inverter. The native NACS development architecture has separate AC conversion and DC charge paths. Keep the prior 800-cell 100s8p configuration as a separately identified energy variant; its specifications must not be carried into this 700-cell model.

| Calculated quantity | V1.0 100s7p | Separate 100s8p comparison |
|---|---:|---:|
| Typical / minimum nominal energy | 26.299 / 25.704 kWh | 30.056 / 29.376 kWh |
| Typical capacity | 77.35 Ah | 88.40 Ah |
| Nominal voltage / summed cell endpoints | 340 V / 250–420 V | Same |
| Cells-only typical mass | 68.11 kg | 77.84 kg |
| Cells at published +2 g mass bound | 69.51 kg | 79.44 kg |
| Pack at assumed 85% cell mass fraction | 80.129 kg | 91.576 kg |
| Pack at assumed 80% cell mass fraction | 85.1375 kg | 97.30 kg |
| Summed typical / maximum charge current | 75.6 / 151.2 A | 86.4 / 172.8 A |
| Ideal per-cell current at 70 kW / 250 V | 40 A | 35 A |

These are calculations, not qualified operating limits. The endpoints do not define everyday SOC limits; resistance, sag, temperature, life and protection tolerances must establish those. The 85% integration assumption leaves only **12.019 kg** for all noncell pack hardware in 7p. CAD material assignments do not establish that this mass contains a functioning enclosure, restraints, cooling, BMS, interconnects and protection.

**The current enclosure calculation exposes an additional mass conflict.** A proposed closed 690×220×550 mm aluminum shell with uniform 3 mm walls has 3.861456 L of metal and calculates to **10.425931 kg at 2,700 kg/m³**, before mounts, lid joints, fasteners, seals or cutouts. With 68.11 kg of cells, the 80.129 kg pack target would leave only **1.5935 kg** for all remaining pack functions. That is not a credible closed pack BOM. This is a geometric shell calculation, not proof the wall thickness or material is structurally suitable. A 2 mm shell would be a separate unqualified structural alternative; no mass saving is credited without retention, impact, fatigue, sealing and manufacturing evidence. The 85% integration target remains unearned and the current 399 lb screening case cannot be promoted to a CAD-derived mass result.

The focused range/mass calculation elsewhere assumes CdA 0.30 and a tightly allocated nonpack mass. It is not established for the new V1.0 wheelbase, structure, body or installed hardware. Do not reuse its approximately 399 lb/209-mile outcome as a measured result or as a mass derived from this CAD assembly. Under 400 lb, 200 miles at 70 mph, 125+ mph and actual Tesla charging remain unclosed owner goals.

## Cells, cartridges and geometric limits

Amprius identifies the reference as **SA504, AMP-TDS-SA504-R1**. Catalog drawing dimensions are L1 125.4±1.0 mm, L2 119.0±1.0 mm, W1 42.2±1.0 mm, T1 8.25±0.3 mm **at 30% SOC**. The drawing does not release tab metallurgy, joining geometry, aged swelling or a compression prescription. [Amprius Q3 2026 catalog, PDF page 52](https://amprius.com/documents/Amprius_Product_Catalog.pdf)

The actual CAD study contains 700 discrete cell objects; its orientation uses maximum stated dimension bounds **126.4 X × 8.55 Y × 43.2 Z mm** and an illustrative pitch **132 X × 10 Y × 50 Z mm**. Ten proposed cartridges each contain 10s7p: two series columns along X, five series rows along Z, seven parallel cells along Y. This provides a countable electrical/spatial hypothesis. It does not prescribe busbar paths, welds, compression or voltage-sense routing.

The 10 mm Y pitch leaves 1.45 mm above the published 8.55 mm thickness bound. That space has **not** been shown sufficient for life/SOC swelling, restraint, dielectric layers or heat transfer. Similarly, maximum L1/W1 bounds do not establish a weld/tool-access corridor. Preserve group and cell IDs through CAD, inspection and the [placement register](cell-placement.csv). Inspect its current coordinate export for the final cartridge placement; do not derive assembly dimensions from renders.

Each cartridge is arithmetically 34 V nominal, up to 42 V summed endpoint and 2.6299 kWh typical. A disconnected cartridge still contains substantial stored energy. Voltage-group monitoring cannot identify every internal parallel-cell fault. Main pack isolation does not stop neighboring parallel cells feeding a failed pouch. Supplier-approved cell support, joining, insulation and fault-containment design is required before manufacture.

## Actual motor/inverter bodies and compatibility

V1.0 imports supplier geometry rather than representing the main drive parts only as bounding boxes:

- [EMRAX208 official page](https://emrax.com/e-motors/emrax-208/) links [208 LC resolver STEP](https://emrax.com/wp-content/uploads/2022/05/208_lc_resolver.step) and a [dimension image](https://emrax.com/wp-content/uploads/2024/09/208-1.png). Nominal LC body is diameter 208 × axial length 85 mm, reference mass 10.3 kg. The downloadable STEP predates current ratings; validate its exact shaft, flange, resolver and drawing revision against the ordered assembly.
- [Cascadia CM200 official page](https://www.cascadiamotion.com/cm-200) links [supplier CAD archive](https://www.cascadiamotion.com/_files/archives/7833d4_c5a4f069bda048a59e996474af1da8b7.zip?dn=0C-0049+CM200.zip), [2D drawing](https://www.cascadiamotion.com/_files/ugd/7833d4_0926ba4d1b844df08b495b2b57a3b6a6.pdf) and [datasheet](https://www.cascadiamotion.com/_files/ugd/7833d4_f46965a239f843afa9a2fa82f7d5d1ed.pdf). CM200DX reference body is 330×188×97 mm, 6.75 kg. Connectors, cable bends, coolant fittings and service access remain installed-package requirements beyond the solid body.

Current [EMRAX208 v1.7](https://emrax.com/wp-content/uploads/2026/08/EMRAX_208_datasheet_v1.7.pdf) gives LC **47 kW / 75 Nm continuous**, **86 kW peak for 30 seconds**, and 7,000 rpm limiting speed. All variants require airflow and must not be fully enclosed. The current family is transitioning out; downloadable geometry is not a supply commitment.

At the previous 125 mph road-load reference, about 41 kW shaft and 73.8 Nm are needed at approximately 5,304 rpm. Compare that demand with 75 Nm continuous: little margin remains. The winding's loaded speed/torque maps at hot, low-SOC voltage determine whether it works. The proposed 60 kW short peak / 45 kW continuous installed targets remain requests, not achieved ratings.

The current CM200 website gives DX operation **200–480 V**, while its linked sheet gives **50–480 V**. Use the conservative intersection pending supplier resolution; 250–420 V lies within both. Its 300 Arms continuous / 740 Arms peak ratings are phase current, not battery current. Peak duration, switching frequency, coolant temperature and electrical frequency must match the motor application.

EMRAX's [recommended-controller list v1.4](https://emrax.com/wp-content/uploads/2026/04/RAZV_ZS_List_of_recommended_controllers_v1.4.pdf) lists CM200DX with **TS2620N1095E161 five-pole-pair resolver** reference. Cascadia's [documentation page](https://www.cascadiamotion.com/documentation) supplies an EMRAX setup guide. That supports investigating this pair; it does not release sensor pins, offset, polarity, firmware or torque maps for this bike. EMRAX says complete motor/controller packages are not yet a standard product. [Integration support](https://emrax.com/solutions/motor-controller-package/)

**Weight alternative:** NX Technologies publishes the **W90**, 3.1 kg, 48–450 V nominal DC link, 410 Arms maximum and 90 kW continuous at 400 V. It also appears in EMRAX's recommended list. Potential saving versus CM200DX is 3.65 kg, but it is a separate unqualified configuration requiring its own drawings, cooling, software and current maps. Do not credit that saving to the CM200 CAD configuration or assume it suits the higher-current LV+100% winding. [NX W90](https://nx-tech.com/products/450v-motor-controller-up-to-90kw/)

## Charging and power paths

Proposed functional topology: monitored cells → pack fuse/service isolation/main contactors → HV bus → inverter/motor and isolated LV converter. NACS inlet → positively interlocked AC/DC routing → either onboard AC charger/protected output or supervised DC inlet contactors/HV bus. A live pack must not backfeed an exposed inlet or the OBC AC input. No complete routing assembly or native inlet is selected yet.

The compact OBC study is the **BROGEN PV1776 catalog entry**, 373×224×76.5 mm, ≤3 kg, 6.6 kW/22 A, 200–430 VDC output and 176–264 VAC input. This establishes a source-backed body reservation, not exact mounting/connector geometry or an orderable qualified revision. **120 V operation is not established.** At 250 V, 22 A caps output at 5.5 kW. [BROGEN catalog, PDF page 11](https://www.brogenmotors.com/wp-content/uploads/2024/06/Requirement_SheetOBC.pdf)

Use **ADVANTICS ADM-CS-EVCC** as the communication candidate; its [current manual](https://documentation.advantics.fr/adm-cs-evcc/index.html) explicitly supports NACS protocols. It performs neither power conversion nor complete AC/DC power routing. Its [interfaces guide](https://documentation.advantics.fr/adm-cs-evcc/interfaces.html) calls for inlet voltage/current plus battery voltage and identifies **IVT-S-300-U3-I-CAN2-12/24** as a current/three-voltage measurement example. An open inlet contactor means inlet voltage need not equal battery voltage.

For 7p, 151.2 A summed maximum charge reference permits 37.8 kW at 250 V; 50 kW is not available across the whole endpoint window. Catalog maximum current does not qualify repeated fast-charge life. Ideal 10–80% stored energy is 18.4093 kWh: constant net 30/40/50 kW would take 36.8/27.6/22.1 minutes. Those are energy/time comparisons, not a predicted charging curve.

Tesla compatibility requires **authorized network access and demonstrated technical interoperability**, separately. Bavuso access is not established. Native connector fit and NACS protocol support do not confer permission or universal station voltage support. Port position, cable reach, stand stability, lock, drainage and safe release require physical tests. [Tesla other-EV charging](https://www.tesla.com/support/charging/supercharging-other-evs)

## Functions that remain unresolved

The [electrical component list](components-electrical.csv) identifies specific candidates and open functions. The deeper [architecture and state/fault definition](../documentation/systems/electrical-energy.md) remains applicable. V1.0 has no complete released schematic, harness or firmware.

Required hardware includes Orion BMS2 108-channel candidate for 100 groups; temperature coverage; pack/inlet current and voltage sensing; insulation monitoring; main and charge isolation; manual service disconnect; coordinated fuses; precharge/discharge; VCU/watchdog and independent inhibits; isolated LV converter, stored LV energy, distribution; complete cables/mates/seals/terminals/clamps; pumps, fans, radiators and all fluid services. Neither a CAD object nor an assembly-level quantity of one means every constituent is selected.

The **0A-0162-03 Cascadia hardware manual** gives CM200DX DC-link reference 650 µF, passive discharge 70 kΩ and Y capacitance 136 nF. The capacitor alone stores about 57.3 J at 420 V; ideal RC time constant is 45.5 seconds. Total vehicle capacitance, tolerances and branches remain unknown, so no precharge resistor or safe wait time is selected. Verify voltage under an approved procedure; passive decay alone is not proof of isolation. [Hardware manual](https://www.cascadiamotion.com/uploads/5/1/3/0/51309945/0a-0162-03_hw_user_manual__002_.pdf)

Battery and drive need distinct controlled temperature domains. A radiator cannot hold cells below ambient. Hot stationary charging therefore needs evidenced derating or refrigeration, with its mass/power included. The old 5 kg thermal allocation does not prove a real installed system fits. Likewise the 300 W average auxiliary range assumption cannot size LV startup, contactor pull-in, ABS, pumps and fans.

An intact OEM electric bike can be a separately approved integration/ergonomics mule. It does not replace this custom product or solve the original goals. Do not transplant firmware-dependent OEM modules as if they were documented standalone components.

## Release closure

Before manufacture/energization, supply the exact supported cell and drive order configurations; released pack restraints/joining/cooling/venting drawings; complete schematics, protection coordination, connector cavity assignments and harness cut lists; controlled VCU/inverter/BMS/EVCC firmware and calibrations; thermal and charge-conformance evidence; cell/module/pack fault testing; and vehicle validation. Critical pinouts, fuse ratings, torque values and pouch compression remain unset until defensible data exists. The CAD model is useful for concrete design review, but the vehicle cannot yet be reproduced as a functioning exact build from these files.
