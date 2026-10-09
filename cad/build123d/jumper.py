"""5 V FLEX JUMPER (D-31, R9, R10): wiring board J2 -> pass-through -> pad end on the insert shelf.

A single-layer flex carries 5 V, so nothing is wired or soldered at assembly. The
connector end (stiffened) latches into J2, a Hirose FH12-6S slide-lock FPC connector on the board's
front face. The run goes up the gap between board and insert at x = JUMPER_X with a Z-folded
service loop (JUMPER_SERVICE of spare length, so it can be plugged in with the board held beside the
insert), up the pass-through's vertical leg, along the bottom of its 45 deg leg (exits the flange
face at shelf height) and onto the shelf, where its pad end (flex on an FR4 stiffener) carries the gold pads the face plate's spring fingers press on.
"""
from build123d import Box, Plane, Pos, Vector
from params import *


def ribbon(pts, w=JUMPER_W, t=JUMPER_T):
    """Flat strip along a polyline: thin boxes along each segment, the width kept horizontal."""
    out = None
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(*a), Vector(*b)
        d = b - a
        up = Vector(0, 0, 1) if abs(d.normalized().Z) < 0.9 else Vector(1, 0, 0)
        x_dir = d.cross(up).normalized()
        s = Plane(origin=(a + b) * 0.5, x_dir=x_dir, z_dir=d) * Box(w, t, d.length + 0.01)
        out = s if out is None else out + s
    return out


def entry():
    """Where the jumper leaves J2 (the connector is turned so the flex enters from +y)."""
    return jumper_path()[0]


def path():
    return jumper_path()


def end():
    """Stiffened connector end, in J2."""
    x, y, z = entry()
    return Pos(x, y - JUMPER_END[1] / 2, z) * Box(JUMPER_END[0], JUMPER_END[1], JUMPER_END[2])


def length():
    return jumper_length()


def tongue_route():
    """Battery-free tongue (D-41) centre line, copper up: from inside the pad end along the flange tunnel,
    down the pocket-wall groove, out of it onto the wall, down to the floor insert's recess."""
    x_pe = FLANGE_OUT[0] / 2 + 0.15                                 # pad end's inner edge
    out_x, in_x = tongue_walls()
    xg = out_x + BC_NA_GROOVE_D - JUMPER_T / 2 - 0.05               # in the groove, against its back
    xw = in_x - JUMPER_T / 2 - 0.05                                 # at the wall's innermost point below the groove
    zt = TARGET_TOP_Z - JUMPER_T / 2
    zf = SEAT_Z + BC_FLOOR_T - JUMPER_T / 2 - BC_RECESS_CLR         # in the floor insert's recess
    y = BC_NA_TONGUE_Y
    return [(x_pe + 0.5, y, zt), (xg, y, zt), (xg, y, BC_NA_GROOVE_BOT + 1.2), (xw, y, BC_NA_GROOVE_BOT),
            (xw, y, zf)]


def tongue():
    """The tongue from the pad end to the pocket floor (the floor part is floor_na's)."""
    return ribbon(tongue_route(), BC_NA_NECK_W, JUMPER_T)


def build(battery_free=False):
    out = {"jumper": ribbon(path()) + end()}
    if battery_free:
        out["jumper"] += tongue()
    return out
