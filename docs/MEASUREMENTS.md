# Measurements to take (fill in, then update cad/build123d/params.py)

Use calipers; record to 0.1 mm. Measure 2 samples where possible. `status`: TODO / DONE /
REF (published or third-party reference value in use until measured).

| param | what | how | value | status |
|-------|------|-----|-------|--------|
| B_W | BILRESA width (widest) | across the short axis | 45.0 (reference: IKEA UK product size; third-party mount pocket 45.4) | REF |
| B_H | BILRESA height | long axis | 70.0 (reference: IKEA UK product size; third-party mount pocket 70.4) | REF |
| B_D | BILRESA depth | back cover to top of wheel | | TODO |
| — | BILRESA face profile | photo + depth of wheel ring vs body | | TODO |
| B_BACK_RUN, B_BACK_RISE | BILRESA back round-over (inset and height of the curve) | radius gauge or profile photo | 8.5 / 8.5 (reference: third-party mount pocket, quarter circle R≈8.5) | REF |
| — | BILRESA supply | IKEA manual AA-2675003-2 (2025), technical data | 2 × AAA HR03 (NiMH, 2 × 1.2 V nominal); recommended LADDA HR03 rechargeable; types E2490, E2704; 0–40 °C | DONE (manual) |
| — | BILRESA battery contacts: positions in the compartment, spring travel, polarity | open the back cover; calipers from the remote centre. FCC ID FHO-E2490 internal photos (TÜV Rheinland, pictures 1, 3, 4): 2 cells side by side along the long axis, the PCB strip between them; SERIES, confirmed: at the radio-module end one metal strap (silk P3) joins both contacts; at the system-button (S1) end two separate terminals, silk "GND"/P2 and P1 (P1 = VBAT: the E2489 board, same layout, labels these positions VBAT and GND/P2). Which slot is + / − at the terminal end: from the compartment markings on a unit. Approx. from picture 1 scaled to its ruler (perspective, ±1 mm): contacts centred on the remote, 45 mm apart along the long axis (≈ AAA length), 23 mm apart across | ±22.6 along, ±11.7 across (approx.) | REF |
| — | BILRESA battery contact types at each end | FCC ID FHO-E2490 internal photo 1 (cover open): diagonal pairs, at each end one leaf spring (bent out of its slot, − side) and one fixed plate with a dimple set in a pocket in the end wall (+ side); at the terminal end GND meets the leaf spring, VBAT the fixed plate (series chain). Measure on a unit: the plate's setback behind the end wall face (`BC_TERM_SETBACK`, behind the cell end plane), the pocket opening round the plate (the S7081 dome, Ø1.3, must reach it), the leaf spring's rest position and travel, which end is the terminal end | 0.0 (placeholder) | TODO |
| JUMPER_T | 2-layer flex jumper thickness (D-41) | PCBWay stack-up for the ordered flex | 0.2 (design value) | TODO |
| — | BILRESA dual button (E2489) battery contacts | FCC ID FHO-E2489 internal photos (TÜV Rheinland, pictures 1-4): same layout as the E2490, 2 cells side by side along the long axis with the PCB strip between; SERIES: metal strap along the radio module joins the two contacts at that end, terminals at the other end silk "VBAT" and "GND"/P2. Approx. from picture 1 scaled to its ruler (perspective, ±1 mm): centred on the remote, 44.8 mm apart along the long axis, 20.1 mm across. Outline and depth: measure | ±22.4 along, ±10.0 across (approx.) | REF |
| — | BILRESA supply as the remote sees it | zigbee2mqtt E2490 page: reports battery voltage in mV and a percentage that "seems to be tuned for Alkalines (1.5V)"; Qorvo chipset; sleeps between presses. Read the voltage in HA with the 3.3 V supply | | TODO |
| BC_* | BILRESA back cover: outline, wall, latch hooks (position, depth), steel plate size and position, cell axis height above the back | calipers on the original cover and the open remote | | TODO |
| — | Magnet hold vs. the back cover's two spring fingers | pull the remote (with the printed cover) off the plate with a force gauge; fingers need >= 2 x 1.2 N at 2.1 mm (S7081-42R) | | TODO |
| — | BILRESA current: sleep and transmit peak | supply at 2.4 V through a current meter / shunt + scope | | TODO |
| WAGO_ROW (NA) | WAGO 2604 solder-pin rows and body, 2604-11xx (0° entry) | WAGO STEP models 2604-1102 / 2604-1106 (CADENAS download 2026-10-08, kept in scratch/) | pole pitch 5.0; 2 pins per pole in rows 8.2 apart (pins 0.8 × 1.0, 4.0 long); first row 5.0 behind the entry face, second row 2.9 inside the closed back (body 16.1 deep at the board, 16.7 high); levers overhang the entry side at the top to 8.1 beyond the first row | DONE (vendor model) |
| WAGO_ROW (EU) | WAGO 2604-3102 (90° entry) pin rows and body | WAGO STEP model 2604-3102 (CADENAS download 2026-10-08, kept in scratch/) | poles 5.0 apart; 2 pins per pole in rows 8.2 apart (pins 0.8 × 1.0, 4.0 long); body 16.7 along the rows, 3.6 before the first row, 4.9 past the second (lever side, levers up to 21.3); 12.4 across the poles, 0.1 off their centre | 8.2 (rows' centre 0.65 from the body centre) | DONE (vendor model) |
| MAGNET | supplied adhesive magnet w × h × t (with its tape); flexible or rigid? | calipers; bend test | | TODO |
| MAGNET_Y | centre of the steel plate inside the remote, from the remote centre | slide a magnet over the back, mark the strongest spot | | TODO |
| MAGNET_END_R | corner radius of the supplied magnet's ends (the recess bottom follows it; the magnet is cut straight at the top) | radius gauge or trace on paper | | TODO |
| SW_PANEL_T | Marquardt 1802.2504 snap-in panel range | drawing 1802.2504 rev g: 0.75–3 mm, cutout length steps 19.2/19.4/19.8; 1.5 mm chosen; confirm on `coupon_rocker` | 1.5 | TODO |
| SW_BEZEL | 1802.2504 flange w × h | drawing 1802.2504 rev g | 21 × 24 (mounted 24 × 21) | DONE (datasheet) |
| SW_ROCKER_H | rocker top above the panel face | drawing 1802.2504 rev g | 5.3 ± 0.5 | DONE (datasheet) |
| SW_BODY | body w × h; PCB seat below the panel face | drawing 1802.2504 rev g | 18.6 × 22; 16.2 | DONE (datasheet) |
| MSR | bare MSR-2 board w × h × max height | out of case, incl. USB-C and header | | TODO |
| — | MSR-2 powered from the mezzanine header 5V/GND | bench test | yes (human, 2026-10-07) | DONE |
| — | MSR-2 rear connector CN2: maker + MPN, and the mating plug's MPN (the GPIO add-on's CN4) | read the add-on's plug marking, or ask Apollo | 0.4 mm pitch, 2 rows (photo measurement, D-27) | TODO |
| — | CN2 contact count and contact-to-signal map (5V, 3V3, GND, SDA = IO1, SCL = IO0) | count + meter from the add-on's header to its plug | ~26-30 (photo) | TODO |
| MSR_CN2_IN, B2B, B2B_STACK | CN2 centre from the board end, housing size, mated stack height | calipers | 6.4; 7.6 × 3.0; 1.5 (photo estimates) | REF |
| MSR_BOARD | bare MSR-2 board w × h | calipers | 38.0 × 21.5 (Apollo case cavity 38.08 × 21.67, Printables 932026) | REF |
| MSR | MSR-2 envelope; its back plane sets the 1.8 mm under CN2 | calipers | | TODO |
| — | MSR-2 current draw at 5 V (sizes the sensor board's input protection) | USB meter, radar on | | TODO |
| LUX_POS | LTR-390 offset from board centre | calipers | | TODO |
| — | MSR-2 radar antenna position on board | photo | | TODO |
| SHT | chosen SHT45 breakout w × h × t | calipers | | TODO |
| BOX_D | box depth, per room | ruler to back wall | | TODO |
| — | box material per room (metal/plastic) | look | | TODO |
| — | neutral present per box (Y/N) | look/test with breaker off | | TODO |
| — | box ear positions / intrusion into opening | calipers; the insert fills the opening corners to ~10 mm deep (45° taper) and the bottom end to 0.75 mm of the wall | | TODO |
| V0_RATED_T | UL94 V-0 test thickness of the insert filament | filament TDS (cite) | Elegoo PC-FR data sheet states no UL94 class; deferred until a certified spool is chosen (2026-10-08) | TODO |
| — | 1802.2504 latch positions / spring-out below the panel | calipers | | TODO |
| — | wall finish to box face offset | ruler | | TODO |

## Estimates from photos and drawings (2026-10-08)

Human request: assume values from the available pictures, diagrams and drawings until a unit is
measured. Tagged `ESTIMATE` in `params.py`; replace each with a caliper reading before printing
anything final. Sources: FCC FHO-E2490 / FHO-E2489 photos (scratch/, steel rulers, perspective
fits), the IKEA label drawings for E2490 / E2489 (drawn 1:1, outline checks at 70.1 × 45.1), and
the IKEA UK product page (height 20 mm).

| Name | Estimate | ± | Source / method | Used |
| --- | --- | --- | --- | --- |
| B_D | 20.0 | 0.5 | IKEA UK product page | REF in params |
| B_SEAM_Z | 12.5 | 1.5 | FCC external photos 1 / 2: back shell (battery cover) ~12.5, front housing ~7 | yes |
| B_FRONT_R | 0.8 | 0.5 | FCC external photo 1 | yes |
| B_BACK_RUN / B_BACK_RISE | 9.1 / 9.0 | 0.4 / 3 | label drawing: flat back 51.8 × 26.7; rise not visible | yes |
| B_WHEEL_D / B_WHEEL_Y / B_WHEEL_GAP | 41.5 / +12.5 / 0.3 | 1.0 / 1.0 / 0.2 | FCC photos; wheel concentric with the end arc, at the radio-module (strap) end | yes |
| B_LED_Y / B_LED_PITCH | −12.0 / 3.9 | 1.0 / 0.3 | FCC photos; LEDs at the terminal (P1 / P2) end | yes |
| BC_STEEL (x × y × t) | 12.0 × 20.0 × 2.0 | measured | human, 2026-10-09: the plate in the cover is a magnet, not steel | DONE |
| MAGNET_Y (remote's plate centre) | 0.0 | 1.0 | FCC internal photo 1: centred in its cover | yes |
| BC_CELL_X | 11.2 | 0.5 | label drawing bays ±10.95; PCB contacts ±11.4 | yes |
| BC_CELL_Z | 6.8 | 0.8 | inferred: cover wall + clearance + cell radius | yes |
| BC_PCB_W | 11.6 (divider) | 0.3 | label drawing: divider 11.1 / 11.6 over its outer edges; the PCB strip is 11.1 | yes (divider) |
| BC_TERM_Y / BC_VBAT_X | −1 / −1 | — | FCC PCB photo: at the terminal end VBAT (P1) is the fixed dimple plate at −x, GND (P2) the leaf spring at +x | confirmed |
| Fixed plate pocket | ~5.6 across × 3.5 along | 0.7 | FCC internal photo 1; depth (BC_TERM_SETBACK) not visible | the S7081 dome (Ø1.3) fits |
| Leaf spring protrusion | ~2–3.5 from the end wall | low | FCC internal photo 1; travel not visible | — |
| MAGNET (supplied) | ~47.4 × 17.5, full round ends (R8.75), t 1.5–2.5 | 1.0 | label drawing back-view rings, FCC external photo 2 | yes: cut to an 18.5 mm piece (D-43) |
| B_SEAM_Z, BC_WALL | cover depth rim to back 9.8, shell 1.6 | measured | human, 2026-10-09 | DONE |
| BC_PRY | screwdriver notch in the rim at the bottom end | — | human, 2026-10-09: present; size MEASURE (6.0 × 1.2) | TODO |
| BC_SIDE_TAB, BC_SIDE_TAB_GAP | side ribs at mid-length, free-standing on the shell's curved floor (stiffening, no hook) | 36.1 inside spacing, top 3.8 above the inside floor (measured); length 6.0 × 1.5 thick (ESTIMATE, photos) | human, 2026-10-09 | DONE |
| — | supplied wall part: magnet or steel? The remote's plate is a magnet, so a second magnet must face it with opposite poles (mark the cut piece's orientation) | magnet / compass | | TODO |
| BC_LATCH_* (cover snap clips, top and bottom) | one clip per end at x 0, ~3.5 wide × 1.2, inner face ~31.4 from the centre (the bottom one at the pry notch); tops 4.7 (bottom) / 6.5 (top) above the inside floor (measured); hook size MEASURE (0.5) | 0.5 | human photos IMG_5088-5090, measurements 2026-10-09 | partly |
| E2489 outline / depth | 69.5 × 40.0 / ~20 | 0.3 / 2 | label drawing; photo comparison | backlog (E2489 version) |
| E2489 cell axes | ±9.6 across, ends ±22 | 0.4 | label drawing | backlog |

Not determinable from the pictures: BC_TERM_SETBACK, BC_BRIDGE_H, BC_STEEL thickness, the leaf
spring's travel, the magnet thickness. They stay MEASURE.

The supplied magnet appears to be about 47 × 17.5 mm (the drawing's ring, from a shape fit). Whole,
it would run into the switch well (NA) and the switch cup (EU) under the remote's upper half. The
user cuts it once across (human decision 2026-10-08): an 18.5 mm piece measured from one round end
(`MAGNET`), round end down into the recess's round end, straight cut edge up. Check the real size
before cutting; the piece length follows from `MAGNET_REC_Y` and the switch well.

