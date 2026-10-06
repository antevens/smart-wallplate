"""Geometry sanity checks for v0.2 (run by `make check`). Every assert is a constraint.

Barrier test: air = (box cavity + space in front of the wall) - insert, with the
single 5 V pass-through plugged. The air volume touching the back of the box
(mains) must not reach the room or the trim's low-voltage hollow.
"""
import sys
import numpy as np
from build123d import Box, Pos, Rectangle, Vector
from params import *
from common import slab, rr
import insert
import trim

FAILS = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def dims():
    print("dimensions")
    check(POCKET_OUT[0] <= PLUG[0] and POCKET_OUT[1] <= PLUG[1], f"pocket {POCKET_OUT[0]:.1f}x{POCKET_OUT[1]:.1f} inside plug {PLUG[0]:.1f}x{PLUG[1]:.1f}")
    check(PSU_X <= PLUG[0] / 2 and PSU_Y0 >= -PLUG[1] / 2, f"PSU rails (+-{PSU_X:.1f}, y>={PSU_Y0:.1f}) inside box opening less clearance")
    check(FLANGE_OUT[0] >= SEAL[0] and FLANGE_OUT[1] >= SEAL[1], "flange covers the seal band on the wall")
    check(IRM[0] / 2 <= PCB[0] / 2 - IRM_KEEPOUT, f"IRM ({IRM[0]}) clear of {IRM_KEEPOUT} mm rail strips on {PCB[0]} mm board")
    check(PCB[0] / 2 - RAIL_ENGAGE >= IRM[0] / 2 + 0.5, "rail lips clear the IRM body")
    check(PCB_TOP_Y <= SW_BODY_BOT_Y - PCB_TOP_GAP + 1e-6, f"PCB top {PCB_TOP_Y:.2f} >= {PCB_TOP_GAP} mm below rocker body")
    gap = SW_BODY_BOT_Y - (PCB_Y + PCB_J1_ENTRY_Y)
    check(gap >= J1_BEND_MIN, f"J1 pigtails have {gap:.1f} mm to turn before the rocker body (>= {J1_BEND_MIN})")
    check(PASS_X * -PCB_J2_X > 0, "5 V pass-through is on the same side as J2")
    check(-BOX_H / 2 + PCB[1] > PCB_Y - PCB[1] / 2, "box wall stops the PCB sliding out of the open rail end")
    check(SW_Y - SW_CUT[1] / 2 - SW_LATCH_CLR >= PSU_Y1, "latch cavity clear of the PSU end stop")
    check(GABLE_PEAK_Z + BARRIER_MIN <= SEAT_Z - STEEL[2] - SEAT_T + 1e-6, "floor >= SEAT_T under steel recess, above PSU roof")
    check(min(POCKET_WALL, BARRIER_MIN) >= V0_RATED_T, f"barrier walls >= V-0 rated thickness {V0_RATED_T} (fill V0_RATED_T from the datasheet)")
    msr_top = MSR_Y + MSR[1] / 2 + CLR
    check(msr_top <= PH / 2 - SKIN, f"MSR-2 bay top {msr_top:.2f} inside trim (<= {PH/2-SKIN})")
    check(SHT_Y - SHT[1] / 2 - 0.4 >= -PH / 2 + SKIN, "SHT45 bay inside trim")
    sw_back = PANEL_BOT_Z - SW_BODY[2]
    psu_back = PCB_FRONT_Z - IRM[2]
    deepest = min(sw_back, psu_back, Z_BOT)
    left = BOX_D + deepest
    print(f"       deepest item {deepest:.1f} mm (rocker {sw_back:.1f}, IRM {psu_back:.1f}, insert {Z_BOT:.1f}); "
          f"wiring space in a {BOX_D} mm box: {left:.1f} mm")
    check(left >= 15, "at least 15 mm left behind everything for wire nuts")


def solids(ins, tr):
    print("solids")
    check(ins.is_valid and len(ins.solids()) == 1, "insert is one valid solid")
    check(tr.is_valid and len(tr.solids()) == 1, "trim is one valid solid")
    ov = (ins & tr).volume
    check(ov < 0.01, f"insert and trim do not overlap ({ov:.3f} mm3)")


def psu_fit(ins):
    print("PSU carrier (KiCad STEP) in the insert")
    import assembly
    if not assembly.PCB_STEP.exists():
        check(False, "cad/vendor/psu_carrier.step missing - run make pcb"); return
    board = assembly.psu()
    ov = 0.0
    for sol in board.solids():
        r = sol & ins
        ov += r.volume if r is not None else 0.0
    print(f"       {len(board.solids())} solids in the board STEP")
    check(ov < 0.5, f"board + parts do not collide with the insert ({ov:.2f} mm3)")
    slab_ = max(board.solids(), key=lambda q: q.bounding_box().size.X * q.bounding_box().size.Y).bounding_box()
    check(abs(slab_.size.X - PCB[0]) < 0.05 and abs(slab_.size.Y - PCB[1]) < 0.05,
          f"KiCad board {slab_.size.X:.2f} x {slab_.size.Y:.2f} matches params PCB {PCB[0]} x {PCB[1]}")
    bb = board.bounding_box()
    check(bb.min.Z >= PANEL_BOT_Z - SW_BODY[2] - 0.01, f"PSU (deepest {bb.min.Z:.1f}) no deeper than the rocker body")


def barrier(ins):
    print("barrier")
    room = slab(rr(PW + 20, PH + 20, 5), 0, PT + 10)
    box = slab(Rectangle(BOX_W, BOX_H), -BOX_D, 0)
    # plug the two openings that are closed by something else when installed:
    # the 5 V pass-through (lead + sleeve) and the rocker cutout (the certified rocker body)
    rocker = Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), PANEL_BOT_Z - 1, WELL_FLOOR_Z + 1)
    air = (room + box) - ins - insert.pass_through() - rocker
    parts = air.solids()
    mains = [s for s in parts if s.is_inside(Vector(0, 0, -BOX_D + 1))]
    check(len(mains) == 1, "found the mains air volume")
    m = mains[0]
    for name, p in [("room in front of the face", (0, 0, PT + 5)),
                    ("remote pocket", (0, 0, SEAT_Z + 1)),
                    ("trim hollow (low-voltage)", (PW / 2 - 4, 0, 5)),
                    ("MSR-2 bay", (0, MSR_Y, 5))]:
        check(not m.is_inside(Vector(*p)), f"mains air does not reach the {name}")
    check(m.bounding_box().max.Z <= 0.01, f"mains air stays behind the wall plane (max z {m.bounding_box().max.Z:.2f})")


def _face_poly(f):
    import shapely
    def ring(w):
        pts = [v for e in w.edges() for v in (e.positions([i / 24 for i in range(25)]) if e.geom_type.name != "LINE" else [e.position_at(0), e.position_at(1)])]
        return [(q.X, q.Y) for q in pts]
    outer = ring(f.outer_wire())
    holes = [ring(w) for w in f.inner_wires()]
    return shapely.Polygon(outer, holes).buffer(0)


def overhangs(name, part, limit=3.0, angle=50.0, hole_r=2.5):
    """Downward faces steeper than `angle` from vertical that are not on the bed.
    Planar faces: width = 2 x max inscribed circle (bridges and short ledges up to
    `limit` mm are accepted). Curved faces: small bores (r <= hole_r) are accepted,
    anything else steeper than `angle` fails."""
    import shapely
    zmin = part.bounding_box().min.Z
    worst, bad = 0.0, []
    lim = -np.sin(np.radians(angle))  # normal.z of a face `angle` deg from vertical
    for f in part.faces():
        if f.bounding_box().max.Z < zmin + 0.05:
            continue  # on the bed
        gt = f.geom_type.name
        if gt == "PLANE":
            n = f.normal_at(f.center())
            if n.Z >= lim:
                continue
            w = 2 * shapely.maximum_inscribed_circle(_face_poly(f)).length
            worst = max(worst, w)
            bb = f.bounding_box()
            if w > limit:
                bad.append(f"plane z={bb.min.Z:.1f} width {w:.1f} at x {bb.min.X:.0f}..{bb.max.X:.0f} y {bb.min.Y:.0f}..{bb.max.Y:.0f}")
            continue
        steep = False
        for u in np.linspace(0.05, 0.95, 7):
            for v in np.linspace(0.05, 0.95, 7):
                if f.normal_at(u, v).Z < lim:
                    steep = True
                    break
            if steep:
                break
        if not steep:
            continue
        r = getattr(f, "radius", None) if gt == "CYLINDER" else None
        if gt in ("CYLINDER", "SPHERE") and f.bounding_box().diagonal < 60 and _small_bore(f, hole_r):
            continue
        bb = f.bounding_box()
        bad.append(f"{gt.lower()} area {f.area:.0f} at x {bb.min.X:.0f}..{bb.max.X:.0f} y {bb.min.Y:.0f}..{bb.max.Y:.0f} z {bb.min.Z:.1f}..{bb.max.Z:.1f}")
    for r in bad[:10]:
        print("         " + r)
    check(not bad, f"{name}: no unsupported overhangs (widest flat ledge/bridge {worst:.1f} mm <= {limit} mm)")


def _small_bore(f, r):
    try:
        return f.radius <= r + 1e-6
    except Exception:
        bb = f.bounding_box()
        return min(bb.size.X, bb.size.Y, bb.size.Z) <= 2 * r + 0.1


def main():
    dims()
    ins = insert.build()
    tr = trim.build()
    solids(ins, tr)
    psu_fit(ins)
    barrier(ins)
    from export import PRINT_ORIENT
    print("printability (no supports)")
    overhangs("insert", PRINT_ORIENT["insert"](ins))
    overhangs("trim", PRINT_ORIENT["trim"](tr), limit=3.5)  # vent windows bridge 3 mm
    print("FAILED: " + "; ".join(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
