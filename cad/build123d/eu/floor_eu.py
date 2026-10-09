"""EU pocket-floor insert (D-35, D-41): printed floor in the remote pocket, on the cap, bonded to the trim
(face plate side, lifts off with it). Openings over the switch cup and round the trim's screw
tabs; the sensor-flex tongue comes in under the right pocket wall between the spring pins, folds
45 deg beside the floor pads (copper up) and carries the two gold pads, flush, under the
replacement back cover's spring fingers (+5V, GND). Geometry in backcover.py.
"""
from build123d import Pos
from params_eu import *
import backcover


def cutouts():
    tabs = [(sx * (POCKET_IN[0] / 2 - TRIM_TAB[0] / 2), TRIM_SCREW_Y, TRIM_TAB[0], TRIM_TAB[1]) for sx in (-1, 1)]
    return [(0.0, SW_Y, CUP_IN[0], CUP_IN[1])] + tabs


def pads():
    """(x0, x1, y0, y1) of the floor pads: +5V, GND."""
    return [(*EU_PAD_X, y - BC_FLOOR_PAD[1] / 2, y + BC_FLOOR_PAD[1] / 2) for _, y in BC_FINGERS]


def tongue_path():
    """The tongue on the floor (x0, x1, y0, y1, layers): run from the wall (copper down), fold square, the
    strip up past the +5V pad and the part beside the fold carrying the GND pad (copper up)."""
    wall_x = POCKET_IN[0] / 2 + POCKET_WALL
    h = EU_TONGUE_W / 2
    f0, f1 = EU_FOLD_X - h, EU_FOLD_X + h
    y_top = max(y for _, y in BC_FINGERS) + BC_FLOOR_PAD[1] / 2 + 0.5
    y_bot = min(y for _, y in BC_FINGERS) - BC_FLOOR_PAD[1] / 2 - 1.0
    run = (f1, wall_x, EU_TONGUE_Y - h, EU_TONGUE_Y + h, 1)
    fold = (f0, f1, EU_TONGUE_Y - h, EU_TONGUE_Y + h, 2)
    up = (EU_STRIP_X0, f1, EU_TONGUE_Y + h, y_top, 1)
    side = (EU_STRIP_X0, f0 - 0.3, y_bot, EU_TONGUE_Y + h, 1)
    return [run, fold, up, side]


def parts():
    p = backcover.floor_insert(POCKET_IN, POCKET_IN[0] / 2 + POCKET_WALL, cutouts(), tongue_path(), pads())
    return {k: Pos(0, 0, CAP_T) * v for k, v in p.items()}
