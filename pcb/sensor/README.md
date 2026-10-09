# Sensor flex and 5 V jumper (D-27, D-29)

Two flex circuits on the 5 V side, generated from `tools/sensor_parts.py`, which takes its
geometry from `cad/build123d/params.py` (the same routes and shelf as the CAD models in
`cad/build123d/sensor_flex.py` and `cad/build123d/jumper.py`).

Nothing here touches mains. Both boards are low-voltage only.

## Sensor flex

Single copper layer (F.Cu; KiCad keeps an empty B.Cu), polyimide, 0.12 mm, FR4 stiffeners.

In the trim the flex runs from the MSR-2 across the top, down the right channel and along the
bottom to the SHT45. Each of the two 90° corners is a 45° fold, which turns the strip over, so
in the flat it is one straight strip about 195 mm long with every part on the copper side:

- J1: mating plug for the MSR-2's rear connector CN2 (faces the MSR-2).
- J2, J3: Harwin S7081-42R spring fingers, +5 V and GND (face the jumper's pad end).
- U1: Sensirion SHT45 with C1 (100 nF) on the tail (face the trim's vents).
- MK1: PUI Audio DMM-4026-B-I2S-R I²S microphone with C2 (100 nF) and R1 (100 kΩ SD pull-down),
  in the right channel above the fingers, port towards the face skin (D-29).

The fold lines are on `Cmts.User`, the stiffeners (behind J1, behind J2/J3 and behind MK1) on
`User.1`.

Between the plug end and the strip the flex tapers over 10 mm (`FLEX_NECK_L`), shallow enough
for the ten lanes to run in parallel; the MSR-2 bay frame's notch is sized from that outline.

Over the finger section the flex widens: towards the flange over the finger pads, and into a
1 mm recess in the trim's side wall for the four tracks that pass the pads.

Above the finger section the flex widens towards the flange (to 4.4 mm from the centre line,
room y 38–46) for the microphone. Its pins face the plug, the port end the fingers; the GND ring
(soldered all round, it seals the port) surrounds a Ø0.5 hole through flex and stiffener. On the
skin side an adhesive gasket ring (OD 2.6, ID 1.0, 0.15 mm) seals the stiffener to the face
skin around the Ø1.0 sound hole.

Nets: +5V (fingers to CN2), GND, +3V3 (CN2 to the SHT45), SDA = IO1, SCL = IO0 (MSR-2 I²C
bus; SHT45 at 0x44), I2S_SCK = IO4, I2S_WS = IO6, I2S_SD = IO7, MIC_3V3 and MIC_GND (the
microphone's own CN2 contacts, joined to +3V3 and GND on the MSR-2, so its lanes cross no
others).

## Microphone firmware (D-29)

ESPHome on the MSR-2, push-to-talk: Home Assistant starts listening (for example from a BILRESA
button automation calling the action) and the voice pipeline ends it on silence. Untested
starting point:

```yaml
i2s_audio:
  - id: i2s_mic_bus
    i2s_lrclk_pin: GPIO6
    i2s_bclk_pin: GPIO4

microphone:
  - platform: i2s_audio
    id: plate_mic
    i2s_audio_id: i2s_mic_bus
    adc_type: external
    i2s_din_pin: GPIO7
    channel: left              # LR tied to GND
    bits_per_sample: 32bit     # 24-bit data in a 32-bit word
    sample_rate: 48000         # BCLK 3.072 MHz; the mic sleeps below 2.048 MHz

voice_assistant:
  microphone: plate_mic

api:
  actions:
    - action: start_listening
      then:
        - voice_assistant.start:
    - action: stop_listening
      then:
        - voice_assistant.stop:
```

Open: whether the pipeline accepts 48 kHz from this microphone on the C3 or needs 32 kHz, and
the C3's RAM / CPU headroom next to the radar, Wi-Fi and BLE.

**Not ready to fabricate.** J1's footprint (0.4 mm, 2 x 15) and its contact map are
placeholders: CN2's part and pin map are not confirmed (D-27, `docs/MEASUREMENTS.md`). The map
in `CN2_MAP` only keeps the single-layer fan-out from crossing. `tools/build.sh` writes no flex
fab files while `CN2_CONFIRMED` is false.

## 5 V jumper

Two copper layers, polyimide, 0.2 mm (design value, confirm with the PCBWay stack-up), 156 mm long
in the flat (`params.jumper_length()` plus the two ends) plus the battery-free tongue (D-41). It replaces the 5 V lead and the target board: nothing on the 5 V path is wired or
soldered at assembly (DESIGN R9).

- J1: six exposed contacts at 0.5 mm pitch on a stiffened end (3.5 wide, 0.3 thick in total,
  `JUMPER_END`, MEASURE: check against Hirose's FPC drawing for the FH12-6S) that plugs into J2
  of the wiring board (Hirose FH12-6S-0.5SH, slide lock). Contacts 1–3 GND, 4–6 +5V, as on J2.
  Which face carries the contacts against J2's bottom contacts is to be checked on a sample.
- Run: 3.0 mm wide, +5V and GND tracks 0.5 mm (the MSR-2 draws < 0.2 A).
- TP1, TP2: gold pads (4.5 × 1.8) on the stiffened pad end (0.6 mm in total, FR4), which lies
  on the insert's shelf under the spring fingers: +5 V nearer the run, GND at the far end, its
  track passing the +5 V pad on the wall side.

Assembly: plug the connector end into J2 with the wiring board held beside the insert, where
the latch can be seen; thread the end up through the pass-through (3.5 mm end, Ø4.5 hole); fit
the board; the 40 mm service loop (`JUMPER_SERVICE`) folds between board and insert; the pad end
lies on the shelf (adhesive on its stiffener).

- Battery-free tongue (D-41): leaves the pad end's inner edge between TP1 and TP2, through a tunnel in
  the insert flange (above the wall plane), down a groove in the pocket wall and the wall into the NA
  floor insert's recess (two 90° bends, copper stays up), then a run, a down strip clear of the switch
  well's opening and the pad strip: TP3 / TP4, 7 × 4 mm gold pads (+5V, GND) under the back cover's
  fingers. GND stays on F.Cu off the edge lane; +5V leaves TP1 through a via and passes under it on
  B.Cu, which is why the jumper has two layers. Drawn flat from `sensor_parts.TONGUE_PTS`.

## Back cover flex

Single copper layer, polyimide, for the replacement back cover that powers a BILRESA E2490
without cells (`cad/build123d/backcover.py`, DESIGN D-35). Drawn flat, seen from the copper side.

- J1, J2: Harwin S7081-42R spring fingers (+3V3, GND) on the pad section, which lies copper down
  on a ledge in the cover; the fingers reach through windows onto the plate's flush floor pads
  (working height 2.0 mm).
- A 2.6 mm run (through a slot under the GND contact block) to the terminal end; one 90° bend
  (copper outside).
- J1 takes +5 V from the floor (D-41); U1 TI TLV75533PDBVR (3.3 V, SOT-23-5) with C3 / C4 1 µF on
  the section below the fingers, copper down in a recess in the cover (0.4 mm wall left), feeds VBAT.
- J3, J4: Harwin S7081-42R spring fingers (VBAT, GND) on the end section, on the cell axes, long
  axis vertical with the bend end up (the battery contacts ride down the arm's ramp as the cover
  goes on), on a 0.4 mm FR4 stiffener (back side). The end section stands 2.0 mm (the fingers'
  working height) in from the cell end plane: J3 presses the remote's fixed VBAT plate, J4 its GND
  leaf spring (finger and leaf share the travel). Between them only a band passes under the
  remote's PCB strip.

Not ready to fabricate: the positions come from the FCC internal photos (REF) or are MEASURE;
`tools/build.sh` writes no `fab/cover_flex/` while `COVER_CONFIRMED` is false.

## EU sensor flex (`kicad/eu_sensor_flex.*`, D-30, D-42)

Single copper layer, the NA topology on the EU route (`cad/build123d/eu/sensor_eu.py`), drawn flat by
`tools/eu_flex_parts.py` (X developed along the strip through the dip, Y inwards).

- J1: CN2 mate (placeholder footprint and contact map, as on the NA flex). GND comes out on two
  contacts: GND (pin pad, tongue) and GND_SHT (the SHT45), joined on the MSR-2; MIC_3V3 / MIC_GND as
  on the NA flex.
- MK1 on the strip's outer side (mic section widened outwards): WS / SCK enter the inner pad column
  from above, SD from below through the gap with R1 (100k to MIC_GND) before the body; MIC_GND /
  MIC_3V3 run under the outer column with C2 across them; GND on to the port ring.
- TP1 / TP2: Ø2.4 pads under the 5 V board's spring pins, GND first (P1), then +5V (P2); +5V and
  the SHT45 lanes step under TP1.
- Battery-free tongue (D-41): off the pad section's inner edge between TP1 and TP2 (GND from TP1,
  +5V from TP2, no crossing on one layer), under the pocket wall, 45° fold beside the floor pads
  (copper up), TP3 / TP4 2.9 × 7 mm floor pads under the back cover's fingers.
- U1 SHT45 + C1 on the tail. Fab files withheld while the CN2 contact map is a placeholder.

## Regenerate

```bash
make pcb        # also builds the wiring board; or pcb/sensor/tools/build.sh
```

`build.sh` runs `tools/gen_sensor.py` (libraries, projects, schematics, boards), ERC and DRC
(all severities, schematic parity), then writes `fab/power_jumper/`. Reports go to `build/`.

## Open

- CN2 mate: part, footprint, contact count and contact map (from the GPIO add-on's plug or
  Apollo). Then set `CN2_CONFIRMED`, regenerate, check the fan-out.
- Flex fab notes for PCBWay: folds, stiffener thickness and side, rolled-annealed copper for
  the folds, MK1's port hole through flex and stiffener, the gasket ring.
- Jumper: the FH12 contact end (`JUMPER_END`, `FPC_PAD`) against Hirose's FPC drawing, and the
  contact side, before ordering; the jumper passes through the mains volume (SAFETY item 4).
- MK1 pin 1 orientation against a part (footprint mirrored from the datasheet's bottom view).
- Microphone firmware test on an MSR-2 (sample rate, load).
