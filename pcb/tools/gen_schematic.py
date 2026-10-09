"""Generate kicad/wiring_board.kicad_sch from parts.py (net labels at the pin ends)."""
import copy
import datetime
from pathlib import Path
from sexpr import loads, dumps, find, first, Sym, S
from parts import PARTS, LIB, PROJECT, uid, REV, IRM_DS

PRJ = Path(__file__).resolve().parents[1] / "kicad"
ROOT = uid("root-sheet")
DATE = datetime.date.today().isoformat()
POWER = ("+5V", "GND")

symlib = {s[1]: s for s in find(loads((PRJ / f"{LIB}.kicad_sym").read_text()), "symbol")}


def pins_of(symname):
    out = {}

    def walk(n):
        for x in n:
            if isinstance(x, list) and x:
                if x[0] == "pin":
                    at = first(x, "at")
                    out[first(x, "number")[1]] = (float(at[1]), float(at[2]), float(at[3]))
                else:
                    walk(x)
    walk(symlib[symname])
    return out


def font(hide=False, justify=None):
    e = S("effects", S("font", S("size", 1.27, 1.27)))
    if justify:
        e.append(S("justify", *[Sym(j) for j in justify.split()]))
    if hide:
        e.append(S("hide", Sym("yes")))
    return e


def prop(name, val, x, y, hide=False, justify=None):
    return S("property", name, val, S("at", x, y, 0), font(hide, justify))


items, lib_used = [], set()


def place(ref, symname, x, y, value, fp="", ds="", desc="", extra=None, in_bom=True, on_board=True):
    lib_used.add(symname)
    s = S("symbol", S("lib_id", f"{LIB}:{symname}"), S("at", x, y, 0), S("unit", 1),
          S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes" if in_bom else "no")),
          S("on_board", Sym("yes" if on_board else "no")), S("dnp", Sym("no")), S("uuid", uid("sym", ref)))
    s.append(prop("Reference", ref, x + 3, y - 8, hide=ref.startswith("#"), justify="left"))
    s.append(prop("Value", value, x + 3, y + 8.5, justify="left"))
    s.append(prop("Footprint", f"{LIB}:{fp}" if fp else "", x, y, hide=True))
    s.append(prop("Datasheet", ds, x, y, hide=True))
    s.append(prop("Description", desc, x, y, hide=True))
    for k, v in (extra or {}).items():
        s.append(prop(k, v, x, y, hide=True))
    for n in pins_of(symname):
        s.append(S("pin", n, S("uuid", uid("pin", ref, n))))
    s.append(S("instances", S("project", PROJECT, S("path", f"/{ROOT}", S("reference", ref), S("unit", 1)))))
    items.append(s)
    return {n: (x + px, y - py, ang) for n, (px, py, ang) in pins_of(symname).items()}


def label(net, xyang):
    x, y, ang = xyang
    # pin angle points from the pin end into the symbol: 0 = pin on the left side
    left = ang in (0.0,)
    items.append(S("label", net, S("at", x, y, 180 if left else 0), S("fields_autoplaced", Sym("yes")),
                   font(justify="right bottom" if left else "left bottom"),
                   S("uuid", uid("label", net, f"{x:.2f},{y:.2f}"))))


def note(text, x, y):
    items.append(S("text", text, S("exclude_from_sim", Sym("no")), S("at", x, y, 0),
                   font(justify="left top"), S("uuid", uid("text", text[:40]))))


G = 2.54
X = {"J1": 14 * G, "S1": 30 * G, "F1": 44 * G, "RV1": 54 * G, "PS1": 66 * G, "C1": 80 * G, "J2": 90 * G}
pwr_n = 0
for ref, p in PARTS.items():
    pins = place(ref, p["sym"], X[ref], 36 * G, p["value"], p["fp"], p["ds"], p["desc"],
                 {"Manufacturer": p["mfr"], "MPN": p["mpn"]})
    for pin, net in p["nets"].items():
        if net == "NC5":
            continue
        if net in POWER:
            pwr_n += 1
            xy = pins[pin]
            place(f"#PWR0{pwr_n:02d}", net, xy[0], xy[1], net, in_bom=False, on_board=False)
        else:
            label(net, pins[pin])

# L_F and N_SW feed power_in pins but are driven only by passives
for i, net in enumerate(["L_F", "N_SW"]):
    xy = ((50 + 8 * i) * G, 24 * G, 90.0)
    place(f"#FLG0{i + 1}", "PWR_FLAG", xy[0], xy[1], "PWR_FLAG", in_bom=False, on_board=False)
    label(net, (xy[0], xy[1], 180.0))

note("Wiring board for the smart wall plate (docs/DESIGN.md D-24, D-25; pcb/README.md).\n"
     "J1 takes the house wiring: L, N, PE in and switched L, N, PE out to the load.\n"
     "S1 (Marquardt 1802.2504) switches line and neutral; the PSU is fed after the switch through F1.\n"
     "F1 rating T1A is a designer's choice (Mean Well gives none): HUMAN REVIEW. F1 breaking capacity 200 A.\n"
     "Spacing targets (not a compliance claim): L-N, L in-L sw, N in-N sw, mains-PE >= 3.5 mm;\n"
     "mains-5 V >= 8.0 mm with a routed slot under PS1. Enforced by wiring_board.kicad_dru.\n"
     f"PS1 pinout per {IRM_DS}: 1=AC/L, 3=AC/N, 14=-Vo, 16=+Vo, 5=NC.", 25, 125)

lib_symbols = S("lib_symbols")
for name in sorted(lib_used):
    s = copy.deepcopy(symlib[name])
    s[1] = f"{LIB}:{name}"
    lib_symbols.append(s)

sch = S("kicad_sch", S("version", Sym("20250114")), S("generator", "eeschema"),
        S("generator_version", "9.0"), S("uuid", ROOT), S("paper", "A4"),
        S("title_block", S("title", "Smart wall plate - wiring board"), S("date", DATE), S("rev", REV),
          S("company", "smart-wallplate"),
          S("comment", 1, "Spacing values are design targets - human review before fab."),
          S("comment", 2, "Generated by pcb/tools/gen_schematic.py - edit parts.py")),
        lib_symbols, *items, S("sheet_instances", S("path", "/", S("page", "1"))),
        S("embedded_fonts", Sym("no")))
(PRJ / f"{PROJECT}.kicad_sch").write_text(dumps(sch) + "\n")
print("schematic written")
