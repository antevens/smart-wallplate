"""Read footprint placement from the wiring board's .kicad_pcb (no pcbnew needed).

Coordinates are returned in the CAD frame: front-view x, y up, origin at the board
outline's centre shifted by WB_Y.
"""
import math
import re
from pathlib import Path
from params import WB_Y

ROOT = Path(__file__).resolve().parents[2]
WB_PCB = ROOT / "pcb" / "kicad" / "wiring_board.kicad_pcb"
_TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def _parse(text):
    stack = [[]]
    for tok in _TOKEN.findall(text):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(tok.strip('"') if tok.startswith('"') else tok)
    return stack[0][0]


def _kids(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def _first(node, key):
    found = _kids(node, key)
    return found[0] if found else None


def _xy(node):
    return float(node[1]), float(node[2])


class Board:
    def __init__(self, path=None):
        self.root = _parse(Path(path or WB_PCB).read_text())
        pts = []
        for item in self.root:
            if isinstance(item, list) and item[0] in ("gr_line", "gr_arc", "gr_rect"):
                if _first(item, "layer")[1] == "Edge.Cuts":
                    pts += [_xy(_first(item, k)) for k in ("start", "mid", "end") if _first(item, k)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.cx, self.cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        self.size = (max(xs) - min(xs), max(ys) - min(ys))
        self.fps = {}
        for fp in _kids(self.root, "footprint"):
            ref = [p[2] for p in _kids(fp, "property") if p[1] == "Reference"]
            if ref:
                self.fps[ref[0]] = fp

    def _place(self, ref):
        fp = self.fps[ref]
        at = _first(fp, "at")
        rot = float(at[3]) if len(at) > 3 else 0.0
        return fp, float(at[1]), float(at[2]), rot, _first(fp, "layer")[1] == "B.Cu"

    def _to_cad(self, fp_x, fp_y, rot, lx, ly):
        """Footprint-local (as stored in the board file) -> CAD x, y."""
        a = math.radians(rot)
        kx = fp_x + lx * math.cos(a) + ly * math.sin(a)
        ky = fp_y - lx * math.sin(a) + ly * math.cos(a)
        return kx - self.cx, self.cy - ky + WB_Y

    def fab_box(self, ref):
        """(xmin, xmax, ymin, ymax) of the footprint's fabrication outline in CAD coordinates."""
        fp, x, y, rot, back = self._place(ref)
        pts = []
        for kind in ("fp_line", "fp_rect", "fp_poly"):
            for item in _kids(fp, kind):
                if _first(item, "layer")[1] != ("B.Fab" if back else "F.Fab"):
                    continue
                if kind == "fp_poly":
                    pts += [_xy(p) for p in _kids(_first(item, "pts"), "xy")]
                else:
                    pts += [_xy(_first(item, "start")), _xy(_first(item, "end"))]
        cad = [self._to_cad(x, y, rot, lx, ly) for lx, ly in pts]
        return (min(p[0] for p in cad), max(p[0] for p in cad),
                min(p[1] for p in cad), max(p[1] for p in cad))

    def origin(self, ref):
        """Footprint origin in CAD coordinates (front-view x, y)."""
        _, x, y, rot, _ = self._place(ref)
        return tuple(round(c, 3) for c in self._to_cad(x, y, rot, 0.0, 0.0))

    def entry_dir(self, ref):
        """Unit vector (CAD x, y) the wire entries face, from the footprint's 'entry side' note."""
        fp, x, y, rot, back = self._place(ref)
        m = re.search(r"entry side ([+-])([xy])", _first(fp, "descr")[1])
        if not m:
            raise ValueError(f"{ref}: footprint description has no 'entry side +/-x/y' note")
        s = 1.0 if m.group(1) == "+" else -1.0
        lx, ly = (s, 0.0) if m.group(2) == "x" else (0.0, s)
        if back:
            ly = -ly                                    # flipped footprints are stored mirrored in y
        ox, oy = self._to_cad(x, y, rot, 0.0, 0.0)
        ex, ey = self._to_cad(x, y, rot, lx, ly)
        return round(ex - ox, 6), round(ey - oy, 6)
