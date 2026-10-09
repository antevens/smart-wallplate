"""Shared generators for the small KiCad projects (sensor flex, 5 V jumper, EU PSU board).

Lib holds a project's library context: project directory, library name, a stable uuid
function and its power nets. Sheet writes a flat schematic, Board builds a board through pcbnew.
Run with the Python that ships pcbnew.
"""
import copy
import datetime
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pcbnew as P
from sexpr import loads, dumps, find, first, Sym, S

DATE = datetime.date.today().isoformat()
OX, OY = 100.0, 100.0


@dataclass
class Lib:
    prj: Path
    name: str
    uid: Callable
    power: tuple


class Sheet:
    def __init__(self, lib, project):
        self.lib = lib
        self.project = project
        self.root = self.lib.uid(project, "root")
        self.items, self.used = [], set()
        tree = loads((self.lib.prj / f"{self.lib.name}.kicad_sym").read_text())
        self.symlib = {s[1]: s for s in find(tree, "symbol")}

    def pins_of(self, symname):
        out = {}

        def walk(n):
            for x in n:
                if isinstance(x, list) and x:
                    if x[0] == "pin":
                        at = first(x, "at")
                        out[first(x, "number")[1]] = (float(at[1]), float(at[2]), float(at[3]))
                    else:
                        walk(x)
        walk(self.symlib[symname])
        return out

    @staticmethod
    def font(hide=False, justify=None):
        e = S("effects", S("font", S("size", 1.27, 1.27)))
        if justify:
            e.append(S("justify", *[Sym(j) for j in justify.split()]))
        if hide:
            e.append(S("hide", Sym("yes")))
        return e

    def prop(self, name, val, x, y, hide=False, justify=None):
        return S("property", name, val, S("at", x, y, 0), self.font(hide, justify))

    def place(self, ref, symname, x, y, value, fp="", ds="", desc="", extra=None, in_bom=True, on_board=True):
        self.used.add(symname)
        s = S("symbol", S("lib_id", f"{self.lib.name}:{symname}"), S("at", x, y, 0), S("unit", 1),
              S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes" if in_bom else "no")),
              S("on_board", Sym("yes" if on_board else "no")), S("dnp", Sym("no")),
              S("uuid", self.lib.uid(self.project, "sym", ref)))
        s.append(self.prop("Reference", ref, x + 3, y - 8, hide=ref.startswith("#"), justify="left"))
        s.append(self.prop("Value", value, x + 3, y + 8.5, justify="left"))
        s.append(self.prop("Footprint", f"{self.lib.name}:{fp}" if fp else "", x, y, hide=True))
        s.append(self.prop("Datasheet", ds, x, y, hide=True))
        s.append(self.prop("Description", desc, x, y, hide=True))
        for k, v in (extra or {}).items():
            s.append(self.prop(k, v, x, y, hide=True))
        pins = self.pins_of(symname)
        for n in pins:
            s.append(S("pin", n, S("uuid", self.lib.uid(self.project, "pin", ref, n))))
        s.append(S("instances", S("project", self.project, S("path", f"/{self.root}", S("reference", ref),
                                                              S("unit", 1)))))
        self.items.append(s)
        return {n: (x + px, y - py, ang) for n, (px, py, ang) in pins.items()}

    def label(self, net, xyang):
        x, y, ang = xyang
        left = ang == 0.0
        self.items.append(S("label", net, S("at", x, y, 180 if left else 0), S("fields_autoplaced", Sym("yes")),
                            self.font(justify="right bottom" if left else "left bottom"),
                            S("uuid", self.lib.uid(self.project, "label", net, f"{x:.2f},{y:.2f}"))))

    def no_connect(self, xyang):
        x, y, _ = xyang
        self.items.append(S("no_connect", S("at", x, y), S("uuid", self.lib.uid(self.project, "nc", f"{x:.2f},{y:.2f}"))))

    def note(self, text, x, y):
        self.items.append(S("text", text, S("exclude_from_sim", Sym("no")), S("at", x, y, 0),
                            self.font(justify="left top"), S("uuid", self.lib.uid(self.project, "text", text[:40]))))

    def write(self, title, rev, comments):
        lib_symbols = S("lib_symbols")
        for name in sorted(self.used):
            s = copy.deepcopy(self.symlib[name])
            s[1] = f"{self.lib.name}:{name}"
            lib_symbols.append(s)
        tb = S("title_block", S("title", title), S("date", DATE), S("rev", rev), S("company", "smart-wallplate"),
               *[S("comment", i + 1, c) for i, c in enumerate(comments)])
        sch = S("kicad_sch", S("version", Sym("20250114")), S("generator", "eeschema"),
                S("generator_version", "9.0"), S("uuid", self.root), S("paper", "A4"), tb, lib_symbols,
                *self.items, S("sheet_instances", S("path", "/", S("page", "1"))), S("embedded_fonts", Sym("no")))
        (self.lib.prj / f"{self.project}.kicad_sch").write_text(dumps(sch) + "\n")


def build_schematic(lib, project, parts, flags, title, rev, comments, notes):
    g = 2.54
    sh = Sheet(lib, project)
    pwr = 0
    for i, (ref, p) in enumerate(parts.items()):
        col, row = i % 6, i // 6
        pins = sh.place(ref, p["sym"], (14 + 16 * col) * g, (36 + 26 * row) * g, p["value"], p["fp"], p.get("ds", ""),
                        p.get("desc", ""), {"Manufacturer": p.get("mfr", ""), "MPN": p.get("mpn", "")},
                        in_bom=p.get("in_bom", True))
        for pin, xy in pins.items():
            net = p["nets"].get(pin)
            if net is None:
                sh.no_connect(xy)
            elif net in lib.power:
                pwr += 1
                sh.place(f"#PWR0{pwr:02d}", net, xy[0], xy[1], net, in_bom=False, on_board=False)
            else:
                sh.label(net, xy)
    for i, net in enumerate(flags):                      # nets fed from off-board: flag them as driven
        x, y = (14 + 12 * i) * g, 20 * g
        pins = sh.place(f"#FLG0{i + 1}", "PWR_FLAG", x, y, "PWR_FLAG", in_bom=False, on_board=False)
        px, py, _ = list(pins.values())[0]
        if net in lib.power:
            pwr += 1
            sh.place(f"#PWR0{pwr:02d}", net, px, py, net, in_bom=False, on_board=False)
        else:
            sh.label(net, (px, py, 90.0))
    sh.note(notes, 25, 180)
    sh.write(title, rev, comments)




def V(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY - y))


def mm(v):
    return P.ToMM(v.x) - OX, OY - P.ToMM(v.y)


def fillet(pts, r, closed):
    """Corners of a polyline as tangent arcs: list of ("seg", a, b) / ("arc", a, mid, b)."""
    n = len(pts)
    idx = range(n) if closed else range(1, n - 1)
    corners = {}
    for i in idx:
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        ux, uy = p1[0] - p0[0], p1[1] - p0[1]
        vx, vy = p2[0] - p1[0], p2[1] - p1[1]
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        ux, uy, vx, vy = ux / lu, uy / lu, vx / lv, vy / lv
        turn = math.acos(max(-1.0, min(1.0, ux * vx + uy * vy)))
        if turn < math.radians(2):
            continue
        t = min(r * math.tan(turn / 2), 0.45 * min(lu, lv))
        rr = t / math.tan(turn / 2)
        a = (p1[0] - ux * t, p1[1] - uy * t)
        b = (p1[0] + vx * t, p1[1] + vy * t)
        bx, by = vx - ux, vy - uy
        bl = math.hypot(bx, by)
        dist = rr / math.cos(turn / 2)
        c = (p1[0] + bx / bl * dist, p1[1] + by / bl * dist)
        mx, my = p1[0] - c[0], p1[1] - c[1]
        ml = math.hypot(mx, my)
        corners[i] = (a, (c[0] + mx / ml * rr, c[1] + my / ml * rr), b)
    out = []
    order = list(range(n)) + ([0] if closed else [])
    start = None
    for i in order:
        p = pts[i]
        here_in, here_out = (corners[i][0], corners[i][2]) if i in corners else (p, p)
        if start is not None and math.hypot(here_in[0] - start[0], here_in[1] - start[1]) > 1e-4:
            out.append(("seg", start, here_in))
        if i in corners and not (closed and start is not None and i == order[-1] and i == 0):
            out.append(("arc",) + corners[i])
        start = here_out
    return out


# ============================== silkscreen part labels ==============================
LABEL_SIZE, LABEL_TH, LABEL_MARGIN = 0.8, 0.12, 0.25        # text height / stroke, clearance to obstacles (mm)
GENERIC_MFR = ("", "-", "any", "TBD")


def label_text(ref, p):
    """Silkscreen label for a part: its reference and maker / model (value for generic parts, or
    p["label"]). None for parts left unlabelled (no label and out of the BOM)."""
    if "label" in p:
        return f"{ref} {p['label']}" if p["label"] else None
    if not p.get("in_bom", True):
        return None
    mfr, mpn = p.get("mfr", ""), p.get("mpn", "")
    return f"{ref} {mfr} {mpn}" if mfr not in GENERIC_MFR else f"{ref} {p['value']}"


def _box(b, grow=0.0):
    g = P.FromMM(grow)
    return (b.GetLeft() - g, b.GetTop() - g, b.GetRight() + g, b.GetBottom() + g)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _courtyard(fp, back):
    poly = fp.GetCourtyard(P.B_CrtYd if back else P.F_CrtYd)
    return poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False, False)


def place_labels(board, items, size=LABEL_SIZE, th=LABEL_TH, margin=LABEL_MARGIN):
    """Add a silkscreen label next to each (footprint, text): on the footprint's side, outside its
    courtyard, inside the board outline, clear of pads, other silkscreen and other courtyards.
    Raises if a label finds no place."""
    outline = P.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline)
    fps = list(board.GetFootprints())
    placed = {False: [], True: []}
    obst = {False: [], True: []}
    for back, layer in ((False, P.F_SilkS), (True, P.B_SilkS)):
        for d in board.GetDrawings():
            if d.GetLayer() == layer:
                obst[back].append(_box(d.GetBoundingBox(), margin))
        for fp in fps:
            for g in fp.GraphicalItems():
                if g.GetLayer() == layer:
                    obst[back].append(_box(g.GetBoundingBox(), margin))
            for f in (fp.Reference(), fp.Value()):
                if f.IsVisible() and f.GetLayer() == layer:
                    obst[back].append(_box(f.GetBoundingBox(), margin))
            for pd in fp.Pads():
                if pd.GetAttribute() in (P.PAD_ATTRIB_PTH, P.PAD_ATTRIB_NPTH) or \
                        pd.IsOnLayer(P.B_Cu if back else P.F_Cu):
                    obst[back].append(_box(pd.GetBoundingBox(), margin))

    edge = margin                                           # silkscreen to board edge, slots included
    bare_back = not any(pd.IsOnLayer(P.B_Cu) for fp in fps for pd in fp.Pads()) and \
        not any(t.GetLayer() == P.B_Cu for t in board.GetTracks())   # single-layer flex: labels may go on its back

    def inside(bx):
        """The label's box, grown by the edge clearance, lies wholly inside the board outline
        (slots and notches included)."""
        g = P.FromMM(edge)
        rect = P.SHAPE_POLY_SET()
        rect.NewOutline()
        for x, y in ((bx[0] - g, bx[1] - g), (bx[2] + g, bx[1] - g), (bx[2] + g, bx[3] + g), (bx[0] - g, bx[3] + g)):
            rect.Append(int(x), int(y))
        rect.BooleanSubtract(outline)
        return rect.OutlineCount() == 0

    def area(it):
        b = _courtyard(it[0], it[0].IsFlipped())
        return b.GetWidth() * b.GetHeight()
    for fp, text in sorted(items, key=area):                 # small parts first: they need the nearby spots
        back = fp.IsFlipped()
        layer = P.B_SilkS if back else P.F_SilkS
        crt = _courtyard(fp, back)
        others = [_box(_courtyard(o, back)) for o in fps if o is not fp and o.IsFlipped() == back]
        ref, rest = text.split(" ", 1) if " " in text else (text, "")
        forms = [text, f"{ref}\n{rest}" if rest else text]
        t = P.PCB_TEXT(board)
        t.SetLayer(layer)
        t.SetTextSize(P.VECTOR2I(P.FromMM(size), P.FromMM(size)))
        t.SetTextThickness(P.FromMM(th))
        t.SetMirrored(back)
        found = None
        why = {"outside": 0, "pads/silk": 0, "labels": 0}
        for strict in (True, False):                          # first also clear of other parts' courtyards
            for d in (0.3, 0.8, 1.5, 2.5, 4.0, 6.0, 9.0, 13.0, 18.0):
                g = P.FromMM(d)
                cx, cy = (crt.GetLeft() + crt.GetRight()) // 2, (crt.GetTop() + crt.GetBottom()) // 2
                for form in forms:
                    for rot in (0, 90):
                        t.SetText(form)
                        t.SetTextAngleDegrees(rot)
                        t.SetPosition(P.VECTOR2I(0, 0))
                        tb = t.GetBoundingBox()
                        hw, hh = tb.GetWidth() // 2, tb.GetHeight() // 2
                        cands = [(cx, crt.GetTop() - g - hh), (cx, crt.GetBottom() + g + hh),
                                 (crt.GetLeft() + hw, crt.GetTop() - g - hh), (crt.GetRight() - hw, crt.GetTop() - g - hh),
                                 (crt.GetLeft() + hw, crt.GetBottom() + g + hh),
                                 (crt.GetRight() - hw, crt.GetBottom() + g + hh)]
                        for k in (0, -1, 1, -2, 2, -3, 3):                 # beside the part, slid across
                            off = P.FromMM(0.6 * k)
                            cands += [(crt.GetLeft() - g - hw, cy + off), (crt.GetRight() + g + hw, cy + off),
                                      (cx + off, crt.GetTop() - g - hh), (cx + off, crt.GetBottom() + g + hh)]
                        for x, y in cands:
                            t.SetPosition(P.VECTOR2I(int(x), int(y)))
                            bx = _box(t.GetBoundingBox())
                            if not inside(bx):
                                why["outside"] += 1
                                continue
                            if any(_hit(bx, o) for o in obst[back]):
                                why["pads/silk"] += 1
                                continue
                            if any(_hit(bx, o) for o in placed[back]):
                                why["labels"] += 1
                                continue
                            if strict and any(_hit(bx, o) for o in others):
                                continue
                            found = (form, rot, x, y)
                            break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        sides = [back] + ([not back] if bare_back else [])
        for side in sides if not found else ():              # nearest free spot anywhere on the board; on a
            if found:                                         # single-layer flex also on its bare back
                break
            back = side
            t.SetLayer(P.B_SilkS if back else P.F_SilkS)
            t.SetMirrored(back)
            ob = outline.BBox()
            cx, cy = (crt.GetLeft() + crt.GetRight()) // 2, (crt.GetTop() + crt.GetBottom()) // 2
            step = P.FromMM(0.5)
            pts = [(x, y) for x in range(ob.GetLeft(), ob.GetRight(), step) for y in range(ob.GetTop(), ob.GetBottom(), step)]
            pts.sort(key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
            for x, y in pts:
                for form in forms:
                    for rot in (0, 90):
                        t.SetText(form)
                        t.SetTextAngleDegrees(rot)
                        t.SetPosition(P.VECTOR2I(int(x), int(y)))
                        bx = _box(t.GetBoundingBox())
                        if inside(bx) and not any(_hit(bx, o) for o in obst[back] + placed[back]):
                            found = (form, rot, x, y)
                            break
                    if found:
                        break
                if found:
                    break
        if not found:
            raise RuntimeError(f"no room for the silkscreen label {text!r} (rejected: {why})")
        form, rot, x, y = found
        t.SetText(form)
        t.SetTextAngleDegrees(rot)
        t.SetPosition(P.VECTOR2I(int(x), int(y)))
        board.Add(t)
        placed[back].append(_box(t.GetBoundingBox(), margin))
    return board


class Board:
    def __init__(self, lib, name, layers, thickness, clearance, track, on_save=None):
        self.lib = lib
        self.on_save = on_save                                # rewrites the .kicad_pro (SaveBoard resets it)
        self.name = name
        self.b = P.BOARD()
        ds = self.b.GetDesignSettings()
        ds.SetAuxOrigin(V(0, 0))
        ds.SetGridOrigin(V(0, 0))
        self.b.SetCopperLayerCount(layers)
        ds.SetBoardThickness(P.FromMM(thickness))
        ds.m_MinClearance = P.FromMM(min(clearance, 0.1))
        ds.m_TrackMinWidth = P.FromMM(min(track, 0.1))
        ds.m_HoleClearance = P.FromMM(0.2)
        ds.m_ViasMinSize = P.FromMM(0.5)
        ds.m_ViasMinAnnularWidth = P.FromMM(0.1)
        nc = ds.m_NetSettings.GetDefaultNetclass()
        nc.SetClearance(P.FromMM(clearance))
        nc.SetTrackWidth(P.FromMM(track))
        self.nets, self.fps, self.parts, self.zones = {}, {}, {}, 0

    def net(self, name):
        if name not in self.lib.power and not name.startswith("unconnected-"):
            name = f"/{name}"                            # local schematic labels are sheet-qualified
        if name not in self.nets:
            n = P.NETINFO_ITEM(self.b, name)
            self.b.Add(n)
            self.nets[name] = n
        return self.nets[name]

    def shape(self, kind, layer, w, *pts):
        s = P.PCB_SHAPE(self.b, kind)
        if kind == P.SHAPE_T_ARC:
            s.SetArcGeometry(V(*pts[0]), V(*pts[1]), V(*pts[2]))
        else:
            s.SetStart(V(*pts[0]))
            s.SetEnd(V(*pts[1]))
        s.SetLayer(layer)
        s.SetWidth(P.FromMM(w))
        self.b.Add(s)

    def zone(self, net, layer, pts, prio=0, min_w=1.0, fillet_r=1.0, name="", clearance=None):
        """Solid copper pour (full pad connection), outline pts (room mm); filled on save. clearance:
        the pour's own clearance to every other net (mm)."""
        z = P.ZONE(self.b)
        z.SetLayer(layer)
        z.SetNet(self.net(net))
        z.SetAssignedPriority(prio)
        z.SetPadConnection(P.ZONE_CONNECTION_FULL)
        z.SetMinThickness(P.FromMM(min_w))
        z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetCornerSmoothingType(P.ZONE_SETTINGS.SMOOTHING_FILLET)
        z.SetCornerRadius(P.FromMM(fillet_r))
        if name:
            z.SetZoneName(name)
        if clearance is not None:
            z.SetLocalClearance(P.FromMM(clearance))
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            ol.Append(V(x, y))
        self.b.Add(z)
        self.zones += 1
        return z

    def keepout(self, x, y, r, name=""):
        """Rule area on both copper layers round (x, y): no pours, tracks or vias (pads allowed)."""
        z = P.ZONE(self.b)
        ls = P.LSET()
        ls.AddLayer(P.F_Cu)
        ls.AddLayer(P.B_Cu)
        z.SetLayerSet(ls)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        if name:
            z.SetZoneName(name)
        ol = z.Outline()
        ol.NewOutline()
        for k in range(48):
            a = 2 * math.pi * k / 48
            ol.Append(V(x + r * math.cos(a), y + r * math.sin(a)))
        self.b.Add(z)

    def polyline(self, pts, layer=P.Edge_Cuts, w=0.05, closed=True):
        n = len(pts)
        for i in range(n if closed else n - 1):
            self.shape(P.SHAPE_T_SEGMENT, layer, w, pts[i], pts[(i + 1) % n])

    def outline(self, pts, r):
        for piece in fillet(pts, r, closed=True):
            if piece[0] == "seg":
                self.shape(P.SHAPE_T_SEGMENT, P.Edge_Cuts, 0.05, piece[1], piece[2])
            else:
                self.shape(P.SHAPE_T_ARC, P.Edge_Cuts, 0.05, piece[1], piece[2], piece[3])

    def text(self, s, x, y, layer, size=0.8, rot=0):
        t = P.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetPosition(V(x, y))
        t.SetLayer(layer)
        t.SetTextSize(P.VECTOR2I(P.FromMM(size), P.FromMM(size)))
        t.SetTextThickness(P.FromMM(size * 0.15))
        t.SetTextAngleDegrees(rot)
        t.SetMirrored(layer in (P.B_SilkS, P.B_Fab, P.B_Cu))  # back-side text reads from the back
        self.b.Add(t)

    def place(self, ref, p, show_ref):
        """Footprint p["fp"] at p["pos"] = (x, y, rot) on p["side"] ("F" default, "B" flipped)."""
        fp = P.FootprintLoad(str(self.lib.prj / f"{self.lib.name}.pretty"), p["fp"])
        fp.SetFPID(P.LIB_ID(self.lib.name, p["fp"]))
        fp.SetReference(ref)
        fp.SetValue(p["value"])
        fp.SetPath(P.KIID_PATH(f"/{self.lib.uid(self.name, 'sym', ref)}"))
        fp.SetSheetname("Root")
        fp.SetSheetfile(f"{self.name}.kicad_sch")
        x, y, rot = p["pos"]
        fp.SetPosition(V(x, y))
        fp.Reference().SetVisible(show_ref)
        fp.Value().SetVisible(False)
        fp.SetExcludedFromBOM(not p.get("in_bom", True))
        self.b.Add(fp)
        if p.get("side", "F") == "B":
            fp.Flip(fp.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        for pd in fp.Pads():
            num = pd.GetNumber()
            if not num:                                  # unnumbered pad (NPTH hole): no net
                continue
            net = p["nets"].get(num)
            if not net:                                  # unused pin: KiCad's name for its schematic net
                name = p.get("pin_names", {}).get(num, f"Pin_{num}")
                net = f"unconnected-({ref}-{name}-Pad{num})"
            pd.SetNet(self.net(net))
        self.fps[ref] = fp
        self.parts[ref] = p
        return fp

    def pad_xy(self, ref, num):
        return mm([q for q in self.fps[ref].Pads() if q.GetNumber() == num][0].GetPosition())

    def track(self, net, w, pts, layer=P.F_Cu):
        for piece in fillet(pts, max(2 * w, 0.6), closed=False):
            if piece[0] == "seg":
                if math.hypot(piece[2][0] - piece[1][0], piece[2][1] - piece[1][1]) < 1e-3:
                    continue
                t = P.PCB_TRACK(self.b)
                t.SetStart(V(*piece[1]))
                t.SetEnd(V(*piece[2]))
            else:
                t = P.PCB_ARC(self.b)
                t.SetStart(V(*piece[1]))
                t.SetMid(V(*piece[2]))
                t.SetEnd(V(*piece[3]))
            t.SetWidth(P.FromMM(w))
            t.SetLayer(layer)
            t.SetNet(self.net(net))
            self.b.Add(t)

    def via(self, net, x, y):
        v = P.PCB_VIA(self.b)
        v.SetPosition(V(x, y))
        v.SetWidth(P.FromMM(0.6))
        v.SetDrill(P.FromMM(0.3))
        v.SetNet(self.net(net))
        self.b.Add(v)

    def save(self):
        items = [(self.fps[r], label_text(r, p)) for r, p in self.parts.items()]
        place_labels(self.b, [(fp, t) for fp, t in items if t])
        out = self.lib.prj / f"{self.name}.kicad_pcb"
        P.SaveBoard(str(out), self.b)
        if self.on_save:
            self.on_save()
        if self.zones:                                       # filling an in-memory board crashes in KiCad 9:
            filled = P.LoadBoard(str(out))                    # reload from disk (net classes from the project),
            filled.BuildConnectivity()                        # then fill
            P.ZONE_FILLER(filled).Fill(filled.Zones())
            P.SaveBoard(str(out), filled)
            if self.on_save:
                self.on_save()
        print("wrote", out)


