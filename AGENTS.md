# AGENTS.md — Smart wall plate (BILRESA + MSR-2 + emergency switch)

Read this whole file before changing anything. Then read `docs/SAFETY.md`.
`docs/DESIGN.md` has the requirements and the decision log; `docs/BOM.md` the parts.

## What this project is

A replacement for a North American single-gang light switch (Decora/Leviton,
Canada, BC) in a house where every bulb is an IKEA Matter-over-Thread smart bulb.
Bulbs stay powered; control is wireless. Each plate holds:

- an **IKEA BILRESA scroll-wheel remote**, kept intact (batteries in), recessed
  into the box and held by its own magnet; it lifts out;
- a **hidden emergency rocker** behind the remote (Bulgin C1300AABBEN602A),
  in series with the lighting load. Off = bulbs AND sensor de-powered.
  Off→on with bulbs set to power-on "On" = lights on when Home Assistant is down;
- a **Mean Well IRM-03-5** (5 V / 600 mA) on a small carrier PCB, fed from the
  **load side** of the rocker, powering the MSR-2;
- an **Apollo MSR-2** (ESP32-C3 + LD2410B mmWave, ESPHome over Wi-Fi) in a bay
  above the remote, behind a 1.2 mm radar skin;
- an **SHT45** temp/humidity tab in its own vented bay below the remote,
  wired to the MSR-2's exposed I²C header.

Home Assistant runs on an Nvidia Orin NX. No Shelly / smart relay: deliberately removed.

## Repository layout

```
AGENTS.md            this file (CLAUDE.md imports it)
docs/                DESIGN (requirements + decisions), SAFETY, BOM,
                     MEASUREMENTS (placeholders to fill), PRINTING
cad/build123d/       ACTIVE parametric CAD (Python, build123d)
  params.py          single source of truth for ALL geometry
  wallplate.py       printable plate  -> build/wallplate.step|.stl
  assembly.py        plate + envelope parts -> build/assembly.step, pcb_outline.dxf
cad/vendor/          vendor STEP models (empty; see BOM)
pcb/                 PSU carrier: SPEC.md, netlist.yaml, mech/pcb_outline.dxf
                     KiCad project goes in pcb/kicad/ (not created yet)
reference/v0.1-openscad/  FROZEN first pass (OpenSCAD source, STL, renders). Do not edit.
build/               generated outputs (git-ignored)
```

## Commands

```
pip install -r cad/build123d/requirements.txt
make cad        # rebuild STEP/STL/DXF into build/
make check      # geometry sanity checks (box fit, wiring depth) - must pass
```
KiCad (9.x preferred, 8.x ok), once `pcb/kicad/` exists:
```
kicad-cli sch erc  pcb/kicad/psu_carrier.kicad_sch
kicad-cli pcb drc  --severity-all --exit-code-violations pcb/kicad/psu_carrier.kicad_pcb
kicad-cli pcb export step pcb/kicad/psu_carrier.kicad_pcb -o cad/vendor/psu_carrier.step
```

## Conventions

- Units: millimetres. Coordinates: X width, Y up, Z out of the wall; z=0 = wall
  surface; z<0 = inside the box = **mains side**.
- Every dimension lives in `cad/build123d/params.py`. Never hard-code a number in
  a model that belongs in params. The PCB outline is generated from params
  (`make cad` -> `build/pcb_outline.dxf`); if you change `PCB`, re-import Edge.Cuts.
- Values tagged `MEASURE` are placeholders. **Do not replace them with guesses or
  values "found online".** Only use readings recorded in `docs/MEASUREMENTS.md`
  or datasheet values with a cited source. If a task needs one that is missing, stop and ask.
- Keep `make check` green; extend `checks()` when you add a constraint.
- Small commits, one concern each; update `docs/DESIGN.md` decision log for any
  design decision.

## Hard constraints (do not violate; ask the human if a task seems to require it)

1. **The 15 A lighting path never runs on the PCB.** Line → rocker → load is wired with
   wire nuts. The PCB only gets a pigtail from the load side + neutral.
2. **Barrier continuity.** The pocket shell + switch well + collar separate the
   mains volume (box) from the low-voltage volume (plate hollow, remote pocket).
   No openings may be added to them except the single 5 V lead pass-through.
   Anything forming the barrier is printed in a UL94 V-0 filament (see PRINTING).
3. **PCB isolation.** Primary-to-secondary: routed slot ≥1.5 mm wide under the
   module plus ≥6.0 mm creepage target; L–N ≥2.5 mm; no copper within 2.0 mm of the
   left/right edges (they ride in plastic rails). These are design targets, not a
   compliance claim — flag them for human review, don't certify.
4. **Bought-in, certified parts carry the safety-critical jobs**: rocker (CSA/UL;
   ENEC to be confirmed), IRM-03-5 (cURus/CB/TÜV). Don't substitute uncertified
   parts on the mains side.
5. Never describe the device as code-compliant, certified, or safe to install.
   Say what was checked. Energising anything mains-side is a human decision.

## Current status (v0.1 → v0.2)

Done: concept, part selection, first-pass plate (OpenSCAD, frozen in reference/),
build123d port with parity, assembly envelopes, PCB concept (render only),
PCB outline DXF, netlist.

Not done: measurements, KiCad project, test prints, slicer profiles.

## Backlog (in order)

1. **Measurements** – help the human fill `docs/MEASUREMENTS.md`, update params,
   `make cad check`, produce test-fit prints (PETG) of: pocket+well section only,
   MSR-2 bay only (fast prints, use a `--coupon` style option you add).
2. **v0.2 split into two printed parts** (see DESIGN D-12): a *box insert*
   (pocket, switch well, collar flange, PSU rails; V-0 material; printed floor-down,
   no supports) and a *trim plate* (face, MSR-2/SHT45 bays, scoops; any filament).
   Add a keyed, screwed interface; the barrier must be entirely in the insert.
3. **KiCad PSU carrier** per `pcb/SPEC.md` + `pcb/netlist.yaml`. Look for an IRM-03
   footprint in KiCad's `Converter_ACDC` library; if absent, build it from the
   Mean Well datasheet and cite the drawing. Custom DRC rules for the slot/creepage.
   Export the board STEP into `cad/vendor/` and add it to `assembly.py`.
4. **Slicer setup** for the human's printer (model TBD — ask): 3MF projects with
   per-region modifiers (barrier walls 100 % / more perimeters), orientation as in
   `docs/PRINTING.md`.
5. Rocker removal/feel: confirm snap-in panel thickness range from the C1300
   datasheet; add a coupon print.
6. Later: EU (60 mm round box) and UK (86 mm, shallow back box) variants as
   separate param sets; jumbo-plate option; ESPHome YAML for MSR-2 + SHT45.

## Open questions for the human

- Box material (metal ears intrude + may shield the remote's radio) and depth per room.
- Neutral present in each switch box? (required for the PSU)
- Printer model / slicer.
- MSR-2 base or CO₂ version; bare-board dimensions.
- Inspector's view on a concealed emergency switch (BC homeowner permit).
