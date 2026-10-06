# Bill of materials (per plate)

Prices/stock as seen Oct 2026; re-check. Bold = safety-critical, don't substitute without review.

| Ref | Part | MPN / source | Notes |
|-----|------|--------------|-------|
| — | IKEA BILRESA remote, scroll wheel | IKEA 906.174.56 (white) | Kept intact, 2×AAA. Remove nothing. |
| — | Steel magnet target | from BILRESA wall mount or similar | MEASURE size. |
| S1 | **Rocker SPST 16 A 250 VAC** | **Bulgin C1300AABBEN602A** (DigiKey 1091-1013-ND) | CSA, UL; 27.3×12.3 mm snap-in; 0.250" QC. Confirm ENEC + panel thickness on datasheet. Alt (EU-only): Würth 471005264152 (ENEC/UL). NA-only budget alt: E-Switch RB141C1100. |
| — | Insulated 0.250" female QC, fully sleeved | any listed | ×2 |
| PS1 | **AC-DC 5 V 600 mA** | **Mean Well IRM-03-5** (DigiKey 1866-3020-ND) | 85–305 VAC, 37×24×15 mm. |
| J1 | **Terminal block 2-pos 5.08 mm** | **Phoenix Contact 1715721** (MKDS 1,5/ 2-5,08) | 400 V; wire entry faces the board top edge. |
| F1 | **Fuse T1A 250 V time-lag, TR5** | **Littelfuse 39211000000** (392 series) | Rating is the designer's choice (Mean Well gives none): human review. |
| RV1 | **MOV 275 VAC, 7 mm** | **TDK B72207S0271K101** (S07K275) | 5.0 mm pitch. Covers 120 V and 230 V. |
| C1 | 47 µF 16 V radial 5 × 11 | Panasonic EEU-FC1C470 or equiv. | Datasheet ripple test uses 47 µF ‖ 0.1 µF. |
| J2 | JST-XH 2-pin | JST B2B-XH-A(LF)(SN) | 5 V out to MSR-2 (1 = +5 V, 2 = GND). |
| PCB | Carrier PCB 42 × 44 mm, 2-layer 1.6 mm, 1 oz | PCBWay, THT turnkey assembly; order pack in `pcb/fab/` | Routed isolation slot in the outline. |
| — | Apollo MSR-2 mmWave multisensor | apolloautomation.com / The Pi Hut | ESP32-C3, LD2410B, DPS310, LTR-390; optional SCD-40. Used out of case. |
| — | SHT45 breakout (small) | e.g. Adafruit SHT45 breakout | On MSR-2 I²C header. |
| — | 5 V lead, 300 V-rated insulation | — | PSU (JST-XH) → MSR-2, through the insert pass-through. |
| — | Mains pigtails L' + N, stranded 18 AWG, ≥ 300 V | — | Load side of rocker / neutral → J1. Flexible: ~5 mm to turn before the rocker body. |
| — | #6-32 × 1" oval-head screws | — | ×2, to box ears. |
| — | **Filament, insert: Elegoo PC-FR** (UL 94 V-0 per listing) | see PRINTING.md | ≈ 56 g. Keep the TDS on file. |
| — | Filament, trim + test fits: PETG (ASA in sun) | see PRINTING.md | ≈ 33 g trim, ≈ 110 g test prints. |

## Links
- PCB order pack + human-review checklist: `pcb/fab/README.md`
- IRM-03 datasheet (2025-08-08): https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF
- Elegoo PC-FR listing (UL 94 V-0 claim): https://www.3djake.com/elegoo (search PC-FR); get Elegoo's TDS
- MSR-2 ESPHome page: https://devices.esphome.io/devices/apollo-automation-msr-2
- MSR-2 firmware repo: https://github.com/ApolloAutomation/MSR-2
- BILRESA: https://www.ikea.com/us/en/p/-70617457/
