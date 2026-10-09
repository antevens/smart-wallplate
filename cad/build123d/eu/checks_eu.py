"""EU variant checks (D-30), run by `make eu`.

Barrier test as in checks.py: air = (box cavity less its four screw domes + space in front of the
wall) - cap, with the rocker cutout (closed by the rocker body) and the two spring-pin holes
(pin barrels) plugged. The air touching the back of the box (mains) must stay behind the wall plane.
"""
import sys
from math import hypot
from build123d import Box, Cylinder, Pos, Rectangle, Rot, Vector
from params_eu import *
from common import rr, slab
import checks as base
import cap_eu
import trim_eu
import boards_eu
import sensor_eu

check = base.check


def _corners(cx, cy, w, h):
    return [(cx + sx * w / 2, cy + sy * h / 2) for sx in (-1, 1) for sy in (-1, 1)]


def _rmax(cx, cy, w, h):
    return max(hypot(x, y) for x, y in _corners(cx, cy, w, h))


def _in_stadium(x, y, w, h):
    """Point inside a stadium w x h (long axis y) centred on the origin."""
    r = w / 2
    yc = max(0.0, abs(y) - (h / 2 - r))
    return hypot(x, yc) <= r


def layout():
    print("layout")
    print(f"       plate {PW:.1f} x {PH:.1f} mm, {PT:.1f} mm proud (remote flush), centre y {PC[1]:.1f} from the box "
          f"centre; cap Ø{2 * CAP_R:.1f} x {CAP_T} mm")
    lim = BOX_R - PLUG_CLR
    r = _rmax(0, SW_Y, *CUP_OUT)
    check(r <= lim, f"switch cup inside the box (corner r {r:.2f} <= {lim:.2f})")
    hidden = all(_in_stadium(x, y, B_W - 2.0, B_H - 2.0) for x, y in _corners(0, SW_Y, *CUP_IN))
    check(hidden, "switch cup under the remote (1 mm inside its outline)")
    for x, y in SCREWS:
        check(abs(hypot(x, y) - BOX_R) < 1e-6 and DOME_D >= SCREW_HEAD_D - 1.0,
              f"cap screw at ({x:.0f}, {y:.0f}) lands on a box dome (Ø{DOME_D})")
        inside = all(_in_stadium(x + dx, y + dy, POCKET_IN[0] - 1.0, POCKET_IN[1] - 1.0)
                     for dx, dy in ((SCREW_HEAD_D / 2, 0), (-SCREW_HEAD_D / 2, 0), (0, SCREW_HEAD_D / 2),
                                    (0, -SCREW_HEAD_D / 2)))
        cup = abs(y - SW_Y) - CUP_OUT[1] / 2 - SCREW_HEAD_D / 2
        check(inside and cup >= 1.0, f"cap screw head in the pocket floor under the remote, {cup:.1f} mm from the cup")
    r = hypot(TRIM_SCREW_X, TRIM_SCREW_Y) + TRIM_BOSS_D / 2
    check(r <= lim, f"trim screw bosses inside the box (r {r:.2f})")
    for x, y in PINS:
        r = hypot(x, y) + PIN_PAD_D / 2
        check(r <= WB_R - 0.25, f"spring pin pad at ({x}, {y}) on the 5 V board (r {r:.2f} <= {WB_R - 0.25:.2f})")
        check(not _in_stadium(x - PIN_CAP_HOLE_D / 2 - 0.3, y, *POCKET_OUT),
              f"spring pin hole at ({x}, {y}) outside the pocket walls (opens into the trim's right channel)")
        d = min(hypot(x - dx, y - dy) for dx, dy in DOMES) - DOME_NOTCH_R - PIN_PAD_D / 2
        check(d >= 0.0, f"spring pin pad {d:.2f} mm clear of the board's dome notches")
    r = _rmax(0, EU_MAGNET_Y, MAGNET[0], MAGNET[1])
    check(r <= lim and EU_MAGNET_Y + MAGNET[1] / 2 <= SW_Y - CUP_OUT[1] / 2 - 0.5,
          f"magnet under the floor inside the box, clear of the switch cup (corner r {r:.2f})")
    s0, s1 = BC_STEEL_Y - BC_STEEL[1] / 2, BC_STEEL_Y + BC_STEEL[1] / 2
    m0, m1 = EU_MAGNET_Y - MAGNET[1] / 2, EU_MAGNET_Y + MAGNET[1] / 2
    share = max(0.0, min(s1, m1) - max(s0, m0)) / MAGNET[1]
    check(share >= 0.75, f"magnet piece ({m0:.1f}..{m1:.1f}) {share * 100:.0f} % under the back cover's steel plate "
                         f"({s0:.1f}..{s1:.1f})")
    top = PANEL_TOP_Z + SW_ROCKER_H + SW_ROCKER_TOL
    check(top <= SEAT_Z - SW_ROCKER_CLR + 1e-6, f"rocker top {top:.2f} under the remote's back ({SEAT_Z:.2f}) at max tolerance")
    print(f"       rocker panel {PANEL_TOP_Z:.1f}..{PANEL_BOT_Z:.1f}, PCB seat (mains board front) {MB_FRONT:.1f} mm")
    # mains board: PSU and WAGO blocks on the back, inside the board, clear of each other and the rocker's pins
    rects = {"PSU": (MB_PSU_C, (PSU[0], PSU[1]))}
    rects.update({f"WAGO block {k}": (c, (WAGO_EU[1], WAGO_EU[0])) for k, c in zip("LN", MB_WAGO_C)})
    for name, (c, (w, h)) in rects.items():
        r = _rmax(*c, w, h)
        check(r <= WB_R - 0.5, f"{name} on the mains board (corner r {r:.2f} <= {WB_R - 0.5:.2f})")
        for dx, dy in DOMES:
            gap = hypot(max(abs(dx - c[0]) - w / 2, 0), max(abs(dy - c[1]) - h / 2, 0)) - DOME_D / 2
            check(gap >= DOME_CLR - 1e-6, f"{name} {gap:.2f} mm from the dome at ({dx:.0f}, {dy:.0f})")
        for sx in (-1, 1):
            for sy in (0, SW_SW_DIR):
                px, py = sx * SW_PIN_GRID[0] / 2, SW_Y + sy * SW_PIN_GRID[1]
                gap = hypot(max(abs(px - c[0]) - w / 2, 0), max(abs(py - c[1]) - h / 2, 0)) - 1.2
                check(gap >= 0.3, f"{name} {gap:.2f} mm clear of the rocker pin at ({px:.1f}, {py:.1f})")
    names = list(rects)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            (c1, (w1, h1)), (c2, (w2, h2)) = rects[names[a]], rects[names[b]]
            gap = max(abs(c1[0] - c2[0]) - (w1 + w2) / 2, abs(c1[1] - c2[1]) - (h1 + h2) / 2)
            check(gap >= 0.8, f"{names[a]} {gap:.2f} mm from the {names[b]}")
    x0, x1, ys, w = MB_SLOT
    pin_out = MB_PSU_C[1] - 10.16                          # PSU output row (TMPS 03, datasheet)
    pin_in = MB_PSU_C[1] + 10.16
    check(pin_out < ys - w / 2 - 1.0 and pin_in > ys + w / 2 + 1.0 and x1 - x0 >= PSU[0] + 6,
          f"relief slot under the PSU between its input row (y {pin_in:.1f}) and output row (y {pin_out:.1f}), "
          f"{x1 - x0:.0f} mm long")
    check(MB_HDR[1] - 2.54 - 1.0 > -WB_R and MB_HDR[1] + 1.0 < ys - w / 2, "header on the 5 V island below the slot")
    for x, y in MB_BOSS:
        r = hypot(x, y) + MB_BOSS_D / 2
        check(r <= lim, f"long boss at ({x}, {y}) inside the box (r {r:.2f})")
        cup = max(abs(x) - CUP_OUT[0] / 2, abs(y - SW_Y) - CUP_OUT[1] / 2) - MB_BOSS_D / 2
        check(cup >= 0.3, f"long boss at ({x}, {y}) {cup:.2f} mm from the switch cup")
        for name, (c, (w, h)) in rects.items():
            gap = hypot(max(abs(x - c[0]) - w / 2, 0), max(abs(y - c[1]) - h / 2, 0)) - TRIM_HEAD_D / 2
            check(gap >= 0.3, f"mains board screw at ({x}, {y}) head {gap:.2f} mm from the {name}")
    check(HDR_ENGAGE >= 2.5, f"header posts {HDR_ENGAGE:.2f} mm into the 5 V board's socket ({HDR_GAP:.1f} mm between "
                            f"the boards; MEASURE with the parts)")
    left = BOX_D + DEEPEST
    print(f"       5 V board {WB_FRONT:.1f}..{WB_BACK:.1f}; mains board {MB_FRONT:.1f}..{MB_BACK:.1f}, PSU to "
          f"{MB_BACK - PSU[2]:.1f}, WAGO to {MB_BACK - WAGO_EU[2]:.1f} (wires enter its back face)")
    print(f"       depth: deepest part {DEEPEST:.1f} mm, {left:.1f} mm left behind it in a {BOX_D} mm box "
          f"(wanted {WIRE_SPACE_MIN}; to be tested in a box, human decision 2026-10-08)")


def solids(cap, tr):
    print("solids")
    check(cap.is_valid and len(cap.solids()) == 1, f"cap: one valid solid ({cap.volume / 1000:.1f} cm3)")
    check(tr.is_valid and len(tr.solids()) == 1, f"trim: one valid solid ({tr.volume / 1000:.1f} cm3)")
    parts = boards_eu.parts()
    rem = boards_eu.remote()
    pairs = [("cap", cap, "trim", tr), ("remote", rem, "cap", cap), ("remote", rem, "trim", tr),
             ("remote", rem, "rocker", parts["switch"])]
    pairs += [(k, v, "cap", cap) for k, v in parts.items() if k != "switch"]
    r = hypot(*max(WB_MOUNT, key=lambda q: hypot(*q))) + WB_BOSS_D / 2
    check(r <= BOX_R - PLUG_CLR, f"5 V board bosses inside the box (r {r:.2f})")
    mb = parts["mains_board"]
    pairs += [("5 V board", parts["board"], "rocker", parts["switch"]),
              ("5 V board", parts["board"], "header", parts["header"]),
              ("mains board", mb, "PSU", parts["psu"]), ("mains board", mb, "WAGO blocks", parts["wago"]),
              ("rocker", parts["switch"], "mains board front parts", parts["mains_front"]),
              ("rocker", parts["switch"], "header", parts["header"]),
              ("WAGO blocks", parts["wago"], "PSU", parts["psu"]),
              ("magnet", parts["magnet"], "5 V board", parts["board"]),
              ("5 V board front parts", parts["front"], "magnet", parts["magnet"]),
              ("5 V board front parts", parts["front"], "rocker", parts["switch"]),
              ("socket", parts["socket"], "mains board front parts", parts["mains_front"]),
              ("socket", parts["socket"], "header body", boards_eu.header_body())]
    for an, a, bn, b in pairs:
        r = a & b
        v = r.volume if r is not None else 0.0
        check(v < 0.05, f"{an} clears the {bn} ({v:.3f} mm3)")
    domes = boards_eu.domes()
    for k, v in {**parts, "cap": cap}.items():
        r = v & domes
        vol = r.volume if r is not None else 0.0
        check(vol < 0.05, f"{k} clears the box's screw domes ({vol:.3f} mm3)")
    r = parts["switch"] & cap
    print(f"       rocker vs. cap: {r.volume if r is not None else 0.0:.2f} mm3 (snap fit in the panel cutout)")
    import cap_eu
    bosses = cap_eu.mains_bosses()
    for k in ("board", "psu", "wago", "switch", "mains_front", "header", "socket", "front", "pins"):
        r = parts[k] & bosses
        v = r.volume if r is not None else 0.0
        check(v < 0.05, f"long cap bosses clear the {k.replace('_', ' ')} ({v:.3f} mm3)")


def sensors(cap, tr):
    print("sensor flex, microphone, spring-pin contact")
    stack = FLEX_T + B2B_STACK
    check(FLEX_LO_Z >= 0.5 + 1e-6, f"flex plug end {FLEX_LO_Z:.2f} mm above the wall (CN2 stack {stack:.2f}, MEASURE)")
    top = FLEX_HI_Z + FLEX_T + STIFF_T
    check(top <= SKIN_Z - 0.1, f"stiffened flex top {top:.2f} mm under the face skin ({SKIN_Z})")
    lo, hi = FLEX_X - FLEX_W / 2, FLEX_X + 4.4
    wall = POCKET_OUT[0] / 2
    check(lo - wall >= 0.5 and (PW / 2 - SKIN) - hi >= 0.5 and FLEX_PAD_SEC[0] - (wall - WALL_RECESS) >= 0.25,
          f"flex x {lo:.1f}..{hi:.1f} (mic on the skin side) inside the right channel ({wall:.1f}..{PW / 2 - SKIN:.2f}); "
          f"pad section from {FLEX_PAD_SEC[0]} in the pocket wall's foot recess")
    probe = Pos(*MIC_PORT, (SKIN_Z + PT) / 2) * Cylinder(MIC_SKIN_HOLE_D / 2 - 0.05, SKIN - 0.1)
    r = probe & tr
    check(r is None or r.volume < 0.001, "microphone sound hole open through the face skin")
    wh = FLEX_PIN_Z - WB_FRONT
    check(PIN_WH_MIN <= wh - PIN_TOL and wh + PIN_TOL <= PIN_WH_MAX,
          f"spring pins at {wh:.2f} +- {PIN_TOL} mm working height, inside {PIN_WH_MIN}..{PIN_WH_MAX} (P70-2200045)")
    span = min(min(x - FLEX_PAD_SEC[0], FLEX_PAD_SEC[1] - x) for x, _ in PINS) - FLEX_PAD_D / 2
    check(span >= 0.3, f"flex pads {span:.2f} mm inside the flex's pad section")
    check(PIN_CAP_HOLE_D - PIN_BARREL_D <= 0.4, f"cap hole {PIN_CAP_HOLE_D} round the {PIN_BARREL_D} mm pin barrel "
                                                 f"({(PIN_CAP_HOLE_D - PIN_BARREL_D) / 2:.2f} mm radial gap)")
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    others = {"cap": cap, "trim": tr, "remote": boards_eu.remote(), "MSR-2 envelope": msr, "box domes": boards_eu.domes(),
              **boards_eu.parts()}
    sens = sensor_eu.parts()
    mated = {("plug", "MSR-2 envelope"), ("pads", "pins")}
    for pn, p in sens.items():
        for on, o in others.items():
            if (pn, on) in mated:
                continue
            r = p & o
            v = r.volume if r is not None else 0.0
            check(v < 0.05, f"{pn} clears the {on} ({v:.3f} mm3)")


def floor_checks(cap, tr):
    """Pocket-floor insert (D-35): fits the pocket, keeps the rocker reachable, pads under the
    back cover's fingers at any position of the remote in the pocket."""
    print("pocket-floor insert (D-35)")
    import floor_eu
    fl = floor_eu.parts()
    check(fl["floor"].is_valid and len(fl["floor"].solids()) == 1, f"floor insert: one valid solid "
                                                                     f"({fl['floor'].volume / 1000:.2f} cm3)")
    b = boards_eu.parts()
    for fn in ("floor", "floor_flex"):
        for on, o in (("cap", cap), ("trim", tr), ("rocker", b["switch"]), ("remote", boards_eu.remote())):
            r = fl[fn] & o
            v = r.volume if r is not None else 0.0
            check(v < 0.05, f"{fn.replace('_', ' ')} clears the {on} ({v:.3f} mm3)")
    cup = Pos(0, SW_Y, CAP_T + BC_FLOOR_T / 2) * Box(CUP_IN[0], CUP_IN[1], BC_FLOOR_T)
    r = fl["floor"] & cup
    check(r is None or r.volume < 0.001, "switch cup open through the floor insert")
    top = fl["floor_pads"].bounding_box().max.Z
    check(abs(top - SEAT_Z) < 0.02, f"floor pads flush with the remote's seat (z {top:.2f} vs {SEAT_Z:.2f})")
    play = CLR
    for (x, y), (x0, x1, y0, y1) in zip(BC_FINGERS, floor_eu.pads()):
        mx = min(x - x0, x1 - x) - play                     # dome contact point to the pad edge, remote at its limit
        my = min(y - y0, y1 - y) - play - abs(BC_DOME_DY)
        check(min(mx, my) >= 0.3, f"finger dome at ({x}, {y}) stays {min(mx, my):.2f} mm inside its pad with the "
                                  f"remote's {play} mm play")
    cut_x = CUP_IN[0] / 2 + BC_FLOOR_CLR
    cut_y0 = SW_Y - CUP_IN[1] / 2 - BC_FLOOR_CLR
    strip = [b for b in floor_eu.tongue_path() if b[3] > cut_y0]
    gap = min(b[0] for b in strip) - 0.15 - cut_x
    check(gap >= 0.2, f"tongue and floor pads clear of the switch cup's opening ({gap:.2f} mm)")
    lo, hi = sorted(y for _, y in PINS)
    room = (hi - lo - PIN_PAD_D) / 2 - EU_TONGUE_W / 2
    check(room >= 0.3, f"tongue between the spring-pin pads ({room:.2f} mm each side)")
    import backcover
    cov = Pos(0, 0, SEAT_Z) * backcover.cover()
    for on, o in (("trim (tabs, walls)", tr), ("floor insert", fl["floor"]), ("tongue", fl["floor_flex"]),
                  ("rocker", b["switch"]), ("cap", cap)):
        r = cov & o
        v = r.volume if r is not None else 0.0
        check(v < 0.05, f"seated back cover clears the {on} ({v:.3f} mm3)")
    gap = SEAT_Z + BC_STEEL_FLOOR
    print(f"       magnet face to steel plate {gap:.1f} mm (cap {CAP_T} + floor {BC_FLOOR_T} + cover {BC_STEEL_FLOOR}); "
          f"hold vs. 2 fingers >= 2 x 1.2 N: MEASURE")


def separation():
    """R9: the face plate (trim) and the cap side are joined electrically only by the spring
    pins pressing on the flex's pads: no wire or part belongs to both."""
    print("face plate / cap separation (R9)")
    sens, b = sensor_eu.parts(), boards_eu.parts()
    msr = Pos(0, MSR_Y, MSR_BACK_Z + MSR[2] / 2) * Box(*MSR)
    face = {"MSR-2": msr, "flex": sens["flex"], "CN2 plug": sens["plug"], "SHT45": sens["sht45"],
            "microphone": sens["mic"], "flex pads": sens["pads"]}
    import floor_eu
    face.update({k.replace("_", " "): v for k, v in floor_eu.parts().items()})
    box_side = {"spring pins": b["pins"], "5 V board": b["board"], "socket": b["socket"], "mains board": b["mains_board"],
                "header": b["header"], "PSU": b["psu"], "WAGO blocks": b["wago"], "5 V board front parts": b["front"],
                "mains board front parts": b["mains_front"], "rocker": b["switch"]}
    flex_only = {"flex": sens["flex"]}
    base._separation({k: v for k, v in face.items() if k != "flex"}, box_side, {("flex pads", "spring pins")})
    base._separation(flex_only, {k: v for k, v in box_side.items() if k != "spring pins"}, set())


def barrier(cap):
    print("barrier")
    room = Pos(PC[0], PC[1], 0) * slab(rr(PW + 20, PH + 20, 5), 0, PT + 10)
    box = Pos(0, 0, -BOX_D / 2) * Cylinder(BOX_R, BOX_D)
    for x, y in DOMES:
        box -= Pos(x, y, -BOX_D / 2) * Cylinder(DOME_D / 2, BOX_D + 0.01)
    plugs = Pos(0, SW_Y, 0) * slab(Rectangle(*SW_CUT), PANEL_BOT_Z - 0.2, PANEL_TOP_Z + 0.2) + cap_eu.pin_holes()
    air = (room + box) - cap - plugs
    mains = [s for s in air.solids() if s.is_inside(Vector(0, 0, -BOX_D + 1))]
    check(len(mains) == 1, "found the mains air volume")
    m = mains[0]
    for name, p in [("room in front of the face", (0, PC[1], PT + 5)),
                    ("remote pocket", (0, -10, SEAT_Z + 1)),
                    ("switch cup", (0, SW_Y, PANEL_TOP_Z + 1)),
                    ("trim hollow (low-voltage)", (-(CAP_R + 0.2), MSR_Y - 15, 5)),
                    ("MSR-2 bay", (0, MSR_Y, 5))]:
        check(not m.is_inside(Vector(*p)), f"mains air does not reach the {name}")
    check(m.bounding_box().max.Z <= 1e-3, f"mains air stays behind the wall plane (max z {m.bounding_box().max.Z:.2f})")


def board_checks():
    import kicad_board
    print("EU boards (KiCad)")
    for name in ("eu_mains_board", "eu_5v_board"):
        path = kicad_board.ROOT / "pcb" / "eu" / "kicad" / f"{name}.kicad_pcb"
        if not path.exists():
            print(f"       {name}: no KiCad board (run make pcb)")
            continue
        gap, pad, body = min(kicad_board.Board(path).pad_body_gaps())
        check(gap >= PAD_BODY_GAP - 1e-6, f"{name}: through-hole pads clear of the bodies on the other side "
              f"(closest {pad} to {body}: {gap:.2f} mm >= {PAD_BODY_GAP})")


def main():
    layout()
    board_checks()
    cap, tr = cap_eu.build(), trim_eu.build()
    solids(cap, tr)
    sensors(cap, tr)
    floor_checks(cap, tr)
    from common import board_hooks
    hooks = board_hooks(MSR_Y, MSR_BOARD[0], MSR_BACK_Z, PT - RADAR_WALL, MSR[0] / 2 + CLR, MSR_HOOK)[0]
    sens = sensor_eu.parts()
    print("MSR-2 retention (D-45)")
    base.msr_hook_checks(hooks, {"sensor flex": sens["flex"], "CN2 plug": sens["plug"]}, MSR_BACK_Z, MSR_BOARD[0], MSR_Y)
    separation()
    barrier(cap)
    print("printability (no supports)")
    base.overhangs("cap", Rot(180, 0, 0) * cap)
    base.overhangs("trim", Rot(180, 0, 0) * tr, limit=3.5)
    import floor_eu
    base.overhangs("floor insert", Pos(0, 0, -CAP_T) * floor_eu.parts()["floor"])
    print("FAILED: " + "; ".join(base.FAILS) if base.FAILS else "all checks passed")
    return 1 if base.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
