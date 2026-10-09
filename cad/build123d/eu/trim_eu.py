"""EU TRIM PLATE (D-30): face, remote pocket walls (standing on the cap), finger notch (left), MSR-2 bay
(radar skin) above, SHT45 bay below, microphone sound hole; the sensor flex runs in its right channel. Two M2 screws through tabs at the foot of the pocket walls
hold it to the cap. Low-voltage side only; any filament (PETG/ASA). Print face-down, no supports.
Run:  python trim_eu.py  -> ../../../build/eu/trim.step / .stl
"""
from build123d import Axis, Box, Circle, Cone, Cylinder, Plane, Pos, Rectangle, chamfer, extrude
from params_eu import *
from common import rr, stadium, slab, frame


def tabs():
    out = None
    for sx in (-1, 1):
        x = sx * (POCKET_IN[0] / 2 - TRIM_TAB[0] / 2 + 0.01)
        t = Pos(x, TRIM_SCREW_Y, CAP_T + TRIM_TAB[2] / 2) * Box(TRIM_TAB[0] + 0.02, TRIM_TAB[1], TRIM_TAB[2])
        out = t if out is None else out + t
    return out


def tab_holes():
    out = None
    sink = (TRIM_HEAD_D - TRIM_SCREW_D) / 2
    for sx in (-1, 1):
        x = sx * TRIM_SCREW_X
        h = Pos(x, TRIM_SCREW_Y, CAP_T + TRIM_TAB[2] / 2) * Cylinder(TRIM_SCREW_D / 2 + 0.1, TRIM_TAB[2] + 1)
        h += Pos(x, TRIM_SCREW_Y, CAP_T + TRIM_TAB[2] - sink / 2 + 0.01) * Cone(TRIM_SCREW_D / 2 + 0.1, TRIM_HEAD_D / 2, sink)
        out = h if out is None else out + h
    return out


def sensor_eu_pin_y():
    import sensor_eu
    return sensor_eu.PIN_Y


def notch(sx):
    """Finger notch beside the pocket: rectangle at the face, 45 deg sides down to NOTCH depth."""
    face = Plane.XY.offset(PT + 0.01) * Rectangle(NOTCH[0] + 2 * NOTCH[2], NOTCH[1] + 2 * NOTCH[2])
    cut = extrude(face, -(NOTCH[2] + 0.01), taper=45)
    return Pos(sx * NOTCH_X, 0, 0) * cut


def notch_block(sx):
    """Solid trim around a notch, from below the notch up to the face."""
    w, h = NOTCH[0] + 2 * NOTCH[2] + 2 * NOTCH_BLOCK, NOTCH[1] + 2 * NOTCH[2] + 2 * NOTCH_BLOCK
    return Pos(sx * NOTCH_X, 0, 0) * slab(Rectangle(w, h), PT - NOTCH[2] - NOTCH_BLOCK, PT)


def build():
    pc = Pos(PC[0], PC[1], 0)
    shell = pc * slab(rr(PW, PH, PR), 0, PT)
    shell = chamfer(shell.edges().group_by(Axis.Z)[-1], FACE_CHAMFER)
    shell -= pc * slab(rr(PW - 2 * SKIN, PH - 2 * SKIN, PR - SKIN), -1, DECK_Z)
    body = shell
    body += slab(stadium(*POCKET_OUT), CAP_T, PT)                                   # pocket walls
    body += notch_block(-1)                                                          # left only: the right channel carries the flex
    body += Pos(0, MSR_Y, 0) * frame(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1.6, 1, 0, PT)
    body += Pos(0, SHT_Y, 0) * frame(SHT[0] + 0.8, SHT[1] + 0.8, 1.6, 0.5, 0, PT)
    # ---------------- cuts ----------------
    body -= slab(stadium(*POCKET_IN), CAP_T, PT + 1)                               # remote pocket
    body += tabs()
    body -= tab_holes()
    body -= notch(-1)                                                                # finger notch
    body -= slab(Circle(CAP_R + SPLIT_CLR), -1, CAP_T)                              # cap clearance
    body -= Pos(0, MSR_Y, 0) * slab(rr(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1), -0.01, PT - RADAR_WALL)
    body -= Pos(LUX_POS[0], MSR_Y + LUX_POS[1], PT - 0.5) * Cylinder(1.5, 6)
    for i in range(-2, 3):                                                           # MSR-2 vents, top edge
        body -= Pos(i * 7 + 1.5, PL_Y[1] - SKIN + 2, 6) * Box(3, 6, 6)
    body -= Pos(0, SHT_Y, 0) * slab(rr(SHT[0] + 0.8, SHT[1] + 0.8, 0.5), -0.01, PT - SKIN)
    # sensor flex through the bay frames' right walls; microphone sound hole
    nx = MSR[0] / 2 + CLR + 0.8
    w = 2 * flex_half_width(nx - 2.0 - MSR_CN2_X) + 0.6
    body -= Pos(nx, MSR_Y, FLEX_LO_Z + FLEX_T / 2) * Box(4.0, w, 1.0)
    sz0 = SKIN_Z - 0.5 - SHT_CHIP[2] - FLEX_T - 0.3
    body -= Pos(SHT[0] / 2 + 0.4 + 0.8, SHT_Y, (sz0 + SKIN_Z) / 2) * Box(3.0, FLEX_W + 0.6, SKIN_Z - sz0 + 0.01)
    body -= Pos(*MIC_PORT, PT - SKIN / 2) * Cylinder(MIC_SKIN_HOLE_D / 2, SKIN + 1)
    # notch under the right pocket wall for the sensor-flex tongue to the pocket-floor insert (D-35)
    body -= Pos((POCKET_IN[0] + POCKET_OUT[0]) / 4, EU_TONGUE_Y, CAP_T + (BC_FLOOR_T + 0.2) / 2 - 0.01) * \
        Box((POCKET_OUT[0] - POCKET_IN[0]) / 2 + 0.2, EU_TONGUE_W + 0.6, BC_FLOOR_T + 0.2)
    # pocket wall's foot thinned where the flex's pad section passes beside it
    (sx0, _), (sy0, sy1) = FLEX_PAD_SEC, sensor_eu_pin_y()
    zt = FLEX_PIN_Z + FLEX_T + STIFF_T + 0.3
    body -= Pos(POCKET_OUT[0] / 2 - WALL_RECESS / 2 + 0.01, (sy0 + sy1) / 2, (CAP_T + zt) / 2) * Box(
        WALL_RECESS + 0.02, sy1 - sy0 + 1.0, zt - CAP_T + 0.01)
    # rib from the face skin down onto the flex stiffener over the spring pins (takes their force)
    import sensor_eu
    (x0, x1), (y0, y1) = sensor_eu.RIB
    zb = FLEX_PIN_Z + FLEX_T + STIFF_T
    body += Pos((x0 + x1) / 2, (y0 + y1) / 2, (zb + SKIN_Z + 0.5) / 2) * Box(x1 - x0, y1 - y0, SKIN_Z + 0.5 - zb)
    for i in (-1, 0, 1):                                                             # SHT45 vents: face + bottom edge
        body -= Pos(i * 4, SHT_Y, PT - 1) * Box(2, 6, 4)
        body -= Pos(i * 4, PL_Y[0] + 4, 5) * Box(2, 10, 6)
    from common import board_hooks                                                   # MSR-2 snap hooks (D-45)
    hooks, reliefs = board_hooks(MSR_Y, MSR_BOARD[0], MSR_BACK_Z, PT - RADAR_WALL, MSR[0] / 2 + CLR, MSR_HOOK)
    return body - reliefs + hooks


if __name__ == "__main__":
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[3] / "build" / "eu"
    out.mkdir(parents=True, exist_ok=True)
    p = build()
    bb = p.bounding_box()
    print(f"trim bbox x {bb.min.X:.1f}..{bb.max.X:.1f} y {bb.min.Y:.1f}..{bb.max.Y:.1f} z {bb.min.Z:.1f}..{bb.max.Z:.1f}"
          f"  vol {p.volume/1000:.1f} cm3 valid={p.is_valid} solids={len(p.solids())}")
    export_step(p, str(out / "trim.step"))
    export_stl(p, str(out / "trim.stl"), tolerance=0.02, angular_tolerance=0.1)
