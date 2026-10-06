# Printing

Printer: **Elegoo Centauri Carbon 2 Combo** (256 × 256 × 256 mm, enclosed, hardened
0.4 mm nozzle up to 350 °C, bed up to 110 °C, CANVAS 4-filament hub). Slicer:
**OrcaSlicer** (tested 2.4.2, Linux AppImage). ElegooSlicer (an OrcaSlicer fork, tested
1.5.3.5) ships the same CC2 profiles and opens the same projects. The CANVAS hub isn't needed:
every part is single-material.

## Files
| File | Part(s) | Filament | Est. time / mass (OrcaSlicer 2.4.2) |
|------|---------|----------|------------------------------------------|
| `print/coupons_PETG.3mf` | pocket+well coupon, MSR-2 bay coupon, rocker panel ladder | PETG | 1 h 45 m / 45 g |
| `print/insert_PETG_testfit.3mf` | box insert (fit check only, **not for mains**) | PETG | 2 h 24 m / 62 g |
| `print/trim_PETG.3mf` | trim plate | PETG (ASA if in sun) | 57 m / 32 g |
| `print/insert_PC-FR.3mf` | box insert, **final** | Elegoo PC-FR (UL94 V-0) | 2 h 13 m / 55 g |

Open a `.3mf` in OrcaSlicer, check the plate, slice, send. The projects carry the
printer (CC2 0.4 nozzle), filament and process settings; the parts are already
oriented. `print/profiles/*.json` hold just the process overrides, importable as
user presets. Thumbnails are missing (generated headless); the slicer redraws them.

Regenerate after any CAD change: `make cad check print` (set `SLICER` to the
OrcaSlicer or ElegooSlicer AppImage, or put `orca-slicer` on PATH; headless machines
need `xvfb-run`). Sliced G-code for checking
time/material lands in `build/print/gcode/`.

## Order of work
1. `coupons_PETG`: rocker ladder → find the panel thickness that latches firmly,
   record it as `SW_PANEL_T` in `docs/MEASUREMENTS.md`. Pocket+well coupon → remote
   drop-in/lift-out, rocker snap-in, key pin, pass-through. MSR-2 coupon → board fit,
   radar skin, light-sensor hole.
2. Update `params.py` from the measurements, `make cad check print`.
3. `insert_PETG_testfit` + `trim_PETG` → full dry fit in the box (breaker off, nothing
   connected). Check the corner taper against the box ears.
4. `insert_PC-FR` for the installed part. Keep the filament datasheet with the build record.

## Settings (and why)
- **Insert** (`BARRIER`): the whole insert is barrier, so no modifiers are needed:
  6 walls (≈ 2.7 mm, so every 1.6 mm barrier wall prints solid), 6 top/bottom layers,
  40 % gyroid, no supports, 5 mm outer brim for PC-FR (warping). Orientation: as
  modelled, lowest face (rail lips / floor) on the bed. `make check` verifies there is
  no unsupported overhang wider than 3 mm (worst: 2.3 mm seal band; the PCB roof is
  45° gables, the flange underside is a 45° chamfer).
- **Trim** (`TRIM`): face down on the textured PEI sheet (gives the face its finish).
  7 bottom layers so the 1.2 mm radar skin over the MSR-2 is fully solid; 4 walls, 20 %.
  Only bridges are the 2–3 mm vent windows.
- Base process: "0.20mm Strength @Elegoo CC2 0.4 nozzle"; bed: Textured PEI Plate.
- PC-FR: stock "Elegoo PC-FR @ECC2" profile (280 °C). Dry the spool first; keep the
  chamber closed; let the part cool on the plate.

## Materials
- Test fits: PETG.
- Insert (barrier): a filament with a **UL94 V-0** rating on its datasheet. Elegoo
  PC-FR is listed as UL 94 V-0; get the TDS, check the rated thickness, and put it in
  `V0_RATED_T` (`make check` compares it with the thinnest barrier wall, 1.6 mm).
  The rating is for the material; a printed part is not certified by it.
- Trim: PETG or ASA.

## Checks after printing
- Remote drops in and lifts out with the finger scoops; magnet holds.
- Rocker snaps in and latches; rocker clears the remote's back in both positions.
- PSU carrier slides up the rails from the bottom end to the top stop; THT leads
  (trimmed ≤ 1.5 mm) clear the gabled roof.
- Trim seats on the flange with the two key pins; island flush with the face.
- MSR-2 detection range compared with and without the radar skin.
