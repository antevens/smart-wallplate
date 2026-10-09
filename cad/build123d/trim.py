"""TRIM PLATE - face, MSR-2 bay (radar skin), SHT45 bay, vents, microphone sound hole.

Low-voltage side only: it carries no barrier duty. Any filament (PETG/ASA).
Print: face down (the exported print STL is already flipped), no supports.
Run:  python trim.py  -> ../../build/trim.step / .stl
"""
from build123d import Box, Cylinder, Cone, Rectangle, Pos, Axis, chamfer
from params import *
from common import rr, slab, frame
import insert


def msr_hooks():
    """Snap hooks holding the MSR-2 board in its bay (D-45): at the board's short ends, from the radar skin."""
    from common import board_hooks
    return board_hooks(MSR_Y, MSR_BOARD[0], MSR_BACK_Z, PT - RADAR_WALL, MSR[0] / 2 + CLR, MSR_HOOK)


def build():
    shell = slab(rr(PW, PH, PR), 0, PT)
    shell = chamfer(shell.edges().group_by(Axis.Z)[-1], FACE_CHAMFER)
    shell -= slab(rr(PW - 2 * SKIN, PH - 2 * SKIN, PR - SKIN), -1, PT - SKIN)
    body = shell
    # MSR-2 and SHT45 bay frames
    body += frame(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1.6, 1, 0, PT, MSR_Y)
    body += frame(SHT[0] + 0.8, SHT[1] + 0.8, 1.6, 0.5, 0, PT, SHT_Y)
    hooks, reliefs = msr_hooks()

    # ---------------- cuts ----------------
    # clearance envelope of the insert: island window through the face, flange underneath
    body -= slab(rr(ISLAND[0] + 2 * SPLIT_CLR, ISLAND[1] + 2 * SPLIT_CLR, ISLAND_R + SPLIT_CLR), DECK_Z - 1, PT + 1)
    fl = slab(rr(FLANGE_OUT[0] + 2 * SPLIT_CLR, FLANGE_OUT[1] + 2 * SPLIT_CLR, ISLAND_R + FLANGE + SPLIT_CLR), -1, DECK_Z)
    for s in (-1, 1):
        fl += Pos(0, s * SCREW_PITCH / 2, DECK_Z / 2) * Cylinder(BOSS_R + SPLIT_CLR, DECK_Z + 2)
    body -= fl
    for kx, ky in KEY_POS:  # sockets for the insert's locating pins
        body -= Pos(kx, ky, DECK_Z + (KEY_H + 0.2) / 2 - 0.01) * Cylinder(KEY_D / 2 + KEY_CLR, KEY_H + 0.2)
    for s in (-1, 1):  # countersunk #6 holes, clamp trim + insert to the box ears
        y = s * SCREW_PITCH / 2
        body -= Pos(0, y, PT / 2) * Cylinder(SCREW_D / 2, PT + 2)
        body -= Pos(0, y, PT - 1.9) * Cone(SCREW_D / 2, SCREW_HEAD_D / 2, 3.81)
    body -= Pos(0, MSR_Y, 0) * slab(rr(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1), -0.01, PT - RADAR_WALL)
    body -= Pos(LUX_POS[0], MSR_Y + LUX_POS[1], PT - 0.5) * Cylinder(1.5, 6)
    for i in range(-2, 3):  # MSR vents, top edge
        body -= Pos(i * 7 + 1.5, PH / 2 - SKIN + 2, 6) * Box(3, 6, 6)
    body -= Pos(0, SHT_Y, 0) * slab(rr(SHT[0] + 0.8, SHT[1] + 0.8, 0.5), -0.01, PT - SKIN)
    # sensor flex (D-27) passes the bay frames: MSR-2 frame (right wall, at the wall plane) and the
    # SHT45 frame (right wall, just under the skin)
    nx = MSR[0] / 2 + CLR + 1.0                    # notch centre (room x), 4 mm long
    w = 2 * flex_half_width(nx - 2.0 - MSR_CN2_X) + 0.6
    body -= Pos(nx, MSR_Y, 0.45) * Box(4.0, w, 0.92)
    w = FLEX_W + 0.6
    body -= Pos(SHT[0] / 2 + 0.4 + 0.8, SHT_Y, (SKIN_Z + 9.4) / 2) * Box(3.0, w, SKIN_Z - 9.4 + 0.01)
    # side wall thinned on the inside over the flex's finger section (track lanes beside the pads)
    ry0, ry1 = FINGER_LANE_Y[0] - 0.5, FINGER_LANE_Y[1] + 0.5
    rz0 = FLEX_HI_Z - 0.5
    body -= Pos(PW / 2 - SKIN + TRIM_WALL_RECESS / 2, (ry0 + ry1) / 2, (rz0 + SKIN_Z) / 2) * Box(
        TRIM_WALL_RECESS, ry1 - ry0, SKIN_Z - rz0 + 0.01)
    body -= Pos(*MIC_PORT, PT - SKIN / 2) * Cylinder(MIC_SKIN_HOLE_D / 2, SKIN + 1)   # microphone sound hole (D-29)
    body = body - reliefs + hooks                       # MSR-2 snap hooks (D-45)
    for i in (-1, 0, 1):  # SHT vents: face + bottom edge
        body -= Pos(i * 4, SHT_Y, PT - 1) * Box(2, 6, 4)
        body -= Pos(i * 4, -PH / 2 + 4, 5) * Box(2, 10, 6)
    return body


if __name__ == "__main__":
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[2] / "build"
    out.mkdir(exist_ok=True)
    p = build()
    bb = p.bounding_box()
    print(f"trim bbox x {bb.min.X:.1f}..{bb.max.X:.1f} y {bb.min.Y:.1f}..{bb.max.Y:.1f} z {bb.min.Z:.1f}..{bb.max.Z:.1f}"
          f"  vol {p.volume/1000:.1f} cm3 valid={p.is_valid} solids={len(p.solids())}")
    export_step(p, str(out / "trim.step"))
    export_stl(p, str(out / "trim.stl"), tolerance=0.02, angular_tolerance=0.1)
