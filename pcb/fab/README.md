# PSU carrier v0.2 – PCBWay order pack

**Not certified. Do the human-review checklist below before ordering.**

| File | Use |
|------|-----|
| `psu_carrier_v0.2_gerbers.zip` | Upload as the PCB file: RS-274X Gerbers with Protel extensions, Excellon drills in mm with PTH and NPTH separate, drill maps |
| `psu_carrier_v0.2_bom.csv` | Assembly BOM in PCBWay's column layout, with MPNs |
| `psu_carrier_v0.2_centroid.csv` | Centroid file. All parts are THT on the top (F) side. Origin = board centre |
| `psu_carrier_v0.2_assembly.pdf` | Assembly drawing (F side: fab, silk, courtyards) |
| `psu_carrier_v0.2_back_silk.pdf` | B side (mirrored view) |
| `psu_carrier_v0.2_schematic.pdf` | Schematic |
| `psu_carrier_3d*.png` | Renders |
| `erc.rpt`, `drc.rpt` | Latest ERC and DRC reports (0 violations, all severities, schematic parity on) |

## PCB order settings
- Board type: single pieces. Size 42 × 44 mm, quantity as needed.
- Layers 2, FR-4 TG130–150, thickness 1.6 mm, 1 oz outer copper.
- Min track/spacing ≥ 6/6 mil (the design uses ≥ 0.6 mm tracks). Min hole 0.6 mm.
- Surface finish HASL lead-free, or ENIG.
- Solder mask green, silkscreen white, both sides.
- **The outline has a 2.0 mm routed slot** from the top edge under the module. It is in
  Edge.Cuts and is part of the board outline, not a drill. Mention "routed isolation slot in
  outline, do not omit" in the order remarks.
- No castellations, no impedance control, no V-cut.

## Assembly (PCBWay "Turnkey" or "Kitted")
- THT only, 6 unique parts, one side (top/F). Wave or selective solder is fine.
  IRM-03 limits per its datasheet: wave 265 °C 5 s max, hand 390 °C 3 s max.
- PS1 must sit flush on the board. Trim leads on the B side to ≤ 1.5 mm, because the B side
  rides close to the plastic of the plate insert.
- C1 is polarised (+ = square pad 1). J1 wire entry must face the board's top edge
  (the "L' N" silkscreen side); see the assembly PDF.
- Source exactly the MPNs in the BOM for PS1, F1, RV1 and J1 (safety-critical; no substitutes
  without review). C1 may be any 47 µF ≥ 16 V 105 °C radial, 5 mm dia, 2.0 mm pitch, ≤ 11 mm tall.

## Human review before ordering
- [ ] F1 rating T1A is the designer's choice. Mean Well's IRM-03 spec sheet and PCB installation
      manual give no fuse rating; inrush is 20 A typ at 230 VAC. Confirm against the Littelfuse
      392 I²t and the 15 A branch breaker.
- [ ] Isolation targets in `../kicad/psu_carrier.kicad_dru` (PRI–SEC ≥ 6.0 mm clearance and
      creepage, L–N ≥ 2.5 mm) reviewed against IEC 62368-1. They are targets, not a compliance claim.
- [ ] Approvals (CSA/cUL) on J1, F1 and RV1 are adequate for your BC homeowner permit and inspector.
- [ ] The board fits the printed insert rails. Run `make cad check` with the STEP in `cad/vendor/`.
- [ ] Open the Gerbers in a viewer (PCBWay's online viewer is fine) and confirm the slot is present.

## Regenerate
From the repo root: `pcb/tools/export_fab.sh`. That rebuilds libs, schematic and board from
`pcb/tools/parts.py`, runs ERC/DRC (and fails on any violation), then writes everything here
plus `cad/vendor/psu_carrier.step`.

Suggested Makefile target:
```
pcb:
	pcb/tools/export_fab.sh
```

## Sources
- IRM-03 datasheet, rev 2025-08-08: https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF
- Mean Well PCB-type installation manual: https://www.meanwell.com/Upload/PDF/PCB_EN.pdf
- Littelfuse 392 series: https://www.littelfuse.com/products/fuses/axial-radial-thru-hole-fuses/te5-fuses/392
- TDK B72207S0271K101: https://www.digikey.com/en/products/detail/epcos-tdk-electronics/B72207S0271K101/593820
- Phoenix 1715721: https://www.phoenixcontact.com/en-ca/products/pcb-terminal-block-mkds-15-2-508-1715721
