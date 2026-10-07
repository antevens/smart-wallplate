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
| J2 | JST PH 2-pin, SMD, side entry | JST S2B-PH-SM4-TB(LF)(SN) | 5 V out to MSR-2 (1 = +5 V, 2 = GND). |
| PCB | Wiring board 47 × 72 mm, 2-layer 1.6 mm | PCBWay; order pack in `pcb/fab/` | Routed isolation slot in the outline. S1 is soldered by hand after it is snapped into the insert. Copper weight: thermal review. |
| — | Apollo MSR-2 mmWave multisensor | apolloautomation.com / The Pi Hut | ESP32-C3, LD2410B, DPS310, LTR-390; optional SCD-40. Used out of case. |
| U? | SHT45 | Sensirion SHT45 (DFN-4 1.5 × 1.5) | Soldered on the sensor flex tail, I²C from the MSR-2 (D-27). |
| — | Sensor flex (to design) | PCBWay flex, single layer, FR4 stiffener at the plug end | D-27: MSR-2 CN2 → power contact → SHT45 on the tail. |
| — | CN2 mating plug | TBD (0.4 mm, 2 rows; part open) | D-27; confirm from the GPIO add-on's plug or Apollo. |
| — | SMT spring fingers ×2 | **Harwin S7081-42R** (gold, 4 A) | D-27: on the sensor flex, +5 V and GND, working height 2.0 mm. |
| — | Target board, 0.6 mm, ENIG pads | PCBWay, with the flex | D-27: on the insert shelf; the 5 V lead is soldered to it. |
| — | 5 V lead: twin, 2 × 0.8 mm OD wires (≈ 28 AWG), 300 V-rated insulation, JST PH plug | — | J2 (JST PH) → pass-through → target board lead pads. Lead OD ≤ 1.6 mm to exit the pass-through under the trim skin (`LEAD_D`). |
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
- BILRESA: https://www.ikea.com/us/en/p/-70617457/
