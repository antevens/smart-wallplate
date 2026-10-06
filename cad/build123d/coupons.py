"""Fast test-fit coupons (print in PETG before committing PC-FR / a full trim).

  coupon_pocket_well  top of the insert: switch well + panel, upper pocket end, key pin,
                      5 V pass-through, top screw boss. Rocker snap-in + remote fit.
  coupon_msr          top of the trim: MSR-2 bay, radar skin, light-sensor hole, vents.
  coupon_rocker       panel-thickness ladder for the C1300 snap-in (SW_PANEL_T is MEASURE):
                      one notch per step on the frame edge = 1.0, 1.5, 2.0, 2.5, 3.0 mm.
"""
from build123d import Box, Pos, Rectangle
from params import *
from common import slab, rr
import insert
import trim

PANEL_STEPS = (1.0, 1.5, 2.0, 2.5, 3.0)


def pocket_well(ins=None):
    ins = ins or insert.build()
    y0 = PSU_Y1 - 6.0                       # just below the latch cavity / end stop
    keep = Pos(0, (y0 + 60) / 2, (PANEL_BOT_Z + PT + 5) / 2) * Box(100, 60 - y0, PT + 5 - PANEL_BOT_Z)
    return ins & keep


def msr(tr=None):
    tr = tr or trim.build()
    y0 = MSR_Y - MSR[1] / 2 - CLR - 1.6 - 2.0
    return tr & (Pos(0, (y0 + PH) / 2, PT / 2) * Box(PW + 2, PH - y0, PT + 2))


def rocker_ladder():
    cell = (SW_CUT[0] + 10, SW_CUT[1] + 10)
    wall_h = 6.0
    parts = None
    for i, t in enumerate(PANEL_STEPS):
        y = (i - (len(PANEL_STEPS) - 1) / 2) * (cell[1] - 2)
        c = Pos(0, y, 0) * slab(rr(*cell, 2), 0, wall_h)
        c -= Pos(0, y, 0) * slab(rr(cell[0] - 4, cell[1] - 4, 1), t, wall_h + 1)       # pocket above the panel
        c -= Pos(0, y, 0) * slab(Rectangle(*SW_CUT), -1, wall_h + 1)                    # datasheet cutout
        for k in range(i + 1):                                                          # step marker notches
            c -= Pos(cell[0] / 2 - 0.5, y - cell[1] / 2 + 3 + 2.2 * k, wall_h) * Box(2.5, 1.2, 3)
        parts = c if parts is None else parts + c
    return parts


if __name__ == "__main__":
    for name, p in (("pocket_well", pocket_well()), ("msr", msr()), ("rocker", rocker_ladder())):
        bb = p.bounding_box()
        print(f"coupon_{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, {p.volume/1000:.1f} cm3, valid={p.is_valid}, solids={len(p.solids())}")
