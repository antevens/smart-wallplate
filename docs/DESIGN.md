# Design: requirements and decision log

## Context
- House in Nanaimo, BC, Canada. NA single-gang device boxes, 2" × 3" opening (≈50.8 × 76.2 mm), Decora/Leviton switches today.
- Every light socket has an IKEA Matter (Thread) smart bulb. Home Assistant on an Nvidia Orin NX.
- Owner has electronics experience, is buying a 3D printer, will do the work under a BC homeowner electrical permit.

## Requirements
| ID | Requirement |
|----|-------------|
| R1 | Replace each light switch with a plate that holds an IKEA BILRESA scroll-wheel remote, flush/recessed. |
| R2 | mmWave presence sensing in every switch location. |
| R3 | Temperature + humidity in every location. |
| R4 | Emergency means to (a) turn lights on when Home Assistant is down and (b) de-power the circuit. Need not be easily accessible. |
| R5 | Emergency off must also de-power the presence sensor. |
| R6 | Keep the face plate as thin as practical. |
| R7 | Same electronics usable in EU/UK (250 VAC-rated parts). |
| R8 | Printable on a hobby FDM printer (Elegoo Centauri Carbon 2 Combo, ElegooSlicer); PCB fab + THT assembly by PCBWay. |

## Decision log
| ID | Decision | Why / rejected alternatives |
|----|----------|-----------------------------|
| D-1 | No existing product does R1+R2+R4 → custom plate. | Inovelli Blue mmWave dimmer (Zigbee, smart-bulb mode) considered; has no humidity, no Bilresa mount. |
| D-2 | Don't design own mains switching electronics or put Li-ion cells in the box. | Certification (CEC approved-equipment requirement), heat, fire risk. |
| D-3 | Presence: Apollo MSR-2 (ESPHome, Wi-Fi) rather than Matter sensor. | Aqara FP300 too big (42×42×50) and battery-tuned; IKEA has no mmWave (MYGGSPRAY is PIR); Everything Presence Lite too big, no climate. HA is the controller, so ESPHome native API is fine/better. MSR-2 is 40×24×15 cased. |
| D-4 | Climate: SHT45 on MSR-2 I²C, thermally isolated bay at plate bottom. | MSR-2's DPS310 reads high from ESP32 heat (Apollo says so); IKEA TIMMERFLOTTE (70×70×30) too big. |
| D-5 | Keep BILRESA intact (batteries in), recessed in box, removable. | De-cased board option explored (I-beam PCB, encoder + tactile) but intact is simpler, stays usable as handheld. |
| D-6 | Emergency control = mechanical rocker in series with the load, hidden behind the remote. | Shelly relay dropped: all bulbs are smart, a relay adds nothing. Spring-carrier "push the remote" idea dropped once the switch could be hidden. |
| D-7 | PSU fed from the load side of the rocker. | R5. |
| D-8 | Bulbs' Matter power-on behaviour set to On. | Off→on of the rocker then turns lights on without HA (R4a). Must be verified per bulb. |
| D-9 | Rocker: Bulgin/Arcolectric C1300AABBEN602A (16 A 250 VAC, CSA/UL, 27.3×12.3 cutout). | R7. E-Switch RB141C1100 is 125 V only. Würth 471005264152 has ENEC/UL but no Canadian mark listed. ENEC on the Bulgin part still to be confirmed from datasheet. |
| D-10 | PSU: Mean Well IRM-03-5 (85–305 VAC, 5 V 600 mA, 37×24×15, cURus/CB/TÜV) on a carrier PCB with fuse + MOV. | Encapsulated, reputable, universal input (R7). Headroom for MSR-2 CO₂ variant. |
| D-11 | Low-voltage electronics in the plate, mains parts in the box; plate stands ~13 mm proud. | 50 mm box width can't hold remote + sensor side by side; puts sensors in room air; clean barrier. |
| D-12 | **v0.2 (done):** split into V-0 "box insert" (all barrier geometry) + "trim plate". | Face-down single-piece print needs supports in the pocket; limits flame-rated material to the part that needs it. |
| D-13 | Fix the v0.1 scoop leak: the region between the pocket shell and the collar is now **solid insert material**, and the scoops sit wholly inside the insert. | In v0.1 that region was hollow under a 2 mm face skin; the finger scoops (bottom at z = 8.5) cut through the skin, opening the mains side to the room. Found by the new barrier test in `checks.py`. |
| D-14 | Insert printed floor-down with no supports: thick floor down to the bed, 45° taper carrying the flange underside, flange underside chamfered outside a 1.25 mm flat seal band on the wall, PSU rails integral with a **gabled (45°) roof** over the PCB back instead of a flat bridge. | Every downward face is either on the bed, ≤ 45°, or a ≤ 2.3 mm ledge (checked). A separate screwed PSU cradle was considered; no room for screws that don't block the PCB or breach the floor. |
| D-15 | PSU carrier 42 × 44 mm (was 40 × 36), slides in from the bottom end of the rails, stops at a top end stop; the box wall keeps it in. | 37 mm IRM-03 + 2 mm rail keep-outs need ≥ 41 mm; J1/F1/RV1 and the isolation slot need the extra height. Top edge stays 4 mm under the rocker body. |
| D-16 | Trim–insert interface: the insert's island is flush with the face; the trim's face clamps the insert flange; both are held by the two #6-32 box screws; two asymmetric Ø3 pins key the orientation. | One screw set, no extra fasteners in the barrier, can't be assembled rotated. |
| D-17 | 5 V lead pass-through: vertical leg out of the box (room-right, J2 side) then 45° out through the flange into the trim hollow. | Only barrier opening; lead never crosses the box rim below the wall plane. |
| D-18 | Insert material: **Elegoo PC-FR** (retailer listing: UL 94 V-0; test thickness still to be confirmed from the datasheet → `V0_RATED_T`). Stock "Elegoo PC-FR @ECC2" slicer profile, 6 walls. | Printable on the CC2 (280 °C), has a vendor profile. A filament's V-0 rating is for moulded bars; a printed part is not certified by it. |
| D-19 | F1 = T1A 250 V TR5 (Littelfuse 39211000000). **Designer's choice, needs human review.** | Mean Well's IRM-03 spec and PCB installation manual give no external fuse rating; inrush 20 A typ at 230 VAC (datasheet). |
| D-20 | PCB: all THT, one side, PCBWay turnkey. Isolation targets enforced as KiCad 9 netclass + custom DRC rules (clearance and `creepage`). | See `pcb/SPEC.md`. Targets, not a compliance claim. |
| D-21 | BILRESA modelled as 45 × 70 mm with an R8.5 back round-over; pocket clearance `CLR` 0.6 → 0.5 mm. | IKEA UK lists the product at 45 × 70 × 20 mm; a third-party wall mount's pocket measures 45.4 × 70.4 with a quarter-circle back of R≈8.5. At 45 mm, `CLR` 0.6 put the pocket shell 0.1 mm outside the insert's box-clearance outline. Reference values until measured. |

## Known risks / to verify
- Metal boxes: ears may collide with the pocket; BILRESA Thread signal may drop when recessed.
- Neutral may be missing in switch-loop boxes → PSU can't be fed there.
- BILRESA scroll wheel reportedly laggy/flaky over Matter in HA; test before scaling.
- Concealed emergency switch vs. code expectation of a wall switch: ask inspector.
- Plate is 82 × 150 mm (larger than standard); may shrink once the bare MSR-2 is measured.
- v0.2 insert fills more of the box than v0.1 (solid floor to z = −22.4 over the pocket footprint, 45° corner taper to −10 mm): include it in the box-fill calculation. The taper reaches into the box's opening corners; check against your box ears / device-screw bosses.
- The rocker body closes the panel cutout and is part of the barrier: never energise with the rocker removed.
- J1 mains pigtails leave the PCB towards the rocker body with ~5 mm to turn back into the box: use flexible stranded wire.
- Elegoo PC-FR V-0 rating thickness unknown until the datasheet is on file.
