"""Generate the sensor flex and power jumper KiCad projects in pcb/sensor/kicad/ (D-27).

Libraries, project and rules, schematics and boards, all from sensor_parts.py (which takes its
geometry from cad/build123d/params.py). Run with the Python that ships pcbnew.
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "tools"))          # pcb/tools: sexpr + stock library lookup
import pcbnew as P
import sensor_parts as sp
import eu_flex_parts as eu
from sexpr import loads, dumps, find, first, Sym, S
import gen_libs as gl
import kigen
from kigen import Board, build_schematic

PRJ = HERE.parent / "kicad"
LIB = sp.LIB
POWER = ("+5V", "+3V3", "GND")

SYMBOLS = [("Connector_Generic", "Conn_02x15_Odd_Even"), ("Connector_Generic", "Conn_01x01"),
           ("Connector_Generic", "Conn_01x06"),
           ("Sensor_Humidity", "SHT4x"), ("Device", "C"), ("Device", "R"), ("Connector", "TestPoint"),
           ("Regulator_Linear", "TLV75533PDBV"),
           ("power", "+5V"), ("power", "+3V3"), ("power", "GND"), ("power", "PWR_FLAG")]
STOCK_FP = {sp.FP_SHT: "Sensor_Humidity", sp.FP_C: "Capacitor_SMD", sp.FP_R: "Resistor_SMD",
            sp.FP_SOT: "Package_TO_SOT_SMD"}
# DMM-4026-B-I2S-R pins (datasheet rev A) from the stock SPH0645LM4H symbol's pins, plus CONFIG
MIC_PINS = {"1": ("5", "WS"), "2": ("1", "LR"), "3": ("4", "GND"), "4": ("6", "SCK"), "5": ("3", "VDD"),
            "6": ("7", "SD")}


# ============================== libraries ==============================
def pad(num, x, y, sx, sy, layers=("F.Cu", "F.Mask"), shape="rect"):
    return S("pad", num, Sym("smd"), Sym(shape), S("at", x, y), S("size", sx, sy), S("layers", *layers))


def courtyard(w, h):
    """Courtyard rectangle w x h around the footprint origin."""
    return gl.rect(-w / 2, -h / 2, w / 2, h / 2, "F.CrtYd", 0.05)


def fp_b2b():
    """Placeholder for the CN2 mating plug: 2 x 15 at 0.4 mm. Odd pins on the row at local -y
    (flat +Y). NOT a vendor footprint: replace once the CN2 part is confirmed."""
    cols = sp.CN2_PINS // 2
    items = []
    for n in range(1, sp.CN2_PINS + 1):
        k = (n - 1) // 2
        x = -(cols - 1) / 2 * sp.CN2_PITCH + k * sp.CN2_PITCH
        y = -sp.CN2_ROW if n % 2 else sp.CN2_ROW
        items.append(pad(str(n), round(x, 3), y, 0.23, 0.8, ("F.Cu", "F.Paste", "F.Mask")))
    items += [gl.rect(-3.8, -1.5, 3.8, 1.5, "F.Fab", 0.1), courtyard(8.2, 3.6),
              S("fp_text", Sym("user"), "PLACEHOLDER: CN2 mate unconfirmed", S("at", 0, 2.6, 0),
                S("layer", "F.Fab"), S("effects", S("font", S("size", 0.6, 0.6), S("thickness", 0.1))))]
    return gl._fp(sp.FP_B2B, "PLACEHOLDER board-to-board plug, 0.4 mm, 2 x 15: mates the MSR-2's CN2 "
                  "(part, footprint and contact map unconfirmed, docs/DESIGN.md D-27)", "placeholder b2b",
                  "smd", items)


def fp_finger():
    """Harwin S7081-42R, recommended pad layout 6.65 x 3.60 (drawing S7081-42R iss. 7); bend end at -x (Fab mark)."""
    bx = -sp.FINGER[1] / 2 + 0.6
    items = [pad("1", 0, 0, sp.FINGER_PAD[1], sp.FINGER_PAD[0], ("F.Cu", "F.Paste", "F.Mask")),
             gl.rect(-sp.FINGER[1] / 2, -sp.FINGER[0] / 2, sp.FINGER[1] / 2, sp.FINGER[0] / 2, "F.Fab", 0.1),
             gl.line(bx, -sp.FINGER[0] / 2, bx, sp.FINGER[0] / 2, "F.Fab", 0.1),
             courtyard(sp.FINGER_PAD[1] + 0.5, sp.FINGER_PAD[0] + 0.5), gl.model3d(sp.FP_FINGER)]
    return gl._fp(sp.FP_FINGER, f"Harwin S7081-42R SMT spring finger, gold, 4 A, bend end at -x, {sp.HARWIN_DS}",
                  "spring finger contact", "smd", items)


def fp_mic():
    """PUI Audio DMM-4026-B-I2S-R land pattern (datasheet rev A): origin = body centre, +y towards the
    port. GND ring pad (soldered all round: it seals the port) and the port hole through flex and stiffener."""
    port_y = sp.MIC[1] / 2 - 1.0                        # MIC_PORT_IN from the body's port end
    rows = [port_y - sp.MIC_PORT_ROW - i * sp.MIC_ROW for i in range(3)]       # nearest the port first
    items = []
    for col, pins in ((-sp.MIC_COL, ("3", "2", "1")), (sp.MIC_COL, ("5", "6", "7"))):
        for y, n in zip(rows, pins):
            items.append(pad(n, round(col, 3), round(y, 3), *sp.MIC_PAD, ("F.Cu", "F.Paste", "F.Mask")))
    r_mid = sum(sp.MIC_RING) / 4                         # ring centre line radius
    ring_w = (sp.MIC_RING[1] - sp.MIC_RING[0]) / 2
    items.append(S("pad", "4", Sym("smd"), Sym("custom"), S("at", r_mid, port_y), S("size", ring_w, ring_w),
                   S("layers", "F.Cu", "F.Paste", "F.Mask"),
                   S("options", S("clearance", Sym("outline")), S("anchor", Sym("circle"))),
                   S("primitives", S("gr_circle", S("center", -r_mid, 0), S("end", 0, 0), S("width", ring_w),
                                     S("fill", Sym("no"))))))
    items.append(S("pad", "", Sym("np_thru_hole"), Sym("circle"), S("at", 0, port_y),
                   S("size", sp.MIC_FLEX_HOLE_D, sp.MIC_FLEX_HOLE_D), S("drill", sp.MIC_FLEX_HOLE_D),
                   S("layers", "*.Mask")))
    w, h = sp.MIC[0], sp.MIC[1]
    items += [gl.rect(-w / 2, -h / 2, w / 2, h / 2, "F.Fab", 0.1), courtyard(w + 0.5, h + 0.5), gl.model3d(sp.FP_MIC)]
    return gl._fp(sp.FP_MIC, f"PUI Audio DMM-4026-B-I2S-R I2S MEMS microphone, bottom port, {sp.MIC_DS}",
                  "microphone MEMS I2S bottom port", "smd", items)


def mic_symbol():
    """DMM-4026-B-I2S symbol: the stock SPH0645LM4H with the DMM-4026 pin numbers and a CONFIG pin."""
    s = gl.stock_symbol("Sensor_Audio", "SPH0645LM4H")
    old, new = s[1], "DMM-4026-B-I2S"
    s[1] = new
    for sub in find(s, "symbol"):
        sub[1] = sub[1].replace(old, new, 1)
    host, lr = None, None
    for sub in find(s, "symbol"):
        for x in sub:
            if isinstance(x, list) and x and x[0] == "pin":
                num, name = first(x, "number"), first(x, "name")
                num[1], name[1] = MIC_PINS[num[1]]
                if num[1] == "1":
                    host, lr = sub, x
    cfg = copy.deepcopy(lr)
    first(cfg, "number")[1], first(cfg, "name")[1] = "2", "CONFIG"
    first(cfg, "at")[2] = -float(first(lr, "at")[2])
    host.append(cfg)
    for p in find(s, "property"):
        p[2] = {"Value": new, "Footprint": f"{LIB}:{sp.FP_MIC}", "Datasheet": sp.MIC_DS,
                "Description": "PUI Audio I2S MEMS microphone, bottom port, LGA-7",
                "ki_fp_filters": "PUI*DMM*4026*", "ki_keywords": "microphone MEMS I2S"}.get(p[1], p[2])
    return s


def fp_plain_pad(name, w, h, descr):
    """Bare gold (ENIG) pad, no paste: x = w, y = h."""
    return gl._fp(name, descr, "pad target contact", "smd", [pad("1", 0, 0, w, h), courtyard(w + 0.25, h + 0.25)])


def fp_round_pad(name, d, descr):
    """Bare gold (ENIG) round pad, no paste."""
    return gl._fp(name, descr, "pad target contact", "smd", [pad("1", 0, 0, d, d, shape="circle"),
                                                             courtyard(d + 0.25, d + 0.25)])


def fp_fpc():
    """Six exposed flex contacts at 0.5 mm pitch for a Hirose FH12 (FPC spec MEASURE); pin 1 at local +y
    (board -Y)."""
    n, pitch, (w, h) = 6, sp.FPC_PITCH, sp.FPC_PAD
    items = [pad(str(i + 1), 0, round(((n - 1) / 2 - i) * pitch, 3), w, h) for i in range(n)]
    items.append(courtyard(w + 0.25, (n - 1) * pitch + h + 0.25))
    return gl._fp(sp.FP_FPC, "Flex contacts, 6 x 0.5 mm, for a Hirose FH12-6S (slide lock)", "FPC contacts",
                  "smd", items)


def build_libs():
    syms = [Sym("kicad_symbol_lib"), S("version", Sym("20241209")), S("generator", "gen_sensor"),
            S("generator_version", "9.0")]
    for lib, name in SYMBOLS:
        syms.append(gl.stock_symbol(lib, name))
    syms.append(mic_symbol())
    (PRJ / f"{LIB}.kicad_sym").write_text(dumps(syms) + "\n")
    d = PRJ / f"{LIB}.pretty"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.kicad_mod"):
        f.unlink()
    for name, lib in STOCK_FP.items():
        fp = gl.localize_models(loads((gl.FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").read_text()), PRJ)
        (d / f"{name}.kicad_mod").write_text(dumps(fp) + "\n")
    for fp in (fp_b2b(), fp_finger(), fp_mic(),
               fp_plain_pad(sp.FP_TP_CONTACT, *sp.CONTACT_PAD, "Gold contact pad under a spring finger"),
               fp_fpc(), fp_plain_pad(sp.FP_FLOOR_CONTACT, sp.BC_FLOOR_PAD[1], sp.BC_FLOOR_PAD[0],
                                      "Gold pad under a back cover spring finger"),
               fp_plain_pad(eu.FP_FLOOR_PAD, eu.E.EU_PAD_X[1] - eu.E.EU_PAD_X[0], eu.E.BC_FLOOR_PAD[1],
                            "Gold pad under a back cover spring finger (EU floor, D-41)"),
               fp_round_pad(eu.FP_PIN_PAD, eu.E.FLEX_PAD_D, "Gold pad under a spring pin (EU)")):
        (d / f"{fp[1]}.kicad_mod").write_text(dumps(fp) + "\n")
    (PRJ / "fp-lib-table").write_text(
        f'(fp_lib_table\n\t(version 7)\n\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.pretty")'
        '(options "")(descr "Sensor flex and power jumper footprints"))\n)\n')
    (PRJ / "sym-lib-table").write_text(
        f'(sym_lib_table\n\t(version 7)\n\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")'
        '(options "")(descr "Sensor flex and power jumper symbols"))\n)\n')


# ============================== project + rules ==============================
RULES = {
    sp.FLEX: """(version 1)
# Sensor flex (5 V side only): single-layer polyimide flex.
(rule "Flex edge clearance"
    (constraint edge_clearance (min 0.2mm)))
""",
    sp.COVER: """(version 1)
# Back cover flex (low voltage only): single-layer polyimide flex.
(rule "Flex edge clearance"
    (constraint edge_clearance (min 0.2mm)))
""",
    eu.NAME: """(version 1)
# EU sensor flex (low voltage only): single-layer polyimide flex.
(rule "Flex edge clearance"
    (constraint edge_clearance (min 0.2mm)))
""",
    sp.JUMPER: """(version 1)
# Power jumper (5 V side only): single-layer polyimide flex.
(rule "Flex edge clearance"
    (constraint edge_clearance (min 0.2mm)))
""",
}


def build_project(name):
    pro = {"board": {"design_settings": {"rule_severities": {"lib_footprint_issues": "warning",
                                                             "lib_footprint_mismatch": "warning"}}},
           "meta": {"filename": f"{name}.kicad_pro", "version": 3},
           "schematic": {"meta": {"version": 1}}, "sheets": [["", "Root"]]}
    (PRJ / f"{name}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")
    (PRJ / f"{name}.kicad_dru").write_text(RULES[name])


# ============================== schematics + boards (pcb/tools/kigen.py) ==============================
CTX = kigen.Lib(PRJ, LIB, sp.uid, POWER)


def build_flex():
    bd = Board(CTX, sp.FLEX, 1, sp.FLEX_T, 0.15, 0.15)
    bd.outline(sp.FLEX_OUTLINE, 0.75)
    for ref, p in sp.FLEX_PARTS.items():
        bd.place(ref, p, False)
    pin = {lane: bd.pad_xy("J1", n) for lane, n in sp.CN2_MAP.items()}
    j2x, j3x = sp.FLEX_PARTS["J2"]["pos"][0], sp.FLEX_PARTS["J3"]["pos"][0]
    pad_x0 = j2x - sp.FINGER_PAD[1] / 2
    j3_end = j3x + sp.FINGER_PAD[1] / 2
    jog0, jog1 = sp.LANE_X0 + 0.3, sp.LANE_X0 + 5.3       # step into the low lanes before J2 (shallow)
    up0, up1 = j3_end + 0.6, j3_end + 5.6                 # step back up after J3
    lo = {"GND": -1.42, "SDA": -1.9, "SCL": -2.25, "+3V3": -2.6}   # lanes beside the finger pads
    sda, scl, vdd, vss = (bd.pad_xy("U1", n) for n in ("1", "2", "3", "4"))
    c_vdd, c_gnd = bd.pad_xy("C1", "1"), bd.pad_xy("C1", "2")
    # CN2 fan-out: top row up, bottom row down (inner pins to the outer levels), then parallel
    # diagonals through the neck into the strip lanes; widths: signals 0.12, mic supply 0.15
    width = {"I2S_WS": 0.12, "I2S_SCK": 0.12, "I2S_SD": 0.12, "MIC_GND": 0.15, "MIC_3V3": 0.15, "+5V": 0.3,
             "GND": 0.3, "SDA": 0.15, "SCL": 0.15, "+3V3": 0.2}
    level = {"I2S_WS": 3.70, "I2S_SCK": 3.38, "I2S_SD": 3.06, "MIC_GND": 2.72, "MIC_3V3": 2.37, "+5V": 1.95,
             "GND": -1.95, "SDA": -2.375, "SCL": -2.70, "+3V3": -3.05}
    lane = {"I2S_WS": 1.625, "I2S_SCK": 1.305, "I2S_SD": 0.985, "MIC_GND": 0.65, "MIC_3V3": 0.30, "+5V": -0.1,
            "GND": -0.55, "SDA": -0.945, "SCL": -1.265, "+3V3": -1.61}
    finger_lane = {"+5V": 1.3, "GND": 0.6, "SDA": -0.1, "SCL": -0.7, "+3V3": -1.2}   # strip lanes at the fingers
    d0, d1 = sp.PLUG_LEN, sp.NECK_X - 0.08               # diagonals follow the neck taper
    head = {}
    for ln, (px, py) in pin.items():
        bd.track(ln, min(width[ln], 0.15), [(px, py), (px, level[ln])])
        head[ln] = [(px, level[ln]), (d0, level[ln]), (d1, lane[ln])]
    # microphone (D-29): pins end towards the plug; LR + CONFIG to GND, GND on to the ring between
    # the pad rows; SCK / WS over the top into their pads, SD from the left with the pull-down R1
    mk = {n: bd.pad_xy("MK1", n) for n in ("1", "2", "3", "5", "6", "7")}
    ring_x, ring_y = sp.MIC_XC + (sp.MIC[1] / 2 - 1.0), sp.MIC_FLEX_Y
    r_mid = sum(sp.MIC_RING) / 4
    r1_sd, r1_gnd = bd.pad_xy("R1", "1"), bd.pad_xy("R1", "2")
    c2_vdd, c2_gnd = bd.pad_xy("C2", "1"), bd.pad_xy("C2", "2")
    x_ws, x_sck, x_sd = mk["1"][0] - 2.9, mk["1"][0] - 2.3, r1_sd[0] - 0.6
    bd.track("I2S_WS", 0.12, head["I2S_WS"] + [(x_ws, lane["I2S_WS"]), (x_ws, 3.95), (mk["5"][0], 3.95), mk["5"]])
    bd.track("I2S_SCK", 0.12, head["I2S_SCK"] + [(x_sck, lane["I2S_SCK"]), (x_sck, 3.62), (mk["6"][0], 3.62),
                                                  mk["6"]])
    bd.track("I2S_SD", 0.12, head["I2S_SD"] + [(x_sd, lane["I2S_SD"]), (x_sd, mk["7"][1]), mk["7"]])
    bd.track("I2S_SD", 0.12, [r1_sd, (r1_sd[0], mk["7"][1])])
    x_gj = mk["1"][0] - 0.9
    bd.track("MIC_GND", 0.15, head["MIC_GND"] + [(x_gj - 0.4, lane["MIC_GND"]), (x_gj, mk["1"][1]), mk["1"], mk["2"],
                                              (mk["2"][0], ring_y), (ring_x - r_mid, ring_y)])
    bd.track("MIC_GND", 0.15, [r1_gnd, (r1_gnd[0], lane["MIC_GND"])])
    bd.track("MIC_3V3", 0.15, head["MIC_3V3"] + [(mk["3"][0], lane["MIC_3V3"]), mk["3"]])
    bd.track("MIC_3V3", 0.15, [(mk["3"][0], lane["MIC_3V3"]), (c2_vdd[0], lane["MIC_3V3"]), c2_vdd])
    bd.track("MIC_GND", 0.15, [c2_gnd, (ring_x + r_mid, ring_y)])
    # through lanes step back up to the finger lanes after the microphone, the upper ones first
    step = {ln: c2_vdd[0] + 0.9 + 0.6 * i for i, ln in enumerate(("+5V", "GND", "SDA", "SCL", "+3V3"))}

    def up(ln):
        return [(step[ln], lane[ln]), (step[ln] + 3.0, finger_lane[ln])]
    bd.track("+5V", 0.3, head["+5V"] + up("+5V") + [(pad_x0 + 0.5, 1.3)])
    bd.track("GND", 0.3, head["GND"] + up("GND") + [(jog0, 0.6), (jog1, lo["GND"])])
    bd.track("GND", 0.25, [(jog1, lo["GND"]), (j3x, lo["GND"]), (j3x, 0.0)])
    bd.track("SDA", 0.15, head["SDA"] + up("SDA") + [(jog0, -0.1), (jog1, lo["SDA"])])
    bd.track("SDA", 0.12, [(jog1, lo["SDA"]), (up0, lo["SDA"]), (up1, 0.4)])
    bd.track("SCL", 0.15, head["SCL"] + up("SCL") + [(jog0, -0.7), (jog1, lo["SCL"])])
    bd.track("SCL", 0.12, [(jog1, lo["SCL"]), (up0, lo["SCL"]), (up1, -0.4)])
    bd.track("+3V3", 0.2, head["+3V3"] + up("+3V3") + [(jog0, -1.2)])
    bd.track("+3V3", 0.12, [(jog0, -1.2), (jog1, lo["+3V3"]), (up0, lo["+3V3"]), (up1, -1.2)])
    # SHT45: SDA / SCL straight into the left pads; GND / +3V3 round the body into the right pads
    # (the footprint's keepout only opens at each pad, from the outside)
    xr = vss[0] + 0.9
    bd.track("SDA", 0.15, [(up1, 0.4), sda])
    bd.track("SCL", 0.15, [(up1, -0.4), scl])
    bd.track("GND", 0.3, [(j3_end - 1.0, 1.2), (xr, 1.2), (xr, vss[1]), vss])
    bd.track("GND", 0.3, [(xr, 1.2), (c_gnd[0], 1.2), c_gnd])
    bd.track("+3V3", 0.2, [(up1, -1.2), (xr, -1.2), (xr, vdd[1]), vdd])
    bd.track("+3V3", 0.2, [(xr, -1.2), (c_vdd[0], -1.2), c_vdd])
    # fab notes: folds, stiffeners, placeholder warning
    h = sp.HALF
    for i, s in enumerate(sp.FOLDS):
        bd.shape(P.SHAPE_T_SEGMENT, P.Cmts_User, 0.1, (s - h, -h), (s + h, h))
        bd.text(f"FOLD {i + 1}: 45 deg, flips the strip", s, h + 1.2, P.Cmts_User, 0.7)
    for (x0, y0), (x1, y1) in sp.STIFFENERS:
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            bd.shape(P.SHAPE_T_SEGMENT, P.User_1, 0.1, a, b)
        bd.text(f"STIFFENER FR4 {sp.STIFF_T} mm, back side", (x0 + x1) / 2, y1 + 0.9, P.User_1, 0.6)
    bd.text(f"MK1 PORT: {sp.MIC_FLEX_HOLE_D} mm hole through flex + stiffener, adhesive gasket ring to the skin",
            sp.MIC_XC, sp.MIC_SEC_W + 1.0, P.Cmts_User, 0.6)
    if not sp.CN2_CONFIRMED:
        bd.text("J1 FOOTPRINT AND PIN MAP ARE PLACEHOLDERS - DO NOT FABRICATE", 40.0, -4.5, P.Cmts_User, 1.0)
    bd.save()


def build_eu_flex():
    """EU sensor flex (eu_flex_parts.py): CN2 fan-out, lanes, microphone, pin pads, tongue, SHT45."""
    bd = Board(CTX, eu.NAME, 1, sp.FLEX_T, 0.15, 0.15)
    bd.outline(eu.FLEX_OUTLINE, 0.75)
    for ref, p in eu.PARTS.items():
        bd.place(ref, p, False)
    j1 = {n: bd.pad_xy("J1", n) for n in eu.CN2_MAP}
    # lanes in the strip (+Y inwards): power / SHT45 group above, microphone group below
    lane = {"19": 1.65, "21": 1.225, "23": 0.835, "25": 0.51, "27": 0.21, "29": -0.115,
            "28": -0.425, "26": -0.725, "24": -1.025, "22": -1.32, "20": -1.62}
    level = {"19": 3.65, "21": 3.25, "23": 2.87, "25": 2.53, "27": 2.23, "29": 1.90,
             "20": -3.65, "22": -3.33, "24": -3.02, "26": -2.72, "28": -2.42}
    width = {"GND": 0.3, "GND_SHT": 0.2, "+5V": 0.25, "SDA": 0.15, "SCL": 0.15, "+3V3": 0.2, "MIC_3V3": 0.15, "MIC_GND": 0.15,
             "I2S_SD": 0.12, "I2S_SCK": 0.12, "I2S_WS": 0.12}
    wn = {n: width[net] for n, net in eu.CN2_MAP.items()}
    hw = {n: (0.2 if n in ("19", "21") else 0.15 if n == "23" else 0.12) for n in eu.CN2_MAP}   # fan-out widths
    d0, d1 = eu.PLUG_LEN, eu.NECK_X - 0.08
    head = {}
    for n, (px, py) in j1.items():
        head[n] = [(px, py), (px, level[n]), (d0, level[n]), (d1, lane[n])]
        bd.track(eu.CN2_MAP[n], hw[n], head[n])
        head[n] = [(d1, lane[n])]
    # microphone: WS / SCK into the inner pad column from above, SD from below through the gap with R1 to
    # MIC_GND; MIC_GND / MIC_3V3 under the outer column (C2 across them), GND on to the port ring
    for ref in ("R1", "C2"):                                   # pad 2 up (towards the strip), pad 1 down
        f = bd.fps[ref]
        for rot in (90, 270):
            f.SetOrientationDegrees(rot)
            if bd.pad_xy(ref, "2")[1] > bd.pad_xy(ref, "1")[1]:
                break
    mk = {n: bd.pad_xy("MK1", n) for n in ("1", "2", "3", "5", "6", "7")}
    ring = (eu.MIC_XC + (sp.MIC[1] / 2 - 1.0), eu.MIC_Y_FLAT)   # port centre (the GND ring round it)
    r1_sd, r1_gnd = bd.pad_xy("R1", "2"), bd.pad_xy("R1", "1")
    c2_gnd, c2_3v3 = bd.pad_xy("C2", "2"), bd.pad_xy("C2", "1")
    y_sd, y_mg, y_m3 = r1_sd[1] + 0.55, c2_gnd[1], c2_3v3[1]
    xa = eu.MX0 + 0.5
    bd.track("MIC_3V3", 0.15, head["20"] + [(xa, lane["20"]), (xa + 0.35, y_m3), (mk["3"][0], y_m3), mk["3"]])
    bd.track("MIC_GND", 0.15, head["22"] + [(xa + 0.45, lane["22"]), (xa + 0.8, y_mg), (mk["2"][0], y_mg), mk["2"]])
    bd.track("MIC_GND", 0.15, [(mk["1"][0], y_mg), mk["1"]])
    bd.track("MIC_GND", 0.15, [(r1_gnd[0], y_mg), r1_gnd])
    bd.track("MIC_GND", 0.15, [mk["2"], (mk["2"][0], ring[1] - 0.4), (ring[0] - 0.5, ring[1] - 0.4)])
    bd.track("I2S_SD", 0.12, head["24"] + [(xa + 0.9, lane["24"]), (xa + 1.25, y_sd), (mk["7"][0], y_sd), mk["7"]])
    bd.track("I2S_SD", 0.12, [(r1_sd[0], y_sd), r1_sd])
    bd.track("I2S_SCK", 0.12, head["26"] + [(mk["6"][0], lane["26"]), mk["6"]])
    bd.track("I2S_WS", 0.12, head["28"] + [(mk["5"][0], lane["28"]), mk["5"]])
    # pin pads (GND first, then +5V) and the tongue between them; the through lanes step down under the pads
    tp1, tp2, tp3, tp4 = (bd.pad_xy(r, "1") for r in ("TP1", "TP2", "TP3", "TP4"))
    shift = 1.125                                              # +5V passes under the GND pin pad
    low = {n: lane[n] - shift for n in ("21", "23", "25", "27", "29")}
    jog = {n: eu.PX0 - 9.0 + 1.5 * k for k, n in enumerate(("29", "27", "25", "23", "21"))}   # bottom lane first
    bd.track("GND", 0.3, head["19"] + [(tp1[0] - 1.6, lane["19"]), tp1])
    for n in low:
        bd.track(eu.CN2_MAP[n], wn[n], head[n] + [(jog[n], lane[n]), (jog[n] + shift, low[n])])
    bd.track("+5V", wn["21"], [(jog["21"] + shift, low["21"]), (tp2[0] - 1.8, low["21"]), tp2])
    g_x, p_x = eu.TONGUE_LANES
    top = eu.PAD_Y[1] + 0.3
    bd.track("GND", 0.3, [tp1, (g_x, top), (g_x, tp4[1]), tp4])
    bd.track("+5V", 0.3, [tp2, (p_x, top), (p_x, tp3[1]), tp3])
    # SHT45 tail: lanes back up to the tail positions, then as on the NA flex
    sda, scl, vdd, vss = (bd.pad_xy("U1", n) for n in ("1", "2", "3", "4"))
    c_vdd, c_gnd = bd.pad_xy("C1", "1"), bd.pad_xy("C1", "2")
    tail = {"23": 1.2, "25": 0.4, "27": -0.4, "29": -1.2}
    u1 = eu.PX1 + 7.0
    for k, (n, y) in enumerate(tail.items()):                  # top lane up first
        u = eu.PX1 + 1.0 + 1.8 * k
        bd.track(eu.CN2_MAP[n], wn[n], [(jog[n] + shift, low[n]), (u, low[n]), (u + (y - low[n]), y), (u1, y)])
    xr = vss[0] + 0.9
    bd.track("SDA", 0.15, [(u1, 0.4), sda])
    bd.track("SCL", 0.15, [(u1, -0.4), scl])
    bd.track("GND_SHT", 0.2, [(u1, 1.2), (xr, 1.2), (xr, vss[1]), vss])
    bd.track("GND_SHT", 0.2, [(xr, 1.2), (c_gnd[0], 1.2), c_gnd])
    bd.track("+3V3", 0.2, [(u1, -1.2), (xr, -1.2), (xr, vdd[1]), vdd])
    bd.track("+3V3", 0.2, [(xr, -1.2), (c_vdd[0], -1.2), c_vdd])
    # fab notes: folds, the tongue's fold, stiffeners, placeholder warning
    h = eu.HALF
    for i, x in enumerate(eu.FOLDS):
        bd.shape(P.SHAPE_T_SEGMENT, P.Cmts_User, 0.1, (x - h, -h), (x + h, h))
        bd.text(f"FOLD {i + 1}: 45 deg, flips the strip", x, h + 1.2, P.Cmts_User, 0.7)
    bd.shape(P.SHAPE_T_SEGMENT, P.Cmts_User, 0.1, *eu.FOLD_LINE)
    bd.text("TONGUE FOLD 45 deg (pads face up)", eu.FOLD_LINE[1][0] + 3.0, eu.FOLD_LINE[1][1], P.Cmts_User, 0.6)
    for (x0, y0), (x1, y1) in eu.STIFFENERS:
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            bd.shape(P.SHAPE_T_SEGMENT, P.User_1, 0.1, a, b)
    if not eu.CN2_CONFIRMED:
        bd.text("J1 FOOTPRINT AND PIN MAP ARE PLACEHOLDERS - DO NOT FABRICATE", 40.0, -6.5, P.Cmts_User, 1.0)
    bd.save()


def build_jumper():
    bd = Board(CTX, sp.JUMPER, 2, sp.JUMPER_T, 0.15, 0.2)
    bd.outline(sp.JUMPER_OUTLINE, 0.3)
    for ref, p in sp.JUMPER_PARTS.items():
        bd.place(ref, p, False)
    w = sp.TRACK_W
    bar = sp.FPC_PAD[0] + 0.45                           # bar joining each net's three contacts, past the pads
    for net, ns, y in (("GND", (1, 2, 3), sp.GND_Y), ("+5V", (4, 5, 6), sp.P5_Y)):
        ends = [bd.pad_xy("J1", str(n)) for n in ns]
        for x, yy in ends:
            bd.track(net, 0.3, [(x + sp.FPC_PAD[0] / 2 - 0.2, yy), (bar, yy)])
        bd.track(net, 0.3, [(bar, ends[0][1]), (bar, ends[-1][1])])
        bd.track(net, w, [(bar, y), (bar + 1.0, y)])
    tp1, tp2 = bd.pad_xy("TP1", "1"), bd.pad_xy("TP2", "1")
    bd.track("+5V", w, [(bar + 1.0, sp.P5_Y), (tp1[0] - sp.CONTACT_PAD[0] / 2 + 0.5, sp.P5_Y)])
    bd.track("GND", w, [(bar + 1.0, sp.GND_Y), (tp2[0], sp.GND_Y), tp2])
    # battery-free tongue (D-41): GND on F off the edge lane; +5V from TP1 over to a via, under the GND lane on B;
    # on the floor GND drops to B under the +5V pad, each net back on F into its pad
    tp3, tp4 = bd.pad_xy("TP3", "1"), bd.pad_xy("TP4", "1")
    g_x, p_x = sp.TONGUE_LANES
    g_turn, p_turn, y_via = sp.TONGUE_TURN
    tw = 0.3
    via_p5, via_g1 = (p_x, tp1[1]), (sp.pe_x(y_via), sp.tongue_y(g_turn))
    via_p5f, via_g2 = (sp.pe_x(y_via), sp.tongue_y(p_turn)), (sp.pe_x(-1.0), sp.tongue_y(sp.BC_FINGERS[1][0]))
    bd.track("+5V", tw, [(tp1[0] + sp.CONTACT_PAD[0] / 2 - 0.5, tp1[1]), via_p5])
    bd.track("+5V", tw, [via_p5, (p_x, sp.tongue_y(p_turn)), via_p5f], P.B_Cu)
    bd.track("+5V", tw, [via_p5f, (tp3[0], via_p5f[1])])
    bd.track("GND", tw, [(g_x, sp.GND_Y), (g_x, sp.tongue_y(g_turn)), via_g1])
    y_b = sp.tongue_y(sp.BC_FINGERS[0][0] + 1.9)
    bd.track("GND", tw, [via_g1, (via_g1[0] + 0.6, y_b), (via_g2[0] - 0.6, y_b), via_g2], P.B_Cu)
    bd.track("GND", tw, [via_g2, (tp4[0], via_g2[1])])
    for net, xy in (("+5V", via_p5), ("+5V", via_p5f), ("GND", via_g1), ("GND", via_g2)):
        bd.via(net, *xy)
    # fab notes: stiffeners, contact side
    for (x0, y0), (x1, y1) in sp.JUMPER_STIFFENERS:
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            bd.shape(P.SHAPE_T_SEGMENT, P.User_1, 0.1, a, b)
    bd.text(f"STIFFENER PI, back side: total {sp.END_T} mm (MEASURE: FH12 FPC spec)", sp.END_L / 2 + 6.0, -3.0,
            P.User_1, 0.6)
    bd.text(f"STIFFENER FR4, back side: total {sp.TARGET_T} mm", sp.PE_X0 + sp.PE_LEN / 2, -3.0, P.User_1, 0.6)
    bd.text("J1: exposed gold contacts; check the side against J2 (FH12) on a sample", 20.0, 3.0,
            P.Cmts_User, 0.7)
    bd.text(f"Flat length {sp.JUMPER_LEN:.1f} mm incl. {sp.JUMPER_SERVICE:.0f} mm service loop (Z-fold)",
            sp.JUMPER_LEN / 2, 3.0, P.Cmts_User, 0.7)
    bd.save()


def build_cover():
    bd = Board(CTX, sp.COVER, 1, sp.FLEX_T, 0.15, sp.COVER_TRACK)
    bd.outline(sp.COVER_OUTLINE, 0.5)
    for ref, p in sp.COVER_PARTS.items():
        bd.place(ref, p, False)
    w = sp.COVER_TRACK
    f1, f2, vbat, gnd = (bd.pad_xy(r, "1") for r in ("J1", "J2", "J3", "J4"))
    x_in, x_out = sp.COVER_LANES
    y_band = sp.COVER_BEND_Y - sp.BC_LANE_H
    # end fingers: long axis across the bend line, bend end away from it (up in the cover)
    for ref in ("J3", "J4"):
        f = bd.fps[ref]
        for rot in (0, 90, 180, 270):
            f.SetOrientationDegrees(rot)
            g = [g for g in f.GraphicalItems() if g.GetLayer() == P.F_Fab and g.GetShape() == P.SHAPE_T_SEGMENT][0]
            (sx, sy), (ex, ey) = kigen.mm(g.GetStart()), kigen.mm(g.GetEnd())
            mark = ((sx + ex) / 2, (sy + ey) / 2)
            c = bd.pad_xy(ref, "1")
            if abs(mark[0] - c[0]) < 0.6 and mark[1] < c[1] - 1.0:
                break
        else:
            raise RuntimeError(f"no orientation of {ref} puts its bend end away from the bend line")
    # regulator: IN, GND, EN on the upper row (IN towards the inner lane), OUT under IN, NC under EN
    u = bd.fps["U1"]
    for rot in (0, 90, 180, 270):
        u.SetOrientationDegrees(rot)
        p_in, p_gnd, p_en, p_out = (bd.pad_xy("U1", n) for n in ("1", "2", "3", "5"))
        if abs(p_in[1] - p_en[1]) < 0.01 and p_in[1] > p_out[1] and p_in[0] > p_en[0]:
            break
    else:
        raise RuntimeError("no orientation of U1 puts IN / GND / EN on the upper row, IN inside")
    c3_gnd, c3_5v = bd.pad_xy("C3", "1"), bd.pad_xy("C3", "2")
    c4_gnd, c4_3v3 = bd.pad_xy("C4", "1"), bd.pad_xy("C4", "2")
    y_tie = c3_5v[1]                                     # +5V over the top: IN, EN, C3
    y_low = c4_gnd[1] + 0.6                              # GND under U1, from the outer lane to the GND pin
    x_left = sp._xs0 + 0.8                               # outer GND lane past the regulator
    # +5V: inner lane past the GND finger, into IN; EN and C3 tied over the top
    x5 = -(sp.BC_STRIP[0] + 0.5)                         # +5V lane inside the pad section's inner edge
    bd.track("+5V", w, [f1, (x5, f1[1]), (x5, y_tie), (p_in[0], y_tie), p_in])
    bd.track("+5V", w, [(p_in[0], y_tie), (p_en[0], y_tie), p_en])
    bd.track("+5V", w, [(p_en[0], y_tie), c3_5v])
    # GND: finger down the outer side, C3, under U1 to its GND pin (between NC and OUT), C4, run, J4
    bd.track("GND", w, [f2, (x_left, f2[1] - 2.0), (x_left, y_low), (p_gnd[0], y_low)])
    bd.track("GND", w, [c3_gnd, (x_left, c3_gnd[1])])
    bd.track("GND", w, [p_gnd, (p_gnd[0], y_low), c4_gnd, (x_out, c4_gnd[1] - 0.6), (x_out, gnd[1] + 2.0), gnd])
    # +3V3: OUT, C4, inner lane down the run, across the band under the PCB strip, into VBAT
    bd.track("+3V3", w, [p_out, (p_out[0], c4_3v3[1] + 0.7), c4_3v3, (x_in, c4_3v3[1] - 0.6), (x_in, y_band),
                         (vbat[0], y_band), vbat])
    bd.shape(P.SHAPE_T_SEGMENT, P.Cmts_User, 0.1, (sp._xr0, sp.COVER_BEND_Y), (sp._xr1, sp.COVER_BEND_Y))
    bd.text("BEND 90 deg, copper outside", 0.0, sp.COVER_BEND_Y + 1.2, P.Cmts_User, 0.6)
    for (a0, b0), (a1, b1) in sp.COVER_STIFF:
        for a, b in (((a0, b0), (a1, b0)), ((a1, b0), (a1, b1)), ((a1, b1), (a0, b1)), ((a0, b1), (a0, b0))):
            bd.shape(P.SHAPE_T_SEGMENT, P.User_1, 0.1, a, b)
        bd.text(f"STIFFENER FR4 {sp.BC_END_T} mm, back side (cut to the outline)", (a0 + a1) / 2, b0 - 1.0, P.User_1, 0.6)
    for (a0, b0), (a1, b1) in sp.COVER_PAD_STIFF:
        for a, b in (((a0, b0), (a1, b0)), ((a1, b0), (a1, b1)), ((a1, b1), (a0, b1)), ((a0, b1), (a0, b0))):
            bd.shape(P.SHAPE_T_SEGMENT, P.User_1, 0.1, a, b)
    bd.text(f"STIFFENER FR4 {sp.BC_PAD_STIFF_T} mm, back side, with the peg holes", sp._xs0 - 4.0, sp._yt - 2.0,
            P.User_1, 0.6, 90)
    for x, y in sp.COVER_PEG_HOLES:                       # heat-stake peg holes through flex and stiffener (D-45)
        bd.shape(P.SHAPE_T_CIRCLE, P.Edge_Cuts, 0.05, (x, y), (x + sp.BC_PEG_HOLE / 2, y))
    if not sp.COVER_CONFIRMED:
        bd.text("POSITIONS REF / MEASURE - DO NOT FABRICATE", 0.0, 2.0, P.Cmts_User, 0.9)
    bd.save()


def main():
    PRJ.mkdir(parents=True, exist_ok=True)
    build_libs()
    for name in (sp.FLEX, sp.JUMPER, sp.COVER, eu.NAME):
        build_project(name)
    status = "CN2 mate and contact map UNCONFIRMED (placeholder) - do not fabricate" if not sp.CN2_CONFIRMED \
        else "CN2 mate confirmed"
    build_schematic(CTX, sp.FLEX, sp.FLEX_PARTS, ("+5V", "+3V3", "GND", "MIC_3V3", "MIC_GND"),
                    "Smart wall plate - sensor flex", sp.REV,
                    [status, "Generated by pcb/sensor/tools/gen_sensor.py - edit sensor_parts.py"],
                    "Sensor flex (docs/DESIGN.md D-27): single layer, two 45 deg folds.\n"
                    "J1 mates the MSR-2's rear connector CN2 (MSR-2 powered through its 5V pin).\n"
                    "J2, J3: Harwin S7081-42R spring fingers on the target board (+5 V, GND from the wiring board).\n"
                    "U1: SHT45 on the flex tail, I2C on the MSR-2 bus (SDA = IO1, SCL = IO0).\n"
                    "MK1: I2S microphone (D-29), left channel; SCK = IO4, WS = IO6, SD = IO7 (CN2 contacts placeholder).\n"
                    "MIC_3V3 / MIC_GND: the microphone's own CN2 contacts, joined to +3V3 / GND on the MSR-2.")
    build_schematic(CTX, sp.JUMPER, sp.JUMPER_PARTS, ("+5V", "GND"), "Smart wall plate - power jumper", sp.REV,
                    ["Generated by pcb/sensor/tools/gen_sensor.py - edit sensor_parts.py"],
                    "5 V flex jumper (docs/DESIGN.md D-27, R9): J1 plugs into the wiring board's J2\n"
                    "(Hirose FH12-6S, slide lock); TP1 / TP2: gold pads on the insert shelf under the\n"
                    "sensor flex's spring fingers. No wires, no solder joints between parts.")
    build_schematic(CTX, sp.COVER, sp.COVER_PARTS, ("+5V", "GND"), "Smart wall plate - back cover flex", sp.REV,
                    ["Generated by pcb/sensor/tools/gen_sensor.py - edit sensor_parts.py"],
                    "Replacement back cover flex (docs/DESIGN.md D-35): J1 / J2 spring fingers on the plate's floor\n"
                    "pads (+5V, GND), U1 3.3 V regulator, J3 / J4 spring fingers on the BILRESA's VBAT plate / GND leaf\n"
                    "spring. One bend, single layer.")
    # board files: build in memory, save (KiCad 9 python cannot refill/reload safely in one board)
    build_schematic(CTX, eu.NAME, eu.PARTS, ("+5V", "+3V3", "GND", "GND_SHT", "MIC_3V3", "MIC_GND"),
                    "Smart wall plate - EU sensor flex", sp.REV,
                    [status, "Generated by pcb/sensor/tools/gen_sensor.py - edit eu_flex_parts.py"],
                    "EU sensor flex (docs/DESIGN.md D-30, D-41): single layer, two 45 deg folds and the tongue's.\n"
                    "J1 mates the MSR-2's rear connector CN2 (MSR-2 powered through its 5V pin).\n"
                    "TP1 / TP2: pads under the 5 V board's spring pins (GND, +5 V).\n"
                    "TP3 / TP4: floor pads under the replacement back cover's fingers (+5 V, GND), on the tongue.\n"
                    "U1: SHT45, I2C on the MSR-2 bus; MK1: I2S microphone (D-29), left channel.\n"
                    "GND_SHT / MIC_3V3 / MIC_GND: their own CN2 contacts, joined to GND / +3V3 on the MSR-2.")
    build_flex()
    build_jumper()
    build_cover()
    build_eu_flex()


if __name__ == "__main__":
    main()
