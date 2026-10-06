"""Parametric wall plate (build123d). Port of reference/openscad/wallplate.scad v0.1.

Run:  python wallplate.py            -> ../../build/wallplate.step / .stl
      python wallplate.py --check    -> prints sanity checks only
"""
import sys
from pathlib import Path
from build123d import (Box, Cylinder, Cone, Sphere, Rectangle, RectangleRounded,
                       SlotCenterToCenter, extrude, chamfer, Pos, Rot, Axis,
                       export_step, export_stl)
from params import *

OUT = Path(__file__).resolve().parents[2] / "build"


def stadium(w, h):
    """BILRESA-like rounded-end oval as a sketch (long axis = Y)."""
    return Rot(0, 0, 90) * SlotCenterToCenter(h - w, w)


def slab(sketch, z0, z1):
    """Extrude a 2D sketch between two absolute z levels."""
    return Pos(0, 0, z0) * extrude(sketch, z1 - z0)


def frame(w, h, wall, r, z0, z1, y=0.0):
    outer = RectangleRounded(w + 2 * wall, h + 2 * wall, r + wall)
    inner = RectangleRounded(w, h, max(r, 0.3))
    return Pos(0, y, 0) * (slab(outer, z0, z1) - slab(inner, z0 - 1, z1 + 1))


def build():
    # hollow shell, open to the wall
    shell = slab(RectangleRounded(PW, PH, PR), 0, PT)
    shell = chamfer(shell.edges().group_by(Axis.Z)[-1], FACE_CHAMFER)
    shell -= slab(RectangleRounded(PW - 2 * SKIN, PH - 2 * SKIN, PR - SKIN), -1, PT - SKIN)

    body = shell
    # collar around the box opening (mains / low-voltage separation)
    body += frame(BOX_W + 2, BOX_H + 2, 1.6, 0.3, 0, PT)
    # screw bosses
    for s in (-1, 1):
        body += Pos(0, s * SCREW_PITCH / 2, PT / 2) * Cylinder(5.5, PT)
    # pocket shell + switch well shell
    body += slab(stadium(*POCKET_OUT), FLOOR_Z, PT)
    well_out = (SW_BEZEL[0] + 2 * CLR + 2 * POCKET_WALL, SW_BEZEL[1] + 2 * CLR + 2 * POCKET_WALL)
    body += Pos(0, SW_Y, 0) * slab(RectangleRounded(*well_out, 2), WELL_FLOOR_Z - SW_PANEL_T, SEAT_Z)
    # PSU slot rails + end stop
    z_pcb = FLOOR_Z - PCB_STANDOFF
    rail_z0 = z_pcb - PCB[2] - 3
    rail_len = PCB[1] + 2
    for s in (-1, 1):
        rail = Pos(s * (PCB[0] / 2 + 1), PCB_Y, (FLOOR_Z + rail_z0) / 2) * Box(4, rail_len, FLOOR_Z - rail_z0)
        groove = Pos(s * (PCB[0] / 2 + 0.25), PCB_Y + 1, z_pcb - PCB[2] / 2) * Box(2.5, rail_len + 2, PCB[2] + 0.4)
        body += rail - groove
    body += Pos(0, PCB_Y - PCB[1] / 2 - 1.6, (FLOOR_Z + z_pcb) / 2) * Box(PCB[0] + 6, 1.6, PCB_STANDOFF)
    # MSR-2 and SHT45 bay frames
    body += frame(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1.6, 1, 0, PT, MSR_Y)
    body += frame(SHT[0] + 0.8, SHT[1] + 0.8, 1.6, 0.5, 0, PT, SHT_Y)

    # ---------------- cuts ----------------
    body -= slab(stadium(*POCKET_IN), SEAT_Z, PT + 5)
    body -= Pos(0, SW_Y, 0) * slab(RectangleRounded(SW_BEZEL[0] + 2 * CLR, SW_BEZEL[1] + 2 * CLR, 1),
                                   WELL_FLOOR_Z, SEAT_Z + 0.1)
    body -= Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), WELL_FLOOR_Z - SW_PANEL_T - 1, WELL_FLOOR_Z + 1)
    body -= Pos(0, STEEL_Y, 0) * slab(Rectangle(STEEL[0], STEEL[1]), SEAT_Z - STEEL[2], SEAT_Z + 0.1)
    for s in (-1, 1):  # finger scoops either side of the remote
        body -= Pos(s * (POCKET_IN[0] / 2 + 1), 0, PT + 2.5) * ellipsoid(5.6, 12.6, 7)
    for s in (-1, 1):  # countersunk #6 holes
        y = s * SCREW_PITCH / 2
        body -= Pos(0, y, PT / 2) * Cylinder(SCREW_D / 2, PT + 2)
        body -= Pos(0, y, PT - 1.9) * Cone(SCREW_D / 2, SCREW_HEAD_D / 2, 3.81)
    body -= Pos(0, MSR_Y, 0) * slab(RectangleRounded(MSR[0] + 2 * CLR, MSR[1] + 2 * CLR, 1), -0.01, PT - RADAR_WALL)
    body -= Pos(LUX_POS[0], MSR_Y + LUX_POS[1], PT - 0.5) * Cylinder(1.5, 6)
    for i in range(-2, 3):  # MSR vents, top edge
        body -= Pos(i * 7 + 1.5, PH / 2 - SKIN + 2, 6) * Box(3, 6, 6)
    body -= Pos(0, SHT_Y, 0) * slab(RectangleRounded(SHT[0] + 0.8, SHT[1] + 0.8, 0.5), -0.01, PT - SKIN)
    for i in (-1, 0, 1):  # SHT vents: face + bottom edge
        body -= Pos(i * 4, SHT_Y, PT - 1) * Box(2, 6, 4)
        body -= Pos(i * 4, -PH / 2 + 4, 5) * Box(2, 10, 6)
    # 5 V lead pass-through in the collar
    body -= Pos(BOX_W / 2 + 3.5, 30, 4) * Rot(0, 90, 0) * Cylinder(1.75, 5)
    return body


def ellipsoid(rx, ry, rz):
    from build123d import Matrix
    return Sphere(1).transform_geometry(Matrix([[rx, 0, 0, 0], [0, ry, 0, 0], [0, 0, rz, 0]]))


def checks(part):
    bb = part.bounding_box()
    print(f"bbox x {bb.min.X:.1f}..{bb.max.X:.1f}  y {bb.min.Y:.1f}..{bb.max.Y:.1f}  z {bb.min.Z:.1f}..{bb.max.Z:.1f}")
    print(f"volume {part.volume/1000:.1f} cm3, valid={part.is_valid}")
    sw_back = WELL_FLOOR_Z - SW_PANEL_T - SW_BODY[2]
    psu_back = FLOOR_Z - PCB_STANDOFF - PCB[2] - IRM[2]
    deepest = min(sw_back, psu_back, bb.min.Z)
    print(f"deepest item {deepest:.1f} mm -> wiring space left in {BOX_D} mm box: {BOX_D + deepest:.1f} mm")
    assert POCKET_OUT[0] < BOX_W - 1 and POCKET_OUT[1] < BOX_H - 1, "pocket does not fit box opening"
    assert BOX_D + deepest >= 15, "less than 15 mm left for wire nuts - check box depth"


if __name__ == "__main__":
    p = build()
    checks(p)
    if "--check" not in sys.argv:
        OUT.mkdir(exist_ok=True)
        export_step(p, str(OUT / "wallplate.step"))
        export_stl(p, str(OUT / "wallplate.stl"), tolerance=0.02, angular_tolerance=0.1)
        print("wrote", OUT / "wallplate.step")
