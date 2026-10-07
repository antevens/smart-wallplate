# Wiring board (v0.3)

The single wiring board for the v0.3 plate (docs/DESIGN.md D-24, D-25, D-26). One board
carries the house wiring terminal block, the
emergency rocker that switches line and neutral, and the PSU that feeds the MSR-2.

Spacing values below are design targets for human review. Nothing here is a
compliance claim, and nothing on this board has been checked by a third party.

## Layout

Coordinates are front view in millimetres: X right, Y up toward the rocker, origin at
the board centre. F faces the plate, B faces the box.

- Board: 47 x 72 x 1.6 mm, corner radius 1.5 mm.
- Routed slot: 5 mm wide at X 3.0, from the bottom edge up to Y -10.9, under PS1.
- PE ring on both layers round the AC part, with stitching vias about every 4 mm.
- 5 V area: bottom right (X 7 to 19.5, Y -33.5 to -13), GND pour on F.
- Mounting holes for the insert's snap posts (D-28), 2.6 mm: MH1 (-21, 33.5), MH2
  (-21, -33.5), MH3 (21, 24.77) plated with a 3.6 mm PE ring; MH4 (21, -33.5) unplated.
  Board-only footprints, not in the BOM or centroid. Mains copper keeps 1.0 mm from holes.

## Parts

| Ref | Part | MPN | Side, position | Source |
| --- | --- | --- | --- | --- |
| S1 | Marquardt rocker, DPST, PCB pins | 1802.2504 | F, (0, 18), turned 90 degrees | Marquardt drawing 1802.2504 rev g (K-drawing 18022504.03) |
| J1 | WAGO PCB terminal block, 6-pole, 5 mm, lever | 2604-1106 | B, pin 1 row at (15.5, 0.93) | <https://www.wago.com/global/pcb-terminal-blocks-and-pluggable-connectors/pcb-terminal-block/p/2604-1106> |
| PS1 | Mean Well AC-DC module, 5 V 600 mA | IRM-03-5 | B, under the slot | <https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF> |
| F1 | Schurter UMT 250 SMD fuse, T1A 250 VAC | 3404.2416.22 | F, (-14.6, -23) | <https://us.schurter.com/bundles/snceschurter/epim/_ProdPool_/newDS/en/typ_UMT_250.pdf> |
| RV1 | TDK SMD varistor 275 VAC | B72660M0271K093 (CU4032K275G2) | F, (-5.5, -22) | <https://www.farnell.com/datasheets/2921094.pdf> |
| C1 | Murata MLCC 22 uF 10 V X5R 1206 | GRM31CR61A226KE19L | F, (13, -26) | <https://www.murata.com> |
| J2 | JST PH 2-pin SMD, side entry, 5 V out | S2B-PH-SM4-TB(LF)(SN) | F, (13, -19) | <https://www.jst-mfg.com/product/pdf/eng/ePH.pdf> |

S1 data from the drawing:

- Contacts 1-1a and 2-2a.
- Holes 1.3 (+0.1) mm (drilled 1.4 mm here) on a 10.2 x 7 mm grid as mounted.
- Body 22 x 18.6 mm below the panel, flange 24 x 21 mm.
- PCB seat 16.2 mm below the panel face; rocker 5.3 mm above it.
- Marked ratings: ENEC 12(4) A 250 V~; UL/CSA 15 A 125-250 VAC.
- The drawing is not in the repository.

## Nets

| Net | Class | Connects |
| --- | --- | --- |
| /L_IN | Mains_L | J1.5, S1.1 |
| /L_SW | Mains_L | J1.4, S1.1a, F1.1 |
| /L_F | Mains_L | F1.2, PS1.1 (AC/L), RV1.1 |
| /N_IN | Mains_N | J1.3, S1.2 |
| /N_SW | Mains_N | J1.2, S1.2a, PS1.3 (AC/N), RV1.2 |
| /PE | PE | J1.1, J1.6, PE ring |
| +5V | SELV | PS1.16, C1.1, J2.1 |
| GND | SELV | PS1.14, C1.2, J2.2 |

S1 pin positions (front view): L_IN (-5.1, 14.5), L_SW (-5.1, 21.5), N_IN (5.1, 14.5),
N_SW (5.1, 21.5).

Load current path:

- Line: J1.5 to S1.1 on F, then S1.1a to J1.4 on B. The B path runs down under J1 and
  up the left edge.
- Neutral: J1.3 to S1.2 on F, then S1.2a to J1.2 on B. The B path runs up the right side.

## Rules

The rules are in `kicad/wiring_board.kicad_dru`, written by `tools/gen_project.py`.

- L to N: 3.5 mm.
- L_IN to L_SW and L_F: 3.5 mm.
- N_IN to N_SW: 3.5 mm.
- Mains to PE: 3.5 mm.
- Mains to SELV: 8.0 mm clearance and creepage, with the routed slot.
- Mains to the PSU NC pin: 8.0 mm.
- Mains copper to board edge: 1.0 mm; other copper 0.5 mm.
- Pads of one footprint keep the part's own spacing. This is the exception for
  certified parts.

Creepage is checked only for mains to SELV. On this flat board the surface path
between copper on one layer is never shorter than the straight gap, so the 3.5 mm
targets are checked as clearance. KiCad evaluates creepage rules without the
footprint, so a per-part creepage exception cannot be written.

## Status

Done:

- Generators for the libraries, the project and rules, the schematic, the board and the
  3D envelopes.
- Placement, outline and slot, PE ring with stitching vias, pours, tracks and silkscreen.
- All nets routed.
- ERC: 0 errors, 0 warnings.
- DRC (`--severity-all --schematic-parity`): 0 violations, 0 unconnected, 0 parity issues.
- STEP model in `build/wiring_board.step`; PCBWay order pack in `fab/`; renders in
  `docs/renders/wiring_board_*.png` (`make renders`).

Open:

- Meter-check the S1 pin numbering on a sample. The drawing's side view labels the
  pins 1a / 1 / 1b.
- Confirm the J1 pin rows (y 0 and -5) and the body offset against the WAGO 2604
  dimension drawing. They are inferred from the 2601 footprint.
- Thermal review of the 15 A paths. The 3.5 mm targets between J1 terminals at 5 mm
  pitch leave only the pad width (about 1.8 mm) where each pour leaves J1. The L_SW
  return on B narrows to about 2.4 to 2.9 mm under J1 and beside the PE pad. Options
  are 2 oz copper, or different targets between in and switched terminals of one pole.
- Check S1 clearance to J1 on the back. The S1 pins at Y 14.5 have a pad edge at
  Y 13.3; the J1 body top edge is at Y 13.1.
- F1 rating (T1A) is a designer's choice. Its 200 A breaking capacity at 250 VAC
  needs review against the branch circuit's prospective fault current.
- RV1 pad gap: the datasheet's D = 10.1 mm does not match B + C + B; the larger gap
  is used.
- C1 is a generic part; any 22 uF 10 V X5R 1206 fits.

## Regenerate

Needs KiCad 9 (`kicad-cli` and the `pcbnew` Python module) and the repository's
`.venv` with build123d.

```bash
make pcb        # runs pcb/tools/build.sh
```

The script runs these steps:

- `gen_3d.py`: the S1 and J1 envelope STEPs in `kicad/3d/`.
- `gen_libs.py`: the symbol and footprint libraries.
- `gen_project.py`: the project seed and DRC rules.
- `gen_schematic.py`: the schematic.
- `gen_pcb.py`: the board, including the zone fill.
- ERC and DRC: reports go to `build/`.
- STEP export to `build/` and the PCBWay order pack in `fab/` (`gen_fab.py` writes the
  BOM and the centroid; S1 is not fitted).

All part data, nets and geometry live in `tools/parts.py`.
