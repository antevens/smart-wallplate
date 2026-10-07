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
| V0_RATED_T | Elegoo PC-FR UL94 V-0 test thickness | filament TDS (cite) | | TODO |
| — | 1802.2504 latch positions / spring-out below the panel | calipers | | TODO |
| — | wall finish to box face offset | ruler | | TODO |
