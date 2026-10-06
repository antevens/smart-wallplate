# PSU carrier PCB – specification (for the KiCad project)

Concept render: `../reference/v0.1-openscad/renders/05_psu_pcb_and_wiring.png`.
Netlist: `netlist.yaml`. Edge.Cuts: `mech/pcb_outline.dxf` (origin = board centre,
generated from `cad/build123d/params.py`).

## Board
- 40 × 36 mm, corner radius 1.5 mm, 2-layer FR-4, 1.6 mm, 1 oz Cu, HASL or ENIG.
- Slides into two plastic rails: **no copper, pads or parts within 2.0 mm of the
  left and right edges.** Bottom edge rests on an end stop.
- All parts on ONE side (the side facing away from the plate, into the box).
- Max component height 15.5 mm (the IRM-03 sets it). J1 screw access must face
  the open top edge or the board's free face.
- Top edge sits ~8 mm below the rocker body: no tall parts along the top edge.

## Circuit
J1 (L', N) → F1 (time-lag) on L' → RV1 across L–N after the fuse → PS1 IRM-03-5
AC inputs. PS1 +Vo/−Vo → optional C1 → J2 (5 V, GND) → lead to MSR-2 5 V/GND.

## Isolation (targets – human review required)
- Routed slot ≥1.5 mm wide between primary and secondary, under the module,
  running to the board edge.
- Creepage primary ↔ secondary ≥ 6.0 mm (reinforced, 250 VAC working, pollution
  degree 2 – verify against IEC 62368-1 tables before fab).
- L ↔ N creepage ≥ 2.5 mm before the fuse/MOV.
- Implement as KiCad netclasses (Primary, Secondary) + custom DRC rules.
- Silkscreen: "MAINS", "230/120 VAC", fuse rating, version.

## Footprints
- PS1: check KiCad `Converter_ACDC` library for a Mean Well IRM-03 THT footprint;
  if missing, build from the IRM-03 datasheet mechanical drawing and cite it.
- J1 5.08 mm 2-pos terminal; F1 TR5; RV1 7 mm disc, 7.5 mm pitch; J2 JST-XH 2.

## Outputs
- ERC/DRC clean (`kicad-cli`, see AGENTS.md).
- Gerbers + drill + BOM + CPL for JLCPCB in `pcb/fab/`.
- STEP to `cad/vendor/psu_carrier.step`, then add it to `cad/build123d/assembly.py`.
