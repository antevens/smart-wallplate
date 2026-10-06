# Bill of materials (per plate)

Prices/stock as seen Oct 2026; re-check. Bold = safety-critical, don't substitute without review.

| Ref | Part | MPN / source | Notes |
|-----|------|--------------|-------|
| — | IKEA BILRESA remote, scroll wheel | IKEA 906.174.56 (white) | Kept intact, 2×AAA. Remove nothing. |
| — | Steel magnet target | from BILRESA wall mount or similar | MEASURE size. |
| S1 | **Rocker SPST 16 A 250 VAC** | **Bulgin C1300AABBEN602A** (DigiKey 1091-1013-ND) | CSA, UL; 27.3×12.3 mm snap-in; 0.250" QC. Confirm ENEC + panel thickness on datasheet. Alt (EU-only): Würth 471005264152 (ENEC/UL). NA-only budget alt: E-Switch RB141C1100. |
| — | Insulated 0.250" female QC, fully sleeved | any listed | ×2 |
| PS1 | **AC-DC 5 V 600 mA** | **Mean Well IRM-03-5** (DigiKey 1866-3020-ND) | 85–305 VAC, 37×24×15 mm. |
| J1 | **Terminal block 2-pos 5.08 mm** | e.g. Phoenix Contact MKDS 1,5/ 2-5,08 | ≥300 V rating. |
| F1 | **Fuse, time-lag, TR5** | e.g. Littelfuse 392 series | Rating per IRM-03 datasheet. |
| RV1 | **MOV 275 VAC, 7 mm** | e.g. TDK/EPCOS S07K275 | Covers 120 V and 230 V. |
| C1 | Output cap (optional) | per IRM-03 datasheet | |
| J2 | JST-XH 2-pin | B2B-XH-A | 5 V out to MSR-2. |
| PCB | Carrier PCB 40×36 mm, 2-layer 1.6 mm | pcb/ | Routed slot. |
| — | Apollo MSR-2 mmWave multisensor | apolloautomation.com / The Pi Hut | ESP32-C3, LD2410B, DPS310, LTR-390; optional SCD-40. Used out of case. |
| — | SHT45 breakout (small) | e.g. Adafruit SHT45 breakout | On MSR-2 I²C header. |
| — | 5 V lead, 300 V-rated insulation | — | PSU → MSR-2. |
| — | #6-32 × 1" oval-head screws | — | ×2, to box ears. |
| — | Filament: UL94 V-0 (barrier), PETG/ASA (trim) | see PRINTING.md | |

## Links
- MSR-2 ESPHome page: https://devices.esphome.io/devices/apollo-automation-msr-2
- MSR-2 firmware repo: https://github.com/ApolloAutomation/MSR-2
- BILRESA: https://www.ikea.com/us/en/p/-70617457/
