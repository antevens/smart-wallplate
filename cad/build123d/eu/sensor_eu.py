"""EU SENSOR FLEX AND POWER CONTACT (D-30, topology of D-27 / D-29).

Flex: plug end under the MSR-2 on its rear connector CN2, out through the bay frame's right wall,
fold into the right channel of the trim, rise to just under the face skin, past the microphone
(port to a sound hole in the skin), dip to just above the cap where two spring pins on the PSU
board press on gold pads on its underside, rise again, fold at the bottom and across to the SHT45
under its vents. The 45 deg folds turn the strip over, as on the NA flex, so the pads face the cap.
No wires: the pins reach up from the 5 V board through two holes in the cap (R9); a rib from the
trim's face skin backs the flex over them.
"""
from build123d import Box, Cylinder, Polyline, Pos, extrude, make_face
from params_eu import *
from sensor_flex import segment

Z_LO = FLEX_LO_Z + FLEX_T / 2
Z_HI = FLEX_HI_Z + FLEX_T / 2
Z_PIN = FLEX_PIN_Z + FLEX_T / 2
Z_SHT = SKIN_Z - 0.5 - SHT_CHIP[2] - FLEX_T / 2
PIN_Y = (min(y for _, y in PINS) - FLEX_PAD_D / 2 - 1.0, max(y for _, y in PINS) + FLEX_PAD_D / 2 + 1.0)
DIP_IN = (PIN_Y[1] + FLEX_DIP, PIN_Y[1])                  # drop: high -> pin level (along -y)
DIP_OUT = (PIN_Y[0], PIN_Y[0] - FLEX_DIP)                 # rise: pin level -> high

ROUTE = [(MSR_CN2_X, MSR_Y, Z_LO), (FLEX_X, MSR_Y, Z_LO),
         (FLEX_X, MSR_Y - FLEX_RISE_DY, Z_HI), (FLEX_X, DIP_IN[0], Z_HI), (FLEX_X, DIP_IN[1], Z_PIN),
         (FLEX_X, DIP_OUT[0], Z_PIN), (FLEX_X, DIP_OUT[1], Z_HI), (FLEX_X, SHT_Y, Z_HI),
         (SHT_ENTRY, SHT_Y, Z_HI), (0.0, SHT_Y, Z_SHT)]
RIB = ((FLEX_PAD_SEC[0] + 0.3, FLEX_PAD_SEC[1] - 0.3), (PIN_Y[0] + 0.3, PIN_Y[1] - 0.3))   # backing rib (x, y)


def plug_end():
    xs = [-FLEX_PLUG[0] / 2, FLEX_PLUG[0] / 2, FLEX_PLUG[0] / 2 + FLEX_NECK_L]
    top = [(MSR_CN2_X + x, MSR_Y + flex_half_width(x)) for x in xs]
    bot = [(MSR_CN2_X + x, MSR_Y - flex_half_width(x)) for x in reversed(xs)]
    return Pos(0, 0, FLEX_LO_Z) * extrude(make_face(Polyline(*top, *bot, top[0])), FLEX_T)


def mic_section():
    """Flex widened towards the skin over the microphone."""
    w, h = EU_MIC_SEC[0] + FLEX_W / 2, EU_MIC_SEC[1]
    return Pos(FLEX_X + (EU_MIC_SEC[0] - FLEX_W / 2) / 2, MIC_Y, Z_HI) * Box(w, h, FLEX_T)


def flex():
    out = plug_end()
    for a, b in zip(ROUTE, ROUTE[1:]):
        out += segment(a, b)
    out += mic_section()
    port = Pos(*MIC_PORT, Z_HI) * Cylinder(MIC_FLEX_HOLE_D / 2, FLEX_T + 0.1)
    return out - port


def stiffeners():
    plug = Pos(MSR_CN2_X, MSR_Y, FLEX_LO_Z - STIFF_T / 2) * Box(B2B[0] + 2.0, FLEX_PLUG[1], STIFF_T)
    (x0, x1), (y0, y1) = FLEX_PAD_SEC, PIN_Y
    pins = Pos((x0 + x1) / 2, (y0 + y1) / 2, FLEX_PIN_Z + FLEX_T + STIFF_T / 2) * Box(x1 - x0, y1 - y0, STIFF_T)
    z = FLEX_HI_Z + FLEX_T + STIFF_T / 2
    mic = Pos(MIC_X, MIC_Y, z) * Box(MIC[0] + 1.0, MIC[1] + 1.0, STIFF_T)
    mic -= Pos(*MIC_PORT, z) * Cylinder(MIC_FLEX_HOLE_D / 2, STIFF_T + 0.1)
    return plug + pins + mic


def plug():
    """CN2 mating plug on the flex, under the MSR-2 (MEASURE: part unconfirmed)."""
    return Pos(MSR_CN2_X, MSR_Y, FLEX_LO_Z + FLEX_T + B2B_STACK / 2) * Box(B2B[0], B2B[1], B2B_STACK)


def mic():
    body = Pos(MIC_X, MIC_Y, FLEX_HI_Z - MIC[2] / 2) * Box(*MIC)
    z0 = FLEX_HI_Z + FLEX_T + STIFF_T
    ring = Pos(*MIC_PORT, (z0 + SKIN_Z) / 2) * (Cylinder(MIC_GASKET_D / 2, SKIN_Z - z0)
                                                - Cylinder(MIC_SKIN_HOLE_D / 2, SKIN_Z - z0 + 0.1))
    return body + ring


def sht45():
    return Pos(0.0, SHT_Y, Z_SHT + FLEX_T / 2 + SHT_CHIP[2] / 2) * Box(*SHT_CHIP)


def pad_section():
    """Flex widened over the spring pins."""
    (x0, x1), (y0, y1) = FLEX_PAD_SEC, PIN_Y
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, Z_PIN) * Box(x1 - x0, y1 - y0, FLEX_T)


def tongue():
    """Battery-free tongue (D-41): from the pad section's inner edge, between the pins, under the pocket wall
    to the floor insert's recess (the floor part is floor_eu's)."""
    wall_x = POCKET_IN[0] / 2 + POCKET_WALL
    z_floor = CAP_T + BC_FLOOR_T - FLEX_T / 2 - BC_RECESS_CLR
    a, b = (FLEX_PAD_SEC[0] + 0.3, EU_TONGUE_Y, Z_PIN), (wall_x, EU_TONGUE_Y, z_floor)
    dx, dz = b[0] - a[0], b[2] - a[2]
    from math import atan2, degrees, hypot
    from build123d import Rot
    return Pos((a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2) * Rot(0, -degrees(atan2(dz, dx)), 0) * \
        Box(hypot(dx, dz) + 0.01, EU_TONGUE_W, FLEX_T)


def flex_pads():
    """Gold pads on the flex underside, under the pin tips (GND, +5 V)."""
    out = None
    for x, y in PINS:
        c = Pos(x, y, FLEX_PIN_Z - 0.015) * Cylinder(FLEX_PAD_D / 2, 0.03)
        out = c if out is None else out + c
    return out


def parts():
    return {"flex": flex() + pad_section() + stiffeners() + tongue(), "plug": plug(), "mic": mic(), "sht45": sht45(),
            "pads": flex_pads()}
