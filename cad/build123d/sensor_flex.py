"""SENSOR FLEX (D-27): single-layer flex in the trim from the MSR-2's CN2 to the SHT45.

Route: plug end under the MSR-2 (CN2 at the board's right end), out through the bay frame,
up the top-right corner to just under the face skin, down the right channel, then along the
bottom to the SHT45 bay, the SHT45 soldered on the flex tail. In the channel two Harwin
S7081-42R spring fingers (+5 V, GND) on the flex underside press on a target board that sits on
a shelf off the insert flange; the 5 V lead from the pass-through is soldered to that board.
Open (D-27): CN2's exact part, contact count and pin map (MEASURE).
"""
from math import atan2, degrees, hypot
from build123d import Box, Pos, Rot
from params import *

Z_LO = STIFF_T + FLEX_T / 2                      # flex centre at the MSR-2 end
Z_HI = FLEX_HI_Z + FLEX_T / 2                    # flex centre in the channel
Z_SHT = SKIN_Z - 0.5 - SHT_CHIP[2] - FLEX_T / 2  # SHT45 on the flex top, 0.5 mm under the face vents

ROUTE = [(MSR_CN2_X, MSR_Y, Z_LO), (FLEX_X, MSR_Y, Z_LO),
         (FLEX_X, MSR_Y - FLEX_RISE_DY, Z_HI), (FLEX_X, SHT_Y, Z_HI),
         (SHT_ENTRY, SHT_Y, Z_HI), (0.0, SHT_Y, Z_SHT)]


def _segment(a, b):
    """Flat strip FLEX_W x FLEX_T from a to b (straight run in x or in the y-z plane)."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    c = Pos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
    if abs(dy) < 1e-9 and abs(dz) < 1e-9:
        return c * Box(abs(dx) + 0.01, FLEX_W, FLEX_T)
    if abs(dx) < 1e-9:
        tilt = degrees(atan2(dz, dy))
        return c * Rot(tilt, 0, 0) * Box(FLEX_W, hypot(dy, dz) + 0.01, FLEX_T)
    tilt = degrees(atan2(dz, dx))                 # x run with a drop in z
    return c * Rot(0, -tilt, 0) * Box(hypot(dx, dz) + 0.01, FLEX_W, FLEX_T)


def flex():
    out = None
    for a, b in zip(ROUTE, ROUTE[1:]):
        s = _segment(a, b)
        out = s if out is None else out + s
    return out


def stiffeners():
    """FR4 stiffeners: under the CN2 plug (wall side) and over the spring fingers (skin side)."""
    plug = Pos(MSR_CN2_X, MSR_Y, STIFF_T / 2) * Box(B2B[0] + 2.0, FLEX_W, STIFF_T)
    x0, x1, (y0, y1) = FINGER_SEC_IN, FINGER_SEC_OUT, FINGER_SEC_Y
    fingers = Pos((x0 + x1) / 2, (y0 + y1) / 2, FLEX_HI_Z + FLEX_T + STIFF_T / 2) * Box(x1 - x0, y1 - y0, STIFF_T)
    return plug + fingers


def finger_section():
    """Flex widened over the finger section: towards the flange over the pads, into the trim wall
    recess (longer) for the tracks that pass them."""
    z = FLEX_HI_Z + FLEX_T / 2
    xi0, xi1, (yi0, yi1) = FINGER_SEC_IN, FLEX_X + FLEX_W / 2, FINGER_SEC_Y
    xo0, xo1, (yo0, yo1) = FLEX_X - FLEX_W / 2, FINGER_SEC_OUT, FINGER_LANE_Y
    pads = Pos((xi0 + xi1) / 2, (yi0 + yi1) / 2, z) * Box(xi1 - xi0, yi1 - yi0, FLEX_T)
    lanes = Pos((xo0 + xo1) / 2, (yo0 + yo1) / 2, z) * Box(xo1 - xo0, yo1 - yo0, FLEX_T)
    return pads + lanes


def fingers():
    """Spring fingers at their working height (envelope: body footprint x working height)."""
    out = None
    for y in FINGER_Y:
        f = Pos(FINGER_X, y, FLEX_HI_Z - FINGER_WH / 2) * Box(FINGER[0], FINGER[1], FINGER_WH)
        out = f if out is None else out + f
    return out


def target():
    """Target board on the shelf: gold pads under the fingers, solder pads for the 5 V lead at the top."""
    x0, x1 = FLANGE_OUT[0] / 2 + 0.15, shelf_edge() - 0.15
    return Pos((x0 + x1) / 2, sum(TARGET_Y) / 2, SHELF_TOP_Z + TARGET_T / 2) * Box(x1 - x0, TARGET_Y[1] - TARGET_Y[0], TARGET_T)


def shelf_edge():
    """Shelf outer edge: the flat underside, then a 45 deg chamfer up to the shelf top."""
    return FLANGE_OUT[0] / 2 + SHELF_OUT + (SHELF_TOP_Z - SHELF_UNDER_Z)


def shelf():
    """Insert shelf off the flange's right face carrying the target board. Underside: flat at
    SHELF_UNDER_Z for SHELF_OUT (the flange is solid to its outer face there; <= 3 mm prints
    unsupported), then 45 deg up to the shelf top."""
    from build123d import Polyline, Plane, extrude, make_face
    x0 = FLANGE_OUT[0] / 2 - 1.0                 # 1 mm into the flange
    xf = FLANGE_OUT[0] / 2 + SHELF_OUT
    pts = [(x0, SHELF_UNDER_Z), (xf, SHELF_UNDER_Z), (shelf_edge(), SHELF_TOP_Z), (x0, SHELF_TOP_Z),
           (x0, SHELF_UNDER_Z)]
    depth = TARGET_Y[1] - TARGET_Y[0] + 1.0
    body = extrude(Plane.XZ * make_face(Polyline(*pts)), depth)   # profile x / z, extruded along -y
    return Pos(0, TARGET_Y[1] + 0.5, 0) * body


def plug():
    """CN2 mating plug envelope (MEASURE: footprint and contact count to be confirmed)."""
    z0 = STIFF_T + FLEX_T
    return Pos(MSR_CN2_X, MSR_Y, z0 + B2B_STACK / 2) * Box(B2B[0], B2B[1], B2B_STACK)


def sht45():
    return Pos(0.0, SHT_Y, Z_SHT + FLEX_T / 2 + SHT_CHIP[2] / 2) * Box(*SHT_CHIP)


def parts():
    return {"flex": flex() + finger_section() + stiffeners(), "fingers": fingers(), "target": target(),
            "plug": plug(), "sht45": sht45()}
