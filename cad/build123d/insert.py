"""BOX INSERT - every piece of mains/low-voltage barrier lives here.

Print: UL94 V-0 filament, as modelled (z up, lowest face Z_BOT = the switch panel's underside
and the mounting bosses on the bed), no supports. The wiring board snaps onto four posts
(post.py) screwed into the bosses' tapped M4 holes (D-28).
Run:  python insert.py  -> ../../build/insert.step / .stl
"""
from build123d import Box, Cone, Cylinder, Rectangle, Pos, Sphere
from params import *
from common import rr, stadium, slab, taper, ellipsoid, rod


def outline_solid():
    """Insert without any cavities (also used by trim.py as its clearance envelope)."""
    # pocket shell / thick floor, from the bed up to the face
    body = slab(stadium(*POCKET_OUT), Z_BOT, PT)
    # 45-degree taper carrying the flange underside out to the plug outline (no overhang)
    t = taper(*POCKET_OUT, POCKET_OUT[0] / 2, -TAPER_D, 0, TAPER_D)
    body += t & slab(rr(*PLUG, PLUG_R), -TAPER_D - 1, 0)
    # flange: island outline + FLANGE, plus screw bosses; underside chamfered 45 deg
    # outside the flat seal band so it prints without supports
    f = slab(rr(*FLANGE_OUT, ISLAND_R + FLANGE), 0, DECK_Z)
    for s in (-1, 1):
        f += Pos(0, s * SCREW_PITCH / 2, DECK_Z / 2) * Cylinder(BOSS_R, DECK_Z)
    body += f & taper(*SEAL, PLUG_R + COLLAR_LIP, 0, DECK_Z, DECK_Z)
    # island: flush with the trim face
    body += slab(rr(*ISLAND, ISLAND_R), DECK_Z - 0.01, PT)
    return body


def build():
    body = outline_solid()
    # ---------------- cuts ----------------
    body -= slab(stadium(*POCKET_IN), SEAT_Z, PT + 5)                      # remote pocket
    body -= Pos(0, SW_Y, 0) * slab(rr(*WELL_IN, 1), WELL_FLOOR_Z, SEAT_Z + 0.1)  # switch well
    body -= Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), PANEL_BOT_Z - 1, WELL_FLOOR_Z + 1)
    body -= magnet_recess()
    for s in (-1, 1):                                                       # finger scoops
        body -= Pos(s * SCOOP_X, 0, SCOOP_ZC) * ellipsoid(*SCOOP)
    for s in (-1, 1):                                                       # #6 screw clearance
        body -= Pos(0, s * SCREW_PITCH / 2, DECK_Z / 2) * Cylinder(SCREW_D / 2, DECK_Z + 2)
    body -= pass_through()
    body -= tongue_slot()                                                   # battery-free tongue (D-41), above z 0
    for kx, ky in KEY_POS:                                                  # locating pins
        body += Pos(kx, ky, DECK_Z + KEY_H / 2 - 0.01) * Cylinder(KEY_D / 2, KEY_H + 0.02)
    import sensor_flex
    body += sensor_flex.shelf()                                             # jumper pad end under the spring fingers (D-27)
    body += mount_bosses()                                                  # after the pocket cut
    body -= mount_holes()
    return body


def mount_bosses():
    """Bosses for the board posts, from the print-bed plane up into the insert."""
    out = None
    for (x, y), top in zip(MOUNT_HOLES, MOUNT_BOSS_TOP):
        b = Pos(x, y, (Z_BOT + top) / 2) * Cylinder(MOUNT_BOSS_D / 2, top - Z_BOT)
        out = b if out is None else out + b
    return out


def mount_hole(x, y):
    """Blind tap-drill hole from the boss face, ending in a 45 deg cone (prints unsupported)."""
    bore = Pos(x, y, Z_BOT + MOUNT_THREAD_L / 2 - 0.01) * Cylinder(MOUNT_TAP_D / 2, MOUNT_THREAD_L)
    r0, r1 = MOUNT_TAP_D / 2, 0.1                             # 45 deg cone, small flat tip (meshes cleanly)
    tip = Pos(x, y, Z_BOT + MOUNT_THREAD_L + (r0 - r1) / 2 - 0.01) * Cone(r0, r1, r0 - r1)
    return bore + tip


def mount_holes():
    out = mount_hole(*MOUNT_HOLES[0])
    for x, y in MOUNT_HOLES[1:]:
        out += mount_hole(x, y)
    return out


def magnet_recess():
    """Supplied magnet recess: from above the magnet's nominal position down to the end of the
    flat back. The bottom end follows the magnet's own rounded end, so the magnet only needs a
    straight cut at the top."""
    w = MAGNET[0] + 2 * MAGNET_CLR
    r = MAGNET_END_R + MAGNET_CLR
    top = MAGNET_REC_Y + MAGNET[1] / 2 + MAGNET_CLR
    z0, z1 = SEAT_Z - MAGNET[2] - MAGNET_SETBACK, SEAT_Z + 0.1
    end = Pos(0, MAGNET_SLOT_BOT + r, 0) * slab(rr(w, 2 * r, r), z0, z1)
    upper = Pos(0, (top + MAGNET_SLOT_BOT + r) / 2, 0) * slab(Rectangle(w, top - MAGNET_SLOT_BOT - r), z0, z1)
    return end + upper


def tongue_slot():
    """Battery-free tongue (D-41): tunnel through the flange from the jumper's pad end to the pocket at the
    pad end's flex height and a groove down the pocket wall; all above the wall plane, between two
    low-voltage spaces (trim hollow, remote pocket)."""
    w, below, above = BC_NA_SLOT
    z0, z1 = TARGET_TOP_Z - JUMPER_T - below, TARGET_TOP_Z + above
    out_x, in_x = tongue_walls()
    x0, x1 = in_x - 0.01, FLANGE_OUT[0] / 2 + 0.01
    slot = Pos((x0 + x1) / 2, BC_NA_TONGUE_Y, (z0 + z1) / 2) * Box(x1 - x0, w, z1 - z0)
    g1 = out_x + BC_NA_GROOVE_D
    groove = Pos((x0 + g1) / 2, BC_NA_TONGUE_Y, (BC_NA_GROOVE_BOT + z1) / 2) * Box(g1 - x0, w, z1 - BC_NA_GROOVE_BOT)
    return slot + groove


def pass_through():
    """The single 5 V jumper hole: up out of the box, then 45 deg out through the flange."""
    sx = -1 if PASS_X < 0 else 1
    z0, zk = -TAPER_D - 2, -1.0
    a = (PASS_X, PASS_Y, z0)
    k = (PASS_X, PASS_Y, zk)
    run = FLANGE_OUT[0] / 2 + 3 - abs(PASS_X)
    b = (PASS_X + sx * run, PASS_Y, zk + run)
    return rod(a, k, PASS_D) + rod(k, b, PASS_D) + Pos(*k) * Sphere(PASS_D / 2)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[2] / "build"
    out.mkdir(exist_ok=True)
    p = build()
    bb = p.bounding_box()
    print(f"insert bbox x {bb.min.X:.1f}..{bb.max.X:.1f} y {bb.min.Y:.1f}..{bb.max.Y:.1f} z {bb.min.Z:.1f}..{bb.max.Z:.1f}"
          f"  vol {p.volume/1000:.1f} cm3 valid={p.is_valid} solids={len(p.solids())}")
    export_step(p, str(out / "insert.step"))
    export_stl(p, str(out / "insert.stl"), tolerance=0.02, angular_tolerance=0.1)
