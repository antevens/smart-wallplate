"""REPLACEMENT BACK COVER (D-35): replaces the BILRESA E2490's back cover; the remote runs without
cells from the plate's +3V3.

The cover keeps the remote's back shape (cut to a 45 deg chamfer below the curve's 45 deg point,
so it prints back down without supports) and carries the remote's steel plate. Inside, a
single-layer flex lies copper down on a ledge BC_FLEX_Z above the back face; two Harwin S7081-42R
spring fingers on it reach down through windows in the back. The flex runs to the terminal end,
bends up once and stands against two contact blocks; two more S7081-42R fingers on it, on the cell
axes, press on the remote's VBAT (fixed plate) and GND (leaf spring) battery contacts. The fingers
on the back take +5 V; a 3.3 V regulator on the flex (copper down, in a recess in the cover) feeds
VBAT. No cells: the remote's strap joins the bridge-end contacts.

On the face plate side a printed pocket-floor insert carries a tongue of the sensor flex in a
recess, its two gold pads flush under the fingers. The magnet holds the cover's back down on the
insert: that hard stop sets the fingers' working height.

Remote coordinates: origin = remote centre, x / y as the front view, z = 0 the back's outer face.
Sizes marked MEASURE / REF in params.py.
"""
from math import atan2, cos, degrees, pi, sin, sqrt
from build123d import Axis, Box, Cylinder, Plane, Pos, Rot, chamfer, loft
from params import *
from common import stadium, slab
import bilresa

Z_BEND = BC_FLEX_Z + FLEX_T / 2                          # flex mid-plane on the ledge
EDGE_C = 2 * B_BACK_RUN * (1 - sqrt(2) / 2)              # 45 deg chamfer tangent to the R B_BACK_RUN back curve


def copper_y():
    """y of the end section's copper face: FINGER_WH from the fixed contact plate, towards the cells."""
    return BC_COPPER_Y


def stiffener_y():
    """y of the stiffener's far face (towards the cells): the contact blocks start here."""
    return copper_y() - BC_TERM_Y * (FLEX_T + BC_END_T)


def end_blocks():
    """End section outline in the (x, z) plane: two pad blocks and the band under the PCB strip."""
    z0, z1 = BC_FLEX_Z, BC_FLEX_Z + BC_END_H
    xi = BC_PCB_W / 2 + BC_PCB_CLR
    xo = BC_CELL_X + BC_CONTACT_W / 2 + 0.5
    return [(-xo, -xi, z0, z1), (xi, xo, z0, z1), (-xi, xi, z0, z0 + BC_BRIDGE_H)]


def strip_top():
    return max(y for _, y in BC_FINGERS) + FINGER[1] / 2 + BC_PEG_END


def strip_bottom():
    """Lower end of the pad section; the run continues to the terminal end after BC_JOG."""
    return min(y for _, y in BC_FINGERS) - FINGER[1] / 2 - 1.0


def strip_boxes(clr=0.0):
    """Flex path on the ledge as (x0, x1, y0, y1): pad section, jog, run to the terminal end."""
    yc = copper_y()
    yt, yb = strip_top(), strip_bottom()
    yj = yb - BC_JOG
    xs0, xs1 = BC_STRIP
    xr0, xr1 = BC_RUN
    return [(xs0 - clr, xs1 + clr, yb, yt), (min(xs0, xr0) - clr, max(xs1, xr1) + clr, yj, yb),
            (xr0 - clr, xr1 + clr, min(yc, yj), max(yc, yj))]


def back_shape(inset=0.0, lift=0.0):
    """The remote's back (flat pad, quarter-circle round-over, straight sides) inset by `inset` all
    round and raised by `lift`. Below the curve's 45 deg point the round-over is replaced by its
    45 deg tangent (a frustum), so the cover prints back down without supports."""
    n = bilresa.N_SECT
    secs = []
    for i in range(n // 2, n + 1):                        # from the 45 deg point up
        t = (pi / 2) * i / n
        run = B_BACK_RUN * (1 - sin(t)) + inset
        secs.append(Plane.XY.offset(lift + B_BACK_RISE * (1 - cos(t))) * stadium(B_W - 2 * run, B_H - 2 * run))
    w, h = B_W - 2 * inset, B_H - 2 * inset
    zt = EDGE_C / 2                                       # height of the 45 deg point (n even)
    frustum = chamfer(slab(stadium(w, h), lift, lift + B_SEAM_Z).edges().group_by(Axis.Z)[0], EDGE_C)
    frustum &= Pos(0, 0, lift + zt / 2) * Box(B_W + 2, B_H + 2, zt)
    top = slab(stadium(w, h), lift + B_BACK_RISE - 0.01, lift + B_SEAM_Z + 5)
    return frustum + loft(secs, ruled=False) + top


def outer():
    return back_shape() & Pos(0, 0, B_SEAM_Z / 2) * Box(B_W + 2, B_H + 2, B_SEAM_Z)


def shell():
    """Cover shell: back_shape hollowed by BC_WALL (inset sideways and raised), open at the seam."""
    return outer() - back_shape(BC_WALL, BC_WALL)


def corner_cuts():
    """45 deg prisms removing the end section's lower outer corners (flex outline follows)."""
    out = None
    yc = copper_y()
    for sx in (-1, 1):
        xo = BC_CELL_X + BC_CONTACT_W / 2 + 0.5
        c = Pos(sx * xo, yc, BC_FLEX_Z) * Rot(0, 45, 0) * Box(BC_END_CORNER * sqrt(2), 10, BC_END_CORNER * sqrt(2))
        out = c if out is None else out + c
    return out


def latches():
    """Snap clips at both ends (x = 0): columns standing on the shell's curved inner surface (fused into it at the
    base, a gap to the end wall above it), tops BC_LATCH_TOPS above the inside floor, a hook at the tip pointing
    inwards over the housing's wall (45 deg top, so the cover prints back down without supports)."""
    from build123d import Polyline, Plane, extrude, make_face
    out = None
    yc = B_H / 2 - BC_LATCH_IN                          # clip centre line (outwards distance from the remote centre)
    t, h = BC_LATCH_T, BC_LATCH_HOOK
    yi, yo = yc - t / 2, yc + t / 2                     # clip faces (inner, outer)
    for s, top_in in ((-1, BC_LATCH_TOPS[0]), (1, BC_LATCH_TOPS[1])):
        top = BC_WALL + top_in
        pts = [(yi, 0.3), (yo, 0.3), (yo, top), (yi - h, top - h), (yi - h, top - 2 * h), (yi, top - 3 * h), (yi, 0.3)]
        prof = extrude(Plane.YZ * make_face(Polyline(*pts)), BC_LATCH_W / 2, both=True)   # profile y / z, along x
        prof &= back_shape(0.0, 0.0)                    # not through the outside
        e = prof if s > 0 else prof.mirror(Plane.XZ)
        out = e if out is None else out + e
    return out


def side_tabs():
    """Free-standing ribs at mid-length, BC_SIDE_TAB_GAP apart on their inner faces, from the shell's curved floor up
    to just below the rim (no hook): they keep the sides from flexing."""
    w, t, rise = BC_SIDE_TAB
    x0 = BC_SIDE_TAB_GAP / 2                            # rib's inner face
    z0, z1 = 0.5, BC_WALL + rise                        # from inside the shell (fuses with it), top above the floor
    out = None
    for s in (1, -1):
        tab = Pos(s * (x0 + t / 2), 0, (z0 + z1) / 2) * Box(t, w, z1 - z0)
        out = tab if out is None else out + tab
    out &= back_shape(0.0, 0.0) + Pos(0, 0, 50 + B_SEAM_Z - 0.01) * Box(200, 200, 100)   # not through the outside
    return out


def cover():
    """Printed cover: shell, flex ledge, contact blocks, finger windows, steel-plate pocket, snap ears, side tabs."""
    body = shell()
    yc, ys = copper_y(), stiffener_y()
    for x0, x1, y0, y1 in strip_boxes():
        body += Pos((x0 + x1) / 2, (y0 + y1) / 2, (BC_WALL + BC_FLEX_Z) / 2 - 0.25) * Box(x1 - x0, y1 - y0,
                                                                                       BC_FLEX_Z - BC_WALL + 0.5)
    for a, b, z0, z1 in end_blocks()[:2]:
        yb = ys - BC_TERM_Y * BC_BLOCK_T / 2
        body += Pos((a + b) / 2, yb, (BC_WALL + z1) / 2 - 0.25) * Box(b - a, BC_BLOCK_T, z1 - BC_WALL + 0.5)
    body += end_retainers()
    # slot under the GND contact block for the run (the flex slides in from the cell side)
    xr0, xr1 = BC_RUN
    yb = ys - BC_TERM_Y * BC_BLOCK_T / 2
    body -= Pos((xr0 + xr1) / 2, yb, BC_FLEX_Z + (FLEX_T + 0.08) / 2) * Box(xr1 - xr0 + 0.3, BC_BLOCK_T + 1.0,
                                                                            FLEX_T + 0.08)
    for x0, x1, y0, y1 in strip_boxes(0.1):               # relief over the flex where the 45 deg fill reaches it
        body -= Pos((x0 + x1) / 2, (y0 + y1) / 2, BC_FLEX_Z + (FLEX_T + 0.3) / 2) * Box(x1 - x0, y1 - y0, FLEX_T + 0.3)
    body &= Pos(0, 0, 50) * Box(200, 200, 100)                             # nothing below the back face
    body &= outer() + Pos(0, 0, 50 + B_SEAM_Z - 0.01) * Box(200, 200, 100)  # blocks may rise above the seam
    body += latches() + side_tabs()
    w, d = BC_PRY                                       # flat-blade screwdriver notch in the rim at the bottom end
    body -= Pos(0, -B_H / 2, B_SEAM_Z - d / 2 + 0.01) * Box(w, 2 * (BC_WALL + 1.0), d + 0.02)
    for x, y in BC_FINGERS:
        body -= Pos(x, y, BC_FLEX_Z / 2) * Box(FINGER[0] + 2 * BC_WIN_CLR, FINGER[1] + 2 * BC_WIN_CLR, BC_FLEX_Z + 1.0)
    cw, ct, ch, cg = BC_STEEL_CLIP
    ext = 0.15 + ct + cg                                 # pocket longer at both ends for the clips
    body -= Pos(0, BC_STEEL_Y, BC_STEEL_FLOOR + 5.0) * Box(BC_STEEL[0] + 0.3, BC_STEEL[1] + 0.3 + 2 * ext, 10.0)
    body += steel_clips() + pegs()
    x0, x1, y0, y1 = BC_REG_RECESS
    body -= Pos((x0 + x1) / 2, (y0 + y1) / 2, (BC_STEEL_FLOOR + BC_FLEX_Z) / 2) * Box(x1 - x0, y1 - y0,
                                                                                      BC_FLEX_Z - BC_STEEL_FLOOR)
    return body


def pegs():
    """Heat-stake pegs on the ledge through the flex and its pad-section stiffener (melted over at assembly)."""
    from build123d import Cylinder
    z0, z1 = BC_FLEX_Z - 0.3, BC_FLEX_Z + FLEX_T + BC_PAD_STIFF_T + BC_PEG_STAKE
    out = None
    for x, y in BC_PEGS:
        p = Pos(x, y, (z0 + z1) / 2) * Cylinder(BC_PEG_D / 2, z1 - z0)
        out = p if out is None else out + p
    return out


def peg_holes(z0, z1):
    from build123d import Cylinder
    out = None
    for x, y in BC_PEGS:
        h = Pos(x, y, (z0 + z1) / 2) * Cylinder(BC_PEG_HOLE / 2, z1 - z0)
        out = h if out is None else out + h
    return out


def pad_stiffener():
    """FR4 on the flex's pad and regulator sections (non-copper side), with the peg holes."""
    z0 = BC_FLEX_Z + FLEX_T
    out = None
    for x0, x1, y0, y1 in strip_boxes()[:2]:
        s = Pos((x0 + x1) / 2, (y0 + y1) / 2, z0 + BC_PAD_STIFF_T / 2) * Box(x1 - x0, y1 - y0, BC_PAD_STIFF_T)
        out = s if out is None else out + s
    return out - peg_holes(z0 - 0.1, z0 + BC_PAD_STIFF_T + 0.1)


def end_retainers():
    """End section retention on each contact block: a lip in front of its foot (the section's lower edge drops into
    the slot between lip and stiffener) and a hook on its top over the section's top edge (snaps in, 45 deg lead-in;
    printed back down: the hook's underside is the only overhang, BC_END_HOOK wide)."""
    from build123d import Polyline, Plane, extrude, make_face
    t, h, gap = BC_END_LIP
    yc = copper_y()
    sy = -BC_TERM_Y                                      # +1: cells side (blocks) is +y
    ys = stiffener_y()                                   # stiffener's far face (the blocks start here)
    out = None
    for a, b, z0, z1 in end_blocks()[:2]:
        a2, b2 = a + 0.5, b - 1.6                        # clear of the 45 deg corner cut and the notch side
        y_l0, y_l1 = yc - sy * gap, yc - sy * (gap + t)  # lip faces
        lip = Pos((a2 + b2) / 2, (y_l0 + y_l1) / 2, (BC_WALL + BC_FLEX_Z + h) / 2) * Box(
            b2 - a2, t, BC_FLEX_Z + h - BC_WALL)
        # hook: from the block's top over the stiffener and flex to the copper face, lead-in on top
        y_b, y_f = ys, yc - sy * BC_END_HOOK
        hk = BC_END_HOOK
        pts = [(y_b + sy * 0.5, z1), (y_b + sy * 0.5, z1 + 1.2), (y_f, z1 + 0.2 + hk), (y_f, z1), (y_b + sy * 0.5, z1)]
        prof = extrude(Plane.YZ * make_face(Polyline(*pts)), (b2 - a2) / 2, both=True)
        part = lip + Pos((a2 + b2) / 2, 0, 0) * prof
        out = part if out is None else out + part
    return out


def flex():
    """The flex in place (FLEX_T thick): pad section and strip on the ledge, end section up the blocks."""
    yc = copper_y()
    yf = yc - BC_TERM_Y * FLEX_T / 2
    out = None
    for x0, x1, y0, y1 in strip_boxes():
        b = Pos((x0 + x1) / 2, (y0 + y1) / 2, Z_BEND) * Box(x1 - x0, y1 - y0, FLEX_T)
        out = b if out is None else out + b
    for a, b, z0, z1 in end_blocks():
        out += Pos((a + b) / 2, yf, (z0 + z1) / 2) * Box(b - a, FLEX_T, z1 - z0)
    return out - corner_cuts() - peg_holes(BC_FLEX_Z - 0.1, BC_FLEX_Z + FLEX_T + 0.1)


def stiffener():
    ys = copper_y() - BC_TERM_Y * (FLEX_T + BC_END_T / 2)
    out = None
    for a, b, z0, z1 in end_blocks():
        s = Pos((a + b) / 2, ys, (z0 + z1) / 2) * Box(b - a, BC_END_T, z1 - z0)
        out = s if out is None else out + s
    return out - corner_cuts()


def pads():
    """The contact fingers' solder pads on the end section's copper face."""
    yc = copper_y()
    out = None
    for sx in (-1, 1):
        p = Pos(sx * BC_CELL_X, yc + BC_TERM_Y * 0.01, BC_CELL_Z) * Box(FINGER_PAD[1], 0.02, FINGER_PAD[0])
        out = p if out is None else out + p
    return out


def end_fingers(h=FINGER_WH):
    """S7081-42R on the end section at the cell axes, domes towards the terminals; long axis vertical with the
    bend end up, so the battery contacts ride down the arm's ramp onto the dome as the cover goes on."""
    out = None
    for sx in (-1, 1):
        f = Pos(sx * BC_CELL_X, copper_y(), BC_CELL_Z) * Rot(90 * BC_TERM_Y, 0, 0) * finger(h)
        out = f if out is None else out + f
    return out


def finger(h):
    """One S7081-42R (drawing iss. 7) hanging from the flex underside at height h: foot on the flex,
    arm down from the bend end, contact dome at the bottom. Local: long axis y, origin at the body centre."""
    foot = Pos(0, 0, -0.075) * Box(FINGER[0], FINGER[1], 0.15)
    yb = -FINGER[1] / 2 + 0.3                             # bend end
    yd = BC_DOME_DY                                       # dome
    run, drop = yd - yb, h - 0.15 - 0.33
    length = sqrt(run * run + drop * drop)
    ang = degrees(atan2(drop, run))
    arm = Pos(0, (yb + yd) / 2, -0.15 - drop / 2) * Rot(-ang, 0, 0) * Box(FINGER[0] - 0.4, length, 0.15)
    dome = Pos(0, yd, -h + 0.33 / 2) * Cylinder(1.3 / 2, 0.33)
    return foot + arm + dome


def fingers(h=FINGER_WH):
    out = None
    for x, y in BC_FINGERS:
        f = Pos(x, y, BC_FLEX_Z) * finger(h)
        out = f if out is None else out + f
    return out


def regulator():
    """TLV75533 and its two capacitors hanging from the flex underside (copper down) into the recess."""
    out = None
    for ref, (x, y) in BC_REG.items():
        w, h, t = BC_REG_BODY if ref == "U1" else BC_CAP0402
        p = Pos(x, y, BC_FLEX_Z - t / 2) * Box(w, h, t)
        out = p if out is None else out + p
    return out


def steel_clips():
    """A clip at each end of the steel plate: a tab from the pocket floor beside the plate's end (a gap behind it to
    flex), a hook over the plate's edge with a 45 deg lead-in on top, so the plate snaps in from above."""
    from build123d import Polyline, Plane, extrude, make_face
    cw, ct, ch, cg = BC_STEEL_CLIP
    z0, zh = BC_STEEL_FLOOR, BC_STEEL_FLOOR + BC_STEEL[2] + 0.1           # pocket floor, hook underside
    out = None
    for s in (1, -1):
        ye = BC_STEEL[1] / 2 + 0.15                     # tab inner face, outwards distance from the plate centre
        pts = [(ye, z0 - 0.01), (ye + ct, z0 - 0.01), (ye + ct, zh + 2 * ch), (ye - ch, zh + ch), (ye - ch, zh),
               (ye, zh), (ye, z0 - 0.01)]
        prof = extrude(Plane.YZ * make_face(Polyline(*pts)), cw / 2, both=True)
        c = Pos(0, BC_STEEL_Y, 0) * (prof if s > 0 else prof.mirror(Plane.XZ))
        out = c if out is None else out + c
    return out


def steel():
    return Pos(0, BC_STEEL_Y, BC_STEEL_FLOOR + BC_STEEL[2] / 2 + 0.01) * Box(*BC_STEEL)


def cover_parts(free=False):
    """The cover assembly in remote coordinates (fingers free or at working height)."""
    h = FINGER_FREE if free else FINGER_WH
    return {"cover": cover(), "flex": flex(), "stiffener": stiffener(), "pads": pads(),
            "fingers": fingers(h), "contacts": end_fingers(h), "regulator": regulator(), "steel": steel(),
            "pad_stiffener": pad_stiffener()}


def tongue_path(wall_x):
    """Sensor-flex tongue in the floor insert: (x0, x1, y0, y1, layers) boxes. It enters along y =
    BC_TONGUE_Y from the right channel (copper down, as the flex's pin pads), folds 45 deg under the
    pads' column (copper up) and runs up past both pads."""
    w = BC_TONGUE_W
    xf = BC_FINGERS[0][0]
    ys = [y for _, y in BC_FINGERS]
    y_top = max(ys) + BC_FLOOR_PAD[1] / 2 + 1.0
    run = (xf + w / 2, wall_x, BC_TONGUE_Y - w / 2, BC_TONGUE_Y + w / 2, 1)
    fold = (xf - w / 2, xf + w / 2, BC_TONGUE_Y - w / 2, BC_TONGUE_Y + w / 2, 2)
    up = (xf - w / 2, xf + w / 2, BC_TONGUE_Y + w / 2, y_top, 1)
    return [run, fold, up]


def floor_insert(pocket_in, wall_x, cutouts=(), path=None, pads=None):
    """Pocket-floor insert (face plate side), z = 0 its underside: printed floor with the tongue's
    recess, the tongue, its flush pads. cutouts: (x, y, w, h) openings (switch, trim tabs, bosses),
    each with BC_FLOOR_CLR all round. path: the tongue's (x0, x1, y0, y1, layers) boxes on the floor
    (default: tongue_path(wall_x)). pads: (x0, x1, y0, y1) of the flush pads (default: BC_FLOOR_PAD under the
    fingers)."""
    w, h = pocket_in[0] - 2 * BC_FLOOR_CLR, pocket_in[1] - 2 * BC_FLOOR_CLR
    plate = slab(stadium(w, h), 0, BC_FLOOR_T)
    for x, y, cw, ch in cutouts:
        plate -= Pos(x, y, BC_FLOOR_T / 2) * Box(cw + 2 * BC_FLOOR_CLR, ch + 2 * BC_FLOOR_CLR, BC_FLOOR_T + 1)
    tongue = None
    for x0, x1, y0, y1, n in (path or tongue_path(wall_x)):
        d = n * FLEX_T
        rec = Pos((x0 + x1) / 2, (y0 + y1) / 2, BC_FLOOR_T - (d + BC_RECESS_CLR) / 2 + 0.005) * \
            Box(x1 - x0 + 0.3, y1 - y0 + 0.3 * (n == 1), d + BC_RECESS_CLR + 0.01)
        plate -= rec
        t = Pos((x0 + x1) / 2, (y0 + y1) / 2, BC_FLOOR_T - d / 2) * Box(x1 - x0, y1 - y0, d)
        tongue = t if tongue is None else tongue + t
    pd = None
    for x0, x1, y0, y1 in (pads or [(x - BC_FLOOR_PAD[0] / 2, x + BC_FLOOR_PAD[0] / 2, y - BC_FLOOR_PAD[1] / 2,
                                      y + BC_FLOOR_PAD[1] / 2) for x, y in BC_FINGERS]):
        p = Pos((x0 + x1) / 2, (y0 + y1) / 2, BC_FLOOR_T + 0.005) * Box(x1 - x0, y1 - y0, 0.01)
        pd = p if pd is None else pd + p
    return {"floor": plate, "floor_flex": tongue, "floor_pads": pd}


def remote_front():
    """The remote above its parting line (its own back cover removed), z = 0 its back face."""
    r = Pos(0, 0, -SEAT_Z) * bilresa.build()
    r &= Pos(0, 0, 50 + B_SEAM_Z) * Box(200, 200, 100)
    return r


if __name__ == "__main__":
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[2] / "build"
    out.mkdir(exist_ok=True)
    c = cover()
    print("cover valid:", c.is_valid, "solids:", len(c.solids()), f"volume {c.volume / 1000:.2f} cm3")
    export_step(c, str(out / "back_cover.step"))
    export_stl(c, str(out / "back_cover.stl"))
