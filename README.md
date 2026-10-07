# Smart wall plate

Replacement for a single-gang light switch: recessed IKEA BILRESA remote, hidden
emergency rocker, Apollo MSR-2 mmWave presence + SHT45 climate, powered by a
Mean Well IRM-03-5 on the wiring board.

Start with `AGENTS.md` (for people too), then `docs/SAFETY.md`.

The plate is two printed parts: a **box insert** (all mains/low-voltage barrier
geometry, UL94 V-0 PC-FR) and a **trim plate** (PETG/ASA), for an Elegoo Centauri
Carbon 2.

The house wiring lands on one board: L/N/PE in and out on a WAGO push-in block,
the Marquardt 1802.2504 DPST emergency rocker, and the PSU, all in a 2.5"
single-gang box. The KiCad project is in `pcb/`.

```bash
make system-deps     # once, Ubuntu 24.04 (KiCad 9, headless slicer libs)
make setup           # once (venv + pinned OrcaSlicer)
make cad check       # CAD -> build/, all checks must pass
make print           # OrcaSlicer projects -> print/*.3mf
make pcb             # wiring board: KiCad ERC/DRC, STEP, PCBWay pack -> pcb/fab/
```

Nothing here is certified or code-compliant; see `docs/SAFETY.md`.

## Renders

### v0.3

Shaded views of the assembly: trim plate (white), box insert (grey), BILRESA
remote (model), Marquardt 1802.2504 rocker (red), wiring board (green, KiCad
model), board posts (orange). Regenerate with `make renders`.

| Front | Remote lifted out |
| --- | --- |
| ![v0.3 front](docs/renders/v0.3_front.png) | ![v0.3 remote out](docs/renders/v0.3_remote_out.png) |

| Half-section | Back, mains side |
| --- | --- |
| ![v0.3 half-section](docs/renders/v0.3_section.png) | ![v0.3 back](docs/renders/v0.3_back.png) |

Exploded: remote, trim plate, box insert, the four board posts that screw into
the insert's bosses (D-28), wiring board (with the rocker, WAGO block and PSU from
the KiCad model).

![v0.3 exploded assembly](docs/renders/v0.3_exploded.png)

Sensor flex (D-27, trim and remote hidden): from the MSR-2's rear connector across
the top, down the right channel past the insert, to the SHT45 on its tail.

![v0.3 sensor flex route](docs/renders/v0.3_flex.png)

Power contact: two spring fingers on the flex press on a target board that sits on a
shelf off the insert flange; the 5 V lead is soldered to the board's top end.

![v0.3 spring-finger power contact](docs/renders/v0.3_contact.png)

5 V power path (insert cut at the pass-through, seen from the right): the twin lead leaves J2
on the wiring board, crosses between the rocker and the right-hand posts, goes up through the
pass-through and out of the flange, and drops onto the target board under the spring fingers.

![v0.3 5 V power path](docs/renders/v0.3_power.png)

BILRESA model: stadium outline, wheel with its gap ring, three LEDs, side
parting line, and a back that curves from a flat central pad out to the sides.

| Front | Back |
| --- | --- |
| ![BILRESA model, front](docs/renders/bilresa_model.png) | ![BILRESA model, back](docs/renders/bilresa_back.png) |

Cross-sections: box insert (red, UL94 V-0), trim plate (blue), wiring board
(green), board posts (orange), BILRESA (grey). The dashed line is the wall surface;
the x = -21 cut runs through two posts and their bosses.

![v0.3 assembly cross-sections](docs/renders/v0.3_sections.png)

### v0.3 wiring board

KiCad renders of `pcb/`. The front faces the plate (rocker, SMD
fuse and MOV, 5 V connector); the back faces the box (WAGO block, PSU). The four
corner holes take the insert's snap posts; three are plated into the PE ring.

| Front | Back |
| --- | --- |
| ![Wiring board, front](docs/renders/wiring_board_front.png) | ![Wiring board, back](docs/renders/wiring_board_back.png) |
| ![Wiring board, front, angled](docs/renders/wiring_board_iso_front.png) | ![Wiring board, back, angled](docs/renders/wiring_board_iso_back.png) |

Without components, so every trace and pour shows:

| Front | Back |
| --- | --- |
| ![Wiring board, bare front](docs/renders/wiring_board_bare_front.png) | ![Wiring board, bare back](docs/renders/wiring_board_bare_back.png) |
| ![Wiring board, front copper](docs/renders/wiring_board_copper_front.png) | ![Wiring board, back copper, seen from behind](docs/renders/wiring_board_copper_back.png) |

![Wiring board, bare, angled](docs/renders/wiring_board_bare_iso.png)

### v0.1 concept (superseded)

Single-piece OpenSCAD plate, kept in `reference/v0.1-openscad/` for reference.

| Front | Remote lifted out |
| --- | --- |
| ![v0.1 front](reference/v0.1-openscad/renders/01_front.png) | ![v0.1 remote out](reference/v0.1-openscad/renders/02_remote_out.png) |

| Section | Back, mains side |
| --- | --- |
| ![v0.1 section](reference/v0.1-openscad/renders/03_section.png) | ![v0.1 back](reference/v0.1-openscad/renders/04_back_mains_side.png) |

![v0.1 PSU PCB and wiring concept](reference/v0.1-openscad/renders/05_psu_pcb_and_wiring.png)
