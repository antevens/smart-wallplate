# Smart wall plate

Replacement for a single-gang light switch: recessed IKEA BILRESA remote, hidden
emergency rocker, Apollo MSR-2 mmWave presence + SHT45 climate + a push-to-talk
microphone for Home Assistant voice, powered by a Mean Well IRM-03-5 on the wiring board.

Start with `AGENTS.md` (for people too), then `docs/SAFETY.md`. `docs/PRINTING.md` lists the print
jobs in order, `docs/ASSEMBLY.md` what holds each part, `docs/MEASUREMENTS.md` what is measured and
what is still an estimate.

Two variants: **NA** (single-gang Decora box, this page's main renders) and **EU** (round DIN 49073
box, `cad/build123d/eu/`, `pcb/eu/`). Both can run the BILRESA without batteries through a
replacement back cover powered from the plate.

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
make pcb             # all boards and flexes: ERC/DRC, STEP, PCBWay packs -> pcb/fab/, pcb/eu/fab/
make eu              # EU variant: CAD, checks, renders
make renders         # docs/renders/*.png
```

Nothing here is certified or code-compliant; see `docs/SAFETY.md`.

## How it is meant to be used

The design assumes every light bulb and device on the switched circuit is a smart
device that turns itself on and off (here IKEA Matter-over-Thread bulbs). The circuit
stays powered; day-to-day control is wireless: the BILRESA remote in the plate, Home
Assistant, the IKEA app, or Alexa / Google / other assistants.

The rocker hidden behind the remote is not the everyday light switch. It is there for
two cases:

- **Controller or cloud down.** When Home Assistant, the IKEA hub or the voice
  assistant is unavailable, turn the rocker off and on again. The bulbs restart and come
  on by themselves at their built-in power-on brightness. This needs each bulb's power-on
  behaviour set to "On" (D-8); check it per bulb.
- **Safety.** Off cuts line and neutral to the fixtures on this circuit (and powers down
  the plate's sensors), for example when a bulb or fixture misbehaves or needs changing.
  It is not a substitute for the breaker: turn the breaker off before working on any
  wiring (`docs/SAFETY.md`).

Voice: the plate's microphone streams to Home Assistant's Assist pipeline only when
listening is started from Home Assistant, for example by an automation on a BILRESA button
(D-29). There is no wake word and no speaker in the plate; replies go to another device.

Plain (non-smart) bulbs on this circuit would just follow the rocker, and the remote,
the sensors and the automations could not control them.

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

Power contact: two spring fingers on the flex press on the gold pads of the 5 V jumper's
stiffened end, which sits on a shelf off the insert flange.

![v0.3 spring-finger power contact](docs/renders/v0.3_contact.png)

5 V power path (insert cut at the pass-through, seen from the right): a single-layer flex
jumper plugs into J2 on the wiring board (Hirose FH12-6S, slide lock), folds once between the
board and the insert (a 40 mm service loop: plug it in with the board held beside the insert,
where the latch can be seen), goes up through the pass-through and out of the flange, and ends
on the shelf under the spring fingers. No wires, no solder joints at assembly.

![v0.3 5 V power path](docs/renders/v0.3_power.png)

Face plate lifted off (trim see-through): the flex with the MSR-2, SHT45, mic and spring fingers goes
with the face plate; the 5 V jumper (wiring board J2 -> pass-through -> pad end on the shelf) stays on
the insert side. The fingers on the jumper's pads are the only electrical interface (R9, checked).

![v0.3 face plate and insert separated](docs/renders/v0.3_separation.png)

Microphone (D-29, push-to-talk voice to Home Assistant): an I²S MEMS microphone under the
flex in the right channel, its port sealed by a gasket ring to a Ø1.0 sound hole in the face
skin. Sections through the sound hole, across and along the channel:

![v0.3 microphone sections](docs/renders/v0.3_mic_section.png)

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
corner holes take the insert's snap posts; they are unplated with no copper round them, and the
PE ring detours round them, so earth continuity never depends on the posts or on vias.

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

### EU variant (concept, D-30, D-36)

A separate design for a round EU flush box (68 mm hole saw, Ø60 inside); `make eu`, `cad/build123d/eu/`,
`pcb/eu/`. The remote sits flush on a V-0 cap over the box; the emergency rocker (Marquardt 1802.2504,
as on the NA plate) under it is hidden until the remote is lifted out. Two boards: a mains board at
the rocker's PCB seat (rocker, two WAGO push-in blocks, fuse, MOV, PSU over a routed relief slot,
5 V island with a header) and a 5 V board just under the cap (pin socket on the header, two spring
pins up through the cap onto gold pads on the sensor flex: nothing soldered, wired or plugged
across). Box values are catalogue placeholders until measured; the stack reaches 43 mm deep (to be
tried in a box).

| Remote in place | Remote lifted: rocker |
| --- | --- |
| ![EU plate](docs/renders/eu_front.png) | ![EU plate, remote out](docs/renders/eu_remote_out.png) |
| ![EU section](docs/renders/eu_section.png) | ![EU box from behind](docs/renders/eu_box.png) |

![EU exploded](docs/renders/eu_exploded.png)

Face plate lifted off: the spring pins on the 5 V board stand through the cap; the flex's pads on
the pins are the only interface (R9, checked).

![EU face plate and cap separated](docs/renders/eu_separation.png)

| Flex | Power contact through the cap |
| --- | --- |
| ![EU flex](docs/renders/eu_flex.png) | ![EU spring-pin contact](docs/renders/eu_contact.png) |

Section through the spring pins: 5 V board, pins through the cap, flex pads, trim rib behind them.

![EU contact section](docs/renders/eu_contact_section.png)

Mains board: L pours on the front, N pours on the back, the relief slot under the PSU, the 5 V island
with the header; installer labels on the back.

| Mains board, front | Mains board, back |
| --- | --- |
| ![EU mains board, front](docs/renders/eu_mains_board_front.png) | ![EU mains board, back](docs/renders/eu_mains_board_back.png) |
| ![EU mains board, front copper](docs/renders/eu_mains_board_copper_front.png) | ![EU mains board, back copper](docs/renders/eu_mains_board_copper_back.png) |

| 5 V board, front | 5 V board, back |
| --- | --- |
| ![EU 5 V board, front](docs/renders/eu_5v_board_front.png) | ![EU 5 V board, back](docs/renders/eu_5v_board_back.png) |

### Replacement back cover (D-35, D-40, D-41, D-44, D-45)

Runs the remote without cells. The printed cover snaps onto the remote like the original (clips at
the top and bottom, side ribs, a pry notch) and carries the remote's magnet plate in a clipped pocket
and a flex: two spring fingers poke through windows in its back onto flush gold pads (+5 V, GND) in a
thin pocket-floor insert, a 3.3 V regulator on the flex feeds the remote, and at the terminal end two
more fingers press on the remote's VBAT plate and GND spring. The flex is held by a stiffener and two
heat-staked pegs and, at the end, by lips and hooks on the contact blocks. On NA the floor pads come
from a tongue of the 5 V jumper through the insert above the wall plane; on EU from a tongue of the
sensor flex. No new openings in the mains barrier. Several remote dimensions are still estimates
(`docs/MEASUREMENTS.md`).

| NA, exploded: floor insert, tongue, cover, remote | NA, section on the tongue |
| --- | --- |
| ![Battery-free, exploded](docs/renders/v0.3_battery_free.png) | ![Battery-free, tongue section](docs/renders/v0.3_tongue.png) |

| Cover, inside | Cover, back (fingers free) |
| --- | --- |
| ![Back cover, inside](docs/renders/bc_inside.png) | ![Back cover, back](docs/renders/bc_back.png) |

| Pocket-floor insert in the EU plate | Exploded: remote, cover, floor insert, plate |
| --- | --- |
| ![Pocket-floor insert](docs/renders/bc_floor.png) | ![Back cover, exploded](docs/renders/bc_exploded.png) |

Cut through a finger: window, finger on the floor pad, ledge, flex. And through the VBAT contact:
the finger on the end section, its dome on the remote's battery plate.

![Back cover, finger section](docs/renders/bc_finger_section.png)

![Back cover, VBAT contact section](docs/renders/bc_contact_section.png)

![Back cover flex, copper](docs/renders/cover_flex_copper_front.png)

### Sensor flex and 5 V jumper

KiCad projects in `pcb/sensor/` (D-27). The flex is drawn flat: one strip, folded twice at 45°
in the trim. Left to right: CN2 plug (placeholder, not for fabrication yet), the microphone on
its widened section (D-29), the two spring fingers over the jumper's pads, the SHT45 at the tail.

![Sensor flex, copper](docs/renders/sensor_flex_copper_front.png)

5 V jumper, drawn flat (two layers): FH12 contacts at the left, gold pads for the spring fingers at
the right (+5 V first, GND passing it to the far pad), and the battery-free tongue down to its two
floor pads.

![5 V jumper, copper](docs/renders/power_jumper_copper_front.png)

EU sensor flex, drawn flat: CN2 plug, the microphone on its outer side, the two pads under the
spring pins, the battery-free tongue between them (folded 45° on the floor), the SHT45 at the tail.

![EU sensor flex, copper](docs/renders/eu_sensor_flex_copper_front.png)
