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
| STEEL | steel target w × h × t | from wall mount | | TODO |
| SW_PANEL_T | C1300 snap-in panel range | datasheet (cite page), then confirm on `coupon_rocker` (notches = 1.0/1.5/2.0/2.5/3.0 mm) | | TODO |
| SW_BEZEL | C1300 bezel w × h | calipers | | TODO |
| SW_ROCKER_H | bezel + rocker height above panel, rocker in ON position | calipers | | TODO |
| SW_BODY | body w × h × depth incl. QC tabs + connectors | calipers, with QCs fitted | | TODO |
| MSR | bare MSR-2 board w × h × max height | out of case, incl. USB-C and header | | TODO |
| LUX_POS | LTR-390 offset from board centre | calipers | | TODO |
| — | MSR-2 radar antenna position on board | photo | | TODO |
| SHT | chosen SHT45 breakout w × h × t | calipers | | TODO |
| BOX_D | box depth, per room | ruler to back wall | | TODO |
| — | box material per room (metal/plastic) | look | | TODO |
| — | neutral present per box (Y/N) | look/test with breaker off | | TODO |
| — | box ear positions / intrusion into opening | calipers; v0.2 insert fills the opening corners to ~10 mm deep (45° taper) and the bottom end to 0.75 mm of the wall | | TODO |
| V0_RATED_T | Elegoo PC-FR UL94 V-0 test thickness | filament TDS (cite) | | TODO |
| SW_LATCH | C1300 latch positions / spring-out below the panel (sets SW_LATCH_CLR, 1.5 mm now) | calipers | | TODO |
| — | wall finish to box face offset | ruler | | TODO |
