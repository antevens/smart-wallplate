"""TRIM PLATE - face, MSR-2 bay (radar skin), SHT45 bay, vents.

Low-voltage side only: it carries no barrier duty. Any filament (PETG/ASA).
Print: face down (the exported print STL is already flipped), no supports.
Run:  python trim.py  -> ../../build/trim.step / .stl
"""
from build123d import Box, Cylinder, Cone, Rectangle, Pos, Axis, chamfer
from params import *
from common import rr, slab, frame
import insert


def build():
    shell = slab(rr(PW, PH, PR), 0, PT)
    shell = chamfer(shell.edges().group_by(Axis.Z)[-1], FACE_CHAMFER)
    shell -= slab(rr(PW - 2 * SKIN, PH - 2 * SKIN, PR - SKIN), -1, PT - SKIN)
    body = shell
    # MSR-2 and SHT45 bay frames
    body += frame(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1.6, 1, 0, PT, MSR_Y)
    body += frame(SHT[0] + 0.8, SHT[1] + 0.8, 1.6, 0.5, 0, PT, SHT_Y)

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
    w = FLEX_W + 0.6
    body -= Pos(MSR[0] / 2 + CLR + 1.0, MSR_Y, 0.45) * Box(4.0, w, 0.92)
    body -= Pos(SHT[0] / 2 + 0.4 + 0.8, SHT_Y, (SKIN_Z + 9.4) / 2) * Box(3.0, w, SKIN_Z - 9.4 + 0.01)
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
