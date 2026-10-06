"""Generate pcb/kicad/psu_carrier.kicad_sch from parts.py (labels at pin ends)."""
import copy, datetime
from pathlib import Path
from sexpr import loads, dumps, find, first, Sym, S
from parts import PARTS, LIB, uid, REV, IRM_DS

PRJ = Path(__file__).resolve().parents[1] / "kicad"
ROOT = uid("root-sheet")
DATE = datetime.date.today().isoformat()

symlib = {s[1]: s for s in find(loads((PRJ / f"{LIB}.kicad_sym").read_text()), "symbol")}


def pins_of(symname):
    out = {}
    def walk(n):
        for x in n:
            if isinstance(x, list) and x:
                if x[0] == "pin":
                    at = first(x, "at")
                    out[first(x, "number")[1]] = (float(at[1]), float(at[2]))
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
    su = uid("sym", ref)
    s = S("symbol", S("lib_id", f"{LIB}:{symname}"), S("at", x, y, 0), S("unit", 1),
          S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes" if in_bom else "no")),
          S("on_board", Sym("yes" if on_board else "no")), S("dnp", Sym("no")), S("uuid", su))
    hidden_ref = ref.startswith("#")
    s.append(prop("Reference", ref, x + 3, y - 6, hide=hidden_ref, justify="left"))
    s.append(prop("Value", value, x + 3, y + 6.5, justify="left"))
    s.append(prop("Footprint", f"{LIB}:{fp}" if fp else "", x, y, hide=True))
    s.append(prop("Datasheet", ds, x, y, hide=True))
    s.append(prop("Description", desc, x, y, hide=True))
    for k, v in (extra or {}).items():
        s.append(prop(k, v, x, y, hide=True))
    for n in pins_of(symname):
        s.append(S("pin", n, S("uuid", uid("pin", ref, n))))
    s.append(S("instances", S("project", "psu_carrier",
                              S("path", f"/{ROOT}", S("reference", ref), S("unit", 1)))))
    items.append(s)
    return {n: (x + px, y - py) for n, (px, py) in pins_of(symname).items()}


def label(net, xy, left=True):
    items.append(S("label", net, S("at", xy[0], xy[1], 180 if left else 0),
                   S("fields_autoplaced", Sym("yes")),
                   font(justify="right bottom" if left else "left bottom"),
                   S("uuid", uid("label", net, f"{xy[0]:.2f},{xy[1]:.2f}"))))


def note(text, x, y):
    items.append(S("text", text, S("exclude_from_sim", Sym("no")), S("at", x, y, 0),
                   font(justify="left top"), S("uuid", uid("text", text[:40]))))


# ---- place parts (schematic coords, mm, Y down) ----
G = 2.54
X = {"J1": 18 * G, "F1": 32 * G, "RV1": 42 * G, "PS1": 56 * G, "C1": 70 * G, "J2": 80 * G}
pwr_n = 0
for ref, p in PARTS.items():
    pins = place(ref, p["sym"], X[ref], 36 * G, p["value"], p["fp"], p["ds"], p["desc"],
                 {"Manufacturer": p["mfr"], "MPN": p["mpn"]})
    for pin, net in p["nets"].items():
        xy = pins[pin]
        if net == "NC5":
            continue  # NC pin: no_connect type, left open
        if net in ("+5V", "GND"):
            pwr_n += 1
            place(f"#PWR0{pwr_n:02d}", net, xy[0], xy[1], net, in_bom=False, on_board=False)
        else:
            left = xy[0] <= X[ref]
            label(net, xy, left=left if p["sym"] != "Fuse" and p["sym"] != "Varistor" else False)

# PWR_FLAGs: L_F and N are only driven by passives (fuse, terminal) but feed power_in pins
for i, net in enumerate(["L_F", "N"]):
    xy = ((44 + 8 * i) * G, 24 * G)
    place(f"#FLG0{i + 1}", "PWR_FLAG", xy[0], xy[1], "PWR_FLAG", in_bom=False, on_board=False)
    label(net, xy, left=False)

note("PSU carrier for the smart wall plate (see pcb/SPEC.md, docs/SAFETY.md).\n"
     "J1 is fed from the LOAD side of the emergency rocker + neutral (pigtail).\n"
     "The 15 A lighting path never runs on this PCB.\n"
     "F1 rating T1A is a designer's choice (Mean Well gives none; IRM-03 inrush 20 A typ @230 VAC): HUMAN REVIEW.\n"
     "Isolation targets (not a compliance claim): PRI-SEC >= 6.0 mm creepage/clearance with routed slot,\n"
     "L-N >= 2.5 mm, no copper within 2 mm of the rail edges. Enforced by psu_carrier.kicad_dru.\n"
     f"PS1 pinout per {IRM_DS} (2025-08-08): 1=AC/L, 3=AC/N, 14=-Vo, 16=+Vo, 5=NC.", 30, 120)

lib_symbols = S("lib_symbols")
for name in sorted(lib_used):
    s = copy.deepcopy(symlib[name])
    s[1] = f"{LIB}:{name}"
    lib_symbols.append(s)

sch = S("kicad_sch", S("version", Sym("20250114")), S("generator", "eeschema"),
        S("generator_version", "9.0"), S("uuid", ROOT), S("paper", "A4"),
        S("title_block", S("title", "Smart wall plate - PSU carrier"), S("date", DATE), S("rev", REV),
          S("company", "smart-wallplate"),
          S("comment", 1, "NOT certified. Design targets only - human review before fab."),
          S("comment", 2, "Generated by pcb/tools/gen_schematic.py - edit parts.py, not this file")),
        lib_symbols, *items,
        S("sheet_instances", S("path", "/", S("page", "1"))),
        S("embedded_fonts", Sym("no")))
(PRJ / "psu_carrier.kicad_sch").write_text(dumps(sch) + "\n")
print("schematic written")
