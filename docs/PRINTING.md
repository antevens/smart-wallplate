# Printing

Printer and slicer are TBD (ask the human). OrcaSlicer / PrusaSlicer / Bambu Studio
all work; keep a 3MF project per part in `print/` once chosen.

## Materials
- Test fits: PETG.
- Barrier parts (pocket shell, switch well, collar; v0.2 box insert): a filament
  with a **UL94 V-0** rating on its datasheet (flame-retardant PC, PC-ABS or ASA
  grades exist). Keep the datasheet with the build record.
- Trim plate: PETG or ASA (ASA if near sunlight).

## v0.1 single-piece plate
- Orientation: face down. The remote pocket floor and switch well floor then bridge
  over open cavities → needs supports (tree supports, pocket only). This is the
  reason for the v0.2 split.
- 0.2 mm layers, 0.4 mm nozzle, 4 walls, 25–30 % gyroid.
- Radar skin is 1.2 mm = 3 extrusion widths: keep it solid, no infill pattern visible.
- The snap-in panel at the switch cutout must hit the datasheet thickness; print a
  coupon first and measure.

## v0.2 (planned)
- Box insert: printed floor-down (pocket opening up) – no supports. 100 % infill or
  ≥6 walls on all barrier walls.
- Trim plate: face down, no supports.

## Checks after printing
- Remote drops in and lifts out with the finger scoops; magnet holds.
- Rocker snaps in and latches; rocker clears the remote's back in both positions.
- PSU carrier slides into the rails and stops at the end stop.
- MSR-2 detection range compared with and without the radar skin.
