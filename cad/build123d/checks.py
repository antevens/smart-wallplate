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
    pin_y = min(SW_Y, SW_Y + SW_SW_DIR * SW_PIN_GRID[1]) - 1.2
    check(pin_y >= WB_Y + WAGO_Y + WAGO6[1] / 2, f"rocker pins (pad edge y {pin_y:.1f}) clear of the terminal block")
    check(PASS_X * J2_POS[0] > 0, "5 V pass-through is on the same side as the 5 V connector")
    mag_floor = SEAT_Z - MAGNET[2] - MAGNET_SETBACK
    check(Z_BOT <= mag_floor - SEAT_T + 1e-6, "floor >= SEAT_T under the magnet recess")
    pad = (B_W - 2 * B_BACK_RUN, B_H - 2 * B_BACK_RUN)
    mag_top = MAGNET_REC_Y + MAGNET[1] / 2 + MAGNET_CLR
    check(MAGNET[0] + 2 * MAGNET_CLR <= pad[0] and mag_top <= pad[1] / 2 and MAGNET_SLOT_BOT >= -pad[1] / 2
          and MAGNET_SLOT_BOT <= MAGNET_REC_Y - MAGNET[1] / 2 - MAGNET_CLR,
          f"magnet recess lies under the remote's flat back ({pad[0]:.0f} x {pad[1]:.0f})")
    check(mag_top - MAGNET_SLOT_BOT >= MAGNET_END_R + MAGNET_CLR and MAGNET_END_R <= MAGNET[0] / 2,
          f"magnet recess {mag_top - MAGNET_SLOT_BOT:.1f} mm long holds the rounded end (R {MAGNET_END_R})")
    well_y0 = SW_Y - WELL_IN[1] / 2
    check(MAGNET_REC_Y + MAGNET[1] / 2 + MAGNET_CLR + SEAT_T <= well_y0, "magnet recess clear of the switch well")
    p0, p1 = MAGNET_Y - BC_STEEL[1] / 2, MAGNET_Y + BC_STEEL[1] / 2
    m0, m1 = MAGNET_REC_Y - MAGNET[1] / 2, MAGNET_REC_Y + MAGNET[1] / 2
    for name, (a, b) in (("the remote's own steel plate", (p0, p1)),
                         ("the back cover's steel plate", (BC_STEEL_Y - BC_STEEL[1] / 2, BC_STEEL_Y + BC_STEEL[1] / 2))):
        share = max(0.0, min(b, m1) - max(a, m0)) / MAGNET[1]
        check(share >= 0.75, f"magnet piece ({m0:.1f}..{m1:.1f}) {share * 100:.0f} % under {name} ({a:.1f}..{b:.1f})")
    check(MAGNET[1] >= MAGNET_END_R + 1.0 and MAGNET[1] <= MAGNET_FULL[1] - MAGNET_END_R,
          f"magnet piece {MAGNET[1]} mm cut from the {MAGNET_FULL[1]} mm magnet keeps one round end")
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
    sx, sy = b.origin("S1")
    check(abs(sx) < 0.01 and abs(sy - SW_Y) < 0.01, f"KiCad S1 at ({sx:.2f}, {sy:.2f}) matches params SW_Y {SW_Y}")
    pad_body_check(b)


def pad_body_check(b):
    """Pin tails and solder fillets of through-hole pads clear of the part bodies on the other side."""
    gap, pad, body = min(b.pad_body_gaps())
    check(gap >= PAD_BODY_GAP - 1e-6,
          f"KiCad: through-hole pads clear of the bodies on the other side (closest {pad} to {body}: "
          f"{gap:.2f} mm >= {PAD_BODY_GAP})")


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
    """Sensor flex (D-27): stack heights, spring-finger working height, clearances, jumper strip."""
    print("sensor flex (D-27)")
    import sensor_flex as sf, bilresa, post
    stack = STIFF_T + FLEX_T + B2B_STACK
    check(stack <= MSR_BACK_Z + 1e-6, f"CN2 plug stack {stack:.2f} mm fits behind the MSR-2 ({MSR_BACK_Z:.2f} mm, "
                                      f"B2B_STACK is MEASURE)")
    top = FLEX_HI_Z + FLEX_T + STIFF_T
    check(top <= SKIN_Z - 0.1, f"stiffened flex top {top:.2f} mm under the face skin ({SKIN_Z})")
    strip_edge = FLEX_X - FLEX_W / 2
    face = FLANGE_OUT[0] / 2
    check(strip_edge - face >= FLEX_LEAD_GAP - 1e-6, f"{strip_edge - face:.2f} mm strip along the flange face for the 5 V jumper")
    wall = PW / 2 - SKIN
    check(wall - (FLEX_X + FLEX_W / 2) >= 0.15, f"flex clears the trim's side wall by {wall - (FLEX_X + FLEX_W / 2):.2f} mm")
    rec = wall + TRIM_WALL_RECESS
    check(rec - FINGER_SEC_OUT >= 0.3 - 1e-6 and SKIN - TRIM_WALL_RECESS >= 0.8,
          f"finger section {rec - FINGER_SEC_OUT:.2f} mm inside the trim wall recess; wall left {SKIN - TRIM_WALL_RECESS} mm")
    lo, hi = FINGER_WH - FINGER_TOL, FINGER_WH + FINGER_TOL
    check(lo >= FINGER_WH_MIN and hi < FINGER_FREE, f"spring fingers at {FINGER_WH} +- {FINGER_TOL} mm working height, inside "
                                                    f"{FINGER_WH_MIN}..{FINGER_FREE} (S7081-42R)")
    tgt = sf.target().bounding_box()
    mx = min(FINGER_X - tgt.min.X, tgt.max.X - FINGER_X)
    my = min(min(y - tgt.min.Y, tgt.max.Y - y) for y in FINGER_Y)
    check(mx >= 1.0 and my >= 1.0, f"finger contact points over the jumper's pad end (margins x {mx:.2f}, y {my:.2f} mm)")
    edge = sf.shelf_edge()
    check(wall - edge >= 0.4, f"insert shelf {wall - edge:.2f} mm from the trim's side wall")
    sec_top = FINGER_Y[1] + FINGER_PAD[1] / 2 + 0.5
    check(TARGET_Y[1] - sec_top >= 2.5, f"{TARGET_Y[1] - sec_top:.2f} mm of the pad end's top left open for the "
                                         f"jumper's run to join")
    parts = sf.parts()
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    others = {"insert": ins, "trim": tr, "remote": bilresa.build(), "MSR-2 envelope": msr, "board posts": post.placed()}
    for pn, p in parts.items():
        for on, o in others.items():
            if pn == "target" and on == "insert":
                continue                                      # the pad end sits on the shelf
            r = p & o
            v = r.volume if r is not None else 0.0
            check(v < 0.01, f"{pn} clears the {on} ({v:.3f} mm3)")


def jumper_checks(ins, tr):
    """5 V flex jumper (D-27, R9): threads through the pass-through, spare length for plugging it in
    with the board beside the insert, clear of everything else."""
    print("5 V flex jumper")
    import jumper, sensor_flex as sf, bilresa, post, assembly
    from math import hypot
    diag = hypot(JUMPER_END[0], JUMPER_END[2])
    check(diag <= PASS_D - 0.5, f"jumper's connector end ({JUMPER_END[0]} x {JUMPER_END[2]}, diagonal {diag:.2f}) "
                                f"threads through the {PASS_D} mm pass-through")
    pts = jumper.path()
    direct = sum(hypot(*(b[i] - a[i] for i in range(3))) for a, b in zip([pts[0]] + pts[5:], pts[5:]))
    spare = jumper.length() - direct
    check(spare >= JUMPER_SERVICE - 1e-6, f"jumper {jumper.length():.0f} mm long, {spare:.0f} mm spare folded between "
                                          f"board and insert (plug in with the board beside the insert)")
    jmp = jumper.build()["jumper"]
    fp = sf.parts()
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    others = {"insert": ins, "trim": tr, "wiring board": assembly.wiring_board(), "board posts": post.placed(),
              "flex": fp["flex"], "spring fingers": fp["fingers"], "microphone": fp["mic"], "MSR-2 envelope": msr,
              "remote": bilresa.build()}
    for on, o in others.items():
        if on == "wiring board":
            continue                                       # its end sits in J2 (checked against the board slab below)
        r = jmp & o
        v = r.volume if r is not None else 0.0
        check(v < 0.05, f"jumper clears the {on} ({v:.3f} mm3)")
    slab_ = Pos(0, WB_Y, WB_FRONT_Z - WB[2] / 2) * Box(*WB)
    r = jmp & slab_
    check(r is None or r.volume < 0.01, "jumper clears the wiring board's slab")


def mic_checks(ins, tr):
    """Microphone (D-29): clear of the insert flange, port sealed to the skin, sound hole open on the flat face."""
    print("microphone (D-29)")
    import sensor_flex as sf
    from build123d import Cylinder
    sec = sf.mic_section().bounding_box()
    body = Pos(MIC_X, MIC_Y, FLEX_HI_Z - MIC[2] / 2) * Box(MIC[0] + 2 * MIC_CLR, MIC[1] + 2 * MIC_CLR, MIC[2])
    zc = (FLEX_HI_Z - MIC[2] + FLEX_HI_Z + FLEX_T) / 2           # mic underside up to the flex top
    zone = Pos(sec.center().X, sec.center().Y, zc) * Box(sec.size.X + 2 * MIC_CLR, sec.size.Y + 2 * MIC_CLR,
                                                         MIC[2] + FLEX_T)
    for name, z in (("widened flex section", zone), ("mic body", body)):
        r = z & ins
        v = r.volume if r is not None else 0.0
        check(v < 0.01, f"{name} keeps {MIC_CLR} mm from the insert ({v:.3f} mm3)")
    rise_end = MSR_Y - FLEX_RISE_DY
    check(MIC_SEC_Y[1] <= rise_end - 1.0 and MIC_SEC_Y[0] >= FINGER_LANE_Y[1] + 1.0,
          f"widened section y {MIC_SEC_Y[0]}..{MIC_SEC_Y[1]} on the flat channel run ({FINGER_LANE_Y[1]:.2f}..{rise_end:.2f})")
    my0, my1 = MIC_Y - MIC[1] / 2, MIC_Y + MIC[1] / 2
    check(MIC_SEC_Y[0] <= my0 - 0.5 and MIC_SEC_Y[1] >= my1 + 0.5 and MIC_SEC_IN <= MIC_X - MIC[0] / 2 - 0.5,
          "mic body footprint inside the widened section")
    z0 = FLEX_HI_Z + FLEX_T + STIFF_T
    check(SKIN_Z - z0 >= 0.1, f"gasket {SKIN_Z - z0:.2f} mm between the mic stiffener and the face skin")
    check(MIC_SKIN_HOLE_D < MIC_GASKET_D - 1.0, f"gasket ring {(MIC_GASKET_D - MIC_SKIN_HOLE_D) / 2:.2f} mm wide")
    probe = Pos(*MIC_PORT, (SKIN_Z + PT) / 2) * Cylinder(MIC_SKIN_HOLE_D / 2 - 0.05, SKIN - 0.1)
    r = probe & tr
    v = r.volume if r is not None else 0.0
    check(v < 0.001, f"sound hole open through the face skin ({v:.4f} mm3 of trim in it)")
    ix = ISLAND[0] / 2 + SPLIT_CLR
    iy = ISLAND[1] / 2 + SPLIT_CLR
    r_hole = MIC_SKIN_HOLE_D / 2
    gap_island = max(MIC_PORT[0] - ix, MIC_PORT[1] - iy) - r_hole
    gap_edge = (PW / 2 - FACE_CHAMFER) - MIC_PORT[0] - r_hole
    check(gap_island >= 1.0 and gap_edge >= 1.0,
          f"sound hole on the flat face: {gap_island:.2f} mm from the insert window, {gap_edge:.2f} mm from the chamfer")


def separation(ins, tr):
    """R9: the face plate (trim) and the insert are joined electrically only by the spring
    fingers on the 5 V jumper's pads: no wire or part belongs to both."""
    print("face plate / insert separation (R9)")
    import sensor_flex as sf, jumper, assembly
    fp = sf.parts()
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    face = {"MSR-2": msr, "flex": fp["flex"], "CN2 plug": fp["plug"], "SHT45": fp["sht45"], "microphone": fp["mic"],
            "spring fingers": fp["fingers"]}
    box_side = {"jumper pad end": fp["target"], "flex jumper": jumper.build()["jumper"],
                "wiring board": assembly.wiring_board()}
    _separation(face, box_side, {("spring fingers", "jumper pad end")})


def _separation(face, box_side, contacts, touch=0.05):
    """Every face-plate part is clear of every box-side part, except the listed contact pairs."""
    for fn, f in face.items():
        for bn, b in box_side.items():
            d = f.distance_to(b)
            if (fn, bn) in contacts:
                check(d < touch, f"{fn} touch the {bn} (contact, gap {d:.3f} mm)")
            else:
                check(d >= touch, f"{fn} not joined to the {bn} (gap {d:.2f} mm)")


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
    # the 5 V pass-through (flex jumper + sleeve) and the rocker cutout (the certified rocker body)
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
        verts, tris = f.tessellate(0.05, 0.5)                # points on the trimmed face, not its whole surface
        step = max(1, len(tris) // 200)
        steep = False
        for t in tris[::step]:
            a, b, c3 = verts[t[0]], verts[t[1]], verts[t[2]]
            try:
                nz = f.normal_at((a + b + c3) / 3).Z
            except Exception:                               # point not projectable: the triangle's own normal
                n = (b - a).cross(c3 - a)
                if n.length < 1e-9:
                    continue
                nz = n.normalized().Z
            if nz < lim:
                steep = True
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


def cover_checks():
    """Replacement back cover (D-35): fingers at working height inside their range, windows, flex
    clear of the body, contact pads on the cell axes clear of the remote's PCB strip, steel plate."""
    print("replacement back cover (D-35)")
    import backcover as bc
    ps = bc.cover_parts()
    c = ps["cover"]
    check(c.is_valid and len(c.solids()) == 1, f"cover: one valid solid ({c.volume / 1000:.2f} cm3)")
    lo, hi = BC_FLEX_Z - FINGER_TOL, BC_FLEX_Z + FINGER_TOL
    check(lo >= FINGER_WH_MIN and hi < FINGER_FREE, f"fingers at {BC_FLEX_Z} +- {FINGER_TOL} mm on the flush floor "
                                                    f"pads, inside {FINGER_WH_MIN}..{FINGER_FREE} (S7081-42R)")
    check(FINGER_FREE - BC_FLEX_Z > 0.1, f"free finger dome {FINGER_FREE - BC_FLEX_Z:.2f} mm below the back")
    for k in ("flex", "stiffener", "steel", "fingers", "contacts", "regulator"):
        r = ps[k] & c
        v = r.volume if r is not None else 0.0
        check(v < 0.01, f"{k} clears the cover body ({v:.3f} mm3)")
    ff = bc.fingers(FINGER_FREE)
    r = ff & c
    check(r is None or r.volume < 0.01, "free fingers pass through their windows")
    xi = BC_PCB_W / 2 + BC_PCB_CLR
    pw, ph = FINGER_PAD[0], FINGER_PAD[1]                    # contact finger pad on the end section (x, z): vertical
    check(BC_CELL_X - pw / 2 >= xi + 0.5, f"contact finger pads clear of the remote's PCB strip "
                                          f"({BC_CELL_X - pw / 2 - xi:.2f} mm beyond the notch)")
    lane = BC_FLEX_Z + BC_LANE_H + 0.15                      # +3V3 trace (0.3) across the band
    check(BC_CELL_Z - ph / 2 - lane >= 0.3, f"+3V3 lane across the band {BC_CELL_Z - ph / 2 - lane:.2f} "
                                            f"mm below the contact finger pads")
    check(BC_FLEX_Z + BC_END_H >= BC_CELL_Z + ph / 2 + 0.5, "contact finger pads within the end section")
    check(BC_CONTACT_W / 2 - pw / 2 >= 0.5, f"contact finger pads {BC_CONTACT_W / 2 - pw / 2:.2f} mm inside the end section")
    plate = BC_CELL_END_Y + BC_TERM_Y * BC_TERM_SETBACK
    dome = bc.end_fingers(FINGER_WH).bounding_box()
    tip = dome.min.Y if BC_TERM_Y < 0 else dome.max.Y
    check(abs(tip - plate) < 0.02, f"contact finger domes at working height {FINGER_WH} on the VBAT plate (y {plate:.2f}, "
                                   f"setback {BC_TERM_SETBACK} MEASURE)")
    import math
    arm = bc.end_fingers(FINGER_WH)
    top = arm.bounding_box().max.Z
    check(top >= BC_CELL_Z + FINGER[1] / 2 - 0.05, f"end fingers vertical, bend end up at z {top:.2f} (ramp faces "
                                                   "the remote as the cover goes on)")
    print(f"       GND contact: finger dome on the remote's leaf spring, which stands proud of the cell end plane "
          f"(its travel MEASURE): finger and leaf share the compression")
    for x, y in BC_FINGERS:
        check(BC_STRIP[0] + 0.2 <= x - FINGER[0] / 2 - BC_WIN_CLR + 1e-6 and x + FINGER[0] / 2 + BC_WIN_CLR <= BC_STRIP[1] - 0.2 + 1e-6,
              f"finger window at ({x}, {y}) inside the flex strip")
    check(BC_STEEL_FLOOR >= 0.4 - 1e-6, f"{BC_STEEL_FLOOR} mm of cover wall under the steel plate and the regulator")
    for k in ("pad_stiffener",):
        r = ps[k] & c
        check(r is None or r.volume < 0.01, f"{k} clears the cover body (pegs through its holes)")
    stake = BC_PEG_STAKE
    check(stake >= 0.8 and BC_PEG_HOLE - BC_PEG_D >= 0.15, f"heat-stake pegs {stake} mm above the stiffener, "
                                                          f"{BC_PEG_HOLE - BC_PEG_D:.1f} mm play in their holes")
    top = bc.end_retainers().bounding_box().max.Z
    check(top <= BC_CELL_Z + AAA_D / 2 + 1e-6, f"end section hooks top at z {top:.2f}, under the cell top "
                                               f"({BC_CELL_Z + AAA_D / 2:.2f}, ESTIMATE): clear of the housing's floor")
    check(BC_END_HOOK >= 0.4 and BC_END_LIP[1] >= 0.8, f"end section held: {BC_END_LIP[1]} mm lip at its foot, "
                                                       f"{BC_END_HOOK} mm hook over its top edge")
    clips = bc.steel_clips()
    r = clips & ps["steel"]
    check(r is None or r.volume < 0.001, "steel plate clips clear the plate")
    over = BC_STEEL_CLIP[2] - 0.15                         # hook reach minus the gap to the plate's end
    check(over >= 0.3, f"steel plate clips hook {over:.2f} mm over the plate's ends")
    ear = bc.latches().bounding_box()
    yc = B_H / 2 - BC_LATCH_IN
    check(ear.max.Y <= B_H / 2 - BC_WALL + 0.11 and yc + BC_LATCH_T / 2 + BC_LATCH_HOOK < B_H / 2 - 0.5,
          f"snap clips inside the outline at y +-{yc:.1f}, hook {BC_LATCH_HOOK} mm inwards (positions ESTIMATE)")
    tops = sorted(round(e.bounding_box().max.Z - BC_WALL, 2) for e in bc.latches().solids())
    check(tops == sorted(BC_LATCH_TOPS) and ear.max.Z <= B_SEAM_Z, f"snap clips {tops} mm above the inside floor "
                                                                  f"(measured), below the rim")
    tab = bc.side_tabs().bounding_box()
    gap = 2 * min(abs(s.bounding_box().min.X) if s.bounding_box().min.X > 0 else abs(s.bounding_box().max.X)
                  for s in bc.side_tabs().solids())
    check(abs(gap - BC_SIDE_TAB_GAP) < 0.01 and abs(tab.max.Z - BC_WALL - BC_SIDE_TAB[2]) < 0.01,
          f"side ribs {gap:.1f} mm apart inside, {BC_SIDE_TAB[2]} mm above the inside floor (both measured)")
    for k in ("flex", "stiffener", "contacts", "regulator"):
        r = bc.latches() & ps[k]
        check(r is None or r.volume < 0.001, f"snap clips clear the {k}")
    x0, x1, y0, y1 = BC_REG_RECESS
    for ref, (x, y) in BC_REG.items():
        w, h, t = BC_REG_BODY if ref == "U1" else BC_CAP0402
        inside = x0 + 0.1 <= x - w / 2 and x + w / 2 <= x1 - 0.1 and y0 + 0.1 <= y - h / 2 and y + h / 2 <= y1 - 0.1
        check(inside and BC_FLEX_Z - t >= BC_STEEL_FLOOR + 0.1, f"regulator part {ref} inside its recess "
                                                                 f"({BC_FLEX_Z - t - BC_STEEL_FLOOR:.2f} mm above the floor)")
    pad, jog = bc.strip_boxes()[:2]                           # the pad section continues above the regulator section
    check(x0 >= max(pad[0], jog[0]) and x1 <= min(pad[1], jog[1]) and y0 >= jog[2] and y1 <= pad[3],
          "regulator recess under the flex (regulator and pad sections)")
    print(f"       contacts on the cell axes at z {BC_CELL_Z} (MEASURE), cell end y {BC_CELL_END_Y:.2f} (REF), "
          f"end section copper y {bc.copper_y():.2f}")


def battery_free_checks(ins, tr):
    """Battery-free remote, NA (D-41): tongue from the jumper's pad end through the insert above the wall
    plane, floor insert in the pocket, replacement back cover seated on it."""
    print("battery-free remote, NA (D-41)")
    from build123d import Pos
    import backcover as bc
    import floor_na
    import jumper
    import sensor_flex as sf
    w, below, above = BC_NA_SLOT
    z_slot = TARGET_TOP_Z - JUMPER_T - below
    low = min(z_slot, BC_NA_GROOVE_BOT)
    check(low >= 0.3, f"tongue tunnel and groove above the wall plane (lowest z {low:.2f}): low-voltage to low-voltage")
    check(w <= 3.0, f"tunnel roof bridges {w} mm (<= 3.0, no supports)")
    check(BC_NA_NECK_W + 0.4 <= w, f"tongue {BC_NA_NECK_W} mm in the {w} mm tunnel")
    t = jumper.tongue()
    sfp = sf.parts()
    fl = floor_na.parts()
    lift = SEAT_Z + BC_FLOOR_T
    cov = {k: Pos(0, 0, lift) * v for k, v in bc.cover_parts().items()}
    rem = Pos(0, 0, lift) * bc.remote_front()

    def vol(a, b):
        r = a & b
        return 0.0 if r is None else r.volume
    for name, other in (("insert", ins), ("trim", tr), ("sensor flex", sfp["flex"]), ("fingers", sfp["fingers"])):
        v = vol(t, other)
        check(v < 0.01, f"tongue clears the {name} ({v:.3f} mm3)")
    for k in ("floor", "floor_flex", "floor_pads"):
        v = vol(fl[k], ins)
        check(v < 0.01, f"{k} clears the insert ({v:.3f} mm3)")
    for k, c in cov.items():
        v = vol(c, ins) + vol(c, t) + vol(c, fl["floor"]) + vol(c, fl["floor_flex"])
        check(v < 0.01, f"back cover {k} clears the insert, tongue and floor ({v:.3f} mm3)")
    v = vol(rem, ins) + vol(rem, t)
    check(v < 0.01, f"remote on the floor insert clears the insert and tongue ({v:.3f} mm3)")
    xd, wd, y_pad = BC_NA_DOWN
    for x, y in BC_FINGERS:
        check(abs(x - BC_FINGERS[0][0]) < 1e-6 and y + BC_FLOOR_PAD[1] / 2 <= y_pad - 0.3,
              f"floor pad under the finger at ({x}, {y}) on the pad strip")
    well_x, well_y0 = WELL_IN[0] / 2 + BC_FLOOR_CLR, SW_Y - WELL_IN[1] / 2 - BC_FLOOR_CLR
    check(xd - wd / 2 - 0.3 >= well_x or y_pad + 0.3 <= well_y0,
          f"tongue strip clear of the switch well's opening ({xd - wd / 2 - 0.3 - well_x:.2f} mm)")
    s0, s1 = BC_STEEL_Y - BC_STEEL[1] / 2, BC_STEEL_Y + BC_STEEL[1] / 2
    m0, m1 = MAGNET_REC_Y - MAGNET[1] / 2, MAGNET_REC_Y + MAGNET[1] / 2
    share = max(0.0, min(s1, m1) - max(s0, m0)) / MAGNET[1]
    print(f"       magnet over the cover's steel plate: {share * 100:.0f} % of its height; remote face "
          f"{B_PROUD + BC_FLOOR_T:.1f} mm proud on the floor insert (pull test: MEASUREMENTS)")


def msr_hook_checks(hooks, others, back_z, board_x, y):
    """MSR-2 snap hooks (D-45): lip over the board's back face, clear of the board and the flex parts."""
    from build123d import Box, Pos
    board = Pos(0, y, back_z + 0.8) * Box(board_x, MSR_BOARD[1], 1.6)
    r = hooks & board
    check(r is None or r.volume < 0.001, "MSR-2 snap hooks clear the board")
    over = MSR_HOOK - 0.2
    check(over >= 0.25, f"MSR-2 snap hooks hold {over:.2f} mm over the board's back face at both short ends")
    for name, o in others.items():
        r = hooks & o
        check(r is None or r.volume < 0.001, f"MSR-2 snap hooks clear the {name}")


def main():
    dims()
    terminal_entry()
    ins = insert.build()
    tr = trim.build()
    solids(ins, tr)
    board_fit(ins)
    mounting(ins)
    sensor_flex_checks(ins, tr)
    jumper_checks(ins, tr)
    mic_checks(ins, tr)
    separation(ins, tr)
    barrier(ins)
    cover_checks()
    battery_free_checks(ins, tr)
    import trim as trim_mod
    import sensor_flex
    sfp = sensor_flex.parts()
    print("MSR-2 retention (D-45)")
    msr_hook_checks(trim_mod.msr_hooks()[0], {"sensor flex": sfp["flex"], "CN2 plug": sfp["plug"]}, MSR_BACK_Z,
                    MSR_BOARD[0], MSR_Y)
    from export import PRINT_ORIENT
    print("printability (no supports)")
    overhangs("insert", PRINT_ORIENT["insert"](ins))
    overhangs("trim", PRINT_ORIENT["trim"](tr), limit=3.5)  # vent windows bridge 3 mm
    import backcover
    overhangs("back cover", backcover.cover())                 # printed back down
    import floor_na
    overhangs("NA floor insert", Pos(0, 0, -SEAT_Z) * floor_na.parts()["floor"])   # printed flat
    print("FAILED: " + "; ".join(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
