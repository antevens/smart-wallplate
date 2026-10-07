"""Build the project-local libraries (kicad/wiring_board.kicad_sym and .pretty).

Stock KiCad parts are copied so the project is self-contained. Three footprints
are built from datasheets: the Marquardt 1802.2504 rocker, the WAGO 2604-1106
terminal block and the TDK CU4032 SMD varistor.
"""
import copy
import os
import shutil
import sys
from pathlib import Path
from sexpr import loads, dumps, find, first, Sym, S
from parts import (LIB, FP_ROCKER, FP_WAGO, FP_IRM, FP_FUSE, FP_MOV, FP_J2, FP_C1, FP_MH_PE, FP_MH, FP_ANT, FP_KICAD,
                   ANT_LOGO_H,
                   MOUNT_D, MOUNT_PAD, POST_SHOULDER_D, POST_HEAD_D, ROCKER_DS, WAGO_DS, CU_DS, BOARD, PS1_PINS)

_BASES = ["/usr/share/kicad", "/usr/local/share/kicad", "/opt/kicad/share/kicad",
          "/var/lib/flatpak/app/org.kicad.KiCad/current/active/files/share/kicad",
          "~/.local/share/flatpak/app/org.kicad.KiCad/current/active/files/share/kicad",
          "/Applications/KiCad/KiCad.app/Contents/SharedSupport"]
_cli = shutil.which("kicad-cli")
if _cli:
    _BASES.insert(0, str(Path(_cli).resolve().parents[1] / "share" / "kicad"))


def stock_dir(kind, env):
    """kind: 'symbols' or 'footprints'; env: SYMBOL or FOOTPRINT."""
    cands = [os.environ.get(f"KICAD{v}_{env}_DIR", "") for v in ("9", "8", "")]
    cands += [str(Path(b).expanduser() / kind) for b in _BASES]
    for c in cands:
        if c and Path(c).is_dir():
            return Path(c)
    return None


SYM_DIR = stock_dir("symbols", "SYMBOL")
FP_DIR = stock_dir("footprints", "FOOTPRINT")
PRJ = Path(__file__).resolve().parents[1] / "kicad"

# (stock lib, stock name, project name)
SYMBOLS = [
    ("Converter_ACDC", "IRM-03-5", "IRM-03-5"),
    ("Device", "Fuse", "Fuse"),
    ("Device", "Varistor", "Varistor"),
    ("Device", "C", "C"),
    ("Connector", "Screw_Terminal_01x06", "Screw_Terminal_01x06"),
    ("Connector_Generic", "Conn_01x02", "Conn_01x02"),
    ("Switch", "SW_DPST", "SW_DPST_Marquardt"),
    ("power", "+5V", "+5V"),
    ("power", "GND", "GND"),
    ("power", "PWR_FLAG", "PWR_FLAG"),
]
STOCK_FP = {
    FP_IRM: ("Converter_ACDC", FP_IRM),
    FP_FUSE: ("Fuse", FP_FUSE),
    FP_J2: ("Connector_JST", FP_J2),
    FP_C1: ("Capacitor_SMD", FP_C1),
    FP_KICAD: ("Symbol", FP_KICAD),
}
ART = Path(__file__).resolve().parents[1] / "art"
# SW_DPST pins 1-2 and 3-4 are the two poles; the Marquardt drawing numbers them 1-1a and 2-2a
ROCKER_PINS = {"1": "1", "2": "1a", "3": "2", "4": "2a"}


def stock_symbol(lib, name):
    """Return a flattened copy of a stock symbol (resolves `extends`)."""
    tree = loads((SYM_DIR / f"{lib}.kicad_sym").read_text())
    syms = {s[1]: s for s in find(tree, "symbol")}
    s = copy.deepcopy(syms[name])
    ext = first(s, "extends")
    if not ext:
        return s
    base = copy.deepcopy(syms[ext[1]])
    bname = base[1]
    base[1] = name
    dprops = {p[1]: p for p in find(s, "property")}
    for i, x in enumerate(base):
        if isinstance(x, list) and x and x[0] == "property" and x[1] in dprops:
            base[i] = dprops.pop(x[1])
    for p in dprops.values():
        base.insert(len(base) - len(find(base, "symbol")) - 1, p)
    for sub in find(base, "symbol"):
        sub[1] = sub[1].replace(bname, name, 1)
    return base


def renumber_rocker(sym):
    """Rename pin numbers and the unit names, set datasheet fields."""
    def walk(node):
        for x in node:
            if isinstance(x, list) and x:
                if x[0] == "pin":
                    num = first(x, "number")
                    num[1] = ROCKER_PINS[num[1]]
                else:
                    walk(x)
    walk(sym)
    for p in find(sym, "property"):
        if p[1] == "Datasheet":
            p[2] = ROCKER_DS
        if p[1] == "Description":
            p[2] = "Marquardt 1802.2504 DPST rocker: 1-1a one pole, 2-2a the other"
        if p[1] == "ki_fp_filters":
            p[2] = "Marquardt*"


def build_symbols():
    out = [Sym("kicad_symbol_lib"), S("version", Sym("20241209")), S("generator", "gen_libs"),
           S("generator_version", "9.0")]
    for lib, name, new in SYMBOLS:
        s = stock_symbol(lib, name)
        old = s[1]
        s[1] = new
        for sub in find(s, "symbol"):
            sub[1] = sub[1].replace(old, new, 1)
        if new == "SW_DPST_Marquardt":
            renumber_rocker(s)
        out.append(s)
    (PRJ / f"{LIB}.kicad_sym").write_text(dumps(out) + "\n")


# ---------------- footprints built from datasheets ----------------
def _fp(name, descr, tags, attr, items):
    head = [Sym("footprint"), name, S("version", Sym("20241229")), S("generator", "gen_libs"),
            S("generator_version", "9.0"), S("layer", "F.Cu"), S("descr", descr), S("tags", tags)]
    props = [S("property", "Reference", "REF**", S("at", 0, 0, 0), S("layer", "F.SilkS"),
               S("effects", S("font", S("size", 1, 1), S("thickness", 0.15)))),
             S("property", "Value", name, S("at", 0, 0, 0), S("layer", "F.Fab"),
               S("effects", S("font", S("size", 1, 1), S("thickness", 0.15))))]
    return head + props + [S("attr", Sym(attr))] + items + [S("embedded_fonts", Sym("no"))]


def rect(x0, y0, x1, y1, layer, w):
    return S("fp_rect", S("start", x0, y0), S("end", x1, y1),
             S("stroke", S("width", w), S("type", Sym("solid"))), S("fill", Sym("no")), S("layer", layer))


def tht(num, x, y, shape, sx, sy, drill):
    return S("pad", num, Sym("thru_hole"), Sym(shape), S("at", x, y), S("size", sx, sy),
             S("drill", drill), S("layers", "*.Cu", "*.Mask"))


def smd(num, x, y, sx, sy):
    return S("pad", num, Sym("smd"), Sym("rect"), S("at", x, y), S("size", sx, sy),
             S("layers", "F.Cu", "F.Paste", "F.Mask"))


def body(w, h, cx=0.0, cy=0.0, crt=0.25, silk=True):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    out = [rect(x0, y0, x1, y1, "F.Fab", 0.1), rect(x0 - crt, y0 - crt, x1 + crt, y1 + crt, "F.CrtYd", 0.05)]
    if silk:
        out.append(rect(x0 - 0.12, y0 - 0.12, x1 + 0.12, y1 + 0.12, "F.SilkS", 0.12))
    return out


def fp_rocker():
    # Marquardt drawing 1802.2504 rev g (recommended hole layout), mounted turned 90 degrees:
    # poles 10.2 mm apart along x (pole 1 = 1/1a at -x, pole 2 = 2/2a at +x), in/switched 7 mm
    # apart along y (1, 2 at +y; 1a, 2a at -y); holes 1.3 (+0.1) mm, pins 0.8 mm; body below the
    # panel 22 x 18.6 mm. Pin numbering per the DPST schematic: confirm on a sample.
    items = [tht("1", -5.1, 3.5, "circle", 2.4, 2.4, 1.4), tht("1a", -5.1, -3.5, "circle", 2.4, 2.4, 1.4),
             tht("2", 5.1, 3.5, "circle", 2.4, 2.4, 1.4), tht("2a", 5.1, -3.5, "circle", 2.4, 2.4, 1.4)]
    items += body(22.0, 18.6, silk=False)
    items.append(S("model", "${KIPRJMOD}/3d/Marquardt_1802.2504.step",
                   S("offset", S("xyz", 0, 0, 0)), S("scale", S("xyz", 1, 1, 1)), S("rotate", S("xyz", 0, 0, 0))))
    return _fp(FP_ROCKER, f"Rocker switch DPST, PCB pins 0.8 mm, holes 1.3 mm on 10.2 x 7 mm grid, "
               f"body 22x18.6 mm, flange 24x21 mm, PCB seat 16.2 mm below the panel face; {ROCKER_DS}",
               "rocker switch DPST Marquardt 1800",
               "through_hole", items)


def fp_wago():
    # WAGO 2604-1106 (datasheet page): 6-pole, pitch 5 mm, 2 solder pins per potential,
    # pins 0.8 x 1 mm, drilled hole 1.3 (+0.1) mm, L = (poles - 1) x 5 + 7.4 = 32.4 mm, depth 19.2 mm.
    # Pin rows at y 0 and -5 and the body offset follow the 2601 series footprint (same family);
    # NOT confirmed against the 2604 dimension drawing.
    items = []
    for i in range(6):
        x = i * 5.0 - 12.5
        for y in (0.0, -5.0):
            shape = "rect" if i == 0 and y == 0.0 else "oval"
            items.append(tht(str(i + 1), x, y, shape, 1.8, 2.6, 1.3))
    items += body(32.4, 19.2, cy=(-12.17 + 7.03) / 2)
    items.append(S("model", "${KIPRJMOD}/3d/WAGO_2604-1106.step",
                   S("offset", S("xyz", 0, 0, 0)), S("scale", S("xyz", 1, 1, 1)), S("rotate", S("xyz", 0, 0, 0))))
    return _fp(FP_WAGO, f"WAGO 2604-1106 PCB terminal block, push-in lever, 6-pole, P5.00 mm, 4 mm2, "
               f"entry parallel to PCB (entry side -y), 400 V III/2, {WAGO_DS}; pin rows inferred from "
               "the 2601 series, confirm with the WAGO drawing", "WAGO 2604 terminal block push-in",
               "through_hole", items)


def fp_ant_logo():
    """The ant logo from pcb/art (the author's own artwork, KiCad 5 format), centred and scaled
    to ANT_LOGO_H tall; stroke widths scale with it."""
    src = loads((ART / "Ant_Logo_SilkScreen.kicad_mod").read_text())
    lines = [(float(first(x, "start")[1]), float(first(x, "start")[2]), float(first(x, "end")[1]),
              float(first(x, "end")[2]), float(first(x, "width")[1])) for x in find(src, "fp_line")]
    xs = [v for l in lines for v in (l[0], l[2])]
    ys = [v for l in lines for v in (l[1], l[3])]
    k = ANT_LOGO_H / (max(ys) - min(ys) + lines[0][4])
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    items = [S("fp_line", S("start", round((x0 - cx) * k, 4), round((y0 - cy) * k, 4)),
               S("end", round((x1 - cx) * k, 4), round((y1 - cy) * k, 4)),
               S("stroke", S("width", round(w * k, 4)), S("type", Sym("solid"))), S("layer", "F.SilkS"))
             for x0, y0, x1, y1, w in lines]
    return _fp(FP_ANT, f"Ant logo, {ANT_LOGO_H} mm, from pcb/art/Ant_Logo_SilkScreen.kicad_mod", "logo ant",
               "board_only exclude_from_pos_files exclude_from_bom allow_missing_courtyard", items)


def fp_mount(plated):
    """Hole for one of the insert's snap posts: plated with a copper ring (net assigned on the
    board), or unplated. The post's shoulder (front) and snap head (back) sit on the ring."""
    circ = lambda layer, r, w: S("fp_circle", S("center", 0, 0), S("end", r, 0),
                                 S("stroke", S("width", w), S("type", Sym("solid"))), S("fill", Sym("no")),
                                 S("layer", layer))
    if plated:
        items = [tht("1", 0, 0, "circle", MOUNT_PAD, MOUNT_PAD, MOUNT_D)]
        name, kind = FP_MH_PE, "plated, copper ring"
    else:
        items = [S("pad", "", Sym("np_thru_hole"), Sym("circle"), S("at", 0, 0), S("size", MOUNT_D, MOUNT_D),
                   S("drill", MOUNT_D), S("layers", "*.Cu", "*.Mask"))]
        name, kind = FP_MH, "unplated"
    # courtyards: the post's shoulder on the front, the ring or snap head on the back
    items += [circ("F.CrtYd", POST_SHOULDER_D / 2 + 0.25, 0.05),
              circ("B.CrtYd", max(MOUNT_PAD, POST_HEAD_D) / 2 + 0.25, 0.05),
              circ("F.Fab", POST_SHOULDER_D / 2, 0.1)]
    return _fp(name, f"Mounting hole {MOUNT_D} mm for the insert's snap posts, {kind} (docs/DESIGN.md D-28)",
               "mounting hole snap post", "through_hole board_only exclude_from_pos_files exclude_from_bom", items)


def fp_mov():
    # TDK SIOV-CU4032K275G2K1 (B72660M0271K093): body 10.2 x 8.0 x 4.5 mm; solder pads
    # A = 3.5 (pad height), B = 2.8 (pad width), C = 6.5 (gap). The datasheet also gives
    # D = 10.1, which disagrees with B + C + B = 12.1; the larger gap is used.
    pitch = 6.5 + 2.8
    items = [smd("1", -pitch / 2, 0, 2.8, 3.5), smd("2", pitch / 2, 0, 2.8, 3.5)]
    items += body(10.2, 8.0, crt=0.5, silk=False)
    items += [rect(-6.3, -4.3, 6.3, 4.3, "F.SilkS", 0.12)]
    return _fp(FP_MOV, f"TDK SMD disk varistor CU4032 (10.2x8.0x4.5 mm), pads per datasheet {CU_DS} "
               "(A 3.5, B 2.8, C 6.5 mm)", "varistor SIOV CU4032", "smd", items)


def build_footprints():
    d = PRJ / f"{LIB}.pretty"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for new, (lib, name) in STOCK_FP.items():
        fp = loads((FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").read_text())
        fp[1] = new
        if new == FP_IRM:
            trim_irm_silk(fp)
        if new == FP_KICAD:                 # no schematic symbol: keep it out of the parity check
            first(fp, "attr").insert(1, Sym("board_only"))
        (d / f"{new}.kicad_mod").write_text(dumps(fp) + "\n")
    for fp in (fp_rocker(), fp_wago(), fp_mov(), fp_mount(True), fp_mount(False), fp_ant_logo()):
        (d / f"{fp[1]}.kicad_mod").write_text(dumps(fp) + "\n")


def trim_irm_silk(fp):
    """Break the body silk line where the slot passes under the module. PS1 sits on the back,
    turned so that local y runs along front-view X (X = pin1 X + y) and local x 21.01 is the
    body edge nearest the board's bottom edge."""
    sx, sw, _ = BOARD["slot"]
    gap = [sx - sw / 2 - 0.5 - PS1_PINS["1"][0], sx + sw / 2 + 0.5 - PS1_PINS["1"][0]]
    for i, x in enumerate(fp):
        if isinstance(x, list) and x and x[0] == "fp_line" and first(x, "layer")[1] == "F.SilkS":
            st, en = first(x, "start"), first(x, "end")
            if float(st[1]) == float(en[1]) == 21.01 and float(st[2]) < gap[0] < gap[1] < float(en[2]):
                upper = copy.deepcopy(x)
                en[2] = gap[0]
                first(upper, "start")[2] = gap[1]
                first(upper, "uuid")[1] = "6d1c1f3e-0000-4000-8000-00000000b3c4"
                fp.insert(i + 1, upper)
                first(fp, "descr")[1] += " | silk body line split at the isolation slot"
                return
    raise RuntimeError("IRM silk line not found")


def build_tables():
    (PRJ / "fp-lib-table").write_text(
        '(fp_lib_table\n\t(version 7)\n'
        f'\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.pretty")(options "")'
        '(descr "Project footprints"))\n)\n')
    (PRJ / "sym-lib-table").write_text(
        '(sym_lib_table\n\t(version 7)\n'
        f'\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")'
        '(descr "Project symbols"))\n)\n')


def _have_stock():
    if not SYM_DIR or not FP_DIR:
        return False
    return all((SYM_DIR / f"{lib}.kicad_sym").exists() for lib, _, _ in SYMBOLS) and \
        all((FP_DIR / f"{lib}.pretty" / f"{n}.kicad_mod").exists() for lib, n in STOCK_FP.values())


if __name__ == "__main__":
    PRJ.mkdir(parents=True, exist_ok=True)
    if _have_stock():
        build_symbols()
        build_footprints()
        print(f"libs written to {PRJ}")
    elif (PRJ / f"{LIB}.kicad_sym").exists() and (PRJ / f"{LIB}.pretty").is_dir():
        print(f"gen_libs: KiCad stock libraries not found; keeping the committed libraries in {PRJ}",
              file=sys.stderr)
    else:
        sys.exit("gen_libs: KiCad stock libraries not found; set KICAD9_SYMBOL_DIR / KICAD9_FOOTPRINT_DIR")
    build_tables()
