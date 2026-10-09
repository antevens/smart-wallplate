# EU mains board and 5 V board (D-30, D-36)

Two boards in the round EU flush box (DIN 49073, Ø60 inside), both hanging from bosses under the
V-0 cap. Generated from `tools/eu_parts.py`, which takes its geometry from
`cad/build123d/eu/params_eu.py`.

## Mains board (`kicad/eu_mains_board.*`)

Round, at the rocker's PCB seat (16.2 mm below its panel face). The rocker breaks line and neutral
of the lights; the PSU is fed from the switched side, so the rocker also turns the sensor off.

| Ref | Part | Side | Nets |
| --- | --- | --- | --- |
| S1 | Marquardt 1802.2504 rocker, DPST, PCB pins, ENEC 12(4) A 250 V~, UL/CSA 15 A | front (through the cap's panel) | 1 L_IN, 1a L_SW, 2 N_IN, 2a N_SW |
| J1 | WAGO 2604-3102, push-in, 2-pole, 4 mm², entry 90° to the board, 400 V III/2; turned 180° from J2 | back | L_SW (pole 1), L_IN (pole 2, upper) |
| J2 | WAGO 2604-3102 (as J1) | back | N_IN (house neutral), N_SW (to the lights) |
| F1 | Schurter UMT 250, T1A 250 VAC | front | L_SW to L_F |
| RV1 | TDK CU4032K275G2, 275 VAC | front | L_F to N_SW |
| PS1 | Traco TMPS 03-105, 5 V 600 mA (IEC/UL 62368-1, IEC 60335-1; OVC II, PD2, reinforced) | back | inputs L_F / N_SW above the slot, outputs +5V / GND below it |
| J3 | Samtec TSM-102-01-L-SV, SMT pin header 1x2, 2.54 mm, 5.84 mm post (no pin tails under the PSU) | front, 5 V island | +5V, GND |
| MH1-MH3 | M2 holes on the cap's long bosses | - | - |

- The lights' current runs in copper pours: L_IN and L_SW on F.Cu (right), N_IN and N_SW on B.Cu
  (left), in above switched, as the rocker's poles; the split between them steps from the rocker's
  poles down to the WAGO block's. WAGO pin rows and body from WAGO's 3D model (8.2 mm apart, levers
  towards the board centre, where the blocks' pins stay 1.0 mm clear of the rocker body on the
  front); blocks at x ±16.6, y 7.5. The PSU feed (L_F, N_SW to F1 / RV1 / PS1) is
  1.0 mm track. Order with 2 oz copper for the load paths (sizing: human review).
- A routed relief slot under the PSU, between its input and output rows, cuts off the 5 V island
  (PSU outputs, J3). Mains copper keeps ≥ 8 mm (clearance and creepage) from it.
- Keep-out areas round the mounting holes: mains copper ≥ 1.0 mm from them.
- No PE on the board: the lights' protective earth is joined in the box (lever connector).
- Installer labels on the back: L IN / L LOAD, N IN / N LOAD at the WAGO blocks, MAINS 230 VAC.

## 5 V board (`kicad/eu_5v_board.*`)

D-shaped, just under the cap, cut below the switch cup; a hole lets the mains board's lower long
boss through. No mains on it.

| Ref | Part | Side | Nets |
| --- | --- | --- | --- |
| J1 | 2.54 mm pin socket 1x2 (8.5 mm), on the mains board's J3 | back | +5V, GND |
| C1 | 22 µF 10 V X5R 1206 | front | +5V to GND |
| P1, P2 | Harwin P70-2200045 SMT spring pins, 2 A | front | GND (P1, upper), +5V (P2) (through the cap onto the flex's pads; order set by the flex's tongue, D-42) |
| MH1, MH2 | M2 holes on the cap's bosses | - | - |

The header posts reach 3.2 mm into the socket (boards 13.8 mm apart; check with the parts).
Nothing is soldered or wired between the boards or across the cap (DESIGN R9, R10).

## Rules

`kicad/eu_mains_board.kicad_dru`: L–N ≥ 3.5 mm, any two different mains nets ≥ 3.5 mm (line / switched
line / fused line, neutral / switched neutral), mains to the 5 V side ≥ 8.0 mm (clearance and
creepage), mains to the PSU's NC pin ≥ 8.0 mm, mains copper ≥ 1.0 mm from the board edge and the
holes; pins of one rated part keep the part's own spacing. The mains pours carry their own 3.5 mm
clearance. Design targets for human review, not a compliance claim.

The net classes come from the project file; `tools/gen_eu.py` rewrites it after every save
(pcbnew's SaveBoard resets it). The single EU PSU board before D-36 was checked without them, so
its isolation was never verified by DRC.

## Regenerate

```bash
make pcb        # or pcb/eu/tools/build.sh
```

PCBWay packs for both boards in `fab/` (`fab/README.md`: order settings and the review checklist).
Order only after the review and a dry fit of the stack in a real box.
