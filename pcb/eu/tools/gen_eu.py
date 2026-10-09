"""Generate the EU KiCad projects in pcb/eu/kicad/ (docs/DESIGN.md D-30, D-36): the mains board and
the 5 V board.

Libraries, projects with net classes and isolation rules, schematics and boards, all from
eu_parts.py (geometry from cad/build123d/eu/params_eu.py). Run with the Python that ships pcbnew.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "tools"))           # pcb/tools: sexpr, gen_libs, kigen
import pcbnew as P
import eu_parts as ep
from sexpr import dumps, loads, Sym, S
import gen_libs as gl
from sexpr import find, first
import kigen
from kigen import Board, build_schematic

PRJ = HERE.parent / "kicad"
CTX = kigen.Lib(PRJ, ep.LIB, ep.uid, ("+5V", "GND"))
STOCK_EXTRA = {ep.FP_HDR: "Connector_PinHeader_2.54mm", ep.FP_SOCKET: "Connector_PinSocket_2.54mm"}

SYMBOLS = [("Device", "Fuse"), ("Device", "Varistor"), ("Device", "C"),
           ("Connector_Generic", "Conn_01x01"), ("Connector_Generic", "Conn_01x02"), ("Connector", "Screw_Terminal_01x02"), ("Mechanical", "MountingHole"),
           ("power", "+5V"), ("power", "GND"), ("power", "PWR_FLAG")]
STOCK_FP = {ep.FP_FUSE: "Fuse", ep.FP_C1: "Capacitor_SMD", ep.FP_MH: "MountingHole"}


# ============================== libraries ==============================
def fp_psu():
    """Traco TMPS 03 (datasheet rev. 2026-07-01): 25.4 x 25.4 body, pins Ø0.6 on a 2.54 grid; top view."""
    items = [gl.tht(n, x, y, "rect" if n == "1" else "circle", ep.PSU_PAD, ep.PSU_PAD, ep.PSU_DRILL)
             for n, (x, y) in ep.PSU_PINS.items()]
    items += gl.body(ep.PSU[0], ep.PSU[1], silk=False)          # no silk outline: it would cross the relief slot
    items.append(gl.model3d(ep.FP_PSU))
    return gl._fp(ep.FP_PSU, f"Traco TMPS 03 AC-DC module, 1 x 1 in, THT, {ep.TMPS_DS}",
                  "AC-DC converter Traco TMPS", "through_hole", items)


def fp_wago():
    """WAGO 2604-3102: 2 poles at 5 mm, 2 solder pins per pole, conductor entry 90 deg to the PCB.
    Origin = body centre (y) and poles' centre (x). Pin rows WAGO_ROW apart, their centre WAGO_ROW_OFF
    towards the entry side (-y); the lever side is +y. Body from WAGO's 3D model."""
    items = []
    y1 = -ep.WAGO_ROW_OFF - ep.WAGO_ROW / 2
    for i, x in enumerate((-ep.WAGO_PITCH / 2, ep.WAGO_PITCH / 2)):
        for y in (y1, y1 + ep.WAGO_ROW):
            shape = "rect" if i == 0 and y == y1 else "circle"
            items.append(gl.tht(str(i + 1), x, y, shape, *ep.WAGO_PAD, ep.WAGO_DRILL))
    items += gl.body(ep.WAGO_EU[0], ep.WAGO_EU[1])
    items.append(gl.model3d(ep.FP_WAGO))
    return gl._fp(ep.FP_WAGO, f"WAGO 2604-3102 PCB terminal block, push-in, lever, 2-pole, P5.00 mm, 4 mm2, "
                  f"entry 90 deg to the PCB, 400 V III/2, {ep.WAGO_DS}; pin rows {ep.WAGO_ROW} mm apart and body "
                  "from WAGO's 3D model (lever side +y)", "WAGO 2604 terminal block push-in", "through_hole", items)


def psu_symbol():
    """TMPS 03-105 symbol: the stock IRM-03-5 with the TMPS pin numbers."""
    s = gl.stock_symbol("Converter_ACDC", "IRM-03-5")
    old, new = s[1], "TMPS03-105"
    s[1] = new
    for sub in find(s, "symbol"):
        sub[1] = sub[1].replace(old, new, 1)
    pins = {"1": ("2", "AC(L)"), "3": ("1", "AC(N)"), "5": ("3", "NC"), "14": ("4", "-Vout"), "16": ("5", "+Vout")}
    for sub in find(s, "symbol"):
        for x in sub:
            if isinstance(x, list) and x and x[0] == "pin":
                num, name = first(x, "number"), first(x, "name")
                num[1], name[1] = pins[num[1]]
    for p in find(s, "property"):
        p[2] = {"Value": new, "Footprint": f"{ep.LIB}:{ep.FP_PSU}", "Datasheet": ep.TMPS_DS,
                "Description": "Traco TMPS 03-105 AC-DC module, 5 V 600 mA, 3 W, 1 x 1 in",
                "ki_fp_filters": "Converter*ACDC*TRACO*TMPS*", "ki_keywords": "AC-DC module Traco"}.get(p[1], p[2])
    return s


def fp_pin():
    """Harwin P70-2200045 spring pin: recommended pad 2.2 with a 1.2 through hole for the peg."""
    pad = S("pad", "1", Sym("thru_hole"), Sym("circle"), S("at", 0, 0), S("size", ep.PIN_PAD_D, ep.PIN_PAD_D),
            S("drill", ep.PIN_HOLE_D), S("layers", "*.Cu", "*.Mask", "F.Paste"))
    crt = S("fp_circle", S("center", 0, 0), S("end", ep.PIN_PAD_D / 2 + 0.25, 0),
            S("stroke", S("width", 0.05), S("type", Sym("solid"))), S("fill", Sym("no")), S("layer", "F.CrtYd"))
    return gl._fp(ep.FP_PIN, f"Harwin P70-2200045 SMT spring pin with peg, {ep.PIN_DS}", "spring pin pogo",
                  "smd", [pad, crt, gl.model3d(ep.FP_PIN)])


def build_libs():
    syms = [Sym("kicad_symbol_lib"), S("version", Sym("20241209")), S("generator", "gen_eu"),
            S("generator_version", "9.0")]
    for lib, name in SYMBOLS:
        syms.append(gl.stock_symbol(lib, name))
    syms.append(psu_symbol())
    sw = gl.stock_symbol("Switch", "SW_DPST")                 # the Marquardt rocker, pins 1 / 1a, 2 / 2a
    old = sw[1]
    sw[1] = "SW_DPST_Marquardt"
    for sub in find(sw, "symbol"):
        sub[1] = sub[1].replace(old, "SW_DPST_Marquardt", 1)
    gl.renumber_rocker(sw)
    syms.append(sw)
    PRJ.mkdir(parents=True, exist_ok=True)
    (PRJ / f"{ep.LIB}.kicad_sym").write_text(dumps(syms) + "\n")
    d = PRJ / f"{ep.LIB}.pretty"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.kicad_mod"):
        f.unlink()
    for name, lib in {**STOCK_FP, **STOCK_EXTRA}.items():
        fp = gl.localize_models(loads((gl.FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").read_text()), PRJ)
        (d / f"{name}.kicad_mod").write_text(dumps(fp) + "\n")
    for fp in (gl.fp_mov(), fp_psu(), fp_wago(), fp_pin(), gl.fp_rocker()):
        (d / f"{fp[1]}.kicad_mod").write_text(dumps(fp) + "\n")
    (PRJ / "fp-lib-table").write_text(
        f'(fp_lib_table\n\t(version 7)\n\t(lib (name "{ep.LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{ep.LIB}.pretty")'
        '(options "")(descr "EU board footprints"))\n)\n')
    (PRJ / "sym-lib-table").write_text(
        f'(sym_lib_table\n\t(version 7)\n\t(lib (name "{ep.LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{ep.LIB}.kicad_sym")'
        '(options "")(descr "EU board symbols"))\n)\n')


# ============================== project + rules ==============================
MAINS = "(A.NetClass == 'Mains_L' || A.NetClass == 'Mains_N')"
DRU = f"""(version 1)
# Spacing design TARGETS for the EU mains board (docs/DESIGN.md D-30, D-36; AGENTS.md hard constraint 3):
# 270 V working, overvoltage category III, pollution degree 2, stricter of IEC 60664-1 / EN 62368-1.
# Not a compliance claim: human review required.

(rule "Board edge clearance"
    (constraint edge_clearance (min 0.5mm)))

(rule "Mains copper to board edge >= 1.0 mm"
    (condition "{MAINS}")
    (constraint edge_clearance (min 1.0mm)))

(rule "Mains copper to mounting holes >= 1.0 mm"
    (condition "{MAINS} && B.Type == 'Hole'")
    (constraint hole_clearance (min 1.0mm)))

(rule "L-N clearance >= 3.5 mm"
    (condition "A.NetClass == 'Mains_L' && B.NetClass == 'Mains_N'")
    (constraint clearance (min 3.5mm)))

(rule "Different mains nets >= 3.5 mm (line / switched line / fused line, neutral / switched neutral)"
    (condition "{MAINS} && (B.NetClass == 'Mains_L' || B.NetClass == 'Mains_N') && A.NetName != B.NetName")
    (constraint clearance (min 3.5mm)))

(rule "Mains to 5 V side >= 8.0 mm (reinforced)"
    (condition "{MAINS} && B.NetClass == 'SELV'")
    (constraint clearance (min 8.0mm))
    (constraint creepage (min 8.0mm)))

(rule "Mains to the PSU's NC pin (DC end) >= 8.0 mm"
    (condition "{MAINS} && B.NetName == 'unconnected-(PS1-NC-Pad3)'")
    (constraint clearance (min 8.0mm)))

# Exception (AGENTS.md hard constraint 3): pins of one rated part keep the part's own spacing
# (TMPS 03 3 kVAC reinforced, WAGO 2604 400 V III/2, Marquardt 1802.2504, UMT 250 fuse, CU4032 varistor).
(rule "Pins of one rated part"
    (condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Parent.Reference == B.Parent.Reference")
    (constraint clearance (min 0.2mm)))
"""


def net_class(name, track):
    return {"bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": name,
            "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647 if name == "Default" else 0,
            "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": track, "via_diameter": 0.6,
            "via_drill": 0.3, "wire_width": 6}


LV_DRU = """(version 1)
# 5 V board (no mains): fab limits only.
(rule "Board edge clearance"
    (constraint edge_clearance (min 0.5mm)))
"""


def build_project(name, dru):
    classes = [net_class("Default", 0.25)] + [net_class(c, ep.TRACK_W[c]) for c in ep.NETCLASS]
    for i, c in enumerate(classes[1:]):
        c["priority"] = i
    patterns = [{"netclass": c, "pattern": n if n in CTX.power else f"/{n}"}
                for c, nets in ep.NETCLASS.items() for n in nets]
    pro = {"board": {"design_settings": {"rule_severities": {"lib_footprint_issues": "warning",
                                                             "lib_footprint_mismatch": "warning"}}},
           "meta": {"filename": f"{name}.kicad_pro", "version": 3},
           "net_settings": {"classes": classes, "meta": {"version": 4}, "net_colors": None,
                            "netclass_assignments": None, "netclass_patterns": patterns},
           "schematic": {"meta": {"version": 1}}, "sheets": [["", "Root"]]}
    (PRJ / f"{name}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")
    (PRJ / f"{name}.kicad_dru").write_text(dru)


# ============================== boards ==============================
def board_outline(cut_y=None):
    """Board outline (room mm): the box circle less clearance, cut straight at cut_y (None: whole
    circle), minus the notches round the box's screw domes; polygon booleans, densely sampled."""
    def circle(cx, cy, r, n):
        poly = P.SHAPE_POLY_SET()
        poly.NewOutline()
        for k in range(n):
            a = 2 * math.pi * k / n
            poly.Append(P.FromMM(cx + r * math.cos(a)), P.FromMM(-(cy + r * math.sin(a))))
        return poly
    board = circle(0, 0, ep.WB_R, 360)
    if cut_y is not None:
        keep = P.SHAPE_POLY_SET()
        keep.NewOutline()
        for x, y in ((-100, cut_y), (100, cut_y), (100, -100), (-100, -100)):
            keep.Append(P.FromMM(x), P.FromMM(-y))
        board.BooleanIntersection(keep)
    for (cx, cy), r in ep.notches(cut_y):
        board.BooleanSubtract(circle(cx, cy, r, 72))
    ol = board.Outline(0)
    return [(P.ToMM(ol.CPoint(i).x), -P.ToMM(ol.CPoint(i).y)) for i in range(ol.PointCount())]


def orient(bd, ref, test):
    """Turn a placed footprint until test(pad positions) holds."""
    fp = bd.fps[ref]
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        if test({q.GetNumber(): kigen.mm(q.GetPosition()) for q in fp.Pads() if q.GetNumber()}):
            return fp
    raise RuntimeError(f"no orientation of {ref} passes its test")


def pads_of(bd, ref, num):
    return [kigen.mm(q.GetPosition()) for q in bd.fps[ref].Pads() if q.GetNumber() == num]


def build_mains():
    bd = Board(CTX, ep.MAINS, 2, 1.6, 0.2, 0.25, on_save=lambda: build_project(ep.MAINS, DRU))
    bd.polyline(board_outline())
    x0, x1, ys, w = ep.MB_SLOT                               # routed relief slot under the PSU
    r = w / 2
    bd.shape(P.SHAPE_T_SEGMENT, P.Edge_Cuts, 0.05, (x0, ys + r), (x1, ys + r))
    bd.shape(P.SHAPE_T_SEGMENT, P.Edge_Cuts, 0.05, (x0, ys - r), (x1, ys - r))
    bd.shape(P.SHAPE_T_ARC, P.Edge_Cuts, 0.05, (x1, ys + r), (x1 + r, ys), (x1, ys - r))
    bd.shape(P.SHAPE_T_ARC, P.Edge_Cuts, 0.05, (x0, ys - r), (x0 - r, ys), (x0, ys + r))
    for ref, p in ep.MAINS_PARTS.items():
        bd.place(ref, p, False)
    c = ep.MB_PSU_C
    orient(bd, "PS1", lambda q: min(q["1"][1], q["2"][1]) > c[1] and q["2"][0] > q["1"][0])
    for ref in ("J1", "J2"):                       # poles along y, in above switched, levers towards the board centre
        nets = ep.MAINS_PARTS[ref]["nets"]
        pin, psw = (next(n for n, v in nets.items() if v.endswith(e)) for e in ("_IN", "_SW"))
        cx = ep.MAINS_PARTS[ref]["pos"][0]
        orient(bd, ref, lambda q: abs(q[pin][0] - q[psw][0]) < 0.01 and q[pin][1] > q[psw][1]
               and abs(sum(p[0] for p in pads_of(bd, ref, pin)) / 2) > abs(cx))
    orient(bd, "F1", lambda q: q["1"][0] > q["2"][0])          # L_SW pad towards the L block
    orient(bd, "RV1", lambda q: q["2"][1] > q["1"][1])         # N_SW pad up, L_F pad down
    s1 = {n: pads_of(bd, "S1", n)[0] for n in ("1", "1a", "2", "2a")}
    assert s1["1"][0] > 0 and s1["1"][1] > s1["1a"][1], "rocker: L pole on the right, in above switched"
    xy = lambda ref, n="1": pads_of(bd, ref, n)[0]
    # load paths: L pours on F.Cu (right), N pours on B.Cu (left); in above, switched below. The split
    # between them runs between the rocker's poles, then steps to between the WAGO block's poles.
    split_s = (s1["1"][1] + s1["1a"][1]) / 2
    top, bot = ep.WB_R + 2, ep.MB_PSU_C[1] + ep.PSU[1] / 2 - 4.5
    for ref, layer, sx, (n_in, n_sw) in (("J1", P.F_Cu, 1, ("L_IN", "L_SW")), ("J2", P.B_Cu, -1, ("N_IN", "N_SW"))):
        nets = ep.MAINS_PARTS[ref]["nets"]
        p_in, p_sw = (pads_of(bd, ref, next(n for n, v in nets.items() if v == net)) for net in (n_in, n_sw))
        split_w = (p_in[0][1] + p_sw[0][1]) / 2
        step = (abs(s1["1"][0]) + min(abs(p[0]) for p in p_in)) / 2
        up = [(2.0, split_s + 0.5), (step + 0.5, split_s + 0.5), (step + 0.5, split_w + 0.5), (top, split_w + 0.5),
              (top, top), (2.0, top)]
        down = [(2.0, bot), (top, bot), (top, split_w - 0.5), (step - 0.5, split_w - 0.5), (step - 0.5, split_s - 0.5),
                (2.0, split_s - 0.5)]
        for net, pts in ((n_in, up), (n_sw, down)):                # mains: 3.5 to any other net
            bd.zone(net, layer, [(sx * x, y) for x, y in pts], name=net, clearance=3.5)
    for i, (x, y) in enumerate(ep.MB_BOSS):                     # mounting holes: mains copper >= 1.0 mm away
        bd.keepout(x, y, 1.1 + 1.0 + 0.2, f"MH{i + 1} keep-out")
    w_l, w_s = ep.TRACK_W["Mains_L"], ep.TRACK_W["SELV"]
    psu_n, psu_l = xy("PS1", "1"), xy("PS1", "2")
    f_lf = xy("F1", "2")
    rv_l, rv_n = xy("RV1", "1"), xy("RV1", "2")
    # PSU feed: fused line from F1 to the PSU and the varistor, neutral from the PSU pin to the varistor
    y_lf = psu_l[1] - 7.0
    bd.track("L_F", w_l, [f_lf, (psu_l[0], f_lf[1]), psu_l], P.F_Cu)
    bd.track("L_F", w_l, [psu_l, (psu_l[0], y_lf), (rv_l[0] + 1.5, y_lf), rv_l], P.F_Cu)
    bd.track("N_SW", w_l, [psu_n, (psu_n[0], rv_n[1]), rv_n], P.F_Cu)
    # 5 V island: PSU outputs to the header
    h5, hg = xy("J3", "1"), xy("J3", "2")
    v5, gnd = xy("PS1", "5"), xy("PS1", "4")
    bd.track("+5V", w_s, [v5, (v5[0], h5[1]), h5], P.F_Cu)    # +5V output and GND output on either side
    bd.track("GND", w_s, [gnd, (gnd[0], hg[1]), hg], P.F_Cu)
    # installer side (back): what goes where
    for ref, side in (("J1", "L"), ("J2", "N")):
        nets = ep.MAINS_PARTS[ref]["nets"]
        y1, y2 = (pads_of(bd, ref, next(n for n, v in nets.items() if v.endswith(e)))[0][1] for e in ("_IN", "_SW"))
        x = ep.MAINS_PARTS[ref]["pos"][0]
        xo = x - (ep.WAGO_EU[1] / 2 + 1.3) * (1 if x > 0 else -1)          # on the lever side, towards the centre
        bd.text(f"{side} IN", xo, y1, P.B_SilkS, 0.8, 90)
        bd.text(f"{side} LOAD", xo, y2, P.B_SilkS, 0.8, 90)
    bd.text("MAINS 230 VAC", 0.0, -27.0 + 2.5, P.B_SilkS, 0.9)
    bd.save()
    hx = ep.MAINS_PARTS["J3"]["pos"][0]                       # SMT header: posts on the footprint's centre line
    return {n: (hx, xy("J3", n)[1]) for n in ("1", "2")}


def build_lv(header):
    bd = Board(CTX, ep.LV, 2, 1.6, 0.2, 0.25, on_save=lambda: build_project(ep.LV, LV_DRU))
    bd.polyline(board_outline(ep.WB_CUT_Y))
    for (x, y), r in ep.LV_BOSS_HOLES:                       # the mains board's long boss passes through
        bd.shape(P.SHAPE_T_CIRCLE, P.Edge_Cuts, 0.05, (x, y), (x + r, y))
    for ref, p in ep.LV_PARTS.items():
        bd.place(ref, p, False)
    orient(bd, "J1", lambda q: all(abs(q[n][0] - header[n][0]) < 0.01 and abs(q[n][1] - header[n][1]) < 0.01
                                   for n in ("1", "2")))      # socket pins on the header's pins
    xy = lambda ref, n="1": pads_of(bd, ref, n)[0]
    w = ep.TRACK_W["SELV"]
    s5, sg = xy("J1", "1"), xy("J1", "2")
    c_p, c_g = xy("C1", "1"), xy("C1", "2")
    p1, p2 = xy("P2"), xy("P1")                         # +5V pin (P2), GND pin (P1)
    x5 = c_p[0] - 3.0
    bd.track("+5V", w, [s5, (s5[0], s5[1] + 2.0), (x5, s5[1] + 2.0), (x5, c_p[1]), c_p], P.F_Cu)
    bd.track("+5V", w, [c_p, (c_p[0] + 1.0, p1[1]), p1], P.F_Cu)
    bd.track("GND", w, [c_g, (p2[0] - 1.5, p2[1]), p2], P.F_Cu)
    bd.track("GND", w, [sg, (sg[0] + 3.0, sg[1]), (sg[0] + 3.0, p2[1] - 3.0), (p2[0] - 2.0, p2[1] - 3.0), p2], P.B_Cu)
    bd.text(f"EU 5V {ep.REV}", -12.0, -17.0, P.F_SilkS, 0.9)
    bd.save()


def main():
    build_libs()
    build_project(ep.MAINS, DRU)
    build_project(ep.LV, LV_DRU)
    build_schematic(CTX, ep.MAINS, ep.MAINS_PARTS, ("L_F", "N_SW", "L_IN", "N_IN"), "Smart wall plate - EU mains board",
                    ep.REV, ["Generated by pcb/eu/tools/gen_eu.py - edit eu_parts.py"],
                    "EU mains board (docs/DESIGN.md D-36): S1 (Marquardt 1802.2504) breaks line and neutral of the\n"
                    "load between the WAGO blocks J1 (L) and J2 (N). F1 / RV1 / PS1 (TMPS 03-105) from the switched side;\n"
                    "PS1's outputs on the 5 V island (relief slot), J3 header to the 5 V board.")
    build_schematic(CTX, ep.LV, ep.LV_PARTS, ("+5V", "GND"), "Smart wall plate - EU 5 V board", ep.REV,
                    ["Generated by pcb/eu/tools/gen_eu.py - edit eu_parts.py"],
                    "EU 5 V board (docs/DESIGN.md D-36): J1 socket on the mains board's header; P1 / P2 spring pins\n"
                    "up through the cap to the sensor flex (no wires).")
    header = build_mains()
    build_lv(header)


if __name__ == "__main__":
    main()
