"""Generate kicad/wiring_board.kicad_pcb with the KiCad 9 pcbnew API.

Run with the Python that ships pcbnew. Board centre sits at page (100, 100) mm; the
aux and grid origins are set there, so exports use board-centre coordinates (X right, Y up).
"""
import datetime
import math
from pathlib import Path
import pcbnew as P
from parts import (VIAS, PARTS, LIB, PROJECT, uid, BOARD, PS1_PINS, NETCLASS, RING_OUTER, RING_INNER,
                   SELV_ZONE, POURS, POUR_PRIO, PE_ARMS, TRACKS, REV, MOUNT, MOUNT_KO, PE_DETOURS, PE_DETOUR_W, FP_MH, LOGOS, URL, URL_POS)

PRJ = Path(__file__).resolve().parents[1] / "kicad"
OX, OY = 100.0, 100.0
DATE = datetime.date.today().isoformat()
NETNAME = {n: f"/{n}" for n in ("L_IN", "L_SW", "L_F", "N_IN", "N_SW", "PE")}
NETNAME.update({"+5V": "+5V", "GND": "GND", "NC5": "unconnected-(PS1-NC-Pad5)"})
LAYERS = {"F.Cu": P.F_Cu, "B.Cu": P.B_Cu, "F.SilkS": P.F_SilkS, "B.SilkS": P.B_SilkS,
          "Edge.Cuts": P.Edge_Cuts}


def V(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY - y))


def mm(v):
    return P.ToMM(v.x) - OX, OY - P.ToMM(v.y)


board = P.BOARD()
ds = board.GetDesignSettings()
ds.SetAuxOrigin(V(0, 0))
ds.SetGridOrigin(V(0, 0))
ds.SetBoardThickness(P.FromMM(BOARD["t"]))
board.SetCopperLayerCount(2)
ds.m_MinClearance = P.FromMM(0.2)
ds.m_TrackMinWidth = P.FromMM(0.2)
ds.m_CopperEdgeClearance = P.FromMM(0.5)
ds.m_HoleClearance = P.FromMM(0.25)
ds.m_HoleToHoleMin = P.FromMM(0.5)
ds.m_MinThroughDrill = P.FromMM(0.3)
ds.m_ViasMinSize = P.FromMM(0.6)
ds.m_ViasMinAnnularWidth = P.FromMM(0.15)

nset = ds.m_NetSettings
widths = {"Mains_L": 1.5, "Mains_N": 1.5, "PE": 2.0, "SELV": 0.8}
for prio, (cls, nets) in enumerate(NETCLASS.items()):
    nc = P.NETCLASS(cls)
    nc.SetTrackWidth(P.FromMM(widths[cls]))
    nc.SetClearance(P.FromMM(0.2))
    nc.SetPriority(prio)
    nset.SetNetclass(cls, nc)
    for n in nets:
        nset.SetNetclassPatternAssignment(NETNAME[n], cls)


# ---------------- outline with the slot notch from the bottom edge ----------------
def seg(a, b, lay="Edge.Cuts", w=0.05):
    s = P.PCB_SHAPE(board, P.SHAPE_T_SEGMENT)
    s.SetStart(V(*a))
    s.SetEnd(V(*b))
    s.SetLayer(LAYERS[lay])
    s.SetWidth(P.FromMM(w))
    board.Add(s)


def arc(a, m, b, lay="Edge.Cuts", w=0.05):
    s = P.PCB_SHAPE(board, P.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*m), V(*b))
    s.SetLayer(LAYERS[lay])
    s.SetWidth(P.FromMM(w))
    board.Add(s)


W, H, R = BOARD["w"] / 2, BOARD["h"] / 2, BOARD["r"]
sx0, sx1, stop = BOARD["slot"]
sr = (sx1 - sx0) / 2
k = R * (1 - 1 / math.sqrt(2))
seg((-W + R, -H), (sx0, -H))
seg((sx0, -H), (sx0, stop - sr))
arc((sx0, stop - sr), ((sx0 + sx1) / 2, stop), (sx1, stop - sr))
seg((sx1, stop - sr), (sx1, -H))
seg((sx1, -H), (W - R, -H))
arc((W - R, -H), (W - k, -H + k), (W, -H + R))
seg((W, -H + R), (W, H - R))
arc((W, H - R), (W - k, H - k), (W - R, H))
seg((W - R, H), (-W + R, H))
arc((-W + R, H), (-W + k, H - k), (-W, H - R))
seg((-W, H - R), (-W, -H + R))
arc((-W, -H + R), (-W + k, -H + k), (-W + R, -H))

# ---------------- nets ----------------
nets = {}
for key, name in NETNAME.items():
    n = P.NETINFO_ITEM(board, name)
    board.Add(n)
    nets[key] = n

# ---------------- footprints ----------------
lib_path = str(PRJ / f"{LIB}.pretty")


def set_field(fp, name, value):
    f = fp.GetFieldByName(name)
    if f is None:
        f = P.PCB_FIELD(fp, fp.GetNextFieldId(), name)
        f.SetLayer(P.F_Fab)
        f.SetVisible(False)
        fp.AddField(f)
    f.SetText(value)


def pad_xy(fp, num):
    return mm([q for q in fp.Pads() if q.GetNumber() == num][0].GetPosition())


fps = {}
for ref, p in PARTS.items():
    fp = P.FootprintLoad(lib_path, p["fp"])
    fp.SetFPID(P.LIB_ID(LIB, p["fp"]))
    fp.SetReference(ref)
    fp.SetValue(p["value"])
    fp.SetPath(P.KIID_PATH(f"/{uid('sym', ref)}"))
    fp.SetSheetname("Root")
    fp.SetSheetfile(f"{PROJECT}.kicad_sch")
    for name, val in (("Datasheet", p["ds"]), ("Description", p["desc"]), ("Manufacturer", p["mfr"]),
                      ("MPN", p["mpn"])):
        set_field(fp, name, val)
    board.Add(fp)
    if ref == "PS1":
        # on the back; find the orientation that puts the pins where parts.py wants them
        best = None
        for rot in (0, 90, 180, 270):
            fp.SetOrientationDegrees(0)
            if fp.IsFlipped():
                fp.Flip(fp.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
            fp.SetPosition(V(0, 0))
            fp.SetOrientationDegrees(rot)
            fp.Flip(fp.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
            x1, y1 = pad_xy(fp, "1")
            fp.Move(V(*PS1_PINS["1"]) - V(x1, y1))
            err = max(math.hypot(pad_xy(fp, n)[0] - x, pad_xy(fp, n)[1] - y) for n, (x, y) in PS1_PINS.items())
            if best is None or err < best[1]:
                best = (rot, err)
            if err < 0.01:
                break
        assert best[1] < 0.01, f"PS1 pins cannot be placed as required (best rot {best})"
    else:
        x, y, rot, side = p["pcb"]
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(rot)
        if side == "B":
            fp.Flip(fp.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
    for pad in fp.Pads():
        net = p["nets"].get(pad.GetNumber())
        if net:
            pad.SetNet(nets[net])
    fp.Reference().SetLayer(P.B_Fab if fp.IsFlipped() else P.F_Fab)
    fps[ref] = fp

# logos (board-only footprints, no symbol)
for ref, (name, (x, y), side, rot) in LOGOS.items():
    fp = P.FootprintLoad(lib_path, name)
    fp.SetFPID(P.LIB_ID(LIB, name))
    fp.SetReference(ref)
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    if side == "B":
        fp.Flip(fp.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
    fps[ref] = fp

# mounting holes for the insert's snap posts (board-only footprints, no symbol): unplated
for ref, (x, y) in MOUNT.items():
    fp = P.FootprintLoad(lib_path, FP_MH)
    fp.SetFPID(P.LIB_ID(LIB, FP_MH))
    fp.SetReference(ref)
    fp.SetValue(FP_MH)
    fp.SetPosition(V(x, y))
    fp.Reference().SetLayer(P.F_Fab)
    fp.Value().SetVisible(False)
    board.Add(fp)
    fps[ref] = fp

# J1 pin positions as built (front view) for the README / checks
J1_PADS = sorted({(n.GetNumber(), round(mm(n.GetPosition())[0], 2), round(mm(n.GetPosition())[1], 2))
                  for n in fps["J1"].Pads()})


# ---------------- zones ----------------
ZONE_FILLET = 1.0          # mm, zone outline corner radius
ZONE_MIN_W = 1.0           # mm, minimum fill width; convex fill corners round to half of it


def zone(net, layers, outline, hole=None, prio=0, connection=P.ZONE_CONNECTION_FULL, name=""):
    z = P.ZONE(board)
    ls = P.LSET()
    for lay in layers:
        ls.AddLayer(LAYERS[lay])
    z.SetLayerSet(ls)
    z.SetNet(nets[net])
    z.SetAssignedPriority(prio)
    z.SetPadConnection(connection)
    z.SetMinThickness(P.FromMM(ZONE_MIN_W))
    z.SetLocalClearance(P.FromMM(0.2))
    z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_ALWAYS)
    if name:
        z.SetZoneName(name)
    z.SetCornerSmoothingType(P.ZONE_SETTINGS.SMOOTHING_FILLET)
    z.SetCornerRadius(P.FromMM(ZONE_FILLET))
    o = z.Outline()
    o.NewOutline()
    for pt in outline:
        o.Append(V(*pt))
    if hole:
        h = o.NewHole()
        for pt in hole:
            o.Append(V(*pt), 0, h)
    board.Add(z)
    return z


def circle_pts(c, r, a0=0.0, a1=360.0, n=48):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def keepout(c, r, name):
    """Rule area on both copper layers: no copper of any kind round a mounting hole."""
    z = P.ZONE(board)
    ls = P.LSET()
    ls.AddLayer(P.F_Cu)
    ls.AddLayer(P.B_Cu)
    z.SetLayerSet(ls)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)                 # the hole itself is an NPTH pad
    z.SetDoNotAllowFootprints(False)
    z.SetZoneName(name)
    o = z.Outline()
    o.NewOutline()
    for pt in circle_pts(c, r)[:-1]:
        o.Append(V(*pt))
    board.Add(z)


zone("PE", ["F.Cu", "B.Cu"], RING_OUTER, RING_INNER, prio=5, name="PE ring (AC part)")
for lay, outline in PE_ARMS:
    zone("PE", [lay], outline, prio=6, name=f"PE arm {lay}")   # overlaps the ring: own priority
for ref, (a0, a1) in PE_DETOURS.items():                     # ring detours round MH1, MH3 (inside)
    c = MOUNT[ref]
    outer = circle_pts(c, MOUNT_KO + PE_DETOUR_W, a0, a1, 24)
    inner = circle_pts(c, MOUNT_KO - 0.1, a1, a0, 24)
    zone("PE", ["F.Cu", "B.Cu"], outer + inner, prio=6, name=f"PE detour {ref}")
for ref, c in MOUNT.items():
    keepout(c, MOUNT_KO, f"no copper under the {ref} post")
zone("GND", ["F.Cu"], SELV_ZONE, prio=4, connection=P.ZONE_CONNECTION_THERMAL, name="5 V side")
for net, lay, outline in POURS:
    zone(net, [lay], outline, prio=POUR_PRIO[net], name=f"{net} pour")


# ---------------- PE stitching vias along the ring centre line ----------------
def ring_centre():
    return [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(RING_OUTER, RING_INNER)]


pts = ring_centre()
pts.append(pts[0])
for a, b in zip(pts, pts[1:]):
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(length // 4.0))
    for i in range(n):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if any(math.hypot(x - mx, y - my) < MOUNT_KO + 0.4 + 0.2 for mx, my in MOUNT.values()):
            continue                      # no vias in the keep-out round the mounting holes
        v = P.PCB_VIA(board)
        v.SetPosition(V(x, y))
        v.SetWidth(P.FromMM(0.8))
        v.SetDrill(P.FromMM(0.4))
        v.SetNet(nets["PE"])
        board.Add(v)

for net, pts in VIAS.items():
    for x, y in pts:
        v = P.PCB_VIA(board)
        v.SetPosition(V(x, y))
        v.SetWidth(P.FromMM(1.0))
        v.SetDrill(P.FromMM(0.5))
        v.SetNet(nets[net])
        board.Add(v)

# ---------------- tracks (bends filleted with tangent arcs) ----------------
def fillet_path(pts, w):
    """Turn a polyline into straight pieces and tangent arcs.

    Returns a list of ("seg", a, b) and ("arc", a, mid, b). The radius is 2 x the track
    width (at least 1.5 mm), reduced so each tangent point stays within 45 % of its
    neighbouring segments.
    """
    out, start = [], pts[0]
    for p0, p1, p2 in zip(pts, pts[1:], pts[2:]):
        ux, uy = p1[0] - p0[0], p1[1] - p0[1]
        vx, vy = p2[0] - p1[0], p2[1] - p1[1]
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        ux, uy, vx, vy = ux / lu, uy / lu, vx / lv, vy / lv
        turn = math.acos(max(-1.0, min(1.0, ux * vx + uy * vy)))
        if turn < math.radians(2):
            continue                      # straight through: no corner to round
        r = max(2 * w, 1.5)
        tan_len = r * math.tan(turn / 2)
        limit = 0.45 * min(lu, lv)
        if tan_len > limit:
            tan_len, r = limit, limit / math.tan(turn / 2)
        a = (p1[0] - ux * tan_len, p1[1] - uy * tan_len)
        b = (p1[0] + vx * tan_len, p1[1] + vy * tan_len)
        bx, by = vx - ux, vy - uy         # bisector towards the centre of the turn
        bl = math.hypot(bx, by)
        dist = r / math.cos(turn / 2)
        c = (p1[0] + bx / bl * dist, p1[1] + by / bl * dist)
        mx, my = p1[0] - c[0], p1[1] - c[1]
        ml = math.hypot(mx, my)
        mid = (c[0] + mx / ml * r, c[1] + my / ml * r)
        out.append(("seg", start, a))
        out.append(("arc", a, mid, b))
        start = b
    out.append(("seg", start, pts[-1]))
    return out


for net, polys in TRACKS.items():
    for lay, w, pts in polys:
        for piece in fillet_path(pts, w):
            if piece[0] == "seg":
                _, a, b = piece
                if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-3:
                    continue
                t = P.PCB_TRACK(board)
                t.SetStart(V(*a))
                t.SetEnd(V(*b))
            else:
                _, a, m, b = piece
                t = P.PCB_ARC(board)
                t.SetStart(V(*a))
                t.SetMid(V(*m))
                t.SetEnd(V(*b))
            t.SetWidth(P.FromMM(w))
            t.SetLayer(LAYERS[lay])
            t.SetNet(nets[net])
            board.Add(t)

# ---------------- silkscreen ----------------
def text(s, x, y, lay="F.SilkS", size=1.0, th=0.15):
    t = P.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(V(x, y))
    t.SetLayer(LAYERS[lay])
    t.SetTextSize(P.VECTOR2I(P.FromMM(size), P.FromMM(size)))
    t.SetTextThickness(P.FromMM(th))
    if lay.startswith("B."):
        t.SetMirrored(True)
    board.Add(t)


# back face (installer side): terminal labels just below the block body (body ends at Y -3.0)
for num, label in (("1", "PE"), ("2", "N SW"), ("3", "N IN"), ("4", "L SW"), ("5", "L IN"), ("6", "PE")):
    x = [mm(q.GetPosition())[0] for q in fps["J1"].Pads() if q.GetNumber() == num][0]
    text(label, x, -7.0, "B.SilkS", 0.8, 0.12)
text("MAINS 270 VAC MAX", -9.0, 29.2, "B.SilkS", 1.0)
text("LOAD: L SW / N SW", 0.0, 16.2, "B.SilkS", 0.8, 0.12)
text(f"wiring_board {REV}", -9.0, 31.0, "B.SilkS", 1.0)
# front face
text("+5V  GND", 12.7, -32.7, "F.SilkS", 0.8, 0.12)
text(DATE, 11.0, 27.5, "B.SilkS", 0.8, 0.12)
text(URL, URL_POS[0], URL_POS[1], f"{URL_POS[2]}.SilkS", 0.8, 0.12)

# part labels: reference + maker / model on each part's side (pcb/tools/kigen.py)
import kigen
kigen.place_labels(board, [(fps[r], t) for r, t in ((r, kigen.label_text(r, p)) for r, p in PARTS.items())
                           if t and r in fps])

# ---------------- fill and save ----------------
out = PRJ / f"{PROJECT}.kicad_pcb"
P.SaveBoard(str(out), board)

# filling an in-memory board crashes in KiCad 9; reload from disk, then fill
filled = P.LoadBoard(str(out))
filled.BuildConnectivity()
P.ZONE_FILLER(filled).Fill(filled.Zones())
P.SaveBoard(str(out), filled)
print("wrote", out)


def pe_continuous(brd, layer):
    """PE copper on one layer alone (zones, tracks, the terminal's THT pads; no vias, no hole
    copper): do all PE pins of J1 (J1.1 and J1.6, both rows) lie in one piece?"""
    u = P.SHAPE_POLY_SET()
    for z in brd.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == NETNAME["PE"] and z.IsOnLayer(layer):
            u.BooleanAdd(z.GetFilledPolysList(layer))
    for t in brd.GetTracks():
        if t.GetNetname() == NETNAME["PE"] and t.GetClass() != "PCB_VIA" and t.GetLayer() == layer:
            sh = P.SHAPE_POLY_SET()
            t.TransformShapeToPolygon(sh, layer, 0, P.FromMM(0.005), P.ERROR_INSIDE)
            u.BooleanAdd(sh)
    term = [pd for fp in brd.GetFootprints() if fp.GetReference() == "J1" for pd in fp.Pads()
            if pd.GetNetname() == NETNAME["PE"]]
    for pd in term:
        sh = P.SHAPE_POLY_SET()
        pd.TransformShapeToPolygon(sh, layer, 0, P.FromMM(0.005), P.ERROR_INSIDE)
        u.BooleanAdd(sh)
    u.Simplify()
    where = [{i for i in range(u.OutlineCount()) if u.Outline(i).PointInside(pd.GetPosition())} for pd in term]
    nums = {pd.GetNumber() for pd in term}
    return nums == {"1", "6"} and bool(set.intersection(*where))      # every PE pin (both rows) in one piece


ok_f = pe_continuous(filled, P.F_Cu)
print("PE J1.1 - J1.6 on F.Cu alone (no vias, no hole copper):", "continuous" if ok_f else "BROKEN")
print("PE J1.1 - J1.6 on B.Cu alone (parallel ring, joined to J1.6 by the vias):",
      "continuous" if pe_continuous(filled, P.B_Cu) else "not continuous")
if not ok_f:
    raise SystemExit("PE continuity on F.Cu must not depend on vias or mounting-hole copper")
print("J1 pads (num, X, Y):", J1_PADS)
for n in ("1", "3", "5", "14", "16"):
    print(f"PS1.{n} at", tuple(round(c, 2) for c in pad_xy(fps["PS1"], n)))
for ref in ("S1", "F1", "RV1", "C1", "J2"):
    print(ref, [(q.GetNumber(), tuple(round(c, 2) for c in mm(q.GetPosition()))) for q in fps[ref].Pads()])
