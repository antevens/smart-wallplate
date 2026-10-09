"""SENSOR FLEX (D-27): single-layer flex in the trim from the MSR-2's CN2 to the SHT45.

Route: plug end under the MSR-2 (CN2 at the board's right end), out through the bay frame,
up the top-right corner to just under the face skin, down the right channel, then along the
bottom to the SHT45 bay, the SHT45 soldered on the flex tail. In the channel two Harwin
S7081-42R spring fingers (+5 V, GND) on the flex underside press on the gold pads of the 5 V
jumper's pad end (D-31), which lies on a shelf off the insert flange.
Above the finger section the flex widens towards the flange for the I2S microphone (D-29), on the
flex underside, its port facing the face skin.
Open (D-27): CN2's exact part, contact count and pin map (MEASURE).
"""
from math import atan2, degrees, hypot
from build123d import Box, Cylinder, Pos, Rot
from params import *

Z_LO = STIFF_T + FLEX_T / 2                      # flex centre at the MSR-2 end
Z_HI = FLEX_HI_Z + FLEX_T / 2                    # flex centre in the channel
Z_SHT = SKIN_Z - 0.5 - SHT_CHIP[2] - FLEX_T / 2  # SHT45 on the flex top, 0.5 mm under the face vents

ROUTE = [(MSR_CN2_X, MSR_Y, Z_LO), (FLEX_X, MSR_Y, Z_LO),
         (FLEX_X, MSR_Y - FLEX_RISE_DY, Z_HI), (FLEX_X, SHT_Y, Z_HI),
         (SHT_ENTRY, SHT_Y, Z_HI), (0.0, SHT_Y, Z_SHT)]


def segment(a, b):
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
    out = plug_end()
    for a, b in zip(ROUTE, ROUTE[1:]):
        out += segment(a, b)
    return out


def plug_end():
    """Plug end and neck taper of the flex at the wall plane (outline from params.flex_half_width)."""
    from build123d import Polyline, extrude, make_face
    xs = [-FLEX_PLUG[0] / 2, FLEX_PLUG[0] / 2, FLEX_PLUG[0] / 2 + FLEX_NECK_L]
    top = [(MSR_CN2_X + x, MSR_Y + flex_half_width(x)) for x in xs]
    bot = [(MSR_CN2_X + x, MSR_Y - flex_half_width(x)) for x in reversed(xs)]
    face = make_face(Polyline(*top, *bot, top[0]))
    return Pos(0, 0, Z_LO - FLEX_T / 2) * extrude(face, FLEX_T)


def stiffeners():
    """FR4 stiffeners: under the CN2 plug (wall side) and over the spring fingers (skin side)."""
    plug = Pos(MSR_CN2_X, MSR_Y, STIFF_T / 2) * Box(B2B[0] + 2.0, FLEX_W, STIFF_T)
    x0, x1, (y0, y1) = FINGER_SEC_IN, FINGER_SEC_OUT, FINGER_SEC_Y
    fingers = Pos((x0 + x1) / 2, (y0 + y1) / 2, FLEX_HI_Z + FLEX_T + STIFF_T / 2) * Box(x1 - x0, y1 - y0, STIFF_T)
    return plug + fingers + mic_stiffener()


def mic_section():
    """Flex widened towards the flange over the microphone (D-29)."""
    (y0, y1), x1 = MIC_SEC_Y, FLEX_X + FLEX_W / 2
    return Pos((MIC_SEC_IN + x1) / 2, (y0 + y1) / 2, FLEX_HI_Z + FLEX_T / 2) * Box(x1 - MIC_SEC_IN, y1 - y0, FLEX_T)


def mic_stiffener():
    """FR4 stiffener over the microphone (skin side), port hole through flex and stiffener."""
    w, h = MIC[0] + 1.0, MIC[1] + 1.0
    z = FLEX_HI_Z + FLEX_T + STIFF_T / 2
    s = Pos(MIC_X, MIC_Y, z) * Box(w, h, STIFF_T)
    return s - Pos(*MIC_PORT, z) * Cylinder(MIC_FLEX_HOLE_D / 2, STIFF_T + 0.1)


def mic():
    """Microphone body under the flex and the adhesive gasket ring between stiffener and skin."""
    body = Pos(MIC_X, MIC_Y, FLEX_HI_Z - MIC[2] / 2) * Box(*MIC)
    z0 = FLEX_HI_Z + FLEX_T + STIFF_T
    ring = Pos(*MIC_PORT, (z0 + SKIN_Z) / 2) * (Cylinder(MIC_GASKET_D / 2, SKIN_Z - z0)
                                                - Cylinder(MIC_SKIN_HOLE_D / 2, SKIN_Z - z0 + 0.1))
    return body + ring


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
    """The 5 V jumper's pad end on the shelf (flex on its stiffener): gold pads under the fingers."""
    x0, x1 = FLANGE_OUT[0] / 2 + 0.15, shelf_edge() - 0.15
    return Pos((x0 + x1) / 2, sum(TARGET_Y) / 2, SHELF_TOP_Z + TARGET_T / 2) * Box(x1 - x0, TARGET_Y[1] - TARGET_Y[0], TARGET_T)


def shelf_edge():
    """Shelf outer edge: the flat underside, then a 45 deg chamfer up to the shelf top."""
    return FLANGE_OUT[0] / 2 + SHELF_OUT + (SHELF_TOP_Z - SHELF_UNDER_Z)


def shelf():
    """Insert shelf off the flange's right face carrying the jumper's pad end. Underside: flat at
    SHELF_UNDER_Z for SHELF_OUT (the flange is solid to its outer face there; <= 3 mm prints
    unsupported), then 45 deg up to the shelf top."""
    from build123d import Polyline, Plane, extrude, make_face
    x0 = FLANGE_OUT[0] / 2 - 1.0                 # 1 mm into the flange
    xf = FLANGE_OUT[0] / 2 + SHELF_OUT
    pts = [(x0, SHELF_UNDER_Z), (xf, SHELF_UNDER_Z), (shelf_edge(), SHELF_TOP_Z), (x0, SHELF_TOP_Z),
           (x0, SHELF_UNDER_Z)]
    depth = TARGET_Y[1] - TARGET_Y[0] + 1.0 + SHELF_STOP[0]
    body = Pos(0, TARGET_Y[1] + 0.5, 0) * extrude(Plane.XZ * make_face(Polyline(*pts)), depth)   # along -y
    # stop at the lower end: the pad end cannot slide down the wall (lower than the pad end's top: fingers clear)
    y0 = TARGET_Y[0] - 0.5 - SHELF_STOP[0]
    xs = shelf_edge() - 0.3
    body += Pos((x0 + xs) / 2, y0 + SHELF_STOP[0] / 2, SHELF_TOP_Z + SHELF_STOP[1] / 2 - 0.01) * Box(
        xs - x0, SHELF_STOP[0], SHELF_STOP[1] + 0.02)
    return body


def plug():
    """CN2 mating plug envelope (MEASURE: footprint and contact count to be confirmed)."""
    z0 = STIFF_T + FLEX_T
    return Pos(MSR_CN2_X, MSR_Y, z0 + B2B_STACK / 2) * Box(B2B[0], B2B[1], B2B_STACK)


def sht45():
    return Pos(0.0, SHT_Y, Z_SHT + FLEX_T / 2 + SHT_CHIP[2] / 2) * Box(*SHT_CHIP)


def parts():
    port = Pos(*MIC_PORT, FLEX_HI_Z + FLEX_T / 2) * Cylinder(MIC_FLEX_HOLE_D / 2, FLEX_T + 0.1)
    return {"flex": flex() + finger_section() + mic_section() + stiffeners() - port, "fingers": fingers(),
            "target": target(), "plug": plug(), "sht45": sht45(), "mic": mic()}
