"""EU CAP (D-30, D-36): the whole mains / low-voltage barrier of the EU plate.

A flat 1.6 mm floor over the box and the seal band round the Ø68 hole (the remote rests on the
pocket-floor insert on it), a cup under the remote's upper half down to the emergency rocker's
panel (Marquardt 1802.2504; the rocker body plugs the cutout), bosses for the trim's two screws, for
the 5 V board and (long) for the mains board, two holes for the 5 V board's spring pins (5 V to the
flex, no wires). Two countersunk screws into the box's top and bottom domes, in the pocket floor,
fix it. The supplied magnet is glued to its underside.
Print: UL94 V-0 filament, top face down (export flips it), no supports.
Run:  python cap_eu.py  -> ../../../build/eu/cap.step / .stl
"""
from build123d import Cone, Cylinder, Pos, Rectangle
from params_eu import *
from common import rr, slab


def screw_hole(x, y):
    bore = Pos(x, y, CAP_T / 2) * Cylinder(SCREW_D / 2, CAP_T + 2)
    sink = (SCREW_HEAD_D - SCREW_D) / 2
    head = Pos(x, y, CAP_T - sink / 2 + 0.01) * Cone(SCREW_D / 2, SCREW_HEAD_D / 2, sink)
    return bore + head


def trim_bosses():
    out = None
    for sx in (-1, 1):
        b = Pos(sx * TRIM_SCREW_X, TRIM_SCREW_Y, -TRIM_BOSS_L / 2 + 0.01) * Cylinder(TRIM_BOSS_D / 2, TRIM_BOSS_L)
        out = b if out is None else out + b
    return out


def board_bosses():
    """Bosses from the floor's underside down to the 5 V board's front, M2 bores from below."""
    out = None
    for x, y in WB_MOUNT:
        b = Pos(x, y, WB_FRONT / 2 + 0.01) * Cylinder(WB_BOSS_D / 2, -WB_FRONT + 0.02)
        b -= Pos(x, y, WB_FRONT + 2.5 - 0.01) * Cylinder(WB_MOUNT_D * 0.75 / 2, 5.0)
        out = b if out is None else out + b
    return out


def mains_bosses():
    """Long bosses from the floor's underside down to the mains board's front, M2 bores from below."""
    out = None
    for x, y in MB_BOSS:
        b = Pos(x, y, MB_FRONT / 2 + 0.01) * Cylinder(MB_BOSS_D / 2, -MB_FRONT + 0.02)
        b -= Pos(x, y, MB_FRONT + 3.0 - 0.01) * Cylinder(WB_MOUNT_D * 0.75 / 2, 6.0)
        out = b if out is None else out + b
    return out


def trim_bores():
    """Blind tap-drill bores for the trim screws: through the floor into the bosses, closed at the bottom."""
    out = None
    depth = CAP_T + TRIM_BOSS_L - 1.0
    for sx in (-1, 1):
        b = Pos(sx * TRIM_SCREW_X, TRIM_SCREW_Y, CAP_T - depth / 2 + 0.01) * Cylinder(TRIM_SCREW_D * 0.8 / 2, depth)
        out = b if out is None else out + b
    return out


def cup():
    """Switch cup: walls from the floor down to the rocker's panel, panel with the snap-in cutout."""
    outer = Pos(0, SW_Y, 0) * slab(rr(*CUP_OUT, 1.0), PANEL_BOT_Z, 0.01)
    return outer


def cup_cut():
    inner = Pos(0, SW_Y, 0) * slab(rr(*CUP_IN, 0.5), PANEL_TOP_Z, CAP_T + 1)
    cutout = Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), PANEL_BOT_Z - 1, PANEL_TOP_Z + 0.1)
    return inner + cutout


def pin_holes():
    """Two of the cap's openings: one round each spring pin (5 V side, R9); the third is the rocker's cutout."""
    out = None
    for x, y in PINS:
        h = Pos(x, y, CAP_T / 2) * Cylinder(PIN_CAP_HOLE_D / 2, CAP_T + 2)
        out = h if out is None else out + h
    return out


def build():
    body = Pos(0, 0, CAP_T / 2) * Cylinder(CAP_R, CAP_T)
    body += cup()
    body += trim_bosses()
    body += board_bosses()
    body += mains_bosses()
    body -= cup_cut()
    for x, y in SCREWS:
        body -= screw_hole(x, y)
    body -= trim_bores()
    body -= pin_holes()
    return body


if __name__ == "__main__":
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[3] / "build" / "eu"
    out.mkdir(parents=True, exist_ok=True)
    p = build()
    bb = p.bounding_box()
    print(f"cap bbox x {bb.min.X:.1f}..{bb.max.X:.1f} y {bb.min.Y:.1f}..{bb.max.Y:.1f} z {bb.min.Z:.1f}..{bb.max.Z:.1f}"
          f"  vol {p.volume/1000:.1f} cm3 valid={p.is_valid} solids={len(p.solids())}")
    export_step(p, str(out / "cap.step"))
    export_stl(p, str(out / "cap.stl"), tolerance=0.02, angular_tolerance=0.1)
