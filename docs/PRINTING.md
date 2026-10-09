# Printing

Printer: **Elegoo Centauri Carbon 2 Combo** (256 × 256 × 256 mm, enclosed, hardened
0.4 mm nozzle up to 350 °C, bed up to 110 °C, CANVAS 4-filament hub). Slicer:
**OrcaSlicer** (tested 2.4.2, Linux AppImage). ElegooSlicer (an OrcaSlicer fork, tested
1.5.3.5) ships the same CC2 profiles and opens the same projects. The CANVAS hub isn't needed:
every part is single-material.

## Files
| File | Part(s) | Filament | Est. time / mass (OrcaSlicer 2.4.2) |
|------|---------|----------|------------------------------------------|
| `print/coupons_PETG.3mf` | pocket+well+magnet coupon, MSR-2 bay coupon, rocker panel ladder | PETG | 2 h 06 m / 53 g |
| `print/insert_PETG_testfit.3mf` | NA box insert (fit check only, **not for mains**) | PETG | 2 h 04 m / 50 g |
| `print/trim_PETG.3mf` | NA trim plate | PETG (ASA if in sun) | 56 m / 31 g |
| `print/insert_PC-FR.3mf` | NA box insert, **final** | Elegoo PC-FR (UL94 V-0) | 1 h 56 m / 45 g |
| `print/posts_PC-FR.3mf` | NA board posts ×5 (4 + 1 spare), lying on their flat | Elegoo PC-FR (UL94 V-0) | 7 m / 2 g |
| `print/backcover_PETG.3mf` | replacement back cover for the battery-free BILRESA (D-35), back down | PETG | 19 m / 7 g |
| `print/floor_inserts_PETG.3mf` | pocket-floor inserts, NA and EU (0.6 mm, 0.08 mm layers for the flex recess) | PETG | 11 m / 3 g |
| `print/eu_cap_PETG_testfit.3mf` | EU cap (fit check only, **not for mains**), face down | PETG | 40 m / 11 g |
| `print/eu_cap_PC-FR.3mf` | EU cap, **final** (the EU barrier), face down | Elegoo PC-FR (UL94 V-0) | 35 m / 10 g |
| `print/eu_trim_PETG.3mf` | EU trim plate, face down | PETG | 1 h 23 m / 48 g |

Open a `.3mf` in OrcaSlicer, check the plate, slice, send. The projects carry the
printer (CC2 0.4 nozzle), filament and process settings; the parts are already
oriented. `print/profiles/*.json` hold just the process overrides, importable as
user presets. Thumbnails are missing (generated headless); the slicer redraws them.

Regenerate after any CAD change: `make cad check print`. `make print` downloads the
pinned OrcaSlicer AppImage into `.tools/` (checksum-verified) on first use; set `SLICER`
to use another OrcaSlicer build. Headless machines need `xvfb-run` (`make system-deps`). Sliced G-code for checking
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
5. Battery-free remote: `backcover_PETG` on a BILRESA (latches, steel plate, contact positions,
   the end fingers' ramp), `floor_inserts_PETG` in the pocket. Cut the supplied magnet first (D-43:
   one straight cut, an 18.5 mm piece with one round end; check its real size).
6. EU: `eu_cap_PETG_testfit` + `eu_trim_PETG` in a 60 mm round box (domes, depth of the board
   stack), then `eu_cap_PC-FR`.

Many BILRESA dimensions are `ESTIMATE` (from photos and drawings, `docs/MEASUREMENTS.md`): the
first prints of the trim pockets, the back cover and the floor inserts are for measuring and
adjusting, not final parts.

## Settings (and why)
- **Back cover** (`COVER`): back down as modelled, 3 walls (1.2 mm), 2 bottom layers (the 0.4 mm
  floor under the steel plate and the regulator), 30 % gyroid, no supports (the back's round-over
  is filled to 45° below its 45° point for that).
- **Floor inserts** (`FLOOR`): flat, 0.08 mm layers after a 0.2 mm first layer, so the flex
  recess (0.14 mm, 0.26 mm at the EU fold) prints; solid.
- **EU cap**: the EU barrier, `BARRIER` settings like the NA insert, face down.
- **Insert** (`BARRIER`): the whole insert is barrier, so no modifiers are needed:
  6 walls (≈ 2.7 mm, so every 1.6 mm barrier wall prints solid), 6 top/bottom layers,
  40 % gyroid, no supports, 5 mm outer brim for PC-FR (warping). Orientation: as
  modelled, lowest face (the rocker panel's underside) on the bed. `make check` verifies
  there is no unsupported overhang wider than 3 mm (worst: 2.3 mm seal band; the flange
  underside is a 45° chamfer).
- **Trim** (`TRIM`): face down on the textured PEI sheet (gives the face its finish).
  7 bottom layers so the 1.2 mm radar skin over the MSR-2 is fully solid; 4 walls, 20 %.
  Only bridges are the 2–3 mm vent windows.
- Base process: "0.20mm Strength @Elegoo CC2 0.4 nozzle"; bed: Textured PEI Plate.
- PC-FR: stock "Elegoo PC-FR @ECC2" profile. Elegoo's data sheet (as listed on
  spoolscout.com/data-sheets/elegoo): dry 80 ± 5 °C for 8 h before use (required); print
  and store at ≤ 20 % RH (sealed, desiccant); nozzle 260–280 °C, hardened steel ≥ 0.4 mm;
  bed 90–110 °C on textured/smooth PEI with glue (required); enclosure required, chamber
  45–60 °C; speed < 100 mm/s. Keep the chamber closed and let the part cool on the plate.
- PC-FR is much weaker across layers than along them (tensile 26 vs 55 MPa, impact
  12.2 vs 70.9 kJ/m², data sheet), which is why the board posts print lying down.

## Materials
- Test fits: PETG.
- Insert (barrier): Elegoo PC-FR for now. Its data sheet claims flame retardancy and
  rapid self-extinguishing but states no UL94 class or test thickness. Certification is
  out of scope for this stage (human decision 2026-10-08); a spool with a stated UL94 V-0
  rating will be chosen before an installed build, and its rated thickness goes into
  `V0_RATED_T` (`make check` compares it with the thinnest barrier wall, 1.6 mm).
- Trim: PETG or ASA.

## Checks after printing
- Remote drops in and lifts out with the finger scoops; magnet holds.
- Magnet strength: fit the supplied magnet in its recess on the pocket coupon
  first. It sits 0.5 mm below the seat (`MAGNET_SETBACK`).
  - Too strong: add a thin non-magnetic spacer on top of it (tape, card), or
    reprint with a larger `MAGNET_SETBACK`. If the magnet is a flexible sheet,
    it can also be cut down with scissors.
  - Too weak: shim under the magnet to bring it up to the seat.
  - Do not cut a rigid magnet: ceramic magnets shatter, and neodymium dust
    can ignite.
- Rocker snaps in and latches; rocker clears the remote's back in both positions.
- Trim seats on the flange with the two key pins; island flush with the face.
- Board posts (D-28): tap the insert's four boss holes M4 × 0.7 (7 mm deep, keep the tap
  square, clear the chips), cut the posts' Ø4 studs with an M4 die, screw the posts in by
  the hex collar until it seats on the boss. The board then snaps over the four heads.
- MSR-2 detection range compared with and without the radar skin.
