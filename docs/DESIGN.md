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
| R8 | Printable on a hobby FDM printer; PCB fab via JLCPCB/PCBWay class services. |

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
| D-12 | **Planned v0.2:** split into V-0 "box insert" (all barrier geometry) + "trim plate". | Face-down single-piece print needs supports in the pocket; limits flame-rated material to the part that needs it. |

## Known risks / to verify
- Metal boxes: ears may collide with the pocket; BILRESA Thread signal may drop when recessed.
- Neutral may be missing in switch-loop boxes → PSU can't be fed there.
- BILRESA scroll wheel reportedly laggy/flaky over Matter in HA; test before scaling.
- Concealed emergency switch vs. code expectation of a wall switch: ask inspector.
- Plate is 82 × 150 mm (larger than standard) in v0.1; may shrink once the bare MSR-2 is measured.
