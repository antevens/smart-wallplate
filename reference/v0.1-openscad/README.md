# Smart wall plate – first pass (v0.1)

Recessed IKEA BILRESA (intact, batteries in) + hidden emergency rocker behind it +
Mean Well IRM-03-5 PSU slot + Apollo MSR-2 bay + vented SHT45 bay.
NA single-gang device box (2" × 3" opening, #6-32 ears at 83.3 mm).

## Files
- `wallplate.scad` – parametric OpenSCAD source (OpenSCAD 2021+). `part="plate"` exports the printable part; `part="assembly"` shows ghost components; `explode=50` lifts the remote out.
- `plate.stl` – printable plate (print face-down; open back sits against the wall).
- `01`–`04` renders, `05` PSU carrier PCB + box wiring concept.

## Key dimensions (v0.1)
| | |
|---|---|
| Plate | 82 × 150 mm, 13 mm proud of wall |
| Remote | sits 2 mm proud; seat 5 mm into the box |
| Rocker well floor | 15 mm into box; switch body to ~40 mm |
| PSU slot | 40 × 36 mm PCB, IRM-03-5 to ~28 mm into box |
| Left for wiring/wire nuts | ~23 mm in a 2.5" box |

## MEASURE before printing (placeholders in the .scad)
`B_W, B_H, B_D` (BILRESA outline/depth) · `SW_BEZEL, SW_ROCKER_H, SW_BODY, SW_PANEL_T` (Bulgin C1300 datasheet) · `MSR` (bare MSR-2 envelope) · `LUX_POS` (light sensor) · steel target size · your box depth `BOX_D`.

## Notes
- Pocket shell + collar form the barrier between mains (box) and low voltage (plate hollow). Print those in a flame-rated filament; PLA/PETG only for test fits.
- Metal boxes: ears intrude at top/bottom of the opening and can shield the remote's radio – check both.
- The lighting circuit (15 A) is switched with wire nuts, not through the PCB.
- PCB is a concept: take the IRM-03 footprint and pinout from Mean Well's datasheet; size F1/RV1 per datasheet.
