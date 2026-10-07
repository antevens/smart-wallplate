# Smart wall plate

Replacement for a single-gang light switch: recessed IKEA BILRESA remote, hidden
emergency rocker, Apollo MSR-2 mmWave presence + SHT45 climate, powered by a
Mean Well IRM-03-5 on a small carrier PCB.

Start with `AGENTS.md` (for people too), then `docs/SAFETY.md`.

v0.2 is two printed parts: a **box insert** (all mains/low-voltage barrier geometry,
UL94 V-0 PC-FR) and a **trim plate** (PETG/ASA), for an Elegoo Centauri Carbon 2.
The PSU carrier PCB is a KiCad 9 project with a PCBWay order pack.

```bash
make system-deps     # once, Ubuntu 24.04 (KiCad 9, headless slicer libs)
make setup           # once (venv + pinned OrcaSlicer)
make cad check       # CAD -> build/, all checks must pass
make print           # OrcaSlicer projects -> print/*.3mf
make pcb             # KiCad ERC/DRC + PCBWay pack -> pcb/fab/
```

Nothing here is certified or code-compliant; see `docs/SAFETY.md`.

## Renders

### v0.2

Cross-sections of the assembly: box insert (red, UL94 V-0), trim plate (blue),
PSU carrier (green). The dashed line is the wall surface. Regenerate with
`make renders`.

![v0.2 assembly cross-sections](docs/renders/v0.2_sections.png)

PSU carrier, component side, from `make pcb`:

![PSU carrier, isometric](pcb/fab/psu_carrier_3d.png)

| Top | Bottom |
| --- | --- |
| ![PSU carrier, top](pcb/fab/psu_carrier_3d_top.png) | ![PSU carrier, bottom](pcb/fab/psu_carrier_3d_bottom.png) |

### v0.1 concept (superseded)

Single-piece OpenSCAD plate, kept in `reference/v0.1-openscad/` for reference.

| Front | Remote lifted out |
| --- | --- |
| ![v0.1 front](reference/v0.1-openscad/renders/01_front.png) | ![v0.1 remote out](reference/v0.1-openscad/renders/02_remote_out.png) |

| Section | Back, mains side |
| --- | --- |
| ![v0.1 section](reference/v0.1-openscad/renders/03_section.png) | ![v0.1 back](reference/v0.1-openscad/renders/04_back_mains_side.png) |

![v0.1 PSU PCB and wiring concept](reference/v0.1-openscad/renders/05_psu_pcb_and_wiring.png)
