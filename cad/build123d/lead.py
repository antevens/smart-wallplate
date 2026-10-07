"""5 V LEAD (D-17, D-27): twin lead from the wiring board's J2 to the target board.

Route: out of J2 on the board's front face, across the gap between board and insert at x =
LEAD_X (between the rocker body and the right-hand posts), up through the pass-through (vertical
leg, then the 45 deg leg kept low so it exits the flange face under the trim skin), down beside
the flange under the flex, and split into its two wires onto the target board's lead pads.
"""
from math import sqrt
from build123d import Pos, Sphere
from params import *
from common import rod
import sensor_flex


def centreline():
    o = LEAD_HOLE_OFFSET / sqrt(2)                       # offset towards the outer, lower side of the hole
    face = FLANGE_OUT[0] / 2
    t = face - PASS_X - o                                # along the 45 deg leg to the flange face
    zk = -1.0                                            # bend of the pass-through (insert.pass_through)
    tp = sensor_flex.target().bounding_box()
    return [(J2_POS[0], WB_Y + J2_POS[1] + 5.6, WB_FRONT_Z + 2.5),   # out of the J2 plug
            (LEAD_X, WB_Y + J2_POS[1] + 9.0, (WB_FRONT_Z + Z_BOT) / 2),
            (LEAD_X, PASS_Y - 4.0, (WB_FRONT_Z + Z_BOT) / 2),
            (PASS_X, PASS_Y, Z_BOT - 1.7),                           # into the vertical leg
            (PASS_X, PASS_Y, zk),
            (PASS_X + t + o, PASS_Y, zk + t - o),                    # leaves the flange face
            (face + 0.85, PASS_Y - 1.0, tp.max.Z + 1.0),             # down beside the flange, under the flex
            (face + 1.9, tp.max.Y - 0.5, tp.max.Z + LEAD_D / 2 + 0.05)]


def wire_ends():
    """(start, end) of the +5 V and GND wires from the end of the jacket to the lead pads."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pcb" / "sensor" / "tools"))
    import sensor_parts as sp
    end = centreline()[-1]
    z = sp.TB_T + SHELF_TOP_Z + LEAD_WIRE_D / 2
    return [(end, (sp.TARGET_PARTS[r]["pos"][0], sp.TARGET_PARTS[r]["pos"][1], z)) for r in ("TP3", "TP4")]


def build():
    pts = centreline()
    jacket = None
    for a, b in zip(pts, pts[1:]):
        r = rod(a, b, LEAD_D)
        jacket = r if jacket is None else jacket + r
    for p in pts[1:-1]:
        jacket += Pos(*p) * Sphere(LEAD_D / 2)
    (a5, b5), (ag, bg) = wire_ends()
    return {"lead": jacket, "wire_5v": rod(a5, b5, LEAD_WIRE_D), "wire_gnd": rod(ag, bg, LEAD_WIRE_D)}
