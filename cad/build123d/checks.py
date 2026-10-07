"""Geometry sanity checks (run by `make check`). Every assert is a constraint.

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
    check(WB[0] / 2 <= PLUG[0] / 2 and WB[1] / 2 + abs(WB_Y) <= PLUG[1] / 2,
          f"wiring board {WB[0]} x {WB[1]} fits the box opening less clearance")
    check(FLANGE_OUT[0] >= SEAL[0] and FLANGE_OUT[1] >= SEAL[1], "flange covers the seal band on the wall")
    top = SEAT_Z - (WELL_FLOOR_Z + SW_ROCKER_H + SW_ROCKER_TOL)
    check(top >= SW_ROCKER_CLR - 1e-6, f"rocker top clears the remote's back by {top:.1f} mm at max tolerance")
    check(SW_BEZEL[0] <= WELL_IN[0] and SW_BEZEL[1] <= WELL_IN[1], "rocker flange fits the switch well")
    m = _well_margin()
    check(m >= 0.5, f"switch well inside the pocket footprint (corner margin {m:.1f} mm, no undercut)")
    pin_y = SW_Y - SW_PIN_GRID[1] / 2 - 1.2
    check(pin_y >= WB_Y + WAGO_Y + WAGO6[1] / 2, f"rocker pins (pad edge y {pin_y:.1f}) clear of the terminal block")
    check(PASS_X * J2_POS[0] > 0, "5 V pass-through is on the same side as the 5 V connector")
    mag_floor = SEAT_Z - MAGNET[2] - MAGNET_SETBACK
    check(Z_BOT <= mag_floor - SEAT_T + 1e-6, "floor >= SEAT_T under the magnet recess")
    pad = (B_W - 2 * B_BACK_RUN, B_H - 2 * B_BACK_RUN)
    mag_top = MAGNET_Y + MAGNET[1] / 2 + MAGNET_CLR
    check(MAGNET[0] + 2 * MAGNET_CLR <= pad[0] and mag_top <= pad[1] / 2 and MAGNET_SLOT_BOT >= -pad[1] / 2
          and MAGNET_SLOT_BOT <= MAGNET_Y - MAGNET[1] / 2 - MAGNET_CLR,
          f"magnet recess lies under the remote's flat back ({pad[0]:.0f} x {pad[1]:.0f})")
    check(mag_top - MAGNET_SLOT_BOT >= MAGNET_END_R + MAGNET_CLR and MAGNET_END_R <= MAGNET[0] / 2,
          f"magnet recess {mag_top - MAGNET_SLOT_BOT:.1f} mm long holds the rounded end (R {MAGNET_END_R})")
    well_y0 = SW_Y - WELL_IN[1] / 2
    check(MAGNET_Y + MAGNET[1] / 2 + MAGNET_CLR + SEAT_T <= well_y0, "magnet recess clear of the switch well")
    check(min(POCKET_WALL, BARRIER_MIN) >= V0_RATED_T, f"barrier walls >= V-0 rated thickness {V0_RATED_T} (fill V0_RATED_T from the datasheet)")
    msr_top = MSR_Y + MSR[1] / 2 + CLR
    check(msr_top <= PH / 2 - SKIN, f"MSR-2 bay top {msr_top:.2f} inside trim (<= {PH/2-SKIN})")
    check(SHT_Y - SHT[1] / 2 - 0.4 >= -PH / 2 + SKIN, "SHT45 bay inside trim")
    deepest = min(WB_BACK_Z - WAGO6[2], WB_BACK_Z - IRM[2])
    left = BOX_D + deepest
    print(f"       board {WB_FRONT_Z:.1f}..{WB_BACK_Z:.1f} mm, deepest part {deepest:.1f} mm; "
          f"behind it in a {BOX_D} mm box: {left:.1f} mm, behind the board above the block: {BOX_D + WB_BACK_Z:.1f} mm")
    check(left >= WIRE_SPACE_MIN, f"at least {WIRE_SPACE_MIN} mm behind the terminal block / PSU")


def _behind(c, depth, e, box_c, box_size):
    """Gap from a block's closed back (centre c, depth along entry e) to a box; < 0 = overlap or in front."""
    back = c[0] * e[0] + c[1] * e[1] - depth / 2
    near = box_c[0] * e[0] + box_c[1] * e[1] + abs(e[0]) * box_size[0] / 2 + abs(e[1]) * box_size[1] / 2
    return back - near


def terminal_entry():
    print("terminal block entry vs. PSU")
    e = WAGO_ENTRY
    gap = _behind((WAGO_X, WB_Y + WAGO_Y), WAGO6[1], e, (IRM_C[0], WB_Y + IRM_C[1]), IRM[:2])
    check(gap >= WAGO_PSU_GAP, f"wire entries face {e}, PSU behind the block's closed back (gap {gap:.1f} mm "
          f">= {WAGO_PSU_GAP})")
    import kicad_board
    if not kicad_board.WB_PCB.exists():
        print("       no KiCad board, params only")
        return
    b = kicad_board.Board()
    ke = b.entry_dir("J1")
    check(ke == tuple(float(v) for v in e), f"KiCad J1 entries face {ke}, params WAGO_ENTRY {e}")
    for ref, c, size in (("J1", (WAGO_X, WB_Y + WAGO_Y), WAGO6[:2]), ("PS1", (IRM_C[0], WB_Y + IRM_C[1]), IRM[:2])):
        x0, x1, y0, y1 = b.fab_box(ref)
        kc, ks = ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0)
        if ref == "J1" and abs(ke[0]) > 0:
            ks = ks[::-1]                                   # depth along x when the entries face x
        ok = all(abs(kc[i] - c[i]) < 0.05 and abs(ks[i] - size[i]) < 0.05 for i in (0, 1))
        check(ok, f"KiCad {ref} body {ks[0]:.1f} x {ks[1]:.1f} at ({kc[0]:.2f}, {kc[1]:.2f}) matches params")
    jx0, jx1, jy0, jy1 = b.fab_box("J1")
    px0, px1, py0, py1 = b.fab_box("PS1")
    kgap = _behind(((jx0 + jx1) / 2, (jy0 + jy1) / 2), abs(ke[0]) * (jx1 - jx0) + abs(ke[1]) * (jy1 - jy0), ke,
                   ((px0 + px1) / 2, (py0 + py1) / 2), (px1 - px0, py1 - py0))
    check(kgap >= WAGO_PSU_GAP, f"KiCad: PSU behind J1's closed back (gap {kgap:.1f} mm >= {WAGO_PSU_GAP})")


def mounting(ins):
    """Board posts (D-28): bosses, tapped holes, posts against the board, KiCad holes."""
    print("board mounting (screw-in snap posts)")
    from build123d import Cylinder
    import bilresa, post, assembly
    check(MOUNT_THREAD_L >= MOUNT_THREAD_MIN, f"tapped depth {MOUNT_THREAD_L} mm >= {MOUNT_THREAD_MIN} (1.5 x M4)")
    for (x, y), top in zip(MOUNT_HOLES, MOUNT_BOSS_TOP):
        tip = Z_BOT + MOUNT_THREAD_L + MOUNT_TAP_D / 2
        shell = Pos(x, y, (Z_BOT + tip + BARRIER_MIN) / 2) * Cylinder(MOUNT_TAP_D / 2 + BARRIER_MIN,
                                                                      tip + BARRIER_MIN - Z_BOT)
        gap = (shell - insert.mount_hole(x, y)) - ins
        v = gap.volume if gap is not None else 0.0
        check(v < 0.05, f"hole at ({x:.1f}, {y:.1f}): {MOUNT_THREAD_L} mm thread with >= {BARRIER_MIN} mm wall "
                        f"({v:.2f} mm3 missing)")
        check(abs(x) + MOUNT_BOSS_D / 2 <= PLUG[0] / 2 and abs(y - WB_Y) + MOUNT_BOSS_D / 2 <= PLUG[1] / 2,
              f"boss at ({x:.1f}, {y:.1f}) inside the box-fit outline")
        d = ((x - PASS_X) ** 2 + (y - PASS_Y) ** 2) ** 0.5 - MOUNT_BOSS_D / 2 - PASS_D / 2
        check(d >= MOUNT_PASS_GAP - 1e-6, f"boss at ({x:.1f}, {y:.1f}) clears the 5 V pass-through by {d:.2f} mm")
        reach = Pos(x, y, (Z_BOT + top + CLR) / 2) * Cylinder(MOUNT_BOSS_D / 2 + CLR, top + CLR - Z_BOT)
        r = reach & bilresa.build()
        check((r.volume if r is not None else 0.0) < 0.01, f"boss at ({x:.1f}, {y:.1f}) clears the remote by {CLR} mm")
    board = assembly.wiring_board()
    r = post.placed() & board
    ov = r.volume if r is not None else 0.0
    src = "KiCad STEP" if assembly.WB_STEP.exists() else "envelope (no holes)"
    check(ov < 0.05 or not assembly.WB_STEP.exists(), f"posts pass through the board holes, clear of all parts "
                                                       f"({src}: {ov:.2f} mm3)")
    lying = export_orient("post", post.build())
    overhangs("post lying on its flat", lying, small=5.0)
    import kicad_board
    if kicad_board.WB_PCB.exists():
        b = kicad_board.Board()
        for i, (x, y) in enumerate(MOUNT_HOLES, 1):
            k = b.origin(f"MH{i}")
            check(abs(k[0] - x) < 0.01 and abs(k[1] - (WB_Y + y)) < 0.01,
                  f"KiCad MH{i} at ({k[0]:.2f}, {k[1]:.2f}) matches params MOUNT_HOLES")
        k = b.origin("J2")
        check(abs(k[0] - J2_POS[0]) < 0.01 and abs(k[1] - (WB_Y + J2_POS[1])) < 0.01,
              f"KiCad J2 at ({k[0]:.2f}, {k[1]:.2f}) matches params J2_POS")


def sensor_flex_checks(ins, tr):
    """Sensor flex (D-27): stack heights, spring-finger working height, clearances, lead strip."""
    print("sensor flex (D-27)")
    import sensor_flex as sf, bilresa, post
    stack = STIFF_T + FLEX_T + B2B_STACK
    check(stack <= MSR_BACK_Z + 1e-6, f"CN2 plug stack {stack:.2f} mm fits behind the MSR-2 ({MSR_BACK_Z:.2f} mm, "
                                      f"B2B_STACK is MEASURE)")
    top = FLEX_HI_Z + FLEX_T + STIFF_T
    check(top <= SKIN_Z - 0.1, f"stiffened flex top {top:.2f} mm under the face skin ({SKIN_Z})")
    lead_edge = FLEX_X - FLEX_W / 2
    face = FLANGE_OUT[0] / 2
    check(lead_edge - face >= FLEX_LEAD_GAP - 1e-6, f"{lead_edge - face:.2f} mm strip along the flange face for the 5 V lead")
    wall = PW / 2 - SKIN
    check(wall - (FLEX_X + FLEX_W / 2) >= 0.15, f"flex clears the trim's side wall by {wall - (FLEX_X + FLEX_W / 2):.2f} mm")
    lo, hi = FINGER_WH - FINGER_TOL, FINGER_WH + FINGER_TOL
    check(lo >= FINGER_WH_MIN and hi < FINGER_FREE, f"spring fingers at {FINGER_WH} +- {FINGER_TOL} mm working height, inside "
                                                    f"{FINGER_WH_MIN}..{FINGER_FREE} (S7081-42R)")
    tgt = sf.target().bounding_box()
    mx = min(FINGER_X - tgt.min.X, tgt.max.X - FINGER_X)
    my = min(min(y - tgt.min.Y, tgt.max.Y - y) for y in FINGER_Y)
    check(mx >= 1.0 and my >= 1.0, f"finger contact points over the target board (margins x {mx:.2f}, y {my:.2f} mm)")
    edge = sf.shelf_edge()
    check(wall - edge >= 0.4, f"insert shelf {wall - edge:.2f} mm from the trim's side wall")
    sec_top = FINGER_Y[1] + FINGER_PAD[1] / 2 + 0.5
    check(TARGET_Y[1] - sec_top >= 2.5, f"{TARGET_Y[1] - sec_top:.2f} mm of the target board's top end left open for the "
                                         f"5 V lead pads")
    parts = sf.parts()
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    others = {"insert": ins, "trim": tr, "remote": bilresa.build(), "MSR-2 envelope": msr, "board posts": post.placed()}
    for pn, p in parts.items():
        for on, o in others.items():
            if pn == "target" and on == "insert":
                continue                                      # the target board sits on the shelf
            r = p & o
            v = r.volume if r is not None else 0.0
            check(v < 0.01, f"{pn} clears the {on} ({v:.3f} mm3)")


def export_orient(name, part):
    from export import PRINT_ORIENT, on_bed
    return on_bed(PRINT_ORIENT[name](part))


def _well_margin():
    """Distance from the well's far corner to the pocket's inner stadium (positive = inside)."""
    from math import hypot
    r = POCKET_IN[0] / 2
    yc = POCKET_IN[1] / 2 - r
    xw, yw = WELL_IN[0] / 2, abs(SW_Y) + WELL_IN[1] / 2
    return r - hypot(xw, max(yw - yc, 0))


def solids(ins, tr):
    print("solids")
    check(ins.is_valid and len(ins.solids()) == 1, "insert is one valid solid")
    check(tr.is_valid and len(tr.solids()) == 1, "trim is one valid solid")
    ov = (ins & tr).volume
    check(ov < 0.01, f"insert and trim do not overlap ({ov:.3f} mm3)")
    import bilresa
    r = bilresa.build() & ins
    ov = r.volume if r is not None else 0.0
    check(ov < 0.01, f"BILRESA model clears the pocket ({ov:.3f} mm3)")


def board_fit(ins):
    print("wiring board in the insert")
    import assembly
    board = assembly.wiring_board()
    ov, rocker_ov = 0.0, 0.0
    for sol in board.solids():
        r = sol & ins
        v = r.volume if r is not None else 0.0
        if sol.bounding_box().max.Z > PANEL_BOT_Z:   # only the rocker reaches through the panel
            rocker_ov += v
        else:
            ov += v
    src = "KiCad STEP" if assembly.WB_STEP.exists() else "envelope"
    check(ov < 0.5, f"board and parts ({src}) do not collide with the insert ({ov:.2f} mm3)")
    print(f"       rocker model vs. panel cutout: {rocker_ov:.2f} mm3 (snap fit; cutout and body per the "
          f"Marquardt drawing tolerances, see the well/cutout checks)")
    if assembly.WB_STEP.exists():
        slab_ = max(board.solids(), key=lambda q: q.bounding_box().size.X * q.bounding_box().size.Y).bounding_box()
        check(abs(slab_.size.X - WB[0]) < 0.05 and abs(slab_.size.Y - WB[1]) < 0.05,
              f"KiCad board {slab_.size.X:.2f} x {slab_.size.Y:.2f} matches params WB {WB[0]} x {WB[1]}")


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


def overhangs(name, part, limit=3.0, angle=50.0, hole_r=2.5, small=0.0):
    """Downward faces steeper than `angle` from vertical that are not on the bed.
    Planar faces: width = 2 x max inscribed circle (bridges and short ledges up to
    `limit` mm are accepted). Curved faces: small bores (r <= hole_r) and features whose
    bounding box diagonal is <= `small` mm are accepted (listed), anything else steeper
    than `angle` fails."""
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
        if bb.diagonal <= small:
            print(f"         accepted small {gt.lower()} overhang, {bb.diagonal:.1f} mm across, z {bb.min.Z:.1f}..{bb.max.Z:.1f}")
            continue
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
    terminal_entry()
    ins = insert.build()
    tr = trim.build()
    solids(ins, tr)
    board_fit(ins)
    mounting(ins)
    sensor_flex_checks(ins, tr)
    barrier(ins)
    from export import PRINT_ORIENT
    print("printability (no supports)")
    overhangs("insert", PRINT_ORIENT["insert"](ins))
    overhangs("trim", PRINT_ORIENT["trim"](tr), limit=3.5)  # vent windows bridge 3 mm
    print("FAILED: " + "; ".join(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
