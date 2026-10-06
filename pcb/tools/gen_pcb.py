"""Generate pcb/kicad/psu_carrier.kicad_pcb with the KiCad 9 pcbnew API.

Run with the system python that ships pcbnew:  python3 pcb/tools/gen_pcb.py
Board centre sits at page (100, 100) mm; aux (drill/place) and grid origins
are set there, so exports use board-centre coordinates (X right, Y up).
"""
import datetime, math
from pathlib import Path
import pcbnew as P
from parts import PARTS, LIB, uid, BOARD, PS1_PINS, PS1_ROT, TRACKS, REV, PRIMARY, SECONDARY

PRJ = Path(__file__).resolve().parents[1] / "kicad"
OX, OY = 100.0, 100.0
DATE = datetime.date.today().isoformat()
NETNAME = {"L_IN": "/L_IN", "L_F": "/L_F", "N": "/N", "+5V": "+5V", "GND": "GND",
           "NC5": "unconnected-(PS1-NC-Pad5)"}


def V(x, yup):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY - yup))


def layer(name):
    return {"F.Cu": P.F_Cu, "B.Cu": P.B_Cu, "F.SilkS": P.F_SilkS, "B.SilkS": P.B_SilkS,
            "Edge.Cuts": P.Edge_Cuts, "F.Fab": P.F_Fab, "Cmts.User": P.Cmts_User}[name]


board = P.BOARD()
ds = board.GetDesignSettings()
ds.SetAuxOrigin(V(0, 0))
ds.SetGridOrigin(V(0, 0))
ds.SetBoardThickness(P.FromMM(BOARD["t"]))
board.SetCopperLayerCount(2)
# PCBWay standard-process minimums (with margin)
ds.m_MinClearance = P.FromMM(0.2)
ds.m_TrackMinWidth = P.FromMM(0.2)
ds.m_CopperEdgeClearance = P.FromMM(0.5)
ds.m_HoleClearance = P.FromMM(0.25)
ds.m_HoleToHoleMin = P.FromMM(0.5)
ds.m_MinThroughDrill = P.FromMM(0.3)
ds.m_ViasMinSize = P.FromMM(0.6)
ds.m_ViasMinAnnularWidth = P.FromMM(0.15)

# netclasses (Primary = mains side, Secondary = 5 V side); DRC rules in psu_carrier.kicad_dru
nset = ds.m_NetSettings
for name, tw, cl, prio in (("Primary", 1.2, 0.5, 0), ("Secondary", 0.6, 0.2, 1)):
    nc = P.NETCLASS(name)
    nc.SetTrackWidth(P.FromMM(tw)); nc.SetClearance(P.FromMM(cl)); nc.SetPriority(prio)
    nset.SetNetclass(name, nc)
for pat in PRIMARY:
    nset.SetNetclassPatternAssignment(f"/{pat}", "Primary")
for pat in SECONDARY:
    nset.SetNetclassPatternAssignment(pat, "Secondary")

# ---------------- outline (with isolation slot notch from the top edge) ----------------
W, H, R = BOARD["w"] / 2, BOARD["h"] / 2, BOARD["r"]
sx0, sx1 = BOARD["slot_x"]
sb = BOARD["slot_bottom"]
sr = (sx1 - sx0) / 2


def seg(a, b, lay="Edge.Cuts", w=0.05):
    s = P.PCB_SHAPE(board, P.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(layer(lay)); s.SetWidth(P.FromMM(w))
    board.Add(s)


def arc(a, m, b, lay="Edge.Cuts", w=0.05):
    s = P.PCB_SHAPE(board, P.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*m), V(*b)); s.SetLayer(layer(lay)); s.SetWidth(P.FromMM(w))
    board.Add(s)


k = R * (1 - 1 / math.sqrt(2))
seg((-W + R, H), (sx0, H))
seg((sx0, H), (sx0, sb + sr))
arc((sx0, sb + sr), ((sx0 + sx1) / 2, sb), (sx1, sb + sr))
seg((sx1, sb + sr), (sx1, H))
seg((sx1, H), (W - R, H))
arc((W - R, H), (W - k, H - k), (W, H - R))
seg((W, H - R), (W, -H + R))
arc((W, -H + R), (W - k, -H + k), (W - R, -H))
seg((W - R, -H), (-W + R, -H))
arc((-W + R, -H), (-W + k, -H + k), (-W, -H + R))
seg((-W, -H + R), (-W, H - R))
arc((-W, H - R), (-W + k, H - k), (-W + R, H))

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


fps = {}
for ref, p in PARTS.items():
    fp = P.FootprintLoad(lib_path, p["fp"])
    fp.SetFPID(P.LIB_ID(LIB, p["fp"]))
    fp.SetReference(ref)
    fp.SetValue(p["value"])
    fp.SetPath(P.KIID_PATH(f"/{uid('sym', ref)}"))
    fp.SetSheetname("Root")
    fp.SetSheetfile("psu_carrier.kicad_sch")
    set_field(fp, "Datasheet", p["ds"])
    set_field(fp, "Description", p["desc"])
    set_field(fp, "Manufacturer", p["mfr"])
    set_field(fp, "MPN", p["mpn"])
    board.Add(fp)
    if ref == "PS1":
        fp.SetOrientationDegrees(PS1_ROT)
        fp.SetPosition(V(0, 0))
        pad1 = [q for q in fp.Pads() if q.GetNumber() == "1"][0].GetPosition()
        tx, ty = PS1_PINS["1"]
        fp.Move(V(tx, ty) - pad1)
    else:
        x, y, rot = p["pcb"]
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(V(x, y))
    for pad in fp.Pads():
        net = p["nets"].get(pad.GetNumber())
        if net:
            pad.SetNet(nets[net])
    fps[ref] = fp

# verify PS1 landed where the CAD/SPEC expects
for num, (x, y) in PS1_PINS.items():
    pos = [q for q in fps["PS1"].Pads() if q.GetNumber() == num][0].GetPosition()
    px, py = P.ToMM(pos.x) - OX, OY - P.ToMM(pos.y)
    assert abs(px - x) < 0.01 and abs(py - y) < 0.01, f"PS1 pin {num} at {px:.2f},{py:.2f}"

# reference designators: keep on F.Fab (silk is crowded); body outlines remain on silk
for fp in fps.values():
    fp.Reference().SetLayer(P.F_Fab)

# ---------------- tracks ----------------
for net, polys in TRACKS.items():
    for lay, w, pts in polys:
        for a, b in zip(pts, pts[1:]):
            t = P.PCB_TRACK(board)
            t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(P.FromMM(w))
            t.SetLayer(layer(lay)); t.SetNet(nets[net])
            board.Add(t)

# ---------------- rule areas (keep-outs) ----------------


def keepout(name, x0, y0, x1, y1, footprints):
    z = P.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    ls = P.LSET(); ls.AddLayer(P.F_Cu); ls.AddLayer(P.B_Cu)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True)
    z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowFootprints(footprints)
    o = z.Outline(); o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(V(x, y))
    board.Add(z)


rk, ek = BOARD["rail_keepout"], BOARD["edge_keepout"]
keepout("rail_left", -W - 1, -H - 1, -W + rk, H + 1, True)
keepout("rail_right", W - rk, -H - 1, W + 1, H + 1, True)
keepout("top_edge", -W - 1, H - ek, W + 1, H + 1, False)
keepout("bottom_edge", -W - 1, -H - 1, W + 1, -H + ek, False)

# ---------------- silkscreen ----------------


def text(s, x, y, lay="F.SilkS", size=1.0, th=0.15, just=0, rot=0):
    t = P.PCB_TEXT(board)
    t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer(lay))
    t.SetTextSize(P.VECTOR2I(P.FromMM(size), P.FromMM(size))); t.SetTextThickness(P.FromMM(th))
    t.SetHorizJustify({0: P.GR_TEXT_H_ALIGN_CENTER, -1: P.GR_TEXT_H_ALIGN_LEFT, 1: P.GR_TEXT_H_ALIGN_RIGHT}[just])
    if lay.startswith("B."):
        t.SetMirrored(True)
    if rot:
        t.SetTextAngleDegrees(rot)
    board.Add(t)


# F side (component side, faces into the box)
text("N", 0.0, 21.3, size=0.8, th=0.12)
text("L'", 5.08, 21.3, size=0.8, th=0.12)
text("+5V", -11.6, 21.3, size=0.8, th=0.12)
text("GND", -15.2, 21.3, size=0.8, th=0.12)
text("T1A", 17.2, 8.7, size=0.8, th=0.12)
text("SEC", -9.4, 4.0, size=0.8, th=0.12)
text("PRI", -3.6, 4.0, size=0.8, th=0.12)
# B side (flat, faces the plate). Kept off the THT pads.
text("PRIMARY", 6.0, 19.6, "B.SilkS", 1.0)
text("SEC 5V", -14.0, 13.5, "B.SilkS", 1.0)
text("MAINS 120/230 VAC", 4.5, -3.6, "B.SilkS", 0.9, 0.14)
text("F1: T1A 250V", 4.5, -5.8, "B.SilkS", 0.9, 0.14)
text("!", 13.0, -9.6, "B.SilkS", 1.4, 0.22)
for a, b in (((10.8, -10.8), (15.2, -10.8)), ((15.2, -10.8), (13.0, -7.0)), ((13.0, -7.0), (10.8, -10.8))):
    seg(a, b, "B.SilkS", 0.2)
text(f"psu_carrier {REV}", 2.0, -13.4, "B.SilkS", 1.0)
text(DATE, 2.0, -15.4, "B.SilkS", 0.8, 0.12)
text("NOT CERTIFIED", 2.0, -17.2, "B.SilkS", 0.8, 0.12)
# isolation boundary marks either side of the slot (both sides)
for lay in ("F.SilkS", "B.SilkS"):
    for x in (sx0 - 0.5, sx1 + 0.5):
        seg((x, 20.5), (x, 2.8), lay, 0.15)

out = PRJ / "psu_carrier.kicad_pcb"
P.SaveBoard(str(out), board)   # also writes psu_carrier.kicad_pro (netclasses, rules)
print("wrote", out)
