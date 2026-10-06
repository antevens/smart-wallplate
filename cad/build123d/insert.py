"""v0.2 BOX INSERT - every piece of mains/low-voltage barrier lives here.

Print: UL94 V-0 filament, as modelled (z up, lowest face Z_BOT on the bed), no supports.
Run:  python insert.py  -> ../../build/insert.step / .stl
"""
from build123d import Box, Cylinder, Polygon, Rectangle, Pos, Rot, Sphere, extrude, Plane
from params import *
from common import rr, stadium, slab, taper, ellipsoid, rod


def outline_solid():
    """Insert without any cavities (also used by trim.py as its clearance envelope)."""
    # pocket shell / thick floor, from the bed up to the face
    body = slab(stadium(*POCKET_OUT), Z_BOT, PT)
    # PSU block: rails, end stop and gable roof sit inside it
    body += Pos(0, (PSU_Y0 + PSU_Y1) / 2, 0) * slab(
        Rectangle(2 * PSU_X, PSU_Y1 - PSU_Y0), Z_BOT, GABLE_PEAK_Z + BARRIER_MIN)
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


def psu_bay():
    """Rails, groove and the gabled roof over the PCB back (open at the bottom end)."""
    y0, y1 = PSU_Y0 - 1, PCB_TOP_Y + RAIL_CLR
    L, yc = y1 - y0, (y0 + y1) / 2
    inner = PCB[0] / 2 - RAIL_ENGAGE
    cav = Pos(0, yc, (Z_BOT - 1 + GABLE_VALLEY_Z) / 2) * Box(2 * inner, L, GABLE_VALLEY_Z - Z_BOT + 1)
    gz0, gz1 = PCB_FRONT_Z - RAIL_CLR, PCB_BACK_Z + RAIL_CLR
    cav += Pos(0, yc, (gz0 + gz1) / 2) * Box(PCB[0] + 2 * RAIL_CLR, L, gz1 - gz0)
    # gables: triangles across X, extruded along Y
    n = int(2 * inner // GABLE_PITCH)
    x = -n * GABLE_PITCH / 2
    pts = [(x, GABLE_VALLEY_Z - 0.01)]
    for i in range(n):
        pts += [(x + (i + 0.5) * GABLE_PITCH, GABLE_PEAK_Z), (x + (i + 1) * GABLE_PITCH, GABLE_VALLEY_Z - 0.01)]
    roof = extrude(Plane.XZ.offset(-y0) * Polygon(*pts, align=None), L)
    assert abs(roof.bounding_box().min.Y - y0) < 0.01, "gable roof misplaced"
    return cav + roof


def build():
    body = outline_solid()
    # ---------------- cuts ----------------
    body -= slab(stadium(*POCKET_IN), SEAT_Z, PT + 5)                      # remote pocket
    body -= Pos(0, SW_Y, 0) * slab(rr(*WELL_IN, 1), WELL_FLOOR_Z, SEAT_Z + 0.1)  # switch well
    body -= Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), PANEL_BOT_Z - 1, WELL_FLOOR_Z + 1)
    latch = (SW_CUT[0] + 2 * SW_LATCH_CLR, SW_CUT[1] + 2 * SW_LATCH_CLR)
    body -= Pos(0, SW_Y, 0) * slab(Rectangle(*latch), Z_BOT - 1, PANEL_BOT_Z)  # rocker body + latches
    body -= psu_bay()
    body -= Pos(0, STEEL_Y, 0) * slab(Rectangle(STEEL[0], STEEL[1]), SEAT_Z - STEEL[2], SEAT_Z + 0.1)
    for s in (-1, 1):                                                       # finger scoops
        body -= Pos(s * SCOOP_X, 0, SCOOP_ZC) * ellipsoid(*SCOOP)
    for s in (-1, 1):                                                       # #6 screw clearance
        body -= Pos(0, s * SCREW_PITCH / 2, DECK_Z / 2) * Cylinder(SCREW_D / 2, DECK_Z + 2)
    body -= pass_through()
    for kx, ky in KEY_POS:                                                  # locating pins
        body += Pos(kx, ky, DECK_Z + KEY_H / 2 - 0.01) * Cylinder(KEY_D / 2, KEY_H + 0.02)
    return body


def pass_through():
    """The single 5 V lead hole: up out of the box, then 45 deg out through the flange."""
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
