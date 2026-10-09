# Bill of materials (per plate)

Prices/stock as seen Oct 2026; re-check. Bold = safety-critical, don't substitute without review.

| Ref | Part | MPN / source | Notes |
|-----|------|--------------|-------|
| — | IKEA BILRESA remote, scroll wheel | IKEA 906.174.56 (white) | Kept intact, 2×AAA. Remove nothing. |
| — | Adhesive magnet | supplied with the BILRESA | Glued into the recess in the pocket floor. Cut to size. |
| S1 | **Rocker DPST, PCB pins** | **Marquardt 1802.2504** (drawing 1802.2504 rev g) | ENEC 12(4) A 250 V~; UL-recognized/CSA 15 A 125–250 VAC; cutout 19.4 × 21.9 (1.25–2 mm panel); 5.3 mm above the panel, PCB seat 16.2 mm below. Pinout to be checked with a meter (D-26). |
| J1 | **Terminal block, push-in lever, 6-pole, 5 mm, 4 mm² / 12 AWG** | **WAGO 2604-1106** | L/N/PE in and out; 400 V (III/2). On the board's back, wire entries face the top edge. |
| PS1 | **AC-DC 5 V 600 mA** | **Mean Well IRM-03-5** (DigiKey 1866-3020-ND) | 85–305 VAC, 37×24×15 mm, on the board's back. |
| F1 | **Fuse T1A 250 VAC, SMD** | **Schurter UMT 250 3404.2416.22** | Rating is the designer's choice (Mean Well gives none); 200 A breaking capacity: human review. |
| RV1 | **Varistor 275 VAC, SMD** | **TDK B72660M0271K093** (CU4032K275G2) | Covers 120 V and 230 V. |
| C1 | 22 µF 10 V X5R 1206 | Murata GRM31CR61A226KE19L or equiv. | 5 V output. |
| J2 | FPC connector, 6 contacts, 0.5 mm, SMD, slide lock | Hirose FH12-6S-0.5SH(55) | 5 V out to the flex jumper (1–3 = GND, 4–6 = +5 V). |
| PCB | Wiring board 47 × 72 mm, 2-layer 1.6 mm | PCBWay; order pack in `pcb/fab/` | Routed isolation slot in the outline. S1 is soldered by hand after it is snapped into the insert. Copper weight: thermal review. |
| — | Apollo MSR-2 mmWave multisensor | apolloautomation.com / The Pi Hut | ESP32-C3, LD2410B, DPS310, LTR-390; optional SCD-40. Used out of case. |
| U? | SHT45 | Sensirion SHT45 (DFN-4 1.5 × 1.5) | Soldered on the sensor flex tail, I²C from the MSR-2 (D-27). |
| — | Sensor flex | PCBWay flex, single layer, 0.12 mm, FR4 stiffeners 0.15 mm; `pcb/sensor/` | D-27: MSR-2 CN2 → spring fingers → SHT45 on the tail. Not orderable until CN2 is confirmed. |
| — | CN2 mating plug | TBD (0.4 mm, 2 rows; part open) | D-27; confirm from the GPIO add-on's plug or Apollo. |
| MK1 | I²S MEMS microphone, bottom port, 4 × 3 × 1 mm | PUI Audio DMM-4026-B-I2S-R | D-29: on the sensor flex, port through flex + stiffener (Ø0.5) to the face skin's Ø1.0 sound hole. |
| C2, R1 | 100 nF X7R 0402; 100 kΩ 1 % 0402 | any | D-29: mic decoupling; I²S SD pull-down (datasheet). |
| — | Mic gasket: double-sided adhesive ring OD 2.6, ID 1.0, 0.15 mm | die-cut | D-29: seals the mic stiffener to the face skin around the sound hole. |
| — | SMT spring fingers ×2 | **Harwin S7081-42R** (gold, 4 A) | D-27: on the sensor flex, +5 V and GND, working height 2.0 mm. |
| — | 5 V jumper: flex, two layers, 0.2 mm, 156 mm + battery-free tongue (D-41), stiffened ends (PI 0.3 mm total at the plug, FR4 0.6 mm total at the pads), ENIG | PCBWay; `pcb/sensor/fab/power_jumper/` | D-27, R9: plugs into J2 (FH12-6S, slide lock) → pass-through → pad end on the insert shelf under the spring fingers. No wires, no soldering at assembly. |
| — | Replacement back cover (BILRESA E2490): printed cover + single-layer flex with 0.4 mm FR4 stiffener, ENIG; the remote's own steel plate | printed; PCBWay flex, `pcb/sensor/` cover_flex (no fab files yet) | D-35: replaces the remote's back cover; no cells. |
| — | SMT spring fingers ×4 (back cover) | **Harwin S7081-42R** | D-35, D-40: on the cover flex, +5V and GND onto the floor pads; VBAT and GND onto the remote's battery contacts. |
| U1 (cover flex) | LDO 3.3 V 500 mA, SOT-23-5 | **TI TLV75533PDBVR** | D-41: the remote's 3.3 V from the floor's +5 V, on the cover flex. Datasheet: https://www.ti.com/lit/ds/symlink/tlv755p.pdf |
| C3, C4 (cover flex) | 1 µF 10 V X5R 0402 | Murata GRM155R61A105KE15D | LDO input / output (TLV755P: ≥ 1 µF). |
| — | Pocket-floor insert (EU): printed 0.6 mm floor, bonded to the trim | printed | D-35: carries the sensor-flex tongue with two flush gold pads. |
| — | Double-sided tape, 0.06 mm | 3M 467MP | D-45: tape points in docs/ASSEMBLY.md (jumper pad end, tongues, NA floor insert, sensor-flex stiffeners, SHT45 tail). |
| — | Cover flex stiffener, FR4 0.3 mm, with two Ø1.4 holes | PCBWay (with the cover flex) | D-45: on the pad and regulator sections; the cover's pegs are heat-staked through it. |
| — | Supplied BILRESA magnet, cut | (ships with the remote) | D-43: cut once across to an 18.5 mm piece from one round end (~47.4 × 17.5 magnet, ESTIMATE); round end down in the recess (NA) / under the cap (EU). |
| — | Pocket-floor insert (NA): printed 0.6 mm floor on the insert's pocket floor | printed | D-41: carries the jumper's tongue with two flush gold pads (battery-free remote). |
| — | EU sensor flex | PCBWay flex, single layer, 0.12 mm, FR4 stiffeners 0.15 mm; `pcb/sensor/` eu_sensor_flex | D-42: MSR-2 CN2 → spring-pin pads → tongue to the floor pads, SHT45 on the tail, microphone. Not orderable until CN2 is confirmed. |
| — | Board posts ×4 (+1 spare) | printed, `print/posts_PC-FR.3mf` | D-28: screw into the insert, snap through the board's mounting holes. |
| — | M4 × 0.7 tap and M4 die | any | Tap the insert's four boss holes, cut the posts' studs after printing. |
| — | #6-32 × 1" oval-head screws | — | ×2, to box ears. |
| — | **Filament, insert: Elegoo PC-FR** (UL 94 V-0 per listing) | see PRINTING.md | ≈ 44 g. Keep the TDS on file. |
| — | Filament, trim + test fits: PETG (ASA in sun) | see PRINTING.md | ≈ 33 g trim, ≈ 110 g test prints. |

## Links
- PCB order pack + human-review checklist: `pcb/fab/README.md`
- IRM-03 datasheet (2025-08-08): https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF
- Harwin S7081-42R drawing: https://content.harwin.com/asset/8cd5d0a8-d578-46b3-8278-7289045a1613/DRG-02322-Technical-Drawing-Datasheet-S7081R-pdf.pdf
- Elegoo PC-FR listing (UL 94 V-0 claim): https://www.3djake.com/elegoo (search PC-FR); get Elegoo's TDS
- MSR-2 GPIO add-on (mezzanine pins 3V, 5V, GND, I²C, 6 GPIO): https://thepihut.com/products/gpio-add-on-for-apollo-automation-msr-2
- MSR-2 ESPHome page: https://devices.esphome.io/devices/apollo-automation-msr-2
- MSR-2 firmware repo: https://github.com/ApolloAutomation/MSR-2
- DMM-4026-B-I2S-R datasheet: https://api.puiaudio.com/filename/DMM-4026-B-I2S-R.pdf
- BILRESA: https://www.ikea.com/us/en/p/-70617457/
