"""Build the project-local KiCad libraries (pcb/kicad/psu_carrier.kicad_sym + .pretty).

Everything is copied from the stock KiCad 9 libraries so the project is
self-contained. Only change: J1's pads are shrunk 2.6 -> 2.4 mm so the
L'-N copper gap is >= 2.5 mm (stock pads leave 2.48 mm at 5.08 mm pitch).
"""
import copy, os, re, shutil, sys
from pathlib import Path
from sexpr import loads, dumps, find, first, Sym, S

# Where KiCad's stock libraries live differs per install. KiCad's own environment
# variables win; then the usual distro / Flatpak / macOS locations.
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
LIB = "psu_carrier"

# (stock lib, stock name, project name)
SYMBOLS = [
    ("Converter_ACDC", "IRM-03-5", "IRM-03-5"),
    ("Device", "Fuse", "Fuse"),
    ("Device", "Varistor", "Varistor"),
    ("Device", "C_Polarized", "C_Polarized"),
    ("Connector", "Screw_Terminal_01x02", "Screw_Terminal_01x02"),
    ("Connector_Generic", "Conn_01x02", "Conn_01x02"),
    ("power", "+5V", "+5V"),
    ("power", "GND", "GND"),
    ("power", "PWR_FLAG", "PWR_FLAG"),
]

FOOTPRINTS = {  # project name: (stock lib, stock name)
    "Converter_ACDC_MeanWell_IRM-03-xx_THT": ("Converter_ACDC", "Converter_ACDC_MeanWell_IRM-03-xx_THT"),
    "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal_Pad2.4mm":
        ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"),
    "Fuse_Littelfuse_372_D8.50mm": ("Fuse", "Fuse_Littelfuse_372_D8.50mm"),
    "RV_Disc_D7mm_W4.5mm_P5mm": ("Varistor", "RV_Disc_D7mm_W4.5mm_P5mm"),
    "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical": ("Connector_JST", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"),
    "CP_Radial_D5.0mm_P2.00mm": ("Capacitor_THT", "CP_Radial_D5.0mm_P2.00mm"),
}


def stock_symbol(lib, name):
    """Return a flattened copy of a stock symbol (resolves `extends`)."""
    L = loads((SYM_DIR / f"{lib}.kicad_sym").read_text())
    syms = {s[1]: s for s in find(L, "symbol")}
    s = copy.deepcopy(syms[name])
    ext = first(s, "extends")
    if not ext:
        return s
    base = copy.deepcopy(syms[ext[1]])
    bname = base[1]
    base[1] = name
    # derived properties override the base ones
    dprops = {p[1]: p for p in find(s, "property")}
    for i, x in enumerate(base):
        if isinstance(x, list) and x and x[0] == "property" and x[1] in dprops:
            base[i] = dprops.pop(x[1])
    for p in dprops.values():
        base.insert(len(base) - len(find(base, "symbol")) - 1, p)
    for sub in find(base, "symbol"):  # unit names follow the symbol name
        sub[1] = sub[1].replace(bname, name, 1)
    return base


def build_symbols():
    out = [Sym("kicad_symbol_lib"), S("version", Sym("20241209")), S("generator", "gen_libs"),
           S("generator_version", "9.0")]
    for lib, name, new in SYMBOLS:
        s = stock_symbol(lib, name)
        s[1] = new
        out.append(s)
    (PRJ / f"{LIB}.kicad_sym").write_text(dumps(out) + "\n")


def build_footprints():
    d = PRJ / f"{LIB}.pretty"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for new, (lib, name) in FOOTPRINTS.items():
        txt = (FP_DIR / f"{lib}.pretty" / f"{name}.kicad_mod").read_text()
        fp = loads(txt)
        fp[1] = new
        if new.endswith("_Pad2.4mm"):
            for pad in find(fp, "pad"):
                first(pad, "size")[1:3] = [2.4, 2.4]
            descr = first(fp, "descr")
            descr[1] += " | pads reduced to 2.4 mm for >=2.5 mm L-N copper gap (smart-wallplate)"
            for p in find(fp, "property"):
                if p[1] == "Value":
                    p[2] = new
        if new.startswith("Fuse_Littelfuse_372"):
            # stock lib has no 3D model for this footprint: use our TR5 envelope
            first(fp, "model")[1] = "${KIPRJMOD}/3d/Fuse_TR5_D8.5mm_H8mm.step"
        if new.startswith("Converter_ACDC_MeanWell_IRM-03"):
            trim_irm_silk(fp)
        (d / f"{new}.kicad_mod").write_text(dumps(fp) + "\n")


def trim_irm_silk(fp):
    """Break the body silk line where the board's isolation slot passes under the
    module (local y 20.0..23.5 = board x -7.75..-4.25 at orientation 270, pin 1 at x=15.24)."""
    for i, x in enumerate(fp):
        if isinstance(x, list) and x and x[0] == "fp_line" and first(x, "layer")[1] == "F.SilkS":
            st, en = first(x, "start"), first(x, "end")
            if float(st[1]) == float(en[1]) == -3.23 and float(st[2]) < 0 < 33 < float(en[2]):
                upper = copy.deepcopy(x)
                en[2] = 20.0
                first(upper, "start")[2] = 23.5
                first(upper, "uuid")[1] = "6d1c1f3e-0000-4000-8000-00000000a1b2"
                fp.insert(i + 1, upper)
                descr = first(fp, "descr")
                descr[1] += " | silk body line split at the isolation slot (smart-wallplate)"
                return
    raise RuntimeError("IRM silk line not found")


def build_tables():
    (PRJ / "fp-lib-table").write_text(
        '(fp_lib_table\n\t(version 7)\n'
        f'\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.pretty")(options "")'
        '(descr "Project footprints (copied from KiCad 9 stock libs)"))\n)\n')
    (PRJ / "sym-lib-table").write_text(
        '(sym_lib_table\n\t(version 7)\n'
        f'\t(lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")'
        '(descr "Project symbols (copied from KiCad 9 stock libs)"))\n)\n')


def _have_stock():
    if not SYM_DIR or not FP_DIR:
        return False
    return all((SYM_DIR / f"{lib}.kicad_sym").exists() for lib, _, _ in SYMBOLS) and \
        all((FP_DIR / f"{lib}.pretty" / f"{n}.kicad_mod").exists() for lib, n in FOOTPRINTS.values())


if __name__ == "__main__":
    PRJ.mkdir(parents=True, exist_ok=True)
    if _have_stock():
        build_symbols()
        build_footprints()
        print(f"libs written to {PRJ} (from {SYM_DIR} and {FP_DIR})")
    elif (PRJ / f"{LIB}.kicad_sym").exists() and (PRJ / f"{LIB}.pretty").is_dir():
        print(f"gen_libs: KiCad stock libraries not found (symbols: {SYM_DIR}, footprints: {FP_DIR});\n"
              f"          keeping the committed project libraries in {PRJ}.\n"
              "          Set KICAD9_SYMBOL_DIR / KICAD9_FOOTPRINT_DIR to rebuild them from stock.",
              file=sys.stderr)
    else:
        sys.exit("gen_libs: KiCad stock libraries not found; install KiCad's symbol and footprint\n"
                 "libraries or set KICAD9_SYMBOL_DIR / KICAD9_FOOTPRINT_DIR")
    build_tables()
